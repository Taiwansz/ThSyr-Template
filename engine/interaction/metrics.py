"""
ThSyr Interaction Layer - Local Interaction Metrics
Coleta metricas locais e privadas para calibrar a qualidade da interacao
(tamanho de resposta, interrupcoes, sucesso de resolucao de referencias, etc.).
"""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

from ..config import get_state_dir, setup_logger

logger = setup_logger("interaction_metrics")


@dataclass
class InteractionMetrics:
    total_turns: int = 0
    total_words_generated: int = 0
    average_response_words: float = 0.0
    user_interrupts: int = 0
    clarifications_requested: int = 0
    reference_resolution_failures: int = 0
    approval_cancellations: int = 0
    details_expansions: int = 0
    user_corrections: int = 0
    command_usage: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InteractionMetrics":
        valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid)


class InteractionMetricsCollector:
    def __init__(self, metrics_file: Optional[Path] = None):
        self.metrics_file = metrics_file or (get_state_dir() / "interaction_metrics.json")
        self.metrics = self._load()

    def _load(self) -> InteractionMetrics:
        if not self.metrics_file.exists():
            return InteractionMetrics()
        try:
            with open(self.metrics_file, "r", encoding="utf-8") as f:
                return InteractionMetrics.from_dict(json.load(f))
        except Exception:
            return InteractionMetrics()

    def save(self) -> None:
        try:
            self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.metrics_file, "w", encoding="utf-8") as f:
                json.dump(self.metrics.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Erro ao salvar interaction_metrics.json: {e}")

    def record_turn(self, response_text: str) -> None:
        self.metrics.total_turns += 1
        word_count = len(response_text.split())
        self.metrics.total_words_generated += word_count
        self.metrics.average_response_words = (
            self.metrics.total_words_generated / self.metrics.total_turns
        )
        self.save()

    def record_command(self, command_name: str) -> None:
        self.metrics.command_usage[command_name] = (
            self.metrics.command_usage.get(command_name, 0) + 1
        )
        if command_name in ("/details", "detalhes"):
            self.metrics.details_expansions += 1
        self.save()

    def record_interrupt(self) -> None:
        self.metrics.user_interrupts += 1
        self.save()

    def record_reference_failure(self) -> None:
        self.metrics.reference_resolution_failures += 1
        self.save()

    def record_approval_cancellation(self) -> None:
        self.metrics.approval_cancellations += 1
        self.save()

    def record_correction(self) -> None:
        self.metrics.user_corrections += 1
        self.save()
