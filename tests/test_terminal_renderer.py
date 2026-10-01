"""
ThSyr Tests - Terminal Renderer & Progress Tracker
Valida estetica ANSI semantica, fallback para NO_COLOR e atualizacoes de progresso.
"""

import io
import os
import unittest
from unittest.mock import patch

from engine.interaction.progress import ProgressTracker
from engine.interaction.response_models import StructuredResponse
from engine.interaction.terminal_renderer import TerminalRenderer


class TestTerminalRenderer(unittest.TestCase):
    def test_progressive_disclosure_rendering(self):
        renderer = TerminalRenderer()
        resp = StructuredResponse(
            summary="Problema no daemon.",
            answer="O daemon perdeu o arquivo de trava PID.",
            details="Arquivo state/daemon.pid removido por processo externo.",
            evidence=[{"exit_code": 1, "verified": True}],
            sources=[{"kind": "observed", "identifier": "pid_file", "description": "Arquivo PID"}],
            actions=[{"shortcut": "1", "label": "Reiniciar daemon"}],
        )

        rendered = renderer.render_response(resp)
        self.assertIn("Syr ›", rendered)
        self.assertIn("O daemon perdeu o arquivo de trava PID.", rendered)
        self.assertIn("[1] Reiniciar daemon", rendered)
        self.assertIn("/details", rendered)
        self.assertIn("/evidence", rendered)
        self.assertIn("/source", rendered)

    def test_no_color_environment_respect(self):
        with patch.dict(os.environ, {"NO_COLOR": "1"}):
            renderer = TerminalRenderer()
            self.assertFalse(renderer.use_color)
            resp = StructuredResponse(summary="Ok", answer="Tudo em ordem.")
            rendered = renderer.render_response(resp)
            self.assertNotIn("\033[", rendered)

    def test_progress_tracker_tty_and_finish(self):
        buf = io.StringIO()
        # Mock de stream com isatty() = True
        buf.isatty = lambda: True  # type: ignore

        progress = ProgressTracker(stream=buf)
        progress.start("Verificando integridade")
        self.assertIn("Verificando integridade...", buf.getvalue())

        progress.finish("Integridade confirmada", success=True)
        self.assertIn("[OK]", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
