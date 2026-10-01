"""ThSyr Executive Planner V2.

Generative planning is attempted through the Model Gateway, but every generated
plan is schema-validated and restricted to the Executive ActionType contract.
The deterministic planner remains the authoritative fallback for offline,
invalid, or unavailable model responses.
"""

from __future__ import annotations

import json
import uuid
from typing import Any

from ..cognitive_router import CognitiveRouter
from ..config import setup_logger
from ..models.base import ChatMessage, ModelRequest, ModelRole, ModelTier
from .models import ActionType, Goal, Plan, Step, StepStatus

logger = setup_logger("executive_planner")


class ExecutivePlanner:
    MAX_GENERATED_STEPS = 8
    MIN_GENERATED_STEPS = 2

    def __init__(self, router: CognitiveRouter | None = None):
        self.router = router or CognitiveRouter()

    @staticmethod
    def _allowed_actions() -> set[str]:
        return {
            ActionType.SEARCH_MEMORY.value,
            ActionType.READ_FILE.value,
            ActionType.INSPECT_GIT.value,
            ActionType.ANALYZE.value,
            ActionType.SYNTHESIZE.value,
        }

    def _parse_generated_steps(
        self,
        payload: Any,
        plan_id: str,
        goal: Goal,
    ) -> list[Step]:
        if not isinstance(payload, dict):
            return []
        raw_steps = payload.get("steps")
        if not isinstance(raw_steps, list):
            return []
        if not self.MIN_GENERATED_STEPS <= len(raw_steps) <= self.MAX_GENERATED_STEPS:
            return []

        allowed = self._allowed_actions()
        steps: list[Step] = []
        for index, raw in enumerate(raw_steps, 1):
            if not isinstance(raw, dict):
                return []
            action = str(raw.get("action", "")).strip()
            target = str(raw.get("target", "")).strip()
            description = str(raw.get("description", "")).strip()
            parameters = raw.get("parameters", {})
            if action not in allowed or not target or not description:
                return []
            if not isinstance(parameters, dict):
                return []

            parameters = dict(parameters)
            parameters["_planner_source"] = "model_gateway"
            steps.append(
                Step(
                    id=f"{plan_id}_s{index}",
                    order=index,
                    action=action,
                    target=target,
                    description=description,
                    parameters=parameters,
                )
            )

        # A generated plan must eventually reason over collected evidence.
        if not any(step.action == ActionType.ANALYZE.value for step in steps):
            return []
        if steps[-1].action != ActionType.SYNTHESIZE.value:
            if len(steps) >= self.MAX_GENERATED_STEPS:
                return []
            steps.append(
                Step(
                    id=f"{plan_id}_s{len(steps) + 1}",
                    order=len(steps) + 1,
                    action=ActionType.SYNTHESIZE.value,
                    target=goal.title,
                    description="Sintetizar a conclusao final somente a partir das evidencias coletadas.",
                    parameters={
                        "goal_id": goal.id,
                        "_planner_source": "model_gateway_guardrail",
                    },
                )
            )
        return steps

    def _generative_plan(self, goal: Goal, plan_id: str) -> list[Step]:
        gateway = self.router.model_gateway
        if not gateway.providers:
            return []

        allowed = sorted(self._allowed_actions())
        system_prompt = (
            "Voce e o Planner V2 do ThSyr. Decomponha a meta em 2 a 8 passos "
            "auditaveis, pequenos e orientados a evidencias. Use SOMENTE as acoes "
            f"{allowed}. Nao invente ferramentas. ANALYZE deve ocorrer depois de "
            "alguma coleta de evidencia e o plano deve terminar em SYNTHESIZE. "
            "Responda SOMENTE JSON no formato "
            '{"steps":[{"action":"search_memory","target":"...","description":"...",'
            '"parameters":{}}]}.'
        )
        request = ModelRequest(
            tier=ModelTier.REASONING,
            temperature=0.1,
            max_tokens=1400,
            messages=[
                ChatMessage(role=ModelRole.SYSTEM, content=system_prompt),
                ChatMessage(
                    role=ModelRole.USER,
                    content=json.dumps(goal.to_dict(), ensure_ascii=False),
                ),
            ],
            metadata={"component": "executive_planner_v2", "goal_id": goal.id},
        )
        try:
            response = gateway.generate(request)
            payload = json.loads(response.content.strip())
        except Exception as exc:
            logger.debug("Planner generativo indisponivel: %s", exc)
            return []

        steps = self._parse_generated_steps(payload, plan_id=plan_id, goal=goal)
        if not steps:
            logger.warning("Plano generativo rejeitado pelo schema; usando fallback deterministico.")
        return steps

    def _deterministic_plan(self, goal: Goal, plan_id: str) -> list[Step]:
        combined = f"{goal.title.lower()} {goal.description.lower()}"

        if any(word in combined for word in ["toklang", "repo", "repositorio", "projeto", "estado"]):
            target = goal.project or ("TokLang" if "toklang" in combined else "ThSyr")
            return [
                Step(
                    id=f"{plan_id}_s1",
                    order=1,
                    action=ActionType.SEARCH_MEMORY.value,
                    target=target,
                    description=f"Buscar contexto e memoria relevante de {target}.",
                    parameters={"query": target, "limit": 3, "_planner_source": "deterministic"},
                ),
                Step(
                    id=f"{plan_id}_s2",
                    order=2,
                    action=ActionType.INSPECT_GIT.value,
                    target=target,
                    description=f"Inspecionar historico Git recente de {target}.",
                    parameters={"log_count": 5, "_planner_source": "deterministic"},
                ),
                Step(
                    id=f"{plan_id}_s3",
                    order=3,
                    action=ActionType.ANALYZE.value,
                    target=target,
                    description=f"Analisar as evidencias coletadas sobre {target}.",
                    parameters={"focus": "status_and_todos", "_planner_source": "deterministic"},
                ),
                Step(
                    id=f"{plan_id}_s4",
                    order=4,
                    action=ActionType.SYNTHESIZE.value,
                    target=goal.title,
                    description=f"Sintetizar conclusao baseada em evidencia para {target}.",
                    parameters={"goal_id": goal.id, "_planner_source": "deterministic"},
                ),
            ]

        if any(word in combined for word in ["memoria", "restricao", "regras", "audit", "entidade"]):
            return [
                Step(
                    id=f"{plan_id}_s1",
                    order=1,
                    action=ActionType.SEARCH_MEMORY.value,
                    target=goal.title,
                    description="Recuperar memorias e restricoes relevantes.",
                    parameters={"query": goal.title, "limit": 5, "_planner_source": "deterministic"},
                ),
                Step(
                    id=f"{plan_id}_s2",
                    order=2,
                    action=ActionType.ANALYZE.value,
                    target=goal.title,
                    description="Analisar aderencia as regras usando a evidencia recuperada.",
                    parameters={"check_constraints": True, "_planner_source": "deterministic"},
                ),
                Step(
                    id=f"{plan_id}_s3",
                    order=3,
                    action=ActionType.SYNTHESIZE.value,
                    target=goal.title,
                    description="Gerar sintese consolidada da auditoria cognitiva.",
                    parameters={"goal_id": goal.id, "_planner_source": "deterministic"},
                ),
            ]

        return [
            Step(
                id=f"{plan_id}_s1",
                order=1,
                action=ActionType.SEARCH_MEMORY.value,
                target=goal.title,
                description=f"Buscar conhecimento previo relevante para {goal.title}.",
                parameters={"query": goal.title, "limit": 3, "_planner_source": "deterministic"},
            ),
            Step(
                id=f"{plan_id}_s2",
                order=2,
                action=ActionType.ANALYZE.value,
                target=goal.title,
                description=f"Examinar requisitos e restricoes da meta {goal.title}.",
                parameters={"query": goal.description, "_planner_source": "deterministic"},
            ),
            Step(
                id=f"{plan_id}_s3",
                order=3,
                action=ActionType.SYNTHESIZE.value,
                target=goal.title,
                description="Elaborar conclusao final limitada as evidencias coletadas.",
                parameters={"goal_id": goal.id, "_planner_source": "deterministic"},
            ),
        ]

    def create_plan(self, goal: Goal) -> Plan:
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        steps = self._generative_plan(goal, plan_id)
        source = "model_gateway" if steps else "deterministic"
        if not steps:
            steps = self._deterministic_plan(goal, plan_id)

        plan = Plan(
            id=plan_id,
            goal_id=goal.id,
            title=f"Plano de Execucao: {goal.title}",
            steps=steps,
        )
        logger.info(
            "Plano %s criado com %s etapas via %s para '%s'",
            plan.id,
            len(steps),
            source,
            goal.title,
        )
        return plan

    def replan(self, goal: Goal, old_plan: Plan, failed_step: Step, reason: str) -> Plan:
        new_plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        completed = [step for step in old_plan.steps if step.status == StepStatus.SUCCESS]
        generated_goal = Goal(
            id=goal.id,
            title=f"Replanejar: {goal.title}",
            description=(
                f"{goal.description}\nFalha anterior: {failed_step.action} em "
                f"{failed_step.target}. Motivo: {reason}"
            ),
            project=goal.project,
            priority=goal.priority,
            metadata=dict(goal.metadata),
        )
        replacement = self._generative_plan(generated_goal, new_plan_id)
        if not replacement:
            replacement = [
                Step(
                    id=f"{new_plan_id}_rec",
                    order=1,
                    action=ActionType.SEARCH_MEMORY.value,
                    target=failed_step.target,
                    description=f"Buscar alternativa apos falha em {failed_step.id}: {reason}",
                    parameters={
                        "fallback": True,
                        "failed_action": failed_step.action,
                        "_planner_source": "deterministic_replan",
                    },
                ),
                Step(
                    id=f"{new_plan_id}_ana",
                    order=2,
                    action=ActionType.ANALYZE.value,
                    target=failed_step.target,
                    description="Analisar a evidencia de recuperacao e a causa da falha.",
                    parameters={"_planner_source": "deterministic_replan"},
                ),
                Step(
                    id=f"{new_plan_id}_fin",
                    order=3,
                    action=ActionType.SYNTHESIZE.value,
                    target=goal.title,
                    description=f"Consolidar replanejamento da meta {goal.id}.",
                    parameters={"replan": True, "_planner_source": "deterministic_replan"},
                ),
            ]

        new_steps: list[Step] = []
        for step in completed:
            step.order = len(new_steps) + 1
            new_steps.append(step)
        for step in replacement:
            step.id = f"{new_plan_id}_s{len(new_steps) + 1}"
            step.order = len(new_steps) + 1
            new_steps.append(step)

        return Plan(
            id=new_plan_id,
            goal_id=goal.id,
            title=f"Plano Revisado (Replan #{old_plan.replan_count + 1}): {goal.title}",
            steps=new_steps,
            replan_count=old_plan.replan_count + 1,
        )
