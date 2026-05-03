import requests
import json
import time
from config.settings import OLLAMA_HOST, OLLAMA_MODEL

class OllamaClient:
    def __init__(self, host=OLLAMA_HOST, model=OLLAMA_MODEL):
        self.host = host
        self.model = model
        self.base_url = f"{host}/api/generate"

    def _log_call(self, prompt, response, error=None):
        try:
            with open("ollama_debug.log", "a", encoding="utf-8") as f:
                ts = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n[{ts}] --- OLLAMA CALL ---\n")
                f.write(f"PROMPT: {prompt[:200]}...\n")
                if error:
                    f.write(f"ERROR: {error}\n")
                else:
                    f.write(f"RESPONSE: {response[:200]}...\n")
        except:
             pass

    def generate(self, prompt, retries=3):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        for attempt in range(retries):
            try:
                response = requests.post(self.base_url, json=payload, timeout=60)
                response.raise_for_status()
                data = response.json()
                text = data.get("response", "").strip()
                self._log_call(prompt, text)
                return text
            except Exception as e:
                self._log_call(prompt, "", str(e))
                print(f"Ollama generation failed (attempt {attempt+1}/{retries}): {e}")
                time.sleep(2)
        return ""

    def generate_json(self, prompt, retries=3):
        # We enforce JSON response by telling the model in the payload
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        
        for attempt in range(retries):
            try:
                response = requests.post(self.base_url, json=payload, timeout=60)
                response.raise_for_status()
                data = response.json()
                text = data.get("response", "").strip()
                self._log_call(prompt, text)
                
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    print("Ollama returned invalid JSON, retrying...")
                    time.sleep(1)
            except Exception as e:
                self._log_call(prompt, "", str(e))
                print(f"Ollama JSON generation failed: {e}")
                time.sleep(2)
        return {}
