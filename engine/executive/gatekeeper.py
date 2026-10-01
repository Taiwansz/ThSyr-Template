"""
ThSyr Executive System - Prefrontal Plan Gate (Fase 4)
Aplica a governanca pre-frontal sobre a criacao e execucao de planos e passos:
- Tolerancia zero absoluta a emojis em titulos, metas, etapas e acoes
- Validacao de seguranca contra operacoes destrutivas nao autorizadas
- Verificacao de restricoes inegociaveis de projetos e entidades
"""

import re
from typing import Any, Optional

from ..config import setup_logger
from ..prefrontal_cortex import PrefrontalCortex
from .models import Goal, Plan, Step

logger = setup_logger("prefrontal_gatekeeper")

# Regex completa de deteccao de emojis em planos astrais Unicode
EMOJI_REGEX = re.compile(
    r"[\U00010000-\U0010ffff]|[\u2600-\u27BF]|[\u2300-\u23FF]|[\u2B50-\u2B55]"
)

DANGEROUS_ACTIONS = {
    "rm -rf", "drop database", "delete from", "truncate", "mkfs", ":(){ :|:& };:"
}


class PrefrontalPlanGate:
    def __init__(self, prefrontal: Optional[PrefrontalCortex] = None):
        self.prefrontal = prefrontal or PrefrontalCortex()

    def audit_goal(self, goal: Goal) -> tuple[bool, list[str]]:
        violations = []
        text = f"{goal.title} {goal.description}"

        if EMOJI_REGEX.search(text):
            violations.append("Presenca de emoji detectada na definicao do objetivo.")

        for dang in DANGEROUS_ACTIONS:
            if dang in text.lower():
                violations.append(f"Objetivo contem padrao de risco critico nao permitido: '{dang}'")

        approved = len(violations) == 0
        if not approved:
            logger.warning(f"Objetivo '{goal.id}' rejeitado pelo portao pre-frontal: {violations}")
        return approved, violations

    def audit_step(self, step: Step) -> tuple[bool, list[str]]:
        violations = []
        text = f"{step.action} {step.target} {step.description} {step.parameters!s}"

        if EMOJI_REGEX.search(text):
            violations.append(f"Presenca de emoji detectada na etapa {step.id}.")

        for dang in DANGEROUS_ACTIONS:
            if dang in text.lower():
                violations.append(f"Etapa {step.id} contem acao destrutiva proibida: '{dang}'")

        # Inviolable entity rules via PrefrontalCortex
        draft_check = f"Acao: {step.action} no alvo: {step.target}. {step.description}"
        audit_res = self.prefrontal.audit(draft_check)
        if audit_res.get("violations"):
            violations.extend(audit_res["violations"])

        approved = len(violations) == 0
        if not approved:
            logger.warning(f"Etapa {step.id} rejeitada pelo portao pre-frontal: {violations}")
        return approved, violations

    def audit_plan(self, plan: Plan) -> tuple[bool, list[str]]:
        violations = []
        if EMOJI_REGEX.search(plan.title):
            violations.append("Presenca de emoji detectada no titulo do plano.")

        for step in plan.steps:
            ok, step_viols = self.audit_step(step)
            if not ok:
                violations.extend(step_viols)

        approved = len(violations) == 0
        return approved, violations

    def adversarial_review(self, plan: Plan) -> dict[str, Any]:
        """
        Executa a Sabatina Adversarial (Doutrina Claudex / Cross-Model Plan Hardening):
        Avalia o plano sob 3 perspectivas de auditoria cética:
        1. Engenheiro Sênior (Complexidade e sobre-engenharia)
        2. Auditor de Segurança e Restrições Inegociáveis
        3. Confiabilidade e Tolerância a Falhas (SRE)

        Retorna veredito formal: APPROVED, REVISE ou BLOCKED.
        """
        approved, basic_violations = self.audit_plan(plan)
        if not approved:
            return {
                "verdict": "BLOCKED",
                "score": 0.0,
                "findings": [f"[SEGURANCA/RESTRICAO] {v}" for v in basic_violations],
                "roles_evaluated": ["senior_engineer", "security_auditor", "sre_architect"]
            }

        findings = []

        # 1. Checagem do Engenheiro Sênior: granularidade e etapas excessivas
        if len(plan.steps) > 8:
            findings.append("[SENIOR_ENGINEER] Plano possui mais de 8 etapas. Risco de complexidade e quebra de contexto. Recomenda-se modularizar.")

        # 2. Checagem SRE: passos sem acao ou alvo
        for s in plan.steps:
            if not s.action or not s.target:
                findings.append(f"[SRE] Etapa {s.id} sem acao ou alvo explicitamente definidos.")

        # 3. Determinar veredito
        if any("[SEGURANCA" in f for f in findings):
            verdict = "BLOCKED"
            score = 0.2
        elif len(findings) > 0:
            verdict = "REVISE"
            score = 0.7
        else:
            verdict = "APPROVED"
            score = 1.0

        return {
            "verdict": verdict,
            "score": score,
            "findings": findings,
            "roles_evaluated": ["senior_engineer", "security_auditor", "sre_architect"],
            "plan_id": plan.id,
            "steps_count": len(plan.steps)
        }
