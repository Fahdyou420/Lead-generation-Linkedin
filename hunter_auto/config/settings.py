import os
from dotenv import load_dotenv

load_dotenv()

import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

DEFAULT_CONFIG = {
    "TARGET_SECTORS": ["Banque", "Industrie", "Commerce", "IT"],
    "TARGET_CITIES": ["Tunis", "Sousse", "Sfax", "Ariana"],
    "TARGET_TITLES": ["Directeur Général", "CEO", "Gérant", "Directeur", "Fondateur"],
    "SCRAPE_INTERVAL_HOURS": 2,
    "OUTREACH_DAILY_LIMIT": 15,
    "CURRENT_STATE": "running"
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading config.json: {e}")
    return DEFAULT_CONFIG

def save_config(config_data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error writing config.json: {e}")
        return False

# Ensure config.json exists
if not os.path.exists(CONFIG_FILE):
    save_config(DEFAULT_CONFIG)

# Dynamic getters
def get_target_sectors():
    return load_config().get("TARGET_SECTORS", DEFAULT_CONFIG["TARGET_SECTORS"])

def get_target_cities():
    return load_config().get("TARGET_CITIES", DEFAULT_CONFIG["TARGET_CITIES"])

def get_target_titles():
    return load_config().get("TARGET_TITLES", DEFAULT_CONFIG["TARGET_TITLES"])

def get_scrape_interval():
    return int(load_config().get("SCRAPE_INTERVAL_HOURS", DEFAULT_CONFIG["SCRAPE_INTERVAL_HOURS"]))

def get_outreach_limit():
    return int(load_config().get("OUTREACH_DAILY_LIMIT", DEFAULT_CONFIG["OUTREACH_DAILY_LIMIT"]))

# Backward compatibility
_cfg = load_config()
TARGET_SECTORS = _cfg.get("TARGET_SECTORS", DEFAULT_CONFIG["TARGET_SECTORS"])

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

TIMEZONE = os.getenv("TIMEZONE", "Africa/Tunis")

# Ensure required config paths exist
os.makedirs(os.path.dirname(GOOGLE_CREDENTIALS_PATH), exist_ok=True)
os.makedirs("playwright_sessions", exist_ok=True)

STATUS_FILE = os.path.join(os.path.dirname(__file__), "status.json")

def load_status():
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "is_scraping": False,
        "current_activity": "Idle",
        "last_scraped_company": "-",
        "last_scraped_source": "-",
        "last_scraped_time": "-",
        "recent_scraped_leads": []
    }

def save_status(status_data):
    try:
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(status_data, f, indent=4, ensure_ascii=False)
    except:
        pass

def update_status(is_scraping=None, current_activity=None, last_scraped_company=None, last_scraped_source=None, found_lead=None):
    status = load_status()
    if is_scraping is not None:
        status["is_scraping"] = is_scraping
    if current_activity is not None:
        status["current_activity"] = current_activity
    if last_scraped_company is not None:
        status["last_scraped_company"] = last_scraped_company
        status["last_scraped_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
    if last_scraped_source is not None:
        status["last_scraped_source"] = last_scraped_source
    if found_lead is not None:
        recent = status.get("recent_scraped_leads", [])
        # Avoid duplicating the same lead in status recent list
        if not any(r.get("Company") == found_lead.get("Company") for r in recent):
            recent.insert(0, found_lead)
            status["recent_scraped_leads"] = recent[:5]
    save_status(status)
