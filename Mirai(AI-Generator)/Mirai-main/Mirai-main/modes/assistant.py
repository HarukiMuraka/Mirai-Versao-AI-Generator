from modes.base_mode import BaseMode
from actions.app_launcher import AppLauncher
import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style
import asyncio
import pyautogui
from PIL import Image
import pytesseract
from datetime import datetime
import json
from pathlib import Path
import re

class AssistantModeV2(BaseMode):
    """Modo Assistente Reimaginado - Inteligente e Proativo"""

    class _SimpleSearch:
        """
        Substitui SearchEngineV2 — busca no DuckDuckGo sem dependência externa.
        Interface compatível: .search(query, max_results=5)
        Retorna: [{"title": ..., "snippet": ..., "url": ..., "source": ...}]
        """
        def search(self, query: str, max_results: int = 5) -> list:
            try:
                r = requests.get(
                    "https://html.duckduckgo.com/html/",
                    params={"q": query},
                    headers={"User-Agent": "Mozilla/5.0"},
                    timeout=6,
                )
                if r.status_code != 200:
                    return []
                soup    = BeautifulSoup(r.content, "html.parser")
                results = []
                for div in soup.find_all("div", class_="result")[:max_results]:
                    t_tag = div.find("a", class_="result__a")
                    s_tag = div.find("a", class_="result__snippet")
                    u_tag = div.find("a", class_="result__url")
                    if t_tag and s_tag:
                        url  = t_tag.get("href", "")
                        src  = u_tag.get_text().strip() if u_tag else "DuckDuckGo"
                        results.append({
                            "title":   t_tag.get_text(),
                            "snippet": s_tag.get_text()[:300],
                            "url":     url,
                            "source":  src,
                        })
                return results
            except Exception:
                return []

    def __init__(self, mirai_instance):
        super().__init__(mirai_instance)
        self.app_launcher = AppLauncher()
        self.search_engine = self._SimpleSearch()
        
        # Contexto da sessão
        self.session_context = {
            'screenshots_analyzed': [],
            'searches_performed': [],
            'apps_opened': [],
            'last_screen_content': None,
            'user_focus_area': None
        }
        
        # Configurar Tesseract dinamicamente
        self._setup_tesseract()
        
        # Cache de análises
        self.analysis_cache = {}
        
    def _setup_tesseract(self):
        """Detecta e configura Tesseract automaticamente"""
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            '/usr/bin/tesseract',
            '/usr/local/bin/tesseract'
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                pytesseract.pytesseract.tesseract_cmd = path
                print(f"  ✓ Tesseract encontrado: {path}")
                return True
        
        print(f"  ⚠️  Tesseract não encontrado - OCR desabilitado")
        return False
    
    async def enter(self):
        """Entra no modo assistente"""
        self.is_active = True
        self.state.set_state("assistant")
        self.print_mode_header("MODO ASSISTENTE V2 - INTELIGENTE")
        
        # Saudação contextual
        greeting = self._generate_contextual_greeting()
        print(f"{Fore.GREEN}{greeting}{Style.RESET_ALL}\n")
        self.speaker.speak(greeting)
        
        # Mostra capacidades
        self._show_capabilities()
        
        await self.run_assistant_loop()
    
    def _generate_contextual_greeting(self) -> str:
        """Gera saudação baseada em contexto"""
        hour = datetime.now().hour
        
        if hour < 12:
            period = "Bom dia"
        elif hour < 18:
            period = "Boa tarde"
        else:
            period = "Boa noite"
        
        greetings = [
            f"{period}! Pronta para ajudar você hoje!",
            f"{period}! Vamos ser produtivos juntos!",
            f"{period}! Me diz no que posso ajudar!",
        ]
        
        import random
        return random.choice(greetings)
    
    def _show_capabilities(self):
        """Mostra capacidades do assistente"""
        print(f"{Fore.CYAN}{'='*60}")
        print(f"💡 O QUE EU POSSO FAZER:")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        capabilities = [
            ("🔍 Pesquisa Inteligente", "pesquisar [tema] - Busca e resume para você"),
            ("📸 Análise de Tela", "analisar tela - Vejo o que você está fazendo"),
            ("🤖 Assistência Contextual", "me ajuda com isso - Baseado na sua tela"),
            ("🚀 Abertura de Apps", "abrir [app] - Chrome, VS Code, etc"),
            ("📝 Criação de Conteúdo", "criar [tipo] sobre [tema]"),
            ("💬 Conversa Natural", "Só falar comigo normalmente!")
        ]
        
        for title, desc in capabilities:
            print(f"  {Fore.YELLOW}{title}{Style.RESET_ALL}")
            print(f"    {Fore.WHITE}{desc}{Style.RESET_ALL}\n")
        
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        print(f"{Fore.YELLOW}💡 Dica: Eu aprendo com o que você faz! Fique à vontade.{Style.RESET_ALL}\n")
    
    async def exit(self):
        """Sai do modo assistente"""
        self.is_active = False
        
        # Salva contexto da sessão
        self._save_session_context()
        
        # Despedida contextual
        farewell = self._generate_contextual_farewell()
        print(f"\n{Fore.CYAN}{farewell}{Style.RESET_ALL}")
        self.speaker.speak(farewell)
    
    def _generate_contextual_farewell(self) -> str:
        """Gera despedida baseada na sessão"""
        stats = {
            'screenshots': len(self.session_context['screenshots_analyzed']),
            'searches': len(self.session_context['searches_performed']),
            'apps': len(self.session_context['apps_opened'])
        }
        
        if stats['screenshots'] > 0 or stats['searches'] > 0:
            return f"Foi produtivo! Analisei {stats['screenshots']} telas e fiz {stats['searches']} pesquisas. Até logo!"
        else:
            return "Até logo! Sempre que precisar, me chama!"
    
    def _save_session_context(self):
        """Salva contexto da sessão para aprendizado"""
        session_file = Path("memory/assistant_sessions.json")
        session_file.parent.mkdir(exist_ok=True)
        
        try:
            # Carrega sessões anteriores
            if session_file.exists():
                with open(session_file, 'r', encoding='utf-8') as f:
                    sessions = json.load(f)
            else:
                sessions = []
            
            # Adiciona sessão atual
            sessions.append({
                'timestamp': datetime.now().isoformat(),
                'duration': (datetime.now() - self.context.session_start).seconds,
                'stats': {
                    'screenshots': len(self.session_context['screenshots_analyzed']),
                    'searches': len(self.session_context['searches_performed']),
                    'apps': len(self.session_context['apps_opened'])
                },
                'topics': list(set([s['query'] for s in self.session_context['searches_performed']]))
            })
            
            # Mantém apenas últimas 50 sessões
            sessions = sessions[-50:]
            
            # Salva
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(sessions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"  ⚠️  Erro ao salvar sessão: {e}")
    
    async def run_assistant_loop(self):
        """Loop principal do assistente"""
        while self.is_active:
            user_input = input(f"{Fore.GREEN}💬 Você: {Style.RESET_ALL}")
            
            if not user_input:
                continue
            
            # Comandos de saída
            if user_input.lower() in ['sair', 'exit', 'voltar', 'tchau']:
                break
            
            # Processa com contexto
            print(f"{Fore.CYAN}💭 Pensando...{Style.RESET_ALL}", end='\r')
            
            result = await self.process_input_intelligent(user_input)
            
            print(" " * 50, end='\r')
            
            if result:
                print(f"\n{Fore.MAGENTA}🌸 Mirai: {result}{Style.RESET_ALL}\n")
                
                # Fala resumo
                summary = self._create_speech_summary(result)
                await asyncio.to_thread(self.speaker.speak, summary)
    
    async def process_input_intelligent(self, user_input: str):
        """Processa input com inteligência contextual"""
        user_input_lower = user_input.lower().strip()
        
        # Classifica intenção
        intent = self._classify_intent(user_input_lower)
        
        print(f"  [DEBUG] Intent detectado: {intent}")
        
        # Roteamento inteligente
        if intent == 'search':
            return await self._handle_search_intent(user_input)
        
        elif intent == 'screen_analysis':
            return await self._handle_screen_analysis_intent(user_input)
        
        elif intent == 'app_control':
            return await self._handle_app_control_intent(user_input)
        
        elif intent == 'help_with_current':
            return await self._handle_contextual_help_intent(user_input)
        
        elif intent == 'create_content':
            return await self._handle_content_creation_intent(user_input)
        
        else:  # conversation
            return await self._handle_conversation_intent(user_input)
    
    def _classify_intent(self, text: str) -> str:
        """Classifica intenção do usuário"""
        # Pesquisa
        if any(word in text for word in ['pesquisar', 'pesquisa', 'buscar', 'procurar', 'me fala sobre', 'o que é']):
            return 'search'
        
        # Análise de tela
        if any(word in text for word in ['analisar tela', 'ver tela', 'o que tem na tela', 'capturar', 'screenshot']):
            return 'screen_analysis'
        
        # Controle de apps
        if any(word in text for word in ['abrir', 'abre', 'fechar', 'fecha', 'iniciar']):
            return 'app_control'
        
        # Ajuda contextual
        if any(word in text for word in ['me ajuda', 'como faço', 'preciso fazer', 'help']):
            return 'help_with_current'
        
        # Criação de conteúdo
        if any(word in text for word in ['criar', 'escrever', 'gerar', 'fazer um']):
            return 'create_content'
        
        # Conversa padrão
        return 'conversation'
    
    async def _handle_search_intent(self, query: str):
        """Pesquisa INTELIGENTE com resumo"""
        # Extrai query limpa
        clean_query = self._extract_search_query(query)
        
        if not clean_query:
            return "Não entendi o que você quer pesquisar. Pode reformular?"
        
        print(f"\n{Fore.CYAN}🔍 Pesquisando: '{clean_query}'{Style.RESET_ALL}\n")
        
        # Pesquisa
        results = self.search_engine.search(clean_query, max_results=5)
        
        if not results:
            return f"Hmm, não achei nada confiável sobre '{clean_query}'. Quer que eu tente outra fonte?"
        
        # Registra pesquisa
        self.session_context['searches_performed'].append({
            'query': clean_query,
            'timestamp': datetime.now().isoformat(),
            'results_count': len(results)
        })
        
        # Monta resumo INTELIGENTE com IA
        search_summary = await self._create_ai_search_summary(clean_query, results)
        
        # Mostra resultados detalhados
        print(f"{Fore.YELLOW}📚 Resultados encontrados:{Style.RESET_ALL}\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {Fore.CYAN}{result['title']}{Style.RESET_ALL}")
            print(f"   {result['snippet'][:150]}...")
            print(f"   🔗 {result['url']}")
            print(f"   📍 Fonte: {result['source']}\n")
        
        return search_summary
    
    def _extract_search_query(self, text: str) -> str:
        """Extrai query de pesquisa do texto"""
        text_lower = text.lower()
        
        # Remove palavras de ação
        for word in ['pesquisar', 'pesquisa', 'buscar', 'procurar', 'me fala sobre', 'sobre', 'o que é']:
            text_lower = text_lower.replace(word, '')
        
        return text_lower.strip()
    
    async def _create_ai_search_summary(self, query: str, results: list) -> str:
        """Cria resumo inteligente dos resultados com IA"""
        # Monta contexto para IA
        context = f"Pesquisei sobre '{query}' e encontrei:\n\n"
        
        for i, result in enumerate(results[:3], 1):
            context += f"{i}. {result['title']}\n"
            context += f"   {result['snippet'][:200]}\n\n"
        
        prompt = f"""Baseado nestes resultados de pesquisa, me dê um resumo breve (2-3 frases) sobre '{query}':

{context}

Resumo natural e informativo:"""
        
        # Usa IA para resumir
        if self.ai.use_gemini or self.ai.use_ollama:
            summary = await self.ai.generate_response(prompt, mode="assistant")
        else:
            # Fallback: primeiro snippet
            summary = f"Sobre {query}: {results[0]['snippet'][:200]}"
        
        summary += f"\n\n💡 Encontrei {len(results)} fontes. Quer que eu aprofunde em alguma?"
        
        return summary
    
    async def _handle_screen_analysis_intent(self, query: str):
        """Análise PROFUNDA de tela com IA"""
        print(f"\n{Fore.CYAN}📸 Capturando e analisando sua tela...{Style.RESET_ALL}\n")
        
        await asyncio.sleep(1)  # Dá tempo para usuário ver
        
        try:
            # Captura
            screenshot = pyautogui.screenshot()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"memory/screenshots/screenshot_{timestamp}.png"
            
            # Cria diretório
            Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)
            screenshot.save(screenshot_path)
            
            # Análise COMPLETA
            analysis = await self._deep_screen_analysis(screenshot)
            
            # Registra
            self.session_context['screenshots_analyzed'].append({
                'timestamp': datetime.now().isoformat(),
                'path': screenshot_path,
                'analysis': analysis
            })
            self.session_context['last_screen_content'] = analysis
            
            # Monta resposta com IA
            response = await self._create_ai_screen_response(analysis, query)
            
            return response
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erro: {e}{Style.RESET_ALL}")
            import traceback
            traceback.print_exc()
            return f"Ops! Tive um problema ao capturar a tela: {e}"
    
    async def _deep_screen_analysis(self, screenshot: Image) -> dict:
        """Análise PROFUNDA da tela"""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'resolution': f"{screenshot.width}x{screenshot.height}",
            'text_content': None,
            'dominant_colors': [],
            'brightness': 0,
            'detected_contexts': [],
            'ui_elements': []
        }
        
        # 1. OCR - Texto
        try:
            text = pytesseract.image_to_string(screenshot, lang='por+eng')
            analysis['text_content'] = text
            
            # Detecta contextos do texto
            analysis['detected_contexts'] = self._detect_contexts_from_text(text)
        except Exception as e:
            print(f"  ⚠️  OCR falhou: {e}")
            analysis['text_content'] = ""
        
        # 2. Análise de cores
        analysis['dominant_colors'] = self._analyze_colors_advanced(screenshot)
        analysis['brightness'] = self._calculate_brightness(screenshot)
        
        # 3. Detecção de UI
        analysis['ui_elements'] = self._detect_ui_elements(screenshot)
        
        return analysis
    
    def _detect_contexts_from_text(self, text: str) -> list:
        """Detecta contextos do texto OCR"""
        contexts = []
        text_lower = text.lower()
        
        # Programação
        code_keywords = ['def ', 'class ', 'import ', 'function', 'var ', 'const ', 'let ', 'python', 'javascript']
        if any(kw in text_lower for kw in code_keywords):
            contexts.append({
                'type': 'programming',
                'confidence': 'high',
                'details': 'Código de programação detectado'
            })
        
        # Navegação web
        web_keywords = ['http', 'www', 'chrome', 'firefox', '.com', '.br', 'google']
        if any(kw in text_lower for kw in web_keywords):
            contexts.append({
                'type': 'web_browsing',
                'confidence': 'high',
                'details': 'Navegação web'
            })
        
        # Vídeo/streaming
        video_keywords = ['play', 'pause', 'youtube', 'video', 'netflix', 'twitch']
        if any(kw in text_lower for kw in video_keywords):
            contexts.append({
                'type': 'video',
                'confidence': 'medium',
                'details': 'Assistindo vídeo/streaming'
            })
        
        # Documentos
        doc_keywords = ['parágrafo', 'título', 'documento', 'word', 'page']
        if any(kw in text_lower for kw in doc_keywords):
            contexts.append({
                'type': 'document',
                'confidence': 'medium',
                'details': 'Editando/lendo documento'
            })
        
        # Games
        game_keywords = ['minecraft', 'game', 'level', 'score', 'health', 'mana']
        if any(kw in text_lower for kw in game_keywords):
            contexts.append({
                'type': 'gaming',
                'confidence': 'high',
                'details': 'Jogando'
            })
        
        return contexts
    
    def _analyze_colors_advanced(self, image: Image) -> list:
        """Análise avançada de cores"""
        # Reduz imagem
        small = image.resize((100, 100))
        pixels = list(small.getdata())
        
        # Agrupa cores
        color_count = {}
        for pixel in pixels:
            # Agrupa em buckets de 30
            r = (pixel[0] // 30) * 30
            g = (pixel[1] // 30) * 30
            b = (pixel[2] // 30) * 30
            color = (r, g, b)
            color_count[color] = color_count.get(color, 0) + 1
        
        # Top 5 cores
        sorted_colors = sorted(color_count.items(), key=lambda x: x[1], reverse=True)
        total_pixels = len(pixels)
        
        result = []
        for color, count in sorted_colors[:5]:
            percentage = (count / total_pixels) * 100
            result.append({
                'rgb': color,
                'name': self._get_color_name(color),
                'percentage': percentage
            })
        
        return result
    
    def _calculate_brightness(self, image: Image) -> float:
        """Calcula brilho médio"""
        gray = image.convert('L')
        pixels = list(gray.getdata())
        return (sum(pixels) / len(pixels) / 255) * 100
    
    def _detect_ui_elements(self, screenshot: Image) -> list:
        """Detecta elementos de UI (simplificado)"""
        elements = []
        
        # Baseado em brilho e contraste
        brightness = self._calculate_brightness(screenshot)
        
        if brightness < 30:
            elements.append('dark_mode')
        elif brightness > 70:
            elements.append('light_mode')
        
        # Tamanho da tela sugere tipo de uso
        if screenshot.width >= 1920:
            elements.append('multi_monitor_or_large_display')
        
        return elements
    
    def _get_color_name(self, rgb: tuple) -> str:
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
        elif r > 150 and g > 150 and b > 150:
            return "Cinza Claro"
        else:
            return "Misto"
    
    async def _create_ai_screen_response(self, analysis: dict, original_query: str) -> str:
        """Cria resposta inteligente sobre a tela com IA"""
        # Monta contexto
        context = f"""Análise da tela do usuário:

TÉCNICO:
- Resolução: {analysis['resolution']}
- Cor dominante: {analysis['dominant_colors'][0]['name'] if analysis['dominant_colors'] else 'N/A'}
- Brilho: {analysis['brightness']:.0f}%
- Modo: {' '.join(analysis['ui_elements'])}

CONTEXTO DETECTADO:
{chr(10).join([f"- {c['type']}: {c['details']}" for c in analysis['detected_contexts']])}

TEXTO DETECTADO (amostra):
{analysis['text_content'][:300] if analysis['text_content'] else 'Nenhum texto detectado'}

Pergunta do usuário: {original_query}

Responda de forma útil e contextual sobre o que o usuário está fazendo:"""
        
        # Usa IA
        if self.ai.use_gemini or self.ai.use_ollama:
            response = await self.ai.generate_response(context, mode="assistant")
        else:
            # Fallback
            if analysis['detected_contexts']:
                main_context = analysis['detected_contexts'][0]
                response = f"Parece que você está {main_context['details']}! "
            else:
                response = "Analisei sua tela. "
            
            response += f"Cor dominante: {analysis['dominant_colors'][0]['name']}. "
            
            if analysis['text_content']:
                words = len(analysis['text_content'].split())
                response += f"Detectei {words} palavras de texto."
        
        return response
    
    async def _handle_app_control_intent(self, text: str):
        """Controle de aplicativos"""
        # Detecta app
        app_name = self._extract_app_name(text)
        
        if not app_name:
            return "Não entendi qual aplicativo você quer abrir. Pode especificar?"
        
        print(f"{Fore.CYAN}🚀 Abrindo {app_name}...{Style.RESET_ALL}")
        
        success = self.app_launcher.open_app(app_name)
        
        if success:
            self.session_context['apps_opened'].append({
                'app': app_name,
                'timestamp': datetime.now().isoformat()
            })
            return f"Pronto! Abri o {app_name} para você!"
        else:
            return f"Não consegui abrir {app_name}. Tem certeza que está instalado?"
    
    def _extract_app_name(self, text: str) -> str:
        """Extrai nome do app do texto"""
        text_lower = text.lower()
        
        # Remove palavras de ação
        for word in ['abrir', 'abre', 'abra', 'iniciar', 'inicia']:
            text_lower = text_lower.replace(word, '')
        
        app_name = text_lower.strip()
        
        # Mapeia variações comuns
        app_map = {
            'google chrome': 'chrome',
            'vs code': 'vscode',
            'visual studio code': 'vscode',
            'bloco de notas': 'notepad',
            'explorador de arquivos': 'explorer'
        }
        
        return app_map.get(app_name, app_name)
    
    async def _handle_contextual_help_intent(self, query: str):
        """Ajuda baseada no contexto atual da tela"""
        # Verifica se tem análise de tela recente
        if not self.session_context.get('last_screen_content'):
            return "Para eu te ajudar melhor, deixa eu ver sua tela primeiro! Diga 'analisar tela'."
        
        last_analysis = self.session_context['last_screen_content']
        
        # Monta contexto para IA
        help_context = f"""O usuário está pedindo ajuda: "{query}"

Contexto da tela atual:
{json.dumps(last_analysis, indent=2, ensure_ascii=False)}

Forneça ajuda específica e prática baseada no que ele está fazendo:"""
        
        # IA responde
        response = await self.ai.generate_response(help_context, mode="assistant")
        
        return response
    
    async def _handle_content_creation_intent(self, query: str):
        """Criação de conteúdo"""
        # Extrai tipo e tema
        content_type, topic = self._parse_content_request(query)
        
        if not topic:
            return "Sobre o que você quer que eu crie?"
        
        print(f"{Fore.CYAN}✍️  Criando {content_type} sobre '{topic}'...{Style.RESET_ALL}\n")
        
        # Prompt para criação
        create_prompt = f"Crie um {content_type} sobre: {topic}. Seja criativo e útil!"
        
        content = await self.ai.generate_response(create_prompt, mode="assistant")
        
        # Salva em arquivo
        filename = self._save_created_content(content_type, topic, content)
        
        return f"Pronto! Criei um {content_type} sobre {topic}.\n\n{content}\n\n💾 Salvo em: {filename}"
    
    def _parse_content_request(self, text: str):
        """Extrai tipo e tema de requisição de conteúdo"""
        text_lower = text.lower()
        
        # Tipos
        if 'resumo' in text_lower:
            content_type = 'resumo'
        elif 'lista' in text_lower:
            content_type = 'lista'
        elif 'roteiro' in text_lower:
            content_type = 'roteiro'
        elif 'email' in text_lower or 'e-mail' in text_lower:
            content_type = 'email'
        else:
            content_type = 'texto'
        
        # Remove palavras de ação
        for word in ['criar', 'escrever', 'fazer', 'gerar', 'sobre', content_type]:
            text_lower = text_lower.replace(word, '')
        
        topic = text_lower.strip()
        
        return content_type, topic
    
    def _save_created_content(self, content_type: str, topic: str, content: str) -> str:
        """Salva conteúdo criado"""
        # Cria filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = re.sub(r'[^\w\s-]', '', topic).strip().replace(' ', '_')
        filename = f"memory/created_content/{content_type}_{safe_topic}_{timestamp}.txt"
        
        # Cria diretório
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        # Salva
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# {content_type.upper()}: {topic}\n")
            f.write(f"Criado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
            f.write(content)
        
        return filename
    
    async def _handle_conversation_intent(self, text: str):
        """Conversa casual"""
        # Adiciona contexto da sessão se relevante
        enhanced_text = text
        
        if self.session_context['last_screen_content']:
            enhanced_text = f"[Contexto: usuário estava {self.session_context['last_screen_content'].get('detected_contexts', [{}])[0].get('details', 'usando computador') if self.session_context['last_screen_content'].get('detected_contexts') else 'usando computador'}]\n\n{text}"
        
        response = await self.ai.generate_response(enhanced_text, mode="assistant", enable_search=False)
        
        return response
    
    def _create_speech_summary(self, text: str, max_sentences: int = 2) -> str:
        """Cria resumo para fala"""
        # Pega primeiras N sentenças
        sentences = text.split('.')[:max_sentences]
        summary = '.'.join(sentences) + '.'
        
        # Limita tamanho
        if len(summary) > 200:
            summary = summary[:197] + "..."
        
        return summary
    
    async def process_input(self, user_input):
        """Método herdado - mantido para compatibilidade"""
        return await self.process_input_intelligent(user_input)

# Alias para compatibilidade com menu.py
AssistantModePro = AssistantModeV2