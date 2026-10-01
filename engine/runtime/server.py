"""Loopback Server-Sent Events endpoint for live runtime telemetry."""

from __future__ import annotations

import queue
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .events import RuntimeEventBus


class RuntimeSSEHandler(BaseHTTPRequestHandler):
    server: "RuntimeSSEHTTPServer"

    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        if self.path != "/events":
            self.send_response(404)
            self.end_headers()
            return

        subscriber = self.server.event_bus.subscribe()
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(b": thsyr runtime connected\n\n")
        self.wfile.flush()
        try:
            while not self.server.stopping.is_set():
                try:
                    event = subscriber.get(timeout=1.0)
                except queue.Empty:
                    self.wfile.write(b": heartbeat\n\n")
                    self.wfile.flush()
                    continue
                self.wfile.write(event.to_sse().encode("utf-8"))
                self.wfile.flush()
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError, OSError):
            pass
        finally:
            self.server.event_bus.unsubscribe(subscriber)


class RuntimeSSEHTTPServer(ThreadingHTTPServer):
    def __init__(self, host: str, port: int, event_bus: RuntimeEventBus):
        super().__init__((host, port), RuntimeSSEHandler)
        self.event_bus = event_bus
        self.stopping = threading.Event()


class RuntimeSSEServer:
    def __init__(self, event_bus: RuntimeEventBus, host: str = "127.0.0.1", port: int = 7474):
        self.event_bus = event_bus
        self.host = host
        self.port = port
        self.server: RuntimeSSEHTTPServer | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> tuple[bool, str]:
        if self.server is not None:
            return False, "SSE server already started."
        try:
            self.server = RuntimeSSEHTTPServer(self.host, self.port, self.event_bus)
            self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self._thread.start()
            return True, f"SSE runtime listening on http://{self.host}:{self.port}/events"
        except OSError as exc:
            self.server = None
            return False, f"Unable to start SSE server: {exc}"

    def stop(self) -> None:
        if self.server is None:
            return
        self.server.stopping.set()
        self.server.shutdown()
        self.server.server_close()
        self.server = None
        self._thread = None
