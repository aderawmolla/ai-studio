"""Provider registry — wires mock or real providers from configuration."""

from __future__ import annotations

from dataclasses import dataclass

from config import AppConfig
from providers.ace_step import AceStepMusicProvider, MockAceStepProvider
from providers.base import (
    ImageProvider,
    MusicProvider,
    StoryProvider,
    TextToSpeechProvider,
    VideoProvider,
)
from providers.flux import FluxImageProvider, MockFluxProvider
from providers.gemini import GeminiStoryProvider, MockGeminiProvider
from providers.tts import MockTTSProvider
from providers.wan import MockWanProvider, WanVideoProvider


@dataclass
class ProviderRegistry:
    story: StoryProvider
    image: ImageProvider
    video: VideoProvider
    tts: TextToSpeechProvider
    music: MusicProvider


def build_registry(config: AppConfig) -> ProviderRegistry:
    if config.use_mock_providers:
        return ProviderRegistry(
            story=MockGeminiProvider(),
            image=MockFluxProvider(config),
            video=MockWanProvider(config),
            tts=MockTTSProvider(config),
            music=MockAceStepProvider(config),
        )
    return ProviderRegistry(
        story=GeminiStoryProvider(config),
        image=FluxImageProvider(config),
        video=WanVideoProvider(config),
        tts=MockTTSProvider(config),  # swap when real TTS credentials are configured
        music=AceStepMusicProvider(config),
    )