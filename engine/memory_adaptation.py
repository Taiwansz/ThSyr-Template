"""Adaptive memory usage scoring.

Usage telemetry is persisted in state instead of rewriting knowledge files on
every retrieval. This keeps Git clean while still giving the retriever a
plasticity signal based on accesses and explicit usefulness feedback.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import settings


class MemoryAdaptationStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (settings.brain.state_dir / "memory_adaptation.json")

    def _load(self) -> dict[str, dict[str, Any]]:
        if not self.path.exists():
            return {}
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            return raw if isinstance(raw, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def _save(self, data: dict[str, dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(".tmp")
        temp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        temp.replace(self.path)

    def get(self, memory_id: str) -> dict[str, Any]:
        data = self._load()
        record = data.get(memory_id, {})
        return {
            "access_count": int(record.get("access_count", 0)),
            "last_accessed": record.get("last_accessed"),
            "utility_score": float(record.get("utility_score", 0.5)),
        }

    def record_access(self, memory_id: str) -> dict[str, Any]:
        data = self._load()
        record = self.get(memory_id)
        record["access_count"] = int(record["access_count"]) + 1
        record["last_accessed"] = datetime.now(timezone.utc).isoformat()
        data[memory_id] = record
        self._save(data)
        return record

    def record_feedback(self, memory_id: str, helpful: bool) -> dict[str, Any]:
        data = self._load()
        record = self.get(memory_id)
        current = float(record["utility_score"])
        target = 1.0 if helpful else 0.0
        record["utility_score"] = round((0.8 * current) + (0.2 * target), 4)
        record["last_accessed"] = datetime.now(timezone.utc).isoformat()
        data[memory_id] = record
        self._save(data)
        return record

    def plasticity_score(self, memory_id: str) -> float:
        record = self.get(memory_id)
        accesses = int(record["access_count"])
        utility = float(record["utility_score"])
        frequency = min(1.0, math.log1p(accesses) / math.log(20.0))
        return max(0.0, min(1.0, (0.65 * utility) + (0.35 * frequency)))
