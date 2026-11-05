import re
from typing import Optional
from colorama import Fore, Style

class AutoExpressionMapper:
    """Mapeia automaticamente texto → expressões VRM/Live2D"""
    
    def __init__(self, vtuber_engine=None):
        self.vtuber = vtuber_engine
        self.enabled = True
        
        # Mapeamento de palavras-chave → emoções
        self.emotion_keywords = {
            "happy": [
                "feliz", "alegre", "legal", "massa", "dahora", "yatta", "genial",
                "ótimo", "bom", "maravilhoso", "incrível", "demais", "😊", "😄", "😁",
                "haha", "rsrs", "kkk", "!!", "✨"
            ],
            "sad": [
                "triste", "mal", "chato", "ruim", "péssimo", "pena", "😢", "😞",
                "😭", "infelizmente", "desculpa", "sinto muito"
            ],
            "angry": [
                "raiva", "bravo", "irritado", "ódio", "droga", "😠", "😡", "grr"
            ],
            "surprised": [
                "nossa", "uau", "sério", "incrível", "não acredito", "😲", "😮",
                "caramba", "eita", "opa"
            ],
            "thinking": [
                "hmm", "pensando", "deixa", "acho", "talvez", "será", "🤔",
                "não sei", "vamos ver", "me pergunto"
            ],
            "confused": [
                "confuso", "não entendi", "como assim", "que", "hein", "🤨",
                "estranho", "esquisito"
            ],
            "excited": [
                "animado", "empolgado", "ansioso", "mal posso", "vamos", "bora",
                "yay", "partiu", "let's go"
            ],
            "love": [
                "amo", "adoro", "fofo", "lindo", "amor", "❤️", "💕", "💖",
                "querido", "carinho"
            ]
        }
        
        # Padrões regex para detecção avançada
        self.patterns = {
            "question": r"\?",
            "exclamation": r"!+",
            "ellipsis": r"\.\.\.",
            "caps": r"[A-Z]{3,}",  # PALAVRAS EM CAPS
        }
    
    def map_text_to_expression(self, text: str) -> str:
        """
        Analisa texto e retorna expressão apropriada
        Retorna: nome da expressão (happy, sad, etc)
        """
        if not text:
            return "neutral"
        
        text_lower = text.lower()
        
        # 1. Verifica palavras-chave (prioridade alta)
        for emotion, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return emotion
        
        # 2. Análise de padrões
        
        # Perguntas → thinking
        if re.search(self.patterns["question"], text):
            return "thinking"
        
        # Múltiplas exclamações → excited
        if len(re.findall(self.patterns["exclamation"], text)) >= 2:
            return "excited"
        
        # Reticências → thinking ou sad
        if re.search(self.patterns["ellipsis"], text):
            # Contexto: se tem palavras tristes, sad, senão thinking
            if any(w in text_lower for w in ["mal", "triste", "pena"]):
                return "sad"
            return "thinking"
        
        # CAPS LOCK → excited ou angry
        if re.search(self.patterns["caps"], text):
            # Contexto: se tem palavras negativas, angry, senão excited
            if any(w in text_lower for w in ["raiva", "ódio", "droga"]):
                return "angry"
            return "excited"
        
        # 3. Análise de sentimento geral (simples)
        sentiment_score = self._analyze_sentiment(text_lower)
        
        if sentiment_score > 2:
            return "happy"
        elif sentiment_score < -2:
            return "sad"
        
        # 4. Default
        return "neutral"
    
    def _analyze_sentiment(self, text: str) -> int:
        """
        Análise de sentimento simples
        Retorna: score positivo/negativo
        """
        positive_words = [
            "bom", "ótimo", "legal", "massa", "dahora", "feliz", "alegre",
            "amor", "gosto", "adoro", "incrível", "genial"
        ]
        
        negative_words = [
            "mal", "ruim", "péssimo", "triste", "chato", "ódio", "raiva",
            "irritado", "pena", "infelizmente"
        ]
        
        score = 0
        
        for word in positive_words:
            if word in text:
                score += 1
        
        for word in negative_words:
            if word in text:
                score -= 1
        
        return score
    
    async def auto_set_expression(self, text: str) -> str:
        """
        Detecta emoção e define expressão VRM automaticamente
        Retorna: expressão escolhida
        """
        if not self.enabled or not self.vtuber:
            return "neutral"
        
        # Detecta expressão
        expression = self.map_text_to_expression(text)
        
        # Define no VTuber
        try:
            if self.vtuber.is_active:
                await self.vtuber.set_expression(expression)
                print(f"{Fore.MAGENTA}  [Auto] Expressão: {expression}{Style.RESET_ALL}")
        except Exception as e:
            pass
        
        return expression
    
    def enable(self):
        """Ativa mapeamento automático"""
        self.enabled = True
        print(f"{Fore.GREEN}✓ Expressões automáticas ativadas{Style.RESET_ALL}")
    
    def disable(self):
        """Desativa mapeamento automático"""
        self.enabled = False
        print(f"{Fore.YELLOW}⚠ Expressões automáticas desativadas{Style.RESET_ALL}")
    
    def add_keyword(self, emotion: str, keyword: str):
        """Adiciona palavra-chave customizada"""
        if emotion not in self.emotion_keywords:
            self.emotion_keywords[emotion] = []
        
        if keyword not in self.emotion_keywords[emotion]:
            self.emotion_keywords[emotion].append(keyword)
            print(f"{Fore.GREEN}✓ Adicionado: '{keyword}' → {emotion}{Style.RESET_ALL}")
    
    def remove_keyword(self, emotion: str, keyword: str):
        """Remove palavra-chave"""
        if emotion in self.emotion_keywords:
            if keyword in self.emotion_keywords[emotion]:
                self.emotion_keywords[emotion].remove(keyword)
                print(f"{Fore.YELLOW}⚠ Removido: '{keyword}' de {emotion}{Style.RESET_ALL}")


class ExpressionAnimator:
    """Animações de transição entre expressões"""
    
    def __init__(self, vtuber_engine):
        self.vtuber = vtuber_engine
        self.current_expression = "neutral"
    
    async def animate_transition(self, target_expression: str, duration: float = 0.5):
        """
        Anima transição suave entre expressões
        duration: duração em segundos
        """
        if not self.vtuber or not self.vtuber.is_active:
            return
        
        # Transição instantânea por enquanto
        # (transições suaves requerem suporte do VSeeFace)
        await self.vtuber.set_expression(target_expression)
        self.current_expression = target_expression
    
    async def pulse_expression(self, expression: str, times: int = 2):
        """Pisca uma expressão (enfatiza emoção)"""
        original = self.current_expression
        
        for _ in range(times):
            await self.vtuber.set_expression(expression)
            await asyncio.sleep(0.3)
            await self.vtuber.set_expression("neutral")
            await asyncio.sleep(0.2)
        
        await self.vtuber.set_expression(original)