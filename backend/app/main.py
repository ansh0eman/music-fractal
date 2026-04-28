from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
import logging
import tempfile
from pathlib import Path

from app.services.lyrics_client import LyricsClient
from app.services.lyrics_analyzer import LyricsAnalyzer
from app.services.audio_analyzer import AudioAnalyzer
from app.services.fractal_renderer import FractalRenderer
from app.services.video_renderer import VideoRenderer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Fractal Music Visualizer API", version="0.1.0")

# Initialize services
lyrics_client = LyricsClient()
lyrics_analyzer = LyricsAnalyzer()
audio_analyzer = AudioAnalyzer()
fractal_renderer = FractalRenderer(width=1024, height=1024)
video_renderer = VideoRenderer(fractal_renderer)

# Create static directory for images (relative to backend/)
STATIC_DIR = Path(__file__).parent.parent / "static"
STATIC_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class GenerateRequest(BaseModel):
    song_title: str = Field(..., min_length=1, max_length=256)
    artist_name: Optional[str] = Field(None, max_length=256)


class FeatureSummary(BaseModel):
    bpm: Optional[float] = None
    repetition_score: Optional[float] = None
    symmetry_score: Optional[float] = None
    notes: Optional[str] = None


class FractalMetadata(BaseModel):
    model: str
    depth: int
    color_palette: str
    seed: str
    math_details: Optional[dict] = None


class GenerateResponse(BaseModel):
    song_title: str
    artist_name: Optional[str]
    image_url: str
    features: FeatureSummary
    fractal: FractalMetadata
    lyrics: Optional[str] = None


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_fractal(
    song_title: str = Form(...),
    artist_name: Optional[str] = Form(None),
    audio_file: Optional[UploadFile] = File(None),
    override_model: Optional[str] = Form("auto"),
    override_palette: Optional[str] = Form("auto"),
    override_depth: Optional[int] = Form(None)
) -> GenerateResponse:
    """
    End-to-end pipeline:
    1. Fetch lyrics from external API
    2. Analyze lyrics and extract features
    3. Analyze audio (if provided)
    4. Map features to fractal parameters
    5. Generate fractal image
    6. Return metadata and image URL
    """
    song_title = song_title.strip()
    artist_name = artist_name.strip() if artist_name else None

    if not song_title:
        raise HTTPException(status_code=400, detail="Song title must not be empty.")

    if not artist_name:
        raise HTTPException(
            status_code=400,
            detail="Artist name is required for lyrics lookup. Please provide both song title and artist.",
        )

    logger.info(f"Generating fractal for: {song_title} by {artist_name}")

    # Step 1: Fetch lyrics
    lyrics = await lyrics_client.fetch_lyrics(artist_name, song_title)
    
    if not lyrics:
        suggestions = [
            "Check spelling of song title and artist name",
            "Try removing 'The' from artist name (e.g., 'Beatles' instead of 'The Beatles')",
            "Try the full album version name if the song has multiple versions",
            "Some songs may not be available in the lyrics database",
        ]
        detail_msg = (
            f"Could not find lyrics for '{song_title}' by {artist_name}. "
            f"Suggestions: {'; '.join(suggestions)}"
        )
        raise HTTPException(status_code=404, detail=detail_msg)

    logger.info(f"Fetched lyrics ({len(lyrics)} characters)")

    # Step 2: Analyze lyrics and extract features
    lyric_features = lyrics_analyzer.extract_features(lyrics)
    
    # Step 3: Analyze audio
    audio_features = {}
    if audio_file and audio_file.filename:
        logger.info(f"Analyzing uploaded audio file: {audio_file.filename}")
        try:
            # Save uploaded file to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as temp_file:
                content = await audio_file.read()
                temp_file.write(content)
                temp_path = temp_file.name
                
            audio_features = audio_analyzer.extract_features(temp_path)
            
            # Clean up
            os.remove(temp_path)
        except Exception as e:
            logger.error(f"Error processing audio file: {e}")
            audio_features = audio_analyzer._default_features()
    else:
        logger.info("No audio file provided, using default audio features")
        audio_features = audio_analyzer._default_features()
        
    # Merge features
    combined_features = {**lyric_features, **audio_features}

    # Prepare Overrides
    overrides = {
        "model": override_model,
        "palette": override_palette,
        "depth": override_depth
    }

    # Step 4 & 5: Generate fractal
    try:
        fractal_image, fractal_metadata = fractal_renderer.render(
            combined_features, song_title, artist_name, overrides
        )
    except Exception as e:
        logger.error(f"Error rendering fractal: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to generate fractal image. Please try again.",
        )

    # Step 6: Save image and generate URL
    import hashlib
    filename_hash = hashlib.md5(
        f"{song_title}:{artist_name}:{fractal_metadata['seed']}".encode()
    ).hexdigest()[:12]
    image_filename = f"fractal_{filename_hash}.png"
    image_path = STATIC_DIR / image_filename
    
    fractal_image.save(image_path, "PNG")
    image_url = f"/static/{image_filename}"

    logger.info(f"Generated fractal image: {image_url}")

    # Prepare response
    features = FeatureSummary(
        bpm=combined_features.get("bpm"),
        repetition_score=round(lyric_features.get("repetition_score", 0.0), 3),
        symmetry_score=round(lyric_features.get("symmetry_score", 0.0), 3),
        notes=f"Analyzed {lyric_features.get('num_lines', 0)} lines of lyrics. "
              f"Audio BPM: {combined_features.get('bpm')}. "
              f"Diversity: {round(lyric_features.get('ngram_diversity', 0.0), 2)}",
    )

    fractal = FractalMetadata(
        model=fractal_metadata["model"],
        depth=fractal_metadata["depth"],
        color_palette=fractal_metadata["color_palette"],
        seed=fractal_metadata["seed"],
    )

    return GenerateResponse(
        song_title=song_title,
        artist_name=artist_name,
        image_url=image_url,
        features=features,
        fractal=fractal,
        lyrics=lyrics
    )


class VideoExportResponse(BaseModel):
    video_url: str

@app.post("/api/export_video", response_model=VideoExportResponse)
async def export_video(
    song_title: str = Form(...),
    artist_name: Optional[str] = Form(None),
    audio_file: Optional[UploadFile] = File(None),
    override_model: Optional[str] = Form("auto"),
    override_palette: Optional[str] = Form("auto"),
    override_depth: Optional[int] = Form(None)
) -> VideoExportResponse:
    song_title = song_title.strip()
    artist_name = artist_name.strip() if artist_name else None

    # Step 1: Analyze audio if provided
    audio_features = {}
    if audio_file and audio_file.filename:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as temp_file:
                content = await audio_file.read()
                temp_file.write(content)
                temp_path = temp_file.name
                
            audio_features = audio_analyzer.extract_features(temp_path)
            os.remove(temp_path)
        except Exception as e:
            logger.error(f"Error processing audio file: {e}")
            audio_features = audio_analyzer._default_features()
    else:
        audio_features = audio_analyzer._default_features()

    overrides = {
        "model": override_model,
        "palette": override_palette,
        "depth": override_depth
    }

    try:
        video_url = video_renderer.render_video(audio_features, song_title, artist_name or "", overrides)
        return VideoExportResponse(video_url=video_url)
    except Exception as e:
        logger.error(f"Error rendering video: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to export video.")

@app.get("/health")
async def health() -> Dict[str, Any]:
    return {"status": "ok"}
