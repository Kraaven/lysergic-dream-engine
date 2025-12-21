import sys
import os
import requests
import logging
from urllib.parse import unquote
# from google import genai
from dotenv import load_dotenv

from validator import validate_environment
from database import is_processed, mark_as_processed
from engine_audio import AudioEngine
from engine_video import create_video
import yt

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()
# client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def fetch_trip_data(url=None):
    """Fetches a random experience or a specific one from the API."""
    if not url:
        logger.info("Fetching random Erowid experience...")
        api_url = "https://lysergic.kaizenklass.xyz/api/v1/erowid/random/experience?size_per_substance=1"
        substances = {"urls": ["https://www.erowid.org/chemicals/lsd/lsd.shtml", "https://www.erowid.org/chemicals/dmt/dmt.shtml"]}
        resp = requests.post(api_url, json=substances).json()
        url = resp["experience"]["url"]

    logger.info(f"Fetching details for: {url}")
    detail_resp = requests.post("https://lysergic.kaizenklass.xyz/api/v1/erowid/experience", json={"url": url})
    return detail_resp.json()["data"], url

def clean_with_gemini(content):
    """Uses Gemini to clean punctuation and extract the primary substance."""
    prompt = (
        "Clean the following trip report: fix punctuation, remove repetitive meta-text, "
        "and return a JSON object: { \"cleaned_content\": \"...\", \"primary_substance\": \"...\" }"
    )
    # response = client.models.generate_content(model="gemini-2.0-flash", contents=f"{prompt}\n\nContent:\n{content}")
    import json
    try:
        data = json.loads(response.text.strip())
        return data["cleaned_content"], data["primary_substance"]
    except:
        return content, "Unknown"

def main():
    if not validate_environment(): return

    # 1. Scraping
    raw_data, experience_url = fetch_trip_data()
    if is_processed(experience_url):
        logger.info("Experience already in database. Skipping.")
        return

    # 2. AI Cleaning
    cleaned_text, substance = clean_with_gemini(raw_data["content"])
    title = raw_data.get("title", "Unknown Experience")

    # 3. Audio & Video Production
    ae = AudioEngine()
    srt_file = ae.generate(cleaned_text, "temp_audio.wav")
    video_file = f"output/{substance.lower()}_report.mp4"
    create_video("temp_audio.wav", srt_file, video_file)

    # 4. Upload & Database
    yt.upload_video(video_file, f"{title} [{substance} Trip Report]")
    mark_as_processed(experience_url, title, substance)
    logger.info("Pipeline Complete.")

if __name__ == "__main__":
    main()