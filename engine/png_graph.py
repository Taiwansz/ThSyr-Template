"""
ThSyr PNG Neural Graph Generator
Renderiza a mente do ThSyr distribuida pelos 5 Lobos Cerebrais em formato PNG nativo,
utilizando geracao raster pura em Python com zlib, sem dependencia de bibliotecas C ou externas.
"""

import math
import struct
import zlib
from pathlib import Path

from .config import settings, setup_logger
from .neural_graph import extract_graph_data
from .svg_graph import simulate_anatomical_forces

logger = setup_logger("png_graph")

ASSETS_DIR = settings.project_root / "assets"
PNG_OUTPUT = ASSETS_DIR / "brain_graph.png"

HEX_COLORS = {
    "cortex": (255, 51, 102),       # #ff3366
    "operador": (88, 166, 255),     # #58a6ff
    "frontal": (255, 123, 114),     # #ff7b72
    "parietal": (121, 192, 255),    # #79c0ff
    "temporal": (188, 140, 255),    # #bc8cff
    "occipital": (210, 153, 34),    # #d29922
    "limbico": (63, 185, 80),       # #3fb950
    "conceito": (139, 148, 158),    # #8b949e
}


class RasterCanvas:
    def __init__(self, width: int = 1200, height: int = 800, bg_color: tuple[int, int, int] = (11, 15, 25)):
        self.width = width
        self.height = height
        self.buffer = bytearray(bg_color[0:3] * (width * height))

    def set_pixel(self, x: int, y: int, color: tuple[int, int, int], alpha: float = 1.0):
        if 0 <= x < self.width and 0 <= y < self.height:
            idx = (y * self.width + x) * 3
            if alpha >= 1.0:
                self.buffer[idx] = color[0]
                self.buffer[idx + 1] = color[1]
                self.buffer[idx + 2] = color[2]
            else:
                inv = 1.0 - alpha
                self.buffer[idx] = int(self.buffer[idx] * inv + color[0] * alpha)
                self.buffer[idx + 1] = int(self.buffer[idx + 1] * inv + color[1] * alpha)
                self.buffer[idx + 2] = int(self.buffer[idx + 2] * inv + color[2] * alpha)

    def draw_line(self, x0: float, y0: float, x1: float, y1: float, color: tuple[int, int, int], alpha: float = 0.4):
        dx = x1 - x0
        dy = y1 - y0
        dist = math.hypot(dx, dy)
        if dist == 0:
            self.set_pixel(int(x0), int(y0), color, alpha)
            return

        steps = int(dist * 1.5)
        for s in range(steps + 1):
            t = s / steps
            px = int(x0 + dx * t)
            py = int(y0 + dy * t)
            self.set_pixel(px, py, color, alpha)

    def draw_circle(self, cx: float, cy: float, radius: float, color: tuple[int, int, int], glow: bool = True):
        icx, icy = int(cx), int(cy)
        r = int(radius)
        if glow:
            glow_r = r + 4
            for dy in range(-glow_r, glow_r + 1):
                for dx in range(-glow_r, glow_r + 1):
                    d = math.hypot(dx, dy)
                    if d <= glow_r:
                        a = max(0.0, 0.35 * (1.0 - d / glow_r))
                        self.set_pixel(icx + dx, icy + dy, color, a)

        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= radius * radius:
                    self.set_pixel(icx + dx, icy + dy, color, 1.0)

    def to_png_bytes(self) -> bytes:
        def make_chunk(tag: bytes, data: bytes) -> bytes:
            return (
                struct.pack(">I", len(data)) +
                tag +
                data +
                struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
            )

        header = b"\x89PNG\r\n\x1a\n"
        ihdr = make_chunk(b"IHDR", struct.pack(">IIBBBBB", self.width, self.height, 8, 2, 0, 0, 0))

        raw_rows = bytearray()
        row_len = self.width * 3
        for y in range(self.height):
            raw_rows.append(0)  # Filter type: None
            offset = y * row_len
            raw_rows.extend(self.buffer[offset : offset + row_len])

        idat = make_chunk(b"IDAT", zlib.compress(bytes(raw_rows), level=6))
        iend = make_chunk(b"IEND", b"")
        return header + ihdr + idat + iend


def render_png_graph(output_path: Path | None = None) -> Path:
    target_path = output_path or PNG_OUTPUT
    target_path.parent.mkdir(parents=True, exist_ok=True)

    data = extract_graph_data(settings.brain.brain_dir)
    nodes = data["nodes"]
    links = data["links"]

    width = 1200
    height = 800
    pos = simulate_anatomical_forces(nodes, links, width, height, iterations=220)

    canvas = RasterCanvas(width, height, bg_color=(11, 15, 25))

    # 1. Desenhar sinapses (arestas)
    for link in links:
        src = link["source"]
        tgt = link["target"]
        if src in pos and tgt in pos:
            x0, y0 = pos[src]
            x1, y1 = pos[tgt]
            canvas.draw_line(x0, y0, x1, y1, color=(56, 139, 253), alpha=0.25)

    # 2. Desenhar nós neuronais
    for node in nodes:
        nid = node["id"]
        if nid in pos:
            x, y = pos[nid]
            group = node.get("group", "conceito")
            color = HEX_COLORS.get(group, (139, 148, 158))
            is_cortex = "cortex" in group or "operador" in group
            radius = 7.0 if is_cortex else 4.5
            canvas.draw_circle(x, y, radius, color, glow=is_cortex)

    target_path.write_bytes(canvas.to_png_bytes())
    logger.info(f"Grafo PNG renderizado: {target_path}")
    return target_path


if __name__ == "__main__":
    render_png_graph()
