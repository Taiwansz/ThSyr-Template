import shutil
import tempfile
import unittest
from pathlib import Path

from engine.memory_manager import MemoryManager


class TestMemoryManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.memory = MemoryManager(root=self.temp_dir)

        # Preencher mock de personalidade e perfil
        (self.temp_dir / "core" / "personality.md").write_text("# Persona Syr\nAnti-sicofante e analitico.", encoding="utf-8")
        (self.temp_dir / "profile" / "user.md").write_text("# Perfil Operador\nArquiteto de software.", encoding="utf-8")
        (self.temp_dir / "memories" / "semantic" / "database.md").write_text("# Database\nPostgreSQL com RLS.", encoding="utf-8")
        (self.temp_dir / "memories" / "semantic" / "frontend.md").write_text("# Frontend\nNext.js App Router.", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_episodic_log_unique_id_prevents_collision(self):
        # Escrever dois logs com o mesmo titulo no mesmo segundo
        p1 = self.memory.append_episodic_log("Refatoracao Sync", "Conteudo 1")
        p2 = self.memory.append_episodic_log("Refatoracao Sync", "Conteudo 2")

        self.assertTrue(p1.exists())
        self.assertTrue(p2.exists())
        self.assertNotEqual(p1.name, p2.name)
        self.assertEqual(self.memory.count_total_episodic_logs(), 2)

    def test_count_total_episodic_logs(self):
        self.assertEqual(self.memory.count_total_episodic_logs(), 0)
        self.memory.append_episodic_log("Sessao 1", "Log 1")
        self.memory.append_episodic_log("Sessao 2", "Log 2")
        self.memory.append_episodic_log("Sessao 3", "Log 3")
        self.assertEqual(self.memory.count_total_episodic_logs(), 3)

    def test_analytical_memory_lifecycle(self):
        self.assertEqual(self.memory.count_total_analytical_memories(), 0)
        p = self.memory.save_analytical_memory(
            title="Deducoes de Segunda Ordem",
            content="Analise comportamental da sessao.",
            importance=0.95
        )
        self.assertTrue(p.exists())
        self.assertEqual(self.memory.count_total_analytical_memories(), 1)

        items = self.memory.get_analytical_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "Deducoes de Segunda Ordem")
        self.assertEqual(items[0].metadata.type, "analytical")

    def test_compact_context_builder(self):
        self.memory.save_analytical_memory("Deducoes Prioritarias", "Meta-analise do operador.")
        ctx = self.memory.build_compact_context(active_seeds=["frontend"], max_semantics=1)
        self.assertIn("Persona Syr", ctx)
        self.assertIn("Perfil Operador", ctx)
        self.assertIn("FRONTEND", ctx)
        self.assertIn("DEDUÇÕES ANALÍTICAS E META-COGNIÇÃO", ctx)
        self.assertIn("Deducoes Prioritarias", ctx)
        # Nao deve conter DATABASE ja que o max foi 1 e a semente foi frontend
        self.assertNotIn("DATABASE", ctx)


if __name__ == "__main__":
    unittest.main()
