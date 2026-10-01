import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

from engine.academic_sync import AcademicMonitor


class TestAcademicSync(unittest.TestCase):
    def setUp(self):
        self.temp_vault = Path(tempfile.mkdtemp())
        self.monitor = AcademicMonitor(
            vault_path=self.temp_vault,
            reference_date=date(2026, 9, 15)
        )

    def tearDown(self):
        shutil.rmtree(self.temp_vault, ignore_errors=True)

    def test_get_upcoming_deadlines_calculated(self):
        deadlines = self.monitor.get_upcoming_deadlines()
        self.assertTrue(len(deadlines) > 0)
        # 18/09/2026 a partir de 15/09/2026 = 3 dias
        p1 = [d for d in deadlines if d["tipo"] == "Prova 1 (P1)"][0]
        self.assertEqual(p1["dias_restantes"], 3)
        self.assertEqual(p1["status_tempo"], "3 dias")

    def test_render_radar_report(self):
        report = self.monitor.render_radar_report()
        self.assertIn("THSYR ACADEMIC RADAR", report)
        self.assertIn("Interacao Humano Computador", report)


if __name__ == "__main__":
    unittest.main()
