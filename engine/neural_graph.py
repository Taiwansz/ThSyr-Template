"""
ThSyr Neural Graph Generator & Live Canvas
Analisa os nós e sinapses em formato Obsidian ([[wikilinks]]) e gera uma visualizacao interativa em HTML
com HUD de rastreabilidade em tempo real (Traceabilidade Sinaptica) e foco animado em D3.js.
"""

import json
import re
import webbrowser
from pathlib import Path
from typing import Any

from .config import settings

PROJECT_ROOT = settings.project_root
BRAIN_DIR = settings.brain.brain_dir
HTML_OUTPUT = BRAIN_DIR / "neural_canvas.html"


def extract_graph_data(brain_dir: Path) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    node_set = set()
    links: list[dict[str, str]] = []
    link_set = set()

    def get_group(file_path: Path, content: str) -> str:
        p_str = str(file_path).lower()
        if "cortex" in file_path.name.lower():
            return "cortex"
        if "operador" in file_path.name.lower():
            return "operador"
        if "frontal" in p_str or "lei" in content or "anti_sicofancia" in p_str or "emoji" in p_str:
            return "regra"
        if "parietal" in p_str or "stack" in p_str or "tech" in content:
            return "tech"
        if "analytical" in p_str or "deducoes" in p_str:
            return "analitica"
        if "temporal" in p_str or "sessao" in p_str or "episodic" in p_str:
            return "sessao"
        if "occipital" in p_str or "design" in p_str or "branding" in p_str:
            return "design"
        if "limbico" in p_str or "valores" in p_str or "restricoes" in p_str:
            return "limbico"
        if "projeto" in content or any(p in file_path.name.lower() for p in ["core", "app", "service", "engine"]):
            return "projeto"
        return "conceito"

    # Encontrar todos os arquivos Markdown no brain
    for md_file in brain_dir.rglob("*.md"):
        node_id = md_file.stem
        node_set.add(node_id)
        p_str = str(md_file).lower()
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            content = ""
        group = get_group(md_file, content)
        try:
            rel_path = str(md_file.relative_to(PROJECT_ROOT))
        except ValueError:
            rel_path = str(md_file)
        nodes.append({
            "id": node_id,
            "label": node_id.replace("_", " "),
            "group": group,
            "path": rel_path
        })

        # Extrair wikilinks [[link]]
        raw_links = re.findall(r"\[\[(.*?)\]\]", content)
        for target in raw_links:
            clean_target = target.split("|")[0].strip()
            edge_key = f"{node_id}->{clean_target}"
            if edge_key not in link_set:
                link_set.add(edge_key)
                links.append({
                    "source": node_id,
                    "target": clean_target
                })

        # Fallback defensivo: se o arquivo nao possui nenhum wikilink, ancorar ao hub anatomico apropriado
        if not raw_links:
            default_hub = "Cortex_Central"
            if "temporal" in p_str or "episodic" in p_str or "sessao" in p_str:
                default_hub = "Lobo_Temporal"
            elif "frontal" in p_str or "procedural" in p_str or "lei" in p_str:
                default_hub = "Lobo_Frontal"
            elif "parietal" in p_str or "tech" in p_str:
                default_hub = "Lobo_Parietal"
            elif "occipital" in p_str or "design" in p_str:
                default_hub = "Lobo_Occipital"
            elif "limbico" in p_str:
                default_hub = "Lobo_Limbico"
            elif "analytical" in p_str:
                default_hub = "Dossie_Psicologico"

            edge_key = f"{node_id}->{default_hub}"
            if edge_key not in link_set and node_id != default_hub:
                link_set.add(edge_key)
                links.append({
                    "source": node_id,
                    "target": default_hub
                })

    # Adicionar nós linkados sem arquivo proprio
    for link in links:
        target = link["target"]
        if target not in node_set:
            node_set.add(target)
            nodes.append({
                "id": target,
                "label": target.replace("_", " "),
                "group": "conceito",
                "path": ""
            })

    degrees: dict[str, int] = {}
    for link in links:
        degrees[link["source"]] = degrees.get(link["source"], 0) + 1
        degrees[link["target"]] = degrees.get(link["target"], 0) + 1
    for node in nodes:
        node["degree"] = degrees.get(node["id"], 0)
        node["is_hub"] = node["degree"] >= 4

    return {"nodes": nodes, "links": links}


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ThSyr Neural Canvas // Live Synaptic Trace</title>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <style>
    :root {
      --bg: #070a0f;
      --card-bg: rgba(13, 17, 23, 0.94);
      --border: #21262d;
      --text: #c9d1d9;
      --text-muted: #8b949e;
      --text-bright: #ffffff;
      --accent: #58a6ff;
      --cortex: #ff3366;
      --operador: #58a6ff;
      --regra: #ff7b72;
      --tech: #79c0ff;
      --sessao: #bc8cff;
      --design: #d2a8ff;
      --limbico: #f778ba;
      --projeto: #3fb950;
      --conceito: #8b949e;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      background-color: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
      overflow: hidden;
      width: 100vw;
      height: 100vh;
    }

    /* Top Left Header */
    #header {
      position: absolute;
      top: 18px;
      left: 22px;
      z-index: 10;
      pointer-events: none;
    }

    .brand-title {
      font-size: 1.15rem;
      font-weight: 700;
      letter-spacing: 1.5px;
      color: var(--accent);
      text-transform: uppercase;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .brand-subtitle {
      margin-top: 4px;
      font-size: 0.78rem;
      color: var(--text-muted);
      letter-spacing: 0.5px;
    }

    /* Top Right Neural HUD */
    #hud-container {
      position: absolute;
      top: 18px;
      right: 22px;
      width: 360px;
      max-height: 90vh;
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      backdrop-filter: blur(14px);
      box-shadow: 0 12px 36px rgba(0, 0, 0, 0.75);
      z-index: 20;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .hud-header {
      padding: 14px 16px;
      border-bottom: 1px solid var(--border);
      background: rgba(22, 27, 34, 0.6);
    }

    .hud-title-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 4px;
    }

    .hud-tag {
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 1px;
      color: var(--accent);
      text-transform: uppercase;
    }

    .badge-status {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 3px 8px;
      border-radius: 12px;
      font-size: 0.68rem;
      font-weight: 600;
      letter-spacing: 0.5px;
      background: #21262d;
      color: var(--text-muted);
      border: 1px solid #30363d;
      transition: all 0.3s ease;
    }

    .badge-status.active {
      background: rgba(63, 185, 80, 0.15);
      color: #3fb950;
      border-color: rgba(63, 185, 80, 0.4);
      box-shadow: 0 0 12px rgba(63, 185, 80, 0.3);
    }

    .pulse-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--text-muted);
    }

    .badge-status.active .pulse-dot {
      background: #3fb950;
      box-shadow: 0 0 6px #3fb950;
      animation: blink 1s ease-in-out infinite alternate;
    }

    @keyframes blink {
      from { opacity: 0.4; }
      to { opacity: 1; }
    }

    .hud-subtitle {
      font-size: 0.70rem;
      color: var(--text-muted);
    }

    .hud-body {
      padding: 14px 16px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .hud-section {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .section-label {
      font-size: 0.68rem;
      font-weight: 700;
      letter-spacing: 0.8px;
      color: var(--text-muted);
      text-transform: uppercase;
    }

    .section-label.alert-label {
      color: var(--regra);
    }

    .query-box {
      font-size: 0.82rem;
      line-height: 1.4;
      color: var(--text-bright);
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 6px;
      padding: 8px 10px;
      word-break: break-word;
    }

    .tags-container {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }

    .seed-pill {
      font-size: 0.72rem;
      padding: 2px 8px;
      border-radius: 4px;
      background: rgba(88, 166, 255, 0.15);
      border: 1px solid rgba(88, 166, 255, 0.35);
      color: var(--accent);
      font-weight: 500;
    }

    .empty-tag, .empty-hint {
      font-size: 0.72rem;
      color: #6e7681;
      font-style: italic;
    }

    .nodes-list {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .node-row {
      display: flex;
      flex-direction: column;
      gap: 3px;
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 6px;
      padding: 6px 8px;
      transition: border-color 0.2s;
    }

    .node-row:hover {
      border-color: var(--accent);
    }

    .node-row-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .node-name {
      font-size: 0.76rem;
      font-weight: 600;
      color: var(--text-bright);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .node-lobe-tag {
      font-size: 0.65rem;
      padding: 1px 6px;
      border-radius: 3px;
      text-transform: uppercase;
      font-weight: 600;
    }

    .energy-bar-bg {
      width: 100%;
      height: 4px;
      background: #21262d;
      border-radius: 2px;
      overflow: hidden;
    }

    .energy-bar-fill {
      height: 100%;
      background: var(--accent);
      border-radius: 2px;
      transition: width 0.4s ease;
    }

    .constraints-list {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .constraint-item {
      font-size: 0.72rem;
      padding: 4px 8px;
      background: rgba(255, 123, 114, 0.12);
      border: 1px solid rgba(255, 123, 114, 0.3);
      color: #ffa198;
      border-radius: 4px;
    }

    .hud-footer {
      padding: 10px 16px;
      border-top: 1px solid var(--border);
      background: rgba(22, 27, 34, 0.6);
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .hud-meta {
      display: flex;
      justify-content: space-between;
      font-size: 0.68rem;
      color: var(--text-muted);
    }

    .hud-actions {
      display: flex;
      gap: 8px;
    }

    .hud-btn {
      flex: 1;
      padding: 6px 10px;
      font-size: 0.72rem;
      font-weight: 600;
      border-radius: 6px;
      border: 1px solid #30363d;
      background: #21262d;
      color: var(--text-bright);
      cursor: pointer;
      transition: all 0.2s;
    }

    .hud-btn:hover {
      background: #30363d;
      border-color: var(--accent);
    }

    .hud-btn.primary {
      background: rgba(88, 166, 255, 0.2);
      border-color: var(--accent);
      color: var(--accent);
    }

    .hud-btn.primary:hover {
      background: rgba(88, 166, 255, 0.35);
    }

    /* Bottom Left Legend */
    #legend {
      position: absolute;
      bottom: 20px;
      left: 22px;
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px 16px;
      font-size: 0.72rem;
      z-index: 10;
      backdrop-filter: blur(10px);
      box-shadow: 0 8px 24px rgba(0,0,0,0.5);
    }

    .legend-title {
      font-size: 0.68rem;
      font-weight: 700;
      color: var(--text-muted);
      letter-spacing: 0.8px;
      margin-bottom: 8px;
      text-transform: uppercase;
    }

    .legend-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px 14px;
    }

    .legend-item {
      display: flex;
      align-items: center;
      gap: 6px;
      color: var(--text);
    }

    .legend-color {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      flex-shrink: 0;
    }

    /* SVG Canvas */
    svg {
      width: 100vw;
      height: 100vh;
      display: block;
    }

    .link {
      stroke: #21262d;
      stroke-opacity: 0.6;
      stroke-width: 1.5px;
      transition: stroke 0.4s, stroke-width 0.4s, stroke-opacity 0.4s;
    }

    .link.active-synapse {
      stroke: #58a6ff;
      stroke-width: 3.5px;
      stroke-opacity: 0.95;
      stroke-dasharray: 6 3;
      animation: dashFlow 1s linear infinite;
    }

    .link.dimmed {
      stroke-opacity: 0.1;
    }

    @keyframes dashFlow {
      to {
        stroke-dashoffset: -18;
      }
    }

    .node {
      cursor: pointer;
      transition: opacity 0.4s;
    }

    .node.dimmed {
      opacity: 0.15;
    }

    .node text {
      font-size: 10px;
      fill: #8b949e;
      pointer-events: none;
      transition: fill 0.2s, font-size 0.2s, font-weight 0.2s;
    }

    .node:hover text {
      fill: #ffffff;
      font-weight: bold;
    }

    .node.activated text {
      fill: #ffffff;
      font-size: 12px;
      font-weight: 700;
    }

    .pulse-halo {
      fill: none;
      stroke-width: 2px;
      opacity: 0;
      animation: haloPulse 2s cubic-bezier(0.25, 1, 0.5, 1) infinite;
    }

    @keyframes haloPulse {
      0% {
        r: 12;
        opacity: 0.8;
      }
      100% {
        r: 28;
        opacity: 0;
      }
    }
  </style>
</head>
<body>
  <div id="header">
    <div class="brand-title">
      <span>THSYR // NEURAL CANVAS</span>
    </div>
    <div class="brand-subtitle">Rede Neural Cognitiva e Grafo de Conhecimento</div>
  </div>

  <div id="hud-container">
    <div class="hud-header">
      <div class="hud-title-row">
        <span class="hud-tag">RASTREABILIDADE SINÁPTICA</span>
        <div id="pulse-badge" class="badge-status">
          <span class="pulse-dot"></span>
          <span id="pulse-status-text">STANDBY</span>
        </div>
      </div>
      <div class="hud-subtitle">MONITOR DE DISPARO NEURAL EM TEMPO REAL</div>
    </div>

    <div class="hud-body">
      <div class="hud-section">
        <div class="section-label">ÚLTIMA SOLICITAÇÃO</div>
        <div id="hud-query" class="query-box">Aguardando novo estímulo neural...</div>
      </div>

      <div class="hud-section">
        <div class="section-label">SEMENTES DISPARADAS (SEEDS)</div>
        <div id="hud-seeds" class="tags-container">
          <span class="empty-tag">Nenhuma semente ativa</span>
        </div>
      </div>

      <div class="hud-section">
        <div class="section-label">NEURÔNIOS ENERGIZADOS</div>
        <div id="hud-nodes" class="nodes-list">
          <div class="empty-hint">Grafo em repouso basal.</div>
        </div>
      </div>

      <div id="hud-constraints-section" class="hud-section" style="display: none;">
        <div class="section-label alert-label">RESTRIÇÕES INEGOCIÁVEIS ACIONADAS</div>
        <div id="hud-constraints" class="constraints-list"></div>
      </div>
    </div>

    <div class="hud-footer">
      <div class="hud-meta">
        <span id="hud-timestamp">Sincronizado</span>
        <span id="hud-active-count">0 nós ativos</span>
      </div>
      <div class="hud-actions">
        <button id="btn-reset-focus" class="hud-btn">Visão Global</button>
      </div>
    </div>
  </div>

  <div id="legend">
    <div class="legend-title">Lobos e Categorias</div>
    <div class="legend-grid">
      <div class="legend-item"><div class="legend-color" style="background:#ff3366"></div>Córtex Central</div>
      <div class="legend-item"><div class="legend-color" style="background:#58a6ff"></div>Operador</div>
      <div class="legend-item"><div class="legend-color" style="background:#ff7b72"></div>Frontal (Leis/Filtros)</div>
      <div class="legend-item"><div class="legend-color" style="background:#f778ba"></div>Límbico (Valores/Vida)</div>
      <div class="legend-item"><div class="legend-color" style="background:#79c0ff"></div>Parietal (Engenharia)</div>
      <div class="legend-item"><div class="legend-color" style="background:#d2a8ff"></div>Occipital (Design/UI)</div>
      <div class="legend-item"><div class="legend-color" style="background:#bc8cff"></div>Temporal (Episódico)</div>
      <div class="legend-item"><div class="legend-color" style="background:#3fb950"></div>Projetos Ativos</div>
    </div>
  </div>

  <svg id="canvas"></svg>

  <script>
    const data = __GRAPH_JSON__;

    const colorMap = {
      "cortex": "#ff3366",
      "operador": "#58a6ff",
      "regra": "#ff7b72",
      "frontal": "#ff7b72",
      "limbico": "#f778ba",
      "tech": "#79c0ff",
      "parietal": "#79c0ff",
      "design": "#d2a8ff",
      "occipital": "#d2a8ff",
      "sessao": "#bc8cff",
      "temporal": "#bc8cff",
      "projeto": "#3fb950",
      "conceito": "#8b949e"
    };

    const width = window.innerWidth;
    const height = window.innerHeight;

    const svg = d3.select("#canvas")
      .attr("viewBox", [0, 0, width, height]);

    // Defs para efeitos de luz e filtros glow
    const defs = svg.append("defs");
    const filter = defs.append("filter")
      .attr("id", "glow")
      .attr("x", "-50%")
      .attr("y", "-50%")
      .attr("width", "200%")
      .attr("height", "200%");

    filter.append("feGaussianBlur")
      .attr("stdDeviation", "5")
      .attr("result", "coloredBlur");

    const feMerge = filter.append("feMerge");
    feMerge.append("feMergeNode").attr("in", "coloredBlur");
    feMerge.append("feMergeNode").attr("in", "SourceGraphic");

    const g = svg.append("g");

    const zoom = d3.zoom()
      .scaleExtent([0.1, 4])
      .on("zoom", (event) => {
        g.attr("transform", event.transform);
      });

    svg.call(zoom);

    const simulation = d3.forceSimulation(data.nodes)
      .force("link", d3.forceLink(data.links).id(d => d.id).distance(120))
      .force("charge", d3.forceManyBody().strength(-380))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(28));

    const link = g.append("g")
      .attr("class", "links-layer")
      .selectAll(".link")
      .data(data.links)
      .enter().append("line")
      .attr("class", "link");

    const node = g.append("g")
      .attr("class", "nodes-layer")
      .selectAll(".node")
      .data(data.nodes)
      .enter().append("g")
      .attr("class", "node")
      .attr("data-id", d => d.id.toLowerCase())
      .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    // Halo para pulsos
    node.append("circle")
      .attr("class", "pulse-halo")
      .attr("r", 12)
      .attr("stroke", d => colorMap[d.group] || "#8b949e");

    // Circulo principal do neuronio
    node.append("circle")
      .attr("class", "node-circle")
      .attr("r", d => d.group === "cortex" ? 14 : (d.group === "operador" ? 12 : 8))
      .attr("fill", d => colorMap[d.group] || "#8b949e")
      .attr("stroke", "#070a0f")
      .attr("stroke-width", 2);

    node.append("text")
      .attr("x", 12)
      .attr("y", 4)
      .text(d => d.label);

    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      node.attr("transform", d => `translate(${d.x},${d.y})`);
    });

    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    function resetGlobalView() {
      node.classed("dimmed", false);
      node.select(".node-circle")
        .transition().duration(400)
        .attr("r", d => d.group === "cortex" ? 14 : (d.group === "operador" ? 12 : 8))
        .attr("filter", null)
        .attr("stroke", "#070a0f")
        .attr("stroke-width", 2);

      svg.transition().duration(800).call(
        zoom.transform,
        d3.zoomIdentity
      );
    }

    document.getElementById("btn-reset-focus").addEventListener("click", resetGlobalView);

  </script>
</body>
</html>
"""


def generate_html_canvas(data: dict[str, Any], output_path: Path):
    graph_json = json.dumps(data, indent=2, ensure_ascii=False)
    html_content = HTML_TEMPLATE.replace("__GRAPH_JSON__", graph_json)
    output_path.write_text(html_content, encoding="utf-8")


def render_and_open_graph(open_browser: bool = True) -> Path:
    from engine.svg_graph import render_svg_graph
    data = extract_graph_data(BRAIN_DIR)
    generate_html_canvas(data, HTML_OUTPUT)
    render_svg_graph()
    if open_browser:
        webbrowser.open(HTML_OUTPUT.as_uri())
    return HTML_OUTPUT


if __name__ == "__main__":
    render_and_open_graph(open_browser=False)
