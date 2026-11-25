"""FFmpeg assembly: concat clips, mix audio, burn subs, export 9:16 and reframed 16:9."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import Any

from config import AppConfig
from core.cache import ArtifactCache
from core.dependency import assembly_inputs, fingerprint
from core.logger import RunLogger
from core.duration import END_CARD_SECONDS, film_duration
from generators.assembly.end_card import generate_end_card


def run_assembly(
    storyboard: dict[str, Any],
    config: AppConfig,
    cache: ArtifactCache,
    log: RunLogger,
) -> dict[str, Any]:
    shots = sorted(storyboard.get("shots", []), key=lambda s: s["shot_order"])
    fp = fingerprint(assembly_inputs(storyboard, True, True))
    key = "assembly:final"
    v_out = config.final_vertical_path()
    h_out = config.final_horizontal_path()
    cached = cache.lookup(key, fp)
    if cached and v_out.is_file() and h_out.is_file():
        storyboard.setdefault("final", {})["vertical_path"] = str(v_out)
        storyboard.setdefault("final", {})["horizontal_path"] = str(h_out)
        log.info("assemble", "Reused final outputs")
        return storyboard

    end_card_img = generate_end_card(config, storyboard["project"]["topic"])
    storyboard.setdefault("final", {})["end_card_path"] = str(end_card_img)
    end_card_clip = config.outputs_dir / "end_card" / "end_card.mp4"
    from providers.mock_media import make_video_from_image

    make_video_from_image(config, end_card_img, end_card_clip, duration=END_CARD_SECONDS)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        concat_list = tmp_path / "clips.txt"
        clip_paths = [Path(s["clip_path"]) for s in shots if s.get("clip_path")]
        clip_paths.append(end_card_clip)
        concat_list.write_text("\n".join(f"file '{p.resolve()}'" for p in clip_paths), encoding="utf-8")
        merged_video = tmp_path / "merged.mp4"
        _ffmpeg_concat_video(config, concat_list, merged_video)

        music = Path(storyboard["audio"]["music_path"])
        narration = Path(storyboard["audio"]["full_narration_path"])
        mixed_audio = tmp_path / "mixed.wav"
        _mix_audio_ducked(config, music, narration, mixed_audio, storyboard)

        subs = Path(storyboard["audio"]["subtitles_path"])
        vertical = tmp_path / "vertical.mp4"
        duration = film_duration(storyboard)
        _mux_with_subs(
            config,
            merged_video,
            mixed_audio,
            subs,
            vertical,
            config.vertical_width,
            config.vertical_height,
            duration,
        )
        v_out.parent.mkdir(parents=True, exist_ok=True)
        vertical.rename(v_out)

        horizontal = tmp_path / "horizontal.mp4"
        _mux_horizontal_with_subs(
            config,
            merged_video,
            mixed_audio,
            subs,
            horizontal,
            config.horizontal_width,
            config.horizontal_height,
            duration,
        )
        horizontal.rename(h_out)

    storyboard.setdefault("final", {})["vertical_path"] = str(v_out)
    storyboard.setdefault("final", {})["horizontal_path"] = str(h_out)
    cache.store(key, fp, v_out, reason="assembled final", stage="assemble")
    log.info("assemble", "Exported vertical and horizontal finals", vertical=str(v_out), horizontal=str(h_out))
    return storyboard


def _ffmpeg_concat_video(config: AppConfig, list_file: Path, output: Path) -> None:
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


def _mix_audio_ducked(
    config: AppConfig,
    music: Path,
    narration: Path,
    output: Path,
    storyboard: dict[str, Any],
) -> None:
    """Sidechain-style ducking: lower music volume under narration timeline."""
    total = film_duration(storyboard)
    cmd = [
        config.ffmpeg_path,
        "-y",
        "-i",
        str(music),
        "-i",
        str(narration),
        "-filter_complex",
        (
            f"[0:a]volume=0.25,apad=pad_dur={total}[m];"
            f"[1:a]volume=1.0,apad=pad_dur={total}[n];"
            f"[m][n]amix=inputs=2:duration=longest:dropout_transition=0"
        ),
        "-t",
        str(total),
        str(output),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def _mux_with_subs(
    config: AppConfig,
    video: Path,
    audio: Path,
    subs: Path,
    output: Path,
    width: int,
    height: int,
    duration_seconds: float,
) -> None:
    subs_esc = subs.resolve().as_posix().replace(":", r"\:")
    vf = f"scale={width}:{height},subtitles={subs_esc}"
    cmd = [
        config.ffmpeg_path,
        "-y",
        "-i",
        str(video),
        "-i",
        str(audio),
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-t",
        str(duration_seconds),
        str(output),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def _mux_horizontal_with_subs(
    config: AppConfig,
    video: Path,
    audio: Path,
    subs: Path,
    output: Path,
    width: int,
    height: int,
    duration_seconds: float,
) -> None:
    """16:9 reframe + burn subtitles (same audio length as vertical)."""
    subs_esc = subs.resolve().as_posix().replace(":", r"\:")
    vf = (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},"
        f"subtitles={subs_esc}"
    )
    cmd = [
        config.ffmpeg_path,
        "-y",
        "-i",
        str(video),
        "-i",
        str(audio),
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-t",
        str(duration_seconds),
        str(output),
    ]
    subprocess.run(cmd, check=True, capture_output=True)