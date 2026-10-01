"""
ThSyr Auto-Evolution Engine & Cognitive Optimization Core (Fase 11)
Implementa a capacidade de auto-incremento e mutacao arquitetural autonoma do ThSyr:
- EntropyAuditor: Analise de conectividade, densidade sinaptica e deteccao de nos orfaos
- InferenceAuditor: Auditoria de eficiencia de modelos, tokens consumidos e latencia
- AutoEvolutionEngine: Geracao de planos de mutacao, validacao pre-frontal e livro-razao evolutivo (state/evolution_ledger.json)
"""

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import settings, setup_logger
from .evolution_lab import EvolutionCandidate, EvolutionLab
from .graph_indexer import reindex_and_audit
from .prefrontal_cortex import PreFrontalCortex

logger = setup_logger("auto_evolution")


@dataclass
class EvolutionProposal:
    id: str
    target: str
    description: str
    impact: str
    prefrontal_approved: bool
    status: str = "PENDING"  # PENDING, APPLIED, REJECTED


@dataclass
class EvolutionReport:
    generation: int
    timestamp: str
    entropy_index: float
    total_nodes: int
    total_edges: int
    orphaned_nodes: list[str]
    inference_efficiency: dict[str, Any]
    proposals: list[EvolutionProposal] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "generation": self.generation,
            "timestamp": self.timestamp,
            "entropy_index": round(self.entropy_index, 4),
            "total_nodes": self.total_nodes,
            "total_edges": self.total_edges,
            "orphaned_count": len(self.orphaned_nodes),
            "orphaned_nodes": self.orphaned_nodes[:10],
            "inference_efficiency": self.inference_efficiency,
            "proposals": [asdict(p) for p in self.proposals]
        }


class EntropyAuditor:
    """Audita a entropia e densidade topologica do grafo neural."""

    def __init__(self, brain_dir: Path | None = None):
        self.brain_dir = brain_dir or settings.brain.brain_dir

    def audit(self) -> dict[str, Any]:
        kg_path = self.brain_dir / "knowledge_graph.json"
        if not kg_path.exists():
            return {
                "total_nodes": 0,
                "total_edges": 0,
                "entropy_index": 0.0,
                "orphaned_nodes": [],
                "density": 0.0
            }

        try:
            data = json.loads(kg_path.read_text(encoding="utf-8"))
            nodes = data.get("nodes", [])
            edges = data.get("edges", [])

            node_ids = set()
            for n in nodes:
                if isinstance(n, dict):
                    node_ids.add(n.get("id", ""))
                elif isinstance(n, str):
                    node_ids.add(n)

            connected_nodes = set()
            for e in edges:
                if isinstance(e, dict):
                    connected_nodes.add(e.get("source", ""))
                    connected_nodes.add(e.get("target", ""))
                elif isinstance(e, (list, tuple)) and len(e) >= 2:
                    connected_nodes.add(e[0])
                    connected_nodes.add(e[1])

            orphans = sorted(list(node_ids - connected_nodes))
            total_n = len(node_ids) or data.get("total_nodes", 0)
            total_e = len(edges) or data.get("total_edges", 0)

            entropy = (len(orphans) / max(1, total_n)) if total_n > 0 else 0.0
            density = (total_e / max(1, total_n)) if total_n > 0 else 0.0

            return {
                "total_nodes": total_n,
                "total_edges": total_e,
                "entropy_index": entropy,
                "orphaned_nodes": orphans,
                "density": density
            }
        except Exception as e:
            logger.error(f"Erro ao auditar entropia: {e}")
            return {
                "total_nodes": 0,
                "total_edges": 0,
                "entropy_index": 0.0,
                "orphaned_nodes": [],
                "density": 0.0,
                "error": str(e)
            }


class InferenceAuditor:
    """Audita o consumo de tokens e a latencia do gateway de modelos."""

    def __init__(self, state_dir: Path | None = None):
        self.state_dir = state_dir or settings.brain.state_dir
        self.telemetry_path = self.state_dir / "model_telemetry.json"

    def audit(self) -> dict[str, Any]:
        if not self.telemetry_path.exists():
            return {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "avg_latency_ms": 0.0,
                "efficiency_rating": "OPTIMAL"
            }

        try:
            data = json.loads(self.telemetry_path.read_text(encoding="utf-8"))
            reqs = data.get("total_requests", 0)
            tokens = data.get("total_tokens", 0)
            cost = data.get("total_cost_usd", 0.0)
            lat = data.get("total_latency_ms", 0.0)

            avg_lat = round(lat / max(1, reqs), 2)
            cost_per_1k = round((cost / max(1, tokens)) * 1000, 4) if tokens > 0 else 0.0

            rating = "OPTIMAL"
            if avg_lat > 2500.0:
                rating = "DEGRADED_LATENCY"
            elif cost > 50.0:
                rating = "BUDGET_PRESSURE"

            return {
                "total_requests": reqs,
                "total_tokens": tokens,
                "total_cost_usd": round(cost, 4),
                "avg_latency_ms": avg_lat,
                "cost_per_1k_tokens": cost_per_1k,
                "efficiency_rating": rating
            }
        except Exception as e:
            logger.error(f"Erro ao auditar telemetria de inferencia: {e}")
            return {"error": str(e), "efficiency_rating": "UNKNOWN"}


class AutoEvolutionEngine:
    """
    Motor Central de Auto-Evolucao e Otimizacao Cognitiva.
    Gera planos de melhoria, valida contra o Pre-Frontal e registra o historico evolutivo.
    """

    def __init__(
        self,
        brain_dir: Path | None = None,
        state_dir: Path | None = None,
        prefrontal: PreFrontalCortex | None = None,
        evolution_lab: EvolutionLab | None = None,
    ):
        self.brain_dir = brain_dir or settings.brain.brain_dir
        self.state_dir = state_dir or settings.brain.state_dir
        self.ledger_file = self.state_dir / "evolution_ledger.json"
        self.entropy_auditor = EntropyAuditor(self.brain_dir)
        self.inference_auditor = InferenceAuditor(self.state_dir)
        self.prefrontal = prefrontal or PreFrontalCortex()
        self.evolution_lab = evolution_lab or EvolutionLab(project_root=settings.project_root)

    def _load_ledger(self) -> list[dict[str, Any]]:
        if not self.ledger_file.exists():
            return []
        try:
            return json.loads(self.ledger_file.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _save_ledger(self, ledger: list[dict[str, Any]]) -> None:
        self.ledger_file.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.ledger_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
        tmp.replace(self.ledger_file)

    def diagnose(self) -> EvolutionReport:
        """Gera um relatorio clinico de maturidade e entropia do sistema."""
        ledger = self._load_ledger()
        generation = len(ledger) + 1

        ent = self.entropy_auditor.audit()
        inf = self.inference_auditor.audit()

        proposals: list[EvolutionProposal] = []

        # 1. Proposta baseada em orfaos no grafo
        if ent.get("orphaned_nodes"):
            prop_text = f"Otimizar topologia sinaptica: reconectar {len(ent['orphaned_nodes'])} nos isolados no cortex."
            audit_res = self.prefrontal.audit(prop_text)
            proposals.append(EvolutionProposal(
                id=f"evo_synapse_{generation:03d}",
                target="neural_topology",
                description=prop_text,
                impact="Reducao de entropia cognitiva e ampliacao de recall associativo",
                prefrontal_approved=bool(audit_res.get("passed", False))
            ))

        # 2. Proposta baseada em densidade sinaptica
        if ent.get("density", 0.0) < 3.0:
            prop_text = "Reindexar e adensar sinapses bidirecionais entre nodulos vitais dos 5 lobos."
            audit_res = self.prefrontal.audit(prop_text)
            proposals.append(EvolutionProposal(
                id=f"evo_density_{generation:03d}",
                target="knowledge_graph",
                description=prop_text,
                impact="Elevacao da taxa de propagacao de energia sinaptica",
                prefrontal_approved=bool(audit_res.get("passed", False))
            ))

        # 3. Proposta baseada em telemetria de modelos
        if inf.get("efficiency_rating") != "OPTIMAL":
            prop_text = f"Ajustar roteamento de modelo e politica de fallback: classificacao {inf.get('efficiency_rating')}."
            audit_res = self.prefrontal.audit(prop_text)
            proposals.append(EvolutionProposal(
                id=f"evo_model_{generation:03d}",
                target="model_gateway",
                description=prop_text,
                impact="Otimizacao de latencia e orcamento de tokens",
                prefrontal_approved=bool(audit_res.get("passed", False))
            ))

        return EvolutionReport(
            generation=generation,
            timestamp=datetime.now(timezone.utc).isoformat(),
            entropy_index=ent.get("entropy_index", 0.0),
            total_nodes=ent.get("total_nodes", 0),
            total_edges=ent.get("total_edges", 0),
            orphaned_nodes=ent.get("orphaned_nodes", []),
            inference_efficiency=inf,
            proposals=proposals
        )

    def _candidate_context(self, proposal: EvolutionProposal) -> dict[str, str]:
        safe_targets: dict[str, tuple[str, ...]] = {
            "neural_topology": (
                "engine/synaptic_engine.py",
                "engine/graph_indexer.py",
            ),
            "knowledge_graph": (
                "engine/graph_indexer.py",
                "engine/memory_consolidator.py",
            ),
            "model_gateway": (
                "engine/models/router.py",
                "engine/models/gateway.py",
            ),
        }
        files: dict[str, str] = {}
        for relative in safe_targets.get(proposal.target, ()):
            path = settings.project_root / relative
            if not path.is_file():
                continue
            try:
                files[relative] = path.read_text(encoding="utf-8")
            except OSError:
                continue
        return files

    def _autonomous_candidate(
        self,
        diag: EvolutionReport,
    ) -> tuple[EvolutionCandidate | None, EvolutionProposal | None]:
        if os.getenv("THSYR_EVOLUTION_AUTOCODE", "").lower() not in {"1", "true", "yes"}:
            return None, None
        proposal = next(
            (item for item in diag.proposals if item.prefrontal_approved),
            None,
        )
        if proposal is None:
            return None, None
        context = self._candidate_context(proposal)
        if not context:
            return None, proposal
        candidate = self.evolution_lab.generate_candidate(
            objective=proposal.description,
            file_context=context,
        )
        return candidate, proposal

    def trigger_evolution(
        self,
        auto_apply: bool = True,
        candidate_patch: str | None = None,
        candidate_objective: str = "Improve ThSyr without regressions",
    ) -> dict[str, Any]:
        """Run governed evolution and optionally evaluate a candidate patch.

        A candidate patch is never applied to the active workspace. It is tested
        inside a disposable Git worktree by EvolutionLab.
        """
        diag = self.diagnose()
        applied_actions: list[str] = []
        lab_verdict: dict[str, Any] | None = None

        candidate: EvolutionCandidate | None = None
        proposal: EvolutionProposal | None = None
        if candidate_patch:
            candidate = EvolutionCandidate(
                id=f"evo_gen_{diag.generation:03d}",
                objective=candidate_objective,
                patch_text=candidate_patch,
                source="trigger_evolution",
            )
        else:
            candidate, proposal = self._autonomous_candidate(diag)

        if candidate is not None:
            verdict = self.evolution_lab.evaluate_candidate(candidate)
            lab_verdict = verdict.to_dict()
            lab_verdict["candidate_source"] = candidate.source
            lab_verdict["proposal_id"] = proposal.id if proposal else None
            if verdict.accepted:
                applied_actions.append("Evolution Lab candidate accepted by all gates.")
                promoted, promotion_message = self.evolution_lab.promote_candidate(candidate)
                lab_verdict["promoted"] = promoted
                lab_verdict["promotion_message"] = promotion_message
                if promoted:
                    applied_actions.append(promotion_message)
            else:
                applied_actions.append(f"Evolution Lab candidate rejected: {verdict.reason}")
        elif os.getenv("THSYR_EVOLUTION_AUTOCODE", "").lower() in {"1", "true", "yes"}:
            applied_actions.append(
                "Evolution autocoding enabled, but no safe approved candidate was generated."
            )

        if auto_apply:
            try:
                reindex_res = reindex_and_audit(brain_dir=self.brain_dir)
                applied_actions.append(
                    f"Reindexacao topologica executada: {reindex_res.get('total_nodes')} nos, "
                    f"{reindex_res.get('total_edges')} sinapses."
                )
            except Exception as e:
                applied_actions.append(f"Reindexacao falhou: {e}")

        ledger = self._load_ledger()
        entry = {
            "generation": diag.generation,
            "timestamp": diag.timestamp,
            "entropy_index": round(diag.entropy_index, 4),
            "total_nodes": diag.total_nodes,
            "total_edges": diag.total_edges,
            "actions_applied": applied_actions,
            "proposals_evaluated": len(diag.proposals),
            "evolution_lab": lab_verdict,
        }
        ledger.append(entry)
        self._save_ledger(ledger)

        logger.info(
            "Salto evolutivo registrado: Geracao %s (Entropia=%.4f)",
            diag.generation,
            diag.entropy_index,
        )
        return {
            "generation": diag.generation,
            "status": "EVOLVED",
            "actions": applied_actions,
            "entropy_index": diag.entropy_index,
            "evolution_lab": lab_verdict,
        }

    def render_report(self) -> str:
        """Renderiza relatorio textual para CLI."""
        diag = self.diagnose()
        ledger = self._load_ledger()
        inf = diag.inference_efficiency

        lines = [
            "==================================================",
            "      THSYR // COGNITIVE AUTO-EVOLUTION ENGINE    ",
            "==================================================",
            f"Geracao Atual:       Gen {diag.generation}",
            f"Indice de Entropia:  {diag.entropy_index:.4f} (Ideal: < 0.15)",
            f"Total de Nos / Arestas: {diag.total_nodes} nos | {diag.total_edges} sinapses",
            f"Nos Orfaos:          {len(diag.orphaned_nodes)}",
            "--------------------------------------------------",
            "Eficiencia de Inferência:",
            f"  • Total de Requisicoes: {inf.get('total_requests', 0)}",
            f"  • Tokens Consumidos:    {inf.get('total_tokens', 0)}",
            f"  • Custo Estimado:       USD {inf.get('total_cost_usd', 0.0)}",
            f"  • Latencia Media:       {inf.get('avg_latency_ms', 0.0)} ms",
            f"  • Classificacao:        {inf.get('efficiency_rating', 'N/D')}",
            "--------------------------------------------------",
            "Propostas de Mutacao Pre-Frontal:"
        ]

        if not diag.proposals:
            lines.append("  Nenhuma mutacao necessaria no ciclo atual. Arquitetura estavel.")
        else:
            for p in diag.proposals:
                app = "APROVADO" if p.prefrontal_approved else "REJEITADO"
                lines.append(f"  [{p.id}] ({p.target}) -> {app}")
                lines.append(f"     Descricao: {p.description}")
                lines.append(f"     Impacto:   {p.impact}")

        lines.append("--------------------------------------------------")
        lines.append(f"Historico do Ledger: {len(ledger)} geracoes registradas")
        lines.append("==================================================")
        return "\n".join(lines)
