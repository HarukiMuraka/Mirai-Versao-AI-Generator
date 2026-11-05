import asyncio
import pyautogui
from PIL import Image, ImageDraw
from colorama import Fore, Style
from datetime import datetime
from pathlib import Path
import pytesseract
import cv2
import numpy as np

# Configurar Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class UnifiedMode:
    """Modo Unificado da Mirai - Todos os recursos em um só lugar"""
    
    def __init__(self, mirai_instance):
        self.mirai = mirai_instance
        self.ai = mirai_instance.ai
        self.context = mirai_instance.context
        self.state = mirai_instance.state
        self.vtuber = mirai_instance.vtuber
        self.speaker = mirai_instance.speaker
        self.is_active = False
        
        # Seleção de área
        self.selecting_area = False
        self.selected_area = None
        
        # Cache de análises
        self.last_screenshot = None
        self.last_analysis = None
    
    async def enter(self):
        """Entra no modo unificado"""
        self.is_active = True
        self.state.set_state("unified")
        
        print(f"\n{Fore.MAGENTA}╔════════════════════════════════════════╗")
        print(f"{Fore.MAGENTA}║    🌸 MIRAI - MODO UNIFICADO 🌸       ║")
        print(f"{Fore.MAGENTA}╚════════════════════════════════════════╝{Style.RESET_ALL}\n")
        
        print(f"{Fore.GREEN}Olá! Todos os meus recursos estão aqui agora! ✨{Style.RESET_ALL}\n")
        
        await self.show_main_menu()
    
    async def show_main_menu(self):
        """Menu principal unificado"""
        while self.is_active:
            print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}O que você gostaria de fazer?{Style.RESET_ALL}\n")
            
            print(f"{Fore.CYAN}💬 CONVERSA & INTERAÇÃO:{Style.RESET_ALL}")
            print("  1. Conversar por texto")
            print("  2. Conversar por voz")
            print("  3. Modo autônomo (eu tomo iniciativa!)")
            
            print(f"\n{Fore.CYAN}🔍 VISÃO & ANÁLISE:{Style.RESET_ALL}")
            print("  4. Analisar tela completa")
            print("  5. Selecionar e analisar área específica ⭐ NOVO")
            print("  6. Análise contínua (monitor em tempo real)")
            print("  7. Identificar objetos e texto")
            
            print(f"\n{Fore.CYAN}🎮 ENTRETENIMENTO:{Style.RESET_ALL}")
            print("  8. Modo Gamer (RetroArch + Citra)")
            print("  9. Modo Streamer")
            
            print(f"\n{Fore.CYAN}🤖 ASSISTENTE:{Style.RESET_ALL}")
            print("  10. Comandos e automação")
            print("  11. Pesquisa web")
            print("  12. Criar conteúdo")
            
            print(f"\n{Fore.CYAN}⚙️ SISTEMA:{Style.RESET_ALL}")
            print("  13. Configurações")
            print("  0. Sair")
            
            print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
            
            choice = input(f"\n{Fore.GREEN}Escolha (0-13): {Style.RESET_ALL}").strip()
            
            if choice == "1":
                await self.text_conversation()
            elif choice == "2":
                await self.voice_conversation()
            elif choice == "3":
                await self.autonomous_mode()
            elif choice == "4":
                await self.analyze_full_screen()
            elif choice == "5":
                await self.analyze_selected_area()
            elif choice == "6":
                await self.continuous_monitoring()
            elif choice == "7":
                await self.identify_objects_and_text()
            elif choice == "8":
                await self.gamer_mode()
            elif choice == "9":
                await self.streamer_mode()
            elif choice == "10":
                await self.assistant_mode()
            elif choice == "11":
                await self.web_search_mode()
            elif choice == "12":
                await self.content_creation_mode()
            elif choice == "13":
                await self.settings_menu()
            elif choice == "0":
                self.is_active = False
                break
    
    # ==========================================
    # VISÃO & ANÁLISE AVANÇADA
    # ==========================================
    
    async def analyze_selected_area(self):
        """Seleciona área específica e analisa - RECURSO NOVO!"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.MAGENTA}🎯 ANÁLISE DE ÁREA SELECIONADA")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}📋 Instruções:{Style.RESET_ALL}")
        print("1. A tela será capturada")
        print("2. Uma janela abrirá para você selecionar a área")
        print("3. Clique e arraste para selecionar")
        print("4. Pressione ENTER para confirmar ou ESC para cancelar\n")
        
        input(f"{Fore.GREEN}Pressione Enter para começar...{Style.RESET_ALL}")
        
        try:
            # Captura tela
            print(f"{Fore.CYAN}📸 Capturando tela...{Style.RESET_ALL}")
            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            
            # Seleção de área com OpenCV
            print(f"{Fore.YELLOW}🖱️ Selecione a área (clique e arraste)...{Style.RESET_ALL}\n")
            
            # Variáveis para seleção
            selecting = True
            start_point = None
            end_point = None
            current_img = screenshot_cv.copy()
            
            def select_area(event, x, y, flags, param):
                nonlocal start_point, end_point, current_img, selecting
                
                if event == cv2.EVENT_LBUTTONDOWN:
                    start_point = (x, y)
                    end_point = (x, y)
                
                elif event == cv2.EVENT_MOUSEMOVE and start_point:
                    end_point = (x, y)
                    current_img = screenshot_cv.copy()
                    cv2.rectangle(current_img, start_point, end_point, (0, 255, 0), 2)
                
                elif event == cv2.EVENT_LBUTTONUP:
                    end_point = (x, y)
                    selecting = False
            
            # Configurar janela
            window_name = 'Selecione a área - ENTER para confirmar | ESC para cancelar'
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.setMouseCallback(window_name, select_area)
            
            # Loop de seleção
            while True:
                cv2.imshow(window_name, current_img)
                key = cv2.waitKey(1) & 0xFF
                
                if key == 13:  # ENTER
                    break
                elif key == 27:  # ESC
                    cv2.destroyAllWindows()
                    print(f"{Fore.YELLOW}Cancelado!{Style.RESET_ALL}")
                    return
            
            cv2.destroyAllWindows()
            
            if start_point and end_point:
                # Extrai área selecionada
                x1, y1 = min(start_point[0], end_point[0]), min(start_point[1], end_point[1])
                x2, y2 = max(start_point[0], end_point[0]), max(start_point[1], end_point[1])
                
                # Converte de volta para PIL
                selected_region = screenshot.crop((x1, y1, x2, y2))
                
                # Salva
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"selected_area_{timestamp}.png"
                selected_region.save(filename)
                
                print(f"\n{Fore.GREEN}✓ Área selecionada: {x2-x1}x{y2-y1} pixels{Style.RESET_ALL}")
                print(f"{Fore.GREEN}✓ Salvo como: {filename}{Style.RESET_ALL}\n")
                
                # ANÁLISE COMPLETA DA ÁREA
                await self._analyze_image_region(selected_region, filename)
            else:
                print(f"{Fore.YELLOW}Nenhuma área selecionada!{Style.RESET_ALL}")
        
        except Exception as e:
            print(f"{Fore.RED}❌ Erro: {e}{Style.RESET_ALL}")
            import traceback
            traceback.print_exc()
        
        input(f"\n{Fore.CYAN}Pressione Enter para continuar...{Style.RESET_ALL}")
    
    async def _analyze_image_region(self, image, filename):
        """Análise COMPLETA de uma região de imagem"""
        print(f"{Fore.CYAN}🔍 Analisando imagem...{Style.RESET_ALL}\n")
        
        analysis_results = {}
        
        # 1. INFORMAÇÕES BÁSICAS
        width, height = image.size
        print(f"{Fore.CYAN}📐 DIMENSÕES:{Style.RESET_ALL}")
        print(f"  Tamanho: {width}x{height} pixels")
        print(f"  Área: {width * height:,} pixels")
        analysis_results['dimensions'] = f"{width}x{height}"
        
        # 2. ANÁLISE DE CORES
        print(f"\n{Fore.CYAN}🎨 CORES DOMINANTES:{Style.RESET_ALL}")
        colors = self._analyze_dominant_colors(image, num_colors=5)
        for i, (color, percentage) in enumerate(colors, 1):
            r, g, b = color
            color_name = self._get_color_name(color)
            print(f"  {i}. {color_name}: RGB({r},{g},{b}) - {percentage:.1f}%")
        analysis_results['dominant_color'] = self._get_color_name(colors[0][0])
        
        # 3. BRILHO
        brightness = self._analyze_brightness(image)
        brightness_desc = "Escura" if brightness < 30 else ("Média" if brightness < 70 else "Clara")
        print(f"\n{Fore.CYAN}💡 BRILHO:{Style.RESET_ALL}")
        print(f"  {brightness_desc} ({brightness:.1f}%)")
        analysis_results['brightness'] = brightness_desc
        
        # 4. EXTRAÇÃO DE TEXTO (OCR)
        print(f"\n{Fore.CYAN}📝 TEXTO DETECTADO:{Style.RESET_ALL}")
        try:
            text = pytesseract.image_to_string(image, lang='por+eng')
            
            if text.strip():
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                word_count = len(text.split())
                
                print(f"  Palavras: {word_count}")
                print(f"  Linhas: {len(lines)}")
                print(f"\n  Texto completo:")
                print(f"{Fore.WHITE}  {'-'*50}")
                for line in lines[:20]:  # Primeiras 20 linhas
                    print(f"  {line}")
                if len(lines) > 20:
                    print(f"  ... ({len(lines) - 20} linhas restantes)")
                print(f"  {'-'*50}{Style.RESET_ALL}")
                
                analysis_results['text'] = text
                analysis_results['has_text'] = True
            else:
                print(f"  {Fore.YELLOW}Nenhum texto detectado{Style.RESET_ALL}")
                analysis_results['has_text'] = False
                analysis_results['text'] = ""
        except Exception as e:
            print(f"  {Fore.RED}Erro no OCR: {e}{Style.RESET_ALL}")
            analysis_results['has_text'] = False
            analysis_results['text'] = ""
        
        # 5. DETECÇÃO DE BORDAS E FORMAS
        print(f"\n{Fore.CYAN}🔲 ANÁLISE DE FORMAS:{Style.RESET_ALL}")
        edges_detected = self._detect_edges(image)
        print(f"  Bordas detectadas: {edges_detected}")
        analysis_results['edges'] = edges_detected
        
        # 6. CONTEXTO INTELIGENTE
        print(f"\n{Fore.CYAN}🤖 IDENTIFICANDO CONTEXTO:{Style.RESET_ALL}")
        context = self._identify_context(analysis_results)
        for ctx in context:
            print(f"  • {ctx}")
        
        # 7. IA INTERPRETA A IMAGEM
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"🌸 INTERPRETAÇÃO DA MIRAI:")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        # Monta prompt para IA
        prompt = f"""Analise esta imagem que o usuário selecionou:

DADOS TÉCNICOS:
- Dimensões: {analysis_results['dimensions']}
- Cor dominante: {analysis_results['dominant_color']}
- Brilho: {analysis_results['brightness']}
- Contém texto: {'Sim' if analysis_results['has_text'] else 'Não'}

TEXTO ENCONTRADO:
{analysis_results['text'][:500] if analysis_results['has_text'] else 'Nenhum'}

CONTEXTO IDENTIFICADO:
{', '.join(context) if context else 'Uso geral'}

Dê sua interpretação DETALHADA sobre o que você vê nesta imagem. 
Seja específica, criativa e útil. Use sua personalidade!
Fale em português brasileiro, de forma natural."""
        
        interpretation = self.ai.generate_response(
            prompt,
            mode="unified"
        )
        
        print(f"{Fore.WHITE}{interpretation}{Style.RESET_ALL}\n")
        self.speaker.speak(interpretation)
        
        # Salvar análise em arquivo
        analysis_file = filename.replace('.png', '_analysis.txt')
        with open(analysis_file, 'w', encoding='utf-8') as f:
            f.write(f"ANÁLISE DE IMAGEM - MIRAI\n")
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Arquivo: {filename}\n")
            f.write(f"{'='*60}\n\n")
            f.write(f"DIMENSÕES: {analysis_results['dimensions']}\n")
            f.write(f"COR DOMINANTE: {analysis_results['dominant_color']}\n")
            f.write(f"BRILHO: {analysis_results['brightness']}\n")
            f.write(f"BORDAS: {edges_detected}\n\n")
            f.write(f"TEXTO EXTRAÍDO:\n{'-'*60}\n")
            f.write(f"{analysis_results['text']}\n")
            f.write(f"{'-'*60}\n\n")
            f.write(f"INTERPRETAÇÃO DA MIRAI:\n{'-'*60}\n")
            f.write(f"{interpretation}\n")
        
        print(f"{Fore.GREEN}✓ Análise completa salva em: {analysis_file}{Style.RESET_ALL}")
    
    async def analyze_full_screen(self):
        """Análise completa da tela"""
        print(f"\n{Fore.CYAN}📸 Capturando tela em 3 segundos...{Style.RESET_ALL}")
        await asyncio.sleep(3)
        
        screenshot = pyautogui.screenshot()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        screenshot.save(filename)
        
        await self._analyze_image_region(screenshot, filename)
        
        input(f"\n{Fore.CYAN}Pressione Enter para continuar...{Style.RESET_ALL}")
    
    async def continuous_monitoring(self):
        """Monitora tela continuamente"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.MAGENTA}👁️ MONITORAMENTO CONTÍNUO")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}Intervalo entre capturas (segundos): {Style.RESET_ALL}", end='')
        interval = input().strip()
        
        try:
            interval = int(interval)
        except:
            interval = 10
        
        print(f"\n{Fore.GREEN}✓ Monitoramento iniciado! (Ctrl+C para parar){Style.RESET_ALL}\n")
        self.speaker.speak("Monitoramento contínuo ativado!")
        
        try:
            while True:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"{Fore.CYAN}[{timestamp}] Capturando...{Style.RESET_ALL}", end='\r')
                
                screenshot = pyautogui.screenshot()
                
                # Análise rápida
                text = pytesseract.image_to_string(screenshot, lang='por')
                words = len(text.split())
                
                brightness = self._analyze_brightness(screenshot)
                
                print(f"{Fore.GREEN}[{timestamp}] Texto: {words} palavras | Brilho: {brightness:.0f}%{Style.RESET_ALL}")
                
                await asyncio.sleep(interval)
        
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Monitoramento encerrado!{Style.RESET_ALL}")
            self.speaker.speak("Monitoramento encerrado!")
    
    async def identify_objects_and_text(self):
        """Identifica objetos e extrai todo texto"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.MAGENTA}🔍 IDENTIFICAÇÃO COMPLETA")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}Capturando em 2 segundos...{Style.RESET_ALL}")
        await asyncio.sleep(2)
        
        screenshot = pyautogui.screenshot()
        
        # OCR Detalhado
        print(f"\n{Fore.CYAN}📝 EXTRAÇÃO DE TEXTO:{Style.RESET_ALL}")
        text_data = pytesseract.image_to_data(screenshot, lang='por+eng', output_type=pytesseract.Output.DICT)
        
        # Filtra palavras com confiança > 60%
        confident_words = []
        for i, word in enumerate(text_data['text']):
            if int(text_data['conf'][i]) > 60 and word.strip():
                confident_words.append({
                    'text': word,
                    'confidence': text_data['conf'][i],
                    'x': text_data['left'][i],
                    'y': text_data['top'][i]
                })
        
        print(f"  Total de palavras detectadas: {len(confident_words)}")
        
        if confident_words:
            print(f"\n  Palavras com alta confiança:")
            for word_data in confident_words[:30]:  # Primeiras 30
                print(f"    • '{word_data['text']}' (confiança: {word_data['confidence']}%)")
        
        # Análise de elementos visuais
        print(f"\n{Fore.CYAN}🎯 ELEMENTOS VISUAIS:{Style.RESET_ALL}")
        
        screenshot_np = np.array(screenshot)
        gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
        
        # Detecta bordas
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        print(f"  Contornos detectados: {len(contours)}")
        
        # Classifica contornos por área
        large_objects = sum(1 for c in contours if cv2.contourArea(c) > 1000)
        medium_objects = sum(1 for c in contours if 100 < cv2.contourArea(c) <= 1000)
        
        print(f"  Objetos grandes: {large_objects}")
        print(f"  Objetos médios: {medium_objects}")
        
        # IA interpreta tudo
        print(f"\n{Fore.MAGENTA}🌸 INTERPRETAÇÃO COMPLETA:{Style.RESET_ALL}\n")
        
        full_text = ' '.join([w['text'] for w in confident_words])
        
        prompt = f"""Análise completa da tela:

TEXTO DETECTADO ({len(confident_words)} palavras):
{full_text[:1000]}

ELEMENTOS VISUAIS:
- {len(contours)} contornos detectados
- {large_objects} objetos grandes
- {medium_objects} objetos médios

Com base nisso, me diga:
1. O que o usuário está fazendo?
2. Que tipo de aplicação/conteúdo está na tela?
3. Alguma observação interessante?

Seja detalhada e útil!"""
        
        interpretation = self.ai.generate_response(prompt, mode="unified")
        
        print(f"{Fore.WHITE}{interpretation}{Style.RESET_ALL}\n")
        self.speaker.speak(interpretation)
        
        input(f"\n{Fore.CYAN}Pressione Enter para continuar...{Style.RESET_ALL}")
    
    # ==========================================
    # FUNÇÕES AUXILIARES DE ANÁLISE
    # ==========================================
    
    def _analyze_dominant_colors(self, image, num_colors=5):
        """Analisa cores dominantes"""
        small_image = image.resize((150, 150))
        pixels = list(small_image.getdata())
        
        color_count = {}
        for pixel in pixels:
            r = (pixel[0] // 30) * 30
            g = (pixel[1] // 30) * 30
            b = (pixel[2] // 30) * 30
            color = (r, g, b)
            
            color_count[color] = color_count.get(color, 0) + 1
        
        sorted_colors = sorted(color_count.items(), key=lambda x: x[1], reverse=True)
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
        return (sum(pixels) / len(pixels) / 255) * 100
    
    def _get_color_name(self, rgb):
        """Nomeia cor RGB"""
        r, g, b = rgb
        
        if r > 200 and g > 200 and b > 200:
            return "Branco"
        elif r < 50 and g < 50 and b < 50:
            return "Preto"
        elif r > 200 and g < 100 and b < 100:
            return "Vermelho"
        elif r < 100 and g > 200 and b < 100:
            return "Verde"
        elif r < 100 and g < 100 and b > 200:
            return "Azul"
        elif r > 200 and g > 200 and b < 100:
            return "Amarelo"
        elif r > 200 and g > 100 and b < 100:
            return "Laranja"
        elif r > 100 and g > 100 and b > 100:
            return "Cinza"
        else:
            return "Misto"
    
    def _detect_edges(self, image):
        """Detecta quantidade de bordas"""
        img_np = np.array(image)
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_pixels = np.sum(edges > 0)
        total_pixels = edges.size
        edge_percentage = (edge_pixels / total_pixels) * 100
        
        if edge_percentage > 20:
            return "Muitas (imagem complexa)"
        elif edge_percentage > 5:
            return "Moderadas"
        else:
            return "Poucas (imagem simples)"
    
    def _identify_context(self, analysis):
        """Identifica contexto baseado na análise"""
        contexts = []
        
        text = analysis.get('text', '').lower()
        
        # Programação
        if any(word in text for word in ['def', 'class', 'import', 'function', 'python', 'java', 'código']):
            contexts.append("Código/Programação")
        
        # Web
        if any(word in text for word in ['http', 'www', 'chrome', 'firefox', 'navegador']):
            contexts.append("Navegação Web")
        
        # Documento
        if any(word in text for word in ['documento', 'parágrafo', 'título', 'texto']):
            contexts.append("Documento/Texto")
        
        # Jogo
        if any(word in text for word in ['score', 'level', 'game', 'play', 'player']):
            contexts.append("Jogo")
        
        # Vídeo
        if any(word in text for word in ['youtube', 'video', 'play', 'pause']):
            contexts.append("Vídeo/Mídia")
        
        # Terminal
        if any(word in text for word in ['$', '>', 'cmd', 'terminal', 'bash']):
            contexts.append("Terminal/Console")
        
        return contexts if contexts else ["Contexto geral"]
    
    # ==========================================
    # OUTROS MODOS (Implementação resumida)
    # ==========================================
    
    async def text_conversation(self):
        """Modo conversa por texto"""
        print(f"\n{Fore.GREEN}💬 Modo texto ativado!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}(Digite 'sair' para voltar){Style.RESET_ALL}\n")
        
        from mirai.perception.text_input import TextInput
        text_input = TextInput()
        
        while True:
            user_input = text_input.get_input(f"{Fore.CYAN}Você: {Style.RESET_ALL}")
            
            if not user_input or user_input.lower() in ['sair', 'exit']:
                break
            
            response = self.ai.generate_response(user_input, mode="unified")
            print(f"{Fore.MAGENTA}Mirai: {response}{Style.RESET_ALL}\n")
            self.speaker.speak(response)
    
    async def voice_conversation(self):
        """Modo conversa por voz"""
        print(f"\n{Fore.GREEN}🎤 Modo voz ativado!{Style.RESET_ALL}\n")
        
        from mirai.perception.voice_listener import VoiceListener
        voice = VoiceListener()
        
        if not voice.initialize():
            print(f"{Fore.RED}Erro ao inicializar microfone!{Style.RESET_ALL}")
            return
        
        print(f"{Fore.YELLOW}Diga 'sair' para voltar{Style.RESET_ALL}\n")
        
        while True:
            text = voice.listen_once()
            
            if not text:
                continue
            
            if text.lower() in ['sair', 'exit', 'parar']:
                break
            
            print(f"{Fore.CYAN}Você: {text}{Style.RESET_ALL}")
            
            response = self.ai.generate_response(text, mode="unified")
            print(f"{Fore.MAGENTA}Mirai: {response}{Style.RESET_ALL}\n")
            self.speaker.speak(response)
    
    async def autonomous_mode(self):
        """Modo autônomo melhorado"""
        print(f"\n{Fore.GREEN}🤖 Modo autônomo! Vou tomar iniciativa!{Style.RESET_ALL}\n")
        self.speaker.speak("Modo autônomo ativado! Vou conversar de verdade com você!")
        
        # Implementar igual ao conversation.py mas integrado aqui
        # ... (código do modo autônomo)
        pass
    
    async def gamer_mode(self):
        """Modo gamer com RetroArch + Citra"""
        from mirai.modes.gamer import GamerMode
        mode = GamerMode(self.mirai)
        await mode.enter()
    
    async def streamer_mode(self):
        """Modo streamer"""
        from mirai.modes.streamer import StreamerMode
        mode = StreamerMode(self.mirai)
        await mode.enter()
    
    async def assistant_mode(self):
        """Modo assistente"""
        from mirai.modes.assistant import AssistantMode
        mode = AssistantMode(self.mirai)
        await mode.enter()
    
    async def web_search_mode(self):
        """Pesquisa web"""
        print(f"\n{Fore.CYAN}🔍 Pesquisa Web{Style.RESET_ALL}\n")
        query = input(f"{Fore.GREEN}O que você quer pesquisar? {Style.RESET_ALL}")
        
        if query:
            from mirai.research.search_engine import SearchEngine
            search = SearchEngine()
            results = search.search(query, max_results=5)
            
            if results:
                print(f"\n{Fore.GREEN}Resultados:{Style.RESET_ALL}\n")
                for i, result in enumerate(results, 1):
                    print(f"{i}. {result['title']}")
                    print(f"   {result['snippet'][:100]}...")
                    print(f"   {result['url']}\n")
        
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    async def content_creation_mode(self):
        """Criação de conteúdo"""
        print(f"\n{Fore.CYAN}✏️ Criar Conteúdo{Style.RESET_ALL}\n")
        topic = input(f"{Fore.GREEN}Sobre o que? {Style.RESET_ALL}")
        
        if topic:
            response = self.ai.generate_response(
                f"Crie um texto interessante sobre: {topic}",
                mode="unified"
            )
            print(f"\n{Fore.MAGENTA}{response}{Style.RESET_ALL}\n")
        
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    async def settings_menu(self):
        """Menu de configurações"""
        print(f"\n{Fore.CYAN}⚙️ Configurações{Style.RESET_ALL}")
        print("(Menu de configurações)")
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    async def exit(self):
        """Sai do modo"""
        self.is_active = False