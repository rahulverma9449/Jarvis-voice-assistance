from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
load_dotenv(PROJECT_DIR / ".env")
DATA_DIR = BASE_DIR / "data"
SCREENSHOT_DIR = DATA_DIR / "screenshots"
GENERATED_IMAGE_DIR = DATA_DIR / "generated_images"
HISTORY_FILE = DATA_DIR / "history.jsonl"
BROWSER_DATA_FILE = DATA_DIR / "browser_data.jsonl"
MEMORY_FILE = DATA_DIR / "memory.json"

ASSISTANT_NAME = os.getenv("JARVIS_NAME", "Jarvis")
USER_NAME = os.getenv("JARVIS_USER", "Rahul")
LANGUAGE = os.getenv("JARVIS_LANGUAGE", "en-IN")
VOICE_RATE = int(os.getenv("JARVIS_VOICE_RATE", "150"))
WEATHER_CITY = os.getenv("JARVIS_WEATHER_CITY", "New Delhi")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-latest")
IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-2")
ATLASSIAN_SITE_URL = os.getenv("ATLASSIAN_SITE_URL", "").rstrip("/")
ATLASSIAN_EMAIL = os.getenv("ATLASSIAN_EMAIL", "")
ATLASSIAN_API_TOKEN = os.getenv("ATLASSIAN_API_TOKEN", "")
JIRA_BOARD_ID = os.getenv("JIRA_BOARD_ID", "")

for directory in (DATA_DIR, SCREENSHOT_DIR, GENERATED_IMAGE_DIR):
    directory.mkdir(parents=True, exist_ok=True)
