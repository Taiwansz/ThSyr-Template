"""
ThSyr Working Memory Manager
Gerencia a memória de trabalho (Working Memory) de curto prazo:
mantém o foco ativo, o scratchpad temporário, variáveis operacionais e restrições
da tarefa em andamento.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import settings, setup_logger
from .memory_models import MemoryItem, MemoryMetadata, MemoryType

logger = setup_logger("working_memory")


class WorkingMemory:
    def __init__(self, state_dir: Path | None = None):
        self.state_dir = state_dir or settings.brain.state_dir
        self.working_file = self.state_dir / "working_memory.json"
        self.focus: str = ""
        self.project: str = "Copilot"
        self.active_entities: list[str] = ["Operador"]
        self.scratchpad: list[str] = []
        self.variables: dict[str, Any] = {}
        self.active_constraints: list[str] = []
        self.last_updated: str = datetime.now(timezone.utc).isoformat()
        self.load()

    def update_focus(self, focus: str, project: str | None = None, entities: list[str] | None = None) -> None:
        self.focus = focus
        if project:
            self.project = project
        if entities:
            self.active_entities = list(set(self.active_entities + entities))
        self.touch()
        self.save()

    def append_scratchpad(self, note: str) -> None:
        self.scratchpad.append(note)
        self.touch()
        self.save()

    def set_variable(self, key: str, value: Any) -> None:
        self.variables[key] = value
        self.touch()
        self.save()

    def get_variable(self, key: str, default: Any = None) -> Any:
        return self.variables.get(key, default)

    def set_constraints(self, constraints: list[str]) -> None:
        self.active_constraints = constraints
        self.touch()
        self.save()

    def clear_scratchpad(self) -> None:
        self.scratchpad.clear()
        self.touch()
        self.save()

    def touch(self) -> None:
        self.last_updated = datetime.now(timezone.utc).isoformat()

    def save(self) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "focus": self.focus,
            "project": self.project,
            "active_entities": self.active_entities,
            "scratchpad": self.scratchpad,
            "variables": self.variables,
            "active_constraints": self.active_constraints,
            "last_updated": self.last_updated
        }
        self.working_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def load(self) -> None:
        if not self.working_file.exists():
            return
        try:
            data = json.loads(self.working_file.read_text(encoding="utf-8"))
            self.focus = data.get("focus", "")
            self.project = data.get("project", "Copilot")
            self.active_entities = data.get("active_entities", ["Operador"])
            self.scratchpad = data.get("scratchpad", [])
            self.variables = data.get("variables", {})
            self.active_constraints = data.get("active_constraints", [])
            self.last_updated = data.get("last_updated", datetime.now(timezone.utc).isoformat())
        except Exception as e:
            logger.warning(f"Falha ao carregar working memory: {e}")

    def to_memory_item(self) -> MemoryItem:
        body_lines = [
            f"**Foco:** {self.focus or 'Nenhum foco ativo'}",
            f"**Projeto:** {self.project}",
            "",
            "### Scratchpad:",
        ]
        if self.scratchpad:
            for note in self.scratchpad:
                body_lines.append(f"- {note}")
        else:
            body_lines.append("- (Vazio)")

        if self.active_constraints:
            body_lines.append("\n### Restricoes Operacionais Ativas:")
            for c in self.active_constraints:
                body_lines.append(f"- {c}")

        meta = MemoryMetadata(
            id="working_memory_active",
            type=MemoryType.WORKING.value,
            source="session_runtime",
            confidence=1.0,
            importance=0.9,
            entities=self.active_entities,
            projects=[self.project],
            tags=["working_memory", "active_context"]
        )
        return MemoryItem(
            metadata=meta,
            title="Memoria de Trabalho Ativa",
            content="\n".join(body_lines),
            filepath=self.working_file
        )
