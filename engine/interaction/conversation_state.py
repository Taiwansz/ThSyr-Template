"""
ThSyr Interaction Layer - Conversation State
Mantem estado conversacional continuo: sujeitos ativos, metas ativas,
arquivos e planos em foco, historico de decisoes, solucoes rejeitadas
e handoff conversacional versionado para persistencia entre sessoes.
"""

import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from ..config import get_state_dir, setup_logger
from .conversation_objects import ConversationObjectRegistry
from .response_models import StructuredResponse

logger = setup_logger("conversation_state")


@dataclass
class SolutionRecord:
    solution_id: str
    description: str
    status: str  # 'accepted', 'rejected', 'modified'
    reason: Optional[str] = None
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class ConversationState:
    def __init__(self, session_id: Optional[str] = None):
        self.session_id: str = session_id or f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        self.active_subject: Optional[str] = None
        self.active_goal: Optional[str] = None
        self.active_project: Optional[str] = None
        self.active_file: Optional[str] = None
        self.active_plan: Optional[str] = None
        self.active_change_set: Optional[str] = None

        self.messages: list[dict[str, Any]] = []
        self.object_registry = ConversationObjectRegistry()
        self.rejected_solutions: list[SolutionRecord] = []
        self.accepted_solutions: list[SolutionRecord] = []
        self.last_response: Optional[StructuredResponse] = None
        self.turn_count: int = 0

    def add_message(self, role: str, content: str, metadata: Optional[dict[str, Any]] = None) -> None:
        self.messages.append({
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "turn": self.turn_count,
        })
        if role == "user":
            self.turn_count += 1
            self.object_registry.tick_turn()

    def record_rejection(self, solution_id: str, description: str, reason: Optional[str] = None) -> None:
        rec = SolutionRecord(solution_id=solution_id, description=description, status="rejected", reason=reason)
        self.rejected_solutions.append(rec)

    def record_acceptance(self, solution_id: str, description: str) -> None:
        rec = SolutionRecord(solution_id=solution_id, description=description, status="accepted")
        self.accepted_solutions.append(rec)

    def is_solution_rejected(self, solution_id: str) -> bool:
        return any(r.solution_id == solution_id for r in self.rejected_solutions)

    def set_active_context(
        self,
        subject: Optional[str] = None,
        goal: Optional[str] = None,
        project: Optional[str] = None,
        file: Optional[str] = None,
        plan: Optional[str] = None,
        change_set: Optional[str] = None,
    ) -> None:
        if subject is not None:
            self.active_subject = subject
        if goal is not None:
            self.active_goal = goal
        if project is not None:
            self.active_project = project
        if file is not None:
            self.active_file = file
        if plan is not None:
            self.active_plan = plan
        if change_set is not None:
            self.active_change_set = change_set

    def get_git_revision(self) -> str:
        try:
            res = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                check=False,
            )
            return res.stdout.strip() or "unknown"
        except Exception:
            return "unknown"

    def export_handoff(self) -> dict[str, Any]:
        """Cria um pacote de handoff conversacional versionado com vinculo de commit git."""
        return {
            "session_id": self.session_id,
            "git_revision": self.get_git_revision(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "active_subject": self.active_subject,
            "active_goal": self.active_goal,
            "active_project": self.active_project,
            "active_file": self.active_file,
            "active_plan": self.active_plan,
            "active_change_set": self.active_change_set,
            "rejected_solutions": [asdict(r) for r in self.rejected_solutions],
            "accepted_solutions": [asdict(r) for r in self.accepted_solutions],
            "last_summary": self.last_response.summary if self.last_response else None,
            "turn_count": self.turn_count,
        }

    def save_handoff(self, target_path: Optional[Path] = None) -> Path:
        path = target_path or (get_state_dir() / "interaction_handoff.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.export_handoff(), f, indent=2, ensure_ascii=False)
        return path

    def load_handoff(self, source_path: Optional[Path] = None) -> bool:
        path = source_path or (get_state_dir() / "interaction_handoff.json")
        if not path.exists():
            return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.session_id = data.get("session_id", self.session_id)
            self.active_subject = data.get("active_subject")
            self.active_goal = data.get("active_goal")
            self.active_project = data.get("active_project")
            self.active_file = data.get("active_file")
            self.active_plan = data.get("active_plan")
            self.active_change_set = data.get("active_change_set")
            self.turn_count = data.get("turn_count", 0)

            for rej in data.get("rejected_solutions", []):
                self.rejected_solutions.append(SolutionRecord(**rej))
            for acc in data.get("accepted_solutions", []):
                self.accepted_solutions.append(SolutionRecord(**acc))
            return True
        except Exception as e:
            logger.warning(f"Falha ao carregar interaction_handoff.json: {e}")
            return False
