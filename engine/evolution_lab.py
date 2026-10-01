"""Governed Evolution Lab for candidate code changes.

Candidates are evaluated inside a disposable Git worktree. The main workspace
is never mutated by the lab. A candidate is accepted only when every configured
quality gate succeeds.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .config import settings, setup_logger
from .models.base import ChatMessage, ModelRequest, ModelRole, ModelTier
from .models.gateway import ModelGateway

logger = setup_logger("evolution_lab")


@dataclass
class GateResult:
    command: list[str]
    returncode: int
    stdout_tail: str
    stderr_tail: str

    @property
    def passed(self) -> bool:
        return self.returncode == 0

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["passed"] = self.passed
        return payload


@dataclass
class EvolutionCandidate:
    id: str
    objective: str
    patch_text: str
    source: str = "manual"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvolutionVerdict:
    candidate_id: str
    accepted: bool
    reason: str
    gates: list[GateResult] = field(default_factory=list)
    baseline_gates: list[GateResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "accepted": self.accepted,
            "reason": self.reason,
            "gates": [gate.to_dict() for gate in self.gates],
            "baseline_gates": [gate.to_dict() for gate in self.baseline_gates],
        }


class EvolutionLab:
    DEFAULT_GATES: tuple[tuple[str, ...], ...] = (
        ("python", "-m", "ruff", "check", "."),
        ("python", "-m", "mypy", "engine"),
        ("python", "-m", "unittest", "discover", "-s", "tests"),
    )

    def __init__(
        self,
        project_root: Path | None = None,
        gateway: ModelGateway | None = None,
        gates: tuple[tuple[str, ...], ...] | None = None,
    ) -> None:
        self.project_root = (project_root or settings.project_root).resolve()
        self.gateway = gateway or ModelGateway()
        self.gates = gates or self.DEFAULT_GATES

    @staticmethod
    def _tail(text: str, limit: int = 4000) -> str:
        return text[-limit:] if len(text) > limit else text

    def _run(self, command: list[str], cwd: Path, timeout: int = 240) -> GateResult:
        executable = command[0]
        if executable == "python":
            executable = os.environ.get("PYTHON", sys.executable)
        resolved = [executable, *command[1:]]
        proc = subprocess.run(
            resolved,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
        return GateResult(
            command=resolved,
            returncode=proc.returncode,
            stdout_tail=self._tail(proc.stdout),
            stderr_tail=self._tail(proc.stderr),
        )

    def _run_gates(self, cwd: Path, *, stop_on_failure: bool = True) -> list[GateResult]:
        results: list[GateResult] = []
        for gate in self.gates:
            result = self._run(list(gate), cwd=cwd)
            results.append(result)
            if stop_on_failure and not result.passed:
                break
        return results

    @staticmethod
    def _all_passed(results: list[GateResult]) -> bool:
        return bool(results) and all(result.passed for result in results)

    @staticmethod
    def _diagnostic_fingerprints(result: GateResult) -> set[str]:
        if result.passed:
            return set()
        text = "\n".join([result.stdout_tail, result.stderr_tail])
        fingerprints: set[str] = set()
        for raw in text.splitlines():
            line = raw.strip()
            if not line:
                continue
            if not re.search(
                r"(?:^|\s)(?:E\d{3}|F\d{3}|I\d{3}|error:|FAILED|FAIL:|AssertionError|Traceback)",
                line,
                re.IGNORECASE,
            ):
                continue
            normalized = re.sub(r"^[A-Za-z]:?[\\/].*?[\\/]", "", line)
            normalized = re.sub(r"\bline\s+\d+\b", "line #", normalized, flags=re.IGNORECASE)
            normalized = re.sub(r":\d+(?::\d+)?", ":#", normalized)
            fingerprints.add(normalized[:500])
        if not fingerprints:
            fingerprints.add(f"returncode:{result.returncode}")
        return fingerprints

    @classmethod
    def _differential_regressions(
        cls,
        baseline: list[GateResult],
        candidate: list[GateResult],
    ) -> list[str]:
        regressions: list[str] = []
        for index, base in enumerate(baseline):
            if index >= len(candidate):
                regressions.append(f"missing candidate gate at index {index}")
                continue
            cand = candidate[index]
            label = " ".join(base.command)
            if base.passed and not cand.passed:
                regressions.append(f"previously green gate became red: {label}")
                continue
            if base.passed or cand.passed:
                continue
            base_issues = cls._diagnostic_fingerprints(base)
            cand_issues = cls._diagnostic_fingerprints(cand)
            new_issues = cand_issues - base_issues
            if new_issues:
                regressions.append(
                    f"new diagnostics in pre-existing red gate {label}: "
                    + " | ".join(sorted(new_issues)[:5])
                )
        return regressions

    def evaluate_candidate(self, candidate: EvolutionCandidate) -> EvolutionVerdict:
        if not candidate.patch_text.strip():
            return EvolutionVerdict(
                candidate_id=candidate.id,
                accepted=False,
                reason="candidate patch is empty",
            )
        if not (self.project_root / ".git").exists():
            return EvolutionVerdict(
                candidate_id=candidate.id,
                accepted=False,
                reason="project root is not a Git repository",
            )

        baseline = self._run_gates(self.project_root, stop_on_failure=False)
        baseline_green = self._all_passed(baseline)

        temp_parent = Path(tempfile.mkdtemp(prefix="thsyr-evolution-"))
        worktree = temp_parent / "candidate"
        try:
            add = subprocess.run(
                ["git", "worktree", "add", "--detach", str(worktree), "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
            if add.returncode != 0:
                return EvolutionVerdict(
                    candidate_id=candidate.id,
                    accepted=False,
                    reason=f"failed to create disposable worktree: {self._tail(add.stderr, 800)}",
                    baseline_gates=baseline,
                )

            patch_file = temp_parent / "candidate.diff"
            patch_file.write_text(candidate.patch_text, encoding="utf-8")
            applied = subprocess.run(
                ["git", "apply", "--whitespace=error", str(patch_file)],
                cwd=worktree,
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
            if applied.returncode != 0:
                return EvolutionVerdict(
                    candidate_id=candidate.id,
                    accepted=False,
                    reason=f"patch rejected by git apply: {self._tail(applied.stderr, 1200)}",
                    baseline_gates=baseline,
                )

            results = self._run_gates(worktree, stop_on_failure=False)
            regressions = self._differential_regressions(baseline, results)
            if regressions:
                return EvolutionVerdict(
                    candidate_id=candidate.id,
                    accepted=False,
                    reason="differential quality regression: " + " || ".join(regressions[:4]),
                    gates=results,
                    baseline_gates=baseline,
                )

            if self._all_passed(results):
                reason = "candidate passed all quality gates in disposable worktree"
            elif baseline_green:
                reason = "candidate preserved the green baseline without regressions"
            else:
                reason = (
                    "candidate introduced no new diagnostics relative to the existing technical-debt baseline"
                )
            return EvolutionVerdict(
                candidate_id=candidate.id,
                accepted=True,
                reason=reason,
                gates=results,
                baseline_gates=baseline,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return EvolutionVerdict(
                candidate_id=candidate.id,
                accepted=False,
                reason=f"evolution lab runtime failure: {exc}",
                baseline_gates=baseline,
            )
        finally:
            if worktree.exists():
                subprocess.run(
                    ["git", "worktree", "remove", "--force", str(worktree)],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=60,
                )
            shutil.rmtree(temp_parent, ignore_errors=True)

    def promote_candidate(self, candidate: EvolutionCandidate) -> tuple[bool, str]:
        """Apply an already-validated patch only when explicit promotion is enabled."""
        if os.getenv("THSYR_EVOLUTION_AUTO_PROMOTE", "").lower() not in {"1", "true", "yes"}:
            return False, "automatic promotion is disabled"
        patch_file = self.project_root / ".thsyr_evolution_candidate.diff"
        try:
            patch_file.write_text(candidate.patch_text, encoding="utf-8")
            applied = subprocess.run(
                ["git", "apply", "--whitespace=error", str(patch_file)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
            if applied.returncode != 0:
                return False, f"promotion failed: {self._tail(applied.stderr, 1200)}"
            return True, "candidate patch promoted to active workspace"
        finally:
            try:
                patch_file.unlink(missing_ok=True)
            except OSError:
                pass

    def generate_candidate(
        self,
        objective: str,
        file_context: dict[str, str],
    ) -> EvolutionCandidate | None:
        if os.getenv("THSYR_EVOLUTION_AUTOCODE", "").lower() not in {"1", "true", "yes"}:
            return None
        if not self.gateway.providers:
            return None

        trimmed_context = {
            path: content[:12000]
            for path, content in list(file_context.items())[:6]
        }
        request = ModelRequest(
            tier=ModelTier.REASONING,
            temperature=0.05,
            max_tokens=5000,
            metadata={"component": "evolution_lab"},
            messages=[
                ChatMessage(
                    role=ModelRole.SYSTEM,
                    content=(
                        "Voce e o Evolution Lab do ThSyr. Produza uma mudanca minima e reversivel "
                        "para atingir o objetivo. Responda SOMENTE JSON com objective:str e "
                        "patch_text:str contendo unified diff aplicavel por git apply. Nao altere "
                        "credenciais, politicas de permissao ou arquivos fora do contexto fornecido."
                    ),
                ),
                ChatMessage(
                    role=ModelRole.USER,
                    content=json.dumps(
                        {"objective": objective, "files": trimmed_context},
                        ensure_ascii=False,
                    ),
                ),
            ],
        )
        try:
            response = self.gateway.generate(request)
            payload = json.loads(response.content.strip())
        except Exception:
            return None
        if not isinstance(payload, dict):
            return None
        patch_text = str(payload.get("patch_text", "")).strip()
        if not patch_text:
            return None
        return EvolutionCandidate(
            id=f"evo_candidate_{uuid.uuid4().hex[:10]}",
            objective=str(payload.get("objective", objective)),
            patch_text=patch_text,
            source="model_gateway",
        )
