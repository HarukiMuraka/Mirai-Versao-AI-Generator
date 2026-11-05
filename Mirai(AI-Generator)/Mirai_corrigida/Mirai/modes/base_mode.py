"""modes/base_mode.py — Classe base para todos os modos."""

from abc import ABC, abstractmethod
from colorama import Fore, Style


class BaseMode(ABC):
    def __init__(self, mirai_instance):
        self.mirai   = mirai_instance
        self.ai      = mirai_instance.ai
        self.context = mirai_instance.context
        self.state   = mirai_instance.state
        self.vtuber  = mirai_instance.vtuber
        self.speaker = mirai_instance.speaker
        self.is_active = False

    @abstractmethod
    async def enter(self): ...

    @abstractmethod
    async def exit(self): ...

    @abstractmethod
    async def process_input(self, user_input): ...

    def print_mode_header(self, title: str):
        print(f"\n{Fore.CYAN}{'═'*52}")
        print(f"{Fore.MAGENTA}🌸 {title}")
        print(f"{Fore.CYAN}{'═'*52}{Style.RESET_ALL}\n")

    def _speak(self, text: str):
        if self.speaker and self.speaker.enabled:
            try:
                self.speaker.speak(text[:200])
            except Exception:
                pass