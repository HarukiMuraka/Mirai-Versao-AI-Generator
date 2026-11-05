"""
API Commands - Comandos para usar APIs externas na Mirai

Este arquivo adiciona comandos de voz e texto que usam as APIs externas
em vez de Python puro, resultando em melhor qualidade e performance.
"""

from api_integration_system import APIManager
import logging

logger = logging.getLogger(__name__)


class APICommands:
    """Comandos que usam APIs externas"""
    
    def __init__(self, api_manager: APIManager, speaker=None):
        self.apis = api_manager
        self.speaker = speaker
    
    def speak(self, text: str):
        """Fala texto se speaker disponível"""
        if self.speaker:
            self.speaker.speak(text)
        print(f"🌸 Mirai: {text}")
    
    # ========================================================================
    # COMANDOS DE MÚSICA (YouTube Music)
    # ========================================================================
    
    def play_music(self, query: str) -> str:
        """
        Toca música via YouTube Music
        
        Comandos de voz:
        - "tocar música bohemian rhapsody"
        - "tocar queen"
        - "música do metallica"
        - "play nothing else matters"
        
        Args:
            query: Nome da música/artista
        
        Returns:
            Resposta para o usuário
        """
        ytmusic = self.apis.get('youtube_music')
        
        if not ytmusic or not ytmusic.is_available():
            return "YouTube Music não está disponível. Instale: pip install ytmusicapi"
        
        if not query.strip():
            return "Qual música você quer ouvir?"
        
        # Busca e toca
        success = ytmusic.play(query)
        
        if success:
            # Pega info da música
            info = ytmusic.get_song_info(query)
            if info:
                title = info.get('title', query)
                artist = info.get('artists', [{}])[0].get('name', '')
                response = f"Tocando: {title}"
                if artist:
                    response += f" - {artist}"
                return response
            else:
                return f"Tocando: {query}"
        else:
            return f"Não encontrei '{query}' no YouTube Music"
    
    def search_music(self, query: str, limit: int = 5) -> str:
        """
        Busca músicas no YouTube Music
        
        Comandos de voz:
        - "buscar música beatles"
        - "procurar queen"
        - "músicas do pink floyd"
        
        Args:
            query: Texto de busca
            limit: Número de resultados
        
        Returns:
            Lista de resultados formatada
        """
        ytmusic = self.apis.get('youtube_music')
        
        if not ytmusic or not ytmusic.is_available():
            return "YouTube Music não disponível"
        
        if not query.strip():
            return "O que você quer buscar?"
        
        results = ytmusic.search(query, limit=limit)
        
        if not results:
            return f"Nenhuma música encontrada para: {query}"
        
        # Formata resposta
        response = f"Encontrei {len(results)} músicas:\n"
        for i, song in enumerate(results, 1):
            title = song.get('title', '')
            artist = song.get('artists', [{}])[0].get('name', '')
            response += f"{i}. {title}"
            if artist:
                response += f" - {artist}"
            response += "\n"
        
        return response.strip()
    
    # ========================================================================
    # COMANDOS DE OCR (EasyOCR)
    # ========================================================================
    
    def read_screen(self) -> str:
        """
        Lê texto da tela usando EasyOCR
        
        Comandos de voz:
        - "ler tela"
        - "o que tá escrito na tela"
        - "extrair texto da tela"
        - "copiar texto da tela"
        
        Returns:
            Texto extraído ou erro
        """
        ocr = self.apis.get('easyocr')
        
        if not ocr or not ocr.is_available():
            return "EasyOCR não disponível. Instale: pip install easyocr"
        
        self.speak("Lendo tela, aguarde...")
        
        text = ocr.read_screenshot()
        
        if text.strip():
            # Copia para clipboard
            try:
                import pyperclip
                pyperclip.copy(text)
                return f"Texto extraído e copiado:\n{text[:200]}..."
            except:
                return f"Texto extraído:\n{text[:200]}..."
        else:
            return "Não encontrei texto na tela"
    
    def read_image(self, image_path: str) -> str:
        """
        Lê texto de imagem
        
        Comandos de voz:
        - "ler imagem screenshot.png"
        - "extrair texto de foto.jpg"
        
        Args:
            image_path: Caminho da imagem
        
        Returns:
            Texto extraído
        """
        ocr = self.apis.get('easyocr')
        
        if not ocr or not ocr.is_available():
            return "EasyOCR não disponível"
        
        from pathlib import Path
        
        img_path = Path(image_path)
        if not img_path.exists():
            return f"Imagem não encontrada: {image_path}"
        
        self.speak("Lendo imagem...")
        
        text = ocr.read_image(str(img_path))
        
        if text.strip():
            return f"Texto extraído:\n{text}"
        else:
            return "Não encontrei texto na imagem"
    
    # ========================================================================
    # COMANDOS DE SCREENSHOT (ShareX)
    # ========================================================================
    
    def screenshot(self) -> str:
        """
        Captura tela inteira
        
        Comandos de voz:
        - "tirar screenshot"
        - "capturar tela"
        - "print screen"
        - "printar tela"
        
        Returns:
            Resultado da operação
        """
        sharex = self.apis.get('sharex')
        
        if not sharex or not sharex.is_available():
            # Fallback para pyautogui
            return self._screenshot_fallback()
        
        success = sharex.capture_screen()
        
        if success:
            return "Screenshot capturada! ShareX vai processar."
        else:
            return "Erro ao capturar screenshot"
    
    def screenshot_region(self) -> str:
        """
        Captura região selecionada
        
        Comandos de voz:
        - "screenshot de região"
        - "capturar área"
        - "printar seleção"
        
        Returns:
            Resultado da operação
        """
        sharex = self.apis.get('sharex')
        
        if not sharex or not sharex.is_available():
            return "ShareX não disponível. Baixe em: https://getsharex.com/"
        
        success = sharex.capture_region()
        
        if success:
            return "Selecione a região na tela!"
        else:
            return "Erro ao capturar região"
    
    def _screenshot_fallback(self) -> str:
        """Fallback usando pyautogui"""
        try:
            import pyautogui
            from datetime import datetime
            from pathlib import Path
            
            # Salva screenshot
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            save_path = Path("data/screenshots") / filename
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            screenshot = pyautogui.screenshot()
            screenshot.save(save_path)
            
            return f"Screenshot salva: {save_path}"
        
        except Exception as e:
            return f"Erro ao capturar screenshot: {e}"
    
    # ========================================================================
    # COMANDOS DE AUTOMAÇÃO (AutoHotkey)
    # ========================================================================
    
    def type_fast(self, text: str) -> str:
        """
        Digita texto rapidamente
        
        Comandos de voz:
        - "digitar [texto]"
        - "escrever [texto]"
        
        Args:
            text: Texto para digitar
        
        Returns:
            Resultado
        """
        ahk = self.apis.get('autohotkey')
        
        if ahk and ahk.is_available():
            success = ahk.type_text_fast(text)
            if success:
                return f"Digitando: {text}"
            else:
                return "Erro ao digitar"
        else:
            # Fallback pyautogui
            try:
                import pyautogui
                pyautogui.write(text, interval=0.01)
                return f"Digitado: {text}"
            except Exception as e:
                return f"Erro: {e}"
    
    def press_shortcut(self, shortcut: str) -> str:
        """
        Pressiona atalho de teclado
        
        Comandos de voz:
        - "pressionar ctrl c" -> Ctrl+C
        - "apertar alt f4" -> Alt+F4
        - "tecla windows" -> Win
        
        Args:
            shortcut: Atalho (ex: "ctrl+c", "alt+tab")
        
        Returns:
            Resultado
        """
        # Converte para formato AHK
        ahk_shortcut = self._convert_to_ahk_shortcut(shortcut)
        
        ahk = self.apis.get('autohotkey')
        
        if ahk and ahk.is_available():
            success = ahk.press_keys(ahk_shortcut)
            if success:
                return f"Pressionado: {shortcut}"
            else:
                return "Erro ao pressionar teclas"
        else:
            # Fallback pyautogui
            try:
                import pyautogui
                pyautogui.hotkey(*shortcut.split('+'))
                return f"Pressionado: {shortcut}"
            except Exception as e:
                return f"Erro: {e}"
    
    def _convert_to_ahk_shortcut(self, shortcut: str) -> str:
        """Converte atalho para formato AHK"""
        # AHK usa: ^ = Ctrl, ! = Alt, + = Shift, # = Win
        shortcut = shortcut.lower().replace(' ', '')
        
        replacements = {
            'ctrl+': '^',
            'alt+': '!',
            'shift+': '+',
            'win+': '#',
            'windows+': '#',
        }
        
        for old, new in replacements.items():
            shortcut = shortcut.replace(old, new)
        
        return shortcut
    
    # ========================================================================
    # COMANDOS COMBINADOS
    # ========================================================================
    
    def screenshot_and_read(self) -> str:
        """
        Captura tela E lê texto
        
        Comandos de voz:
        - "ler e copiar tela"
        - "screenshot com texto"
        - "capturar e extrair texto"
        
        Returns:
            Texto extraído
        """
        # Primeiro captura
        self.speak("Capturando tela...")
        self.screenshot()
        
        # Depois lê
        import time
        time.sleep(0.5)  # Aguarda um pouco
        
        return self.read_screen()


# ============================================================================
# INTEGRAÇÃO COM MIRAI
# ============================================================================

def integrate_api_commands_with_mirai(mirai_instance):
    """
    Integra comandos de API com a Mirai
    
    Adiciona comandos aos modos Assistente e Voz Ativa
    """
    # Inicializa APIs
    api_manager = APIManager()
    api_manager.initialize_all()
    
    # Cria comandos
    api_commands = APICommands(api_manager, mirai_instance.speaker)
    
    # Salva na instância da Mirai
    mirai_instance.api_manager = api_manager
    mirai_instance.api_commands = api_commands
    
    logger.info("✓ Comandos de API integrados à Mirai")
    
    return api_commands


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Simula integração
    api_manager = APIManager()
    api_manager.initialize_all()
    
    commands = APICommands(api_manager)
    
    print("\n=== TESTE DE COMANDOS ===\n")
    
    # Teste música
    print("1. Tocando música:")
    result = commands.play_music("Bohemian Rhapsody")
    print(f"   {result}\n")
    
    # Teste busca
    print("2. Buscando músicas:")
    result = commands.search_music("Queen", limit=3)
    print(f"   {result}\n")
    
    # Teste OCR
    print("3. Lendo tela:")
    # result = commands.read_screen()
    # print(f"   {result}\n")
    
    # Teste screenshot
    print("4. Screenshot:")
    result = commands.screenshot()
    print(f"   {result}\n")
    
    print("✅ Testes concluídos!")