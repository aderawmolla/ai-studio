"""Human-readable pipeline progress from storyboard + filesystem."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from validation.storyboard import load_storyboard


@dataclass
class TaskStatus:
    stage: str
    description: str
    done: bool
    detail: str


STAGE_TASKS: list[tuple[str, str, str]] = [
    ("validate", "Storyboard valid", "JSON schema + 60–90s duration"),
    ("story", "Story / script", "Narration lines in storyboard"),
    ("references", "Reference images", "Character & location sheets"),
    ("images", "Keyframes", "One still per shot"),
    ("videos", "Moving shots", "One clip per shot"),
    ("audio", "Narration, music, subtitles", "WAV + SRT"),
    ("end-card", "End card", "PNG + 4s clip (Made with AI)"),
    ("validate-media", "Media checks", "All files exist before edit"),
    ("assemble", "Final edit", "9:16 + 16:9 MP4, ducking"),
    ("final-check", "Deliverable validation", "validation_report.json"),
]


def _shot_count(data: dict[str, Any]) -> int:
    return len(data.get("shots", []))


def build_task_statuses(storyboard_path: Path) -> list[TaskStatus]:
    data = load_storyboard(storyboard_path)
    shots = data.get("shots", [])
    refs = data.get("references", {})
    audio = data.get("audio", {})
    final = data.get("final", {})

    refs_done = all(r.get("image_path") and Path(r["image_path"]).is_file() for r in refs.values())
    kf_done = all(s.get("keyframe_path") and Path(s["keyframe_path"]).is_file() for s in shots)
    vid_done = all(s.get("clip_path") and Path(s["clip_path"]).is_file() for s in shots)
    nar_done = all(s.get("narration_path") and Path(s["narration_path"]).is_file() for s in shots)
    music_ok = bool(audio.get("music_path") and Path(audio["music_path"]).is_file())
    subs_ok = bool(audio.get("subtitles_path") and Path(audio["subtitles_path"]).is_file())
    vert_ok = bool(final.get("vertical_path") and Path(final["vertical_path"]).is_file())
    horiz_ok = bool(final.get("horizontal_path") and Path(final["horizontal_path"]).is_file())
    report_path = Path(final.get("vertical_path") or ".").parent / "validation_report.json"
    report_ok = report_path.is_file()

    end_png_p = Path(final["end_card_path"]) if final.get("end_card_path") else Path("outputs/end_card/end_card.png")
    end_clip_p = (
        Path(final["end_card_clip_path"])
        if final.get("end_card_clip_path")
        else Path("outputs/end_card/end_card.mp4")
    )
    end_ok = end_png_p.is_file() and end_clip_p.is_file()

    flags = {
        "validate": True,  # assumed if storyboard loads; run validate for certainty
        "story": bool(shots and all(s.get("narration_text") for s in shots)),
        "references": refs_done or len(refs) == 0,
        "images": kf_done,
        "videos": vid_done,
        "audio": nar_done and music_ok and subs_ok,
        "validate-media": nar_done and vid_done and music_ok and subs_ok,
        "end-card": end_ok,
        "assemble": vert_ok and horiz_ok,
        "final-check": report_ok and vert_ok and horiz_ok,
    }
    details = {
        "validate": f"{_shot_count(data)} shots in storyboard",
        "story": f"{_shot_count(data)} narration lines",
        "references": f"{sum(1 for r in refs.values() if r.get('image_path'))}/{len(refs)} refs",
        "images": f"{sum(1 for s in shots if s.get('keyframe_path'))}/{len(shots)} keyframes",
        "videos": f"{sum(1 for s in shots if s.get('clip_path'))}/{len(shots)} clips",
        "audio": "narration + music + subtitles",
        "validate-media": "pre-assembly",
        "end-card": "PNG + clip" if end_ok else "run make end-card",
        "assemble": "vertical + horizontal" if vert_ok and horiz_ok else "not exported",
        "final-check": "report OK" if report_ok else "run final-check",
    }

    out: list[TaskStatus] = []
    for stage, title, desc in STAGE_TASKS:
        out.append(
            TaskStatus(
                stage=stage,
                description=f"{title} — {desc}",
                done=flags.get(stage, False),
                detail=details.get(stage, ""),
            )
        )
    return out


def format_status_report(storyboard_path: Path) -> str:
    tasks = build_task_statuses(storyboard_path)
    lines = ["Heritage Short pipeline tasks", "=" * 40]
    for t in tasks:
        mark = "[x]" if t.done else "[ ]"
        lines.append(f"{mark} {t.stage:16} {t.detail}")
        lines.append(f"    {t.description}")
    done = sum(1 for t in tasks if t.done)
    lines.append("")
    lines.append(f"Progress: {done}/{len(tasks)} stages look complete (run validate/final-check to confirm).")
    lines.append("")
    lines.append("Run everything:  python3 run_film.py")
    lines.append("Run one stage:   python main.py <stage>")
    lines.append("View logs:       python main.py logs")
    return "\n".join(lines)