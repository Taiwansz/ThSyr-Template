"""
Outcome learning: learn from the delta between rejected and approved versions.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from ..config import settings


class OutcomeLearningStore:
    VERSION = 1

    def __init__(self, storage_path: str | Path | None = None) -> None:
        self.storage_path = (
            Path(storage_path)
            if storage_path
            else settings.brain.state_dir / "outcome_learning.json"
        )

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @classmethod
    def _empty(cls) -> dict[str, Any]:
        return {"version": cls.VERSION, "outcomes": {}, "metrics": {"resolved": 0}}

    def load(self) -> dict[str, Any]:
        if not self.storage_path.exists():
            return self._empty()
        try:
            data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return self._empty()
        if not isinstance(data, dict) or data.get("version") != self.VERSION:
            return self._empty()
        data.setdefault("outcomes", {})
        data.setdefault("metrics", {"resolved": 0})
        return data

    def _save(self, state: dict[str, Any]) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def begin(
        self,
        objective: str,
        *,
        project_id: str | None = None,
        domain: str | None = None,
        artifact_kind: str | None = None,
        outcome_id: str | None = None,
    ) -> str:
        oid = outcome_id or f"outcome_{uuid4().hex[:12]}"
        state = self.load()
        state["outcomes"][oid] = {
            "id": oid,
            "objective": objective,
            "project_id": project_id,
            "domain": domain,
            "artifact_kind": artifact_kind,
            "created_at": self._now(),
            "resolved_at": None,
            "versions": [],
            "resolution": None,
        }
        self._save(state)
        return oid

    def record_version(
        self,
        outcome_id: str,
        *,
        label: str,
        artifact_ref: str,
        verdict: str = "unknown",
        review_report: dict[str, Any] | None = None,
        note: str = "",
    ) -> dict[str, Any]:
        state = self.load()
        outcome = state["outcomes"].get(outcome_id)
        if not outcome:
            raise KeyError(f"outcome nao encontrado: {outcome_id}")
        version = {
            "label": label,
            "artifact_ref": artifact_ref,
            "verdict": verdict,
            "review_report": review_report,
            "note": note[:500],
            "timestamp": self._now(),
        }
        outcome["versions"].append(version)
        outcome["versions"] = outcome["versions"][-20:]
        self._save(state)
        return version

    @staticmethod
    def _aggregate_scores(report: dict[str, Any] | None) -> dict[str, float]:
        if not report:
            return {}
        scores: dict[str, list[float]] = {}
        for critique in report.get("critiques", []):
            for key, value in critique.get("scores", {}).items():
                try:
                    scores.setdefault(key, []).append(float(value))
                except (TypeError, ValueError):
                    continue
        return {
            key: round(sum(values) / len(values), 2)
            for key, values in scores.items()
            if values
        }

    @staticmethod
    def _issue_keys(report: dict[str, Any] | None) -> dict[str, str]:
        issues: dict[str, str] = {}
        if not report:
            return issues
        for critique in report.get("critiques", []):
            for issue in critique.get("issues", []):
                category = str(issue.get("category", "visual"))
                problem = str(issue.get("problem", ""))
                key = f"{category}:{problem.strip().lower()[:120]}"
                issues[key] = f"{category}: {problem}"
        return issues

    def resolve(
        self,
        outcome_id: str,
        *,
        rejected_label: str,
        approved_label: str,
        note: str = "",
    ) -> dict[str, Any]:
        state = self.load()
        outcome = state["outcomes"].get(outcome_id)
        if not outcome:
            raise KeyError(f"outcome nao encontrado: {outcome_id}")
        versions = {version["label"]: version for version in outcome["versions"]}
        rejected = versions.get(rejected_label)
        approved = versions.get(approved_label)
        if not rejected or not approved:
            raise KeyError("versoes rejeitada/aprovada nao encontradas")

        before_scores = self._aggregate_scores(rejected.get("review_report"))
        after_scores = self._aggregate_scores(approved.get("review_report"))
        score_delta = {
            key: round(after_scores.get(key, 0.0) - value, 2)
            for key, value in before_scores.items()
            if key in after_scores
        }

        before_issues = self._issue_keys(rejected.get("review_report"))
        after_issues = self._issue_keys(approved.get("review_report"))
        fixed = [before_issues[key] for key in before_issues.keys() - after_issues.keys()]
        regressions = [after_issues[key] for key in after_issues.keys() - before_issues.keys()]

        strongest = sorted(
            score_delta.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:4]
        resolution = {
            "rejected_label": rejected_label,
            "approved_label": approved_label,
            "score_delta": score_delta,
            "strongest_improvements": strongest,
            "fixed_issues": fixed[:12],
            "regressions": regressions[:12],
            "note": note[:500],
            "timestamp": self._now(),
        }
        outcome["resolution"] = resolution
        outcome["resolved_at"] = resolution["timestamp"]
        state["metrics"]["resolved"] += 1
        self._save(state)
        return {**outcome, "resolution": resolution}

    def get(self, outcome_id: str) -> dict[str, Any] | None:
        return self.load()["outcomes"].get(outcome_id)

    def status(self) -> dict[str, Any]:
        state = self.load()
        return {
            "total": len(state["outcomes"]),
            "resolved": state["metrics"].get("resolved", 0),
        }
