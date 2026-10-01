"""
Unit Tests for ThSyr Brand & Logo Design Engine
Verifica o acervo de 1.400+ logos, busca por tecnicas, auditoria geometrica,
regras de refinamento optico, geracao de briefs e integracao com o ToolBus.
"""

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

from engine.brand import (
    MARK_TYPES,
    OPTICAL_REFINEMENT_RULES,
    VISUAL_TECHNIQUES,
    BrandEngine,
    BrandStrategyEngine,
    LogoLibrary,
    SvgAuditor,
)
from engine.cli.logo import cmd_logo
from engine.tools.bus import ToolBus


class TestLogoEngine(unittest.TestCase):
    def setUp(self):
        self.engine = BrandEngine()

    def test_logo_library_stats(self):
        stats = self.engine.get_stats()
        self.assertGreaterEqual(stats.get("total_logos", 0), 1400)
        self.assertGreaterEqual(stats.get("exemplary_count", 0), 100)
        mark_types = stats.get("mark_types", {})
        self.assertIn("abstract", mark_types)
        self.assertIn("letterform", mark_types)
        self.assertIn("wordmark", mark_types)

    def test_logo_library_search_by_technique(self):
        results = self.engine.search_references(technique="negative-space", limit=5)
        self.assertGreaterEqual(len(results), 1)
        for r in results:
            self.assertTrue(r.path.name.endswith(".svg"))

    def test_logo_library_search_exemplary(self):
        results = self.engine.search_references(exemplary=True, limit=5)
        self.assertEqual(len(results), 5)
        for r in results:
            self.assertTrue(r.exemplary)

    def test_svg_auditor_clean_svg(self):
        clean_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
            <title>Pure Test Mark</title>
            <path d="M32 32 L224 32 L224 224 L32 224 Z" fill="#000000"/>
        </svg>"""
        report = self.engine.auditor.audit_content(clean_svg, filename="clean.svg")
        self.assertTrue(report.passed)
        self.assertEqual(report.viewbox, (0.0, 0.0, 256.0, 256.0))
        self.assertEqual(report.aspect_ratio, 1.0)
        self.assertFalse(any(f.level == "FAIL" for f in report.findings))

    def test_svg_auditor_detects_violations(self):
        dirty_svg = """<svg xmlns="http://www.w3.org/2000/svg">
            <text x="10" y="20">Non-outlined Font</text>
            <image href="raster.png" width="100" height="100"/>
            <foreignObject width="50" height="50"><div>test</div></foreignObject>
            <path d="M10 10 L100 12" fill="#ff0000"/>
        </svg>"""
        report = self.engine.auditor.audit_content(dirty_svg, filename="dirty.svg")
        self.assertFalse(report.passed)
        codes = [f.code for f in report.findings]
        self.assertIn("no-viewbox", codes)
        self.assertIn("live-text", codes)
        self.assertIn("raster-image", codes)
        self.assertIn("foreign-object", codes)

    def test_brand_strategy_brief(self):
        strategy = BrandStrategyEngine()
        brief = strategy.generate_brief(
            brand_name="TestFin",
            industry="fintech",
            adjectives=["seguro", "monolitico"],
        )
        self.assertEqual(brief.brand_name, "TestFin")
        self.assertIn("seta verde para cima", brief.cliches_to_avoid)
        self.assertGreater(len(brief.recommended_mark_types), 0)
        md = brief.render_markdown()
        self.assertIn("Design Brief Estruturado", md)
        self.assertIn("Alerta Pre-Frontal de Cliches", md)

    def test_tool_bus_integration(self):
        bus = ToolBus()
        tool_names = [t.name for t in bus.list_tools()]
        self.assertIn("logo_search", tool_names)
        self.assertIn("logo_audit", tool_names)
        self.assertIn("logo_stats", tool_names)

        # Execute logo_stats
        res_stats = bus.execute("logo_stats")
        self.assertTrue(res_stats.success)
        self.assertIn("1432", res_stats.raw_output)

        # Execute logo_search
        res_search = bus.execute("logo_search", technique="negative-space", limit=2)
        self.assertTrue(res_search.success)
        self.assertEqual(len(res_search.data["matches"]), 2)

    def test_cli_logo_commands(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            cmd_logo(SimpleNamespace(logo_action="stats"))
        out = buf.getvalue()
        self.assertIn("THSYR // ACERVO DE LOGOS E MARCAS", out)
        self.assertIn("abstract", out)

        buf = io.StringIO()
        with redirect_stdout(buf):
            cmd_logo(SimpleNamespace(logo_action="principles"))
        out = buf.getvalue()
        self.assertIn("8 TIPOS DE MARCA", out)
        self.assertIn("14 TECNICAS VISUAIS", out)


if __name__ == "__main__":
    unittest.main()
