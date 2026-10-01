import unittest

from engine.toklang import (
    AttentionConstraint,
    CompressionDirective,
    CompressionEstimator,
    ContextBlock,
    InstructionBlock,
    PromptDocument,
    TokenBudgetDirective,
    TokenType,
    TokLangLexer,
    TokLangParser,
)


class TestTokLangEngine(unittest.TestCase):
    def test_lexer_tokenization(self):
        source = '@compress(level="aggressive") @budget(max_tokens=500) context "db" { postgres rls }'
        lexer = TokLangLexer(source)
        tokens = lexer.tokenize()

        self.assertTrue(len(tokens) > 0)
        self.assertEqual(tokens[0].type, TokenType.DIRECTIVE)
        self.assertEqual(tokens[0].value, "@compress")

    def test_parser_ast_construction(self):
        source = """
        @compress(level="aggressive", drop_stopwords=true)
        @budget(max_tokens=600, reserve_completion=150)
        @constraint(name="auth_security", focus="rls,jwt")
        context "system" {
            Use PostgreSQL with Row Level Security.
        }
        instruction {
            "Execute test suite"
            "Build migrations"
        }
        """
        lexer = TokLangLexer(source)
        tokens = lexer.tokenize()
        parser = TokLangParser(tokens)
        doc = parser.parse()

        self.assertIsNotNone(doc.compression)
        self.assertEqual(doc.compression.level, "aggressive")
        self.assertTrue(doc.compression.drop_stopwords)

        self.assertIsNotNone(doc.budget)
        self.assertEqual(doc.budget.max_tokens, 600)
        self.assertEqual(doc.budget.reserve_completion, 150)

        self.assertEqual(len(doc.constraints), 1)
        self.assertEqual(doc.constraints[0].name, "auth_security")
        self.assertIn("rls", doc.constraints[0].focus_terms)

        self.assertEqual(len(doc.contexts), 1)
        self.assertEqual(doc.contexts[0].name, "system")
        self.assertIn("PostgreSQL", doc.contexts[0].content)

        self.assertIsNotNone(doc.instruction)
        self.assertEqual(len(doc.instruction.instructions), 2)
        self.assertEqual(doc.instruction.instructions[0], "Execute test suite")

    def test_ast_serialization_roundtrip(self):
        doc = PromptDocument(name="test_doc")
        doc.compression = CompressionDirective(level="lossless")
        doc.budget = TokenBudgetDirective(max_tokens=800)
        doc.constraints.append(AttentionConstraint(name="inviolable_oven", focus_terms=["forno"]))
        doc.contexts.append(ContextBlock(name="cozinha", content="Sem forno embutido"))
        doc.instruction = InstructionBlock(instructions=["Seguir planta"])

        d = doc.to_dict()
        restored = PromptDocument.from_dict(d)

        self.assertEqual(restored.name, doc.name)
        self.assertEqual(restored.compression.level, "lossless")
        self.assertEqual(restored.budget.max_tokens, 800)
        self.assertEqual(len(restored.constraints), 1)
        self.assertEqual(restored.contexts[0].content, "Sem forno embutido")
        self.assertEqual(restored.instruction.instructions, ["Seguir planta"])

    def test_compression_and_flops_estimator(self):
        raw = "Esta e uma solicitacao extremamente verbosa e repetitiva que descreve detalhes irrelevantes para a execucao tecnica da tarefa em questao ao longo de multiplos paragrafos desnecessarios."
        compiled = "Execute a tarefa tecnica com foco direto."

        metrics = CompressionEstimator.estimate_metrics(raw, compiled)

        self.assertGreater(metrics["raw_tokens"], metrics["compiled_tokens"])
        self.assertGreater(metrics["tokens_saved"], 0)
        self.assertGreater(metrics["compression_ratio_percent"], 50.0)
        # O ganho de FLOPs O(N^2) -> O(K^2) deve ser superior a 70%
        self.assertGreater(metrics["attention_flops_reduction_percent"], 70.0)
        self.assertGreater(metrics["theoretical_speedup_factor"], 2.0)


if __name__ == "__main__":
    unittest.main()
