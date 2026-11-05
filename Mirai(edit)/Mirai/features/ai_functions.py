"""
features/ai_functions.py — Funções de IA da Mirai

Implementa capacidades extras além de chat:
  - Geração de texto  (resumo, tradução, continuação, história)
  - Geração de imagem (Pollinations.ai — grátis, sem chave)
  - Text-to-Speech    (edge-tts — grátis, sem chave)
  - Análise de texto  (sentimento, palavras-chave, tópico)

Todas as funções são async e independentes do provider de chat.
"""

import asyncio
import hashlib
import re
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path


# ══════════════════════════════════════════════════════════════════════════════
# 1. GERAÇÃO DE TEXTO  (usa o provider de IA ativo)
# ══════════════════════════════════════════════════════════════════════════════

class TextFunctions:
    """
    Funções de texto que delegam para o MiraiAI.
    Cada função monta um prompt especializado e chama generate_response().
    """

    def __init__(self, ai_instance):
        self.ai = ai_instance

    async def resumir(self, texto: str) -> str:
        """Resume um texto longo em 3-5 frases."""
        prompt = (
            f"Resume o seguinte texto em 3 a 5 frases curtas, em português brasileiro. "
            f"Seja direto, sem introdução:\n\n{texto[:3000]}"
        )
        return await self.ai.generate_response(prompt, mode="text_function", enable_search=False)

    async def traduzir(self, texto: str, idioma_destino: str = "inglês") -> str:
        """Traduz texto para o idioma especificado."""
        prompt = (
            f"Traduza o seguinte texto para {idioma_destino}. "
            f"Retorne APENAS a tradução, sem explicações:\n\n{texto[:2000]}"
        )
        return await self.ai.generate_response(prompt, mode="text_function", enable_search=False)

    async def continuar(self, texto: str) -> str:
        """Continua um texto a partir de onde parou."""
        prompt = (
            f"Continue o seguinte texto de forma natural, mantendo o mesmo estilo e tom. "
            f"Escreva mais 2-4 parágrafos:\n\n{texto[-1000:]}"
        )
        return await self.ai.generate_response(prompt, mode="text_function", enable_search=False)

    async def criar_historia(self, tema: str, estilo: str = "aventura") -> str:
        """Cria uma história curta com tema e estilo definidos."""
        prompt = (
            f"Crie uma história curta de {estilo} com o tema: {tema}. "
            f"A história deve ter início, meio e fim. "
            f"Escreva em português brasileiro, de forma envolvente."
        )
        return await self.ai.generate_response(prompt, mode="text_function", enable_search=False)

    async def melhorar_texto(self, texto: str) -> str:
        """Melhora gramática e clareza de um texto."""
        prompt = (
            f"Melhore o seguinte texto: corrija gramática, melhore clareza e fluidez. "
            f"Mantenha o sentido original. Retorne APENAS o texto melhorado:\n\n{texto[:2000]}"
        )
        return await self.ai.generate_response(prompt, mode="text_function", enable_search=False)

    async def gerar_titulo(self, texto: str) -> str:
        """Gera 3 opções de título para um texto."""
        prompt = (
            f"Gere 3 opções de título criativo para o seguinte texto. "
            f"Um por linha, sem numeração:\n\n{texto[:1000]}"
        )
        return await self.ai.generate_response(prompt, mode="text_function", enable_search=False)

    async def analisar_sentimento(self, texto: str) -> dict:
        """Analisa sentimento do texto. Retorna dict com resultado."""
        prompt = (
            f"Analise o sentimento do texto abaixo. Responda APENAS com uma linha no formato:\n"
            f"SENTIMENTO: [positivo/negativo/neutro] | INTENSIDADE: [baixa/média/alta] | "
            f"EMOÇÃO: [alegria/tristeza/raiva/medo/surpresa/nenhuma]\n\n{texto[:500]}"
        )
        raw = await self.ai.generate_response(prompt, mode="text_function", enable_search=False)
        result = {"sentimento": "neutro", "intensidade": "baixa", "emocao": "nenhuma", "raw": raw}
        try:
            for part in raw.split("|"):
                part = part.strip()
                if "SENTIMENTO:" in part:
                    result["sentimento"] = part.split(":")[1].strip().lower()
                elif "INTENSIDADE:" in part:
                    result["intensidade"] = part.split(":")[1].strip().lower()
                elif "EMOÇÃO:" in part or "EMOCAO:" in part:
                    result["emocao"] = part.split(":")[1].strip().lower()
        except Exception:
            pass
        return result

    async def extrair_palavras_chave(self, texto: str) -> list[str]:
        """Extrai as palavras-chave principais do texto."""
        prompt = (
            f"Extraia as 5 principais palavras-chave do texto abaixo. "
            f"Retorne APENAS as palavras separadas por vírgula:\n\n{texto[:1000]}"
        )
        raw = await self.ai.generate_response(prompt, mode="text_function", enable_search=False)
        return [w.strip() for w in raw.split(",") if w.strip()][:8]


# ══════════════════════════════════════════════════════════════════════════════
# 2. GERAÇÃO DE IMAGEM  (Pollinations.ai — 100% grátis, sem chave)
# ══════════════════════════════════════════════════════════════════════════════

class ImageFunctions:
    """
    Geração de imagens — delega para features.image_generator.ImageGenerator,
    que lê config/ai.json e suporta tanto Stable Diffusion local (Automatic1111)
    quanto Pollinations.ai (grátis, online, fallback automático).

    Mantém a mesma interface pública de antes (gerar, gerar_avatar, gerar_fundo,
    listar_estilos) para não quebrar quem já chama esta classe.
    """

    OUTPUT_DIR = Path("outputs/images")

    # mapa estilo (pt) -> estilo aceito pelo ImageGenerator
    _ESTILO_MAP = {
        "anime": "anime", "realista": "realistic", "pintura": "painting",
        "pixel": "pixel", "cartoon": "chibi", "sketch": "painting",
        "cyberpunk": "realistic", "fantasia": "painting",
    }

    def __init__(self):
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self._gen = None
        self._init_lock = asyncio.Lock()

    async def _get_generator(self):
        """Cria o ImageGenerator uma vez, lendo config/ai.json (provider, sd_url)."""
        if self._gen is not None:
            return self._gen
        async with self._init_lock:
            if self._gen is not None:
                return self._gen
            from features.image_generator import ImageGenerator
            image_config = {}
            try:
                import json
                with open("config/ai.json", "r", encoding="utf-8") as f:
                    image_config = json.load(f).get("image", {})
            except Exception:
                pass
            self._gen = ImageGenerator(image_config)
            await self._gen.initialize()
            return self._gen

    async def gerar(
        self,
        descricao: str,
        largura: int = 512,
        altura: int = 512,
        estilo: str = "",
        salvar: bool = True,
    ) -> dict:
        """
        Gera uma imagem a partir de descrição em texto.

        Retorna dict com:
          arquivo  → caminho local do arquivo gerado (ou None se falhou)
          prompt   → prompt usado
          sucesso  → bool
          provider → qual motor gerou (stable_diffusion ou pollinations)
        """
        gen = await self._get_generator()
        estilo_gen = self._ESTILO_MAP.get(estilo.lower(), estilo) if estilo else "anime"

        result = {"arquivo": None, "prompt": descricao, "sucesso": False, "provider": gen.provider}

        try:
            caminho = await gen.generate(descricao, style=estilo_gen, width=largura, height=altura)
            if caminho:
                result["arquivo"]  = str(caminho)
                result["sucesso"]  = True
                result["provider"] = gen.provider
        except Exception as e:
            print(f"  ⚠️  Erro ao gerar imagem: {e}")

        return result

    async def gerar_avatar(self, descricao_personagem: str) -> dict:
        """Gera avatar/personagem com estilo anime."""
        prompt = (
            f"anime character portrait, {descricao_personagem}, "
            f"high quality, detailed face, clean lines, vibrant colors"
        )
        return await self.gerar(prompt, largura=512, altura=512)

    async def gerar_fundo(self, cenario: str) -> dict:
        """Gera imagem de fundo/cenário."""
        prompt = f"background scene, {cenario}, wide angle, detailed, high quality"
        return await self.gerar(prompt, largura=1024, altura=512)

    @staticmethod
    def listar_estilos() -> list[str]:
        return ["anime", "realista", "pintura", "pixel", "cartoon", "sketch", "cyberpunk", "fantasia"]


# ══════════════════════════════════════════════════════════════════════════════
# 3. TEXT-TO-SPEECH  (edge-tts — grátis, 300+ vozes)
# ══════════════════════════════════════════════════════════════════════════════

class TTSFunctions:
    """
    Text-to-Speech usando edge-tts (Microsoft Edge TTS, grátis).
    Requer: pip install edge-tts pygame
    """

    OUTPUT_DIR = Path("outputs/audio")

    # Vozes recomendadas em PT-BR
    VOZES_PTBR = {
        "feminina_1": "pt-BR-FranciscaNeural",   # suave e clara
        "feminina_2": "pt-BR-LeticiaNeural",      # jovem e animada
        "masculina":  "pt-BR-AntonioNeural",      # grave e claro
    }
    VOZ_PADRAO = "pt-BR-FranciscaNeural"

    def __init__(self):
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self._edge_tts_ok = self._check_edge_tts()

    @staticmethod
    def _check_edge_tts() -> bool:
        try:
            import edge_tts  # noqa
            return True
        except ImportError:
            return False

    async def falar(
        self,
        texto: str,
        voz: str | None = None,
        velocidade: str = "+0%",
        salvar: bool = True,
        tocar: bool = True,
    ) -> dict:
        """
        Converte texto em fala.

        velocidade: "+20%" (mais rápido), "-10%" (mais lento), "+0%" (normal)
        Retorna dict com: arquivo, sucesso, duracao_estimada
        """
        if not self._edge_tts_ok:
            return {
                "sucesso": False,
                "erro": "edge-tts não instalado. Execute: pip install edge-tts",
                "arquivo": None,
            }

        import edge_tts

        voz_real = voz or self.VOZ_PADRAO
        ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo  = self.OUTPUT_DIR / f"mirai_tts_{ts}.mp3"

        result = {"arquivo": str(arquivo), "sucesso": False, "erro": None}

        try:
            communicate = edge_tts.Communicate(
                text=texto[:3000],
                voice=voz_real,
                rate=velocidade,
            )
            await communicate.save(str(arquivo))
            result["sucesso"] = True

            # Toca o áudio se solicitado
            if tocar and salvar:
                await asyncio.to_thread(self._tocar_audio, str(arquivo))

        except Exception as e:
            result["erro"] = str(e)
            print(f"  ⚠️  TTS erro: {e}")

        return result

    @staticmethod
    def _tocar_audio(arquivo: str):
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(arquivo)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                import time; time.sleep(0.1)
        except Exception as e:
            print(f"  ⚠️  Erro ao tocar áudio: {e}")

    def listar_vozes(self) -> dict:
        return self.VOZES_PTBR


# ══════════════════════════════════════════════════════════════════════════════
# 4. FACADE — AIFunctions (interface unificada)
# ══════════════════════════════════════════════════════════════════════════════

class AIFunctions:
    """
    Interface unificada para todas as funções de IA.
    Use esta classe nos modos e no menu.

    Exemplo:
        funcs = AIFunctions(mirai.ai)
        resumo = await funcs.texto.resumir("texto longo...")
        img    = await funcs.imagem.gerar("gato roxo voando")
        await  funcs.tts.falar("Olá, sou a Mirai!")
    """

    def __init__(self, ai_instance):
        self.texto  = TextFunctions(ai_instance)
        self.imagem = ImageFunctions()
        self.tts    = TTSFunctions()

    # ── atalhos convenientes ──────────────────────────────────────────

    async def resumir(self, texto: str) -> str:
        return await self.texto.resumir(texto)

    async def traduzir(self, texto: str, idioma: str = "inglês") -> str:
        return await self.texto.traduzir(texto, idioma)

    async def gerar_imagem(self, descricao: str, estilo: str = "") -> dict:
        return await self.imagem.gerar(descricao, estilo=estilo)

    async def falar(self, texto: str) -> dict:
        return await self.tts.falar(texto)

    def status(self) -> dict:
        """Retorna quais funções estão disponíveis."""
        return {
            "texto":  True,  # sempre disponível (depende do provider de IA)
            "imagem": True,  # Pollinations.ai não precisa de chave
            "tts":    self.tts._edge_tts_ok,
        }