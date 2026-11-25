"""Wan image-to-video provider."""

from __future__ import annotations

from pathlib import Path

from config import AppConfig
from providers.base import ProviderResult, VideoProvider
from providers.mock_media import make_video_from_image


class MockWanProvider(VideoProvider):
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def generate_clip(
        self,
        keyframe_path: Path,
        motion_prompt: str,
        output_path: Path,
        duration: float,
        fps: int,
    ) -> ProviderResult:
        try:
            make_video_from_image(self.config, keyframe_path, output_path, duration)
            return ProviderResult(success=True, path=output_path, message="mock clip", metadata={"prompt": motion_prompt})
        except Exception as exc:
            return ProviderResult(success=False, message=str(exc))


class WanVideoProvider(VideoProvider):
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        if not config.wan_api_url:
            raise ValueError("WAN_API_URL required when USE_MOCK_PROVIDERS=false")

    def generate_clip(
        self,
        keyframe_path: Path,
        motion_prompt: str,
        output_path: Path,
        duration: float,
        fps: int,
    ) -> ProviderResult:
        raise NotImplementedError("Wan TI2V: implement per hosted or local API.")