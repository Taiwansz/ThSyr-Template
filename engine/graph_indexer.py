"""
ThSyr Graph Indexer & Neural Topology Auditor
Varredura completa, indexacao sinaptica e regeneracao multi-formato (JSON, HTML, SVG, PNG)
Suporte estrito a isolamento de diretorio de saida para testes hermeticos.
"""

from pathlib import Path
from typing import Any

from .config import settings, setup_logger
from .neural_graph import HTML_OUTPUT, extract_graph_data, generate_html_canvas
from .png_graph import render_png_graph
from .svg_graph import render_svg_graph
from .synaptic_engine import SynapticEngine

logger = setup_logger("graph_indexer")


def reindex_and_audit(brain_dir: Path | None = None, output_dir: Path | None = None) -> dict[str, Any]:
    b_dir = brain_dir or settings.brain.brain_dir
    out_dir = output_dir or (settings.brain.state_dir if settings.env == "test" else b_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    graph_file = out_dir / "knowledge_graph.json"
    html_file = out_dir / "neural_canvas.html" if settings.env == "test" or output_dir else HTML_OUTPUT

    logger.info("Iniciando varredura e reindexacao dos nodulos cerebrais...")

    # 1. Instanciar SynapticEngine e reconstruir grafo
    engine = SynapticEngine(brain_dir=b_dir, graph_file=graph_file)
    engine._persist_graph()

    # 2. Extrair dados para visualizacao e renderizar Neural Canvas
    data = extract_graph_data(b_dir)
    generate_html_canvas(data, html_file)

    # 3. Renderizar grafos anatomicos (SVG e PNG)
    svg_target = out_dir / "anatomical_map.svg" if (settings.env == "test" or output_dir) else None
    png_target = out_dir / "brain_graph.png" if (settings.env == "test" or output_dir) else None
    svg_path = render_svg_graph(output_path=svg_target)
    png_path = render_png_graph(output_path=png_target)

    # 4. Auditoria de conectividade e distribuicao
    degree_map: dict[str, int] = {}
    for edge in engine.edges.keys():
        degree_map[edge[0]] = degree_map.get(edge[0], 0) + 1
        degree_map[edge[1]] = degree_map.get(edge[1], 0) + 1

    top_hubs = sorted(degree_map.items(), key=lambda x: x[1], reverse=True)[:10]

    lobe_distribution: dict[str, int] = {}
    for node in engine.nodes.values():
        lobe = node.get("lobe", "cortex")
        lobe_distribution[lobe] = lobe_distribution.get(lobe, 0) + 1

    summary = {
        "total_nodes": len(engine.nodes),
        "total_edges": len(engine.edges),
        "top_hubs": [{"node": h[0], "synapses": h[1]} for h in top_hubs],
        "lobe_distribution": lobe_distribution,
        "canvas_html": str(html_file),
        "graph_svg": str(svg_path),
        "graph_png": str(png_path)
    }

    logger.info(f"Reindexacao concluida: {len(engine.nodes)} nos, {len(engine.edges)} sinapses ativas.")
    return summary
