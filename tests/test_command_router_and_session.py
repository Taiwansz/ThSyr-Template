"""
ThSyr Tests - Command Router, Approvals, Interruption & Full Session
Valida roteamento de comandos de barra, aliases naturais, parsing de aprovacoes,
interrupcao de execucao e ciclo conversacional completo.
"""

import unittest

from engine.interaction.approval_ui import ApprovalDecision, ApprovalRequest, ApprovalUI
from engine.interaction.command_router import CommandRouter
from engine.interaction.conversation_state import ConversationState
from engine.interaction.interruption import InterruptionController, InterruptionType
from engine.interaction.presentation.mock_adapter import MockPresentationAdapter
from engine.interaction.reference_resolver import ReferenceResolver
from engine.interaction.response_models import ResponseKind, StructuredResponse
from engine.interaction.session_orchestrator import SyrConversationSession
from engine.interaction.terminal_renderer import TerminalRenderer
from engine.interaction.verbosity import VerbosityLevel, VerbosityManager


class TestCommandRouterAndSession(unittest.TestCase):
    def setUp(self):
        self.state = ConversationState()
        self.renderer = TerminalRenderer()
        self.verbosity = VerbosityManager()
        self.resolver = ReferenceResolver(self.state.object_registry, self.state)
        self.router = CommandRouter(self.state, self.renderer, self.verbosity, self.resolver)

    def test_universal_commands(self):
        # /help
        resp_help = self.router.handle("/help")
        self.assertIsNotNone(resp_help)
        self.assertIn("/details", resp_help.answer)

        # /status
        resp_status = self.router.handle("/status")
        self.assertIsNotNone(resp_status)
        self.assertIn("ThSyr v0.4.0", resp_status.summary)

        # /v 5
        resp_v = self.router.handle("/v 5")
        self.assertIsNotNone(resp_v)
        self.assertEqual(self.verbosity.current_level, VerbosityLevel.DEEP)

        # /details quando disponivel
        self.state.last_response = StructuredResponse(
            summary="Sumario",
            answer="Resposta",
            details="Logs detalhados de execucao",
        )
        resp_det = self.router.handle("/details")
        self.assertIsNotNone(resp_det)
        self.assertIn("Logs detalhados", resp_det.answer)

    def test_natural_aliases(self):
        self.state.last_response = StructuredResponse(
            summary="Decisao tomada",
            answer="Recomendo manter o supervisor.",
            sources=[{"kind": "observed", "identifier": "ci", "description": "CI run"}],
        )

        # "por que?" alias para /why
        resp_why = self.router.handle("por que?")
        self.assertIsNotNone(resp_why)
        self.assertIn("Justificativa", resp_why.answer)

        # "fonte" alias para /source
        resp_src = self.router.handle("fonte")
        self.assertIsNotNone(resp_src)
        self.assertEqual(len(resp_src.sources), 1)

    def test_approval_ui_parsing(self):
        ui = ApprovalUI()
        req = ApprovalRequest(
            action_name="git_push",
            impact_summary="Sincronizacao remota na branch main",
            risk_level=4,
            reversible=False,
        )
        rendered = ui.render_request(req)
        self.assertIn("GIT_PUSH", rendered)
        self.assertIn("4/6", rendered)

        # Aprovacao direta
        decision, _ = ui.parse_user_response("sim")
        self.assertEqual(decision, ApprovalDecision.APPROVED)

        decision_manda, _ = ui.parse_user_response("manda")
        self.assertEqual(decision_manda, ApprovalDecision.APPROVED)

        # Rejeicao
        decision_rej, _ = ui.parse_user_response("não")
        self.assertEqual(decision_rej, ApprovalDecision.REJECTED)

        # Aprovacao modificada
        decision_mod, mod_text = ui.parse_user_response("só cria a branch sem push")
        self.assertEqual(decision_mod, ApprovalDecision.MODIFIED)
        self.assertIn("sem push", mod_text)

    def test_interruption_controller(self):
        ctrl = InterruptionController()
        itype, reason = ctrl.classify_user_input("para")
        self.assertEqual(itype, InterruptionType.CANCEL)

        itype_pause, _ = ctrl.classify_user_input("pausa")
        self.assertEqual(itype_pause, InterruptionType.PAUSE)

        itype_mod, _ = ctrl.classify_user_input("não mexe no daemon")
        self.assertEqual(itype_mod, InterruptionType.MODIFY_PLAN)

        # Sinalizacao e checagem
        ctrl.signal_interruption(InterruptionType.CANCEL, "Abortado pelo operador")
        self.assertTrue(ctrl.should_abort())

    def test_syr_conversation_session_mock_turn(self):
        adapter = MockPresentationAdapter()
        session = SyrConversationSession(adapter=adapter)

        # Turno 1: Comand universal /status
        resp1 = session.process_turn("/status")
        self.assertIn("ThSyr v0.4.0", resp1.summary)

        # Turno 2: Restricao operacional
        resp2 = session.process_turn("não mexe no daemon")
        self.assertEqual(resp2.kind, ResponseKind.OPERATIONAL)
        self.assertIn("daemon", resp2.answer)
        self.assertTrue(session.interruption.is_entity_excluded("daemon"))


if __name__ == "__main__":
    unittest.main()
