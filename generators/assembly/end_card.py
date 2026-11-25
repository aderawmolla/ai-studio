"""AI end card placeholder (mock: static image + short clip segment)."""

from __future__ import annotations

from pathlib import Path

from config import AppConfig
from providers.mock_media import make_png_placeholder


def generate_end_card(config: AppConfig, title: str) -> Path:
    img = config.outputs_dir / "end_card" / "end_card.png"
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        make_png_placeholder(img, config.vertical_width, config.vertical_height, title)
        return img

    w, h = config.vertical_width, config.vertical_height
    img.parent.mkdir(parents=True, exist_ok=True)
    canvas = Image.new("RGB", (w, h), color=(18, 16, 14))
    draw = ImageDraw.Draw(canvas)
    margin = 64
    draw.rectangle([margin, margin, w - margin, h - margin], outline=(180, 140, 90), width=6)
    topic = (title or "Heritage")[:72]
    lines = ["A short heritage film", topic, "Created with AI-assisted production"]
    y = h // 2 - len(lines) * 36
    for line in lines:
        draw.text((margin + 24, y), line, fill=(235, 225, 205))
        y += 72
    canvas.save(img)
    return img