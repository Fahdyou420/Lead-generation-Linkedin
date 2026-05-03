# Hunter Auto 1.0

Autonomous B2B lead generation and cold outreach agent for the Tunisian market, selling Ooredoo B2B packages.

## Features
- **Scraping**: Playwright + BeautifulSoup extracts leads from Google Maps and LinkedIn
- **AI Brain**: Local Ollama (qwen2.5:7b) automatically scores leads, extracts names, and generates hyper-personalised emails/messages in FR/AR/EN.
- **Outreach**: Automated emails (SMTP), LinkedIn messages (Playwright), and Telegram handoffs for hot leads.
- **Database**: Google Sheets (transparent, editable, shareable).
- **Dashboard**: Minimal Flask + HTMX web interface.

## Quick Start Setup

### 1. Install Dependencies
Make sure you have Docker installed.

```bash
docker pull ollama/ollama
ollama pull qwen2.5:7b
```

### 2. Configuration & Credentials
1. Copy `.env.example` to `.env` and fill out your details.
2. Go to Google Cloud Console, enable "Google Sheets API" and "Google Drive API".
3. Create a Service Account, download the JSON key, rename it to `credentials.json` and place it in the `config/` folder.
4. Share your Target Google Sheet with the Service Account email.

### 3. Telegram Bot
1. Talk to `@BotFather` on Telegram.
2. Type `/newbot`, follow steps, copy Bot Token.
3. Talk to your new bot, say "Hello".
4. Go to `https://api.telegram.org/bot<YourToken>/getUpdates` to get your `chat_id`.

### 4. Setup LinkedIn Session (Crucial)
To send messages on LinkedIn, playwrigt needs your authenticated session cookies. You must run this once locally before starting docker:

```bash
# In your local python environment
pip install playwright
playwright install chromium
python -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto('https://www.linkedin.com/login')
    print('Login manually in the browser window...')
    page.wait_for_timeout(60000) # give yourself 1 minute to login
    context.storage_state(path='playwright_sessions/state.json')
    browser.close()
"
```

### 5. Launch System
```bash
docker-compose up -d --build
```

Access Dashboard at `http://localhost:5000`
