"""Per-shot and combined narration."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from config import AppConfig
from core.cache import ArtifactCache
from core.dependency import fingerprint, shot_narration_inputs
from core.duration import film_duration
from core.logger import RunLogger
from core.errors import StageAbort
from core.registry import ProviderRegistry

# Brief pause after each line so the next shot does not feel stacked on the previous one.
NARRATION_TAIL_MARGIN_S = 0.25


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


def _pad_wav_to_duration(config: AppConfig, path: Path, target_seconds: float) -> None:
    actual = _probe_audio_duration(config, path)
    target = max(target_seconds, 0.1)
    if actual >= target - 0.03:
        return
    pad = target - actual
    tmp = path.with_suffix(".fit.wav")
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
    subprocess.run(cmd, check=True, capture_output=True)
    tmp.replace(path)


def _align_narration_to_shot(config: AppConfig, path: Path, shot: dict[str, Any]) -> bool:
    """Match storyboard slot to TTS length: extend duration when needed; never trim speech."""
    actual = _probe_audio_duration(config, path)
    target = float(shot["duration_seconds"])
    extended = False
    if actual + 0.05 > target:
        shot["duration_seconds"] = round(actual + NARRATION_TAIL_MARGIN_S, 1)
        target = float(shot["duration_seconds"])
        extended = True
    _pad_wav_to_duration(config, path, target)
    return extended


def _sync_film_duration_metadata(storyboard: dict[str, Any]) -> None:
    total = int(round(film_duration(storyboard)))
    storyboard["project"]["target_duration_seconds"] = total
    meta = storyboard["project"].get("music_metadata")
    if isinstance(meta, dict):
        meta["duration_seconds"] = total


def run_narration(
    storyboard: dict[str, Any],
    config: AppConfig,
    registry: ProviderRegistry,
    cache: ArtifactCache,
    log: RunLogger,
) -> dict[str, Any]:
    lang = storyboard["project"]["narration_language"]
    narration_paths: list[Path] = []
    extended_any = False
    shots = sorted(storyboard.get("shots", []), key=lambda s: s["shot_order"])
    for shot in shots:
        sid = shot["shot_id"]
        out = config.outputs_dir / "narration" / f"{sid}.wav"
        fp = fingerprint(shot_narration_inputs(shot, lang))
        key = f"narration:{sid}"
        cached = cache.lookup(key, fp)
        status = shot.setdefault("generation_status", {})
        if cached:
            shot["narration_path"] = cached["path"]
            status["narration"] = "reused"
            wav = Path(cached["path"])
            if _align_narration_to_shot(config, wav, shot):
                extended_any = True
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
        if _align_narration_to_shot(config, out, shot):
            extended_any = True
        shot["narration_path"] = str(out)
        status["narration"] = "generated"
        cache.store(key, fp, out, reason="new narration", stage="audio")
        narration_paths.append(out)
        log.info("audio", f"Narration {sid}", path=str(out))

    full_out = config.outputs_dir / "narration" / "full.wav"
    _concat_wavs(config, narration_paths, full_out)
    storyboard.setdefault("audio", {})["full_narration_path"] = str(full_out)
    if extended_any:
        _sync_film_duration_metadata(storyboard)
        log.info(
            "audio",
            "Shot durations extended to fit narration (no trim). Run: make videos && make subtitles && make assemble",
            target_seconds=storyboard["project"]["target_duration_seconds"],
        )
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