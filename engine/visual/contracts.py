"""
Contratos tipados do ThSyr Visual Studio.
O objetivo deste modulo e tornar o fluxo visual observavel, testavel e impossivel
de "aprovar por feeling" sem evidencia renderizada.
"""

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class VisualArtifactKind(str, Enum):
    WEBSITE = "website"
    UI_SCREEN = "ui_screen"
    IMAGE = "image"
    ICON = "icon"
    LOGO = "logo"
    OTHER = "other"


class IssueSeverity(str, Enum):
    BLOCKER = "blocker"
    MAJOR = "major"
    MINOR = "minor"


@dataclass
class VisualBrief:
    objective: str
    artifact_kind: VisualArtifactKind = VisualArtifactKind.WEBSITE
    niche: str | None = None
    audience: str | None = None
    desired_impression: str | None = None
    brand_constraints: list[str] = field(default_factory=list)
    must_have: list[str] = field(default_factory=list)
    must_avoid: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    project_id: str | None = None
    domain: str = "design"
    minimum_score: int = 85
    minimum_dimension_score: int = 70

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["artifact_kind"] = self.artifact_kind.value
        return data


@dataclass
class CritiqueIssue:
    severity: IssueSeverity
    category: str
    problem: str
    evidence: str
    fix: str
    viewport: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["severity"] = self.severity.value
        return data


@dataclass
class VisualCritique:
    passed: bool
    score: int
    summary: str
    scores: dict[str, int]
    issues: list[CritiqueIssue]
    viewport: str
    provider_name: str = "unknown"
    model_name: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "score": self.score,
            "summary": self.summary,
            "scores": dict(self.scores),
            "issues": [issue.to_dict() for issue in self.issues],
            "viewport": self.viewport,
            "provider_name": self.provider_name,
            "model_name": self.model_name,
        }
