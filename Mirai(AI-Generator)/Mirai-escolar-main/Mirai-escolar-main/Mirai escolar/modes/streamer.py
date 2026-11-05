from modes.base_mode import BaseMode
from colorama import Fore, Style
from perception.text_input import TextInput
import asyncio
from datetime import datetime

# YouTube (opcional)
try:
    from pytchat import LiveChat
    YOUTUBE_OK = True
except:
    YOUTUBE_OK = False

# Twitch (opcional)
try:
    from twitchio.ext import commands as twitch_commands
    TWITCH_OK = True
except:
    TWITCH_OK = False


class StreamerMode(BaseMode):
    """Modo Streamer"""
    
    def __init__(self, mirai_instance):
        super().__init__(mirai_instance)
        
        self.platform = None
        self.youtube_chat = None
        self.twitch_bot = None
        
        self.last_messages = []
        self.max_history = 50
        self.response_cooldown = 3
        self.last_response = 0
    
    async def enter(self):
        """Entra no modo streamer"""
        self.is_active = True
        self.state.set_state("streamer")
        self.print_mode_header("MODO STREAMER")
        
        print(f"{Fore.GREEN}Modo Streamer ativado! Vamos fazer uma live! 🎥{Style.RESET_ALL}\n")
        
        await self.show_streamer_menu()
    
    async def exit(self):
        """Sai do modo streamer"""
        self.is_active = False
        
        if self.youtube_chat:
            self.youtube_chat.terminate()
        
        print(f"\n{Fore.CYAN}Saindo do modo streamer...{Style.RESET_ALL}")
    
    async def process_input(self, user_input):
        """Processa input"""
        return self.ai.generate_response(user_input, mode="gamer")
    
    async def show_streamer_menu(self):
        """Menu principal"""
        print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}🎥 MODO STREAMER{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}\n")
        
        print("Escolha a plataforma:")
        print(f"  1. 📺 YouTube {'' if YOUTUBE_OK else '(pip install pytchat)'}")
        print(f"  2. 💜 Twitch {'' if TWITCH_OK else '(pip install twitchio)'}")
        print(f"  3. 💬 Chat Simulado (TESTE - sempre funciona)")
        print("  0. ⬅️ Voltar")
        
        print(f"\n{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.GREEN}Plataforma: {Style.RESET_ALL}").strip()
        
        if choice == '0':
            return
        elif choice == '1' and YOUTUBE_OK:
            await self.setup_youtube()
        elif choice == '2' and TWITCH_OK:
            await self.setup_twitch()
        elif choice == '3':
            await self.simulated_chat()
        else:
            print(f"{Fore.RED}Opção inválida!{Style.RESET_ALL}")
            await asyncio.sleep(2)
            await self.show_streamer_menu()
    
    async def setup_youtube(self):
        """Configura YouTube"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}📺 CONFIGURAR YOUTUBE{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        print("ID da live/vídeo:")
        print("Exemplo: youtube.com/watch?v=ABC123")
        print("         O ID é: ABC123\n")
        
        video_id = input(f"{Fore.GREEN}ID: {Style.RESET_ALL}").strip()
        
        if not video_id:
            print(f"{Fore.RED}ID inválido!{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.YELLOW}⏳ Conectando...{Style.RESET_ALL}")
        self.speaker.speak("Conectando ao YouTube...")
        
        try:
            self.youtube_chat = LiveChat(video_id=video_id)
            self.platform = 'youtube'
            
            print(f"{Fore.GREEN}✓ Conectado!{Style.RESET_ALL}\n")
            self.speaker.speak("Conectada! Vamos ler o chat!")
            
            await self.run_youtube_stream()
        
        except Exception as e:
            print(f"{Fore.RED}❌ Erro: {e}{Style.RESET_ALL}")
            self.speaker.speak("Não consegui conectar!")
    
    async def setup_twitch(self):
        """Configura Twitch"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}💜 CONFIGURAR TWITCH{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        print("Configuração:")
        print("  1. Canal (seu username)")
        print("  2. Token OAuth (twitchapps.com/tmi)\n")
        
        channel = input(f"{Fore.GREEN}Canal: {Style.RESET_ALL}").strip()
        token = input(f"{Fore.GREEN}Token: {Style.RESET_ALL}").strip()
        
        if not channel or not token:
            print(f"{Fore.RED}Dados inválidos!{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.YELLOW}⏳ Conectando...{Style.RESET_ALL}")
        self.speaker.speak("Conectando à Twitch...")
        
        try:
            self.twitch_bot = MiraiTwitchBot(
                token=token,
                prefix='!',
                initial_channels=[channel],
                mirai_mode=self
            )
            
            self.platform = 'twitch'
            
            print(f"{Fore.GREEN}✓ Conectado!{Style.RESET_ALL}\n")
            self.speaker.speak("Conectada!")
            
            await self.twitch_bot.start()
        
        except Exception as e:
            print(f"{Fore.RED}❌ Erro: {e}{Style.RESET_ALL}")
            self.speaker.speak("Erro ao conectar!")
    
    async def run_youtube_stream(self):
        """Loop YouTube"""
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}📺 LENDO CHAT YOUTUBE{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        print("Ctrl+C para encerrar\n")
        
        try:
            while self.youtube_chat.is_alive():
                for chat in self.youtube_chat.get().sync_items():
                    author = chat.author.name
                    message = chat.message
                    
                    # Registra
                    self.last_messages.append({
                        'author': author,
                        'message': message,
                        'time': datetime.now()
                    })
                    
                    if len(self.last_messages) > self.max_history:
                        self.last_messages.pop(0)
                    
                    # Mostra
                    print(f"{Fore.CYAN}💬 {author}: {message}{Style.RESET_ALL}")
                    
                    # Responde
                    if await self._should_respond(message):
                        await self._respond_to_chat(author, message)
                
                await asyncio.sleep(1)
        
        except KeyboardInterrupt:
            print(f"\n{Fore.GREEN}✓ Stream encerrada{Style.RESET_ALL}")
        
        finally:
            if self.youtube_chat:
                self.youtube_chat.terminate()
    
    async def simulated_chat(self):
        """Chat simulado - SEMPRE FUNCIONA"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}💬 CHAT SIMULADO{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        print(f"{Fore.GREEN}✓ Modo teste - sem live real!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Formato: [Nome] mensagem{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Exemplo: [João] oi mirai!{Style.RESET_ALL}\n")
        print(f"{Fore.CYAN}Digite 'sair' para voltar{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        self.speaker.speak("Olá chat! Modo teste ativado!")
        
        text_input = TextInput()
        
        while True:
            user_input = text_input.get_input(f"{Fore.CYAN}[Chat]: {Style.RESET_ALL}")
            
            if not user_input or user_input.lower() == 'sair':
                break
            
            # Parse [Nome] mensagem
            if user_input.startswith('[') and ']' in user_input:
                parts = user_input.split(']', 1)
                author = parts[0][1:].strip()
                message = parts[1].strip() if len(parts) > 1 else ""
            else:
                author = "Viewer"
                message = user_input
            
            if message:
                # Mostra
                print(f"{Fore.CYAN}💬 {author}: {message}{Style.RESET_ALL}")
                
                # Responde
                if await self._should_respond(message):
                    await self._respond_to_chat(author, message)
            
            await asyncio.sleep(0.5)
    
    async def _should_respond(self, message):
        """Decide se responde"""
        import time as time_module
        
        # Cooldown
        now = time_module.time()
        if now - self.last_response < self.response_cooldown:
            return False
        
        # Muito curto
        if len(message) < 3:
            return False
        
        msg_lower = message.lower()
        
        # Menciona Mirai
        if any(word in msg_lower for word in ['mirai', 'oi mirai', 'hey mirai']):
            return True
        
        # Pergunta
        if '?' in message:
            import random
            return random.random() < 0.3
        
        return False
    
    async def _respond_to_chat(self, author, message):
        """Responde chat"""
        import time as time_module
        
        self.last_response = time_module.time()
        
        # Gera resposta
        response = self.ai.generate_response(message, mode="gamer")
        
        # Mostra
        print(f"\n{Fore.MAGENTA}🌸 Mirai → {author}: {response}{Style.RESET_ALL}\n")
        self.speaker.speak(f"{author}, {response}")


# Bot Twitch (se disponível)
if TWITCH_OK:
    class MiraiTwitchBot(twitch_commands.Bot):
        """Bot Twitch da Mirai"""
        
        def __init__(self, token, prefix, initial_channels, mirai_mode):
            super().__init__(
                token=token,
                prefix=prefix,
                initial_channels=initial_channels
            )
            self.mirai = mirai_mode
        
        async def event_ready(self):
            print(f"{Fore.GREEN}✓ Conectado à Twitch!{Style.RESET_ALL}\n")
            await self.mirai.speaker.speak("Conectada à Twitch!")
        
        async def event_message(self, message):
            if message.echo:
                return
            
            author = message.author.name
            content = message.content
            
            # Registra
            self.mirai.last_messages.append({
                'author': author,
                'message': content,
                'time': datetime.now()
            })
            
            # Mostra
            print(f"{Fore.CYAN}💬 {author}: {content}{Style.RESET_ALL}")
            
            # Responde
            if await self.mirai._should_respond(content):
                await self.mirai._respond_to_chat(author, content)


# Teste
if __name__ == "__main__":
    print("=== TESTE MODO STREAMER ===\n")
    print("Dependências opcionais:")
    print(f"  YouTube: {'✓' if YOUTUBE_OK else '✗ pip install pytchat'}")
    print(f"  Twitch: {'✓' if TWITCH_OK else '✗ pip install twitchio'}")
    print(f"\n✓ Chat Simulado sempre disponível!")