"""
core/ai_engine.py — Orquestrador da IA da Mirai  (v4.0 — modular)

Importa e coordena os módulos especializados:
  memory_manager.py  → memória persistente
  providers.py       → Gemini, Grok, Ollama
  responder.py       → respostas offline + busca web
  initiative.py      → saudações e livre-arbítrio

Tamanho reduzido: de ~1200 linhas para ~230 linhas.
"""

import asyncio
import json
from pathlib import Path

from core.memory_manager import MemoryManager
from core.providers      import GeminiProvider, GrokProvider, OllamaProvider
from core.responder      import (needs_search, search_web,
                                  offline_response, remove_emojis, personalize)
from core.initiative     import InitiativeEngine


# ── compatibilidade com knowledge_manager.py legado ──────────────────────────

class _ProvidersCompat:
    """
    Emula dict self.ai._providers para o knowledge_manager.py antigo.
    Intercepta _providers[provider] = x  →  chama set_provider(provider).
    """
    def __init__(self, ai):       self._ai = ai
    def __setitem__(self, k, v):  self._ai.set_provider(k)
    def __getitem__(self, k):     return self._ai
    def __contains__(self, k):    return k in ("gemini","grok","ollama","offline")
    def get(self, k, d=None):     return self._ai if k in self else d


# ── MiraiAI ───────────────────────────────────────────────────────────────────

class MiraiAI:
    """
    Motor de IA da Mirai.
    Coordena memória, providers e geração de resposta.
    """

    def __init__(self, context_manager=None):
        self.context = context_manager

        # ── memória ───────────────────────────────────────────────────
        self._mem_mgr         = MemoryManager()
        self.permanent_memory = self._mem_mgr.data   # acesso direto legado

        # ── providers (instâncias) ────────────────────────────────────
        gemini_key = MemoryManager.load_key("config/gemini_key.txt")
        grok_key   = MemoryManager.load_key("config/grok_key.txt")
        ollama_model = self._load_ollama_model()

        self._gemini = GeminiProvider(gemini_key) if gemini_key else None
        self._grok   = GrokProvider(grok_key)     if grok_key   else None
        self._ollama = OllamaProvider(ollama_model)

        # ── estado dos providers (exposto para o menu) ────────────────
        self.use_gemini      = False
        self.use_grok        = False
        self.use_ollama      = False
        self.active_provider = "offline"

        # Chaves expostas para compatibilidade com menu.py legado
        self.gemini_api_key = gemini_key
        self.grok_api_key   = grok_key
        self.ollama_model   = ollama_model
        self.gemini_url     = getattr(self._gemini, "url", "")

        # ── compatibilidade com knowledge_manager.py legado ───────────
        self._providers = _ProvidersCompat(self)

        # ── iniciativa / livre-arbítrio ───────────────────────────────
        self._initiative = InitiativeEngine(self.permanent_memory)

    # ── configuração ─────────────────────────────────────────────────

    def _load_ollama_model(self) -> str:
        try:
            cfg = Path("config/ai.json")
            if cfg.exists():
                return json.loads(cfg.read_text(encoding="utf-8")).get("ollama", {}).get("model", "llama3")
        except Exception:
            pass
        return "llama3"

    # ── inicialização async ───────────────────────────────────────────

    async def initialize(self) -> bool:
        print("  🔍 Verificando providers de IA...\n")

        # Gemini
        if not self._gemini:
            print("  ⚠️  Gemini: chave não configurada")
            print("       Arquivo: config/gemini_key.txt")
            print("       Grátis em: https://aistudio.google.com/app/apikey\n")
        else:
            ok, msg = await asyncio.to_thread(self._gemini.test)
            if ok:
                self.use_gemini = True; self.active_provider = "gemini"
                self.gemini_url = self._gemini.url
                print(f"  ✓ Gemini ativo! ({msg}) — 1500 req/dia grátis\n")
                return True
            print(f"  ✗ Gemini falhou: {msg}\n")

        # Grok
        if not self._grok:
            print("  ⚠️  Grok: chave não configurada (opcional)")
            print("       Arquivo: config/grok_key.txt")
            print("       Grátis em: https://console.x.ai\n")
        else:
            ok, msg = await asyncio.to_thread(self._grok.test)
            if ok:
                self.use_grok = True; self.active_provider = "grok"
                print(f"  ✓ Grok ativo! ({msg})\n")
                return True
            print(f"  ✗ Grok falhou: {msg}\n")

        # Ollama
        ok, msg = await asyncio.to_thread(self._ollama.test)
        if ok:
            self.use_ollama = True; self.active_provider = "ollama"
            print(f"  ✓ Ollama ativo! (modelo: {self.ollama_model})\n")
            return True
        print(f"  ✗ Ollama: {msg}\n")

        # Offline
        self.active_provider = "offline"
        print("  ⚠️  Modo OFFLINE — configure Gemini, Grok ou Ollama para respostas completas\n")
        return True

    # ── geração de resposta ───────────────────────────────────────────

    async def generate_response(
        self,
        user_input: str,
        mode: str = "conversation",
        enable_search: bool = True,
    ) -> str:
        """SEMPRE async. Use: response = await self.ai.generate_response(texto)"""
        self._initiative.touch()

        # Busca web quando necessário
        sr = []
        if enable_search and needs_search(user_input):
            sr = await asyncio.to_thread(search_web, user_input)

        # Monta prompt comum para Gemini/Grok/Ollama
        mem_block = self._mem_mgr.format_for_prompt()
        conv      = self._format_context(6)
        sr_ctx    = f"\n\n[INFO WEB]:\n{sr[0]['snippet'][:300]}" if sr else ""

        response = None

        # ── Gemini ────────────────────────────────────────────────────
        if self.use_gemini:
            prompt   = f"{mem_block}\n\nMODO: {mode}\n\nCONVERSA:\n{conv}Usuário: {user_input}{sr_ctx}\n\nMirai:"
            response = await asyncio.to_thread(self._gemini.call, prompt)
            if response:
                response = remove_emojis(response)
            else:
                print("  ⚠️  Gemini não retornou resposta")

        # ── Grok ──────────────────────────────────────────────────────
        if response is None and self.use_grok:
            messages = [{"role": "system", "content": mem_block}]
            for line in conv.strip().split("\n"):
                if line.startswith("Usuário:"):
                    messages.append({"role": "user",      "content": line[8:].strip()})
                elif line.startswith("Mirai:"):
                    messages.append({"role": "assistant", "content": line[6:].strip()})
            messages.append({"role": "user", "content": user_input + sr_ctx})
            response = await asyncio.to_thread(self._grok.call, messages)
            if response:
                response = remove_emojis(response)

        # ── Ollama ────────────────────────────────────────────────────
        # Usa prompt COMPACTO — modelos locais são lentos com prompts grandes
        if response is None and self.use_ollama:
            ollama_sys = self._mem_mgr.format_for_ollama()
            prompt     = f"{ollama_sys}\n\nMODO: {mode}\n\n{conv}Usuário: {user_input}{sr_ctx}\n\nMirai:"
            response   = await asyncio.to_thread(self._ollama.call, prompt)
            if response:
                response = remove_emojis(response)

        # ── Offline ───────────────────────────────────────────────────
        if response is None:
            if self.use_gemini or self.use_grok or self.use_ollama:
                print("  ⚠️  Todos os providers falharam — usando resposta offline")
            response = offline_response(user_input.lower(), sr, self.permanent_memory)

        response = personalize(response, self.permanent_memory)

        # Salva no contexto
        if self.context:
            self.context.add_message("user", user_input)
            self.context.add_message("assistant", response)

        return response

    # ── contexto ─────────────────────────────────────────────────────

    def _format_context(self, n: int = 6) -> str:
        if not self.context:
            return ""
        ctx   = self.context.get_recent_context(n)
        lines = [
            f"{'Usuário' if m['role']=='user' else 'Mirai'}: {m['content']}"
            for m in ctx[-n:]
        ]
        return "\n".join(lines) + "\n" if lines else ""

    # ── memória (interface pública legada) ────────────────────────────

    def save_permanent_memory(self, memory=None):
        if memory:
            self._mem_mgr.data = memory
        self._mem_mgr.save()

    def save_memory(self):
        self._mem_mgr.save()

    def add_user_note(self, note: str):
        self._mem_mgr.add_nota(note)

    # ── iniciativa / livre-arbítrio ───────────────────────────────────

    def generate_greeting(self)   -> str: return self._initiative.greeting()
    def generate_farewell(self)   -> str: return self._initiative.farewell()
    def generate_initiative(self) -> str: return self._initiative.initiative()
    def should_take_initiative(self) -> bool: return self._initiative.should_speak()

    # ── providers (interface pública) ─────────────────────────────────

    def get_provider_info(self) -> dict:
        available = [p for p, a in [("gemini", self.use_gemini),
                                     ("grok",   self.use_grok),
                                     ("ollama", self.use_ollama)] if a] or ["offline"]
        return {
            "active":            self.active_provider,
            "available":         available,
            "gemini_configured": bool(self._gemini),
            "grok_configured":   bool(self._grok),
            "ollama_model":      self.ollama_model,
        }

    def set_provider(self, provider: str) -> str:
        """Troca o provider ativo. Retorna mensagem de resultado."""
        provider = provider.lower().strip()
        self.use_gemini = self.use_grok = self.use_ollama = False

        if provider == "gemini":
            if not self._gemini:
                return "❌ Gemini: chave não configurada (config/gemini_key.txt)"
            ok, msg = self._gemini.test()
            if ok:
                self.use_gemini = True; self.active_provider = "gemini"
                return f"✓ Gemini ativado ({msg})"
            return f"❌ Gemini falhou: {msg}"

        elif provider == "grok":
            if not self._grok:
                return "❌ Grok: chave não configurada (config/grok_key.txt)"
            ok, msg = self._grok.test()
            if ok:
                self.use_grok = True; self.active_provider = "grok"
                return f"✓ Grok ativado ({msg})"
            return f"❌ Grok falhou: {msg}"

        elif provider == "ollama":
            ok, msg = self._ollama.test()
            if ok:
                self.use_ollama = True; self.active_provider = "ollama"
                return f"✓ Ollama ativado (modelo: {self.ollama_model})"
            return f"❌ Ollama falhou: {msg}"

        elif provider == "offline":
            self.active_provider = "offline"
            return "✓ Modo offline ativado"

        return f"❌ Provider desconhecido: '{provider}'. Use: gemini, grok, ollama, offline"

    def _load_provider(self, provider: str):
        """Compatibilidade com knowledge_manager.py legado."""
        self.set_provider(provider)
        return self

    # ── teste direto (usado pelo menu) ────────────────────────────────

    def _test_gemini(self) -> tuple:
        return self._gemini.test() if self._gemini else (False, "chave não configurada")

    def _test_ollama(self) -> tuple:
        return self._ollama.test()

    def _test_grok(self) -> tuple:
        return self._grok.test() if self._grok else (False, "chave não configurada")