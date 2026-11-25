"""Reference images and per-shot keyframes."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from config import AppConfig
from core.cache import ArtifactCache
from core.dependency import fingerprint, shot_keyframe_inputs
from core.logger import RunLogger
from core.registry import ProviderRegistry


def _reference_paths(storyboard: dict[str, Any]) -> list[str]:
    return sorted(
        r.get("image_path") or ""
        for r in storyboard.get("references", {}).values()
        if r.get("image_path")
    )


def run_references(
    storyboard: dict[str, Any],
    config: AppConfig,
    registry: ProviderRegistry,
    cache: ArtifactCache,
    log: RunLogger,
) -> dict[str, Any]:
    for ref_id, ref in storyboard.get("references", {}).items():
        out = config.outputs_dir / "references" / f"{ref_id}.png"
        fp = fingerprint({"ref_id": ref_id, "description": ref["description"]})
        key = f"ref:{ref_id}"
        cached = cache.lookup(key, fp)
        if cached:
            ref["image_path"] = cached["path"]
            ref["generation_status"] = "reused"
            log.info("references", f"Reused {ref_id}", reason="cache hit")
            continue
        result = registry.image.generate_image(
            ref["description"], out, config.vertical_width, config.vertical_height
        )
        if not result.success:
            raise RuntimeError(f"Reference {ref_id} failed: {result.message}")
        ref["image_path"] = str(out)
        ref["generation_status"] = "generated"
        cache.store(key, fp, out, reason="new reference", stage="references")
        log.info("references", f"Generated {ref_id}", path=str(out))
    return storyboard


def run_keyframes(
    storyboard: dict[str, Any],
    config: AppConfig,
    registry: ProviderRegistry,
    cache: ArtifactCache,
    log: RunLogger,
) -> dict[str, Any]:
    ref_paths = _reference_paths(storyboard)
    for shot in storyboard.get("shots", []):
        sid = shot["shot_id"]
        out = config.outputs_dir / "keyframes" / f"{sid}.png"
        fp = fingerprint(shot_keyframe_inputs(shot, ref_paths))
        key = f"keyframe:{sid}"
        cached = cache.lookup(key, fp)
        if cached:
            shot["keyframe_path"] = cached["path"]
            shot["generation_status"]["keyframe"] = "reused"
            log.info("images", f"Reused keyframe {sid}")
            continue
        result = registry.image.generate_image(
            shot["image_prompt"], out, config.vertical_width, config.vertical_height
        )
        if not result.success:
            raise RuntimeError(f"Keyframe {sid} failed: {result.message}")
        shot["keyframe_path"] = str(out)
        shot["generation_status"]["keyframe"] = "generated"
        cache.store(key, fp, out, reason="new keyframe", stage="images")
        log.info("images", f"Generated keyframe {sid}", path=str(out))
    return storyboard