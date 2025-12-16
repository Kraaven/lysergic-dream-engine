import subprocess
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

AUDIO_SCRIPT = "audio.py"
VIDEO_SCRIPT = "video.py"

# Optional experience URL argument
experience_url = sys.argv[1] if len(sys.argv) > 1 else None

# -------------------------
# Run audio.py
# -------------------------
logger.info("Running audio.py...")
cmd = ["python", AUDIO_SCRIPT]
if experience_url:
    cmd.append(experience_url)

result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    logger.error("audio.py failed!\n%s", result.stderr)
    exit(1)

# Only take the last line of stdout as the audio file
audio_file = result.stdout.strip().splitlines()[-1]
logger.info("Generated audio: %s", audio_file)

# -------------------------
# Run video.py with audio
# -------------------------
logger.info("Running video.py...")
video_result = subprocess.run(["python", VIDEO_SCRIPT, audio_file])
if video_result.returncode != 0:
    logger.error("video.py failed!")
    exit(1)

logger.info("Pipeline completed successfully!")
