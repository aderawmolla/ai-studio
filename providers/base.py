"""Abstract provider interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ProviderResult:
    success: bool
    path: Path | None = None
    message: str = ""
    metadata: dict[str, Any] | None = None


class StoryProvider(ABC):
    @abstractmethod
    def generate_storyboard_draft(self, project: dict[str, Any]) -> dict[str, Any]:
        """Return partial storyboard updates (mock expands existing sample)."""


class ImageProvider(ABC):
    @abstractmethod
    def generate_image(self, prompt: str, output_path: Path, width: int, height: int) -> ProviderResult:
        ...


class VideoProvider(ABC):
    @abstractmethod
    def generate_clip(
        self,
        keyframe_path: Path,
        motion_prompt: str,
        output_path: Path,
        duration: float,
        fps: int,
        camera_movement: str = "slow push in",
    ) -> ProviderResult:
        ...


class TextToSpeechProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str, output_path: Path, language: str, duration_hint: float) -> ProviderResult:
        ...


class MusicProvider(ABC):
    @abstractmethod
    def generate_music(self, prompt: str, output_path: Path, duration: float) -> ProviderResult:
        ...