"""Per-shot and combined narration."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from config import AppConfig
from core.cache import ArtifactCache
from core.dependency import fingerprint, shot_narration_inputs
from core.logger import RunLogger
from core.registry import ProviderRegistry


def run_narration(
    storyboard: dict[str, Any],
    config: AppConfig,
    registry: ProviderRegistry,
    cache: ArtifactCache,
    log: RunLogger,
) -> dict[str, Any]:
    lang = storyboard["project"]["narration_language"]
    narration_paths: list[Path] = []
    for shot in storyboard.get("shots", []):
        sid = shot["shot_id"]
        out = config.outputs_dir / "narration" / f"{sid}.wav"
        fp = fingerprint(shot_narration_inputs(shot, lang))
        key = f"narration:{sid}"
        cached = cache.lookup(key, fp)
        if cached:
            shot["narration_path"] = cached["path"]
            shot["generation_status"]["narration"] = "reused"
            narration_paths.append(Path(cached["path"]))
            continue
        result = registry.tts.synthesize(
            shot["narration_text"], out, lang, float(shot["duration_seconds"])
        )
        if not result.success:
            raise RuntimeError(f"Narration {sid} failed: {result.message}")
        shot["narration_path"] = str(out)
        shot["generation_status"]["narration"] = "generated"
        cache.store(key, fp, out, reason="new narration", stage="audio")
        narration_paths.append(out)
        log.info("audio", f"Narration {sid}", path=str(out))

    full_out = config.outputs_dir / "narration" / "full.wav"
    _concat_wavs(config, narration_paths, full_out)
    storyboard.setdefault("audio", {})["full_narration_path"] = str(full_out)
    return storyboard


def _concat_wavs(config: AppConfig, paths: list[Path], output: Path) -> None:
    if not paths:
        raise RuntimeError("No narration segments to concatenate")
    output.parent.mkdir(parents=True, exist_ok=True)
    list_file = output.parent / "_concat_list.txt"
    lines = [f"file '{p.resolve()}'" for p in paths]
    list_file.write_text("\n".join(lines), encoding="utf-8")
    cmd = [
        config.ffmpeg_path,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_file),
        "-c",
        "copy",
        str(output),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    list_file.unlink(missing_ok=True)