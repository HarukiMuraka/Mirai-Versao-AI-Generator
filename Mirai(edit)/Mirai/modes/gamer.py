from modes.base_mode import BaseMode
from perception.text_input import TextInput
from colorama import Fore, Style
import asyncio
import random
from datetime import datetime

class GamerMode(BaseMode):
    """Modo Gamer - Chat e Lives"""
    
    def __init__(self, mirai_instance):
        super().__init__(mirai_instance)
        self.current_game = None
        
    async def enter(self):
        self.is_active = True
        self.state.set_state("gamer")
        self.print_mode_header("MODO GAMER / LIVES")
        
        print(f"{Fore.GREEN}Yatta! Modo gamer ativado! 🎮{Style.RESET_ALL}\n")
        
        await self.show_gamer_menu()
    
    async def exit(self):
        self.is_active = False
        print(f"\n{Fore.CYAN}Saindo do modo gamer...{Style.RESET_ALL}")
    
    async def process_input(self, user_input):
        return self.ai.generate_response(user_input, mode="gamer")
    
    async def show_gamer_menu(self):
        """Menu principal gamer"""
        while self.is_active:
            print(f"\n{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}🎮 MODO GAMER{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}\n")
            
            print("1. 💬 Chat da Live (Simulado)")
            print("2. 🎲 Conversa sobre Jogos")
            print("3. 😊 Teste de Reações")
            print("4. 🎯 Quiz de Jogos")
            print("0. ⬅️  Voltar")
            
            choice = input(f"\n{Fore.GREEN}Opção: {Style.RESET_ALL}")
            
            if choice == "1":
                await self.chat_mode()
            elif choice == "2":
                await self.game_talk()
            elif choice == "3":
                await self.test_reactions()
            elif choice == "4":
                await self.game_quiz()
            elif choice == "0":
                break
    
    async def chat_mode(self):
        """Modo chat de live SIMULADO"""
        print(f"\n{Fore.GREEN}💬 Chat da Live Ativado!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Formato: [Nome] mensagem{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Exemplo: [João] oi mirai!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}(Digite 'sair' para voltar){Style.RESET_ALL}\n")
        
        text_input = TextInput()
        
        # Mensagem inicial
        print(f"{Fore.MAGENTA}Mirai: Olá chat! Como estão? 😊{Style.RESET_ALL}\n")
        self.speaker.speak("Olá chat! Como estão?")
        
        chat_history = []
        
        while True:
            user_input = text_input.get_input(f"{Fore.CYAN}[Chat]: {Style.RESET_ALL}")
            
            if not user_input or user_input.lower() == 'sair':
                print(f"\n{Fore.GREEN}Chat encerrado! Valeu pessoal!{Style.RESET_ALL}")
                break
            
            # Parse [Nome] mensagem
            if user_input.startswith('[') and ']' in user_input:
                parts = user_input.split(']', 1)
                author = parts[0][1:].strip()
                message = parts[1].strip() if len(parts) > 1 else ""
            else:
                author = "Viewer"
                message = user_input
            
            if message:
                # Mostra
                print(f"{Fore.CYAN}💬 {author}: {message}{Style.RESET_ALL}")
                
                # Salva histórico
                chat_history.append({'author': author, 'message': message})
                
                # Decide se responde
                should_respond = await self._should_respond_to_chat(message, chat_history)
                
                if should_respond:
                    response = await self.process_chat_message(author, message, chat_history)
                    
                    print(f"\n{Fore.MAGENTA}🌸 Mirai → {author}: {response}{Style.RESET_ALL}\n")
                    
                    # Fala
                    speech = f"{author}, {response}" if len(response) < 100 else response[:100]
                    await asyncio.to_thread(self.speaker.speak, speech)
            
            await asyncio.sleep(0.5)
    
    async def _should_respond_to_chat(self, message, history):
        """Decide se deve responder"""
        msg_lower = message.lower()
        
        # Sempre responde se mencionar Mirai
        if 'mirai' in msg_lower:
            return True
        
        # Responde perguntas
        if '?' in message:
            return random.random() < 0.5
        
        # Responde saudações
        if any(word in msg_lower for word in ['oi', 'olá', 'hey', 'hi']):
            return random.random() < 0.6
        
        # Responde elogios
        if any(word in msg_lower for word in ['legal', 'massa', 'top', 'incrível', 'linda']):
            return True
        
        # Aleatório (10%)
        return random.random() < 0.1
    
    async def process_chat_message(self, author, message, history):
        """Processa mensagem do chat com contexto"""
        # Monta contexto do chat
        recent_chat = history[-5:] if len(history) > 5 else history
        
        context = "CHAT DA LIVE:\n"
        for msg in recent_chat:
            context += f"{msg['author']}: {msg['message']}\n"
        
        context += f"\n{author} disse: {message}\n\nResponda de forma casual e divertida:"
        
        response = self.ai.generate_response(context, mode="gamer")
        
        return response
    
    async def game_talk(self):
        """Conversa sobre jogos"""
        print(f"\n{Fore.GREEN}🎮 Conversa sobre Jogos{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Vamos conversar sobre seus jogos favoritos!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}(Digite 'sair' para voltar){Style.RESET_ALL}\n")
        
        # Inicia conversa
        starters = [
            "Qual jogo você tá jogando agora?",
            "Me conta, qual seu jogo favorito de todos os tempos?",
            "Tá jogando algo interessante ultimamente?",
            "Qual jogo você mais recomendaria para mim?"
        ]
        
        starter = random.choice(starters)
        print(f"{Fore.MAGENTA}Mirai: {starter}{Style.RESET_ALL}\n")
        await asyncio.to_thread(self.speaker.speak, starter)
        
        text_input = TextInput()
        conversation_context = []
        
        while True:
            user_input = text_input.get_input(f"{Fore.GREEN}Você: {Style.RESET_ALL}")
            
            if not user_input or user_input.lower() in ['sair', 'voltar']:
                break
            
            conversation_context.append(f"Você: {user_input}")
            
            # Gera resposta com contexto
            context_str = "\n".join(conversation_context[-5:])
            full_prompt = f"Conversa sobre jogos:\n{context_str}\n\nMirai:"
            
            response = self.ai.generate_response(full_prompt, mode="gamer")
            
            conversation_context.append(f"Mirai: {response}")
            
            print(f"{Fore.MAGENTA}Mirai: {response}{Style.RESET_ALL}\n")
            await asyncio.to_thread(self.speaker.speak, response)
    
    async def test_reactions(self):
        """Teste de reações verbais"""
        print(f"\n{Fore.YELLOW}😊 Teste de Reações{Style.RESET_ALL}\n")
        
        reactions = [
            ("happy", "Yatta! Estou feliz! ✨", "🎉"),
            ("surprised", "Nani?! Que surpresa!", "😲"),
            ("sad", "Ahh... que tristeza...", "😢"),
            ("confused", "Hmm? Não entendi...", "🤔"),
            ("excited", "Sugoi! Incrível! 🎉", "⭐"),
            ("thinking", "Deixa eu pensar...", "💭"),
            ("angry", "Mou! Que raiva!", "😠"),
            ("joy", "Hehehe! Que legal!", "😊")
        ]
        
        for expression, text, emoji in reactions:
            print(f"{Fore.MAGENTA}{emoji} Mirai ({expression}): {text}{Style.RESET_ALL}")
            await asyncio.to_thread(self.speaker.speak, text)
            await asyncio.sleep(2)
        
        print(f"\n{Fore.GREEN}✓ Teste concluído!{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    async def game_quiz(self):
        """Quiz sobre jogos"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}🎯 QUIZ DE JOGOS{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        questions = [
            {
                'question': 'Em que ano Minecraft foi lançado?',
                'options': ['2009', '2011', '2013', '2015'],
                'correct': 0,
                'explanation': 'Minecraft foi lançado em 2009 por Markus Persson!'
            },
            {
                'question': 'Qual é o boss final de Terraria (pré-hardmode)?',
                'options': ['Eye of Cthulhu', 'Wall of Flesh', 'Skeletron', 'King Slime'],
                'correct': 1,
                'explanation': 'Wall of Flesh é o boss final do pré-hardmode!'
            },
            {
                'question': 'Quantos elementos tem em Genshin Impact?',
                'options': ['5', '6', '7', '8'],
                'correct': 2,
                'explanation': 'São 7 elementos: Anemo, Geo, Electro, Dendro, Hydro, Pyro, Cryo!'
            },
            {
                'question': 'Qual jogo popularizou o gênero Battle Royale?',
                'options': ['Fortnite', 'PUBG', 'Apex Legends', 'H1Z1'],
                'correct': 1,
                'explanation': 'PUBG (PlayerUnknown\'s Battlegrounds) popularizou o gênero em 2017!'
            }
        ]
        
        score = 0
        
        for i, q in enumerate(questions, 1):
            print(f"{Fore.YELLOW}Pergunta {i}/{len(questions)}:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{q['question']}{Style.RESET_ALL}\n")
            
            for idx, option in enumerate(q['options'], 1):
                print(f"  {idx}. {option}")
            
            answer = input(f"\n{Fore.GREEN}Sua resposta (1-4): {Style.RESET_ALL}")
            
            try:
                answer_idx = int(answer) - 1
                
                if answer_idx == q['correct']:
                    score += 1
                    print(f"\n{Fore.GREEN}✓ Correto! {q['explanation']}{Style.RESET_ALL}\n")
                    await asyncio.to_thread(self.speaker.speak, "Correto!")
                else:
                    correct_answer = q['options'][q['correct']]
                    print(f"\n{Fore.RED}✗ Errado! A resposta certa é: {correct_answer}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}{q['explanation']}{Style.RESET_ALL}\n")
                    await asyncio.to_thread(self.speaker.speak, "Errou!")
            except:
                print(f"{Fore.RED}Resposta inválida!{Style.RESET_ALL}\n")
            
            if i < len(questions):
                input("Pressione Enter para próxima pergunta...")
                print()
        
        # Resultado final
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}📊 RESULTADO FINAL{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        percentage = (score / len(questions)) * 100
        print(f"Pontuação: {score}/{len(questions)} ({percentage:.0f}%)\n")
        
        if percentage == 100:
            message = "Perfeito! Você é expert em jogos! Sugoi!"
        elif percentage >= 75:
            message = "Muito bem! Você manja bastante de jogos!"
        elif percentage >= 50:
            message = "Legal! Você conhece jogos!"
        else:
            message = "Precisa jogar mais! Hehe~"
        
        print(f"{Fore.MAGENTA}Mirai: {message}{Style.RESET_ALL}")
        await asyncio.to_thread(self.speaker.speak, message)
        
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")