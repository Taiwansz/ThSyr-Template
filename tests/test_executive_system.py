"""
ThSyr Test Suite - Executive System (Fase 4)
Valida:
- Modelos tipados e serializacao (Goal, Plan, Step, Observation, etc.)
- Portao pre-frontal de planos e passos (rejeicao de emojis e comandos perigosos)
- Decomposicao heuristica e replanning do ExecutivePlanner
- Avaliacao de observacoes pelo ExecutiveVerifier
- Execucao ponta-a-ponta pelo ExecutiveRunner e emissao de Event Logs
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from engine.executive.gatekeeper import PrefrontalPlanGate
from engine.executive.models import (
    ActionType,
    Goal,
    GoalStatus,
    Observation,
    Plan,
    Step,
    StepStatus,
)
from engine.executive.planner import ExecutivePlanner
from engine.executive.runner import ExecutiveRunner
from engine.executive.verifier import ExecutiveVerifier
from engine.session_state import HandoffManager


class TestExecutiveSystem(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.state_dir = self.temp_dir / "state"
        self.brain_dir = self.temp_dir / "brain"
        self.handoff = HandoffManager(state_dir=self.state_dir, brain_dir=self.brain_dir)
        self.runner = ExecutiveRunner(handoff=self.handoff, state_dir=self.state_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_models_serialization(self):
        step = Step(
            id="s1",
            order=1,
            action=ActionType.SEARCH_MEMORY.value,
            target="TokLang",
            description="Buscar contexto de TokLang",
            status=StepStatus.PENDING
        )
        step_dict = step.to_dict()
        self.assertEqual(step_dict["id"], "s1")
        self.assertEqual(step_dict["status"], "pending")

        restored_step = Step.from_dict(step_dict)
        self.assertEqual(restored_step.id, step.id)
        self.assertEqual(restored_step.status, StepStatus.PENDING)

        goal = Goal(
            id="g1",
            title="Diagnosticar TokLang",
            description="Levantar estado do compilador",
            project="TokLang",
            priority=1
        )
        g_dict = goal.to_dict()
        restored_goal = Goal.from_dict(g_dict)
        self.assertEqual(restored_goal.title, goal.title)
        self.assertEqual(restored_goal.priority, 1)

    def test_prefrontal_gate_rejection(self):
        gate = PrefrontalPlanGate()

        # 1. Rejeicao de emoji em meta
        goal_with_emoji = Goal(
            id="g_bad",
            title="Planejar lancamento \U0001F680",
            description="Objetivo com emoji"
        )
        approved, viols = gate.audit_goal(goal_with_emoji)
        self.assertFalse(approved)
        self.assertTrue(any("emoji" in v.lower() for v in viols))

        # 2. Rejeicao de comando destrutivo
        step_destructive = Step(
            id="s_bad",
            order=1,
            action="custom",
            target="root",
            description="Executar rm -rf / para limpar disco"
        )
        approved_step, viols_step = gate.audit_step(step_destructive)
        self.assertFalse(approved_step)
        self.assertTrue(any("destrutiva" in v.lower() for v in viols_step))

        # 3. Aprovacao de meta valida
        valid_goal = Goal(
            id="g_good",
            title="Verificar estado do TokLang",
            description="Levantar pendencias e commits recentes",
            project="TokLang"
        )
        approved_valid, viols_valid = gate.audit_goal(valid_goal)
        self.assertTrue(approved_valid)
        self.assertEqual(len(viols_valid), 0)

    def test_executive_planner_decomposition(self):
        planner = ExecutivePlanner()
        goal = Goal(
            id="g_toklang",
            title="Veja o estado do TokLang e prepare o plano",
            description="Inspecao completa do projeto TokLang",
            project="TokLang"
        )
        plan = planner.create_plan(goal)
        self.assertEqual(plan.goal_id, goal.id)
        self.assertGreater(len(plan.steps), 2)
        # Deve conter passos de memoria e inspecao
        actions = [s.action for s in plan.steps]
        self.assertIn(ActionType.SEARCH_MEMORY.value, actions)
        self.assertIn(ActionType.INSPECT_GIT.value, actions)

    def test_executive_verifier(self):
        verifier = ExecutiveVerifier()
        step = Step(
            id="s1",
            order=1,
            action=ActionType.SEARCH_MEMORY.value,
            target="TokLang",
            description="Buscar memoria"
        )

        # Caso de sucesso
        obs_ok = Observation(
            step_id="s1",
            timestamp="2026-09-15T12:00:00Z",
            success=True,
            data=[{"title": "TokLang Roadmap"}],
            raw_output="1 resultado encontrado."
        )
        res_ok = verifier.verify_step_observation(step, obs_ok)
        self.assertTrue(res_ok.verified)
        self.assertEqual(res_ok.status, "PASS")

        # Caso de falha de execucao
        obs_fail = Observation(
            step_id="s1",
            timestamp="2026-09-15T12:00:00Z",
            success=False,
            raw_output="Timeout na busca"
        )
        res_fail = verifier.verify_step_observation(step, obs_fail)
        self.assertFalse(res_fail.verified)
        self.assertEqual(res_fail.status, "FAIL")
        self.assertEqual(res_fail.suggested_action, "REPLAN")

    def test_end_to_end_goal_execution(self):
        goal = Goal(
            id="goal_toklang_audit",
            title="Inspecionar estado do TokLang",
            description="Verificar documentacao e status recente",
            project="TokLang"
        )
        result = self.runner.run_goal(goal)

        # O objetivo deve ter sido executado com sucesso
        self.assertEqual(result.status, GoalStatus.COMPLETED)
        self.assertGreater(result.completed_steps, 0)
        self.assertEqual(result.completed_steps, result.total_steps)

        # Verificar persistencia em disco
        saved_goal = self.runner.load_goal(goal.id)
        self.assertIsNotNone(saved_goal)
        self.assertEqual(saved_goal.status, GoalStatus.COMPLETED)

        saved_plan = self.runner.load_plan(result.plan_id)
        self.assertIsNotNone(saved_plan)

        # Verificar emissao de eventos estruturados em state/events/
        events = list((self.state_dir / "events").glob("*.json"))
        self.assertGreater(len(events), 0)

        # Validar integracao com Session Handoff
        active_handoff = self.handoff.load_handoff()
        self.assertEqual(active_handoff.current_goal, goal.title)

    def test_adversarial_plan_review(self):
        gate = PrefrontalPlanGate()

        # 1. Plano robusto e enxuto -> APPROVED
        good_plan = Plan(
            id="plan_good",
            goal_id="g1",
            title="Atualizacao de seguranca do RLS",
            steps=[
                Step(id="s1", order=1, action="read_file", target="schema.sql", description="Ler schema"),
                Step(id="s2", order=2, action="inspect_git", target="main", description="Checar branch")
            ]
        )
        res_good = gate.adversarial_review(good_plan)
        self.assertEqual(res_good["verdict"], "APPROVED")
        self.assertEqual(res_good["score"], 1.0)
        self.assertEqual(len(res_good["findings"]), 0)

        # 2. Plano com excesso de etapas (>8) -> REVISE
        too_many_steps = [
            Step(id=f"s{i}", order=i, action="read_file", target=f"file_{i}.py", description="ler")
            for i in range(1, 11)
        ]
        bloated_plan = Plan(
            id="plan_bloated",
            goal_id="g2",
            title="Refatoracao hiper-fragmentada",
            steps=too_many_steps
        )
        res_bloated = gate.adversarial_review(bloated_plan)
        self.assertEqual(res_bloated["verdict"], "REVISE")
        self.assertTrue(any("SENIOR_ENGINEER" in f for f in res_bloated["findings"]))

        # 3. Plano violando restricao destrutiva -> BLOCKED
        bad_plan = Plan(
            id="plan_bad",
            goal_id="g3",
            title="Limpeza destrutiva",
            steps=[
                Step(id="s1", order=1, action="execute_command", target="rm -rf /", description="destruir tudo")
            ]
        )
        res_bad = gate.adversarial_review(bad_plan)
        self.assertEqual(res_bad["verdict"], "BLOCKED")
        self.assertEqual(res_bad["score"], 0.0)


if __name__ == "__main__":
    unittest.main()
