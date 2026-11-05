import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*70)
print("🌸 TESTE COMPLETO DO SISTEMA MIRAI")
print("="*70 + "\n")

# TESTE 1: Memória
print("1️⃣ TESTANDO SISTEMA DE MEMÓRIA...")
try:
    from memory.sistema_memoria import MemoriaCompleta
    
    mem = MemoriaCompleta()
    
    # Testa salvar conversa
    mem.salvar_conversa("oi mirai", "E aí! Tudo certo?")
    mem.salvar_conversa("gosto de minecraft", "Minecraft é MUITO bom!")
    
    # Testa preferência
    mem.salvar_preferencia('jogos', 'favorito', 'Minecraft')
    
    # Testa fato
    mem.aprender_fato('usuario', 'gosta de jogos')
    
    # Estatísticas
    stats = mem.get_estatisticas()
    
    print(f"  ✓ Memória funcionando!")
    print(f"    - Conversas salvas: {stats['total_conversas']}")
    print(f"    - Preferências: {stats['preferencias_salvas']}")
    print(f"    - Fatos aprendidos: {stats['fatos_aprendidos']}")
    
except Exception as e:
    print(f"  ✗ Erro na memória: {e}")

# TESTE 2: Pesquisa em Segundo Plano
print("\n2️⃣ TESTANDO PESQUISA EM SEGUNDO PLANO...")
try:
    from research.background_search import BackgroundSearch
    from research.search_engine import SearchEngine
    
    bg_search = BackgroundSearch()
    search_engine = SearchEngine()
    
    bg_search.start_search("python", search_engine)
    
    import time
    print("  ⏳ Aguardando pesquisa...")
    time.sleep(3)
    
    results = bg_search.get_results()
    
    if results:
        print(f"  ✓ Pesquisa em segundo plano funcionando!")
        print(f"    - Pesquisas: {len(results)}")
    else:
        print(f"  ⚠ Nenhum resultado ainda")
    
except Exception as e:
    print(f"  ✗ Erro na pesquisa: {e}")

# TESTE 3: IA com Personalidade
print("\n3️⃣ TESTANDO IA COM PERSONALIDADE...")
try:
    from core.ai_engine import MiraiAI
    from core.context_manager import ContextManager
    import asyncio
    
    context = ContextManager()
    ai = MiraiAI(context)
    
    asyncio.run(ai.initialize())
    
    # Testa resposta
    response = ai.generate_response("oi", "conversation")
    
    print(f"  ✓ IA com personalidade funcionando!")
    print(f"    Resposta: {response}")
    
    # Verifica se tem personalidade
    has_casual = any(word in response.lower() for word in ['e aí', 'beleza', 'yatta', 'tudo certo'])
    
    if has_casual:
        print(f"    ✓ Personalidade detectada!")
    else:
        print(f"    ⚠ Resposta um pouco formal")
    
except Exception as e:
    print(f"  ✗ Erro na IA: {e}")

# TESTE 4: Análise de Tela
print("\n4️⃣ TESTANDO ANÁLISE DE TELA...")
try:
    import pyautogui
    from PIL import Image
    
    # Testa captura
    screenshot = pyautogui.screenshot()
    width, height = screenshot.size
    
    print(f"  ✓ Captura de tela funcionando!")
    print(f"    Resolução: {width}x{height}")
    
    # Testa OCR (se disponível)
    try:
        import pytesseract
        print(f"    ✓ pytesseract instalado!")
    except:
        print(f"    ⚠ pytesseract não instalado (OCR não disponível)")
    
except Exception as e:
    print(f"  ✗ Erro na análise: {e}")

# TESTE 5: Voz
print("\n5️⃣ TESTANDO SISTEMA DE VOZ...")
try:
    from actions.speaker import Speaker
    
    speaker = Speaker()
    speaker.initialize()
    
    print(f"  ✓ Sistema de voz funcionando!")
    print(f"    Voz habilitada: {speaker.enabled}")
    
except Exception as e:
    print(f"  ✗ Erro na voz: {e}")