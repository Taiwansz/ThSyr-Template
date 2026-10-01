"""Evidence-first reasoning layer for the ThSyr executive loop."""

from __future__ import annotations

import json
from typing import Any

from ..models.base import ChatMessage, ModelRequest, ModelRole, ModelTier
from ..models.gateway import ModelGateway
from .hypothesis import HypothesisEngine
from .models import Goal, Observation, Step


class EvidenceReasoner:
    """Turns tool observations into analysis without fabricating verification."""

    def __init__(
        self,
        gateway: ModelGateway | None = None,
        hypothesis_engine: HypothesisEngine | None = None,
    ) -> None:
        self.gateway = gateway or ModelGateway()
        self.hypothesis_engine = hypothesis_engine or HypothesisEngine(self.gateway)

    @staticmethod
    def _evidence(observations: list[Observation]) -> list[dict[str, Any]]:
        return [
            {
                "evidence_id": obs.evidence_id,
                "step_id": obs.step_id,
                "success": obs.success,
                "error": obs.error,
                "raw_output": obs.raw_output[:1600],
                "data": obs.data,
            }
            for obs in observations[-10:]
        ]

    @staticmethod
    def _confidence(observations: list[Observation]) -> float:
        if not observations:
            return 0.1
        successful = sum(1 for obs in observations if obs.success)
        failures = len(observations) - successful
        value = 0.3 + (successful * 0.1) - (failures * 0.08)
        return max(0.05, min(0.9, value))

    def _model_reasoning(
        self,
        mode: str,
        goal: Goal,
        step: Step,
        observations: list[Observation],
        hypotheses: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        if not self.gateway.providers:
            return None

        request = ModelRequest(
            tier=ModelTier.REASONING,
            temperature=0.1,
            max_tokens=1200,
            messages=[
                ChatMessage(
                    role=ModelRole.SYSTEM,
                    content=(
                        "Voce e a camada Evidence-First do ThSyr. Raciocine exclusivamente sobre "
                        "as observacoes fornecidas. Diferencie fato, inferencia e lacuna. Nunca use "
                        "expressoes como 'verificado' ou 'estavel' sem evidencia observavel. "
                        "Responda SOMENTE JSON com conclusion:str, confidence:0..1, "
                        "evidence_ids:[str], gaps:[str], recommended_next_action:str."
                    ),
                ),
                ChatMessage(
                    role=ModelRole.USER,
                    content=json.dumps(
                        {
                            "mode": mode,
                            "goal": goal.to_dict(),
                            "step": step.to_dict(),
                            "observations": self._evidence(observations),
                            "hypotheses": hypotheses,
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
            return None
        if not isinstance(parsed, dict) or not str(parsed.get("conclusion", "")).strip():
            return None

        valid_ids = {obs.evidence_id for obs in observations}
        evidence_ids = [
            str(item) for item in parsed.get("evidence_ids", [])
            if str(item) in valid_ids
        ]
        try:
            confidence = float(parsed.get("confidence", self._confidence(observations)))
        except (TypeError, ValueError):
            confidence = self._confidence(observations)

        return {
            "conclusion": str(parsed["conclusion"]).strip(),
            "confidence": max(0.0, min(1.0, confidence)),
            "evidence_ids": evidence_ids,
            "gaps": [str(item) for item in parsed.get("gaps", []) if str(item).strip()],
            "recommended_next_action": str(
                parsed.get("recommended_next_action", "continue_with_evidence")
            ),
            "reasoning_source": "model_gateway",
        }

    def analyze(
        self,
        goal: Goal,
        step: Step,
        observations: list[Observation],
    ) -> dict[str, Any]:
        hypotheses = [
            hypothesis.to_dict()
            for hypothesis in self.hypothesis_engine.generate(goal, step, observations)
        ]
        model_result = self._model_reasoning(
            "analysis", goal, step, observations, hypotheses
        )
        if model_result is not None:
            model_result["hypotheses"] = hypotheses
            model_result["evidence_count"] = len(observations)
            model_result["status"] = "reasoned"
            return model_result

        successful = [obs for obs in observations if obs.success]
        failed = [obs for obs in observations if not obs.success]
        evidence_ids = [obs.evidence_id for obs in observations]
        gaps: list[str] = []
        if not observations:
            gaps.append("Nenhuma observacao anterior disponivel.")
        if failed:
            gaps.append(f"{len(failed)} observacao(oes) falharam e exigem isolamento de causa.")

        conclusion = (
            f"Analise baseada em {len(observations)} evidencia(s): "
            f"{len(successful)} bem-sucedida(s) e {len(failed)} falha(s)."
        )
        return {
            "conclusion": conclusion,
            "confidence": self._confidence(observations),
            "evidence_ids": evidence_ids,
            "gaps": gaps,
            "recommended_next_action": "investigate_failures" if failed else "continue_with_evidence",
            "reasoning_source": "deterministic_evidence_fallback",
            "hypotheses": hypotheses,
            "evidence_count": len(observations),
            "status": "evidence_limited" if not observations else "reasoned",
        }

    def synthesize(
        self,
        goal: Goal,
        step: Step,
        observations: list[Observation],
    ) -> dict[str, Any]:
        hypotheses = [
            hypothesis.to_dict()
            for hypothesis in self.hypothesis_engine.generate(goal, step, observations)
        ]
        model_result = self._model_reasoning(
            "synthesis", goal, step, observations, hypotheses
        )
        if model_result is not None:
            model_result["hypotheses"] = hypotheses
            model_result["evidence_count"] = len(observations)
            model_result["status"] = "reasoned"
            return model_result

        successful = [obs for obs in observations if obs.success]
        failed = [obs for obs in observations if not obs.success]
        if observations:
            conclusion = (
                f"Sintese do objetivo '{goal.title}': {len(successful)} evidencia(s) "
                f"positiva(s), {len(failed)} falha(s). "
                "A conclusao permanece limitada ao que foi observado."
            )
        else:
            conclusion = (
                f"Sintese do objetivo '{goal.title}': nao ha evidencia observavel suficiente "
                "para declarar conclusao material."
            )

        return {
            "conclusion": conclusion,
            "confidence": self._confidence(observations),
            "evidence_ids": [obs.evidence_id for obs in observations],
            "gaps": ["Resolver observacoes com falha."] if failed else [],
            "recommended_next_action": "replan" if failed else "finish_or_collect_more_evidence",
            "reasoning_source": "deterministic_evidence_fallback",
            "hypotheses": hypotheses,
            "evidence_count": len(observations),
            "status": "evidence_limited" if not observations else "reasoned",
        }
