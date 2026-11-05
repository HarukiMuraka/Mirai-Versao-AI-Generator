"""
API Integration System - Sistema de Integração com APIs Externas

Substitui funcionalidades Python puras por APIs e ferramentas especializadas:
- YouTube Music API para música
- Tesseract/EasyOCR para OCR (melhor que Python puro)
- ShareX para screenshots
- AutoHotkey para automação Windows
- E muito mais!
"""

import os
import subprocess
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


# ============================================================================
# BASE DO INTEGRADOR DE API
# ============================================================================

class ExternalAPI(ABC):
    """Classe base para integrações com APIs externas"""
    
    def __init__(self):
        self.enabled = False
        self.config = {}
    
    @abstractmethod
    def initialize(self) -> bool:
        """Inicializa a API"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Verifica se API está disponível"""
        pass
    
    def get_config_path(self) -> Path:
        """Retorna caminho do arquivo de config"""
        return Path("config") / "apis" / f"{self.__class__.__name__.lower()}.json"
    
    def load_config(self):
        """Carrega configuração da API"""
        config_path = self.get_config_path()
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar config de {self.__class__.__name__}: {e}")
    
    def save_config(self):
        """Salva configuração da API"""
        config_path = self.get_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar config de {self.__class__.__name__}: {e}")


# ============================================================================
# YOUTUBE MUSIC API
# ============================================================================

class YouTubeMusicAPI(ExternalAPI):
    """
    Integração com YouTube Music
    
    Dependências:
        pip install ytmusicapi
    
    Setup:
        1. ytmusicapi oauth
        2. Autoriza no navegador
        3. Salva oauth.json
    """
    
    def __init__(self):
        super().__init__()
        self.ytmusic = None
    
    def initialize(self) -> bool:
        """Inicializa YouTube Music"""
        try:
            from ytmusicapi import YTMusic
            
            # Tenta carregar oauth
            oauth_path = Path("config/apis/youtube_oauth.json")
            
            if oauth_path.exists():
                self.ytmusic = YTMusic(str(oauth_path))
                self.enabled = True
                logger.info("✓ YouTube Music inicializado com OAuth")
                return True
            else:
                # Sem autenticação
                self.ytmusic = YTMusic()
                self.enabled = True
                logger.info("✓ YouTube Music inicializado (sem autenticação)")
                return True
        
        except ImportError:
            logger.warning("ytmusicapi não instalado: pip install ytmusicapi")
            return False
        except Exception as e:
            logger.error(f"Erro ao inicializar YouTube Music: {e}")
            return False
    
    def is_available(self) -> bool:
        """Verifica se está disponível"""
        return self.enabled and self.ytmusic is not None
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Busca música no YouTube Music
        
        Args:
            query: Texto de busca
            limit: Número máximo de resultados
        
        Returns:
            Lista de resultados [{title, artist, videoId, thumbnails}, ...]
        """
        if not self.is_available():
            return []
        
        try:
            results = self.ytmusic.search(query, filter="songs", limit=limit)
            return results
        except Exception as e:
            logger.error(f"Erro ao buscar no YouTube Music: {e}")
            return []
    
    def play(self, query: str) -> bool:
        """
        Busca e abre música no navegador
        
        Args:
            query: Nome da música
        
        Returns:
            True se abriu com sucesso
        """
        if not self.is_available():
            return False
        
        # Busca
        results = self.search(query, limit=1)
        
        if not results:
            logger.warning(f"Nenhuma música encontrada para: {query}")
            return False
        
        song = results[0]
        video_id = song.get('videoId')
        
        if not video_id:
            return False
        
        # Abre no navegador
        url = f"https://music.youtube.com/watch?v={video_id}"
        
        try:
            import webbrowser
            webbrowser.open(url)
            logger.info(f"Abrindo: {song.get('title')} - {song.get('artists', [{}])[0].get('name', '')}")
            return True
        except Exception as e:
            logger.error(f"Erro ao abrir música: {e}")
            return False
    
    def get_song_info(self, query: str) -> Optional[Dict]:
        """
        Retorna informações sobre música
        
        Returns:
            {title, artist, album, duration, videoId, thumbnails}
        """
        if not self.is_available():
            return None
        
        results = self.search(query, limit=1)
        if results:
            return results[0]
        return None


# ============================================================================
# EASY OCR (Melhor que Python puro)
# ============================================================================

class EasyOCRAPI(ExternalAPI):
    """
    EasyOCR - OCR de alta qualidade
    
    Dependências:
        pip install easyocr
    
    Vantagens sobre Tesseract:
    - Mais preciso
    - Suporta 80+ idiomas
    - Não precisa instalar binário externo
    - Melhor com texto em imagens complexas
    """
    
    def __init__(self):
        super().__init__()
        self.reader = None
    
    def initialize(self) -> bool:
        """Inicializa EasyOCR"""
        try:
            import easyocr
            
            # Cria reader com português e inglês
            self.reader = easyocr.Reader(['pt', 'en'], gpu=False)
            self.enabled = True
            logger.info("✓ EasyOCR inicializado")
            return True
        
        except ImportError:
            logger.warning("easyocr não instalado: pip install easyocr")
            return False
        except Exception as e:
            logger.error(f"Erro ao inicializar EasyOCR: {e}")
            return False
    
    def is_available(self) -> bool:
        """Verifica se está disponível"""
        return self.enabled and self.reader is not None
    
    def read_image(self, image_path: str) -> str:
        """
        Extrai texto de imagem
        
        Args:
            image_path: Caminho da imagem
        
        Returns:
            Texto extraído
        """
        if not self.is_available():
            return ""
        
        try:
            result = self.reader.readtext(image_path)
            
            # Extrai apenas o texto
            text = " ".join([detection[1] for detection in result])
            return text
        
        except Exception as e:
            logger.error(f"Erro ao ler imagem: {e}")
            return ""
    
    def read_screenshot(self) -> str:
        """
        Captura tela e extrai texto
        
        Returns:
            Texto extraído da tela
        """
        if not self.is_available():
            return ""
        
        try:
            import pyautogui
            import tempfile
            
            # Captura tela
            screenshot = pyautogui.screenshot()
            
            # Salva temporariamente
            temp_path = Path(tempfile.gettempdir()) / "mirai_screenshot.png"
            screenshot.save(temp_path)
            
            # Lê texto
            text = self.read_image(str(temp_path))
            
            # Remove temp
            try:
                temp_path.unlink()
            except:
                pass
            
            return text
        
        except Exception as e:
            logger.error(f"Erro ao ler screenshot: {e}")
            return ""


# ============================================================================
# SHAREX (Screenshot e Upload)
# ============================================================================

class ShareXAPI(ExternalAPI):
    """
    ShareX - Ferramenta profissional de screenshots
    
    Download: https://getsharex.com/
    
    Vantagens:
    - Capturas melhores que Python
    - Upload automático
    - Edição de imagens
    - Gravação de tela/GIF
    - Hotkeys configuráveis
    """
    
    def __init__(self):
        super().__init__()
        self.sharex_path = None
    
    def initialize(self) -> bool:
        """Inicializa ShareX"""
        # Procura ShareX instalado
        possible_paths = [
            Path(r"C:\Program Files\ShareX\ShareX.exe"),
            Path(r"C:\Program Files (x86)\ShareX\ShareX.exe"),
            Path.home() / "AppData" / "Local" / "ShareX" / "ShareX.exe",
        ]
        
        for path in possible_paths:
            if path.exists():
                self.sharex_path = path
                self.enabled = True
                logger.info(f"✓ ShareX encontrado: {path}")
                return True
        
        logger.warning("ShareX não encontrado. Baixe em: https://getsharex.com/")
        return False
    
    def is_available(self) -> bool:
        """Verifica se está disponível"""
        return self.enabled and self.sharex_path is not None
    
    def capture_screen(self) -> bool:
        """
        Captura tela inteira
        
        Returns:
            True se capturou
        """
        if not self.is_available():
            return False
        
        try:
            # ShareX CLI: -capture
            subprocess.Popen([str(self.sharex_path), "-capture"])
            return True
        except Exception as e:
            logger.error(f"Erro ao capturar tela: {e}")
            return False
    
    def capture_region(self) -> bool:
        """
        Captura região selecionada
        
        Returns:
            True se capturou
        """
        if not self.is_available():
            return False
        
        try:
            # ShareX CLI: -RegionCapture
            subprocess.Popen([str(self.sharex_path), "-RegionCapture"])
            return True
        except Exception as e:
            logger.error(f"Erro ao capturar região: {e}")
            return False
    
    def capture_window(self) -> bool:
        """
        Captura janela ativa
        
        Returns:
            True se capturou
        """
        if not self.is_available():
            return False
        
        try:
            subprocess.Popen([str(self.sharex_path), "-CaptureActiveWindow"])
            return True
        except Exception as e:
            logger.error(f"Erro ao capturar janela: {e}")
            return False


# ============================================================================
# AUTOHOTKEY (Automação Windows Avançada)
# ============================================================================

class AutoHotkeyAPI(ExternalAPI):
    """
    AutoHotkey - Automação Windows profissional
    
    Download: https://www.autohotkey.com/
    
    Vantagens sobre pyautogui:
    - Muito mais rápido
    - Mais confiável
    - Hotkeys globais
    - Manipulação de janelas avançada
    - Scripts compiláveis
    """
    
    def __init__(self):
        super().__init__()
        self.ahk_path = None
    
    def initialize(self) -> bool:
        """Inicializa AutoHotkey"""
        # Procura AutoHotkey instalado
        possible_paths = [
            Path(r"C:\Program Files\AutoHotkey\AutoHotkey.exe"),
            Path(r"C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe"),
        ]
        
        for path in possible_paths:
            if path.exists():
                self.ahk_path = path
                self.enabled = True
                logger.info(f"✓ AutoHotkey encontrado: {path}")
                return True
        
        logger.warning("AutoHotkey não encontrado. Baixe em: https://www.autohotkey.com/")
        return False
    
    def is_available(self) -> bool:
        """Verifica se está disponível"""
        return self.enabled and self.ahk_path is not None
    
    def run_script(self, script: str) -> bool:
        """
        Executa script AHK
        
        Args:
            script: Código AutoHotkey
        
        Returns:
            True se executou
        """
        if not self.is_available():
            return False
        
        try:
            import tempfile
            
            # Salva script temporário
            temp_script = Path(tempfile.gettempdir()) / "mirai_ahk_temp.ahk"
            with open(temp_script, 'w', encoding='utf-8') as f:
                f.write(script)
            
            # Executa
            subprocess.Popen([str(self.ahk_path), str(temp_script)])
            return True
        
        except Exception as e:
            logger.error(f"Erro ao executar script AHK: {e}")
            return False
    
    def type_text_fast(self, text: str) -> bool:
        """
        Digita texto MUITO mais rápido que pyautogui
        
        Args:
            text: Texto para digitar
        """
        script = f'''
SendInput, {text}
ExitApp
'''
        return self.run_script(script)
    
    def press_keys(self, keys: str) -> bool:
        """
        Pressiona teclas/combinações
        
        Args:
            keys: Teclas (ex: "^c" = Ctrl+C)
        """
        script = f'''
Send, {keys}
ExitApp
'''
        return self.run_script(script)
    
    def move_window(self, title: str, x: int, y: int, w: int, h: int) -> bool:
        """
        Move e redimensiona janela
        
        Args:
            title: Título da janela
            x, y: Posição
            w, h: Tamanho
        """
        script = f'''
WinMove, {title},, {x}, {y}, {w}, {h}
ExitApp
'''
        return self.run_script(script)


# ============================================================================
# GERENCIADOR DE APIs
# ============================================================================

class APIManager:
    """Gerencia todas as APIs externas"""
    
    def __init__(self):
        self.apis: Dict[str, ExternalAPI] = {}
        self._register_apis()
    
    def _register_apis(self):
        """Registra APIs disponíveis"""
        self.apis = {
            'youtube_music': YouTubeMusicAPI(),
            'easyocr': EasyOCRAPI(),
            'sharex': ShareXAPI(),
            'autohotkey': AutoHotkeyAPI(),
        }
    
    def initialize_all(self):
        """Inicializa todas as APIs"""
        logger.info("Inicializando APIs externas...")
        
        for name, api in self.apis.items():
            api.load_config()
            if api.initialize():
                logger.info(f"  ✓ {name}")
            else:
                logger.info(f"  ✗ {name} (não disponível)")
    
    def get(self, name: str) -> Optional[ExternalAPI]:
        """
        Retorna API pelo nome
        
        Args:
            name: Nome da API
        
        Returns:
            Instância da API ou None
        """
        return self.apis.get(name)
    
    def is_available(self, name: str) -> bool:
        """Verifica se API está disponível"""
        api = self.get(name)
        return api.is_available() if api else False
    
    def list_available(self) -> List[str]:
        """Lista APIs disponíveis"""
        return [
            name for name, api in self.apis.items()
            if api.is_available()
        ]
    
    def list_unavailable(self) -> List[str]:
        """Lista APIs não disponíveis"""
        return [
            name for name, api in self.apis.items()
            if not api.is_available()
        ]


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Cria gerenciador
    manager = APIManager()
    manager.initialize_all()
    
    print("\n=== APIs DISPONÍVEIS ===")
    for api_name in manager.list_available():
        print(f"  ✓ {api_name}")
    
    print("\n=== APIs NÃO DISPONÍVEIS ===")
    for api_name in manager.list_unavailable():
        print(f"  ✗ {api_name}")
    
    # Teste YouTube Music
    print("\n=== TESTE YOUTUBE MUSIC ===")
    ytmusic = manager.get('youtube_music')
    if ytmusic and ytmusic.is_available():
        # Busca música
        results = ytmusic.search("Bohemian Rhapsody", limit=3)
        print(f"\nResultados para 'Bohemian Rhapsody':")
        for i, song in enumerate(results, 1):
            title = song.get('title', '')
            artist = song.get('artists', [{}])[0].get('name', '')
            print(f"  {i}. {title} - {artist}")
        
        # Toca primeira
        # ytmusic.play("Bohemian Rhapsody")
    
    # Teste EasyOCR
    print("\n=== TESTE EASYOCR ===")
    ocr = manager.get('easyocr')
    if ocr and ocr.is_available():
        print("EasyOCR pronto para uso!")
        # text = ocr.read_screenshot()
        # print(f"Texto da tela: {text}")
    
    # Teste ShareX
    print("\n=== TESTE SHAREX ===")
    sharex = manager.get('sharex')
    if sharex and sharex.is_available():
        print("ShareX disponível!")
        # sharex.capture_region()
    
    # Teste AutoHotkey
    print("\n=== TESTE AUTOHOTKEY ===")
    ahk = manager.get('autohotkey')
    if ahk and ahk.is_available():
        print("AutoHotkey disponível!")
        # ahk.type_text_fast("Hello from Mirai!")