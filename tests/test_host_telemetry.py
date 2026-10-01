import unittest
from unittest.mock import MagicMock, patch

from engine.host_telemetry import HostTelemetryObserver


class TestHostTelemetry(unittest.TestCase):
    def setUp(self):
        self.observer = HostTelemetryObserver()

    def test_get_telemetry_structure(self):
        data = self.observer.get_telemetry()
        self.assertIn("timestamp", data)
        self.assertIn("platform", data)
        self.assertIn("cpu", data)
        self.assertIn("ram", data)
        self.assertIn("disk", data)
        self.assertIn("gpu", data)
        self.assertGreater(data["cpu"]["cores_logical"], 0)

    def test_render_report_contains_standard_headers(self):
        report = self.observer.render_report()
        self.assertIn("THSYR HOST TELEMETRY", report)
        self.assertIn("CPU", report)
        self.assertIn("Memoria RAM", report)
        self.assertIn("Disco", report)

    def test_gpu_mocked_presence(self):
        mock_output = "NVIDIA GeForce RTX 4070 Laptop GPU, 8188, 2048, 6140, 52, 18\n"
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_proc.stdout = mock_output
            mock_run.return_value = mock_proc

            gpu = self.observer._get_gpu_metrics()
            self.assertTrue(gpu["available"])
            self.assertEqual(gpu["model"], "NVIDIA GeForce RTX 4070 Laptop GPU")
            self.assertEqual(gpu["vram_total_mb"], 8188)
            self.assertEqual(gpu["vram_used_mb"], 2048)
            self.assertEqual(gpu["temperature_c"], 52)

    def test_gpu_fallback_when_absent(self):
        with patch("subprocess.run", side_effect=FileNotFoundError):
            gpu = self.observer._get_gpu_metrics()
            self.assertFalse(gpu["available"])
            self.assertEqual(gpu["model"], "N/D")


if __name__ == "__main__":
    unittest.main()
