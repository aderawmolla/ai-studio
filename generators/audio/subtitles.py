"""English SRT subtitles from shot metadata."""

from __future__ import annotations

from typing import Any

from config import AppConfig
from core.cache import ArtifactCache
from core.dependency import fingerprint, subtitles_inputs
from core.logger import RunLogger


def _format_ts(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def run_subtitles(
    storyboard: dict[str, Any],
    config: AppConfig,
    cache: ArtifactCache,
    log: RunLogger,
) -> dict[str, Any]:
    shots = sorted(storyboard.get("shots", []), key=lambda s: s["shot_order"])
    fp = fingerprint(subtitles_inputs(shots))
    key = "subtitles:en"
    out = config.outputs_dir / "subtitles" / "en.srt"
    cached = cache.lookup(key, fp)
    if cached:
        storyboard.setdefault("audio", {})["subtitles_path"] = cached["path"]
        log.info("audio", "Reused subtitles")
        return storyboard

    lines: list[str] = []
    t = 0.0
    for i, shot in enumerate(shots, start=1):
        dur = float(shot["duration_seconds"])
        lines.append(str(i))
        lines.append(f"{_format_ts(t)} --> {_format_ts(t + dur)}")
        lines.append(shot["subtitle_text_en"])
        lines.append("")
        t += dur
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    storyboard.setdefault("audio", {})["subtitles_path"] = str(out)
    cache.store(key, fp, out, reason="new subtitles", stage="audio")
    log.info("audio", "Generated subtitles", path=str(out))
    return storyboard