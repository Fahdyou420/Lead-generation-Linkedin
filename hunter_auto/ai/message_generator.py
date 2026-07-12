import os
from ai.ai_client import AIClient

class MessageGenerator:
    def __init__(self):
        self.ai = AIClient()
        self.skills_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'knowledge', 'skills.md')
        
    def _get_agent_skills(self):
        if os.path.exists(self.skills_path):
            with open(self.skills_path, 'r', encoding='utf-8') as f:
                return f.read()
        return "No specific skills provided."
        
    def generate_messages(self, name, title, company):
        skills = self._get_agent_skills()
        
        prompt = f"""
        AGENT KNOWLEDGE & SKILLS:
        -------------------------
        {skills}
        -------------------------
        
        TASK:
        Generate a SHORT (max 3 sentences), friendly, non-salesy outreach message in French, Arabic, and English 
        for an Ooredoo B2B sales agent reaching out to a prospect.
        
        Prospect details:
        Name: {name}
        Title: {title}
        Company: {company}
        
        Rules:
        - Read and apply the guidelines from the AGENT KNOWLEDGE & SKILLS above.
        - Ask ONLY for a 15-minute call or meeting to present our bespoke business telecom offers.
        - The tone should be highly professional yet conversational.
        - Sign as: Ooredoo Business Team.
        
        Return ONLY a valid JSON object:
        {{
            "fr": "<French message>",
            "ar": "<Arabic message>",
            "en": "<English message>",
            "subject": "<A catchy professional French subject line for email (max 6 words)>"
        }}
        """
        
        result = self.ai.generate_json(prompt)
        
        default_fr = f"Bonjour {name}, je vous contacte au nom d'Ooredoo Business. Nous proposons des offres B2B sur-mesure pour les entreprises tunisiennes comme {company}. Seriez-vous disponible pour un court appel pour vous les présenter ? Bien à vous, Ooredoo Business Team."
        
        return {
            "fr": result.get("fr", default_fr),
            "ar": result.get("ar", default_fr),  # Fallback just in case
            "en": result.get("en", default_fr),
            "subject": result.get("subject", "Optimisation de vos outils de communication")
        }
