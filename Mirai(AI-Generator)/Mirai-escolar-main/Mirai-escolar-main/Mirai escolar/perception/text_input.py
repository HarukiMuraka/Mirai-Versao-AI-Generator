class TextInput:
    """Gerencia entrada de texto do usuário"""
    
    def __init__(self):
        # Removemos prompt_toolkit para evitar conflitos com asyncio
        pass
    
    def get_input(self, prompt_text="Você: "):
        """Obtém input do usuário usando input() padrão"""
        try:
            # Usa input() nativo do Python
            # Funciona perfeitamente com asyncio
            user_input = input(prompt_text)
            return user_input.strip()
        except KeyboardInterrupt:
            return None
        except EOFError:
            return None
    
    def get_multiline_input(self, prompt_text="Você (Ctrl+Z + Enter para enviar): "):
        """Obtém input de múltiplas linhas"""
        try:
            lines = []
            print(prompt_text)
            while True:
                try:
                    line = input()
                    lines.append(line)
                except EOFError:
                    break
            return '\n'.join(lines).strip()
        except KeyboardInterrupt:
            return None