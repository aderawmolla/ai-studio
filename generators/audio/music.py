"""Background music generation."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from config import AppConfig
from core.cache import ArtifactCache
from core.dependency import fingerprint, music_inputs
from core.duration import film_duration
from core.logger import RunLogger
from core.registry import ProviderRegistry


def build_music_prompt(project: dict[str, Any], duration: float) -> str:
    """Prompt for ACE-Step / future providers (mock provider ignores this)."""
    base = (project.get("music_prompt") or "ambient heritage documentary").strip()
    meta = project.get("music_metadata")
    if not isinstance(meta, dict) or not meta:
        return base
    tags: list[str] = []
    if meta.get("bpm") is not None:
        tags.append(f"{meta['bpm']} BPM")
    if meta.get("key"):
        tags.append(f"key of {meta['key']}")
    if meta.get("time_signature"):
        tags.append(meta["time_signature"])
    if meta.get("instrumental"):
        tags.append("instrumental only, no vocals")
    tags.append(f"exact length about {duration:.0f} seconds")
    return f"{base} | Mix notes: {', '.join(tags)}."


def run_music(
    storyboard: dict[str, Any],
    config: AppConfig,
    registry: ProviderRegistry,
    cache: ArtifactCache,
    log: RunLogger,
    *,
    force: bool = False,
) -> dict[str, Any]:
    total = film_duration(storyboard)
    project = storyboard["project"]
    prompt = build_music_prompt(project, total)
    out = config.outputs_dir / "music" / "background.wav"
    fp = fingerprint(music_inputs(project, total))
    key = "music:main"
    if not force:
        cached = cache.lookup(key, fp)
        if cached:
            storyboard.setdefault("audio", {})["music_path"] = cached["path"]
            log.info("audio", "Reused music")
            return storyboard
    elif out.is_file():
        out.unlink(missing_ok=True)
        log.info("audio", "Force regenerate: removed previous background.wav")
    if not force and config.music_file_override:
        src = Path(config.music_file_override).expanduser()
        if src.is_file():
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, out)
            storyboard.setdefault("audio", {})["music_path"] = str(out)
            cache.store(key, fp, out, reason="manual MUSIC_FILE", stage="audio")
            log.info("audio", "Using manual music file (ACE-Step / your WAV)", path=str(src))
            return storyboard
    if force and config.music_file_override:
        log.warn(
            "audio",
            "MUSIC_FILE ignored because this is a forced regenerate (unset MUSIC_FILE to use an import)",
        )
    result = registry.music.generate_music(prompt, out, total)
    if not result.success:
        raise RuntimeError(f"Music generation failed: {result.message}")
    storyboard.setdefault("audio", {})["music_path"] = str(out)
    cache.store(key, fp, out, reason="new music", stage="audio")
    log.info("audio", "Generated music", path=str(out))
    return storyboard