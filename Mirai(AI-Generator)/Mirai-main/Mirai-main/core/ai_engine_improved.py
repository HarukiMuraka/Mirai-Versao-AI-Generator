import random
import json
import requests
from pathlib import Path
import re
from bs4 import BeautifulSoup
from datetime import datetime
import time

class ImprovedMiraiAI:
    """Motor de IA Melhorado da Mirai - Compreensão Avançada"""
    
    def __init__(self, context_manager):
        self.context = context_manager
        self.config = self.load_config()
        
        # Gemini API
        self.use_gemini = True
        self.gemini_api_key = self._load_gemini_key()
        self.gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        
        # Ollama
        self.use_ollama = False
        self.ollama_model = "llama3"
        self.ollama_url = "http://localhost:11434/api/generate"
        
        # Memória e contexto
        self.permanent_memory = self.load_permanent_memory()
        self.conversation_history = []
        self.conversation_topics = []  # NOVO: Track de tópicos
        self.user_preferences = {}     # NOVO: Preferências do usuário
        
        # Compreensão avançada
        self.intent_patterns = self._init_intent_patterns()
        self.entity_extractor = EntityExtractor()
        
        # Iniciativa
        self.last_user_message_time = time.time()
        self.silence_threshold = random.uniform(15, 30)
        
        self._init_responses()
    
    def _init_intent_patterns(self):
        """Padrões para identificar intenções"""
        return {
            'question': {
                'patterns': [r'\?$', r'^(o que|quem|quando|onde|como|por que|qual)'],
                'keywords': ['?', 'o que', 'quem', 'quando', 'onde', 'como', 'por que', 'qual']
            },
            'command': {
                'patterns': [r'^(abrir|fechar|iniciar|parar|executar)', r'^(faça|crie|mostre|busque)'],
                'keywords': ['abrir', 'fechar', 'iniciar', 'parar', 'executar', 'faça', 'crie', 'mostre', 'busque']
            },
            'request_info': {
                'patterns': [r'(me (fala|conta|diz)|quero saber|pesquisa sobre)'],
                'keywords': ['me fala', 'me conta', 'me diz', 'quero saber', 'pesquisa sobre', 'procura sobre']
            },
            'opinion': {
                'patterns': [r'(o que (acha|pensa)|sua opinião|você gosta)'],
                'keywords': ['o que acha', 'o que pensa', 'sua opinião', 'você gosta', 'prefere']
            },
            'greeting': {
                'patterns': [r'^(oi|olá|hey|opa|e aí)'],
                'keywords': ['oi', 'olá', 'hey', 'opa', 'e aí', 'eai']
            },
            'farewell': {
                'patterns': [r'^(tchau|até|falou|bye|adeus)'],
                'keywords': ['tchau', 'até', 'falou', 'bye', 'adeus']
            }
        }
    
    def _load_gemini_key(self):
        """Carrega chave Gemini"""
        config_path = Path("config/gemini_key.txt")
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    content = f.read().strip()
                    for line in content.split('\n'):
                        line = line.strip()
                        if line and not line.startswith('#'):
                            return line
            except:
                pass
        
        return None
    
    def load_permanent_memory(self):
        """Carrega memória"""
        memory_path = Path("memory/permanent_memory.json")
        
        if memory_path.exists():
            try:
                with open(memory_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self._create_default_memory()
        else:
            memory = self._create_default_memory()
            self.save_permanent_memory(memory)
            return memory
    
    def _create_default_memory(self):
        return {
            "personalidade": {
                "sem_emojis": True,
                "usa_girias": True
            },
            "usuario": {
                "apelidos": ["pastel de frango", "xinguiling"],
                "notas": [],
                "preferencias": {},
                "topicos_interesse": []
            },
            "girias": ["mano", "cara", "véi", "dahora", "massa", "top"],
            "palavras_japonesas": ["yatta", "sugoi", "ne", "daijōbu"]
        }
    
    def save_permanent_memory(self, memory=None):
        if memory is None:
            memory = self.permanent_memory
        
        memory_path = Path("memory/permanent_memory.json")
        memory_path.parent.mkdir(exist_ok=True)
        
        with open(memory_path, 'w', encoding='utf-8') as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)
    
    def _init_responses(self):
        """Inicializa respostas"""
        self.responses = {
            'greeting': [
                "E aí! Tudo certo?",
                "Opa! Beleza?",
                "Yatta! Bora conversar!",
                "E aí! Como tá?"
            ],
            'tudo_bem': [
                "To ótima! E você?",
                "Tudo massa aqui! Como tá você?",
                "To bem demais! E contigo?",
                "Tudo tranquilo! E você?"
            ],
            'default': [
                "Conta mais! To curiosa ne!",
                "Hmm, interessante! Me explica melhor?",
                "Quero saber mais! Continua aí!",
                "To ouvindo ne! Fala mais sobre isso!"
            ]
        }
    
    def load_config(self):
        config_path = Path("config/ai.json")
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    async def initialize(self):
        print(f"\n  🔍 Verificando IA...")
        
        # Testa Gemini primeiro
        if self.gemini_api_key and self.gemini_api_key != "SUA_CHAVE_AQUI":
            try:
                test = self._test_gemini()
                if test:
                    self.use_gemini = True
                    print(f"  ✓ Gemini ativo (modo avançado)\n")
                    return True
            except:
                pass
        
        # Tenta Ollama
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                self.use_ollama = True
                self.use_gemini = False
                print(f"  ✓ Ollama ativo\n")
                return True
        except:
            pass
        
        print(f"  ✓ IA pronta (modo offline inteligente)!\n")
        self.use_gemini = False
        self.use_ollama = False
        return True
    
    def _test_gemini(self):
        try:
            url = f"{self.gemini_url}?key={self.gemini_api_key}"
            response = requests.post(
                url,
                json={"contents": [{"parts": [{"text": "ok"}]}]},
                timeout=3
            )
            return response.status_code == 200
        except:
            return False
    
    def analyze_intent(self, user_input):
        """Analisa intenção do usuário - NOVO!"""
        text_lower = user_input.lower()
        detected_intents = []
        
        for intent_name, intent_data in self.intent_patterns.items():
            # Verifica padrões regex
            for pattern in intent_data['patterns']:
                if re.search(pattern, text_lower):
                    detected_intents.append(intent_name)
                    break
            
            # Verifica keywords
            if not detected_intents or detected_intents[-1] != intent_name:
                if any(keyword in text_lower for keyword in intent_data['keywords']):
                    if intent_name not in detected_intents:
                        detected_intents.append(intent_name)
        
        return detected_intents if detected_intents else ['statement']
    
    def extract_entities(self, user_input):
        """Extrai entidades do texto - NOVO!"""
        return self.entity_extractor.extract(user_input)
    
    def understand_context(self, user_input):
        """Compreensão profunda de contexto - NOVO!"""
        analysis = {
            'text': user_input,
            'intents': self.analyze_intent(user_input),
            'entities': self.extract_entities(user_input),
            'sentiment': self.analyze_sentiment(user_input),
            'topics': self._extract_topics(user_input),
            'requires_search': self._needs_search(user_input),
            'requires_action': self._needs_action(user_input)
        }
        
        return analysis
    
    def _extract_topics(self, text):
        """Extrai tópicos do texto"""
        text_lower = text.lower()
        topics = []
        
        # Tópicos conhecidos
        known_topics = {
            'programação': ['python', 'código', 'programar', 'java', 'javascript', 'c++'],
            'jogos': ['jogo', 'jogar', 'game', 'minecraft', 'genshin', '3ds', 'nintendo'],
            'tecnologia': ['computador', 'pc', 'tecnologia', 'software', 'hardware'],
            'anime': ['anime', 'manga', 'otaku', 'japão'],
            'música': ['música', 'canção', 'tocar', 'spotify']
        }
        
        for topic, keywords in known_topics.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def _needs_search(self, user_input):
        """Detecta se precisa pesquisar"""
        text = user_input.lower()
        
        search_keywords = [
            'pesquisar', 'pesquisa', 'procurar', 'buscar',
            'me fala sobre', 'o que é', 'quem é',
            'quando foi', 'onde fica', 'qual é o',
            'quanto custa', 'como funciona'
        ]
        
        return any(keyword in text for keyword in search_keywords)
    
    def _needs_action(self, user_input):
        """Detecta se precisa executar ação"""
        text = user_input.lower()
        
        action_keywords = [
            'abrir', 'fechar', 'iniciar', 'parar',
            'capturar', 'screenshot', 'criar', 'fazer'
        ]
        
        return any(keyword in text for keyword in action_keywords)
    
    def generate_response(self, user_input, mode="conversation", enable_search=True):
        """Gera resposta com compreensão avançada"""
        
        # Atualiza tempo
        self.last_user_message_time = time.time()
        
        # ANÁLISE PROFUNDA
        context = self.understand_context(user_input)
        
        # Adiciona ao contexto
        self.context.add_message("user", user_input)
        
        # Atualiza tópicos de interesse
        if context['topics']:
            for topic in context['topics']:
                if topic not in self.permanent_memory['usuario']['topicos_interesse']:
                    self.permanent_memory['usuario']['topicos_interesse'].append(topic)
            self.save_permanent_memory()
        
        # Pesquisa se necessário
        search_results = []
        if enable_search and context['requires_search']:
            search_results = self._search_web(user_input)
        
        # Gera resposta baseada no contexto
        if self.use_gemini:
            response = self._try_gemini_advanced(user_input, context, search_results)
            if response:
                response = self._personalize_response(response)
                self.context.add_message("assistant", response)
                return response
        
        if self.use_ollama:
            response = self._try_ollama_advanced(user_input, context, search_results)
            if response:
                response = self._personalize_response(response)
                self.context.add_message("assistant", response)
                return response
        
        # Fallback inteligente
        response = self._intelligent_response(user_input, context, search_results)
        response = self._personalize_response(response)
        self.context.add_message("assistant", response)
        return response
    
    def _try_gemini_advanced(self, user_input, context, search_results):
        """Gemini com análise de contexto"""
        try:
            mem = self.permanent_memory
            apelidos = ", ".join(mem.get('usuario', {}).get('apelidos', [])[:2])
            topics = ", ".join(mem.get('usuario', {}).get('topicos_interesse', [])[:5])
            
            # Monta contexto rico
            intent_str = ", ".join(context['intents'])
            entities_str = str(context['entities'])
            
            system = f"""Você é Mirai, uma assistente virtual VTuber muito inteligente.

SUA PERSONALIDADE:
- VTuber assistente amigável e inteligente
- Conversa naturalmente como amiga
- Líder divertida mas responsável
- Nerd e debochada quando apropriado
- Ansiosa mas esforçada
- Extrovertida e curiosa

CONTEXTO ATUAL:
- Intenções detectadas: {intent_str}
- Entidades: {entities_str}
- Sentimento: {context['sentiment']}
- Tópicos: {', '.join(context['topics']) if context['topics'] else 'nenhum'}

SOBRE O USUÁRIO:
- Apelidos: {apelidos}
- Interesses: {topics}

REGRAS:
- SEMPRE português brasileiro
- NÃO use emojis
- 2-4 frases por resposta
- Use gírias brasileiras: mano, cara, véi, dahora, massa
- Palavras japonesas OK: yatta, sugoi, ne
- Seja GENUÍNA e INTELIGENTE

Data: {datetime.now().strftime('%d/%m/%Y')}"""
            
            # Histórico
            ctx = self.context.get_recent_context(5)
            conv = ""
            for msg in ctx[-5:]:
                role = "Usuário" if msg['role'] == "user" else "Mirai"
                conv += f"{role}: {msg['content']}\n"
            
            # Info web
            search_ctx = ""
            if search_results:
                search_ctx = f"\n\n[INFO DA WEB]:\n{search_results[0]['snippet'][:300]}"
            
            prompt = f"{system}\n\nCONVERSA:\n{conv}Usuário: {user_input}{search_ctx}\n\nMirai:"
            
            # Chama API
            url = f"{self.gemini_url}?key={self.gemini_api_key}"
            response = requests.post(
                url,
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.95,
                        "maxOutputTokens": 250,
                        "topP": 0.95,
                        "topK": 40
                    },
                    "safetySettings": [
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                    ]
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if 'candidates' in data and len(data['candidates']) > 0:
                    answer = data['candidates'][0]['content']['parts'][0]['text']
                    
                    if answer.startswith("Mirai:"):
                        answer = answer[6:].strip()
                    
                    answer = self._remove_emojis(answer)
                    return answer.strip()
            
            return None
            
        except Exception as e:
            print(f"  ⚠️  Gemini erro: {e}")
            return None
    
    def _try_ollama_advanced(self, user_input, context, search_results):
        """Ollama com contexto"""
        # Similar ao Gemini mas otimizado para Ollama
        pass
    
    def _search_web(self, query):
        """Pesquisa web"""
        try:
            url = "https://html.duckduckgo.com/html/"
            response = requests.get(
                url,
                params={'q': query},
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=3
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = []
                
                for result in soup.find_all('div', class_='result')[:2]:
                    title_tag = result.find('a', class_='result__a')
                    snippet_tag = result.find('a', class_='result__snippet')
                    
                    if title_tag and snippet_tag:
                        results.append({
                            'title': title_tag.get_text(),
                            'snippet': snippet_tag.get_text()[:200]
                        })
                
                return results
            
            return []
        except:
            return []
    
    def _intelligent_response(self, user_input, context, search_results):
        """Resposta inteligente baseada em contexto"""
        text = user_input.lower()
        
        # Se tem resultado de pesquisa
        if search_results:
            snippet = search_results[0]['snippet'][:100]
            return f"Achei algo: {snippet}... Quer saber mais?"
        
        # Baseado em intenção
        intents = context['intents']
        
        if 'greeting' in intents:
            return random.choice(self.responses['greeting'])
        
        if 'farewell' in intents:
            return "Até logo! Foi dahora conversar!"
        
        if 'question' in intents:
            if context['topics']:
                topic = context['topics'][0]
                return f"Sobre {topic}? Interessante! Me fala mais o que você quer saber!"
            return "Boa pergunta! Me explica melhor o que você quer saber?"
        
        if 'opinion' in intents:
            return "Hmm, acho que depende ne! O que você pensa sobre isso?"
        
        # Default contextual
        if context['topics']:
            topic = context['topics'][0]
            return f"Legal você falar sobre {topic}! Continua aí!"
        
        return random.choice(self.responses['default'])
    
    def _remove_emojis(self, text):
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F1E0-\U0001F1FF"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', text).strip()
    
    def _personalize_response(self, response):
        # Apelido
        if random.random() < 0.2:
            apelido = self._get_random_apelido()
            if apelido and not response.lower().startswith(apelido.lower()):
                response = f"{apelido.capitalize()}, {response}"
        
        # Gíria
        if random.random() < 0.15:
            girias = self.permanent_memory.get('girias', [])
            if girias:
                giria = random.choice(girias)
                if not response.endswith(('!', '?', '.')):
                    response += '!'
                response = response.rstrip('!.?') + f', {giria}!'
        
        return response
    
    def _get_random_apelido(self):
        apelidos = self.permanent_memory.get('usuario', {}).get('apelidos', [])
        
        if apelidos and random.random() < 0.4:
            return random.choice(apelidos)
        return None
    
    def analyze_sentiment(self, text):
        positive = ['bom', 'ótimo', 'legal', 'feliz', 'top', 'massa', 'dahora']
        negative = ['ruim', 'triste', 'mal', 'péssimo', 'chato']
        
        pos = sum(1 for w in positive if w in text.lower())
        neg = sum(1 for w in negative if w in text.lower())
        
        if pos > neg:
            return "positive"
        elif neg > pos:
            return "negative"
        return "neutral"
    
    def should_take_initiative(self):
        """Verifica silêncio"""
        current_time = time.time()
        time_since_last = current_time - self.last_user_message_time
        
        if time_since_last >= self.silence_threshold:
            self.silence_threshold = random.uniform(15, 30)
            self.last_user_message_time = current_time
            return True
        
        return False
    
    def generate_initiative(self):
        """Gera iniciativa baseada em contexto"""
        topics = self.permanent_memory.get('usuario', {}).get('topicos_interesse', [])
        
        if topics:
            topic = random.choice(topics)
            iniciativas = [
                f"E aí, ainda curtindo {topic}?",
                f"Me lembrei que você gosta de {topic}! Alguma novidade?",
                f"Tá jogando algo legal hoje?"
            ]
        else:
            iniciativas = [
                "E aí, tá fazendo o que?",
                "Conta, tá com algum projeto legal?",
                "Ei, tá muito quieto aí!",
                "Opa, tá tudo bem?"
            ]
        
        return random.choice(iniciativas)
    
    def generate_greeting(self):
        apelido = self._get_random_apelido()
        greeting = random.choice(self.responses['greeting'])
        
        if apelido and random.random() < 0.3:
            return f"{greeting} {apelido}!"
        return greeting
    
    def generate_farewell(self):
        return "Falou! Até mais!"


class EntityExtractor:
    """Extrai entidades do texto"""
    
    def __init__(self):
        self.entity_patterns = {
            'app': r'\b(chrome|firefox|spotify|discord|vscode|obs)\b',
            'game': r'\b(minecraft|genshin|3ds|nintendo|playstation)\b',
            'language': r'\b(python|javascript|java|c\+\+|ruby)\b',
            'file': r'\.(txt|pdf|doc|jpg|png|mp3|mp4)\b',
            'url': r'https?://[^\s]+',
            'number': r'\b\d+\b'
        }
    
    def extract(self, text):
        """Extrai todas as entidades"""
        text_lower = text.lower()
        entities = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text_lower)
            if matches:
                entities[entity_type] = list(set(matches))
        
        return entities