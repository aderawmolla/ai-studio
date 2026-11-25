"""Simple log management for runs.jsonl."""

from __future__ import annotations

import json
from pathlib import Path


def tail_runs_jsonl(path: Path, n: int = 30) -> str:
    if not path.is_file():
        return f"No log file yet at {path}. Run python3 run_film.py first."

    lines = path.read_text(encoding="utf-8").splitlines()
    tail = lines[-n:] if len(lines) > n else lines
    out: list[str] = [f"Last {len(tail)} entries from {path}", "=" * 50]
    for line in tail:
        try:
            rec = json.loads(line)
            ts = rec.get("timestamp", "")[:19]
            level = rec.get("level", "?")
            stage = rec.get("stage", "?")
            msg = rec.get("message", "")
            out.append(f"{ts} | {level:5} | {stage:16} | {msg}")
        except json.JSONDecodeError:
            out.append(line)
    return "\n".join(out)


def count_log_levels(path: Path) -> str:
    if not path.is_file():
        return "Log file empty or missing."
    counts = {"INFO": 0, "WARN": 0, "ERROR": 0}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
            lvl = rec.get("level", "INFO")
            counts[lvl] = counts.get(lvl, 0) + 1
        except json.JSONDecodeError:
            pass
    total = sum(counts.values())
    return f"runs.jsonl: {total} lines — INFO {counts.get('INFO',0)}, WARN {counts.get('WARN',0)}, ERROR {counts.get('ERROR',0)}"