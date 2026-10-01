import shutil
import tempfile
import unittest
from pathlib import Path

from engine.memory_manager import MemoryManager
from engine.runtime.events import RuntimeEventBus
from engine.runtime.rem import REMConsolidator


class TestREMConsolidator(unittest.TestCase):
    def setUp(self):
        self.brain = Path(tempfile.mkdtemp())
        self.state = Path(tempfile.mkdtemp())
        self.bus = RuntimeEventBus()
        self.rem = REMConsolidator(
            self.bus,
            memory_manager=MemoryManager(root=self.brain, state_dir=self.state),
        )

    def tearDown(self):
        shutil.rmtree(self.brain, ignore_errors=True)
        shutil.rmtree(self.state, ignore_errors=True)

    def test_consolidates_workspace_events_into_episodic_memory(self):
        self.bus.publish(
            "workspace_mutation",
            {"files": ("engine/auth.py", ".env"), "high_signal": True},
        )
        result = self.rem.run_cycle()
        self.assertEqual(result["status"], "consolidated")
        self.assertTrue(result["high_signal"])
        memories = list((self.brain / "memories" / "episodic").glob("*.md"))
        self.assertEqual(len(memories), 1)
        content = memories[0].read_text(encoding="utf-8")
        self.assertIn("engine/auth.py", content)
        self.assertIn("high_signal", content)

    def test_consolidates_analysis_summary_without_content(self):
        self.bus.publish(
            "workspace_mutation",
            {
                "files": ("module.py",),
                "high_signal": False,
                "analysis": {"summary": "1 arquivo(s): .py"},
            },
        )
        result = self.rem.run_cycle()
        self.assertEqual(result["status"], "consolidated")
        content = next((self.brain / "memories" / "episodic").glob("*.md")).read_text(encoding="utf-8")
        self.assertIn("Resumo: 1 arquivo(s): .py", content)

    def test_empty_cycle_is_idle(self):
        self.assertEqual(self.rem.run_cycle()["status"], "idle")


if __name__ == "__main__":
    unittest.main()
