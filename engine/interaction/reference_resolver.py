"""
ThSyr Interaction Layer - Reference Resolver
Resolve referencias contextuais em linguagem natural para objetos concretos
da conversa (opcoes, arquivos, planos, acoes) com base em estado estruturado.
"""

import re
from dataclasses import dataclass, field
from typing import Optional

from .conversation_objects import ConversationObject, ConversationObjectRegistry
from .conversation_state import ConversationState


@dataclass
class ResolutionResult:
    resolved: bool
    intent: str
    target_object: Optional[ConversationObject] = None
    confidence: float = 0.0
    ambiguity_options: list[ConversationObject] = field(default_factory=list)
    extracted_param: Optional[str] = None
    message: Optional[str] = None


class ReferenceResolver:
    def __init__(self, registry: ConversationObjectRegistry, state: Optional[ConversationState] = None):
        self.registry = registry
        self.state = state

    def resolve(self, user_input: str) -> ResolutionResult:
        cleaned = user_input.strip()
        lower = cleaned.lower()

        # 1. Atalho numerico direto ("1", "2", "3")
        if cleaned.isdigit():
            obj = self.registry.get_by_shortcut(cleaned)
            if obj:
                return ResolutionResult(
                    resolved=True,
                    intent="SELECT_OPTION",
                    target_object=obj,
                    confidence=1.0,
                )

        # 2. Referencia ordinal ("o primeiro", "o segundo", "a segunda opcao", etc.)
        ordinal_map = {
            "primeiro": "1",
            "primeira": "1",
            "segundo": "2",
            "segunda": "2",
            "terceiro": "3",
            "terceira": "3",
            "quarto": "4",
            "quarta": "4",
            "quinto": "5",
            "quinta": "5",
        }
        for word, num in ordinal_map.items():
            if f"o {word}" in lower or f"a {word}" in lower or f"opcao {word}" in lower or f"opção {word}" in lower:
                obj = self.registry.get_by_shortcut(num)
                if obj:
                    return ResolutionResult(
                        resolved=True,
                        intent="SELECT_OPTION",
                        target_object=obj,
                        confidence=0.95,
                    )

        # 3. Referencia a "o anterior" / "a anterior" / "opcao anterior"
        if any(p in lower for p in ("o anterior", "a anterior", "opcao anterior", "opção anterior", "o de antes")):
            active_options = self.registry.get_active_options()
            if len(active_options) >= 2:
                # O anterior em relacao ao ultimo
                return ResolutionResult(
                    resolved=True,
                    intent="SELECT_OPTION",
                    target_object=active_options[-2],
                    confidence=0.85,
                )

        # 4. Afirmativas de continuidade / acao direta ("manda", "faz", "segue", "vai", "continua daqui", "executa")
        if lower in ("manda", "faz", "segue", "vai", "continua", "continua daqui", "executa", "sim", "pode"):
            latest_action = self.registry.get_latest_by_category("action")
            latest_option = self.registry.get_latest_by_category("option")
            target = latest_action or latest_option
            return ResolutionResult(
                resolved=target is not None,
                intent="CONFIRM",
                target_object=target,
                confidence=0.9 if target else 0.5,
            )

        # 5. Restricao ou negacao sobre entidade ("nao mexe no daemon", "nao mexe nisso", "ignora esse arquivo")
        neg_match = re.search(r"(?:n[aã]o mexe|n[aã]o altera|ignora|pula|esquece)\s+(?:no\s+|na\s+|em\s+|o\s+|a\s+)?([a-zA-Z0-9_\-./]+)", lower)
        if neg_match:
            entity_name = neg_match.group(1).strip()
            return ResolutionResult(
                resolved=True,
                intent="CONSTRAINT_EXCLUDE",
                extracted_param=entity_name,
                confidence=0.9,
            )

        # 6. Referencia a plano ("aquele plano", "esse plano", "usa aquele plano")
        if any(p in lower for p in ("aquele plano", "esse plano", "o plano", "ultimo plano", "último plano")):
            latest_plan = self.registry.get_latest_by_category("plan")
            if latest_plan:
                return ResolutionResult(
                    resolved=True,
                    intent="SELECT_PLAN",
                    target_object=latest_plan,
                    confidence=0.9,
                )
            elif self.state and self.state.active_plan:
                return ResolutionResult(
                    resolved=True,
                    intent="SELECT_PLAN",
                    extracted_param=self.state.active_plan,
                    confidence=0.8,
                )

        # 7. Referencia a arquivo ("aquele arquivo", "esse arquivo", "o arquivo")
        if any(p in lower for p in ("aquele arquivo", "esse arquivo", "o arquivo", "ultimo arquivo", "último arquivo")):
            latest_file = self.registry.get_latest_by_category("file")
            if latest_file:
                return ResolutionResult(
                    resolved=True,
                    intent="SELECT_FILE",
                    target_object=latest_file,
                    confidence=0.9,
                )
            elif self.state and self.state.active_file:
                return ResolutionResult(
                    resolved=True,
                    intent="SELECT_FILE",
                    extracted_param=self.state.active_file,
                    confidence=0.8,
                )

        # 8. Reversao ou insatisfacao ("volta como estava", "desfaz", "nao gostei dessa solucao")
        if any(p in lower for p in ("volta como estava", "desfaz", "reverte", "cancela isso", "nao gostei")):
            return ResolutionResult(
                resolved=True,
                intent="REVERT_OR_REJECT",
                confidence=0.85,
            )

        # Sem resolucao especifica detectada
        return ResolutionResult(
            resolved=False,
            intent="UNKNOWN",
            confidence=0.0,
        )
