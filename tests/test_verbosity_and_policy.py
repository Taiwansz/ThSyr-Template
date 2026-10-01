"""
ThSyr Tests - Verbosity & Response Policy
Valida niveis de verbosidade, progressive disclosure e Evidence-First guard.
"""

import unittest

from engine.interaction.response_models import StructuredResponse
from engine.interaction.response_policy import ResponsePolicy
from engine.interaction.verbosity import VerbosityLevel, VerbosityManager


class TestVerbosityAndPolicy(unittest.TestCase):
    def test_verbosity_levels_and_shortcuts(self):
        vm = VerbosityManager()
        self.assertEqual(vm.current_level, VerbosityLevel.NORMAL)

        vm.set_global_level(1)
        self.assertEqual(vm.current_level, VerbosityLevel.COMPACT)

        vm.set_global_level("deep")
        self.assertEqual(vm.current_level, VerbosityLevel.DEEP)

        vm.set_global_level("c")
        self.assertEqual(vm.current_level, VerbosityLevel.COMPACT)

        # Override temporario
        vm.set_override(VerbosityLevel.DETAILED)
        self.assertEqual(vm.current_level, VerbosityLevel.DETAILED)
        vm.clear_override()
        self.assertEqual(vm.current_level, VerbosityLevel.COMPACT)

    def test_adaptive_verbosity_heuristics(self):
        vm = VerbosityManager(default_level=VerbosityLevel.NORMAL)
        # Operacao de alto risco operacional -> DETAILED
        v_risk = vm.calculate_effective_level("qualquer acao", operation_risk=5)
        self.assertEqual(v_risk, VerbosityLevel.DETAILED)

        # Pergunta curta direta -> COMPACT
        v_short = vm.calculate_effective_level("status")
        self.assertEqual(v_short, VerbosityLevel.COMPACT)

        # Analise profunda explicita -> DEEP
        v_deep = vm.calculate_effective_level("faca uma analise profunda da arquitetura")
        self.assertEqual(v_deep, VerbosityLevel.DEEP)

    def test_evidence_first_guard_demotes_unverified_claims(self):
        policy = ResponsePolicy()
        # Resposta alegando "resolvido" sem evidencia fisica
        resp = StructuredResponse(
            summary="Bug resolvido com sucesso.",
            answer="Corrigi o bug no supervisor.",
            evidence=[],  # Nenhuma evidencia
        )
        guarded = policy.apply_evidence_first_guard(resp)
        self.assertNotIn("resolvido", guarded.summary.lower())
        self.assertIn("planejado", guarded.summary.lower())

    def test_evidence_first_guard_permits_verified_claims(self):
        policy = ResponsePolicy()
        # Resposta com evidencia real comprovada
        resp = StructuredResponse(
            summary="Bug resolvido.",
            answer="O teste passou.",
            evidence=[{"verified": True, "exit_code": 0}],
        )
        guarded = policy.apply_evidence_first_guard(resp)
        self.assertEqual(guarded.summary, "Bug resolvido.")


if __name__ == "__main__":
    unittest.main()
