import unittest

from engine.config import PROJECT_ROOT, Settings


class TestConfig(unittest.TestCase):
    def test_default_project_root_exists(self):
        self.assertTrue(PROJECT_ROOT.exists())
        self.assertTrue((PROJECT_ROOT / "brain").exists())

    def test_settings_structure(self):
        s = Settings()
        self.assertEqual(s.project_root, PROJECT_ROOT)
        self.assertTrue(s.sync.auto_push)
        self.assertEqual(s.sync.branch_name, "main")

    def test_ensure_directories(self):
        s = Settings()
        s.ensure_directories()
        self.assertTrue(s.brain.brain_dir.exists())
        self.assertTrue(s.brain.state_dir.exists())
        self.assertTrue((s.brain.state_dir / "sessions").exists())
        self.assertTrue((s.brain.state_dir / "events").exists())


if __name__ == "__main__":
    unittest.main()
