"""Thread-safe event bus shared by runtime workers and local observability."""

from __future__ import annotations

import json
import queue
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class RuntimeEvent:
    event_type: str
    payload: dict[str, Any]
    occurred_at: str

    def to_sse(self) -> str:
        body = json.dumps(
            {"event_type": self.event_type, "occurred_at": self.occurred_at, "payload": self.payload},
            ensure_ascii=False,
        )
        return f"event: {self.event_type}\ndata: {body}\n\n"


class RuntimeEventBus:
    def __init__(self, max_queue_size: int = 100):
        self.max_queue_size = max(1, max_queue_size)
        self._subscribers: set[queue.Queue[RuntimeEvent]] = set()
        self._lock = threading.Lock()

    def publish(self, event_type: str, payload: dict[str, Any]) -> RuntimeEvent:
        event = RuntimeEvent(event_type, payload, datetime.now(timezone.utc).isoformat())
        with self._lock:
            subscribers = tuple(self._subscribers)
        for subscriber in subscribers:
            try:
                subscriber.put_nowait(event)
            except queue.Full:
                try:
                    subscriber.get_nowait()
                    subscriber.put_nowait(event)
                except queue.Empty:
                    continue
        return event

    def subscribe(self) -> queue.Queue[RuntimeEvent]:
        subscriber: queue.Queue[RuntimeEvent] = queue.Queue(maxsize=self.max_queue_size)
        with self._lock:
            self._subscribers.add(subscriber)
        return subscriber

    def unsubscribe(self, subscriber: queue.Queue[RuntimeEvent]) -> None:
        with self._lock:
            self._subscribers.discard(subscriber)

    @property
    def subscriber_count(self) -> int:
        with self._lock:
            return len(self._subscribers)
