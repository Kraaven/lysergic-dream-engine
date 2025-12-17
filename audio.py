import requests
from dotenv import load_dotenv
from TTS.api import TTS
import soundfile as sf
import numpy as np
import re
import logging
import string
import os
import sys
from urllib.parse import unquote
import librosa




# -------------------------
# Logging setup
# -------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

load_dotenv()

# -------------------------
# Helpers
# -------------------------
def slow_audio(wav, rate=0.9):
    if not isinstance(wav, np.ndarray):
        wav = np.asarray(wav, dtype=np.float32)

    # librosa expects mono float32
    wav = wav.astype(np.float32)

    return librosa.effects.time_stretch(wav, rate=rate)


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def chunk_text(text: str, max_chars: int = 400):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks, buf = [], ""
    for s in sentences:
        if len(buf) + len(s) <= max_chars:
            buf += " " + s
        else:
            chunks.append(buf.strip())
            buf = s
    if buf:
        chunks.append(buf.strip())
    return chunks

def silence(seconds: float, sr: int):
    return np.zeros(int(seconds * sr), dtype=np.float32)

def sanitize_filename(name: str) -> str:
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return "".join(c for c in name if c in valid_chars).replace(" ", "_")

# -------------------------
# Check for URL argument
# -------------------------
experience_url = None
if len(sys.argv) > 1:
    raw_url = sys.argv[1]
    experience_url = unquote(raw_url)  # decode if URL-encoded
    logger.info("Using provided experience URL: %s", experience_url)

# -------------------------
# Fetch random experience if no URL provided
# -------------------------
if not experience_url:
    logger.info("Fetching random Erowid experience")
    url = "https://lysergic.kaizenklass.xyz/api/v1/erowid/random/experience?size_per_substance=1"
    substances = {
        "urls": [
            "https://www.erowid.org/chemicals/dmt/dmt.shtml",
            "https://www.erowid.org/chemicals/lsd/lsd.shtml",
            "https://www.erowid.org/plants/salvia/salvia.shtml",
            "https://www.erowid.org/plants/cannabis/cannabis.shtml",
        ]
    }
    experience = requests.post(url, json=substances).json()
    experience_url = experience["experience"]["url"]

# -------------------------
# Fetch full experience details
# -------------------------
logger.info("Fetching full experience details")
url = "https://lysergic.kaizenklass.xyz/api/v1/erowid/experience"
payload = {"url": experience_url}
experience_details = requests.post(url, json=payload).json()
data = experience_details["data"]

# -------------------------
# Clean fields
# -------------------------
clean_experience = {
    "title": data["title"],
    "username": data["author"],
    "gender": data["metadata"].get("gender", "Unknown"),
    "age": data["metadata"].get("age", "Unknown"),
    "content": data["content"],
    "doses": data["doses"],
}

logger.info("Loaded experience: '%s' by %s", clean_experience["title"], clean_experience["username"])

# -------------------------
# Substances ONLY
# -------------------------
substances_used = sorted({d["substance"] for d in clean_experience["doses"]})
substances_text = ", ".join(substances_used)
logger.info("Substances involved: %s", substances_text)

# -------------------------
# Build narration script
# -------------------------
tts_script = f"""
Welcome.

This is a narrated experience report sourced from Erowid dot org,
a public archive of psychoactive experience reports shared for
educational and harm reduction purposes.

This video is not an endorsement, not medical advice,
and does not encourage illegal activity.

Listener discretion is advised.

{clean_experience['title']}

This experience was submitted under the username
{clean_experience['username']}.

Reported age: {clean_experience['age']}.
Reported gender: {clean_experience['gender']}.

The substances involved in this experience include:
{substances_text}.

What follows is the original experience,
with minimal edits for clarity.

{clean_experience['content']}

Experiences like this can be deeply personal and unpredictable,
and are influenced by mindset, environment,
and many other factors.

If you choose to explore altered states of consciousness,
education, preparation, and harm reduction are essential.

Thank you for listening.
"""


# -------------------------
# Normalize + chunk
# -------------------------
clean_text = normalize_text(tts_script)
chunks = chunk_text(clean_text)
logger.info("Text normalized and split into %d chunks", len(chunks))

# -------------------------
# Load TTS model
# -------------------------
logger.info("Loading Coqui TTS model")
tts = TTS(
    model_name="tts_models/en/vctk/vits",
    progress_bar=False,
    gpu=False
)

speaker = "p232"  # male
sample_rate = tts.synthesizer.output_sample_rate

# -------------------------
# Generate audio
# -------------------------
audio_parts = []
for i, chunk in enumerate(chunks):
    logger.info("Synthesizing chunk %d/%d", i + 1, len(chunks))
    wav = tts.tts(text=chunk, speaker=speaker)
    # wav = slow_audio(wav, rate=0.88) 
    audio_parts.append(wav)
    audio_parts.append(silence(0.5, sample_rate))

final_audio = np.concatenate(audio_parts)

# -------------------------
# Save audio with sanitized title
# -------------------------
audio_filename = sanitize_filename(clean_experience['title']) + ".wav"
sf.write(audio_filename, final_audio, sample_rate)
logger.info("Saved audio as %s", audio_filename)

# -------------------------
# Print the filename for the runner
# -------------------------
print(audio_filename)
