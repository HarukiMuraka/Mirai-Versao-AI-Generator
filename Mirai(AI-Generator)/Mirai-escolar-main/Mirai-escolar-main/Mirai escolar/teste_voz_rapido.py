import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*60)
print("🔊 TESTE RÁPIDO DE VOZ DA MIRAI")
print("="*60 + "\n")

# Testa importação
try:
    from actions.speaker import Speaker
    print("✓ Speaker importado com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar Speaker: {e}")
    sys.exit(1)

# Inicializa speaker
print("\nInicializando speaker...")
speaker = Speaker()
if not speaker.initialize():
    print("❌ Falha ao inicializar speaker!")
    sys.exit(1)

# Testa fala
print("\n" + "="*60)
print("TESTE 1: Fala Síncrona")
print("="*60)
speaker.speak("Olá! Sou a Mirai! Este é um teste de voz!")

input("\nPressione Enter para continuar...")

print("\n" + "="*60)
print("TESTE 2: Fala Assíncrona")
print("="*60)
speaker.speak_async("Teste de fala assíncrona funcionando!")

import time
time.sleep(3)

print("\n" + "="*60)
print("TESTE 3: Várias Frases")
print("="*60)

frases = [
    "Oi! Tudo bem?",
    "Meu nome é Mirai!",
    "Adoro conversar com você!",
    "Yatta! Teste concluído!"
]

for frase in frases:
    speaker.speak(frase)
    time.sleep(0.5)

print("\n" + "="*60)
print("✓ TODOS OS TESTES CONCLUÍDOS!")
print("="*60)
print("\nSe você ouviu a Mirai falando, está tudo OK! 🌸")
print("Se não ouviu nada, verifique:")
print("  • Volume do sistema")
print("  • Mixer de volume (se Python está mutado)")
print("  • Alto-falantes conectados")
print("\n")