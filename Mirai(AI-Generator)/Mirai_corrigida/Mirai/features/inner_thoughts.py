import asyncio
from typing import Optional
from colorama import Fore, Style

class InnerThoughtsSystem:
    """Sistema de pensamentos internos - mostra raciocínio da IA"""
    
    def __init__(self, ai_engine):
        self.ai = ai_engine
        self.enabled = True
        self.show_emotions = True
        self.show_planning = True
        
    async def process_with_thoughts(self, user_input: str, enable_search: bool = False) -> tuple:
        """
        Processa entrada mostrando pensamentos internos
        Retorna: (thoughts, response, emotion)
        """
        if not self.enabled:
            response = await self.ai.generate_response(user_input, enable_search)
            return None, response, None
        
        # 1. Análise inicial (pensamento)
        thoughts = await self._analyze_input(user_input)
        
        # 2. Mostra pensamento
        self._display_thought(thoughts)
        
        # 3. Gera resposta baseada na análise
        response = await self.ai.generate_response(user_input, enable_search)
        
        # 4. Detecta emoção da resposta
        emotion = self._detect_emotion(response)
        
        return thoughts, response, emotion
    
    async def _analyze_input(self, user_input: str) -> dict:
        """Analisa entrada e gera pensamento"""
        # Análise rápida baseada em padrões
        analysis = {
            "intent": self._detect_intent(user_input),
            "emotion_detected": self._detect_user_emotion(user_input),
            "topic": self._detect_topic(user_input),
            "requires_search": self._should_search(user_input),
            "planning": self._plan_response(user_input)
        }
        
        return analysis
    
    def _detect_intent(self, text: str) -> str:
        """Detecta intenção do usuário"""
        text_lower = text.lower()
        
        if any(q in text_lower for q in ["?", "como", "por que", "qual", "quando", "onde"]):
            return "pergunta"
        elif any(g in text_lower for g in ["oi", "olá", "hey", "e aí"]):
            return "saudação"
        elif any(c in text_lower for q in ["obrigado", "valeu", "thanks"]):
            return "agradecimento"
        elif any(c in text_lower for q in ["tchau", "até", "bye", "flw"]):
            return "despedida"
        elif any(c in text_lower for q in ["ajuda", "help", "socorro"]):
            return "pedido_ajuda"
        else:
            return "conversa_casual"
    
    def _detect_user_emotion(self, text: str) -> str:
        """Detecta emoção do usuário"""
        text_lower = text.lower()
        
        if any(w in text_lower for w in ["feliz", "legal", "massa", "dahora", "😊", "😄"]):
            return "feliz"
        elif any(w in text_lower for w in ["triste", "mal", "chato", "ruim", "😢", "😞"]):
            return "triste"
        elif any(w in text_lower for w in ["bravo", "raiva", "irritado", "😠", "😡"]):
            return "bravo"
        elif any(w in text_lower for w in ["cansado", "sono", "exausto", "😴"]):
            return "cansado"
        else:
            return "neutro"
    
    def _detect_topic(self, text: str) -> str:
        """Detecta tópico principal"""
        text_lower = text.lower()
        
        topics = {
            "minecraft": ["minecraft", "craft", "creeper", "steve"],
            "genshin": ["genshin", "teyvat", "primogem"],
            "honkai": ["honkai", "star rail"],
            "jogos": ["jogo", "game", "jogar", "gameplay"],
            "anime": ["anime", "manga", "otaku"],
            "programação": ["código", "programar", "python", "código"],
            "pessoal": ["eu", "mim", "minha", "meu"]
        }
        
        for topic, keywords in topics.items():
            if any(k in text_lower for k in keywords):
                return topic
        
        return "geral"
    
    def _should_search(self, text: str) -> bool:
        """Verifica se deve fazer pesquisa web"""
        text_lower = text.lower()
        
        search_indicators = [
            "pesquisa", "procura", "busca", "qual é", "me fala sobre",
            "informação", "notícia", "aconteceu", "atual"
        ]
        
        return any(ind in text_lower for ind in search_indicators)
    
    def _plan_response(self, text: str) -> str:
        """Planeja como responder"""
        intent = self._detect_intent(text)
        emotion = self._detect_user_emotion(text)
        topic = self._detect_topic(text)
        
        plans = {
            "pergunta": "Vou responder com informação útil!",
            "saudação": "Vou cumprimentar de volta com energia!",
            "agradecimento": "Vou aceitar o agradecimento de forma fofa!",
            "despedida": "Vou me despedir de forma carinhosa!",
            "pedido_ajuda": "Vou ajudar com tudo que puder!",
            "conversa_casual": "Vou bater um papo legal!"
        }
        
        plan = plans.get(intent, "Vou responder naturalmente!")
        
        # Ajusta baseado em emoção
        if emotion == "triste":
            plan += " Com empatia e carinho!"
        elif emotion == "feliz":
            plan += " Com muita energia!"
        elif emotion == "bravo":
            plan += " Com calma e compreensão!"
        
        return plan
    
    def _detect_emotion(self, response: str) -> str:
        """Detecta emoção da própria resposta"""
        response_lower = response.lower()
        
        if any(w in response_lower for w in ["feliz", "legal", "massa", "yatta", "!"]):
            return "happy"
        elif any(w in response_lower for w in ["triste", "mal", "pena"]):
            return "sad"
        elif any(w in response_lower for w in ["hmm", "pensando", "deixa", "?"]):
            return "thinking"
        elif any(w in response_lower for w in ["nossa", "uau", "sério"]):
            return "surprised"
        else:
            return "neutral"
    
    def _display_thought(self, thoughts: dict):
        """Exibe pensamento interno formatado"""
        if not self.enabled:
            return
        
        print(f"\n{Fore.CYAN}╔══════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║  {Fore.MAGENTA}💭 Pensamento Interno{Fore.CYAN}            ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╠══════════════════════════════════════╣{Style.RESET_ALL}")
        
        # Intenção
        intent_text = {
            "pergunta": "Pergunta detectada!",
            "saudação": "Opa, tá me cumprimentando!",
            "agradecimento": "Aww, tão me agradecendo!",
            "despedida": "Tá indo embora...",
            "pedido_ajuda": "Precisa de ajuda!",
            "conversa_casual": "Bora bater papo!"
        }
        print(f"{Fore.CYAN}║{Style.RESET_ALL} 🎯 {intent_text.get(thoughts['intent'], 'Analisando...')}")
        
        # Emoção detectada
        if thoughts['emotion_detected'] != "neutro":
            emotion_text = {
                "feliz": "Tá feliz! Que bom!",
                "triste": "Parece triste... vou ser gentil!",
                "bravo": "Tá bravo... preciso acalmar!",
                "cansado": "Tá cansado coitado!"
            }
            print(f"{Fore.CYAN}║{Style.RESET_ALL} 😊 {emotion_text.get(thoughts['emotion_detected'])}")
        
        # Tópico
        if thoughts['topic'] != "geral":
            topic_reactions = {
                "minecraft": "Minecraft! Eu amo!",
                "genshin": "Genshin! Que jogo dahora!",
                "jogos": "Jogos! Meu assunto favorito!",
                "anime": "Anime! Sou otaku também!"
            }
            reaction = topic_reactions.get(thoughts['topic'], f'Tópico: {thoughts["topic"]}')
            print(f"{Fore.CYAN}║{Style.RESET_ALL} 🎮 {reaction}")
        
        # Pesquisa
        if thoughts['requires_search']:
            print(f"{Fore.CYAN}║{Style.RESET_ALL} 🔍 Vou pesquisar pra dar info atual!")
        
        # Plano
        print(f"{Fore.CYAN}║{Style.RESET_ALL} 💡 {thoughts['planning']}")
        
        print(f"{Fore.CYAN}╚══════════════════════════════════════╝{Style.RESET_ALL}\n")
    
    def enable(self):
        """Ativa pensamentos"""
        self.enabled = True
        print(f"{Fore.GREEN}✓ Pensamentos internos ativados{Style.RESET_ALL}")
    
    def disable(self):
        """Desativa pensamentos"""
        self.enabled = False
        print(f"{Fore.YELLOW}⚠ Pensamentos internos desativados{Style.RESET_ALL}")
    
    def toggle(self):
        """Alterna estado"""
        self.enabled = not self.enabled
        if self.enabled:
            self.enable()
        else:
            self.disable()