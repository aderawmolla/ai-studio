"""Final deliverable validation."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from config import AppConfig


@dataclass
class FinalCheckReport:
    ok: bool
    vertical: dict[str, Any] | None
    horizontal: dict[str, Any] | None
    errors: list[str]


def _probe_video(config: AppConfig, path: Path) -> dict[str, Any] | None:
    cmd = [
        config.ffprobe_path,
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height,duration",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(path),
    ]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(out.stdout)
        stream = data.get("streams", [{}])[0]
        fmt = data.get("format", {})
        duration = float(stream.get("duration") or fmt.get("duration") or 0)
        return {
            "width": int(stream.get("width", 0)),
            "height": int(stream.get("height", 0)),
            "duration": duration,
        }
    except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError):
        return None


def validate_final_outputs(storyboard: dict[str, Any], config: AppConfig) -> FinalCheckReport:
    errors: list[str] = []
    final = storyboard.get("final", {})
    v_path = final.get("vertical_path")
    h_path = final.get("horizontal_path")

    v_info = None
    h_info = None

    if not v_path or not Path(v_path).is_file():
        errors.append("Missing vertical final MP4")
    else:
        v_info = _probe_video(config, Path(v_path))
        if not v_info:
            errors.append("Could not probe vertical video")
        else:
            if abs(v_info["width"] / v_info["height"] - 9 / 16) > 0.05:
                errors.append(f"Vertical aspect mismatch: {v_info['width']}x{v_info['height']}")
            if v_info["duration"] < 60 or v_info["duration"] > 90:
                errors.append(f"Vertical duration {v_info['duration']:.1f}s outside 60-90s")

    if not h_path or not Path(h_path).is_file():
        errors.append("Missing horizontal final MP4")
    else:
        h_info = _probe_video(config, Path(h_path))
        if not h_info:
            errors.append("Could not probe horizontal video")
        else:
            if abs(h_info["width"] / h_info["height"] - 16 / 9) > 0.05:
                errors.append(f"Horizontal aspect mismatch: {h_info['width']}x{h_info['height']}")
            if h_info["duration"] < 60 or h_info["duration"] > 90:
                errors.append(f"Horizontal duration {h_info['duration']:.1f}s outside 60-90s")

    end_card = final.get("end_card_path")
    if not end_card or not Path(end_card).is_file():
        errors.append("Missing end card asset")

    subs = storyboard.get("audio", {}).get("subtitles_path")
    if not subs or not Path(subs).is_file():
        errors.append("Missing subtitles file for final validation evidence")

    return FinalCheckReport(ok=not errors, vertical=v_info, horizontal=h_info, errors=errors)


def write_report(path: Path, report: FinalCheckReport) -> None:
    path.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")