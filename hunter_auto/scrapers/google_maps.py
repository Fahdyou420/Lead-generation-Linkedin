import time
import random
from playwright.sync_api import sync_playwright
from config.settings import get_target_sectors, get_target_cities, update_status

class GoogleMapsScraper:
    def scrape(self, city=None):
        leads = []
        sectors = get_target_sectors()
        cities = [city] if city else get_target_cities()
        
        update_status(is_scraping=True, current_activity="Initializing Google Maps scraping session...")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                for c in cities:
                    for sector in sectors:
                        query = f"entreprises {sector} {c}"
                        msg = f"Google Maps: Scraping {sector} in {c}..."
                        print(msg)
                        update_status(current_activity=msg)
                        
                        try:
                            page.goto("https://www.google.com/maps")
                            
                            # Wait for search box
                            page.wait_for_selector('input#searchboxinput')
                            page.fill('input#searchboxinput', query)
                            page.keyboard.press('Enter')
                            
                            # Wait for results to load
                            page.wait_for_timeout(5000)
                            
                            # Google Maps uses a feed container
                            feed_selector = 'div[role="feed"]'
                           
                            for _ in range(3): # Scroll a few times
                                try:
                                    page.hover(feed_selector)
                                    page.mouse.wheel(0, 1000)
                                except:
                                    pass
                                page.wait_for_timeout(random.randint(1500, 3000))
                                
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
                                   
                                   lead_item = {
                                       "Company": name,
                                       "Source": "google_maps",
                                       "Category": sector,
                                       "Link": link
                                   }
                                   leads.append(lead_item)
                                   print(f"Found on Maps: {name}")
                                   update_status(last_scraped_company=name, last_scraped_source="google_maps", found_lead=lead_item)
                                except Exception as inner_e:
                                    pass
                        except Exception as e:
                            print(f"Error scraping sector {sector} in {c}: {e}")
                            
                        page.wait_for_timeout(random.randint(2000, 5000))
                        
                browser.close()
        except Exception as outer_e:
            print(f"Fatal Google Maps scraping error: {outer_e}")
        finally:
            update_status(is_scraping=False, current_activity="Idle")
        
        return leads
