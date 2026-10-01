"""
ThSyr Neural Canvas Generator - v3.0 Premium
Gera brain/neural_canvas.html com D3.js v7, inspector de nos, busca com autocomplete,
filtros por lobo, controles de fisica, minimap e animacoes de pulso sinaptico.
Zero emojis. Zero placeholders.
"""

import json
from pathlib import Path
from typing import Any

from .config import settings, setup_logger
from .synaptic_engine import SynapticEngine

logger = setup_logger("generate_canvas")

HTML_OUTPUT = settings.brain.brain_dir / "neural_canvas.html"


def _build_graph_data() -> dict[str, Any]:
    se = SynapticEngine()
    degree: dict[str, int] = {}
    for (s, t) in se.edges.keys():
        degree[s] = degree.get(s, 0) + 1
        degree[t] = degree.get(t, 0) + 1

    # Coleta neighbours para cada no
    neighbours: dict[str, list[str]] = {nid: [] for nid in se.nodes}
    for (s, t) in se.edges.keys():
        if s in neighbours:
            if t not in neighbours[s]:
                neighbours[s].append(t)
        if t in neighbours:
            if s not in neighbours[t]:
                neighbours[t].append(s)

    nodes_out: list[dict] = []
    for nid, data in se.nodes.items():
        nodes_out.append({
            "id": nid,
            "label": nid.replace("_", " "),
            "lobe": data["lobe"],
            "path": data["path"],
            "degree": degree.get(nid, 0),
            "neighbours": neighbours.get(nid, [])
        })

    edges_out: list[dict] = [
        {"source": s, "target": t, "weight": w}
        for (s, t), w in se.edges.items()
    ]

    return {"nodes": nodes_out, "edges": edges_out}


def _build_html(graph_data: dict[str, Any]) -> str:
    graph_json = json.dumps(graph_data, ensure_ascii=False, separators=(",", ":"))
    return _TEMPLATE.replace("__GRAPH_JSON__", graph_json)


def generate() -> Path:
    logger.info("Iniciando geracao do Neural Canvas Premium...")
    data = _build_graph_data()
    html = _build_html(data)
    HTML_OUTPUT.write_text(html, encoding="utf-8")
    logger.info(
        "Neural Canvas gerado: %s (%d nos, %d sinapses)",
        HTML_OUTPUT,
        len(data["nodes"]),
        len(data["edges"]),
    )
    return HTML_OUTPUT


# =============================================================================
# HTML TEMPLATE PREMIUM
# =============================================================================
_TEMPLATE = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>ThSyr // Neural Canvas v3</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
/* ===== RESET & BASE ===== */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#070a0f;
  --surface:#0d1117;
  --surface2:#161b22;
  --surface3:#21262d;
  --border:#21262d;
  --border2:#30363d;
  --text:#c9d1d9;
  --text-muted:#8b949e;
  --text-dim:#6e7681;
  --text-bright:#f0f6fc;
  --accent:#58a6ff;
  --accent-dim:rgba(88,166,255,0.15);
  --accent-border:rgba(88,166,255,0.35);
  --green:#3fb950;
  --green-dim:rgba(63,185,80,0.15);
  --red:#ff7b72;
  --red-dim:rgba(255,123,114,0.15);
  --lobe-cortex:#ff3366;
  --lobe-operador:#58a6ff;
  --lobe-frontal:#ff7b72;
  --lobe-parietal:#79c0ff;
  --lobe-temporal:#bc8cff;
  --lobe-occipital:#d2a8ff;
  --lobe-limbico:#3fb950;
  --lobe-projeto:#f778ba;
  --lobe-conceito:#8b949e;
  --panel-w:340px;
  --top-bar-h:52px;
  --font-mono:'JetBrains Mono','Fira Code','Cascadia Code','Consolas',monospace;
  --font-ui:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  --radius:8px;
  --shadow:0 12px 40px rgba(0,0,0,0.7);
  --shadow-sm:0 4px 16px rgba(0,0,0,0.5);
}
html,body{
  width:100%;height:100%;overflow:hidden;
  background:var(--bg);color:var(--text);
  font-family:var(--font-ui);font-size:13px;line-height:1.5;
}

/* ===== TOP BAR ===== */
#top-bar{
  position:fixed;top:0;left:0;right:0;height:var(--top-bar-h);
  background:rgba(7,10,15,0.92);border-bottom:1px solid var(--border);
  backdrop-filter:blur(12px);
  display:flex;align-items:center;gap:16px;padding:0 18px;
  z-index:100;
}
#brand{
  display:flex;flex-direction:column;white-space:nowrap;flex-shrink:0;
}
#brand-name{
  font-family:var(--font-mono);font-size:0.78rem;font-weight:700;
  letter-spacing:2px;color:var(--accent);text-transform:uppercase;
}
#brand-sub{
  font-size:0.62rem;color:var(--text-dim);letter-spacing:0.5px;
  font-family:var(--font-mono);
}
#search-wrap{
  position:relative;flex:1;max-width:400px;
}
#search-input{
  width:100%;padding:7px 12px 7px 34px;
  background:var(--surface2);border:1px solid var(--border2);
  border-radius:var(--radius);color:var(--text-bright);
  font-size:0.80rem;font-family:var(--font-mono);
  outline:none;transition:border-color 0.2s,box-shadow 0.2s;
}
#search-input::placeholder{color:var(--text-dim);}
#search-input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(88,166,255,0.12);}
#search-icon{
  position:absolute;left:10px;top:50%;transform:translateY(-50%);
  width:14px;height:14px;
}
#autocomplete{
  position:absolute;top:calc(100% + 4px);left:0;right:0;
  background:var(--surface2);border:1px solid var(--border2);
  border-radius:var(--radius);overflow:hidden;z-index:200;
  box-shadow:var(--shadow-sm);display:none;max-height:240px;overflow-y:auto;
}
.ac-item{
  padding:7px 12px;cursor:pointer;font-size:0.78rem;
  display:flex;align-items:center;gap:8px;
  transition:background 0.1s;
}
.ac-item:hover,.ac-item.selected{background:var(--surface3);}
.ac-lobe{
  font-size:0.62rem;font-family:var(--font-mono);font-weight:700;
  padding:1px 5px;border-radius:3px;flex-shrink:0;
}
.ac-label{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--text-bright);}
#lobe-pills{
  display:flex;gap:6px;align-items:center;flex-wrap:nowrap;overflow-x:auto;
}
#lobe-pills::-webkit-scrollbar{display:none;}
.lobe-pill{
  padding:4px 10px;border-radius:20px;border:1px solid var(--border2);
  background:var(--surface2);color:var(--text-muted);
  font-size:0.68rem;font-family:var(--font-mono);font-weight:700;
  letter-spacing:0.5px;cursor:pointer;white-space:nowrap;
  transition:all 0.18s;user-select:none;text-transform:uppercase;
}
.lobe-pill:hover{border-color:currentColor;opacity:0.9;}
.lobe-pill.active{border-color:currentColor;opacity:1;}
.lobe-pill.inactive{opacity:0.35;}

/* ===== SVG CANVAS ===== */
#canvas{
  position:fixed;top:var(--top-bar-h);left:0;right:0;
  bottom:0;width:100%;height:calc(100vh - var(--top-bar-h));
}

/* ===== SVG NODE/LINK STYLES ===== */
.link{
  stroke:#21262d;stroke-opacity:0.55;stroke-width:1.2px;
  transition:stroke 0.3s,stroke-opacity 0.3s,stroke-width 0.3s;
}
.link.active-synapse{
  stroke:var(--accent);stroke-width:2.8px;stroke-opacity:0.9;
  stroke-dasharray:8 4;animation:dashFlow 1.2s linear infinite;
}
.link.highlighted{
  stroke:var(--accent);stroke-width:2px;stroke-opacity:0.75;
}
.link.dimmed{stroke-opacity:0.06;}

@keyframes dashFlow{to{stroke-dashoffset:-24;}}

.node{cursor:pointer;}
.node.dimmed{opacity:0.1;}
.node.activated .node-circle{filter:url(#glow);}
.node-circle{transition:r 0.25s,stroke-width 0.25s;}
.node-label{
  font-size:9px;fill:var(--text-dim);pointer-events:none;
  transition:fill 0.2s,font-size 0.2s,font-weight 0.2s;
}
.node:hover .node-label,.node.activated .node-label{
  fill:var(--text-bright);font-size:10.5px;font-weight:700;
}
.pulse-halo{
  fill:none;stroke-width:2px;opacity:0;
  animation:haloPulse 2.2s cubic-bezier(0.25,1,0.5,1) infinite;
}
@keyframes haloPulse{
  0%{r:13;opacity:0.75;}
  100%{r:30;opacity:0;}
}

/* ===== INSPECTOR (RIGHT PANEL) ===== */
#inspector{
  position:fixed;top:var(--top-bar-h);right:0;
  width:var(--panel-w);height:calc(100vh - var(--top-bar-h));
  background:rgba(13,17,23,0.97);border-left:1px solid var(--border);
  backdrop-filter:blur(14px);z-index:80;
  display:flex;flex-direction:column;overflow:hidden;
  transform:translateX(100%);transition:transform 0.28s cubic-bezier(0.16,1,0.3,1);
}
#inspector.open{transform:translateX(0);}

.panel-header{
  padding:14px 16px;border-bottom:1px solid var(--border);
  background:rgba(22,27,34,0.8);display:flex;flex-direction:column;gap:4px;
  flex-shrink:0;
}
.panel-tag{
  font-family:var(--font-mono);font-size:0.65rem;font-weight:700;
  letter-spacing:1.5px;text-transform:uppercase;color:var(--text-dim);
}
.panel-title{
  font-size:0.95rem;font-weight:700;color:var(--text-bright);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
}
.panel-close{
  position:absolute;top:12px;right:12px;
  width:26px;height:26px;cursor:pointer;
  background:var(--surface3);border:1px solid var(--border2);
  border-radius:6px;display:flex;align-items:center;justify-content:center;
  color:var(--text-muted);font-size:1rem;
  transition:background 0.15s,color 0.15s;
}
.panel-close:hover{background:var(--red-dim);color:var(--red);}

.panel-body{
  flex:1;overflow-y:auto;padding:14px 16px;
  display:flex;flex-direction:column;gap:14px;
}
.panel-body::-webkit-scrollbar{width:4px;}
.panel-body::-webkit-scrollbar-track{background:transparent;}
.panel-body::-webkit-scrollbar-thumb{background:var(--border2);border-radius:2px;}

.info-block{display:flex;flex-direction:column;gap:5px;}
.info-label{
  font-family:var(--font-mono);font-size:0.63rem;font-weight:700;
  letter-spacing:0.8px;text-transform:uppercase;color:var(--text-dim);
}
.info-value{
  font-size:0.78rem;color:var(--text);background:var(--surface2);
  border:1px solid var(--border2);border-radius:5px;padding:5px 8px;
  font-family:var(--font-mono);word-break:break-all;
}
.lobe-badge{
  display:inline-block;padding:2px 8px;border-radius:4px;
  font-family:var(--font-mono);font-size:0.70rem;font-weight:700;
  letter-spacing:0.5px;text-transform:uppercase;
}
.degree-bar-bg{
  width:100%;height:5px;background:var(--surface3);border-radius:3px;overflow:hidden;
}
.degree-bar-fill{
  height:100%;border-radius:3px;transition:width 0.5s ease;
}

.neighbours-list{
  display:flex;flex-direction:column;gap:4px;max-height:220px;overflow-y:auto;
}
.neighbours-list::-webkit-scrollbar{width:3px;}
.neighbours-list::-webkit-scrollbar-thumb{background:var(--border2);}
.neighbour-item{
  padding:5px 8px;background:var(--surface2);border:1px solid var(--border2);
  border-radius:5px;font-size:0.72rem;color:var(--text);cursor:pointer;
  transition:border-color 0.15s,color 0.15s;
  display:flex;align-items:center;gap:6px;
  font-family:var(--font-mono);
}
.neighbour-item:hover{border-color:var(--accent);color:var(--text-bright);}
.neighbour-dot{width:6px;height:6px;border-radius:50%;flex-shrink:0;}

/* ===== HUD (LEFT PANEL - COLLAPSIBLE) ===== */
#hud{
  position:fixed;top:calc(var(--top-bar-h) + 14px);left:14px;
  width:300px;
  background:rgba(13,17,23,0.94);border:1px solid var(--border);
  border-radius:var(--radius);backdrop-filter:blur(12px);
  box-shadow:var(--shadow);z-index:70;
  display:flex;flex-direction:column;overflow:hidden;
  transition:width 0.25s ease,opacity 0.25s ease;
}
#hud.collapsed{width:auto;overflow:visible;}
#hud-header{
  padding:10px 14px;border-bottom:1px solid var(--border);
  background:rgba(22,27,34,0.7);display:flex;align-items:center;
  justify-content:space-between;cursor:pointer;user-select:none;flex-shrink:0;
}
#hud-tag{
  font-family:var(--font-mono);font-size:0.62rem;font-weight:700;
  letter-spacing:1.5px;text-transform:uppercase;color:var(--accent);
}
#hud-toggle-btn{
  font-family:var(--font-mono);font-size:0.68rem;color:var(--text-dim);
  transition:color 0.15s;
}
#hud-body{display:flex;flex-direction:column;gap:10px;padding:12px 14px;overflow:hidden;}
#hud.collapsed #hud-body{display:none;}

.hud-stat-row{display:flex;justify-content:space-between;align-items:center;}
.hud-stat-label{font-size:0.68rem;color:var(--text-dim);font-family:var(--font-mono);}
.hud-stat-value{
  font-size:0.75rem;font-weight:700;color:var(--text-bright);
  font-family:var(--font-mono);
}
#pulse-badge{
  display:inline-flex;align-items:center;gap:5px;
  padding:3px 8px;border-radius:12px;font-size:0.65rem;font-weight:700;
  background:var(--surface3);color:var(--text-dim);border:1px solid var(--border2);
  font-family:var(--font-mono);transition:all 0.3s;
}
#pulse-badge.active{
  background:var(--green-dim);color:var(--green);
  border-color:rgba(63,185,80,0.4);box-shadow:0 0 10px rgba(63,185,80,0.2);
}
.pulse-dot{
  width:5px;height:5px;border-radius:50%;background:var(--text-dim);
}
#pulse-badge.active .pulse-dot{
  background:var(--green);box-shadow:0 0 5px var(--green);
  animation:blink 1s ease-in-out infinite alternate;
}
@keyframes blink{from{opacity:0.4;}to{opacity:1;}}
.hud-divider{height:1px;background:var(--border);margin:2px 0;}

#hud-query-text{
  font-size:0.72rem;color:var(--text);background:var(--surface2);
  border:1px solid var(--border2);border-radius:5px;padding:6px 8px;
  line-height:1.4;font-family:var(--font-mono);word-break:break-word;
}
.hud-btn-row{display:flex;gap:6px;}
.hud-btn{
  flex:1;padding:6px 8px;font-size:0.68rem;font-weight:700;
  border-radius:5px;border:1px solid var(--border2);background:var(--surface2);
  color:var(--text-bright);cursor:pointer;font-family:var(--font-mono);
  transition:all 0.15s;letter-spacing:0.5px;
}
.hud-btn:hover{background:var(--surface3);border-color:var(--accent);}
.hud-btn.primary{
  background:var(--accent-dim);border-color:var(--accent-border);color:var(--accent);
}
.hud-btn.primary:hover{background:rgba(88,166,255,0.28);}

/* ===== LEGEND (BOTTOM-LEFT) ===== */
#legend{
  position:fixed;bottom:64px;left:14px;
  background:rgba(13,17,23,0.94);border:1px solid var(--border);
  border-radius:var(--radius);padding:10px 14px;
  backdrop-filter:blur(10px);box-shadow:var(--shadow-sm);z-index:60;
}
#legend-title{
  font-family:var(--font-mono);font-size:0.60rem;font-weight:700;
  letter-spacing:1px;text-transform:uppercase;color:var(--text-dim);
  margin-bottom:7px;
}
#legend-grid{display:grid;grid-template-columns:1fr 1fr;gap:4px 12px;}
.legend-item{display:flex;align-items:center;gap:6px;font-size:0.68rem;color:var(--text);}
.legend-dot{width:7px;height:7px;border-radius:50%;flex-shrink:0;}

/* ===== PHYSICS CONTROLS (BOTTOM CENTER) ===== */
#physics-toggle{
  position:fixed;bottom:16px;left:50%;transform:translateX(-50%);
  padding:6px 16px;font-size:0.68rem;font-weight:700;font-family:var(--font-mono);
  background:var(--surface2);border:1px solid var(--border2);
  border-radius:20px;color:var(--text-muted);cursor:pointer;
  letter-spacing:1px;text-transform:uppercase;z-index:60;
  transition:all 0.15s;
}
#physics-toggle:hover{border-color:var(--accent);color:var(--accent);}
#physics-panel{
  position:fixed;bottom:52px;left:50%;transform:translateX(-50%);
  background:rgba(13,17,23,0.96);border:1px solid var(--border);
  border-radius:var(--radius);padding:14px 18px;
  backdrop-filter:blur(12px);box-shadow:var(--shadow);z-index:59;
  display:none;min-width:360px;
}
#physics-panel.open{display:block;}
#physics-title{
  font-family:var(--font-mono);font-size:0.62rem;font-weight:700;
  letter-spacing:1.2px;text-transform:uppercase;color:var(--text-dim);
  margin-bottom:12px;
}
.slider-row{
  display:flex;align-items:center;gap:10px;margin-bottom:8px;
}
.slider-name{
  font-family:var(--font-mono);font-size:0.65rem;color:var(--text-muted);
  width:110px;flex-shrink:0;
}
.slider-range{
  flex:1;-webkit-appearance:none;height:3px;border-radius:2px;
  background:var(--surface3);outline:none;cursor:pointer;
}
.slider-range::-webkit-slider-thumb{
  -webkit-appearance:none;width:13px;height:13px;border-radius:50%;
  background:var(--accent);cursor:pointer;border:2px solid var(--bg);
}
.slider-val{
  font-family:var(--font-mono);font-size:0.65rem;color:var(--text-bright);
  width:36px;text-align:right;
}

/* ===== MINIMAP (BOTTOM-RIGHT) ===== */
#minimap-wrap{
  position:fixed;bottom:16px;right:14px;z-index:60;
}
#minimap{
  width:160px;height:110px;
  border:1px solid var(--border);border-radius:var(--radius);
  background:rgba(7,10,15,0.9);backdrop-filter:blur(8px);
  cursor:crosshair;display:block;
}
#minimap-label{
  font-family:var(--font-mono);font-size:0.58rem;color:var(--text-dim);
  text-align:center;margin-top:3px;letter-spacing:0.5px;text-transform:uppercase;
}

/* ===== COUNTER HUD (TOP RIGHT) ===== */
#stats-hud{
  margin-left:auto;flex-shrink:0;
  display:flex;align-items:center;gap:12px;
}
.stat-chip{
  display:flex;flex-direction:column;align-items:flex-end;
}
.stat-n{
  font-family:var(--font-mono);font-size:0.85rem;font-weight:700;color:var(--text-bright);
  line-height:1.1;
}
.stat-l{
  font-family:var(--font-mono);font-size:0.58rem;color:var(--text-dim);
  text-transform:uppercase;letter-spacing:0.5px;
}
.stat-sep{width:1px;height:24px;background:var(--border2);}

/* ===== TOOLTIP ===== */
#tooltip{
  position:fixed;z-index:200;pointer-events:none;
  background:rgba(13,17,23,0.97);border:1px solid var(--border2);
  border-radius:var(--radius);padding:7px 10px;
  font-size:0.72rem;font-family:var(--font-mono);color:var(--text);
  box-shadow:var(--shadow-sm);white-space:nowrap;display:none;
}

/* ===== SCROLLBAR GLOBAL ===== */
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:3px;}
</style>
</head>
<body>

<!-- TOP BAR -->
<div id="top-bar">
  <div id="brand">
    <div id="brand-name">ThSyr // Neural Canvas</div>
    <div id="brand-sub">v3.0 // Rede Cognitiva Sagital</div>
  </div>

  <div id="search-wrap">
    <svg id="search-icon" viewBox="0 0 16 16" fill="none" stroke="#6e7681" stroke-width="1.6">
      <circle cx="6.5" cy="6.5" r="4"/><line x1="9.9" y1="9.9" x2="14" y2="14"/>
    </svg>
    <input id="search-input" type="text" placeholder="Buscar nodulo..." autocomplete="off" spellcheck="false">
    <div id="autocomplete"></div>
  </div>

  <div id="lobe-pills">
    <div class="lobe-pill active" data-lobe="all" style="color:var(--text-muted)">TODOS</div>
    <div class="lobe-pill active" data-lobe="cortex" style="color:var(--lobe-cortex)">CORTEX</div>
    <div class="lobe-pill active" data-lobe="frontal" style="color:var(--lobe-frontal)">FRONTAL</div>
    <div class="lobe-pill active" data-lobe="parietal" style="color:var(--lobe-parietal)">PARIETAL</div>
    <div class="lobe-pill active" data-lobe="temporal" style="color:var(--lobe-temporal)">TEMPORAL</div>
    <div class="lobe-pill active" data-lobe="occipital" style="color:var(--lobe-occipital)">OCCIPITAL</div>
    <div class="lobe-pill active" data-lobe="limbico" style="color:var(--lobe-limbico)">LIMBICO</div>
  </div>

  <div id="stats-hud">
    <div class="stat-chip">
      <span class="stat-n" id="stat-nodes">144</span>
      <span class="stat-l">nodulos</span>
    </div>
    <div class="stat-sep"></div>
    <div class="stat-chip">
      <span class="stat-n" id="stat-edges">546</span>
      <span class="stat-l">sinapses</span>
    </div>
    <div class="stat-sep"></div>
    <div class="stat-chip" id="stat-active-wrap" style="display:none">
      <span class="stat-n" id="stat-active">0</span>
      <span class="stat-l">ativos</span>
    </div>
  </div>
</div>

<!-- MAIN SVG CANVAS -->
<svg id="canvas"></svg>

<!-- NODE INSPECTOR PANEL (RIGHT) -->
<div id="inspector">
  <div class="panel-header" style="position:relative">
    <div class="panel-tag">Inspetor de Nodulo</div>
    <div class="panel-title" id="inspector-title">--</div>
    <div class="panel-close" id="inspector-close">x</div>
  </div>
  <div class="panel-body" id="inspector-body">
    <div class="info-block">
      <div class="info-label">Lobo</div>
      <div id="insp-lobe"></div>
    </div>
    <div class="info-block">
      <div class="info-label">Grau de Conectividade</div>
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
        <span id="insp-degree" style="font-family:var(--font-mono);font-size:0.82rem;font-weight:700;color:var(--text-bright)"></span>
        <span style="font-size:0.68rem;color:var(--text-dim)">conexoes diretas</span>
      </div>
      <div class="degree-bar-bg"><div class="degree-bar-fill" id="insp-degree-bar"></div></div>
    </div>
    <div class="info-block">
      <div class="info-label">Caminho</div>
      <div class="info-value" id="insp-path" style="font-size:0.68rem;word-break:break-all;"></div>
    </div>
    <div class="info-block">
      <div class="info-label">Vizinhos Sinápticos (<span id="insp-neighbour-count">0</span>)</div>
      <div class="neighbours-list" id="insp-neighbours"></div>
    </div>
  </div>
</div>

<!-- HUD PANEL (LEFT) -->
<div id="hud">
  <div id="hud-header">
    <span id="hud-tag">Rastreabilidade Sinaptica</span>
    <span id="hud-toggle-btn">[recolher]</span>
  </div>
  <div id="hud-body">
    <div class="hud-stat-row">
      <span class="hud-stat-label">STATUS</span>
      <span id="pulse-badge"><span class="pulse-dot"></span><span id="pulse-text">STANDBY</span></span>
    </div>
    <div class="hud-divider"></div>
    <div class="info-label">ULTIMO EVENTO</div>
    <div id="hud-query-text">Aguardando estimulo neural...</div>
    <div class="hud-stat-row">
      <span class="hud-stat-label">HORA</span>
      <span class="hud-stat-value" id="hud-time">--</span>
    </div>
    <div class="hud-divider"></div>
    <div class="hud-btn-row">
      <button class="hud-btn primary" id="btn-pulse-demo">Simular Pulso</button>
      <button class="hud-btn" id="btn-reset">Visao Global</button>
    </div>
  </div>
</div>

<!-- LEGEND -->
<div id="legend">
  <div id="legend-title">Lobos Cerebrais</div>
  <div id="legend-grid">
    <div class="legend-item"><div class="legend-dot" style="background:var(--lobe-cortex)"></div>Cortex Central</div>
    <div class="legend-item"><div class="legend-dot" style="background:var(--lobe-frontal)"></div>Frontal</div>
    <div class="legend-item"><div class="legend-dot" style="background:var(--lobe-parietal)"></div>Parietal</div>
    <div class="legend-item"><div class="legend-dot" style="background:var(--lobe-temporal)"></div>Temporal</div>
    <div class="legend-item"><div class="legend-dot" style="background:var(--lobe-occipital)"></div>Occipital</div>
    <div class="legend-item"><div class="legend-dot" style="background:var(--lobe-limbico)"></div>Limbico</div>
  </div>
</div>

<!-- PHYSICS CONTROLS -->
<button id="physics-toggle">[FISICA]</button>
<div id="physics-panel">
  <div id="physics-title">Controles de Simulacao Fisica</div>
  <div class="slider-row">
    <span class="slider-name">Repulsao (charge)</span>
    <input type="range" class="slider-range" id="sl-charge" min="-800" max="-50" value="-380" step="10">
    <span class="slider-val" id="sl-charge-val">-380</span>
  </div>
  <div class="slider-row">
    <span class="slider-name">Dist. de Link</span>
    <input type="range" class="slider-range" id="sl-link" min="40" max="280" value="120" step="5">
    <span class="slider-val" id="sl-link-val">120</span>
  </div>
  <div class="slider-row">
    <span class="slider-name">Colisao</span>
    <input type="range" class="slider-range" id="sl-coll" min="10" max="60" value="28" step="1">
    <span class="slider-val" id="sl-coll-val">28</span>
  </div>
  <div class="slider-row">
    <span class="slider-name">Alpha Decay</span>
    <input type="range" class="slider-range" id="sl-alpha" min="1" max="50" value="15" step="1">
    <span class="slider-val" id="sl-alpha-val">15</span>
  </div>
</div>

<!-- MINIMAP -->
<div id="minimap-wrap">
  <canvas id="minimap" width="160" height="110"></canvas>
  <div id="minimap-label">Visao Macro</div>
</div>

<!-- TOOLTIP -->
<div id="tooltip"></div>

<script>
// =====================================================================
// DATA EMBARCADA
// =====================================================================
const GRAPH = __GRAPH_JSON__;

// =====================================================================
// CONFIG
// =====================================================================
const COLOR = {
  cortex:"#ff3366",
  frontal:"#ff7b72",
  parietal:"#79c0ff",
  temporal:"#bc8cff",
  occipital:"#d2a8ff",
  limbico:"#3fb950",
  operador:"#58a6ff",
  projeto:"#f778ba",
  conceito:"#8b949e"
};
const LOBE_LABEL = {
  cortex:"CORTEX",frontal:"FRONTAL",parietal:"PARIETAL",
  temporal:"TEMPORAL",occipital:"OCCIPITAL",limbico:"LIMBICO",
  operador:"OPERADOR",projeto:"PROJETO",conceito:"CONCEITO"
};
const MAX_DEGREE = Math.max(...GRAPH.nodes.map(n => n.degree));

// =====================================================================
// STATE
// =====================================================================
let currentTransform = d3.zoomIdentity;
let highlightNodeId = null;
let activeLobes = new Set(["cortex","frontal","parietal","temporal","occipital","limbico","operador","projeto","conceito"]);
let searchQuery = "";
let physicsOpen = false;
let hudCollapsed = false;
let acIndex = -1;
let filteredNodes = new Set(GRAPH.nodes.map(n => n.id));
let currentPulseId = null;
let decayTimer = null;

// Neighbour lookup por id
const nodeMap = {};
GRAPH.nodes.forEach(n => { nodeMap[n.id] = n; });

// =====================================================================
// SVG SETUP
// =====================================================================
const svgEl = document.getElementById("canvas");
const W = () => svgEl.clientWidth;
const H = () => svgEl.clientHeight;

const svg = d3.select("#canvas");

// Defs - filtros
const defs = svg.append("defs");
const glowFilter = defs.append("filter").attr("id","glow").attr("x","-60%").attr("y","-60%").attr("width","220%").attr("height","220%");
glowFilter.append("feGaussianBlur").attr("stdDeviation","5").attr("result","coloredBlur");
const feMerge = glowFilter.append("feMerge");
feMerge.append("feMergeNode").attr("in","coloredBlur");
feMerge.append("feMergeNode").attr("in","SourceGraphic");

const strongGlow = defs.append("filter").attr("id","glow-strong").attr("x","-80%").attr("y","-80%").attr("width","260%").attr("height","260%");
strongGlow.append("feGaussianBlur").attr("stdDeviation","9").attr("result","coloredBlur");
const feMerge2 = strongGlow.append("feMerge");
feMerge2.append("feMergeNode").attr("in","coloredBlur");
feMerge2.append("feMergeNode").attr("in","SourceGraphic");

// Grupo principal para zoom/pan
const g = svg.append("g").attr("id","graph-root");

// =====================================================================
// ZOOM
// =====================================================================
const zoom = d3.zoom()
  .scaleExtent([0.05, 6])
  .on("zoom", (e) => {
    currentTransform = e.transform;
    g.attr("transform", e.transform);
    drawMinimap();
  });

svg.call(zoom).on("dblclick.zoom", null);

// =====================================================================
// SIMULATION
// =====================================================================
const simulation = d3.forceSimulation(GRAPH.nodes)
  .force("link", d3.forceLink(GRAPH.edges).id(d => d.id).distance(120))
  .force("charge", d3.forceManyBody().strength(-380))
  .force("center", d3.forceCenter(800, 500))
  .force("collision", d3.forceCollide().radius(28))
  .alphaDecay(0.015)
  .on("tick", ticked);

// =====================================================================
// LINKS
// =====================================================================
const linkG = g.append("g").attr("class","links-layer");
const link = linkG.selectAll(".link")
  .data(GRAPH.edges).enter()
  .append("line").attr("class","link");

// =====================================================================
// NODES
// =====================================================================
const nodeG = g.append("g").attr("class","nodes-layer");
const node = nodeG.selectAll(".node")
  .data(GRAPH.nodes).enter()
  .append("g").attr("class","node")
  .attr("data-id", d => d.id)
  .call(
    d3.drag()
      .on("start", (e,d) => { if(!e.active) simulation.alphaTarget(0.3).restart(); d.fx=d.x; d.fy=d.y; })
      .on("drag",  (e,d) => { d.fx=e.x; d.fy=e.y; })
      .on("end",   (e,d) => { if(!e.active) simulation.alphaTarget(0); d.fx=null; d.fy=null; })
  )
  .on("click", onNodeClick)
  .on("mouseover", onNodeHover)
  .on("mouseout", onNodeOut);

// Pulse halo
node.append("circle")
  .attr("class","pulse-halo")
  .attr("r", 12)
  .attr("stroke", d => COLOR[d.lobe] || COLOR.conceito);

// Main circle
node.append("circle")
  .attr("class","node-circle")
  .attr("r", d => nodeRadius(d))
  .attr("fill", d => COLOR[d.lobe] || COLOR.conceito)
  .attr("stroke","#070a0f")
  .attr("stroke-width", 2);

// Label
node.append("text")
  .attr("class","node-label")
  .attr("x", d => nodeRadius(d) + 5)
  .attr("y", 3.5)
  .text(d => d.label);

function nodeRadius(d) {
  const lobe = d.lobe;
  if (d.id === "Cortex_Central") return 16;
  if (d.id === "ThSyr" || d.id === "Operador") return 13;
  if (lobe === "cortex") return 11;
  const base = 7;
  const bonus = Math.min(5, Math.floor(d.degree / 8));
  return base + bonus;
}

// =====================================================================
// TICK
// =====================================================================
function ticked() {
  link
    .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
  node.attr("transform", d => `translate(${d.x},${d.y})`);
  drawMinimap();
}

// =====================================================================
// NODE EVENTS
// =====================================================================
function onNodeClick(e, d) {
  e.stopPropagation();
  highlightNode(d.id);
  openInspector(d);
}

function onNodeHover(e, d) {
  const tt = document.getElementById("tooltip");
  tt.style.display = "block";
  tt.textContent = `[${(LOBE_LABEL[d.lobe]||"??")}]  ${d.label}  (${d.degree})`;
  tt.style.left = (e.clientX + 14) + "px";
  tt.style.top  = (e.clientY - 10) + "px";
}

function onNodeOut() {
  document.getElementById("tooltip").style.display = "none";
}

svg.on("click", () => { closeInspector(); clearHighlight(); });

// =====================================================================
// HIGHLIGHT
// =====================================================================
function highlightNode(id) {
  highlightNodeId = id;
  const ndata = nodeMap[id];
  if (!ndata) return;
  const neighbourSet = new Set(ndata.neighbours);

  node.each(function(d) {
    const el = d3.select(this);
    const isTarget = (d.id === id);
    const isNeighbour = neighbourSet.has(d.id);
    el.classed("dimmed", !isTarget && !isNeighbour);
    el.classed("activated", isTarget);

    el.select(".node-circle")
      .transition().duration(250)
      .attr("r", isTarget ? nodeRadius(d) + 5 : nodeRadius(d))
      .attr("stroke-width", isTarget ? 3 : 2)
      .attr("stroke", isTarget ? "#ffffff" : "#070a0f")
      .attr("filter", isTarget ? "url(#glow-strong)" : (isNeighbour ? "url(#glow)" : null));

    el.select(".pulse-halo")
      .style("display", isTarget ? "block" : "none")
      .style("opacity", isTarget ? "0.8" : "0");
  });

  link.each(function(d) {
    const sId = typeof d.source==="object" ? d.source.id : d.source;
    const tId = typeof d.target==="object" ? d.target.id : d.target;
    const isConnected = (sId === id || tId === id);
    const isBetweenActive = (sId === id && neighbourSet.has(tId)) || (tId === id && neighbourSet.has(sId));
    d3.select(this)
      .classed("active-synapse", isBetweenActive)
      .classed("highlighted", isConnected && !isBetweenActive)
      .classed("dimmed", !isConnected);
  });

  // Update stats
  document.getElementById("stat-active-wrap").style.display = "flex";
  document.getElementById("stat-active").textContent = ndata.neighbours.length;
}

function clearHighlight() {
  highlightNodeId = null;
  node.classed("dimmed", false).classed("activated", false);
  node.select(".node-circle")
    .transition().duration(300)
    .attr("r", d => nodeRadius(d))
    .attr("stroke-width", 2)
    .attr("stroke","#070a0f")
    .attr("filter", null);
  node.select(".pulse-halo").style("display","none");
  link.classed("active-synapse",false).classed("highlighted",false).classed("dimmed",false);
  document.getElementById("stat-active-wrap").style.display = "none";
}

// =====================================================================
// INSPECTOR PANEL
// =====================================================================
function openInspector(d) {
  document.getElementById("inspector-title").textContent = d.label;
  const lobeColor = COLOR[d.lobe] || COLOR.conceito;
  document.getElementById("insp-lobe").innerHTML =
    `<span class="lobe-badge" style="background:${lobeColor}22;color:${lobeColor};border:1px solid ${lobeColor}55">${LOBE_LABEL[d.lobe]||d.lobe}</span>`;
  document.getElementById("insp-degree").textContent = d.degree;
  const pct = MAX_DEGREE > 0 ? Math.round((d.degree / MAX_DEGREE) * 100) : 0;
  document.getElementById("insp-degree-bar").style.width = pct + "%";
  document.getElementById("insp-degree-bar").style.background = lobeColor;
  document.getElementById("insp-path").textContent = d.path || "(sem arquivo mapeado)";

  const nl = document.getElementById("insp-neighbours");
  nl.innerHTML = "";
  document.getElementById("insp-neighbour-count").textContent = d.neighbours.length;
  d.neighbours.slice().sort((a,b) => {
    const da = (nodeMap[a]||{}).degree||0;
    const db = (nodeMap[b]||{}).degree||0;
    return db - da;
  }).forEach(nid => {
    const nn = nodeMap[nid];
    if (!nn) return;
    const nc = COLOR[nn.lobe] || COLOR.conceito;
    const item = document.createElement("div");
    item.className = "neighbour-item";
    item.innerHTML = `<span class="neighbour-dot" style="background:${nc}"></span><span>${nid.replace(/_/g," ")}</span>`;
    item.addEventListener("click", (e) => {
      e.stopPropagation();
      highlightNode(nid);
      openInspector(nn);
      focusNode(nn);
    });
    nl.appendChild(item);
  });

  document.getElementById("inspector").classList.add("open");
}

function closeInspector() {
  document.getElementById("inspector").classList.remove("open");
}
document.getElementById("inspector-close").addEventListener("click", (e) => {
  e.stopPropagation();
  closeInspector();
  clearHighlight();
});

// =====================================================================
// FOCUS / CAMERA
// =====================================================================
function focusNode(d, scale) {
  if (!d || d.x === undefined) return;
  const s = scale || 1.8;
  const tx = W()/2 - s * d.x;
  const ty = H()/2 - s * d.y;
  svg.transition().duration(700).call(
    zoom.transform,
    d3.zoomIdentity.translate(tx, ty).scale(s)
  );
}

function focusGroup(ids) {
  const pts = ids.map(id => nodeMap[id]).filter(n => n && n.x !== undefined);
  if (!pts.length) return;
  const xs = pts.map(n => n.x), ys = pts.map(n => n.y);
  const x0=Math.min(...xs), x1=Math.max(...xs), y0=Math.min(...ys), y1=Math.max(...ys);
  const cx=(x0+x1)/2, cy=(y0+y1)/2;
  const pad=60;
  const s = Math.min(W()/(x1-x0+pad), H()/(y1-y0+pad), 3) * 0.8;
  svg.transition().duration(750).call(
    zoom.transform,
    d3.zoomIdentity.translate(W()/2 - s*cx, H()/2 - s*cy).scale(s)
  );
}

// =====================================================================
// SEARCH
// =====================================================================
const searchInput = document.getElementById("search-input");
const autocomplete = document.getElementById("autocomplete");

let acData = GRAPH.nodes.map(n => ({id:n.id, label:n.label, lobe:n.lobe}));

searchInput.addEventListener("input", () => {
  const q = searchInput.value.trim().toLowerCase();
  searchQuery = q;
  acIndex = -1;
  if (!q) { autocomplete.style.display="none"; return; }
  const results = acData.filter(n =>
    n.id.toLowerCase().includes(q) || n.label.toLowerCase().includes(q)
  ).slice(0, 14);
  if (!results.length) { autocomplete.style.display="none"; return; }
  autocomplete.innerHTML = "";
  autocomplete.style.display = "block";
  results.forEach((n, i) => {
    const c = COLOR[n.lobe] || COLOR.conceito;
    const item = document.createElement("div");
    item.className = "ac-item";
    item.dataset.index = i;
    item.innerHTML = `<span class="ac-lobe" style="background:${c}22;color:${c}">${LOBE_LABEL[n.lobe]||"??"}</span><span class="ac-label">${n.label}</span>`;
    item.addEventListener("mousedown", (e) => { e.preventDefault(); selectSearchItem(n); });
    autocomplete.appendChild(item);
  });
  autocomplete._results = results;
});

searchInput.addEventListener("keydown", (e) => {
  const items = autocomplete.querySelectorAll(".ac-item");
  if (e.key === "ArrowDown") {
    e.preventDefault();
    acIndex = Math.min(acIndex+1, items.length-1);
    items.forEach((el,i) => el.classList.toggle("selected", i===acIndex));
  } else if (e.key === "ArrowUp") {
    e.preventDefault();
    acIndex = Math.max(acIndex-1, 0);
    items.forEach((el,i) => el.classList.toggle("selected", i===acIndex));
  } else if (e.key === "Enter") {
    if (acIndex >= 0 && autocomplete._results) {
      selectSearchItem(autocomplete._results[acIndex]);
    } else if (autocomplete._results && autocomplete._results.length) {
      selectSearchItem(autocomplete._results[0]);
    }
  } else if (e.key === "Escape") {
    autocomplete.style.display = "none";
  }
});

searchInput.addEventListener("blur", () => {
  setTimeout(() => { autocomplete.style.display = "none"; }, 150);
});

function selectSearchItem(n) {
  searchInput.value = n.label;
  autocomplete.style.display = "none";
  const nd = nodeMap[n.id];
  if (!nd) return;
  highlightNode(n.id);
  openInspector(nd);
  // wait for sim to place node
  setTimeout(() => focusNode(nd), 80);
  updateHUDEvent(`Busca: ${n.label}`);
}

// =====================================================================
// LOBE FILTER PILLS
// =====================================================================
document.querySelectorAll(".lobe-pill").forEach(pill => {
  pill.addEventListener("click", () => {
    const lobe = pill.dataset.lobe;
    if (lobe === "all") {
      const allActive = [...activeLobes].length >= 6;
      if (allActive) {
        activeLobes.clear();
        document.querySelectorAll(".lobe-pill:not([data-lobe='all'])").forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
      } else {
        activeLobes = new Set(["cortex","frontal","parietal","temporal","occipital","limbico","operador","projeto","conceito"]);
        document.querySelectorAll(".lobe-pill").forEach(p => p.classList.add("active"));
      }
    } else {
      if (activeLobes.has(lobe)) {
        activeLobes.delete(lobe);
        pill.classList.remove("active");
        pill.classList.add("inactive");
      } else {
        activeLobes.add(lobe);
        pill.classList.add("active");
        pill.classList.remove("inactive");
      }
      const allPill = document.querySelector(".lobe-pill[data-lobe='all']");
      const allActive = [...activeLobes].length >= 6;
      allPill.classList.toggle("active", allActive);
    }
    applyLobeFilter();
  });
});

function applyLobeFilter() {
  node.each(function(d) {
    const visible = activeLobes.has(d.lobe) || activeLobes.size === 0;
    d3.select(this).style("display", visible ? null : "none");
  });
  link.each(function(d) {
    const sId = typeof d.source==="object" ? d.source.id : d.source;
    const tId = typeof d.target==="object" ? d.target.id : d.target;
    const sn = nodeMap[sId], tn = nodeMap[tId];
    const visible = sn && tn && activeLobes.has(sn.lobe) && activeLobes.has(tn.lobe);
    d3.select(this).style("display", visible ? null : "none");
  });

  const visibleCount = GRAPH.nodes.filter(n => activeLobes.has(n.lobe)).length;
  document.getElementById("stat-nodes").textContent = visibleCount;
}

// =====================================================================
// HUD
// =====================================================================
document.getElementById("hud-header").addEventListener("click", () => {
  hudCollapsed = !hudCollapsed;
  const hud = document.getElementById("hud");
  hud.classList.toggle("collapsed", hudCollapsed);
  document.getElementById("hud-toggle-btn").textContent = hudCollapsed ? "[expandir]" : "[recolher]";
});

function updateHUDEvent(text) {
  const badge = document.getElementById("pulse-badge");
  badge.classList.add("active");
  document.getElementById("pulse-text").textContent = "ATIVO";
  document.getElementById("hud-query-text").textContent = text;
  document.getElementById("hud-time").textContent = new Date().toLocaleTimeString("pt-BR");
  if (decayTimer) clearTimeout(decayTimer);
  decayTimer = setTimeout(() => {
    badge.classList.remove("active");
    document.getElementById("pulse-text").textContent = "REPOUSO";
  }, 20000);
}

// Pulse Demo
document.getElementById("btn-pulse-demo").addEventListener("click", () => {
  const demoIds = ["Cortex_Central","Anti_Sicofancia","ThSyr","Operador","Decisoes_Arquitetura"];
  updateHUDEvent("Simulacao: Qual o protocolo de decisoes arquiteturais do Copiloto?");
  demoIds.forEach(id => {
    const nd = nodeMap[id];
    if (!nd) return;
  });
  focusGroup(demoIds.filter(id => nodeMap[id]));
  // light up all demo nodes
  node.each(function(d) {
    const isDemo = demoIds.includes(d.id);
    d3.select(this).classed("dimmed", !isDemo);
    d3.select(this).classed("activated", isDemo);
    d3.select(this).select(".node-circle")
      .transition().duration(400)
      .attr("r", isDemo ? nodeRadius(d)+5 : nodeRadius(d))
      .attr("filter", isDemo ? "url(#glow)" : null)
      .attr("stroke", isDemo ? "#fff" : "#070a0f");
    d3.select(this).select(".pulse-halo")
      .style("display", isDemo ? "block" : "none");
  });
  const demoSet = new Set(demoIds);
  link.each(function(d) {
    const sId = typeof d.source==="object"?d.source.id:d.source;
    const tId = typeof d.target==="object"?d.target.id:d.target;
    const active = demoSet.has(sId) && demoSet.has(tId);
    const semi = demoSet.has(sId)||demoSet.has(tId);
    d3.select(this).classed("active-synapse",active).classed("dimmed",!semi);
  });
});

// Reset
document.getElementById("btn-reset").addEventListener("click", resetView);
function resetView() {
  clearHighlight();
  closeInspector();
  searchInput.value = "";
  svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
  document.getElementById("stat-nodes").textContent = GRAPH.nodes.length;
  document.getElementById("stat-active-wrap").style.display = "none";
}

// =====================================================================
// PHYSICS CONTROLS
// =====================================================================
document.getElementById("physics-toggle").addEventListener("click", () => {
  physicsOpen = !physicsOpen;
  document.getElementById("physics-panel").classList.toggle("open", physicsOpen);
  document.getElementById("physics-toggle").textContent = physicsOpen ? "[FISICA ON]" : "[FISICA]";
});

function bindSlider(id, fn, valId) {
  const el = document.getElementById(id);
  el.addEventListener("input", () => {
    document.getElementById(valId).textContent = el.value;
    fn(+el.value);
    simulation.alpha(0.4).restart();
  });
}
bindSlider("sl-charge", v => simulation.force("charge", d3.forceManyBody().strength(v)), "sl-charge-val");
bindSlider("sl-link",   v => simulation.force("link", d3.forceLink(GRAPH.edges).id(d=>d.id).distance(v)), "sl-link-val");
bindSlider("sl-coll",   v => simulation.force("collision", d3.forceCollide().radius(v)), "sl-coll-val");
bindSlider("sl-alpha",  v => simulation.alphaDecay(v/1000), "sl-alpha-val");

// =====================================================================
// MINIMAP
// =====================================================================
const mmCanvas = document.getElementById("minimap");
const mmCtx = mmCanvas.getContext("2d");

function drawMinimap() {
  const mw = mmCanvas.width, mh = mmCanvas.height;
  mmCtx.clearRect(0, 0, mw, mh);
  mmCtx.fillStyle = "rgba(7,10,15,0.0)";
  mmCtx.fillRect(0,0,mw,mh);

  const visNodes = GRAPH.nodes.filter(n => n.x !== undefined && activeLobes.has(n.lobe));
  if (!visNodes.length) return;

  const xs = visNodes.map(n=>n.x), ys = visNodes.map(n=>n.y);
  const x0=Math.min(...xs)-40, x1=Math.max(...xs)+40;
  const y0=Math.min(...ys)-40, y1=Math.max(...ys)+40;
  const gw=x1-x0||1, gh=y1-y0||1;
  const scale = Math.min(mw/gw, mh/gh);
  const ox = (mw - gw*scale)/2, oy = (mh - gh*scale)/2;

  // Draw links
  mmCtx.lineWidth = 0.5;
  mmCtx.strokeStyle = "rgba(33,38,45,0.8)";
  mmCtx.beginPath();
  GRAPH.edges.forEach(e => {
    const s = e.source, t = e.target;
    const sx = typeof s==="object"?s.x:nodeMap[s]?.x;
    const sy = typeof s==="object"?s.y:nodeMap[s]?.y;
    const tx = typeof t==="object"?t.x:nodeMap[t]?.x;
    const ty = typeof t==="object"?t.y:nodeMap[t]?.y;
    if (sx===undefined||tx===undefined) return;
    mmCtx.moveTo(ox+(sx-x0)*scale, oy+(sy-y0)*scale);
    mmCtx.lineTo(ox+(tx-x0)*scale, oy+(ty-y0)*scale);
  });
  mmCtx.stroke();

  // Draw nodes
  visNodes.forEach(n => {
    const px = ox+(n.x-x0)*scale, py = oy+(n.y-y0)*scale;
    const r = Math.max(1.2, nodeRadius(n)*0.22);
    mmCtx.beginPath();
    mmCtx.arc(px,py,r,0,Math.PI*2);
    mmCtx.fillStyle = COLOR[n.lobe] || COLOR.conceito;
    mmCtx.fill();
  });

  // Draw viewport rect
  const t = currentTransform;
  const vx = (-t.x)/t.k, vy = (-t.y)/t.k;
  const vw = W()/t.k, vh = H()/t.k;
  const rx = ox+(vx-x0)*scale, ry = oy+(vy-y0)*scale;
  const rw = vw*scale, rh = vh*scale;
  mmCtx.strokeStyle = "rgba(88,166,255,0.6)";
  mmCtx.lineWidth = 1;
  mmCtx.strokeRect(rx,ry,rw,rh);
}

// Click minimap to navigate
mmCanvas.addEventListener("click", (e) => {
  const rect = mmCanvas.getBoundingClientRect();
  const mx = (e.clientX - rect.left), my = (e.clientY - rect.top);
  const mw = mmCanvas.width, mh = mmCanvas.height;
  const visNodes = GRAPH.nodes.filter(n => n.x !== undefined && activeLobes.has(n.lobe));
  if (!visNodes.length) return;
  const xs = visNodes.map(n=>n.x), ys = visNodes.map(n=>n.y);
  const x0=Math.min(...xs)-40, x1=Math.max(...xs)+40;
  const y0=Math.min(...ys)-40, y1=Math.max(...ys)+40;
  const gw=x1-x0||1, gh=y1-y0||1;
  const scale = Math.min(mw/gw, mh/gh);
  const ox=(mw-gw*scale)/2, oy=(mh-gh*scale)/2;
  const gx = (mx-ox)/scale + x0;
  const gy = (my-oy)/scale + y0;
  const k = currentTransform.k;
  svg.transition().duration(450).call(
    zoom.transform,
    d3.zoomIdentity.translate(W()/2 - k*gx, H()/2 - k*gy).scale(k)
  );
});

// =====================================================================
// KEYBOARD SHORTCUTS
// =====================================================================
document.addEventListener("keydown", (e) => {
  if (e.target.tagName === "INPUT") return;
  if (e.key === "Escape") { resetView(); }
  if (e.key === "f" || e.key === "F") { searchInput.focus(); e.preventDefault(); }
});

// =====================================================================
// RESIZE
// =====================================================================
window.addEventListener("resize", () => {
  simulation.force("center", d3.forceCenter(W()/2, H()/2));
  drawMinimap();
});

// =====================================================================
// LIVE PULSE WATCHER (file:// + HTTP fallback)
// =====================================================================
let _lastPulseId = null;
function pollPulse() {
  const old = document.getElementById("dyn-pulse");
  if (old) old.remove();
  const s = document.createElement("script");
  s.id = "dyn-pulse";
  s.src = "active_synapses.js?_t=" + Date.now();
  s.onload = () => {
    if (window.__THSYR_PULSE__ && window.__THSYR_PULSE__.id !== _lastPulseId) {
      _lastPulseId = window.__THSYR_PULSE__.id;
      const p = window.__THSYR_PULSE__;
      updateHUDEvent(p.query || "Pulso externo recebido");
      if (p.top_activated && p.top_activated.length) {
        const ids = p.top_activated.map(i => i.id);
        focusGroup(ids.filter(id => nodeMap[id]));
        const actSet = new Set(ids);
        node.each(function(d) {
          const act = actSet.has(d.id);
          d3.select(this).classed("dimmed",!act).classed("activated",act);
          d3.select(this).select(".node-circle")
            .transition().duration(400)
            .attr("r", act ? nodeRadius(d)+4 : nodeRadius(d))
            .attr("filter", act ? "url(#glow)" : null)
            .attr("stroke", act ? "#fff" : "#070a0f");
          d3.select(this).select(".pulse-halo").style("display", act?"block":"none");
        });
        link.each(function(d) {
          const sId = typeof d.source==="object"?d.source.id:d.source;
          const tId = typeof d.target==="object"?d.target.id:d.target;
          const a = actSet.has(sId) && actSet.has(tId);
          const semi = actSet.has(sId) || actSet.has(tId);
          d3.select(this).classed("active-synapse",a).classed("dimmed",!semi);
        });
      }
    }
  };
  s.onerror = () => {
    fetch("../state/active_synapses.json?_t=" + Date.now())
      .then(r => r.json()).then(p => {
        if (p && p.id !== _lastPulseId) {
          _lastPulseId = p.id;
          updateHUDEvent(p.query || "Pulso externo");
        }
      }).catch(()=>{});
  };
  document.head.appendChild(s);
}
setInterval(pollPulse, 1500);
pollPulse();

// =====================================================================
// INIT: center on Cortex_Central
// =====================================================================
simulation.on("end", () => {
  const cc = nodeMap["Cortex_Central"];
  if (cc && cc.x !== undefined) {
    const s = 1.2;
    svg.call(zoom.transform, d3.zoomIdentity
      .translate(W()/2 - s*cc.x, H()/2 - s*cc.y).scale(s));
  }
  drawMinimap();
});

</script>
</body>
</html>
"""


if __name__ == "__main__":
    p = generate()
    print(f"Canvas gerado: {p}")
