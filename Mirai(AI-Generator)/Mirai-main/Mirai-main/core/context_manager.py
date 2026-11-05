from collections import deque
from datetime import datetime
from pathlib import Path
import json

class ContextManager:
    """Gerencia contexto e memória da conversa - COM MEMÓRIA PERMANENTE"""
    
    def __init__(self, max_history=10):
        self.max_history = max_history
        self.conversation_history = deque(maxlen=max_history)
        self.session_start = datetime.now()
        self.user_preferences = {}
        self.current_topic = None
        
        # Memória permanente
        self.permanent_memory_path = Path("memory/permanent_memory.json")
        self.load_preferences_from_permanent()
        
    def add_message(self, role, content):
        """Adiciona mensagem ao histórico"""
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now()
        }
        self.conversation_history.append(message)
    
    def get_recent_context(self, n=5):
        """Retorna últimas N mensagens"""
        return list(self.conversation_history)[-n:]
    
    def get_full_context(self):
        """Retorna todo o contexto"""
        return list(self.conversation_history)
    
    def clear_context(self):
        """Limpa o contexto atual (temporário)"""
        self.conversation_history.clear()
        self.current_topic = None
    
    def set_preference(self, key, value):
        """Define preferência do usuário"""
        self.user_preferences[key] = value
    
    def get_preference(self, key, default=None):
        """Obtém preferência do usuário"""
        return self.user_preferences.get(key, default)
    
    def get_session_duration(self):
        """Retorna duração da sessão"""
        return (datetime.now() - self.session_start).seconds
    
    def load_preferences_from_permanent(self):
        """Carrega preferências da memória permanente"""
        if self.permanent_memory_path.exists():
            try:
                with open(self.permanent_memory_path, 'r', encoding='utf-8') as f:
                    memory = json.load(f)
                    
                    # Carrega preferências do usuário
                    user_data = memory.get('usuario', {})
                    if 'preferencias' in user_data:
                        self.user_preferences.update(user_data['preferencias'])
                    
            except Exception as e:
                print(f"  ⚠️  Não foi possível carregar preferências: {e}")
    
    def save_preferences_to_permanent(self):
        """Salva preferências na memória permanente"""
        if not self.permanent_memory_path.exists():
            return
        
        try:
            with open(self.permanent_memory_path, 'r', encoding='utf-8') as f:
                memory = json.load(f)
            
            # Atualiza preferências
            if 'usuario' not in memory:
                memory['usuario'] = {}
            
            memory['usuario']['preferencias'] = self.user_preferences
            
            with open(self.permanent_memory_path, 'w', encoding='utf-8') as f:
                json.dump(memory, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"  ⚠️  Erro ao salvar preferências: {e}")
    
    def salvar_na_memoria(self, memoria_sistema):
        """Salva contexto atual na memória permanente"""
        recent = self.get_recent_context(10)
        
        # Salva pares de user-assistant
        for i in range(0, len(recent) - 1, 2):
            if recent[i]['role'] == 'user' and i + 1 < len(recent):
                if recent[i + 1]['role'] == 'assistant':
                    memoria_sistema.salvar_conversa(
                        recent[i]['content'],
                        recent[i + 1]['content']
                    )