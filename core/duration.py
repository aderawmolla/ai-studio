"""Shared timeline length (shots + end card)."""

from __future__ import annotations

from typing import Any

END_CARD_SECONDS = 4.0


def shots_duration(storyboard: dict[str, Any]) -> float:
    return sum(float(s["duration_seconds"]) for s in storyboard.get("shots", []))


def film_duration(storyboard: dict[str, Any]) -> float:
    return shots_duration(storyboard) + END_CARD_SECONDS