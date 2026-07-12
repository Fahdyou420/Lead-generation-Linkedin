import os
from dotenv import load_dotenv

load_dotenv()

NOUS_API_KEY = os.getenv("NOUS_API_KEY")
NOUS_MODEL = os.getenv("NOUS_MODEL", "stepfun/step-3.7-flash:free")
NOUS_API_BASE = os.getenv("NOUS_API_BASE", "https://api.nousresearch.com/v1")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "./config/credentials.json")

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

HUNTER_IO_API_KEY = os.getenv("HUNTER_IO_API_KEY")

TARGET_SECTORS = os.getenv("TARGET_SECTORS", "Banque,Industrie,Commerce,IT").split(",")

OUTREACH_DAILY_LIMIT = int(os.getenv("OUTREACH_DAILY_LIMIT", "15"))
SCRAPE_INTERVAL_HOURS = int(os.getenv("SCRAPE_INTERVAL_HOURS", "2"))
TIMEZONE = os.getenv("TIMEZONE", "Africa/Tunis")

# Ensure required config paths exist
os.makedirs(os.path.dirname(GOOGLE_CREDENTIALS_PATH), exist_ok=True)
os.makedirs("playwright_sessions", exist_ok=True)
