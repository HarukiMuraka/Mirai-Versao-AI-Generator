import subprocess
import sys

def print_header():
    print("\n" + "="*60)
    print("🌸 CORRETOR DE DEPENDÊNCIAS DA MIRAI 🌸")
    print("="*60 + "\n")

def check_python_version():
    """Verifica versão do Python"""
    version = sys.version_info
    print(f"Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ ERRO: Python 3.10 ou superior necessário!")
        return False
    
    print("✓ Versão do Python OK\n")
    return True

def check_torch():
    """Verifica versão do PyTorch"""
    try:
        import torch
        print(f"PyTorch instalado: {torch.__version__}")
        
        # Verifica se tem CUDA
        if torch.cuda.is_available():
            print(f"✓ CUDA disponível: {torch.version.cuda}")
        else:
            print("⚠ CUDA não disponível (rodará em CPU)")
        
        return True
    except ImportError:
        print("❌ PyTorch não instalado")
        return False

def fix_dependencies():
    """Corrige dependências"""
    print("\n" + "="*60)
    print("CORRIGINDO DEPENDÊNCIAS...")
    print("="*60 + "\n")
    
    # Lista de pacotes essenciais (sem versão específica)
    essential_packages = [
        "colorama",
        "rich", 
        "prompt-toolkit",
        "pyautogui",
        "keyboard",
        "psutil",
        "requests",
        "beautifulsoup4",
        "python-dotenv",
        "pillow",
        "pyttsx3",
        "SpeechRecognition"
    ]
    
    print("Instalando pacotes essenciais...\n")
    
    for package in essential_packages:
        try:
            print(f"→ Instalando {package}...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package, "--upgrade"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"  ✓ {package} instalado")
        except:
            print(f"  ⚠ Erro ao instalar {package}")
    
    print("\n✓ Pacotes essenciais instalados!\n")

def check_pyaudio():
    """Verifica e dá instruções para PyAudio"""
    print("\n" + "="*60)
    print("VERIFICANDO PyAudio...")
    print("="*60 + "\n")
    
    try:
        import pyaudio
        print("✓ PyAudio já instalado!")
        return True
    except ImportError:
        print("⚠ PyAudio não instalado")
        print("\nO PyAudio é necessário para reconhecimento de voz.")
        print("\nPara instalar no Windows:")
        print("1. Acesse: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio")
        print("2. Baixe o arquivo .whl compatível")
        print("3. Execute: pip install [arquivo].whl")
        
        version = sys.version_info
        print(f"\nSua versão Python: 3.{version.minor}")
        print(f"Baixe: PyAudio-0.2.14-cp3{version.minor}-cp3{version.minor}-win_amd64.whl")
        
        return False

def test_imports():
    """Testa importações essenciais"""
    print("\n" + "="*60)
    print("TESTANDO IMPORTAÇÕES...")
    print("="*60 + "\n")
    
    modules = {
        "colorama": "Interface colorida",
        "pyttsx3": "Sistema de voz",
        "pyautogui": "Automação",
        "requests": "Pesquisa web",
        "prompt_toolkit": "Entrada de texto"
    }
    
    all_ok = True
    
    for module, description in modules.items():
        try:
            __import__(module)
            print(f"✓ {description:20s} OK")
        except ImportError:
            print(f"❌ {description:20s} FALTANDO")
            all_ok = False
    
    return all_ok

def main():
    print_header()
    
    # 1. Verifica Python
    if not check_python_version():
        return
    
    # 2. Verifica PyTorch
    has_torch = check_torch()
    
    # 3. Pergunta se quer corrigir
    print("\n" + "="*60)
    resposta = input("Deseja corrigir as dependências? (s/n): ").lower()
    
    if resposta != 's':
        print("Operação cancelada.")
        return
    
    # 4. Corrige dependências
    fix_dependencies()
    
    # 5. Verifica PyAudio
    check_pyaudio()
    
    # 6. Testa importações
    if test_imports():
        print("\n" + "="*60)
        print("✓ TUDO PRONTO!")
        print("="*60)
        print("\nAgora você pode executar:")
        print("  python main.py")
        print("\n🌸 Divirta-se com a Mirai! 🌸\n")
    else:
        print("\n" + "="*60)
        print("⚠ ALGUNS MÓDULOS FALTANDO")
        print("="*60)
        print("\nVerifique os erros acima e tente:")
        print("  pip install [nome-do-modulo]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()