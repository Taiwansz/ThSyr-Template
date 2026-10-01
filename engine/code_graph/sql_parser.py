"""
Parser de esquemas relacionais SQL deterministico.
Extrai tabelas, colunas, chaves primarias (PK) e relacionamentos de chave estrangeira (FK).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .models import CodeEdge, CodeGraph, CodeNode, CodeRelationshipType, CodeSymbolType


class SQLDDLParser:
    """Disseca instrucoes DDL em arquivos .sql populando o grafo relacional."""

    # Expressao para limpar comentarios
    COMMENT_BLOCK_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
    COMMENT_LINE_RE = re.compile(r"--.*$", re.MULTILINE)

    # Identificacao do cabecalho de CREATE TABLE
    CREATE_TABLE_HEADER_RE = re.compile(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:`?(\w+)`?\.)?`?(\w+)`?\s*\(",
        re.IGNORECASE,
    )

    # Identificacao de ALTER TABLE ADD CONSTRAINT FK
    ALTER_TABLE_FK_RE = re.compile(
        r"ALTER\s+TABLE\s+(?:`?(\w+)`?\.)?`?(\w+)`?\s+ADD\s+(?:CONSTRAINT\s+`?(\w+)`?\s+)?FOREIGN\s+KEY\s*\(`?(\w+)`?\)\s*REFERENCES\s+(?:`?(\w+)`?\.)?`?(\w+)`?\s*\(`?(\w+)`?\)",
        re.IGNORECASE,
    )

    # Constraints inline em CREATE TABLE
    INLINE_FK_RE = re.compile(
        r"(?:CONSTRAINT\s+`?(\w+)`?\s+)?FOREIGN\s+KEY\s*\(`?(\w+)`?\)\s*REFERENCES\s+(?:`?(\w+)`?\.)?`?(\w+)`?\s*\(`?(\w+)`?\)",
        re.IGNORECASE,
    )

    INLINE_PK_RE = re.compile(
        r"PRIMARY\s+KEY\s*\(([^)]+)\)",
        re.IGNORECASE,
    )

    def parse_file(self, file_path: Path, graph: CodeGraph) -> None:
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return

        self.parse_content(content, str(file_path), graph)

    def parse_content(self, content: str, filepath: str, graph: CodeGraph) -> None:
        # Remover comentarios
        sanitized = self.COMMENT_BLOCK_RE.sub("", content)
        sanitized = self.COMMENT_LINE_RE.sub("", sanitized)

        # 1. Parse de CREATE TABLE com extracao exata de corpo balanceado
        for match in self.CREATE_TABLE_HEADER_RE.finditer(sanitized):
            schema_name, table_name = match.groups()
            schema_name = schema_name or "default"
            table_id = f"sql:table:{table_name.lower()}"

            # Extrair corpo delimitado por parenteses balanceados
            start_idx = match.end()
            body_chars: list[str] = []
            depth = 1
            idx = start_idx
            while idx < len(sanitized) and depth > 0:
                char = sanitized[idx]
                if char == "(":
                    depth += 1
                    body_chars.append(char)
                elif char == ")":
                    depth -= 1
                    if depth > 0:
                        body_chars.append(char)
                else:
                    body_chars.append(char)
                idx += 1

            body = "".join(body_chars)

            graph.add_node(
                CodeNode(
                    id=table_id,
                    name=table_name,
                    symbol_type=CodeSymbolType.TABLE,
                    language="sql",
                    filepath=filepath,
                    metadata={"schema": schema_name},
                )
            )

            # Analisar colunas e constraints internas
            self._parse_table_body(table_name, table_id, body, filepath, graph)

        # 2. Parse de ALTER TABLE ... ADD CONSTRAINT FK
        for match in self.ALTER_TABLE_FK_RE.finditer(sanitized):
            src_schema, src_table, fk_name, src_col, tgt_schema, tgt_table, tgt_col = match.groups()
            src_table_id = f"sql:table:{src_table.lower()}"
            tgt_table_id = f"sql:table:{tgt_table.lower()}"

            graph.add_edge(
                CodeEdge(
                    source_id=src_table_id,
                    target_id=tgt_table_id,
                    rel_type=CodeRelationshipType.REFERENCES_FK,
                    metadata={
                        "fk_name": fk_name or f"fk_{src_table}_{tgt_table}",
                        "source_column": src_col,
                        "target_column": tgt_col,
                    },
                )
            )

    def _parse_table_body(
        self,
        table_name: str,
        table_id: str,
        body: str,
        filepath: str,
        graph: CodeGraph,
    ) -> None:
        # Separar declaracoes internas por virgula (respeitando parenteses)
        declarations = self._split_declarations(body)

        primary_keys: set[str] = set()

        # Primeiro passo: detectar inline PRIMARY KEY (...)
        for decl in declarations:
            pk_match = self.INLINE_PK_RE.search(decl)
            if pk_match:
                cols = [c.strip().strip("`").strip('"').lower() for c in pk_match.group(1).split(",")]
                primary_keys.update(cols)

        # Segundo passo: detectar FOREIGN KEY inline
        for decl in declarations:
            fk_match = self.INLINE_FK_RE.search(decl)
            if fk_match:
                fk_name, src_col, tgt_schema, tgt_table, tgt_col = fk_match.groups()
                tgt_table_id = f"sql:table:{tgt_table.lower()}"
                graph.add_edge(
                    CodeEdge(
                        source_id=table_id,
                        target_id=tgt_table_id,
                        rel_type=CodeRelationshipType.REFERENCES_FK,
                        metadata={
                            "fk_name": fk_name or f"fk_{table_name}_{tgt_table}",
                            "source_column": src_col,
                            "target_column": tgt_col,
                        },
                    )
                )

        # Terceiro passo: processar colunas
        for decl in declarations:
            decl_strip = decl.strip()
            if not decl_strip:
                continue

            upper = decl_strip.upper()
            if (
                upper.startswith("PRIMARY KEY")
                or upper.startswith("KEY")
                or upper.startswith("INDEX")
                or upper.startswith("CONSTRAINT")
                or upper.startswith("UNIQUE")
                or upper.startswith("FOREIGN KEY")
                or upper.startswith("CHECK")
            ):
                continue

            # Formato de coluna: `nome_coluna` TIPO ...
            tokens = decl_strip.split(None, 2)
            if not tokens:
                continue

            col_raw_name = tokens[0].strip("`").strip('"')
            col_type = tokens[1].strip(",") if len(tokens) > 1 else "UNKNOWN"

            is_pk = col_raw_name.lower() in primary_keys or "PRIMARY KEY" in upper
            is_nullable = "NOT NULL" not in upper

            col_id = f"sql:col:{table_name.lower()}.{col_raw_name.lower()}"
            graph.add_node(
                CodeNode(
                    id=col_id,
                    name=col_raw_name,
                    symbol_type=CodeSymbolType.COLUMN,
                    language="sql",
                    filepath=filepath,
                    metadata={
                        "data_type": col_type,
                        "primary_key": is_pk,
                        "nullable": is_nullable,
                        "table": table_name,
                    },
                )
            )

            graph.add_edge(
                CodeEdge(
                    source_id=table_id,
                    target_id=col_id,
                    rel_type=CodeRelationshipType.CONTAINS,
                )
            )

    def _split_declarations(self, body: str) -> list[str]:
        items: list[str] = []
        current: list[str] = []
        paren_depth = 0

        for char in body:
            if char == "(":
                paren_depth += 1
                current.append(char)
            elif char == ")":
                paren_depth = max(0, paren_depth - 1)
                current.append(char)
            elif char == "," and paren_depth == 0:
                items.append("".join(current).strip())
                current = []
            else:
                current.append(char)

        if current:
            items.append("".join(current).strip())

        return items
