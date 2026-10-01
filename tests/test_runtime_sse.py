import socket
import time
import unittest

from engine.runtime.events import RuntimeEventBus
from engine.runtime.server import RuntimeSSEServer


class TestRuntimeSSE(unittest.TestCase):
    def test_sse_stream_delivers_published_event(self):
        bus = RuntimeEventBus()
        server = RuntimeSSEServer(bus, port=0)
        started, message = server.start()
        self.assertTrue(started, message)
        self.assertIsNotNone(server.server)
        port = server.server.server_address[1]
        connection = socket.create_connection(("127.0.0.1", port), timeout=2)
        connection.sendall(b"GET /events HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n")
        deadline = time.time() + 2
        data = b""
        while b"thsyr runtime connected" not in data and time.time() < deadline:
            connection.settimeout(0.2)
            try:
                data += connection.recv(4096)
            except socket.timeout:
                continue
        bus.publish("test_event", {"value": 7})
        while b"test_event" not in data and time.time() < deadline:
            connection.settimeout(0.2)
            try:
                data += connection.recv(4096)
            except socket.timeout:
                continue
        connection.close()
        server.stop()
        self.assertIn(b"test_event", data)
        self.assertIn(b'"value": 7', data)


if __name__ == "__main__":
    unittest.main()
