"""Operational self-model for ThSyr.

This module describes what the runtime can actually do *now*, based on
registered tools, model providers and persisted state. It intentionally avoids
personality claims and reports only observable capabilities.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .memory_manager import MemoryManager
from .models.gateway import ModelGateway
from .tools.bus import ToolBus


@dataclass(frozen=True)
class Capability:
    name: str
    available: bool
    source: str
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class OperationalSelfModel:
    def __init__(
        self,
        memory: MemoryManager | None = None,
        gateway: ModelGateway | None = None,
        tool_bus: ToolBus | None = None,
    ) -> None:
        self.memory = memory or MemoryManager()
        self.gateway = gateway or ModelGateway()
        self.tool_bus = tool_bus or ToolBus()

    def capabilities(self) -> list[Capability]:
        tool_names = {metadata.name for metadata in self.tool_bus.list_tools()}
        providers = [provider.provider_name for provider in self.gateway.providers]
        return [
            Capability(
                name="memory_retrieval",
                available=True,
                source="memory",
                detail="Hybrid lexical/dense/graph retrieval is installed.",
            ),
            Capability(
                name="model_reasoning",
                available=bool(providers),
                source="model_gateway",
                detail=(
                    f"Providers: {', '.join(providers)}"
                    if providers
                    else "No external model provider is currently available."
                ),
            ),
            Capability(
                name="filesystem_read",
                available="read_file" in tool_names,
                source="tool_bus",
                detail="Governed filesystem read tool.",
            ),
            Capability(
                name="filesystem_write",
                available="write_file" in tool_names,
                source="tool_bus",
                detail="Governed filesystem write tool; permission policy still applies.",
            ),
            Capability(
                name="git_inspection",
                available={"git_status", "git_log"}.issubset(tool_names),
                source="tool_bus",
                detail="Git status and history inspection tools.",
            ),
            Capability(
                name="shell_execution",
                available="shell_command" in tool_names,
                source="tool_bus",
                detail="Shell tool exists but remains subject to the Permission Cortex.",
            ),
            Capability(
                name="semantic_memory",
                available=True,
                source="memory",
                detail=f"{len(self.memory.get_semantic_items())} semantic memories currently indexed.",
            ),
        ]

    def snapshot(self) -> dict[str, Any]:
        capabilities = self.capabilities()
        available = [item.name for item in capabilities if item.available]
        unavailable = [item.name for item in capabilities if not item.available]
        return {
            "identity": "ThSyr",
            "self_model_version": 1,
            "capabilities": [item.to_dict() for item in capabilities],
            "available": available,
            "unavailable": unavailable,
            "provider_count": len(self.gateway.providers),
            "tool_count": len(self.tool_bus.list_tools()),
            "memory": {
                "semantic": len(self.memory.get_semantic_items()),
                "procedural": len(self.memory.get_procedural_items()),
                "analytical": len(self.memory.get_analytical_items(limit=1000)),
                "episodic": self.memory.count_total_episodic_logs(),
            },
        }
