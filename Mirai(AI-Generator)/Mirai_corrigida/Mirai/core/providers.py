"""
core/providers.py — Providers de IA da Mirai

Cada provider tem:
  - _test_X()  → verifica se está disponível (síncrono, chamado via asyncio.to_thread)
  - _call_X()  → gera resposta (síncrono, chamado via asyncio.to_thread)

Providers disponíveis: Gemini, Grok, Ollama
"""

import json
import requests
from datetime import datetime


# ── constantes ────────────────────────────────────────────────────────────────

GEMINI_URL_V1     = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
GEMINI_URL_V1BETA = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
GROK_URL          = "https://api.x.ai/v1/chat/completions"
OLLAMA_URL        = "http://localhost:11434/api/generate"
OLLAMA_TAGS_URL   = "http://localhost:11434/api/tags"

GEMINI_SAFETY = [
    {"category": c, "threshold": "BLOCK_NONE"} for c in [
        "HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH",
        "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT",
    ]
]


# ── Gemini ────────────────────────────────────────────────────────────────────

class GeminiProvider:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url     = GEMINI_URL_V1          # fixado após teste bem-sucedido

    def test(self) -> tuple[bool, str]:
        """Testa v1 e v1beta. Fixa a URL que funcionar."""
        payload = {
            "contents": [{"parts": [{"text": "oi"}]}],
            "generationConfig": {"maxOutputTokens": 5},
        }
        for label, url in [("v1", GEMINI_URL_V1), ("v1beta", GEMINI_URL_V1BETA)]:
            try:
                r = requests.post(f"{url}?key={self.api_key}", json=payload, timeout=8)
                if r.status_code == 200:
                    self.url = url
                    return True, f"OK ({label})"
                if r.status_code == 400:
                    return False, "chave inválida — verifique config/gemini_key.txt"
                if r.status_code == 403:
                    return False, "chave sem permissão (erro 403)"
                if r.status_code == 429:
                    return False, "quota excedida — aguarde ou use Grok/Ollama"
            except requests.exceptions.ConnectionError:
                return False, "sem internet"
            except requests.exceptions.Timeout:
                pass  # tenta o próximo
            except Exception as e:
                return False, str(e)
        return False, "timeout em ambas as URLs — internet lenta?"

    def call(self, prompt: str, temperature: float = 0.92, max_tokens: int = 300) -> str | None:
        try:
            r = requests.post(
                f"{self.url}?key={self.api_key}",
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": max_tokens,
                        "topP": 0.95,
                        "topK": 40,
                    },
                    "safetySettings": GEMINI_SAFETY,
                },
                timeout=15,
            )

            if r.status_code == 200:
                data       = r.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    fb = data.get("promptFeedback", {})
                    print(f"  ⚠️  Gemini: bloqueado — {fb.get('blockReason','?')}")
                    return None
                c = candidates[0]
                if c.get("finishReason") == "SAFETY":
                    print("  ⚠️  Gemini: safety filter")
                    return None
                text = c["content"]["parts"][0]["text"].strip()
                return text.removeprefix("Mirai:").strip() or None

            if r.status_code == 429:
                print("  ⚠️  Gemini: quota excedida")
            elif r.status_code == 400:
                print(f"  ⚠️  Gemini: chave inválida (400) — {r.text[:100]}")
            else:
                print(f"  ⚠️  Gemini: HTTP {r.status_code}")

        except requests.exceptions.Timeout:
            print("  ⚠️  Gemini: timeout")
        except requests.exceptions.ConnectionError:
            print("  ⚠️  Gemini: sem conexão")
        except Exception as e:
            print(f"  ⚠️  Gemini erro: {type(e).__name__}: {e}")
        return None


# ── Grok ──────────────────────────────────────────────────────────────────────

class GrokProvider:
    def __init__(self, api_key: str, model: str = "grok-3-mini"):
        self.api_key = api_key
        self.model   = model
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def test(self) -> tuple[bool, str]:
        try:
            r = requests.post(
                GROK_URL,
                headers=self._headers,
                json={"model": self.model, "messages": [{"role": "user", "content": "oi"}], "max_tokens": 5},
                timeout=8,
            )
            if r.status_code == 200: return True, "OK"
            if r.status_code == 401: return False, "chave inválida — verifique config/grok_key.txt"
            if r.status_code == 429: return False, "quota excedida"
            return False, f"HTTP {r.status_code}"
        except requests.exceptions.ConnectionError:
            return False, "sem internet"
        except requests.exceptions.Timeout:
            return False, "timeout"
        except Exception as e:
            return False, str(e)

    def call(self, messages: list, temperature: float = 0.9, max_tokens: int = 300) -> str | None:
        try:
            r = requests.post(
                GROK_URL,
                headers=self._headers,
                json={"model": self.model, "messages": messages,
                      "max_tokens": max_tokens, "temperature": temperature},
                timeout=20,
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"].strip() or None
            if r.status_code == 429:
                print("  ⚠️  Grok: quota excedida")
            else:
                print(f"  ⚠️  Grok: HTTP {r.status_code}")
        except requests.exceptions.Timeout:
            print("  ⚠️  Grok: timeout")
        except Exception as e:
            print(f"  ⚠️  Grok erro: {e}")
        return None


# ── Ollama ────────────────────────────────────────────────────────────────────

class OllamaProvider:
    def __init__(self, model: str = "llama3"):
        self.model = model

    def test(self) -> tuple[bool, str]:
        """Verifica servidor + modelo. NÃO faz geração (evita lentidão no startup)."""
        try:
            r = requests.get(OLLAMA_TAGS_URL, timeout=5)
            if r.status_code != 200:
                return False, "servidor não responde — rode: ollama serve"
            models = [m.get("name", "") for m in r.json().get("models", [])]
            if not models:
                return False, f"nenhum modelo baixado — rode: ollama pull {self.model}"
            if not any(self.model in m for m in models):
                lista = ", ".join(models)
                return False, (
                    f"modelo '{self.model}' não encontrado\n"
                    f"       Disponíveis: {lista}\n"
                    f"       Baixe com: ollama pull {self.model}"
                )
            return True, "OK"
        except requests.exceptions.ConnectionError:
            return False, "Ollama não está rodando — instale em ollama.com e rode: ollama serve"
        except requests.exceptions.Timeout:
            return False, "timeout ao conectar com Ollama"
        except Exception as e:
            return False, str(e)

    def call(self, prompt: str, temperature: float = 0.9, max_tokens: int = 120) -> str | None:
        """Streaming para evitar timeout em modelos lentos."""
        try:
            print("  🤖 Ollama pensando", end="", flush=True)
            r = requests.post(
                OLLAMA_URL,
                json={
                    "model":  self.model,
                    "prompt": prompt,
                    "stream": True,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                        "num_ctx":     2048,   # contexto menor = mais rápido
                        "num_thread":  4,      # usa 4 threads da CPU
                        "stop": ["\nUsuário:", "\nU:", "\n\n"],
                    },
                },
                stream=True,
                timeout=120,
            )

            if r.status_code != 200:
                print(f"\r  ⚠️  Ollama: HTTP {r.status_code}          ")
                return None

            full = ""
            dots = 0
            for line in r.iter_lines():
                if not line:
                    continue
                try:
                    chunk = json.loads(line.decode("utf-8"))
                    full += chunk.get("response", "")
                    dots += 1
                    if dots % 5 == 0:
                        print(".", end="", flush=True)
                    if chunk.get("done") or len(full) > 600:
                        break
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue

            print(f"\r" + " " * 40 + "\r", end="", flush=True)
            text = full.strip().removeprefix("Mirai:").strip()
            return text or None

        except requests.exceptions.Timeout:
            print("\r  ⚠️  Ollama: timeout — tente: ollama pull phi3")
            return None
        except requests.exceptions.ConnectionError:
            print("\r  ⚠️  Ollama: conexão perdida")
            return None
        except Exception as e:
            print(f"\r  ⚠️  Ollama erro: {e}")
            return None