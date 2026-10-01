"""
ThSyr Brand & Logo Architecture Engine (Occipital Lobe)
Integra a ciencia geometrica de marcas, acervo canonico de 1.400+ logos,
auditoria de pureza vetorial e orquestracao conceitual de identidade visual.
"""

from typing import Any, Dict, List, Optional
from pathlib import Path

from .auditor import AuditReport, Finding, SvgAuditor
from .generator import BrandGenerator
from .library import LogoLibrary, LogoRecord
from .pipeline import (
    INDUSTRY_CLICHES,
    MARK_TYPES,
    OPTICAL_REFINEMENT_RULES,
    VISUAL_TECHNIQUES,
    BrandStrategyEngine,
    DesignBrief,
)


class BrandEngine:
    """Motor unificado de design de identidade e marcas do ThSyr."""

    def __init__(self):
        self.library = LogoLibrary.get_instance()
        self.auditor = SvgAuditor()
        self.strategy = BrandStrategyEngine()
        self.generator = BrandGenerator()

    def search_references(
        self,
        query: Optional[str] = None,
        mark_type: Optional[str] = None,
        technique: Optional[str] = None,
        geometry: Optional[str] = None,
        industry: Optional[str] = None,
        exemplary: bool = False,
        limit: int = 15,
    ) -> List[LogoRecord]:
        return self.library.search(
            query=query,
            mark_type=mark_type,
            technique=technique,
            geometry=geometry,
            industry=industry,
            exemplary=exemplary,
            limit=limit,
        )

    def audit_svg(self, svg_path: Path | str, bg_color: Optional[str] = None) -> AuditReport:
        return self.auditor.audit_file(svg_path, bg_color=bg_color)

    def create_brief(
        self,
        brand_name: str,
        industry: str,
        adjectives: Optional[List[str]] = None,
        offering: str = "",
        promise: str = "",
    ) -> DesignBrief:
        return self.strategy.generate_brief(
            brand_name=brand_name,
            industry=industry,
            adjectives=adjectives,
            offering=offering,
            promise=promise,
        )

    def get_stats(self) -> Dict[str, Any]:
        return self.library.get_stats()


__all__ = [
    "BrandEngine",
    "LogoLibrary",
    "LogoRecord",
    "SvgAuditor",
    "AuditReport",
    "Finding",
    "BrandStrategyEngine",
    "DesignBrief",
    "BrandGenerator",
    "MARK_TYPES",
    "VISUAL_TECHNIQUES",
    "INDUSTRY_CLICHES",
    "OPTICAL_REFINEMENT_RULES",
]
