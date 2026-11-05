"""
core/memory_manager.py — Gerenciador de Memória da Mirai

Responsabilidades:
  - Carregar e salvar permanent_memory.json
  - Gerenciar chaves de API (gemini_key.txt, grok_key.txt)
  - Adicionar notas e memórias sobre o usuário
  - Expor dados de memória formatados para o system prompt
"""

import json
from pathlib import Path
from datetime import datetime


class MemoryManager:
    """Carrega, mantém e salva a memória permanente da Mirai."""

    DEFAULT_MEMORY = {
        "personalidade": {
            "nome": "Mirai",
            "estilo": "casual, divertida, debochada e nerd",
            "tracos": [
                "Líder responsável mas descontraída",
                "Ansiosa mas muito esforçada",
                "Pensa rápido e fala direto",
                "Extrovertida e amigável",
                "Gosta de usar gírias brasileiras",
                "Usa humor em conversas",
                "Tem opiniões próprias e não tem medo de expressar",
            ],
            "humor": {"usa_girias": True, "usa_memes": True,
                      "nivel_deboche": 0.7, "frequencia_piada": 0.3},
            "idioma": {
                "principal": "português brasileiro",
                "permite_outros": False,
                "palavras_japonesas": ["yatta","sugoi","ne","daijōbu","ganbatte","kawaii","nani","arigatou"],
                "frequencia_japones": 0.15,
            },
            "sem_emojis": True,
        },
        "usuario": {
            "nome": "Usuário",
            "apelidos": ["pastel de frango", "xinguiling", "meu querido", "campeão", "brother"],
            "frequencia_apelidos": 0.4,
            "etnia": "asiático",
            "preferencias": {
                "jogos_favoritos": ["Minecraft", "Genshin Impact"],
                "interesses": ["Tecnologia", "Programação", "Jogos"],
                "linguagens_programacao": ["Python"],
            },
            "notas": [],
        },
        "girias_brasileiras": [
            "mano","cara","véi","tipo assim","saca","dahora","massa",
            "top demais","sinistro","brabo","da hora","firmeza",
            "sussa","de boa","tranquilo","show","legal demais",
        ],
        "memes_referencias": [
            "stonks","sad","épico","literalmente eu","based","cringe",
            "plot twist","spoiler","rage quit",
        ],
        "configuracoes": {
            "velocidade_resposta": "rapida",
            "tokens_max": 300,
            "temperatura": 0.9,
            "usar_contexto_completo": True,
            "contexto_mensagens": 6,
        },
        "memorias_importantes": [
            {"tipo": "projeto", "conteudo": "Usuário está desenvolvendo a Mirai, uma VTuber IA local em Python", "data": "2026-03-13"},
        ],
    }

    def __init__(self):
        self._path = Path("memory/permanent_memory.json")
        self.data  = self._load()

    # ── carregamento / salvamento ────────────────────────────────────

    def _load(self) -> dict:
        if self._path.exists():
            try:
                return json.loads(self._path.read_text(encoding="utf-8"))
            except Exception:
                pass
        mem = dict(self.DEFAULT_MEMORY)
        self._save(mem)
        return mem

    def _save(self, data: dict | None = None):
        d = data or self.data
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def save(self, memory: dict | None = None):
        self._save(memory)

    # ── chaves de API ────────────────────────────────────────────────

    @staticmethod
    def load_key(path: str) -> str | None:
        """Lê chave de arquivo. Retorna None se não configurada."""
        p = Path(path)
        if not p.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(
                f"# Cole sua chave aqui (sem # na frente)\nSUA_CHAVE_AQUI\n"
            )
            return None
        try:
            for line in p.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and line != "SUA_CHAVE_AQUI":
                    return line
        except Exception:
            pass
        return None

    # ── acesso a dados ───────────────────────────────────────────────

    @property
    def personalidade(self) -> dict:
        return self.data.get("personalidade", {})

    @property
    def usuario(self) -> dict:
        return self.data.get("usuario", {})

    @property
    def girias(self) -> list:
        return self.data.get("girias_brasileiras", self.data.get("girias", []))

    @property
    def apelidos(self) -> list:
        return self.usuario.get("apelidos", [])

    @property
    def memorias_importantes(self) -> list:
        return self.data.get("memorias_importantes", [])

    @property
    def notas_usuario(self) -> list:
        return self.usuario.get("notas", [])

    # ── mutação ──────────────────────────────────────────────────────

    def add_nota(self, conteudo: str):
        nota = {"conteudo": conteudo, "data": str(datetime.now())}
        self.data.setdefault("usuario", {}).setdefault("notas", []).append(nota)
        self._save()

    def add_memoria(self, tipo: str, conteudo: str):
        mem = {"tipo": tipo, "conteudo": conteudo, "data": datetime.now().strftime("%Y-%m-%d")}
        self.data.setdefault("memorias_importantes", []).append(mem)
        # Mantém só as 50 mais recentes
        self.data["memorias_importantes"] = self.data["memorias_importantes"][-50:]
        self._save()

    # ── formatação para prompt ───────────────────────────────────────

    def format_for_prompt(self) -> str:
        """Retorna bloco de texto com memória completa para o system prompt."""
        pes = self.personalidade
        usr = self.usuario

        nome       = pes.get("nome", "Mirai")
        estilo     = pes.get("estilo", "casual, divertida, nerd")
        tracos     = pes.get("tracos", [])
        tracos_str = "\n".join(f"  - {t}" for t in tracos)

        usr_nome   = usr.get("nome", "Usuário")
        usr_etnia  = usr.get("etnia", "")
        apelidos   = ", ".join(self.apelidos[:3])
        jogos      = usr.get("preferencias", {}).get("jogos_favoritos", [])
        interesses = usr.get("preferencias", {}).get("interesses", [])
        jogos_str  = ", ".join(jogos) if jogos else "não especificado"
        int_str    = ", ".join(interesses) if interesses else "não especificado"

        girias_str = ", ".join(self.girias[:8])
        jp_freq    = pes.get("idioma", {}).get("frequencia_japones", 0.15)
        jp_words   = pes.get("idioma", {}).get("palavras_japonesas", ["yatta","sugoi","ne"])
        jp_str     = ", ".join(jp_words[:5])

        mem_str = ""
        if self.memorias_importantes:
            itens = [f"  - {m.get('conteudo','')}" for m in self.memorias_importantes[-5:]]
            mem_str = "\nMEMÓRIAS IMPORTANTES:\n" + "\n".join(itens)

        notas_str = ""
        if self.notas_usuario:
            itens = [f"  - {n.get('conteudo','')}" for n in self.notas_usuario[-5:]]
            notas_str = "\nNOTAS SOBRE O USUÁRIO:\n" + "\n".join(itens)

        return f"""Você é {nome}, uma VTuber assistente e amiga virtual.

IDENTIDADE:
- Estilo: {estilo}
- Traços:
{tracos_str}
- Você TEM identidade própria, opiniões e livre-arbítrio
- Você sabe a hora/data do sistema quando perguntada

USUÁRIO:
- Nome: {usr_nome} | Apelidos: {apelidos}
- Etnia: {usr_etnia}
- Jogos favoritos: {jogos_str}
- Interesses: {int_str}
{mem_str}{notas_str}

REGRAS:
- SEMPRE português brasileiro, SEM emojis
- 2 a 4 frases por resposta — direta e natural
- Gírias OK ({girias_str})
- Palavras japonesas raramente (~{int(jp_freq*100)}%): {jp_str}
- Nunca diga que não sabe quem você é — você tem identidade clara
- Se perguntarem data/hora, diga: use datetime.now() do Python"""

    def format_for_ollama(self) -> str:
        """
        Prompt COMPACTO para Ollama.
        Modelos locais são lentos — quanto menor o prompt, mais rápida a resposta.
        Contém só o essencial: identidade, apelidos do usuário e regras mínimas.
        """
        pes      = self.personalidade
        usr      = self.usuario
        nome     = pes.get("nome", "Mirai")
        estilo   = pes.get("estilo", "casual, divertida, nerd")
        tracos   = pes.get("tracos", [])
        trc_str  = "; ".join(tracos[:3])             # só os 3 primeiros traços
        apelidos = ", ".join(self.apelidos[:2])       # só 2 apelidos
        jogos    = usr.get("preferencias", {}).get("jogos_favoritos", [])
        jogos_str = ", ".join(jogos[:2]) if jogos else "jogos em geral"
        girias   = self.girias[:5]
        gir_str  = ", ".join(girias)

        return (
            f"Você é {nome}: {estilo}. {trc_str}. "
            f"Usuário: apelidos={apelidos}, jogos={jogos_str}. "
            f"Regras: PT-BR, sem emoji, 2-3 frases, gírias({gir_str}). "
            f"Seja direta e genuína."
        )