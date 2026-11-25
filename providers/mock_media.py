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
    import math
    import wave
    import struct

    path.parent.mkdir(parents=True, exist_ok=True)
    sample_rate = 44100
    nframes = int(duration * sample_rate)
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for i in range(nframes):
            t = i / sample_rate
            amp = 0.15 * math.sin(2 * math.pi * freq * t)
            frames.extend(struct.pack("<h", int(amp * 32767)))
        wf.writeframes(frames)


def make_video_from_image(
    config: AppConfig,
    image_path: Path,
    output_path: Path,
    duration: float,
) -> None:
    ffmpeg = ensure_ffmpeg(config)
    output_path.parent.mkdir(parents=True, exist_ok=True)
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
        f"scale={config.vertical_width}:{config.vertical_height}:force_original_aspect_ratio=decrease,"
        f"pad={config.vertical_width}:{config.vertical_height}:(ow-iw)/2:(oh-ih)/2",
        "-r",
        str(config.fps),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(output_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)