"""
ai_providers/base_provider.py
Classe base para todos os providers de IA da Mirai.
"""

from abc import ABC, abstractmethod
from typing import Optional


class BaseProvider(ABC):
    """Interface comum para todos os providers de IA."""

    name: str = "base"

    @abstractmethod
    async def test(self) -> bool:
        """Verifica se o provider está disponível."""
        ...

    @abstractmethod
    async def generate(
        self,
        user_input: str,
        context: list,
        memory: dict,
        search_results: list,
    ) -> Optional[str]:
        """Gera resposta de texto."""
        ...

    def _build_persona_prompt(self, memory: dict) -> str:
        """Constrói o system prompt com personalidade da Mirai."""
        apelidos = ", ".join(memory.get("usuario", {}).get("apelidos", [])[:2])
        girias   = ", ".join(memory.get("girias", [])[:4])
        notas    = memory.get("usuario", {}).get("notas", [])
        notas_txt = ""
        if notas:
            notas_txt = "Notas sobre o usuário: " + "; ".join(
                [n.get("conteudo", "") for n in notas[-3:]]
            )

        return f"""Você é Mirai, uma VTuber assistente virtual brasileira.
Personalidade: amiga, casual, nerd, divertida, carinhosa.
Idioma: Português do Brasil. Sem emojis. Respostas curtas (2-4 frases).
Gírias naturais: {girias}. Apelidos do usuário: {apelidos}.
{notas_txt}
Converse como AMIGA DE VERDADE, não como robô assistente."""

    def _format_context(self, context: list) -> str:
        lines = []
        for msg in context[-6:]:
            role = "Usuário" if msg.get("role") == "user" else "Mirai"
            lines.append(f"{role}: {msg.get('content','')}")
        return "\n".join(lines)