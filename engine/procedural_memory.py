"""
ThSyr Procedural Memory Manager
Gerencia a memória procedural (Procedural Memory) do ThSyr:
armazena e recupera procedimentos operacionais padrão (SOPs), runbooks de engenharia,
regras de design e receitas de execução contínua.
"""

import re
from pathlib import Path

from .config import settings, setup_logger
from .memory_models import MemoryItem, MemoryMetadata, MemoryType

logger = setup_logger("procedural_memory")


class ProceduralMemoryManager:
    def __init__(self, brain_dir: Path | None = None):
        self.brain_dir = brain_dir or settings.brain.brain_dir
        self.procedural_dir = self.brain_dir / "memories" / "procedural"
        self._ensure_dir()

    def _ensure_dir(self) -> None:
        self.procedural_dir.mkdir(parents=True, exist_ok=True)

    def save_procedure(
        self,
        name: str,
        title: str,
        content: str,
        projects: list[str] | None = None,
        entities: list[str] | None = None,
        tags: list[str] | None = None,
        importance: float = 0.85
    ) -> Path:
        slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", name.lower().strip()).strip("_")
        filepath = self.procedural_dir / f"{slug}.md"

        meta = MemoryMetadata(
            id=f"proc_{slug}",
            type=MemoryType.PROCEDURAL.value,
            source="canonical_procedure",
            confidence=1.0,
            importance=importance,
            entities=entities or ["Operador"],
            projects=projects or ["Copilot"],
            tags=tags or ["procedure", "runbook"]
        )

        item = MemoryItem(metadata=meta, title=title, content=content, filepath=filepath)
        filepath.write_text(item.to_markdown(), encoding="utf-8")
        logger.info(f"Procedimento salvo: {filepath.name}")
        return filepath

    def get_procedure(self, name: str) -> MemoryItem | None:
        slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", name.lower().strip()).strip("_")
        direct = self.procedural_dir / f"{slug}.md"
        if direct.exists():
            return MemoryItem.from_markdown(
                direct.read_text(encoding="utf-8"),
                filepath=direct,
                fallback_type=MemoryType.PROCEDURAL.value
            )

        # Busca por correspondência aproximada
        for f in self.procedural_dir.glob("*.md"):
            if slug in f.stem.lower():
                return MemoryItem.from_markdown(
                    f.read_text(encoding="utf-8"),
                    filepath=f,
                    fallback_type=MemoryType.PROCEDURAL.value
                )
        return None

    def list_procedures(self) -> list[MemoryItem]:
        items = []
        for f in sorted(self.procedural_dir.glob("*.md")):
            try:
                item = MemoryItem.from_markdown(
                    f.read_text(encoding="utf-8"),
                    filepath=f,
                    fallback_type=MemoryType.PROCEDURAL.value
                )
                items.append(item)
            except Exception as e:
                logger.warning(f"Erro ao ler procedimento {f.name}: {e}")
        return items

    def search_procedures(self, query: str) -> list[MemoryItem]:
        q = query.lower().strip()
        matched = []
        for p in self.list_procedures():
            if q in p.title.lower() or q in p.content.lower() or any(q in t.lower() for t in p.metadata.tags):
                matched.append(p)
        return matched
