"""
ThSyr Code Graph Builder (Graphify Core Engine)
Orquestra parsers de multiplas linguagens (Python, Java, SQL),
constrói o grafo estrutural unificado e resolve sinapses e dependencias.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .java_parser import JavaStructuralParser
from .models import CodeEdge, CodeGraph, CodeNode, CodeRelationshipType, CodeSymbolType
from .python_parser import PythonASTParser
from .sql_parser import SQLDDLParser


class CodeGraphBuilder:
    """Varre diretorios, analisa arquetipos e unifica grafos de codigo."""

    DEFAULT_IGNORE_DIRS = {
        ".git",
        "__pycache__",
        "venv",
        ".venv",
        "node_modules",
        ".idea",
        "dist",
        "build",
        ".pytest_cache",
        ".gemini",
        ".gradle",
        "target",
        ".system_generated",
    }

    def __init__(self) -> None:
        self.py_parser = PythonASTParser()
        self.java_parser = JavaStructuralParser()
        self.sql_parser = SQLDDLParser()
        self.graph = CodeGraph()

    def build_from_paths(
        self,
        paths: list[str | Path],
        ignore_dirs: set[str] | None = None,
    ) -> CodeGraph:
        """Varre os caminhos fornecidos e popula o grafo."""
        ignored = ignore_dirs or self.DEFAULT_IGNORE_DIRS

        for p_raw in paths:
            path = Path(p_raw).resolve()
            if not path.exists():
                continue

            if path.is_file():
                self._parse_single_file(path)
            elif path.is_dir():
                for file_path in self._walk_dir(path, ignored):
                    self._parse_single_file(file_path)

        self._resolve_dangling_references()
        return self.graph

    def _walk_dir(self, root: Path, ignored: set[str]) -> Iterable[Path]:
        """Caminha recursivamente pelo diretorio filtrando pastas ignoradas."""
        try:
            for entry in root.iterdir():
                if entry.name in ignored:
                    continue
                if entry.is_dir():
                    yield from self._walk_dir(entry, ignored)
                elif entry.is_file():
                    yield entry
        except PermissionError:
            return

    def _parse_single_file(self, file_path: Path) -> None:
        """Roteia cada arquivo para o parser correspondente conforme extensao."""
        ext = file_path.suffix.lower()
        if ext == ".py":
            self.py_parser.parse_file(file_path, self.graph)
        elif ext == ".java":
            self.java_parser.parse_file(file_path, self.graph)
        elif ext == ".sql":
            self.sql_parser.parse_file(file_path, self.graph)

    def _resolve_dangling_references(self) -> None:
        """Resolve arestas cujos alvos sao parciais, ligando aos nós reais."""
        name_to_node_ids: dict[str, list[str]] = {}
        for node_id, node in self.graph.nodes.items():
            name_to_node_ids.setdefault(node.name, []).append(node_id)

        # Ajustar arestas onde target_id e uma referencia generica
        for edge in self.graph.edges:
            if edge.target_id not in self.graph.nodes:
                target_raw = edge.target_id.split(":")[-1]
                # Se for ex: py:func:foo e houver foo nos nós
                base_name = target_raw.split(".")[-1]
                matches = name_to_node_ids.get(base_name, [])
                if len(matches) == 1:
                    edge.target_id = matches[0]

    # Metodos de GraphRAG e Consulta
    def find_symbols(self, query: str) -> list[CodeNode]:
        """Busca nós por nome ou id aproximado."""
        q = query.lower()
        results: list[CodeNode] = []
        for node in self.graph.nodes.values():
            if q in node.name.lower() or q in node.id.lower():
                results.append(node)
        return results

    def get_neighborhood(self, symbol_id: str, depth: int = 1) -> dict[str, Any]:
        """Retorna subgrafo ao redor de um simbolo com profundidade especificada."""
        visited_nodes: set[str] = {symbol_id}
        frontier: set[str] = {symbol_id}
        collected_edges: list[CodeEdge] = []

        for _ in range(depth):
            next_frontier: set[str] = set()
            for cur_id in frontier:
                for edge in self.graph.edges:
                    if edge.source_id == cur_id:
                        collected_edges.append(edge)
                        if edge.target_id not in visited_nodes:
                            visited_nodes.add(edge.target_id)
                            next_frontier.add(edge.target_id)
                    elif edge.target_id == cur_id:
                        collected_edges.append(edge)
                        if edge.source_id not in visited_nodes:
                            visited_nodes.add(edge.source_id)
                            next_frontier.add(edge.source_id)
            frontier = next_frontier

        sub_nodes = [self.graph.nodes[n_id].to_dict() for n_id in visited_nodes if n_id in self.graph.nodes]
        sub_edges = [e.to_dict() for e in collected_edges]

        return {
            "root_id": symbol_id,
            "depth": depth,
            "nodes": sub_nodes,
            "edges": sub_edges,
        }

    def get_impact_analysis(self, symbol_id: str) -> dict[str, Any]:
        """Analisa impacto: quem chama, quem herda ou quem referencia este simbolo."""
        callers = self.graph.get_callers(symbol_id)
        referencing_fks = [
            e.source_id
            for e in self.graph.edges
            if e.target_id == symbol_id and e.rel_type == CodeRelationshipType.REFERENCES_FK
        ]
        inheritors = [
            e.source_id
            for e in self.graph.edges
            if e.target_id == symbol_id and e.rel_type in (CodeRelationshipType.INHERITS, CodeRelationshipType.IMPLEMENTS)
        ]

        return {
            "symbol_id": symbol_id,
            "direct_callers": callers,
            "referencing_foreign_keys": referencing_fks,
            "inheritors_or_implementers": inheritors,
            "total_dependents": len(callers) + len(referencing_fks) + len(inheritors),
        }

    def export_json(self, destination_path: Path | str) -> Path:
        """Serializa o grafo completo em arquivo JSON."""
        dest = Path(destination_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(self.graph.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return dest

    def import_json(self, source_path: Path | str) -> CodeGraph:
        """Carrega o grafo a partir de arquivo JSON."""
        src = Path(source_path)
        data = json.loads(src.read_text(encoding="utf-8"))

        self.graph = CodeGraph()
        for n_data in data.get("nodes", []):
            node = CodeNode(
                id=n_data["id"],
                name=n_data["name"],
                symbol_type=CodeSymbolType(n_data["symbol_type"]),
                language=n_data["language"],
                filepath=n_data["filepath"],
                line_number=n_data.get("line_number", 1),
                docstring=n_data.get("docstring", ""),
                metadata=n_data.get("metadata", {}),
            )
            self.graph.add_node(node)

        for e_data in data.get("edges", []):
            edge = CodeEdge(
                source_id=e_data["source_id"],
                target_id=e_data["target_id"],
                rel_type=CodeRelationshipType(e_data["rel_type"]),
                metadata=e_data.get("metadata", {}),
            )
            self.graph.add_edge(edge)

        return self.graph
