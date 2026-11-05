import json
from pathlib import Path
from datetime import datetime
from collections import deque

class MemoriaCompleta:
    """Sistema de memória completo"""
    
    def __init__(self):
        self.memory_dir = Path("memory")
        self.memory_dir.mkdir(exist_ok=True)
        
        # Arquivos de memória
        self.conversas_file = self.memory_dir / "conversas.json"
        self.preferencias_file = self.memory_dir / "preferencias.json"
        self.fatos_file = self.memory_dir / "fatos_aprendidos.json"
        
        # Carrega memórias
        self.conversas = self.load_conversas()
        self.preferencias = self.load_preferencias()
        self.fatos_aprendidos = self.load_fatos()
        
        # Memória de curto prazo (sessão atual)
        self.short_term = deque(maxlen=50)
    
    def load_conversas(self):
        """Carrega histórico de conversas"""
        if self.conversas_file.exists():
            try:
                with open(self.conversas_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def load_preferencias(self):
        """Carrega preferências do usuário"""
        if self.preferencias_file.exists():
            try:
                with open(self.preferencias_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def load_fatos(self):
        """Carrega fatos aprendidos"""
        if self.fatos_file.exists():
            try:
                with open(self.fatos_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def salvar_conversa(self, user_msg, mirai_msg):
        """Salva conversa no histórico"""
        conversa = {
            'timestamp': datetime.now().isoformat(),
            'user': user_msg,
            'mirai': mirai_msg
        }
        
        self.conversas.append(conversa)
        self.short_term.append(conversa)
        
        # Mantém apenas últimas 1000 conversas
        if len(self.conversas) > 1000:
            self.conversas = self.conversas[-1000:]
        
        # Salva no arquivo
        with open(self.conversas_file, 'w', encoding='utf-8') as f:
            json.dump(self.conversas, f, ensure_ascii=False, indent=2)
    
    def salvar_preferencia(self, categoria, chave, valor):
        """Salva preferência do usuário"""
        if categoria not in self.preferencias:
            self.preferencias[categoria] = {}
        
        self.preferencias[categoria][chave] = {
            'valor': valor,
            'timestamp': datetime.now().isoformat()
        }
        
        # Salva no arquivo
        with open(self.preferencias_file, 'w', encoding='utf-8') as f:
            json.dump(self.preferencias, f, ensure_ascii=False, indent=2)
    
    def aprender_fato(self, topico, informacao):
        """Aprende um fato novo"""
        if topico not in self.fatos_aprendidos:
            self.fatos_aprendidos[topico] = []
        
        fato = {
            'info': informacao,
            'timestamp': datetime.now().isoformat()
        }
        
        self.fatos_aprendidos[topico].append(fato)
        
        # Salva no arquivo
        with open(self.fatos_file, 'w', encoding='utf-8') as f:
            json.dump(self.fatos_aprendidos, f, ensure_ascii=False, indent=2)
    
    def buscar_preferencia(self, categoria, chave=None):
        """Busca preferência"""
        if categoria in self.preferencias:
            if chave:
                return self.preferencias[categoria].get(chave, {}).get('valor')
            return self.preferencias[categoria]
        return None
    
    def buscar_fatos(self, topico):
        """Busca fatos sobre um tópico"""
        return self.fatos_aprendidos.get(topico, [])
    
    def get_contexto_recente(self, n=5):
        """Pega contexto recente da conversa"""
        return list(self.short_term)[-n:]
    
    def buscar_conversas_sobre(self, palavra_chave):
        """Busca conversas antigas sobre um tema"""
        palavra_lower = palavra_chave.lower()
        resultados = []
        
        for conversa in self.conversas[-100:]:  # Últimas 100
            if palavra_lower in conversa['user'].lower() or palavra_lower in conversa['mirai'].lower():
                resultados.append(conversa)
        
        return resultados
    
    def get_estatisticas(self):
        """Retorna estatísticas da memória"""
        return {
            'total_conversas': len(self.conversas),
            'preferencias_salvas': sum(len(v) for v in self.preferencias.values()),
            'fatos_aprendidos': sum(len(v) for v in self.fatos_aprendidos.values()),
            'conversas_sessao': len(self.short_term)
        }
    
    def limpar_sessao(self):
        """Limpa memória de curto prazo"""
        self.short_term.clear()
    
    def exportar_memoria(self, arquivo_saida="memoria_backup.json"):
        """Exporta toda a memória"""
        backup = {
            'conversas': self.conversas,
            'preferencias': self.preferencias,
            'fatos_aprendidos': self.fatos_aprendidos,
            'data_backup': datetime.now().isoformat()
        }
        
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            json.dump(backup, f, ensure_ascii=False, indent=2)
        
        return arquivo_saida