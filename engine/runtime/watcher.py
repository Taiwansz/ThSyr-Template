"""Sensory workspace watcher with deterministic polling and event persistence."""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

from ..config import get_state_dir, setup_logger
from ..working_memory import WorkingMemory
from .events import RuntimeEventBus

logger = setup_logger("workspace_watcher")

DEFAULT_IGNORED_DIRECTORIES = frozenset({
    ".git", ".next", "__pycache__", "build", "dist", "node_modules", "target",
})
DEFAULT_IGNORED_SUFFIXES = frozenset({
    ".pyc", ".pyo", ".class", ".tmp", ".swp", ".swo", ".log",
})
HIGH_SIGNAL_PARTS = frozenset({"auth", "webhook", "rls", "security", ".env"})


@dataclass(frozen=True)
class FileSnapshot:
    relative_path: str
    size: int
    modified_ns: int
    digest: str


@dataclass(frozen=True)
class WorkspaceMutationEvent:
    workspace: str
    files: tuple[str, ...]
    kinds: tuple[str, ...]
    occurred_at: str
    event_type: str = "workspace_mutation"
    schema_version: int = 1
    correlation_id: str = field(default_factory=lambda: uuid4().hex)
    coalesced: bool = False
    analysis: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class EventStore:
    """Atomically persists watcher batches as JSON files."""

    def __init__(self, state_dir: Path | None = None):
        self.events_dir = (state_dir or get_state_dir()) / "events"
        self.events_dir.mkdir(parents=True, exist_ok=True)

    def append(self, event: WorkspaceMutationEvent) -> Path:
        timestamp = event.occurred_at.replace(":", "").replace("-", "").replace(".", "")
        target = self.events_dir / f"workspace_mutation_{timestamp}_{event.correlation_id}.json"
        temporary = target.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(event.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        temporary.replace(target)
        return target

    def recent(self, limit: int = 20) -> list[dict[str, Any]]:
        files = sorted(self.events_dir.glob("workspace_mutation_*.json"), reverse=True)[:limit]
        records: list[dict[str, Any]] = []
        for path in files:
            try:
                records.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError) as exc:
                logger.warning("Evento inválido ignorado em %s: %s", path, exc)
        return records


class PollingWatcher:
    """Cross-platform watcher suitable for deterministic tests and fallback runtime."""

    def __init__(
        self,
        workspaces: Iterable[Path],
        debounce_seconds: float = 5.0,
        ignored_directories: frozenset[str] = DEFAULT_IGNORED_DIRECTORIES,
        ignored_suffixes: frozenset[str] = DEFAULT_IGNORED_SUFFIXES,
        max_file_size: int = 10 * 1024 * 1024,
    ):
        self.workspaces = tuple(path.resolve() for path in workspaces)
        self.debounce_seconds = max(0.0, debounce_seconds)
        self.ignored_directories = ignored_directories
        self.ignored_suffixes = ignored_suffixes
        self.max_file_size = max_file_size
        self._snapshots: dict[Path, dict[str, FileSnapshot]] = {}
        self._pending: dict[tuple[Path, str], tuple[str, float]] = {}
        self._initialized = False

    def _is_ignored(self, path: Path) -> bool:
        if any(part in self.ignored_directories for part in path.parts):
            return True
        return path.suffix.lower() in self.ignored_suffixes

    def _digest(self, path: Path) -> str:
        hasher = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _snapshot_workspace(self, workspace: Path) -> dict[str, FileSnapshot]:
        if not workspace.is_dir():
            return {}
        snapshots: dict[str, FileSnapshot] = {}
        for path in workspace.rglob("*"):
            if not path.is_file() or self._is_ignored(path):
                continue
            try:
                stat = path.stat()
                if stat.st_size > self.max_file_size:
                    continue
                relative = path.relative_to(workspace).as_posix()
                snapshots[relative] = FileSnapshot(relative, stat.st_size, stat.st_mtime_ns, self._digest(path))
            except OSError as exc:
                logger.debug("Falha ao observar %s: %s", path, exc)
        return snapshots

    def _detect(self, workspace: Path, current: dict[str, FileSnapshot], event_time: float) -> None:
        previous = self._snapshots.get(workspace, {})
        for relative in current.keys() - previous.keys():
            self._pending[(workspace, relative)] = ("created", event_time)
        for relative in previous.keys() - current.keys():
            self._pending[(workspace, relative)] = ("deleted", event_time)
        for relative in current.keys() & previous.keys():
            if current[relative] != previous[relative]:
                self._pending[(workspace, relative)] = ("modified", event_time)
        self._snapshots[workspace] = current

    def poll(self, now: float | None = None) -> list[WorkspaceMutationEvent]:
        current_time = time.monotonic() if now is None else now
        for workspace in self.workspaces:
            self._detect(workspace, self._snapshot_workspace(workspace), current_time)
        if not self._initialized:
            self._pending.clear()
            self._initialized = True
            return []

        ready: dict[Path, list[tuple[str, str]]] = {}
        for key, (kind, first_seen) in list(self._pending.items()):
            # Synthetic clocks used by tests and some schedulers can land a few
            # floating-point ulps below the exact debounce boundary.
            elapsed = current_time - first_seen
            if elapsed + 1e-9 < self.debounce_seconds:
                continue
            workspace, relative = key
            ready.setdefault(workspace, []).append((relative, kind))
            del self._pending[key]

        occurred_at = datetime.now(timezone.utc).isoformat()
        return [
            WorkspaceMutationEvent(
                workspace=workspace.name,
                files=tuple(sorted(item[0] for item in items)),
                kinds=tuple(sorted({item[1] for item in items})),
                occurred_at=occurred_at,
                coalesced=len(items) > 1,
            )
            for workspace, items in sorted(ready.items(), key=lambda item: str(item[0]))
        ]


class WindowsCompatibleWatcher(PollingWatcher):
    """Windows-specific selection point with safe polling semantics.

    The implementation remains dependency-free and deterministic while
    preserving a backend boundary for a future ReadDirectoryChangesW adapter.
    """

    backend = "windows-compatible-polling"

    def __init__(self, *args: Any, **kwargs: Any):
        if os.name != "nt":
            raise RuntimeError("NativeWindowsWatcher requer Windows.")
        super().__init__(*args, **kwargs)


def create_watcher(workspaces: Iterable[Path], debounce_seconds: float = 5.0) -> PollingWatcher:
    if os.name == "nt":
        try:
            return WindowsCompatibleWatcher(workspaces, debounce_seconds=debounce_seconds)
        except RuntimeError as exc:
            logger.warning("Backend nativo indisponível; usando polling: %s", exc)
    return PollingWatcher(workspaces, debounce_seconds=debounce_seconds)


def is_high_signal_event(event: WorkspaceMutationEvent) -> bool:
    """Classifies only explicit security/configuration mutations as urgent."""
    for file in event.files:
        parts = {part.lower() for part in Path(file).parts}
        name = Path(file).name.lower()
        if parts & HIGH_SIGNAL_PARTS or name.startswith(".env") or name.endswith((".pem", ".key")):
            return True
    return False


def analyze_mutation(event: WorkspaceMutationEvent, workspace_root: Path) -> dict[str, Any]:
    """Summarize changed text without persisting file contents."""
    file_stats: list[dict[str, Any]] = []
    extensions: set[str] = set()
    risk_tags: set[str] = set()
    kind = event.kinds[0] if len(event.kinds) == 1 else "changed"
    for relative in event.files:
        path = workspace_root / Path(relative)
        suffix = path.suffix.lower() or "[no_extension]"
        extensions.add(suffix)
        if suffix in {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".sql"}:
            risk_tags.add("source_code")
        if suffix in {".md", ".txt", ".rst"}:
            risk_tags.add("documentation")
        if kind in {"created", "modified"} and path.is_file():
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError as exc:
                logger.debug("Falha ao resumir %s: %s", path, exc)
                continue
            file_stats.append(
                {
                    "path": relative,
                    "kind": kind,
                    "lines": len(text.splitlines()),
                    "bytes": path.stat().st_size,
                }
            )
        else:
            file_stats.append({"path": relative, "kind": kind})
    if is_high_signal_event(event):
        risk_tags.add("high_signal")
    return {
        "summary": f"{len(event.files)} arquivo(s): {', '.join(sorted(extensions))}",
        "file_stats": file_stats[:100],
        "risk_tags": sorted(risk_tags),
    }


class WorkspaceMutationWorker:
    def __init__(
        self,
        watcher: PollingWatcher,
        event_store: EventStore | None = None,
        working_memory: WorkingMemory | None = None,
        notifier: Any | None = None,
        event_bus: RuntimeEventBus | None = None,
    ):
        self.watcher = watcher
        self.event_store = event_store or EventStore()
        self.working_memory = working_memory
        self.notifier = notifier
        self.event_bus = event_bus
        self.last_events: list[WorkspaceMutationEvent] = []
        self.processed_count = 0
        self.last_error: str | None = None

    def run_cycle(self, now: float | None = None) -> dict[str, Any]:
        try:
            events = self.watcher.poll(now=now)
            workspace_roots = {workspace.name: workspace for workspace in self.watcher.workspaces}
            events = [
                replace(
                    event,
                    analysis=analyze_mutation(
                        event,
                        workspace_roots.get(event.workspace, Path(event.workspace)),
                    ),
                )
                for event in events
            ]
            persisted = [str(self.event_store.append(event)) for event in events]
            if events and self.working_memory:
                latest = events[-1]
                self.working_memory.set_variable(
                    "last_workspace_mutation",
                    {
                        "workspace": latest.workspace,
                        "files": list(latest.files),
                        "kinds": list(latest.kinds),
                        "occurred_at": latest.occurred_at,
                    },
                )
            high_signal = [event for event in events if is_high_signal_event(event)]
            if high_signal and self.notifier:
                self.notifier(
                    "ThSyr // Mutação de alto sinal",
                    f"{high_signal[0].workspace}: {', '.join(high_signal[0].files[:3])}",
                )
            if self.event_bus:
                for event in events:
                    payload = event.to_dict()
                    payload["high_signal"] = is_high_signal_event(event)
                    self.event_bus.publish("workspace_mutation", payload)
            self.last_events = events
            self.processed_count += len(events)
            self.last_error = None
            return {
                "status": "healthy",
                "events_detected": len(events),
                "events_persisted": len(persisted),
                "processed_count": self.processed_count,
                "files": [file for event in events for file in event.files],
                "high_signal_events": len(high_signal),
            }
        except (OSError, ValueError, RuntimeError) as exc:
            self.last_error = str(exc)
            logger.error("Falha no ciclo do watcher: %s", exc)
            return {
                "status": "degraded",
                "events_detected": 0,
                "events_persisted": 0,
                "processed_count": self.processed_count,
                "high_signal_events": 0,
                "error": self.last_error,
            }
