import json
import tempfile
import unittest
from pathlib import Path

from engine.knowledge_ingestor import ingest_workspaces


class TestKnowledgeIngestor(unittest.TestCase):
    def test_indexes_traceable_files_and_excludes_noise(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            (root / ".git").mkdir()
            (root / "node_modules").mkdir()
            (root / "README.md").write_text("# Project", encoding="utf-8")
            (root / "src" / "main.py").write_text("print('ok')", encoding="utf-8")
            (root / ".env").write_text("TOKEN=secret", encoding="utf-8")
            (root / "node_modules" / "ignored.js").write_text("ignored", encoding="utf-8")
            output = root / "index.json"

            graph = ingest_workspaces([root], output)

            labels = {node["label"] for node in graph["nodes"]}
            self.assertIn("README.md", labels)
            self.assertIn("src/main.py", labels)
            self.assertNotIn(".env", labels)
            self.assertNotIn("node_modules/ignored.js", labels)
            self.assertTrue(output.exists())
            persisted = json.loads(output.read_text(encoding="utf-8"))
            self.assertNotIn("TOKEN=secret", json.dumps(persisted))


if __name__ == "__main__":
    unittest.main()
