import datetime
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

class AudioEngine:
    def __init__(self, voice: str = "af_sky"):
        """
        voice: name of the voice in voices-v1.0.bin (e.g., "af_sky", "af", etc.)
        """
        self.kokoro = Kokoro(
            model_path="models/kokoro-v1.0.onnx",
            voices_path="models/voices-v1.0.bin",
        )
        self.voice = voice

    def _format_time(self, seconds: float) -> str:
        td = datetime.timedelta(seconds=seconds)
        total = int(td.total_seconds())
        h, r = divmod(total, 3600)
        m, s = divmod(r, 60)
        ms = int((seconds - int(seconds)) * 1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

    def generate(self, text: str, output_wav: str) -> str:
        """
        Generates audio + SRT from the given text.
        Returns the path to the generated .srt
        """
        # Split on periods (simple sentence break)
        sentences = [s.strip() for s in text.split(".") if s.strip()]

        audio_buffers = []
        srt_lines = []
        current_t = 0.0

        for idx, sentence in enumerate(sentences, start=1):
            # Generate with a trailing period for better TTS
            samples, sample_rate = self.kokoro.create(
                sentence + ".",
                voice=self.voice,
                speed=1.0,
                lang="en-us",
            )

            duration = len(samples) / sample_rate

            # Build SRT entry
            srt_lines.append(
                f"{idx}\n"
                f"{self._format_time(current_t)} --> {self._format_time(current_t + duration)}\n"
                f"{sentence}.\n\n"
            )

            audio_buffers.append(samples)
            current_t += duration

        # Concatenate all audio segments
        final_audio = np.concatenate(audio_buffers)

        # Write WAV
        sf.write(output_wav, final_audio, sample_rate)

        # Write SRT
        srt_path = output_wav.replace(".wav", ".srt")
        with open(srt_path, "w", encoding="utf-8") as f:
            f.writelines(srt_lines)

        return srt_path
