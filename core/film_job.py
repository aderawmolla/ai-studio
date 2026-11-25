"""Prepare a named film run: topic + output filename + optional real-AI mode."""

from __future__ import annotations

import os
import re
from pathlib import Path

from validation.storyboard import load_storyboard, save_storyboard


def _safe_filename(name: str) -> str:
    name = name.strip()
    if not name.lower().endswith(".mp4"):
        name += ".mp4"
    base = Path(name).name
    base = re.sub(r"[^\w.\-]+", "_", base)
    return base or "heritage.mp4"


def configure_film_job(
    *,
    topic: str,
    output_mp4: str,
    storyboard_path: Path,
    use_real: bool = False,
    fresh: bool = False,
    cache_dir: Path,
) -> tuple[str, str]:
    """
    Set env for output names, update storyboard topic, optionally enable real providers.
    Returns (vertical_filename, horizontal_filename).
    """
    vertical = _safe_filename(output_mp4)
    stem = Path(vertical).stem
    horizontal = f"{stem}_16x9.mp4"

    os.environ["FILM_OUTPUT_VERTICAL"] = vertical
    os.environ["FILM_OUTPUT_HORIZONTAL"] = horizontal

    if use_real:
        os.environ["USE_MOCK_PROVIDERS"] = "false"
        if not os.getenv("TTS_PROVIDER") or os.getenv("TTS_PROVIDER", "").lower() == "mock":
            os.environ["TTS_PROVIDER"] = "gemini"

    data = load_storyboard(storyboard_path)
    project = data.setdefault("project", {})
    project["topic"] = topic.strip()
    project.setdefault(
        "music_prompt",
        f"Instrumental heritage documentary score inspired by {topic}, warm, meditative, no vocals",
    )
    data.setdefault("metadata", {})["film_output"] = vertical
    save_storyboard(storyboard_path, data)

    if fresh:
        index = cache_dir / "index.json"
        if index.is_file():
            index.unlink()

    return vertical, horizontal


def print_film_banner(topic: str, vertical: str, horizontal: str, use_real: bool) -> None:
    mode = "REAL AI (FLUX + Gemini TTS + FFmpeg clips)" if use_real else "MOCK providers"
    print(f"\n=== Make film: {topic!r} ===")
    print(f"Mode: {mode}")
    print(f"Output (9:16):  outputs/final/{vertical}")
    print(f"Output (16:9):  outputs/final/{horizontal}")
    if use_real:
        print("Note: Video motion = Ken Burns on FLUX stills unless WAN_API_URL is set (Wan on Kaggle).")
    print()