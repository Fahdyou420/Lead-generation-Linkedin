import requests
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

class TelegramNotifier:
    def notify_human_agent(self, lead, suggested_message=""):
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            print("Telegram config missing.")
            return False
            
        text = f"""🎯 <b>New lead ready for cold call</b>:
        
👤 <b>Name</b>: {lead.get('Name')}
💼 <b>Title</b>: {lead.get('Title')}
🏢 <b>Company</b>: {lead.get('Company')}
📞 <b>Phone</b>: {lead.get('Phone')}
⭐ <b>Score</b>: {lead.get('Score')}/10

<b>AI Notes / Reason</b>: 
{lead.get('Notes')}

<b>Suggested opening</b>: 
"{suggested_message}"
"""
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        }
        
        try:
            r = requests.post(url, json=payload)
            return r.status_code == 200
        except Exception as e:
            print(f"Telegram error: {e}")
            return False
            
    def send_summary(self, stats):
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID: return False
        
        text = f"""📊 <b>Daily Hunter Auto Summary</b>:
Total Leads: {stats.get('total')}
Sent Today: {stats.get('sent_today')}
Meetings: {stats.get('meetings')}
Response Rate: {stats.get('response_rate')}
"""
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"})
