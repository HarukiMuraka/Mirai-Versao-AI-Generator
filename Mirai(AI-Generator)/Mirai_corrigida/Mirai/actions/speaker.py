# actions/speaker.py
import asyncio
import threading
import time
from pathlib import Path


class Speaker:

    def __init__(self):
        self.enabled = True
        self.voice_volume = 0.8
        self.language = "pt-br"
        self.audio_initialized = False
        self.use_edge_tts = False
        self.temp_dir = Path("temp_audio")
        self._pygame = None
        self._gTTS = None

        try:
            import edge_tts  # noqa
            self.use_edge_tts = True
        except ImportError:
            pass

        try:
            import pygame
            self._pygame = pygame
        except ImportError:
            self.enabled = False

        try:
            from gtts import gTTS
            self._gTTS = gTTS
        except ImportError:
            if not self.use_edge_tts:
                self.enabled = False

    # ── initialize() SÍNCRONO ────────────────────────────────────────
    def initialize(self):
        """Inicializa áudio de forma síncrona (compatível com main.py)."""
        self.temp_dir.mkdir(exist_ok=True)

        if self._pygame is None:
            print("  ⚠️  pygame não encontrado — voz desativada")
            self.enabled = False
            return True

        try:
            self._pygame.mixer.init()
            self._pygame.mixer.music.set_volume(self.voice_volume)
            self.audio_initialized = True
        except Exception as e:
            print(f"  ⚠️  Erro ao inicializar áudio: {e}")
            self.audio_initialized = False
            self.enabled = False
            return True

        if self.use_edge_tts:
            print("  ✓ Sistema de voz Edge TTS inicializado")
        elif self._gTTS:
            print("  ✓ Sistema de voz gTTS inicializado")
        else:
            print("  ⚠️  Nenhum TTS disponível — voz desativada")
            self.enabled = False

        return True

    # ── fala síncrona ────────────────────────────────────────────────
    def speak(self, text: str):
        if not self.enabled or not text or not text.strip():
            return
        try:
            if self.use_edge_tts:
                t = threading.Thread(
                    target=self._speak_edge_threaded, args=(text,), daemon=False
                )
                t.start()
                t.join()
            elif self._gTTS:
                self._speak_gtts(text)
        except Exception as e:
            print(f"  ⚠️  Erro na voz: {e}")

    def _speak_edge_threaded(self, text: str):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._speak_edge_async(text))
        finally:
            loop.close()

    async def _speak_edge_async(self, text: str):
        try:
            import edge_tts
            text = text.replace("*", "").replace("_", "")[:500]
            audio_file = self.temp_dir / f"edge_{int(time.time()*1000)}.mp3"
            comm = edge_tts.Communicate(text, "pt-BR-FranciscaNeural")
            await comm.save(str(audio_file))
            self._play_and_wait(audio_file)
        except Exception as e:
            print(f"  ⚠️  Edge TTS erro: {e}")
            if self._gTTS:
                self._speak_gtts(text)

    def _speak_gtts(self, text: str):
        try:
            text = text[:500]
            audio_file = self.temp_dir / f"gtts_{int(time.time()*1000)}.mp3"
            tts = self._gTTS(text=text, lang=self.language, slow=False)
            tts.save(str(audio_file))
            self._play_and_wait(audio_file)
        except Exception as e:
            print(f"  ⚠️  gTTS erro: {e}")

    def _play_and_wait(self, audio_file: Path):
        if not self.audio_initialized or self._pygame is None:
            return
        try:
            self._pygame.mixer.music.load(str(audio_file))
            self._pygame.mixer.music.set_volume(self.voice_volume)
            self._pygame.mixer.music.play()
            while self._pygame.mixer.music.get_busy():
                self._pygame.time.Clock().tick(10)
        except Exception:
            pass
        finally:
            try:
                time.sleep(0.1)
                audio_file.unlink(missing_ok=True)
            except Exception:
                pass

    # ── fala assíncrona ──────────────────────────────────────────────
    async def speak_async(self, text: str):
        if not self.enabled or not text or not text.strip():
            return
        fn = self._speak_edge_threaded if self.use_edge_tts else self._speak_gtts
        t = threading.Thread(target=fn, args=(text,), daemon=True)
        t.start()

    # ── utilitários ──────────────────────────────────────────────────
    def set_volume(self, volume: float):
        self.voice_volume = max(0.0, min(1.0, volume))
        if self.audio_initialized and self._pygame:
            self._pygame.mixer.music.set_volume(self.voice_volume)

    def stop(self):
        if self.audio_initialized and self._pygame:
            try:
                self._pygame.mixer.music.stop()
            except Exception:
                pass

    def shutdown(self):
        if self.audio_initialized and self._pygame:
            try:
                self._pygame.mixer.music.stop()
                self._pygame.mixer.quit()
            except Exception:
                pass
        print("  ✓ Sistema de voz encerrado")