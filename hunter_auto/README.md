# Hunter Auto 1.0 - Dummy-Proof Prod Setup Guide 🚀

Since you already have Docker and Ollama running on your Windows machine, the setup is much simpler! We've made the system use the models you already have downloaded.

## Step 1: Export & Unzip the Code
1. Click the ⚙️ **Settings** gear in the top right of this AI Studio interface.
2. Select **Download ZIP**.
3. Extract the ZIP file in your Windows PC (e.g. `C:\Users\user\Desktop\hunter_auto`).

## Step 2: Configure Secrets
1. Inside the `hunter_auto` folder, you will see a file named `.env.example`.
2. **Rename** it to `.env` (just `.env`, without `.example`).
3. Open `.env` in a text editor (like Notepad).
4. Notice that we already set `OLLAMA_HOST=http://host.docker.internal:11434` (this tells Docker to use your Windows Ollama) and `OLLAMA_MODEL=qwen-coder:latest` (since you already downloaded it).
5. Fill in the rest of the file:
   - `GOOGLE_SHEETS_ID`: Create a Google Sheet. Look at the URL: `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit`. Copy that ID.
   - `GMAIL_ADDRESS` / `GMAIL_APP_PASSWORD`: For email. You must create an App Password in your Google Account security settings (2FA must be on).
   - `TELEGRAM_BOT_TOKEN`: Create a bot via `@BotFather` on Telegram.
   - `TELEGRAM_CHAT_ID`: `2037668278` (Already extracted from your JSON!)
   - `HUNTER_IO_API_KEY`: Go to [Hunter.io](https://hunter.io/), sign up for a free account, click your profile in the top right -> **API**, and copy your API key (gives you 25 free email searches/month).

## Step 3: Google Sheets API
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a Project.
3. Search for **Google Sheets API** and **Google Drive API** and "Enable" both.
4. Go to **Credentials** -> Create Credentials -> **Service Account**.
5. Once created, click the service account -> **Keys** -> Add Key -> Create new key -> **JSON**.
6. A file will download. Rename it to `credentials.json` and place it inside the `hunter_auto/config/` folder.
7. **Important**: Open the JSON file, find the `client_email`, and **Share your Google Sheet** with that email exactly as you would share it with a regular person. Give it "Editor" permissions!

## Step 4: Validate LinkedIn Session (Do this on your Windows machine first)
LinkedIn is heavily protected. The bot needs YOUR real browser session to not get blocked. 
Open a Command Prompt (`cmd`) in your `hunter_auto` folder and run:
**(You must have python installed on your host PC for this single step)**

```cmd
pip install playwright
playwright install chromium
python -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); browser=p.chromium.launch(headless=False); context=browser.new_context(); page=context.new_page(); page.goto('https://www.linkedin.com/login'); print('>>> LOGIN OFFICIALLY IN THE POPUP BROWSER NOW. YOU HAVE 60 SECONDS... <<<'); page.wait_for_timeout(60000); context.storage_state(path='playwright_sessions/state.json'); browser.close(); p.stop()"
```
*A browser will pop up. Login to LinkedIn. After 60 seconds it will close and save `playwright_sessions/state.json`. Do not close it early!*

## Step 5: Launch in Docker (Prod Mode)
Now the easy part. Because we removed Ollama from the docker compose (since you have it), we just run the app!

Open Command Prompt (`cmd`) in the `hunter_auto` folder and type:
```cmd
docker compose up -d --build
```

**That's it!** The system is running.
- To view the dashboard, open your browser to `http://localhost:5000`
- To stop the system safely, type: `docker compose down`
- To see the logs and make sure it's scraping, type: `docker compose logs -f`
