"""
ThSyr Desktop Graph Service
Fornece snapshot normalizado e deterministico do grafo neural real do ThSyr
para visualizacao 3D no Desktop Control Center (Fase 1 / 04_NEURAL_GRAPH_INTEGRATION.md).
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Optional

from ..config import settings, setup_logger
from ..knowledge_ingestor import extract_ecosystem_graph
from .protocol import GraphEdgeDto, GraphNodeDto, GraphSnapshotDto

logger = setup_logger("desktop_graph_service")

# Paleta e layout de lobos canonicos para posicionamento 3D
LOBE_LAYOUT: dict[str, tuple[tuple[float, float, float], str]] = {
    "regra": ((0, 0, 0), "#ffb52e"),
    "tech": ((0, 0, 0), "#ffd66b"),
    "sessao": ((0, 0, 0), "#e58b20"),
    "design": ((0, 0, 0), "#ffc04d"),
    "limbico": ((0, 0, 0), "#ff8b1f"),
    "cortex": ((0, 0, 0), "#ffe29a"),
    "analitica": ((0, 0, 0), "#f6a928"),
    "projeto": ((0, 0, 0), "#ffca57"),
    "conceito": ((0, 0, 0), "#d88a1c"),
    "operador": ((0, 0, 0), "#fff0bd"),
}


class DesktopGraphService:
    def __init__(
        self,
        brain_dir: Optional[Path] = None,
        ecosystem_path: Optional[Path] = None,
    ):
        self.brain_dir = brain_dir or settings.brain.brain_dir
        self.ecosystem_path = ecosystem_path or (self.brain_dir / "knowledge_ecosystem.json")
        self._cached_snapshot: Optional[GraphSnapshotDto] = None
        self._node_id_lookup: dict[str, str] = {}  # lowercase or label -> canonical node_id

    def _compute_coordinates(self, raw_nodes: list[dict[str, Any]]) -> list[GraphNodeDto]:
        total = max(len(raw_nodes), 1)
        node_dtos: list[GraphNodeDto] = []

        for index, raw in enumerate(raw_nodes):
            group = str(raw.get("group", "conceito"))
            _, color = LOBE_LAYOUT.get(group, LOBE_LAYOUT["conceito"])
            workspace = str(raw.get("workspace", "brain"))
            depth = int(raw.get("depth", 0))
            kind = str(raw.get("kind", "concept"))

            fraction = (index + 0.5) / total
            longitude = index * 2.3999632297
            # Inclinacao deterministica com protecao contra math domain error
            clamped_arg = max(-1.0, min(1.0, 1.0 - 2.0 * fraction))
            latitude = math.acos(clamped_arg)

            direction = (
                math.sin(latitude) * math.cos(longitude),
                math.cos(latitude),
                math.sin(latitude) * math.sin(longitude),
            )

            if kind == "project":
                radius = 1.25 + (index % 7) * 0.12
            elif kind == "directory":
                radius = 2.15 + min(depth, 4) * 0.48
            elif workspace == "brain":
                radius = 3.05 + min(depth, 4) * 0.4
            else:
                radius = 4.15 + min(depth, 4) * 0.48
            radius += ((index % 5) - 2) * 0.06

            degree = int(raw.get("degree", 0))
            is_hub = bool(raw.get("is_hub", degree >= 10))

            node_dto = GraphNodeDto(
                id=str(raw.get("id", f"node_{index}")),
                label=str(raw.get("label", raw.get("id", ""))),
                group=group,
                lobe=group,
                kind=kind,
                degree=degree,
                is_hub=is_hub,
                workspace=workspace,
                path=str(raw.get("path", "")),
                x=round(direction[0] * radius, 4),
                y=round(direction[1] * radius, 4),
                z=round(direction[2] * radius, 4),
                color=color,
            )
            node_dtos.append(node_dto)

        return node_dtos

    def build_snapshot(self, force_refresh: bool = False) -> GraphSnapshotDto:
        """Carrega e normaliza os nos e edges reais do ecossistema de conhecimento."""
        if self._cached_snapshot is not None and not force_refresh:
            return self._cached_snapshot

        raw_graph: dict[str, Any] = {}
        try:
            raw_graph = extract_ecosystem_graph(self.brain_dir, self.ecosystem_path)
        except Exception as e:
            logger.warning(f"Erro ao extrair ecossistema em {self.ecosystem_path}: {e}")

        raw_nodes = raw_graph.get("nodes", [])
        raw_links = raw_graph.get("links", raw_graph.get("edges", []))

        # Calcular graus reais caso ausentes
        degrees: dict[str, int] = {}
        for link in raw_links:
            src = str(link.get("source", ""))
            tgt = str(link.get("target", ""))
            degrees[src] = degrees.get(src, 0) + 1
            degrees[tgt] = degrees.get(tgt, 0) + 1

        for n in raw_nodes:
            nid = str(n.get("id", ""))
            if "degree" not in n:
                n["degree"] = degrees.get(nid, 0)

        # Gerar nós posicionados em 3D
        nodes_dto = self._compute_coordinates(raw_nodes)

        # Mapear edges
        edges_dto: list[GraphEdgeDto] = []
        for link_item in raw_links:
            edges_dto.append(
                GraphEdgeDto(
                    source=str(link_item.get("source", "")),
                    target=str(link_item.get("target", "")),
                    weight=float(link_item.get("weight", 1.0)),
                    kind=str(link_item.get("kind", "semantic")),
                )
            )

        snapshot = GraphSnapshotDto(
            version=1,
            total_nodes=len(nodes_dto),
            total_edges=len(edges_dto),
            nodes=nodes_dto,
            edges=edges_dto,
        )

        # Atualizar lookup index
        self._node_id_lookup.clear()
        for n in nodes_dto:
            self._node_id_lookup[n.id.lower()] = n.id
            if n.label:
                self._node_id_lookup[n.label.lower()] = n.id

        self._cached_snapshot = snapshot
        logger.info(f"GraphSnapshot gerado com sucesso: {snapshot.total_nodes} nos, {snapshot.total_edges} conexoes.")
        return snapshot

    def match_pulse_nodes(self, pulse_data: dict[str, Any]) -> dict[str, Any]:
        """
        Mapeia os dados brutos de um NeuralPulse para os IDs canônicos existentes no grafo.
        Retorna IDs correspondentes e IDs nao encontrados para conformidade com a auditoria visual.
        """
        snapshot = self.build_snapshot()
        all_ids = {n.id for n in snapshot.nodes}

        seeds = pulse_data.get("seeds", [])
        top_activated = pulse_data.get("top_activated", [])
        constraints = pulse_data.get("constraints", [])
        retrieved = pulse_data.get("retrieved", [])

        matched_seeds: list[str] = []
        unmatched_seeds: list[str] = []
        for s in seeds:
            s_str = str(s)
            canonical = self._node_id_lookup.get(s_str.lower()) or (s_str if s_str in all_ids else None)
            if canonical:
                matched_seeds.append(canonical)
            else:
                unmatched_seeds.append(s_str)

        matched_activated: list[dict[str, Any]] = []
        unmatched_activated: list[str] = []
        for item in top_activated:
            raw_id = str(item.get("id", item.get("node", "")))
            canonical = self._node_id_lookup.get(raw_id.lower()) or (raw_id if raw_id in all_ids else None)
            if canonical:
                matched_activated.append({
                    "id": canonical,
                    "energy": float(item.get("energy", 1.0)),
                    "lobe": str(item.get("lobe", "cortex")),
                })
            else:
                unmatched_activated.append(raw_id)

        return {
            "pulse_id": pulse_data.get("id"),
            "matched_seeds": matched_seeds,
            "unmatched_seeds": unmatched_seeds,
            "matched_activated": matched_activated,
            "unmatched_activated": unmatched_activated,
            "constraints": constraints,
            "retrieved_count": len(retrieved),
        }
