"""
ThSyr Memory Models (Memory V2)
Define os modelos formais, tipagem e serialização das 4 categorias de memória do ThSyr:
1. Working Memory (Contexto temporário da tarefa/sessão ativa)
2. Episodic Memory (O que aconteceu - diários e registros históricos)
3. Semantic Memory (O que sabemos atualmente - fatos consolidados e decisões)
4. Procedural Memory (Como fazemos algo - SOPs, runbooks e receitas de execução)
"""

import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class MemoryType(str, Enum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    ANALYTICAL = "analytical"


@dataclass
class MemoryMetadata:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    type: str = MemoryType.SEMANTIC.value
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source: str = "interaction"
    confidence: float = 1.0
    importance: float = 0.8
    entities: list[str] = field(default_factory=list)
    projects: list[str] = field(default_factory=list)
    source_commit: str | None = None
    supersedes: str | None = None
    superseded_by: str | None = None
    contradicts: str | None = None
    contradicted_by: str | None = None
    last_verified: str | None = None
    tags: list[str] = field(default_factory=list)

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryMetadata":
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered: dict[str, Any] = {}
        for k, v in data.items():
            if k in valid_keys:
                if k in ("confidence", "importance") and v is not None:
                    try:
                        filtered[k] = float(v)
                    except (ValueError, TypeError):
                        filtered[k] = 1.0 if k == "confidence" else 0.8
                elif k in ("entities", "projects", "tags"):
                    if isinstance(v, list):
                        filtered[k] = [str(x).strip() for x in v if str(x).strip()]
                    elif isinstance(v, str):
                        filtered[k] = [x.strip() for x in v.split(",") if x.strip()]
                    else:
                        filtered[k] = []
                else:
                    filtered[k] = v
        return cls(**filtered)


def dump_yaml_frontmatter(metadata: MemoryMetadata) -> str:
    """Serializa metadados em formato YAML compativel com Obsidian e Dataview sem dependencias externas."""
    lines = ["---"]
    d = metadata.to_dict()

    simple_keys = ["id", "type", "created_at", "updated_at", "source", "confidence", "importance"]
    for k in simple_keys:
        val = d.get(k)
        if val is not None:
            lines.append(f"{k}: {val}")

    if d.get("source_commit"):
        lines.append(f"source_commit: {d['source_commit']}")
    if d.get("supersedes"):
        lines.append(f"supersedes: {d['supersedes']}")
    if d.get("superseded_by"):
        lines.append(f"superseded_by: {d['superseded_by']}")
    if d.get("contradicts"):
        lines.append(f"contradicts: {d['contradicts']}")
    if d.get("contradicted_by"):
        lines.append(f"contradicted_by: {d['contradicted_by']}")
    if d.get("last_verified"):
        lines.append(f"last_verified: {d['last_verified']}")

    list_keys = ["entities", "projects", "tags"]
    for k in list_keys:
        items = d.get(k, [])
        if items:
            lines.append(f"{k}:")
            for item in items:
                lines.append(f"  - {item}")
        else:
            lines.append(f"{k}: []")

    lines.append("---")
    return "\n".join(lines)


def parse_yaml_frontmatter(raw_text: str) -> tuple[dict[str, Any], str]:
    """
    Faz o parse de cabecalho YAML frontmatter (delimitado por ---).
    Retorna o dicionario de metadados e o corpo textual restante.
    """
    stripped = raw_text.strip()
    if not stripped.startswith("---"):
        return {}, raw_text

    parts = stripped.split("---", 2)
    if len(parts) < 3:
        return {}, raw_text

    yaml_block = parts[1]
    body = parts[2].lstrip("\n")

    metadata: dict[str, Any] = {}
    current_list_key = None

    for line in yaml_block.splitlines():
        line_clean = line.strip()
        if not line_clean or line_clean.startswith("#"):
            continue

        if line_clean.startswith("- ") and current_list_key:
            item_val = line_clean[2:].strip().strip("\"'")
            if item_val:
                metadata[current_list_key].append(item_val)
            continue

        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()

            if val == "" or val == "[]":
                if val == "[]":
                    metadata[key] = []
                else:
                    metadata[key] = []
                    current_list_key = key
            elif val.startswith("[") and val.endswith("]"):
                inner = val[1:-1].strip()
                metadata[key] = [x.strip().strip("\"'") for x in inner.split(",") if x.strip()]
                current_list_key = None
            else:
                clean_val: Optional[str] = val.strip("\"'")
                if clean_val and (clean_val.lower() == "null" or clean_val.lower() == "none"):
                    clean_val = None
                metadata[key] = clean_val
                current_list_key = None

    return metadata, body


@dataclass
class MemoryItem:
    metadata: MemoryMetadata
    title: str
    content: str
    filepath: Path | None = None

    @property
    def id(self) -> str:
        return self.metadata.id

    @property
    def memory_type(self) -> str:
        return self.metadata.type

    def to_markdown(self) -> str:
        frontmatter = dump_yaml_frontmatter(self.metadata)
        header = f"# {self.title}\n\n" if not self.content.lstrip().startswith("# ") else ""
        return f"{frontmatter}\n\n{header}{self.content.strip()}\n"

    @classmethod
    def from_markdown(
        cls,
        text: str,
        filepath: Path | None = None,
        fallback_type: str = MemoryType.SEMANTIC.value
    ) -> "MemoryItem":
        meta_dict, body = parse_yaml_frontmatter(text)

        # Extrair título da primeira linha de cabeçalho ou do nome do arquivo
        title = ""
        first_h1 = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
        if first_h1:
            title = first_h1.group(1).strip()
        elif filepath:
            title = filepath.stem.replace("_", " ").title()
        else:
            title = "Registro de Memoria"

        if "type" not in meta_dict:
            meta_dict["type"] = fallback_type
        if "id" not in meta_dict:
            meta_dict["id"] = filepath.stem if filepath else uuid.uuid4().hex[:8]

        metadata = MemoryMetadata.from_dict(meta_dict)
        return cls(metadata=metadata, title=title, content=body, filepath=filepath)

    def to_dict(self) -> dict[str, Any]:
        return {
            "metadata": self.metadata.to_dict(),
            "title": self.title,
            "content": self.content,
            "filepath": str(self.filepath) if self.filepath else None
        }
