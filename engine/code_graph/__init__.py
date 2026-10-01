"""
ThSyr Code Graph & Structural GraphRAG Engine (Graphify Architecture).
Motor deterministico de extracao AST e relacional para Python, Java e SQL.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .builder import CodeGraphBuilder
from .java_parser import JavaStructuralParser
from .models import (
    CodeEdge,
    CodeGraph,
    CodeNode,
    CodeRelationshipType,
    CodeSymbolType,
)
from .python_parser import PythonASTParser
from .sql_parser import SQLDDLParser
from .visualizer import CODE_CANVAS_3D_OUTPUT, render_code_graph_3d


class GraphifyEngine:
    """Fachada executiva do motor Graphify para ThSyr."""

    DEFAULT_CACHE_FILE = Path("state/code_graph.json")

    def __init__(self) -> None:
        self.builder = CodeGraphBuilder()

    @property
    def graph(self) -> CodeGraph:
        return self.builder.graph

    def build(
        self,
        paths: list[str | Path],
        persist: bool = True,
        cache_path: Path | str = DEFAULT_CACHE_FILE,
    ) -> CodeGraph:
        """Varre os caminhos indicados e gera o grafo de codigo consolidado."""
        graph = self.builder.build_from_paths(paths)
        if persist:
            self.builder.export_json(cache_path)
        return graph

    def load_cache(self, cache_path: Path | str = DEFAULT_CACHE_FILE) -> CodeGraph:
        """Carrega o grafo persistido anteriormente em cache JSON."""
        return self.builder.import_json(cache_path)

    def query(self, query_str: str) -> list[CodeNode]:
        """Localiza simbolos no grafo por nome ou ID."""
        return self.builder.find_symbols(query_str)

    def neighborhood(self, symbol_id: str, depth: int = 1) -> dict[str, Any]:
        """Recupera o subgrafo ao redor de um simbolo."""
        return self.builder.get_neighborhood(symbol_id, depth=depth)

    def impact(self, symbol_id: str) -> dict[str, Any]:
        """Executa analise de impacto deterministica para um simbolo."""
        return self.builder.get_impact_analysis(symbol_id)

    def render_3d(
        self,
        output_path: Path | str = CODE_CANVAS_3D_OUTPUT,
        open_browser: bool = False,
    ) -> Path:
        """Renderiza o canvas 3D WebGL interativo."""
        return render_code_graph_3d(self.builder.graph, output_path=output_path, open_browser=open_browser)


__all__ = [
    "CodeSymbolType",
    "CodeRelationshipType",
    "CodeNode",
    "CodeEdge",
    "CodeGraph",
    "PythonASTParser",
    "JavaStructuralParser",
    "SQLDDLParser",
    "CodeGraphBuilder",
    "render_code_graph_3d",
    "GraphifyEngine",
]
