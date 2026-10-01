"""
Hermetic Cross-Platform Unit Tests for ThSyr Daemon and Process Supervisor
Valida supervisao de processos, isolamento de PIDs, batimentos cardiacos e backends Windows/POSIX/Mock.
"""

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from engine.runtime.daemon import SyrDaemonManager
from engine.runtime.process_supervisor import (
    MockProcessSupervisor,
    PosixProcessSupervisor,
    WindowsProcessSupervisor,
    get_process_supervisor,
)


class TestDaemonManagerWithMockSupervisor(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.pid_file = self.temp_dir / "test_daemon.pid"
        self.hb_file = self.temp_dir / "test_daemon_hb.json"
        self.supervisor = MockProcessSupervisor()
        self.manager = SyrDaemonManager(
            pid_file=self.pid_file,
            repo_root=self.temp_dir,
            supervisor=self.supervisor,
            heartbeat_file=self.hb_file,
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_pid_lifecycle(self):
        self.assertIsNone(self.manager.read_pid())
        self.manager.write_pid(12345)
        self.assertEqual(self.manager.read_pid(), 12345)
        self.manager.clear_pid()
        self.assertIsNone(self.manager.read_pid())

    def test_status_when_stopped(self):
        stat = self.manager.status()
        self.assertEqual(stat["status"], "STOPPED")
        self.assertFalse(stat["is_running"])
        self.assertIsNone(stat["pid"])

    def test_start_success(self):
        success, msg = self.manager.start()
        self.assertTrue(success)
        pid = self.manager.read_pid()
        self.assertIsNotNone(pid)
        self.assertIn(str(pid), msg)
        self.assertTrue(self.manager.is_running())

        hb = self.manager.get_heartbeat()
        self.assertIsNotNone(hb)
        self.assertEqual(hb["status"], "INITIALIZED")

    def test_start_already_running(self):
        self.manager.start()
        success, msg = self.manager.start()
        self.assertFalse(success)
        self.assertIn("ja esta em execucao", msg)

    def test_stop_running(self):
        self.manager.start()
        pid = self.manager.read_pid()
        self.assertIsNotNone(pid)
        self.assertTrue(self.manager.is_running())

        success, msg = self.manager.stop()
        self.assertTrue(success)
        self.assertIn("encerrado com sucesso", msg)
        self.assertIsNone(self.manager.read_pid())
        self.assertFalse(self.manager.is_running())

    def test_stop_not_running_cleans_stale_pid(self):
        self.manager.write_pid(99999)
        # Not in mock supervisor active_pids
        self.assertFalse(self.manager.is_running())

        success, msg = self.manager.stop()
        self.assertTrue(success)
        self.assertIn("removido", msg)
        self.assertIsNone(self.manager.read_pid())


class TestProcessSupervisorBackends(unittest.TestCase):
    def test_mock_supervisor_isolated(self):
        mock_sup = MockProcessSupervisor(initial_pids=[5001])
        self.assertTrue(mock_sup.is_running(5001))
        self.assertFalse(mock_sup.is_running(5002))

        spawned_pid = mock_sup.spawn(["cmd", "arg"], cwd=Path("."))
        self.assertTrue(mock_sup.is_running(spawned_pid))

        fingerprint = mock_sup.get_fingerprint(spawned_pid)
        self.assertIsNotNone(fingerprint)
        self.assertEqual(fingerprint["platform"], "mock")

        terminated = mock_sup.terminate(spawned_pid)
        self.assertTrue(terminated)
        self.assertFalse(mock_sup.is_running(spawned_pid))

    @patch("subprocess.check_output")
    def test_windows_supervisor_is_running(self, mock_check_output):
        mock_check_output.return_value = '"python.exe","1234","Console","1","10,240 K"'
        win_sup = WindowsProcessSupervisor()
        self.assertTrue(win_sup.is_running(1234))

        mock_check_output.return_value = 'INFO: No tasks are running which match the specified criteria.'
        self.assertFalse(win_sup.is_running(5678))

    @patch("subprocess.run")
    def test_windows_supervisor_terminate(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        win_sup = WindowsProcessSupervisor()
        with patch.object(win_sup, "is_running", side_effect=[True, False]):
            success = win_sup.terminate(1234)
            self.assertTrue(success)

    @patch("os.kill")
    def test_posix_supervisor_is_running(self, mock_kill):
        posix_sup = PosixProcessSupervisor()
        mock_kill.return_value = None
        self.assertTrue(posix_sup.is_running(1234))

        mock_kill.side_effect = ProcessLookupError()
        self.assertFalse(posix_sup.is_running(5678))

    @patch("os.kill")
    def test_posix_supervisor_terminate(self, mock_kill):
        posix_sup = PosixProcessSupervisor()
        mock_kill.return_value = None
        with patch.object(posix_sup, "is_running", side_effect=[True, False]):
            success = posix_sup.terminate(1234)
            self.assertTrue(success)

    def test_factory_get_process_supervisor(self):
        mock_sup = get_process_supervisor("mock")
        self.assertIsInstance(mock_sup, MockProcessSupervisor)

        win_sup = get_process_supervisor("windows")
        self.assertIsInstance(win_sup, WindowsProcessSupervisor)

        posix_sup = get_process_supervisor("posix")
        self.assertIsInstance(posix_sup, PosixProcessSupervisor)


if __name__ == "__main__":
    unittest.main()
