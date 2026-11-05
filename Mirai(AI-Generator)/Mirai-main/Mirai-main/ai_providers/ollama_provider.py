"""
ai_providers/ollama_provider.py
Provider para Ollama (LLM local — llama3, mistral, etc.).
"""

from typing import Optional
import requests

from ai_providers.base_provider import BaseProvider


class OllamaProvider(BaseProvider):
    name = "ollama"

    def __init__(self, config: dict):
        self.model   = config.get("model", "llama3")
        self.base    = config.get("base_url", "http://localhost:11434")
        self.gen_url = f"{self.base}/api/generate"
        self.tag_url = f"{self.base}/api/tags"

    async def test(self) -> bool:
        try:
            r = requests.get(self.tag_url, timeout=2)
            return r.status_code == 200
        except Exception:
            return False

    async def generate(self, user_input, context, memory, search_results) -> Optional[str]:
        try:
            system  = self._build_persona_prompt(memory)
            history = self._format_context(context)
            search  = ""
            if search_results:
                search = f"\n[Web: {search_results[0].get('snippet','')[:100]}]"

            prompt = f"{system}\n{history}\nUsuário: {user_input}{search}\nMirai:"

            r = requests.post(
                self.gen_url,
                json={
                    "model":  self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.9,
                        "num_predict": 200,
                        "stop": ["\nUsuário:", "\nUser:"],
                    },
                },
                timeout=20,
            )

            if r.status_code == 200:
                return r.json().get("response", "").strip()
        except Exception as e:
            print(f"  ⚠ Ollama: {e}")
        return None