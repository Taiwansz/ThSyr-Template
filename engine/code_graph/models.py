"""
ThSyr Code Graph & Structural GraphRAG Engine (Graphify Paradigm)
Modelos de dados fortemente tipados para representacao de grafos de codigo:
classes, metodos, funcoes, chamadas, heranca e esquemas relacionais SQL.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class CodeSymbolType(str, Enum):
    MODULE = "module"
    CLASS = "class"
    INTERFACE = "interface"
    METHOD = "method"
    FUNCTION = "function"
    TABLE = "table"
    COLUMN = "column"


class CodeRelationshipType(str, Enum):
    CONTAINS = "contains"
    CALLS = "calls"
    INHERITS = "inherits"
    IMPLEMENTS = "implements"
    IMPORTS = "imports"
    REFERENCES_FK = "references_fk"


@dataclass
class CodeNode:
    id: str
    name: str
    symbol_type: CodeSymbolType
    language: str  # python, java, sql
    filepath: str
    line_number: int = 1
    docstring: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["symbol_type"] = self.symbol_type.value
        return d


@dataclass
class CodeEdge:
    source_id: str
    target_id: str
    rel_type: CodeRelationshipType
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["rel_type"] = self.rel_type.value
        return d


@dataclass
class CodeGraph:
    nodes: dict[str, CodeNode] = field(default_factory=dict)
    edges: list[CodeEdge] = field(default_factory=list)

    def add_node(self, node: CodeNode) -> None:
        self.nodes[node.id] = node

    def add_edge(self, edge: CodeEdge) -> None:
        self.edges.append(edge)

    def get_callees(self, symbol_id: str) -> list[str]:
        return [
            e.target_id
            for e in self.edges
            if e.source_id == symbol_id and e.rel_type == CodeRelationshipType.CALLS
        ]

    def get_callers(self, symbol_id: str) -> list[str]:
        return [
            e.source_id
            for e in self.edges
            if e.target_id == symbol_id and e.rel_type == CodeRelationshipType.CALLS
        ]

    def get_foreign_keys(self, table_id: str) -> list[CodeEdge]:
        return [
            e
            for e in self.edges
            if e.source_id == table_id and e.rel_type == CodeRelationshipType.REFERENCES_FK
        ]

    def summary(self) -> dict[str, Any]:
        by_type: dict[str, int] = {}
        by_lang: dict[str, int] = {}
        for n in self.nodes.values():
            by_type[n.symbol_type.value] = by_type.get(n.symbol_type.value, 0) + 1
            by_lang[n.language] = by_lang.get(n.language, 0) + 1

        by_rel: dict[str, int] = {}
        for e in self.edges:
            by_rel[e.rel_type.value] = by_rel.get(e.rel_type.value, 0) + 1

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "nodes_by_type": by_type,
            "nodes_by_language": by_lang,
            "edges_by_relationship": by_rel,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges],
            "summary": self.summary(),
        }
