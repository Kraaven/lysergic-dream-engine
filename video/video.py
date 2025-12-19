import sys
import os
import logging
import random

from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    CompositeAudioClip,
)
from moviepy.audio.fx.all import volumex, audio_loop

# -------------------------
# Logging
# -------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------
# Parameters
# -------------------------
if len(sys.argv) < 2:
    logger.error("Usage: python video.py <tts_audio_file>")
    sys.exit(1)

tts_audio_file = sys.argv[1]

random_music_index = random.randint(1, 7)
random_clip_index = random.randint(1, 5)

music_file = f"music/{random_music_index}.mp3"
clip_file = f"clips/{random_clip_index}.mp4"

output_folder = "output"
os.makedirs(output_folder, exist_ok=True)

base_name = os.path.splitext(os.path.basename(tts_audio_file))[0]
output_file = os.path.join(output_folder, f"{base_name}.mp4")

TARGET_FPS = 30
MUSIC_VOLUME = 0.05

# -------------------------
# Load media
# -------------------------
logger.info("Loading TTS audio: %s", tts_audio_file)
tts_clip = AudioFileClip(tts_audio_file)

logger.info("Loading background music: %s", music_file)
music_clip = AudioFileClip(music_file)

logger.info("Loading video clip: %s", clip_file)
video_clip = VideoFileClip(clip_file)

# -------------------------
# Prepare video (loop to TTS duration)
# -------------------------
loops = int(tts_clip.duration // video_clip.duration) + 1

video_clip = (
    video_clip
    .loop(n=loops)
    .subclip(0, tts_clip.duration)
)

# -------------------------
# Prepare music
# -------------------------
music_clip = audio_loop(music_clip, duration=tts_clip.duration)
music_clip = volumex(music_clip, MUSIC_VOLUME)

# -------------------------
# Combine audio
# -------------------------
combined_audio = CompositeAudioClip([
    music_clip,
    tts_clip
])

video_clip = video_clip.set_audio(combined_audio)

# -------------------------
# Export
# -------------------------
logger.info("Exporting final video to %s", output_file)

video_clip.write_videofile(
    output_file,
    codec="libx264",
    audio_codec="aac",
    preset="medium",
    threads=4,
    fps=TARGET_FPS
)

logger.info("Video exported successfully!")

# -------------------------
# Cleanup
# -------------------------
try:
    if os.path.exists(tts_audio_file):
        os.remove(tts_audio_file)
        logger.info("Removed temporary audio file: %s", tts_audio_file)
except Exception as e:
    logger.warning("Failed to remove temp audio file: %s", e)
    
# -------------------------
# Output for runner
# -------------------------
print(output_file)
