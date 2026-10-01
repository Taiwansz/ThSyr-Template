import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from engine.evaluation import CognitiveBenchmark, RetrievalCase


class StubRetriever:
    def __init__(self, title: str, content: str):
        self.title = title
        self.content = content

    def retrieve(self, query: str, limit: int = 5, min_score: float = 0.01):
        item = SimpleNamespace(item=SimpleNamespace(title=self.title, content=self.content))
        return [item][:limit]


class CognitiveBenchmarkTests(unittest.TestCase):
    def test_passes_when_expected_evidence_is_retrieved(self):
        benchmark = CognitiveBenchmark(
            retriever=StubRetriever("Hybrid Retrieval", "Busca lexical e semantica"),
            cases=(RetrievalCase("case", "busca", ("hybrid", "retrieval")),),
        )

        report = benchmark.run()

        self.assertEqual(report["pass_rate"], 1.0)
        self.assertTrue(report["cases"][0]["passed"])

    def test_rejects_forbidden_evidence(self):
        benchmark = CognitiveBenchmark(
            retriever=StubRetriever("Memory", "conteudo mock"),
            cases=(RetrievalCase("case", "memoria", ("memory",), ("mock",)),),
        )

        report = benchmark.run()

        self.assertEqual(report["pass_rate"], 0.0)
        self.assertTrue(report["cases"][0]["forbidden_hit"])

    def test_save_writes_machine_readable_report(self):
        benchmark = CognitiveBenchmark(
            retriever=StubRetriever("Memory", "conteudo"),
            cases=(),
        )
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "report.json"
            benchmark.save(target)
            payload = json.loads(target.read_text(encoding="utf-8"))

        self.assertEqual(payload["benchmark"], "cognitive-retrieval-v1")
        self.assertEqual(payload["total"], 0)


if __name__ == "__main__":
    unittest.main()
