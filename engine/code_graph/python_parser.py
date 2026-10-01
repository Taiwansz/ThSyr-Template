"""
Parser de codigo Python baseado no modulo nativo AST.
Extrai classes, funcoes, metodos, heranca, imports e chamadas.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from .models import CodeEdge, CodeGraph, CodeNode, CodeRelationshipType, CodeSymbolType


class PythonASTParser:
    """Disseca arquivos Python gerando nós e arestas relacionais a nivel de AST."""

    def parse_file(self, file_path: Path, graph: CodeGraph) -> None:
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content, filename=str(file_path))
        except Exception:
            return

        module_id = f"py:mod:{file_path.stem}"
        graph.add_node(
            CodeNode(
                id=module_id,
                name=file_path.stem,
                symbol_type=CodeSymbolType.MODULE,
                language="python",
                filepath=str(file_path),
                line_number=1,
                docstring=ast.get_docstring(tree) or "",
            )
        )

        for stmt in tree.body:
            if isinstance(stmt, ast.ClassDef):
                self._parse_class(stmt, file_path, module_id, graph)
            elif isinstance(stmt, ast.FunctionDef) or isinstance(stmt, ast.AsyncFunctionDef):
                self._parse_function(stmt, file_path, module_id, graph, parent_id=module_id)

    def _parse_class(
        self,
        node: ast.ClassDef,
        file_path: Path,
        module_id: str,
        graph: CodeGraph,
    ) -> None:
        class_id = f"py:class:{file_path.stem}.{node.name}"
        doc = ast.get_docstring(node) or ""
        bases = [self._get_name(b) for b in node.bases if self._get_name(b)]

        graph.add_node(
            CodeNode(
                id=class_id,
                name=node.name,
                symbol_type=CodeSymbolType.CLASS,
                language="python",
                filepath=str(file_path),
                line_number=node.lineno,
                docstring=doc,
                metadata={"bases": bases},
            )
        )

        # Aresta de contencao: modulo contem classe
        graph.add_edge(
            CodeEdge(
                source_id=module_id,
                target_id=class_id,
                rel_type=CodeRelationshipType.CONTAINS,
            )
        )

        # Arestas de heranca
        for base in bases:
            base_id = f"py:class:{base}"
            graph.add_edge(
                CodeEdge(
                    source_id=class_id,
                    target_id=base_id,
                    rel_type=CodeRelationshipType.INHERITS,
                )
            )

        # Parsear metodos da classe
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._parse_function(item, file_path, module_id, graph, parent_id=class_id, is_method=True)

    def _parse_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: Path,
        module_id: str,
        graph: CodeGraph,
        parent_id: str,
        is_method: bool = False,
    ) -> None:
        prefix = "method" if is_method else "func"
        symbol_type = CodeSymbolType.METHOD if is_method else CodeSymbolType.FUNCTION
        func_id = f"py:{prefix}:{file_path.stem}.{node.name}"
        doc = ast.get_docstring(node) or ""

        # Args
        args = [a.arg for a in node.args.args]

        graph.add_node(
            CodeNode(
                id=func_id,
                name=node.name,
                symbol_type=symbol_type,
                language="python",
                filepath=str(file_path),
                line_number=node.lineno,
                docstring=doc,
                metadata={"args": args, "is_async": isinstance(node, ast.AsyncFunctionDef)},
            )
        )

        graph.add_edge(
            CodeEdge(
                source_id=parent_id,
                target_id=func_id,
                rel_type=CodeRelationshipType.CONTAINS,
            )
        )

        # Detectar chamadas de funcoes dentro do corpo
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                called_name = self._get_name(child.func)
                if called_name:
                    graph.add_edge(
                        CodeEdge(
                            source_id=func_id,
                            target_id=f"py:func:{called_name}",
                            rel_type=CodeRelationshipType.CALLS,
                            metadata={"called_name": called_name},
                        )
                    )

    def _get_name(self, node: ast.AST) -> str | None:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            val = self._get_name(node.value)
            return f"{val}.{node.attr}" if val else node.attr
        return None
