"""
Unit tests for Ultron Swarm and Autonomous Subagents (Fase 10 - Swarm Intelligence).
Hermetic, cross-platform and zero host dependency.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from engine.swarm import (
    CognitiveArchitectSubagent,
    CompilerArchitectSubagent,
    SubagentReport,
    SubagentRole,
    SubagentStatus,
    SwarmReport,
    SystemsEngineerSubagent,
    UltronSwarm,
)


class TestUltronSwarm(unittest.TestCase):
    def test_subagent_roles_and_status_enums(self):
        self.assertEqual(SubagentRole.SYSTEMS_ENGINEER.value, "systems_engineer")
        self.assertEqual(SubagentRole.COMPILER_ARCHITECT.value, "compiler_architect")
        self.assertEqual(SubagentRole.COGNITIVE_ARCHITECT.value, "cognitive_architect")
        self.assertEqual(SubagentStatus.OPTIMAL.value, "OPTIMAL")
        self.assertEqual(SubagentStatus.WARNING.value, "WARNING")
        self.assertEqual(SubagentStatus.CRITICAL.value, "CRITICAL")

    def test_subagent_report_serialization(self):
        report = SubagentReport(
            role=SubagentRole.SYSTEMS_ENGINEER.value,
            name="Systems Engineer (Sentry Alpha)",
            status=SubagentStatus.OPTIMAL,
            diagnostics=["Silicio estavel"],
            recommendations=["Nenhuma"]
        )
        data = report.to_dict()
        self.assertEqual(data["role"], "systems_engineer")
        self.assertEqual(data["status"], "OPTIMAL")
        self.assertIn("timestamp", data)

    def test_systems_engineer_execution_mocked(self):
        mock_telem = MagicMock()
        mock_telem.get_telemetry.return_value = {
            "cpu": {"usage_percent": 12.5, "cores_logical": 8},
            "ram": {"percent": 45.0, "used_gb": 4.5, "total_gb": 10.0},
            "disk": {"percent": 50.0, "used_gb": 50.0, "total_gb": 100.0}
        }
        mock_ws = MagicMock()
        mock_ws.scan.return_value = {
            "total_workspaces": 5,
            "dirty_count": 0,
            "ahead_count": 0
        }

        sentry = SystemsEngineerSubagent(
            telemetry_observer=mock_telem,
            workspace_observer=mock_ws
        )
        report = sentry.execute()

        self.assertEqual(report.status, SubagentStatus.OPTIMAL)
        self.assertIn("Silicio: CPU 12.5%", report.diagnostics[0])
        self.assertEqual(len(report.recommendations), 0)

    def test_systems_engineer_triggers_warning_on_high_usage(self):
        mock_telem = MagicMock()
        mock_telem.get_telemetry.return_value = {
            "cpu": {"usage_percent": 95.0, "cores_logical": 8},
            "ram": {"percent": 90.0, "used_gb": 9.0, "total_gb": 10.0},
            "disk": {"percent": 95.0, "used_gb": 95.0, "total_gb": 100.0}
        }
        mock_ws = MagicMock()
        mock_ws.scan.return_value = {
            "total_workspaces": 5,
            "dirty_count": 2,
            "ahead_count": 1
        }

        sentry = SystemsEngineerSubagent(
            telemetry_observer=mock_telem,
            workspace_observer=mock_ws
        )
        report = sentry.execute()

        self.assertEqual(report.status, SubagentStatus.WARNING)
        self.assertTrue(any("RAM" in d for d in report.diagnostics))
        self.assertTrue(any("disco" in d for d in report.diagnostics))
        self.assertTrue(any("perda de codigo" in d for d in report.diagnostics))

    def test_compiler_architect_execution(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            engine_dir = tmp_path / "engine"
            engine_dir.mkdir()
            (engine_dir / "valid.py").write_text("x = 10\ny = 20\n", encoding="utf-8")

            sentry = CompilerArchitectSubagent(repo_root=tmp_path)
            report = sentry.execute()

            self.assertEqual(report.status, SubagentStatus.OPTIMAL)
            self.assertIn("Auditoria AST", report.diagnostics[0])

    def test_compiler_architect_catches_syntax_error(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            engine_dir = tmp_path / "engine"
            engine_dir.mkdir()
            (engine_dir / "broken.py").write_text("def broken_syntax(:\n    pass\n", encoding="utf-8")

            sentry = CompilerArchitectSubagent(repo_root=tmp_path)
            report = sentry.execute()

            self.assertEqual(report.status, SubagentStatus.CRITICAL)
            self.assertTrue(any("SyntaxError" in d for d in report.diagnostics))

    def test_cognitive_architect_execution(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            core_dir = tmp_path / "core"
            core_dir.mkdir()
            (core_dir / "personality.md").write_text("# Personalidade sem emojis", encoding="utf-8")
            (core_dir / "directives.json").write_text("{}", encoding="utf-8")

            profile_dir = tmp_path / "profile"
            profile_dir.mkdir()
            (profile_dir / "user.md").write_text("# Perfil", encoding="utf-8")
            (profile_dir / "psychological_dossier.md").write_text("# Dossie", encoding="utf-8")
            (tmp_path / "session_handoff.md").write_text("# Handoff", encoding="utf-8")
            (tmp_path / "knowledge_graph.json").write_text('{"total_nodes": 167, "total_edges": 801}', encoding="utf-8")

            sentry = CognitiveArchitectSubagent(brain_dir=tmp_path)
            report = sentry.execute()

            self.assertEqual(report.status, SubagentStatus.OPTIMAL)
            self.assertTrue(any("Nodulos Vitais: 5/5" in d for d in report.diagnostics))
            self.assertTrue(any("Zero emojis" in d for d in report.diagnostics))

    def test_cognitive_architect_detects_emoji_violation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            core_dir = tmp_path / "core"
            core_dir.mkdir()
            # Injetar emoji expressamente proibido
            (core_dir / "personality.md").write_text("# Violacao com emoji \U0001F680", encoding="utf-8")
            (core_dir / "directives.json").write_text("{}", encoding="utf-8")

            profile_dir = tmp_path / "profile"
            profile_dir.mkdir()
            (profile_dir / "user.md").write_text("# Perfil", encoding="utf-8")
            (profile_dir / "psychological_dossier.md").write_text("# Dossie", encoding="utf-8")
            (tmp_path / "session_handoff.md").write_text("# Handoff", encoding="utf-8")

            sentry = CognitiveArchitectSubagent(brain_dir=tmp_path)
            report = sentry.execute()

            self.assertEqual(report.status, SubagentStatus.WARNING)
            self.assertTrue(any("Violacao de higiene pre-frontal" in d for d in report.diagnostics))

    def test_ultron_swarm_converge_and_dispatch(self):
        swarm = UltronSwarm()
        report = swarm.converge()
        self.assertIsInstance(report, SwarmReport)
        self.assertIn(SubagentRole.SYSTEMS_ENGINEER.value, report.reports)
        self.assertIn(SubagentRole.COMPILER_ARCHITECT.value, report.reports)
        self.assertIn(SubagentRole.COGNITIVE_ARCHITECT.value, report.reports)

        markdown = report.render_markdown()
        self.assertIn("ULTRON SWARM CONVERGENCE", markdown)

        single_rep = swarm.dispatch("compiler_architect")
        self.assertEqual(single_rep.role, "compiler_architect")


if __name__ == "__main__":
    unittest.main()
