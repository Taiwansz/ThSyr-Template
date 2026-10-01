import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from engine.embeddings import LayeredEmbeddingEngine
from engine.evolution_lab import EvolutionCandidate, EvolutionLab
from engine.executive.models import ActionType, Goal
from engine.executive.planner import ExecutivePlanner
from engine.memory_adaptation import MemoryAdaptationStore
from engine.memory_contradiction import MemoryContradictionDetector
from engine.memory_models import MemoryItem, MemoryMetadata
from engine.security_scanner import RepositorySecretScanner
from engine.war_room import WarRoomServer


class JsonGateway:
    def __init__(self, payload):
        self.providers = [object()]
        self.payload = payload

    def generate(self, request):
        return SimpleNamespace(content=json.dumps(self.payload))


class CognitiveExpansionV3Tests(unittest.TestCase):
    def test_planner_accepts_schema_valid_model_plan(self):
        gateway = JsonGateway(
            {
                "steps": [
                    {
                        "action": "search_memory",
                        "target": "ThSyr",
                        "description": "Collect prior evidence",
                        "parameters": {"query": "ThSyr"},
                    },
                    {
                        "action": "analyze",
                        "target": "ThSyr",
                        "description": "Analyze collected evidence",
                        "parameters": {},
                    },
                    {
                        "action": "synthesize",
                        "target": "Goal",
                        "description": "Synthesize evidence",
                        "parameters": {},
                    },
                ]
            }
        )
        planner = ExecutivePlanner(router=SimpleNamespace(model_gateway=gateway))
        goal = Goal(id="g-v3", title="Improve ThSyr", description="Use evidence")

        plan = planner.create_plan(goal)

        self.assertEqual(len(plan.steps), 3)
        self.assertTrue(all(step.parameters["_planner_source"] == "model_gateway" for step in plan.steps))
        self.assertEqual(plan.steps[-1].action, ActionType.SYNTHESIZE.value)

    def test_planner_rejects_unknown_model_action_and_falls_back(self):
        gateway = JsonGateway(
            {
                "steps": [
                    {
                        "action": "invent_tool",
                        "target": "x",
                        "description": "invalid",
                        "parameters": {},
                    },
                    {
                        "action": "analyze",
                        "target": "x",
                        "description": "invalid dependency",
                        "parameters": {},
                    },
                ]
            }
        )
        planner = ExecutivePlanner(router=SimpleNamespace(model_gateway=gateway))
        plan = planner.create_plan(Goal(id="g2", title="General goal", description="Do work"))

        self.assertEqual(plan.steps[0].parameters["_planner_source"], "deterministic")
        self.assertIn(ActionType.SEARCH_MEMORY.value, [step.action for step in plan.steps])

    def test_memory_adaptation_reinforces_useful_memory(self):
        with tempfile.TemporaryDirectory() as directory:
            store = MemoryAdaptationStore(Path(directory) / "adaptation.json")
            before = store.plasticity_score("m1")
            store.record_access("m1")
            store.record_feedback("m1", helpful=True)
            after = store.plasticity_score("m1")

        self.assertGreater(after, before)

    def test_contradiction_detector_requires_overlap_and_polarity_flip(self):
        existing = MemoryItem(
            metadata=MemoryMetadata(id="old"),
            title="War Room network mode",
            content="War Room ativo e permitido na rede local",
        )

        matches = MemoryContradictionDetector.detect(
            title="War Room network mode",
            content="War Room nao ativo e proibido na rede local",
            candidates=[existing],
        )

        self.assertEqual(matches[0].memory_id, "old")
        self.assertGreater(matches[0].score, 0.5)

    def test_layered_embedding_hash_fallback_is_normalized(self):
        engine = LayeredEmbeddingEngine(dim=32, mode="hash")
        vector = engine.embed("semantic memory planner evidence")
        norm = sum(value * value for value in vector)

        self.assertEqual(len(vector), 32)
        self.assertAlmostEqual(norm, 1.0, places=3)
        self.assertEqual(engine.last_backend, "hash")

    def test_evolution_lab_rejects_empty_candidate_without_touching_repo(self):
        lab = EvolutionLab(project_root=Path(tempfile.gettempdir()))
        verdict = lab.evaluate_candidate(
            EvolutionCandidate(id="empty", objective="none", patch_text="")
        )

        self.assertFalse(verdict.accepted)
        self.assertIn("empty", verdict.reason)

    def test_security_scanner_redacts_detected_values(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            secret_value = "super-secret-value-123"
            (root / "config.txt").write_text(
                f"api_key={secret_value}\n",
                encoding="utf-8",
            )
            findings = RepositorySecretScanner(root=root).scan()

        self.assertEqual(len(findings), 1)
        self.assertNotIn(secret_value, findings[0].preview)
        self.assertIn("REDACTED", findings[0].preview)

    def test_war_room_defaults_to_loopback_and_lan_requires_auth(self):
        local = WarRoomServer()
        lan = WarRoomServer(host="0.0.0.0", port=8081)

        self.assertEqual(local.host, "127.0.0.1")
        self.assertFalse(local.require_auth)
        self.assertTrue(lan.require_auth)
        self.assertTrue(bool(lan.auth_token))


if __name__ == "__main__":
    unittest.main()
