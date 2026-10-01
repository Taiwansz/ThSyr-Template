"""
ThSyr Desktop Control Center - Protocol Specification & DTOs
Define schemas, tipos de eventos, comandos e envelopes versionados
para o Desktop Runtime Bridge (Fase 1 / ADR-004 / 02_RUNTIME_AND_EVENTS.md).
"""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

PROTOCOL_VERSION = 1


class CommandType(str, Enum):
    # Comandos UI -> Runtime
    COMMAND_MESSAGE = "command.message"
    COMMAND_GOAL = "command.goal"
    COMMAND_CANCEL = "command.cancel"
    COMMAND_GRAPH_FOCUS = "command.graph.focus"
    COMMAND_STATUS = "command.status"


class EventType(str, Enum):
    # Lifecycle
    RUNTIME_STARTING = "runtime.starting"
    RUNTIME_READY = "runtime.ready"
    RUNTIME_DEGRADED = "runtime.degraded"
    RUNTIME_ERROR = "runtime.error"
    RUNTIME_STOPPING = "runtime.stopping"

    # Conversation
    MESSAGE_ACCEPTED = "message.accepted"
    RESPONSE_STARTED = "response.started"
    RESPONSE_DELTA = "response.delta"
    RESPONSE_FINAL = "response.final"
    RESPONSE_ERROR = "response.error"

    # Neural
    NEURAL_PULSE = "neural.pulse"
    NEURAL_NODES_ACTIVATED = "neural.nodes.activated"
    NEURAL_CONSTRAINTS_ACTIVATED = "neural.constraints.activated"
    MEMORY_RETRIEVED = "memory.retrieved"

    # Executive
    GOAL_STARTED = "goal.started"
    PLAN_CREATED = "plan.created"
    PLAN_CHANGED = "plan.changed"
    STEP_STARTED = "step.started"
    STEP_COMPLETED = "step.completed"
    STEP_FAILED = "step.failed"
    PROGRESS_UPDATED = "progress.updated"
    HYPOTHESIS_UPDATED = "hypothesis.updated"
    VERIFICATION_COMPLETED = "verification.completed"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"

    # Tools & Artifacts
    TOOL_STARTED = "tool.started"
    TOOL_FINISHED = "tool.finished"
    TOOL_FAILED = "tool.failed"
    ARTIFACT_CREATED = "artifact_created"

    # System / Policy
    OPERATION_CANCEL_UNSUPPORTED = "operation.cancel.unsupported"


@dataclass
class ProtocolEnvelope:
    """Envelope canonico para comunicacao bidirecional Desktop <-> Runtime."""
    type: str
    session_id: str
    correlation_id: str
    payload: dict[str, Any] = field(default_factory=dict)
    protocol: int = PROTOCOL_VERSION
    id: str = field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "protocol": self.protocol,
            "type": self.type,
            "id": self.id,
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProtocolEnvelope:
        if not isinstance(data, dict):
            raise ValueError("Frame deve ser um dicionario JSON valido.")

        protocol = data.get("protocol", PROTOCOL_VERSION)
        if protocol != PROTOCOL_VERSION:
            raise ValueError(f"Versao de protocolo nao suportada: {protocol}. Esperado: {PROTOCOL_VERSION}")

        msg_type = data.get("type")
        if not msg_type or not isinstance(msg_type, str):
            raise ValueError("Campo 'type' obrigatorio e deve ser string.")

        session_id = data.get("session_id", "default")
        correlation_id = data.get("correlation_id", f"op_{uuid.uuid4().hex[:8]}")
        payload = data.get("payload", {})
        if not isinstance(payload, dict):
            raise ValueError("Campo 'payload' deve ser um objeto JSON.")

        envelope_id = data.get("id") or f"evt_{uuid.uuid4().hex[:12]}"
        timestamp = data.get("timestamp") or datetime.now(timezone.utc).isoformat()

        return cls(
            protocol=protocol,
            type=msg_type,
            id=envelope_id,
            timestamp=timestamp,
            session_id=session_id,
            correlation_id=correlation_id,
            payload=payload,
        )


@dataclass
class CommandMessagePayload:
    text: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CommandMessagePayload:
        text = data.get("text", "")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Texto da mensagem deve ser string nao vazia.")
        return cls(text=text.strip())


@dataclass
class CommandGoalPayload:
    title: str
    description: str = ""
    project: Optional[str] = None
    priority: int = 2
    goal_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CommandGoalPayload:
        title = data.get("title", "")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Titulo do objetivo deve ser string nao vazia.")
        return cls(
            title=title.strip(),
            description=str(data.get("description", "")),
            project=data.get("project"),
            priority=int(data.get("priority", 2)),
            goal_id=data.get("goal_id"),
        )


@dataclass
class RuntimeStatusDto:
    status: str
    runtime_version: str
    protocol: int = PROTOCOL_VERSION
    total_nodes: int = 0
    total_synapses: int = 0
    active_sessions: list[str] = field(default_factory=list)
    current_goal: Optional[str] = None
    model_provider: Optional[str] = None
    model_name: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GraphNodeDto:
    id: str
    label: str
    group: str
    lobe: str
    kind: str
    degree: int = 0
    is_hub: bool = False
    workspace: str = "brain"
    path: str = ""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    color: str = "#8ba3bb"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GraphEdgeDto:
    source: str
    target: str
    weight: float = 1.0
    kind: str = "semantic"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GraphSnapshotDto:
    version: int = 1
    total_nodes: int = 0
    total_edges: int = 0
    nodes: list[GraphNodeDto] = field(default_factory=list)
    edges: list[GraphEdgeDto] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "total_nodes": self.total_nodes,
            "total_edges": self.total_edges,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
        }
