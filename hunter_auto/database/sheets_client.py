import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from config.settings import GOOGLE_CREDENTIALS_PATH, GOOGLE_SHEETS_ID
import os

class SheetsClient:
    def __init__(self):
        self.scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_PATH, self.scope)
        self.client = gspread.authorize(self.creds)
        self.sheet_id = GOOGLE_SHEETS_ID
        
    def _get_or_create_sheet(self, sheet_name, headers):
        try:
            workbook = self.client.open_by_key(self.sheet_id)
            try:
                sheet = workbook.worksheet(sheet_name)
            except gspread.exceptions.WorksheetNotFound:
                sheet = workbook.add_worksheet(title=sheet_name, rows="1000", cols=str(len(headers)))
                sheet.append_row(headers)
            return sheet
        except Exception as e:
            print(f"Error accessing Google Sheets: {e}")
            return None

    def get_leads_sheet(self):
        headers = ["ID", "Company", "Name", "Title", "Phone", "Email", "LinkedIn URL", "Source", "Score", "Status", "Message Sent", "Sent At", "Notes"]
        return self._get_or_create_sheet("Hunter_Auto_Leads", headers)
        
    def get_logs_sheet(self):
        headers = ["Timestamp", "Action", "Lead ID", "Company", "Status", "Details"]
        return self._get_or_create_sheet("Hunter_Auto_Log", headers)

    def log_action(self, action, lead_id="", company="", status="", details=""):
        sheet = self.get_logs_sheet()
        if sheet:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row([timestamp, action, lead_id, company, status, details])

    def lead_exists(self, linkedin_url=None, phone=None, company=None):
        sheet = self.get_leads_sheet()
        if not sheet: return False
        
        records = sheet.get_all_records()
        for r in records:
            if linkedin_url and r.get("LinkedIn URL") == linkedin_url:
                return True
            if phone and str(r.get("Phone")) == str(phone):
                return True
            if company and r.get("Company") == company and not linkedin_url and not phone:
                 return True
        return False

    def add_lead(self, lead_data):
        if self.lead_exists(linkedin_url=lead_data.get("LinkedIn URL"), phone=lead_data.get("Phone"), company=lead_data.get("Company")):
            return False
            
        sheet = self.get_leads_sheet()
        if not sheet: return False
        
        row_id = len(sheet.get_all_values())
        row = [
            row_id,
            lead_data.get("Company", ""),
            lead_data.get("Name", ""),
            lead_data.get("Title", ""),
            str(lead_data.get("Phone", "")),
            lead_data.get("Email", ""),
            lead_data.get("LinkedIn URL", ""),
            lead_data.get("Source", ""),
            lead_data.get("Score", ""),
            lead_data.get("Status", "pending"),
            lead_data.get("Message Sent", ""),
            "", # Sent At
            lead_data.get("Notes", "")
        ]
        sheet.append_row(row)
        self.log_action("New Lead Added", lead_id=row_id, company=lead_data.get("Company"), status="pending")
        return True

    def get_pending_leads(self):
        sheet = self.get_leads_sheet()
        if not sheet: return []
        records = sheet.get_all_records()
        return [r for r in records if r.get("Status") == "pending"]

    def update_lead_status(self, lead_id, status, message_sent="", notes="", sent_at=""):
        sheet = self.get_leads_sheet()
        if not sheet: return False
        
        # Find cell by ID
        cell = sheet.find(str(lead_id), in_column=1)
        if cell:
            row_num = cell.row
            if status: sheet.update_cell(row_num, 10, status)
            if message_sent: sheet.update_cell(row_num, 11, message_sent)
            if sent_at: sheet.update_cell(row_num, 12, sent_at)
            if notes:
                existing_notes = sheet.cell(row_num, 13).value or ""
                sheet.update_cell(row_num, 13, existing_notes + " | " + notes)
            self.log_action("Lead Updated", lead_id=lead_id, status=status, details=f"Status to {status}")
            return True
        return False

    def get_stats(self):
        sheet = self.get_leads_sheet()
        if not sheet: return {"total": 0, "sent_today": 0, "meetings": 0, "response_rate": 0}
        
        records = sheet.get_all_records()
        total = len(records)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        sent_today = len([r for r in records if today in str(r.get("Sent At", ""))])
        meetings = len([r for r in records if r.get("Status") == "meeting_booked"])
        responded = len([r for r in records if r.get("Status") in ["responded", "meeting_booked", "not_interested"]])
        
        outreached = len([r for r in records if r.get("Status") not in ["pending", "phone_handoff"]])
        rate = round((responded / outreached) * 100, 1) if outreached > 0 else 0
        
        return {
            "total": total,
            "sent_today": sent_today,
            "meetings": meetings,
            "response_rate": f"{rate}%"
        }
