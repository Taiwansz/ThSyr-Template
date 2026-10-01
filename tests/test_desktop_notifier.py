import unittest

from engine.desktop_notifier import DesktopNotifier


class TestDesktopNotifier(unittest.TestCase):
    def setUp(self):
        self.notifier = DesktopNotifier()

    def test_sanitize_text_strips_emojis(self):
        dirty = "Alerta 🚨 Importante ⚠️ Verifique!"
        clean = self.notifier.sanitize_text(dirty)
        self.assertNotIn("🚨", clean)
        self.assertNotIn("⚠️", clean)
        self.assertIn("Alerta", clean)

    def test_notify_empty_message_returns_false(self):
        res = self.notifier.notify("Titulo", "", async_dispatch=False)
        self.assertFalse(res)


if __name__ == "__main__":
    unittest.main()
