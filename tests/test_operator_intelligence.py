import json
import tempfile
import unittest
from pathlib import Path

from engine.operator_intelligence import OperatorIntelligence


class OperatorIntelligenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "operator.json"
        self.intelligence = OperatorIntelligence(self.path)

    def test_explicit_preference_is_persisted_and_contextualized(self):
        result = self.intelligence.observe(
            "Eu prefiro interfaces mobile first e bem limpas."
        )
        context = self.intelligence.build_context(
            "preciso criar uma interface mobile"
        )

        self.assertGreaterEqual(result["new_beliefs"], 1)
        self.assertIn("interfaces mobile first", context.lower())
        self.assertGreaterEqual(self.intelligence.status()["beliefs_total"], 1)

    def test_repeated_working_style_signal_strengthens_model(self):
        self.intelligence.observe("Manda bala e faz completo.")
        first = max(
            belief["confidence"]
            for belief in self.intelligence.snapshot()["beliefs"]
            if belief["category"] == "working_style"
        )
        self.intelligence.observe("Manda bala nisso, quero end to end.")
        second = max(
            belief["confidence"]
            for belief in self.intelligence.snapshot()["beliefs"]
            if belief["category"] == "working_style"
        )

        self.assertGreaterEqual(second, first)

    def test_conflicting_explicit_preference_creates_surprise(self):
        self.intelligence.observe("Eu gosto de fundos escuros.")
        result = self.intelligence.observe("Eu nao gosto de fundos escuros.")

        self.assertGreaterEqual(result["surprises"], 1)
        self.assertGreaterEqual(self.intelligence.status()["contested"], 1)

    def test_sensitive_domains_are_not_learned(self):
        result = self.intelligence.observe(
            "Eu gosto do partido X e minha religiao e Y."
        )

        self.assertEqual(result["signals"], 0)
        self.assertGreaterEqual(result["sensitive_skips"], 1)
        self.assertEqual(self.intelligence.status()["beliefs_total"], 0)

    def test_explicit_feedback_has_high_priority(self):
        result = self.intelligence.record_feedback(
            subject="hero editorial com fotografia grande",
            verdict="approved",
            reason="nao parece template",
        )

        self.assertTrue(result["recorded"])
        self.assertEqual(result["belief"]["status"], "confirmed")
        self.assertGreaterEqual(result["belief"]["confidence"], 0.78)

    def test_state_file_never_keeps_plain_secret_assignment(self):
        self.intelligence.observe(
            "Eu uso uma API. token=super-secret-value"
        )

        raw = self.path.read_text(encoding="utf-8")
        self.assertNotIn("super-secret-value", raw)

    def test_contextual_feedback_learns_active_subject(self):
        result = self.intelligence.observe(
            "Ficou ruim, melhore.",
            context_subject="Hero da cafeteria",
            context_project="Cafe Aurora",
        )

        self.assertGreaterEqual(result["signals"], 1)
        beliefs = self.intelligence.snapshot()["beliefs"]
        contextual = [
            belief for belief in beliefs
            if belief["category"] == "context_feedback"
        ]
        self.assertEqual(len(contextual), 1)
        self.assertEqual(contextual[0]["subject"], "Hero da cafeteria")
        self.assertEqual(contextual[0]["stance"], "negative")

    def test_negative_preference_does_not_create_positive_duplicate(self):
        self.intelligence.observe("Eu nao gosto de fundos escuros.")

        beliefs = [
            belief for belief in self.intelligence.snapshot()["beliefs"]
            if belief["category"] == "preference"
        ]
        self.assertEqual(len(beliefs), 1)
        self.assertEqual(beliefs[0]["stance"], "negative")

    def test_forget_removes_only_target_belief(self):
        self.intelligence.observe("Eu prefiro respostas diretas.")
        self.intelligence.observe("Eu uso terminal para desenvolver.")

        before = self.intelligence.snapshot()["beliefs"]
        self.assertGreaterEqual(len(before), 2)
        target = next(
            belief["key"]
            for belief in before
            if "respostas_diretas" in belief["key"]
        )

        self.assertTrue(self.intelligence.forget(target))
        after = self.intelligence.snapshot()["beliefs"]
        self.assertEqual(len(after), len(before) - 1)
        self.assertTrue(any("terminal" in belief["subject"] for belief in after))

    def test_secret_in_subject_is_redacted(self):
        self.intelligence.observe("Eu uso token=super-secret-value no terminal.")

        raw = self.path.read_text(encoding="utf-8")
        self.assertNotIn("super-secret-value", raw)
        self.assertIn("[REDACTED]", raw)

    def test_snapshot_is_json_serializable(self):
        self.intelligence.observe("Eu prefiro respostas diretas.")

        encoded = json.dumps(
            self.intelligence.snapshot(),
            ensure_ascii=False,
        )
        self.assertIn("respostas diretas", encoded)


if __name__ == "__main__":
    unittest.main()
