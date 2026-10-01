import unittest
from pathlib import Path

from engine.graph_indexer import reindex_and_audit


class TestGraphIndexer(unittest.TestCase):
    def test_reindex_and_audit_execution(self):
        summary = reindex_and_audit()
        self.assertIn("total_nodes", summary)
        self.assertIn("total_edges", summary)
        self.assertGreater(summary["total_nodes"], 50)
        self.assertGreater(summary["total_edges"], 100)
        self.assertIn("top_hubs", summary)
        self.assertTrue(len(summary["top_hubs"]) > 0)
        canvas_path = Path(summary["canvas_html"])
        self.assertTrue(canvas_path.exists())
        self.assertTrue(canvas_path.parent.joinpath("knowledge_graph.json").exists())


if __name__ == "__main__":
    unittest.main()
