"""
Reusable render -> vision -> refine loop.

The executor is injected as a callback because ThSyr may use Antigravity, a
coding agent or another executor. The quality loop is independent from the
editing backend.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .contracts import VisualBrief


class VisualRefinementLoop:
    def __init__(self, studio: Any, max_iterations: int = 4) -> None:
        self.studio = studio
        self.max_iterations = max(1, max_iterations)

    def run(
        self,
        *,
        brief: VisualBrief,
        initial_instruction: str,
        executor: Callable[[str, int], Any],
        target_resolver: Callable[[int], str | Path],
        output_root: str | Path = ".thsyr/visual-refinement",
    ) -> dict[str, Any]:
        history = []
        instruction = initial_instruction
        root = Path(output_root)
        outcome_id = self.studio.begin_outcome(brief)
        last_rejected_label: str | None = None

        for iteration in range(1, self.max_iterations + 1):
            executor_result = executor(instruction, iteration)
            target = target_resolver(iteration)
            report = self.studio.review(
                target,
                brief,
                output_dir=root / f"iteration-{iteration}",
            )
            label = f"iteration-{iteration}"
            verdict = "approved" if report.get("passed") else "rejected"
            self.studio.record_outcome_version(
                outcome_id,
                label=label,
                artifact_ref=str(target),
                verdict=verdict,
                review_report=report,
            )
            history.append({
                "iteration": iteration,
                "instruction": instruction,
                "executor_result": str(executor_result)[:1000],
                "target": str(target),
                "report": report,
            })
            if report.get("passed"):
                learned_outcome = None
                if last_rejected_label:
                    learned_outcome = self.studio.resolve_outcome(
                        outcome_id,
                        rejected_label=last_rejected_label,
                        approved_label=label,
                        note="aprovacao apos ciclo visual automatico",
                    )
                return {
                    "status": "passed",
                    "iterations": iteration,
                    "history": history,
                    "final_report": report,
                    "outcome_id": outcome_id,
                    "outcome_learning": learned_outcome,
                }
            last_rejected_label = label
            instruction = report["refinement_prompt"]

        return {
            "status": "blocked",
            "iterations": self.max_iterations,
            "history": history,
            "final_report": history[-1]["report"] if history else None,
            "outcome_id": outcome_id,
            "outcome_learning": None,
        }
