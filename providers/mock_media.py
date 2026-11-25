"""Shared helpers to create placeholder media with FFmpeg and Pillow."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from config import AppConfig


def ensure_ffmpeg(config: AppConfig) -> str:
    exe = shutil.which(config.ffmpeg_path)
    if not exe:
        raise RuntimeError(f"FFmpeg not found: {config.ffmpeg_path}")
    return exe


def make_png_placeholder(path: Path, width: int, height: int, label: str) -> None:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise RuntimeError("Pillow required for mock images. pip install Pillow") from exc

    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (width, height), color=(45, 38, 32))
    draw = ImageDraw.Draw(img)
    text = label[:80]
    draw.rectangle([20, 20, width - 20, height - 20], outline=(180, 140, 90), width=4)
    draw.text((40, height // 2 - 10), text, fill=(230, 220, 200))
    img.save(path)


def make_silent_wav(path: Path, duration: float, sample_rate: int = 44100) -> None:
    import wave
    import struct

    path.parent.mkdir(parents=True, exist_ok=True)
    nframes = int(duration * sample_rate)
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        silence = struct.pack("<h", 0)
        wf.writeframes(silence * nframes)


def make_tone_wav(path: Path, duration: float, freq: float = 220.0) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg not found on PATH (needed for mock music)")
    cmd = [
        ffmpeg,
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"sine=frequency={freq}:duration={duration}:sample_rate=44100",
        "-ac",
        "1",
        "-af",
        "volume=0.15",
        str(path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def _ken_burns_filter(
    config: AppConfig,
    camera_movement: str,
    duration: float,
) -> str:
    """Build FFmpeg zoompan filter from storyboard camera_movement."""
    w, h, fps = config.vertical_width, config.vertical_height, config.fps
    frames = max(int(duration * fps), 1)
    cam = (camera_movement or "").lower()

    if any(k in cam for k in ("push", "dolly", "zoom in", "crane up")):
        z = "min(zoom+0.0012,1.25)"
        x = "iw/2-(iw/zoom/2)"
        y = "ih/2-(ih/zoom/2)"
    elif "orbit" in cam or "pan" in cam or "track" in cam:
        z = "1.08"
        x = "iw/2-(iw/zoom/2)+(on*2)"
        y = "ih/2-(ih/zoom/2)"
    elif "crane" in cam or "tilt" in cam:
        z = "1.08"
        x = "iw/2-(iw/zoom/2)"
        y = "ih/2-(ih/zoom/2)-(on*1.2)"
    else:
        z = "min(zoom+0.0008,1.18)"
        x = "iw/2-(iw/zoom/2)"
        y = "ih/2-(ih/zoom/2)"

    return (
        f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
        f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,"
        f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={w}x{h}:fps={fps}"
    )


def make_ken_burns_video(
    config: AppConfig,
    image_path: Path,
    output_path: Path,
    duration: float,
    camera_movement: str = "slow push in",
) -> None:
    """Visible motion on FLUX stills (assignment-accepted until Wan clips are wired)."""
    ffmpeg = ensure_ffmpeg(config)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    vf = _ken_burns_filter(config, camera_movement, duration)
    cmd = [
        ffmpeg,
        "-y",
        "-loop",
        "1",
        "-i",
        str(image_path),
        "-t",
        str(duration),
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(output_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def make_video_from_image(
    config: AppConfig,
    image_path: Path,
    output_path: Path,
    duration: float,
    camera_movement: str = "slow push in",
) -> None:
    """Delegate to Ken Burns so clips are never a single frozen frame."""
    make_ken_burns_video(config, image_path, output_path, duration, camera_movement)