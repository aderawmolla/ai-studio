"""Print a visible summary when the pipeline stops on an error."""

from __future__ import annotations

import sys
from pathlib import Path


def print_failure_summary(
    stage: str,
    reason: str,
    *,
    detail: str | None = None,
    logs_path: Path,
    resume_hint: str | None = None,
) -> None:
    lines = [
        "",
        "=" * 60,
        "PIPELINE STOPPED — NOT SUCCESSFUL",
        f"  Stage:  {stage}",
        f"  Reason: {reason}",
    ]
    if detail and detail.strip() and detail.strip() != reason.strip():
        lines.append(f"  Detail: {detail.strip()}")
    lines.extend(
        [
            f"  Log:    {logs_path}",
            "  More:   python3 main.py logs -n 15",
        ]
    )
    if resume_hint:
        lines.append(f"  Resume: {resume_hint}")
    lines.append("=" * 60)
    lines.append("")
    block = "\n".join(lines)
    print(block, file=sys.stderr)
    print(block)