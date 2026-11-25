"""Turn raw provider / SDK errors into short, actionable messages."""

from __future__ import annotations

import re
from typing import Any


def explain_api_error(exc: BaseException | str) -> str:
    """Short headline for what went wrong (console + logs)."""
    return parse_api_error(exc)[0]


def parse_api_error(exc: BaseException | str) -> tuple[str, str]:
    """(headline reason, technical detail) from a provider or SDK exception."""
    text = str(exc).strip()
    lower = text.lower()
    detail = technical_detail(exc)

    code = _http_code(text)
    status = _grpc_status(text)

    if code == 429 or "too many requests" in lower or "rate limit" in lower:
        return (
            "API rate limit (HTTP 429). Free tier or trial may be throttling you—"
            "wait, retry later, or check billing.",
            detail,
        )

    if (
        code in (402, 403)
        or "resource_exhausted" in lower
        or "quota" in lower
        or "billing" in lower
        or "exceeded" in lower and "quota" in lower
    ):
        return (
            "API quota or billing limit. Key may be out of credits or daily quota—"
            "check Google AI Studio / Cloudflare billing.",
            detail,
        )

    if code == 401 or "invalid api key" in lower or "unauthorized" in lower:
        return (
            "Invalid or missing API credentials (HTTP 401). Run: python3 main.py doctor",
            detail,
        )

    if code == 400 or status == "invalid_argument":
        return (
            "Invalid API request (HTTP 400). Often wrong model name or request fields.",
            detail,
        )

    if "timeout" in lower or "timed out" in lower:
        return ("API request timed out.", detail)

    if "temporaryerror" in lower and "429" in text:
        return parse_api_error("429 Too Many Requests")

    return (_short_detail(text, max_len=200), detail)


def technical_detail(exc: BaseException | str, max_len: int = 800) -> str:
    return _short_detail(str(exc).strip(), max_len=max_len)


def _http_code(text: str) -> int | None:
    m = re.search(r"\b([1-5]\d{2})\b", text)
    if not m:
        return None
    try:
        return int(m.group(1))
    except ValueError:
        return None


def _grpc_status(text: str) -> str | None:
    m = re.search(r"'status':\s*'([A-Z_]+)'", text)
    return m.group(1).lower() if m else None


def _short_detail(text: str, max_len: int = 220) -> str:
    one = " ".join(text.split())
    if len(one) <= max_len:
        return one
    return one[: max_len - 3] + "..."