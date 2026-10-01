"""
Testes Unitarios do Codenotch Launcher & Supervisor do ThSyr
"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from engine.config import settings
from engine.runtime.codenotch_launcher import CodenotchLauncher, get_codenotch_status


class TestCodenotchLauncher(unittest.TestCase):

    def setUp(self):
        self.launcher = CodenotchLauncher()

    def test_platform_detection(self):
        plat = self.launcher._detect_platform()
        self.assertIn(plat, ["windows", "darwin", "linux"])

    def test_find_executable_custom_path(self):
        with patch.object(Path, "is_file", return_value=True), \
             patch("os.access", return_value=True):
            launcher = CodenotchLauncher(custom_path="/custom/path/Codenotch.exe")
            exe = launcher.find_executable()
            self.assertIsNotNone(exe)
            self.assertIn("Codenotch.exe", str(exe))

    def test_find_executable_not_found(self):
        with patch.object(Path, "is_file", return_value=False), \
             patch("shutil.which", return_value=None):
            launcher = CodenotchLauncher(custom_path="/nao/existe/codenotch")
            exe = launcher.find_executable()
            self.assertIsNone(exe)

    def test_is_running_returns_bool(self):
        running = self.launcher.is_running()
        self.assertIsInstance(running, bool)

    def test_launch_disabled(self):
        with patch.object(settings.codenotch, "enabled", False):
            success, msg = self.launcher.launch()
            self.assertFalse(success)
            self.assertIn("desabilitado", msg)

    def test_launch_already_running(self):
        with patch.object(self.launcher, "is_running", return_value=True):
            success, msg = self.launcher.launch()
            self.assertTrue(success)
            self.assertIn("ja se encontra ativo", msg)

    def test_launch_not_found(self):
        with patch.object(self.launcher, "is_running", return_value=False), \
             patch.object(self.launcher, "find_executable", return_value=None):
            success, msg = self.launcher.launch()
            self.assertFalse(success)
            self.assertIn("nao localizado", msg)

    def test_launch_success_mocked(self):
        fake_exe = Path("/usr/local/bin/codenotch")
        with patch.object(self.launcher, "is_running", return_value=False), \
             patch.object(self.launcher, "find_executable", return_value=fake_exe), \
             patch("subprocess.Popen", return_value=MagicMock()):
            success, msg = self.launcher.launch()
            self.assertTrue(success)
            self.assertIn("iniciado com sucesso", msg)

    def test_ensure_running_structure(self):
        with patch.object(self.launcher, "is_running", return_value=True), \
             patch.object(self.launcher, "find_executable", return_value=Path("/bin/codenotch")):
            status = self.launcher.ensure_running()
            self.assertIn("running", status)
            self.assertIn("action_taken", status)
            self.assertIn("executable", status)
            self.assertIn("platform", status)
            self.assertIn("message", status)
            self.assertTrue(status["running"])
            self.assertEqual(status["action_taken"], "already_running")

    def test_get_codenotch_status(self):
        stat = get_codenotch_status()
        self.assertIn("installed", stat)
        self.assertIn("running", stat)
        self.assertIn("executable", stat)
        self.assertIn("platform", stat)
        self.assertIn("enabled", stat)


if __name__ == "__main__":
    unittest.main()
