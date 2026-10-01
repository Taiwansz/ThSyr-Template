"""
Design Tournament.

Generates multiple genuinely distinct art directions and, when real renders are
available, lets the multimodal critic choose only among directions that pass
the visual quality gate.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ..models import ModelGateway, ModelRouter
from ..models.base import ModelTier
from .contracts import VisualBrief
from .critic import VisualCritic


@dataclass
class DesignDirection:
    id: str
    name: str
    thesis: str
    composition: str
    typography: str
    palette_strategy: str
    imagery: str
    interaction: str
    anti_template_move: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DesignTournament:
    def __init__(
        self,
        gateway: ModelGateway | None = None,
        model_router: ModelRouter | None = None,
        critic: VisualCritic | None = None,
    ) -> None:
        self.gateway = gateway or ModelGateway()
        self.model_router = model_router or ModelRouter()
        self.critic = critic or VisualCritic(self.gateway)

    @staticmethod
    def _parse_json(content: str) -> dict[str, Any]:
        raw = content.strip()
        if raw.startswith("~~~"):
            raw = raw.strip("~")
        start, end = raw.find("{"), raw.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("tournament response has no JSON object")
        payload = json.loads(raw[start : end + 1])
        if not isinstance(payload, dict):
            raise ValueError("tournament response must be an object")
        return payload

    def generate(
        self,
        brief: VisualBrief,
        *,
        personalization_context: str = "",
        failure_context: str = "",
        count: int = 3,
    ) -> dict[str, Any]:
        if not getattr(self.gateway, "providers", None):
            return {
                "status": "unavailable",
                "reason": "no reasoning provider configured",
                "directions": [],
            }

        system = (
            "Voce e diretor de arte senior. Gere direcoes realmente diferentes, nao pequenas "
            "variacoes do mesmo template. Cada direcao precisa assumir uma tese de composicao, "
            "tipografia, imagem e interacao. Evite AI-slop, layouts SaaS por padrao e cliches. "
            "Retorne SOMENTE JSON valido."
        )
        schema = {
            "directions": [
                {
                    "id": "direction_a",
                    "name": "nome curto",
                    "thesis": "ideia central",
                    "composition": "estrutura espacial",
                    "typography": "estrategia tipografica",
                    "palette_strategy": "estrategia de cor",
                    "imagery": "direcao fotografica ou ilustrativa",
                    "interaction": "movimento e comportamento",
                    "anti_template_move": "decisao que impede aparencia de template",
                }
            ]
        }
        query = json.dumps(
            {
                "brief": brief.to_dict(),
                "personalization": personalization_context,
                "known_failures": failure_context,
                "count": max(2, min(4, count)),
                "schema": schema,
            },
            ensure_ascii=False,
        )
        request = self.model_router.build_request(
            query=query,
            system_prompt=system,
            forced_tier=ModelTier.REASONING,
        )
        try:
            response = self.gateway.generate(request)
            payload = self._parse_json(response.content)
        except Exception as exc:
            return {
                "status": "error",
                "reason": str(exc)[:220],
                "directions": [],
            }

        directions = []
        signatures: list[set[str]] = []
        for index, raw in enumerate(payload.get("directions", [])):
            if not isinstance(raw, dict):
                continue
            direction = DesignDirection(
                id=str(raw.get("id") or f"direction_{index + 1}"),
                name=str(raw.get("name") or f"Direcao {index + 1}")[:80],
                thesis=str(raw.get("thesis", ""))[:300],
                composition=str(raw.get("composition", ""))[:300],
                typography=str(raw.get("typography", ""))[:240],
                palette_strategy=str(raw.get("palette_strategy", ""))[:240],
                imagery=str(raw.get("imagery", ""))[:300],
                interaction=str(raw.get("interaction", ""))[:240],
                anti_template_move=str(raw.get("anti_template_move", ""))[:300],
            )
            signature = set(
                re.findall(
                    r"[a-zA-ZÀ-ÿ]{4,}",
                    " ".join([
                        direction.composition.lower(),
                        direction.typography.lower(),
                        direction.imagery.lower(),
                    ]),
                )
            )
            duplicate = any(
                len(signature.intersection(existing)) / max(1, len(signature)) > 0.78
                for existing in signatures
            )
            if duplicate:
                continue
            signatures.append(signature)
            directions.append(direction.to_dict())
            if len(directions) >= count:
                break

        status = "ready" if len(directions) >= 2 else "insufficient_diversity"
        return {
            "status": status,
            "provider": response.provider_name,
            "model": response.model_name,
            "directions": directions,
        }

    def review_renders(
        self,
        brief: VisualBrief,
        renders: dict[str, str | Path],
    ) -> dict[str, Any]:
        results = []
        for direction_id, image_path in renders.items():
            critique = self.critic.critique(
                image_path,
                brief,
                viewport=f"tournament:{direction_id}",
            )
            results.append({
                "direction_id": direction_id,
                "critique": critique.to_dict(),
            })

        passing = [
            result
            for result in results
            if result["critique"].get("passed")
        ]
        passing.sort(
            key=lambda result: result["critique"].get("score", 0),
            reverse=True,
        )
        return {
            "winner": passing[0]["direction_id"] if passing else None,
            "status": "winner_selected" if passing else "no_direction_passed",
            "results": results,
        }
