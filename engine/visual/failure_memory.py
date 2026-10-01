"""
Persistent failure memory for visual work.

A visual mistake that was already observed becomes an explicit pre-flight
constraint on future work in the same scope.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..config import settings


class VisualFailureMemory:
    VERSION = 1

    def __init__(self, storage_path: str | Path | None = None) -> None:
        self.storage_path = (
            Path(storage_path)
            if storage_path
            else settings.brain.state_dir / "visual_failure_memory.json"
        )

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @classmethod
    def _empty(cls) -> dict[str, Any]:
        return {"version": cls.VERSION, "patterns": {}, "metrics": {"observations": 0}}

    def load(self) -> dict[str, Any]:
        if not self.storage_path.exists():
            return self._empty()
        try:
            data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return self._empty()
        if not isinstance(data, dict) or data.get("version") != self.VERSION:
            return self._empty()
        data.setdefault("patterns", {})
        data.setdefault("metrics", {"observations": 0})
        return data

    def _save(self, state: dict[str, Any]) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    @staticmethod
    def _signature(category: str, problem: str) -> str:
        normalized = " ".join(f"{category}:{problem}".strip().lower().split())
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:20]

    def record(
        self,
        *,
        category: str,
        problem: str,
        fix: str = "",
        severity: str = "major",
        project_id: str | None = None,
        artifact_kind: str | None = None,
        domain: str = "design",
        source: str = "visual_critic",
    ) -> dict[str, Any]:
        signature = self._signature(category, problem)
        state = self.load()
        now = self._now()
        pattern = state["patterns"].get(signature) or {
            "id": signature,
            "category": category,
            "problem": problem[:240],
            "recommended_fix": fix[:320],
            "severity": severity,
            "domain": domain,
            "project_id": project_id,
            "artifact_kind": artifact_kind,
            "count": 0,
            "first_seen": now,
            "last_seen": now,
            "sources": [],
        }
        pattern["count"] = int(pattern.get("count", 0)) + 1
        pattern["last_seen"] = now
        if fix:
            pattern["recommended_fix"] = fix[:320]
        if severity == "blocker":
            pattern["severity"] = "blocker"
        sources = set(pattern.get("sources", []))
        sources.add(source)
        pattern["sources"] = sorted(sources)
        state["patterns"][signature] = pattern
        state["metrics"]["observations"] += 1
        self._save(state)
        return pattern

    def ingest_report(
        self,
        report: dict[str, Any],
        *,
        project_id: str | None = None,
        artifact_kind: str | None = None,
    ) -> int:
        count = 0
        for critique in report.get("critiques", []):
            for issue in critique.get("issues", []):
                self.record(
                    category=str(issue.get("category", "visual")),
                    problem=str(issue.get("problem", "problema visual")),
                    fix=str(issue.get("fix", "")),
                    severity=str(issue.get("severity", "major")),
                    project_id=project_id,
                    artifact_kind=artifact_kind,
                )
                count += 1
        return count

    def record_human_rejection(
        self,
        note: str,
        *,
        project_id: str | None = None,
        artifact_kind: str | None = None,
    ) -> dict[str, Any]:
        return self.record(
            category="human_rejection",
            problem=note or "resultado rejeitado pelo operador",
            severity="major",
            project_id=project_id,
            artifact_kind=artifact_kind,
            source="human_feedback",
        )

    @staticmethod
    def _scope_ok(
        pattern: dict[str, Any],
        project_id: str | None,
        artifact_kind: str | None,
    ) -> bool:
        pattern_project = pattern.get("project_id")
        if pattern_project and pattern_project != project_id:
            return False
        pattern_artifact = pattern.get("artifact_kind")
        if pattern_artifact and artifact_kind and pattern_artifact != artifact_kind:
            return False
        return True

    def relevant(
        self,
        *,
        project_id: str | None = None,
        artifact_kind: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        patterns = [
            pattern
            for pattern in self.load()["patterns"].values()
            if self._scope_ok(pattern, project_id, artifact_kind)
        ]
        patterns.sort(
            key=lambda pattern: (
                pattern.get("severity") == "blocker",
                int(pattern.get("count", 0)),
                str(pattern.get("last_seen", "")),
            ),
            reverse=True,
        )
        return patterns[: max(1, limit)]

    def build_context(
        self,
        *,
        project_id: str | None = None,
        artifact_kind: str | None = None,
        limit: int = 10,
    ) -> str:
        patterns = self.relevant(
            project_id=project_id,
            artifact_kind=artifact_kind,
            limit=limit,
        )
        lines = [
            "FAILURE MEMORY - ERROS QUE NAO DEVEM SE REPETIR",
            "Trate recorrencia de erro conhecido como regressao, nao como nova tentativa.",
        ]
        if not patterns:
            lines.append("- Nenhum failure pattern aplicavel a este escopo.")
            return "\n".join(lines)
        for pattern in patterns:
            fix = pattern.get("recommended_fix") or "eliminar a causa raiz"
            lines.append(
                f"- [{pattern.get('severity')} | visto {pattern.get('count')}x] "
                f"{pattern.get('problem')} -> {fix}"
            )
        return "\n".join(lines)

    def status(self) -> dict[str, Any]:
        state = self.load()
        return {
            "patterns": len(state["patterns"]),
            "observations": state["metrics"].get("observations", 0),
        }
