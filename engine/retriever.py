"""
ThSyr Hybrid Memory Retriever (Fase 2 - Hybrid Retrieval)
Implementa recuperação híbrida combinando:
1. Lexical Score (Correspondência de termos e relevância textual)
2. Semantic / Synonyms Score (Expansão de vocabulário e sinônimos operacionais)
3. Knowledge Graph Proximity (Spreading activation e distância sináptica)
4. Recency Score (Decaimento temporal exponencial de memórias episódicas)
5. Importance Score (Peso intrínseco calibrado pelo operador/sistema)
6. Contextual & Entity Boost (Alinhamento com entidades e projetos em foco)
"""

import math
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import settings, setup_logger
from .memory_adaptation import MemoryAdaptationStore
from .memory_manager import MemoryManager
from .memory_models import MemoryItem, MemoryType
from .synaptic_engine import SynapticEngine
from .vector_store import LocalVectorStore

logger = setup_logger("retriever")

# Dicionario de expansao semantica e sinonimos frequentes no universo operacional do Operador
SEMANTIC_SYNONYMS: dict[str, set[str]] = {
    "servidor": {"host", "instancia", "maquina", "vm", "computacao", "hardware"},
    "infraestrutura": {"servidor", "rede", "hardware", "datacenter", "deploy", "cluster"},
    "estetica": {"design", "visual", "paleta", "interface", "layout"},
    "academico": {"estudos", "pesquisa", "paper", "artigo", "referencias", "notas"},
    "pesquisa": {"benchmark", "experimento", "artigo", "metricas", "avaliacao"},
    "branding": {"design", "identidade", "industrial_pop", "editorial", "paleta", "tipografia", "cores"},
    "banco": {"database", "postgres", "supabase", "rls", "tabelas", "sqlite"},
    "autenticacao": {"auth", "login", "jwt", "rls", "usuarios", "permissoes"},
    "api": {"endpoint", "rest", "graphql", "gateway", "chamada", "requisicao"},
    "testes": {"tdd", "unitario", "integracao", "cobertura", "validacao"},
}

STOPWORDS = {
    "a", "o", "as", "os", "de", "do", "da", "dos", "das", "em", "no", "na", "nos", "nas",
    "por", "para", "com", "sem", "sob", "sobre", "um", "uma", "uns", "umas", "e", "ou",
    "que", "se", "como", "qual", "quais", "quando", "onde", "quem", "por que", "porque",
    "eu", "meu", "minha", "meus", "minhas", "voce", "ele", "ela", "eles", "elas",
    "foi", "era", "tem", "ha", "escolhi", "definido", "definida", "esta", "estao"
}


@dataclass
class ScoredMemoryResult:
    item: MemoryItem
    score: float
    lexical_score: float = 0.0
    semantic_score: float = 0.0
    dense_score: float = 0.0
    graph_score: float = 0.0
    recency_score: float = 0.0
    importance_score: float = 0.0
    confidence_score: float = 0.0
    plasticity_score: float = 0.0
    integrity_penalty: float = 1.0
    context_boost: float = 0.0
    matched_terms: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.item.metadata.id,
            "title": self.item.title,
            "type": self.item.metadata.type,
            "score": round(self.score, 4),
            "breakdown": {
                "lexical": round(self.lexical_score, 4),
                "semantic": round(self.semantic_score, 4),
                "dense": round(self.dense_score, 4),
                "graph": round(self.graph_score, 4),
                "recency": round(self.recency_score, 4),
                "importance": round(self.importance_score, 4),
                "confidence": round(self.confidence_score, 4),
                "plasticity": round(self.plasticity_score, 4),
                "integrity_penalty": round(self.integrity_penalty, 4),
                "context_boost": round(self.context_boost, 4),
            },
            "matched_terms": self.matched_terms,
            "filepath": str(self.item.filepath) if self.item.filepath else None
        }


class MemoryRetriever:
    def __init__(
        self,
        memory_manager: MemoryManager | None = None,
        synaptic_engine: SynapticEngine | None = None,
        vector_store: LocalVectorStore | None = None,
        adaptation_store: MemoryAdaptationStore | None = None,
        brain_dir: Path | None = None
    ):
        self.brain_dir = brain_dir or settings.brain.brain_dir
        self.memory = memory_manager or MemoryManager(root=self.brain_dir)
        self.synaptic = synaptic_engine or SynapticEngine(brain_dir=self.brain_dir)
        self.vector_store = vector_store or LocalVectorStore()
        self.adaptation = adaptation_store or MemoryAdaptationStore()

    def _tokenize(self, text: str) -> list[str]:
        words = re.findall(r"\b[a-zA-Z0-9_\u00C0-\u00FF-]{2,}\b", text.lower())
        return [w for w in words if w not in STOPWORDS]

    def _expand_query_terms(self, query_tokens: list[str]) -> tuple[set[str], set[str]]:
        direct_tokens = set(query_tokens)
        synonyms: set[str] = set()

        for t in direct_tokens:
            for syn_key, syn_set in SEMANTIC_SYNONYMS.items():
                if t == syn_key or t in syn_set:
                    synonyms.update(syn_set)
                    synonyms.add(syn_key)

        return direct_tokens, synonyms - direct_tokens

    def _load_all_candidate_items(self) -> list[MemoryItem]:
        candidates: list[MemoryItem] = []

        # 1. Memorias semanticas
        candidates.extend(self.memory.get_semantic_items())

        # 2. Procedimentos
        candidates.extend(self.memory.get_procedural_items())

        # 3. Memorias episodicas recentes
        candidates.extend(self.memory.get_episodic_items(limit=30))

        # 4. Nós conceituais do cérebro (brain/nodes/)
        nodes_dir = self.brain_dir / "nodes"
        if nodes_dir.exists():
            for f in sorted(nodes_dir.glob("*.md")):
                try:
                    candidates.append(MemoryItem.from_markdown(
                        f.read_text(encoding="utf-8"),
                        filepath=f,
                        fallback_type=MemoryType.SEMANTIC.value
                    ))
                except Exception as e:
                    logger.debug(f"Erro ao ler node {f.name}: {e}")

        # 5. Working Memory
        candidates.append(self.memory.get_working_memory_item())

        return candidates

    def retrieve(
        self,
        query: str,
        limit: int = 10,
        min_score: float = 0.15,
        project_filter: str | None = None,
        entity_filter: str | None = None
    ) -> list[ScoredMemoryResult]:
        tokens = self._tokenize(query)
        if not tokens:
            return []

        direct_tokens, expanded_synonyms = self._expand_query_terms(tokens)

        # Disparar ativacao sinaptica para calcular proximidade no knowledge graph
        activation = self.synaptic.activate(query)
        graph_energy_map: dict[str, float] = {
            n["node"].lower(): n["energy"] for n in activation.get("top_activated", [])
        }

        candidates = self._load_all_candidate_items()
        now = datetime.now(timezone.utc)

        active_working_project = self.memory.working.project.lower() if self.memory.working.project else ""

        scored_results: list[ScoredMemoryResult] = []

        query_vec = self.vector_store.compute_embedding(query)

        for item in candidates:
            meta = item.metadata
            full_text = f"{item.title} {item.content} {' '.join(meta.tags)} {' '.join(meta.entities)} {' '.join(meta.projects)}".lower()
            text_tokens = set(self._tokenize(full_text))

            # 1. Lexical Score
            direct_matches = direct_tokens.intersection(text_tokens)
            # Match exato no título confere bônus
            title_lower = item.title.lower()
            title_hits = sum(1 for t in direct_tokens if t in title_lower)

            lexical_score = 0.0
            if direct_tokens:
                lexical_score = (len(direct_matches) / len(direct_tokens)) * 0.7 + (min(1.0, title_hits) * 0.3)

            # 2. Semantic / Synonyms Score
            syn_matches = expanded_synonyms.intersection(text_tokens)
            semantic_score = 0.0
            if expanded_synonyms:
                semantic_score = min(1.0, len(syn_matches) / max(1, len(expanded_synonyms) * 0.4))
            elif direct_matches:
                semantic_score = lexical_score * 0.8

            # 3. Dense Vector Similarity Score
            item_vec = self.vector_store.compute_embedding(f"{item.title} {item.content[:300]}")
            dense_score = max(0.0, self.vector_store.cosine_similarity(query_vec, item_vec))

            # 4. Knowledge Graph Score
            stem_id = (item.filepath.stem.lower() if item.filepath else meta.id.lower())
            title_key = item.title.lower().replace(" ", "_")
            graph_score = 0.0
            if stem_id in graph_energy_map:
                graph_score = min(1.0, graph_energy_map[stem_id] / 20.0)
            elif title_key in graph_energy_map:
                graph_score = min(1.0, graph_energy_map[title_key] / 20.0)
            elif direct_matches and any(m in graph_energy_map for m in direct_matches):
                matching_energy = max(graph_energy_map[m] for m in direct_matches if m in graph_energy_map)
                graph_score = min(0.8, matching_energy / 25.0)

            # 5. Recency / forgetting score. Verification or update refreshes a memory.
            recency_score = 0.5
            try:
                freshness_raw = meta.last_verified or meta.updated_at or meta.created_at
                freshness_dt = datetime.fromisoformat(freshness_raw.replace("Z", "+00:00"))
                days_diff = max(0.0, (now - freshness_dt).total_seconds() / 86400.0)
                recency_score = math.exp(-0.015 * days_diff)
            except Exception:
                recency_score = 0.5

            # 6. Importance and confidence are independent signals.
            importance_score = max(0.0, min(1.0, float(meta.importance)))
            confidence_score = max(0.0, min(1.0, float(meta.confidence)))

            # Superseded or contradicted memories remain searchable for provenance,
            # but they should not outrank current canonical knowledge.
            integrity_penalty = 1.0
            if meta.superseded_by:
                integrity_penalty *= 0.25
            if meta.contradicted_by:
                integrity_penalty *= 0.45

            # 7. Adaptive plasticity: frequently useful memories receive a small boost.
            plasticity_score = self.adaptation.plasticity_score(meta.id)

            # 8. Context & Entity Boost
            context_boost = 0.0
            if entity_filter and any(entity_filter.lower() in e.lower() for e in meta.entities):
                context_boost += 0.4
            if project_filter and any(project_filter.lower() in p.lower() for p in meta.projects):
                context_boost += 0.4
            if active_working_project and any(active_working_project in p.lower() for p in meta.projects):
                context_boost += 0.2

            # Exige relevância textual ou semântica direta para qualificar como resultado
            if lexical_score == 0.0 and semantic_score == 0.0 and dense_score < 0.25:
                continue

            # Ponderação híbrida V2:
            # relevancia textual/semantica continua dominante, mas conhecimento
            # confiavel e vigente supera memorias antigas, contraditas ou substituidas.
            base_score = (
                0.21 * lexical_score +
                0.17 * semantic_score +
                0.14 * dense_score +
                0.11 * graph_score +
                0.11 * importance_score +
                0.08 * confidence_score +
                0.05 * recency_score +
                0.06 * plasticity_score +
                0.07 * min(1.0, context_boost)
            )
            total_score = base_score * integrity_penalty

            matched_all = list(direct_matches) + list(syn_matches)

            if total_score >= min_score:
                scored_results.append(ScoredMemoryResult(
                    item=item,
                    score=total_score,
                    lexical_score=lexical_score,
                    semantic_score=semantic_score,
                    dense_score=dense_score,
                    graph_score=graph_score,
                    recency_score=recency_score,
                    importance_score=importance_score,
                    confidence_score=confidence_score,
                    plasticity_score=plasticity_score,
                    integrity_penalty=integrity_penalty,
                    context_boost=context_boost,
                    matched_terms=matched_all
                ))

        scored_results.sort(key=lambda x: x.score, reverse=True)

        # Deduplicação por título / ID
        seen_titles = set()
        deduped = []
        for r in scored_results:
            key = r.item.title.lower().strip()
            if key not in seen_titles:
                seen_titles.add(key)
                deduped.append(r)
            if len(deduped) >= limit:
                break

        for result in deduped:
            self.adaptation.record_access(result.item.metadata.id)

        return deduped

    def record_feedback(self, memory_ids: list[str], helpful: bool) -> None:
        """Reinforce or weaken memories after an explicit outcome signal."""
        for memory_id in memory_ids:
            self.adaptation.record_feedback(memory_id, helpful=helpful)

    def retrieve_rrf(self, query: str, limit: int = 10, k: int = 60) -> list[ScoredMemoryResult]:
        """
        Reciprocal Rank Fusion (RRF):
        RRF_score = 1.0 / (k + rank_lexical) + 1.0 / (k + rank_dense) + 1.0 / (k + rank_graph)
        """
        results = self.retrieve(query, limit=limit * 2, min_score=0.01)
        if not results:
            return []

        by_lex = sorted(results, key=lambda x: x.lexical_score, reverse=True)
        lex_rank = {r.item.metadata.id: rank + 1 for rank, r in enumerate(by_lex)}

        by_dense = sorted(results, key=lambda x: x.dense_score, reverse=True)
        dense_rank = {r.item.metadata.id: rank + 1 for rank, r in enumerate(by_dense)}

        by_graph = sorted(results, key=lambda x: x.graph_score, reverse=True)
        graph_rank = {r.item.metadata.id: rank + 1 for rank, r in enumerate(by_graph)}

        for r in results:
            mid = r.item.metadata.id
            r1 = lex_rank.get(mid, len(results) + 1)
            r2 = dense_rank.get(mid, len(results) + 1)
            r3 = graph_rank.get(mid, len(results) + 1)
            r.score = (1.0 / (k + r1)) + (1.0 / (k + r2)) + (1.0 / (k + r3))

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]

    def get_compact_context_pack(
        self,
        query: str,
        max_items: int = 6,
        results: list[ScoredMemoryResult] | None = None,
    ) -> str:
        """Format a compact context pack, reusing retrieval results when provided."""
        selected = list(results[:max_items]) if results is not None else self.retrieve(query, limit=max_items)
        if not selected:
            return ""

        blocks = ["# CONTEXTO NEURAL RECUPERADO (HYBRID RETRIEVAL)"]
        for r in selected:
            m = r.item.metadata
            blocks.append(
                f"## [[{r.item.title}]] (Relevância: {round(r.score, 2)} | Tipo: {m.type.upper()})\n"
                f"- Metadados: ID={m.id} | Importância={m.importance} | Termos={', '.join(r.matched_terms[:4])}\n"
                f"{r.item.content.strip()[:800]}\n"
            )
        return "\n".join(blocks)
