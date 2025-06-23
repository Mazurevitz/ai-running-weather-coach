import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
STRAVA_REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI", "http://localhost:8080/callback")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

FREE_AI_MODEL = "meta-llama/llama-3.1-8b-instruct:free"
CACHE_DURATION_HOURS = 24
MAX_ACTIVITIES_TO_ANALYZE = 15
FALLBACK_TO_RULES = True

STRAVA_AUTH_URL = "https://www.strava.com/oauth/authorize"
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
STRAVA_API_BASE = "https://www.strava.com/api/v3"

TOKENS_FILE = DATA_DIR / "tokens.json"
CACHE_FILE = DATA_DIR / "cache.json"
PROFILE_FILE = DATA_DIR / "profile.json"