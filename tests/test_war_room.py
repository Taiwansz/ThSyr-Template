"""
Unit tests for Ultron War Room Tactical Web HUD (Fase 12).
Hermetic, cross-platform and zero host dependency.
"""

import time
import unittest
import urllib.request

from engine.war_room import WarRoomServer


class TestWarRoom(unittest.TestCase):
    def setUp(self):
        # Usar porta de teste efemera
        self.server = WarRoomServer(host="127.0.0.1", port=8099)
        self.started, self.msg = self.server.start(background=True)
        time.sleep(0.2)

    def tearDown(self):
        self.server.stop()

    def test_war_room_server_lifecycle(self):
        self.assertTrue(self.started)

        # 1. Testar endpoint raiz HTML
        req = urllib.request.Request("http://127.0.0.1:8099/")
        with urllib.request.urlopen(req, timeout=3) as resp:
            self.assertEqual(resp.status, 200)
            body = resp.read().decode("utf-8")
            self.assertIn("ULTRON WAR ROOM", body)
            self.assertIn("Silício e Hardware", body)

        # 2. Testar endpoint API status
        req_status = urllib.request.Request("http://127.0.0.1:8099/api/status")
        with urllib.request.urlopen(req_status, timeout=3) as resp:
            self.assertEqual(resp.status, 200)
            body = resp.read().decode("utf-8")
            self.assertIn("total_nodes", body)


if __name__ == "__main__":
    unittest.main()
