"""Input fingerprints per stage for selective regeneration."""

from __future__ import annotations

from typing import Any

from core.cache import fingerprint_payload


def shot_keyframe_inputs(shot: dict[str, Any], reference_paths: list[str]) -> dict[str, Any]:
    return {
        "shot_id": shot["shot_id"],
        "image_prompt": shot["image_prompt"],
        "visual_description": shot["visual_description"],
        "refs": sorted(reference_paths),
    }


def shot_video_inputs(shot: dict[str, Any], keyframe_path: str) -> dict[str, Any]:
    return {
        "shot_id": shot["shot_id"],
        "video_prompt": shot["video_prompt"],
        "camera_movement": shot["camera_movement"],
        "keyframe_path": keyframe_path,
        "duration_seconds": shot["duration_seconds"],
    }


def shot_narration_inputs(shot: dict[str, Any], lang: str) -> dict[str, Any]:
    return {
        "shot_id": shot["shot_id"],
        "narration_text": shot["narration_text"],
        "language": lang,
        "duration_seconds": shot["duration_seconds"],
    }


def music_inputs(project: dict[str, Any], duration: float) -> dict[str, Any]:
    return {
        "music_prompt": project.get("music_prompt", ""),
        "visual_style": project.get("visual_style", ""),
        "duration": duration,
    }


def subtitles_inputs(shots: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "lines": [(s["shot_id"], s["subtitle_text_en"], s["duration_seconds"]) for s in shots],
    }


def assembly_inputs(storyboard: dict[str, Any], export_vertical: bool, export_horizontal: bool) -> dict[str, Any]:
    return {
        "shots": [
            (s["shot_id"], s.get("clip_path"), s.get("narration_path"), s["duration_seconds"])
            for s in storyboard.get("shots", [])
        ],
        "music": storyboard.get("audio", {}).get("music_path"),
        "subs": storyboard.get("audio", {}).get("subtitles_path"),
        "vertical": export_vertical,
        "horizontal": export_horizontal,
    }


def fingerprint(inputs: dict[str, Any]) -> str:
    return fingerprint_payload(inputs)


# Human-readable dependency map for documentation and tests
REGENERATION_MAP: dict[str, list[str]] = {
    "image_prompt": ["keyframe", "video"],
    "video_prompt": ["video"],
    "narration_text": ["narration", "subtitles", "assembly"],
    "music_prompt": ["music", "assembly"],
    "subtitle_text_en": ["subtitles", "assembly"],
    "export_settings": ["assembly"],
}