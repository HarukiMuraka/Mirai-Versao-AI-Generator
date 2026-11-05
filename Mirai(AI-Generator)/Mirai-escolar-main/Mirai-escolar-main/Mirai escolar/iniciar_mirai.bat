@echo off
chcp 65001 >nul
color 0D

echo.
echo ╔════════════════════════════════════════╗
echo ║                                        ║
echo ║            🌸 MIRAI 🌸                 ║
echo ║         Assistente Virtual             ║
echo ║                                        ║
echo ╚════════════════════════════════════════╝
echo.

echo [1/4] Verificando Ollama...

:: Testa se Ollama está instalado
where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Ollama não está instalado!
    echo.
    echo Baixe em: https://ollama.ai
    echo.
    pause
    exit /b 1
)

echo ✓ Ollama encontrado!
echo.

echo [2/4] Iniciando servidor Ollama...

:: Inicia Ollama serve em janela separada
start "Ollama Server - NÃO FECHE ESTA JANELA!" /MIN ollama serve

echo ✓ Servidor iniciado!
echo.

echo [3/4] Aguardando Ollama inicializar (5 segundos)...
timeout /t 5 /nobreak >nul

echo ✓ Pronto!
echo.

echo [4/4] Iniciando Mirai...
echo.

:: Muda para diretório da Mirai
cd /d "%~dp0"

:: Ativa venv
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✓ Ambiente virtual ativado!
    echo.
) else (
    echo ⚠️ Ambiente virtual não encontrado!
    echo    Criando venv...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo ✓ Ambiente criado e ativado!
    echo.
)

:: Verifica dependências
echo Verificando dependências...
python -c "import gtts, pygame, requests, colorama, pytesseract, bs4" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ⚠️ Instalando dependências faltantes...
    pip install -q gtts pygame requests colorama pytesseract pillow beautifulsoup4 lxml
    echo ✓ Dependências instaladas!
)

echo.
echo ╔════════════════════════════════════════╗
echo ║                                        ║
echo ║     ✨ MIRAI ESTÁ INICIANDO ✨         ║
echo ║                                        ║
echo ╚════════════════════════════════════════╝
echo.
echo IMPORTANTE:
echo • Ollama está rodando em segundo plano
echo • NÃO FECHE a janela "Ollama Server"
echo • Se fechar, a IA para de funcionar
echo.
echo ═══════════════════════════════════════════
echo.

:: Inicia Mirai
python main.py

echo.
echo ═══════════════════════════════════════════
echo.
echo Mirai encerrada!
echo.

:: Pergunta se quer fechar Ollama
echo Fechar servidor Ollama? (S/N)
choice /c SN /n /m "Escolha: "

if %errorlevel% equ 1 (
    taskkill /f /im ollama.exe >nul 2>nul
    echo ✓ Ollama encerrado!
)

echo.
echo Até logo! 🌸
echo.
pause