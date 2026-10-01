"""Deterministic TokLang compiler from AST documents to bounded prompts."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .ast_nodes import PromptDocument


@dataclass(frozen=True)
class CompiledPrompt:
    text: str
    token_count: int
    max_tokens: int
    truncated: bool
    constraints: tuple[str, ...]


class TokLangCompiler:
    """Compiles parsed TokLang without model calls or silent budget overflow."""

    @staticmethod
    def _tokens(text: str) -> list[str]:
        return re.findall(r"\S+", text)

    def compile(self, document: PromptDocument) -> CompiledPrompt:
        budget = document.budget.max_tokens if document.budget else 1000
        if budget <= 0:
            raise ValueError("TokLang budget must be positive.")

        sections: list[str] = []
        for context in sorted(document.contexts, key=lambda item: item.priority, reverse=True):
            sections.append(f"[context:{context.name}]\n{context.content.strip()}")

        constraints = tuple(
            f"{constraint.name}: {', '.join(constraint.focus_terms)}"
            for constraint in document.constraints
        )
        if constraints:
            sections.append("[constraints]\n" + "\n".join(f"- {item}" for item in constraints))
        if document.instruction and document.instruction.instructions:
            sections.append(
                "[instructions]\n"
                + "\n".join(f"- {instruction}" for instruction in document.instruction.instructions)
            )

        raw = "\n\n".join(section for section in sections if section)
        words = self._tokens(raw)
        truncated = len(words) > budget
        compiled = " ".join(words[:budget])
        return CompiledPrompt(
            text=compiled,
            token_count=len(self._tokens(compiled)),
            max_tokens=budget,
            truncated=truncated,
            constraints=constraints,
        )
