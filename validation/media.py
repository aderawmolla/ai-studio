"""Pre-assembly media validation."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from config import AppConfig


@dataclass
class MediaValidationReport:
    ok: bool
    errors: list[str]
    warnings: list[str]


def _ffprobe_duration(config: AppConfig, path: Path) -> float | None:
    try:
        cmd = [
            config.ffprobe_path,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(path),
        ]
        out = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(out.stdout)
        return float(data["format"]["duration"])
    except (subprocess.CalledProcessError, KeyError, ValueError, json.JSONDecodeError):
        return None


def validate_media(storyboard: dict[str, Any], config: AppConfig) -> MediaValidationReport:
    errors: list[str] = []
    warnings: list[str] = []

    for shot in storyboard.get("shots", []):
        sid = shot["shot_id"]
        for field, label in (("keyframe_path", "keyframe"), ("clip_path", "clip"), ("narration_path", "narration")):
            p = shot.get(field)
            if not p:
                errors.append(f"{sid}: missing {label}")
                continue
            path = Path(p)
            if not path.is_file():
                errors.append(f"{sid}: {label} file not found: {p}")

        clip = shot.get("clip_path")
        if clip and Path(clip).is_file():
            dur = _ffprobe_duration(config, Path(clip))
            expected = float(shot["duration_seconds"])
            if dur is not None and abs(dur - expected) > 1.5:
                warnings.append(f"{sid}: clip duration {dur:.1f}s vs expected {expected:.1f}s")

    audio = storyboard.get("audio", {})
    for key in ("music_path", "full_narration_path", "subtitles_path"):
        p = audio.get(key)
        if not p:
            errors.append(f"audio.{key} missing")
        elif not Path(p).is_file():
            errors.append(f"audio.{key} not found: {p}")

    final = storyboard.get("final", {})
    end_png = final.get("end_card_path") or str(config.outputs_dir / "end_card" / "end_card.png")
    end_clip = final.get("end_card_clip_path") or str(config.outputs_dir / "end_card" / "end_card.mp4")
    if not Path(end_png).is_file():
        errors.append(f"end card PNG missing (run: make end-card): {end_png}")
    if not Path(end_clip).is_file():
        errors.append(f"end card clip missing (run: make end-card): {end_clip}")

    return MediaValidationReport(ok=not errors, errors=errors, warnings=warnings)