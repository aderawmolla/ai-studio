"""Story stage — updates project config and optional LLM draft."""

from __future__ import annotations

from typing import Any

from core.logger import RunLogger
from core.registry import ProviderRegistry


def run_story(storyboard: dict[str, Any], registry: ProviderRegistry, log: RunLogger) -> dict[str, Any]:
    log.info("story", "Generating story draft", topic=storyboard["project"]["topic"])
    draft = registry.story.generate_storyboard_draft(storyboard["project"])
    log.info("story", "Story stage complete", provider_note=draft.get("note", ""))
    return storyboard