"""
Semantic, scoped and temporal preference graph.

This is the canonical bridge between Operator Intelligence and domain-specific
learning systems. It does not replace the raw evidence stores; it normalizes
their conclusions into a queryable graph with scope, provenance and timeline.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4

from ..config import settings
from ..operator_intelligence import OperatorIntelligence
from ..vector_store import LocalVectorStore


class PreferenceScope(str, Enum):
    GLOBAL = "global"
    DOMAIN = "domain"
    PROJECT = "project"
    ARTIFACT = "artifact"


@dataclass
class PreferenceNode:
    key: str
    category: str
    subject: str
    stance: str
    confidence: float
    status: str
    scope: str
    domain: str | None
    project_id: str | None
    artifact_kind: str | None
    source_types: list[str]
    evidence_count: int
    evidence: list[dict[str, Any]]
    created_at: str
    updated_at: str
    revision: int = 1

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TimelineEvent:
    id: str
    node_key: str
    event_type: str
    previous_stance: str | None
    new_stance: str
    confidence: float
    source: str
    timestamp: str
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PreferenceGraph:
    VERSION = 1

    def __init__(
        self,
        storage_path: str | Path | None = None,
        vector_store: LocalVectorStore | None = None,
    ) -> None:
        self.storage_path = (
            Path(storage_path)
            if storage_path
            else settings.brain.state_dir / "preference_graph.json"
        )
        self.vector_store = vector_store or LocalVectorStore(
            db_path=settings.brain.state_dir / "preference_vectors.db"
        )

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @classmethod
    def _empty(cls) -> dict[str, Any]:
        return {
            "version": cls.VERSION,
            "nodes": {},
            "timeline": [],
            "metrics": {
                "updates": 0,
                "semantic_queries": 0,
                "scope_blocks": 0,
                "operator_bootstrap_version": 0,
            },
        }

    def load(self) -> dict[str, Any]:
        if not self.storage_path.exists():
            return self._empty()
        try:
            data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return self._empty()
        if not isinstance(data, dict) or data.get("version") != self.VERSION:
            return self._empty()
        empty = self._empty()
        for key, value in empty.items():
            data.setdefault(key, value)
        for key, value in empty["metrics"].items():
            data["metrics"].setdefault(key, value)
        return data

    def _save(self, state: dict[str, Any]) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    @staticmethod
    def _normalize(value: str | None) -> str:
        if not value:
            return ""
        value = value.lower().strip()
        value = re.sub(r"[^a-z0-9à-ÿ]+", "_", value)
        return value.strip("_")[:100]

    def _key(
        self,
        category: str,
        subject: str,
        scope: PreferenceScope,
        domain: str | None,
        project_id: str | None,
        artifact_kind: str | None,
    ) -> str:
        return ":".join([
            scope.value,
            self._normalize(domain) or "_",
            self._normalize(project_id) or "_",
            self._normalize(artifact_kind) or "_",
            self._normalize(category),
            self._normalize(subject),
        ])

    @staticmethod
    def _decayed_confidence(node: dict[str, Any]) -> float:
        confidence = float(node.get("confidence", 0.0))
        try:
            updated = datetime.fromisoformat(str(node["updated_at"]))
            if updated.tzinfo is None:
                updated = updated.replace(tzinfo=timezone.utc)
            age_days = max(
                0.0,
                (datetime.now(timezone.utc) - updated).total_seconds() / 86400.0,
            )
        except (KeyError, TypeError, ValueError):
            return confidence
        half_life = 540.0 if node.get("status") == "confirmed" else 180.0
        return max(0.25, confidence * math.pow(0.5, age_days / half_life))

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return {
            token
            for token in re.findall(r"[a-zA-Z0-9À-ÿ]{3,}", text.lower())
            if token not in {"para", "com", "uma", "que", "isso", "como", "mais", "por", "dos", "das"}
        }

    @staticmethod
    def _scope_for_context(
        project_id: str | None,
        domain: str | None,
        artifact_kind: str | None,
    ) -> PreferenceScope:
        if project_id and artifact_kind:
            return PreferenceScope.ARTIFACT
        if project_id:
            return PreferenceScope.PROJECT
        if domain:
            return PreferenceScope.DOMAIN
        return PreferenceScope.GLOBAL

    def upsert(
        self,
        *,
        category: str,
        subject: str,
        stance: str,
        confidence: float,
        source: str,
        scope: PreferenceScope | str = PreferenceScope.GLOBAL,
        domain: str | None = None,
        project_id: str | None = None,
        artifact_kind: str | None = None,
        evidence: str = "",
        status: str = "probable",
    ) -> dict[str, Any]:
        if OperatorIntelligence.is_sensitive(f"{category} {subject} {evidence}"):
            return {"recorded": False, "reason": "sensitive"}
        if stance not in {"positive", "negative", "contested"}:
            return {"recorded": False, "reason": "invalid_stance"}

        scope_enum = scope if isinstance(scope, PreferenceScope) else PreferenceScope(scope)
        key = self._key(
            category,
            subject,
            scope_enum,
            domain,
            project_id,
            artifact_kind,
        )
        now = self._now()
        state = self.load()
        previous = state["nodes"].get(key)
        previous_stance = previous.get("stance") if previous else None

        if previous is None:
            node = PreferenceNode(
                key=key,
                category=category,
                subject=subject.strip()[:180],
                stance=stance,
                confidence=max(0.0, min(0.99, confidence)),
                status=status,
                scope=scope_enum.value,
                domain=domain,
                project_id=project_id,
                artifact_kind=artifact_kind,
                source_types=[source],
                evidence_count=1,
                evidence=[],
                created_at=now,
                updated_at=now,
            ).to_dict()
            event_type = "created"
        else:
            node = dict(previous)
            event_type = "reinforced"
            if previous_stance != stance and previous_stance in {"positive", "negative"}:
                node["status"] = "contested"
                node["stance"] = "contested"
                node["confidence"] = min(0.65, max(float(node.get("confidence", 0)), confidence))
                event_type = "contradicted"
            else:
                node["stance"] = stance
                node["confidence"] = min(
                    0.99,
                    max(float(node.get("confidence", 0.0)), confidence)
                    + min(0.12, 0.025 * int(node.get("evidence_count", 0))),
                )
                if status == "confirmed" or node["confidence"] >= 0.84:
                    node["status"] = "confirmed"
                elif node["confidence"] >= 0.68:
                    node["status"] = "probable"
            node["evidence_count"] = int(node.get("evidence_count", 0)) + 1
            node["updated_at"] = now
            node["revision"] = int(node.get("revision", 1)) + 1
            source_types = set(node.get("source_types", []))
            source_types.add(source)
            node["source_types"] = sorted(source_types)

        if evidence:
            node.setdefault("evidence", []).append({
                "source": source,
                "text": OperatorIntelligence._redact(evidence),
                "timestamp": now,
            })
            node["evidence"] = node["evidence"][-12:]

        state["nodes"][key] = node
        state["timeline"].append(
            TimelineEvent(
                id=f"prefevt_{uuid4().hex[:12]}",
                node_key=key,
                event_type=event_type,
                previous_stance=previous_stance,
                new_stance=node["stance"],
                confidence=float(node["confidence"]),
                source=source,
                timestamp=now,
                note=OperatorIntelligence._redact(evidence),
            ).to_dict()
        )
        state["timeline"] = state["timeline"][-2000:]
        state["metrics"]["updates"] += 1
        self._save(state)
        self._index_node(node)
        return {"recorded": True, "event_type": event_type, "node": node}

    def _index_node(self, node: dict[str, Any]) -> None:
        text = " | ".join([
            str(node.get("category", "")),
            str(node.get("subject", "")),
            str(node.get("stance", "")),
            str(node.get("domain", "") or ""),
            str(node.get("project_id", "") or ""),
            str(node.get("artifact_kind", "") or ""),
        ])
        self.vector_store.upsert(
            doc_id=f"preference:{node['key']}",
            text=text,
            metadata={
                "node_key": node["key"],
                "scope": node.get("scope"),
                "project_id": node.get("project_id"),
                "domain": node.get("domain"),
                "artifact_kind": node.get("artifact_kind"),
            },
        )

    def rebuild_index(self) -> int:
        count = 0
        for node in self.load()["nodes"].values():
            self._index_node(node)
            count += 1
        return count

    def sync_operator_beliefs(
        self,
        intelligence: OperatorIntelligence,
        touched_keys: list[str],
        *,
        project_id: str | None = None,
        domain: str | None = None,
        artifact_kind: str | None = None,
    ) -> list[dict[str, Any]]:
        state = intelligence.load()
        synced = []
        global_categories = {"working_style", "feedback_style", "tooling", "routine"}
        for key in touched_keys:
            belief = state["beliefs"].get(key)
            if not belief or belief.get("status") == "contested":
                continue
            category = str(belief.get("category", "preference"))
            if category in global_categories:
                scope = PreferenceScope.GLOBAL
                scoped_project = None
                scoped_domain = None
                scoped_artifact = None
            else:
                scope = self._scope_for_context(project_id, domain, artifact_kind)
                scoped_project = project_id
                scoped_domain = domain
                scoped_artifact = artifact_kind
            result = self.upsert(
                category=category,
                subject=str(belief.get("subject", "")),
                stance=str(belief.get("stance", "positive")),
                confidence=float(belief.get("confidence", 0.5)),
                source="operator_intelligence",
                scope=scope,
                domain=scoped_domain,
                project_id=scoped_project,
                artifact_kind=scoped_artifact,
                evidence=(belief.get("evidence") or [{}])[-1].get("snippet", ""),
                status=str(belief.get("status", "hypothesis")),
            )
            if result.get("recorded"):
                synced.append(result["node"])
        return synced

    def bootstrap_operator_beliefs(
        self,
        intelligence: OperatorIntelligence,
        *,
        bootstrap_version: int = 1,
    ) -> int:
        graph_state = self.load()
        current = int(graph_state["metrics"].get("operator_bootstrap_version", 0))
        if current >= bootstrap_version:
            return 0

        operator_state = intelligence.load()
        imported = 0
        for belief in operator_state.get("beliefs", {}).values():
            if belief.get("status") == "contested":
                continue
            category = str(belief.get("category", "preference"))
            if category == "context_feedback":
                continue
            result = self.upsert(
                category=category,
                subject=str(belief.get("subject", "")),
                stance=str(belief.get("stance", "positive")),
                confidence=float(belief.get("confidence", 0.5)),
                source="operator_bootstrap",
                scope=PreferenceScope.GLOBAL,
                evidence="legacy OperatorIntelligence belief",
                status=str(belief.get("status", "hypothesis")),
            )
            imported += int(bool(result.get("recorded")))

        graph_state = self.load()
        graph_state["metrics"]["operator_bootstrap_version"] = bootstrap_version
        self._save(graph_state)
        return imported

    def _scope_score(
        self,
        node: dict[str, Any],
        *,
        project_id: str | None,
        domain: str | None,
        artifact_kind: str | None,
    ) -> float | None:
        scope = node.get("scope", "global")
        if scope == PreferenceScope.PROJECT.value:
            if not project_id or self._normalize(project_id) != self._normalize(node.get("project_id")):
                return None
            return 0.28
        if scope == PreferenceScope.ARTIFACT.value:
            if not project_id or self._normalize(project_id) != self._normalize(node.get("project_id")):
                return None
            if artifact_kind and node.get("artifact_kind"):
                if self._normalize(artifact_kind) != self._normalize(node.get("artifact_kind")):
                    return None
            return 0.34
        if scope == PreferenceScope.DOMAIN.value:
            if not domain or self._normalize(domain) != self._normalize(node.get("domain")):
                return None
            return 0.20
        return 0.08

    def query(
        self,
        query: str,
        *,
        project_id: str | None = None,
        domain: str | None = None,
        artifact_kind: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        state = self.load()
        nodes = state["nodes"]
        query_tokens = self._tokens(query)
        semantic = self.vector_store.search(query, top_k=max(30, limit * 4), min_score=0.0)
        semantic_scores = {
            item["metadata"].get("node_key"): float(item["score"])
            for item in semantic
            if item.get("metadata", {}).get("node_key")
        }

        ranked: list[tuple[float, dict[str, Any]]] = []
        blocked = 0
        for key, node in nodes.items():
            if node.get("status") == "contested":
                continue
            scope_score = self._scope_score(
                node,
                project_id=project_id,
                domain=domain,
                artifact_kind=artifact_kind,
            )
            if scope_score is None:
                blocked += 1
                continue

            text = f"{node.get('category', '')} {node.get('subject', '')}".lower()
            node_tokens = self._tokens(text)
            lexical = (
                len(query_tokens.intersection(node_tokens)) / max(1, len(query_tokens))
                if query_tokens
                else 0.0
            )
            dense = max(0.0, semantic_scores.get(key, 0.0))
            confidence = self._decayed_confidence(node)
            source_bonus = min(0.10, 0.02 * len(node.get("source_types", [])))
            status_bonus = 0.10 if node.get("status") == "confirmed" else 0.04
            score = (
                0.40 * dense
                + 0.22 * lexical
                + 0.18 * confidence
                + scope_score
                + source_bonus
                + status_bonus
            )
            if dense < 0.12 and lexical == 0 and scope_score <= 0.08:
                continue
            ranked.append((score, {**node, "retrieval_score": round(score, 4)}))

        ranked.sort(key=lambda pair: pair[0], reverse=True)
        state["metrics"]["semantic_queries"] += 1
        state["metrics"]["scope_blocks"] += blocked
        self._save(state)
        return [node for _, node in ranked[: max(1, limit)]]

    def build_context(
        self,
        query: str,
        *,
        project_id: str | None = None,
        domain: str | None = None,
        artifact_kind: str | None = None,
        limit: int = 8,
    ) -> str:
        nodes = self.query(
            query,
            project_id=project_id,
            domain=domain,
            artifact_kind=artifact_kind,
            limit=limit,
        )
        lines = [
            "# PREFERENCE GRAPH — PERSONALIZACAO SEMANTICA E ESCOPADA",
            "Aplique apenas quando relevante ao pedido atual. Preferencias de projeto nao vazam para outros projetos.",
        ]
        if not nodes:
            lines.append("- Nenhuma preferencia relevante recuperada.")
            return "\n".join(lines)

        for node in nodes:
            action = "favorece" if node.get("stance") == "positive" else "evita"
            scope_bits = [node.get("scope", "global")]
            if node.get("domain"):
                scope_bits.append(f"domain={node['domain']}")
            if node.get("project_id"):
                scope_bits.append(f"project={node['project_id']}")
            if node.get("artifact_kind"):
                scope_bits.append(f"artifact={node['artifact_kind']}")
            lines.append(
                f"- [{'/'.join(scope_bits)} | {node.get('status')} | "
                f"conf {float(node.get('confidence', 0)):.2f}] "
                f"{action} {node.get('subject')}"
            )
        return "\n".join(lines)

    def timeline(self, node_key: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        events = self.load()["timeline"]
        if node_key:
            events = [event for event in events if event.get("node_key") == node_key]
        return events[-max(1, limit):]

    def status(self) -> dict[str, Any]:
        state = self.load()
        nodes = list(state["nodes"].values())
        by_scope: dict[str, int] = {}
        for node in nodes:
            scope = str(node.get("scope", "global"))
            by_scope[scope] = by_scope.get(scope, 0) + 1
        return {
            "nodes": len(nodes),
            "timeline_events": len(state["timeline"]),
            "by_scope": by_scope,
            "vector_index_count": self.vector_store.count(),
            "embedding": self.vector_store.embedding_status(),
            "metrics": dict(state["metrics"]),
        }
