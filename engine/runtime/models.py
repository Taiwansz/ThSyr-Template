"""
ThSyr Runtime Models (Fase 7 e Fase 8)
Contratos formais para o Runtime Continuo e Proactive Engine:
- Job: Tarefa agendada ou enfileirada no Event Loop
- RuntimeNotification: Alerta gerado pelo sistema
- ProactivityEvaluation: Calculo formal de interrupcao proativa
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Job:
    id: str
    name: str
    interval_seconds: int = 0  # 0 significa tarefa one-shot
    next_run_at: float = 0.0   # timestamp epoch
    last_run_at: float | None = None
    status: JobStatus = JobStatus.PENDING
    handler_name: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d


@dataclass
class RuntimeNotification:
    id: str
    title: str
    message: str
    importance: float  # 0.0 a 1.0
    urgency: float     # 0.0 a 1.0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    delivered: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProactivityEvaluation:
    observation: str
    importance: float       # Peso 0.0 a 1.0 (relevancia para objetivos do operador)
    urgency: float          # Peso 0.0 a 1.0 (proximidade de prazo ou dano)
    actionability: float    # Peso 0.0 a 1.0 (se o operador pode agir agora)
    confidence: float       # Peso 0.0 a 1.0 (certeza do dado)
    interruption_cost: float# Custo 0.0 a 1.0 (risco de quebra de foco do operador)
    score: float = 0.0
    should_interrupt: bool = False
    rationale: str = ""

    def calculate(self, threshold: float = 1.2) -> "ProactivityEvaluation":
        """
        Calcula a pontuacao proativa canônica:
        score = importance + urgency + actionability + confidence - interruption_cost
        """
        self.score = round(
            self.importance + self.urgency + self.actionability + self.confidence - self.interruption_cost,
            3
        )
        self.should_interrupt = self.score >= threshold
        if self.should_interrupt:
            self.rationale = f"Interrupcao proativa recomendada (Score {self.score} >= {threshold})."
        else:
            self.rationale = f"Registro silencioso em working state (Score {self.score} < {threshold})."
        return self

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
