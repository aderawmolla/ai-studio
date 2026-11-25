"""Content-addressed cache for generated artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def fingerprint_payload(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class ArtifactCache:
    """Maps fingerprint -> artifact metadata and supports reuse decisions."""

    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.cache_dir / "index.json"
        self._index: dict[str, dict[str, Any]] = self._load()

    def _load(self) -> dict[str, dict[str, Any]]:
        if not self.index_path.exists():
            return {}
        return json.loads(self.index_path.read_text(encoding="utf-8"))

    def _save(self) -> None:
        self.index_path.write_text(
            json.dumps(self._index, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def lookup(self, key: str, fingerprint: str) -> dict[str, Any] | None:
        entry = self._index.get(key)
        if entry and entry.get("fingerprint") == fingerprint:
            path = Path(entry["path"])
            if path.exists():
                return entry
        return None

    def store(
        self,
        key: str,
        fingerprint: str,
        path: Path,
        *,
        reason: str,
        stage: str,
    ) -> None:
        self._index[key] = {
            "fingerprint": fingerprint,
            "path": str(path),
            "reason": reason,
            "stage": stage,
        }
        self._save()