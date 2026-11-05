"""
features/knowledge_manager.py
Controle do Conhecimento da Mirai — "cérebro" da IA.

Permite:
  - Ensinar novos fatos à Mirai
  - Consultar o conhecimento salvo
  - Editar personalidade (gírias, apelidos, comportamento)
  - Resetar ou exportar conhecimento
  - Ajustar parâmetros do provider de IA em runtime
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


KNOWLEDGE_PATH   = Path("memory/knowledge.json")
PERSONALITY_PATH = Path("memory/permanent_memory.json")
PROVIDER_PATH    = Path("config/ai.json")


class KnowledgeManager:
    """Gerencia o conhecimento e a personalidade da Mirai."""

    def __init__(self, ai_engine=None):
        self.ai = ai_engine
        self.knowledge = self._load(KNOWLEDGE_PATH, default={
            "fatos":      [],
            "topicos":    {},
            "instrucoes": [],
        })

    # ------------------------------------------------------------------
    # CONHECIMENTO FACTUAL
    # ------------------------------------------------------------------

    def teach(self, fato: str, categoria: str = "geral") -> str:
        """Ensina um novo fato à Mirai."""
        entry = {
            "fato":      fato,
            "categoria": categoria,
            "data":      datetime.now().isoformat(),
        }
        self.knowledge.setdefault("fatos", []).append(entry)
        self.knowledge.setdefault("topicos", {}).setdefault(categoria, []).append(fato)
        self._save(KNOWLEDGE_PATH, self.knowledge)
        return f"Aprendi: {fato} (categoria: {categoria})"

    def recall(self, categoria: Optional[str] = None) -> list[dict]:
        """Retorna fatos conhecidos, opcionalmente filtrados por categoria."""
        fatos = self.knowledge.get("fatos", [])
        if categoria:
            fatos = [f for f in fatos if f.get("categoria") == categoria]
        return fatos

    def forget(self, fato: str) -> str:
        """Remove um fato do conhecimento."""
        antes = len(self.knowledge.get("fatos", []))
        self.knowledge["fatos"] = [
            f for f in self.knowledge.get("fatos", [])
            if fato.lower() not in f.get("fato", "").lower()
        ]
        depois = len(self.knowledge["fatos"])
        self._save(KNOWLEDGE_PATH, self.knowledge)
        removidos = antes - depois
        return f"{removidos} fato(s) removido(s)." if removidos else "Nenhum fato encontrado com esse termo."

    def add_instruction(self, instrucao: str) -> str:
        """Adiciona instrução permanente de comportamento."""
        self.knowledge.setdefault("instrucoes", []).append({
            "instrucao": instrucao,
            "data":      datetime.now().isoformat(),
        })
        self._save(KNOWLEDGE_PATH, self.knowledge)
        return f"Instrução adicionada: {instrucao}"

    def get_instructions(self) -> list[str]:
        return [i["instrucao"] for i in self.knowledge.get("instrucoes", [])]

    # ------------------------------------------------------------------
    # PERSONALIDADE
    # ------------------------------------------------------------------

    def edit_personality(self, campo: str, valor: Any) -> str:
        """
        Edita um campo da personalidade.
        Campos disponíveis: apelidos, girias, palavras_japonesas,
                            sem_emojis, usa_girias
        """
        memory = self._load(PERSONALITY_PATH, default={})

        if campo == "apelidos":
            memory.setdefault("usuario", {})["apelidos"] = (
                valor if isinstance(valor, list) else [valor]
            )
        elif campo == "girias":
            memory["girias"] = valor if isinstance(valor, list) else valor.split(",")
        elif campo == "palavras_japonesas":
            memory["palavras_japonesas"] = valor if isinstance(valor, list) else [valor]
        elif campo in ("sem_emojis", "usa_girias"):
            memory.setdefault("personalidade", {})[campo] = bool(valor)
        else:
            return f"Campo '{campo}' desconhecido."

        self._save(PERSONALITY_PATH, memory)

        # Atualiza em runtime se ai_engine disponível
        if self.ai:
            self.ai.permanent_memory = memory

        return f"Personalidade atualizada: {campo} = {valor}"

    def get_personality_summary(self) -> str:
        memory = self._load(PERSONALITY_PATH, default={})
        apelidos  = memory.get("usuario", {}).get("apelidos", [])
        girias    = memory.get("girias", [])
        sem_emj   = memory.get("personalidade", {}).get("sem_emojis", True)
        usa_giria = memory.get("personalidade", {}).get("usa_girias", True)
        return (
            f"Apelidos: {', '.join(apelidos)}\n"
            f"Gírias: {', '.join(girias)}\n"
            f"Sem emojis: {sem_emj} | Usa gírias: {usa_giria}"
        )

    # ------------------------------------------------------------------
    # PROVIDER DE IA
    # ------------------------------------------------------------------

    def set_provider(self, provider: str, config: dict = None) -> str:
        """
        Altera o provider de IA em runtime e salva no config.
        Ex: set_provider("gemini", {"api_key": "xxx"})
        """
        cfg = self._load(PROVIDER_PATH, default={})
        cfg["provider_priority"] = [provider] + [p for p in cfg.get("provider_priority", []) if p != provider]
        if config:
            cfg[provider] = {**cfg.get(provider, {}), **config}
        self._save(PROVIDER_PATH, cfg)

        if self.ai:
            self.ai.active_provider = provider
            new_provider = self.ai._load_provider(provider)
            if new_provider:
                self.ai._providers[provider] = new_provider

        return f"Provider alterado para: {provider}"

    def get_provider_status(self) -> str:
        if self.ai:
            info = self.ai.get_provider_info()
            return f"Ativo: {info['active']} | Disponíveis: {', '.join(info['available'])}"
        return "AI engine não conectado."

    def set_api_key(self, provider: str, key: str) -> str:
        """Salva chave de API de um provider."""
        key_files = {
            "gemini": Path("config/gemini_key.txt"),
            "claude": Path("config/claude_key.txt"),
            "openai": Path("config/openai_key.txt"),
        }
        if provider not in key_files:
            return f"Provider '{provider}' não suportado para chave direta."
        path = key_files[provider]
        path.parent.mkdir(exist_ok=True)
        path.write_text(key.strip())
        return f"Chave de {provider} salva! Reinicie a Mirai para aplicar."

    # ------------------------------------------------------------------
    # EXPORTAR / RESETAR
    # ------------------------------------------------------------------

    def export(self) -> Path:
        """Exporta todo o conhecimento para um arquivo JSON."""
        memory      = self._load(PERSONALITY_PATH, default={})
        provider_cfg = self._load(PROVIDER_PATH, default={})
        export_data = {
            "knowledge":    self.knowledge,
            "personality":  memory,
            "provider_cfg": provider_cfg,
            "exported_at":  datetime.now().isoformat(),
        }
        out = Path("outputs/mirai_knowledge_export.json")
        out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps(export_data, indent=2, ensure_ascii=False), encoding="utf-8")
        return out

    def reset_knowledge(self) -> str:
        """Reseta fatos e instruções (mantém personalidade)."""
        self.knowledge = {"fatos": [], "topicos": {}, "instrucoes": []}
        self._save(KNOWLEDGE_PATH, self.knowledge)
        return "Conhecimento resetado (personalidade mantida)."

    def stats(self) -> str:
        fatos = len(self.knowledge.get("fatos", []))
        cats  = len(self.knowledge.get("topicos", {}))
        instr = len(self.knowledge.get("instrucoes", []))
        return f"Fatos: {fatos} | Categorias: {cats} | Instruções: {instr}"

    # ------------------------------------------------------------------
    # UTILITÁRIOS
    # ------------------------------------------------------------------

    def _load(self, path: Path, default: Any) -> Any:
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return default

    def _save(self, path: Path, data: Any):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")