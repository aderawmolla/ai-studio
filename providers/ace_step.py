"""ACE-Step music provider."""

from __future__ import annotations

from pathlib import Path

from config import AppConfig
from providers.base import MusicProvider, ProviderResult
from providers.mock_media import make_heritage_ambient_wav


class MockAceStepProvider(MusicProvider):
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def generate_music(self, prompt: str, output_path: Path, duration: float) -> ProviderResult:
        try:
            make_heritage_ambient_wav(output_path, duration)
            return ProviderResult(success=True, path=output_path, message="mock heritage ambient")
        except Exception as exc:
            return ProviderResult(success=False, message=str(exc))


class AceStepMusicProvider(MusicProvider):
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        if not config.ace_step_url:
            raise ValueError("ACE_STEP_URL required when USE_MOCK_PROVIDERS=false")

    def generate_music(self, prompt: str, output_path: Path, duration: float) -> ProviderResult:
        raise NotImplementedError("ACE-Step: implement per service documentation.")