# 🎨 Instalando gerador de imagem local (grátis, sem limites) para a Mirai

A Mirai já vem pronta para conversar com o **Automatic1111 (Stable Diffusion WebUI)**
rodando na sua própria máquina — o código em `features/image_generator.py` já aponta
para `http://127.0.0.1:7860`. Falta só instalar o servidor. Depois disso, toda geração
de imagem passa a ser 100% local, gratuita e sem limite de uso (só depende do seu hardware).

> Alternativa: enquanto não instala, a Mirai já usa o **Pollinations.ai** (grátis, online,
> sem chave) como fallback automático — então ela não fica sem gerar imagens nesse meio tempo.

---

## Requisitos

- **Windows 10/11** (o guia abaixo é focado nisso, já que você usa `iniciar_mirai.bat`)
- **Placa de vídeo NVIDIA** com pelo menos 4 GB de VRAM (o ideal é 6 GB+). Sem GPU NVIDIA
  também funciona, mas fica bem mais lento (rodando na CPU).
- ~15 GB livres em disco (WebUI + pelo menos um modelo)
- Python 3.10.6 (o Automatic1111 é sensível à versão do Python — recomenda-se essa
  especificamente, não precisa ser a mesma da Mirai)
- Git instalado

---

## Passo a passo

### 1. Baixe o Automatic1111

```
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
```

Ou baixe o `.zip` direto da página do projeto no GitHub e extraia, se preferir não usar Git.

### 2. Baixe um modelo (checkpoint)

O WebUI sozinho não gera nada — ele precisa de um modelo `.safetensors`. Opções gratuitas
recomendadas (baixe de [Civitai](https://civitai.com) ou [Hugging Face](https://huggingface.co)):

- **Style estilo anime/vtuber** (combina com o `style="anime"` / `"vtuber"` que a Mirai já usa):
  procure por `Anything V5`, `MeinaMix` ou `Counterfeit-V3` no Civitai
- **Estilo realista**: `Realistic Vision` ou `epiCRealism`
- **Leve/rápido** (bom se sua GPU for fraca): `SDXL Turbo` ou `LCM` (gera em poucos passos)

Coloque o arquivo `.safetensors` baixado em:
```
stable-diffusion-webui/models/Stable-diffusion/
```

### 3. Ative a API (passo crítico — sem isso a Mirai não consegue conversar com o WebUI)

Abra o arquivo `webui-user.bat` (dentro da pasta do Automatic1111) com um editor de texto
e edite a linha `COMMANDLINE_ARGS`:

```bat
set COMMANDLINE_ARGS=--api
```

Se sua GPU tiver pouca VRAM (4 GB ou menos), adicione também `--medvram` ou `--lowvram`:

```bat
set COMMANDLINE_ARGS=--api --medvram
```

### 4. Primeira execução

Dê duplo clique em `webui-user.bat`. A primeira vez demora bastante (baixa dependências
do PyTorch etc). Quando terminar, ele mostra algo como:

```
Running on local URL:  http://127.0.0.1:7860
```

Deixe essa janela aberta — é o servidor rodando. Você pode testar abrindo esse endereço
no navegador: deve aparecer a interface web do Stable Diffusion.

### 5. Configure a Mirai para usar o SD local

Edite `config/ai.json` e troque o provider de imagem:

```json
"image": {
  "provider": "stable_diffusion",
  "sd_url": "http://127.0.0.1:7860"
}
```

(Se o WebUI estiver rodando em outra porta ou outra máquina na rede, ajuste `sd_url`
de acordo.)

### 6. Teste

Com o Automatic1111 rodando em segundo plano, inicie a Mirai normalmente
(`iniciar_mirai.bat` ou `python main.py`) e peça pra ela gerar uma imagem. No console
dela deve aparecer:

```
✓ Stable Diffusion local disponível
```

Se aparecer "SD não disponível, usando Pollinations", confira se:
- a janela do `webui-user.bat` ainda está aberta e sem erro
- o `--api` está mesmo na linha de `COMMANDLINE_ARGS`
- o `sd_url` no `config/ai.json` bate com a porta mostrada no console do WebUI

---

## Rotina de uso

Toda vez que quiser usar a Mirai com geração de imagem local, é preciso primeiro abrir o
`webui-user.bat` do Automatic1111 e esperar ele subir, **antes** de abrir a Mirai. Se preferir
automatizar isso, dá pra editar o `iniciar_mirai.bat` da Mirai para abrir os dois em sequência
— posso te ajudar a montar isso se quiser.

## Alternativa mais leve: ComfyUI

Se o Automatic1111 for pesado demais para sua máquina, o **ComfyUI** é uma alternativa mais
leve e rápida, mas exige montar um "workflow" visual em vez de só clicar em gerar. Para a
Mirai funcionar com ele seria preciso adaptar `features/image_generator.py` (o formato de
API é diferente do Automatic1111). Recomendo começar pelo A1111 por ser mais simples, e só
migrar para ComfyUI depois se a velocidade for um problema.
