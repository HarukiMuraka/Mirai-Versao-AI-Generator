import sys
import asyncio
from colorama import init, Fore, Style
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from interface.menu import MainMenu
from core.ai_engine import MiraiAI
from core.state_machine import StateMachine
from core.context_manager import ContextManager
from vtuber.vrm_engine import VRMEngine as VTuberEngine
from perception.voice_listener import VoiceListener
from actions.speaker import Speaker
from memory.sistema_memoria import MemoriaCompleta  # NOVO!

init(autoreset=True)

class Mirai:
    """Classe principal da Mirai COM MEMÓRIA"""
    
    def __init__(self):
        self.print_banner()
        self.ai = None
        self.vtuber = None
        self.state = None
        self.context = None
        self.menu = None
        self.voice = None
        self.speaker = None
        self.memoria = None  # NOVO!
        self.running = False
        
    def print_banner(self):
        """Mostra o banner inicial"""
        print(f"\n{Fore.MAGENTA}╔════════════════════════════╗")
        print(f"{Fore.MAGENTA}║        🌸 MIRAI 🌸        ║")
        print(f"{Fore.MAGENTA}║    IA VTuber Local v1.0    ║")
        print(f"{Fore.MAGENTA}╚════════════════════════════╝{Style.RESET_ALL}\n")
        
    async def initialize(self):
        """Inicializa todos os componentes"""
        print(f"{Fore.CYAN}[INFO] Iniciando sistemas da Mirai...{Style.RESET_ALL}\n")
        
        try:
            # Context Manager
            print(f"{Fore.YELLOW}→ Inicializando gerenciador de contexto...{Style.RESET_ALL}")
            self.context = ContextManager()
            
            # State Machine
            print(f"{Fore.YELLOW}→ Inicializando máquina de estados...{Style.RESET_ALL}")
            self.state = StateMachine()
            
            # IA Engine
            print(f"{Fore.YELLOW}→ Carregando modelo de IA...{Style.RESET_ALL}")
            self.ai = MiraiAI(self.context)
            await self.ai.initialize()
            
            # Speaker (TTS)
            print(f"{Fore.YELLOW}→ Inicializando sistema de voz...{Style.RESET_ALL}")
            self.speaker = Speaker()
            self.speaker.initialize()
            
            # VTuber Engine (opcional)
            print(f"{Fore.YELLOW}→ Inicializando VTuber (se disponível)...{Style.RESET_ALL}")
            self.vtuber = VTuberEngine()
            vtuber_ready = await self.vtuber.initialize()
            if not vtuber_ready:
                print(f"{Fore.YELLOW}  ⚠ VTuber não disponível (modo texto){Style.RESET_ALL}")
            
            # Voice Listener
            print(f"{Fore.YELLOW}→ Inicializando reconhecimento de voz...{Style.RESET_ALL}")
            self.voice = VoiceListener()
            
            # SISTEMA DE MEMÓRIA - NOVO!
            print(f"{Fore.YELLOW}→ Inicializando sistema de memória...{Style.RESET_ALL}")
            self.memoria = MemoriaCompleta()
            stats = self.memoria.get_estatisticas()
            print(f"  ✓ Memória carregada ({stats['total_conversas']} conversas salvas)")
            
            # Menu
            self.menu = MainMenu(self)
            
            print(f"\n{Fore.GREEN}✓ Todos os sistemas prontos!{Style.RESET_ALL}\n")
            self.running = True
            return True
            
        except Exception as e:
            print(f"{Fore.RED}✗ Erro na inicialização: {e}{Style.RESET_ALL}")
            import traceback
            traceback.print_exc()
            return False
    
    async def run(self):
        """Loop principal"""
        if not await self.initialize():
            return
        
        # Saudação inicial
        greeting = self.ai.generate_greeting()
        print(f"{Fore.MAGENTA}Mirai: {greeting}{Style.RESET_ALL}\n")
        self.speaker.speak(greeting)
        
        if self.vtuber and self.vtuber.is_active:
            await self.vtuber.set_expression("happy")
        
        # Mostrar menu
        await self.menu.show()
    
    async def shutdown(self):
        """Encerra o sistema"""
        print(f"\n{Fore.CYAN}[INFO] Encerrando Mirai...{Style.RESET_ALL}")
        
        # SALVA CONTEXTO NA MEMÓRIA - NOVO!
        if self.memoria and self.context:
            print(f"{Fore.CYAN}Salvando conversas na memória...{Style.RESET_ALL}")
            recent = self.context.get_recent_context(10)
            
            for i in range(0, len(recent) - 1, 2):
                if recent[i]['role'] == 'user' and i + 1 < len(recent):
                    if recent[i + 1]['role'] == 'assistant':
                        self.memoria.salvar_conversa(
                            recent[i]['content'],
                            recent[i + 1]['content']
                        )
            
            # Estatísticas da sessão
            stats = self.memoria.get_estatisticas()
            print(f"Sessão atual: {stats['conversas_sessao']} conversas")
        
        farewell = self.ai.generate_farewell()
        print(f"{Fore.MAGENTA}Mirai: {farewell}{Style.RESET_ALL}")
        self.speaker.speak(farewell)
        
        if self.vtuber and self.vtuber.is_active:
            await self.vtuber.set_expression("sad")
            await self.vtuber.stop()
        
        self.running = False
        print(f"{Fore.GREEN}Até logo! ✨{Style.RESET_ALL}\n")

async def main():
    mirai = Mirai()
    try:
        await mirai.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[INFO] Interrompido pelo usuário{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[ERRO] {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
    finally:
        await mirai.shutdown()

if __name__ == "__main__":
    asyncio.run(main())