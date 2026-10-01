"""
ThSyr Memory Manager V2
Gerencia e orquestra as quatro categorias formais de memória do ThSyr:
1. Working Memory (memória de trabalho ativa da sessão)
2. Episodic Memory (histórico cronológico e diários de sessões)
3. Semantic Memory (fatos consolidados, projetos e decisões)
4. Procedural Memory (SOPs, runbooks e procedimentos de execução)

Inclui indexação com metadados tipados (entidades, projetos, tags, importância)
e suporte completo a YAML frontmatter legível pelo Obsidian.
"""

import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .config import settings, setup_logger
from .memory_contradiction import MemoryContradictionDetector
from .memory_models import MemoryItem, MemoryMetadata, MemoryType
from .procedural_memory import ProceduralMemoryManager
from .working_memory import WorkingMemory

logger = setup_logger("memory_manager")


class MemoryManager:
    def __init__(self, root: Path | None = None, state_dir: Path | None = None):
        self.root = root or settings.brain.brain_dir
        self.state_dir = state_dir or settings.brain.state_dir

        self.core_dir = self.root / "core"
        self.profile_dir = self.root / "profile"
        self.episodic_dir = self.root / "memories" / "episodic"
        self.semantic_dir = self.root / "memories" / "semantic"
        self.procedural_dir = self.root / "memories" / "procedural"
        self.analytical_dir = self.root / "memories" / "analytical"

        self._ensure_dirs()
        self.working = WorkingMemory(state_dir=self.state_dir)
        self.procedural = ProceduralMemoryManager(brain_dir=self.root)

    def _ensure_dirs(self) -> None:
        self.core_dir.mkdir(parents=True, exist_ok=True)
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.episodic_dir.mkdir(parents=True, exist_ok=True)
        self.semantic_dir.mkdir(parents=True, exist_ok=True)
        self.procedural_dir.mkdir(parents=True, exist_ok=True)
        self.analytical_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------
    # 1. CORE & PERFIL
    # -------------------------------------------------------------
    def get_personality(self) -> str:
        path = self.core_dir / "personality.md"
        return path.read_text(encoding="utf-8") if path.exists() else ""

    def get_user_profile(self) -> str:
        path = self.profile_dir / "user.md"
        return path.read_text(encoding="utf-8") if path.exists() else ""

    # -------------------------------------------------------------
    # 2. WORKING MEMORY
    # -------------------------------------------------------------
    def get_working_memory_item(self) -> MemoryItem:
        return self.working.to_memory_item()

    def update_working_focus(self, focus: str, project: str | None = None, entities: list[str] | None = None) -> None:
        self.working.update_focus(focus, project, entities)

    # -------------------------------------------------------------
    # 3. EPISODIC MEMORY
    # -------------------------------------------------------------
    def count_total_episodic_logs(self) -> int:
        if not self.episodic_dir.exists():
            return 0
        return len(list(self.episodic_dir.glob("*.md")))

    def get_recent_episodic_logs(self, limit: int = 3) -> list[dict[str, str]]:
        if not self.episodic_dir.exists():
            return []
        files = sorted(self.episodic_dir.glob("*.md"), reverse=True)[:limit]
        logs = []
        for f in files:
            logs.append({"filename": f.name, "content": f.read_text(encoding="utf-8")})
        return logs

    def get_episodic_items(self, limit: int = 10) -> list[MemoryItem]:
        if not self.episodic_dir.exists():
            return []
        files = sorted(self.episodic_dir.glob("*.md"), reverse=True)[:limit]
        items = []
        for f in files:
            try:
                items.append(MemoryItem.from_markdown(
                    f.read_text(encoding="utf-8"),
                    filepath=f,
                    fallback_type=MemoryType.EPISODIC.value
                ))
            except Exception as e:
                logger.warning(f"Erro ao carregar log episodico {f.name}: {e}")
        return items

    def append_episodic_log(
        self,
        title: str,
        content: str,
        session_id: str | None = None,
        entities: list[str] | None = None,
        projects: list[str] | None = None,
        tags: list[str] | None = None,
        importance: float = 0.8
    ) -> Path:
        now = datetime.now(timezone.utc)
        timestamp_str = now.strftime("%Y-%m-%dT%H-%M-%SZ")
        short_id = (session_id[-6:] if session_id else uuid.uuid4().hex[:6])
        slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", title.lower().strip())[:30].strip("_")
        if not slug:
            slug = "session"

        filename = f"{timestamp_str}_{short_id}_{slug}.md"
        target = self.episodic_dir / filename

        meta = MemoryMetadata(
            id=f"epi_{short_id}",
            type=MemoryType.EPISODIC.value,
            created_at=now.isoformat(),
            updated_at=now.isoformat(),
            source="manual_log" if not session_id else "session_checkpoint",
            confidence=1.0,
            importance=importance,
            entities=entities or ["Operador"],
            projects=projects or ["Copilot"],
            tags=tags or ["session", "log"]
        )

        item = MemoryItem(metadata=meta, title=title, content=content, filepath=target)
        target.write_text(item.to_markdown(), encoding="utf-8")
        logger.info(f"Episodio registrado: {filename}")
        return target

    # -------------------------------------------------------------
    # 4. SEMANTIC MEMORY
    # -------------------------------------------------------------
    def get_semantic_memories(self) -> dict[str, str]:
        memories = {}
        if self.semantic_dir.exists():
            for md_file in sorted(self.semantic_dir.glob("*.md")):
                memories[md_file.stem] = md_file.read_text(encoding="utf-8")
        return memories

    def get_semantic_items(self) -> list[MemoryItem]:
        items: list[MemoryItem] = []
        if not self.semantic_dir.exists():
            return items
        for md_file in sorted(self.semantic_dir.glob("*.md")):
            try:
                items.append(MemoryItem.from_markdown(
                    md_file.read_text(encoding="utf-8"),
                    filepath=md_file,
                    fallback_type=MemoryType.SEMANTIC.value
                ))
            except Exception as e:
                logger.warning(f"Erro ao carregar memoria semantica {md_file.name}: {e}")
        return items

    def save_semantic_memory(
        self,
        name: str,
        title: str,
        content: str,
        entities: list[str] | None = None,
        projects: list[str] | None = None,
        tags: list[str] | None = None,
        importance: float = 0.85
    ) -> Path:
        slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", name.lower().strip()).strip("_")
        filepath = self.semantic_dir / f"{slug}.md"

        existing_items = [
            item for item in self.get_semantic_items()
            if item.metadata.id != f"sem_{slug}"
        ]
        contradictions = MemoryContradictionDetector.detect(
            title=title,
            content=content,
            candidates=existing_items,
        )
        strongest = contradictions[0] if contradictions else None
        effective_tags = list(tags or ["knowledge", "fact"])
        if strongest and "contradiction-detected" not in effective_tags:
            effective_tags.append("contradiction-detected")

        meta = MemoryMetadata(
            id=f"sem_{slug}",
            type=MemoryType.SEMANTIC.value,
            source="semantic_consolidation",
            confidence=1.0,
            importance=importance,
            entities=entities or ["Operador"],
            projects=projects or ["Copilot"],
            tags=effective_tags,
            contradicts=strongest.memory_id if strongest else None,
        )

        item = MemoryItem(metadata=meta, title=title, content=content, filepath=filepath)
        filepath.write_text(item.to_markdown(), encoding="utf-8")

        if strongest:
            for previous in existing_items:
                if previous.metadata.id != strongest.memory_id or previous.filepath is None:
                    continue
                previous.metadata.contradicted_by = meta.id
                previous.metadata.touch()
                previous.filepath.write_text(previous.to_markdown(), encoding="utf-8")
                break
            logger.warning(
                "Contradicao semantica detectada entre %s e %s (score %.3f)",
                meta.id,
                strongest.memory_id,
                strongest.score,
            )

        logger.info(f"Memoria semantica salva: {filepath.name}")
        return filepath

    # -------------------------------------------------------------
    # 5. PROCEDURAL MEMORY
    # -------------------------------------------------------------
    def get_procedural_items(self) -> list[MemoryItem]:
        return self.procedural.list_procedures()

    def get_procedure(self, name: str) -> MemoryItem | None:
        return self.procedural.get_procedure(name)

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
        return self.procedural.save_procedure(
            name=name,
            title=title,
            content=content,
            projects=projects,
            entities=entities,
            tags=tags,
            importance=importance
        )

    # -------------------------------------------------------------
    # 6. ANALYTICAL MEMORY (DEDUÇÕES DE SEGUNDA ORDEM & META-COGNIÇÃO)
    # -------------------------------------------------------------
    def count_total_analytical_memories(self) -> int:
        if not self.analytical_dir.exists():
            return 0
        return len(list(self.analytical_dir.glob("*.md")))

    def get_recent_analytical_logs(self, limit: int = 3) -> list[dict[str, str]]:
        if not self.analytical_dir.exists():
            return []
        files = sorted(self.analytical_dir.glob("*.md"), reverse=True)[:limit]
        logs = []
        for f in files:
            logs.append({"filename": f.name, "content": f.read_text(encoding="utf-8")})
        return logs

    def get_analytical_items(self, limit: int = 10) -> list[MemoryItem]:
        if not self.analytical_dir.exists():
            return []
        files = sorted(self.analytical_dir.glob("*.md"), reverse=True)[:limit]
        items = []
        for f in files:
            try:
                items.append(MemoryItem.from_markdown(
                    f.read_text(encoding="utf-8"),
                    filepath=f,
                    fallback_type=MemoryType.ANALYTICAL.value
                ))
            except Exception as e:
                logger.warning(f"Erro ao carregar memoria analitica {f.name}: {e}")
        return items

    def save_analytical_memory(
        self,
        title: str,
        content: str,
        session_id: str | None = None,
        entities: list[str] | None = None,
        projects: list[str] | None = None,
        tags: list[str] | None = None,
        importance: float = 0.95,
        confidence: float = 0.95
    ) -> Path:
        now = datetime.now(timezone.utc)
        timestamp_str = now.strftime("%Y-%m-%d")
        slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", title.lower().strip())[:40].strip("_")
        if not slug:
            slug = "deducoes"

        filename = f"{timestamp_str}_{slug}.md"
        target = self.analytical_dir / filename

        meta = MemoryMetadata(
            id=f"ana_{uuid.uuid4().hex[:6]}",
            type=MemoryType.ANALYTICAL.value,
            created_at=now.isoformat(),
            updated_at=now.isoformat(),
            source="analytical_deduction",
            confidence=confidence,
            importance=importance,
            entities=entities or ["Operador"],
            projects=projects or ["Copilot"],
            tags=tags or ["meta-cognicao", "analise-comportamental", "deducoes-segunda-ordem"]
        )

        item = MemoryItem(metadata=meta, title=title, content=content, filepath=target)
        target.write_text(item.to_markdown(), encoding="utf-8")
        logger.info(f"Memoria analitica salva: {filename}")
        return target

    # -------------------------------------------------------------
    # 7. UNIFIED QUERY & SEARCH INTERFACE
    # -------------------------------------------------------------
    def query(
        self,
        memory_type: MemoryType | None = None,
        entity: str | None = None,
        project: str | None = None,
        tag: str | None = None,
        min_importance: float = 0.0,
        limit: int = 50
    ) -> list[MemoryItem]:
        candidates: list[MemoryItem] = []

        # Determinar quais categorias examinar
        types_to_fetch = [memory_type] if memory_type else [
            MemoryType.WORKING,
            MemoryType.ANALYTICAL,
            MemoryType.PROCEDURAL,
            MemoryType.SEMANTIC,
            MemoryType.EPISODIC
        ]

        for t in types_to_fetch:
            if t == MemoryType.WORKING:
                candidates.append(self.get_working_memory_item())
            elif t == MemoryType.ANALYTICAL:
                candidates.extend(self.get_analytical_items(limit=25))
            elif t == MemoryType.PROCEDURAL:
                candidates.extend(self.get_procedural_items())
            elif t == MemoryType.SEMANTIC:
                candidates.extend(self.get_semantic_items())
            elif t == MemoryType.EPISODIC:
                candidates.extend(self.get_episodic_items(limit=25))

        filtered = []
        for item in candidates:
            meta = item.metadata
            if meta.importance < min_importance:
                continue
            if entity and not any(entity.lower() in e.lower() for e in meta.entities):
                continue
            if project and not any(project.lower() in p.lower() for p in meta.projects):
                continue
            if tag and not any(tag.lower() in t.lower() for t in meta.tags):
                continue
            filtered.append(item)
            if len(filtered) >= limit:
                break

        return filtered

    # -------------------------------------------------------------
    # 7. COMPACT CONTEXT BUILDER
    # -------------------------------------------------------------
    def build_compact_context(
        self,
        active_seeds: list[str] | None = None,
        max_semantics: int = 5,
        include_procedures: bool = True,
        include_working: bool = True
    ) -> str:
        personality = self.get_personality()
        user_profile = self.get_user_profile()
        semantics = self.get_semantic_memories()

        selected_semantics = {}
        if active_seeds:
            lower_seeds = [s.lower() for s in active_seeds]
            for key, val in semantics.items():
                if any(s in key.lower() or s in val.lower() for s in lower_seeds):
                    selected_semantics[key] = val
                    if len(selected_semantics) >= max_semantics:
                        break

        if len(selected_semantics) < max_semantics:
            for key, val in semantics.items():
                if key not in selected_semantics:
                    selected_semantics[key] = val
                    if len(selected_semantics) >= max_semantics:
                        break

        prompt_parts = [
            "# INSTRUÇÕES MESTRAS DE PERSONALIDADE (THSYR)",
            personality,
            "\n# PERFIL DO OPERADOR",
            user_profile,
        ]

        if include_working and self.working.focus:
            prompt_parts.append("\n# MEMÓRIA DE TRABALHO (WORKING MEMORY)")
            prompt_parts.append(f"- Foco Atual: {self.working.focus}")
            prompt_parts.append(f"- Projeto Ativo: {self.working.project}")
            if self.working.scratchpad:
                prompt_parts.append(f"- Scratchpad: {'; '.join(self.working.scratchpad[-3:])}")

        prompt_parts.append("\n# MEMÓRIAS SEMÂNTICAS RELEVANTES")
        for name, text in selected_semantics.items():
            prompt_parts.append(f"## {name.upper()}\n{text[:1200]}\n")

        if include_procedures:
            procs = self.get_procedural_items()
            if procs:
                prompt_parts.append("\n# PROCEDIMENTOS RELEVANTES (PROCEDURAL MEMORY)")
                for p in procs[:3]:
                    prompt_parts.append(f"### [[{p.metadata.id}]] {p.title}\n{p.content[:600]}\n")

        analytical_items = self.get_analytical_items(limit=2)
        if analytical_items:
            prompt_parts.append("\n# DEDUÇÕES ANALÍTICAS E META-COGNIÇÃO RECENTES (ANALYTICAL MEMORY)")
            for a in analytical_items:
                prompt_parts.append(f"### [[{a.metadata.id}]] {a.title}\n{a.content[:800]}\n")

        recents = self.get_recent_episodic_logs(limit=2)
        if recents:
            prompt_parts.append("\n# MEMÓRIAS EPISÓDICAS RECENTES")
            for r in recents:
                prompt_parts.append(f"### {r['filename']}\n{r['content'][:600]}\n")

        return "\n".join(prompt_parts)

    def build_system_prompt(self) -> str:
        return self.build_compact_context(max_semantics=8)
