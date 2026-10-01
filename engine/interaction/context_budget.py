"""Token-budgeted context compiler for the ThSyr interaction layer.

The previous implementation concatenated every section and exposed a
max_prompt_tokens setting without enforcing it. This version treats the limit
as a hard budget and gives priority to system invariants, active state,
retrieved evidence, and only then recent conversational history.
"""

from __future__ import annotations

import math

from ..toklang import ContextBlock, PromptDocument, TokenBudgetDirective, TokLangCompiler
from .conversation_state import ConversationState


class ContextBudgetManager:
    def __init__(self, max_prompt_tokens: int = 4000) -> None:
        if max_prompt_tokens <= 0:
            raise ValueError("max_prompt_tokens deve ser maior que zero")
        self.max_prompt_tokens = max_prompt_tokens

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Cheap deterministic estimator used when a tokenizer is unavailable."""
        if not text:
            return 0
        return max(1, math.ceil(len(text) / 4))

    @classmethod
    def _truncate(cls, text: str, token_budget: int, keep_tail: bool = False) -> str:
        if token_budget <= 0 or not text:
            return ""
        if cls.estimate_tokens(text) <= token_budget:
            return text

        char_budget = max(1, token_budget * 4)
        marker = "\n...[contexto truncado por orçamento]...\n"
        usable = max(1, char_budget - len(marker))
        if keep_tail:
            return marker + text[-usable:]
        return text[:usable] + marker

    def build_effective_context(
        self,
        state: ConversationState,
        system_base: str,
        retrieved_pack: str = "",
        max_history_turns: int = 4,
    ) -> str:
        """Build a context that never exceeds the configured token budget."""
        state_lines = ["# ESTADO OPERACIONAL ATIVO"]
        if state.active_subject:
            state_lines.append(f"Sujeito em Foco: {state.active_subject}")
        if state.active_goal:
            state_lines.append(f"Meta Ativa: {state.active_goal}")
        if state.active_project:
            state_lines.append(f"Projeto Ativo: {state.active_project}")
        if state.active_file:
            state_lines.append(f"Arquivo em Foco: {state.active_file}")
        if state.active_plan:
            state_lines.append(f"Plano em Execucao: {state.active_plan}")

        if state.rejected_solutions:
            state_lines.append(
                "# SOLUCOES PREVIAMENTE REJEITADAS PELO OPERADOR (NAO REPETIR)"
            )
            for rejected in state.rejected_solutions[-3:]:
                state_lines.append(
                    f"- {rejected.solution_id}: {rejected.description} "
                    f"(Motivo: {rejected.reason or 'rejeitada'})"
                )

        state_block = "\n".join(state_lines) if len(state_lines) > 1 else ""

        recent_messages = state.messages[-max_history_turns:] if state.messages else []
        history_lines: list[str] = []
        if recent_messages:
            history_lines.append("# HISTORICO RECENTE DE INTERACAO")
            for message in recent_messages:
                role = "OPERADOR" if message["role"] == "user" else "SYR"
                history_lines.append(f"{role}: {message['content']}")
        history_block = "\n".join(history_lines)

        # Soft caps preserve room for evidence and recent state even when one
        # source is abnormally large. Any unused room is consumed by later blocks.
        system_cap = max(1, int(self.max_prompt_tokens * 0.45))
        state_cap = max(0, int(self.max_prompt_tokens * 0.15))
        history_reserve = max(0, int(self.max_prompt_tokens * 0.15))

        parts: list[str] = []
        remaining = self.max_prompt_tokens

        system_part = self._truncate(system_base, min(system_cap, remaining))
        if system_part:
            parts.append(system_part)
            remaining -= self.estimate_tokens(system_part)

        if state_block and remaining > 0:
            allocation = min(state_cap, remaining)
            state_part = self._truncate(state_block, allocation)
            if state_part:
                parts.append(state_part)
                remaining -= self.estimate_tokens(state_part)

        if retrieved_pack and remaining > 0:
            retrieval_budget = max(0, remaining - history_reserve)
            if retrieval_budget == 0 and not history_block:
                retrieval_budget = remaining
            retrieved_part = self._truncate(retrieved_pack, retrieval_budget)
            if retrieved_part:
                parts.append(retrieved_part)
                remaining -= self.estimate_tokens(retrieved_part)

        if history_block and remaining > 0:
            # Keep the tail because the latest turns are usually the most useful.
            history_part = self._truncate(history_block, remaining, keep_tail=True)
            if history_part:
                parts.append(history_part)

        # TokLang is the semantic assembly layer: the already-prioritized
        # sections are represented as context blocks and compiled under a budget.
        # The final estimator remains the hard safety boundary because TokLang's
        # tokenizer is intentionally dependency-free and word-based.
        context_blocks = [
            ContextBlock(
                name=f"runtime_{index}",
                content=part,
                priority=max(1, len(parts) - index),
            )
            for index, part in enumerate(parts)
            if part
        ]
        if context_blocks:
            document = PromptDocument(
                name="thsyr_runtime_context",
                budget=TokenBudgetDirective(max_tokens=self.max_prompt_tokens),
                contexts=context_blocks,
            )
            compiled = TokLangCompiler().compile(document).text
        else:
            compiled = ""

        if self.estimate_tokens(compiled) > self.max_prompt_tokens:
            compiled = self._truncate(compiled, self.max_prompt_tokens, keep_tail=False)
        return compiled
