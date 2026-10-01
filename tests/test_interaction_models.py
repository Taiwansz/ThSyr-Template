"""
ThSyr Tests - Interaction Layer Models & Contracts
Valida serializacao, progressive disclosure e contratos de resposta.
"""

import unittest

from engine.interaction.interaction_profile import InteractionProfile
from engine.interaction.response_models import (
    ResponseAction,
    ResponseKind,
    ResponseSource,
    SourceType,
    StructuredResponse,
)


class TestInteractionModels(unittest.TestCase):
    def test_structured_response_minimal(self):
        resp = StructuredResponse(summary="Operacao concluida.", answer="Tudo em ordem.")
        self.assertEqual(resp.summary, "Operacao concluida.")
        self.assertEqual(resp.answer, "Tudo em ordem.")
        self.assertEqual(resp.kind, ResponseKind.CHAT)
        self.assertFalse(resp.has_details())
        self.assertFalse(resp.has_evidence())
        self.assertFalse(resp.has_sources())
        self.assertFalse(resp.has_changes())

    def test_structured_response_full_roundtrip(self):
        action = ResponseAction(id="act1", label="Corrigir", command="git checkout", shortcut="1")
        source = ResponseSource(kind=SourceType.OBSERVED, identifier="ci_log", description="CI failure run")
        resp = StructuredResponse(
            summary="Falha no daemon.",
            answer="O supervisor do daemon travou.",
            kind=ResponseKind.ERROR,
            details="Traceback no subprocesso PID 1024",
            evidence=[{"exit_code": 1, "verified": False}],
            sources=[source.to_dict()],
            actions=[action.to_dict()],
            changes=[{"path": "daemon.py", "status": "modified"}],
        )

        self.assertTrue(resp.has_details())
        self.assertTrue(resp.has_evidence())
        self.assertTrue(resp.has_sources())
        self.assertTrue(resp.has_changes())
        self.assertTrue(resp.has_actions())

        d = resp.to_dict()
        reconstructed = StructuredResponse.from_dict(d)
        self.assertEqual(reconstructed.summary, resp.summary)
        self.assertEqual(reconstructed.kind, ResponseKind.ERROR)
        self.assertEqual(reconstructed.details, resp.details)
        self.assertEqual(len(reconstructed.evidence), 1)
        self.assertEqual(len(reconstructed.sources), 1)
        self.assertEqual(len(reconstructed.actions), 1)

    def test_interaction_profile_defaults_and_version(self):
        prof = InteractionProfile()
        self.assertEqual(prof.language, "pt-BR")
        self.assertEqual(prof.technical_depth, "high")
        self.assertTrue(prof.direct_answers)
        self.assertEqual(prof.version, 1)

        d = prof.to_dict()
        loaded = InteractionProfile.from_dict(d)
        self.assertEqual(loaded.version, 1)


if __name__ == "__main__":
    unittest.main()
