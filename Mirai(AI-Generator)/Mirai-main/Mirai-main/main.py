import sys
import asyncio
from colorama import init, Fore, Style
from pathlib import Path

# Garante que o diretório do projeto está no path
sys.path.insert(0, str(Path(__file__).parent))

init(autoreset=True)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers de importação segura
# ──────────────────────────────────────────────────────────────────────────────

def _try_import(dotted_path: str, attr: str = None):
    """Importa módulo/atributo sem lançar exceção; retorna None se falhar."""
    try:
        import importlib
        mod = importlib.import_module(dotted_path)
        return getattr(mod, attr) if attr else mod
    except Exception as e:
        print(f"{Fore.YELLOW}  ⚠ Módulo '{dotted_path}' não carregado: {e}{Style.RESET_ALL}")
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Classe principal
# ──────────────────────────────────────────────────────────────────────────────

class Mirai:

    def __init__(self):
        self._print_banner()

        # Núcleo
        self.ai       = None
        self.context  = None
        self.state    = None

        # Saídas / entradas
        self.speaker  = None
        self.voice    = None

        # Avatar
        self.vtuber   = None

        # Memória
        self.memoria  = None

        # Features de IA
        self.text_gen  = None
        self.image_gen = None
        self.knowledge = None

        # Menu / UI
        self.menu    = None
        self.running = False

    # ── banner ─────────────────────────────────────────────────────────────

    def _print_banner(self):
        print(f"\n{Fore.MAGENTA}╔══════════════════════════════╗")
        print(f"{Fore.MAGENTA}║         🌸 MIRAI 🌸          ║")
        print(f"{Fore.MAGENTA}║   IA VTuber Assistant v2.0   ║")
        print(f"{Fore.MAGENTA}╚══════════════════════════════╝{Style.RESET_ALL}\n")

    # ── inicialização ───────────────────────────────────────────────────────

    async def initialize(self) -> bool:
        print(f"{Fore.CYAN}[INFO] Iniciando sistemas...{Style.RESET_ALL}\n")

        # 1. Contexto (obrigatório)
        self._step("Gerenciador de contexto")
        ContextManager = _try_import("core.context_manager", "ContextManager")
        if not ContextManager:
            print(f"{Fore.RED}✗ ContextManager é obrigatório!{Style.RESET_ALL}")
            return False
        self.context = ContextManager()
        self._ok()

        # 2. Estado (opcional — não quebra se faltar)
        self._step("Máquina de estados")
        StateMachine = _try_import("core.state_machine", "StateMachine")
        self.state = StateMachine() if StateMachine else None
        self._ok(self.state is not None)

        # 3. AI Engine (obrigatório)
        self._step("Motor de IA")
        MiraiAI = _try_import("core.ai_engine", "MiraiAI")
        if not MiraiAI:
            print(f"{Fore.RED}✗ MiraiAI é obrigatório!{Style.RESET_ALL}")
            return False
        self.ai = MiraiAI(self.context)
        await self.ai.initialize()
        self._ok()

        # 4. Features de IA
        self._step("Gerador de texto")
        TextGenerator = _try_import("features.text_generator", "TextGenerator")
        self.text_gen = TextGenerator(self.ai) if TextGenerator else None
        self._ok(self.text_gen is not None)

        self._step("Gerador de imagens")
        ImageGenerator = _try_import("features.image_generator", "ImageGenerator")
        if ImageGenerator:
            self.image_gen = ImageGenerator()
            await self.image_gen.initialize()
        self._ok(self.image_gen is not None)

        self._step("Knowledge Manager")
        KnowledgeManager = _try_import("features.knowledge_manager", "KnowledgeManager")
        self.knowledge = KnowledgeManager(self.ai) if KnowledgeManager else None
        self._ok(self.knowledge is not None)

        # 5. Voz (opcional)
        self._step("Sistema de voz (speaker)")
        Speaker = _try_import("actions.speaker", "Speaker")
        if Speaker:
            try:
                self.speaker = Speaker()
                result = self.speaker.initialize()
                if asyncio.iscoroutine(result):
                    await result
                self._ok()
            except Exception as e:
                print(f"{Fore.YELLOW}  ⚠ Speaker falhou: {e}{Style.RESET_ALL}")
                self.speaker = None

        self._step("Reconhecimento de voz")
        VoiceListener = _try_import("perception.voice_listener", "VoiceListener")
        self.voice = VoiceListener() if VoiceListener else None
        self._ok(self.voice is not None)

        # 6. VTuber (opcional)
        self._step("VTuber engine")
        VTuberEngine = _try_import("vtuber.vrm_engine", "VRMEngine")
        if VTuberEngine:
            try:
                self.vtuber = VTuberEngine()
                ok = await self.vtuber.initialize()
                if not ok:
                    self.vtuber = None
                    print(f"{Fore.YELLOW}  ⚠ VTuber não disponível (modo texto){Style.RESET_ALL}")
                else:
                    self._ok()
            except Exception:
                self.vtuber = None

        # 7. Memória (opcional)
        self._step("Sistema de memória")
        MemoriaCompleta = _try_import("memory.sistema_memoria", "MemoriaCompleta")
        if MemoriaCompleta:
            try:
                self.memoria = MemoriaCompleta()
                stats = self.memoria.get_estatisticas()
                print(f"  ✓ Memória: {stats.get('total_conversas', 0)} conversas salvas")
            except Exception as e:
                print(f"{Fore.YELLOW}  ⚠ Memória: {e}{Style.RESET_ALL}")

        # 8. Menu
        self._step("Interface/Menu")
        MainMenu = _try_import("interface.menu", "MainMenu")
        self.menu = MainMenu(self) if MainMenu else None
        self._ok(self.menu is not None)

        print(f"\n{Fore.GREEN}✓ Mirai pronta!{Style.RESET_ALL}\n")
        self.running = True
        return True

    def _step(self, name: str):
        print(f"{Fore.YELLOW}→ {name}...{Style.RESET_ALL}", end=" ", flush=True)

    def _ok(self, success: bool = True):
        if success:
            print(f"{Fore.GREEN}✓{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠ (opcional, ignorado){Style.RESET_ALL}")

    # ── run ─────────────────────────────────────────────────────────────────

    async def run(self):
        if not await self.initialize():
            print(f"{Fore.RED}Falha na inicialização. Verifique os módulos obrigatórios.{Style.RESET_ALL}")
            return

        greeting = self.ai.generate_greeting()
        print(f"{Fore.MAGENTA}Mirai: {greeting}{Style.RESET_ALL}\n")

        if self.speaker:
            try:
                self.speaker.speak(greeting)
            except Exception:
                pass

        if self.vtuber and getattr(self.vtuber, "is_active", False):
            try:
                await self.vtuber.set_expression("happy")
            except Exception:
                pass

        if self.menu:
            await self.menu.show()
        else:
            # Fallback: loop de conversa simples
            await self._simple_loop()

    async def _simple_loop(self):
        """Loop de conversa mínimo quando o menu não está disponível."""
        print(f"{Fore.CYAN}[Modo simples — menu não disponível]{Style.RESET_ALL}")
        print("Digite 'sair' para encerrar.\n")
        while self.running:
            try:
                user_input = input(f"{Fore.WHITE}Você: {Style.RESET_ALL}").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if not user_input:
                continue
            if user_input.lower() in ("sair", "exit", "quit"):
                break

            response = await self.ai.generate_response(user_input)
            print(f"{Fore.MAGENTA}Mirai: {response}{Style.RESET_ALL}\n")
            if self.speaker:
                try:
                    self.speaker.speak(response)
                except Exception:
                    pass

    # ── shutdown ─────────────────────────────────────────────────────────────

    async def shutdown(self):
        print(f"\n{Fore.CYAN}[INFO] Encerrando Mirai...{Style.RESET_ALL}")

        # Salva histórico na memória
        if self.memoria and self.context:
            try:
                recent = self.context.get_recent_context(10)
                for i in range(0, len(recent) - 1, 2):
                    if recent[i]["role"] == "user" and recent[i + 1]["role"] == "assistant":
                        self.memoria.salvar_conversa(recent[i]["content"], recent[i + 1]["content"])
                stats = self.memoria.get_estatisticas()
                print(f"{Fore.CYAN}Sessão salva: {stats.get('conversas_sessao', 0)} conversas{Style.RESET_ALL}")
            except Exception:
                pass

        # Salva knowledge
        if self.knowledge:
            try:
                self.knowledge._save(
                    Path("memory/knowledge.json"),
                    self.knowledge.knowledge
                )
            except Exception:
                pass

        farewell = self.ai.generate_farewell() if self.ai else "Até logo!"
        print(f"{Fore.MAGENTA}Mirai: {farewell}{Style.RESET_ALL}")

        if self.speaker:
            try:
                self.speaker.speak(farewell)
            except Exception:
                pass

        if self.vtuber and getattr(self.vtuber, "is_active", False):
            try:
                await self.vtuber.set_expression("sad")
                await self.vtuber.stop()
            except Exception:
                pass

        self.running = False
        print(f"{Fore.GREEN}Até logo! ✨{Style.RESET_ALL}\n")


# ──────────────────────────────────────────────────────────────────────────────

async def main():
    mirai = Mirai()
    try:
        await mirai.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[INFO] Interrompido pelo usuário{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[ERRO CRÍTICO] {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
    finally:
        await mirai.shutdown()


if __name__ == "__main__":
    asyncio.run(main())