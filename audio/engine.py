import logging
import os
from kokoro_onnx import Kokoro
import soundfile as sf
import numpy as np

logger = logging.getLogger(__name__)

class AudioEngine:
    def __init__(self, model_path="kokoro-v0_19.onnx", voices_path="voices.bin"):
        # We assume the models are in the root or a known location. 
        # If not found, kokoro-onnx might try to download or error out.
        # But per user, it's already installed.
        try:
            self.kokoro = Kokoro(model_path, voices_path)
            logger.info("Kokoro engine initialized with %s", model_path)
        except Exception as e:
            logger.error("Failed to initialize Kokoro: %s", e)
            raise

    def synthesize(self, text, voice="af_sky", speed=1.0):
        """
        Synthesizes text to audio.
        Returns (audio_data, sample_rate)
        """
        samples, sample_rate = self.kokoro.create(text, voice=voice, speed=speed)
        return samples, sample_rate

    def save(self, samples, sample_rate, output_path):
        sf.write(output_path, samples, sample_rate)
        logger.info("Saved audio to %s", output_path)

def get_engine():
    # Helper to find models
    model_path = "kokoro-v0_19.onnx"
    voices_path = "voices.bin"
    
    # Check if they exist in root, otherwise check common locations if needed
    # For now, assume they are in the project root as per standard setup
    return AudioEngine(model_path, voices_path)
