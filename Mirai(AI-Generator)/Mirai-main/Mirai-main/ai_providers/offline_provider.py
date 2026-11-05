"""
ai_providers/offline_provider.py
Provider offline — responde sem nenhuma API externa.
Sempre disponível como fallback final.
"""

import random
from typing import Optional
from ai_providers.base_provider import BaseProvider


class OfflineProvider(BaseProvider):
    name = "offline"

    async def test(self) -> bool:
        return True   # sempre disponível

    async def generate(self, user_input, context, memory, search_results) -> Optional[str]:
        return None   # ai_engine usa _offline_response como fallback