import unittest

from engine.memory_consolidator import MemoryConsolidator


class TestMemoryConsolidator(unittest.TestCase):
    def setUp(self):
        self.consolidator = MemoryConsolidator()

    def test_audit_ontology_structure(self):
        diag = self.consolidator.audit_ontology()
        self.assertIn("timestamp", diag)
        self.assertIn("ohi_score", diag)
        self.assertIn("status", diag)
        self.assertIn("total_nodes", diag)
        self.assertIn("total_synapses", diag)
        self.assertIn("orphaned_entities_count", diag)
        self.assertGreaterEqual(diag["ohi_score"], 0.0)
        self.assertLessEqual(diag["ohi_score"], 1.0)

    def test_scan_orphaned_nodes(self):
        data = self.consolidator.scan_orphaned_nodes()
        self.assertIn("total_wikilinks", data)
        self.assertIn("valid_wikilinks", data)
        self.assertIn("orphaned_count", data)
        self.assertIn("orphans", data)

    def test_render_report(self):
        report = self.consolidator.render_report()
        self.assertIn("CONSOLIDADOR ONTOLOGICO", report)
        self.assertIn("Indice de Saude (OHI):", report)


if __name__ == "__main__":
    unittest.main()
