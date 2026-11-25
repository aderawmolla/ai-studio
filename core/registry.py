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
from providers.gemini_tts import GeminiTTSProvider
from providers.tts import MockTTSProvider
from providers.wan import KenBurnsVideoProvider, MockWanProvider, WanVideoProvider


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
    if config.tts_provider.strip().lower() == "gemini":
        tts: TextToSpeechProvider = GeminiTTSProvider(config)
    else:
        tts = MockTTSProvider(config)

    video: VideoProvider = (
        WanVideoProvider(config) if config.wan_api_url else KenBurnsVideoProvider(config)
    )

    music: MusicProvider = (
        AceStepMusicProvider(config) if config.ace_step_url else MockAceStepProvider(config)
    )

    return ProviderRegistry(
        story=GeminiStoryProvider(config),
        image=FluxImageProvider(config),
        video=video,
        tts=tts,
        music=music,
    )