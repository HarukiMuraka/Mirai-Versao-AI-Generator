import requests
import subprocess
import sys

print("="*60)
print("🔍 DIAGNÓSTICO DO OLLAMA")
print("="*60)

# Teste 1: Ollama está respondendo?
print("\n[1/4] Testando se Ollama está ativo...")
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=3)
    
    if response.status_code == 200:
        print("   ✅ Ollama ESTÁ RODANDO!")
        
        # Mostra modelos
        data = response.json()
        models = data.get('models', [])
        
        print("\n[2/4] Modelos instalados:")
        if models:
            for model in models:
                name = model.get('name', 'unknown')
                size = model.get('size', 0) / (1024**3)  # GB
                print(f"   • {name} ({size:.1f} GB)")
            
            # Verifica llama3
            has_llama = any('llama3' in m.get('name', '').lower() for m in models)
            
            if has_llama:
                print("\n   ✅ llama3 encontrado!")
            else:
                print("\n   ⚠️  llama3 NÃO encontrado")
                print("   Execute: ollama pull llama3")
        else:
            print("   ⚠️  Nenhum modelo instalado")
            print("   Execute: ollama pull llama3")
        
        # Teste de geração
        print("\n[3/4] Testando geração de texto...")
        
        if models and has_llama:
            # Pega primeiro modelo com llama3
            model_name = None
            for m in models:
                if 'llama3' in m.get('name', '').lower():
                    model_name = m.get('name')
                    break
            
            try:
                test_resp = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        'model': model_name,
                        'prompt': 'Diga apenas: OK',
                        'stream': False,
                        'options': {'num_predict': 5}
                    },
                    timeout=20
                )
                
                if test_resp.status_code == 200:
                    result = test_resp.json()
                    answer = result.get('response', '').strip()
                    print(f"   ✅ Geração funcionando! Resposta: {answer}")
                else:
                    print(f"   ❌ Geração falhou (status {test_resp.status_code})")
            except Exception as e:
                print(f"   ❌ Erro na geração: {e}")
        
        # Verifica processos
        print("\n[4/4] Verificando processos do Ollama...")
        try:
            if sys.platform == "win32":
                result = subprocess.run(
                    ['tasklist', '/FI', 'IMAGENAME eq ollama.exe'],
                    capture_output=True,
                    text=True
                )
                
                if 'ollama.exe' in result.stdout:
                    print("   ✅ Processo ollama.exe encontrado")
                    
                    # Conta quantos
                    count = result.stdout.count('ollama.exe')
                    print(f"   📊 {count} instância(s) rodando")
                else:
                    print("   ⚠️  Processo não encontrado (mas API responde)")
        except:
            print("   ⚠️  Não foi possível verificar processos")
        
        # RESULTADO FINAL
        print("\n" + "="*60)
        print("✅ OLLAMA FUNCIONANDO!")
        print("="*60)
        print("\n💡 NÃO PRECISA executar 'ollama serve'!")
        print("   O Ollama já está ativo em segundo plano.")
        print("\n🎯 Próximos passos:")
        print("   1. Se llama3 está instalado → Use a Mirai normalmente")
        print("   2. Se llama3 NÃO está instalado → Execute: ollama pull llama3")
        print("   3. Teste a Mirai: python main.py → Menu 7 → 3")
        
    else:
        print(f"   ❌ Ollama respondeu com erro: {response.status_code}")

except requests.exceptions.ConnectionError:
    print("   ❌ Ollama NÃO está rodando")
    print("\n💡 Possíveis causas:")
    print("   1. Serviço não instalado")
    print("   2. Processo travado")
    
    print("\n🔧 Soluções:")
    print("   1. Reinicie o computador")
    print("   2. Ou execute: ollama serve")

except Exception as e:
    print(f"   ❌ Erro: {e}")

print("\n" + "="*60)