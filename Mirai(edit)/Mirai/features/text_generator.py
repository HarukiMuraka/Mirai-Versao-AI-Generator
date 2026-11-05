"""
features/text_generator.py
Geração de texto criativo pela Mirai:
  - histórias, poemas, roteiros, piadas, posts, etc.
"""

import asyncio
from pathlib import Path
from typing import Optional
import requests


class TextGenerator:
    """Gera texto criativo usando o provider de IA ativo."""

    # Tipos suportados
    TYPES = {
        "historia":   "uma história curta",
        "poema":      "um poema",
        "piada":      "uma piada engraçada",
        "roteiro":    "um roteiro de VTuber live",
        "post":       "um post para redes sociais",
        "legenda":    "uma legenda criativa",
        "descricao":  "uma descrição de personagem",
        "tweet":      "um tweet",
    }

    def __init__(self, ai_engine):
        self.ai = ai_engine

    async def generate(
        self,
        tipo: str,
        tema: str,
        estilo: Optional[str] = None,
        tamanho: str = "médio",
    ) -> str:
        """
        Gera texto criativo.

        Args:
            tipo: chave de TYPES ('historia', 'poema', etc.)
            tema: assunto principal
            estilo: estilo adicional (ex: 'cômico', 'sério')
            tamanho: 'curto', 'médio', 'longo'
        """
        tipo_desc = self.TYPES.get(tipo, tipo)
        estilo_txt = f" com estilo {estilo}" if estilo else ""
        size_map = {"curto": "em até 3 frases", "médio": "em até 8 frases", "longo": "em até 20 frases"}
        tamanho_txt = size_map.get(tamanho, "em tamanho adequado")

        prompt = (
            f"Crie {tipo_desc}{estilo_txt} sobre '{tema}' {tamanho_txt}. "
            f"Escreva em português do Brasil, seja criativo e original."
        )

        provider = self.ai._providers.get(self.ai.active_provider)
        if provider and self.ai.active_provider != "offline":
            result = await provider.generate(
                user_input=prompt,
                context=[],
                memory=self.ai.permanent_memory,
                search_results=[],
            )
            if result:
                return result

        # Fallback: template simples
        return self._template_fallback(tipo, tema)

    def _template_fallback(self, tipo: str, tema: str) -> str:
        templates = {
            "piada":   f"Por que {tema} é tão incrível? Porque ninguém consegue parar de falar sobre ele!",
            "poema":   f"{tema.capitalize()} brilla no céu,\nComo estrela entre nuvens a voar,\nTraz alegria no seu anel,\nE faz o coração sonhar.",
            "post":    f"Ei pessoal! 🌸 Hoje quero falar sobre {tema}! É um assunto que adoro e tenho muito a compartilhar. Fiquem ligados!",
            "tweet":   f"Acabei de descobrir algo incrível sobre {tema}! Não consigo parar de pensar nisso. #VTuber #Mirai",
        }
        return templates.get(tipo, f"[Texto sobre '{tema}' gerado pela Mirai — configure uma API para resultados melhores!]")

    def list_types(self) -> str:
        """Retorna lista formatada dos tipos disponíveis."""
        return "\n".join(f"  • {k:12} → {v}" for k, v in self.TYPES.items())