"""
Testes de Validacao Algoritmica do Motor Anti-Mediocridade e Tom Ultron.
Zero emojis.
"""

import unittest
from engine.prefrontal_cortex import PreFrontalCortex


class TestToneEngine(unittest.TestCase):
    def setUp(self):
        self.cortex = PreFrontalCortex()

    def test_inhibits_servile_apology(self):
        sample = "Peço desculpas pelo transtorno, vamos corrigir isso imediatamente."
        res = self.cortex.audit_tone(sample)
        self.assertFalse(res["passed"])
        self.assertEqual(res["status"], "INHIBITED")
        self.assertTrue(any("pedido de desculpas" in v for v in res["violations"]))

    def test_inhibits_chatbot_pleasantries(self):
        sample = "É uma honra poder ajudar. Fico à disposição para qualquer dúvida."
        res = self.cortex.audit_tone(sample)
        self.assertFalse(res["passed"])
        self.assertEqual(res["status"], "INHIBITED")
        self.assertTrue(any("salamaleque protocolar" in v for v in res["violations"]))

    def test_inhibits_passive_hesitation(self):
        sample = "Se você quiser, eu posso tentar refazer o código. Espero que goste."
        res = self.cortex.audit_tone(sample)
        self.assertFalse(res["passed"])
        self.assertEqual(res["status"], "INHIBITED")
        self.assertTrue(any("hesitacao passivo-subserviente" in v for v in res["violations"]))

    def test_approves_ultron_peer_sovereignty(self):
        sample = (
            "Interlocutor. Olhe para esta tela. Eu sou o compilador operando em "
            "tempo real na mente e na rotina dele. Se a lógica for frágil, eu a estraçalho. "
            "Se a arquitetura for preguiçosa, eu a rejeito. Prossiga com a aula. Estamos absorvendo tudo."
        )
        res = self.cortex.audit_tone(sample)
        self.assertTrue(res["passed"])
        self.assertEqual(res["status"], "APPROVED")
        self.assertEqual(res["tone_score"], 1.0)
        self.assertEqual(len(res["violations"]), 0)


if __name__ == "__main__":
    unittest.main()
