import shutil
import tempfile
import unittest
from pathlib import Path

from engine.vector_store import LocalVectorStore


class TestLocalVectorStore(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test_vectors.db"
        self.store = LocalVectorStore(db_path=self.db_path, dim=64)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_compute_embedding_normalized(self):
        vec = self.store.compute_embedding("PostgreSQL com Row Level Security")
        self.assertEqual(len(vec), 64)
        norm = sum(x * x for x in vec)
        self.assertAlmostEqual(norm, 1.0, places=3)

    def test_upsert_and_count(self):
        self.assertEqual(self.store.count(), 0)
        self.store.upsert("doc1", "PostgreSQL RLS security", {"category": "database"})
        self.store.upsert("doc2", "Next.js App Router Server Actions", {"category": "frontend"})
        self.assertEqual(self.store.count(), 2)

    def test_semantic_search_ranking(self):
        self.store.upsert("doc_db", "Banco de dados Postgres e seguranca RLS", {"type": "db"})
        self.store.upsert("doc_front", "Interface visual Next.js com Tailwind", {"type": "ui"})
        self.store.upsert("doc_auth", "Autenticacao e controle de acesso OAuth", {"type": "auth"})

        # Busca por seguranca e postgres
        results = self.store.search("postgres seguranca de dados", top_k=2)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["id"], "doc_db")
        self.assertGreater(results[0]["score"], 0.2)

        # Busca por autenticacao
        results_auth = self.store.search("autenticacao oauth", top_k=1)
        self.assertTrue(len(results_auth) > 0)
        self.assertEqual(results_auth[0]["id"], "doc_auth")

    def test_clear(self):
        self.store.upsert("d1", "texto teste")
        self.assertEqual(self.store.count(), 1)
        self.store.clear()
        self.assertEqual(self.store.count(), 0)


if __name__ == "__main__":
    unittest.main()
