"""
Parser de codigo Java baseado em analise estrutural e gramatical deterministica.
Extrai pacotes, classes, interfaces, heranca (extends/implements) e metodos.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .models import CodeEdge, CodeGraph, CodeNode, CodeRelationshipType, CodeSymbolType


class JavaStructuralParser:
    """Disseca codigo-fonte Java (.java) mapeando POO estrita para o grafo."""

    CLASS_PATTERN = re.compile(
        r"(?:public\s+|private\s+|protected\s+)?(?:abstract\s+)?(class|interface)\s+([A-Za-z0-9_]+)"
        r"(?:\s+extends\s+([A-Za-z0-9_]+))?"
        r"(?:\s+implements\s+([A-Za-z0-9_,\s]+))?"
    )

    METHOD_PATTERN = re.compile(
        r"(?:public|protected|private|static|\s)+[\w\<\>\[\]]+\s+([A-Za-z0-9_]+)\s*\(([^)]*)\)\s*\{"
    )

    PACKAGE_PATTERN = re.compile(r"^\s*package\s+([A-Za-z0-9_.]+)\s*;", re.MULTILINE)
    IMPORT_PATTERN = re.compile(r"^\s*import\s+([A-Za-z0-9_.]+)\s*;", re.MULTILINE)

    def parse_file(self, file_path: Path, graph: CodeGraph) -> None:
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return

        lines = content.splitlines()

        # Pacote
        pkg_match = self.PACKAGE_PATTERN.search(content)
        pkg_name = pkg_match.group(1) if pkg_match else "default"

        # Imports
        imports = [m.group(1) for m in self.IMPORT_PATTERN.finditer(content)]

        # Encontrar classes / interfaces
        for lineno, line in enumerate(lines, 1):
            class_match = self.CLASS_PATTERN.search(line)
            if not class_match:
                continue

            kind, class_name, extends_class, implements_list = class_match.groups()
            symbol_type = CodeSymbolType.INTERFACE if kind == "interface" else CodeSymbolType.CLASS

            class_id = f"java:{kind}:{pkg_name}.{class_name}"
            implements = [i.strip() for i in implements_list.split(",")] if implements_list else []

            graph.add_node(
                CodeNode(
                    id=class_id,
                    name=class_name,
                    symbol_type=symbol_type,
                    language="java",
                    filepath=str(file_path),
                    line_number=lineno,
                    metadata={
                        "package": pkg_name,
                        "extends": extends_class,
                        "implements": implements,
                        "imports": imports,
                    },
                )
            )

            # Relacoes de Heranca
            if extends_class:
                graph.add_edge(
                    CodeEdge(
                        source_id=class_id,
                        target_id=f"java:class:{extends_class}",
                        rel_type=CodeRelationshipType.INHERITS,
                        metadata={"type": "extends"},
                    )
                )

            # Relacoes de Implementacao de Interface
            for iface in implements:
                graph.add_edge(
                    CodeEdge(
                        source_id=class_id,
                        target_id=f"java:interface:{iface}",
                        rel_type=CodeRelationshipType.IMPLEMENTS,
                        metadata={"type": "implements"},
                    )
                )

            # Metodos dentro da classe
            for m_lineno, m_line in enumerate(lines, 1):
                method_match = self.METHOD_PATTERN.search(m_line)
                if method_match:
                    m_name, m_params = method_match.groups()
                    if m_name in ("if", "for", "while", "switch", "catch"):
                        continue
                    method_id = f"java:method:{class_name}.{m_name}"
                    graph.add_node(
                        CodeNode(
                            id=method_id,
                            name=m_name,
                            symbol_type=CodeSymbolType.METHOD,
                            language="java",
                            filepath=str(file_path),
                            line_number=m_lineno,
                            metadata={"params": m_params.strip()},
                        )
                    )
                    graph.add_edge(
                        CodeEdge(
                            source_id=class_id,
                            target_id=method_id,
                            rel_type=CodeRelationshipType.CONTAINS,
                        )
                    )
