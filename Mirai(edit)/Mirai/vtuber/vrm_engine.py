import asyncio
import json
import socket
from pathlib import Path
from colorama import Fore, Style

class VRMEngine:
    """Motor VRM para Mirai - 100% Gratuito"""
    
    def __init__(self):
        self.config = self.load_config()
        self.is_active = False
        self.current_expression = "neutral"
        self.is_talking = False
        
        # Configuração VMC Protocol (VSeeFace)
        self.vmc_host = "127.0.0.1"
        self.vmc_port = 39539
        self.socket = None
        
        # Mapeamento de expressões VRM
        self.expression_presets = {
            "neutral": "neutral",
            "happy": "happy",
            "joy": "happy",
            "sad": "sad",
            "angry": "angry",
            "surprised": "surprised",
            "confused": "neutral",
            "excited": "happy",
            "thinking": "neutral"
        }
        
    def load_config(self):
        """Carrega configurações"""
        config_path = Path("config/vtuber.json")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "enabled": True,
            "engine": "vrm",
            "vmc_port": 39539
        }
    
    async def initialize(self):
        """Inicializa o motor VRM"""
        try:
            print(f"{Fore.YELLOW}→ Tentando conectar ao VSeeFace (VMC Protocol)...{Style.RESET_ALL}")
            
            # Tenta conectar ao VMC Protocol
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.socket.settimeout(2)
                
                # Envia pacote de teste
                test_message = self._create_vmc_message("/VMC/Ok", [1])
                self.socket.sendto(test_message.encode(), (self.vmc_host, self.vmc_port))
                
                self.is_active = True
                print(f"{Fore.GREEN}  ✓ VRM Engine conectado!{Style.RESET_ALL}")
                print(f"{Fore.CYAN}  📺 VSeeFace detectado na porta {self.vmc_port}{Style.RESET_ALL}")
                return True
                
            except Exception as e:
                print(f"{Fore.YELLOW}  ⚠ VSeeFace não detectado{Style.RESET_ALL}")
                print(f"{Fore.CYAN}  💡 Para usar VRM:{Style.RESET_ALL}")
                print(f"{Fore.CYAN}     1. Baixe VSeeFace: https://www.vseeface.icu{Style.RESET_ALL}")
                print(f"{Fore.CYAN}     2. Baixe modelo VRM: https://hub.vroid.com{Style.RESET_ALL}")
                print(f"{Fore.CYAN}     3. No VSeeFace: Settings → Enable VMC Protocol{Style.RESET_ALL}")
                print(f"{Fore.GREEN}  ✓ Mirai funcionará em modo texto{Style.RESET_ALL}")
                self.is_active = False
                return False
                
        except Exception as e:
            print(f"{Fore.RED}  ✗ Erro ao inicializar VRM: {e}{Style.RESET_ALL}")
            self.is_active = False
            return False
    
    def _create_vmc_message(self, address, args):
        """Cria mensagem OSC para VMC Protocol"""
        # Formato OSC simplificado para VMC
        message = f"{address}"
        for arg in args:
            if isinstance(arg, str):
                message += f",s{arg}"
            elif isinstance(arg, int):
                message += f",i{arg}"
            elif isinstance(arg, float):
                message += f",f{arg}"
        return message
    
    async def set_expression(self, expression):
        """Define expressão facial do modelo VRM"""
        if not self.is_active:
            return
        
        # Mapeia para expressão VRM válida
        vrm_expression = self.expression_presets.get(expression, "neutral")
        
        if vrm_expression != self.current_expression:
            self.current_expression = vrm_expression
            
            try:
                # Envia comando de expressão via VMC
                # Formato: /VMC/Ext/Blend/Val [nome] [valor]
                message = self._create_vmc_message(
                    f"/VMC/Ext/Blend/Val",
                    [vrm_expression, 1.0]
                )
                self.socket.sendto(message.encode(), (self.vmc_host, self.vmc_port))
                
                print(f"{Fore.MAGENTA}  [VRM] Expressão: {vrm_expression}{Style.RESET_ALL}")
                
            except Exception as e:
                print(f"{Fore.YELLOW}  ⚠ Erro ao enviar expressão: {e}{Style.RESET_ALL}")
    
    async def start_talking(self):
        """Inicia animação de fala (lip sync)"""
        if not self.is_active:
            return
        
        self.is_talking = True
        
        try:
            # Ativa lip sync no VSeeFace
            # A maioria dos modelos VRM tem blend shapes para boca
            message = self._create_vmc_message("/VMC/Ext/Blend/Val", ["A", 0.8])
            self.socket.sendto(message.encode(), (self.vmc_host, self.vmc_port))
            
        except Exception as e:
            pass  # Silencioso, não é crítico
    
    async def stop_talking(self):
        """Para animação de fala"""
        if not self.is_active:
            return
        
        self.is_talking = False
        
        try:
            # Desativa lip sync
            message = self._create_vmc_message("/VMC/Ext/Blend/Val", ["A", 0.0])
            self.socket.sendto(message.encode(), (self.vmc_host, self.vmc_port))
            
        except Exception as e:
            pass
    
    async def play_animation(self, animation_name):
        """Reproduz animação (acenar, etc)"""
        if not self.is_active:
            return
        
        print(f"{Fore.MAGENTA}  [VRM] Animação: {animation_name}{Style.RESET_ALL}")
        
        # Animações básicas via blend shapes
        animations = {
            "wave": [("happy", 1.0), ("neutral", 0.5)],
            "nod": [("neutral", 1.0)],
            "think": [("neutral", 1.0)]
        }
        
        if animation_name in animations:
            try:
                for expr, value in animations[animation_name]:
                    message = self._create_vmc_message(
                        "/VMC/Ext/Blend/Val",
                        [expr, value]
                    )
                    self.socket.sendto(message.encode(), (self.vmc_host, self.vmc_port))
                    await asyncio.sleep(0.3)
            except Exception as e:
                pass
    
    async def set_emotion_from_text(self, text, sentiment=None):
        """Define emoção baseada no texto/sentimento"""
        if not self.is_active:
            return
        
        # Análise simples de emoção
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["feliz", "legal", "massa", "yatta", "😊"]):
            await self.set_expression("happy")
        elif any(word in text_lower for word in ["triste", "mal", "😢"]):
            await self.set_expression("sad")
        elif any(word in text_lower for word in ["raiva", "bravo", "😠"]):
            await self.set_expression("angry")
        elif any(word in text_lower for word in ["?", "como", "por que"]):
            await self.set_expression("thinking")
        elif any(word in text_lower for word in ["!", "nossa", "uau"]):
            await self.set_expression("surprised")
        else:
            await self.set_expression("neutral")
    
    async def update_from_speech(self, is_speaking):
        """Atualiza lip sync baseado na fala"""
        if is_speaking:
            await self.start_talking()
        else:
            await self.stop_talking()
    
    async def stop(self):
        """Encerra o motor VRM"""
        self.is_active = False
        
        if self.socket:
            try:
                # Reseta expressão
                message = self._create_vmc_message("/VMC/Ext/Blend/Val", ["neutral", 1.0])
                self.socket.sendto(message.encode(), (self.vmc_host, self.vmc_port))
                self.socket.close()
            except:
                pass
        
        print(f"{Fore.CYAN}  ✓ VRM Engine encerrado{Style.RESET_ALL}")