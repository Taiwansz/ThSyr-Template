"""
Critico visual multimodal do ThSyr.

Regra central: se o screenshot nao chegou a um provedor de visao real, a
auditoria falha fechada. Nunca converter ausencia de visao em "aprovado".
"""

import json
import re
from pathlib import Path
from typing import Any

from ..models.base import ChatMessage, ModelRequest, ModelRole, ModelTier
from ..models.gateway import ModelGateway, ModelUnavailableError
from .contracts import CritiqueIssue, IssueSeverity, VisualBrief, VisualCritique

REQUIRED_SCORE_DIMENSIONS = (
    "composition",
    "hierarchy",
    "typography",
    "color_contrast",
    "brand_specificity",
    "asset_quality",
    "usability",
    "originality",
)


class VisualCritic:
    def __init__(self, gateway: ModelGateway | None = None):
        self.gateway = gateway or ModelGateway()

    @staticmethod
    def _extract_json(text: str) -> dict[str, Any]:
        cleaned = text.strip()
        fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", cleaned, re.DOTALL | re.IGNORECASE)
        if fenced:
            cleaned = fenced.group(1)
        else:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start >= 0 and end > start:
                cleaned = cleaned[start:end + 1]
        data = json.loads(cleaned)
        if not isinstance(data, dict):
            raise ValueError("resposta do critico nao e um objeto JSON")
        return data

    @staticmethod
    def _failure(viewport: str, reason: str) -> VisualCritique:
        issue = CritiqueIssue(
            severity=IssueSeverity.BLOCKER,
            category="vision_pipeline",
            problem="Auditoria visual real indisponivel.",
            evidence=reason,
            fix="Configurar um provedor VISION que consuma a imagem renderizada e executar a auditoria novamente.",
            viewport=viewport,
        )
        return VisualCritique(
            passed=False,
            score=0,
            summary="Falha fechada: nao existe evidencia visual suficiente para aprovar o artefato.",
            scores={dimension: 0 for dimension in REQUIRED_SCORE_DIMENSIONS},
            issues=[issue],
            viewport=viewport,
        )

    def critique(self, image_path: str | Path, brief: VisualBrief, viewport: str = "asset") -> VisualCritique:
        path = Path(image_path)
        if not path.is_file():
            return self._failure(viewport, f"Imagem nao encontrada: {path}")

        system_prompt = """
Voce e o diretor de arte e QA visual do ThSyr.
Avalie APENAS o que esta realmente visivel na imagem anexada.
Seja severo com AI-slop, genericidade, composicao preguiçosa, iconografia ruim,
imagens sem intencao, hierarquia fraca, inconsistencias mobile e falta de
identidade de marca.

Retorne SOMENTE JSON valido com este schema:
{
  "summary": "diagnostico curto e concreto",
  "scores": {
    "composition": 0,
    "hierarchy": 0,
    "typography": 0,
    "color_contrast": 0,
    "brand_specificity": 0,
    "asset_quality": 0,
    "usability": 0,
    "originality": 0
  },
  "issues": [
    {
      "severity": "blocker|major|minor",
      "category": "categoria",
      "problem": "problema observavel",
      "evidence": "o que na imagem prova o problema",
      "fix": "correcao especifica"
    }
  ]
}
Nao aprove por cortesia. Nao invente elementos que nao estao visiveis.
""".strip()

        user_prompt = (
            "BRIEF CANONICO:\n"
            + json.dumps(brief.to_dict(), ensure_ascii=False, indent=2)
            + f"\n\nVIEWPORT/ARTEFATO AVALIADO: {viewport}"
        )

        request = ModelRequest(
            messages=[
                ChatMessage(role=ModelRole.SYSTEM, content=system_prompt),
                ChatMessage(role=ModelRole.USER, content=user_prompt),
            ],
            tier=ModelTier.VISION,
            images=[str(path.resolve())],
            temperature=0.1,
            max_tokens=1800,
            metadata={"purpose": "visual_quality_gate", "viewport": viewport},
        )

        try:
            response = self.gateway.generate(request)
            payload = self._extract_json(response.content)
        except (ModelUnavailableError, RuntimeError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
            return self._failure(viewport, str(exc))

        raw_scores = payload.get("scores")
        if not isinstance(raw_scores, dict):
            return self._failure(viewport, "Critico retornou JSON sem objeto scores.")

        scores: dict[str, int] = {}
        for dimension in REQUIRED_SCORE_DIMENSIONS:
            value = raw_scores.get(dimension, 0)
            try:
                scores[dimension] = max(0, min(100, int(value)))
            except (TypeError, ValueError):
                scores[dimension] = 0

        issues: list[CritiqueIssue] = []
        for item in payload.get("issues", []):
            if not isinstance(item, dict):
                continue
            severity_raw = str(item.get("severity", "major")).lower()
            severity = IssueSeverity(severity_raw) if severity_raw in {s.value for s in IssueSeverity} else IssueSeverity.MAJOR
            issues.append(
                CritiqueIssue(
                    severity=severity,
                    category=str(item.get("category", "visual")),
                    problem=str(item.get("problem", "Problema visual nao especificado.")),
                    evidence=str(item.get("evidence", "Sem evidencia descrita.")),
                    fix=str(item.get("fix", "Revisar manualmente.")),
                    viewport=viewport,
                )
            )

        overall = round(sum(scores.values()) / len(REQUIRED_SCORE_DIMENSIONS))
        has_blocker = any(issue.severity == IssueSeverity.BLOCKER for issue in issues)
        floor_ok = all(value >= brief.minimum_dimension_score for value in scores.values())
        passed = overall >= brief.minimum_score and floor_ok and not has_blocker

        return VisualCritique(
            passed=passed,
            score=overall,
            summary=str(payload.get("summary", "Auditoria concluida.")),
            scores=scores,
            issues=issues,
            viewport=viewport,
            provider_name=response.provider_name,
            model_name=response.model_name,
        )
