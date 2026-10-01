"""
Unified personalization hub.

Coordinates immediate operator learning, semantic preference retrieval, scoped
knowledge and outcome-based reinforcement without conflating personalization
with authentication.
"""

from __future__ import annotations

import re
from typing import Any

from ..operator_intelligence import OperatorIntelligence
from .outcomes import OutcomeLearningStore
from .preference_graph import PreferenceGraph, PreferenceScope


class PersonalizationHub:
    def __init__(
        self,
        operator_intelligence: OperatorIntelligence | None = None,
        preference_graph: PreferenceGraph | None = None,
        outcomes: OutcomeLearningStore | None = None,
    ) -> None:
        self.operator = operator_intelligence or OperatorIntelligence()
        self.graph = preference_graph or PreferenceGraph()
        self.outcomes = outcomes or OutcomeLearningStore()
        self.graph.bootstrap_operator_beliefs(self.operator)

    @staticmethod
    def infer_scope_context(
        message: str,
        context_subject: str | None = None,
    ) -> tuple[str | None, str | None]:
        text = f"{message} {context_subject or ''}".lower()
        design_terms = {
            "site", "ui", "ux", "layout", "hero", "icone", "ícone", "logo",
            "imagem", "visual", "mobile", "desktop", "landing", "tipografia",
        }
        engineering_terms = {
            "repo", "codigo", "código", "python", "api", "backend", "frontend",
            "teste", "bug", "git", "deploy", "arquitetura", "banco",
        }
        artifact = None
        if any(term in text for term in {"logo", "marca"}):
            artifact = "logo"
        elif any(term in text for term in {"icone", "ícone"}):
            artifact = "icon"
        elif any(term in text for term in {"imagem", "foto", "ilustracao", "ilustração"}):
            artifact = "image"
        elif any(term in text for term in {"tela", "ui", "interface"}):
            artifact = "ui_screen"
        elif any(term in text for term in {"site", "landing", "pagina", "página", "hero"}):
            artifact = "website"

        if any(term in text for term in design_terms):
            return "design", artifact
        if any(term in text for term in engineering_terms):
            return "engineering", artifact
        if re.search(r"(?i)\b(?:compare|decida|opcoes|opções|escolha)\b", text):
            return "decision", artifact
        return None, artifact

    def observe(
        self,
        message: str,
        *,
        context_subject: str | None = None,
        project_id: str | None = None,
        domain: str | None = None,
        artifact_kind: str | None = None,
        source: str = "conversation",
    ) -> dict[str, Any]:
        learning = self.operator.observe(
            message,
            source=source,
            context_subject=context_subject,
            context_project=project_id,
        )
        touched_keys = [
            item["key"]
            for item in learning.get("touched", [])
            if item.get("key")
        ]
        synced = self.graph.sync_operator_beliefs(
            self.operator,
            touched_keys,
            project_id=project_id,
            domain=domain,
            artifact_kind=artifact_kind,
        )
        return {
            **learning,
            "graph_nodes_synced": len(synced),
        }

    def build_context(
        self,
        query: str,
        *,
        project_id: str | None = None,
        domain: str | None = None,
        artifact_kind: str | None = None,
    ) -> str:
        graph_context = self.graph.build_context(
            query,
            project_id=project_id,
            domain=domain,
            artifact_kind=artifact_kind,
            limit=8,
        )
        return graph_context

    def record_preference(
        self,
        *,
        subject: str,
        verdict: str,
        reason: str = "",
        category: str = "preference",
        project_id: str | None = None,
        domain: str | None = None,
        artifact_kind: str | None = None,
        source: str = "explicit_feedback",
    ) -> dict[str, Any]:
        if verdict not in {"approved", "rejected"}:
            raise ValueError("verdict deve ser approved ou rejected")
        stance = "positive" if verdict == "approved" else "negative"
        scope = PreferenceGraph._scope_for_context(project_id, domain, artifact_kind)
        graph_result = self.graph.upsert(
            category=category,
            subject=subject,
            stance=stance,
            confidence=0.96,
            status="confirmed",
            source=source,
            scope=scope,
            domain=domain,
            project_id=project_id,
            artifact_kind=artifact_kind,
            evidence=reason or verdict,
        )
        if scope == PreferenceScope.GLOBAL:
            operator_result = self.operator.record_feedback(
                subject=subject,
                verdict=verdict,
                reason=reason,
                category=category,
            )
        else:
            operator_result = {
                "recorded": False,
                "reason": "scoped_preference_kept_in_preference_graph",
            }
        return {
            "graph": graph_result,
            "operator": operator_result,
        }

    def learn_outcome_resolution(
        self,
        outcome_id: str,
        *,
        rejected_label: str,
        approved_label: str,
        note: str = "",
    ) -> dict[str, Any]:
        outcome = self.outcomes.resolve(
            outcome_id,
            rejected_label=rejected_label,
            approved_label=approved_label,
            note=note,
        )
        resolution = outcome["resolution"]
        improvements = [
            f"{name} +{delta:g}"
            for name, delta in resolution.get("strongest_improvements", [])
            if delta > 0
        ]
        fixed = resolution.get("fixed_issues", [])
        summary_parts = []
        if improvements:
            summary_parts.append("melhorias mensuradas: " + ", ".join(improvements))
        if fixed:
            summary_parts.append("problemas removidos: " + "; ".join(fixed[:4]))
        if note:
            summary_parts.append(note)
        subject = (
            "aprovacao ocorreu apos " + " | ".join(summary_parts)
            if summary_parts
            else "aprovacao ocorreu apos refinamento iterativo"
        )
        preference = self.graph.upsert(
            category="outcome_preference",
            subject=subject,
            stance="positive",
            confidence=0.82,
            status="probable",
            source="outcome_learning",
            scope=PreferenceGraph._scope_for_context(
                outcome.get("project_id"),
                outcome.get("domain"),
                outcome.get("artifact_kind"),
            ),
            project_id=outcome.get("project_id"),
            domain=outcome.get("domain"),
            artifact_kind=outcome.get("artifact_kind"),
            evidence=f"{rejected_label} -> {approved_label}",
        )
        return {"outcome": outcome, "preference": preference}

    def status(self) -> dict[str, Any]:
        return {
            "operator": self.operator.status(),
            "preference_graph": self.graph.status(),
            "outcomes": self.outcomes.status(),
        }
