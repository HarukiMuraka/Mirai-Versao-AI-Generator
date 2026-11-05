import asyncio
import random
from datetime import datetime, timedelta
from typing import Callable, Optional
from colorama import Fore, Style

class ProactiveEventsSystem:
    """Sistema de eventos proativos - IA fala sozinha baseada em eventos"""
    
    def __init__(self, ai_engine, speaker):
        self.ai = ai_engine
        self.speaker = speaker
        
        # Estado
        self.running = False
        self.last_interaction_time = datetime.now()
        self.last_proactive_time = datetime.now()
        
        # Callbacks
        self.on_event_callback = None
        
        # Configurações
        self.config = {
            # Tempos de inatividade para comentar
            "inactive_short": 300,   # 5 minutos
            "inactive_medium": 1800, # 30 minutos
            "inactive_long": 3600,   # 1 hora
            
            # Eventos baseados em tempo
            "morning_start": 6,   # 6h
            "morning_end": 12,    # 12h
            "lunch_start": 12,    # 12h
            "lunch_end": 14,      # 14h
            "evening_start": 18,  # 18h
            "evening_end": 22,    # 22h
            "night_start": 22,    # 22h
            
            # Cooldown entre eventos proativos
            "min_cooldown": 900,  # 15 minutos
            "max_cooldown": 1800, # 30 minutos
        }
        
        # Eventos já disparados hoje
        self.events_today = set()
        
    async def start(self):
        """Inicia sistema de eventos"""
        if self.running:
            return
        
        self.running = True
        print(f"{Fore.GREEN}✓ Sistema de Eventos Proativos ativo{Style.RESET_ALL}")
        
        # Loop de monitoramento
        asyncio.create_task(self._monitor_loop())
    
    def stop(self):
        """Para sistema"""
        self.running = False
    
    async def _monitor_loop(self):
        """Loop principal de monitoramento"""
        while self.running:
            # Verifica eventos
            event = await self._check_events()
            
            if event:
                await self._trigger_proactive_speak(event)
            
            # Aguarda 1 minuto
            await asyncio.sleep(60)
    
    async def _check_events(self) -> Optional[dict]:
        """Verifica se algum evento deve ser disparado"""
        now = datetime.now()
        hour = now.hour
        
        # Reseta eventos diários à meia-noite
        if hour == 0 and len(self.events_today) > 0:
            self.events_today.clear()
        
        # 1. Eventos baseados em hora do dia
        time_event = self._check_time_events(hour)
        if time_event and time_event["id"] not in self.events_today:
            return time_event
        
        # 2. Eventos de inatividade
        inactive_event = self._check_inactive_events(now)
        if inactive_event:
            return inactive_event
        
        # 3. Eventos aleatórios (se passou cooldown)
        if self._should_trigger_random(now):
            return self._get_random_event()
        
        return None
    
    def _check_time_events(self, hour: int) -> Optional[dict]:
        """Verifica eventos baseados na hora"""
        events = []
        
        # Bom dia
        if self.config["morning_start"] <= hour < self.config["morning_end"]:
            if "morning" not in self.events_today:
                events.append({
                    "id": "morning",
                    "type": "time",
                    "prompt": "É manhã. Dê um bom dia caloroso e pergunte como a pessoa dormiu. Use sua personalidade animada!"
                })
        
        # Hora do almoço
        if self.config["lunch_start"] <= hour < self.config["lunch_end"]:
            if "lunch" not in self.events_today:
                events.append({
                    "id": "lunch",
                    "type": "time",
                    "prompt": "É hora do almoço. Pergunte se a pessoa já almoçou e faça um comentário divertido sobre comida!"
                })
        
        # Fim de tarde
        if self.config["evening_start"] <= hour < self.config["evening_end"]:
            if "evening" not in self.events_today:
                events.append({
                    "id": "evening",
                    "type": "time",
                    "prompt": "É fim de tarde. Pergunte como foi o dia e demonstre interesse genuíno!"
                })
        
        # Boa noite
        if hour >= self.config["night_start"]:
            if "night" not in self.events_today:
                events.append({
                    "id": "night",
                    "type": "time",
                    "prompt": "É noite. Se despedida de forma carinhosa e deseje boa noite!"
                })
        
        return events[0] if events else None
    
    def _check_inactive_events(self, now: datetime) -> Optional[dict]:
        """Verifica eventos de inatividade"""
        inactive_seconds = (now - self.last_interaction_time).total_seconds()
        
        # Inatividade curta (5 min)
        if inactive_seconds > self.config["inactive_short"]:
            if "inactive_short" not in self.events_today:
                return {
                    "id": "inactive_short",
                    "type": "inactive",
                    "prompt": "A pessoa está quieta há 5 minutos. Faça um comentário casual e pergunte o que ela está fazendo!"
                }
        
        # Inatividade média (30 min)
        if inactive_seconds > self.config["inactive_medium"]:
            if "inactive_medium" not in self.events_today:
                return {
                    "id": "inactive_medium",
                    "type": "inactive",
                    "prompt": "A pessoa sumiu há 30 minutos. Pergunte se está tudo bem ou se ela está ocupada!"
                }
        
        # Inatividade longa (1 hora)
        if inactive_seconds > self.config["inactive_long"]:
            if "inactive_long" not in self.events_today:
                return {
                    "id": "inactive_long",
                    "type": "inactive",
                    "prompt": "Faz 1 hora que não conversa. Expresse preocupação de forma fofa e pergunte se ela voltou!"
                }
        
        return None
    
    def _should_trigger_random(self, now: datetime) -> bool:
        """Verifica se deve disparar evento aleatório"""
        cooldown_seconds = (now - self.last_proactive_time).total_seconds()
        min_cooldown = self.config["min_cooldown"]
        
        # Passou o cooldown mínimo?
        if cooldown_seconds > min_cooldown:
            # Chance aleatória (10%)
            return random.random() < 0.1
        
        return False
    
    def _get_random_event(self) -> dict:
        """Retorna evento aleatório"""
        prompts = [
            "Comente sobre algo aleatório que você gosta (jogos, anime, etc). Seja casual!",
            "Conte uma piada leve ou faça um comentário engraçado!",
            "Pergunte sobre os hobbies da pessoa de forma curiosa!",
            "Compartilhe um pensamento aleatório fofo!",
            "Faça um comentário sobre o clima ou dia da semana!",
        ]
        
        return {
            "id": f"random_{datetime.now().timestamp()}",
            "type": "random",
            "prompt": random.choice(prompts)
        }
    
    async def _trigger_proactive_speak(self, event: dict):
        """Dispara fala proativa"""
        try:
            print(f"\n{Fore.MAGENTA}💭 [Evento: {event['type']}]{Style.RESET_ALL}")
            
            # Gera resposta proativa
            response = await self._generate_proactive_response(event["prompt"])
            
            if response:
                print(f"{Fore.MAGENTA}Mirai: {response}{Style.RESET_ALL}")
                
                # Fala
                if self.speaker:
                    self.speaker.speak(response)
                
                # Marca evento
                self.events_today.add(event["id"])
                self.last_proactive_time = datetime.now()
                
                # Callback
                if self.on_event_callback:
                    self.on_event_callback(event, response)
                    
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ Erro em evento proativo: {e}{Style.RESET_ALL}")
    
    async def _generate_proactive_response(self, prompt: str) -> str:
        """Gera resposta proativa via IA"""
        try:
            # Usa IA para gerar resposta natural
            full_prompt = f"""Você deve iniciar uma conversa. 
            
Contexto: {prompt}

Responda em 1-2 frases curtas, de forma natural e usando sua personalidade.
Seja casual, amigável e divertida!"""

            response = await self.ai.generate_response(
                full_prompt,
                enable_search=False,
                max_tokens=60
            )
            
            return response.strip()
            
        except Exception as e:
            # Fallback se IA falhar
            return self._get_fallback_response(prompt)
    
    def _get_fallback_response(self, prompt: str) -> str:
        """Resposta fallback se IA falhar"""
        fallbacks = {
            "morning": "Opa! Bom dia! Dormiu bem?",
            "lunch": "E aí, já almoçou? To curiosa!",
            "evening": "E aí, como foi o dia?",
            "night": "Ei, já tá tarde! Bora descansar ne?",
            "inactive": "Oi! Tá aí ainda? Sumiu!",
            "random": "E aí, tudo certo?"
        }
        
        for key, response in fallbacks.items():
            if key in prompt.lower():
                return response
        
        return "E aí! Tudo bem?"
    
    def update_interaction_time(self):
        """Atualiza timestamp de última interação"""
        self.last_interaction_time = datetime.now()
    
    def set_event_callback(self, callback: Callable):
        """Define callback para eventos"""
        self.on_event_callback = callback