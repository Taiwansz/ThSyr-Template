"""
ThSyr SVG Brand & Logo Auditor
Auditoria automatica de rigor geometrico, producao vetorial e conformidade
com os principios de design de marcas: resolucao a 16px, monocromia e pureza geometrica.
"""

import math
import os
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..config import PROJECT_ROOT

CLEAN_ANGLES = [0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180]


@dataclass
class Finding:
    level: str  # "FAIL", "WARN", "INFO"
    code: str
    message: str

    def to_dict(self) -> Dict[str, str]:
        return {"level": self.level, "code": self.code, "message": self.message}


@dataclass
class AuditReport:
    filename: str
    passed: bool
    bytes_count: int
    findings: List[Finding] = field(default_factory=list)
    viewbox: Optional[Tuple[float, float, float, float]] = None
    aspect_ratio: Optional[float] = None
    colors_detected: List[str] = field(default_factory=list)
    element_counts: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "filename": self.filename,
            "passed": self.passed,
            "bytes": self.bytes_count,
            "viewbox": list(self.viewbox) if self.viewbox else None,
            "aspect_ratio": self.aspect_ratio,
            "colors_detected": self.colors_detected,
            "element_counts": self.element_counts,
            "findings": [f.to_dict() for f in self.findings],
        }


class SvgAuditor:
    """Motor de auditoria geometrica e estrutural de logos vetoriais SVG."""

    def __init__(self):
        pass

    def audit_file(self, svg_path: Path | str, bg_color: Optional[str] = None) -> AuditReport:
        p = Path(svg_path)
        if not p.is_file():
            report = AuditReport(filename=str(svg_path), passed=False, bytes_count=0)
            report.findings.append(Finding("FAIL", "file-not-found", f"Arquivo nao encontrado: {svg_path}"))
            return report

        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                raw_content = f.read()
            return self.audit_content(raw_content, filename=p.name, bg_color=bg_color)
        except Exception as e:
            report = AuditReport(filename=p.name, passed=False, bytes_count=0)
            report.findings.append(Finding("FAIL", "parse-error", f"Falha ao ler ou analisar SVG: {e}"))
            return report

    def audit_content(
        self,
        raw_svg: str,
        filename: str = "inline.svg",
        bg_color: Optional[str] = None,
    ) -> AuditReport:
        findings: List[Finding] = []

        try:
            root = ET.fromstring(raw_svg)
        except Exception as e:
            rep = AuditReport(filename=filename, passed=False, bytes_count=len(raw_svg.encode("utf-8")))
            rep.findings.append(Finding("FAIL", "xml-syntax-error", f"XML malformado: {e}"))
            return rep

        bytes_count = len(raw_svg.encode("utf-8"))
        element_counts: Dict[str, int] = {}
        for elem in root.iter():
            tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            element_counts[tag] = element_counts.get(tag, 0) + 1

        # 1. ViewBox & Proporcao
        vb_attr = root.get("viewBox")
        viewbox: Optional[Tuple[float, float, float, float]] = None
        aspect_ratio: Optional[float] = None

        if not vb_attr:
            findings.append(Finding("WARN", "no-viewbox", "Ausencia de viewBox: o logo nao escalara de forma deterministica."))
        else:
            try:
                parts = [float(x) for x in re.split(r"[\s,]+", vb_attr.strip()) if x]
                if len(parts) == 4:
                    viewbox = (parts[0], parts[1], parts[2], parts[3])
                    w, h = parts[2], parts[3]
                    aspect_ratio = round(w / h, 3) if h else None
                    if any(abs(v - round(v)) > 1e-4 for v in parts):
                        findings.append(Finding("INFO", "fractional-viewbox", "viewBox contem decimais; inteiros facilitam o alinhamento ao grid."))
            except Exception:
                findings.append(Finding("WARN", "invalid-viewbox", f"Formato invalido de viewBox: '{vb_attr}'."))

        # 2. Inspecao de Elementos Criticos
        if element_counts.get("text", 0) > 0 or element_counts.get("tspan", 0) > 0:
            findings.append(Finding("FAIL", "live-text", "Contem <text>: fontes nao outlineadas geram inconsistencias em clientes sem a tipografia instalada."))

        if element_counts.get("image", 0) > 0:
            findings.append(Finding("FAIL", "raster-image", "Contem <image>: logos mestres devem ser puramente vetoriais."))

        if element_counts.get("foreignObject", 0) > 0:
            findings.append(Finding("FAIL", "foreign-object", "Contem <foreignObject>: dependencia de parser HTML impede renderizacao em sistemas nativos."))

        if element_counts.get("filter", 0) > 0:
            findings.append(Finding("WARN", "filter-effects", "Usa <filter> (blur, glow, shadow). Filtros quebram impressao serigrafica e corte a laser."))

        if element_counts.get("mask", 0) > 0:
            findings.append(Finding("INFO", "mask-used", "Usa <mask>. Para producao final (bordado/plotter), funda a geometria com fill-rule='evenodd'."))

        if not element_counts.get("title", 0):
            findings.append(Finding("INFO", "no-title", "Sem tag <title>: adicione titulo semantico para acessibilidade e leitores de tela."))

        # 3. Precisao de Coordenadas
        if re.search(r"\d+\.\d{4,}", raw_svg):
            findings.append(Finding("INFO", "excessive-precision", "Coordenadas com mais de 3 casas decimais. Arredonde para 1 ou 2 casas decimais."))

        # 4. Auditoria de Cores
        hex_colors = set(m.lower() for m in re.findall(r"#(?:[0-9a-fA-F]{3}){1,2}\b", raw_svg))
        colors_detected = sorted(list(hex_colors))
        if len(hex_colors) > 3:
            findings.append(Finding("WARN", "excessive-colors", f"Detectadas {len(hex_colors)} cores distintas. Marcas iconicas concentram-se em 1 a 2 cores primarias."))

        # 5. Segmentos e Angulos
        d_attrs = [e.get("d", "") for e in root.iter() if e.get("d")]
        near_misses = self._find_near_miss_angles(d_attrs)
        for nm in near_misses[:3]:
            findings.append(Finding("WARN", "near-miss-angle", f"Angulo de {nm[0]:.1f}° proximo a {nm[1]}° ({nm[2]:.2f}° de desvio). Alinhe a geometria."))

        # Determinacao de Sucesso: zero FAILs
        passed = not any(f.level == "FAIL" for f in findings)

        return AuditReport(
            filename=filename,
            passed=passed,
            bytes_count=bytes_count,
            findings=findings,
            viewbox=viewbox,
            aspect_ratio=aspect_ratio,
            colors_detected=colors_detected,
            element_counts=element_counts,
        )

    def _find_near_miss_angles(self, d_strings: List[str]) -> List[Tuple[float, int, float]]:
        near_misses = []
        seg_pat = re.compile(r"([LlMm])\s*(-?[\d.]+)[,\s]+(-?[\d.]+)")

        for d in d_strings:
            coords = []
            for match in seg_pat.finditer(d):
                try:
                    coords.append((float(match.group(2)), float(match.group(3))))
                except ValueError:
                    continue

            for i in range(len(coords) - 1):
                dx = coords[i + 1][0] - coords[i][0]
                dy = coords[i + 1][1] - coords[i][1]
                dist = math.hypot(dx, dy)
                if dist < 4.0:
                    continue

                angle = (math.degrees(math.atan2(dy, dx)) + 360) % 180
                for clean in CLEAN_ANGLES:
                    diff = abs(angle - clean)
                    if 0.35 <= diff <= 2.8:
                        near_misses.append((angle, clean, diff))
                        break

        return near_misses
