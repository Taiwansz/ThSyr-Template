"""
ThSyr Tool Bus - Logo & Brand Design Adapters
Ferramentas para busca no acervo de 1.400+ logos, auditoria geometrica
e geracao de briefs de identidade visual.
"""

from pathlib import Path
from typing import Any, Optional

from ...brand import BrandEngine, LogoLibrary, SvgAuditor
from ...config import PROJECT_ROOT
from ..base import BaseTool, RiskLevel, ToolMetadata, ToolResult


class LogoSearchTool(BaseTool):
    def __init__(self):
        super().__init__(ToolMetadata(
            name="logo_search",
            description="Pesquisa no acervo de 1.400+ logos SVG reais por tecnica, geometria, tipo e industria",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Termo de busca textual"},
                    "mark_type": {"type": "string", "description": "Tipo de marca (wordmark, lettermark, letterform, pictorial, abstract, mascot, emblem, combination)"},
                    "technique": {"type": "string", "description": "Tecnica visual (negative-space, geometric-construction, continuous-line, modular-system...)"},
                    "geometry": {"type": "string", "description": "Geometria dominante (circle, hexagon, triangle, organic...)"},
                    "industry": {"type": "string", "description": "Industria ou setor"},
                    "exemplary": {"type": "boolean", "default": False, "description": "Filtrar apenas exemplos de alta maestria"},
                    "limit": {"type": "integer", "default": 10, "description": "Limite de resultados"}
                }
            },
            output_schema={"type": "object", "properties": {"matches": {"type": "array"}}},
            risk_level=RiskLevel.LEVEL_1_READ,
            requires_confirmation=False,
            timeout=10,
            reversible=True
        ))

    def execute(
        self,
        query: Optional[str] = None,
        mark_type: Optional[str] = None,
        technique: Optional[str] = None,
        geometry: Optional[str] = None,
        industry: Optional[str] = None,
        exemplary: bool = False,
        limit: int = 10,
        **kwargs: Any
    ) -> ToolResult:
        engine = BrandEngine()
        results = engine.search_references(
            query=query,
            mark_type=mark_type,
            technique=technique,
            geometry=geometry,
            industry=industry,
            exemplary=exemplary,
            limit=limit,
        )
        data = [r.to_dict() for r in results]
        summary_lines = [
            f"- {r['filename']} [{r['mark_type']}] | cores: {r['colors']} | {r['subject']}"
            for r in data
        ]
        raw_output = f"{len(data)} logos encontrados:\n" + "\n".join(summary_lines) if data else "Nenhum logo encontrado com esses filtros."
        return ToolResult(
            tool_name=self.name,
            success=True,
            data={"count": len(data), "matches": data},
            raw_output=raw_output,
        )


class LogoAuditTool(BaseTool):
    def __init__(self):
        super().__init__(ToolMetadata(
            name="logo_audit",
            description="Audita rigorosamente um arquivo SVG de logo contra regras de escala 16px, producao e geometria",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Caminho do arquivo SVG a ser auditado"},
                    "bg_color": {"type": "string", "description": "Opcional: cor de fundo para teste de contraste (#ffffff)"}
                },
                "required": ["path"]
            },
            output_schema={"type": "object", "properties": {"passed": {"type": "boolean"}, "findings": {"type": "array"}}},
            risk_level=RiskLevel.LEVEL_1_READ,
            requires_confirmation=False,
            timeout=10,
            reversible=True
        ))

    def execute(self, path: str = "", bg_color: Optional[str] = None, **kwargs: Any) -> ToolResult:
        if not path:
            return ToolResult(tool_name=self.name, success=False, error="Caminho do arquivo SVG nao informado.")

        target_path = Path(path)
        if not target_path.is_absolute():
            target_path = PROJECT_ROOT / target_path

        engine = BrandEngine()
        report = engine.audit_svg(target_path, bg_color=bg_color)
        rep_dict = report.to_dict()

        status_str = "APROVADO" if report.passed else "REPROVADO"
        lines = [f"Auditoria SVG: {report.filename} [{status_str}]"]
        for f in report.findings:
            lines.append(f"  [{f.level}] {f.code}: {f.message}")

        return ToolResult(
            tool_name=self.name,
            success=True,
            data=rep_dict,
            raw_output="\n".join(lines),
        )


class LogoStatsTool(BaseTool):
    def __init__(self):
        super().__init__(ToolMetadata(
            name="logo_stats",
            description="Retorna estatisticas e composicao da taxonomia de 1.400+ logos no acervo do ThSyr",
            input_schema={"type": "object", "properties": {}},
            output_schema={"type": "object", "properties": {"total_logos": {"type": "integer"}}},
            risk_level=RiskLevel.LEVEL_1_READ,
            requires_confirmation=False,
            timeout=5,
            reversible=True
        ))

    def execute(self, **kwargs: Any) -> ToolResult:
        engine = BrandEngine()
        stats = engine.get_stats()
        return ToolResult(
            tool_name=self.name,
            success=True,
            data=stats,
            raw_output=f"Acervo de Marcas: {stats.get('total_logos', 0)} logos cadastrados.",
        )
