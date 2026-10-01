"""
ThSyr Executive System - Runner & Orchestrator (Fase 4)
Orquestra o ciclo executivo completo orientado a objetivos:
Goal -> Planner -> Plan -> Prefrontal Gate -> Step Execution -> Observation -> Verifier -> Next / Replan / Finish
Gera logs estruturados de eventos em state/events/ e atualiza o estado operacional em state/handoff.json.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

from ..cognitive_router import CognitiveRouter
from ..config import get_state_dir, setup_logger
from ..retriever import MemoryRetriever
from ..session_state import HandoffManager
from ..sync_engine import GitSyncEngine
from .gatekeeper import PrefrontalPlanGate
from .models import (
    ActionType,
    ExecutionResult,
    Goal,
    GoalStatus,
    Observation,
    Plan,
    Step,
    StepStatus,
)
from .planner import ExecutivePlanner
from .reasoning import EvidenceReasoner
from .verifier import ExecutiveVerifier

logger = setup_logger("executive_runner")


class ExecutiveRunner:
    def __init__(
        self,
        router: CognitiveRouter | None = None,
        handoff: HandoffManager | None = None,
        sync: GitSyncEngine | None = None,
        state_dir: Path | None = None,
        tool_bus: Any | None = None,
        event_sink: Optional[Callable[[dict[str, Any]], None]] = None,
    ):
        self.router = router or CognitiveRouter()
        self.handoff = handoff or HandoffManager()
        self.sync = sync or GitSyncEngine()
        self.state_dir = state_dir or get_state_dir()
        self.event_sink = event_sink

        self.goals_dir = self.state_dir / "goals"
        self.plans_dir = self.state_dir / "plans"
        self.events_dir = self.state_dir / "events"

        self.goals_dir.mkdir(parents=True, exist_ok=True)
        self.plans_dir.mkdir(parents=True, exist_ok=True)
        self.events_dir.mkdir(parents=True, exist_ok=True)

        self.planner = ExecutivePlanner(router=self.router)
        self.gatekeeper = PrefrontalPlanGate()
        self.verifier = ExecutiveVerifier()
        self.reasoner = EvidenceReasoner(gateway=self.router.model_gateway)
        self.retriever = MemoryRetriever(memory_manager=self.router.memory)

        from ..tools.bus import ToolBus
        self.tool_bus = tool_bus or ToolBus(state_dir=self.state_dir)

    # --- Persistencia de Metas e Planos ---

    def save_goal(self, goal: Goal) -> Path:
        path = self.goals_dir / f"{goal.id}.json"
        goal.updated_at = datetime.now(timezone.utc).isoformat()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(goal.to_dict(), f, indent=2, ensure_ascii=False)
        return path

    def load_goal(self, goal_id: str) -> Goal | None:
        path = self.goals_dir / f"{goal_id}.json"
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return Goal.from_dict(json.load(f))

    def list_goals(self) -> list[Goal]:
        goals = []
        for p in self.goals_dir.glob("*.json"):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    goals.append(Goal.from_dict(json.load(f)))
            except Exception as e:
                logger.warning(f"Erro ao carregar meta de {p}: {e}")
        goals.sort(key=lambda g: g.created_at, reverse=True)
        return goals

    def save_plan(self, plan: Plan) -> Path:
        path = self.plans_dir / f"{plan.id}.json"
        plan.updated_at = datetime.now(timezone.utc).isoformat()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(plan.to_dict(), f, indent=2, ensure_ascii=False)
        return path

    def load_plan(self, plan_id: str) -> Plan | None:
        path = self.plans_dir / f"{plan_id}.json"
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return Plan.from_dict(json.load(f))

    def emit_event(
        self,
        event_type: str,
        payload: dict[str, Any],
        project: str | None = None,
        entity: str | None = None,
        confidence: float = 1.0,
        importance: int = 3
    ) -> dict[str, Any]:
        """
        Registra um evento estruturado no Event Log (state/events/).
        """
        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()
        event_data = {
            "id": event_id,
            "timestamp": now,
            "type": event_type,
            "source": "executive_runner",
            "project": project or "ThSyr",
            "entity": entity or "ExecutiveSystem",
            "payload": payload,
            "confidence": confidence,
            "importance": importance
        }
        event_file = self.events_dir / f"{now.replace(':', '-')}_{event_id}.json"
        with open(event_file, "w", encoding="utf-8") as f:
            json.dump(event_data, f, indent=2, ensure_ascii=False)
        if self.event_sink is not None:
            try:
                self.event_sink(event_data)
            except Exception as e:
                logger.warning(f"Erro ao publicar evento no event_sink: {e}")
        return event_data

    # --- Execucao de Passos ---

    def execute_step(
        self,
        step: Step,
        goal: Goal,
        prior_observations: list[Observation] | None = None,
    ) -> Observation:
        step.status = StepStatus.IN_PROGRESS
        step.started_at = datetime.now(timezone.utc).isoformat()

        obs_time = datetime.now(timezone.utc).isoformat()
        action = step.action

        # Captura hash inicial de estado se alvo for arquivo local
        before_hash: Optional[str] = None
        target_path: Optional[Path] = None
        if step.target:
            try:
                candidate = Path(step.target)
                if candidate.exists() and candidate.is_file():
                    target_path = candidate
                    before_hash = hashlib.sha256(candidate.read_bytes()).hexdigest()
            except Exception:
                pass

        def build_observation(
            success: bool,
            data: Any = None,
            raw_output: str = "",
            error: Optional[str] = None,
            exit_code: int = 0
        ) -> Observation:
            after_hash: Optional[str] = None
            if target_path and target_path.exists() and target_path.is_file():
                try:
                    after_hash = hashlib.sha256(target_path.read_bytes()).hexdigest()
                except Exception:
                    pass
            stdout_hash = hashlib.sha256(raw_output.encode("utf-8")).hexdigest() if raw_output else None
            return Observation(
                step_id=step.id,
                timestamp=obs_time,
                success=success,
                before_state_hash=before_hash,
                after_state_hash=after_hash,
                exit_code=exit_code if not success and exit_code == 0 else exit_code,
                stdout_hash=stdout_hash,
                data=data,
                raw_output=raw_output,
                error=error
            )

        try:
            if action == ActionType.SEARCH_MEMORY.value:
                query = step.parameters.get("query", step.target)
                limit = step.parameters.get("limit", 3)
                t_res = self.tool_bus.execute("search_memory", query=query, limit=limit)
                return build_observation(
                    success=t_res.success,
                    data=t_res.data,
                    raw_output=t_res.raw_output,
                    error=t_res.error,
                    exit_code=0 if t_res.success else 1
                )

            elif action == ActionType.INSPECT_GIT.value:
                log_count = step.parameters.get("log_count", 3)
                t_res = self.tool_bus.execute("git_log", count=log_count)
                return build_observation(
                    success=t_res.success,
                    data=t_res.data,
                    raw_output=t_res.raw_output,
                    error=t_res.error,
                    exit_code=0 if t_res.success else 1
                )

            elif action == ActionType.READ_FILE.value:
                t_res = self.tool_bus.execute("read_file", path=step.target)
                return build_observation(
                    success=t_res.success,
                    data=t_res.data,
                    raw_output=t_res.raw_output,
                    error=t_res.error,
                    exit_code=0 if t_res.success else 1
                )

            elif self.tool_bus.get_tool(action):
                t_res = self.tool_bus.execute(action, **step.parameters)
                return build_observation(
                    success=t_res.success,
                    data=t_res.data,
                    raw_output=t_res.raw_output,
                    error=t_res.error,
                    exit_code=0 if t_res.success else 1
                )

            elif action == ActionType.ANALYZE.value:
                reasoning = self.reasoner.analyze(
                    goal,
                    step,
                    prior_observations or [],
                )
                conclusion = str(reasoning.get("conclusion", "")).strip()
                return build_observation(
                    success=True,
                    data=reasoning,
                    raw_output=conclusion,
                    exit_code=0,
                )

            elif action == ActionType.SYNTHESIZE.value:
                synthesis = self.reasoner.synthesize(
                    goal,
                    step,
                    prior_observations or [],
                )
                conclusion = str(synthesis.get("conclusion", "")).strip()
                return build_observation(
                    success=True,
                    data=synthesis,
                    raw_output=conclusion,
                    exit_code=0,
                )

            else:
                # Acao desconhecida e estritamente proibida sem ferramenta ou tratador formal (Lei 1)
                logger.warning(f"Rejeicao executiva: acao '{action}' nao permitida.")
                return build_observation(
                    success=False,
                    exit_code=1,
                    error="UNKNOWN_ACTION_NOT_PERMITTED",
                    data={"action": action, "target": step.target},
                    raw_output=f"Acao desconhecida '{action}' rejeitada: execucao exige ferramenta autorizada com evidencias (Lei 1)."
                )

        except Exception as e:
            logger.error(f"Erro na execucao do passo {step.id}: {e}", exc_info=True)
            return build_observation(
                success=False,
                exit_code=1,
                error=str(e),
                raw_output=str(e)
            )

    # --- Ciclo Executivo Completo ---

    def run_goal(self, goal: Goal) -> ExecutionResult:
        """
        Executa o pipeline completo:
        1. Auditoria pre-frontal do objetivo
        2. Planejamento (ou carregamento de plano)
        3. Auditoria pre-frontal do plano
        4. Execucao sequencial com verificacao e replanning
        5. Atualizacao de Session Handoff
        6. Emissao de eventos estruturados
        """
        self.emit_event("task_started", {"goal_id": goal.id, "title": goal.title}, project=goal.project)

        # 1. Auditoria da Meta
        ok_goal, viols_goal = self.gatekeeper.audit_goal(goal)
        if not ok_goal:
            goal.status = GoalStatus.FAILED
            self.save_goal(goal)
            self.emit_event("failure", {"goal_id": goal.id, "violations": viols_goal}, project=goal.project)
            return ExecutionResult(
                goal_id=goal.id,
                plan_id="",
                status=GoalStatus.FAILED,
                completed_steps=0,
                total_steps=0,
                final_summary=f"Meta rejeitada pelo Portao Pre-Frontal: {'; '.join(viols_goal)}"
            )

        goal.status = GoalStatus.IN_PROGRESS
        self.save_goal(goal)

        # Atualizar Handoff
        self.handoff.update_working_state(
            current_goal=goal.title,
            current_project=goal.project or "ThSyr"
        )

        # 2. Criar Plano
        plan = self.planner.create_plan(goal)
        self.save_plan(plan)

        # 3. Auditoria do Plano
        ok_plan, viols_plan = self.gatekeeper.audit_plan(plan)
        if not ok_plan:
            goal.status = GoalStatus.FAILED
            self.save_goal(goal)
            return ExecutionResult(
                goal_id=goal.id,
                plan_id=plan.id,
                status=GoalStatus.FAILED,
                completed_steps=0,
                total_steps=len(plan.steps),
                final_summary=f"Plano rejeitado pelo Portao Pre-Frontal: {'; '.join(viols_plan)}"
            )

        observations: list[Observation] = []
        max_replans = 2
        step_idx = 0

        while step_idx < len(plan.steps):
            step = plan.steps[step_idx]

            # Auditoria pre-frontal do passo individual
            ok_step, viols_step = self.gatekeeper.audit_step(step)
            if not ok_step:
                step.status = StepStatus.FAILURE
                step.error = f"Violacao pre-frontal: {'; '.join(viols_step)}"
                observations.append(Observation(
                    step_id=step.id,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    success=False,
                    raw_output=step.error
                ))
                break

            # Executar passo
            obs = self.execute_step(step, goal, prior_observations=observations)
            observations.append(obs)
            step.observation = obs.raw_output
            step.completed_at = datetime.now(timezone.utc).isoformat()

            observation_payload: dict[str, Any] = {
                "step_id": step.id,
                "action": step.action,
                "success": obs.success,
                "evidence_id": obs.evidence_id,
            }
            if isinstance(obs.data, dict):
                for key in (
                    "conclusion",
                    "confidence",
                    "evidence_ids",
                    "hypotheses",
                    "gaps",
                    "reasoning_source",
                ):
                    if key in obs.data:
                        observation_payload[key] = obs.data[key]
            self.emit_event(
                "observation",
                observation_payload,
                project=goal.project,
            )

            # Verificar observacao
            verif = self.verifier.verify_step_observation(step, obs)

            if verif.verified:
                step.status = StepStatus.SUCCESS
                self.handoff.complete_task(step.description)
                step_idx += 1
            else:
                step.status = StepStatus.FAILURE
                step.error = verif.feedback

                # Tentativa de Replanning
                if plan.replan_count < max_replans and verif.suggested_action == "REPLAN":
                    logger.info(f"Disparando replanning para o plano {plan.id}...")
                    self.emit_event("decision", {"action": "replan", "reason": verif.feedback}, project=goal.project)
                    plan = self.planner.replan(goal, plan, step, verif.feedback)
                    self.save_plan(plan)
                    step_idx = 0  # Reiniciar execucao a partir do novo plano
                else:
                    logger.warning(f"Falha definitiva no passo {step.id}. Abortando plano.")
                    break

        self.save_plan(plan)

        # Avaliacao final
        all_success = all(s.status == StepStatus.SUCCESS for s in plan.steps)
        if all_success:
            goal.status = GoalStatus.COMPLETED
            synthesis_observations = [
                obs for obs in observations
                if isinstance(obs.data, dict) and obs.data.get("conclusion")
            ]
            if synthesis_observations:
                summary = str(synthesis_observations[-1].data["conclusion"])
            else:
                summary = (
                    f"Objetivo '{goal.title}' executado em {len(plan.steps)} etapas; "
                    "nenhuma sintese baseada em evidencia foi produzida."
                )
            self.emit_event("task_completed", {"goal_id": goal.id, "status": "completed"}, project=goal.project)
        else:
            goal.status = GoalStatus.FAILED
            summary = f"Objetivo '{goal.title}' falhou. {sum(1 for s in plan.steps if s.status == StepStatus.SUCCESS)} de {len(plan.steps)} etapas concluidas."
            self.emit_event("failure", {"goal_id": goal.id, "status": "failed"}, project=goal.project)

        self.save_goal(goal)

        completed_count = sum(1 for s in plan.steps if s.status == StepStatus.SUCCESS)
        return ExecutionResult(
            goal_id=goal.id,
            plan_id=plan.id,
            status=goal.status,
            completed_steps=completed_count,
            total_steps=len(plan.steps),
            observations=observations,
            final_summary=summary
        )
