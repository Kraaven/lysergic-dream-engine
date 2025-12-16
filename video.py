from moviepy.editor import VideoClip, AudioFileClip
import numpy as np
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------
# Parameters
# -------------------------
audio_file = "experience.wav"  # your TTS audio
output_folder = "output"
output_file = os.path.join(output_folder, "experience_video.mp4")
fps = 30
width, height = 720, 720  # square video

# -------------------------
# Ensure output folder exists
# -------------------------
os.makedirs(output_folder, exist_ok=True)

# -------------------------
# Load audio
# -------------------------
logger.info("Loading audio: %s", audio_file)
audio_clip = AudioFileClip(audio_file)
duration = audio_clip.duration

# -------------------------
# Video generator function
# -------------------------
def make_frame(t):
    """
    Generates a frame at time t.
    Trippy example: moving sine-based color pattern.
    """
    x = np.linspace(0, 4*np.pi, width)
    y = np.linspace(0, 4*np.pi, height)
    X, Y = np.meshgrid(x, y)
    R = np.sin(X + t*3) + np.cos(Y + t*2)
    G = np.cos(X + t*2) + np.sin(Y + t*3)
    B = np.sin(X + Y + t*2)
    frame = np.stack([
        ((R + 2)/4 * 255),
        ((G + 2)/4 * 255),
        ((B + 2)/4 * 255)
    ], axis=2).astype(np.uint8)
    return frame

# -------------------------
# Create video clip
# -------------------------
logger.info("Creating video clip (duration: %.2fs)", duration)
video_clip = VideoClip(make_frame, duration=duration)
video_clip = video_clip.set_audio(audio_clip)
video_clip = video_clip.set_fps(fps)

# -------------------------
# Export
# -------------------------
logger.info("Exporting video to %s", output_file)
video_clip.write_videofile(
    output_file,
    codec="libx264",
    audio_codec="aac",
    preset="medium",
    threads=4
)

logger.info("Video exported successfully!")
