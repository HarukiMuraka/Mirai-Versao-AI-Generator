from abc import ABC, abstractmethod

class BaseMode(ABC):
    def __init__(self, mirai_instance):
        self.mirai = mirai_instance
        self.ai = mirai_instance.ai
        self.context = mirai_instance.context
        self.state = mirai_instance.state
        self.vtuber = mirai_instance.vtuber
        self.speaker = mirai_instance.speaker
        self.is_active = False
    
    @abstractmethod
    async def enter(self):
        pass
    
    @abstractmethod
    async def exit(self):
        pass
    
    @abstractmethod
    async def process_input(self, user_input):
        pass
    
    def print_mode_header(self, title):
        from colorama import Fore, Style
        print(f"\\n{Fore.CYAN}{'='*50}")
        print(f"{Fore.MAGENTA}🌸 {title}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\\n")