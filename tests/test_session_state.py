import json
import shutil
import tempfile
import unittest
from pathlib import Path

from engine.session_state import HandoffManager, SessionState


class TestSessionState(unittest.TestCase):
    def setUp(self):
        self.temp_state = Path(tempfile.mkdtemp())
        self.temp_brain = Path(tempfile.mkdtemp())
        self.manager = HandoffManager(state_dir=self.temp_state, brain_dir=self.temp_brain)

    def tearDown(self):
        shutil.rmtree(self.temp_state, ignore_errors=True)
        shutil.rmtree(self.temp_brain, ignore_errors=True)

    def test_session_state_creation_and_serialization(self):
        s = SessionState(
            current_goal="Construir motor de continuidade",
            current_project="ThSyr",
            pending_steps=["etapa 1", "etapa 2"]
        )
        self.assertTrue(s.session_id)
        d = s.to_dict()
        self.assertEqual(d["current_goal"], "Construir motor de continuidade")

        restored = SessionState.from_dict(d)
        self.assertEqual(restored.session_id, s.session_id)
        self.assertEqual(restored.current_goal, s.current_goal)
        self.assertEqual(restored.pending_steps, ["etapa 1", "etapa 2"])

    def test_handoff_persistence_and_dual_format(self):
        s = SessionState(
            current_goal="Validar Handoff",
            next_action="Executar testes unitarios",
            completed_steps=["Etapa A"],
            pending_steps=["Etapa B"]
        )
        saved_path = self.manager.save_session(s)
        self.assertTrue(saved_path.exists())

        # Verifica handoff.json
        handoff_json = self.temp_state / "handoff.json"
        self.assertTrue(handoff_json.exists())
        data = json.loads(handoff_json.read_text(encoding="utf-8"))
        self.assertEqual(data["current_goal"], "Validar Handoff")

        # Verifica session_handoff.md
        handoff_md = self.temp_brain / "session_handoff.md"
        self.assertTrue(handoff_md.exists())
        md_text = handoff_md.read_text(encoding="utf-8")
        self.assertIn("Validar Handoff", md_text)
        self.assertIn("[x] Etapa A", md_text)
        self.assertIn("[ ] Etapa B", md_text)

        # Testa load_handoff
        loaded = self.manager.load_handoff()
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.session_id, s.session_id)
        self.assertEqual(loaded.current_goal, "Validar Handoff")


if __name__ == "__main__":
    unittest.main()
