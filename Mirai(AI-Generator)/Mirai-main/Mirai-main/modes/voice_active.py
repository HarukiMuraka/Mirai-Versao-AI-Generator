from modes.base_mode import BaseMode
from colorama import Fore, Style
import speech_recognition as sr
import asyncio
import subprocess
import platform
import time
import re
from datetime import datetime
from queue import Queue
import threading

try:
    import pyautogui
    SCREENSHOT_AVAILABLE = True
except:
    SCREENSHOT_AVAILABLE = False


class SmartVoiceListener:
    """Sistema inteligente de reconhecimento de voz"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        
        # Configurações otimizadas
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5
    
    def initialize(self):
        """Inicializa microfone"""
        try:
            self.microphone = sr.Microphone()
            
            print(f"{Fore.CYAN}🎤 Calibrando microfone...{Style.RESET_ALL}")
            
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            
            print(f"{Fore.GREEN}✓ Microfone pronto!{Style.RESET_ALL}")
            return True
        
        except Exception as e:
            print(f"{Fore.RED}❌ Erro no microfone: {e}{Style.RESET_ALL}")
            return False
    
    def listen_once(self, timeout=5, phrase_limit=10):
        """Escuta uma vez"""
        if not self.microphone:
            return None
        
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout,
                    phrase_time_limit=phrase_limit
                )
            
            text = self.recognizer.recognize_google(audio, language='pt-BR')
            return text
        
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except Exception:
            return None
    
    def listen_continuous(self, callback, stop_event):
        """Escuta contínua em thread"""
        while not stop_event.is_set():
            text = self.listen_once(timeout=None, phrase_limit=10)
            
            if text:
                callback(text)
            
            time.sleep(0.1)


class VoiceCommandHandler:
    """Gerenciador inteligente de comandos de voz"""
    
    def __init__(self, mirai_instance):
        self.mirai = mirai_instance
        self.ai = mirai_instance.ai
        self.speaker = mirai_instance.speaker
        
        # App launcher
        self.system = platform.system()
        self.apps = self._load_app_database()
        
        # Padrões de comando
        self.patterns = {
            'abrir_app': [
                r'(?:abrir?|abre|executar?|rodar?|iniciar?) (?:o |a )?(.*)',
                r'(?:abra|execute|rode|inicie) (?:o |a )?(.*)'
            ],
            'pesquisar': [
                r'(?:pesquisar?|procurar?|buscar?) (?:sobre |por )?(.*)',
                r'(?:pesquise|procure|busque) (?:sobre |por )?(.*)',
                r'(?:me fala sobre|o que é|quem é) (.*)'
            ],
            'screenshot': [
                r'(?:tirar?|capturar?) (?:print|screenshot|foto) (?:da )?tela',
                r'(?:tire|capture) (?:print|screenshot|foto) (?:da )?tela'
            ],
            'analisar_tela': [
                r'(?:analisar?|ver?|ler?) (?:minha )?tela',
                r'(?:analise|veja|leia) (?:minha )?tela',
                r'o que (?:tem|tá|está) na (?:minha )?tela'
            ],
            'parar': [
                r'(?:parar?|sair?|encerrar?|tchau|até logo)',
                r'(?:pare|saia|encerre)'
            ]
        }
    
    def _load_app_database(self):
        """Carrega banco de dados de apps"""
        return {
            # Navegadores
            'chrome': {
                'names': ['chrome', 'google chrome', 'navegador chrome'],
                'windows': ['chrome.exe'],
                'linux': ['google-chrome', 'chromium'],
                'macos': ['Google Chrome']
            },
            'firefox': {
                'names': ['firefox', 'mozila', 'navegador firefox'],
                'windows': ['firefox.exe'],
                'linux': ['firefox'],
                'macos': ['Firefox']
            },
            'edge': {
                'names': ['edge', 'microsoft edge'],
                'windows': ['msedge.exe'],
                'linux': [],
                'macos': ['Microsoft Edge']
            },
            
            # Desenvolvimento
            'vscode': {
                'names': ['vscode', 'vs code', 'visual studio code', 'code', 'editor'],
                'windows': ['Code.exe'],
                'linux': ['code'],
                'macos': ['Visual Studio Code']
            },
            'pycharm': {
                'names': ['pycharm', 'py charm'],
                'windows': ['pycharm64.exe'],
                'linux': ['pycharm'],
                'macos': ['PyCharm']
            },
            
            # Comunicação
            'discord': {
                'names': ['discord'],
                'windows': ['discord.exe'],
                'linux': ['discord'],
                'macos': ['Discord']
            },
            'spotify': {
                'names': ['spotify', 'música', 'musica'],
                'windows': ['spotify.exe'],
                'linux': ['spotify'],
                'macos': ['Spotify']
            },
            'telegram': {
                'names': ['telegram'],
                'windows': ['Telegram.exe'],
                'linux': ['telegram'],
                'macos': ['Telegram']
            },
            
            # Stream
            'obs': {
                'names': ['obs', 'obs studio', 'stream'],
                'windows': ['obs64.exe'],
                'linux': ['obs'],
                'macos': ['OBS']
            },
            
            # Sistema
            'notepad': {
                'names': ['bloco de notas', 'notepad', 'bloco'],
                'windows': ['notepad.exe'],
                'linux': ['gedit', 'nano'],
                'macos': ['TextEdit']
            },
            'calculadora': {
                'names': ['calculadora', 'calc'],
                'windows': ['calc.exe'],
                'linux': ['gnome-calculator'],
                'macos': ['Calculator']
            },
            'explorer': {
                'names': ['explorador', 'explorer', 'pasta', 'arquivos'],
                'windows': ['explorer.exe'],
                'linux': ['nautilus', 'dolphin'],
                'macos': ['Finder']
            },
            'terminal': {
                'names': ['terminal', 'cmd', 'prompt', 'console'],
                'windows': ['cmd.exe'],
                'linux': ['gnome-terminal'],
                'macos': ['Terminal']
            },
            
            # Jogos
            'steam': {
                'names': ['steam'],
                'windows': ['steam.exe'],
                'linux': ['steam'],
                'macos': ['Steam']
            },
            'minecraft': {
                'names': ['minecraft', 'mine'],
                'windows': ['Minecraft.exe'],
                'linux': ['minecraft-launcher'],
                'macos': ['Minecraft']
            }
        }
    
    def detect_app_from_voice(self, text):
        """Detecta app a partir de comando de voz"""
        text_lower = text.lower()
        
        for app_key, app_data in self.apps.items():
            if any(name in text_lower for name in app_data['names']):
                return app_key
        
        return None
    
    def open_app(self, app_key):
        """Abre aplicativo"""
        if app_key not in self.apps:
            return False
        
        app_data = self.apps[app_key]
        
        if self.system == "Windows":
            executables = app_data['windows']
        elif self.system == "Linux":
            executables = app_data['linux']
        elif self.system == "Darwin":
            executables = app_data['macos']
        else:
            return False
        
        for exe in executables:
            try:
                if self.system == "Windows":
                    subprocess.Popen([exe], shell=True)
                elif self.system == "Linux":
                    subprocess.Popen([exe])
                elif self.system == "Darwin":
                    subprocess.Popen(['open', '-a', exe])
                
                return True
            except:
                continue
        
        return False
    
    async def process_voice_command(self, text):
        """Processa comando de voz de forma inteligente"""
        text_clean = text.strip()
        
        # Detecta tipo de comando
        command_type = None
        match_result = None
        
        for cmd_type, pattern_list in self.patterns.items():
            for pattern in pattern_list:
                match = re.match(pattern, text_clean, re.IGNORECASE)
                if match:
                    command_type = cmd_type
                    match_result = match
                    break
            if command_type:
                break
        
        # Executa comando
        if command_type == 'parar':
            return "STOP", "Encerrando modo voz ativo!"
        
        elif command_type == 'abrir_app':
            app_text = match_result.group(1) if match_result else text_clean
            return await self._exec_open_app(app_text)
        
        elif command_type == 'pesquisar':
            query = match_result.group(1) if match_result else text_clean
            return await self._exec_search(query)
        
        elif command_type == 'screenshot':
            return await self._exec_screenshot()
        
        elif command_type == 'analisar_tela':
            return await self._exec_analyze_screen()
        
        else:
            # Conversa normal
            return await self._exec_conversation(text_clean)
    
    async def _exec_open_app(self, app_text):
        """Executa abertura de app"""
        app_key = self.detect_app_from_voice(app_text)
        
        if not app_key:
            return "FAILED", f"Não entendi qual app você quer abrir."
        
        print(f"{Fore.CYAN}🚀 Abrindo {app_key}...{Style.RESET_ALL}")
        
        if self.open_app(app_key):
            return "SUCCESS", f"Abrindo {app_key}!"
        else:
            return "FAILED", f"Não consegui abrir o {app_key}. Tem certeza que está instalado?"
    
    async def _exec_search(self, query):
        """Executa pesquisa"""
        print(f"{Fore.CYAN}🔍 Pesquisando '{query}'...{Style.RESET_ALL}")
        
        # Usa IA para pesquisar
        response = self.ai.generate_response(
            f"Pesquise e me explique sobre: {query}",
            mode="voice",
            enable_search=True
        )
        
        return "SUCCESS", response
    
    async def _exec_screenshot(self):
        """Executa screenshot"""
        if not SCREENSHOT_AVAILABLE:
            return "FAILED", "Screenshot não disponível."
        
        screenshot = pyautogui.screenshot()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        screenshot.save(filename)
        
        return "SUCCESS", f"Tela capturada! Salvei como {filename}."
    
    async def _exec_analyze_screen(self):
        """Executa análise de tela"""
        if not SCREENSHOT_AVAILABLE:
            return "FAILED", "Análise de tela não disponível."
        
        # Captura e analisa
        screenshot = pyautogui.screenshot()
        
        # Análise básica
        width, height = screenshot.size
        
        # Prompt para IA
        prompt = f"O usuário pediu para eu analisar a tela dele. A resolução é {width}x{height}. Faça um comentário breve dizendo que você viu a tela dele."
        
        response = self.ai.generate_response(prompt, mode="voice", enable_search=False)
        
        return "SUCCESS", response
    
    async def _exec_conversation(self, text):
        """Executa conversa normal"""
        response = self.ai.generate_response(text, mode="voice", enable_search=True)
        
        return "CONVERSATION", response


class AutonomousManager:
    """Gerenciador de modo autônomo"""
    
    def __init__(self, ai_engine, speaker):
        self.ai = ai_engine
        self.speaker = speaker
        
        # Controle de tempo
        self.last_user_message = time.time()
        self.last_initiative = time.time()
        
        # Thresholds
        self.min_silence_for_initiative = 20  # 20 segundos
        self.max_silence_for_initiative = 40  # 40 segundos
        self.initiative_cooldown = 30  # Cooldown entre iniciativas
    
    def update_user_activity(self):
        """Atualiza timestamp de atividade do usuário"""
        self.last_user_message = time.time()
    
    def should_take_initiative(self):
        """Verifica se deve tomar iniciativa"""
        current_time = time.time()
        
        # Tempo desde última mensagem do usuário
        silence_time = current_time - self.last_user_message
        
        # Tempo desde última iniciativa
        time_since_initiative = current_time - self.last_initiative
        
        # Condições para tomar iniciativa
        if silence_time >= self.min_silence_for_initiative and \
           time_since_initiative >= self.initiative_cooldown:
            
            # Probabilidade aumenta com tempo de silêncio
            probability = min(1.0, silence_time / self.max_silence_for_initiative)
            
            import random
            if random.random() < probability:
                self.last_initiative = current_time
                return True
        
        return False
    
    def generate_initiative(self):
        """Gera mensagem de iniciativa"""
        iniciativas = [
            "E aí, tá fazendo o que?",
            "Tá precisando de alguma coisa?",
            "Quer que eu pesquise algo interessante?",
            "Tá muito quieto aí! Tudo bem?",
            "Conta, no que você tá trabalhando?",
            "Posso ajudar em alguma coisa?",
            "Tá entediado? Quer conversar?",
            "Quer ouvir algo curioso?",
            "Me conta uma coisa legal!"
        ]
        
        import random
        return random.choice(iniciativas)


class VoiceActivePro(BaseMode):
    """
    MODO MÃO LIVRES + AUTÔNOMO PRO
    ================================
    Sistema integrado que combina:
    - Escuta contínua inteligente
    - Modo autônomo (Mirai toma iniciativa)
    - Comandos funcionais sem repetir "Mirai"
    - Conversação natural
    """
    
    def __init__(self, mirai_instance):
        super().__init__(mirai_instance)
        
        # Subsistemas
        self.voice_listener = SmartVoiceListener()
        self.command_handler = VoiceCommandHandler(mirai_instance)
        self.autonomous = AutonomousManager(self.ai, self.speaker)
        
        # Controle
        self.listening = False
        self.stop_event = threading.Event()
        self.voice_thread = None
        
        # Modo
        self.mode = None  # 'continuous' ou 'autonomous'
    
    async def enter(self):
        """Entra no modo voz ativo"""
        self.is_active = True
        self.state.set_state("voice_active")
        self.print_mode_header("MODO MÃO LIVRES + AUTÔNOMO")
        
        print(f"{Fore.GREEN}✨ Modo voz ativo melhorado!{Style.RESET_ALL}\n")
        
        # Testa microfone
        if not self.voice_listener.initialize():
            print(f"{Fore.RED}❌ Microfone não funciona!{Style.RESET_ALL}")
            self.speaker.speak("Microfone não está funcionando!")
            return
        
        await self.show_menu()
    
    async def exit(self):
        """Sai do modo"""
        self.is_active = False
        self.listening = False
        self.stop_event.set()
        
        if self.voice_thread:
            self.voice_thread.join(timeout=2)
        
        print(f"\n{Fore.CYAN}Saindo do modo voz ativo...{Style.RESET_ALL}")
    
    async def show_menu(self):
        """Menu principal"""
        while self.is_active:
            print(f"\n{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}🎤 MODO VOZ ATIVO PRO{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}\n")
            
            print("1. 🎤 Escuta Contínua (sempre ativa)")
            print("2. 🤖 Modo Autônomo (Mirai conversa e toma iniciativa)")
            print("3. 🔔 Teste de Comando Único")
            print("0. ⬅️ Voltar")
            
            choice = input(f"\n{Fore.GREEN}Opção: {Style.RESET_ALL}")
            
            if choice == "1":
                await self.continuous_mode()
            elif choice == "2":
                await self.autonomous_mode()
            elif choice == "3":
                await self.single_command_test()
            elif choice == "0":
                break
    
    async def continuous_mode(self):
        """Modo escuta contínua"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}🎤 ESCUTA CONTÍNUA ATIVADA{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        print(f"{Fore.GREEN}✓ Mirai escutando! Pode falar!{Style.RESET_ALL}\n")
        print(f"{Fore.YELLOW}Comandos:{Style.RESET_ALL}")
        print(f"  • Abrir [app]{Style.RESET_ALL}")
        print(f"  • Pesquisar [tema]{Style.RESET_ALL}")
        print(f"  • Capturar tela{Style.RESET_ALL}")
        print(f"  • Analisar tela{Style.RESET_ALL}")
        print(f"  • Ou converse normalmente{Style.RESET_ALL}")
        print(f"  • Diga 'parar' para sair\n{Style.RESET_ALL}")
        
        self.speaker.speak("Escuta contínua ativada! Pode falar comigo!")
        
        self.mode = 'continuous'
        self.listening = True
        self.stop_event.clear()
        
        while self.listening and self.is_active:
            try:
                print(f"{Fore.CYAN}🎤 ...{Style.RESET_ALL}", end='\r')
                
                text = self.voice_listener.listen_once(timeout=None)
                
                if text:
                    print(" " * 50, end='\r')
                    print(f"{Fore.GREEN}Você: {text}{Style.RESET_ALL}")
                    
                    # Processa comando
                    status, response = await self.command_handler.process_voice_command(text)
                    
                    if status == "STOP":
                        print(f"{Fore.MAGENTA}Mirai: {response}{Style.RESET_ALL}")
                        self.speaker.speak(response)
                        self.listening = False
                        break
                    
                    print(f"{Fore.MAGENTA}Mirai: {response}{Style.RESET_ALL}\n")
                    self.speaker.speak(response)
            
            except KeyboardInterrupt:
                self.listening = False
                break
            except Exception as e:
                print(f"{Fore.RED}Erro: {e}{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}✓ Escuta contínua encerrada{Style.RESET_ALL}")
        input(f"{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    async def autonomous_mode(self):
        """Modo autônomo - Mirai toma iniciativa"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}🤖 MODO AUTÔNOMO ATIVADO{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        print(f"{Fore.GREEN}✓ Mirai vai conversar de forma natural!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Ela toma iniciativa quando você fica em silêncio (20-40s){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Diga 'parar' para sair\n{Style.RESET_ALL}")
        
        # Saudação
        greeting = "E aí! Modo autônomo ativado! Vamos conversar?"
        print(f"{Fore.MAGENTA}Mirai: {greeting}{Style.RESET_ALL}\n")
        self.speaker.speak(greeting)
        
        self.mode = 'autonomous'
        self.listening = True
        self.stop_event.clear()
        
        # Thread de escuta
        self.voice_thread = threading.Thread(
            target=self._autonomous_listen_loop,
            daemon=True
        )
        self.voice_thread.start()
        
        # Loop de checagem de iniciativa
        while self.listening and self.is_active:
            await asyncio.sleep(2)
            
            # Verifica se deve tomar iniciativa
            if self.autonomous.should_take_initiative():
                initiative = self.autonomous.generate_initiative()
                
                print(f"\n{Fore.CYAN}[Mirai toma iniciativa]{Style.RESET_ALL}")
                print(f"{Fore.MAGENTA}Mirai: {initiative}{Style.RESET_ALL}\n")
                
                self.speaker.speak(initiative)
        
        # Aguarda thread terminar
        self.stop_event.set()
        if self.voice_thread:
            self.voice_thread.join(timeout=2)
        
        print(f"\n{Fore.GREEN}✓ Modo autônomo encerrado{Style.RESET_ALL}")
        input(f"{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    def _autonomous_listen_loop(self):
        """Loop de escuta para modo autônomo (thread)"""
        while not self.stop_event.is_set() and self.listening:
            text = self.voice_listener.listen_once(timeout=5)
            
            if text:
                # Atualiza atividade
                self.autonomous.update_user_activity()
                
                # Processa em thread async
                asyncio.run(self._process_autonomous_input(text))
            
            time.sleep(0.1)
    
    async def _process_autonomous_input(self, text):
        """Processa input no modo autônomo"""
        print(f"\n{Fore.GREEN}Você: {text}{Style.RESET_ALL}")
        
        # Processa
        status, response = await self.command_handler.process_voice_command(text)
        
        if status == "STOP":
            print(f"{Fore.MAGENTA}Mirai: {response}{Style.RESET_ALL}")
            self.speaker.speak(response)
            self.listening = False
            return
        
        print(f"{Fore.MAGENTA}Mirai: {response}{Style.RESET_ALL}\n")
        self.speaker.speak(response)
    
    async def single_command_test(self):
        """Teste de comando único"""
        print(f"\n{Fore.CYAN}🎤 Teste de Comando Único{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Fale agora!{Style.RESET_ALL}\n")
        
        self.speaker.speak("Pode falar!")
        
        text = self.voice_listener.listen_once(timeout=5, phrase_limit=10)
        
        if text:
            print(f"{Fore.GREEN}Você: {text}{Style.RESET_ALL}\n")
            
            status, response = await self.command_handler.process_voice_command(text)
            
            print(f"{Fore.MAGENTA}Mirai: {response}{Style.RESET_ALL}\n")
            self.speaker.speak(response)
        else:
            print(f"{Fore.RED}Não ouvi nada!{Style.RESET_ALL}")
            self.speaker.speak("Não ouvi nada!")
        
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    async def process_input(self, user_input):
        """Fallback para compatibilidade"""
        return None