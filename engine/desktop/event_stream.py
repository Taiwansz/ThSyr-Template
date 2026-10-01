"""
ThSyr Desktop Event Stream & Event Bridge
Subscriber hub, fan-out, circular buffer em memoria e adaptadores para
EventBroadcaster e ExecutiveRunner (Fase 2 / 02_RUNTIME_AND_EVENTS.md / 06_IMPLEMENTATION_PHASES.md).
"""

from __future__ import annotations

import threading
from collections import deque
from typing import Any, Callable, Optional

from ..config import setup_logger
from ..interaction.interaction_events import EventBroadcaster, InteractionEvent
from .protocol import EventType, ProtocolEnvelope

logger = setup_logger("desktop_event_stream")


class DesktopEventStream:
    """
    Gerenciador central de publicacao de eventos para o Desktop Control Center.
    Mantem um buffer circular curto para recuperacao rapida em reconexao
    e despacha eventos para assinantes (ex: WebSockets conectados).
    """

    def __init__(self, max_buffer_size: int = 200):
        self._max_buffer_size = max_buffer_size
        self._buffer: deque[ProtocolEnvelope] = deque(maxlen=max_buffer_size)
        self._subscribers: list[Callable[[ProtocolEnvelope], None]] = []
        self._lock = threading.Lock()

    def subscribe(self, callback: Callable[[ProtocolEnvelope], None]) -> None:
        with self._lock:
            if callback not in self._subscribers:
                self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[ProtocolEnvelope], None]) -> None:
        with self._lock:
            if callback in self._subscribers:
                self._subscribers.remove(callback)

    def publish(self, envelope: ProtocolEnvelope) -> None:
        """Armazena o envelope no buffer e distribui para todos os subscribers."""
        with self._lock:
            self._buffer.append(envelope)
            subscribers_snapshot = list(self._subscribers)

        for sub in subscribers_snapshot:
            try:
                sub(envelope)
            except Exception as e:
                logger.warning(f"Erro ao entregar envelope {envelope.id} a subscriber: {e}")

    def get_recent(
        self,
        limit: int = 50,
        session_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> list[ProtocolEnvelope]:
        """Recupera eventos recentes do buffer circular com filtros opcionais."""
        with self._lock:
            events = list(self._buffer)

        if session_id:
            events = [e for e in events if e.session_id == session_id]
        if correlation_id:
            events = [e for e in events if e.correlation_id == correlation_id]

        return events[-limit:]

    def clear(self) -> None:
        with self._lock:
            self._buffer.clear()


class DesktopEventAdapter:
    """
    Adapta eventos gerados pelo core existente (EventBroadcaster e ExecutiveRunner)
    para envelopes canônicos do protocolo de desktop.
    """

    def __init__(
        self,
        event_stream: DesktopEventStream,
        default_session_id: str = "default",
    ):
        self.event_stream = event_stream
        self.default_session_id = default_session_id
        # Mapeamento de correlation_id ativo por sessao
        self._active_correlations: dict[str, str] = {}
        self._lock = threading.Lock()

    def set_active_correlation(self, session_id: str, correlation_id: str) -> None:
        with self._lock:
            self._active_correlations[session_id] = correlation_id

    def get_active_correlation(self, session_id: str) -> str:
        with self._lock:
            return self._active_correlations.get(session_id, f"op_{session_id}")

    def on_interaction_event(self, event: InteractionEvent) -> None:
        """Callback tipado para EventBroadcaster."""
        self.handle_interaction_event(event)

    def attach_broadcaster(self, broadcaster: EventBroadcaster) -> None:
        """Conecta o adapter como subscriber no EventBroadcaster existente."""
        broadcaster.subscribe(self.on_interaction_event)

    def detach_broadcaster(self, broadcaster: EventBroadcaster) -> None:
        broadcaster.unsubscribe(self.on_interaction_event)

    def handle_interaction_event(
        self,
        event: InteractionEvent,
        session_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> ProtocolEnvelope:
        """Traduz InteractionEvent para ProtocolEnvelope e publica no stream."""
        sid = session_id or self.default_session_id
        cid = correlation_id or self.get_active_correlation(sid)

        # Mapear tipo do InteractionEvent para EventType do protocolo desktop
        type_str = event.type.value if hasattr(event.type, "value") else str(event.type)

        envelope = ProtocolEnvelope(
            type=type_str,
            session_id=sid,
            correlation_id=cid,
            payload={
                "message": event.message,
                "level": event.level.value if hasattr(event.level, "value") else str(event.level),
                **event.payload,
            },
        )
        self.event_stream.publish(envelope)
        return envelope

    def handle_executive_event(
        self,
        event_dict: dict[str, Any],
        session_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> ProtocolEnvelope:
        """Traduz evento emitido pelo ExecutiveRunner para ProtocolEnvelope."""
        sid = session_id or self.default_session_id
        cid = correlation_id or self.get_active_correlation(sid)

        raw_type = str(event_dict.get("type", "step.completed"))
        type_map = {
            "step_start": EventType.STEP_STARTED.value,
            "step_end": EventType.STEP_COMPLETED.value,
            "step_fail": EventType.STEP_FAILED.value,
            "plan_create": EventType.PLAN_CREATED.value,
            "plan_change": EventType.PLAN_CHANGED.value,
            "goal_start": EventType.GOAL_STARTED.value,
            "goal_end": EventType.TASK_COMPLETED.value,
            "hypothesis_update": EventType.HYPOTHESIS_UPDATED.value,
            "verification": EventType.VERIFICATION_COMPLETED.value,
        }
        event_type = type_map.get(raw_type, raw_type)

        envelope = ProtocolEnvelope(
            id=str(event_dict.get("id", "")),
            type=event_type,
            session_id=sid,
            correlation_id=cid,
            timestamp=str(event_dict.get("timestamp", "")),
            payload={
                "source": event_dict.get("source", "executive_runner"),
                "project": event_dict.get("project"),
                "entity": event_dict.get("entity"),
                "confidence": event_dict.get("confidence", 1.0),
                "importance": event_dict.get("importance", 3),
                **(event_dict.get("payload") or {}),
            },
        )
        self.event_stream.publish(envelope)
        return envelope
