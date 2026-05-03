import time
import random
from playwright.sync_api import sync_playwright
from config.settings import TARGET_SECTORS

class GoogleMapsScraper:
    def scrape(self, city="Tunis"):
        leads = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            for sector in TARGET_SECTORS:
                query = f"entreprises {sector} {city}"
                print(f"Scraping Maps for: {query}")
                page.goto("https://www.google.com/maps")
                
                # Wait for search box
                page.wait_for_selector('input#searchboxinput')
                page.fill('input#searchboxinput', query)
                page.keyboard.press('Enter')
                
                # Wait for results to load
                page.wait_for_timeout(5000)
                
                # Google Maps uses a feed container
                feed_selector = 'div[role="feed"]'
               
                try:
                    for _ in range(3): # Scroll a few times
                        page.hover(feed_selector)
                        page.mouse.wheel(0, 1000)
                        page.wait_for_timeout(random.randint(3000, 8000))
                        
                    # Extract entities
                    elements = page.query_selector_all('div.Nv254') # Often the wrapper for elements, this changes per Google updates
                    # Fallback generic parsing
                    if not elements:
                        elements = page.query_selector_all('a[href*="google.com/maps/place/"]')

                    for el in elements[:10]: # Limit for demo to 10 per sector
                        try:
                           name = el.get_attribute('aria-label')
                           if not name:
                               name = el.inner_text().split('\n')[0]
                               
                           link = el.get_attribute('href')
                           
                           # We can click each item to get exact details, but keeping it simple to avoid bans
                           leads.append({
                               "Company": name,
                               "Source": "google_maps",
                               "Category": sector,
                               "Link": link
                           })
                        except:
                            pass
                except Exception as e:
                    print(f"Error scraping sector {sector}: {e}")
                    
                page.wait_for_timeout(random.randint(2000, 5000))
                
            browser.close()
        
        return leads
