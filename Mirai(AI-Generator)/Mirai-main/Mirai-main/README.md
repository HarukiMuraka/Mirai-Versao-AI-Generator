# 🌸 Mirai — IA VTuber Assistant v2.0

Assistente virtual VTuber com múltiplos providers de IA, geração de texto e imagem, e controle de conhecimento.

---

## 🚀 Instalação Rápida

```bash
# 1. Clone o repositório
git clone https://github.com/HarukiMuraka/Mirai
cd Mirai

# 2. Crie o ambiente virtual
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/macOS

# 3. Instale dependências
pip install -r requirements.txt

# 4. Execute
python main.py
```

No Windows, basta dar duplo clique em **`iniciar_mirai.bat`**.

---

## 🤖 Configuração de IA

Edite `config/ai.json` para definir a ordem de preferência dos providers:

```json
{
  "provider_priority": ["claude", "gemini", "openai", "ollama", "offline"]
}
```

### Chaves de API

| Provider | Arquivo de chave | Grátis? |
|----------|-----------------|---------|
| Claude (Anthropic) | `config/claude_key.txt` | Não (trial disponível) |
| Gemini (Google) | `config/gemini_key.txt` | Sim (gemini-1.5-flash) |
| OpenAI | `config/openai_key.txt` | Não |
| Ollama | — (local) | Sim |
| Offline | — | Sim (sem IA real) |

Cole apenas a chave no arquivo, sem aspas.

---

## 📁 Estrutura do Projeto

```
mirai/
├── main.py                  ← Ponto de entrada (CORRIGIDO v2)
├── iniciar_mirai.bat        ← Launcher Windows
├── requirements.txt
│
├── core/
│   ├── ai_engine.py         ← Motor principal de IA (orquestrador)
│   ├── context_manager.py
│   └── state_machine.py
│
├── ai_providers/            ← NOVO: Providers de IA modulares
│   ├── base_provider.py     ← Interface base
│   ├── claude_provider.py   ← Anthropic Claude
│   ├── gemini_provider.py   ← Google Gemini
│   ├── openai_provider.py   ← OpenAI GPT
│   ├── ollama_provider.py   ← Ollama (local)
│   └── offline_provider.py  ← Modo offline (fallback)
│
├── features/                ← NOVO: Funcionalidades de IA
│   ├── text_generator.py    ← Geração de texto criativo
│   ├── image_generator.py   ← Geração de imagens
│   └── knowledge_manager.py ← Controle do conhecimento da Mirai
│
├── config/
│   ├── ai.json              ← Configuração de providers de IA
│   ├── general.json
│   └── *.txt                ← Chaves de API (não commitar!)
│
├── memory/
│   ├── permanent_memory.json ← Personalidade e preferências
│   └── knowledge.json        ← Fatos ensinados pelo usuário
│
├── actions/
├── interface/
├── modes/
├── perception/
├── research/
├── roms/
└── vtuber/
```

---

## ✨ Features de IA

### 🖊️ Geração de Texto

```python
from features.text_generator import TextGenerator

gen = TextGenerator(mirai.ai)
texto = await gen.generate(tipo="historia", tema="uma raposa no espaço")
texto = await gen.generate(tipo="poema", tema="anime", estilo="melancólico")
```

Tipos suportados: `historia`, `poema`, `piada`, `roteiro`, `post`, `legenda`, `descricao`, `tweet`

---

### 🎨 Geração de Imagens

```python
from features.image_generator import ImageGenerator

gen = ImageGenerator()
await gen.initialize()
path = await gen.generate("Mirai no espaço sideral", style="anime")
# Salvo em outputs/images/
```

- **Pollinations.ai** — gratuito, sem chave API necessária
- **Stable Diffusion local** — via Automatic1111, configure `sd_url` no `config/ai.json`

Estilos: `anime`, `realistic`, `chibi`, `pixel`, `painting`, `vtuber`

---

### 🧠 Controle de Conhecimento

```python
from features.knowledge_manager import KnowledgeManager

km = KnowledgeManager(mirai.ai)

# Ensinar fatos
km.teach("Python foi criado em 1991", categoria="tecnologia")

# Editar personalidade
km.edit_personality("apelidos", ["senpai", "chefe"])
km.edit_personality("girias", ["top", "massa", "dahora", "véi"])

# Trocar provider de IA em runtime
km.set_provider("gemini")
km.set_api_key("gemini", "sua_chave_aqui")

# Exportar conhecimento
path = km.export()  # → outputs/mirai_knowledge_export.json
```

---

## 🔧 Problemas Comuns

### `ModuleNotFoundError` na inicialização
O novo `main.py` usa importações opcionais — módulos faltantes são ignorados sem quebrar o sistema. Apenas `core.context_manager` e `core.ai_engine` são obrigatórios.

### Nenhum provider de IA disponível
A Mirai entra em modo offline automaticamente com respostas baseadas em regras.

### Erro de voz / PyAudio
```bash
# Windows
pip install pipwin
pipwin install pyaudio

# Linux
sudo apt install python3-pyaudio

# macOS
brew install portaudio
pip install pyaudio
```

---

## 📝 Licença

MIT License

---

Feito com 💕 — Mirai VTuber Project