import time
from modes.base_mode import BaseMode
from colorama import Fore, Style
import speech_recognition as sr
import asyncio
import threading
from queue import Queue
import subprocess
import os

class VoiceActiveMode(BaseMode):
    """Modo Voz Ativo MELHORADO - Apps + Comandos Completos"""
    
    def __init__(self, mirai_instance):
        super().__init__(mirai_instance)
        
        # Reconhecedor de voz
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Controle
        self.listening = False
        self.voice_thread = None
        self.command_queue = Queue()
        
        # Ajustes otimizados
        self.recognizer.energy_threshold = 3000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.6
        
        # Palavras de ativação
        self.wake_words = ['mirai', 'hey mirai', 'oi mirai', 'ei mirai']
        self.stop_words = ['parar', 'sair', 'desativar', 'tchau']
        
        # Apps conhecidos (EXPANDIDO)
        self.apps = {
            'chrome': ['chrome', 'google chrome'],
            'firefox': ['firefox', 'mozila'],
            'edge': ['edge', 'microsoft edge'],
            'spotify': ['spotify', 'musica'],
            'discord': ['discord'],
            'obs': ['obs', 'obs studio'],
            'vscode': ['vscode', 'visual studio code', 'vs code'],
            'notepad': ['bloco de notas', 'notepad'],
            'calculadora': ['calculadora', 'calc'],
            'paint': ['paint'],
            'explorer': ['explorer', 'explorador de arquivos'],
            'cmd': ['cmd', 'prompt', 'terminal'],
            'steam': ['steam'],
            'minecraft': ['minecraft']
        }
    
    async def enter(self):
        """Entra no modo voz ativo"""
        self.is_active = True
        self.state.set_state("voice_active")
        self.print_mode_header("MODO VOZ ATIVO - MÃOS LIVRES")
        
        print(f"{Fore.GREEN}Yatta! Modo voz ativo melhorado! 🎤{Style.RESET_ALL}\n")
        
        if not await self._test_microphone():
            print(f"{Fore.RED}❌ Microfone não funciona!{Style.RESET_ALL}")
            self.speaker.speak("Microfone não está funcionando!")
            return
        
        await self.show_voice_menu()
    
    async def exit(self):
        """Sai do modo voz ativo"""
        self.is_active = False
        self.listening = False
        print(f"\n{Fore.CYAN}Saindo do modo voz ativo...{Style.RESET_ALL}")
    
    async def _test_microphone(self):
        """Testa microfone"""
        print(f"{Fore.CYAN}🎤 Testando microfone...{Style.RESET_ALL}\n")
        
        try:
            with self.microphone as source:
                print(f"{Fore.YELLOW}Ajustando ruído...{Style.RESET_ALL}")
                self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
                print(f"{Fore.GREEN}✓ Microfone OK!{Style.RESET_ALL}\n")
                return True
        except Exception as e:
            print(f"{Fore.RED}✗ Erro: {e}{Style.RESET_ALL}")
            return False
    
    async def show_voice_menu(self):
        """Menu do modo voz"""
        while self.is_active:
            print(f"\n{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}🎤 MODO VOZ ATIVO{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}\n")
            
            print("1. 🎤 Escuta Contínua (sempre ativa)")
            print("2. 🔔 Palavra de Ativação (diga 'Mirai')")
            print("3. 💬 Comando Único (fala uma vez)")
            print("0. ⬅️ Voltar")
            
            choice = input(f"\n{Fore.GREEN}Opção: {Style.RESET_ALL}")
            
            if choice == "1":
                await self.continuous_listening()
            elif choice == "2":
                await self.wake_word_mode()
            elif choice == "3":
                await self.single_command()
            elif choice == "0":
                break
    
    async def continuous_listening(self):
        """Escuta contínua MELHORADA"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}🎤 ESCUTA CONTÍNUA ATIVADA{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        print(f"{Fore.GREEN}✓ Mirai escutando!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Comandos disponíveis:{Style.RESET_ALL}")
        print(f"  • Abrir [app] - Ex: abrir chrome{Style.RESET_ALL}")
        print(f"  • Pesquisar [tema]{Style.RESET_ALL}")
        print(f"  • Capturar tela{Style.RESET_ALL}")
        print(f"  • Conversa normal{Style.RESET_ALL}")
        print(f"  • Diga 'parar' para sair\n{Style.RESET_ALL}")
        
        self.speaker.speak("Escuta contínua ativada! Pode falar comigo!")
        
        self.listening = True
        
        while self.listening:
            try:
                print(f"{Fore.CYAN}🎤 Escutando...{Style.RESET_ALL}", end='\r')
                
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=10)
                
                print(" " * 50, end='\r')
                print(f"{Fore.YELLOW}🔄 Reconhecendo...{Style.RESET_ALL}", end='\r')
                text = self.recognizer.recognize_google(audio, language='pt-BR')
                
                print(" " * 50, end='\r')
                print(f"{Fore.GREEN}💤 Você: {text}{Style.RESET_ALL}")
                
                # Parar
                if any(word in text.lower() for word in self.stop_words):
                    self.speaker.speak("Encerrando!")
                    self.listening = False
                    break
                
                # Processa
                await self._process_voice_command(text)
                
            except sr.UnknownValueError:
                print(" " * 50, end='\r')
            except sr.RequestError as e:
                print(f"{Fore.RED}❌ Erro: {e}{Style.RESET_ALL}")
                self.speaker.speak("Erro no reconhecimento!")
                break
            except KeyboardInterrupt:
                self.listening = False
                break
            except Exception as e:
                print(f"{Fore.RED}❌ Erro: {e}{Style.RESET_ALL}")
    
    async def wake_word_mode(self):
        """Modo palavra de ativação"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}🔔 MODO PALAVRA DE ATIVAÇÃO{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        print(f"{Fore.GREEN}✓ Aguardando ser chamada!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Diga: 'Mirai' ou 'Hey Mirai'{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Para parar: 'parar'\n{Style.RESET_ALL}")
        
        self.speaker.speak("Modo palavra de ativação! Me chama quando precisar!")
        
        self.listening = True
        
        while self.listening:
            try:
                print(f"{Fore.CYAN}🔇 Aguardando...{Style.RESET_ALL}", end='\r')
                
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=5)
                
                text = self.recognizer.recognize_google(audio, language='pt-BR')
                text_lower = text.lower()
                
                # Palavra de ativação
                if any(word in text_lower for word in self.wake_words):
                    print(" " * 50, end='\r')
                    print(f"\n{Fore.GREEN}🔔 ATIVADA!{Style.RESET_ALL}")
                    self.speaker.speak("Oi! Tô aqui!")
                    
                    # Escuta comando
                    print(f"{Fore.CYAN}🎤 Pode falar...{Style.RESET_ALL}")
                    
                    with self.microphone as source:
                        audio2 = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    
                    command = self.recognizer.recognize_google(audio2, language='pt-BR')
                    print(f"\n{Fore.GREEN}💤 Você: {command}{Style.RESET_ALL}")
                    
                    # Parar
                    if any(word in command.lower() for word in self.stop_words):
                        self.speaker.speak("Até logo!")
                        self.listening = False
                        break
                    
                    # Processa
                    await self._process_voice_command(command)
                
            except sr.UnknownValueError:
                pass
            except sr.WaitTimeoutError:
                pass
            except KeyboardInterrupt:
                self.listening = False
                break
            except Exception as e:
                print(f"{Fore.RED}❌ Erro: {e}{Style.RESET_ALL}")
    
    async def single_command(self):
        """Comando único"""
        print(f"\n{Fore.CYAN}🎤 Modo Comando Único{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Fale agora...{Style.RESET_ALL}\n")
        
        self.speaker.speak("Pode falar!")
        
        try:
            with self.microphone as source:
                print(f"{Fore.CYAN}🎤 Escutando...{Style.RESET_ALL}")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print(f"{Fore.YELLOW}🔄 Reconhecendo...{Style.RESET_ALL}")
            text = self.recognizer.recognize_google(audio, language='pt-BR')
            
            print(f"\n{Fore.GREEN}💤 Você: {text}{Style.RESET_ALL}")
            
            await self._process_voice_command(text)
            
        except sr.UnknownValueError:
            print(f"{Fore.RED}❌ Não entendi!{Style.RESET_ALL}")
            self.speaker.speak("Não entendi!")
        except sr.WaitTimeoutError:
            print(f"{Fore.RED}⏱️ Timeout!{Style.RESET_ALL}")
            self.speaker.speak("Tempo esgotado!")
        except Exception as e:
            print(f"{Fore.RED}❌ Erro: {e}{Style.RESET_ALL}")
        
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    async def _process_voice_command(self, text):
        """Processa comando MELHORADO"""
        text_lower = text.lower()
        
        # ABRIR APP (MELHORADO)
        if 'abrir' in text_lower or 'abre' in text_lower:
            await self._execute_open_app(text_lower)
        
        # PESQUISAR
        elif 'pesquisar' in text_lower or 'pesquisa' in text_lower or 'procurar' in text_lower:
            await self._execute_search(text)
        
        # SCREENSHOT
        elif 'capturar tela' in text_lower or 'screenshot' in text_lower or 'print' in text_lower:
            await self._execute_screenshot()
        
        # VER TELA (NOVO!)
        elif 'ver tela' in text_lower or 'analisar tela' in text_lower:
            await self._execute_analyze_screen()
        
        # CONVERSA
        else:
            response = self.ai.generate_response(text, mode="voice", enable_search=True)
            print(f"{Fore.MAGENTA}🌸 Mirai: {response}{Style.RESET_ALL}\n")
            self.speaker.speak(response)
    
    async def _execute_open_app(self, text):
        """Executa abertura de app MELHORADO"""
        # Detecta qual app
        app_found = None
        for app_name, variations in self.apps.items():
            if any(var in text for var in variations):
                app_found = app_name
                break
        
        if not app_found:
            response = "Não entendi qual app você quer abrir!"
            print(f"{Fore.MAGENTA}🌸 Mirai: {response}{Style.RESET_ALL}\n")
            self.speaker.speak(response)
            return
        
        # Abre o app
        print(f"{Fore.CYAN}🚀 Abrindo {app_found}...{Style.RESET_ALL}")
        
        try:
            if app_found == 'chrome':
                subprocess.Popen(['start', 'chrome'], shell=True)
            elif app_found == 'firefox':
                subprocess.Popen(['start', 'firefox'], shell=True)
            elif app_found == 'edge':
                subprocess.Popen(['start', 'msedge'], shell=True)
            elif app_found == 'spotify':
                subprocess.Popen(['start', 'spotify'], shell=True)
            elif app_found == 'discord':
                subprocess.Popen(['start', 'discord'], shell=True)
            elif app_found == 'obs':
                subprocess.Popen(['start', 'obs64'], shell=True)
            elif app_found == 'vscode':
                subprocess.Popen(['code'], shell=True)
            elif app_found == 'notepad':
                subprocess.Popen(['notepad.exe'])
            elif app_found == 'calculadora':
                subprocess.Popen(['calc.exe'])
            elif app_found == 'paint':
                subprocess.Popen(['mspaint.exe'])
            elif app_found == 'explorer':
                subprocess.Popen(['explorer.exe'])
            elif app_found == 'cmd':
                subprocess.Popen(['cmd.exe'])
            elif app_found == 'steam':
                subprocess.Popen(['start', 'steam'], shell=True)
            elif app_found == 'minecraft':
                subprocess.Popen(['start', 'minecraft'], shell=True)
            
            response = f"Abrindo {app_found}!"
            print(f"{Fore.GREEN}✓ {response}{Style.RESET_ALL}\n")
            self.speaker.speak(response)
            
        except Exception as e:
            response = f"Erro ao abrir {app_found}!"
            print(f"{Fore.RED}❌ {response}: {e}{Style.RESET_ALL}\n")
            self.speaker.speak(response)
    
    async def _execute_search(self, text):
        """Executa pesquisa"""
        # Remove palavra 'pesquisar'
        query = text.lower()
        for word in ['pesquisar', 'pesquisa', 'procurar', 'sobre']:
            query = query.replace(word, '')
        
        query = query.strip()
        
        if not query:
            response = "O que você quer pesquisar?"
            print(f"{Fore.MAGENTA}🌸 Mirai: {response}{Style.RESET_ALL}\n")
            self.speaker.speak(response)
            return
        
        print(f"{Fore.CYAN}🔍 Pesquisando '{query}'...{Style.RESET_ALL}\n")
        self.speaker.speak(f"Pesquisando sobre {query}")
        
        # Usa AI para pesquisar
        response = self.ai.generate_response(query, mode="voice", enable_search=True)
        
        print(f"{Fore.MAGENTA}🌸 Mirai: {response}{Style.RESET_ALL}\n")
        self.speaker.speak(response)
    
    async def _execute_screenshot(self):
        """Captura screenshot"""
        import pyautogui
        
        self.speaker.speak("Capturando tela!")
        
        screenshot = pyautogui.screenshot()
        filename = f"screenshot_{int(time.time())}.png"
        screenshot.save(filename)
        
        response = f"Tela capturada! Salvo como {filename}"
        print(f"{Fore.GREEN}✓ {response}{Style.RESET_ALL}\n")
        self.speaker.speak(response)
    
    async def _execute_analyze_screen(self):
        """Analisa tela (NOVO!)"""
        import pyautogui
        import pytesseract
        from PIL import Image
        
        print(f"{Fore.CYAN}📸 Capturando e analisando...{Style.RESET_ALL}\n")
        self.speaker.speak("Analisando sua tela!")
        
        try:
            # Captura
            screenshot = pyautogui.screenshot()
            
            # OCR básico
            try:
                text = pytesseract.image_to_string(screenshot, lang='por')
                words = text.split()[:20]  # Primeiras 20 palavras
                
                if words:
                    context = ' '.join(words)
                    prompt = f"O usuário pediu para eu ver a tela dele. Detectei este texto: {context}. Comenta brevemente o que ele está fazendo!"
                else:
                    prompt = "O usuário pediu para eu ver a tela. Não detectei texto. Diz que não conseguiu ler nada mas que a tela foi capturada!"
            except:
                prompt = "Tela capturada mas OCR não disponível. Fala que capturou mas não conseguiu ler!"
            
            # IA comenta
            response = self.ai.generate_response(prompt, mode="voice")
            
            print(f"{Fore.MAGENTA}🌸 Mirai: {response}{Style.RESET_ALL}\n")
            self.speaker.speak(response)
            
        except Exception as e:
            response = "Erro ao analisar a tela!"
            print(f"{Fore.RED}❌ {response}: {e}{Style.RESET_ALL}\n")
            self.speaker.speak(response)