import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from engine.sync_engine import GitSyncEngine


class TestSyncEngine(unittest.TestCase):
    def setUp(self):
        self.temp_repo = Path(tempfile.mkdtemp())
        # Inicializa um repo git temporário para isolar os testes
        subprocess.run(["git", "init"], cwd=str(self.temp_repo), capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "ThSyr Test"], cwd=str(self.temp_repo), capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "test@thsyr.ai"], cwd=str(self.temp_repo), capture_output=True, check=True)
        self.sync = GitSyncEngine(repo_root=self.temp_repo)

    def tearDown(self):
        shutil.rmtree(self.temp_repo, ignore_errors=True)

    def test_clean_and_dirty_detection(self):
        self.assertFalse(self.sync.is_dirty())
        test_file = self.temp_repo / "teste.txt"
        test_file.write_text("conteudo", encoding="utf-8")
        self.assertTrue(self.sync.is_dirty())

    def test_checkpoint_commits_changes(self):
        test_file = self.temp_repo / "teste.txt"
        test_file.write_text("conteudo para checkpoint", encoding="utf-8")

        result = self.sync.checkpoint(
            scope="state(test)",
            summary="validacao de checkpoint",
            auto_push=False
        )

        self.assertEqual(result["status"], "success")
        self.assertTrue(result["committed"])
        self.assertFalse(self.sync.is_dirty())

        # Verifica log do commit
        log_proc = subprocess.run(["git", "log", "-1", "--pretty=%B"], cwd=str(self.temp_repo), capture_output=True, text=True)
        self.assertIn("state(test): validacao de checkpoint", log_proc.stdout)


if __name__ == "__main__":
    unittest.main()
