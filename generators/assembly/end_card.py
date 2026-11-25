"""End card image: your file, FLUX prompt, or built-in placeholder."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from config import AppConfig
from core.registry import ProviderRegistry
from providers.mock_media import make_png_placeholder


def _fit_image_to_vertical(src: Path, dest: Path, config: AppConfig) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image

        img = Image.open(src).convert("RGB")
        w, h = config.vertical_width, config.vertical_height
        img = img.resize((w, h), Image.Resampling.LANCZOS)
        img.save(dest, format="PNG")
    except ImportError:
        shutil.copy2(src, dest)


def _placeholder(
    config: AppConfig,
    storyboard: dict[str, Any] | None = None,
    title: str = "",
) -> Path:
    img = config.outputs_dir / "end_card" / "end_card.png"
    try:
        from PIL import Image, ImageDraw

        w, h = config.vertical_width, config.vertical_height
        img.parent.mkdir(parents=True, exist_ok=True)
        canvas = Image.new("RGB", (w, h), color=(18, 16, 14))
        draw = ImageDraw.Draw(canvas)
        margin = 64
        draw.rectangle([margin, margin, w - margin, h - margin], outline=(180, 140, 90), width=6)
        project = (storyboard or {}).get("project", {})
        final = (storyboard or {}).get("final", {})
        closing = (storyboard or {}).get("closing_line", {})
        headline = (project.get("title") or title or "Heritage short")[:72]
        tagline = (closing.get("text") or project.get("logline") or "")[:120]
        disclosure = final.get("end_card_text") or "Made with AI"
        lines = [headline]
        if tagline:
            lines.append(tagline)
        lines.append(disclosure)
        y = h // 2 - len(lines) * 40
        for line in lines:
            draw.text((margin + 24, y), line, fill=(235, 225, 205))
            y += 80
        canvas.save(img)
        return img
    except ImportError:
        make_png_placeholder(img, config.vertical_width, config.vertical_height, title)
        return img


def resolve_end_card_image(
    config: AppConfig,
    storyboard: dict[str, Any],
    registry: ProviderRegistry | None = None,
) -> Path:
    """
    Priority:
    1. END_CARD_IMAGE env or storyboard.final.end_card_image_path (your own image)
    2. FLUX via project.end_card_prompt when USE_MOCK_PROVIDERS=false
    3. Simple placeholder PNG
    """
    out = config.outputs_dir / "end_card" / "end_card.png"
    project = storyboard.get("project", {})
    final = storyboard.setdefault("final", {})

    custom = config.end_card_image or final.get("end_card_image_path")
    if custom:
        src = Path(custom).expanduser()
        if src.is_file():
            _fit_image_to_vertical(src, out, config)
            final["end_card_image_path"] = str(src.resolve())
            return out

    prompt = project.get("end_card_prompt")
    if prompt and registry and not config.use_mock_providers:
        result = registry.image.generate_image(
            prompt,
            out,
            config.vertical_width,
            config.vertical_height,
        )
        if result.success and result.path:
            return result.path

    return _placeholder(config, storyboard, project.get("title", project.get("topic", "")))


def generate_end_card(config: AppConfig, title: str) -> Path:
    """Backward-compatible entry (placeholder only). Prefer resolve_end_card_image."""
    return _placeholder(config, None, title)