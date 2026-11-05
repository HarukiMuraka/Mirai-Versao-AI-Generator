from enum import Enum

class SystemState(Enum):
    IDLE = "idle"
    CONVERSATION = "conversation"
    ASSISTANT = "assistant"
    GAMER = "gamer"
    OBSERVER = "observer"
    VOICE_ACTIVE = "voice_active"  # NOVO!
    STREAMER = "streamer"  # NOVO!
    BACKGROUND = "background"
    PAUSED = "paused"

class StateMachine:
    def __init__(self):
        self.current_state = SystemState.IDLE
        self.previous_state = None
        self.state_data = {}
        
    def set_state(self, new_state):
        if isinstance(new_state, str):
            new_state = SystemState(new_state)
        
        self.previous_state = self.current_state
        self.current_state = new_state
        print(f"  → Estado: {self.previous_state.value} → {self.current_state.value}")
    
    def get_state(self):
        return self.current_state
    
    def is_state(self, state):
        if isinstance(state, str):
            state = SystemState(state)
        return self.current_state == state
    
    def can_transition_to(self, new_state):
        return True
    
    def set_data(self, key, value):
        self.state_data[key] = value
    
    def get_data(self, key, default=None):
        return self.state_data.get(key, default)