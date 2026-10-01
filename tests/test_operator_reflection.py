import json
import tempfile
import unittest
from pathlib import Path

from engine.models import ModelGateway
from engine.models.providers.mock import MockProvider
from engine.operator_intelligence import OperatorIntelligence
from engine.operator_reflection import OperatorReflectionEngine


class OperatorReflectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.intelligence = OperatorIntelligence(root / "operator.json")
        self.reflection_path = root / "reflections.json"
        self.telemetry_path = root / "telemetry.json"

    def _seed_signals(self):
        self.intelligence.observe("Manda bala e faz completo.")
        self.intelligence.observe("Manda bala nisso, quero end to end.")
        self.intelligence.observe("Documenta isso pra depois.")
        self.intelligence.observe("Deixa registrado para depois.")
        state = self.intelligence.load()
        return [
            signal["id"]
            for signal in state["signals"]
            if signal.get("source") != "deep_reflection"
        ]

    def _engine(self, response: str, **kwargs):
        provider = MockProvider(default_response=response)
        gateway = ModelGateway(
            providers=[provider],
            telemetry_file=self.telemetry_path,
            allow_mock=True,
        )
        return OperatorReflectionEngine(
            intelligence=self.intelligence,
            gateway=gateway,
            storage_path=self.reflection_path,
            enabled=True,
            min_signals=2,
            cooldown_seconds=0,
            max_signals=50,
            **kwargs,
        )

    def test_deep_reflection_records_second_order_hypothesis(self):
        ids = self._seed_signals()
        payload = {
            "patterns": [
                {
                    "category": "continuity_pattern",
                    "subject": "prefere que entregas sejam registradas para retomada futura",
                    "stance": "positive",
                    "confidence": 0.91,
                    "supporting_signal_ids": ids[-2:],
                    "counter_signal_ids": [],
                    "reason": "dois sinais independentes pedem documentacao e continuidade",
                }
            ],
            "curiosity": [],
        }
        engine = self._engine(json.dumps(payload))

        result = engine.run(force=True)

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["accepted_patterns"], 1)
        belief = next(
            belief
            for belief in self.intelligence.snapshot()["beliefs"]
            if belief["category"] == "reflection_continuity_pattern"
        )
        self.assertEqual(belief["status"], "hypothesis")
        self.assertLessEqual(belief["confidence"], 0.70)
        self.assertEqual(belief["explicit_count"], 0)

    def test_single_signal_model_claim_is_rejected(self):
        ids = self._seed_signals()
        payload = {
            "patterns": [
                {
                    "category": "working_style",
                    "subject": "prefere executar tudo imediatamente",
                    "stance": "positive",
                    "confidence": 0.95,
                    "supporting_signal_ids": [ids[0]],
                    "counter_signal_ids": [],
                    "reason": "apenas um sinal",
                }
            ],
            "curiosity": [],
        }
        result = self._engine(json.dumps(payload)).run(force=True)

        self.assertEqual(result["accepted_patterns"], 0)
        self.assertEqual(result["rejected_patterns"], 1)

    def test_unknown_signal_ids_are_rejected(self):
        self._seed_signals()
        payload = {
            "patterns": [
                {
                    "category": "decision_pattern",
                    "subject": "compara opcoes antes de consolidar decisoes",
                    "stance": "positive",
                    "confidence": 0.8,
                    "supporting_signal_ids": ["sig_fake_1", "sig_fake_2"],
                    "counter_signal_ids": [],
                    "reason": "evidencia inexistente",
                }
            ],
            "curiosity": [],
        }
        result = self._engine(json.dumps(payload)).run(force=True)
        self.assertEqual(result["accepted_patterns"], 0)

    def test_sensitive_inference_is_rejected(self):
        ids = self._seed_signals()
        payload = {
            "patterns": [
                {
                    "category": "decision_pattern",
                    "subject": "sua politica determina suas decisoes de produto",
                    "stance": "positive",
                    "confidence": 0.9,
                    "supporting_signal_ids": ids[:2],
                    "counter_signal_ids": [],
                    "reason": "inferir politica",
                }
            ],
            "curiosity": [],
        }
        result = self._engine(json.dumps(payload)).run(force=True)
        self.assertEqual(result["accepted_patterns"], 0)

    def test_counterevidence_can_block_model_hypothesis(self):
        ids = self._seed_signals()
        payload = {
            "patterns": [
                {
                    "category": "decision_pattern",
                    "subject": "prefere decidir rapidamente sem revisar alternativas",
                    "stance": "positive",
                    "confidence": 0.8,
                    "supporting_signal_ids": ids[:2],
                    "counter_signal_ids": ids[2:4],
                    "reason": "ha suporte e contraevidencia em igual volume",
                }
            ],
            "curiosity": [],
        }
        result = self._engine(json.dumps(payload)).run(force=True)
        self.assertEqual(result["accepted_patterns"], 0)

    def test_weak_reflected_hypothesis_only_enters_relevant_context(self):
        ids = self._seed_signals()
        payload = {
            "patterns": [
                {
                    "category": "continuity_pattern",
                    "subject": "prefere continuidade documentada entre sessoes de projeto",
                    "stance": "positive",
                    "confidence": 0.8,
                    "supporting_signal_ids": ids[-2:],
                    "counter_signal_ids": [],
                    "reason": "pedidos repetidos de registro",
                }
            ],
            "curiosity": [],
        }
        engine = self._engine(json.dumps(payload))
        engine.run(force=True)

        relevant = self.intelligence.build_context("como manter continuidade do projeto")
        unrelated = self.intelligence.build_context("qual geladeira escolher")

        self.assertIn("continuidade documentada", relevant)
        self.assertNotIn("continuidade documentada", unrelated)

    def test_invalid_json_does_not_advance_watermark(self):
        self._seed_signals()
        engine = self._engine("not json")

        result = engine.run(force=True)
        state = engine.load()

        self.assertEqual(result["status"], "error")
        self.assertIsNone(state["last_signal_id"])
        self.assertEqual(state["metrics"]["parse_failures"], 1)

    def test_curiosity_gap_from_reflection_is_persisted(self):
        self._seed_signals()
        payload = {
            "patterns": [],
            "curiosity": [
                {
                    "question": "Observar se prefere prototipos visuais antes da implementacao final",
                    "priority": 0.7,
                    "reason": "os sinais atuais ainda nao distinguem planejamento de preferencia visual",
                }
            ],
        }
        result = self._engine(json.dumps(payload)).run(force=True)

        self.assertEqual(result["curiosity_added"], 1)
        gaps = self.intelligence.snapshot()["curiosity"]
        self.assertTrue(any("prototipos visuais" in gap["question"] for gap in gaps))

    def test_duplicate_forced_reflection_does_not_reinforce_same_pattern(self):
        ids = self._seed_signals()
        payload = {
            "patterns": [
                {
                    "category": "working_style",
                    "subject": "prefere execucao ponta a ponta com registro de continuidade",
                    "stance": "positive",
                    "confidence": 0.8,
                    "supporting_signal_ids": ids[:2],
                    "counter_signal_ids": [],
                    "reason": "sinais repetidos de autonomia",
                }
            ],
            "curiosity": [],
        }
        engine = self._engine(json.dumps(payload))
        first = engine.run(force=True)
        second = engine.run(force=True)

        self.assertEqual(first["accepted_patterns"], 1)
        self.assertEqual(second["accepted_patterns"], 0)

    def test_non_forced_run_waits_for_minimum_signal_count(self):
        self.intelligence.observe("Manda bala.")
        provider = MockProvider(default_response='{"patterns":[],"curiosity":[]}')
        gateway = ModelGateway(
            providers=[provider],
            telemetry_file=self.telemetry_path,
            allow_mock=True,
        )
        engine = OperatorReflectionEngine(
            intelligence=self.intelligence,
            gateway=gateway,
            storage_path=self.reflection_path,
            enabled=True,
            min_signals=4,
            cooldown_seconds=0,
        )

        readiness = engine.should_reflect()
        self.assertFalse(readiness["ready"])
        self.assertIn(readiness["reason"], {"insufficient_evidence", "waiting_for_more_signals"})


if __name__ == "__main__":
    unittest.main()
