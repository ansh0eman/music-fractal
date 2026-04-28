import imageio
import numpy as np
import os
import tempfile
from typing import Dict, Any
from app.services.fractal_renderer import FractalRenderer
import logging

logger = logging.getLogger(__name__)

class VideoRenderer:
    def __init__(self, fractal_renderer: FractalRenderer):
        # We create a lower-resolution renderer specifically for fast video generation
        self.fast_renderer = FractalRenderer(width=512, height=512)

    def render_video(self, features: Dict[str, float], song_title: str, artist_name: str, overrides: Dict[str, Any], duration: int = 3, fps: int = 24) -> str:
        """
        Renders a looping video of the fractal by mutating the energy/features over time.
        Returns the path to the generated MP4 file.
        """
        logger.info(f"Generating {duration}s video for {song_title}")
        
        frames = []
        num_frames = duration * fps
        
        base_energy = features.get("energy", 0.5)
        
        # Render each frame
        for i in range(num_frames):
            # Mutate energy using a sine wave to create a pulsing effect
            t = i / num_frames
            pulse = np.sin(t * np.pi * 2) * 0.2  # +/- 20%
            
            frame_features = features.copy()
            frame_features["energy"] = max(0.1, min(1.0, base_energy + pulse))
            
            # For Mandelbrot, we can also pulse the complexity slightly to zoom in/out
            if overrides.get("model", "auto") == "mandelbrot" or features.get("complexity", 0.5) > 0.8:
                 frame_features["complexity"] = features.get("complexity", 0.5) + (pulse * 0.5)
            
            # Render frame
            img, _ = self.fast_renderer.render(frame_features, song_title, artist_name, overrides)
            frames.append(np.array(img))
            
        # Save to temp file
        import hashlib
        import uuid
        seed = self.fast_renderer.generate_seed(song_title, artist_name)
        filename_hash = hashlib.md5(f"{song_title}:{artist_name}:{seed}:{uuid.uuid4()}".encode()).hexdigest()[:12]
        
        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "static")
        os.makedirs(static_dir, exist_ok=True)
        
        video_path = os.path.join(static_dir, f"fractal_{filename_hash}.mp4")
        
        logger.info(f"Saving video to {video_path}")
        imageio.mimwrite(video_path, frames, fps=fps, format='FFMPEG', macro_block_size=None)
        
        return f"/static/fractal_{filename_hash}.mp4"
