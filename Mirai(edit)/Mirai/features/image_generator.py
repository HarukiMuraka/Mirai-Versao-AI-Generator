"""
features/image_generator.py
Geração de imagens pela Mirai.
Suporta: Stable Diffusion (local via Automatic1111), Pollinations (gratuito/online).

Uso:
    gen = ImageGenerator(config)
    path = await gen.generate("uma raposa no espaço, anime style")
"""

import asyncio
import base64
import json
import time
from pathlib import Path
from typing import Optional
import requests


class ImageGenerator:
    """Gera imagens a partir de prompts de texto."""

    PROVIDERS = ["pollinations", "stable_diffusion"]

    def __init__(self, config: dict = None):
        self.config      = config or {}
        self.output_dir  = Path("outputs/images")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Provider preferido
        self.provider = self.config.get("provider", "pollinations")
        # SD local
        self.sd_url   = self.config.get("sd_url", "http://127.0.0.1:7860")

    async def initialize(self) -> bool:
        """Verifica qual provider está disponível."""
        if self.provider == "stable_diffusion":
            if await self._test_sd():
                print("  ✓ Stable Diffusion local disponível")
                return True
            print("  ⚠ SD não disponível, usando Pollinations")
            self.provider = "pollinations"

        print(f"  ✓ Gerador de imagens ativo ({self.provider})")
        return True

    async def _test_sd(self) -> bool:
        try:
            r = requests.get(f"{self.sd_url}/sdapi/v1/sd-models", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    async def generate(
        self,
        prompt: str,
        style: str = "anime",
        width:  int = 512,
        height: int = 512,
        steps:  int = 20,
    ) -> Optional[Path]:
        """
        Gera imagem e salva em outputs/images/.

        Returns:
            Path do arquivo salvo, ou None em caso de erro.
        """
        # Enriquece o prompt com estilo
        full_prompt = self._enrich_prompt(prompt, style)

        if self.provider == "stable_diffusion":
            return await self._generate_sd(full_prompt, width, height, steps)

        return await self._generate_pollinations(full_prompt, width, height)

    def _enrich_prompt(self, prompt: str, style: str) -> str:
        styles = {
            "anime":      "anime style, high quality, vibrant colors, detailed",
            "realistic":  "photorealistic, 8k, detailed, professional photography",
            "chibi":      "chibi style, cute, kawaii, anime, pastel colors",
            "pixel":      "pixel art, retro, 16bit, detailed",
            "painting":   "digital painting, artstation, concept art, detailed",
            "vtuber":     "vtuber avatar, anime, cute, colorful background, stream overlay",
        }
        style_tag = styles.get(style, style)
        return f"{prompt}, {style_tag}"

    async def _generate_pollinations(self, prompt: str, width: int, height: int) -> Optional[Path]:
        """Usa Pollinations.ai — gratuito, sem chave API."""
        try:
            import urllib.parse
            encoded = urllib.parse.quote(prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true"

            print(f"  🎨 Gerando imagem via Pollinations...")
            r = requests.get(url, timeout=30, stream=True)

            if r.status_code == 200:
                filename = self.output_dir / f"mirai_{int(time.time())}.jpg"
                with open(filename, "wb") as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
                print(f"  ✓ Imagem salva: {filename}")
                return filename

        except Exception as e:
            print(f"  ⚠ Pollinations erro: {e}")
        return None

    async def _generate_sd(self, prompt: str, width: int, height: int, steps: int) -> Optional[Path]:
        """Usa Automatic1111 Stable Diffusion local."""
        try:
            print(f"  🎨 Gerando imagem via Stable Diffusion...")
            r = requests.post(
                f"{self.sd_url}/sdapi/v1/txt2img",
                json={
                    "prompt":           prompt,
                    "negative_prompt":  "lowres, bad anatomy, bad hands, blurry, nsfw",
                    "width":            width,
                    "height":           height,
                    "steps":            steps,
                    "cfg_scale":        7,
                    "sampler_name":     "DPM++ 2M Karras",
                },
                timeout=60,
            )

            if r.status_code == 200:
                data = r.json()
                img_b64 = data["images"][0]
                img_bytes = base64.b64decode(img_b64)
                filename = self.output_dir / f"mirai_{int(time.time())}.png"
                filename.write_bytes(img_bytes)
                print(f"  ✓ Imagem salva: {filename}")
                return filename

        except Exception as e:
            print(f"  ⚠ SD erro: {e}")
        return None

    def list_styles(self) -> str:
        styles = ["anime", "realistic", "chibi", "pixel", "painting", "vtuber"]
        return "\n".join(f"  • {s}" for s in styles)