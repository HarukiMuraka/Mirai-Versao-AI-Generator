import speech_recognition as sr
import threading
import time

class VoiceListener:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_listening = False
        self.callback = None
        self.language = "pt-BR"
        
        # Configurações otimizadas
        self.recognizer.pause_threshold = 1.0  # 1 segundo de pausa para parar
        self.recognizer.energy_threshold = 300  # Sensibilidade ao som
        self.recognizer.dynamic_energy_threshold = True  # Ajuste automático
        
    def initialize(self):
        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                print("  🎤 Ajustando para ruído ambiente...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("  ✓ Microfone pronto")
            return True
        except Exception as e:
            print(f"  ⚠  Microfone não disponível: {e}")
            return False
    
    def listen_once(self):
        """Escuta uma vez com feedback visual"""
        if not self.microphone:
            return None
        
        try:
            print("  🎤 Escutando...")
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source, 
                    timeout=5,  # 5s para começar a falar
                    phrase_time_limit=10  # 10s máximo de fala
                )
            
            print("  ⏳ Processando...")
            text = self.recognizer.recognize_google(audio, language=self.language)
            print(f"  ✓ Reconhecido: {text}")
            return text
        
        except sr.WaitTimeoutError:
            print("  ⏱ Tempo esgotado")
            return None
        except sr.UnknownValueError:
            print("  ❌ Não entendi")
            return None
        except Exception as e:
            print(f"  ❌ Erro: {e}")
            return None
    
    def listen_once_silent(self):
        """Escuta uma vez SEM feedback visual (para modo autônomo)"""
        if not self.microphone:
            return None
        
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source, 
                    timeout=5,
                    phrase_time_limit=10
                )
            
            text = self.recognizer.recognize_google(audio, language=self.language)
            return text
        
        except:
            return None
    
    def start_continuous_listening(self, callback):
        """Escuta contínua em thread separada"""
        self.callback = callback
        self.is_listening = True
        
        def listen_loop():
            while self.is_listening:
                text = self.listen_once()
                if text and self.callback:
                    self.callback(text)
        
        thread = threading.Thread(target=listen_loop, daemon=True)
        thread.start()
    
    def stop_listening(self):
        """Para escuta contínua"""
        self.is_listening = False