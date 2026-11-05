# memory/sistema_memoria.py
import json
from pathlib import Path
from datetime import datetime


class MemoriaCompleta:
    """
    Gerencia memória persistente entre sessões.
    
    CORREÇÃO: aceita tanto o formato novo {"conversas": [...]}
    quanto o formato antigo [{timestamp, user, mirai}] e converte automaticamente.
    """

    def __init__(self):
        self.memory_dir = Path("memory")
        self.memory_dir.mkdir(exist_ok=True)
        self.db_path = self.memory_dir / "conversas.json"
        self.conversas_sessao = 0
        self._dados = self._carregar()

    def _carregar(self) -> dict:
        """Carrega o JSON e normaliza para {"conversas": [...]}."""
        if self.db_path.exists():
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    raw = json.load(f)

                # Formato novo correto: {"conversas": [...]}
                if isinstance(raw, dict) and "conversas" in raw:
                    return raw

                # Formato antigo: lista com {timestamp, user, mirai}
                if isinstance(raw, list):
                    print("  ⚠  Memória: convertendo formato antigo para novo...")
                    conversas = []
                    for item in raw:
                        if isinstance(item, dict):
                            conversas.append({
                                "data":     item.get("timestamp", "")[:16].replace("T", " "),
                                "pergunta": item.get("user", "")[:500],
                                "resposta": item.get("mirai", "")[:500],
                            })
                    dados = {"conversas": conversas}
                    # Salva já no formato correto
                    self._salvar_dados(dados)
                    print(f"  ✓  {len(conversas)} conversas convertidas e salvas")
                    return dados

            except Exception as e:
                print(f"  ⚠  Memória: erro ao carregar ({e}) — iniciando do zero")

        # Arquivo não existe ou corrompido — começa vazio
        return {"conversas": []}

    def _salvar(self):
        self._salvar_dados(self._dados)

    def _salvar_dados(self, dados: dict):
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"  ⚠️  Erro ao salvar memória: {e}")

    def salvar_conversa(self, pergunta: str, resposta: str):
        entrada = {
            "data":     datetime.now().strftime("%d/%m/%Y %H:%M"),
            "pergunta": pergunta[:500],
            "resposta": resposta[:500],
        }
        self._dados["conversas"].append(entrada)
        # Mantém só as 500 mais recentes
        self._dados["conversas"] = self._dados["conversas"][-500:]
        self._salvar()
        self.conversas_sessao += 1

    def get_estatisticas(self) -> dict:
        return {
            "total_conversas":  len(self._dados["conversas"]),
            "conversas_sessao": self.conversas_sessao,
        }

    def buscar_contexto(self, query: str, limite: int = 3) -> list:
        q = query.lower()
        resultados = [
            c for c in reversed(self._dados["conversas"])
            if q in c.get("pergunta", "").lower()
            or q in c.get("resposta",  "").lower()
        ]
        return resultados[:limite]