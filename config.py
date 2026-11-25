"""Application configuration loaded from environment and defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

try:
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env", override=False)
except ImportError:
    pass


def _env_bool(key: str, default: bool) -> bool:
    val = os.getenv(key)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


@dataclass
class AppConfig:
    root: Path = PROJECT_ROOT
    storyboard_path: Path = field(default_factory=lambda: PROJECT_ROOT / "storyboard.json")
    schema_path: Path = field(
        default_factory=lambda: PROJECT_ROOT / "schemas" / "storyboard.schema.json"
    )
    outputs_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "outputs")
    cache_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "cache")
    logs_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "logs")

    use_mock_providers: bool = True
    gemini_api_key: str | None = None
    gemini_model: str | None = None
    cloudflare_account_id: str | None = None
    cloudflare_api_token: str | None = None
    cloudflare_flux_model: str | None = None
    flux_api_key: str | None = None  # fallback alias for cloudflare token
    wan_api_url: str | None = None
    tts_provider: str = "mock"
    ace_step_url: str | None = None
    kaggle_username: str | None = None
    kaggle_key: str | None = None
    kaggle_api_token: str | None = None

    vertical_width: int = 1080
    vertical_height: int = 1920
    horizontal_width: int = 1920
    horizontal_height: int = 1080
    fps: int = 24
    ffmpeg_path: str = "ffmpeg"
    ffprobe_path: str = "ffprobe"

    api_retry_max: int = 3
    api_timeout_seconds: int = 120
    final_vertical_filename: str = "heritage_vertical.mp4"
    final_horizontal_filename: str = "heritage_horizontal.mp4"

    def final_vertical_path(self) -> Path:
        return self.outputs_dir / "final" / self.final_vertical_filename

    def final_horizontal_path(self) -> Path:
        return self.outputs_dir / "final" / self.final_horizontal_filename

    @classmethod
    def from_env(cls) -> AppConfig:
        root = Path(os.getenv("HERITAGE_ROOT", str(PROJECT_ROOT)))
        return cls(
            root=root,
            storyboard_path=Path(os.getenv("STORYBOARD_PATH", str(root / "storyboard.json"))),
            schema_path=Path(
                os.getenv("STORYBOARD_SCHEMA", str(root / "schemas" / "storyboard.schema.json"))
            ),
            outputs_dir=Path(os.getenv("OUTPUTS_DIR", str(root / "outputs"))),
            cache_dir=Path(os.getenv("CACHE_DIR", str(root / "cache"))),
            logs_dir=Path(os.getenv("LOGS_DIR", str(root / "logs"))),
            use_mock_providers=_env_bool("USE_MOCK_PROVIDERS", True),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            gemini_model=os.getenv("GEMINI_MODEL"),
            cloudflare_account_id=os.getenv("CLOUDFLARE_ACCOUNT_ID"),
            cloudflare_api_token=os.getenv("CLOUDFLARE_API_TOKEN") or os.getenv("FLUX_API_KEY"),
            cloudflare_flux_model=os.getenv("CLOUDFLARE_FLUX_MODEL"),
            flux_api_key=os.getenv("FLUX_API_KEY") or os.getenv("CLOUDFLARE_API_TOKEN"),
            wan_api_url=os.getenv("WAN_API_URL"),
            tts_provider=os.getenv("TTS_PROVIDER", "mock"),
            ace_step_url=os.getenv("ACE_STEP_URL"),
            kaggle_username=os.getenv("KAGGLE_USERNAME"),
            kaggle_key=os.getenv("KAGGLE_KEY"),
            kaggle_api_token=os.getenv("KAGGLE_API_TOKEN"),
            vertical_width=int(os.getenv("VERTICAL_WIDTH", "1080")),
            vertical_height=int(os.getenv("VERTICAL_HEIGHT", "1920")),
            horizontal_width=int(os.getenv("HORIZONTAL_WIDTH", "1920")),
            horizontal_height=int(os.getenv("HORIZONTAL_HEIGHT", "1080")),
            fps=int(os.getenv("OUTPUT_FPS", "24")),
            ffmpeg_path=os.getenv("FFMPEG_PATH", "ffmpeg"),
            ffprobe_path=os.getenv("FFPROBE_PATH", "ffprobe"),
            api_retry_max=int(os.getenv("API_RETRY_MAX", "3")),
            api_timeout_seconds=int(os.getenv("API_TIMEOUT_SECONDS", "120")),
            final_vertical_filename=os.getenv("FILM_OUTPUT_VERTICAL", "heritage_vertical.mp4"),
            final_horizontal_filename=os.getenv(
                "FILM_OUTPUT_HORIZONTAL", "heritage_horizontal.mp4"
            ),
        )

    def ensure_dirs(self) -> None:
        for name in (
            "references",
            "keyframes",
            "clips",
            "narration",
            "music",
            "subtitles",
            "final",
            "end_card",
        ):
            (self.outputs_dir / name).mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


def load_config() -> AppConfig:
    cfg = AppConfig.from_env()
    cfg.ensure_dirs()
    return cfg