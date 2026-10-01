import unittest

from engine.cognitive_router import CognitiveRouter


class TestCognitiveRouter(unittest.TestCase):
    def setUp(self):
        self.router = CognitiveRouter()

    def test_status_returns_real_metrics(self):
        stat = self.router.status()
        self.assertEqual(stat["status"], "online")
        self.assertGreater(stat["total_nodes"], 0)
        self.assertGreater(stat["total_synapses"], 0)
        self.assertIsInstance(stat["total_episodic_sessions"], int)
        self.assertGreaterEqual(stat["total_episodic_sessions"], 0)
        self.assertIn("frontal", stat["lobes"])

    def test_route_activation_and_compact_prompt(self):
        result = self.router.route("padroes de engenharia e arquitetura")
        self.assertIn("prompt", result)
        self.assertIn("activation", result)
        self.assertIn("seeds", result)
        self.assertIn("Padroes_Engenharia", result["seeds"])
        self.assertTrue(len(result["activation"]["top_activated"]) > 0)


if __name__ == "__main__":
    unittest.main()
