from enum import Enum

class SystemState(Enum):
    """Estados do sistema"""
    IDLE = "idle"
    PRINCIPAL = "principal"  # ✅ MODO PRINCIPAL UNIFICADO
    CONVERSATION = "conversation"
    ASSISTANT = "assistant"
    GAMER = "gamer"
    OBSERVER = "observer"
    VOICE_ACTIVE = "voice_active"
    STREAMER = "streamer"
    BACKGROUND = "background"
    PAUSED = "paused"


class StateMachine:
    """Máquina de estados"""
    
    def __init__(self):
        self.current_state = SystemState.IDLE
        self.previous_state = None
        self.state_data = {}
        
    def set_state(self, new_state):
        """Define novo estado"""
        if isinstance(new_state, str):
            new_state = SystemState(new_state)
        
        self.previous_state = self.current_state
        self.current_state = new_state
    
    def get_state(self):
        """Retorna estado atual"""
        return self.current_state
    
    def is_state(self, state):
        """Verifica se está em determinado estado"""
        if isinstance(state, str):
            state = SystemState(state)
        return self.current_state == state
    
    def can_transition_to(self, new_state):
        """Verifica se pode transitar (sempre True por enquanto)"""
        return True
    
    def set_data(self, key, value):
        """Armazena dados do estado"""
        self.state_data[key] = value
    
    def get_data(self, key, default=None):
        """Recupera dados do estado"""
        return self.state_data.get(key, default)
    
    def clear_data(self):
        """Limpa dados do estado"""
        self.state_data.clear()