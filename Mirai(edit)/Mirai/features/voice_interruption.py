import asyncio
import threading
from typing import Callable, Optional
from colorama import Fore, Style

class VoiceInterruptionSystem:
    """Sistema de interrupção de voz - permite interromper a IA falando"""
    
    def __init__(self, voice_listener, speaker):
        self.voice_listener = voice_listener
        self.speaker = speaker
        
        # Estado
        self.is_speaking = False
        self.is_listening_for_interruption = False
        self.interruption_detected = False
        
        # Thread de monitoramento
        self.monitor_thread = None
        self.running = False
        
        # Callbacks
        self.on_interrupt_callback = None
        
        # Configurações
        self.interruption_energy_threshold = 4000  # Sensibilidade
        self.interruption_phrase_time_limit = 0.5  # Detecta voz rápida
        
    def start_monitoring(self):
        """Inicia monitoramento de interrupções"""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Para monitoramento"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
    
    def _monitor_loop(self):
        """Loop de monitoramento em background"""
        while self.running:
            if self.is_listening_for_interruption and self.is_speaking:
                # Verifica se usuário está falando
                if self._detect_voice_activity():
                    self.interruption_detected = True
                    self._handle_interruption()
            
            asyncio.sleep(0.1)  # Checa a cada 100ms
    
    def _detect_voice_activity(self) -> bool:
        """Detecta atividade de voz (simples)"""
        try:
            import speech_recognition as sr
            
            # Cria recognizer temporário
            r = sr.Recognizer()
            r.energy_threshold = self.interruption_energy_threshold
            r.pause_threshold = 0.3
            
            with sr.Microphone() as source:
                try:
                    # Escuta muito curto (0.5s)
                    audio = r.listen(source, timeout=0.5, phrase_time_limit=self.interruption_phrase_time_limit)
                    return True  # Detectou voz!
                except sr.WaitTimeoutError:
                    return False  # Silêncio
                    
        except Exception as e:
            return False
    
    def _handle_interruption(self):
        """Lida com interrupção detectada"""
        print(f"\n{Fore.YELLOW}⚡ Interrupção detectada!{Style.RESET_ALL}")
        
        # Para a fala imediatamente
        self.stop_speaking()
        
        # Callback
        if self.on_interrupt_callback:
            try:
                self.on_interrupt_callback()
            except:
                pass
    
    async def speak_with_interruption(self, text: str) -> bool:
        """
        Fala com suporte a interrupção
        Retorna True se completou, False se foi interrompido
        """
        self.is_speaking = True
        self.is_listening_for_interruption = True
        self.interruption_detected = False
        
        # Inicia fala em thread separada
        speak_thread = threading.Thread(target=self.speaker.speak, args=(text,))
        speak_thread.start()
        
        # Aguarda fala terminar ou ser interrompida
        while speak_thread.is_alive():
            if self.interruption_detected:
                # Interrompido!
                self.stop_speaking()
                speak_thread.join(timeout=0.5)
                
                self.is_speaking = False
                self.is_listening_for_interruption = False
                return False  # Interrompido
            
            await asyncio.sleep(0.1)
        
        # Completou sem interrupção
        self.is_speaking = False
        self.is_listening_for_interruption = False
        return True  # Completou
    
    def stop_speaking(self):
        """Para a fala imediatamente"""
        try:
            # Para speaker
            if hasattr(self.speaker, 'stop_speaking'):
                self.speaker.stop_speaking()
            
            # Limpa buffer se possível
            if hasattr(self.speaker, 'clear_queue'):
                self.speaker.clear_queue()
                
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ Erro ao parar fala: {e}{Style.RESET_ALL}")
    
    def set_interrupt_callback(self, callback: Callable):
        """Define callback quando interrupção ocorre"""
        self.on_interrupt_callback = callback


class EnhancedSpeaker:
    """Wrapper para Speaker com suporte a interrupção"""
    
    def __init__(self, original_speaker):
        self.original_speaker = original_speaker
        self.should_stop = False
        self.current_audio_thread = None
        
    def speak(self, text: str):
        """Fala com suporte a parada"""
        self.should_stop = False
        
        # Chama speaker original
        try:
            self.original_speaker.speak(text)
        except Exception as e:
            pass
    
    def stop_speaking(self):
        """Para a fala atual"""
        self.should_stop = True
        
        # Para pygame/audio
        try:
            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.stop()
        except:
            pass
    
    def clear_queue(self):
        """Limpa fila de áudio"""
        self.should_stop = True
        
    # Repassa outros métodos
    def __getattr__(self, name):
        return getattr(self.original_speaker, name)