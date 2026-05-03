import requests
import re
from bs4 import BeautifulSoup
from config.settings import HUNTER_IO_API_KEY
import time

class WebEnricher:
    def enrich(self, company_name, website=None):
        info = {
            "Phone": "",
            "Email": "",
            "About_Text": ""
        }
        
        # 1. Fallback heuristic: Try to find website if not given (Basic DuckDuckGo or skip)
        if not website:
            # Not implemented complex search to respect simplicity, but one could use a free search provider
            return info
            
        try:
             # Basic scraping
             headers = {'User-Agent': 'Mozilla/5.0'}
             resp = requests.get(website, headers=headers, timeout=10)
             soup = BeautifulSoup(resp.content, "html.parser")
             
             # Extract text for contact extractor
             texts = soup.stripped_strings
             full_text = " ".join(texts)
             
             # Look for emails
             emails = re.findall(r'[a-zA-Z0-9.\-+_]+@[a-zA-Z0-9.\-+_]+\.[a-zA-Z]+', full_text)
             emails = [e for e in emails if not e.endswith(('.png', '.gif', '.jpg', '.jpeg', '.webp'))]
             if emails:
                 info["Email"] = emails[0]
                 
             # Look for Tunisian phone numbers (+216 20 000 000, 20000000 etc.)
             phones = re.findall(r'(?:\+216\s*)?[234579]\d{1}\s*\d{3}\s*\d{3}', full_text)
             # Basic cleanup
             clean_phones = [re.sub(r'\s+', '', p) for p in phones]
             if clean_phones:
                 # Prefer the first one that looks right
                 info["Phone"] = clean_phones[0]
                 
             info["About_Text"] = " ".join(full_text.split()[:500]) # First 500 words
                 
        except Exception as e:
             print(f"Scraping failed for {website}: {e}")
             
        # Hunter.io fallback
        if not info["Email"] and HUNTER_IO_API_KEY and website:
            domain = website.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
            try:
                h_url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={HUNTER_IO_API_KEY}"
                h_resp = requests.get(h_url).json()
                if "data" in h_resp and h_resp["data"]["emails"]:
                    info["Email"] = h_resp["data"]["emails"][0]["value"]
            except:
                pass
                
        return info
