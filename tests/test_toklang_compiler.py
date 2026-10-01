import unittest

from engine.toklang import (
    AttentionConstraint,
    ContextBlock,
    InstructionBlock,
    PromptDocument,
    TokenBudgetDirective,
    TokLangCompiler,
)


class TestTokLangCompiler(unittest.TestCase):
    def test_compiles_priority_context_under_budget(self):
        document = PromptDocument(
            name="security",
            budget=TokenBudgetDirective(max_tokens=8),
            constraints=[AttentionConstraint(name="rls", focus_terms=["tenant_id"])],
            contexts=[
                ContextBlock(name="low", content="low priority context", priority=1),
                ContextBlock(name="high", content="high priority context", priority=2),
            ],
            instruction=InstructionBlock(["Execute safely"]),
        )
        result = TokLangCompiler().compile(document)
        self.assertLessEqual(result.token_count, 8)
        self.assertTrue(result.truncated)
        self.assertIn("high", result.text)
        self.assertEqual(result.constraints, ("rls: tenant_id",))

    def test_rejects_invalid_budget(self):
        with self.assertRaises(ValueError):
            TokLangCompiler().compile(PromptDocument(budget=TokenBudgetDirective(max_tokens=0)))


if __name__ == "__main__":
    unittest.main()
