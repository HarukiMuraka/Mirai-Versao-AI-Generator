class VRMExpressionManager:
    """Gerencia expressões para modelos VRM"""
    
    def __init__(self):
        # Mapeamento de emoções para expressões VRM padrão
        self.emotion_to_expression = {
            'happy': 'happy',
            'joy': 'happy',
            'excited': 'happy',
            'sad': 'sad',
            'angry': 'angry',
            'surprised': 'surprised',
            'neutral': 'neutral',
            'confused': 'neutral',
            'thinking': 'neutral',
            'relaxed': 'neutral',
            'bored': 'neutral'
        }
        
        # Blend shapes comuns em modelos VRM
        self.blend_shapes = {
            'happy': ['Joy', 'Fun', 'Happy'],
            'sad': ['Sorrow', 'Sad'],
            'angry': ['Angry'],
            'surprised': ['Surprised'],
            'neutral': ['Neutral'],
            'blink': ['Blink', 'Blink_L', 'Blink_R'],
            'mouth_a': ['A'],
            'mouth_i': ['I'],
            'mouth_u': ['U'],
            'mouth_e': ['E'],
            'mouth_o': ['O']
        }
    
    def get_expression_for_emotion(self, emotion):
        """Retorna expressão VRM baseada na emoção"""
        return self.emotion_to_expression.get(emotion.lower(), 'neutral')
    
    def get_expression_for_sentiment(self, sentiment):
        """Retorna expressão VRM baseada no sentimento"""
        sentiment_map = {
            'positive': 'happy',
            'negative': 'sad',
            'neutral': 'neutral'
        }
        emotion = sentiment_map.get(sentiment.lower(), 'neutral')
        return self.get_expression_for_emotion(emotion)
    
    def get_blend_shapes_for_expression(self, expression):
        """Retorna blend shapes necessários para a expressão"""
        return self.blend_shapes.get(expression.lower(), ['Neutral'])
    
    def analyze_text_emotion(self, text):
        """Analisa texto e retorna emoção detectada"""
        text_lower = text.lower()
        
        # Palavras-chave para detectar emoções
        emotions = {
            'happy': ['feliz', 'legal', 'massa', 'yatta', 'genial', 'ótimo', 'bom', 'alegre'],
            'sad': ['triste', 'mal', 'chato', 'ruim', 'péssimo'],
            'angry': ['raiva', 'bravo', 'irritado', 'ódio'],
            'surprised': ['nossa', 'uau', 'incrível', 'sério'],
            'confused': ['confuso', 'não entendi', 'como assim'],
            'thinking': ['hmm', 'pensando', 'deixa ver', 'acho que']
        }
        
        for emotion, keywords in emotions.items():
            if any(keyword in text_lower for keyword in keywords):
                return emotion
        
        # Detecta pontuação
        if '!' in text:
            return 'excited'
        elif '?' in text:
            return 'thinking'
        
        return 'neutral'
    
    def get_lip_sync_shapes(self, phoneme):
        """Retorna blend shapes para lip sync baseado em fonema"""
        # Mapeamento simplificado de fonemas para visemas
        phoneme_map = {
            'a': 'mouth_a',
            'e': 'mouth_e',
            'i': 'mouth_i',
            'o': 'mouth_o',
            'u': 'mouth_u'
        }
        
        return self.blend_shapes.get(phoneme_map.get(phoneme, 'mouth_a'), ['A'])