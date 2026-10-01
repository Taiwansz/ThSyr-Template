"""
ThSyr Interaction Layer - Response Models
Contrato estruturado para respostas cognitivas e operacionais.
Garante progressive disclosure e desacoplamento do renderer.
"""

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Optional


class ResponseKind(str, Enum):
    CHAT = "chat"
    OPERATIONAL = "operational"
    ANALYSIS = "analysis"
    APPROVAL = "approval"
    ERROR = "error"
    WARNING = "warning"
    RESULT = "result"
    PROACTIVE = "proactive"


class SourceType(str, Enum):
    OBSERVED = "observed"
    RETRIEVED = "retrieved"
    INFERRED = "inferred"
    ASSUMED = "assumed"


@dataclass
class ResponseSource:
    kind: SourceType
    identifier: str
    description: str
    location: Optional[str] = None
    confidence: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind.value,
            "identifier": self.identifier,
            "description": self.description,
            "location": self.location,
            "confidence": self.confidence,
        }


@dataclass
class ResponseAction:
    id: str
    label: str
    command: str
    shortcut: Optional[str] = None
    is_primary: bool = False
    requires_confirmation: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class StructuredResponse:
    summary: str
    answer: str
    kind: ResponseKind = ResponseKind.CHAT
    details: Optional[str] = None
    evidence: list[dict[str, Any]] = field(default_factory=list)
    sources: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    confidence: Optional[dict[str, Any]] = None
    actions: list[dict[str, Any]] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)
    status: Optional[str] = None
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    changes: list[dict[str, Any]] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)
    references: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def has_details(self) -> bool:
        return bool(self.details and self.details.strip())

    def has_evidence(self) -> bool:
        return bool(self.evidence)

    def has_sources(self) -> bool:
        return bool(self.sources)

    def has_changes(self) -> bool:
        return bool(self.changes)

    def has_actions(self) -> bool:
        return bool(self.actions)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind.value,
            "summary": self.summary,
            "answer": self.answer,
            "details": self.details,
            "evidence": self.evidence,
            "sources": self.sources,
            "warnings": self.warnings,
            "confidence": self.confidence,
            "actions": self.actions,
            "questions": self.questions,
            "status": self.status,
            "artifacts": self.artifacts,
            "changes": self.changes,
            "next_steps": self.next_steps,
            "references": self.references,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StructuredResponse":
        kind_str = data.get("kind", ResponseKind.CHAT.value)
        try:
            kind = ResponseKind(kind_str)
        except ValueError:
            kind = ResponseKind.CHAT

        return cls(
            summary=data.get("summary", ""),
            answer=data.get("answer", ""),
            kind=kind,
            details=data.get("details"),
            evidence=data.get("evidence", []),
            sources=data.get("sources", []),
            warnings=data.get("warnings", []),
            confidence=data.get("confidence"),
            actions=data.get("actions", []),
            questions=data.get("questions", []),
            status=data.get("status"),
            artifacts=data.get("artifacts", []),
            changes=data.get("changes", []),
            next_steps=data.get("next_steps", []),
            references=data.get("references", []),
            metadata=data.get("metadata", {}),
        )
