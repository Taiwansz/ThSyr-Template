import tempfile
import unittest
from pathlib import Path

from engine.readme_stats import update_readme_graph_stats


class TestReadmeStats(unittest.TestCase):
    def test_replaces_only_generated_block(self):
        with tempfile.TemporaryDirectory() as directory:
            readme = Path(directory) / "README.md"
            readme.write_text(
                "# ThSyr\n\n<!-- THSYR_GRAPH_STATS:START -->\nold\n<!-- THSYR_GRAPH_STATS:END -->\n\nKeep this.",
                encoding="utf-8",
            )

            update_readme_graph_stats({"nodes": [1, 2], "links": [1]}, readme)

            content = readme.read_text(encoding="utf-8")
            self.assertIn("`2` nós e `1` sinapses", content)
            self.assertIn("Keep this.", content)
            self.assertNotIn("old", content)


if __name__ == "__main__":
    unittest.main()
