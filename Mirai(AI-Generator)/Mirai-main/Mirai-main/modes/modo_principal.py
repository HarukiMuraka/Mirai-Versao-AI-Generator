"""
modes/modo_principal.py — Modo Principal Unificado (CORRIGIDO)
- Removidos imports mirai.*
- pytesseract, cv2, PIL opcionais
- generate_response async
- VoiceListener e TextInput opcionais com fallback
"""
import asyncio, subprocess, threading, os, platform
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style

try: import pyautogui; _GUI = True
except: _GUI = False

try: import pytesseract; from PIL import Image; _OCR = True
except: _OCR = False

try: import cv2, numpy as np; _CV = True
except: _CV = False

def _setup_tesseract():
    if not _OCR: return
    for p in [r"C:\Program Files\Tesseract-OCR\tesseract.exe",
              r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
              "/usr/bin/tesseract", "/usr/local/bin/tesseract"]:
        if Path(p).exists():
            pytesseract.pytesseract.tesseract_cmd = p; return

_setup_tesseract()

def _inp(prompt):
    try: return input(prompt).strip()
    except: return ""

class ModoPrincipal:
    def __init__(self, mirai_instance):
        self.mirai   = mirai_instance
        self.ai      = mirai_instance.ai
        self.context = mirai_instance.context
        self.state   = mirai_instance.state
        self.vtuber  = mirai_instance.vtuber
        self.speaker = mirai_instance.speaker
        self.is_active = False

        # Voz (opcional)
        self._voice = None
        try:
            from perception.voice_listener import VoiceListener
            self._voice = VoiceListener()
        except ImportError:
            pass

        # RetroArch
        self.retroarch = self._find_retroarch()
        self.roms_path = Path("roms")

    def _find_retroarch(self):
        for p in ["C:/RetroArch/retroarch.exe",
                  os.path.expanduser("~/RetroArch/retroarch.exe"),
                  "/usr/bin/retroarch"]:
            if os.path.exists(p): return p
        return None

    async def enter(self):
        self.is_active = True
        if self.state: self.state.set_state("principal")
        self._header()
        await self._menu()

    async def exit(self):
        self.is_active = False

    def _header(self):
        print(f"\n{Fore.MAGENTA}╔══════════════════════════════════╗")
        print(f"║    🌸 MIRAI — MODO PRINCIPAL 🌸  ║")
        print(f"╚══════════════════════════════════╝{Style.RESET_ALL}\n")

    async def _menu(self):
        while self.is_active:
            print(f"\n{Fore.CYAN}{'═'*52}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}O que você gostaria de fazer?{Style.RESET_ALL}\n")
            print(f"{Fore.CYAN}💬 CONVERSA:{Style.RESET_ALL}")
            print("  1. Por texto   2. Por voz   3. Autônoma")
            print(f"\n{Fore.CYAN}👁 TELA:{Style.RESET_ALL}")
            print("  4. Analisar tela   5. Monitoramento contínuo   6. OCR (ler texto)")
            print(f"\n{Fore.CYAN}🎮 JOGOS:{Style.RESET_ALL}")
            print("  7. RetroArch")
            print(f"\n{Fore.CYAN}🤖 ASSISTENTE:{Style.RESET_ALL}")
            print("  8. Abrir app   9. Pesquisar   10. Criar conteúdo")
            print(f"\n{Fore.CYAN}🎤 VOZ:{Style.RESET_ALL}")
            print("  11. Modo mãos-livres")
            print(f"\n{Fore.RED}  0. Voltar{Style.RESET_ALL}")
            c = _inp(f"\n{Fore.GREEN}Escolha (0-11): {Style.RESET_ALL}")
            if   c == "1":  await self._texto()
            elif c == "2":  await self._voz()
            elif c == "3":  await self._autonomo()
            elif c == "4":  await self._analisar()
            elif c == "5":  await self._monitorar()
            elif c == "6":  await self._ocr()
            elif c == "7":  await self._jogos()
            elif c == "8":  await self._app()
            elif c == "9":  await self._pesquisar()
            elif c == "10": await self._criar()
            elif c == "11": await self._maos_livres()
            elif c == "0":  break

    # ── conversa ──────────────────────────────────────────────────

    async def _texto(self):
        print(f"\n{Fore.GREEN}💬 Conversa por Texto — 'sair' para voltar{Style.RESET_ALL}\n")
        while True:
            ui = _inp(f"{Fore.CYAN}Você: {Style.RESET_ALL}")
            if not ui or ui.lower() in ("sair","voltar"): break
            r = await self._processar(ui)
            print(f"{Fore.MAGENTA}Mirai: {r}{Style.RESET_ALL}\n")
            self._speak(r)

    async def _voz(self):
        if not self._voice:
            print(f"{Fore.RED}Microfone não disponível.{Style.RESET_ALL}"); return
        if not self._voice.initialize(): return
        print(f"\n{Fore.GREEN}🎤 Conversa por Voz — diga 'sair' para voltar{Style.RESET_ALL}\n")
        while True:
            t = self._voice.listen_once()
            if not t: continue
            if t.lower() in ("sair","parar"): break
            print(f"{Fore.CYAN}Você: {t}{Style.RESET_ALL}")
            r = await self._processar(t)
            print(f"{Fore.MAGENTA}Mirai: {r}{Style.RESET_ALL}\n")
            self._speak(r)

    async def _autonomo(self):
        print(f"\n{Fore.GREEN}🤖 Modo Autônomo — Ctrl+C para sair{Style.RESET_ALL}\n")
        self._speak("Modo autônomo ativado!")
        try:
            while True:
                await asyncio.sleep(5)
                if self.ai.should_take_initiative():
                    msg = self.ai.generate_initiative()
                    print(f"\n{Fore.MAGENTA}Mirai: {msg}{Style.RESET_ALL}\n")
                    self._speak(msg)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Encerrado.{Style.RESET_ALL}")

    # ── tela ──────────────────────────────────────────────────────

    async def _analisar(self):
        if not _GUI: print(f"{Fore.RED}pyautogui não instalado.{Style.RESET_ALL}"); return
        print(f"{Fore.CYAN}📸 Capturando em 2s...{Style.RESET_ALL}")
        await asyncio.sleep(2)
        try:
            ss = pyautogui.screenshot()
            texto = ""
            if _OCR:
                texto = pytesseract.image_to_string(ss, lang="por+eng")[:400]
            if texto.strip():
                r = await self._processar(f"Texto detectado na tela:\n{texto}\n\nO que o usuário faz?")
            else:
                r = "Não detectei texto na tela."
            print(f"\n{Fore.MAGENTA}Mirai: {r}{Style.RESET_ALL}")
            self._speak(r)
        except Exception as e:
            print(f"{Fore.RED}Erro: {e}{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Enter...{Style.RESET_ALL}")

    async def _monitorar(self):
        if not _GUI: print(f"{Fore.RED}pyautogui não instalado.{Style.RESET_ALL}"); return
        try:
            intervalo = int(_inp("Intervalo em segundos [30]: ") or "30")
        except: intervalo = 30
        print(f"{Fore.GREEN}Monitoramento ativo (Ctrl+C para parar){Style.RESET_ALL}\n")
        count = 0
        try:
            while True:
                count += 1
                ss = pyautogui.screenshot()
                texto = pytesseract.image_to_string(ss, lang="por+eng") if _OCR else ""
                palavras = len(texto.split())
                print(f"{Fore.CYAN}[{datetime.now().strftime('%H:%M:%S')}] #{count} | {palavras} palavras{Style.RESET_ALL}")
                await asyncio.sleep(intervalo)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}✓ Encerrado.{Style.RESET_ALL}")

    async def _ocr(self):
        if not _GUI or not _OCR:
            print(f"{Fore.RED}pyautogui/pytesseract não instalados.{Style.RESET_ALL}"); return
        print(f"{Fore.CYAN}📝 Leitura OCR — capturando em 2s...{Style.RESET_ALL}")
        await asyncio.sleep(2)
        try:
            ss    = pyautogui.screenshot()
            texto = pytesseract.image_to_string(ss, lang="por+eng")
            if texto.strip():
                linhas = [l.strip() for l in texto.split("\n") if l.strip()]
                print(f"\n{Fore.GREEN}{len(linhas)} linhas detectadas:{Style.RESET_ALL}\n")
                for i, l in enumerate(linhas[:25], 1):
                    print(f"{i:2d}. {l}")
                Path("texto_extraido.txt").write_text(texto, encoding="utf-8")
                print(f"\n{Fore.GREEN}✓ Salvo: texto_extraido.txt{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Nenhum texto detectado.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Erro: {e}{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Enter...{Style.RESET_ALL}")

    # ── jogos ─────────────────────────────────────────────────────

    async def _jogos(self):
        if not self.retroarch:
            print(f"{Fore.RED}RetroArch não encontrado.{Style.RESET_ALL}")
            input("Enter..."); return
        roms = self._list_roms()
        if not roms:
            print(f"{Fore.YELLOW}Nenhuma ROM encontrada em: {self.roms_path}{Style.RESET_ALL}")
            input("Enter..."); return
        print(f"\n{Fore.CYAN}🎮 JOGOS:{Style.RESET_ALL}\n")
        for i, r in enumerate(roms, 1):
            print(f"  {i}. [{r['console'].upper()}] {r['name']}")
        c = _inp(f"\n{Fore.GREEN}Jogo: {Style.RESET_ALL}")
        if c.isdigit():
            idx = int(c) - 1
            if 0 <= idx < len(roms): await self._launch(roms[idx])

    def _list_roms(self):
        cores = {"nes":"fceumm_libretro.dll","snes":"snes9x_libretro.dll",
                 "gba":"mgba_libretro.dll","n64":"mupen64plus_next_libretro.dll"}
        roms = []
        for console, core in cores.items():
            p = self.roms_path / console
            if p.exists():
                for rom in p.glob("*.*"):
                    roms.append({"console":console,"name":rom.stem,"path":str(rom),"core":core})
        return sorted(roms, key=lambda x: x["name"])

    async def _launch(self, game):
        print(f"\n{Fore.CYAN}🎮 Iniciando {game['name']}...{Style.RESET_ALL}")
        self._speak(f"Iniciando {game['name']}!")
        try:
            proc = subprocess.Popen([self.retroarch, "-L", game["core"], game["path"]],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            await asyncio.sleep(3)
            if proc.poll() is None:
                print(f"{Fore.GREEN}✓ Rodando!{Style.RESET_ALL}")
                proc.wait()
                print(f"{Fore.YELLOW}Jogo encerrado.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Erro: {e}{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Enter...{Style.RESET_ALL}")

    # ── assistente ────────────────────────────────────────────────

    async def _app(self):
        print(f"\n{Fore.CYAN}🚀 Abrir App{Style.RESET_ALL}\n")
        app = _inp(f"{Fore.GREEN}Nome do app: {Style.RESET_ALL}")
        if app:
            try: subprocess.Popen([app], shell=True); print(f"{Fore.GREEN}✓ Abrindo {app}{Style.RESET_ALL}")
            except Exception as e: print(f"{Fore.RED}Erro: {e}{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Enter...{Style.RESET_ALL}")

    async def _pesquisar(self):
        q = _inp(f"\n{Fore.GREEN}Pesquisar: {Style.RESET_ALL}")
        if q:
            r = await self._processar(f"Pesquise sobre: {q}")
            print(f"\n{Fore.MAGENTA}Mirai: {r}{Style.RESET_ALL}\n")
            self._speak(r[:150])
        input(f"\n{Fore.CYAN}Enter...{Style.RESET_ALL}")

    async def _criar(self):
        topic = _inp(f"\n{Fore.GREEN}Sobre o quê? {Style.RESET_ALL}")
        if topic:
            r = await self._processar(f"Crie um texto interessante sobre: {topic}")
            print(f"\n{Fore.MAGENTA}{r}{Style.RESET_ALL}\n")
        input(f"\n{Fore.CYAN}Enter...{Style.RESET_ALL}")

    # ── mãos-livres ───────────────────────────────────────────────

    async def _maos_livres(self):
        if not self._voice:
            print(f"{Fore.RED}Microfone não disponível.{Style.RESET_ALL}"); return
        if not self._voice.initialize(): return
        print(f"\n{Fore.GREEN}🎤 Mãos-Livres — diga 'Mirai' para ativar. 'parar' para sair.{Style.RESET_ALL}\n")
        self._speak("Modo mãos-livres! Diga Mirai para ativar.")
        try:
            while True:
                t = self._voice.listen_once_silent() if hasattr(self._voice, "listen_once_silent") else self._voice.listen_once()
                if not t: continue
                if any(w in t.lower() for w in ["mirai","hey mirai"]):
                    self._speak("Oi!")
                    cmd = self._voice.listen_once()
                    if cmd:
                        if cmd.lower() in ("parar","sair"): self._speak("Desativando!"); break
                        print(f"{Fore.CYAN}Você: {cmd}{Style.RESET_ALL}")
                        r = await self._processar(cmd)
                        print(f"{Fore.MAGENTA}Mirai: {r}{Style.RESET_ALL}\n")
                        self._speak(r)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Encerrado.{Style.RESET_ALL}")

    # ── helpers ───────────────────────────────────────────────────

    async def _processar(self, text: str) -> str:
        if self.context: self.context.add_message("user", text)
        r = await self.ai.generate_response(text)
        if self.context: self.context.add_message("assistant", r)
        return r

    def _speak(self, text: str):
        if self.speaker and self.speaker.enabled:
            try: self.speaker.speak(text[:200])
            except Exception: pass