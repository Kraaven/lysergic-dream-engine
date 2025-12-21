import os
import logging
import requests
from database import init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Official paths
MODEL_PATH = "models/kokoro-v1.0.onnx"
VOICES_PATH = "models/voices-v1.0.bin"

# Download URLs
KOKORO_MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
VOICES_BIN_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"


def download(url: str, dest: str):
    logger.info(f"Downloading {url} → {dest}")
    resp = requests.get(url, stream=True, timeout=60)
    resp.raise_for_status()
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)


def validate_environment() -> bool:
    logger.info("--- Starting Pre-flight Validation ---")

    # 1. Create required folders
    for folder in ["models", "data", "output", "music", "clips"]:
        os.makedirs(folder, exist_ok=True)

    # 2. Database
    init_db()

    # 3. Kokoro Model
    if not os.path.exists(MODEL_PATH):
        logger.warning("Kokoro model missing. Downloading…")
        try:
            download(KOKORO_MODEL_URL, MODEL_PATH)
        except Exception as e:
            logger.error(f"Failed to download Kokoro model: {e}")
            return False

    # 4. Voices
    if not os.path.exists(VOICES_PATH):
        logger.warning("Voices file missing. Downloading…")
        try:
            download(VOICES_BIN_URL, VOICES_PATH)
        except Exception as e:
            logger.error(f"Failed to download voices file: {e}")
            return False

    # 5. Internet check (optional but useful)
    try:
        requests.get("https://www.erowid.org", timeout=5)
    except Exception:
        logger.error("Network might be unreachable (erowid.org unreachable).")
        return False

    logger.info("Validation Successful.")
    return True
