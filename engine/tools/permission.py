"""
ThSyr Permission Cortex (Fase 6)
Governa a autorizacao e execucao de chamadas do Tool Bus:
- Avalia niveis de risco de 0 (pesquisa) a 6 (critico)
- Portao de confirmacao para acoes de risco elevado
- Registro de auditoria operacional
"""

from collections.abc import Callable
from enum import Enum
from typing import Any

from ..config import setup_logger
from .base import RiskLevel, ToolMetadata

logger = setup_logger("permission_cortex")


class PermissionDecision(str, Enum):
    ALLOW = "allow"
    REQUIRE_CONFIRMATION = "require_confirmation"
    DENY = "deny"


class PermissionCortex:
    def __init__(
        self,
        max_autonomous_risk: RiskLevel = RiskLevel.LEVEL_2_CREATE_LOCAL,
        confirmation_handler: Callable[[str, dict[str, Any]], bool] | None = None
    ):
        self.max_autonomous_risk = max_autonomous_risk
        self.confirmation_handler = confirmation_handler

    def evaluate(self, tool: ToolMetadata, arguments: dict[str, Any]) -> tuple[PermissionDecision, str]:
        """
        Avalia se a chamada da ferramenta pode ser executada automaticamente,
        se exige confirmacao do operador, ou se deve ser negada.
        """
        risk = tool.risk_level

        # Nivel 6: Critico / Credenciais -> Negado por padrao a menos que explicitamente autorizado
        if risk >= RiskLevel.LEVEL_6_CRITICAL:
            msg = f"Acao de risco critico (Nivel {risk}) bloqueada por politica de seguranca."
            logger.warning(f"[PERMISSION DENIED] {tool.name}: {msg}")
            return PermissionDecision.DENY, msg

        # Nivel 5: Exclusao destrutiva de dados -> Exige confirmacao forte
        if risk == RiskLevel.LEVEL_5_DELETE_DATA:
            if not self.confirmation_handler:
                msg = "Acao destrutiva de Nivel 5 requer confirmacao humana explicita."
                logger.warning(f"[PERMISSION REQUIRED] {tool.name}: {msg}")
                return PermissionDecision.REQUIRE_CONFIRMATION, msg
            confirmed = self.confirmation_handler(tool.name, arguments)
            if confirmed:
                return PermissionDecision.ALLOW, "Autorizado pelo operador sob confirmacao forte."
            return PermissionDecision.DENY, "Rejeitado pelo operador."

        # Requer confirmacao explicita na ferramenta
        if tool.requires_confirmation or risk > self.max_autonomous_risk:
            if self.confirmation_handler:
                confirmed = self.confirmation_handler(tool.name, arguments)
                if confirmed:
                    return PermissionDecision.ALLOW, "Autorizado pelo operador via confirmacao."
                return PermissionDecision.DENY, "Rejeitado pelo operador."
            return PermissionDecision.REQUIRE_CONFIRMATION, (
                f"Ferramenta '{tool.name}' (Risco {risk}) excede o limiar autonomo "
                f"({self.max_autonomous_risk}) e necessita de confirmacao."
            )

        # Niveis 0, 1, 2: Execucao autonoma permitida
        return PermissionDecision.ALLOW, "Execucao autonoma autorizada."
