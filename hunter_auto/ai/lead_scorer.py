import os
from ai.ollama_client import OllamaClient

class LeadScorer:
    def __init__(self):
        self.ollama = OllamaClient()
        self.skills_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'knowledge', 'skills.md')
        
    def _get_agent_skills(self):
        if os.path.exists(self.skills_path):
            with open(self.skills_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
        
    def score_lead(self, company_name, category, description=""):
        skills = self._get_agent_skills()
        
        prompt = f"""
        AGENT KNOWLEDGE & SKILLS (Use this for your scoring criteria):
        -------------------------
        {skills}
        -------------------------
        
        TASK:
        Rate this Tunisian company's likelihood of needing B2B telecom packages (phone lines, internet, mobile fleet).
        Company: {company_name}
        Category/Sector: {category}
        Description: {description}
        
        Return ONLY a valid JSON object:
        {{
            "score": <number between 1 and 10>,
            "reason": "<short 1-sentence reason>"
        }}
        """
        
        result = self.ollama.generate_json(prompt)
        score = result.get("score", 5)
        reason = result.get("reason", "Standard business profile")
        
        try:
            score = int(score)
            if score < 1: score = 1
            if score > 10: score = 10
        except:
             score = 3
             
        return score, reason
