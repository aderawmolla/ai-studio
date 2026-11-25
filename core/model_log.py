"""Append assignment-style model call lines to logs/runs.jsonl."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def log_model_call(
    logs_dir: Path,
    *,
    stage: str,
    model: str,
    latency_ms: float,
    success: bool,
    parameters: dict[str, Any] | None = None,
    cost_usd: float | None = None,
    seed: int | str | None = None,
    message: str = "model call",
) -> None:
    logs_dir.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": "INFO" if success else "ERROR",
        "stage": stage,
        "message": message,
        "extra": {
            "type": "model_call",
            "model": model,
            "latency_ms": round(latency_ms, 2),
            "success": success,
            "parameters": parameters or {},
            "cost_usd": cost_usd,
            "seed": seed,
        },
    }
    with (logs_dir / "runs.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")