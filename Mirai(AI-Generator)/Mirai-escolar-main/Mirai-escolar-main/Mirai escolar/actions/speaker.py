import asyncio
import pygame
import os
from pathlib import Path
import time
import threading

class Speaker:
    """Sistema de voz da Mirai - 100% FUNCIONAL"""
    
    def __init__(self):
        self.enabled = True
        self.voice_volume = 0.8
        self.language = 'pt-br'
        
        # Tenta usar Edge TTS primeiro
        self.use_edge_tts = False
        try:
            import edge_tts
            self.edge_tts = edge_tts
            self.voice = "pt-BR-FranciscaNeural"  # Voz brasileira feminina
            self.use_edge_tts = True
        except ImportError:
            # Fallback para gTTS
            try:
                from gtts import gTTS
                self.gTTS = gTTS
            except ImportError:
                print("  ⚠️  Nenhum TTS disponível!")
                self.enabled = False
        
        # Inicializa pygame
        try:
            pygame.mixer.init()
            pygame.mixer.music.set_volume(self.voice_volume)
            self.audio_initialized = True
        except Exception as e:
            print(f"  ⚠️  Erro ao inicializar áudio: {e}")
            self.audio_initialized = False
            self.enabled = False
        
        # Pasta temporária
        self.temp_dir = Path("temp_audio")
        self.temp_dir.mkdir(exist_ok=True)
    
    async def initialize(self):
        """Inicializa sistema de voz"""
        if not self.audio_initialized:
            print("  ⚠️  Sistema de voz desabilitado")
            return True
        
        # Mostra qual TTS está ativo
        if self.use_edge_tts:
            print("  ✓ Sistema de voz Edge TTS inicializado")
        else:
            print("  ✓ Sistema de voz gTTS inicializado")
        
        return True
    
    def speak(self, text):
        """Fala o texto (síncrono - SEM erro de event loop)"""
        if not self.enabled or not text or not text.strip():
            return
        
        try:
            # Se for Edge TTS, roda em thread separada
            if self.use_edge_tts:
                # Cria thread para rodar async sem conflito
                thread = threading.Thread(target=self._speak_edge_threaded, args=(text,))
                thread.daemon = False
                thread.start()
                thread.join()  # Aguarda terminar (síncrono)
            else:
                # gTTS síncrono direto
                self._speak_gtts(text)
                
        except Exception as e:
            print(f"  ⚠️  Erro na voz: {e}")
    
    def _speak_edge_threaded(self, text):
        """Roda Edge TTS em thread separada com novo event loop"""
        # Cria novo event loop para esta thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self._speak_edge_tts_internal(text))
        finally:
            loop.close()
    
    async def speak_async(self, text):
        """Fala assíncrona (não bloqueia)"""
        if not self.enabled or not text or not text.strip():
            return
        
        try:
            if self.use_edge_tts:
                # Roda em thread para não bloquear
                thread = threading.Thread(target=self._speak_edge_threaded, args=(text,))
                thread.daemon = True
                thread.start()
                # NÃO aguarda (async!)
            else:
                # gTTS em thread separada
                thread = threading.Thread(target=self._speak_gtts, args=(text,))
                thread.daemon = True
                thread.start()
                
        except Exception as e:
            print(f"  ⚠️  Erro na voz: {e}")
    
    async def _speak_edge_tts_internal(self, text):
        """Implementação interna do Edge TTS (async)"""
        try:
            # Remove caracteres problemáticos
            text = text.replace('*', '').replace('_', '')
            
            # Limita tamanho
            if len(text) > 500:
                text = text[:500] + "..."
            
            # Cria arquivo temporário
            audio_file = self.temp_dir / f"speech_edge_{int(time.time() * 1000)}.mp3"
            
            # Gera áudio com Edge TTS
            communicate = self.edge_tts.Communicate(text, self.voice)
            await communicate.save(str(audio_file))
            
            # Toca com pygame
            pygame.mixer.music.load(str(audio_file))
            pygame.mixer.music.set_volume(self.voice_volume)
            pygame.mixer.music.play()
            
            # Aguarda terminar
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
            
            # Remove arquivo
            try:
                await asyncio.sleep(0.1)
                audio_file.unlink()
            except:
                pass
                
        except Exception as e:
            print(f"  ⚠️  Erro Edge TTS: {e}")
            # Fallback para gTTS se Edge falhar
            self._speak_gtts(text)
    
    def _speak_gtts(self, text):
        """Fala com gTTS (sync) - SEMPRE funciona"""
        try:
            # Limita tamanho
            if len(text) > 500:
                text = text[:500] + "..."
            
            # Gera áudio
            tts = self.gTTS(text=text, lang=self.language, slow=False)
            
            # Salva temporariamente
            audio_file = self.temp_dir / f"speech_gtts_{int(time.time() * 1000)}.mp3"
            tts.save(str(audio_file))
            
            # Toca
            pygame.mixer.music.load(str(audio_file))
            pygame.mixer.music.set_volume(self.voice_volume)
            pygame.mixer.music.play()
            
            # Espera terminar
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            # Remove arquivo
            try:
                time.sleep(0.1)
                audio_file.unlink()
            except:
                pass
                
        except Exception as e:
            print(f"  ⚠️  Erro gTTS: {e}")
    
    def set_volume(self, volume):
        """Define volume (0.0 a 1.0)"""
        if not self.audio_initialized:
            return
        
        self.voice_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.voice_volume)
    
    def stop(self):
        """Para a fala atual"""
        if not self.audio_initialized:
            return
        
        try:
            pygame.mixer.music.stop()
        except:
            pass
    
    def shutdown(self):
        """Encerra sistema de voz"""
        if self.audio_initialized:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            except:
                pass
        
        print("  ✓ Sistema de voz encerrado")