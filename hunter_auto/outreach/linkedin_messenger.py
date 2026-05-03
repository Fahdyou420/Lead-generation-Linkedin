import os
import time
import random
from playwright.sync_api import sync_playwright

class LinkedinMessenger:
    def __init__(self):
        self.session_dir = "playwright_sessions"
        
    def send_message(self, profile_url, message_text):
        success = False
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(storage_state=os.path.join(self.session_dir, "state.json")) if os.path.exists(os.path.join(self.session_dir, "state.json")) else browser.new_context()
            page = context.new_page()
            
            try:
                page.goto(profile_url)
                page.wait_for_timeout(random.randint(45000, 120000)) # Random delays 45-120s to avoid bans
                
                # Check if connected
                # Typically, there's a "Message" button if connected, or "Connect" if not.
                # Playwright selectors are brittle for LinkedIn, simplified here:
                
                try:
                    # Look for Message button first
                    message_btn = page.locator('button:has-text("Message")').first
                    if message_btn and message_btn.is_visible():
                        message_btn.click()
                        page.wait_for_timeout(2000)
                        # Type message in the chat box
                        page.fill('div.msg-form__contenteditable', message_text)
                        page.wait_for_timeout(1000)
                        page.click('button.msg-form__send-button')
                        success = True
                    else:
                        # Find Connect button
                        connect_btn = page.locator('button:-soup-contains("Connect")').first
                        if connect_btn and connect_btn.is_visible():
                             connect_btn.click()
                             page.wait_for_timeout(1500)
                             page.click('button[aria-label="Add a note"]')
                             page.wait_for_timeout(1000)
                             # Note limits to 300 chars
                             short_msg = message_text[:290] + "..." if len(message_text) > 300 else message_text
                             page.fill('textarea[name="message"]', short_msg)
                             page.wait_for_timeout(1000)
                             page.click('button[aria-label="Send now"]')
                             success = True
                except Exception as e:
                     print(f"Error interacting with {profile_url}: {e}")
            except Exception as e:
                print(f"Failed to load {profile_url}: {e}")
                
            context.close()
            browser.close()
            
        return success
