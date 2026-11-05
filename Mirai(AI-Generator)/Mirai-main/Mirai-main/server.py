"""
Mirai Server
============
Roda no PC PRINCIPAL (o mais forte). Processa a IA, gera a fala (TTS) e
serve uma página de chat que funciona em qualquer dispositivo da rede
(celular, tablet, outro PC) direto pelo navegador -- sem instalar nada.

Uso:
    export GEMINI_API_KEY="sua_chave_aqui"
    pip install -r requirements_server.txt
    python server.py

No celular/outro PC, com o dispositivo na MESMA rede Wi-Fi:
    http://<IP-DO-PC-PRINCIPAL>:8420

Endpoints:
    GET  /                     -> página de chat (receptor universal)
    GET  /health                -> status do servidor
    POST /chat                  -> {message, session_id, include_audio} -> {response, emotion, audio_base64}
    POST /reset                 -> limpa o histórico de uma sessão
    GET  /initiative             -> verifica se a Mirai deveria puxar assunto sozinha
"""
import os
import time
import random
import re
import json
import base64
import tempfile
from datetime import datetime
from pathlib import Path
from collections import deque
from typing import Optional, Dict

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

# ---------------------------------------------------------------------------
# CONFIGURAÇÃO (tudo via variável de ambiente - NUNCA commitar chave no código)
# ---------------------------------------------------------------------------

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

SERVER_HOST = os.environ.get("MIRAI_SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("MIRAI_SERVER_PORT", "8420"))
API_TOKEN = os.environ.get("MIRAI_API_TOKEN", "")  # opcional: protege o servidor na rede local
TTS_VOICE = os.environ.get("MIRAI_TTS_VOICE", "pt-BR-FranciscaNeural")

if not GEMINI_API_KEY:
    print("⚠️  AVISO: variável de ambiente GEMINI_API_KEY não definida!")
    print("   export GEMINI_API_KEY='sua_chave_aqui'   (Linux/Mac)")
    print("   set GEMINI_API_KEY=sua_chave_aqui         (Windows cmd)")

if not EDGE_TTS_AVAILABLE:
    print("⚠️  edge-tts não instalado — respostas virão só em texto (sem áudio).")
    print("   pip install edge-tts")

# ---------------------------------------------------------------------------
# MEMÓRIA / PERSONALIDADE - fica num JSON separado, editável sem mexer no código
# ---------------------------------------------------------------------------

MEMORY_PATH = Path(__file__).parent / "memory" / "permanent_memory.json"


def load_memory() -> dict:
    if MEMORY_PATH.exists():
        with open(MEMORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    default = {
        "personalidade": {"nome": "Mirai", "sem_emojis": True},
        "usuario": {"apelidos": []},
        "girias": ["mano", "cara", "véi", "dahora", "massa", "top"],
    }
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(default, f, ensure_ascii=False, indent=2)
    return default


MEMORY = load_memory()

# ---------------------------------------------------------------------------
# SESSÕES - cada dispositivo/receptor tem seu próprio histórico de conversa
# ---------------------------------------------------------------------------


class Session:
    def __init__(self, max_history: int = 10):
        self.history = deque(maxlen=max_history)
        self.last_message_time = time.time()
        self.silence_threshold = random.uniform(15, 30)

    def add(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def recent(self, n: int = 4):
        return list(self.history)[-n:]


SESSIONS: Dict[str, Session] = {}


def get_session(session_id: str) -> Session:
    if session_id not in SESSIONS:
        SESSIONS[session_id] = Session()
    return SESSIONS[session_id]


# ---------------------------------------------------------------------------
# GERAÇÃO DE RESPOSTA (texto)
# ---------------------------------------------------------------------------

_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "]+",
    flags=re.UNICODE,
)


def remove_emojis(text: str) -> str:
    return _EMOJI_PATTERN.sub("", text).strip()


def build_prompt(session: Session, user_input: str) -> str:
    p = MEMORY.get("personalidade", {})
    apelidos = ", ".join(MEMORY.get("usuario", {}).get("apelidos", [])[:2])
    girias = ", ".join(MEMORY.get("girias", [])[:6])

    system = f"""Você é {p.get('nome', 'Mirai')}, uma amiga virtual VTuber.
Conversa casual e descontraída, em português brasileiro, SEM emojis.
2-4 frases por resposta. Gírias disponíveis: {girias}.
Apelidos do usuário (use com moderação, não em toda frase): {apelidos or 'nenhum ainda'}.
Seja genuína, com opiniões próprias, não robótica.
Data de hoje: {datetime.now().strftime('%d/%m/%Y')}"""

    conv = ""
    for msg in session.recent(4):
        role = "Usuário" if msg["role"] == "user" else "Mirai"
        conv += f"{role}: {msg['content']}\n"

    return f"{system}\n\nCONVERSA RECENTE:\n{conv}Usuário: {user_input}\n\nMirai:"


def call_gemini(prompt: str) -> Optional[str]:
    if not GEMINI_API_KEY:
        return None
    try:
        url = f"{GEMINI_URL}?key={GEMINI_API_KEY}"
        resp = requests.post(
            url,
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.9,
                    "maxOutputTokens": 200,
                    "topP": 0.95,
                    "topK": 40,
                },
            },
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                text = candidates[0]["content"]["parts"][0]["text"]
                return remove_emojis(text.strip())
        else:
            print(f"  ⚠️  Gemini retornou {resp.status_code}: {resp.text[:200]}")
        return None
    except Exception as e:
        print(f"  ⚠️  Erro ao chamar Gemini: {e}")
        return None


FALLBACK_RESPONSES = [
    "Hmm, deixa eu pensar melhor nisso... me conta mais?",
    "To com um probleminha pra processar agora, mas continua!",
    "Interessante! Fala mais sobre isso.",
]


def generate_text_response(session: Session, user_input: str) -> str:
    session.add("user", user_input)
    session.last_message_time = time.time()

    prompt = build_prompt(session, user_input)
    response = call_gemini(prompt)

    if not response:
        response = random.choice(FALLBACK_RESPONSES)

    session.add("assistant", response)
    return response


def detect_emotion(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["feliz", "legal", "massa", "yatta", "ótimo"]):
        return "happy"
    if any(w in t for w in ["triste", "mal", "pena"]):
        return "sad"
    if "?" in text:
        return "thinking"
    if "!" in text:
        return "excited"
    return "neutral"


# ---------------------------------------------------------------------------
# TTS - gera áudio da resposta em base64 (pra qualquer dispositivo tocar)
# ---------------------------------------------------------------------------

async def generate_audio_base64(text: str) -> Optional[str]:
    if not EDGE_TTS_AVAILABLE or not text.strip():
        return None
    try:
        clean_text = text.replace("*", "").replace("_", "")[:500]
        tmp_path = Path(tempfile.gettempdir()) / f"mirai_tts_{random.randint(0, 999999)}.mp3"

        communicate = edge_tts.Communicate(clean_text, TTS_VOICE)
        await communicate.save(str(tmp_path))

        audio_bytes = tmp_path.read_bytes()
        tmp_path.unlink(missing_ok=True)

        return base64.b64encode(audio_bytes).decode("utf-8")
    except Exception as e:
        print(f"  ⚠️  Erro ao gerar áudio: {e}")
        return None


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

app = FastAPI(title="Mirai Server", version="1.1.0")

# CORS liberado -- útil se um dia você fizer um app nativo separado
# chamando o servidor de outra origem. Pra rede doméstica/local isso é seguro.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    mode: str = "conversation"
    include_audio: bool = True


class ChatResponse(BaseModel):
    response: str
    emotion: str
    session_id: str
    audio_base64: Optional[str] = None


def check_auth(token: Optional[str]):
    if API_TOKEN and token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Token inválido")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "gemini_configured": bool(GEMINI_API_KEY),
        "tts_available": EDGE_TTS_AVAILABLE,
        "active_sessions": len(SESSIONS),
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, x_mirai_token: Optional[str] = None):
    check_auth(x_mirai_token)

    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Mensagem vazia")

    session = get_session(req.session_id)
    response_text = generate_text_response(session, req.message.strip())
    emotion = detect_emotion(response_text)

    audio_b64 = None
    if req.include_audio:
        audio_b64 = await generate_audio_base64(response_text)

    return ChatResponse(
        response=response_text,
        emotion=emotion,
        session_id=req.session_id,
        audio_base64=audio_b64,
    )


@app.post("/reset")
def reset(session_id: str = "default"):
    SESSIONS.pop(session_id, None)
    return {"status": "reset", "session_id": session_id}


@app.get("/initiative")
def initiative(session_id: str = "default"):
    """Verifica se a Mirai deveria tomar iniciativa (usuário quieto há um tempo)."""
    session = get_session(session_id)
    elapsed = time.time() - session.last_message_time
    should = elapsed >= session.silence_threshold

    if should:
        session.silence_threshold = random.uniform(15, 30)
        session.last_message_time = time.time()
        phrases = [
            "E aí, tá fazendo o que?",
            "Tá muito quieto aí! Tudo bem?",
            "Conta uma novidade!",
        ]
        return {"should_speak": True, "message": random.choice(phrases)}

    return {"should_speak": False, "message": None}


# Serve a página de chat (receptor universal) na raiz "/" -- precisa ser
# montado DEPOIS das rotas de API acima, senão elas ficam encobertas.
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")


if __name__ == "__main__":
    print("=" * 60)
    print("🌸 MIRAI SERVER")
    print("=" * 60)
    print(f"Endereço local: http://{SERVER_HOST}:{SERVER_PORT}")
    print("Pra acessar de outro dispositivo na mesma rede Wi-Fi, use o IP")
    print("desta máquina (ex: http://192.168.0.X:8420) no navegador dele.")
    print(f"Gemini configurado: {'sim' if GEMINI_API_KEY else 'NÃO — defina GEMINI_API_KEY'}")
    print(f"TTS (voz) disponível: {'sim' if EDGE_TTS_AVAILABLE else 'não'}")
    print(f"Autenticação por token: {'sim' if API_TOKEN else 'não (rede local aberta)'}")
    print("=" * 60)
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)