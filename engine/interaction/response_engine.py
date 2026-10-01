"""
ThSyr Interaction Layer - Response Engine
Intermediario soberano entre os motores cognitivos/executivos e a camada de visualizacao.
Decide o que deve ser exibido, nivel de detalhe, evidencias e acoes seguintes.
"""

import json
import re
from typing import Any, Optional

from .conversation_state import ConversationState
from .interaction_profile import InteractionProfile
from .personality import SyrPersonalityEngine
from .response_models import ResponseKind, StructuredResponse
from .response_policy import ResponsePolicy
from .verbosity import VerbosityManager


class ResponseEngine:
    def __init__(
        self,
        personality: Optional[SyrPersonalityEngine] = None,
        policy: Optional[ResponsePolicy] = None,
        verbosity: Optional[VerbosityManager] = None,
        profile: Optional[InteractionProfile] = None,
        state: Optional[ConversationState] = None,
    ):
        self.personality = personality or SyrPersonalityEngine()
        self.policy = policy or ResponsePolicy()
        self.verbosity = verbosity or VerbosityManager()
        self.profile = profile or InteractionProfile()
        self.state = state or ConversationState()

    def process_raw_generation(
        self,
        raw_text: str,
        user_query: str = "",
        kind: ResponseKind = ResponseKind.CHAT,
        evidence: Optional[list[dict[str, Any]]] = None,
        sources: Optional[list[dict[str, Any]]] = None,
        actions: Optional[list[dict[str, Any]]] = None,
        details: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> StructuredResponse:
        """
        Transforma a saida bruta do modelo em um StructuredResponse consistente,
        aplicando sanitizacao de personalidade, politicas de evidencia e verbosidade.
        """
        # 1. Tentar parsear JSON estruturado caso o modelo tenha gerado contrato completo
        structured_candidate = self._try_parse_structured_json(raw_text)
        if structured_candidate:
            resp = structured_candidate
            if evidence:
                resp.evidence.extend(evidence)
            if sources:
                resp.sources.extend(sources)
            if actions:
                resp.actions.extend(actions)
            if details and not resp.details:
                resp.details = details
        else:
            # 2. Extrair sintese e resposta limpa a partir do texto
            cleaned_text = self.personality.sanitize_output(raw_text, user_query)
            cleaned_text = self.policy.sanitize_trivial_narration(cleaned_text)

            summary = self._extract_summary(cleaned_text)
            resp = StructuredResponse(
                summary=summary,
                answer=cleaned_text,
                kind=kind,
                details=details,
                evidence=evidence or [],
                sources=sources or [],
                actions=actions or [],
                metadata=metadata or {},
            )

        # 3. Aplicar guarda de Evidence-First
        resp = self.policy.apply_evidence_first_guard(resp)

        # 4. Ajustar conforme verbosidade efetiva
        effective_v = self.verbosity.calculate_effective_level(user_query)
        resp = self.policy.format_for_verbosity(resp, effective_v)

        # 5. Registrar acoes e opcoes no registro conversacional de objetos
        if resp.actions:
            self.state.object_registry.register_options(resp.actions)

        # 6. Salvar ultima resposta no estado
        self.state.last_response = resp
        return resp

    def _extract_summary(self, text: str) -> str:
        """Extrai a primeira oracao ou linha significativa como conclusao imediata."""
        if not text:
            return ""
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return ""
        first_line = lines[0]
        # Cortar na primeira sentenca se for longa
        sentences = re.split(r"(?<=[.!?])\s+", first_line)
        return sentences[0].strip()

    def _try_parse_structured_json(self, raw_text: str) -> Optional[StructuredResponse]:
        """Verifica se o output do modelo contem um JSON puro com o contrato de resposta."""
        candidate = raw_text.strip()
        if candidate.startswith("```json"):
            candidate = candidate.removeprefix("```json").removesuffix("```").strip()
        elif candidate.startswith("```"):
            candidate = candidate.removeprefix("```").removesuffix("```").strip()

        if candidate.startswith("{") and candidate.endswith("}"):
            try:
                data = json.loads(candidate)
                if "summary" in data or "answer" in data:
                    data["answer"] = self.personality.sanitize_output(data.get("answer", ""))
                    data["summary"] = self.personality.sanitize_output(data.get("summary", ""))
                    return StructuredResponse.from_dict(data)
            except Exception:
                pass
        return None
