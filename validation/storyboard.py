"""JSON Schema validation and business rules for storyboard."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jsonschema


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str]


def load_storyboard(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_storyboard(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def validate_schema(data: dict[str, Any], schema_path: Path) -> ValidationResult:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    validator = jsonschema.Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        loc = ".".join(str(p) for p in err.path) or "(root)"
        errors.append(f"{loc}: {err.message}")
    return ValidationResult(ok=not errors, errors=errors)


def validate_duration_budget(data: dict[str, Any], min_s: float = 60, max_s: float = 90) -> ValidationResult:
    total = sum(float(s["duration_seconds"]) for s in data.get("shots", []))
    errors: list[str] = []
    if total < min_s or total > max_s:
        errors.append(f"Total shot duration {total:.1f}s outside required [{min_s}, {max_s}]")
    shot_ids = [s["shot_id"] for s in data.get("shots", [])]
    if len(shot_ids) != len(set(shot_ids)):
        errors.append("Duplicate shot_id values detected")
    orders = [s["shot_order"] for s in data.get("shots", [])]
    if sorted(orders) != list(range(len(orders))):
        errors.append("shot_order must be contiguous from 0")
    return ValidationResult(ok=not errors, errors=errors)


def validate_storyboard(data: dict[str, Any], schema_path: Path) -> ValidationResult:
    r1 = validate_schema(data, schema_path)
    r2 = validate_duration_budget(data)
    errors = r1.errors + r2.errors
    return ValidationResult(ok=not errors, errors=errors)