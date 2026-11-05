from mirai.modes.base_mode import BaseMode
from mirai.perception.text_input import TextInput
from colorama import Fore, Style
import asyncio
import os
import subprocess
import time
from pathlib import Path

class GamerMode(BaseMode):
    """Modo Gamer MELHORADO - RetroArch + Citra (3DS)"""
    
    def __init__(self, mirai_instance):
        super().__init__(mirai_instance)
        
        # RetroArch
        self.retroarch_path = self._find_retroarch()
        self.roms_path = Path("C:/Mirai/roms")
        
        # Cores suportados (emuladores RetroArch)
        self.cores_config = {
            'nes': 'fceumm_libretro.dll',
            'snes': 'snes9x_libretro.dll',
            'gba': 'mgba_libretro.dll',
            'n64': 'mupen64plus_next_libretro.dll',
            'ps1': 'pcsx_rearmed_libretro.dll',
            'genesis': 'genesis_plus_gx_libretro.dll'
        }
        
        # Citra (emulador de 3DS standalone)
        self.citra_path = self._find_citra()
        self.citra_roms_path = Path("C:/Mirai/roms/3ds")
        
        self.current_game = None
        self.game_process = None
    
    def _find_retroarch(self):
        """Procura RetroArch instalado"""
        paths = [
            "C:/RetroArch/retroarch.exe",
            "C:/Program Files/RetroArch/retroarch.exe",
            "C:/Program Files (x86)/RetroArch/retroarch.exe",
            os.path.expanduser("~/RetroArch/retroarch.exe")
        ]
        
        for path in paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _find_citra(self):
        """Procura Citra instalado"""
        paths = [
            "C:/Program Files/Citra/citra-qt.exe",
            "C:/Program Files (x86)/Citra/citra-qt.exe",
            "C:/Citra/citra-qt.exe",
            os.path.expanduser("~/Citra/citra-qt.exe")
        ]
        
        for path in paths:
            if os.path.exists(path):
                return path
        
        return None
    
    async def enter(self):
        self.is_active = True
        self.state.set_state("gamer")
        self.print_mode_header("MODO GAMER - RETROARCH + CITRA")
        
        print(f"{Fore.GREEN}Yatta! Modo gamer ativado! 🎮{Style.RESET_ALL}\n")
        
        # Verifica emuladores
        print(f"{Fore.CYAN}{'='*60}")
        print(f"EMULADORES DETECTADOS:")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        if self.retroarch_path:
            print(f"{Fore.GREEN}✓ RetroArch: {self.retroarch_path}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}✗ RetroArch não encontrado{Style.RESET_ALL}")
            print(f"{Fore.CYAN}  Baixe em: https://www.retroarch.com{Style.RESET_ALL}")
        
        if self.citra_path:
            print(f"{Fore.GREEN}✓ Citra (3DS): {self.citra_path}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}✗ Citra não encontrado{Style.RESET_ALL}")
            print(f"{Fore.CYAN}  Baixe em: https://citra-emu.org{Style.RESET_ALL}")
        
        print()
        
        await self.show_gamer_menu()
    
    async def exit(self):
        self.is_active = False
        
        # Fecha jogo se estiver rodando
        if self.game_process:
            self.game_process.terminate()
            self.game_process = None
        
        print(f"\n{Fore.CYAN}Saindo do modo gamer...{Style.RESET_ALL}")
    
    async def process_input(self, user_input):
        return self.ai.generate_response(user_input, mode="gamer")
    
    async def show_gamer_menu(self):
        """Menu principal gamer"""
        while self.is_active:
            print(f"\n{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}🎮 MODO GAMER{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}\n")
            
            print("1. 🕹️  Jogar (RetroArch - NES/SNES/GBA/N64/PS1)")
            print("2. 🎮 Jogar 3DS (Citra)")
            print("3. 💬 Chat da Live")
            print("4. 😊 Teste de Reações")
            print("0. ⬅️  Voltar")
            
            choice = input(f"\n{Fore.GREEN}Opção: {Style.RESET_ALL}")
            
            if choice == "1":
                await self.play_retro_games()
            elif choice == "2":
                await self.play_3ds_games()
            elif choice == "3":
                await self.chat_mode()
            elif choice == "4":
                await self.test_reactions()
            elif choice == "0":
                break
    
    async def play_retro_games(self):
        """Sistema de jogos retrô (RetroArch)"""
        if not self.retroarch_path:
            print(f"\n{Fore.RED}❌ RetroArch não instalado!{Style.RESET_ALL}")
            self.speaker.speak("Precisa instalar o RetroArch primeiro!")
            input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
            return
        
        # Lista ROMs
        roms = self._list_retro_roms()
        
        if not roms:
            print(f"\n{Fore.YELLOW}📂 Nenhuma ROM encontrada!{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}Coloque suas ROMs em:{Style.RESET_ALL}")
            print(f"  {self.roms_path}/")
            print(f"    ├── nes/     (jogos .nes)")
            print(f"    ├── snes/    (jogos .smc, .sfc)")
            print(f"    ├── gba/     (jogos .gba)")
            print(f"    ├── n64/     (jogos .n64, .z64)")
            print(f"    ├── ps1/     (jogos .bin, .cue)")
            print(f"    └── genesis/ (jogos .md, .gen)\n")
            
            self.speaker.speak("Não achei nenhum jogo! Coloca umas ROMs aí!")
            input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
            return
        
        # Mostra lista
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}🎮 JOGOS DISPONÍVEIS (RetroArch){Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        for i, rom in enumerate(roms, 1):
            console = rom['console'].upper()
            name = rom['name']
            print(f"  {i}. [{console:8s}] {name}")
        
        print(f"\n  0. Voltar")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.GREEN}Escolha um jogo: {Style.RESET_ALL}").strip()
        
        if choice == '0':
            return
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(roms):
                await self.launch_retro_game(roms[idx])
            else:
                print(f"{Fore.RED}Número inválido!{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Digite um número!{Style.RESET_ALL}")
    
    async def play_3ds_games(self):
        """Sistema de jogos 3DS (Citra) - NOVO!"""
        if not self.citra_path:
            print(f"\n{Fore.RED}❌ Citra não instalado!{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}Instalação do Citra:{Style.RESET_ALL}")
            print(f"  1. Baixe em: https://citra-emu.org")
            print(f"  2. Instale em C:/Program Files/Citra")
            print(f"  3. Configure controles e gráficos")
            print(f"  4. Coloque ROMs .3ds em C:/Mirai/roms/3ds\n")
            
            self.speaker.speak("Citra não está instalado! Baixe no site oficial!")
            input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
            return
        
        # Cria diretório de ROMs se não existir
        self.citra_roms_path.mkdir(parents=True, exist_ok=True)
        
        # Lista ROMs de 3DS
        roms = list(self.citra_roms_path.glob("*.3ds")) + \
               list(self.citra_roms_path.glob("*.cia"))
        
        if not roms:
            print(f"\n{Fore.YELLOW}📂 Nenhum jogo de 3DS encontrado!{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}Coloque seus jogos em:{Style.RESET_ALL}")
            print(f"  {self.citra_roms_path}/")
            print(f"  Formatos: .3ds, .cia\n")
            print(f"{Fore.YELLOW}⚠️  IMPORTANTE:{Style.RESET_ALL}")
            print(f"  • Use apenas ROMs que você possui")
            print(f"  • Jogos de 3DS precisam ser descriptografados")
            print(f"  • Configure o Citra antes (System > Configure)\n")
            
            self.speaker.speak("Não achei jogos de 3DS! Coloca alguns arquivos ponto 3ds!")
            input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
            return
        
        # Mostra lista
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}🎮 JOGOS DE NINTENDO 3DS (Citra){Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        for i, rom in enumerate(roms, 1):
            name = rom.stem
            ext = rom.suffix
            print(f"  {i}. [{ext:5s}] {name}")
        
        print(f"\n  0. Voltar")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.GREEN}Escolha um jogo: {Style.RESET_ALL}").strip()
        
        if choice == '0':
            return
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(roms):
                await self.launch_citra_game(roms[idx])
            else:
                print(f"{Fore.RED}Número inválido!{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Digite um número!{Style.RESET_ALL}")
    
    def _list_retro_roms(self):
        """Lista ROMs do RetroArch"""
        roms = []
        
        if not self.roms_path.exists():
            self.roms_path.mkdir(parents=True, exist_ok=True)
            return roms
        
        extensions = {
            'nes': ['.nes'],
            'snes': ['.smc', '.sfc'],
            'gba': ['.gba'],
            'n64': ['.n64', '.z64'],
            'ps1': ['.bin', '.cue', '.iso'],
            'genesis': ['.md', '.gen']
        }
        
        for console, exts in extensions.items():
            console_path = self.roms_path / console
            if console_path.exists():
                for ext in exts:
                    for rom in console_path.glob(f"*{ext}"):
                        roms.append({
                            'console': console,
                            'name': rom.stem,
                            'path': str(rom),
                            'core': self.cores_config[console]
                        })
        
        return sorted(roms, key=lambda x: (x['console'], x['name']))
    
    async def launch_retro_game(self, game):
        """Inicia jogo no RetroArch"""
        self.current_game = game
        
        print(f"\n{Fore.CYAN}🎮 Iniciando: {game['name']} ({game['console'].upper()}){Style.RESET_ALL}")
        self.speaker.speak(f"Iniciando {game['name']}! Bora jogar!")
        
        print(f"{Fore.YELLOW}⏳ Carregando...{Style.RESET_ALL}\n")
        
        try:
            # Comando RetroArch
            cmd = [
                self.retroarch_path,
                "-L", game['core'],
                game['path']
            ]
            
            # Inicia jogo
            self.game_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            await asyncio.sleep(3)
            
            if self.game_process.poll() is None:
                print(f"{Fore.GREEN}✓ Jogo iniciado!{Style.RESET_ALL}")
                self.speaker.speak("Jogo carregado! Vamos nessa!")
                
                await self.gameplay_interaction()
            else:
                print(f"{Fore.RED}❌ Jogo fechou inesperadamente{Style.RESET_ALL}")
                self.speaker.speak("Eita, o jogo fechou!")
        
        except Exception as e:
            print(f"{Fore.RED}❌ Erro ao iniciar: {e}{Style.RESET_ALL}")
            self.speaker.speak("Deu ruim ao abrir o jogo!")
    
    async def launch_citra_game(self, rom_path):
        """Inicia jogo no Citra - NOVO!"""
        game_name = rom_path.stem
        
        print(f"\n{Fore.CYAN}🎮 Iniciando: {game_name} (Nintendo 3DS){Style.RESET_ALL}")
        self.speaker.speak(f"Iniciando {game_name} no Citra! Bora jogar 3DS!")
        
        print(f"{Fore.YELLOW}⏳ Carregando Citra...{Style.RESET_ALL}\n")
        
        try:
            # Comando Citra
            cmd = [
                self.citra_path,
                str(rom_path)
            ]
            
            # Inicia jogo
            self.game_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            await asyncio.sleep(5)  # Citra demora um pouco mais
            
            if self.game_process.poll() is None:
                print(f"{Fore.GREEN}✓ Citra iniciado!{Style.RESET_ALL}")
                print(f"\n{Fore.CYAN}💡 DICAS CITRA:{Style.RESET_ALL}")
                print(f"  • Use F11 para tela cheia")
                print(f"  • Emulation > Configure para controles")
                print(f"  • View > Screen Layout para mudar layout")
                print(f"  • Salve com File > Save State\n")
                
                self.speaker.speak("Citra carregado! Divirta-se!")
                
                self.current_game = {'name': game_name, 'console': '3ds'}
                await self.gameplay_interaction()
            else:
                print(f"{Fore.RED}❌ Citra fechou inesperadamente{Style.RESET_ALL}")
                print(f"\n{Fore.YELLOW}Possíveis causas:{Style.RESET_ALL}")
                print(f"  • ROM corrompida ou inválida")
                print(f"  • Jogo precisa ser descriptografado")
                print(f"  • Falta configuração no Citra")
                
                self.speaker.speak("Eita, o Citra fechou!")
        
        except Exception as e:
            print(f"{Fore.RED}❌ Erro ao iniciar: {e}{Style.RESET_ALL}")
            self.speaker.speak("Erro ao abrir o Citra!")
    
    async def gameplay_interaction(self):
        """Interação durante gameplay"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}🎮 JOGANDO: {self.current_game['name']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        print("Comandos:")
        print("  'c' - Comentar sobre o jogo")
        print("  'p' - Pausar e conversar")
        print("  'q' - Sair do jogo")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        text_input = TextInput()
        
        while self.game_process and self.game_process.poll() is None:
            try:
                # Input não-bloqueante
                print(f"{Fore.GREEN}> {Style.RESET_ALL}", end='', flush=True)
                
                cmd = await asyncio.wait_for(
                    asyncio.to_thread(text_input.get_input, ""),
                    timeout=5.0
                )
                
                cmd = cmd.strip().lower()
                
                if cmd == 'q':
                    await self.quit_game()
                    break
                
                elif cmd == 'c':
                    await self.comment_gameplay()
                
                elif cmd == 'p':
                    await self.pause_and_chat()
                
                elif cmd:
                    # Conversa normal
                    response = self.ai.generate_response(cmd, mode="gamer")
                    print(f"{Fore.MAGENTA}Mirai: {response}{Style.RESET_ALL}\n")
                    await self.speaker.speak_async(response)
            
            except asyncio.TimeoutError:
                continue
            
            except KeyboardInterrupt:
                await self.quit_game()
                break
        
        if self.game_process and self.game_process.poll() is not None:
            print(f"\n{Fore.YELLOW}Jogo encerrado!{Style.RESET_ALL}")
            self.current_game = None
            self.game_process = None
    
    async def comment_gameplay(self):
        """Comenta sobre o jogo"""
        comments = [
            "Tá indo bem! Sugoi! ✨",
            "Esse jogo é muito bom, ne~",
            "Você joga bem! Ganbatte!",
            "Cuidado! Olha ali!",
            "Yatta! Conseguimos!",
            "Esse level tá difícil, hein? 😅",
            "Dahora! Continua assim!",
            "Que nostalgia, né? ❤️",
            "Esse boss é brabo!",
            "Salva o jogo, não esquece!"
        ]
        
        import random
        comment = random.choice(comments)
        print(f"\n{Fore.MAGENTA}Mirai: {comment}{Style.RESET_ALL}\n")
        self.speaker.speak(comment)
    
    async def pause_and_chat(self):
        """Pausa para conversar"""
        print(f"\n{Fore.CYAN}💬 PAUSADO - Bora conversar!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}(Digite 'voltar' para continuar jogando){Style.RESET_ALL}\n")
        
        self.speaker.speak("Vamos conversar um pouco?")
        
        text_input = TextInput()
        
        while True:
            user_msg = text_input.get_input(f"{Fore.GREEN}Você: {Style.RESET_ALL}")
            
            if not user_msg or user_msg.lower() in ['voltar', 'jogar', 'continuar']:
                self.speaker.speak("Beleza! Vamos voltar pro jogo!")
                print(f"\n{Fore.GREEN}Voltando ao jogo...{Style.RESET_ALL}\n")
                break
            
            response = self.ai.generate_response(user_msg, mode="gamer")
            print(f"{Fore.MAGENTA}Mirai: {response}{Style.RESET_ALL}\n")
            await self.speaker.speak_async(response)
    
    async def quit_game(self):
        """Encerra o jogo"""
        if self.game_process:
            self.game_process.terminate()
            self.game_process = None
        
        print(f"\n{Fore.GREEN}✓ Jogo encerrado{Style.RESET_ALL}")
        self.speaker.speak("Jogo encerrado! Foi divertido!")
        
        self.current_game = None
    
    async def chat_mode(self):
        """Modo chat de live"""
        print(f"\n{Fore.GREEN}💬 Chat da Live Ativado!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}(Digite 'sair' para voltar){Style.RESET_ALL}\n")
        
        text_input = TextInput()
        
        print(f"{Fore.MAGENTA}Mirai: Olá chat! Como estão? 😊{Style.RESET_ALL}")
        self.speaker.speak("Olá chat! Como estão?")
        
        while True:
            user_input = text_input.get_input(f"{Fore.CYAN}[Chat]: {Style.RESET_ALL}")
            
            if not user_input or user_input.lower() == 'sair':
                break
            
            response = await self.process_chat_message(user_input)
            
            print(f"{Fore.MAGENTA}Mirai: {response}{Style.RESET_ALL}\n")
            await self.speaker.speak_async(response)
    
    async def process_chat_message(self, message):
        """Processa mensagem do chat"""
        return self.ai.generate_response(message, mode="gamer")
    
    async def test_reactions(self):
        """Teste de reações"""
        print(f"\n{Fore.YELLOW}😊 Teste de Reações{Style.RESET_ALL}\n")
        
        reactions = [
            ("happy", "Yatta! Estou feliz! ✨"),
            ("surprised", "Nani?! Que surpresa!"),
            ("sad", "Ahh... que tristeza..."),
            ("confused", "Hmm? Não entendi..."),
            ("joy", "Sugoi! Incrível! 🎉")
        ]
        
        for expression, text in reactions:
            print(f"{Fore.MAGENTA}Mirai: {text}{Style.RESET_ALL}")
            
            if self.vtuber and self.vtuber.is_active:
                await self.vtuber.set_expression(expression)
            
            self.speaker.speak(text)
            await asyncio.sleep(2)
        
        if self.vtuber and self.vtuber.is_active:
            await self.vtuber.set_expression("neutral")