import subprocess
import os
import logging

# -------------------------
# Logging setup
# -------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# -------------------------
# Paths
# -------------------------
TTS_SCRIPT = "audio.py"       # your TTS generation script
VIDEO_SCRIPT = "video.py"    # your video generation script
AUDIO_FILE = "experience.wav"

# -------------------------
# Run TTS script
# -------------------------
logger.info("Running TTS script...")
tts_result = subprocess.run(["python", TTS_SCRIPT])
if tts_result.returncode != 0:
    logger.error("TTS script failed! Exiting.")
    exit(1)

if not os.path.exists(AUDIO_FILE):
    logger.error(f"{AUDIO_FILE} not found after TTS script! Exiting.")
    exit(1)

# -------------------------
# Run Video script
# -------------------------
logger.info("Running video script...")
video_result = subprocess.run(["python", VIDEO_SCRIPT, AUDIO_FILE])
if video_result.returncode != 0:
    logger.error("Video script failed! Exiting.")
    exit(1)

# -------------------------
# Clean up WAV
# -------------------------
if os.path.exists(AUDIO_FILE):
    os.remove(AUDIO_FILE)
    logger.info(f"Removed temporary audio file: {AUDIO_FILE}")

logger.info("All done!")
