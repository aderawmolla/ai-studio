"""Structured run logging to console and logs/runs.jsonl."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class LogRecord:
    timestamp: str
    level: str
    stage: str
    message: str
    extra: dict[str, Any] | None = None


class RunLogger:
    def __init__(self, logs_dir: Path) -> None:
        self.logs_dir = logs_dir
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.jsonl_path = self.logs_dir / "runs.jsonl"

    def _write(self, record: LogRecord) -> None:
        line = json.dumps(asdict(record), ensure_ascii=False)
        with self.jsonl_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
        print(f"[{record.level}] {record.stage}: {record.message}", file=sys.stderr)

    def info(self, stage: str, message: str, **extra: Any) -> None:
        self._write(
            LogRecord(
                timestamp=datetime.now(timezone.utc).isoformat(),
                level="INFO",
                stage=stage,
                message=message,
                extra=extra or None,
            )
        )

    def error(self, stage: str, message: str, **extra: Any) -> None:
        self._write(
            LogRecord(
                timestamp=datetime.now(timezone.utc).isoformat(),
                level="ERROR",
                stage=stage,
                message=message,
                extra=extra or None,
            )
        )

    def warn(self, stage: str, message: str, **extra: Any) -> None:
        self._write(
            LogRecord(
                timestamp=datetime.now(timezone.utc).isoformat(),
                level="WARN",
                stage=stage,
                message=message,
                extra=extra or None,
            )
        )