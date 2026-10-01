"""
ThSyr Code Graph 3D Holographic Visualizer (Graphify Paradigm).
Renderiza nós e arestas de codigo-fonte (Python, Java, SQL) em um canvas Three.js WebGL.
"""

from __future__ import annotations

import json
import math
import webbrowser
from pathlib import Path
from typing import Any

from .models import CodeGraph

CODE_CANVAS_3D_OUTPUT = Path("brain/code_canvas_3d.html")

COLOR_SCHEME = {
    "python": "#00d4ff",   # Ciano eletrico
    "java": "#ffb52e",     # Ouro ambar
    "sql": "#10b981",      # Esmeralda profundo
    "default": "#8b949e",
}

SYMBOL_RADIUS = {
    "module": 1.4,
    "class": 1.1,
    "interface": 1.0,
    "table": 1.3,
    "method": 0.65,
    "function": 0.65,
    "column": 0.45,
}


def _calculate_3d_coordinates(graph_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Calcula posicoes esfericas tridimensionais com base no idioma e no agrupamento."""
    nodes = graph_data.get("nodes", [])
    total = max(len(nodes), 1)

    lang_offsets = {
        "python": (-4.0, 0.0, 0.0),
        "java": (4.0, 0.0, 0.0),
        "sql": (0.0, -4.0, 0.0),
    }

    positioned_nodes = []
    for idx, node in enumerate(nodes):
        lang = node.get("language", "python").lower()
        stype = node.get("symbol_type", "function")
        center_x, center_y, center_z = lang_offsets.get(lang, (0.0, 0.0, 0.0))

        fraction = (idx + 0.5) / total
        longitude = idx * 2.3999632297  # Golden ratio
        latitude = math.acos(1 - 2 * fraction)

        base_radius = 4.5 + (idx % 5) * 0.45
        if stype in ("module", "table", "class"):
            base_radius += 0.8

        x = center_x + math.sin(latitude) * math.cos(longitude) * base_radius
        y = center_y + math.cos(latitude) * base_radius
        z = center_z + math.sin(latitude) * math.sin(longitude) * base_radius

        node_color = COLOR_SCHEME.get(lang, COLOR_SCHEME["default"])
        radius = SYMBOL_RADIUS.get(stype, 0.6)

        positioned_nodes.append({
            **node,
            "x": round(x, 3),
            "y": round(y, 3),
            "z": round(z, 3),
            "color": node_color,
            "radius": radius,
        })

    return positioned_nodes


HTML_CODE_CANVAS_TEMPLATE = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ThSyr // Code Graph 3D Canvas (Graphify)</title>
<style>
*{box-sizing:border-box}
html,body{margin:0;width:100%;height:100%;overflow:hidden;background:radial-gradient(circle at 50% 50%,#09121a 0%,#04070b 60%,#010305 100%);color:#dce8f5;font:12px "Geist","Segoe UI",sans-serif}
#scene{position:fixed;inset:0}
#hud{position:fixed;inset:20px;pointer-events:none;display:flex;justify-content:space-between}
.panel{pointer-events:auto;background:rgba(4,14,24,.75);border:1px solid rgba(0,212,255,.2);border-radius:12px;padding:14px;backdrop-filter:blur(16px);box-shadow:0 0 35px rgba(0,180,240,.08)}
.eyebrow{font-size:10px;letter-spacing:.22em;color:#00d4ff;text-transform:uppercase}
.title{font-size:16px;letter-spacing:.08em;margin:6px 0 12px;font-weight:600}
.metric{display:flex;justify-content:space-between;gap:24px;margin-top:6px;color:#7f94aa}
.metric b{color:#eef7ff;font-weight:500}
#inspector{min-width:280px;max-width:340px;align-self:flex-start;opacity:0;transform:translateY(-8px);transition:opacity .35s ease,transform .35s ease}
#inspector.visible{opacity:1;transform:translateY(0)}
#tools{position:fixed;left:20px;bottom:20px;width:280px}
#tools input{width:100%;background:rgba(2,9,16,.85);border:1px solid rgba(0,212,255,.25);border-radius:8px;color:#eef7ff;padding:8px 10px;outline:none}
#tools input:focus{border-color:#00d4ff}
.filters{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.filters button{padding:4px 8px;font-size:9px;background:rgba(0,212,255,.08);border:1px solid rgba(0,212,255,.25);color:#c5d8ea;border-radius:4px;cursor:pointer;text-transform:uppercase}
.filters button.active{background:rgba(0,212,255,.25);border-color:#00d4ff;color:#ffffff}
.connections{margin-top:10px;max-height:160px;overflow:auto;color:#91a6b8;font-size:11px;line-height:1.4}
.connections div{border-top:1px solid rgba(0,212,255,.1);padding:4px 0}
button.action-btn{background:rgba(0,212,255,.1);border:1px solid rgba(0,212,255,.4);color:#dce8f5;border-radius:6px;padding:6px 12px;cursor:pointer;letter-spacing:.06em;text-transform:uppercase;font-size:10px;margin-top:8px}
button.action-btn:hover{background:rgba(0,212,255,.25);color:#ffffff}
#status{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);color:#52697e;letter-spacing:.16em;font-size:10px;text-transform:uppercase}
.badge{display:inline-block;padding:2px 6px;border-radius:4px;font-size:9px;font-weight:600;text-transform:uppercase}
.badge-python{background:rgba(0,212,255,.2);color:#00d4ff;border:1px solid #00d4ff}
.badge-java{background:rgba(255,181,46,.2);color:#ffb52e;border:1px solid #ffb52e}
.badge-sql{background:rgba(16,185,129,.2);color:#10b981;border:1px solid #10b981}
</style>
</head>
<body>
<div id="scene"></div>
<div id="hud">
  <section class="panel">
    <div class="eyebrow">ThSyr // Code Graph Architecture</div>
    <div class="title">GRAPHIFY CORE 3D</div>
    <div class="metric"><span>Total Nós:</span><b id="nodes-count">0</b></div>
    <div class="metric"><span>Sinapses de Código:</span><b id="edges-count">0</b></div>
    <div class="metric"><span>Linguagens:</span><b id="lang-breakdown">PY / JA / SQL</b></div>
    <button class="action-btn" id="btn-recenter">Recentralizar</button>
  </section>

  <section id="inspector" class="panel">
    <div class="eyebrow">Símbolo Selecionado</div>
    <div class="title" id="node-name">—</div>
    <div class="metric"><span>Tipo:</span><b id="node-type">—</b></div>
    <div class="metric"><span>Linguagem:</span><b id="node-lang">—</b></div>
    <div class="metric"><span>Arquivo:</span><b id="node-file" style="font-size:10px;word-break:break-all;">—</b></div>
    <div class="metric"><span>Linha:</span><b id="node-line">—</b></div>
    <div class="connections" id="connections-list">Nenhum nó selecionado.</div>
  </section>
</div>

<section id="tools" class="panel">
  <div class="eyebrow">Filtro de Símbolos</div>
  <input id="search-input" placeholder="Buscar classe, método ou tabela..." autocomplete="off">
  <div class="filters">
    <button class="active" data-lang="all">Todos</button>
    <button data-lang="python">Python</button>
    <button data-lang="java">Java</button>
    <button data-lang="sql">SQL</button>
  </div>
</section>

<div id="status">Graphify Deterministic AST Engine // Operational</div>

<script src="../assets/three.min.js"></script>
<script src="../assets/OrbitControls.js"></script>
<script>
// Fallback para CDN caso assets locais nao sejam acessiveis
if (typeof THREE === "undefined") {
  document.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"><\\/script>');
}
</script>
<script>
const RAW_GRAPH = __GRAPH_DATA__;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 10, 36);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setClearColor(0x02060a, 1);
document.getElementById("scene").appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.maxDistance = 120;
controls.minDistance = 5;

// Iluminacao
scene.add(new THREE.AmbientLight(0x406080, 0.8));
const pointLight = new THREE.PointLight(0x00d4ff, 2.5, 80);
pointLight.position.set(10, 20, 20);
scene.add(pointLight);

const group = new THREE.Group();
scene.add(group);

const nodesMap = new Map();
const nodeMeshes = [];
const edgeLines = [];

document.getElementById("nodes-count").textContent = RAW_GRAPH.nodes.length;
document.getElementById("edges-count").textContent = RAW_GRAPH.edges.length;

// Criar malha dos nós
const sphereGeo = new THREE.SphereGeometry(1, 16, 16);
RAW_GRAPH.nodes.forEach(n => {
  nodesMap.set(n.id, n);
  const colorHex = parseInt(n.color.replace("#", "0x"));
  const mat = new THREE.MeshStandardMaterial({
    color: colorHex,
    roughness: 0.3,
    metalness: 0.8,
    emissive: colorHex,
    emissiveIntensity: 0.25
  });
  const mesh = new THREE.Mesh(sphereGeo, mat);
  mesh.scale.setScalar(n.radius || 0.7);
  mesh.position.set(n.x, n.y, n.z);
  mesh.userData = n;
  group.add(mesh);
  nodeMeshes.push(mesh);
});

// Criar arestas
const lineMaterial = new THREE.LineBasicMaterial({
  color: 0x00a8d6,
  transparent: true,
  opacity: 0.25
});

RAW_GRAPH.edges.forEach(e => {
  const src = nodesMap.get(e.source_id);
  const tgt = nodesMap.get(e.target_id);
  if (src && tgt) {
    const points = [
      new THREE.Vector3(src.x, src.y, src.z),
      new THREE.Vector3(tgt.x, tgt.y, tgt.z)
    ];
    const geom = new THREE.BufferGeometry().setFromPoints(points);
    const line = new THREE.Line(geom, lineMaterial);
    line.userData = e;
    group.add(line);
    edgeLines.push(line);
  }
});

// Raycasting e Selecao
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let selectedMesh = null;

window.addEventListener("pointermove", (e) => {
  mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
});

window.addEventListener("click", () => {
  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(nodeMeshes);
  if (intersects.length > 0) {
    selectNode(intersects[0].object);
  }
});

function selectNode(mesh) {
  if (selectedMesh) {
    selectedMesh.material.emissiveIntensity = 0.25;
  }
  selectedMesh = mesh;
  selectedMesh.material.emissiveIntensity = 0.95;

  const data = mesh.userData;
  const inspector = document.getElementById("inspector");
  inspector.classList.add("visible");

  document.getElementById("node-name").textContent = data.name;
  document.getElementById("node-type").textContent = data.symbol_type.toUpperCase();
  document.getElementById("node-lang").textContent = data.language.toUpperCase();
  document.getElementById("node-file").textContent = data.filepath;
  document.getElementById("node-line").textContent = data.line_number || "—";

  // Buscar conexoes
  const outRels = RAW_GRAPH.edges.filter(e => e.source_id === data.id);
  const inRels = RAW_GRAPH.edges.filter(e => e.target_id === data.id);

  let html = `<b>Relações de Saída (${outRels.length}):</b><br>`;
  outRels.forEach(r => {
    html += `<div>&rarr; [${r.rel_type}] ${r.target_id.split(':').pop()}</div>`;
  });

  html += `<br><b>Relações de Entrada (${inRels.length}):</b><br>`;
  inRels.forEach(r => {
    html += `<div>&larr; [${r.rel_type}] ${r.source_id.split(':').pop()}</div>`;
  });

  document.getElementById("connections-list").innerHTML = html;
}

// Filtros de busca e linguagem
let activeLang = "all";
const searchInput = document.getElementById("search-input");

searchInput.addEventListener("input", applyFilters);

document.querySelectorAll(".filters button").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".filters button").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    activeLang = btn.dataset.lang;
    applyFilters();
  });
});

function applyFilters() {
  const query = searchInput.value.toLowerCase().trim();
  nodeMeshes.forEach(mesh => {
    const d = mesh.userData;
    const matchLang = activeLang === "all" || d.language.toLowerCase() === activeLang;
    const matchQuery = !query || d.name.toLowerCase().includes(query) || d.id.toLowerCase().includes(query);
    const visible = matchLang && matchQuery;
    mesh.visible = visible;
  });
}

document.getElementById("btn-recenter").addEventListener("click", () => {
  camera.position.set(0, 10, 36);
  controls.target.set(0, 0, 0);
  controls.update();
});

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// Loop de Animacao
function animate() {
  requestAnimationFrame(animate);
  group.rotation.y += 0.0008;
  controls.update();
  renderer.render(scene, camera);
}
animate();
</script>
</body>
</html>
"""


def render_code_graph_3d(
    graph: CodeGraph,
    output_path: Path | str = CODE_CANVAS_3D_OUTPUT,
    open_browser: bool = False,
) -> Path:
    """Gera o arquivo HTML com canvas 3D do CodeGraph e abre opcionalmente no navegador."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    raw_data = graph.to_dict()
    positioned_nodes = _calculate_3d_coordinates(raw_data)

    payload = {
        "nodes": positioned_nodes,
        "edges": raw_data["edges"],
        "summary": raw_data["summary"],
    }

    html = HTML_CODE_CANVAS_TEMPLATE.replace("__GRAPH_DATA__", json.dumps(payload, ensure_ascii=False))
    out.write_text(html, encoding="utf-8")

    if open_browser:
        webbrowser.open(out.resolve().as_uri())

    return out
