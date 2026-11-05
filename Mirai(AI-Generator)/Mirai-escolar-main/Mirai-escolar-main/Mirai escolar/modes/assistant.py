from modes.base_mode import BaseMode
from perception.text_input import TextInput
from actions.app_launcher import AppLauncher
from research.search_engine import SearchEngine
from research.background_search import BackgroundSearch
from colorama import Fore, Style
import asyncio
import pyautogui
from PIL import Image
import pytesseract
from datetime import datetime

# Configurar Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class AssistantMode(BaseMode):
    """Modo Assistente - Simples, Prático e com Análise de Tela"""
    
    def __init__(self, mirai_instance):
        super().__init__(mirai_instance)
        self.app_launcher = AppLauncher()
        self.search_engine = SearchEngine()
        self.background_search = BackgroundSearch()
        
        # Screenshot
        self.last_screenshot = None
        self.last_screenshot_analysis = None
    
    async def enter(self):
        """Entra no modo assistente"""
        self.is_active = True
        self.state.set_state("assistant")
        self.print_mode_header("MODO ASSISTENTE")
        
        print(f"{Fore.GREEN}Pronta para ajudar! Me diga o que precisa.{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}💡 Comandos rápidos:{Style.RESET_ALL}")
        print(f"  {Fore.CYAN}abrir [app]{Style.RESET_ALL}       - Ex: abrir chrome")
        print(f"  {Fore.CYAN}pesquisar [tema]{Style.RESET_ALL}  - Ex: pesquisar Python")
        print(f"  {Fore.CYAN}ver tela{Style.RESET_ALL}          - Captura e analisa sua tela")
        print(f"  {Fore.CYAN}opinar tela{Style.RESET_ALL}       - Mirai opina sobre sua tela")
        print(f"  {Fore.CYAN}criar texto{Style.RESET_ALL}       - Ex: criar texto sobre IA")
        print(f"  {Fore.CYAN}menu{Style.RESET_ALL}              - Ver menu completo")
        print(f"  {Fore.CYAN}sair{Style.RESET_ALL}              - Voltar\n")
        
        await self.run_assistant_loop()
    
    async def exit(self):
        """Sai do modo assistente"""
        self.is_active = False
        self.background_search.stop_all()
        print(f"\n{Fore.CYAN}Saindo do modo assistente...{Style.RESET_ALL}")
    
    async def process_input(self, user_input):
        """Processa comando - SIMPLIFICADO"""
        if not user_input or user_input.strip() == "":
            return None
        
        user_input_lower = user_input.lower().strip()
        
        # SAIR
        if user_input_lower in ['sair', 'exit', 'voltar']:
            return "EXIT"
        
        # MENU
        if user_input_lower == 'menu':
            self.show_menu()
            return None
        
        # ABRIR APP
        if user_input_lower.startswith('abrir '):
            app_name = user_input[6:].strip()
            return await self.open_application(app_name)
        
        # PESQUISAR
        if user_input_lower.startswith(('pesquisar ', 'buscar ', 'procurar ')):
            query = user_input_lower
            for cmd in ['pesquisar', 'buscar', 'procurar']:
                query = query.replace(cmd, '', 1).strip()
            
            return await self.search_web(query)
        
        # PESQUISA EM SEGUNDO PLANO
        if user_input_lower.startswith('pesquisa segundo plano '):
            query = user_input[23:].strip()
            return await self.background_search_start(query)
        
        # VER RESULTADOS DA PESQUISA EM SEGUNDO PLANO
        if user_input_lower == 'ver pesquisas':
            return self.show_background_results()
        
        # VER TELA (NOVO!)
        if user_input_lower in ['ver tela', 'analisar tela', 'screenshot', 'capturar tela']:
            return await self.analyze_screen()
        
        # OPINAR SOBRE TELA (NOVO!)
        if user_input_lower in ['opinar tela', 'o que acha', 'comenta tela']:
            return await self.opinion_on_screen()
        
        # CRIAR TEXTO
        if user_input_lower.startswith(('criar texto', 'escrever', 'texto sobre')):
            topic = user_input_lower
            for cmd in ['criar texto sobre', 'criar texto', 'escrever sobre', 'escrever', 'texto sobre']:
                topic = topic.replace(cmd, '', 1).strip()
            
            return await self.create_text(topic)
        
        # RESPOSTA GENÉRICA (Ollama responde)
        response = self.ai.generate_response(user_input, mode="assistant")
        return response
    
    def show_menu(self):
        """Mostra menu de opções"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.MAGENTA}📋 MENU DO ASSISTENTE")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}🖥️ APLICATIVOS:{Style.RESET_ALL}")
        print("  abrir chrome / firefox / edge / spotify / discord / obs / vscode")
        
        print(f"\n{Fore.YELLOW}🔍 PESQUISA:{Style.RESET_ALL}")
        print("  pesquisar [tema]              - Pesquisa imediata")
        print("  pesquisa segundo plano [tema] - Pesquisa em background")
        print("  ver pesquisas                 - Ver resultados das pesquisas")
        
        print(f"\n{Fore.YELLOW}📸 ANÁLISE DE TELA (NOVO!):{Style.RESET_ALL}")
        print("  ver tela                      - Captura e analisa sua tela")
        print("  opinar tela                   - Mirai opina sobre o que vê")
        
        print(f"\n{Fore.YELLOW}✏️ CRIAÇÃO:{Style.RESET_ALL}")
        print("  criar texto sobre [tema]")
        print("  escrever sobre [tema]")
        
        print(f"\n{Fore.YELLOW}💬 CONVERSA:{Style.RESET_ALL}")
        print("  Ou simplesmente converse comigo!\n")
    
    async def analyze_screen(self):
        """Captura e analisa a tela - COMPLETO"""
        print(f"\n{Fore.CYAN}📸 Capturando sua tela...{Style.RESET_ALL}")
        await asyncio.sleep(1)
        
        try:
            # Captura screenshot
            screenshot = pyautogui.screenshot()
            self.last_screenshot = screenshot
            
            # Salva
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"screenshot_{timestamp}.png"
            screenshot.save(screenshot_path)
            
            print(f"{Fore.GREEN}✓ Screenshot salvo: {screenshot_path}{Style.RESET_ALL}\n")
            
            # ANÁLISE BÁSICA
            width, height = screenshot.size
            print(f"{Fore.CYAN}📐 Resolução: {width}x{height}{Style.RESET_ALL}")
            
            # ANÁLISE DE CORES
            print(f"{Fore.CYAN}🎨 Analisando cores...{Style.RESET_ALL}")
            colors = self._analyze_colors(screenshot)
            dominant_color = self._get_color_name(colors[0][0])
            
            print(f"  Cor dominante: {dominant_color}")
            
            # BRILHO
            brightness = self._analyze_brightness(screenshot)
            brightness_desc = "Escura" if brightness < 30 else ("Média" if brightness < 70 else "Clara")
            print(f"  Brilho: {brightness_desc} ({brightness:.0f}%)")
            
            # OCR - LÊ TEXTO
            print(f"\n{Fore.CYAN}📝 Lendo texto da tela...{Style.RESET_ALL}")
            try:
                text = pytesseract.image_to_string(screenshot, lang='por')
                words = text.split()
                
                if len(words) > 0:
                    print(f"  Texto encontrado: {len(words)} palavras")
                    print(f"  Prévia: {' '.join(words[:15])}...")
                    text_preview = text[:300]
                else:
                    print(f"  Nenhum texto detectado")
                    text_preview = "Sem texto"
            except Exception as e:
                print(f"  Erro OCR: {e}")
                text_preview = "OCR não disponível"
            
            # MONTA ANÁLISE
            analysis = {
                'resolution': f"{width}x{height}",
                'dominant_color': dominant_color,
                'brightness': brightness_desc,
                'text_preview': text_preview,
                'colors': colors[:3]
            }
            
            self.last_screenshot_analysis = analysis
            
            # CONTEXTO PARA IA
            context = f"""Análise da tela do usuário:
- Resolução: {width}x{height}
- Cor dominante: {dominant_color}
- Brilho: {brightness_desc}
- Texto detectado: {text_preview}

Comente brevemente sobre o que vê na tela do usuário."""
            
            # IA COMENTA
            ai_comment = self.ai.generate_response(
                "O que você vê na minha tela?",
                mode="assistant"
            )
            
            print(f"\n{Fore.MAGENTA}🌸 Mirai: {ai_comment}{Style.RESET_ALL}\n")
            
            return ai_comment
            
        except Exception as e:
            error_msg = f"Ops! Tive problema ao capturar a tela: {e}"
            print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}")
            return error_msg
    
    async def opinion_on_screen(self):
        """Mirai dá opinião DETALHADA sobre a tela"""
        if not self.last_screenshot or not self.last_screenshot_analysis:
            return "Preciso ver sua tela primeiro! Digite 'ver tela' antes!"
        
        print(f"\n{Fore.CYAN}🤔 Analisando mais profundamente...{Style.RESET_ALL}")
        await asyncio.sleep(1)
        
        try:
            # Análise mais profunda
            screenshot = self.last_screenshot
            
            # OCR completo
            print(f"{Fore.CYAN}📖 Lendo todo o texto...{Style.RESET_ALL}")
            full_text = pytesseract.image_to_string(screenshot, lang='por')
            
            # Detecta contexto
            context_hints = []
            text_lower = full_text.lower()
            
            # Programação
            if any(word in text_lower for word in ['python', 'def', 'import', 'class', 'function', 'código']):
                context_hints.append("Código de programação (Python?)")
            
            # Web/YouTube
            if any(word in text_lower for word in ['youtube', 'play', 'video', 'subscribe']):
                context_hints.append("Assistindo vídeo/YouTube")
            
            # Jogos
            if any(word in text_lower for word in ['minecraft', 'game', 'play', 'level', 'score']):
                context_hints.append("Jogando")
            
            # Navegador
            if any(word in text_lower for word in ['chrome', 'firefox', 'http', 'https', 'www']):
                context_hints.append("Navegador web")
            
            # Documento
            if any(word in text_lower for word in ['documento', 'texto', 'parágrafo', 'título']):
                context_hints.append("Lendo/editando documento")
            
            # Terminal
            if any(word in text_lower for word in ['terminal', 'cmd', 'bash', 'shell', '$', '>']):
                context_hints.append("Terminal/Console")
            
            # Monta contexto completo
            analysis = self.last_screenshot_analysis
            full_context = f"""ANÁLISE COMPLETA DA TELA:

Dados técnicos:
- Resolução: {analysis['resolution']}
- Cor dominante: {analysis['dominant_color']}
- Brilho: {analysis['brightness']}

Texto detectado:
{full_text[:500]}

Contexto identificado:
{', '.join(context_hints) if context_hints else 'Uso geral'}

Dê sua opinião DETALHADA sobre o que o usuário está fazendo. Seja específica, 
faça observações interessantes e dê sugestões se relevante. Use sua personalidade!"""
            
            # IA opina (Ollama vai usar toda criatividade aqui)
            opinion = self.ai.generate_response(
                "Quero sua opinião detalhada sobre o que estou fazendo na tela!",
                mode="assistant"
            )
            
            print(f"\n{Fore.MAGENTA}🌸 Opinião da Mirai:{Style.RESET_ALL}")
            print(f"{Fore.WHITE}{opinion}{Style.RESET_ALL}\n")
            
            # Oferece pesquisa
            if context_hints:
                print(f"{Fore.YELLOW}💡 Quer que eu pesquise algo relacionado? (s/n){Style.RESET_ALL}")
                choice = input(f"{Fore.GREEN}> {Style.RESET_ALL}").strip().lower()
                
                if choice == 's':
                    # Pega primeiro contexto como query
                    query = context_hints[0] if context_hints else full_text[:50]
                    print(f"\n{Fore.CYAN}🔍 Pesquisando sobre '{query}'...{Style.RESET_ALL}\n")
                    await self.search_web(query)
            
            return opinion
            
        except Exception as e:
            error_msg = f"Não consegui analisar direito! Erro: {e}"
            print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}")
            return error_msg
    
    def _analyze_colors(self, image):
        """Analisa cores dominantes"""
        small = image.resize((100, 100))
        pixels = list(small.getdata())
        
        color_count = {}
        for pixel in pixels:
            r = (pixel[0] // 30) * 30
            g = (pixel[1] // 30) * 30
            b = (pixel[2] // 30) * 30
            color = (r, g, b)
            color_count[color] = color_count.get(color, 0) + 1
        
        sorted_colors = sorted(color_count.items(), key=lambda x: x[1], reverse=True)
        total = len(pixels)
        return [(color, (count/total)*100) for color, count in sorted_colors[:5]]
    
    def _analyze_brightness(self, image):
        """Calcula brilho médio"""
        gray = image.convert('L')
        pixels = list(gray.getdata())
        return (sum(pixels) / len(pixels) / 255) * 100
    
    def _get_color_name(self, rgb):
        """Nomeia cor"""
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
        else:
            return "Misto"
    
    async def open_application(self, app_name):
        """Abre aplicativo"""
        print(f"{Fore.CYAN}  🚀 Abrindo {app_name}...{Style.RESET_ALL}")
        
        if self.app_launcher.open_app(app_name):
            return f"Yatta! Abri o {app_name} pra você!"
        else:
            return f"Eita... Não achei o {app_name}. Tem certeza que tá instalado?"
    
    async def search_web(self, query):
        """Pesquisa na web - IMEDIATA"""
        if not query:
            return "Me diz o que você quer pesquisar!"
        
        print(f"{Fore.CYAN}  🔍 Pesquisando '{query}'...{Style.RESET_ALL}")
        
        results = self.search_engine.search(query, max_results=5)
        
        if not results:
            return "Hmm... Não achei nada sobre isso. Tenta reformular?"
        
        response = f"Achei algumas coisas sobre '{query}'!\n\n"
        for i, result in enumerate(results, 1):
            response += f"{i}. {result['title']}\n"
            response += f"   {result['snippet'][:100]}...\n"
            response += f"   🔗 {result['url']}\n\n"
        
        response += "Quer que eu abra algum desses?"
        return response
    
    async def background_search_start(self, query):
        """Inicia pesquisa em segundo plano"""
        if not query:
            return "Me diz o que pesquisar em segundo plano!"
        
        print(f"{Fore.YELLOW}  🔄 Iniciando pesquisa em segundo plano...{Style.RESET_ALL}")
        
        self.background_search.start_search(query, self.search_engine)
        
        return f"Beleza! Tô pesquisando sobre '{query}' em segundo plano. Digite 'ver pesquisas' para ver os resultados!"
    
    def show_background_results(self):
        """Mostra resultados de pesquisas em segundo plano"""
        results = self.background_search.get_results()
        
        if not results:
            return "Não tem nenhuma pesquisa rolando agora, ne~"
        
        response = "📊 Pesquisas em segundo plano:\n\n"
        
        for search in results:
            status = "✅ Completa" if search['completed'] else "⏳ Pesquisando..."
            response += f"• {search['query']} - {status}\n"
            
            if search['completed'] and search['results']:
                response += f"  Encontrei {len(search['results'])} resultados!\n"
                for i, result in enumerate(search['results'][:3], 1):
                    response += f"  {i}. {result['title']}\n"
            
            response += "\n"
        
        return response
    
    async def create_text(self, topic):
        """Cria texto"""
        if not topic:
            return "Me diz sobre o que você quer que eu escreva!"
        
        print(f"{Fore.CYAN}  ✏️ Criando texto sobre '{topic}'...{Style.RESET_ALL}")
        
        # Ollama gera o texto
        text = self.ai.generate_response(
            f"Escreva um texto curto (3-4 parágrafos) sobre: {topic}. Seja informativo mas mantenha tom casual.",
            mode="assistant"
        )
        
        return f"Sobre {topic}:\n\n{text}\n\nPronto! O que achou?"
    
    async def run_assistant_loop(self):
        """Loop principal do assistente"""
        text_input = TextInput()
        
        while self.is_active:
            user_input = text_input.get_input(f"{Fore.GREEN}> {Style.RESET_ALL}")
            
            if not user_input:
                continue
            
            result = await self.process_input(user_input)
            
            if result == "EXIT":
                break
            
            if result:
                print(f"\n{Fore.MAGENTA}Mirai: {result}{Style.RESET_ALL}\n")
                
                # Fala apenas primeiras 2 frases
                sentences = result.split('.')[:2]
                speech_text = '.'.join(sentences) + '.'
                if len(speech_text) < 200:
                    self.speaker.speak_async(speech_text)