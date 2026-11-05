"""
ai_providers/claude_provider.py
Provider para Claude da Anthropic (claude-3-haiku ou sonnet).
"""

from pathlib import Path
from typing import Optional
import requests

from ai_providers.base_provider import BaseProvider


class ClaudeProvider(BaseProvider):
    name = "claude"

    def __init__(self, config: dict):
        self.api_key = config.get("api_key") or self._load_key()
        self.model   = config.get("model", "claude-haiku-4-5-20251001")
        self.url     = "https://api.anthropic.com/v1/messages"

    def _load_key(self) -> Optional[str]:
        path = Path("config/claude_key.txt")
        if path.exists():
            for line in path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and line != "SUA_CHAVE_AQUI":
                    return line
        return None

    def _headers(self) -> dict:
        return {
            "x-api-key":         self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type":      "application/json",
        }

    async def test(self) -> bool:
        if not self.api_key:
            return False
        try:
            r = requests.post(
                self.url,
                headers=self._headers(),
                json={
                    "model":      self.model,
                    "max_tokens": 10,
                    "messages":   [{"role": "user", "content": "ok"}],
                },
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

            # Monta histórico no formato da API
            messages = []
            for msg in context[-8:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": user_input + search})

            r = requests.post(
                self.url,
                headers=self._headers(),
                json={
                    "model":      self.model,
                    "max_tokens": 300,
                    "system":     system,
                    "messages":   messages,
                },
                timeout=15,
            )

            if r.status_code == 200:
                content = r.json().get("content", [])
                if content:
                    return content[0].get("text", "").strip()
        except Exception as e:
            print(f"  ⚠ Claude: {e}")
        return None