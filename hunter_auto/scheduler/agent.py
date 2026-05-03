from apscheduler.schedulers.background import BackgroundScheduler
import pytz
import datetime
from config.settings import TIMEZONE
from scrapers.google_maps import GoogleMapsScraper
from scrapers.web_enricher import WebEnricher
from scrapers.linkedin_scraper import LinkedinScraper
from ai.contact_extractor import ContactExtractor
from ai.lead_scorer import LeadScorer
from ai.message_generator import MessageGenerator
from database.sheets_client import SheetsClient
from outreach.router import Router
from outreach.telegram_notifier import TelegramNotifier
import random
import json

class HunterAgent:
    def __init__(self):
        tz = pytz.timezone(TIMEZONE)
        self.scheduler = BackgroundScheduler(timezone=tz)
        self.db = SheetsClient()
        self.router = Router()
        
    def start(self):
        # Job 1 - Scrape 24/7 every 2 hours
        self.scheduler.add_job(self.scrape_job, 'interval', hours=2, id='scrape_job')
        
        # Job 2 - Enrich 24/7 every 4 hours
        self.scheduler.add_job(self.enrich_job, 'interval', hours=4, id='enrich_job')
        
        # Job 3 - Outreach ONLY at specific TN business hours
        for hour in [8, 10, 14, 16]:
             self.scheduler.add_job(self.outreach_job, 'cron', hour=hour, minute=0, id=f'outreach_job_{hour}')
             
        # Job 4 - Daily Stats to Telegram
        self.scheduler.add_job(self.stats_job, 'cron', hour=9, minute=0, id='stats_job')
        
        self.scheduler.start()
        print("Hunter Auto Agent Scheduled & Running.")

    def scrape_job(self):
        print(f"[{datetime.datetime.now()}] Running scrape job...")
        
        # Google Maps
        maps = GoogleMapsScraper()
        leads = maps.scrape()
        
        enricher = WebEnricher()
        for lead in leads:
             info = enricher.enrich(lead.get("Company"), lead.get("Link"))
             lead["Phone"] = info.get("Phone", "")
             lead["Email"] = info.get("Email", "")
             lead["Notes"] = info.get("About_Text", "")[:200]
             self.db.add_lead(lead)
             
    def enrich_job(self):
        print(f"[{datetime.datetime.now()}] Running enrich job...")
        # 1. Scrape LinkedIn Directly
        li = LinkedinScraper()
        leads = li.scrape()
        for lead in leads:
            self.db.add_lead(lead)
            
        # 2. Score pending leads and generate messages
        pending = self.db.get_pending_leads()
        scorer = LeadScorer()
        msg_gen = MessageGenerator()
        
        for lead in pending[:20]: # Process in batches
            if not lead.get("Score"):
                 score, reason = scorer.score_lead(lead.get("Company"), lead.get("Source"), lead.get("Notes"))
                 # Just update notes temporarily, we'll do full update next
                 
                 messages = msg_gen.generate_messages(
                     lead.get("Name", "Responsable"), 
                     lead.get("Title", ""), 
                     lead.get("Company", "")
                 )
                 
                 # Using status "scored" internally before router takes over
                 self.db.update_lead_status(
                     lead.get("ID"), 
                     status="pending", 
                     message_sent=json.dumps(messages),
                     notes=reason
                 )

    def outreach_job(self):
        print(f"[{datetime.datetime.now()}] Running outreach job...")
        pending = self.db.get_pending_leads()
        
        # Filter for those that have been scored
        ready = [l for l in pending if l.get("Message Sent")]
        
        for lead in ready[:10]: # Max 10 per slot
            self.router.process_lead(lead)

    def stats_job(self):
        print(f"[{datetime.datetime.now()}] Running stats job...")
        stats = self.db.get_stats()
        tg = TelegramNotifier()
        tg.send_summary(stats)
