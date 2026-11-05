import sys

def print_header():
    print("\n" + "="*60)
    print("🔊 TESTE DO SISTEMA DE VOZ DA MIRAI")
    print("="*60 + "\n")

def test_pyttsx3():
    """Testa o pyttsx3"""
    print("1. Testando pyttsx3...")
    
    try:
        import pyttsx3
        print("   ✓ pyttsx3 instalado")
        
        # Tenta inicializar
        engine = pyttsx3.init()
        print("   ✓ Engine inicializado")
        
        # Lista vozes disponíveis
        voices = engine.getProperty('voices')
        print(f"\n   Vozes disponíveis: {len(voices)}")
        
        for i, voice in enumerate(voices):
            print(f"\n   Voz {i+1}:")
            print(f"     ID: {voice.id}")
            print(f"     Nome: {voice.name}")
            print(f"     Idiomas: {voice.languages}")
        
        # Tenta falar
        print("\n   Testando fala...")
        engine.setProperty('rate', 180)
        engine.setProperty('volume', 0.9)
        
        # Procura voz em português
        pt_voice = None
        for voice in voices:
            if 'portuguese' in voice.name.lower() or 'brazil' in voice.name.lower():
                pt_voice = voice
                break
        
        if pt_voice:
            engine.setProperty('voice', pt_voice.id)
            print(f"   ✓ Usando voz: {pt_voice.name}")
        else:
            print("   ⚠ Nenhuma voz em português encontrada")
            print("   Usando voz padrão...")
        
        print("\n   🔊 A Mirai vai falar agora...")
        engine.say("Oi! Sou a Mirai! Teste de voz funcionando!")
        engine.runAndWait()
        
        print("   ✓ Teste de voz concluído!")
        
        engine.stop()
        return True
        
    except ImportError:
        print("   ❌ pyttsx3 não está instalado!")
        print("   Execute: pip install pyttsx3")
        return False
    
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_speech_recognition():
    """Testa reconhecimento de voz"""
    print("\n2. Testando SpeechRecognition...")
    
    try:
        import speech_recognition as sr
        print("   ✓ SpeechRecognition instalado")
        
        # Testa microfone
        try:
            recognizer = sr.Recognizer()
            mic = sr.Microphone()
            print("   ✓ Microfone disponível")
            
            with mic as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            print("   ✓ Microfone configurado")
            return True
            
        except Exception as e:
            print(f"   ⚠ Problema com microfone: {e}")
            return False
        
    except ImportError:
        print("   ❌ SpeechRecognition não está instalado!")
        print("   Execute: pip install SpeechRecognition")
        return False

def check_audio_drivers():
    """Verifica drivers de áudio"""
    print("\n3. Verificando sistema de áudio...")
    
    try:
        import platform
        print(f"   Sistema: {platform.system()}")
        
        if platform.system() == "Windows":
            print("   ✓ Windows detectado")
            print("\n   Verificando drivers de áudio...")
            
            # Tenta usar winsound (Windows)
            try:
                import winsound
                winsound.Beep(1000, 100)
                print("   ✓ Áudio do Windows funcionando")
            except:
                print("   ⚠ Problema com áudio do Windows")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def suggest_fixes():
    """Sugere correções"""
    print("\n" + "="*60)
    print("💡 SOLUÇÕES RECOMENDADAS")
    print("="*60 + "\n")
    
    print("Se a voz não funcionar, tente:")
    print()
    print("1. Verificar volume do sistema:")
    print("   - Abra o mixer de volume do Windows")
    print("   - Certifique-se que Python não está mutado")
    print()
    print("2. Instalar vozes em português:")
    print("   - Windows > Configurações > Hora e Idioma")
    print("   - Fala > Adicionar vozes")
    print("   - Baixe 'Microsoft Maria Desktop - Portuguese (Brazil)'")
    print()
    print("3. Reiniciar o serviço de áudio:")
    print("   - Abra Serviços (services.msc)")
    print("   - Reinicie 'Áudio do Windows'")
    print()
    print("4. Testar com outro programa:")
    print("   - Abra o Bloco de Notas")
    print("   - Use Ctrl+H (Narrador do Windows)")
    print("   - Se não funcionar, o problema é do sistema")
    print()

def main():
    print_header()
    
    # Testa cada componente
    voz_ok = test_pyttsx3()
    mic_ok = test_speech_recognition()
    audio_ok = check_audio_drivers()
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DO DIAGNÓSTICO")
    print("="*60 + "\n")
    
    print(f"Sistema de voz (pyttsx3):      {'✓ OK' if voz_ok else '❌ PROBLEMA'}")
    print(f"Reconhecimento (microfone):    {'✓ OK' if mic_ok else '❌ PROBLEMA'}")
    print(f"Drivers de áudio:              {'✓ OK' if audio_ok else '❌ PROBLEMA'}")
    
    if voz_ok and audio_ok:
        print("\n✅ Sistema de voz FUNCIONANDO!")
        print("\nSe a Mirai não fala, o problema pode ser:")
        print("  • Modo texto ativo (não chama speaker.speak)")
        print("  • Volume do sistema muito baixo")
        print("  • Python mutado no mixer de volume")
    else:
        print("\n⚠ Problemas detectados!")
        suggest_fixes()
    
    print("\n" + "="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTeste cancelado pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()