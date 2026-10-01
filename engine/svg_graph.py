"""
ThSyr SVG Neural Graph Generator - Edicao Anatomica Cerebral
Renderiza a mente do ThSyr distribuida espacialmente pelos 5 Lobos Cerebrais
sobre a silhueta anatomica do cortex humano, com pesos sinapticos Hebbianos ativos.
"""

import math
import random
from pathlib import Path
from typing import Any, Optional

from .config import settings

PROJECT_ROOT = settings.project_root
BRAIN_DIR = settings.brain.brain_dir
ASSETS_DIR = PROJECT_ROOT / "assets"
SVG_OUTPUT = ASSETS_DIR / "brain_graph.svg"
GRAPH_FILE = BRAIN_DIR / "knowledge_graph.json"

COLOR_MAP = {
    "cortex": "#ff3366",       # Tronco / Nucleo
    "operador": "#58a6ff",     # Consciencia do Operador
    "frontal": "#ff7b72",      # Planejamento & Decisao
    "parietal": "#79c0ff",     # Motor & Engenharia
    "temporal": "#bc8cff",     # Hipocampo & Memoria
    "occipital": "#d29922",    # Cortex Visual & Design
    "limbico": "#3fb950",      # Valores & Vida Pessoal
    "conceito": "#8b949e",
}

# Centros de gravidade anatomicos para cada lobo no plano 1200x800
LOBE_CENTERS = {
    "frontal": (360.0, 310.0),    # Anterior / Superior
    "parietal": (660.0, 240.0),   # Superior / Dorsal
    "occipital": (940.0, 390.0),  # Posterior / Caudal
    "temporal": (580.0, 520.0),   # Inferior / Ventral
    "limbico": (600.0, 380.0),    # Interior Profundo
    "cortex": (600.0, 430.0),     # Tronco / Centro
    "operador": (420.0, 420.0),   # Consciencia
    "conceito": (600.0, 380.0)
}


def simulate_anatomical_forces(nodes: list[dict[str, Any]], links: list[dict[str, Any]], width: int = 1200, height: int = 800, iterations: int = 280) -> dict[str, tuple]:
    random.seed(42)
    pos = {}

    for n in nodes:
        group = n.get("group", "conceito")
        cx, cy = LOBE_CENTERS.get(group, (600.0, 400.0))
        pos[n["id"]] = [
            cx + random.uniform(-45.0, 45.0),
            cy + random.uniform(-45.0, 45.0)
        ]

    k_repulsion = 90000.0
    k_spring = 0.045
    spring_length = 95.0
    damping = 0.86

    velocities = {n["id"]: [0.0, 0.0] for n in nodes}

    for step in range(iterations):
        forces = {n["id"]: [0.0, 0.0] for n in nodes}

        # 1. Repulsao entre todos os pares
        for i in range(len(nodes)):
            id_a = nodes[i]["id"]
            pos_a = pos[id_a]
            for j in range(i + 1, len(nodes)):
                id_b = nodes[j]["id"]
                pos_b = pos[id_b]

                dx = pos_a[0] - pos_b[0]
                dy = pos_a[1] - pos_b[1]
                dist_sq = dx * dx + dy * dy + 80.0
                dist = math.sqrt(dist_sq)

                rep_force = k_repulsion / dist_sq
                fx = (dx / dist) * rep_force
                fy = (dy / dist) * rep_force

                forces[id_a][0] += fx
                forces[id_a][1] += fy
                forces[id_b][0] -= fx
                forces[id_b][1] -= fy

        # 2. Atracao elastica pelas sinapses
        for link in links:
            src = link["source"]
            tgt = link["target"]
            if src not in pos or tgt not in pos:
                continue

            pos_src = pos[src]
            pos_tgt = pos[tgt]

            dx = pos_tgt[0] - pos_src[0]
            dy = pos_tgt[1] - pos_src[1]
            dist = math.sqrt(dx * dx + dy * dy) + 0.1
            displacement = dist - spring_length

            spring_force = k_spring * displacement
            fx = (dx / dist) * spring_force
            fy = (dy / dist) * spring_force

            forces[src][0] += fx
            forces[src][1] += fy
            forces[tgt][0] -= fx
            forces[tgt][1] -= fy

        # 3. Gravidade anatomica em direcao ao centro do lobo
        decay = (1.0 - step / iterations)
        for n in nodes:
            nid = n["id"]
            group = n.get("group", "conceito")
            target_cx, target_cy = LOBE_CENTERS.get(group, (600.0, 400.0))

            forces[nid][0] += (target_cx - pos[nid][0]) * 0.035
            forces[nid][1] += (target_cy - pos[nid][1]) * 0.035

            vx = (velocities[nid][0] + forces[nid][0] * 0.08) * damping * decay
            vy = (velocities[nid][1] + forces[nid][1] * 0.08) * damping * decay
            velocities[nid] = [vx, vy]

            pos[nid][0] += vx
            pos[nid][1] += vy

            pos[nid][0] = max(70, min(width - 70, pos[nid][0]))
            pos[nid][1] = max(70, min(height - 70, pos[nid][1]))

    return {k: (v[0], v[1]) for k, v in pos.items()}


def generate_anatomical_svg(data: dict[str, Any], positions: dict[str, tuple], width: int = 1200, height: int = 800) -> str:
    nodes = data["nodes"]
    links = data["links"]

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" style="background-color:#090d13; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, monospace;">',
        '<defs>',
        '  <!-- Gradientes de Lobos Cerebrais -->',
        '  <radialGradient id="frontalGlow" cx="30%" cy="40%" r="40%">',
        '    <stop offset="0%" stop-color="#ff7b72" stop-opacity="0.12"/>',
        '    <stop offset="100%" stop-color="#090d13" stop-opacity="0"/>',
        '  </radialGradient>',
        '  <radialGradient id="parietalGlow" cx="55%" cy="30%" r="40%">',
        '    <stop offset="0%" stop-color="#79c0ff" stop-opacity="0.10"/>',
        '    <stop offset="100%" stop-color="#090d13" stop-opacity="0"/>',
        '  </radialGradient>',
        '  <radialGradient id="occipitalGlow" cx="80%" cy="50%" r="35%">',
        '    <stop offset="0%" stop-color="#d29922" stop-opacity="0.10"/>',
        '    <stop offset="100%" stop-color="#090d13" stop-opacity="0"/>',
        '  </radialGradient>',
        '  <radialGradient id="limbicGlow" cx="50%" cy="50%" r="40%">',
        '    <stop offset="0%" stop-color="#3fb950" stop-opacity="0.12"/>',
        '    <stop offset="100%" stop-color="#090d13" stop-opacity="0"/>',
        '  </radialGradient>',
        '  <filter id="cortexGlow" x="-50%" y="-50%" width="200%" height="200%">',
        '    <feGaussianBlur stdDeviation="4" result="blur"/>',
        '    <feMerge>',
        '      <feMergeNode in="blur"/>',
        '      <feMergeNode in="SourceGraphic"/>',
        '    </feMerge>',
        '  </filter>',
        '</defs>',
        f'<rect width="{width}" height="{height}" fill="#090d13"/>',
        '<!-- Halos de Lobos Cerebrais -->',
        '<circle cx="360" cy="310" r="280" fill="url(#frontalGlow)"/>',
        '<circle cx="660" cy="240" r="280" fill="url(#parietalGlow)"/>',
        '<circle cx="940" cy="390" r="260" fill="url(#occipitalGlow)"/>',
        '<circle cx="600" cy="400" r="240" fill="url(#limbicGlow)"/>',
        '<!-- Silhueta Anatomica do Cortex Humano (Vista Sagital Estilizada) -->',
        '<path d="M 230 420 C 190 320 250 180 400 130 C 530 90 750 90 880 150 C 1010 210 1080 320 1060 450 C 1040 560 960 620 880 620 C 820 620 780 570 730 570 C 670 570 650 690 580 690 C 510 690 490 580 430 570 C 350 560 260 520 230 420 Z" fill="none" stroke="#21262d" stroke-width="1.8" stroke-dasharray="6 6" opacity="0.65"/>',
        '<!-- Rotulos Anatomicos Sutis -->',
        '<text x="260" y="160" fill="#ff7b72" font-size="11" font-weight="700" letter-spacing="1" opacity="0.45">LOBO FRONTAL</text>',
        '<text x="640" y="125" fill="#79c0ff" font-size="11" font-weight="700" letter-spacing="1" opacity="0.45">LOBO PARIETAL</text>',
        '<text x="960" y="320" fill="#d29922" font-size="11" font-weight="700" letter-spacing="1" opacity="0.45">LOBO OCCIPITAL</text>',
        '<text x="500" y="650" fill="#bc8cff" font-size="11" font-weight="700" letter-spacing="1" opacity="0.45">LOBO TEMPORAL</text>',
        '<text x="545" y="375" fill="#3fb950" font-size="10" font-weight="700" letter-spacing="1" opacity="0.45">SISTEMA LIMBICO</text>',
        '<!-- Sinapses Neurais -->',
        '<g stroke="#30363d" stroke-width="1.2" stroke-opacity="0.55">'
    ]

    for link in links:
        src = link["source"]
        tgt = link["target"]
        if src in positions and tgt in positions:
            x1, y1 = positions[src]
            x2, y2 = positions[tgt]
            svg_parts.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" />')

    svg_parts.append('</g>')
    svg_parts.append('<!-- Neurônios -->')
    svg_parts.append('<g>')

    for n in nodes:
        nid = n["id"]
        if nid not in positions:
            continue
        x, y = positions[nid]
        group = n.get("group", "conceito")
        color = COLOR_MAP.get(group, "#8b949e")
        radius = 15 if group == "cortex" else (13 if group == "operador" else (10 if "lobo" in nid.lower() else 8))
        label = n.get("label", nid).replace("_", " ")

        if group in ("cortex", "operador") or "lobo" in nid.lower():
            svg_parts.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{radius + 4}" fill="{color}" opacity="0.25" filter="url(#cortexGlow)"/>')

        svg_parts.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{radius}" fill="{color}" stroke="#090d13" stroke-width="2"/>')
        svg_parts.append(f'  <text x="{x + radius + 5:.1f}" y="{y + 4:.1f}" fill="#c9d1d9" font-size="9.5" font-weight="500">{label}</text>')

    svg_parts.append('</g>')

    # Cabecalho
    svg_parts.append('<!-- Cabecalho -->')
    svg_parts.append('<g transform="translate(35, 45)">')
    svg_parts.append('  <text fill="#58a6ff" font-size="18" font-weight="700" letter-spacing="1.5">THSYR // ARQUITETURA COGNITIVA SAGITAL</text>')
    svg_parts.append(f'  <text y="22" fill="#8b949e" font-size="12">Mapeamento em 5 Lobos Cerebrais | {len(nodes)} Nos | {len(links)} Sinapses Ativas | Plasticidade Hebbiana</text>')
    svg_parts.append('</g>')

    # Legenda dos Lobos
    svg_parts.append('<!-- Legenda -->')
    svg_parts.append(f'<g transform="translate(35, {height - 135})">')
    svg_parts.append('  <rect width="320" height="110" rx="6" fill="#161b22" fill-opacity="0.90" stroke="#30363d"/>')
    svg_parts.append('  <text x="14" y="20" fill="#8b949e" font-size="10" font-weight="600" letter-spacing="0.5">LOBOS CEREBRAIS E FUNCOES</text>')

    legend_items = [
        ("Cortex Central", "#ff3366"),
        ("Consciencia Operador", "#58a6ff"),
        ("Frontal (Decisao & Leis)", "#ff7b72"),
        ("Parietal (Engenharia & Stacks)", "#79c0ff"),
        ("Temporal (Hipocampo & Sessoes)", "#bc8cff"),
        ("Occipital (Design & Cores)", "#d29922"),
        ("Limbico (Valores & Vida)", "#3fb950"),
    ]

    for idx, (lbl, col) in enumerate(legend_items):
        col_idx = idx % 2
        row_idx = idx // 2
        lx = 14 + col_idx * 155
        ly = 38 + row_idx * 17
        svg_parts.append(f'  <circle cx="{lx}" cy="{ly}" r="4" fill="{col}"/>')
        svg_parts.append(f'  <text x="{lx + 10}" y="{ly + 3}" fill="#c9d1d9" font-size="9">{lbl}</text>')

    svg_parts.append('</g>')
    svg_parts.append('</svg>')

    return "\n".join(svg_parts)


def classify_node_group(node_id: str, _content: str, file_path: Path) -> str:
    nid = node_id.lower()
    fp = str(file_path).lower()

    if "cortex_central" in nid:
        return "cortex"
    if "operador" in nid:
        return "operador"
    if "frontal" in fp or "anti_sicofancia" in nid or "emoji" in nid or "sincronizacao" in nid:
        return "frontal"
    if "parietal" in fp or "stack" in nid or "engenharia" in nid or "atlas" in nid:
        return "parietal"
    if "temporal" in fp or "sessao" in nid or "crm" in nid or "episodic" in fp:
        return "temporal"
    if "occipital" in fp or "design" in nid or "copywriting" in nid or "visual" in nid:
        return "occipital"
    if "limbico" in fp or "valores" in nid or "restricoes" in nid or "estilo" in nid:
        return "limbico"
    return "conceito"


def render_svg_graph(output_path: Optional[Path] = None) -> Path:
    from engine.neural_graph import extract_graph_data
    data = extract_graph_data(BRAIN_DIR)

    # Reclassificar grupos com base na anatomia dos lobos
    for n in data["nodes"]:
        file_path = PROJECT_ROOT / n.get("path", "")
        content = file_path.read_text(encoding="utf-8") if file_path.exists() and file_path.is_file() else ""
        n["group"] = classify_node_group(n["id"], content, file_path)

    positions = simulate_anatomical_forces(data["nodes"], data["links"], width=1200, height=800, iterations=280)
    svg_markup = generate_anatomical_svg(data, positions, width=1200, height=800)
    target = output_path or SVG_OUTPUT
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(svg_markup, encoding="utf-8")
    return target


if __name__ == "__main__":
    out = render_svg_graph()
    print(f"SVG anatomico gerado em: {out}")
