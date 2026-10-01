"""Repository secret and legacy credential scanner.

The scanner reports locations and redacts values. It never returns secret
material in findings.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .config import settings

_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("assignment-secret", re.compile(r"(?i)\b(password|passwd|token|api[_-]?key|secret)\s*[:=]\s*['\"]?([^\s'\"]{6,})")),
    ("bearer-token", re.compile(r"(?i)\bbearer\s+([A-Za-z0-9._~+/=-]{12,})")),
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
)


@dataclass(frozen=True)
class SecretFinding:
    path: str
    line: int
    kind: str
    preview: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RepositorySecretScanner:
    DEFAULT_SUFFIXES = frozenset({
        ".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".ini", ".env",
    })

    def __init__(self, root: Path | None = None) -> None:
        self.root = (root or settings.project_root).resolve()

    @staticmethod
    def _redact(line: str) -> str:
        redacted = line
        for kind, pattern in _PATTERNS:
            if kind == "private-key":
                if pattern.search(redacted):
                    return "[REDACTED PRIVATE KEY HEADER]"
                continue
            redacted = pattern.sub(lambda match: f"{match.group(1) if match.lastindex and match.lastindex > 1 else 'secret'}=[REDACTED]", redacted)
        return redacted[:240]

    def scan(self, paths: Iterable[Path] | None = None) -> list[SecretFinding]:
        candidates = list(paths) if paths is not None else list(self.root.rglob("*"))
        findings: list[SecretFinding] = []
        for path in candidates:
            if not path.is_file():
                continue
            if ".git" in path.parts or "__pycache__" in path.parts:
                continue
            if path.suffix.lower() not in self.DEFAULT_SUFFIXES and not path.name.startswith(".env"):
                continue
            try:
                lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
            except OSError:
                continue
            for number, line in enumerate(lines, 1):
                for kind, pattern in _PATTERNS:
                    if pattern.search(line):
                        findings.append(
                            SecretFinding(
                                path=str(path.relative_to(self.root)),
                                line=number,
                                kind=kind,
                                preview=self._redact(line),
                            )
                        )
                        break
        return findings
