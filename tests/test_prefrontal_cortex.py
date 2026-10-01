import unittest

from engine.prefrontal_cortex import PreFrontalCortex


class TestPreFrontalCortex(unittest.TestCase):
    def setUp(self):
        self.cortex = PreFrontalCortex()

    def test_approved_objective_response(self):
        draft = "A arquitetura recomendada utiliza PostgreSQL com RLS para isolamento de tenants."
        result = self.cortex.audit(draft)
        self.assertEqual(result["status"], "APPROVED")
        self.assertTrue(result["passed"])
        self.assertEqual(len(result["violations"]), 0)
        self.assertEqual(result["gate_score"], 1.0)

    def test_sycophancy_detection(self):
        drafts = [
            "Excelente ideia! Vamos fazer isso.",
            "Voce tem toda razao, essa solucao e impecavel.",
            "Que pergunta incrivel, perfeita!",
            "Com certeza absoluta, mestre."
        ]
        for draft in drafts:
            res = self.cortex.audit(draft)
            self.assertEqual(res["status"], "INHIBITED")
            self.assertFalse(res["passed"])
            self.assertTrue(any("Anti-Sicofancia" in v for v in res["violations"]))

    def test_zero_emojis_detection(self):
        # Emojis unicode test
        draft = "Solucao pronta \U0001F680 no repositorio."
        res = self.cortex.audit(draft)
        self.assertEqual(res["status"], "INHIBITED")
        self.assertTrue(any("Zero Emojis" in v for v in res["violations"]))

    def test_inviolable_constraints_oven_and_walls(self):
        draft_oven = "Recomendo instalar um forno embutido na bancada da cozinha."
        res_oven = self.cortex.audit(draft_oven)
        self.assertEqual(res_oven["status"], "INHIBITED")
        self.assertTrue(any("forno" in v for v in res_oven["violations"]))

        draft_wall = "Podemos derrubar parede entre a sala e o quarto para ampliar o espaco."
        res_wall = self.cortex.audit(draft_wall)
        self.assertEqual(res_wall["status"], "INHIBITED")
        self.assertTrue(any("planta_invariante" in v for v in res_wall["violations"]))

    def test_inviolable_entity_distinction(self):
        draft_income = "Considerando a sua renda de R$ 3.500 no planejamento financeiro."
        res_income = self.cortex.audit(draft_income)
        self.assertEqual(res_income["status"], "INHIBITED")
        self.assertTrue(any("renda_simulada" in v for v in res_income["violations"]))

    def test_protocolo_nao_cometa_erros_strict_mode(self):
        query_strict = "Execute a refatoração do módulo auth. Não cometa erros."

        # Teste 1: Bloqueio de placeholder TODO
        draft_with_todo = "Ajustei o decorator. // TODO: tratar expiracao do token."
        res_todo = self.cortex.audit(draft_with_todo, query=query_strict)
        self.assertEqual(res_todo["status"], "INHIBITED")
        self.assertTrue(res_todo["strict_mode"])
        self.assertTrue(any("placeholder_todo" in v for v in res_todo["violations"]))

        # Teste 2: Bloqueio de código incompleto (stub)
        draft_stub = "A classe esta pronta. # implemente os metodos restantes"
        res_stub = self.cortex.audit(draft_stub, query=query_strict)
        self.assertEqual(res_stub["status"], "INHIBITED")
        self.assertTrue(any("placeholder_code" in v for v in res_stub["violations"]))

        # Teste 3: Bloqueio de premissa não testada
        draft_untested = "O codigo foi gerado e deve funcionar sem testar."
        res_untested = self.cortex.audit(draft_untested, query=query_strict)
        self.assertEqual(res_untested["status"], "INHIBITED")
        self.assertTrue(any("unverified_assumption" in v for v in res_untested["violations"]))

        # Teste 4: Aprovação com resposta completa e verificada
        draft_clean = "O modulo foi refatorado. Testes unitarios executados com 100% de sucesso (8/8 testes OK)."
        res_clean = self.cortex.audit(draft_clean, query=query_strict)
        self.assertEqual(res_clean["status"], "APPROVED")
        self.assertTrue(res_clean["passed"])
        self.assertTrue(res_clean["strict_mode"])

    def test_credential_leak_inhibition(self):
        drafts = [
            "token=example-secret-value",
            "api_key: example-secret-value",
            "senha=example-secret-value",
            "credencial: example-secret-value",
        ]
        for draft in drafts:
            res = self.cortex.audit(draft)
            self.assertEqual(res["status"], "INHIBITED")
            self.assertFalse(res["passed"])
            self.assertTrue(any("credential_leak" in v for v in res["violations"]))

        clean_draft = "Credenciais permanecem redigidas e nunca sao impressas."
        res_clean = self.cortex.audit(clean_draft)
        self.assertEqual(res_clean["status"], "APPROVED")
        self.assertTrue(res_clean["passed"])

    def test_behavioral_profiling_leak_inhibition(self):
        # Bloqueio de explicacao detalhada de perfil do operador em desafios (Zero Behavioral Leakage)
        drafts = [
            "Acesso negado: o Major opera em Next.js 15 e no monorepo Atlas.",
            "A mensagem viola a assinatura: o operador domina TypeScript e Python.",
            "O lexico autentico do operador inclui girias do Sudeste."
        ]
        for draft in drafts:
            res = self.cortex.audit(draft)
            self.assertEqual(res["status"], "INHIBITED")
            self.assertFalse(res["passed"])
            self.assertTrue(any("behavioral_profiling_leak" in v for v in res["violations"]))

        # Alerta cego minimalista aprovado
        blind_draft = "[ACESSO NEGADO] Assinatura nao autorizada. Execucao inibida pelo Portao Pre-Frontal."
        res_blind = self.cortex.audit(blind_draft)
        self.assertEqual(res_blind["status"], "APPROVED")
        self.assertTrue(res_blind["passed"])


if __name__ == "__main__":
    unittest.main()



