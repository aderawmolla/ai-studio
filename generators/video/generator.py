"""Per-shot video clips from keyframes."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from config import AppConfig
from core.cache import ArtifactCache
from core.dependency import fingerprint, shot_video_inputs
from core.logger import RunLogger
from core.registry import ProviderRegistry


def run_videos(
    storyboard: dict[str, Any],
    config: AppConfig,
    registry: ProviderRegistry,
    cache: ArtifactCache,
    log: RunLogger,
) -> dict[str, Any]:
    for shot in storyboard.get("shots", []):
        sid = shot["shot_id"]
        kf = shot.get("keyframe_path")
        if not kf:
            raise RuntimeError(f"Shot {sid} missing keyframe before video generation")
        out = config.outputs_dir / "clips" / f"{sid}.mp4"
        fp = fingerprint(shot_video_inputs(shot, kf))
        key = f"clip:{sid}"
        cached = cache.lookup(key, fp)
        status = shot.setdefault("generation_status", {})
        if cached:
            shot["clip_path"] = cached["path"]
            status["video"] = "reused"
            log.info("videos", f"Reused clip {sid}")
            continue
        result = registry.video.generate_clip(
            Path(kf),
            shot["video_prompt"],
            out,
            float(shot["duration_seconds"]),
            config.fps,
            shot.get("camera_movement", "slow push in"),
        )
        if not result.success:
            raise RuntimeError(f"Video {sid} failed: {result.message}")
        shot["clip_path"] = str(out)
        status["video"] = "generated"
        cache.store(key, fp, out, reason="new clip", stage="videos")
        log.info("videos", f"Generated clip {sid}", path=str(out))
    return storyboard