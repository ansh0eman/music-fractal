import librosa
import numpy as np
import logging
import random
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AudioAnalyzer:
    """Analyzes audio files to extract features for fractal mapping."""

    def __init__(self):
        pass

    def extract_features(self, file_path: str) -> Dict[str, float]:
        """
        Extract rhythmic and spectral features from an audio file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dict containing normalized features (0.0 to 1.0 where possible)
        """
        try:
            # Load audio file (downsample to 22050Hz, mono for performance)
            # For faster processing, we only load the first 30 seconds
            logger.info(f"Loading audio file: {file_path}")
            y, sr = librosa.load(file_path, sr=22050, mono=True, duration=30.0)
            
            if len(y) == 0:
                logger.warning("Empty audio file loaded")
                return self._default_features()

            # 1. Tempo (BPM)
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            tempo_array, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
            tempo = float(tempo_array[0]) if isinstance(tempo_array, (np.ndarray, list)) and len(tempo_array) > 0 else float(tempo_array)
            # Normalize tempo (assume typical range 60 - 200 BPM)
            normalized_tempo = min(max((tempo - 60) / 140.0, 0.0), 1.0)
            
            # 2. Spectral Centroid (brightness)
            cent = librosa.feature.spectral_centroid(y=y, sr=sr)
            mean_cent = float(np.mean(cent))
            # Normalize (assume typical range 500 - 5000 Hz)
            normalized_cent = min(max((mean_cent - 500) / 4500.0, 0.0), 1.0)
            
            # 3. RMS Energy
            rms = librosa.feature.rms(y=y)
            mean_rms = float(np.mean(rms))
            # Normalize (assume 0.0 to 0.5)
            normalized_energy = min(mean_rms * 2.0, 1.0)
            
            # 4. Spectral Bandwidth (timbral complexity)
            bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)
            mean_bw = float(np.mean(bw))
            # Normalize (assume 1000 - 4000)
            normalized_bw = min(max((mean_bw - 1000) / 3000.0, 0.0), 1.0)

            features = {
                "bpm": round(tempo, 1),
                "normalized_tempo": round(normalized_tempo, 3),
                "brightness": round(normalized_cent, 3),
                "energy": round(normalized_energy, 3),
                "complexity": round(normalized_bw, 3)
            }
            logger.info(f"Audio features extracted: {features}")
            return features
            
        except Exception as e:
            logger.error(f"Error analyzing audio: {e}", exc_info=True)
            return self._default_features()

    def _default_features(self) -> Dict[str, float]:
        """Return randomized default feature values when audio analysis fails or is missing."""
        return {
            "bpm": random.uniform(80.0, 160.0),
            "normalized_tempo": random.uniform(0.3, 0.8),
            "brightness": random.uniform(0.3, 0.8),
            "energy": random.uniform(0.2, 0.9),  # Wide range so L-system gets triggered sometimes
            "complexity": random.uniform(0.4, 0.8)
        }
