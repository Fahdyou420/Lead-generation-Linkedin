# Hunter Auto 1.0 - Deployment & Setup Guide

Since you already have Docker and Ollama running on your Windows machine, the setup is straightforward!

## Step 1: Export the Codebase
1. Click the **Settings** menu (⚙️ gear icon) in AI Studio.
2. Select **Download ZIP** or **Export to GitHub**.
3. Extract the ZIP file on your Windows PC (e.g. `C:\Users\user\Desktop\hunter_auto`).

## Step 2: Configure Secrets
1. Inside the `hunter_auto` folder, rename the file `.env.example` to `.env`.
2. Open `.env` in a text editor like Notepad.
3. Your Telegram Chat ID is: `2037668278` (It is already set in the .env.example)
4. Fill in the rest of the file:
   - **GMAIL_ADDRESS**: Your normal Gmail address.
   - **GMAIL_APP_PASSWORD**: Go to your Google Account Security Settings -> search "App passwords" -> create a new one named "Hunter Auto". Copy the 16-letter code here.
   - **HUNTER_IO_API_KEY**: Go to [Hunter.io](https://hunter.io/), sign up for a free account, click your profile in the top right -> **API**, and copy your API key.
   - **GOOGLE_SHEETS_ID**: Create a Google Sheet. Look at the URL: `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit`. Copy that ID.

## Step 3: Google Sheets API
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a Project.
3. Search for **Google Sheets API** and **Google Drive API** and "Enable" both.
4. Go to **Credentials** -> Create Credentials -> **Service Account**.
5. Once created, click the service account -> **Keys** -> Add Key -> Create new key -> **JSON**.
6. A file will download. Rename it to `credentials.json` and place it inside the `hunter_auto/config/` folder.
7. **Important**: Open the JSON file, find the `client_email`, and **Share your Google Sheet** with that exact email address. Give it "Editor" permissions!

## Step 4: Validate LinkedIn Session (Do this on your Windows machine first)
LinkedIn is heavily protected. The bot needs YOUR real browser session to not get blocked. 
Open a Command Prompt (`cmd`) in your `hunter_auto` folder and run:
*(You must have python installed on your host PC for this single step)*

```cmd
pip install playwright
playwright install chromium
python -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); browser=p.chromium.launch(headless=False); context=browser.new_context(); page=context.new_page(); page.goto('https://www.linkedin.com/login'); print('>>> LOGIN IN THE BROWSER NOW. YOU HAVE 60 SECONDS... <<<'); page.wait_for_timeout(60000); context.storage_state(path='playwright_sessions/state.json'); browser.close(); p.stop()"
```

## Step 5: Launch in Docker (Prod Mode)
Open Command Prompt (`cmd`) in the `hunter_auto` folder and type:
```cmd
docker compose up -d --build
```

**That's it!** The system is running.
- To view the dashboard, keep this AI Studio page open. It connects directly to your local Docker container.
- To stop the system safely, type: `docker compose down`
- To see the logs, type: `docker compose logs -f`
