import pyttsx3
import threading
import time

class Speaker:
    """Sintetiza e reproduz voz"""
    
    def __init__(self):
        self.engine = None
        self.is_speaking = False
        self.voice_rate = 180  # Velocidade
        self.voice_volume = 0.9  # Volume
        self.enabled = True  # NOVO: controle de ativação
        
    def initialize(self):
        """Inicializa o motor TTS"""
        try:
            print("  [VOZ] Inicializando pyttsx3...")
            self.engine = pyttsx3.init()
            
            # Configurações
            self.engine.setProperty('rate', self.voice_rate)
            self.engine.setProperty('volume', self.voice_volume)
            
            # Tenta usar voz feminina em português
            voices = self.engine.getProperty('voices')
            print(f"  [VOZ] Vozes disponíveis: {len(voices)}")
            
            pt_voice_found = False
            for voice in voices:
                voice_name = voice.name.lower()
                if 'portuguese' in voice_name or 'brazil' in voice_name or 'maria' in voice_name:
                    self.engine.setProperty('voice', voice.id)
                    print(f"  [VOZ] ✓ Usando voz: {voice.name}")
                    pt_voice_found = True
                    break
            
            if not pt_voice_found:
                print(f"  [VOZ] ⚠ Voz em português não encontrada, usando padrão")
                # Usa a primeira voz disponível
                if voices:
                    self.engine.setProperty('voice', voices[0].id)
            
            # Teste rápido
            print("  [VOZ] Testando sistema...")
            self.engine.say("Sistema de voz pronto")
            self.engine.runAndWait()
            
            print("  ✓ Sistema de voz pronto")
            self.enabled = True
            return True
            
        except Exception as e:
            print(f"  ⚠ Sistema de voz não disponível: {e}")
            self.enabled = False
            return False
    
    def speak(self, text):
        """Fala o texto (síncrono) - VERSÃO CORRIGIDA"""
        if not self.enabled or not self.engine:
            print(f"  [VOZ DESABILITADA] Texto: {text}")
            return
        
        try:
            # Debug: mostra que está tentando falar
            print(f"\n🔊 [FALANDO] {text[:80]}{'...' if len(text) > 80 else ''}")
            
            self.is_speaking = True
            
            # Limpa a fila antes de falar
            self.engine.stop()
            
            # Fala o texto
            self.engine.say(text)
            self.engine.runAndWait()
            
            self.is_speaking = False
            print(f"✓ [VOZ] Fala concluída\n")
            
        except Exception as e:
            print(f"❌ [VOZ] Erro ao falar: {e}")
            self.is_speaking = False
            
            # Tenta reinicializar
            try:
                print("  [VOZ] Tentando reinicializar...")
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', self.voice_rate)
                self.engine.setProperty('volume', self.voice_volume)
            except:
                print("  [VOZ] Falha ao reinicializar")
                self.enabled = False
    
    def speak_async(self, text):
        """Fala o texto (assíncrono) - VERSÃO CORRIGIDA"""
        if not self.enabled or not self.engine:
            print(f"  [VOZ DESABILITADA] Texto: {text}")
            return
        
        def speak_thread():
            try:
                print(f"\n🔊 [FALANDO ASYNC] {text[:80]}{'...' if len(text) > 80 else ''}")
                
                self.is_speaking = True
                
                # Cria novo engine para thread
                thread_engine = pyttsx3.init()
                thread_engine.setProperty('rate', self.voice_rate)
                thread_engine.setProperty('volume', self.voice_volume)
                
                # Copia configuração de voz do engine principal
                if self.engine:
                    try:
                        voice = self.engine.getProperty('voice')
                        thread_engine.setProperty('voice', voice)
                    except:
                        pass
                
                thread_engine.say(text)
                thread_engine.runAndWait()
                thread_engine.stop()
                
                self.is_speaking = False
                print(f"✓ [VOZ] Fala async concluída\n")
                
            except Exception as e:
                print(f"❌ [VOZ] Erro ao falar async: {e}")
                self.is_speaking = False
        
        thread = threading.Thread(target=speak_thread, daemon=True)
        thread.start()
    
    def stop(self):
        """Para a fala"""
        if self.engine:
            try:
                self.engine.stop()
                self.is_speaking = False
                print("  [VOZ] Parado")
            except:
                pass
    
    def set_rate(self, rate):
        """Define velocidade da voz (100-300)"""
        self.voice_rate = rate
        if self.engine:
            try:
                self.engine.setProperty('rate', rate)
                print(f"  [VOZ] Velocidade alterada para: {rate}")
            except Exception as e:
                print(f"  [VOZ] Erro ao alterar velocidade: {e}")
    
    def set_volume(self, volume):
        """Define volume (0.0 a 1.0)"""
        self.voice_volume = volume
        if self.engine:
            try:
                self.engine.setProperty('volume', volume)
                print(f"  [VOZ] Volume alterado para: {volume}")
            except Exception as e:
                print(f"  [VOZ] Erro ao alterar volume: {e}")
    
    def toggle(self):
        """Liga/desliga a voz"""
        self.enabled = not self.enabled
        status = "ATIVADA" if self.enabled else "DESATIVADA"
        print(f"  [VOZ] {status}")
        return self.enabled
    
    def test_voice(self):
        """Testa o sistema de voz"""
        print("\n🔊 Testando sistema de voz...")
        
        if not self.engine:
            print("❌ Engine não inicializado!")
            return False
        
        try:
            # Lista vozes
            voices = self.engine.getProperty('voices')
            print(f"\nVozes disponíveis: {len(voices)}")
            
            for i, voice in enumerate(voices):
                print(f"  {i+1}. {voice.name}")
            
            # Testa fala
            print("\n🔊 A Mirai vai falar agora...")
            self.speak("Olá! Sou a Mirai! Teste de voz funcionando perfeitamente!")
            
            print("✓ Teste de voz concluído!")
            return True
            
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
            return False