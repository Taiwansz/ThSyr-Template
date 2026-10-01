"""
Unit tests for Auto-Evolution Engine & Cognitive Optimization Core (Fase 11).
Hermetic, cross-platform and zero host dependency.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from engine.auto_evolution import (
    AutoEvolutionEngine,
    EntropyAuditor,
    EvolutionReport,
    InferenceAuditor,
)


class TestAutoEvolution(unittest.TestCase):
    def test_entropy_auditor_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            auditor = EntropyAuditor(brain_dir=Path(tmp_dir))
            res = auditor.audit()
            self.assertEqual(res["total_nodes"], 0)
            self.assertEqual(res["entropy_index"], 0.0)

    def test_entropy_auditor_with_graph_data(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            graph_data = {
                "total_nodes": 3,
                "total_edges": 2,
                "nodes": [{"id": "NodeA"}, {"id": "NodeB"}, {"id": "OrphanNode"}],
                "edges": [{"source": "NodeA", "target": "NodeB"}]
            }
            (tmp_path / "knowledge_graph.json").write_text(json.dumps(graph_data), encoding="utf-8")

            auditor = EntropyAuditor(brain_dir=tmp_path)
            res = auditor.audit()

            self.assertEqual(res["total_nodes"], 3)
            self.assertEqual(res["total_edges"], 1)
            self.assertIn("OrphanNode", res["orphaned_nodes"])
            self.assertAlmostEqual(res["entropy_index"], 1 / 3, places=2)
            self.assertAlmostEqual(res["density"], 1 / 3, places=2)

    def test_inference_auditor_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            auditor = InferenceAuditor(state_dir=Path(tmp_dir))
            res = auditor.audit()
            self.assertEqual(res["total_requests"], 0)
            self.assertEqual(res["efficiency_rating"], "OPTIMAL")

    def test_inference_auditor_with_telemetry_data(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            telem_data = {
                "total_requests": 10,
                "total_tokens": 10000,
                "total_cost_usd": 0.05,
                "total_latency_ms": 200.0
            }
            (tmp_path / "model_telemetry.json").write_text(json.dumps(telem_data), encoding="utf-8")

            auditor = InferenceAuditor(state_dir=tmp_path)
            res = auditor.audit()

            self.assertEqual(res["total_requests"], 10)
            self.assertEqual(res["total_tokens"], 10000)
            self.assertEqual(res["avg_latency_ms"], 20.0)
            self.assertEqual(res["efficiency_rating"], "OPTIMAL")

    def test_auto_evolution_engine_diagnose_and_render(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            brain_dir = tmp_path / "brain"
            state_dir = tmp_path / "state"
            brain_dir.mkdir()
            state_dir.mkdir()

            graph_data = {
                "total_nodes": 2,
                "total_edges": 1,
                "nodes": [{"id": "NodeA"}, {"id": "NodeB"}],
                "edges": [{"source": "NodeA", "target": "NodeB"}]
            }
            (brain_dir / "knowledge_graph.json").write_text(json.dumps(graph_data), encoding="utf-8")

            engine = AutoEvolutionEngine(brain_dir=brain_dir, state_dir=state_dir)
            report = engine.diagnose()

            self.assertIsInstance(report, EvolutionReport)
            self.assertEqual(report.generation, 1)
            self.assertEqual(report.total_nodes, 2)

            rendered = engine.render_report()
            self.assertIn("THSYR // COGNITIVE AUTO-EVOLUTION ENGINE", rendered)
            self.assertIn("Gen 1", rendered)

    @patch("engine.auto_evolution.reindex_and_audit")
    def test_trigger_evolution_saves_ledger(self, mock_reindex):
        mock_reindex.return_value = {"total_nodes": 50, "total_edges": 120}

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            brain_dir = tmp_path / "brain"
            state_dir = tmp_path / "state"
            brain_dir.mkdir()
            state_dir.mkdir()

            engine = AutoEvolutionEngine(brain_dir=brain_dir, state_dir=state_dir)
            res = engine.trigger_evolution(auto_apply=True)

            self.assertEqual(res["generation"], 1)
            self.assertEqual(res["status"], "EVOLVED")

            ledger = engine._load_ledger()
            self.assertEqual(len(ledger), 1)
            self.assertEqual(ledger[0]["generation"], 1)


if __name__ == "__main__":
    unittest.main()
