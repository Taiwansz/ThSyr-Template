"""
ThSyr Executive System - Modelos de Dados (Fase 4)
Define contratos e estruturas formais para execucao orientada a objetivos:
- Goal: Objetivo de alto nivel
- Step: Etapa discreta de acao
- Plan: Sequencia estruturada de passos
- Observation: Evidencia/resultado de uma etapa
- VerificationResult: Validacao da observacao pos-execucao
- ExecutionResult: Resumo consolidado do ciclo executivo
"""

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class GoalStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILURE = "failure"
    SKIPPED = "skipped"


class ActionType(str, Enum):
    SEARCH_MEMORY = "search_memory"
    READ_FILE = "read_file"
    INSPECT_GIT = "inspect_git"
    ANALYZE = "analyze"
    SYNTHESIZE = "synthesize"
    EXECUTE_COMMAND = "execute_command"
    CUSTOM = "custom"


@dataclass
class Step:
    id: str
    order: int
    action: str
    target: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)
    status: StepStatus = StepStatus.PENDING
    observation: str | None = None
    error: str | None = None
    started_at: str | None = None
    completed_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Step":
        status = StepStatus(data.get("status", StepStatus.PENDING.value))
        return cls(
            id=data["id"],
            order=data.get("order", 0),
            action=data.get("action", ActionType.CUSTOM.value),
            target=data.get("target", ""),
            description=data.get("description", ""),
            parameters=data.get("parameters", {}),
            status=status,
            observation=data.get("observation"),
            error=data.get("error"),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at")
        )


@dataclass
class Goal:
    id: str
    title: str
    description: str
    project: str | None = None
    priority: int = 3
    status: GoalStatus = GoalStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Goal":
        status = GoalStatus(data.get("status", GoalStatus.PENDING.value))
        return cls(
            id=data["id"],
            title=data.get("title", ""),
            description=data.get("description", ""),
            project=data.get("project"),
            priority=data.get("priority", 3),
            status=status,
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat()),
            metadata=data.get("metadata", {})
        )


@dataclass
class Plan:
    id: str
    goal_id: str
    title: str
    steps: list[Step] = field(default_factory=list)
    replan_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "goal_id": self.goal_id,
            "title": self.title,
            "replan_count": self.replan_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "steps": [s.to_dict() for s in self.steps]
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Plan":
        steps = [Step.from_dict(s) for s in data.get("steps", [])]
        return cls(
            id=data["id"],
            goal_id=data.get("goal_id", ""),
            title=data.get("title", ""),
            steps=steps,
            replan_count=data.get("replan_count", 0),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat())
        )


@dataclass
class Observation:
    step_id: str
    success: bool
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    evidence_id: str = field(default_factory=lambda: f"ev_{uuid.uuid4().hex[:12]}")
    before_state_hash: Optional[str] = None
    after_state_hash: Optional[str] = None
    exit_code: int = 0
    stdout_hash: Optional[str] = None
    stderr_hash: Optional[str] = None
    diff: Optional[str] = None
    data: Any = None
    raw_output: str = ""
    error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Observation":
        return cls(
            step_id=data.get("step_id", ""),
            success=data.get("success", False),
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            evidence_id=data.get("evidence_id", f"ev_{uuid.uuid4().hex[:12]}"),
            before_state_hash=data.get("before_state_hash"),
            after_state_hash=data.get("after_state_hash"),
            exit_code=data.get("exit_code", 0),
            stdout_hash=data.get("stdout_hash"),
            stderr_hash=data.get("stderr_hash"),
            diff=data.get("diff"),
            data=data.get("data"),
            raw_output=data.get("raw_output", ""),
            error=data.get("error")
        )


@dataclass
class VerificationResult:
    verified: bool
    status: str  # PASS, FAIL, REPLAN, ABORT
    score: float
    feedback: str
    suggested_action: str  # NEXT_STEP, REPLAN, ABORT, FINISH

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ExecutionResult:
    goal_id: str
    plan_id: str
    status: GoalStatus
    completed_steps: int
    total_steps: int
    observations: list[Observation] = field(default_factory=list)
    final_summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "plan_id": self.plan_id,
            "status": self.status.value,
            "completed_steps": self.completed_steps,
            "total_steps": self.total_steps,
            "observations": [o.to_dict() for o in self.observations],
            "final_summary": self.final_summary
        }
