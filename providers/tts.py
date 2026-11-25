"""Text-to-speech provider."""

from __future__ import annotations

from pathlib import Path

from config import AppConfig
from providers.base import ProviderResult, TextToSpeechProvider
from providers.mock_media import make_silent_wav


class MockTTSProvider(TextToSpeechProvider):
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def synthesize(
        self, text: str, output_path: Path, language: str, duration_hint: float
    ) -> ProviderResult:
        try:
            make_silent_wav(output_path, max(duration_hint, 0.5))
            return ProviderResult(success=True, path=output_path, message=f"mock tts ({language})")
        except Exception as exc:
            return ProviderResult(success=False, message=str(exc))