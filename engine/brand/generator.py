"""
ThSyr Brand Asset & Presentation Generator
Wrapper de execucao dos motores de geracao de variantes, folhas de teste,
pranchas de conceito e apresentacao executiva de marcas.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..config import PROJECT_ROOT


class BrandGenerator:
    """Orquestrador de scripts geradores de ativos e apresentacoes visuais."""

    def __init__(self, scripts_dir: Optional[Path] = None):
        self.scripts_dir = self._resolve_scripts_dir(scripts_dir)

    def _resolve_scripts_dir(self, override: Optional[Path]) -> Path:
        if override and override.exists():
            return override

        candidates = [
            PROJECT_ROOT / ".agents" / "skills" / "logo-design" / "scripts",
            Path("/root/.gemini/config/skills/logo-design/scripts"),
            Path("/tmp/logo-design-skill/skills/logo-design/scripts"),
        ]
        for c in candidates:
            if c.exists() and (c / "export_variants.py").exists():
                return c

        return candidates[0]

    def export_variants(
        self,
        svg_file: Path | str,
        title: str,
        mono_color: Optional[str] = None,
        icon_bg: Optional[str] = None,
        web_icons: bool = False,
        favicon_source: Optional[Path | str] = None,
        out_dir: Optional[Path | str] = None,
    ) -> Dict[str, Any]:
        """Gera variantes (black, white, mono, square, favicon, app-icon)."""
        script = self.scripts_dir / "export_variants.py"
        if not script.exists():
            return {"success": False, "error": f"Script export_variants.py nao encontrado em {self.scripts_dir}"}

        cmd = [sys.executable, str(script), str(svg_file), "--title", title]
        if mono_color:
            cmd.extend(["--mono", mono_color])
        if icon_bg:
            cmd.extend(["--icon-bg", icon_bg])
        if web_icons:
            cmd.append("--web-icons")
        if favicon_source:
            cmd.extend(["--favicon-source", str(favicon_source)])

        cwd = Path(out_dir) if out_dir else Path(svg_file).parent
        cwd.mkdir(parents=True, exist_ok=True)

        res = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, check=False)
        return {
            "success": res.returncode == 0,
            "stdout": res.stdout.strip(),
            "stderr": res.stderr.strip(),
            "returncode": res.returncode,
            "target_dir": str(cwd),
        }

    def generate_preview_sheet(
        self,
        svg_files: List[Path | str],
        output_html: Path | str,
        industry: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Gera folha HTML de inspecao: escala, fundos, squint blur, teste de prateleira."""
        script = self.scripts_dir / "preview_sheet.py"
        if not script.exists():
            return {"success": False, "error": f"Script preview_sheet.py nao encontrado em {self.scripts_dir}"}

        cmd = [sys.executable, str(script)]
        for f in svg_files:
            cmd.append(str(f))
        if industry:
            cmd.extend(["--refs-industry", industry])
        cmd.extend(["-o", str(output_html)])

        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return {
            "success": res.returncode == 0,
            "output_file": str(output_html),
            "stdout": res.stdout.strip(),
            "stderr": res.stderr.strip(),
            "returncode": res.returncode,
        }

    def generate_concept_sheet(
        self,
        symbol_files: List[Path | str],
        output_png: Path | str,
        lockup_files: Optional[List[Path | str]] = None,
        names: Optional[List[str]] = None,
        notes: Optional[List[str]] = None,
        recommend_idx: int = 1,
        greyscale: bool = False,
    ) -> Dict[str, Any]:
        """Gera prancha unificada comparativa dos conceitos de marca."""
        script = self.scripts_dir / "concept_sheet.py"
        if not script.exists():
            return {"success": False, "error": f"Script concept_sheet.py nao encontrado em {self.scripts_dir}"}

        cmd = [sys.executable, str(script)]
        for s in symbol_files:
            cmd.append(str(s))

        if lockup_files:
            cmd.append("--lockups")
            for lk in lockup_files:
                cmd.append(str(lk))

        if names:
            cmd.append("--names")
            cmd.extend(names)

        if notes:
            cmd.append("--notes")
            cmd.extend(notes)

        if recommend_idx:
            cmd.extend(["--recommend", str(recommend_idx)])

        if greyscale:
            cmd.append("--greyscale")

        cmd.extend(["-o", str(output_png)])

        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return {
            "success": res.returncode == 0,
            "output_file": str(output_png),
            "stdout": res.stdout.strip(),
            "stderr": res.stderr.strip(),
            "returncode": res.returncode,
        }

    def generate_presentation_board(
        self,
        spec_json: Path | str,
        output_html: Path | str,
        png_dir: Optional[Path | str] = None,
    ) -> Dict[str, Any]:
        """Gera prancha de apresentacao corporativa e mockups de aplicacao real."""
        script = self.scripts_dir / "presentation_board.py"
        if not script.exists():
            return {"success": False, "error": f"Script presentation_board.py nao encontrado em {self.scripts_dir}"}

        cmd = [sys.executable, str(script), str(spec_json), "-o", str(output_html)]
        if png_dir:
            cmd.extend(["--png-dir", str(png_dir)])

        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return {
            "success": res.returncode == 0,
            "output_file": str(output_html),
            "stdout": res.stdout.strip(),
            "stderr": res.stderr.strip(),
            "returncode": res.returncode,
        }
