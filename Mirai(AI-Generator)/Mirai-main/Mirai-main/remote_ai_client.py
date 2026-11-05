"""
RemoteMiraiAI
=============
Cliente que roda no PC PRINCIPAL e conversa com o mirai_server (rodando
no PC mais fraco) via HTTP, em vez de processar a IA localmente.

Mantém a MESMA interface pública do MiraiAI original:
    - generate_response(user_input, mode, enable_search)
    - generate_greeting()
    - generate_farewell()
    - should_take_initiative()
    - generate_initiative()

Isso significa que dá pra trocar, no main.py:
    self.ai = MiraiAI(self.context)
por:
    self.ai = RemoteMiraiAI(self.context)
sem precisar mexer no resto do código (modos, menu, etc.).

Configuração via variável de ambiente (ou parâmetros no construtor):
    MIRAI_SERVER_URL   -> ex: http://192.168.0.42:8420
    MIRAI_API_TOKEN    -> opcional, se o servidor tiver token configurado
"""
import os
import random
import requests


class RemoteMiraiAI:
    """Drop-in replacement para MiraiAI, processando no servidor remoto."""

    def __init__(self, context_manager=None, server_url=None, session_id="default", token=None):
        self.context = context_manager
        self.server_url = (
            server_url or os.environ.get("MIRAI_SERVER_URL", "http://192.168.0.100:8420")
        ).rstrip("/")
        self.session_id = session_id
        self.token = token or os.environ.get("MIRAI_API_TOKEN", "")
        self.timeout = 20
        self.online = False

        # Mantidos por compatibilidade com código que checa esses atributos
        self.use_gemini = True
        self.use_ollama = False

    async def initialize(self):
        """Testa a conexão com o servidor. Chamar no início, como o MiraiAI original."""
        try:
            r = requests.get(f"{self.server_url}/health", timeout=5)
            if r.status_code == 200:
                data = r.json()
                self.online = True
                print(f"  ✓ Conectado ao servidor Mirai ({self.server_url})")
                if not data.get("gemini_configured"):
                    print("  ⚠️  Servidor está rodando SEM a GEMINI_API_KEY configurada!")
                return True
        except Exception as e:
            print(f"  ✗ Não consegui conectar ao servidor Mirai em {self.server_url}: {e}")

        self.online = False
        print("  ⚠️  Mirai vai operar em modo offline (respostas de fallback)")
        return False

    def _headers(self):
        return {"x-mirai-token": self.token} if self.token else {}

    def generate_response(self, user_input, mode="conversation", enable_search=True):
        if self.context:
            self.context.add_message("user", user_input)

        response = self._offline_fallback()
        try:
            r = requests.post(
                f"{self.server_url}/chat",
                json={"message": user_input, "session_id": self.session_id, "mode": mode},
                headers=self._headers(),
                timeout=self.timeout,
            )
            if r.status_code == 200:
                response = r.json()["response"]
            else:
                print(f"  ⚠️  Servidor respondeu {r.status_code}: {r.text[:200]}")
        except requests.exceptions.ConnectionError:
            print(f"  ⚠️  Servidor Mirai offline ({self.server_url})")
        except Exception as e:
            print(f"  ⚠️  Erro ao falar com o servidor: {e}")

        if self.context:
            self.context.add_message("assistant", response)
        return response

    def _offline_fallback(self):
        return random.choice(
            [
                "Hmm, não consegui falar com meu cérebro agora (servidor offline).",
                "Opa, perdi a conexão com o servidor! Tenta de novo?",
                "Eita, o servidor não respondeu. Confere se ele tá ligado?",
            ]
        )

    def should_take_initiative(self):
        try:
            r = requests.get(
                f"{self.server_url}/initiative",
                params={"session_id": self.session_id},
                headers=self._headers(),
                timeout=5,
            )
            if r.status_code == 200:
                return r.json().get("should_speak", False)
        except Exception:
            pass
        return False

    def generate_initiative(self):
        try:
            r = requests.get(
                f"{self.server_url}/initiative",
                params={"session_id": self.session_id},
                headers=self._headers(),
                timeout=5,
            )
            if r.status_code == 200:
                data = r.json()
                if data.get("message"):
                    return data["message"]
        except Exception:
            pass
        return "E aí, tudo bem?"

    def generate_greeting(self):
        return "E aí! Tô conectada e pronta pra conversar!" if self.online else "Oi... acho que meu servidor tá offline."

    def generate_farewell(self):
        return "Falou! Até mais!"

    def reset_session(self):
        """Limpa o histórico da sessão atual no servidor."""
        try:
            requests.post(
                f"{self.server_url}/reset",
                params={"session_id": self.session_id},
                headers=self._headers(),
                timeout=5,
            )
        except Exception:
            pass