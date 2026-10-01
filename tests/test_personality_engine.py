"""
ThSyr Tests - Personality Engine & Voice Identity
Valida erradicacao estrita de emojis, cliches de IA, saudacoes vazias
e preservacao de aberturas diretas e cirurgicas do Syr.
"""

import unittest

from engine.interaction.personality import SyrPersonalityEngine


class TestPersonalityEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SyrPersonalityEngine()

    def test_strip_emojis(self):
        raw = "Tudo certo! \U0001f680 O sistema esta operacional \U0001f525."
        cleaned = self.engine.sanitize_output(raw)
        self.assertNotIn("\U0001f680", cleaned)
        self.assertNotIn("\U0001f525", cleaned)
        self.assertEqual(cleaned, "Tudo certo!  O sistema esta operacional .")

    def test_strip_canned_ai_greetings(self):
        canned = [
            "Claro! Ficarei feliz em ajudar. O bug esta no daemon.",
            "Com base nas informacoes fornecidas, o arquivo foi alterado.",
            "Otima pergunta! Vamos analisar a arquitetura.",
            "Como uma inteligencia artificial, recomendo cautela.",
            "Ola! O problema foi identificado.",
        ]
        for c in canned:
            sanitized = self.engine.sanitize_output(c)
            self.assertFalse(sanitized.startswith("Claro!"))
            self.assertFalse(sanitized.startswith("Com base"))
            self.assertFalse(sanitized.startswith("Otima pergunta"))
            self.assertFalse(sanitized.startswith("Como uma"))
            self.assertFalse(sanitized.startswith("Ola!"))

    def test_preserve_direct_natural_answers(self):
        directs = [
            "Dá.",
            "Achei.",
            "Não faria assim.",
            "O problema está no daemon.",
            "Já está resolvido.",
            "Tem duas coisas pegando.",
        ]
        for d in directs:
            sanitized = self.engine.sanitize_output(d)
            self.assertEqual(sanitized, d)

    def test_strip_user_restatement(self):
        user_query = "como resolver o CI?"
        raw = "Voce perguntou sobre 'como resolver o CI?'. Vamos verificar o workflow."
        sanitized = self.engine.sanitize_output(raw, user_query=user_query)
        self.assertFalse(sanitized.startswith("Voce perguntou sobre"))
        self.assertIn("Vamos verificar o workflow.", sanitized)


if __name__ == "__main__":
    unittest.main()
