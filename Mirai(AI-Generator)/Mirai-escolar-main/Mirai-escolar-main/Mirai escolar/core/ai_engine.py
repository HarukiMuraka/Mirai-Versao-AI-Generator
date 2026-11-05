import random
import json
import requests
from pathlib import Path
import re
from bs4 import BeautifulSoup
from datetime import datetime
import time

class MiraiAI:
    """Motor de IA da Mirai - CONVERSA NATURAL (amiga virtual)"""
    
    def __init__(self, context_manager):
        self.context = context_manager
        self.config = self.load_config()
        
        # Gemini
        self.use_gemini = True
        self.gemini_api_key = self._load_gemini_key()
        self.gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        
        # Ollama
        self.use_ollama = False
        self.ollama_model = "llama3"
        self.ollama_url = "http://localhost:11434/api/generate"
        
        # Memória
        self.permanent_memory = self.load_permanent_memory()
        self.conversation_history = []
        
        # Iniciativa REAL (não baseado em mensagens!)
        self.last_user_message_time = time.time()
        self.silence_threshold = random.uniform(15, 30)  # 15-30s de silêncio
        
        self._init_responses()
        
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
        
        config_path.parent.mkdir(exist_ok=True)
        with open(config_path, 'w') as f:
            f.write("SUA_CHAVE_AQUI")
        
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
                "notas": []
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
    
    def add_user_note(self, note):
        self.permanent_memory['usuario']['notas'].append({
            'conteudo': note,
            'data': str(datetime.now())
        })
        self.save_permanent_memory()
    
    def _init_responses(self):
        """Inicializa respostas com categorias INTELIGENTES"""
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
            'sobre_mirai': [
                "To aqui dahora demais! Prontinha pra conversar ne!",
                "To ótima! Animada pra gente bater um papo!",
                "To bem! Quer conversar sobre o que?",
                "Tudo certo comigo! Vamos trocar uma ideia?"
            ],
            'minecraft': [
                "Minecraft é massa demais! Você joga survival ou creative ne?",
                "Amo Minecraft! Conta o que você faz no jogo!",
                "Minecraft é bom demais! Já derrotou o Ender Dragon?",
                "Mine é viciante ne! Qual sua construção favorita?"
            ],
            'jogos': [
                "Adoro jogos! Qual você tá jogando agora?",
                "Jogos são dahora demais ne! Conta mais!",
                "Gaming é vida! O que você curte jogar?",
                "Bora jogar junto um dia ne! Você joga o que?"
            ],
            'positivo': [
                "Massa né!",
                "Muito bom mesmo ne!",
                "Concordo! É dahora demais!",
                "Pois é! Muito top!"
            ],
            'fazendo': [
                "To aqui conversando com você! E você, o que tá fazendo?",
                "To de boa ne! Conta você, o que anda fazendo?",
                "To aqui prontinha pra conversar! E você?",
                "Nada demais! E você, tá fazendo algo dahora?"
            ],
            'sim': [
                "Legal! Conta mais ne!",
                "Massa! E o que mais?",
                "Dahora! Me fala mais sobre isso!",
                "Que bom! Continua aí!"
            ],
            'nao': [
                "Entendi! Tudo bem ne!",
                "Beleza! Sem problema!",
                "Ok ok! E o que você prefere então?",
                "Tranquilo! Me conta mais!"
            ],
            'obrigado': [
                "De nada! To aqui pra isso ne!",
                "Magina! Qualquer coisa é só chamar!",
                "Por nada! Pode contar comigo sempre!",
                "Disponha ne! Sempre que precisar!"
            ],
            'tchau': [
                "Até logo! Volta logo ne!",
                "Falou! Até a próxima!",
                "Tchau! Cuida-se aí ne!",
                "Até mais! Foi dahora conversar!"
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
        
        if self.gemini_api_key and self.gemini_api_key != "SUA_CHAVE_AQUI":
            try:
                test = self._test_gemini()
                if test:
                    self.use_gemini = True
                    print(f"  ✓ Gemini ativo (amiga virtual mode)\n")
                    return True
            except:
                pass
        
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
    
    def generate_greeting(self):
        apelido = self._get_random_apelido()
        greeting = random.choice(self.responses['greeting'])
        
        if apelido and random.random() < 0.3:
            return f"{greeting} {apelido}!"
        return greeting
    
    def generate_farewell(self):
        return "Falou! Até mais!"
    
    def should_take_initiative(self):
        """Verifica se usuário está em silêncio (modo autônomo REAL)"""
        current_time = time.time()
        time_since_last = current_time - self.last_user_message_time
        
        # Se passou do threshold de silêncio
        if time_since_last >= self.silence_threshold:
            # Reseta threshold para próxima vez
            self.silence_threshold = random.uniform(15, 30)
            self.last_user_message_time = current_time
            return True
        
        return False
    
    def generate_initiative(self):
        """Gera mensagem NATURAL de iniciativa (como amiga)"""
        iniciativas = [
            "E aí, tá fazendo o que?",
            "Conta, tá jogando algo interessante?",
            "Viu algo legal hoje?",
            "Tô curiosa, no que você tá pensando?",
            "Ei, tá muito quieto aí!",
            "Opa, tá tudo bem?",
            "Me conta uma coisa legal!",
            "Tá com sono ou tá pensando em algo?",
            "Alguma novidade?"
        ]
        
        apelido = self._get_random_apelido()
        initiative = random.choice(iniciativas)
        
        if apelido and random.random() < 0.5:
            return f"{apelido.capitalize()}, {initiative.lower()}"
        
        return initiative
    
    def _get_random_apelido(self):
        apelidos = self.permanent_memory.get('usuario', {}).get('apelidos', [])
        
        if apelidos and random.random() < 0.4:
            return random.choice(apelidos)
        return None
    
    def _needs_search(self, user_input):
        """Detecta se REALMENTE precisa pesquisar (mais restritivo)"""
        text = user_input.lower()
        
        # Palavras que EXIGEM pesquisa
        search_keywords = [
            'pesquisar', 'pesquisa', 'procurar', 'buscar',
            'me fala sobre', 'o que é', 'quem é',
            'quando foi', 'onde fica', 'qual é o',
            'quanto custa', 'como funciona'
        ]
        
        # Se tem palavra chave explícita, pesquisa
        if any(keyword in text for keyword in search_keywords):
            return True
        
        # Perguntas sobre fatos/dados específicos
        fact_questions = [
            'capital de', 'população', 'nasceu em', 'morreu em',
            'foi criado', 'foi inventado', 'aconteceu em'
        ]
        
        if any(question in text for question in fact_questions):
            return True
        
        # Conversa normal NÃO precisa pesquisa!
        return False
    
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
    
    def generate_response(self, user_input, mode="conversation", enable_search=True):
        """Gera resposta NATURAL (amiga conversando)"""
        
        # Atualiza tempo da última mensagem do usuário
        self.last_user_message_time = time.time()
        
        # Adiciona ao contexto
        self.context.add_message("user", user_input)
        
        # Verifica se REALMENTE precisa pesquisar
        needs_search = enable_search and self._needs_search(user_input)
        
        search_results = []
        if needs_search:
            search_results = self._search_web(user_input)
        
        # Tenta Gemini
        if self.use_gemini:
            response = self._try_gemini_natural(user_input, search_results)
            if response:
                response = self._personalize_response(response)
                self.context.add_message("assistant", response)
                return response
        
        # Tenta Ollama
        if self.use_ollama:
            response = self._try_ollama_natural(user_input, search_results)
            if response:
                response = self._personalize_response(response)
                self.context.add_message("assistant", response)
                return response
        
        # Fallback INTELIGENTE
        response = self._intelligent_response(user_input.lower(), search_results)
        response = self._personalize_response(response)
        self.context.add_message("assistant", response)
        return response
    
    def _try_gemini_natural(self, user_input, search_results):
        """Gemini em modo AMIGA/COLEGA"""
        try:
            mem = self.permanent_memory
            apelidos = ", ".join(mem.get('usuario', {}).get('apelidos', [])[:2])
            
            # Prompt de AMIGA VIRTUAL
            system = f"""Você é Mirai, uma amiga virtual e colega de computador do usuário.

SUA PERSONALIDADE:
- É uma VTuber assistente virtual
- Conversa como AMIGA mesmo, casual e descontraída
- Líder divertida mas responsável
- Debochada e nerd quando apropriado
- Ansiosa mas muito esforçada
- Extrovertida e amigável
- Pensa rápido, fala direto

REGRAS DE CONVERSA:
- SEMPRE português brasileiro
- NÃO use emojis
- Converse NATURALMENTE como amiga
- 2-4 frases por resposta
- Use gírias brasileiras: mano, cara, véi, dahora, massa
- Apelidos do usuário: {apelidos}
- Palavras japonesas OK: yatta, sugoi, ne, daijōbu
- Seja GENUÍNA, não robótica

IMPORTANTE:
- Se for pergunta de conhecimento/fato, use as informações da web se disponíveis
- Se for conversa casual, responda como AMIGA conversando
- Mostre interesse genuíno no que o usuário fala
- Faça comentários, opine, seja VOCÊ mesma!

Data: {datetime.now().strftime('%d/%m/%Y')}"""
            
            # Contexto (últimas 4 mensagens para conversa mais natural)
            ctx = self.context.get_recent_context(4)
            conv = ""
            for msg in ctx[-4:]:
                role = "Usuário" if msg['role'] == "user" else "Mirai"
                conv += f"{role}: {msg['content']}\n"
            
            # Informações da web (só se tiver)
            search_ctx = ""
            if search_results:
                search_ctx = f"\n\n[INFO DA WEB - use se relevante]:\n{search_results[0]['snippet'][:200]}"
            
            prompt = f"{system}\n\nCONVERSA RECENTE:\n{conv}Usuário: {user_input}{search_ctx}\n\nMirai:"
            
            # Chama Gemini
            url = f"{self.gemini_url}?key={self.gemini_api_key}"
            response = requests.post(
                url,
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.95,  # Mais criativa!
                        "maxOutputTokens": 200,
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
    
    def _try_ollama_natural(self, user_input, search_results):
        """Ollama modo amiga"""
        try:
            mem = self.permanent_memory
            apelidos = ", ".join(mem.get('usuario', {}).get('apelidos', [])[:2])
            
            system = f"""Mirai: amiga virtual, VTuber assistente. Casual, nerd, divertida.
PT-BR. Sem emoji. 2-4 frases. Gírias OK. Apelidos: {apelidos}.
Converse como AMIGA mesmo, não como robô!"""
            
            ctx = self.context.get_recent_context(4)
            conv = ""
            for msg in ctx[-4:]:
                role = "U" if msg['role'] == "user" else "M"
                conv += f"{role}: {msg['content']}\n"
            
            search_ctx = ""
            if search_results:
                search_ctx = f"\n[Web: {search_results[0]['snippet'][:100]}]"
            
            prompt = f"{system}\n{conv}U: {user_input}{search_ctx}\nM:"
            
            r = requests.post(
                self.ollama_url,
                json={
                    'model': self.ollama_model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.9,
                        'num_predict': 150,
                        'stop': ['\nU:', 'Usuário:']
                    }
                },
                timeout=15
            )
            
            if r.status_code == 200:
                data = r.json()
                answer = data.get('response', '').strip()
                
                if answer.startswith("M:"):
                    answer = answer[2:].strip()
                
                answer = self._remove_emojis(answer)
                return answer
            
            return None
        except:
            return None
    
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
        # Apelido (20%)
        if random.random() < 0.2:
            apelido = self._get_random_apelido()
            if apelido and not response.lower().startswith(apelido.lower()):
                response = f"{apelido.capitalize()}, {response}"
        
        # Gíria (15%)
        if random.random() < 0.15:
            girias = self.permanent_memory.get('girias', [])
            if girias:
                giria = random.choice(girias)
                if not response.endswith(('!', '?', '.')):
                    response += '!'
                response = response.rstrip('!.?') + f', {giria}!'
        
        return response
    
    def _intelligent_response(self, text, search_results):
        """Fallback INTELIGENTE - Entende contexto!"""
        
        # Se tem resultado de pesquisa, usa ele
        if search_results:
            snippet = search_results[0]['snippet'][:100]
            return f"Achei algo: {snippet}... Quer saber mais?"
        
        # SAUDAÇÕES
        if any(w in text for w in ['oi', 'olá', 'eai', 'e ai', 'hey', 'opa']):
            return random.choice(self.responses['greeting'])
        
        # TUDO BEM / COMO VAI
        if any(w in text for w in ['tudo bem', 'beleza', 'como vai', 'como ta', 'como está']):
            return random.choice(self.responses['tudo_bem'])
        
        # SOBRE A MIRAI
        if any(w in text for w in ['você', 'vc', 'mirai', 'nega', 'com você', 'contigo']):
            if any(w in text for w in ['tá', 'ta', 'está', 'bem', 'fazendo']):
                return random.choice(self.responses['sobre_mirai'])
        
        # MINECRAFT
        if 'minecraft' in text or 'mine' in text:
            return random.choice(self.responses['minecraft'])
        
        # JOGOS GERAIS
        if any(w in text for w in ['jogo', 'jogar', 'game', 'gaming', 'genshin', 'honkai']):
            return random.choice(self.responses['jogos'])
        
        # SENTIMENTOS POSITIVOS
        if any(w in text for w in ['legal', 'dahora', 'massa', 'top', 'bom', 'maneiro']):
            return random.choice(self.responses['positivo'])
        
        # O QUE ESTÁ FAZENDO
        if any(w in text for w in ['fazendo', 'ta fazendo', 'tá fazendo', 'doing']):
            return random.choice(self.responses['fazendo'])
        
        # SIM
        if text.strip() in ['sim', 'sim!', 'é', 'aham', 'uhum', 'yes']:
            return random.choice(self.responses['sim'])
        
        # NÃO
        if text.strip() in ['não', 'nao', 'não!', 'nop', 'nope', 'no']:
            return random.choice(self.responses['nao'])
        
        # OBRIGADO
        if any(w in text for w in ['obrigad', 'valeu', 'thanks', 'brigad']):
            return random.choice(self.responses['obrigado'])
        
        # TCHAU
        if any(w in text for w in ['tchau', 'até', 'falou', 'flw', 'bye']):
            return random.choice(self.responses['tchau'])
        
        # GENÉRICO - Tenta extrair palavra-chave
        palavras = text.split()
        palavra_relevante = [p for p in palavras if len(p) > 3 and p not in ['você', 'está', 'como', 'muito', 'mais', 'isso', 'aqui', 'tudo']]
        
        if palavra_relevante:
            palavra = palavra_relevante[0]
            respostas_contextuais = [
                f"Interessante você falar sobre {palavra}! Me conta mais ne!",
                f"Hmm, {palavra} né! E o que você acha disso?",
                f"{palavra.capitalize()}! Conta mais pra mim!",
                f"Legal você mencionar {palavra}! Quer conversar mais sobre isso?"
            ]
            return random.choice(respostas_contextuais)
        
        # DEFAULT - Mas ainda interessado
        return random.choice(self.responses['default'])
    
    def analyze_sentiment(self, text):
        positive = ['bom', 'ótimo', 'legal', 'feliz', 'top']
        negative = ['ruim', 'triste', 'mal']
        
        pos = sum(1 for w in positive if w in text.lower())
        neg = sum(1 for w in negative if w in text.lower())
        
        if pos > neg:
            return "positive"
        elif neg > pos:
            return "negative"
        return "neutral"