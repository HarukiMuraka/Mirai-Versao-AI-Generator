from modes.base_mode import BaseMode
import pyautogui
import time
from PIL import Image, ImageDraw, ImageFont
from colorama import Fore, Style
import asyncio
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# OCR gratuito
try:
    import pytesseract
    OCR_AVAILABLE = True
except:
    OCR_AVAILABLE = False

class ObserverMode(BaseMode):
    """Modo observação com análise inteligente"""
    
    def __init__(self, mirai_instance):
        super().__init__(mirai_instance)
        self.observing = False
        self.screenshot_interval = 5
        
    async def enter(self):
        """Entra no modo observador"""
        self.is_active = True
        self.state.set_state("observer")
        self.print_mode_header("MODO OBSERVAÇÃO & ANÁLISE")
        
        if not OCR_AVAILABLE:
            print(f"{Fore.YELLOW}⚠️ pytesseract não instalado. Análise de texto limitada.{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Instale com: pip install pytesseract{Style.RESET_ALL}")
            print(f"{Fore.CYAN}E baixe Tesseract: https://github.com/UB-Mannheim/tesseract/wiki{Style.RESET_ALL}\n")
        
        await self.show_observer_menu()
    
    async def exit(self):
        """Sai do modo observador"""
        self.is_active = False
        self.observing = False
        print(f"\n{Fore.CYAN}Saindo do modo observação...{Style.RESET_ALL}")
    
    async def process_input(self, user_input):
        """Processa input"""
        return self.ai.generate_response(user_input, mode="observer")
    
    async def show_observer_menu(self):
        """Menu do observador"""
        while self.is_active:
            print(f"\n{Fore.YELLOW}O que deseja fazer?{Style.RESET_ALL}")
            print("1. 📸 Capturar e Analisar Tela COMPLETA")
            print("2. 🔍 Analisar e Pesquisar Conteúdo")
            print("3. 📊 Análise de Cores Dominantes")
            print("4. 📝 Extrair Texto da Tela (OCR)")
            print("5. 🎯 Detectar Objetos Visuais")
            print("0. ⬅️ Voltar")
            
            choice = input(f"\n{Fore.GREEN}Opção: {Style.RESET_ALL}")
            
            if choice == "1":
                await self.analyze_screen_complete()
            elif choice == "2":
                await self.analyze_and_search()
            elif choice == "3":
                await self.analyze_colors()
            elif choice == "4":
                await self.extract_text_ocr()
            elif choice == "5":
                await self.detect_objects()
            elif choice == "0":
                break
    
    async def analyze_screen_complete(self):
        """Análise COMPLETA da tela"""
        print(f"\n{Fore.CYAN}📸 Análise Completa da Tela{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Capturando em 3 segundos...{Style.RESET_ALL}\n")
        
        await asyncio.sleep(3)
        
        try:
            # Captura
            screenshot = pyautogui.screenshot()
            screenshot_path = "screenshot_analise.png"
            screenshot.save(screenshot_path)
            
            print(f"{Fore.GREEN}✓ Captura realizada!{Style.RESET_ALL}\n")
            
            # ANÁLISE BÁSICA
            width, height = screenshot.size
            pixels = width * height
            
            print(f"{Fore.CYAN}📐 INFORMAÇÕES BÁSICAS:{Style.RESET_ALL}")
            print(f"  Resolução: {width}x{height}")
            print(f"  Total de pixels: {pixels:,}")
            print(f"  Proporção: {width/height:.2f}:1")
            
            # ANÁLISE DE CORES
            print(f"\n{Fore.CYAN}🎨 ANÁLISE DE CORES:{Style.RESET_ALL}")
            colors = self._analyze_dominant_colors(screenshot)
            
            for i, (color, percentage) in enumerate(colors[:5], 1):
                r, g, b = color
                color_name = self._get_color_name(color)
                print(f"  {i}. {color_name}: RGB({r},{g},{b}) - {percentage:.1f}%")
            
            # ANÁLISE DE BRILHO
            brightness = self._analyze_brightness(screenshot)
            print(f"\n{Fore.CYAN}💡 BRILHO MÉDIO:{Style.RESET_ALL}")
            print(f"  {brightness:.1f}% - ", end='')
            
            if brightness < 30:
                print("Tela escura (modo noturno?)")
            elif brightness < 70:
                print("Brilho médio")
            else:
                print("Tela clara/brilhante")
            
            # TEXTO (se OCR disponível)
            if OCR_AVAILABLE:
                print(f"\n{Fore.CYAN}📝 TEXTO DETECTADO:{Style.RESET_ALL}")
                try:
                    text = pytesseract.image_to_string(screenshot, lang='por')
                    words = text.split()
                    
                    if len(words) > 0:
                        print(f"  Encontrei {len(words)} palavras!")
                        print(f"  Primeiras palavras: {' '.join(words[:10])}...")
                    else:
                        print("  Nenhum texto detectado")
                except:
                    print("  Erro ao extrair texto")
            
            # INTERPRETAÇÃO DA MIRAI
            print(f"\n{Fore.MAGENTA}🌸 INTERPRETAÇÃO DA MIRAI:{Style.RESET_ALL}")
            interpretation = self._interpret_screen(screenshot, colors, brightness)
            print(f"  {interpretation}")
            
            self.speaker.speak(interpretation)
            
            print(f"\n{Fore.GREEN}Análise salva em: {screenshot_path}{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erro: {e}{Style.RESET_ALL}")
        
        input(f"\n{Fore.CYAN}Pressione Enter para voltar...{Style.RESET_ALL}")
    
    async def analyze_and_search(self):
        """Analisa tela e pesquisa sobre o conteúdo"""
        print(f"\n{Fore.CYAN}🔍 Analisar e Pesquisar Conteúdo{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Capturando em 3 segundos...{Style.RESET_ALL}\n")
        
        await asyncio.sleep(3)
        
        try:
            screenshot = pyautogui.screenshot()
            
            # Tenta extrair texto
            if OCR_AVAILABLE:
                print(f"{Fore.CYAN}Extraindo texto...{Style.RESET_ALL}")
                text = pytesseract.image_to_string(screenshot, lang='por')
                words = text.split()
                
                if len(words) > 5:
                    # Pega palavras mais relevantes
                    important_words = [w for w in words if len(w) > 4][:5]
                    
                    if important_words:
                        print(f"{Fore.GREEN}Detectei: {', '.join(important_words)}{Style.RESET_ALL}\n")
                        
                        # Pergunta se quer pesquisar
                        search_query = ' '.join(important_words)
                        print(f"Quer que eu pesquise sobre: '{search_query}'? (s/n)")
                        
                        choice = input(f"{Fore.GREEN}> {Style.RESET_ALL}")
                        
                        if choice.lower() == 's':
                            from research.search_engine import SearchEngine
                            search = SearchEngine()
                            
                            print(f"\n{Fore.CYAN}Pesquisando...{Style.RESET_ALL}\n")
                            results = search.search(search_query, max_results=3)
                            
                            if results:
                                print(f"{Fore.GREEN}Encontrei:{Style.RESET_ALL}\n")
                                for i, result in enumerate(results, 1):
                                    print(f"{i}. {result['title']}")
                                    print(f"   {result['url']}\n")
                            
                            response = f"Pesquisei sobre o que vi na tela! Achei {len(results)} resultados!"
                            self.speaker.speak(response)
                        else:
                            print("Ok, sem pesquisa então!")
                    else:
                        print(f"{Fore.YELLOW}Não achei palavras relevantes pra pesquisar{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}Pouco texto na tela{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}OCR não disponível. Instale pytesseract!{Style.RESET_ALL}")
        
        except Exception as e:
            print(f"{Fore.RED}❌ Erro: {e}{Style.RESET_ALL}")
        
        input(f"\n{Fore.CYAN}Pressione Enter para voltar...{Style.RESET_ALL}")
    
    async def analyze_colors(self):
        """Análise detalhada de cores"""
        print(f"\n{Fore.CYAN}🎨 Análise de Cores Dominantes{Style.RESET_ALL}\n")
        
        await asyncio.sleep(2)
        
        try:
            screenshot = pyautogui.screenshot()
            
            colors = self._analyze_dominant_colors(screenshot, num_colors=10)
            
            print(f"{Fore.CYAN}Top 10 Cores Dominantes:{Style.RESET_ALL}\n")
            
            for i, (color, percentage) in enumerate(colors, 1):
                r, g, b = color
                color_name = self._get_color_name(color)
                
                # Barra visual
                bar_length = int(percentage / 2)  # Max 50 caracteres
                bar = '█' * bar_length
                
                print(f"{i:2d}. {color_name:15s} RGB({r:3d},{g:3d},{b:3d}) {bar} {percentage:.1f}%")
            
            response = f"A cor dominante na sua tela é {self._get_color_name(colors[0][0])}!"
            print(f"\n{Fore.MAGENTA}Mirai: {response}{Style.RESET_ALL}")
            self.speaker.speak(response)
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erro: {e}{Style.RESET_ALL}")
        
        input(f"\n{Fore.CYAN}Pressione Enter para voltar...{Style.RESET_ALL}")
    
    async def extract_text_ocr(self):
        """Extrai texto da tela"""
        if not OCR_AVAILABLE:
            print(f"{Fore.RED}pytesseract não está instalado!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Instale: pip install pytesseract{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}📝 Extração de Texto (OCR){Style.RESET_ALL}\n")
        
        await asyncio.sleep(2)
        
        try:
            screenshot = pyautogui.screenshot()
            
            print(f"{Fore.YELLOW}Processando OCR...{Style.RESET_ALL}\n")
            
            text = pytesseract.image_to_string(screenshot, lang='por')
            
            if text.strip():
                print(f"{Fore.GREEN}Texto encontrado:{Style.RESET_ALL}\n")
                print(f"{Fore.CYAN}{text}{Style.RESET_ALL}\n")
                
                # Salva em arquivo
                with open("texto_extraido.txt", 'w', encoding='utf-8') as f:
                    f.write(text)
                
                print(f"{Fore.GREEN}Texto salvo em: texto_extraido.txt{Style.RESET_ALL}")
                
                word_count = len(text.split())
                response = f"Extraí {word_count} palavras da tela!"
                self.speaker.speak(response)
            else:
                print(f"{Fore.YELLOW}Nenhum texto detectado{Style.RESET_ALL}")
        
        except Exception as e:
            print(f"{Fore.RED}❌ Erro: {e}{Style.RESET_ALL}")
        
        input(f"\n{Fore.CYAN}Pressione Enter para voltar...{Style.RESET_ALL}")
    
    async def detect_objects(self):
        """Detecta objetos visuais básicos"""
        print(f"\n{Fore.CYAN}🎯 Detecção de Elementos Visuais{Style.RESET_ALL}\n")
        
        await asyncio.sleep(2)
        
        try:
            screenshot = pyautogui.screenshot()
            
            print(f"{Fore.CYAN}Analisando elementos...{Style.RESET_ALL}\n")
            
            # Converte para escala de cinza
            gray = screenshot.convert('L')
            
            # Análise de contraste
            pixels = list(gray.getdata())
            avg_brightness = sum(pixels) / len(pixels)
            
            # Detecta áreas claras e escuras
            bright_pixels = sum(1 for p in pixels if p > 200)
            dark_pixels = sum(1 for p in pixels if p < 50)
            
            bright_percent = (bright_pixels / len(pixels)) * 100
            dark_percent = (dark_pixels / len(pixels)) * 100
            
            print(f"{Fore.YELLOW}Elementos detectados:{Style.RESET_ALL}")
            print(f"  Áreas claras: {bright_percent:.1f}%")
            print(f"  Áreas escuras: {dark_percent:.1f}%")
            print(f"  Contraste médio: {abs(bright_percent - dark_percent):.1f}%")
            
            # Interpreta
            if bright_percent > 70:
                print(f"\n  💡 Tela predominantemente CLARA")
                print(f"     Provavelmente: documentos, sites com fundo branco")
            elif dark_percent > 70:
                print(f"\n  🌙 Tela predominantemente ESCURA")
                print(f"     Provavelmente: modo escuro, vídeos, jogos")
            else:
                print(f"\n  ⚖️ Tela com EQUILÍBRIO de cores")
                print(f"     Provavelmente: interface mista, imagens variadas")
            
            response = "Analisei os elementos visuais da tela!"
            self.speaker.speak(response)
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erro: {e}{Style.RESET_ALL}")
        
        input(f"\n{Fore.CYAN}Pressione Enter para voltar...{Style.RESET_ALL}")
    
    # FUNÇÕES AUXILIARES
    
    def _analyze_dominant_colors(self, image, num_colors=5):
        """Analisa cores dominantes"""
        # Reduz imagem para análise mais rápida
        small_image = image.resize((150, 150))
        pixels = list(small_image.getdata())
        
        # Conta cores
        color_count = {}
        for pixel in pixels:
            # Agrupa cores similares
            r = (pixel[0] // 30) * 30
            g = (pixel[1] // 30) * 30
            b = (pixel[2] // 30) * 30
            color = (r, g, b)
            
            color_count[color] = color_count.get(color, 0) + 1
        
        # Ordena por frequência
        sorted_colors = sorted(color_count.items(), key=lambda x: x[1], reverse=True)
        
        # Calcula porcentagens
        total_pixels = len(pixels)
        result = []
        for color, count in sorted_colors[:num_colors]:
            percentage = (count / total_pixels) * 100
            result.append((color, percentage))
        
        return result
    
    def _analyze_brightness(self, image):
        """Calcula brilho médio"""
        gray = image.convert('L')
        pixels = list(gray.getdata())
        avg = sum(pixels) / len(pixels)
        return (avg / 255) * 100
    
    def _get_color_name(self, rgb):
        """Nomeia a cor"""
        r, g, b = rgb
        
        # Cores específicas
        if r > 200 and g < 100 and b < 100:
            return "Vermelho"
        elif r < 100 and g > 200 and b < 100:
            return "Verde"
        elif r < 100 and g < 100 and b > 200:
            return "Azul"
        elif r > 200 and g > 200 and b < 100:
            return "Amarelo"
        elif r > 200 and g < 100 and b > 200:
            return "Magenta"
        elif r < 100 and g > 200 and b > 200:
            return "Ciano"
        elif r > 200 and g > 150 and b < 100:
            return "Laranja"
        elif r < 50 and g < 50 and b < 50:
            return "Preto"
        elif r > 200 and g > 200 and b > 200:
            return "Branco"
        elif r > 150 and g > 150 and b > 150:
            return "Cinza Claro"
        elif r < 100 and g < 100 and b < 100:
            return "Cinza Escuro"
        else:
            return "Misto"
    
    def _interpret_screen(self, screenshot, colors, brightness):
        """Interpretação inteligente da tela"""
        dominant_color = self._get_color_name(colors[0][0])
        
        interpretations = []
        
        # Baseado em brilho
        if brightness < 30:
            interpretations.append("Tá com modo escuro ativado aí?")
        elif brightness > 80:
            interpretations.append("Tela bem clara!")
        
        # Baseado em cor
        if dominant_color in ["Preto", "Cinza Escuro"]:
            interpretations.append("Parece que tem muito preto na tela. Tá programando? Ou assistindo algo?")
        elif dominant_color in ["Branco", "Cinza Claro"]:
            interpretations.append("Bastante branco! Lendo algo? Documento talvez?")
        elif dominant_color in ["Azul"]:
            interpretations.append("Muito azul! Tá navegando na web?")
        elif dominant_color in ["Verde"]:
            interpretations.append("Verde predominante! Terminal? Código?")
        
        # Padrão
        if not interpretations:
            interpretations.append(f"Vi que a cor {dominant_color} domina sua tela!")
        
        return " ".join(interpretations) 