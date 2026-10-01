"""
ThSyr Tests - Conversation Intelligence & Reference Resolution
Valida resolucao contextual de referentes (o primeiro, aquele arquivo, nao mexe no daemon),
memoria de rejeicoes e persistencia de estado conversacional.
"""

import tempfile
import unittest
from pathlib import Path

from engine.interaction.conversation_state import ConversationState
from engine.interaction.reference_resolver import ReferenceResolver


class TestConversationIntelligence(unittest.TestCase):
    def setUp(self):
        self.state = ConversationState(session_id="test_session_1")
        self.registry = self.state.object_registry
        self.resolver = ReferenceResolver(registry=self.registry, state=self.state)

    def test_resolve_numbered_and_ordinal_options(self):
        # Registra duas opcoes ativas
        self.registry.register_options([
            {"id": "opt_a", "label": "Corrigir no daemon", "command": "fix_daemon"},
            {"id": "opt_b", "label": "Corrigir no supervisor", "command": "fix_supervisor"},
        ])

        # 1. Atalho numerico
        res1 = self.resolver.resolve("1")
        self.assertTrue(res1.resolved)
        self.assertEqual(res1.intent, "SELECT_OPTION")
        self.assertEqual(res1.target_object.label, "Corrigir no daemon")

        # 2. Ordinal textual "o primeiro"
        res_ord1 = self.resolver.resolve("faz o primeiro")
        self.assertTrue(res_ord1.resolved)
        self.assertEqual(res_ord1.target_object.label, "Corrigir no daemon")

        # 3. Ordinal textual "o segundo"
        res_ord2 = self.resolver.resolve("prefiro o segundo")
        self.assertTrue(res_ord2.resolved)
        self.assertEqual(res_ord2.target_object.label, "Corrigir no supervisor")

        # 4. "o anterior"
        res_prev = self.resolver.resolve("executa o anterior")
        self.assertTrue(res_prev.resolved)
        self.assertEqual(res_prev.target_object.label, "Corrigir no daemon")

    def test_resolve_file_and_plan_references(self):
        self.registry.register(
            id="file_daemon",
            label="engine/runtime/daemon.py",
            category="file",
            value="engine/runtime/daemon.py",
        )
        self.registry.register(
            id="plan_ci",
            label="Plano de Correcao do CI",
            category="plan",
            value="plan_ci_123",
        )

        res_file = self.resolver.resolve("mostra aquele arquivo")
        self.assertTrue(res_file.resolved)
        self.assertEqual(res_file.intent, "SELECT_FILE")
        self.assertEqual(res_file.target_object.id, "file_daemon")

        res_plan = self.resolver.resolve("usa aquele plano")
        self.assertTrue(res_plan.resolved)
        self.assertEqual(res_plan.intent, "SELECT_PLAN")
        self.assertEqual(res_plan.target_object.id, "plan_ci")

    def test_resolve_exclusion_constraints(self):
        res = self.resolver.resolve("não mexe no daemon")
        self.assertTrue(res.resolved)
        self.assertEqual(res.intent, "CONSTRAINT_EXCLUDE")
        self.assertEqual(res.extracted_param, "daemon")

        res_ignore = self.resolver.resolve("ignora o arquivo de teste")
        self.assertTrue(res_ignore.resolved)
        self.assertEqual(res_ignore.intent, "CONSTRAINT_EXCLUDE")

    def test_rejection_memory(self):
        self.state.record_rejection("sol_mock_provider", "Usar MockProvider em producao", reason="inseguro")
        self.assertTrue(self.state.is_solution_rejected("sol_mock_provider"))
        self.assertFalse(self.state.is_solution_rejected("sol_other"))

    def test_conversation_state_handoff_roundtrip(self):
        self.state.set_active_context(
            subject="TokLang AST",
            goal="Otimizar parser",
            project="TokLang",
            file="engine/toklang/parser.py",
            plan="plan_toklang_1",
        )
        self.state.record_rejection("old_plan", "Plano com regex pura")

        with tempfile.TemporaryDirectory() as tmpdir:
            handoff_path = Path(tmpdir) / "interaction_handoff.json"
            self.state.save_handoff(handoff_path)

            restored = ConversationState(session_id="session_new")
            ok = restored.load_handoff(handoff_path)
            self.assertTrue(ok)
            self.assertEqual(restored.active_subject, "TokLang AST")
            self.assertEqual(restored.active_goal, "Otimizar parser")
            self.assertEqual(restored.active_file, "engine/toklang/parser.py")
            self.assertTrue(restored.is_solution_rejected("old_plan"))


if __name__ == "__main__":
    unittest.main()
