print("="*60)
print("🔍 DIAGNÓSTICO DO SISTEMA DE VOZ")
print("="*60)

# Teste 1: Imports
print("\n[1/6] Verificando imports...")
try:
    from gtts import gTTS
    print("  ✓ gTTS disponível")
    has_gtts = True
except ImportError:
    print("  ✗ gTTS NÃO instalado!")
    has_gtts = False

try:
    import edge_tts
    print("  ✓ Edge TTS disponível")
    has_edge = True
except ImportError:
    print("  ⚠️  Edge TTS não instalado (opcional)")
    has_edge = False

try:
    import pygame
    print("  ✓ Pygame disponível")
    has_pygame = True
except ImportError:
    print("  ✗ Pygame NÃO instalado!")
    has_pygame = False

# Teste 2: Speaker
print("\n[2/6] Testando Speaker...")
try:
    from actions.speaker import Speaker
    speaker = Speaker()
    print(f"  ✓ Speaker inicializado")
    print(f"  • Enabled: {speaker.enabled}")
    print(f"  • Audio initialized: {speaker.audio_initialized}")
    print(f"  • Use Edge TTS: {speaker.use_edge_tts}")
except Exception as e:
    print(f"  ✗ Erro ao criar Speaker: {e}")
    speaker = None

# Teste 3: Pygame
print("\n[3/6] Testando Pygame Mixer...")
if has_pygame:
    try:
        pygame.mixer.init()
        print("  ✓ Pygame mixer inicializado")
        pygame.mixer.quit()
    except Exception as e:
        print(f"  ✗ Erro no pygame: {e}")

# Teste 4: Teste de fala DIRETO
print("\n[4/6] Teste de fala DIRETO...")
if speaker and speaker.enabled:
    print("  Tentando falar...")
    try:
        speaker.speak("Teste de voz direto")
        print("  ✓ Fala executada!")
    except Exception as e:
        print(f"  ✗ Erro ao falar: {e}")
        import traceback
        traceback.print_exc()
else:
    print("  ✗ Speaker não está habilitado")

# Teste 5: Verificar arquivos
print("\n[5/6] Verificando arquivos...")
from pathlib import Path

files = [
    "actions/speaker.py",
    "modes/conversation.py",
    "core/ai_engine.py"
]

for file in files:
    p = Path(file)
    if p.exists():
        print(f"  ✓ {file} encontrado")
    else:
        print(f"  ✗ {file} NÃO encontrado!")

# Teste 6: Verificar pasta temp
print("\n[6/6] Verificando pasta temporária...")
temp_dir = Path("temp_audio")
if temp_dir.exists():
    print(f"  ✓ Pasta temp_audio existe")
    files = list(temp_dir.glob("*.mp3"))
    print(f"  • Arquivos temporários: {len(files)}")
    if len(files) > 10:
        print(f"  ⚠️  {len(files)} arquivos temporários! Limpe a pasta.")
else:
    print(f"  ⚠️  Pasta temp_audio não existe (será criada)")

# RESUMO
print("\n" + "="*60)
print("📋 RESUMO")
print("="*60)

if speaker and speaker.enabled:
    print("✅ Sistema de voz FUNCIONANDO")
    print(f"\nMétodo TTS: {'Edge TTS' if speaker.use_edge_tts else 'gTTS'}")
    print(f"Volume: {speaker.voice_volume}")
    
    print("\n💡 SOLUÇÃO:")
    print("Se a voz não funciona no modo conversa:")
    print("1. Substitua modes/conversation.py pelo artefato conversation_corrigido_voz")
    print("2. Certifique-se que speaker.speak() está sendo chamado")
    print("3. Verifique se há erros no console durante a conversa")
else:
    print("❌ Sistema de voz NÃO está funcionando")
    
    print("\n💡 SOLUÇÃO:")
    if not has_gtts:
        print("1. Instale gTTS: pip install gtts")
    if not has_pygame:
        print("2. Instale pygame: pip install pygame")
    print("3. Reinicie o sistema")

print("\n" + "="*60)