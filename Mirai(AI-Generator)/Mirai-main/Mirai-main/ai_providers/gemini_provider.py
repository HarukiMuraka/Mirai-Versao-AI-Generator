"""
ai_providers/gemini_provider.py
Provider para Google Gemini (gemini-1.5-flash).
"""

from pathlib import Path
from typing import Optional
import requests

from ai_providers.base_provider import BaseProvider


class GeminiProvider(BaseProvider):
    name = "gemini"

    def __init__(self, config: dict):
        self.api_key = config.get("api_key") or self._load_key()
        self.model   = config.get("model", "gemini-1.5-flash")
        self.url     = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def _load_key(self) -> Optional[str]:
        path = Path("config/gemini_key.txt")
        if path.exists():
            for line in path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and line != "SUA_CHAVE_AQUI":
                    return line
        return None

    async def test(self) -> bool:
        if not self.api_key:
            return False
        try:
            r = requests.post(
                f"{self.url}?key={self.api_key}",
                json={"contents": [{"parts": [{"text": "ok"}]}]},
                timeout=4,
            )
            return r.status_code == 200
        except Exception:
            return False

    async def generate(self, user_input, context, memory, search_results) -> Optional[str]:
        if not self.api_key:
            return None
        try:
            system  = self._build_persona_prompt(memory)
            history = self._format_context(context)
            search  = ""
            if search_results:
                search = f"\n[Pesquisa web: {search_results[0].get('snippet','')[:150]}]"

            prompt = f"{system}\n\nCONVERSA:\n{history}\nUsuário: {user_input}{search}\n\nMirai:"

            r = requests.post(
                f"{self.url}?key={self.api_key}",
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.9,
                        "maxOutputTokens": 250,
                        "topP": 0.95,
                    },
                    "safetySettings": [
                        {"category": "HARM_CATEGORY_HARASSMENT",        "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH",       "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                    ],
                },
                timeout=12,
            )

            if r.status_code == 200:
                candidates = r.json().get("candidates", [])
                if candidates:
                    return candidates[0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"  ⚠ Gemini: {e}")
        return None