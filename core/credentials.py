"""Check which credentials are present (never print secret values)."""

from __future__ import annotations

from dataclasses import dataclass

from config import AppConfig


@dataclass
class CredentialRow:
    name: str
    purpose_plain: str
    set: bool
    used_by_pipeline_today: str


def credential_report(config: AppConfig) -> list[CredentialRow]:
    kaggle_any = bool(
        config.kaggle_api_token
        or (config.kaggle_username and config.kaggle_key)
    )
    return [
        CredentialRow(
            "GEMINI_API_KEY",
            "Writes the story and speaks your narration (your language).",
            bool(config.gemini_api_key),
            "Soon (TTS/story); still mock until wired",
        ),
        CredentialRow(
            "CLOUDFLARE_*",
            "Creates still pictures: character sheet + one image per shot.",
            bool(config.cloudflare_account_id and config.cloudflare_api_token),
            "Soon (FLUX); still mock until wired",
        ),
        CredentialRow(
            "KAGGLE_API_TOKEN (or USERNAME+KEY)",
            "Proves who you are on Kaggle so you can open GPU notebooks for video + music.",
            kaggle_any,
            "You, in the browser/notebook — not auto-called by run_film.py yet",
        ),
        CredentialRow(
            "WAN_API_URL",
            "Only if you build a video server; most students skip this and use Kaggle manually.",
            bool(config.wan_api_url),
            "Optional",
        ),
        CredentialRow(
            "ACE_STEP_URL",
            "Only if you build a music server; most students skip this and use Kaggle manually.",
            bool(config.ace_step_url),
            "Optional",
        ),
        CredentialRow(
            "USE_MOCK_PROVIDERS",
            "true = fake pictures/sounds on your laptop (fast test). false = try real APIs.",
            True,
            f"currently mock={config.use_mock_providers}",
        ),
    ]


def format_credential_report(config: AppConfig) -> str:
    rows = credential_report(config)
    lines = [
        "Credential check (values are never shown)",
        "=" * 50,
    ]
    for r in rows:
        mark = "OK" if r.set else "missing"
        lines.append(f"[{mark:7}] {r.name}")
        lines.append(f"         Why: {r.purpose_plain}")
        lines.append(f"         Pipeline: {r.used_by_pipeline_today}")
        lines.append("")
    lines.append("Next: python3 main.py doctor --kaggle   (test Kaggle token if set)")
    return "\n".join(lines)


def verify_kaggle_token(token: str) -> tuple[bool, str]:
    """Light check: call Kaggle env auth if kaggle package installed."""
    if not token or not token.strip():
        return False, "KAGGLE_API_TOKEN not set in .env"
    try:
        import os

        os.environ["KAGGLE_API_TOKEN"] = token.strip()
        from kaggle.api.kaggle_api_extended import KaggleApi

        api = KaggleApi()
        api.authenticate()
        # minimal call
        api.competitions_list(max_size=1)
        return True, "Kaggle token accepted (API reachable)."
    except ImportError:
        return False, "Install kaggle package: pip install kaggle"
    except Exception as exc:
        return False, f"Kaggle auth failed: {exc}"