"""Benchmark cognitivo deterministico para medir recuperação do ThSyr.

O benchmark nao chama modelos externos. Ele mede a camada que o runtime
controla diretamente: se consultas conhecidas recuperam memorias esperadas,
respeitam filtros e evitam evidencias explicitamente proibidas.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .retriever import MemoryRetriever


@dataclass(frozen=True)
class RetrievalCase:
    id: str
    query: str
    expected_terms: tuple[str, ...]
    forbidden_terms: tuple[str, ...] = ()
    limit: int = 5


@dataclass
class CaseResult:
    case_id: str
    passed: bool
    hit: bool
    forbidden_hit: bool
    top_titles: list[str]
    matched_terms: list[str]


DEFAULT_CASES: tuple[RetrievalCase, ...] = (
    RetrievalCase(
        id="engineering-hybrid-retrieval",
        query="como funciona a busca híbrida do ThSyr",
        expected_terms=("hybrid", "retrieval", "memoria"),
    ),
    RetrievalCase(
        id="toklang-context-compilation",
        query="compilação TokLang e orçamento de contexto",
        expected_terms=("toklang", "compiler", "compress"),
    ),
    RetrievalCase(
        id="visual-neural-canvas",
        query="grafo neural 3D e canvas holográfico",
        expected_terms=("neural", "canvas", "3d"),
    ),
    RetrievalCase(
        id="real-data-constraint",
        query="nós reais sinapses reais sem dados inventados",
        expected_terms=("real", "knowledge", "neural"),
        forbidden_terms=("mock", "fabricated"),
    ),
)


class CognitiveBenchmark:
    """Executa casos de recuperação e produz resultados auditaveis."""

    def __init__(
        self,
        retriever: MemoryRetriever | None = None,
        cases: tuple[RetrievalCase, ...] = DEFAULT_CASES,
    ) -> None:
        self.retriever = retriever or MemoryRetriever()
        self.cases = cases

    @staticmethod
    def _normalise(text: str) -> str:
        return " ".join(text.lower().replace("_", " ").split())

    def run(self) -> dict[str, Any]:
        results: list[CaseResult] = []
        for case in self.cases:
            retrieved = self.retriever.retrieve(case.query, limit=case.limit, min_score=0.01)
            corpus = " ".join(
                self._normalise(f"{item.item.title} {item.item.content}")
                for item in retrieved
            )
            expected = [
                term for term in case.expected_terms
                if self._normalise(term) in corpus
            ]
            forbidden = [
                term for term in case.forbidden_terms
                if self._normalise(term) in corpus
            ]
            hit = bool(expected)
            forbidden_hit = bool(forbidden)
            results.append(
                CaseResult(
                    case_id=case.id,
                    passed=hit and not forbidden_hit,
                    hit=hit,
                    forbidden_hit=forbidden_hit,
                    top_titles=[item.item.title for item in retrieved],
                    matched_terms=expected,
                )
            )

        passed = sum(result.passed for result in results)
        total = len(results)
        return {
            "benchmark": "cognitive-retrieval-v1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "passed": passed,
            "total": total,
            "pass_rate": round(passed / total, 4) if total else 0.0,
            "cases": [asdict(result) for result in results],
        }

    def save(self, path: Path) -> dict[str, Any]:
        report = self.run()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return report
