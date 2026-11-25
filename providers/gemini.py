"""Gemini story provider (stub for API integration)."""

from __future__ import annotations

from typing import Any

from config import AppConfig
from providers.base import StoryProvider


class MockGeminiProvider(StoryProvider):
    def generate_storyboard_draft(self, project: dict[str, Any]) -> dict[str, Any]:
        return {
            "project": project,
            "note": "Mock story provider: using existing storyboard.json shots.",
        }


class GeminiStoryProvider(StoryProvider):
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        if not config.gemini_api_key:
            raise ValueError("GEMINI_API_KEY required when USE_MOCK_PROVIDERS=false")

    def generate_storyboard_draft(self, project: dict[str, Any]) -> dict[str, Any]:
        # Story lives in storyboard.json; optional LLM assist can be added later.
        return {"project": project, "note": "Using storyboard.json as source (Gemini story pass-through)."}