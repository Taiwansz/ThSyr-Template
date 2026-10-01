import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from engine.gods_eye_bridge import GodsEyeBridge


class TestGodsEyeBridge(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.package_json = self.temp_dir / "package.json"
        self.vite_config = self.temp_dir / "vite.config.js"

        # Simula estrutura essencial instalada
        pkg_data = {
            "name": "gods-eye-view",
            "version": "1.0.0",
            "description": "Gods Eye View Planetary Telemetry Console",
            "scripts": {"dev": "vite", "build": "vite build"}
        }
        self.package_json.write_text(json.dumps(pkg_data), encoding="utf-8")
        self.vite_config.write_text("export default {};", encoding="utf-8")

        self.bridge = GodsEyeBridge(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_installation_check(self):
        self.assertTrue(self.bridge.is_installed())

    def test_metadata_retrieval(self):
        meta = self.bridge.get_metadata()
        self.assertTrue(meta["installed"])
        self.assertEqual(meta["name"], "gods-eye-view")
        self.assertIn("dev", meta["scripts"])

    def test_sensory_layers(self):
        layers = self.bridge.list_sensory_layers()
        self.assertGreaterEqual(len(layers), 6)
        layer_ids = [layer["layer_id"] for layer in layers]
        self.assertIn("adsb_aviation", layer_ids)
        self.assertIn("ais_maritime", layer_ids)
        self.assertIn("satellites_sgp4", layer_ids)

    def test_status_report(self):
        status = self.bridge.get_status()
        self.assertEqual(status["status"], "OPERATIONAL")
        self.assertTrue(status["installed"])
        self.assertIn("Cesium", status["telemetry_engine"])

    def test_dependency_and_launch_guard(self):
        # Sem node_modules presente
        self.assertFalse(self.bridge.has_dependencies())
        res = self.bridge.launch()
        self.assertFalse(res["success"])
        self.assertIn("Dependencias", res["error"])

    def test_missing_installation_handling(self):
        missing_bridge = GodsEyeBridge(self.temp_dir / "non_existent")
        self.assertFalse(missing_bridge.is_installed())
        meta = missing_bridge.get_metadata()
        self.assertFalse(meta["installed"])
        status = missing_bridge.get_status()
        self.assertEqual(status["status"], "MISSING")
        self.assertFalse(status["installed"])
        launch_res = missing_bridge.launch()
        self.assertFalse(launch_res["success"])
        self.assertIn("nao localizado", launch_res["error"])

    @patch("subprocess.Popen")
    def test_launch_success_mocked(self, mock_popen):
        # Criar node_modules para simular dependencias presentes
        (self.temp_dir / "node_modules").mkdir(exist_ok=True)
        self.assertTrue(self.bridge.has_dependencies())

        mock_proc = MagicMock()
        mock_proc.pid = 4242
        mock_popen.return_value = mock_proc

        res = self.bridge.launch(port=4173)
        self.assertTrue(res["success"])
        self.assertEqual(res["pid"], 4242)
        self.assertEqual(res["url"], "http://localhost:4173")


if __name__ == "__main__":
    unittest.main()
