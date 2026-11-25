"""Per-shot and combined narration."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from config import AppConfig
from core.cache import ArtifactCache
from core.dependency import fingerprint, shot_narration_inputs
from core.logger import RunLogger
from core.errors import StageAbort
from core.registry import ProviderRegistry


def _probe_audio_duration(config: AppConfig, path: Path) -> float:
    cmd = [
        config.ffprobe_path,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def _fit_narration_to_shot(
    config: AppConfig, path: Path, target_seconds: float
) -> None:
    """Pad or trim WAV so each shot's audio matches storyboard clip length."""
    actual = _probe_audio_duration(config, path)
    target = max(target_seconds, 0.1)
    if abs(actual - target) < 0.05:
        return
    tmp = path.with_suffix(".fit.wav")
    if actual < target:
        pad = target - actual
        cmd = [
            config.ffmpeg_path,
            "-y",
            "-i",
            str(path),
            "-af",
            f"apad=pad_dur={pad:.3f}",
            "-t",
            f"{target:.3f}",
            str(tmp),
        ]
    else:
        cmd = [
            config.ffmpeg_path,
            "-y",
            "-i",
            str(path),
            "-t",
            f"{target:.3f}",
            "-c:a",
            "pcm_s16le",
            str(tmp),
        ]
    subprocess.run(cmd, check=True, capture_output=True)
    tmp.replace(path)


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
        status = shot.setdefault("generation_status", {})
        if not cached and out.is_file():
            try:
                if _probe_audio_duration(config, out) > 0.5:
                    _fit_narration_to_shot(config, out, float(shot["duration_seconds"]))
                    cache.store(key, fp, out, reason="reused existing wav", stage="audio")
                    shot["narration_path"] = str(out)
                    status["narration"] = "reused"
                    narration_paths.append(out)
                    log.info(
                        "audio",
                        f"Narration {sid} (reused file on disk, skipped API)",
                        path=str(out),
                    )
                    continue
            except (subprocess.CalledProcessError, ValueError):
                pass
        if cached:
            shot["narration_path"] = cached["path"]
            status["narration"] = "reused"
            wav = Path(cached["path"])
            _fit_narration_to_shot(config, wav, float(shot["duration_seconds"]))
            narration_paths.append(wav)
            continue
        log.info("audio", f"Generating narration {sid} (calling TTS API; please wait)")
        result = registry.tts.synthesize(
            shot["narration_text"], out, lang, float(shot["duration_seconds"])
        )
        if not result.success:
            log.error(
                "audio",
                f"Narration {sid} failed",
                reason=result.message,
                detail=result.detail or result.message,
                shot_id=sid,
            )
            raise StageAbort(result.message, result.detail or result.message)
        _fit_narration_to_shot(config, out, float(shot["duration_seconds"]))
        shot["narration_path"] = str(out)
        status["narration"] = "generated"
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