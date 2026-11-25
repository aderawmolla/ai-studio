"""FLUX image provider (Cloudflare Workers AI)."""

from __future__ import annotations

import io
import time
from pathlib import Path

import requests

from config import AppConfig
from core.model_log import log_model_call
from providers.base import ImageProvider, ProviderResult
from providers.mock_media import make_png_placeholder

DEFAULT_FLUX_MODEL = "@cf/black-forest-labs/flux-1-schnell"


class MockFluxProvider(ImageProvider):
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def generate_image(self, prompt: str, output_path: Path, width: int, height: int) -> ProviderResult:
        try:
            make_png_placeholder(output_path, width, height, prompt)
            return ProviderResult(success=True, path=output_path, message="mock image")
        except Exception as exc:
            return ProviderResult(success=False, message=str(exc))


class FluxImageProvider(ImageProvider):
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.account_id = config.cloudflare_account_id
        self.token = config.cloudflare_api_token or config.flux_api_key
        if not self.account_id or not self.token:
            raise ValueError(
                "CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN required when USE_MOCK_PROVIDERS=false"
            )
        self.model = config.cloudflare_flux_model or DEFAULT_FLUX_MODEL

    def generate_image(self, prompt: str, output_path: Path, width: int, height: int) -> ProviderResult:
        t0 = time.perf_counter()
        url = (
            f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/{self.model}"
        )
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        try:
            resp = requests.post(url, headers=headers, json={"prompt": prompt}, timeout=120)
            resp.raise_for_status()
            data = resp.content
            if resp.headers.get("content-type", "").startswith("application/json"):
                payload = resp.json()
                if not payload.get("success", True):
                    err = payload.get("errors", payload)
                    raise RuntimeError(str(err))
                result = payload.get("result", {})
                if isinstance(result, dict) and "image" in result:
                    import base64

                    data = base64.b64decode(result["image"])
                else:
                    raise RuntimeError(f"Unexpected JSON from Cloudflare: {list(payload.keys())}")
        except Exception as exc:
            log_model_call(
                self.config.logs_dir,
                stage="image",
                model=self.model,
                latency_ms=(time.perf_counter() - t0) * 1000,
                success=False,
                parameters={"prompt_len": len(prompt), "width": width, "height": height},
                message=str(exc),
            )
            return ProviderResult(success=False, message=f"FLUX failed: {exc}")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            from PIL import Image

            img = Image.open(io.BytesIO(data)).convert("RGB")
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            img.save(output_path, format="PNG")
        except Exception:
            output_path.write_bytes(data)

        log_model_call(
            self.config.logs_dir,
            stage="image",
            model=self.model,
            latency_ms=(time.perf_counter() - t0) * 1000,
            success=True,
            parameters={"prompt_len": len(prompt), "width": width, "height": height},
            cost_usd=0.0,
        )
        return ProviderResult(success=True, path=output_path, message="cloudflare flux")