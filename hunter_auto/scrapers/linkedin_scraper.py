import os
import time
import random
from playwright.sync_api import sync_playwright
from config.settings import get_target_sectors, get_target_titles, update_status

class LinkedinScraper:
    def __init__(self):
        self.session_dir = "playwright_sessions"
        
    def scrape(self):
        leads = []
        sectors = get_target_sectors()
        titles = get_target_titles()
        
        update_status(is_scraping=True, current_activity="Initializing LinkedIn scraping session...")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(storage_state=os.path.join(self.session_dir, "state.json")) if os.path.exists(os.path.join(self.session_dir, "state.json")) else browser.new_context()
                page = context.new_page()
                
                for sector in sectors:
                    for title in titles:
                        query = f"{title} {sector} Tunisie"
                        msg = f"LinkedIn: Searching for '{query}'..."
                        print(msg)
                        update_status(current_activity=msg)
                        
                        encoded_query = query.replace(" ", "%20")
                        url = f"https://www.linkedin.com/search/results/people/?keywords={encoded_query}"
                        
                        try:
                            page.goto(url)
                            page.wait_for_timeout(random.randint(5000, 10000))
                            
                            # Verify login
                            if "login" in page.url or "checkpoint" in page.url:
                                 print("LinkedIn session expired or not authenticated. Please run manual login.")
                                 update_status(current_activity="LinkedIn authentication required (session expired)")
                                 return leads
                                 
                            page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
                            page.wait_for_timeout(2000)
                            
                            elements = page.query_selector_all('li.reusable-search__result-container')
                            for el in elements:
                                try:
                                    name_el = el.query_selector('span[aria-hidden="true"]') # usually holds the name cleanly
                                    name = name_el.inner_text().strip() if name_el else ""
                                    
                                    title_el = el.query_selector('div.entity-result__primary-subtitle')
                                    person_title = title_el.inner_text().strip() if title_el else ""
                                    
                                    link_el = el.query_selector('a.app-aware-link')
                                    link = link_el.get_attribute('href') if link_el else ""
                                    link = link.split('?')[0] # clean URL
                                    
                                    if name and "LinkedIn" not in name:
                                        lead_item = {
                                            "Name": name,
                                            "Title": person_title,
                                            "Company": sector, # Guessing sector as company if not explicitly clear
                                            "LinkedIn URL": link,
                                            "Source": "linkedin",
                                            "Category": sector
                                        }
                                        leads.append(lead_item)
                                        print(f"Found on LinkedIn: {name} ({person_title})")
                                        update_status(last_scraped_company=name, last_scraped_source="linkedin", found_lead=lead_item)
                                except Exception as inner_e:
                                    pass
                                    
                                if len(leads) >= 10: # Limit per run to avoid bans
                                    break
                        except Exception as e:
                             print(f"LinkedIn scrape error: {e}")
                        
                        if len(leads) >= 10:
                            break
                    if len(leads) >= 10:
                         break
                         
                context.close()
                browser.close()
        except Exception as outer_e:
            print(f"Fatal LinkedIn scraper error: {outer_e}")
        finally:
            update_status(is_scraping=False, current_activity="Idle")
            
        return leads
