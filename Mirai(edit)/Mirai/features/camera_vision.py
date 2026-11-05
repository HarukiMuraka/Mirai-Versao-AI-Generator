import cv2
import base64
import asyncio
from io import BytesIO
from PIL import Image
from typing import Optional
from colorama import Fore, Style

class CameraVisionSystem:
    """Sistema de visão por câmera - IA vê você!"""
    
    def __init__(self, ai_engine):
        self.ai = ai_engine
        self.camera = None
        self.enabled = False
        self.monitoring = False
        
        # Configurações
        self.config = {
            "camera_index": 0,
            "capture_interval": 5,  # Captura a cada 5 segundos
            "analysis_interval": 30,  # Analisa a cada 30 segundos
            "face_detection": True,
            "emotion_detection": True,
        }
        
        # Face detection
        self.face_cascade = None
        
    def initialize(self) -> bool:
        """Inicializa câmera"""
        try:
            # Tenta abrir câmera
            self.camera = cv2.VideoCapture(self.config["camera_index"])
            
            if not self.camera.isOpened():
                print(f"{Fore.YELLOW}⚠ Câmera não disponível{Style.RESET_ALL}")
                return False
            
            # Carrega detector de faces
            try:
                self.face_cascade = cv2.CascadeClassifier(
                    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                )
            except:
                print(f"{Fore.YELLOW}⚠ Detector de faces não disponível{Style.RESET_ALL}")
            
            self.enabled = True
            print(f"{Fore.GREEN}✓ Câmera inicializada{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}✗ Erro ao inicializar câmera: {e}{Style.RESET_ALL}")
            return False
    
    def capture_frame(self) -> Optional[Image.Image]:
        """Captura frame atual"""
        if not self.camera or not self.camera.isOpened():
            return None
        
        try:
            ret, frame = self.camera.read()
            
            if not ret:
                return None
            
            # Converte BGR → RGB → PIL
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            
            return image
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ Erro ao capturar: {e}{Style.RESET_ALL}")
            return None
    
    def detect_faces(self, image: Image.Image) -> list:
        """Detecta faces na imagem"""
        if not self.face_cascade:
            return []
        
        try:
            # Converte PIL → numpy array
            import numpy as np
            frame = np.array(image)
            
            # Converte para grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            
            # Detecta faces
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(30, 30)
            )
            
            return faces.tolist() if len(faces) > 0 else []
            
        except Exception as e:
            return []
    
    async def analyze_with_gemini(self, image: Image.Image, prompt: str = None) -> str:
        """Analisa imagem com Gemini Vision"""
        try:
            # Converte imagem para base64
            buffered = BytesIO()
            image.save(buffered, format="JPEG", quality=85)
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Prompt padrão
            if not prompt:
                prompt = """Analise esta imagem rapidamente:
                
1. Quantas pessoas você vê?
2. O que elas estão fazendo?
3. Como elas parecem estar se sentindo?
4. Algo interessante acontecendo?

Responda em 2-3 frases curtas, de forma casual e amigável!"""

            # Chama Gemini Vision
            import google.generativeai as genai
            
            # Configura se ainda não configurado
            if not hasattr(self.ai, 'gemini_model'):
                return "Gemini Vision não configurado!"
            
            # Upload image
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            response = model.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": img_base64}
            ])
            
            return response.text.strip()
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ Erro em análise: {e}{Style.RESET_ALL}")
            return self._fallback_analysis(image)
    
    def _fallback_analysis(self, image: Image.Image) -> str:
        """Análise fallback (sem IA)"""
        # Detecta faces
        faces = self.detect_faces(image)
        
        if len(faces) == 0:
            return "Hmm, não tô te vendo na câmera! Tá aí?"
        elif len(faces) == 1:
            return "Te vejo aí! Como tá indo?"
        else:
            return f"Opa, vejo {len(faces)} pessoas aí! Galera reunida?"
    
    async def start_monitoring(self, callback=None):
        """Inicia monitoramento contínuo"""
        if not self.enabled:
            if not self.initialize():
                return
        
        self.monitoring = True
        print(f"{Fore.GREEN}✓ Monitoramento de câmera iniciado{Style.RESET_ALL}")
        
        # Loop de monitoramento
        asyncio.create_task(self._monitoring_loop(callback))
    
    def stop_monitoring(self):
        """Para monitoramento"""
        self.monitoring = False
        print(f"{Fore.YELLOW}⚠ Monitoramento parado{Style.RESET_ALL}")
    
    async def _monitoring_loop(self, callback=None):
        """Loop de monitoramento em background"""
        last_analysis = 0
        
        while self.monitoring:
            try:
                # Captura frame
                image = self.capture_frame()
                
                if image:
                    import time
                    current_time = time.time()
                    
                    # Analisa periodicamente
                    if current_time - last_analysis > self.config["analysis_interval"]:
                        # Analisa com IA
                        analysis = await self.analyze_with_gemini(image)
                        
                        print(f"\n{Fore.CYAN}📷 [Visão]: {analysis}{Style.RESET_ALL}\n")
                        
                        # Callback
                        if callback:
                            callback(analysis, image)
                        
                        last_analysis = current_time
                
                # Aguarda intervalo
                await asyncio.sleep(self.config["capture_interval"])
                
            except Exception as e:
                print(f"{Fore.YELLOW}⚠ Erro no monitor: {e}{Style.RESET_ALL}")
                await asyncio.sleep(5)
    
    def check_presence(self) -> tuple:
        """
        Verifica se usuário está presente
        Retorna: (presente: bool, num_faces: int)
        """
        image = self.capture_frame()
        
        if not image:
            return False, 0
        
        faces = self.detect_faces(image)
        return len(faces) > 0, len(faces)
    
    async def react_to_user_action(self, action: str):
        """IA reage a ação do usuário detectada por câmera"""
        reactions = {
            "wave": "Opa! Tá acenando pra mim? Oi! 👋",
            "leave": "Ei, onde você foi? Volta aqui!",
            "arrive": "Opa! Chegou! E aí, como tá?",
            "smile": "Aww, tá sorrindo! Que fofo! 😊",
            "frown": "Ei, tá triste? O que foi?",
        }
        
        reaction = reactions.get(action, "Hmm, o que você tá fazendo aí?")
        print(f"{Fore.MAGENTA}Mirai: {reaction}{Style.RESET_ALL}")
        
        return reaction
    
    def shutdown(self):
        """Encerra câmera"""
        self.monitoring = False
        
        if self.camera:
            self.camera.release()
            self.camera = None
        
        self.enabled = False
        print(f"{Fore.CYAN}✓ Câmera encerrada{Style.RESET_ALL}")


# Exemplo de uso simples
async def demo_camera():
    """Demo do sistema de câmera"""
    camera = CameraVisionSystem(None)
    
    if camera.initialize():
        print("Câmera funcionando!")
        
        # Captura e analisa
        image = camera.capture_frame()
        if image:
            analysis = await camera.analyze_with_gemini(image)
            print(f"Análise: {analysis}")
        
        camera.shutdown()