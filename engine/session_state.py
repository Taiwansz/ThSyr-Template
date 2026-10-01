"""
ThSyr Session State & Handoff Manager
Gerencia a continuidade operacional cross-device do Syr, implementando os
modelos de Working State, Session Checkpoint e Session Handoff.
"""

import json
import subprocess
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import settings, setup_logger

logger = setup_logger("session_state")


@dataclass
class SessionState:
    session_id: str = field(default_factory=lambda: (
        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ") + "_" + uuid.uuid4().hex[:6]
    ))
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    current_goal: str = ""
    current_project: str = "ThSyr"
    active_context: str = ""
    open_tasks: list[str] = field(default_factory=list)
    current_plan: list[str] = field(default_factory=list)
    completed_steps: list[str] = field(default_factory=list)
    pending_steps: list[str] = field(default_factory=list)
    next_action: str = ""
    active_files: list[str] = field(default_factory=list)
    recent_decisions: list[str] = field(default_factory=list)
    unresolved_questions: list[str] = field(default_factory=list)
    handoff_summary: str = ""
    git_revision: str = ""

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SessionState":
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)

    @classmethod
    def create_new(cls, project: str = "ThSyr", goal: str = "") -> "SessionState":
        return cls(current_project=project, current_goal=goal)


class HandoffManager:
    def __init__(self, state_dir: Path | None = None, brain_dir: Path | None = None):
        self.state_dir = state_dir or settings.brain.state_dir
        self.brain_dir = brain_dir or settings.brain.brain_dir
        self.sessions_dir = self.state_dir / "sessions"
        self.handoff_json_path = self.state_dir / "handoff.json"
        self.handoff_md_path = self.brain_dir / "session_handoff.md"
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.brain_dir.mkdir(parents=True, exist_ok=True)

    def save_session(self, session: SessionState) -> Path:
        session.touch()
        if not session.git_revision:
            try:
                res = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False)
                session.git_revision = res.stdout.strip()
            except Exception:
                session.git_revision = ""
        filepath = self.sessions_dir / f"{session.session_id}.json"
        payload = session.to_dict()
        filepath.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        self.save_handoff(session)
        logger.debug(f"Sessao {session.session_id} salva com sucesso.")
        return filepath

    def save_handoff(self, session: SessionState) -> None:
        if not session.git_revision:
            try:
                res = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False)
                session.git_revision = res.stdout.strip()
            except Exception:
                pass
        # 1. JSON estruturado para máquinas
        self.handoff_json_path.write_text(
            json.dumps(session.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        # 2. Markdown canônico para leitura humana e Obsidian
        md_content = self._render_handoff_markdown(session)
        self.handoff_md_path.write_text(md_content, encoding="utf-8")

    def load_handoff(self) -> SessionState | None:
        if not self.handoff_json_path.exists():
            return None
        try:
            data = json.loads(self.handoff_json_path.read_text(encoding="utf-8"))
            return SessionState.from_dict(data)
        except Exception as e:
            logger.error(f"Erro ao carregar handoff.json: {e}")
            return None

    def check_reconciliation(self, session: SessionState | None = None) -> dict[str, Any]:
        """Verifica se o handoff esta sincronizado com o HEAD atual do git."""
        curr = session or self.load_handoff()
        if not curr or not curr.git_revision:
            return {"is_reconciled": True, "reason": "Sem revisao de handoff registrada"}
        try:
            res = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False)
            current_head = res.stdout.strip()
            if not current_head:
                return {"is_reconciled": True, "reason": "Git indisponivel"}
            if current_head == curr.git_revision:
                return {"is_reconciled": True, "head": current_head}

            diff_res = subprocess.run(
                ["git", "rev-list", "--count", f"{curr.git_revision}..{current_head}"],
                capture_output=True, text=True, check=False
            )
            count = int(diff_res.stdout.strip() or 0)
            return {
                "is_reconciled": False,
                "handoff_sha": curr.git_revision,
                "current_head": current_head,
                "drift_commits": count,
                "action_recommended": "Reconciliar handoff com novo HEAD do repositorio"
            }
        except Exception as e:
            return {"is_reconciled": True, "error": str(e)}

    def update_working_state(
        self,
        current_goal: str | None = None,
        current_project: str | None = None,
        active_context: str | None = None,
        next_action: str | None = None,
        add_pending_steps: list[str] | None = None,
        completed_steps: list[str] | None = None
    ) -> SessionState:
        session = self.load_handoff()
        if not session:
            session = SessionState.create_new(
                project=current_project or "ThSyr",
                goal=current_goal or ""
            )
        if current_goal is not None:
            session.current_goal = current_goal
        if current_project is not None:
            session.current_project = current_project
        if active_context is not None:
            session.active_context = active_context
        if next_action is not None:
            session.next_action = next_action
        if add_pending_steps:
            for s in add_pending_steps:
                if s not in session.pending_steps and s not in session.completed_steps:
                    session.pending_steps.append(s)
        if completed_steps:
            for s in completed_steps:
                if s in session.pending_steps:
                    session.pending_steps.remove(s)
                if s not in session.completed_steps:
                    session.completed_steps.append(s)
        self.save_session(session)
        return session

    def complete_task(self, task_name: str) -> SessionState | None:
        session = self.load_handoff()
        if not session:
            return None
        if task_name in session.pending_steps:
            session.pending_steps.remove(task_name)
        if task_name not in session.completed_steps:
            session.completed_steps.append(task_name)
        self.save_session(session)
        return session

    def _render_handoff_markdown(self, s: SessionState) -> str:
        lines = [
            "# ThSyr // Session Handoff",
            "",
            f"**Session ID:** `{s.session_id}`  ",
            f"**Projeto:** `{s.current_project}`  ",
            f"**Iniciada em:** `{s.started_at}`  ",
            f"**Atualizada em:** `{s.updated_at}`  ",
            "",
            "## Objetivo Atual",
            s.current_goal or "Nenhum objetivo definido.",
            "",
            "## Contexto Ativo",
            s.active_context or "Nenhum contexto ativo.",
            "",
            "## Plano de Execução",
        ]

        if s.current_plan:
            for step in s.current_plan:
                lines.append(f"- {step}")
        else:
            lines.append("Nenhum plano cadastrado.")

        lines.extend([
            "",
            "## Etapas Concluídas",
        ])
        if s.completed_steps:
            for step in s.completed_steps:
                lines.append(f"- [x] {step}")
        else:
            lines.append("- Nenhuma etapa concluída.")

        lines.extend([
            "",
            "## Etapas Pendentes",
        ])
        if s.pending_steps:
            for step in s.pending_steps:
                lines.append(f"- [ ] {step}")
        else:
            lines.append("- Nenhuma etapa pendente.")

        lines.extend([
            "",
            "## Próxima Ação Recomendada",
            s.next_action or "Aguardando próxima instrução.",
            "",
            "## Decisões Recentes",
        ])
        if s.recent_decisions:
            for d in s.recent_decisions:
                lines.append(f"- {d}")
        else:
            lines.append("- Nenhuma decisão registrada nesta sessão.")

        lines.extend([
            "",
            "## Questões em Aberto",
        ])
        if s.unresolved_questions:
            for q in s.unresolved_questions:
                lines.append(f"- {q}")
        else:
            lines.append("- Nenhuma questão conflitante em aberto.")

        lines.extend([
            "",
            "## Resumo de Continuidade (Handoff Summary)",
            s.handoff_summary or "Sem resumo adicional.",
            ""
        ])

        return "\n".join(lines)
