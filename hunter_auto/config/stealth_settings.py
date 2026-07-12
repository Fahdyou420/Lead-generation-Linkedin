# LinkedIn Stealth & Safety Settings

# 1. BRAKING SYSTEM (Rate Limits)
# LinkedIn detects bots by their speed. These limits keep you under the radar.
MAX_PROFILE_VIEWS_PER_DAY = 50 
MAX_SEARCHES_PER_DAY = 30
MIN_SECONDS_BETWEEN_ACTIONS = 15
MAX_SECONDS_BETWEEN_ACTIONS = 60

# 2. HUMAN BEHAVIOR SIMULATION
# These settings make Playwright act like a real user.
SCROLL_SPEED_RANGE = (200, 800)  # Random pixels per scroll
MOUSE_MOVE_JITTER = True        # Adds small "hand shakes" to movements
RANDOM_PAUSE_ON_LOAD = (2, 5)   # Pause before scraping to simulate reading

# 3. TECHNICAL STEALTH
# Hides the "Automated Browser" flag from LinkedIn's scripts.
STEALTH_MODE_ENABLED = True     # Uses playwright-stealth
CUSTOM_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"

# 4. SESSION PERSISTENCE
# We reuse your existing browser cookies so you don't have to log in every time.
# WARNING: If you log in from a different IP (e.g. VPN) while this is running, 
# you might get a "Suspicious Login" warning.
USE_PERSISTENT_CONTEXT = True
SESSION_STORAGE_PATH = "./playwright_sessions"
