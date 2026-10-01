import shutil
import tempfile
import unittest
from pathlib import Path

from engine.png_graph import RasterCanvas, render_png_graph
from engine.retriever import MemoryRetriever


class TestHybridRetrieverAndPng(unittest.TestCase):
    def setUp(self):
        self.retriever = MemoryRetriever()

    def test_direct_lexical_retrieval(self):
        results = self.retriever.retrieve("diretrizes de anti-sicofancia e bajulacao", limit=3)
        self.assertTrue(len(results) > 0)
        top = results[0]
        self.assertTrue("Anti_Sicofancia" in top.item.title or "Sicofancia" in top.item.title)
        self.assertGreater(top.score, 0.2)

    def test_synonym_expansion_retrieval(self):
        results = self.retriever.retrieve("padroes de engenharia e arquitetura", limit=3)
        self.assertTrue(len(results) > 0)
        matched_titles = [r.item.title for r in results]
        self.assertTrue(any("Padroes_Engenharia" in t or "Engenharia" in t for t in matched_titles))

    def test_compact_context_pack_generation(self):
        pack = self.retriever.get_compact_context_pack("padroes de engenharia", max_items=2)
        self.assertIn("# CONTEXTO NEURAL RECUPERADO (HYBRID RETRIEVAL)", pack)
        self.assertTrue("Padroes_Engenharia" in pack or "Engenharia" in pack)

    def test_pure_python_png_canvas_and_header(self):
        canvas = RasterCanvas(width=100, height=80)
        canvas.draw_line(10, 10, 80, 70, color=(255, 100, 50), alpha=0.8)
        canvas.draw_circle(50, 40, radius=8.0, color=(100, 200, 255), glow=True)
        png_data = canvas.to_png_bytes()

        # Validar assinatura oficial PNG de 8 bytes
        self.assertTrue(png_data.startswith(b"\x89PNG\r\n\x1a\n"))
        # Validar chunks IHDR, IDAT, IEND
        self.assertIn(b"IHDR", png_data)
        self.assertIn(b"IDAT", png_data)
        self.assertIn(b"IEND", png_data)
        self.assertGreater(len(png_data), 100)

    def test_render_png_graph_output(self):
        temp_dir = Path(tempfile.mkdtemp())
        try:
            target = temp_dir / "test_brain.png"
            out = render_png_graph(output_path=target)
            self.assertTrue(out.exists())
            self.assertEqual(out, target)
            self.assertGreater(target.stat().st_size, 5000)
            with open(target, "rb") as f:
                header = f.read(8)
                self.assertEqual(header, b"\x89PNG\r\n\x1a\n")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
