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

    def _console_lines(self, record: LogRecord) -> list[str]:
        lines = [f"[{record.level}] {record.stage}: {record.message}"]
        extra = record.extra or {}
        reason = extra.get("reason")
        detail = extra.get("detail")
        if record.level == "ERROR":
            if reason:
                lines.append(f"  Reason: {reason}")
            if detail:
                wrapped = _wrap_detail(str(detail), width=96)
                for i, chunk in enumerate(wrapped):
                    prefix = "  Detail: " if i == 0 else "          "
                    lines.append(f"{prefix}{chunk}")
        return lines

    def _write(self, record: LogRecord) -> None:
        line = json.dumps(asdict(record), ensure_ascii=False)
        with self.jsonl_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
        for out_line in self._console_lines(record):
            print(out_line, file=sys.stderr, flush=True)
            if record.level == "ERROR":
                print(out_line, flush=True)

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


def _wrap_detail(text: str, width: int = 96) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current: list[str] = []
    length = 0
    for word in words:
        add = len(word) + (1 if current else 0)
        if length + add > width and current:
            lines.append(" ".join(current))
            current = [word]
            length = len(word)
        else:
            current.append(word)
            length += add
    if current:
        lines.append(" ".join(current))
    return lines