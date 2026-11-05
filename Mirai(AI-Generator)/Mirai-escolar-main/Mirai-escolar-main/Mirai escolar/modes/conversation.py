from modes.base_mode import BaseMode
from perception.text_input import TextInput
from perception.voice_listener import VoiceListener
from colorama import Fore, Style
import asyncio
import time
import threading

class ConversationMode(BaseMode):
    def __init__(self, mirai_instance):
        super().__init__(mirai_instance)
        self.listening = False
        self.autonomous_active = False
        
    async def enter(self):
        self.is_active = True
        self.state.set_state("conversation")
        self.print_mode_header("MODO CONVERSA")
        
        print(f"{Fore.YELLOW}Escolha o tipo de conversa:{Style.RESET_ALL}")
        print("1. Por Voz")
        print("2. Por Texto")
        print("3. Mista (voz e texto)")
        print(f"{Fore.CYAN}4. Conversa Autônoma ⭐ (Mirai conversa DE VERDADE!){Style.RESET_ALL}")
        print("0. Voltar")
        
        choice = input(f"\n{Fore.MAGENTA}Opção: {Style.RESET_ALL}")
        
        if choice == "1":
            await self.voice_conversation()
        elif choice == "2":
            await self.text_conversation()
        elif choice == "3":
            await self.mixed_conversation()
        elif choice == "4":
            await self.autonomous_voice_conversation()
    
    async def exit(self):
        self.is_active = False
        self.autonomous_active = False
        print(f"\n{Fore.CYAN}Saindo do modo conversa...{Style.RESET_ALL}")
    
    async def process_input(self, user_input, enable_search=True):
        """Processa input"""
        if not user_input or user_input.strip() == "":
            return None
        
        if user_input.lower() in ['sair', 'exit', 'voltar', 'parar']:
            return "EXIT"
        
        # Gera resposta (pesquisa SÓ quando necessário!)
        response = self.ai.generate_response(user_input, mode="conversation", enable_search=enable_search)
        
        sentiment = self.ai.analyze_sentiment(response)
        
        if self.vtuber and self.vtuber.is_active:
            try:
                from vtuber.expressions import ExpressionManager
                expr_manager = ExpressionManager()
                expression = expr_manager.get_expression_for_sentiment(sentiment)
                await self.vtuber.set_expression(expression)
            except:
                pass
        
        return response
    
    async def text_conversation(self):
        """Conversa por texto"""
        print(f"\n{Fore.GREEN}💬 Modo texto ativado!")
        print(f"{Fore.YELLOW}(Digite 'sair' para voltar){Style.RESET_ALL}\n")
        
        text_input = TextInput()
        
        while self.is_active:
            user_input = text_input.get_input()
            
            if not user_input:
                continue
            
            print(f"{Fore.CYAN}Pensando...{Style.RESET_ALL}", end='\r')
            
            result = await self.process_input(user_input)
            
            print(" " * 50, end='\r')
            
            if result == "EXIT":
                break
            
            if result:
                print(f"{Fore.MAGENTA}Mirai: {result}{Style.RESET_ALL}\n")
                
                try:
                    self.speaker.speak(result)
                except Exception as e:
                    print(f"  ⚠️  Erro: {e}")
    
    async def voice_conversation(self):
        """Conversa por voz"""
        print(f"\n{Fore.GREEN}🎤 Modo voz ativado!")
        print(f"{Fore.YELLOW}(Diga 'sair' para voltar){Style.RESET_ALL}\n")
        
        voice = VoiceListener()
        if not voice.initialize():
            print(f"{Fore.RED}Erro ao inicializar microfone!{Style.RESET_ALL}")
            return
        
        # Ajustes otimizados
        voice.recognizer.pause_threshold = 1.0
        voice.recognizer.phrase_time_limit = 10
        
        while self.is_active:
            try:
                print(f"{Fore.CYAN}🎤 Escutando...{Style.RESET_ALL}", end='\r')
                
                user_input = voice.listen_once()
                
                print(" " * 50, end='\r')
                
                if not user_input:
                    continue
                
                print(f"{Fore.CYAN}Você: {user_input}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Pensando...{Style.RESET_ALL}", end='\r')
                
                result = await self.process_input(user_input)
                
                print(" " * 50, end='\r')
                
                if result == "EXIT":
                    break
                
                if result:
                    print(f"{Fore.MAGENTA}Mirai: {result}{Style.RESET_ALL}\n")
                    
                    try:
                        self.speaker.speak(result)
                    except Exception as e:
                        print(f"  ⚠️  Erro: {e}")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"{Fore.RED}Erro: {e}{Style.RESET_ALL}")
    
    async def mixed_conversation(self):
        """Conversa mista"""
        print(f"\n{Fore.GREEN}🎤💬 Modo misto ativado!")
        print(f"{Fore.YELLOW}(Pressione Enter para voz, ou digite){Style.RESET_ALL}\n")
        
        text_input = TextInput()
        voice = VoiceListener()
        voice.initialize()
        
        voice.recognizer.pause_threshold = 1.0
        voice.recognizer.phrase_time_limit = 10
        
        while self.is_active:
            user_input = text_input.get_input()
            
            if user_input == "":
                print(f"{Fore.CYAN}🎤 Escutando...{Style.RESET_ALL}", end='\r')
                user_input = voice.listen_once()
                print(" " * 50, end='\r')
                
                if not user_input:
                    continue
                    
                print(f"{Fore.CYAN}Você (voz): {user_input}{Style.RESET_ALL}")
            
            print(f"{Fore.CYAN}Pensando...{Style.RESET_ALL}", end='\r')
            
            result = await self.process_input(user_input)
            
            print(" " * 50, end='\r')
            
            if result == "EXIT":
                break
            
            if result:
                print(f"{Fore.MAGENTA}Mirai: {result}{Style.RESET_ALL}\n")
                
                try:
                    self.speaker.speak(result)
                except Exception as e:
                    print(f"  ⚠️  Erro: {e}")
    
    async def autonomous_voice_conversation(self):
        """Conversa AUTÔNOMA DE VERDADE - Como AMIGA conversando!"""
        print(f"\n{Fore.GREEN}🤖🎤 Modo Autônoma - Amiga Virtual!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Mirai vai CONVERSAR DE VERDADE como sua amiga!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Ela fala quando você fica em silêncio (15-30s){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}(Diga 'parar' para sair){Style.RESET_ALL}\n")
        
        voice = VoiceListener()
        if not voice.initialize():
            print(f"{Fore.RED}Erro ao inicializar microfone!{Style.RESET_ALL}")
            return
        
        # Ajustes
        voice.recognizer.pause_threshold = 1.0
        voice.recognizer.phrase_time_limit = 10
        voice.recognizer.energy_threshold = 3000
        
        self.autonomous_active = True
        
        # Saudação natural
        greeting = self.ai.generate_greeting()
        print(f"{Fore.MAGENTA}Mirai: {greeting}{Style.RESET_ALL}\n")
        
        try:
            self.speaker.speak(greeting)
        except:
            pass
        
        # Thread de escuta contínua
        def listen_loop():
            while self.autonomous_active and self.is_active:
                try:
                    # Escuta sem mostrar "escutando" o tempo todo
                    user_input = voice.listen_once_silent()
                    
                    if user_input:
                        # Processa
                        asyncio.run(self._handle_autonomous_input(user_input))
                        
                except:
                    time.sleep(0.5)
        
        # Inicia escuta
        listen_thread = threading.Thread(target=listen_loop)
        listen_thread.daemon = True
        listen_thread.start()
        
        # Loop de verificação de silêncio (REAL!)
        print(f"{Fore.CYAN}💭 Mirai está aqui conversando com você...{Style.RESET_ALL}\n")
        
        while self.is_active and self.autonomous_active:
            # Aguarda um pouco
            await asyncio.sleep(3)
            
            # Verifica se usuário está em silêncio
            if self.ai.should_take_initiative():
                # Mirai toma iniciativa NATURALMENTE
                initiative = self.ai.generate_initiative()
                
                print(f"{Fore.CYAN}[Mirai nota o silêncio e fala]{Style.RESET_ALL}")
                print(f"{Fore.MAGENTA}Mirai: {initiative}{Style.RESET_ALL}\n")
                
                try:
                    self.speaker.speak(initiative)
                except:
                    pass
    
    async def _handle_autonomous_input(self, user_input):
        """Processa input autônomo"""
        print(f"{Fore.CYAN}Você: {user_input}{Style.RESET_ALL}")
        
        if user_input.lower() in ['parar', 'sair', 'exit', 'tchau']:
            self.is_active = False
            self.autonomous_active = False
            farewell = "Falou! Foi legal conversar com você! Até mais!"
            print(f"\n{Fore.MAGENTA}Mirai: {farewell}{Style.RESET_ALL}")
            self.speaker.speak(farewell)
            return
        
        print(f"{Fore.CYAN}💭 Pensando...{Style.RESET_ALL}", end='\r')
        
        result = await self.process_input(user_input, enable_search=True)
        
        print(" " * 50, end='\r')
        
        if result and result != "EXIT":
            print(f"{Fore.MAGENTA}Mirai: {result}{Style.RESET_ALL}\n")
            
            try:
                self.speaker.speak(result)
            except Exception as e:
                print(f"  ⚠️  Erro: {e}")