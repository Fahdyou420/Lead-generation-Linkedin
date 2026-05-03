from ai.ollama_client import OllamaClient

class LeadScorer:
    def __init__(self):
        self.ollama = OllamaClient()
        
    def score_lead(self, company_name, category, description=""):
        prompt = f"""
        Rate this Tunisian company's likelihood of needing B2B telecom packages (phone lines, internet, mobile fleet).
        Company: {company_name}
        Category/Sector: {category}
        Description: {description}
        
        High score (8-10) = large company, intensive IT/communications needs (e.g. IT, Call centers, Logistics, large retail).
        Medium score (4-7) = normal business (e.g. standard agency, small hotel).
        Low score (1-3) = micro-business, kiosk, unlikely to need B2B fleet.
        
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
