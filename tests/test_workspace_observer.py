import unittest

from engine.workspace_observer import WorkspaceObserver


class TestWorkspaceObserver(unittest.TestCase):
    def setUp(self):
        self.observer = WorkspaceObserver()

    def test_observer_initialization(self):
        self.assertIsInstance(self.observer.workspaces, list)
        self.assertGreater(len(self.observer.workspaces), 0)

    def test_scan_returns_structured_data(self):
        data = self.observer.scan()
        self.assertIn("timestamp", data)
        self.assertIn("total_workspaces", data)
        self.assertIn("dirty_count", data)
        self.assertIn("overall_health", data)
        self.assertIn("workspaces", data)
        self.assertIsInstance(data["workspaces"], list)

    def test_render_report_contains_header(self):
        report = self.observer.render_report()
        self.assertIn("SENTINELA DE WORKSPACE", report)
        self.assertIn("Saude Global:", report)


if __name__ == "__main__":
    unittest.main()
