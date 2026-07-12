import requests
import json
import time
from config.settings import NOUS_API_KEY, NOUS_MODEL, NOUS_API_BASE, GEMINI_API_KEY, GEMINI_MODEL

class AIClient:
    def __init__(self):
        self.nous_key = NOUS_API_KEY
        self.nous_model = NOUS_MODEL
        self.nous_base = NOUS_API_BASE
        
        self.gemini_key = GEMINI_API_KEY
        self.gemini_model = GEMINI_MODEL

    def _log_call(self, provider, model, prompt, response, error=None):
        try:
            with open("ai_debug.log", "a", encoding="utf-8") as f:
                ts = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n[{ts}] --- {provider.upper()} CALL ({model}) ---\n")
                f.write(f"PROMPT: {prompt[:300]}...\n")
                if error:
                    f.write(f"ERROR: {error}\n")
                else:
                    f.write(f"RESPONSE: {response[:300]}...\n")
        except:
             pass

    def _call_nous(self, prompt, require_json=False):
        if not self.nous_key:
            raise ValueError("NOUS_API_KEY is not configured")
            
        url = f"{self.nous_base.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.nous_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.nous_model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }
        
        if require_json:
            payload["response_format"] = {"type": "json_object"}

        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    def _call_gemini(self, prompt, require_json=False):
        if not self.gemini_key:
            raise ValueError("GEMINI_API_KEY is not configured")
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent?key={self.gemini_key}"
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }
        
        if require_json:
            payload["generationConfig"] = {
                "responseMimeType": "application/json"
            }
            
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        # Extract content from v1beta API format
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()

    def generate(self, prompt, retries=3):
        # 1. Try Nous Research
        if self.nous_key:
            for attempt in range(retries):
                try:
                    text = self._call_nous(prompt)
                    self._log_call("Nous", self.nous_model, prompt, text)
                    return text
                except Exception as e:
                    self._log_call("Nous", self.nous_model, prompt, "", str(e))
                    print(f"Nous Portal generation failed (attempt {attempt+1}/{retries}): {e}")
                    if attempt < retries - 1:
                        time.sleep(2)
                        
        # 2. Try Fallback Gemini
        if self.gemini_key:
            print("Falling back to Google Gemini...")
            for attempt in range(retries):
                try:
                    text = self._call_gemini(prompt)
                    self._log_call("Gemini", self.gemini_model, prompt, text)
                    return text
                except Exception as e:
                    self._log_call("Gemini", self.gemini_model, prompt, "", str(e))
                    print(f"Gemini generation fallback failed (attempt {attempt+1}/{retries}): {e}")
                    if attempt < retries - 1:
                        time.sleep(2)
                        
        raise RuntimeError("Both primary and fallback AI generation attempts failed or were unconfigured.")

    def generate_json(self, prompt, retries=3):
        # 1. Try Nous Research
        if self.nous_key:
            for attempt in range(retries):
                try:
                    text = self._call_nous(prompt, require_json=True)
                    self._log_call("Nous-JSON", self.nous_model, prompt, text)
                    return self._clean_and_load_json(text)
                except Exception as e:
                    self._log_call("Nous-JSON", self.nous_model, prompt, "", str(e))
                    print(f"Nous Portal JSON generation failed (attempt {attempt+1}/{retries}): {e}")
                    if attempt < retries - 1:
                        time.sleep(2)
                        
        # 2. Try Fallback Gemini
        if self.gemini_key:
            print("Falling back to Google Gemini for JSON...")
            for attempt in range(retries):
                try:
                    text = self._call_gemini(prompt, require_json=True)
                    self._log_call("Gemini-JSON", self.gemini_model, prompt, text)
                    return self._clean_and_load_json(text)
                except Exception as e:
                    self._log_call("Gemini-JSON", self.gemini_model, prompt, "", str(e))
                    print(f"Gemini JSON generation fallback failed (attempt {attempt+1}/{retries}): {e}")
                    if attempt < retries - 1:
                        time.sleep(2)
                        
        raise RuntimeError("Both primary and fallback AI JSON generation attempts failed or were unconfigured.")

    def _clean_and_load_json(self, text):
        text = text.strip()
        # Strip markdown fences if present
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()
            
        # Clean any trailing or leading invalid formatting that can happen sometimes
        return json.loads(text)
