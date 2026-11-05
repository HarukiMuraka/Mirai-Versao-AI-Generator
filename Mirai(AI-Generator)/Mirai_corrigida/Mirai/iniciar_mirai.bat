@echo off
chcp 65001 >nul
color 0D
title Mirai - Assistente VTuber

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║            🌸  MIRAI  🌸                 ║
echo  ║       IA VTuber Assistant v2.0           ║
echo  ╚══════════════════════════════════════════╝
echo.

:: ─────────────────────────────────────────────
:: [1] Verifica Python
:: ─────────────────────────────────────────────
echo [1/5] Verificando Python...
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo  ❌ Python não encontrado!
    echo     Baixe em: https://www.python.org/downloads/
    pause & exit /b 1
)
echo  ✓ Python OK
echo.

:: ─────────────────────────────────────────────
:: [2] Ambiente virtual
:: ─────────────────────────────────────────────
cd /d "%~dp0"

echo [2/5] Ambiente virtual...
if not exist "venv\Scripts\activate.bat" (
    echo  Criando venv...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo  ❌ Falha ao criar venv!
        pause & exit /b 1
    )
)
call venv\Scripts\activate.bat
echo  ✓ Venv ativo
echo.

:: ─────────────────────────────────────────────
:: [3] Dependências core
:: ─────────────────────────────────────────────
echo [3/5] Verificando dependências...
python -c "import colorama, requests, bs4, gtts, pygame" >nul 2>nul
if %errorlevel% neq 0 (
    echo  Instalando dependências core...
    pip install -q colorama requests beautifulsoup4 python-dotenv Pillow gTTS pygame SpeechRecognition pyautogui keyboard psutil rich
    if %errorlevel% neq 0 (
        echo  ⚠️ Algumas dependências podem ter falhado - continuando...
    )
)
echo  ✓ Dependências OK
echo.

:: ─────────────────────────────────────────────
:: [4] Ollama (opcional)
:: ─────────────────────────────────────────────
echo [4/5] Verificando Ollama (opcional)...
where ollama >nul 2>nul
if %errorlevel% equ 0 (
    echo  ✓ Ollama encontrado - iniciando servidor...
    start "Ollama Server" /MIN ollama serve
    timeout /t 3 /nobreak >nul
) else (
    echo  ⚠️ Ollama não instalado ^(usando API online ou modo offline^)
    echo     Para instalar: https://ollama.ai
)
echo.

:: ─────────────────────────────────────────────
:: [5] Verifica config de IA
:: ─────────────────────────────────────────────
echo [5/5] Verificando configuração de IA...
if not exist "config\ai.json" (
    echo  ⚠️ config\ai.json não encontrado - será criado com padrões
)
if exist "config\gemini_key.txt" (
    echo  ✓ Chave Gemini encontrada
) else if exist "config\claude_key.txt" (
    echo  ✓ Chave Claude encontrada
) else if exist "config\openai_key.txt" (
    echo  ✓ Chave OpenAI encontrada
) else (
    echo  ℹ️ Nenhuma chave de API configurada ^- usando Ollama ou modo offline
    echo     Adicione sua chave em config\gemini_key.txt, claude_key.txt ou openai_key.txt
)
echo.

:: ─────────────────────────────────────────────
:: INICIA MIRAI
:: ─────────────────────────────────────────────
echo  ╔══════════════════════════════════════════╗
echo  ║        ✨ INICIANDO MIRAI ✨             ║
echo  ╚══════════════════════════════════════════╝
echo.

python main.py

echo.
echo  ═══════════════════════════════════════════
echo  Mirai encerrada!
echo.

:: Fecha Ollama se estava rodando
tasklist /fi "imagename eq ollama.exe" 2>nul | find /i "ollama.exe" >nul
if %errorlevel% equ 0 (
    choice /c SN /n /m " Fechar servidor Ollama? (S/N): "
    if %errorlevel% equ 1 (
        taskkill /f /im ollama.exe >nul 2>nul
        echo  ✓ Ollama encerrado!
    )
)

echo.
echo  Até logo! 🌸
echo.
pause