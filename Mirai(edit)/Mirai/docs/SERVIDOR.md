# 🌐 Mirai Server — acessar a Mirai do celular ou de outro PC

Esse é um recurso separado do `main.py` principal. Em vez de rodar a Mirai no console,
o `server.py` sobe um servidor web local que qualquer aparelho na mesma rede Wi-Fi
consegue acessar pelo navegador — sem instalar nada no celular.

## Quando usar

- Quer conversar com a Mirai pelo celular enquanto ela roda no PC
- Quer que ela rode num PC mais fraco/sempre ligado e acessar de outro dispositivo
- Não precisa do avatar VTuber nem dos modos (gamer, streamer etc.) — é só chat + voz

Para o uso normal (console, avatar, todos os modos), continue usando `iniciar_mirai.bat` /
`python main.py` como sempre. O `server.py` é um modo alternativo e independente.

## Como usar

1. Instale as dependências extras:
   ```
   pip install fastapi uvicorn pydantic requests edge-tts
   ```
2. Defina sua chave do Gemini como variável de ambiente (não usa o arquivo `config/gemini_key.txt` neste modo):
   ```
   set GEMINI_API_KEY=sua_chave_aqui
   ```
   (No Linux/Mac seria `export GEMINI_API_KEY="sua_chave_aqui"`)
3. Rode:
   ```
   python server.py
   ```
4. Vai aparecer algo como:
   ```
   Endereço local: http://0.0.0.0:8420
   ```
5. Descubra o IP do seu PC na rede local (Windows: `ipconfig`, procure "Endereço IPv4",
   algo tipo `192.168.0.42`)
6. No celular (mesma rede Wi-Fi), abra o navegador e acesse:
   ```
   http://192.168.0.42:8420
   ```
   Vai abrir a página de chat (`static/index.html`) — dá pra conversar por texto e
   ouvir a resposta em áudio (gerado com Edge TTS).

## Segurança

Por padrão, qualquer aparelho na sua rede Wi-Fi consegue acessar (sem senha). Se quiser
proteger, defina um token antes de rodar o servidor:
```
set MIRAI_API_TOKEN=alguma-senha-só-sua
```
E anexe `?token=alguma-senha-só-sua` na URL ao acessar de outro aparelho.

## Variáveis de ambiente disponíveis

| Variável | Padrão | O que faz |
|---|---|---|
| `GEMINI_API_KEY` | (vazio) | Sua chave do Gemini |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Modelo do Gemini a usar |
| `MIRAI_SERVER_HOST` | `0.0.0.0` | Endereço que o servidor escuta |
| `MIRAI_SERVER_PORT` | `8420` | Porta do servidor |
| `MIRAI_API_TOKEN` | (vazio) | Token opcional de proteção |
| `MIRAI_TTS_VOICE` | `pt-BR-FranciscaNeural` | Voz do Edge TTS |

## Limitações atuais

- Não usa o `core/ai_engine.py` nem a memória de longo prazo da Mirai (`memory/sistema_memoria.py`)
  — é uma implementação independente e mais simples, pensada pra ser leve
- Não tem os modos (gamer, streamer, observer) — só conversa
- A "memória" desse modo fica em `memory/permanent_memory.json`, separada da memória do `main.py`
