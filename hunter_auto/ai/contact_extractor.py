from ai.ai_client import AIClient

class ContactExtractor:
    def __init__(self):
        self.ai = AIClient()
        
    def extract_from_html(self, raw_text):
        if not raw_text or len(raw_text) < 10:
             return []
             
        # truncation to avoid token limit overflow, depending on model size
        truncated_text = raw_text[:4000] 
        
        prompt = f"""
        Extract key personnel (Executives, Managers, Directors, Founders) from the following text scraped from a company's About Us/Team page.
        Text: '{truncated_text}'
        
        Return ONLY a JSON object with this exact structure:
        {{
            "contacts": [
                 {{ "name": "...", "title": "..." }}
            ]
        }}
        If no contacts are found, return {{"contacts": []}}
        """
        
        result = self.ai.generate_json(prompt)
        contacts = result.get("contacts", [])
        
        if not isinstance(contacts, list):
            return []
            
        return [c for c in contacts if isinstance(c, dict) and "name" in c and "title" in c]
