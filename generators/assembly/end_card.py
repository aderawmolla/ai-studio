"""AI end card placeholder (mock: static image + short clip segment)."""

from __future__ import annotations

from pathlib import Path

from config import AppConfig
from providers.mock_media import make_png_placeholder, make_video_from_image


def generate_end_card(config: AppConfig, title: str) -> Path:
    img = config.outputs_dir / "end_card" / "end_card.png"
    make_png_placeholder(img, config.vertical_width, config.vertical_height, f"AI-generated end card\n{title}")
    return img