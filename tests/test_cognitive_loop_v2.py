import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from engine.executive.hypothesis import HypothesisEngine
from engine.executive.models import Goal, Observation, Step
from engine.executive.reasoning import EvidenceReasoner
from engine.interaction.context_budget import ContextBudgetManager
from engine.interaction.conversation_state import ConversationState
from engine.memory_models import MemoryItem, MemoryMetadata
from engine.retriever import MemoryRetriever
from engine.vector_store import LocalVectorStore


class NoProviderGateway:
    providers: list[object] = []

    def generate(self, request):
        raise AssertionError("Model gateway must not be called in deterministic fallback tests")


class EmptySynapticEngine:
    def activate(self, query: str):
        return {"top_activated": []}


class CandidateRetriever(MemoryRetriever):
    def __init__(self, candidates, db_path: Path):
        memory = SimpleNamespace(working=SimpleNamespace(project=""))
        super().__init__(
            memory_manager=memory,
            synaptic_engine=EmptySynapticEngine(),
            vector_store=LocalVectorStore(db_path=db_path, dim=64),
            brain_dir=db_path.parent,
        )
        self._candidates = candidates

    def _load_all_candidate_items(self):
        return list(self._candidates)


class CognitiveLoopV2Tests(unittest.TestCase):
    def test_hypothesis_engine_marks_missing_evidence(self):
        engine = HypothesisEngine(gateway=NoProviderGateway())
        goal = Goal(id="g1", title="Diagnosticar falha", description="Encontrar causa")
        step = Step(id="s1", order=1, action="analyze", target="repo", description="Analisar")

        hypotheses = engine.generate(goal, step, [])

        self.assertEqual(len(hypotheses), 1)
        self.assertEqual(hypotheses[0].status, "insufficient_evidence")
        self.assertLess(hypotheses[0].confidence, 0.3)

    def test_reasoner_uses_real_evidence_ids(self):
        gateway = NoProviderGateway()
        reasoner = EvidenceReasoner(
            gateway=gateway,
            hypothesis_engine=HypothesisEngine(gateway=gateway),
        )
        goal = Goal(id="g2", title="Investigar CI", description="Encontrar erros")
        step = Step(id="s2", order=2, action="analyze", target="ci", description="Analisar CI")
        observations = [
            Observation(step_id="read", success=True, raw_output="mypy encontrou erro"),
            Observation(step_id="test", success=False, raw_output="exit 1", error="TYPE_ERROR"),
        ]

        result = reasoner.analyze(goal, step, observations)

        self.assertEqual(result["evidence_count"], 2)
        self.assertEqual(set(result["evidence_ids"]), {obs.evidence_id for obs in observations})
        self.assertEqual(result["reasoning_source"], "deterministic_evidence_fallback")
        self.assertNotIn("status operacional estavel", result["conclusion"].lower())

    def test_context_budget_is_a_hard_limit(self):
        state = ConversationState(session_id="budget-test")
        state.set_active_context(goal="Corrigir o ThSyr", project="ThSyr")
        state.add_message("user", "mensagem recente " * 80)
        state.add_message("assistant", "resposta recente " * 80)

        manager = ContextBudgetManager(max_prompt_tokens=220)
        compiled = manager.build_effective_context(
            state=state,
            system_base="invariantes do sistema " * 30,
            retrieved_pack="evidencia recuperada " * 160,
            max_history_turns=2,
        )

        self.assertLessEqual(manager.estimate_tokens(compiled), 220)
        self.assertIn("ESTADO OPERACIONAL ATIVO", compiled)
        self.assertIn("Corrigir o ThSyr", compiled)

    def test_contradicted_memory_is_penalized(self):
        temp_dir = Path(tempfile.mkdtemp())
        try:
            current = MemoryItem(
                metadata=MemoryMetadata(
                    id="current",
                    confidence=0.9,
                    importance=0.8,
                ),
                title="Current database policy",
                content="database security rule postgres",
            )
            legacy = MemoryItem(
                metadata=MemoryMetadata(
                    id="legacy",
                    confidence=1.0,
                    importance=1.0,
                    contradicted_by="current",
                ),
                title="Legacy database policy",
                content="database security rule postgres",
            )
            retriever = CandidateRetriever(
                [legacy, current],
                temp_dir / "vectors.db",
            )

            results = retriever.retrieve("database security rule postgres", limit=2, min_score=0.01)

            self.assertGreaterEqual(len(results), 2)
            self.assertEqual(results[0].item.metadata.id, "current")
            legacy_result = next(item for item in results if item.item.metadata.id == "legacy")
            self.assertLess(legacy_result.integrity_penalty, 1.0)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
