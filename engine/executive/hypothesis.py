"""Hypothesis engine for evidence-driven executive reasoning.

The engine never treats a hypothesis as a fact. It can ask the configured
ModelGateway for structured candidates, but always falls back to deterministic
hypotheses grounded in observations when a provider is unavailable or returns
an invalid payload.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from typing import Any

from ..models.base import ChatMessage, ModelRequest, ModelRole, ModelTier
from ..models.gateway import ModelGateway
from .models import Goal, Observation, Step


@dataclass
class Hypothesis:
    id: str
    statement: str
    confidence: float
    evidence_ids: list[str]
    counterevidence_ids: list[str]
    status: str = "open"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class HypothesisEngine:
    """Creates competing explanations from the evidence collected so far."""

    def __init__(self, gateway: ModelGateway | None = None) -> None:
        self.gateway = gateway or ModelGateway()

    @staticmethod
    def _clamp_confidence(value: Any, default: float = 0.5) -> float:
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            return default
        return max(0.0, min(1.0, parsed))

    @staticmethod
    def _evidence_payload(observations: list[Observation]) -> list[dict[str, Any]]:
        payload: list[dict[str, Any]] = []
        for observation in observations[-8:]:
            payload.append(
                {
                    "evidence_id": observation.evidence_id,
                    "step_id": observation.step_id,
                    "success": observation.success,
                    "error": observation.error,
                    "raw_output": observation.raw_output[:1200],
                    "data": observation.data,
                }
            )
        return payload

    def _from_model(
        self,
        goal: Goal,
        step: Step,
        observations: list[Observation],
    ) -> list[Hypothesis]:
        if not self.gateway.providers:
            return []

        evidence = self._evidence_payload(observations)
        request = ModelRequest(
            tier=ModelTier.REASONING,
            temperature=0.1,
            max_tokens=900,
            messages=[
                ChatMessage(
                    role=ModelRole.SYSTEM,
                    content=(
                        "Voce e o motor de hipoteses do ThSyr. Gere no maximo 4 hipoteses "
                        "concorrentes e falsificaveis. Use somente as evidencias fornecidas. "
                        "Nao trate ausencia de evidencia como confirmacao. Responda SOMENTE JSON "
                        "no formato {\"hypotheses\":[{\"statement\":str,\"confidence\":0..1,"
                        "\"evidence_ids\":[str],\"counterevidence_ids\":[str]}]}."
                    ),
                ),
                ChatMessage(
                    role=ModelRole.USER,
                    content=json.dumps(
                        {
                            "goal": goal.to_dict(),
                            "step": step.to_dict(),
                            "evidence": evidence,
                        },
                        ensure_ascii=False,
                    ),
                ),
            ],
        )
        try:
            response = self.gateway.generate(request)
            parsed = json.loads(response.content.strip())
        except Exception:
            return []

        raw_hypotheses = parsed.get("hypotheses", []) if isinstance(parsed, dict) else []
        if not isinstance(raw_hypotheses, list):
            return []

        valid_evidence = {obs.evidence_id for obs in observations}
        result: list[Hypothesis] = []
        for raw in raw_hypotheses[:4]:
            if not isinstance(raw, dict):
                continue
            statement = str(raw.get("statement", "")).strip()
            if not statement:
                continue
            evidence_ids = [
                str(item) for item in raw.get("evidence_ids", [])
                if str(item) in valid_evidence
            ]
            counter_ids = [
                str(item) for item in raw.get("counterevidence_ids", [])
                if str(item) in valid_evidence
            ]
            result.append(
                Hypothesis(
                    id=f"hyp_{uuid.uuid4().hex[:10]}",
                    statement=statement,
                    confidence=self._clamp_confidence(raw.get("confidence")),
                    evidence_ids=evidence_ids,
                    counterevidence_ids=counter_ids,
                )
            )
        return result

    @staticmethod
    def _fallback(observations: list[Observation]) -> list[Hypothesis]:
        if not observations:
            return [
                Hypothesis(
                    id=f"hyp_{uuid.uuid4().hex[:10]}",
                    statement="Evidencia insuficiente para formular uma explicacao material.",
                    confidence=0.15,
                    evidence_ids=[],
                    counterevidence_ids=[],
                    status="insufficient_evidence",
                )
            ]

        successful = [obs for obs in observations if obs.success]
        failed = [obs for obs in observations if not obs.success]
        hypotheses: list[Hypothesis] = []

        if failed:
            hypotheses.append(
                Hypothesis(
                    id=f"hyp_{uuid.uuid4().hex[:10]}",
                    statement=(
                        "Existe uma falha operacional ou de ambiente nas etapas observadas; "
                        "a causa precisa ser isolada antes de concluir sobre o objetivo."
                    ),
                    confidence=min(0.8, 0.45 + 0.08 * len(failed)),
                    evidence_ids=[obs.evidence_id for obs in failed],
                    counterevidence_ids=[obs.evidence_id for obs in successful[:2]],
                )
            )

        if successful:
            hypotheses.append(
                Hypothesis(
                    id=f"hyp_{uuid.uuid4().hex[:10]}",
                    statement=(
                        "As evidencias coletadas sustentam parcialmente a continuidade do plano, "
                        "mas nao provam por si so a conclusao final."
                    ),
                    confidence=min(0.75, 0.4 + 0.05 * len(successful)),
                    evidence_ids=[obs.evidence_id for obs in successful],
                    counterevidence_ids=[obs.evidence_id for obs in failed],
                )
            )

        return hypotheses

    def generate(
        self,
        goal: Goal,
        step: Step,
        observations: list[Observation],
    ) -> list[Hypothesis]:
        generated = self._from_model(goal, step, observations)
        return generated or self._fallback(observations)
