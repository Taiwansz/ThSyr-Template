"""
ThSyr Synaptic Engine - Motor de Ativacao Sinaptica Propagada e Plasticidade Hebbiana
Implementa neurocomputacao real sobre o grafo de conhecimento do ThSyr.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import settings, setup_logger

logger = setup_logger("synaptic_engine")


class SynapticEngine:
    def __init__(self, brain_dir: Path | None = None, graph_file: Path | None = None):
        self.brain_dir = brain_dir or settings.brain.brain_dir
        if graph_file:
            self.graph_file = graph_file
        elif settings.env == "test":
            self.graph_file = settings.brain.state_dir / "knowledge_graph.json"
        else:
            self.graph_file = self.brain_dir / "knowledge_graph.json"
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: dict[tuple[str, str], float] = {}
        self.load_or_build_graph()

    def load_or_build_graph(self):
        # 1. Mapear arquivos Markdown
        for md_file in self.brain_dir.rglob("*.md"):
            node_id = md_file.stem
            content = md_file.read_text(encoding="utf-8")
            try:
                rel_path = str(md_file.relative_to(settings.project_root))
            except ValueError:
                rel_path = str(md_file)
            self.nodes[node_id] = {
                "id": node_id,
                "path": rel_path,
                "content": content,
                "keywords": self._extract_keywords(node_id, content),
                "lobe": self._detect_lobe(md_file, content)
            }

        # 2. Carregar ou inicializar pesos sinapticos
        persisted_edges = {}
        source_file = self.graph_file if self.graph_file.exists() else (self.brain_dir / "knowledge_graph.json")
        if source_file.exists():
            try:
                data = json.loads(source_file.read_text(encoding="utf-8"))
                for e in data.get("edges", []):
                    persisted_edges[(e["source"], e["target"])] = float(e.get("weight", 1.0))
            except Exception:
                persisted_edges = {}

        # 3. Mapear sinapses a partir dos wikilinks
        for node_id, data in self.nodes.items():
            links = re.findall(r"\[\[(.*?)\]\]", data["content"])
            for target in links:
                clean_target = target.split("|")[0].strip()
                if clean_target in self.nodes:
                    pair = (node_id, clean_target)
                    initial_weight = persisted_edges.get(pair, 1.0)
                    self.edges[pair] = initial_weight

    def _extract_keywords(self, node_id: str, content: str) -> set[str]:
        words = set(re.findall(r"\b[a-zA-Z0-9_-]{3,}\b", node_id.lower()))
        # Adicionar termos relevantes dos primeiros paragrafos
        lines = content.splitlines()[:15]
        for line in lines:
            tokens = re.findall(r"\b[a-zA-Z0-9_-]{4,}\b", line.lower())
            words.update(tokens)
        return words

    def _detect_lobe(self, path: Path, content: str) -> str:
        p_str = str(path).lower()
        if "frontal" in p_str or "lei" in content or "anti_sicofancia" in p_str:
            return "frontal"
        if "parietal" in p_str or "stack" in p_str or "engenharia" in content:
            return "parietal"
        if "temporal" in p_str or "episodic" in p_str or "sessao" in p_str:
            return "temporal"
        if "occipital" in p_str or "design" in p_str or "visual" in content:
            return "occipital"
        if "limbico" in p_str or "valores" in p_str or "restricoes" in p_str:
            return "limbico"
        return "cortex"

    def activate(self, query: str, max_hops: int = 2, decay: float = 0.65) -> dict[str, Any]:
        """
        Executa ativacao propagada a partir da mensagem do operador.
        Retorna os nós energizados, restricoes ativadas e o subgrafo contextual.
        """
        query_tokens = set(re.findall(r"\b[a-zA-Z0-9_-]{3,}\b", query.lower()))
        energy: dict[str, float] = {}

        # 1. Impulso inicial (Seed Nodes)
        seeds = []
        for nid, node in self.nodes.items():
            matches = query_tokens.intersection(node["keywords"])
            if matches:
                score = len(matches) * 1.5
                if nid.lower() in query.lower():
                    score += 5.0
                energy[nid] = score
                seeds.append(nid)

        if not seeds:
            # Se nenhuma correspondencia exata, ativar Cortex Central como fallback
            energy["Cortex_Central"] = 1.0
            seeds.append("Cortex_Central")

        # 2. Propagacao Sinaptica (Spreading Activation)
        for hop in range(max_hops):
            current_active = list(energy.keys())
            for src in current_active:
                src_energy = energy[src]
                if src_energy <= 0.1:
                    continue

                # Propagar atraves das conexoes de saida e entrada
                for (s, t), weight in self.edges.items():
                    target = None
                    if s == src:
                        target = t
                    elif t == src:
                        target = s

                    if target and target in self.nodes:
                        transfer = src_energy * (weight / (weight + 1.0)) * decay
                        energy[target] = energy.get(target, 0.0) + transfer

        # 3. Ordenar por nivel de ativacao
        sorted_nodes = sorted(energy.items(), key=lambda x: x[1], reverse=True)
        top_nodes = sorted_nodes[:10]

        # 4. Plasticidade Hebbiana: neurônios ativados juntos fortalecem suas sinapses
        self._hebbian_reinforce([n[0] for n in top_nodes[:5]])

        # 5. Mapear restricoes inegociaveis dos nos ativados
        constraints = self._extract_constraints([n[0] for n in top_nodes])

        return {
            "query": query,
            "seeds": seeds,
            "top_activated": [{"node": n[0], "energy": round(n[1], 2), "lobe": self.nodes[n[0]]["lobe"]} for n in top_nodes],
            "inviolable_constraints": constraints,
            "subgraph_nodes": [n[0] for n in top_nodes]
        }

    def _hebbian_reinforce(self, active_nodes: list[str]):
        """Fortalece o peso sinaptico das conexoes ativadas em conjunto (Hebbian Learning)"""
        updated = False
        for i in range(len(active_nodes)):
            for j in range(i + 1, len(active_nodes)):
                pair_forward = (active_nodes[i], active_nodes[j])
                pair_backward = (active_nodes[j], active_nodes[i])
                if pair_forward in self.edges:
                    self.edges[pair_forward] = min(5.0, self.edges[pair_forward] + 0.05)
                    updated = True
                if pair_backward in self.edges:
                    self.edges[pair_backward] = min(5.0, self.edges[pair_backward] + 0.05)
                    updated = True

        if updated:
            self._persist_graph()

    def _extract_constraints(self, active_node_ids: list[str]) -> list[str]:
        constraints = []
        for nid in active_node_ids:
            content = self.nodes[nid]["content"]
            # Extrair secoes de Leis / Mandatos / Restricoes
            for block in re.findall(r"(?:Lei|Mandato|Restri|Inegoci|Regra)[\w\s:]+\n([^\n#]+)", content, re.IGNORECASE):
                cleaned = block.strip().replace("- ", "")
                if cleaned and cleaned not in constraints:
                    constraints.append(f"[{nid}] {cleaned}")
        return constraints[:6]

    def _persist_graph(self):
        edges_data = []
        for (s, t), w in self.edges.items():
            edges_data.append({"source": s, "target": t, "weight": round(w, 3)})

        payload = {
            "version": "2.0.0",
            "updated_at": datetime.now().isoformat(),
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "edges": edges_data
        }
        self.graph_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    engine = SynapticEngine()
    result = engine.activate("arquitetura software")
    print("Sementes ativadas:", result["seeds"])
    print("Top neurônios:", result["top_activated"])
    print("Restricoes:", result["inviolable_constraints"])
