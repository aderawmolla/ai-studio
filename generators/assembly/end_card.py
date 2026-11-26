"""End card image: your file, FLUX prompt, or built-in placeholder."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from typing import TYPE_CHECKING

from config import AppConfig
from core.duration import END_CARD_SECONDS
from core.registry import ProviderRegistry
from providers.mock_media import make_png_placeholder, make_static_video_from_image

if TYPE_CHECKING:
    from core.logger import RunLogger


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


def _apply_disclosure_overlay(path: Path, disclosure: str, config: AppConfig) -> None:
    """Burn readable disclosure text (e.g. Made with AI) on the lower third."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return

    disclosure = (disclosure or "Made with AI").strip()
    if not disclosure:
        return

    img = Image.open(path).convert("RGBA")
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    bar_h = max(int(h * 0.12), 120)
    draw.rectangle([0, h - bar_h, w, h], fill=(0, 0, 0, 168))

    font = ImageFont.load_default()
    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ):
        try:
            font = ImageFont.truetype(candidate, size=max(int(w * 0.042), 36))
            break
        except OSError:
            continue

    bbox = draw.textbbox((0, 0), disclosure, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (w - tw) // 2
    y = h - bar_h + (bar_h - th) // 2
    draw.text((x, y), disclosure, fill=(245, 235, 210, 255), font=font)

    composed = Image.alpha_composite(img, overlay).convert("RGB")
    composed.save(path, format="PNG")


def _load_title_font(size: int):
    from PIL import ImageFont

    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    ):
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _placeholder(
    config: AppConfig,
    storyboard: dict[str, Any] | None = None,
    title: str = "",
) -> Path:
    """Fallback when FLUX/custom art is unavailable — title only (no logline wall of text)."""
    img = config.outputs_dir / "end_card" / "end_card.png"
    try:
        from PIL import Image, ImageDraw

        w, h = config.vertical_width, config.vertical_height
        img.parent.mkdir(parents=True, exist_ok=True)
        canvas = Image.new("RGB", (w, h), color=(92, 58, 38))
        draw = ImageDraw.Draw(canvas)
        for y in range(h):
            t = y / max(h - 1, 1)
            r = int(140 + 40 * (1 - t))
            g = int(88 + 35 * (1 - t))
            b = int(52 + 25 * (1 - t))
            draw.line([(0, y), (w, y)], fill=(r, g, b))
        project = (storyboard or {}).get("project", {})
        headline = (project.get("title") or title or "Heritage short")[:72]
        font = _load_title_font(max(int(w * 0.065), 48))
        bbox = draw.textbbox((0, 0), headline, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text(((w - tw) // 2, (h - th) // 2 - int(h * 0.06)), headline, fill=(245, 235, 210), font=font)
        canvas.save(img)
        return img
    except ImportError:
        make_png_placeholder(img, config.vertical_width, config.vertical_height, title)
        return img


def resolve_end_card_image(
    config: AppConfig,
    storyboard: dict[str, Any],
    registry: ProviderRegistry | None = None,
    log: "RunLogger | None" = None,
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
    disclosure = final.get("end_card_text") or "Made with AI"
    art_dest = config.outputs_dir / "end_card" / "end_card_art.png"

    custom = config.end_card_image or final.get("end_card_image_path")
    if custom:
        src = Path(custom).expanduser()
        if src.is_file():
            _fit_image_to_vertical(src, art_dest, config)
            shutil.copy2(art_dest, out)
            final["end_card_image_path"] = str(src.resolve())
            _apply_disclosure_overlay(out, disclosure, config)
            return out

    prompt = project.get("end_card_prompt")
    if prompt and registry and not config.use_mock_providers:
        result = registry.image.generate_image(
            prompt,
            art_dest,
            config.vertical_width,
            config.vertical_height,
        )
        if result.success and result.path and Path(result.path).is_file():
            shutil.copy2(result.path, out)
            _apply_disclosure_overlay(out, disclosure, config)
            if log:
                log.info("end-card", "End card art from FLUX", path=str(art_dest))
            return out
        if log:
            log.warn(
                "end-card",
                "FLUX end card failed — using fallback art",
                reason=result.message if not result.success else "no image file",
            )
        if art_dest.is_file():
            shutil.copy2(art_dest, out)
            _apply_disclosure_overlay(out, disclosure, config)
            if log:
                log.info("end-card", "Reused previous end_card_art.png")
            return out

    if art_dest.is_file():
        shutil.copy2(art_dest, out)
        _apply_disclosure_overlay(out, disclosure, config)
        if log:
            log.info("end-card", "Reused end_card_art.png (no new FLUX call)")
        return out

    if log:
        log.warn(
            "end-card",
            "Built-in placeholder end card (not FLUX hills)",
            hint="Retry later, set END_CARD_IMAGE in .env, or copy art to outputs/end_card/end_card_art.png",
        )
    path = _placeholder(config, storyboard, project.get("title", project.get("topic", "")))
    _apply_disclosure_overlay(path, disclosure, config)
    return path


def generate_end_card(config: AppConfig, title: str) -> Path:
    """Backward-compatible entry (placeholder only). Prefer resolve_end_card_image."""
    return _placeholder(config, None, title)


def end_card_png_path(config: AppConfig) -> Path:
    return config.outputs_dir / "end_card" / "end_card.png"


def end_card_clip_path(config: AppConfig) -> Path:
    return config.outputs_dir / "end_card" / "end_card.mp4"


def require_end_card_assets(
    config: AppConfig,
    storyboard: dict[str, Any],
) -> tuple[Path, Path]:
    """PNG + clip must exist from a prior `make end-card` run."""
    final = storyboard.setdefault("final", {})
    png = final.get("end_card_path")
    png_path = Path(png) if png else end_card_png_path(config)
    clip_path = end_card_clip_path(config)
    if not png_path.is_file():
        raise FileNotFoundError(
            f"Missing end card PNG ({png_path}). Generate first: make end-card"
        )
    if not clip_path.is_file():
        raise FileNotFoundError(
            f"Missing end card clip ({clip_path}). Generate first: make end-card"
        )
    final["end_card_path"] = str(png_path.resolve())
    final.setdefault("end_card_clip_path", str(clip_path.resolve()))
    return png_path, clip_path


def run_end_card(
    storyboard: dict[str, Any],
    config: AppConfig,
    registry: ProviderRegistry | None,
    log: "RunLogger",
) -> dict[str, Any]:
    """Pipeline stage: FLUX/placeholder PNG, disclosure overlay, and static MP4 clip."""
    path = resolve_end_card_image(config, storyboard, registry, log=log)
    clip = end_card_clip_path(config)
    make_static_video_from_image(config, path, clip, duration=END_CARD_SECONDS)
    final = storyboard.setdefault("final", {})
    final["end_card_path"] = str(path.resolve())
    final["end_card_clip_path"] = str(clip.resolve())
    log.info("end-card", "End card PNG + clip ready", path=str(path), clip=str(clip))
    return storyboard