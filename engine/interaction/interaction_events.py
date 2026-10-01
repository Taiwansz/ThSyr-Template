"""
ThSyr Interaction Layer - Interaction Events
Sistema de eventos desacoplado do modelo para rastreamento de progresso,
execucao de ferramentas, mudancas de plano, aprovacoes e conclusao de tarefas.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional


class EventType(str, Enum):
    TASK_STARTED = "task_started"
    PROGRESS_UPDATED = "progress_updated"
    FINDING_DETECTED = "finding_detected"
    PLAN_CHANGED = "plan_changed"
    TOOL_STARTED = "tool_started"
    TOOL_FINISHED = "tool_finished"
    APPROVAL_REQUIRED = "approval_required"
    WARNING = "warning"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TASK_PAUSED = "task_paused"
    TASK_CANCELLED = "task_cancelled"
    ARTIFACT_CREATED = "artifact_created"
    VERIFICATION_COMPLETED = "verification_completed"


class EventLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    IMPORTANT = "important"
    CRITICAL = "critical"


@dataclass
class InteractionEvent:
    type: EventType
    message: str
    level: EventLevel = EventLevel.INFO
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type.value,
            "message": self.message,
            "level": self.level.value,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }


class EventBroadcaster:
    def __init__(self):
        self._subscribers: list[Callable[[InteractionEvent], None]] = []

    def subscribe(self, callback: Callable[[InteractionEvent], None]) -> None:
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[InteractionEvent], None]) -> None:
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    def emit(
        self,
        event_type: EventType,
        message: str,
        level: EventLevel = EventLevel.INFO,
        payload: Optional[dict[str, Any]] = None,
    ) -> InteractionEvent:
        event = InteractionEvent(
            type=event_type,
            message=message,
            level=level,
            payload=payload or {},
        )
        for sub in list(self._subscribers):
            try:
                sub(event)
            except Exception:
                pass
        return event
