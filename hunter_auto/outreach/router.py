from outreach.email_sender import EmailSender
from outreach.telegram_notifier import TelegramNotifier
from outreach.linkedin_messenger import LinkedinMessenger
from database.sheets_client import SheetsClient
import datetime

class Router:
    def __init__(self):
        self.email_sender = EmailSender()
        self.telegram = TelegramNotifier()
        self.linkedin = LinkedinMessenger()
        self.db = SheetsClient()

    def process_lead(self, lead):
        # lead is a dict representing a row from Google Sheets
        lead_id = lead.get("ID")
        name = lead.get("Name", "Professionnel")
        phone = str(lead.get("Phone", "")).strip()
        email = str(lead.get("Email", "")).strip()
        linkedin_url = str(lead.get("LinkedIn URL", "")).strip()
        messages = lead.get("Message Sent", "{}") # Ideally JSON string of generated messages
        
        try:
             import json
             msg_data = json.loads(messages)
             content_fr = msg_data.get("fr")
             subject = msg_data.get("subject", "Opportunité B2B")
        except:
             content_fr = getattr(lead, "Message Sent", "Bonjour, pouvons-nous fixer un rdv?")
             subject = "Ooredoo Business"

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Logic
        if phone:
            self.telegram.notify_human_agent(lead, content_fr)
            self.db.update_lead_status(lead_id, "phone_handoff", notes="Sent to Telegram")
        elif email:
            success = self.email_sender.send(email, subject, content_fr)
            if success:
                self.db.update_lead_status(lead_id, "email_sent", content_fr, sent_at=now)
            else:
                 self.db.update_lead_status(lead_id, "pending", notes="Email failed")
            
            # Optionally also send LinkedIn if available
            if linkedin_url:
                 # Normally queued separately to respect rate limits
                 pass
        elif linkedin_url:
            success = self.linkedin.send_message(linkedin_url, content_fr)
            if success:
                 self.db.update_lead_status(lead_id, "linkedin_sent", content_fr, sent_at=now)
            else:
                 self.db.update_lead_status(lead_id, "pending", notes="LinkedIn failed")
        else:
            self.db.update_lead_status(lead_id, "missing_contact", notes="No phone, email, or LinkedIn")
