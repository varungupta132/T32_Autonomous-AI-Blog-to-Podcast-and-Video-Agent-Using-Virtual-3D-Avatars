import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./podcasts.db")
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./generated_podcasts"))
TEMP_DIR = Path(os.getenv("TEMP_DIR", "./temp_audio"))
MAX_BLOG_LENGTH = int(os.getenv("MAX_BLOG_LENGTH", 15000))
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", 10))

OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

VOICE_LIBRARY = {
    "speaker_1": {"voice": "en-IN-PrabhatNeural",  "name": "Prabhat (Indian Male)"},
    "speaker_2": {"voice": "en-IN-NeerjaNeural",   "name": "Neerja (Indian Female)"},
    "speaker_3": {"voice": "hi-IN-MadhurNeural",   "name": "Madhur (Hindi Male)"},
    "speaker_4": {"voice": "hi-IN-SwaraNeural",    "name": "Swara (Hindi Female)"},
    "speaker_5": {"voice": "en-US-GuyNeural",      "name": "Guy (US Male)"},
    "speaker_6": {"voice": "en-US-JennyNeural",    "name": "Jenny (US Female)"},
}
