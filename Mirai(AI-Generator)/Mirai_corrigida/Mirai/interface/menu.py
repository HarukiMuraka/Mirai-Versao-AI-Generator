from colorama import Fore, Style
import asyncio
import platform


class MenuPrincipal:
    """Menu Principal"""
    
    def __init__(self, mirai_instance):
        self.mirai = mirai_instance
        self.running = True
        self.system = platform.system()
    
    def print_header(self):
        """Cabeçalho do menu"""
        print(f"\n{Fore.MAGENTA}{'='*70}")
        print(f"{Fore.MAGENTA}║                    🌸 MIRAI v2.0 🌸                              ║")
        print(f"{Fore.MAGENTA}║              Assistente Virtual VTuber Profissional             ║")
        print(f"{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
    
    def print_status(self):
        """Status dos sistemas"""
        print(f"\n{Fore.CYAN}📊 STATUS DOS SISTEMAS:{Style.RESET_ALL}")
        
        # IA
        ia_status = "🟢 Gemini" if self.mirai.ai.use_gemini else ("🟢 Ollama" if self.mirai.ai.use_ollama else "🟡 Offline")
        print(f"  IA: {ia_status}")
        
        # Voz
        voz_status = "🟢 Ativa" if self.mirai.speaker.enabled else "🔴 Desativada"
        print(f"  Voz: {voz_status}")
        
        # VTuber
        vtuber_status = "🟢 Ativo" if (self.mirai.vtuber and self.mirai.vtuber.is_active) else "🟡 Desativado"
        print(f"  VTuber: {vtuber_status}")
        
        # Sistema
        print(f"  Sistema: {self.system}")
        
        print()
    
    def print_menu(self):
        """Menu principal"""
        self.print_header()
        self.print_status()
        
        print(f"{Fore.YELLOW}╔════════════════════════════════════════════════════════════════╗")
        print(f"{Fore.YELLOW}║                        MODOS PRINCIPAIS                        ║")
        print(f"{Fore.YELLOW}╠════════════════════════════════════════════════════════════════╣")
        print(f"{Fore.GREEN}║ 1 ▶ 💬 Conversa Inteligente                                   ║")
        print(f"{Fore.GREEN}║     └─ Texto, Voz, Mista ou Autônoma                          ║")
        print(f"{Fore.GREEN}║                                                                ║")
        print(f"{Fore.GREEN}║ 2 ▶ 🤖 Assistente Profissional                                ║")
        print(f"{Fore.GREEN}║     └─ Pesquisa Web, Criar Conteúdo, Análise de Tela          ║")
        print(f"{Fore.GREEN}║                                                                ║")
        print(f"{Fore.GREEN}║ 3 ▶ 🎤 Mãos Livres + Autônomo                                  ║")
        print(f"{Fore.GREEN}║     └─ Comandos por Voz, Mirai toma Iniciativa                ║")
        print(f"{Fore.GREEN}║                                                                ║")
        print(f"{Fore.CYAN}║ 4 ▶ 🎮 Modo Gamer                                              ║")
        print(f"{Fore.CYAN}║     └─ RetroArch, Chat de Live                                 ║")
        print(f"{Fore.CYAN}║                                                                ║")
        print(f"{Fore.CYAN}║ 5 ▶ 📸 Observação & Análise                                    ║")
        print(f"{Fore.CYAN}║     └─ Captura e Análise de Tela                               ║")
        print(f"{Fore.CYAN}║                                                                ║")
        print(f"{Fore.CYAN}║ 6 ▶ 🎥 Modo Streamer                                           ║")
        print(f"{Fore.CYAN}║     └─ YouTube, Twitch, Chat Simulado                          ║")
        print(f"{Fore.YELLOW}╠════════════════════════════════════════════════════════════════╣")
        print(f"{Fore.YELLOW}║                       CONFIGURAÇÕES                            ║")
        print(f"{Fore.YELLOW}╠════════════════════════════════════════════════════════════════╣")
        print(f"{Fore.MAGENTA}║ 7 ▶ ⚙️  Sistema & Configurações                               ║")
        print(f"{Fore.MAGENTA}║ 8 ▶ 🎭 VTuber & Avatar                                         ║")
        print(f"{Fore.MAGENTA}║ 9 ▶ 💾 Memória & Personalidade                                ║")
        print(f"{Fore.YELLOW}╠════════════════════════════════════════════════════════════════╣")
        print(f"{Fore.YELLOW}║                     FUNÇÕES DE IA EXTRAS                       ║")
        print(f"{Fore.YELLOW}╠════════════════════════════════════════════════════════════════╣")
        print(f"{Fore.GREEN}║ F ▶ ✨ Funções de IA                                           ║")
        print(f"{Fore.GREEN}║     └─ Texto, Imagem, Voz, Tradução, Resumo                   ║")
        print(f"{Fore.YELLOW}╠════════════════════════════════════════════════════════════════╣")
        print(f"{Fore.MAGENTA}║ A ▶ 📖 Sobre a Mirai & Ajuda                                   ║")
        print(f"{Fore.RED}║ 0 ▶ 🚪 Sair                                                     ║")
        print(f"{Fore.YELLOW}╚════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
    
    async def show(self):
        """Mostra e gerencia o menu"""
        # Importa modos
        from modes.conversation import ConversationModeImproved
        from modes.assistant import AssistantModePro
        from modes.voice_active import VoiceActivePro
        from modes.gamer import GamerMode
        from modes.observer import ObserverMode
        
        # Importa streamer se disponível
        try:
            from modes.streamer import StreamerMode
            STREAMER_OK = True
        except:
            STREAMER_OK = False
        
        while self.running:
            self.print_menu()
            
            choice = input(f"{Fore.GREEN}➤ Escolha uma opção: {Style.RESET_ALL}").strip().lower()
            
            # Modos principais
            if choice == "1":
                mode = ConversationModeImproved(self.mirai)
                await mode.enter()
                await mode.exit()
            
            elif choice == "2":
                mode = AssistantModePro(self.mirai)
                await mode.enter()
                await mode.exit()
            
            elif choice == "3":
                mode = VoiceActivePro(self.mirai)
                await mode.enter()
                await mode.exit()
            
            elif choice == "4":
                mode = GamerMode(self.mirai)
                await mode.enter()
                await mode.exit()
            
            elif choice == "5":
                mode = ObserverMode(self.mirai)
                await mode.enter()
                await mode.exit()
            
            elif choice == "6":
                if STREAMER_OK:
                    mode = StreamerMode(self.mirai)
                    await mode.enter()
                    await mode.exit()
                else:
                    print(f"{Fore.RED}❌ Modo Streamer não disponível{Style.RESET_ALL}")
                    input(f"{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
            
            # Configurações
            elif choice == "7":
                await self.menu_system_config()
            
            elif choice == "8":
                await self.menu_vtuber()
            
            elif choice == "9":
                await self.menu_memory()
            
            # Funções de IA
            elif choice == "f":
                await self.menu_ai_functions()

            # Ajuda
            elif choice == "a":
                self.show_about()
            
            # Sair
            elif choice == "0":
                self.running = False
                break
            
            else:
                print(f"{Fore.RED}❌ Opção inválida! Tente novamente.{Style.RESET_ALL}")
                await asyncio.sleep(1)
    
    async def menu_system_config(self):
        """Menu de configurações do sistema"""
        while True:
            print(f"\n{Fore.CYAN}{'='*70}")
            print(f"{Fore.MAGENTA}⚙️  SISTEMA & CONFIGURAÇÕES")
            print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
            
            print("1. 🤖 Configurar IA (Gemini/Ollama)")
            print("2. 🔊 Configurar Voz")
            print("3. 🎤 Testar Microfone")
            print("4. 🧪 Diagnóstico Completo")
            print("5. 🗑️  Limpar Memória Temporária")
            print("6. 📊 Ver Estatísticas")
            print("0. ⬅️  Voltar")
            
            choice = input(f"\n{Fore.GREEN}➤ Opção: {Style.RESET_ALL}")
            
            if choice == "1":
                await self.config_ia()
            elif choice == "2":
                await self.config_voice()
            elif choice == "3":
                await self.test_microphone()
            elif choice == "4":
                await self.run_diagnostics()
            elif choice == "5":
                self.clear_memory()
            elif choice == "6":
                self.show_stats()
            elif choice == "0":
                break
    
    async def menu_vtuber(self):
        """Menu VTuber"""
        while True:
            print(f"\n{Fore.CYAN}{'='*70}")
            print(f"{Fore.MAGENTA}🎭 VTUBER & AVATAR")
            print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
            
            status = "🟢 Ativo" if (self.mirai.vtuber and self.mirai.vtuber.is_active) else "🔴 Inativo"
            print(f"Status: {status}\n")
            
            print("1. 🔄 Recarregar VTuber")
            print("2. 🎭 Testar Expressões")
            print("3. 💬 Testar Lip Sync")
            print("4. ⚙️  Configurações VTuber")
            print("0. ⬅️  Voltar")
            
            choice = input(f"\n{Fore.GREEN}➤ Opção: {Style.RESET_ALL}")
            
            if choice == "1":
                await self.reload_vtuber()
            elif choice == "2":
                await self.test_expressions()
            elif choice == "3":
                await self.test_lip_sync()
            elif choice == "4":
                await self.config_vtuber()
            elif choice == "0":
                break
    
    async def menu_memory(self):
        """Menu de memória"""
        while True:
            print(f"\n{Fore.CYAN}{'='*70}")
            print(f"{Fore.MAGENTA}💾 MEMÓRIA & PERSONALIDADE")
            print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
            
            print("1. 📖 Ver Memória Permanente")
            print("2. ✏️  Editar Personalidade")
            print("3. 👤 Gerenciar Apelidos")
            print("4. 📝 Adicionar Nota sobre Você")
            print("5. 🗑️  Limpar Histórico de Conversas")
            print("6. 💾 Salvar Contexto Atual")
            print("0. ⬅️  Voltar")
            
            choice = input(f"\n{Fore.GREEN}➤ Opção: {Style.RESET_ALL}")
            
            if choice == "1":
                self.show_permanent_memory()
            elif choice == "2":
                self.edit_personality()
            elif choice == "3":
                self.manage_nicknames()
            elif choice == "4":
                self.add_user_note()
            elif choice == "5":
                self.clear_conversation_history()
            elif choice == "6":
                self.save_current_context()
            elif choice == "0":
                break
    
    async def config_ia(self):
        """Configuração da IA"""
        print(f"\n{Fore.CYAN}🤖 CONFIGURAÇÃO DA IA{Style.RESET_ALL}\n")
        
        print(f"Status atual:")
        if self.mirai.ai.use_gemini:
            print(f"  🟢 Gemini ativo")
        elif self.mirai.ai.use_ollama:
            print(f"  🟢 Ollama ativo (modelo: {self.mirai.ai.ollama_model})")
        else:
            print(f"  🟡 Modo offline")
        
        print(f"\n{Fore.YELLOW}Opções:{Style.RESET_ALL}")
        print("1. Testar Gemini")
        print("2. Testar Ollama")
        print("3. Reativar IA")
        print("0. Voltar")
        
        choice = input(f"\n{Fore.GREEN}➤ Opção: {Style.RESET_ALL}")
        
        if choice == "1":
            await self.test_gemini()
        elif choice == "2":
            await self.test_ollama()
        elif choice == "3":
            await self.mirai.ai.initialize()
    
    async def test_gemini(self):
        """Testa Gemini"""
        print(f"\n{Fore.CYAN}Testando Gemini...{Style.RESET_ALL}")
        
        if not self.mirai.ai.gemini_api_key or self.mirai.ai.gemini_api_key == "SUA_CHAVE_AQUI":
            print(f"{Fore.RED}❌ Chave Gemini não configurada!{Style.RESET_ALL}")
            print(f"\nConfigure em: config/gemini_key.txt")
        else:
            if self.mirai.ai._test_gemini():
                print(f"{Fore.GREEN}✓ Gemini funcionando!{Style.RESET_ALL}")
                self.mirai.ai.use_gemini = True
                self.mirai.ai.use_ollama = False
            else:
                print(f"{Fore.RED}❌ Gemini não respondeu{Style.RESET_ALL}")
        
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    async def test_ollama(self):
        """Testa Ollama"""
        print(f"\n{Fore.CYAN}Testando Ollama...{Style.RESET_ALL}")
        
        import requests
        
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                
                if models:
                    print(f"{Fore.GREEN}✓ Ollama ativo!{Style.RESET_ALL}\n")
                    print("Modelos disponíveis:")
                    for i, model in enumerate(models, 1):
                        print(f"  {i}. {model.get('name', 'unknown')}")
                    
                    self.mirai.ai.use_ollama = True
                    self.mirai.ai.use_gemini = False
                else:
                    print(f"{Fore.YELLOW}⚠️  Ollama ativo mas sem modelos{Style.RESET_ALL}")
                    print("Execute: ollama pull llama3")
            else:
                print(f"{Fore.RED}❌ Ollama não respondeu{Style.RESET_ALL}")
        
        except:
            print(f"{Fore.RED}❌ Ollama offline{Style.RESET_ALL}")
            print("\nInicie com: ollama serve")
        
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    async def config_voice(self):
        """Configuração de voz"""
        print(f"\n{Fore.CYAN}🔊 CONFIGURAÇÃO DE VOZ{Style.RESET_ALL}\n")
        
        print(f"Status: {'🟢 Ativa' if self.mirai.speaker.enabled else '🔴 Desativada'}")
        print(f"Volume: {self.mirai.speaker.voice_volume:.1f}")
        
        print(f"\n{Fore.YELLOW}Opções:{Style.RESET_ALL}")
        print("1. Ajustar volume")
        print("2. Testar voz")
        print("3. Ativar/Desativar")
        print("0. Voltar")
        
        choice = input(f"\n{Fore.GREEN}➤ Opção: {Style.RESET_ALL}")
        
        if choice == "1":
            try:
                volume = float(input("Novo volume (0.0-1.0): "))
                self.mirai.speaker.set_volume(volume)
                print(f"{Fore.GREEN}✓ Volume ajustado!{Style.RESET_ALL}")
            except:
                print(f"{Fore.RED}❌ Valor inválido{Style.RESET_ALL}")
        
        elif choice == "2":
            print(f"\n{Fore.CYAN}Testando voz...{Style.RESET_ALL}")
            self.mirai.speaker.speak("Sistema de voz funcionando perfeitamente! Yatta!")
        
        elif choice == "3":
            self.mirai.speaker.enabled = not self.mirai.speaker.enabled
            status = "ativada" if self.mirai.speaker.enabled else "desativada"
            print(f"{Fore.GREEN}✓ Voz {status}!{Style.RESET_ALL}")
        
        if choice != "0":
            input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    async def test_microphone(self):
        """Testa microfone"""
        print(f"\n{Fore.CYAN}🎤 TESTE DE MICROFONE{Style.RESET_ALL}\n")
        
        from mirai.perception.voice_listener import VoiceListener
        
        voice = VoiceListener()
        
        if not voice.initialize():
            print(f"{Fore.RED}❌ Microfone não disponível!{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}✓ Microfone detectado!{Style.RESET_ALL}\n")
        print(f"{Fore.YELLOW}Fale algo para testar...{Style.RESET_ALL}\n")
        
        text = voice.listen_once()
        
        if text:
            print(f"\n{Fore.GREEN}✓ Reconhecido: {text}{Style.RESET_ALL}")
            self.mirai.speaker.speak(f"Ouvi você dizer: {text}")
        else:
            print(f"\n{Fore.RED}❌ Nada foi reconhecido{Style.RESET_ALL}")
        
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    async def run_diagnostics(self):
        """Diagnóstico completo"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.MAGENTA}🧪 DIAGNÓSTICO COMPLETO DO SISTEMA")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
        
        # IA
        print(f"{Fore.YELLOW}[1/5] Testando IA...{Style.RESET_ALL}")
        if self.mirai.ai.use_gemini:
            print(f"  🟢 Gemini ativo")
        elif self.mirai.ai.use_ollama:
            print(f"  🟢 Ollama ativo")
        else:
            print(f"  🟡 Modo offline")
        
        # Voz
        print(f"\n{Fore.YELLOW}[2/5] Testando voz...{Style.RESET_ALL}")
        if self.mirai.speaker.enabled:
            print(f"  🟢 Voz ativa")
        else:
            print(f"  🔴 Voz desativada")
        
        # Microfone
        print(f"\n{Fore.YELLOW}[3/5] Testando microfone...{Style.RESET_ALL}")
        from mirai.perception.voice_listener import VoiceListener
        voice = VoiceListener()
        if voice.initialize():
            print(f"  🟢 Microfone OK")
        else:
            print(f"  🔴 Microfone não disponível")
        
        # VTuber
        print(f"\n{Fore.YELLOW}[4/5] Testando VTuber...{Style.RESET_ALL}")
        if self.mirai.vtuber and self.mirai.vtuber.is_active:
            print(f"  🟢 VTuber ativo")
        else:
            print(f"  🟡 VTuber desativado")
        
        # Dependências
        print(f"\n{Fore.YELLOW}[5/5] Verificando dependências...{Style.RESET_ALL}")
        
        deps = {
            'requests': 'requests',
            'beautifulsoup4': 'bs4',
            'pillow': 'PIL',
            'pyautogui': 'pyautogui'
        }
        
        for name, import_name in deps.items():
            try:
                __import__(import_name)
                print(f"  🟢 {name}")
            except:
                print(f"  🔴 {name} (ausente)")
        
        print(f"\n{Fore.GREEN}{'='*70}")
        print("DIAGNÓSTICO COMPLETO")
        print(f"{'='*70}{Style.RESET_ALL}")
        
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    def clear_memory(self):
        """Limpa memória temporária"""
        print(f"\n{Fore.CYAN}🗑️  LIMPAR MEMÓRIA{Style.RESET_ALL}\n")
        
        confirm = input("Limpar histórico de conversas? (s/n): ")
        
        if confirm.lower() == 's':
            self.mirai.context.clear_context()
            if hasattr(self.mirai.ai, 'conversation_history'):
                self.mirai.ai.conversation_history = []
            
            print(f"{Fore.GREEN}✓ Memória limpa!{Style.RESET_ALL}")
            self.mirai.speaker.speak("Memória limpa!")
        
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    def show_stats(self):
        """Mostra estatísticas"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.MAGENTA}📊 ESTATÍSTICAS DO SISTEMA")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
        
        duration = self.mirai.context.get_session_duration()
        messages = len(self.mirai.context.conversation_history)
        
        print(f"{Fore.YELLOW}Sessão Atual:{Style.RESET_ALL}")
        print(f"  Duração: {duration // 60}m {duration % 60}s")
        print(f"  Mensagens: {messages}")
        print(f"  Estado: {self.mirai.state.get_state().value}")
        
        print(f"\n{Fore.YELLOW}IA:{Style.RESET_ALL}")
        if self.mirai.ai.use_gemini:
            print(f"  Modo: Gemini")
        elif self.mirai.ai.use_ollama:
            print(f"  Modo: Ollama")
            print(f"  Modelo: {self.mirai.ai.ollama_model}")
        else:
            print(f"  Modo: Offline")
        
        print(f"\n{Fore.YELLOW}Voz:{Style.RESET_ALL}")
        print(f"  Status: {'Ativa' if self.mirai.speaker.enabled else 'Desativada'}")
        print(f"  Volume: {self.mirai.speaker.voice_volume:.1f}")
        
        print(f"\n{Fore.YELLOW}VTuber:{Style.RESET_ALL}")
        if self.mirai.vtuber and self.mirai.vtuber.is_active:
            print(f"  Status: Ativo")
        else:
            print(f"  Status: Desativado")
        
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    async def reload_vtuber(self):
        """Recarrega VTuber"""
        print(f"\n{Fore.CYAN}Recarregando VTuber...{Style.RESET_ALL}")
        
        if self.mirai.vtuber:
            await self.mirai.vtuber.stop()
        
        from mirai.vtuber.vrm_engine import VRMEngine
        self.mirai.vtuber = VRMEngine()
        await self.mirai.vtuber.initialize()
        
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    async def test_expressions(self):
        """Testa expressões"""
        if not self.mirai.vtuber or not self.mirai.vtuber.is_active:
            print(f"{Fore.RED}❌ VTuber não está ativo!{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}Testando expressões...{Style.RESET_ALL}\n")
        
        expressions = ["happy", "sad", "angry", "surprised", "neutral"]
        
        for expr in expressions:
            print(f"  {expr}...")
            await self.mirai.vtuber.set_expression(expr)
            await asyncio.sleep(2)
        
        print(f"\n{Fore.GREEN}✓ Teste completo!{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    async def test_lip_sync(self):
        """Testa lip sync"""
        if not self.mirai.vtuber or not self.mirai.vtuber.is_active:
            print(f"{Fore.RED}❌ VTuber não está ativo!{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}Testando lip sync...{Style.RESET_ALL}\n")
        
        text = "Testando sincronização labial da Mirai!"
        
        await self.mirai.vtuber.start_talking()
        self.mirai.speaker.speak(text)
        await self.mirai.vtuber.stop_talking()
        
        print(f"\n{Fore.GREEN}✓ Teste completo!{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    async def config_vtuber(self):
        """Configurações VTuber"""
        print(f"\n{Fore.CYAN}⚙️  CONFIGURAÇÕES VTUBER{Style.RESET_ALL}\n")
        print("Em desenvolvimento...")
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    def show_permanent_memory(self):
        """Mostra memória permanente"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.MAGENTA}📖 MEMÓRIA PERMANENTE")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
        
        mem = self.mirai.ai.permanent_memory
        
        print(f"{Fore.YELLOW}Personalidade:{Style.RESET_ALL}")
        for key, value in mem.get('personalidade', {}).items():
            print(f"  {key}: {value}")
        
        print(f"\n{Fore.YELLOW}Seus Apelidos:{Style.RESET_ALL}")
        apelidos = mem.get('usuario', {}).get('apelidos', [])
        if apelidos:
            for apelido in apelidos:
                print(f"  • {apelido}")
        else:
            print("  (nenhum)")
        
        print(f"\n{Fore.YELLOW}Notas sobre Você:{Style.RESET_ALL}")
        notas = mem.get('usuario', {}).get('notas', [])
        if notas:
            for nota in notas[:5]:
                print(f"  • {nota.get('conteudo', '')}")
        else:
            print("  (nenhuma)")
        
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    def edit_personality(self):
        """Edita personalidade"""
        print(f"\n{Fore.CYAN}Em desenvolvimento...{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    def manage_nicknames(self):
        """Gerencia apelidos"""
        print(f"\n{Fore.CYAN}👤 GERENCIAR APELIDOS{Style.RESET_ALL}\n")
        
        apelidos = self.mirai.ai.permanent_memory.get('usuario', {}).get('apelidos', [])
        
        print("Apelidos atuais:")
        if apelidos:
            for i, apelido in enumerate(apelidos, 1):
                print(f"  {i}. {apelido}")
        else:
            print("  (nenhum)")
        
        print(f"\n{Fore.YELLOW}Opções:{Style.RESET_ALL}")
        print("1. Adicionar apelido")
        print("2. Remover apelido")
        print("0. Voltar")
        
        choice = input(f"\n{Fore.GREEN}➤ Opção: {Style.RESET_ALL}")
        
        if choice == "1":
            novo = input("Novo apelido: ")
            if novo:
                if 'usuario' not in self.mirai.ai.permanent_memory:
                    self.mirai.ai.permanent_memory['usuario'] = {}
                if 'apelidos' not in self.mirai.ai.permanent_memory['usuario']:
                    self.mirai.ai.permanent_memory['usuario']['apelidos'] = []
                
                self.mirai.ai.permanent_memory['usuario']['apelidos'].append(novo)
                self.mirai.ai.save_permanent_memory()
                
                print(f"{Fore.GREEN}✓ Apelido adicionado!{Style.RESET_ALL}")
        
        elif choice == "2":
            if apelidos:
                try:
                    idx = int(input("Número do apelido: ")) - 1
                    if 0 <= idx < len(apelidos):
                        removed = apelidos.pop(idx)
                        self.mirai.ai.save_permanent_memory()
                        print(f"{Fore.GREEN}✓ '{removed}' removido!{Style.RESET_ALL}")
                except:
                    print(f"{Fore.RED}❌ Inválido{Style.RESET_ALL}")
    
    def add_user_note(self):
        """Adiciona nota sobre o usuário"""
        print(f"\n{Fore.CYAN}📝 ADICIONAR NOTA{Style.RESET_ALL}\n")
        
        nota = input("Escreva uma nota sobre você: ")
        
        if nota:
            self.mirai.ai.add_user_note(nota)
            print(f"{Fore.GREEN}✓ Nota salva!{Style.RESET_ALL}")
        
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    def clear_conversation_history(self):
        """Limpa histórico de conversas"""
        self.clear_memory()
    
    def save_current_context(self):
        """Salva contexto atual"""
        print(f"\n{Fore.CYAN}💾 SALVAR CONTEXTO{Style.RESET_ALL}\n")
        
        self.mirai.context.save_preferences_to_permanent()
        
        print(f"{Fore.GREEN}✓ Contexto salvo!{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
    
    async def menu_ai_functions(self):
        """Menu de Funções de IA Extras (Texto, Imagem, Voz)"""
        try:
            from features.ai_functions import AIFunctions
            funcs = AIFunctions(self.mirai.ai)
        except ImportError:
            print(f"\n{Fore.RED}❌ features/ai_functions.py não encontrado!")
            print(f"   Copie o arquivo para C:\\Mirai\\features\\ai_functions.py{Style.RESET_ALL}")
            input(f"{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")
            return

        while True:
            status = funcs.status()
            tts_ok  = f"{Fore.GREEN}✓ Disponível{Style.RESET_ALL}" if status["tts"] else f"{Fore.RED}✗ Instale: pip install edge-tts{Style.RESET_ALL}"

            print(f"\n{Fore.MAGENTA}{'='*60}")
            print(f"✨ FUNÇÕES DE IA EXTRAS")
            print(f"{'='*60}{Style.RESET_ALL}\n")
            print(f"  TTS (voz): {tts_ok}\n")
            print(f"{Fore.YELLOW}── TEXTO ─────────────────────────────{Style.RESET_ALL}")
            print(f"  1 ▶ Resumir um texto")
            print(f"  2 ▶ Traduzir um texto")
            print(f"  3 ▶ Criar história")
            print(f"  4 ▶ Melhorar meu texto")
            print(f"  5 ▶ Analisar sentimento")
            print(f"{Fore.CYAN}── IMAGEM ────────────────────────────{Style.RESET_ALL}")
            print(f"  6 ▶ Gerar imagem")
            print(f"  7 ▶ Gerar avatar anime")
            print(f"{Fore.GREEN}── VOZ ───────────────────────────────{Style.RESET_ALL}")
            print(f"  8 ▶ Mirai falar um texto (TTS)")
            print(f"  0 ▶ Voltar\n")

            choice = input(f"{Fore.GREEN}➤ Opção: {Style.RESET_ALL}").strip()

            if choice == "0":
                break

            elif choice == "1":
                print(f"\n{Fore.CYAN}Cole o texto que quer resumir (Enter em branco para terminar):{Style.RESET_ALL}")
                linhas = []
                while True:
                    linha = input()
                    if linha == "":
                        break
                    linhas.append(linha)
                texto = " ".join(linhas)
                if texto.strip():
                    print(f"\n{Fore.YELLOW}Resumindo...{Style.RESET_ALL}")
                    resultado = await funcs.resumir(texto)
                    print(f"\n{Fore.GREEN}📝 Resumo:{Style.RESET_ALL}\n{resultado}")
                else:
                    print(f"{Fore.RED}Nenhum texto informado.{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")

            elif choice == "2":
                texto = input(f"\n{Fore.CYAN}Texto para traduzir: {Style.RESET_ALL}")
                idioma = input(f"{Fore.CYAN}Para qual idioma? (padrão: inglês): {Style.RESET_ALL}").strip() or "inglês"
                if texto.strip():
                    print(f"\n{Fore.YELLOW}Traduzindo...{Style.RESET_ALL}")
                    resultado = await funcs.traduzir(texto, idioma)
                    print(f"\n{Fore.GREEN}🌐 Tradução ({idioma}):{Style.RESET_ALL}\n{resultado}")
                input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")

            elif choice == "3":
                tema   = input(f"\n{Fore.CYAN}Tema da história: {Style.RESET_ALL}")
                print(f"{Fore.CYAN}Estilo (aventura/romance/mistério/ficção científica/terror): {Style.RESET_ALL}", end="")
                estilo = input().strip() or "aventura"
                if tema.strip():
                    print(f"\n{Fore.YELLOW}Criando história...{Style.RESET_ALL}")
                    resultado = await funcs.texto.criar_historia(tema, estilo)
                    print(f"\n{Fore.GREEN}📖 História:{Style.RESET_ALL}\n{resultado}")
                input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")

            elif choice == "4":
                print(f"\n{Fore.CYAN}Cole seu texto (Enter em branco para terminar):{Style.RESET_ALL}")
                linhas = []
                while True:
                    linha = input()
                    if linha == "":
                        break
                    linhas.append(linha)
                texto = " ".join(linhas)
                if texto.strip():
                    print(f"\n{Fore.YELLOW}Melhorando texto...{Style.RESET_ALL}")
                    resultado = await funcs.texto.melhorar_texto(texto)
                    print(f"\n{Fore.GREEN}✏️  Texto melhorado:{Style.RESET_ALL}\n{resultado}")
                input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")

            elif choice == "5":
                texto = input(f"\n{Fore.CYAN}Texto para analisar: {Style.RESET_ALL}")
                if texto.strip():
                    print(f"\n{Fore.YELLOW}Analisando sentimento...{Style.RESET_ALL}")
                    resultado = await funcs.texto.analisar_sentimento(texto)
                    print(f"\n{Fore.GREEN}💭 Análise:{Style.RESET_ALL}")
                    print(f"  Sentimento: {resultado.get('sentimento','?').upper()}")
                    print(f"  Intensidade: {resultado.get('intensidade','?')}")
                    print(f"  Emoção: {resultado.get('emocao','?')}")
                input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")

            elif choice == "6":
                descricao = input(f"\n{Fore.CYAN}Descreva a imagem que quer gerar: {Style.RESET_ALL}")
                print(f"{Fore.CYAN}Estilo (anime/realista/pixel/cyberpunk/fantasia/sketch/pintura/cartoon ou Enter=sem estilo): {Style.RESET_ALL}", end="")
                estilo = input().strip()
                if descricao.strip():
                    print(f"\n{Fore.YELLOW}Gerando imagem... (pode levar ~10 segundos){Style.RESET_ALL}")
                    resultado = await funcs.gerar_imagem(descricao, estilo)
                    if resultado["sucesso"]:
                        print(f"\n{Fore.GREEN}🎨 Imagem gerada!")
                        print(f"  Arquivo: {resultado['arquivo']}")
                        print(f"  URL: {resultado['url']}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}❌ Falha ao gerar. Verifique sua internet.{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")

            elif choice == "7":
                descricao = input(f"\n{Fore.CYAN}Descreva o personagem (ex: garota com cabelo azul, olhos verdes): {Style.RESET_ALL}")
                if descricao.strip():
                    print(f"\n{Fore.YELLOW}Gerando avatar anime...{Style.RESET_ALL}")
                    resultado = await funcs.imagem.gerar_avatar(descricao)
                    if resultado["sucesso"]:
                        print(f"\n{Fore.GREEN}🎨 Avatar gerado!")
                        print(f"  Arquivo: {resultado['arquivo']}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}❌ Falha ao gerar. Verifique sua internet.{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")

            elif choice == "8":
                texto = input(f"\n{Fore.CYAN}Texto para a Mirai falar: {Style.RESET_ALL}")
                if texto.strip():
                    if not status["tts"]:
                        print(f"{Fore.RED}❌ edge-tts não instalado. Execute: pip install edge-tts pygame{Style.RESET_ALL}")
                    else:
                        print(f"\n{Fore.YELLOW}Convertendo texto em voz...{Style.RESET_ALL}")
                        resultado = await funcs.falar(texto)
                        if resultado["sucesso"]:
                            print(f"{Fore.GREEN}✓ Áudio gerado e tocado!{Style.RESET_ALL}")
                            print(f"  Arquivo: {resultado['arquivo']}")
                        else:
                            print(f"{Fore.RED}❌ Erro: {resultado.get('erro','?')}{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")

            else:
                print(f"{Fore.RED}Opção inválida.{Style.RESET_ALL}")

    def show_about(self):
        """Sobre a Mirai"""
        print(f"\n{Fore.MAGENTA}{'='*70}")
        print(f"🌸 SOBRE A MIRAI v2.0")
        print(f"{'='*70}{Style.RESET_ALL}\n")
        
        print(f"{Fore.CYAN}Nome:{Style.RESET_ALL} Mirai")
        print(f"{Fore.CYAN}Versão:{Style.RESET_ALL} 2.0.0 Professional")
        print(f"{Fore.CYAN}Tipo:{Style.RESET_ALL} Assistente Virtual VTuber")
        
        print(f"\n{Fore.YELLOW}✨ Funcionalidades v2.0:{Style.RESET_ALL}")
        print("  ✅ Pesquisa web funcional")
        print("  ✅ Criação de conteúdo (textos, código)")
        print("  ✅ Análise de tela com OCR")
        print("  ✅ Abertura de apps multiplataforma")
        print("  ✅ Modo autônomo integrado")
        print("  ✅ Comandos de voz funcionais")
        print("  ✅ Conversa inteligente")
        
        print(f"\n{Fore.YELLOW}💡 Dicas Rápidas:{Style.RESET_ALL}")
        print("  • Modo 2: 'abrir chrome', 'pesquisar python'")
        print("  • Modo 3: Fale naturalmente sem dizer 'Mirai'")
        print("  • Modo autônomo: Mirai toma iniciativa!")
        
        print(f"\n{Fore.CYAN}Desenvolvido com 💕 pela comunidade{Style.RESET_ALL}")
        print(f"{Fore.CYAN}GitHub: HarukiMuraka/Mirai{Style.RESET_ALL}")
        
        input(f"\n{Fore.CYAN}Pressione Enter...{Style.RESET_ALL}")

# Alias para compatibilidade com main.py
MainMenu = MenuPrincipal