"""Event-driven episodic consolidation for the continuous runtime."""

from __future__ import annotations

import queue
from typing import Any

from ..memory_manager import MemoryManager
from .events import RuntimeEvent, RuntimeEventBus


class REMConsolidator:
    """Turns high-signal runtime events into bounded episodic memories."""

    def __init__(
        self,
        event_bus: RuntimeEventBus,
        memory_manager: MemoryManager | None = None,
        max_events_per_cycle: int = 50,
    ):
        self.subscription = event_bus.subscribe()
        self.memory = memory_manager or MemoryManager()
        self.max_events_per_cycle = max(1, max_events_per_cycle)

    def run_cycle(self) -> dict[str, Any]:
        events: list[RuntimeEvent] = []
        for _ in range(self.max_events_per_cycle):
            try:
                events.append(self.subscription.get_nowait())
            except queue.Empty:
                break

        if not events:
            return {"status": "idle", "events_consumed": 0, "memory_path": None}

        files: list[str] = []
        high_signal = False
        analyses: list[str] = []
        for event in events:
            if event.event_type != "workspace_mutation":
                continue
            payload_files = event.payload.get("files", ())
            files.extend(str(path) for path in payload_files)
            high_signal = high_signal or bool(event.payload.get("high_signal", False))
            analysis = event.payload.get("analysis", {})
            if analysis.get("summary"):
                analyses.append(str(analysis["summary"]))

        unique_files = list(dict.fromkeys(files))
        if not unique_files:
            return {"status": "ignored", "events_consumed": len(events), "memory_path": None}

        title = "Mutacoes de workspace de alto sinal" if high_signal else "Mutacoes de workspace"
        content = "\n".join(
            [
                f"Eventos consolidados: {len(events)}",
                f"Arquivos observados: {len(unique_files)}",
                *[f"Resumo: {summary}" for summary in dict.fromkeys(analyses)],
                "",
                *[f"- {path}" for path in unique_files[:100]],
            ]
        )
        memory_path = self.memory.append_episodic_log(
            title=title,
            content=content,
            entities=["Operador"],
            projects=["Copilot"],
            tags=["runtime", "sensory_watcher", "high_signal" if high_signal else "workspace"],
            importance=0.95 if high_signal else 0.7,
        )
        return {
            "status": "consolidated",
            "events_consumed": len(events),
            "files": unique_files,
            "high_signal": high_signal,
            "memory_path": str(memory_path),
        }
