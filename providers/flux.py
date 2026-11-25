"""FLUX image provider."""

from __future__ import annotations

from pathlib import Path

from config import AppConfig
from providers.base import ImageProvider, ProviderResult
from providers.mock_media import make_png_placeholder


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
        if not config.flux_api_key:
            raise ValueError("FLUX_API_KEY required when USE_MOCK_PROVIDERS=false")

    def generate_image(self, prompt: str, output_path: Path, width: int, height: int) -> ProviderResult:
        raise NotImplementedError("FLUX API: implement per provider documentation.")