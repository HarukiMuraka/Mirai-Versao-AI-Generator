from modes.base_mode import BaseMode
import pyautogui
import time
from PIL import Image
import pytesseract
from colorama import Fore, Style
import asyncio
from datetime import datetime
import json
from pathlib import Path
import threading
from collections import deque

class ObserverModeV2(BaseMode):
    """Modo Observação Reimaginado - Proativo e Inteligente"""
    
    def __init__(self, mirai_instance):
        super().__init__(mirai_instance)
        
        # Configuração de observação
        self.observing = False
        self.observation_interval = 30  # segundos entre observações
        self.observation_thread = None
        
        # Histórico de observações
        self.observation_history = deque(maxlen=50)
        
        # Padrões detectados
        self.detected_patterns = {
            'app_usage': {},
            'time_of_day_activities': {},
            'productivity_score': 0,
            'distraction_score': 0
        }
        
        # Categorias de atividades
        self.activity_categories = {
            'productive': ['vscode', 'code', 'python', 'programming', 'work', 'study'],
            'communication': ['email', 'slack', 'teams', 'zoom', 'discord', 'whatsapp'],
            'entertainment': ['youtube', 'netflix', 'twitch', 'game', 'spotify', 'music'],
            'social': ['facebook', 'instagram', 'twitter', 'reddit', 'tiktok'],
            'reading': ['article', 'documentation', 'pdf', 'book', 'wikipedia']
        }
        
        # Configurar Tesseract
        self._setup_tesseract()
    
    def _setup_tesseract(self):
        """Detecta Tesseract"""
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            '/usr/bin/tesseract',
            '/usr/local/bin/tesseract'
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                pytesseract.pytesseract.tesseract_cmd = path
                return True
        
        print(f"  ⚠️  Tesseract não encontrado - análise de texto limitada")
        return False
    
    async def enter(self):
        """Entra no modo observador"""
        self.is_active = True
        self.state.set_state("observer")
        self.print_mode_header("MODO OBSERVAÇÃO V2 - INTELIGENTE")
        
        print(f"{Fore.GREEN}Modo observação ativado! Vou te observar e te ajudar!{Style.RESET_ALL}\n")
        
        await self.show_observer_menu()
    
    async def exit(self):
        """Sai do modo observador"""
        self.is_active = False
        self.observing = False
        
        # Para thread se estiver rodando
        if self.observation_thread and self.observation_thread.is_alive():
            self.observing = False
            self.observation_thread.join(timeout=2)
        
        # Salva padrões detectados
        self._save_observation_data()
        
        print(f"\n{Fore.CYAN}Saindo do modo observação...{Style.RESET_ALL}")
    
    async def process_input(self, user_input):
        """Processa input"""
        return self.ai.generate_response(user_input, mode="observer")
    
    async def show_observer_menu(self):
        """Menu do observador"""
        while self.is_active:
            print(f"\n{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}👁️  MODO OBSERVAÇÃO V2{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}\n")
            
            print("1. 🔄 Observação Contínua (Inteligente)")
            print("2. 📸 Análise Única de Tela")
            print("3. 📊 Ver Padrões Detectados")
            print("4. 💡 Sugestões de Produtividade")
            print("5. 📈 Relatório de Atividades")
            print("6. ⚙️  Configurar Observação")
            print("0. ⬅️  Voltar")
            
            choice = input(f"\n{Fore.GREEN}Opção: {Style.RESET_ALL}")
            
            if choice == "1":
                await self.continuous_observation()
            elif choice == "2":
                await self.single_screen_analysis()
            elif choice == "3":
                self.show_detected_patterns()
            elif choice == "4":
                await self.show_productivity_suggestions()
            elif choice == "5":
                await self.generate_activity_report()
            elif choice == "6":
                await self.configure_observation()
            elif choice == "0":
                break
    
    async def continuous_observation(self):
        """Observação contínua INTELIGENTE"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}🔄 OBSERVAÇÃO CONTÍNUA ATIVADA{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        print(f"{Fore.GREEN}✓ Vou observar sua tela a cada {self.observation_interval}s{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Vou detectar padrões e te dar sugestões!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⏸️  Pressione Ctrl+C para pausar\n{Style.RESET_ALL}")
        
        self.speaker.speak(f"Observação contínua ativada! Vou te observar a cada {self.observation_interval} segundos.")
        
        self.observing = True
        observation_count = 0
        
        try:
            while self.observing:
                observation_count += 1
                
                print(f"{Fore.CYAN}📸 Observação #{observation_count} - {datetime.now().strftime('%H:%M:%S')}{Style.RESET_ALL}")
                
                # Captura e analisa
                observation = await self._perform_intelligent_observation()
                
                # Armazena
                self.observation_history.append(observation)
                
                # Atualiza padrões
                self._update_patterns(observation)
                
                # Mostra resumo
                self._display_observation_summary(observation)
                
                # Verifica se deve dar sugestão
                if observation_count % 5 == 0:  # A cada 5 observações
                    await self._check_and_suggest()
                
                # Aguarda
                for i in range(self.observation_interval):
                    if not self.observing:
                        break
                    await asyncio.sleep(1)
                    
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⏸️  Observação pausada{Style.RESET_ALL}")
            self.observing = False
        
        # Mostra resumo final
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}📊 RESUMO DA SESSÃO{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        print(f"Total de observações: {observation_count}")
        print(f"Duração: ~{(observation_count * self.observation_interval) // 60} minutos\n")
        
        self._show_session_insights()
        
        input(f"\n{Fore.CYAN}Pressione Enter para continuar...{Style.RESET_ALL}")
    
    async def _perform_intelligent_observation(self) -> dict:
        """Realiza observação inteligente da tela"""
        observation = {
            'timestamp': datetime.now().isoformat(),
            'screenshot_path': None,
            'text_content': "",
            'detected_activity': None,
            'activity_category': None,
            'apps_detected': [],
            'dominant_color': None,
            'brightness': 0,
            'productivity_indicator': 0  # -1 a 1
        }
        
        try:
            # Captura screenshot
            screenshot = pyautogui.screenshot()
            
            # Salva (opcional - pode desabilitar para economizar espaço)
            if observation_count := len(self.observation_history) % 10 == 0:  # Salva 1 a cada 10
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                path = f"memory/observations/obs_{timestamp}.png"
                Path(path).parent.mkdir(parents=True, exist_ok=True)
                screenshot.save(path)
                observation['screenshot_path'] = path
            
            # OCR - Extrai texto
            try:
                text = pytesseract.image_to_string(screenshot, lang='por+eng')
                observation['text_content'] = text
            except:
                observation['text_content'] = ""
            
            # Detecta atividade do texto
            activity_info = self._detect_activity_from_text(observation['text_content'])
            observation['detected_activity'] = activity_info['activity']
            observation['activity_category'] = activity_info['category']
            observation['apps_detected'] = activity_info['apps']
            observation['productivity_indicator'] = activity_info['productivity_score']
            
            # Análise visual
            observation['dominant_color'] = self._get_dominant_color(screenshot)
            observation['brightness'] = self._calculate_brightness(screenshot)
            
        except Exception as e:
            print(f"  ⚠️  Erro na observação: {e}")
        
        return observation
    
    def _detect_activity_from_text(self, text: str) -> dict:
        """Detecta atividade do usuário baseado no texto"""
        text_lower = text.lower()
        
        result = {
            'activity': 'unknown',
            'category': 'unknown',
            'apps': [],
            'productivity_score': 0
        }
        
        # Detecta apps/sites
        apps_keywords = {
            'vscode': ['visual studio code', 'vscode', 'vs code'],
            'chrome': ['chrome', 'google chrome'],
            'youtube': ['youtube', 'yt'],
            'discord': ['discord'],
            'spotify': ['spotify'],
            'excel': ['excel', 'spreadsheet'],
            'word': ['word', 'documento'],
            'minecraft': ['minecraft'],
            'python': ['python', 'def ', 'import '],
            'javascript': ['javascript', 'const ', 'let '],
        }
        
        for app, keywords in apps_keywords.items():
            if any(kw in text_lower for kw in keywords):
                result['apps'].append(app)
        
        # Categoriza atividade
        for category, keywords in self.activity_categories.items():
            if any(kw in text_lower for kw in keywords):
                result['category'] = category
                
                # Score de produtividade
                if category == 'productive':
                    result['productivity_score'] = 1
                    result['activity'] = 'working_or_studying'
                elif category == 'reading':
                    result['productivity_score'] = 0.5
                    result['activity'] = 'reading'
                elif category == 'communication':
                    result['productivity_score'] = 0.3
                    result['activity'] = 'communicating'
                elif category in ['entertainment', 'social']:
                    result['productivity_score'] = -0.5
                    result['activity'] = 'entertainment'
                
                break
        
        return result
    
    def _get_dominant_color(self, screenshot: Image) -> str:
        """Pega cor dominante"""
        small = screenshot.resize((50, 50))
        pixels = list(small.getdata())
        
        # Média RGB
        avg_r = sum(p[0] for p in pixels) / len(pixels)
        avg_g = sum(p[1] for p in pixels) / len(pixels)
        avg_b = sum(p[2] for p in pixels) / len(pixels)
        
        # Nomeia
        if avg_r > 200 and avg_g > 200 and avg_b > 200:
            return "light"
        elif avg_r < 50 and avg_g < 50 and avg_b < 50:
            return "dark"
        else:
            return "mixed"
    
    def _calculate_brightness(self, screenshot: Image) -> float:
        """Calcula brilho"""
        gray = screenshot.convert('L')
        pixels = list(gray.getdata())
        return sum(pixels) / len(pixels) / 255
    
    def _display_observation_summary(self, observation: dict):
        """Mostra resumo da observação"""
        activity = observation.get('detected_activity', 'unknown')
        category = observation.get('activity_category', 'unknown')
        apps = observation.get('apps_detected', [])
        
        if activity != 'unknown':
            print(f"  Atividade: {Fore.CYAN}{activity}{Style.RESET_ALL}")
            print(f"  Categoria: {category}")
            
            if apps:
                print(f"  Apps: {', '.join(apps)}")
            
            # Indicador de produtividade
            score = observation.get('productivity_indicator', 0)
            if score > 0.5:
                print(f"  💚 Produtivo!")
            elif score < -0.3:
                print(f"  🎮 Entretenimento")
            else:
                print(f"  ⚪ Neutro")
        else:
            print(f"  {Fore.YELLOW}❓ Atividade não identificada{Style.RESET_ALL}")
        
        print()
    
    def _update_patterns(self, observation: dict):
        """Atualiza padrões detectados"""
        # Uso de apps
        for app in observation.get('apps_detected', []):
            if app not in self.detected_patterns['app_usage']:
                self.detected_patterns['app_usage'][app] = 0
            self.detected_patterns['app_usage'][app] += 1
        
        # Atividades por hora
        hour = datetime.now().hour
        category = observation.get('activity_category', 'unknown')
        
        if hour not in self.detected_patterns['time_of_day_activities']:
            self.detected_patterns['time_of_day_activities'][hour] = {}
        
        if category not in self.detected_patterns['time_of_day_activities'][hour]:
            self.detected_patterns['time_of_day_activities'][hour][category] = 0
        
        self.detected_patterns['time_of_day_activities'][hour][category] += 1
        
        # Scores acumulados
        score = observation.get('productivity_indicator', 0)
        if score > 0:
            self.detected_patterns['productivity_score'] += score
        else:
            self.detected_patterns['distraction_score'] += abs(score)
    
    async def _check_and_suggest(self):
        """Verifica padrões e sugere melhorias"""
        # Calcula estatísticas recentes
        recent = list(self.observation_history)[-10:]  # Últimas 10
        
        if not recent:
            return
        
        # Conta categorias
        categories_count = {}
        for obs in recent:
            cat = obs.get('activity_category', 'unknown')
            categories_count[cat] = categories_count.get(cat, 0) + 1
        
        # Verifica padrões preocupantes
        entertainment_ratio = categories_count.get('entertainment', 0) / len(recent)
        productive_ratio = categories_count.get('productive', 0) / len(recent)
        
        suggestion = None
        
        # Muita distração
        if entertainment_ratio > 0.6:
            suggestion = "Percebi que você está muito tempo em entretenimento. Que tal fazer uma pausa produtiva?"
        
        # Muito trabalho
        elif productive_ratio > 0.8:
            suggestion = "Você está trabalhando muito! Que tal fazer uma pausa de 5 minutos?"
        
        # Modo escuro sempre
        dark_screens = sum(1 for obs in recent if obs.get('dominant_color') == 'dark')
        if dark_screens >= 8:
            suggestion = "Sua tela está sempre escura. Lembre-se de iluminar o ambiente!"
        
        if suggestion:
            print(f"\n{Fore.YELLOW}💡 SUGESTÃO:{Style.RESET_ALL}")
            print(f"  {suggestion}\n")
            self.speaker.speak(suggestion)
    
    async def single_screen_analysis(self):
        """Análise única e detalhada"""
        print(f"\n{Fore.CYAN}📸 Análise Detalhada da Tela{Style.RESET_ALL}\n")
        
        await asyncio.sleep(2)
        
        observation = await self._perform_intelligent_observation()
        
        # Mostra TUDO
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}ANÁLISE COMPLETA{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        print(f"🕐 Timestamp: {observation['timestamp']}")
        print(f"🎯 Atividade: {observation['detected_activity']}")
        print(f"📂 Categoria: {observation['activity_category']}")
        print(f"📱 Apps: {', '.join(observation['apps_detected']) if observation['apps_detected'] else 'Nenhum detectado'}")
        print(f"🎨 Tema: {observation['dominant_color']}")
        print(f"💡 Brilho: {observation['brightness']*100:.0f}%")
        print(f"📊 Produtividade: {observation['productivity_indicator']:.2f}")
        
        # Texto detectado
        if observation['text_content']:
            words = len(observation['text_content'].split())
            print(f"\n📝 Texto detectado: {words} palavras")
            print(f"Amostra: {observation['text_content'][:200]}...")
        
        # Pede comentário da IA
        print(f"\n{Fore.YELLOW}💬 Pedindo comentário da Mirai...{Style.RESET_ALL}\n")
        
        comment_prompt = f"""Analise esta atividade do usuário e comente:

Atividade: {observation['detected_activity']}
Categoria: {observation['activity_category']}
Apps: {observation['apps_detected']}
Texto detectado: {observation['text_content'][:300]}

Dê um comentário breve e útil:"""
        
        comment = self.ai.generate_response(comment_prompt, mode="observer")
        
        print(f"{Fore.MAGENTA}🌸 Mirai: {comment}{Style.RESET_ALL}\n")
        self.speaker.speak(comment)
        
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    def show_detected_patterns(self):
        """Mostra padrões detectados"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}📊 PADRÕES DETECTADOS{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        # Apps mais usados
        if self.detected_patterns['app_usage']:
            print(f"{Fore.YELLOW}📱 Apps Mais Usados:{Style.RESET_ALL}\n")
            sorted_apps = sorted(
                self.detected_patterns['app_usage'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            for app, count in sorted_apps[:5]:
                print(f"  {app}: {count} vezes")
            print()
        
        # Score de produtividade
        total_observations = len(self.observation_history)
        if total_observations > 0:
            prod_score = self.detected_patterns['productivity_score']
            dist_score = self.detected_patterns['distraction_score']
            
            print(f"{Fore.YELLOW}📈 Scores da Sessão:{Style.RESET_ALL}\n")
            print(f"  Produtividade: {prod_score:.1f}")
            print(f"  Distração: {dist_score:.1f}")
            
            # Ratio
            if prod_score + dist_score > 0:
                ratio = prod_score / (prod_score + dist_score)
                print(f"  Ratio: {ratio*100:.0f}% produtivo\n")
        
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    async def show_productivity_suggestions(self):
        """Mostra sugestões de produtividade"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}💡 SUGESTÕES DE PRODUTIVIDADE{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        if len(self.observation_history) < 5:
            print(f"{Fore.YELLOW}Preciso observar mais antes de dar sugestões!{Style.RESET_ALL}")
            print(f"Use a observação contínua por alguns minutos.\n")
            input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
            return
        
        # Analisa padrões com IA
        analysis_data = {
            'total_observations': len(self.observation_history),
            'app_usage': dict(list(self.detected_patterns['app_usage'].items())[:10]),
            'productivity_score': self.detected_patterns['productivity_score'],
            'distraction_score': self.detected_patterns['distraction_score']
        }
        
        prompt = f"""Baseado nestes dados de observação, dê 3 sugestões práticas de produtividade:

{json.dumps(analysis_data, indent=2)}

Sugestões:"""
        
        suggestions = self.ai.generate_response(prompt, mode="observer")
        
        print(f"{Fore.GREEN}{suggestions}{Style.RESET_ALL}\n")
        self.speaker.speak("Tenho algumas sugestões de produtividade para você!")
        
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    async def generate_activity_report(self):
        """Gera relatório de atividades"""
        print(f"\n{Fore.CYAN}📊 Gerando relatório...{Style.RESET_ALL}\n")
        
        if len(self.observation_history) == 0:
            print(f"{Fore.YELLOW}Nenhuma observação registrada ainda!{Style.RESET_ALL}\n")
            input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
            return
        
        # Cria relatório
        report = self._create_activity_report()
        
        # Mostra
        print(report)
        
        # Salva
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"memory/reports/activity_report_{timestamp}.txt"
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n{Fore.GREEN}💾 Relatório salvo: {report_path}{Style.RESET_ALL}\n")
        
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    def _create_activity_report(self) -> str:
        """Cria relatório textual"""
        report = f"""
{'='*60}
RELATÓRIO DE ATIVIDADES - MIRAI OBSERVER
{'='*60}

Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Total de Observações: {len(self.observation_history)}

RESUMO GERAL
{'='*60}

Apps Mais Usados:
"""
        
        # Apps
        sorted_apps = sorted(
            self.detected_patterns['app_usage'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for i, (app, count) in enumerate(sorted_apps[:10], 1):
            report += f"{i}. {app}: {count} vezes\n"
        
        # Scores
        report += f"""
Scores de Produtividade:
- Produtividade: {self.detected_patterns['productivity_score']:.1f}
- Distração: {self.detected_patterns['distraction_score']:.1f}
"""
        
        # Atividades por categoria
        categories_count = {}
        for obs in self.observation_history:
            cat = obs.get('activity_category', 'unknown')
            categories_count[cat] = categories_count.get(cat, 0) + 1
        
        report += "\nAtividades por Categoria:\n"
        for cat, count in sorted(categories_count.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(self.observation_history)) * 100
            report += f"- {cat}: {count} ({percentage:.1f}%)\n"
        
        report += f"\n{'='*60}\n"
        report += "Gerado por Mirai Observer V2\n"
        
        return report
    
    def _show_session_insights(self):
        """Mostra insights da sessão"""
        if len(self.observation_history) == 0:
            return
        
        # Categorias
        categories_count = {}
        for obs in self.observation_history:
            cat = obs.get('activity_category', 'unknown')
            categories_count[cat] = categories_count.get(cat, 0) + 1
        
        # Categoria dominante
        dominant_category = max(categories_count.items(), key=lambda x: x[1])[0]
        
        print(f"Categoria dominante: {Fore.CYAN}{dominant_category}{Style.RESET_ALL}")
        
        # Score médio
        if self.observation_history:
            avg_productivity = sum(obs.get('productivity_indicator', 0) for obs in self.observation_history) / len(self.observation_history)
            
            if avg_productivity > 0.3:
                print(f"Avaliação: {Fore.GREEN}Sessão produtiva! 💚{Style.RESET_ALL}")
            elif avg_productivity < -0.3:
                print(f"Avaliação: {Fore.YELLOW}Sessão de lazer 🎮{Style.RESET_ALL}")
            else:
                print(f"Avaliação: {Fore.CYAN}Sessão balanceada ⚖️{Style.RESET_ALL}")
    
    async def configure_observation(self):
        """Configura parâmetros"""
        print(f"\n{Fore.CYAN}⚙️  CONFIGURAÇÃO{Style.RESET_ALL}\n")
        
        print(f"Intervalo atual: {self.observation_interval}s")
        
        try:
            new_interval = input(f"\nNovo intervalo (10-300s): ")
            
            if new_interval:
                interval = int(new_interval)
                if 10 <= interval <= 300:
                    self.observation_interval = interval
                    print(f"{Fore.GREEN}✓ Intervalo atualizado!{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Valor inválido!{Style.RESET_ALL}")
        except:
            print(f"{Fore.RED}Entrada inválida!{Style.RESET_ALL}")
        
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    def _save_observation_data(self):
        """Salva dados de observação"""
        data_file = Path("memory/observation_data.json")
        data_file.parent.mkdir(exist_ok=True)
        
        try:
            # Carrega dados anteriores
            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8') as f:
                    all_data = json.load(f)
            else:
                all_data = {'sessions': []}
            
            # Adiciona sessão atual
            session_data = {
                'timestamp': datetime.now().isoformat(),
                'total_observations': len(self.observation_history),
                'patterns': self.detected_patterns,
                'observations_sample': [
                    {k: v for k, v in obs.items() if k != 'text_content'}  # Remove texto para economizar espaço
                    for obs in list(self.observation_history)[-10:]
                ]
            }
            
            all_data['sessions'].append(session_data)
            
            # Mantém últimas 20 sessões
            all_data['sessions'] = all_data['sessions'][-20:]
            
            # Salva
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=2, ensure_ascii=False)
            
            print(f"  ✓ Dados salvos")
        except Exception as e:
            print(f"  ⚠️  Erro ao salvar: {e}")-e 

# Alias para compatibilidade com menu.py
ObserverMode = ObserverModeV2