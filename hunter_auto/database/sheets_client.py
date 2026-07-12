import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from config.settings import GOOGLE_CREDENTIALS_PATH, GOOGLE_SHEETS_ID
import os
import json

class SheetsClient:
    def __init__(self):
        self.scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        self.use_fallback = False
        
        # Local paths
        self.local_leads_path = "config/local_leads.json"
        self.local_logs_path = "config/local_logs.json"
        
        # Ensure directories exist
        os.makedirs("config", exist_ok=True)
        
        try:
            if not GOOGLE_CREDENTIALS_PATH or not os.path.exists(GOOGLE_CREDENTIALS_PATH):
                raise FileNotFoundError(f"Credentials file missing at: {GOOGLE_CREDENTIALS_PATH}")
                
            self.creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_PATH, self.scope)
            self.client = gspread.authorize(self.creds)
            self.sheet_id = GOOGLE_SHEETS_ID
            if not self.sheet_id:
                raise ValueError("GOOGLE_SHEETS_ID environment variable is not configured.")
            print("Successfully connected to Google Sheets cloud database.")
        except Exception as e:
            print(f"Warning: Sheets initialization failed: {e}. Falling back to offline/local JSON DB mode.")
            self.use_fallback = True
            self._init_local_db()

    def _init_local_db(self):
        # Initialise local leads DB with beautiful starter mock leads if empty or missing
        if not os.path.exists(self.local_leads_path):
            mock_leads = [
                {
                    "ID": "1",
                    "Company": "Tunisie Telecom",
                    "Name": "Kamel Saidi",
                    "Title": "Directeur Réseaux & B2B",
                    "Phone": "71120120",
                    "Email": "kamel.saidi@tunisietelecom.tn",
                    "LinkedIn URL": "https://linkedin.com/in/kamel-saidi-tt",
                    "Source": "LinkedIn",
                    "Score": "9",
                    "Status": "meeting_booked",
                    "Message Sent": "Bonjour M. Saidi, nous proposons une optimisation intelligente de vos flux de leads B2B...",
                    "Sent At": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Notes": "Intéressé par la démo de notre CRM d'automation."
                },
                {
                    "ID": "2",
                    "Company": "Ooredoo Tunisie",
                    "Name": "Amira Ben Romdhane",
                    "Title": "Gérante Achats IT",
                    "Phone": "71111111",
                    "Email": "amira.br@ooredoo.tn",
                    "LinkedIn URL": "https://linkedin.com/in/amira-br-ooredoo",
                    "Source": "Google Maps",
                    "Score": "8",
                    "Status": "pending",
                    "Message Sent": "Bonjour Mme. Amira, intéressée par nos services?",
                    "Sent At": "",
                    "Notes": "A recontacter d'ici mardi prochain."
                },
                {
                    "ID": "3",
                    "Company": "SOPAT",
                    "Name": "Youssef Chahed",
                    "Title": "Directeur Général",
                    "Phone": "73302400",
                    "Email": "y.chahed@sopat.com.tn",
                    "LinkedIn URL": "",
                    "Source": "Google Maps",
                    "Score": "7",
                    "Status": "not_interested",
                    "Message Sent": "Bonjour, SOPAT souhaite-t-il moderniser ses outils de prospection B2B?",
                    "Sent At": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Notes": "Pas intéressé pour le moment."
                }
            ]
            try:
                with open(self.local_leads_path, "w", encoding="utf-8") as f:
                    json.dump(mock_leads, f, indent=4, ensure_ascii=False)
            except Exception as ex:
                print(f"Error seeding local leads: {ex}")

        if not os.path.exists(self.local_logs_path):
            mock_logs = [
                {
                    "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Action": "System Init",
                    "Lead ID": "",
                    "Company": "",
                    "Status": "Active",
                    "Details": "Hunter B2B Lead Gen OS started successfully."
                }
            ]
            try:
                with open(self.local_logs_path, "w", encoding="utf-8") as f:
                    json.dump(mock_logs, f, indent=4, ensure_ascii=False)
            except Exception as ex:
                print(f"Error seeding local logs: {ex}")

    def _read_local_leads(self):
        if not os.path.exists(self.local_leads_path):
            return []
        try:
            with open(self.local_leads_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading local leads: {e}")
            return []

    def _write_local_leads(self, leads):
        try:
            with open(self.local_leads_path, "w", encoding="utf-8") as f:
                json.dump(leads, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error writing local leads: {e}")
            return False

    def _read_local_logs(self):
        if not os.path.exists(self.local_logs_path):
            return []
        try:
            with open(self.local_logs_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading local logs: {e}")
            return []

    def _write_local_logs(self, logs):
        try:
            with open(self.local_logs_path, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error writing local logs: {e}")
            return False
        
    def _get_or_create_sheet(self, sheet_name, headers):
        if self.use_fallback:
            return None
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

    def _get_records_safe(self, sheet, expected_headers):
        if self.use_fallback or not sheet:
            return []
        try:
            values = sheet.get_all_values()
            if not values:
                sheet.append_row(expected_headers)
                return []
            
            headers = values[0]
            non_empty_headers = [h for h in headers if h.strip()]
            if len(set(non_empty_headers)) != len(non_empty_headers) or len(non_empty_headers) == 0:
                for col_idx, val in enumerate(expected_headers, 1):
                    sheet.update_cell(1, col_idx, val)
                headers = expected_headers
                values = sheet.get_all_values()
            
            records = []
            for row in values[1:]:
                record = {}
                for idx, header in enumerate(headers):
                    if header:
                        record[header] = row[idx] if idx < len(row) else ""
                records.append(record)
            return records
        except Exception as e:
            print(f"Error reading sheets records safely: {e}")
            return []

    def get_leads_sheet(self):
        if self.use_fallback:
            return None
        headers = ["ID", "Company", "Name", "Title", "Phone", "Email", "LinkedIn URL", "Source", "Score", "Status", "Message Sent", "Sent At", "Notes"]
        return self._get_or_create_sheet("Hunter_Auto_Leads", headers)
        
    def get_logs_sheet(self):
        if self.use_fallback:
            return None
        headers = ["Timestamp", "Action", "Lead ID", "Company", "Status", "Details"]
        return self._get_or_create_sheet("Hunter_Auto_Log", headers)

    def log_action(self, action, lead_id="", company="", status="", details=""):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.use_fallback:
            logs = self._read_local_logs()
            logs.append({
                "Timestamp": timestamp,
                "Action": action,
                "Lead ID": str(lead_id),
                "Company": company,
                "Status": status,
                "Details": details
            })
            self._write_local_logs(logs)
            return
            
        sheet = self.get_logs_sheet()
        if sheet:
            try:
                sheet.append_row([timestamp, action, lead_id, company, status, details])
            except Exception as e:
                print(f"Failed to append to log sheet: {e}")

    def lead_exists(self, linkedin_url=None, phone=None, company=None):
        if self.use_fallback:
            records = self._read_local_leads()
            for r in records:
                if linkedin_url and r.get("LinkedIn URL") == linkedin_url:
                    return True
                if phone and str(r.get("Phone")) == str(phone):
                    return True
                if company and r.get("Company") == company and not linkedin_url and not phone:
                    return True
            return False

        sheet = self.get_leads_sheet()
        if not sheet: return False
        
        headers = ["ID", "Company", "Name", "Title", "Phone", "Email", "LinkedIn URL", "Source", "Score", "Status", "Message Sent", "Sent At", "Notes"]
        records = self._get_records_safe(sheet, headers)
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
            
        if self.use_fallback:
            leads = self._read_local_leads()
            row_id = str(len(leads) + 1)
            new_lead = {
                "ID": row_id,
                "Company": lead_data.get("Company", ""),
                "Name": lead_data.get("Name", ""),
                "Title": lead_data.get("Title", ""),
                "Phone": str(lead_data.get("Phone", "")),
                "Email": lead_data.get("Email", ""),
                "LinkedIn URL": lead_data.get("LinkedIn URL", ""),
                "Source": lead_data.get("Source", ""),
                "Score": str(lead_data.get("Score", "")),
                "Status": lead_data.get("Status", "pending"),
                "Message Sent": lead_data.get("Message Sent", ""),
                "Sent At": "",
                "Notes": lead_data.get("Notes", "")
            }
            leads.append(new_lead)
            self._write_local_leads(leads)
            self.log_action("New Lead Added", lead_id=row_id, company=lead_data.get("Company"), status="pending")
            return True

        sheet = self.get_leads_sheet()
        if not sheet: return False
        
        try:
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
        except Exception as e:
            print(f"Failed to append lead to sheet: {e}")
            return False

    def get_all_leads_records(self):
        if self.use_fallback:
            return self._read_local_leads()
            
        sheet = self.get_leads_sheet()
        if not sheet: return []
        headers = ["ID", "Company", "Name", "Title", "Phone", "Email", "LinkedIn URL", "Source", "Score", "Status", "Message Sent", "Sent At", "Notes"]
        return self._get_records_safe(sheet, headers)

    def get_pending_leads(self):
        if self.use_fallback:
            records = self._read_local_leads()
            return [r for r in records if r.get("Status") == "pending"]

        sheet = self.get_leads_sheet()
        if not sheet: return []
        headers = ["ID", "Company", "Name", "Title", "Phone", "Email", "LinkedIn URL", "Source", "Score", "Status", "Message Sent", "Sent At", "Notes"]
        records = self._get_records_safe(sheet, headers)
        return [r for r in records if r.get("Status") == "pending"]

    def update_lead_status(self, lead_id, status, message_sent="", notes="", sent_at=""):
        if self.use_fallback:
            leads = self._read_local_leads()
            updated = False
            for r in leads:
                if str(r.get("ID")) == str(lead_id):
                    if status: r["Status"] = status
                    if message_sent: r["Message Sent"] = message_sent
                    if sent_at: r["Sent At"] = sent_at
                    if notes:
                        existing = r.get("Notes") or ""
                        r["Notes"] = (existing + " | " + notes).strip(" | ")
                    updated = True
                    break
            if updated:
                self._write_local_leads(leads)
                self.log_action("Lead Updated", lead_id=lead_id, status=status, details=f"Status to {status}")
                return True
            return False

        sheet = self.get_leads_sheet()
        if not sheet: return False
        
        try:
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
        except Exception as e:
            print(f"Failed to update lead sheet: {e}")
        return False

    def get_stats(self):
        records = []
        if self.use_fallback:
            records = self._read_local_leads()
        else:
            sheet = self.get_leads_sheet()
            if sheet:
                headers = ["ID", "Company", "Name", "Title", "Phone", "Email", "LinkedIn URL", "Source", "Score", "Status", "Message Sent", "Sent At", "Notes"]
                records = self._get_records_safe(sheet, headers)
                
        if not records:
            return {"total": 0, "sent_today": 0, "meetings": 0, "response_rate": "0%"}
            
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
