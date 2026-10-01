"""Conservative contradiction detection for semantic memory.

The detector only flags candidates with substantial lexical overlap and
opposing assertion markers. It is intentionally conservative: a weak match is
reported as related, not contradictory.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass

from .memory_models import MemoryItem

_NEGATIONS = {"nao", "não", "nunca", "sem", "proibido", "desativado", "false", "falso"}
_POSITIVE = {"sim", "ativo", "ativado", "permitido", "true", "verdadeiro", "usar", "usa"}


@dataclass(frozen=True)
class ContradictionMatch:
    memory_id: str
    score: float
    reason: str


class MemoryContradictionDetector:
    @staticmethod
    def _tokens(text: str) -> set[str]:
        return {
            token
            for token in re.findall(r"\b[\wÀ-ÿ-]{3,}\b", text.lower())
            if token not in {"para", "como", "com", "uma", "que", "por", "dos", "das"}
        }

    @classmethod
    def detect(
        cls,
        title: str,
        content: str,
        candidates: Iterable[MemoryItem],
    ) -> list[ContradictionMatch]:
        incoming_text = f"{title} {content}"
        incoming_tokens = cls._tokens(incoming_text)
        incoming_negative = bool(incoming_tokens & _NEGATIONS)
        incoming_positive = bool(incoming_tokens & _POSITIVE)
        matches: list[ContradictionMatch] = []

        for item in candidates:
            existing_text = f"{item.title} {item.content}"
            existing_tokens = cls._tokens(existing_text)
            union = incoming_tokens | existing_tokens
            if not union:
                continue
            overlap = len(incoming_tokens & existing_tokens) / len(union)
            if overlap < 0.28:
                continue

            existing_negative = bool(existing_tokens & _NEGATIONS)
            existing_positive = bool(existing_tokens & _POSITIVE)
            polarity_flip = (
                incoming_negative != existing_negative
                and (incoming_positive or existing_positive or incoming_negative or existing_negative)
            )
            if polarity_flip:
                matches.append(
                    ContradictionMatch(
                        memory_id=item.metadata.id,
                        score=round(min(1.0, 0.55 + overlap), 4),
                        reason="high lexical overlap with opposing assertion polarity",
                    )
                )

        matches.sort(key=lambda match: match.score, reverse=True)
        return matches
