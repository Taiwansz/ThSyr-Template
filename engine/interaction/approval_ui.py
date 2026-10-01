"""
ThSyr Interaction Layer - Approval UI
Sistema estruturado de aprovacoes operacionais com apresentacao de impacto,
arquivos afetados, nivel de risco (0-6), reversibilidade e parsing natural.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional


class ApprovalDecision(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    VIEW_DIFF = "view_diff"
    MODIFIED = "modified"


@dataclass
class ApprovalRequest:
    action_name: str
    impact_summary: str
    affected_files: list[str] = field(default_factory=list)
    risk_level: int = 3
    reversible: bool = True
    rollback_strategy: Optional[str] = None
    verification_available: str = "Testes unitarios e hash diff"
    options: list[dict[str, str]] = field(default_factory=list)

    def __post_init__(self):
        if not self.options:
            self.options = [
                {"key": "A", "label": "Aprovar execucao"},
                {"key": "D", "label": "Ver diff planejado"},
                {"key": "N", "label": "Cancelar"},
            ]


class ApprovalUI:
    def __init__(self, input_provider: Optional[Callable[[str], str]] = None):
        self.input_provider = input_provider or input

    def render_request(self, req: ApprovalRequest) -> str:
        """Renderiza o quadro estruturado de solicitacao de autorizacao."""
        lines = [
            "--------------------------------------------------",
            f"SOLICITACAO DE APROVACAO OPERACIONAL: {req.action_name.upper()}",
            "--------------------------------------------------",
            f"Impacto:          {req.impact_summary}",
            f"Nivel de Risco:   {req.risk_level}/6",
            f"Reversivel:       {'SIM' if req.reversible else 'NAO'}",
        ]
        if req.rollback_strategy:
            lines.append(f"Rollback:         {req.rollback_strategy}")
        if req.affected_files:
            lines.append(f"Arquivos:         {', '.join(req.affected_files)}")
        lines.append(f"Verificacao:      {req.verification_available}")
        lines.append("Opcoes:")
        for opt in req.options:
            lines.append(f"  [{opt['key']}] {opt['label']}")
        lines.append("--------------------------------------------------")
        return "\n".join(lines)

    def parse_user_response(self, user_response: str) -> tuple[ApprovalDecision, Optional[str]]:
        """
        Analisa a resposta do operador, aceitando atalhos de tecla unica ou linguagem natural.
        """
        cleaned = user_response.strip().lower()

        # Teclas de atalho simples
        if cleaned in ("a", "[a]", "sim", "s", "pode", "manda", "vai", "autorizo", "ok"):
            return ApprovalDecision.APPROVED, None

        if cleaned in ("n", "[n]", "nao", "não", "cancela", "para", "deixa", "abortar"):
            return ApprovalDecision.REJECTED, None

        if cleaned in ("d", "[d]", "diff", "ver diff"):
            return ApprovalDecision.VIEW_DIFF, None

        # Aprovacoes modificadas em linguagem natural ("só cria a branch", "não faz push", etc.)
        if "só" in cleaned or "so" in cleaned or "sem" in cleaned or "nao faz" in cleaned or "não faz" in cleaned:
            return ApprovalDecision.MODIFIED, user_response.strip()

        # Padrao conservador: qualquer entrada incompreendida nao autoriza acao de risco
        return ApprovalDecision.REJECTED, "Entrada nao reconhecida como aprovacao explicita."
