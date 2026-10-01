"""
Testes unitarios para o gravador de pulso neural e rastreabilidade sinaptica.
"""

import json
import tempfile
import unittest
from pathlib import Path

from engine.neural_pulse import get_last_neural_pulse, record_neural_pulse


class TestNeuralPulse(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.state_dir = Path(self.temp_dir.name) / "state"
        self.brain_dir = Path(self.temp_dir.name) / "brain"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_record_and_get_neural_pulse(self):
        pulse = record_neural_pulse(
            query="Como configurar o RLS no Supabase?",
            seeds=["Supabase_Stack"],
            top_activated=[
                {"id": "Supabase_Stack", "energy": 1.0, "lobe": "parietal"},
                {"id": "Padroes_Engenharia", "energy": 0.8, "lobe": "parietal"}
            ],
            constraints=["Sem bypass de RLS"],
            retrieved=[{"id": "mem_1", "title": "Supabase RLS Best Practices", "type": "procedural", "score": 0.95}],
            state_dir=self.state_dir,
            brain_dir=self.brain_dir
        )

        self.assertIsNotNone(pulse)
        self.assertTrue(pulse["id"].startswith("pulse_"))
        self.assertEqual(len(pulse["top_activated"]), 2)
        self.assertEqual(pulse["top_activated"][0]["lobe"], "parietal")

        # Verificar se o JSON foi persistido
        json_file = self.state_dir / "active_synapses.json"
        self.assertTrue(json_file.exists())
        saved_data = json.loads(json_file.read_text(encoding="utf-8"))
        self.assertEqual(saved_data["id"], pulse["id"])

        # Verificar se o JS foi gerado
        js_file = self.brain_dir / "active_synapses.js"
        self.assertTrue(js_file.exists())
        self.assertIn("window.__THSYR_PULSE__ =", js_file.read_text(encoding="utf-8"))

        # Testar get_last_neural_pulse
        last = get_last_neural_pulse(state_dir=self.state_dir)
        self.assertIsNotNone(last)
        self.assertEqual(last["id"], pulse["id"])


if __name__ == "__main__":
    unittest.main()
