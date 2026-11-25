"""Background music generation."""

from __future__ import annotations

from typing import Any

from config import AppConfig
from core.cache import ArtifactCache
from core.dependency import fingerprint, music_inputs
from core.duration import film_duration
from core.logger import RunLogger
from core.registry import ProviderRegistry


def run_music(
    storyboard: dict[str, Any],
    config: AppConfig,
    registry: ProviderRegistry,
    cache: ArtifactCache,
    log: RunLogger,
) -> dict[str, Any]:
    total = film_duration(storyboard)
    project = storyboard["project"]
    prompt = project.get("music_prompt", "ambient heritage documentary")
    out = config.outputs_dir / "music" / "background.wav"
    fp = fingerprint(music_inputs(project, total))
    key = "music:main"
    cached = cache.lookup(key, fp)
    if cached:
        storyboard.setdefault("audio", {})["music_path"] = cached["path"]
        log.info("audio", "Reused music")
        return storyboard
    result = registry.music.generate_music(prompt, out, total)
    if not result.success:
        raise RuntimeError(f"Music generation failed: {result.message}")
    storyboard.setdefault("audio", {})["music_path"] = str(out)
    cache.store(key, fp, out, reason="new music", stage="audio")
    log.info("audio", "Generated music", path=str(out))
    return storyboard