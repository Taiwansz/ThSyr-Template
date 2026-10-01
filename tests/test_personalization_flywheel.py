import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from engine.evolution_lab import EvolutionLab, GateResult
from engine.operator_intelligence import OperatorIntelligence
from engine.personalization.benchmark import PersonalBenchmarkSuite
from engine.personalization.hub import PersonalizationHub
from engine.personalization.outcomes import OutcomeLearningStore
from engine.personalization.preference_graph import PreferenceGraph, PreferenceScope
from engine.vector_store import LocalVectorStore
from engine.visual.contracts import VisualArtifactKind, VisualBrief
from engine.visual.failure_memory import VisualFailureMemory
from engine.visual.tournament import DesignTournament


class PersonalizationFlywheelTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        operator = OperatorIntelligence(root / "operator.json")
        vector = LocalVectorStore(db_path=root / "preferences.db", dim=64)
        graph = PreferenceGraph(root / "graph.json", vector_store=vector)
        outcomes = OutcomeLearningStore(root / "outcomes.json")
        self.hub = PersonalizationHub(
            operator_intelligence=operator,
            preference_graph=graph,
            outcomes=outcomes,
        )
        self.root = root

    def test_operator_signal_syncs_into_scoped_graph(self):
        result = self.hub.observe(
            "Eu prefiro interfaces mobile first e bem limpas.",
            project_id="Cafe Aurora",
            domain="design",
            artifact_kind="website",
        )

        self.assertGreaterEqual(result["graph_nodes_synced"], 1)
        same_project = self.hub.graph.query(
            "interface mobile",
            project_id="Cafe Aurora",
            domain="design",
            artifact_kind="website",
        )
        other_project = self.hub.graph.query(
            "interface mobile",
            project_id="Outro Projeto",
            domain="design",
            artifact_kind="website",
        )

        self.assertTrue(any("mobile first" in node["subject"] for node in same_project))
        self.assertFalse(any("mobile first" in node["subject"] for node in other_project))

    def test_semantic_graph_uses_vector_index_and_scope(self):
        self.hub.graph.upsert(
            category="visual_preference",
            subject="fotografia editorial grande com hierarquia forte",
            stance="positive",
            confidence=0.93,
            status="confirmed",
            source="test",
            scope=PreferenceScope.DOMAIN,
            domain="design",
        )

        results = self.hub.graph.query(
            "fotografia editorial",
            domain="design",
            artifact_kind="website",
        )

        self.assertTrue(results)
        self.assertEqual(results[0]["scope"], "domain")
        self.assertGreater(self.hub.graph.status()["vector_index_count"], 0)

    def test_contradiction_is_preserved_in_timeline(self):
        kwargs = dict(
            category="visual_preference",
            subject="fundos escuros",
            confidence=0.9,
            source="test",
            scope=PreferenceScope.GLOBAL,
        )
        self.hub.graph.upsert(stance="positive", **kwargs)
        result = self.hub.graph.upsert(stance="negative", **kwargs)

        self.assertEqual(result["node"]["status"], "contested")
        events = self.hub.graph.timeline(result["node"]["key"])
        self.assertEqual(events[-1]["event_type"], "contradicted")

    def test_outcome_learning_extracts_delta_and_updates_graph(self):
        outcome_id = self.hub.outcomes.begin(
            "Hero de cafeteria",
            project_id="Cafe Aurora",
            domain="design",
            artifact_kind="website",
        )
        bad = {
            "critiques": [{
                "scores": {"composition": 61, "originality": 55},
                "issues": [{
                    "category": "composition",
                    "problem": "hero parece template",
                }],
            }]
        }
        good = {
            "critiques": [{
                "scores": {"composition": 91, "originality": 88},
                "issues": [],
            }]
        }
        self.hub.outcomes.record_version(
            outcome_id,
            label="v1",
            artifact_ref="v1.png",
            verdict="rejected",
            review_report=bad,
        )
        self.hub.outcomes.record_version(
            outcome_id,
            label="v2",
            artifact_ref="v2.png",
            verdict="approved",
            review_report=good,
        )

        learned = self.hub.learn_outcome_resolution(
            outcome_id,
            rejected_label="v1",
            approved_label="v2",
            note="operador aprovou a segunda versao",
        )

        self.assertEqual(
            learned["outcome"]["resolution"]["score_delta"]["composition"],
            30.0,
        )
        self.assertTrue(learned["preference"]["recorded"])

    def test_visual_failure_memory_is_project_scoped(self):
        memory = VisualFailureMemory(self.root / "failures.json")
        memory.record(
            category="composition",
            problem="cards demais",
            fix="reduzir containers",
            project_id="Projeto A",
            artifact_kind="website",
        )

        same = memory.build_context(project_id="Projeto A", artifact_kind="website")
        other = memory.build_context(project_id="Projeto B", artifact_kind="website")

        self.assertIn("cards demais", same)
        self.assertNotIn("cards demais", other)

    def test_personal_benchmark_has_real_operator_work_cases(self):
        suite = PersonalBenchmarkSuite(self.hub)
        catalog = suite.catalog()

        self.assertGreaterEqual(len(catalog), 20)
        self.assertTrue(any(case["id"] == "visual_cafe" for case in catalog))
        self.assertTrue(any(case["id"] == "code_continue" for case in catalog))

    def test_evolution_differential_gate_allows_existing_debt_without_new_issue(self):
        baseline = [
            GateResult(
                command=["ruff"],
                returncode=1,
                stdout_tail="x.py:1:1 F401 imported but unused",
                stderr_tail="",
            )
        ]
        candidate_same = [
            GateResult(
                command=["ruff"],
                returncode=1,
                stdout_tail="x.py:1:1 F401 imported but unused",
                stderr_tail="",
            )
        ]
        candidate_worse = [
            GateResult(
                command=["ruff"],
                returncode=1,
                stdout_tail=(
                    "x.py:1:1 F401 imported but unused\n"
                    "y.py:4:1 E501 line too long"
                ),
                stderr_tail="",
            )
        ]

        self.assertEqual(
            EvolutionLab._differential_regressions(baseline, candidate_same),
            [],
        )
        self.assertTrue(
            EvolutionLab._differential_regressions(baseline, candidate_worse)
        )


class TournamentGateway:
    providers = [object()]

    def generate(self, request):
        payload = {
            "directions": [
                {
                    "id": "editorial",
                    "name": "Editorial",
                    "thesis": "fotografia como protagonista",
                    "composition": "assimetria com grande area fotografica",
                    "typography": "serif expressiva com sans funcional",
                    "palette_strategy": "tons quentes naturais",
                    "imagery": "fotografia documental de produto",
                    "interaction": "movimento sutil de revelacao",
                    "anti_template_move": "sem grade de cards na primeira dobra",
                },
                {
                    "id": "poster",
                    "name": "Poster",
                    "thesis": "marca como cartaz urbano",
                    "composition": "tipografia oversized e blocos verticais",
                    "typography": "grotesca condensada",
                    "palette_strategy": "alto contraste controlado",
                    "imagery": "recortes macro de cafe",
                    "interaction": "scroll tipografico",
                    "anti_template_move": "navegacao incorporada ao cartaz",
                },
                {
                    "id": "quiet",
                    "name": "Quiet Craft",
                    "thesis": "ritual e detalhe",
                    "composition": "espaco negativo e ritmo horizontal",
                    "typography": "serif discreta e microtipografia",
                    "palette_strategy": "neutros minerais",
                    "imagery": "natureza morta artesanal",
                    "interaction": "microinteracoes lentas",
                    "anti_template_move": "conteudo sem containers visiveis",
                },
            ]
        }
        return SimpleNamespace(
            content=json.dumps(payload),
            provider_name="fake",
            model_name="fake-reasoner",
        )


class TournamentTests(unittest.TestCase):
    def test_tournament_generates_distinct_directions(self):
        tournament = DesignTournament(gateway=TournamentGateway())
        brief = VisualBrief(
            objective="Site premium de cafeteria",
            artifact_kind=VisualArtifactKind.WEBSITE,
        )

        result = tournament.generate(brief)

        self.assertEqual(result["status"], "ready")
        self.assertEqual(len(result["directions"]), 3)
        names = {direction["name"] for direction in result["directions"]}
        self.assertEqual(len(names), 3)


if __name__ == "__main__":
    unittest.main()
