"""
ai_providers/openai_provider.py
Provider para OpenAI (gpt-4o-mini ou gpt-3.5-turbo).
"""

from pathlib import Path
from typing import Optional
import requests

from ai_providers.base_provider import BaseProvider


class OpenAIProvider(BaseProvider):
    name = "openai"

    def __init__(self, config: dict):
        self.api_key = config.get("api_key") or self._load_key()
        self.model   = config.get("model", "gpt-4o-mini")
        self.url     = "https://api.openai.com/v1/chat/completions"

    def _load_key(self) -> Optional[str]:
        path = Path("config/openai_key.txt")
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
            r = requests.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=5,
            )
            return r.status_code == 200
        except Exception:
            return False

    async def generate(self, user_input, context, memory, search_results) -> Optional[str]:
        if not self.api_key:
            return None
        try:
            system  = self._build_persona_prompt(memory)
            search  = ""
            if search_results:
                search = f"\n[Pesquisa: {search_results[0].get('snippet','')[:150]}]"

            messages = [{"role": "system", "content": system}]
            for msg in context[-8:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": user_input + search})

            r = requests.post(
                self.url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type":  "application/json",
                },
                json={
                    "model":       self.model,
                    "messages":    messages,
                    "max_tokens":  250,
                    "temperature": 0.9,
                },
                timeout=15,
            )

            if r.status_code == 200:
                choices = r.json().get("choices", [])
                if choices:
                    return choices[0]["message"]["content"].strip()
        except Exception as e:
            print(f"  ⚠ OpenAI: {e}")
        return None