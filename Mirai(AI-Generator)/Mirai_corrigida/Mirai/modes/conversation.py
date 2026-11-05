"""
modes/conversation.py — Modo Conversa (CORRIGIDO)

Correções:
  1. Import: from mirai.modes.base_mode → from modes.base_mode
  2. Import: from mirai.perception.voice_listener → try/except sem prefixo
  3. generate_response() sem await → adicionado await
  4. Adicionado alias ConversationModeImproved = ConversationMode
     (menu.py importa ConversationModeImproved)
"""

from modes.base_mode import BaseMode
from colorama import Fore, Style
import asyncio
import time


def _input(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        return ""


class ConversationMode(BaseMode):
    def __init__(self, mirai_instance):
        super().__init__(mirai_instance)
        self.listening        = False
        self.autonomous_active = False

    async def enter(self):
        self.is_active = True
        if self.state:
            self.state.set_state("conversation")
        self.print_mode_header("MODO CONVERSA")

        print(f"{Fore.YELLOW}Escolha o tipo de conversa:{Style.RESET_ALL}")
        print("  1. Texto (recomendado)")
        print("  2. Voz (precisa SpeechRecognition)")
        print("  3. Autônoma (Mirai toma iniciativa)")
        print("  0. Voltar")

        choice = _input(f"\n{Fore.MAGENTA}Opção: {Style.RESET_ALL}")

        if   choice == "1": await self.text_conversation()
        elif choice == "2": await self.voice_conversation()
        elif choice == "3": await self.autonomous_conversation()

    async def exit(self):
        self.is_active         = False
        self.autonomous_active = False
        print(f"\n{Fore.CYAN}Saindo do modo conversa...{Style.RESET_ALL}")

    async def process_input(self, user_input: str, enable_search: bool = True):
        if not user_input or not user_input.strip():
            return None
        if user_input.lower() in {"sair", "exit", "voltar", "parar", "tchau"}:
            return "EXIT"
        # CORRIGIDO: await obrigatório
        return await self.mirai.ai.generate_response(
            user_input, mode="conversation", enable_search=enable_search
        )

    # ── conversa por texto ────────────────────────────────────────────

    async def text_conversation(self):
        print(f"\n{Fore.GREEN}Texto ativado! Digite \'sair\' para voltar.{Style.RESET_ALL}\n")

        greeting = self.mirai.ai.generate_greeting()
        print(f"{Fore.MAGENTA}Mirai: {greeting}{Style.RESET_ALL}\n")
        self._speak(greeting)

        while self.is_active:
            user_input = _input(f"{Fore.GREEN}Você: {Style.RESET_ALL}")
            if not user_input:
                continue

            print(f"{Fore.CYAN}Pensando...{Style.RESET_ALL}", end="\r")
            result = await self.process_input(user_input)
            print(" " * 40, end="\r")

            if result == "EXIT":
                msg = "Até logo! Foi legal conversar!"
                print(f"{Fore.MAGENTA}Mirai: {msg}{Style.RESET_ALL}\n")
                self._speak(msg)
                break

            if result:
                print(f"{Fore.MAGENTA}Mirai: {result}{Style.RESET_ALL}\n")
                self._speak(result[:200])

    # ── conversa por voz ─────────────────────────────────────────────

    async def voice_conversation(self):
        try:
            from perception.voice_listener import VoiceListener
        except ImportError:
            print(f"{Fore.RED}SpeechRecognition não instalado!")
            print(f"Instale: pip install SpeechRecognition{Style.RESET_ALL}")
            _input("Pressione Enter...")
            return

        print(f"\n{Fore.GREEN}Voz ativada! Diga \'sair\' para voltar.{Style.RESET_ALL}\n")

        voice = VoiceListener()
        if not voice.initialize():
            print(f"{Fore.RED}Erro ao inicializar microfone!{Style.RESET_ALL}")
            _input("Pressione Enter...")
            return

        while self.is_active:
            try:
                print(f"{Fore.CYAN}Escutando...{Style.RESET_ALL}", end="\r")
                user_input = voice.listen_once()
                print(" " * 40, end="\r")
                if not user_input:
                    continue
                print(f"{Fore.CYAN}Você: {user_input}{Style.RESET_ALL}")
                result = await self.process_input(user_input)
                if result == "EXIT":
                    break
                if result:
                    print(f"{Fore.MAGENTA}Mirai: {result}{Style.RESET_ALL}\n")
                    self._speak(result)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"{Fore.RED}Erro: {e}{Style.RESET_ALL}")

    # ── conversa autônoma ─────────────────────────────────────────────

    async def autonomous_conversation(self):
        print(f"\n{Fore.GREEN}Modo Autônomo! Mirai toma iniciativa após silêncio.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Digite \'parar\' para sair.{Style.RESET_ALL}\n")

        greeting = self.mirai.ai.generate_greeting()
        print(f"{Fore.MAGENTA}Mirai: {greeting}{Style.RESET_ALL}\n")
        self._speak(greeting)

        self.autonomous_active = True
        last_interaction       = time.time()
        silence_threshold      = 25  # segundos

        while self.is_active and self.autonomous_active:
            elapsed = time.time() - last_interaction

            if elapsed >= silence_threshold:
                initiative = self.mirai.ai.generate_initiative()
                print(f"{Fore.YELLOW}[Mirai percebe o silêncio]{Style.RESET_ALL}")
                print(f"{Fore.MAGENTA}Mirai: {initiative}{Style.RESET_ALL}\n")
                self._speak(initiative)
                last_interaction = time.time()
                continue

            print(f"{Fore.GREEN}Você: {Style.RESET_ALL}", end="", flush=True)
            try:
                import sys
                if sys.platform == "win32":
                    user_input = input()
                else:
                    import select
                    ready, _, _ = select.select([sys.stdin], [], [], 5)
                    user_input  = sys.stdin.readline().strip() if ready else ""

                if not user_input:
                    continue

                last_interaction = time.time()

                if user_input.lower() in {"parar", "sair", "exit"}:
                    msg = "Entendido! Foi legal conversar!"
                    print(f"\n{Fore.MAGENTA}Mirai: {msg}{Style.RESET_ALL}")
                    self._speak(msg)
                    break

                print(f"{Fore.CYAN}Pensando...{Style.RESET_ALL}", end="\r")
                result = await self.process_input(user_input)
                print(" " * 40, end="\r")

                if result and result != "EXIT":
                    print(f"{Fore.MAGENTA}Mirai: {result}{Style.RESET_ALL}\n")
                    self._speak(result)

            except Exception as e:
                print(f"\n{Fore.RED}Erro: {e}{Style.RESET_ALL}")

    # ── helper de voz ─────────────────────────────────────────────────

    def _speak(self, text: str):
        try:
            if self.speaker and self.speaker.enabled:
                # Não bloqueia o loop async
                asyncio.ensure_future(
                    asyncio.to_thread(self.speaker.speak, text[:200])
                )
        except Exception:
            pass


# Alias para compatibilidade com menu.py
# menu.py faz: from modes.conversation import ConversationModeImproved
ConversationModeImproved = ConversationMode