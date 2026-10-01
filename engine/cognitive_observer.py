"""Read-only observer for the live cognitive state exposed to War Room."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import settings


class CognitiveStateObserver:
    def __init__(self, state_dir: Path | None = None) -> None:
        self.state_dir = state_dir or settings.brain.state_dir

    @staticmethod
    def _latest_json(directory: Path) -> dict[str, Any] | None:
        if not directory.exists():
            return None
        files = sorted(directory.glob("*.json"), reverse=True)
        for path in files:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(payload, dict):
                return payload
        return None

    def _latest_reasoning_event(self) -> dict[str, Any] | None:
        events_dir = self.state_dir / "events"
        if not events_dir.exists():
            return None
        for path in sorted(events_dir.glob("*.json"), reverse=True):
            try:
                event = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(event, dict):
                continue
            payload = event.get("payload")
            if not isinstance(payload, dict):
                continue
            if payload.get("action") in {"analyze", "synthesize"} and payload.get("conclusion"):
                return event
        return None

    def snapshot(self) -> dict[str, Any]:
        goal = self._latest_json(self.state_dir / "goals") or {}
        plan = self._latest_json(self.state_dir / "plans") or {}
        reasoning_event = self._latest_reasoning_event() or {}
        reasoning = reasoning_event.get("payload", {})
        hypotheses = reasoning.get("hypotheses", []) if isinstance(reasoning, dict) else []
        if not isinstance(hypotheses, list):
            hypotheses = []

        steps = plan.get("steps", []) if isinstance(plan, dict) else []
        if not isinstance(steps, list):
            steps = []

        return {
            "goal": {
                "id": goal.get("id"),
                "title": goal.get("title"),
                "status": goal.get("status"),
            },
            "plan": {
                "id": plan.get("id"),
                "title": plan.get("title"),
                "replan_count": plan.get("replan_count", 0),
                "steps_total": len(steps),
                "steps_success": sum(1 for step in steps if isinstance(step, dict) and step.get("status") == "success"),
            },
            "reasoning": {
                "action": reasoning.get("action") if isinstance(reasoning, dict) else None,
                "conclusion": reasoning.get("conclusion") if isinstance(reasoning, dict) else None,
                "confidence": reasoning.get("confidence") if isinstance(reasoning, dict) else None,
                "evidence_ids": reasoning.get("evidence_ids", []) if isinstance(reasoning, dict) else [],
                "gaps": reasoning.get("gaps", []) if isinstance(reasoning, dict) else [],
                "hypotheses": hypotheses[:4],
                "source": reasoning.get("reasoning_source") if isinstance(reasoning, dict) else None,
            },
        }
