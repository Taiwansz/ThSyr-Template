"""
ThSyr Workspace Observer & Git Sentinel (Fase 9)
Monitora ativamente os repositorios e diretorios vitais do Major:
- Detecta arquivos modificados sem commit e risco de perda de codigo
- Mapeia arquivos nao rastreados (untracked)
- Rastreia commits pendentes de push (divergencia de branch)
- Emite relatorios consolidados de saude operacional do ecossistema
"""

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import setup_logger

logger = setup_logger("workspace_observer")

DEFAULT_WORKSPACES: list[Path] = []


def discover_workspaces() -> list[Path]:
    """Descobre repositorios git locais com suporte cross-platform."""
    existing_defaults = [p for p in DEFAULT_WORKSPACES if p.exists()]
    if existing_defaults:
        return existing_defaults

    found: list[Path] = []
    candidates_root = Path.home()
    try:
        if candidates_root.exists():
            for entry in sorted(candidates_root.iterdir()):
                if entry.is_dir() and (entry / ".git").exists() and entry not in found:
                    found.append(entry)
    except Exception:
        pass

    cwd = Path.cwd()
    if (cwd / ".git").exists() and cwd not in found:
        found.append(cwd)

    return found if found else DEFAULT_WORKSPACES


class WorkspaceObserver:
    def __init__(self, workspaces: list[Path] | None = None):
        self.workspaces = workspaces or discover_workspaces()

    def _inspect_git_repo(self, path: Path) -> dict[str, Any]:
        """Inspeciona o estado de um repositorio Git individual."""
        res = {
            "name": path.name,
            "path": str(path),
            "is_git": False,
            "branch": "N/D",
            "is_dirty": False,
            "modified_count": 0,
            "untracked_count": 0,
            "ahead_commits": 0,
            "behind_commits": 0,
            "status_label": "UNKNOWN",
            "sample_files": []
        }

        if not (path / ".git").exists():
            return res

        res["is_git"] = True

        try:
            # 1. Branch ativa
            cmd_branch = ["git", "-C", str(path), "branch", "--show-current"]
            p_branch = subprocess.run(cmd_branch, capture_output=True, text=True, timeout=5)
            res["branch"] = p_branch.stdout.strip() or "HEAD desacoplado"

            # 2. Status simplificado
            cmd_status = ["git", "-C", str(path), "status", "-s"]
            p_status = subprocess.run(cmd_status, capture_output=True, text=True, timeout=5)
            lines = [item_line for item_line in p_status.stdout.splitlines() if item_line.strip()]

            modified = 0
            untracked = 0
            sample: list[str] = []

            for line in lines:
                prefix = line[:2]
                filename = line[3:].strip()
                if prefix == "??":
                    untracked += 1
                else:
                    modified += 1
                if len(sample) < 5:
                    sample.append(filename)

            res["modified_count"] = modified
            res["untracked_count"] = untracked
            res["is_dirty"] = bool(modified > 0 or untracked > 0)
            res["sample_files"] = sample

            # 3. Ahead / Behind em relacao ao remoto
            cmd_ahead = ["git", "-C", str(path), "rev-list", "--count", "@{u}..HEAD"]
            p_ahead = subprocess.run(cmd_ahead, capture_output=True, text=True, timeout=5)
            if p_ahead.returncode == 0:
                res["ahead_commits"] = int(p_ahead.stdout.strip() or "0")

            cmd_behind = ["git", "-C", str(path), "rev-list", "--count", "HEAD..@{u}"]
            p_behind = subprocess.run(cmd_behind, capture_output=True, text=True, timeout=5)
            if p_behind.returncode == 0:
                res["behind_commits"] = int(p_behind.stdout.strip() or "0")

            # Rotulo sintetico de estado
            if res["is_dirty"]:
                res["status_label"] = "MODIFICADO (RISCO)"
            elif int(str(res["ahead_commits"])) > 0:
                res["status_label"] = "AHEAD (PENDENTE DE PUSH)"
            elif int(str(res["behind_commits"])) > 0:
                res["status_label"] = "BEHIND (DESATUALIZADO)"
            else:
                res["status_label"] = "LIMPO (SINCRONIZADO)"

        except Exception as e:
            logger.debug(f"Falha ao auditar git em {path}: {e}")
            res["status_label"] = "ERRO NA VARREDURA"

        return res

    def scan(self) -> dict[str, Any]:
        """Realiza a varredura completa de todos os workspaces registrados."""
        results = []
        dirty_count = 0
        ahead_count = 0
        total_tracked = 0

        for ws in self.workspaces:
            if ws.exists():
                total_tracked += 1
                stat = self._inspect_git_repo(ws)
                results.append(stat)
                if stat.get("is_dirty"):
                    dirty_count += 1
                if stat.get("ahead_commits", 0) > 0:
                    ahead_count += 1

        overall_health = "OTIMO"
        if dirty_count > 0:
            overall_health = "ATENCAO (ARVORES MODIFICADAS)"
        elif ahead_count > 0:
            overall_health = "ATENCAO (COMMITS PENDENTES)"

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_workspaces": total_tracked,
            "dirty_count": dirty_count,
            "ahead_count": ahead_count,
            "overall_health": overall_health,
            "workspaces": results
        }

    def render_report(self) -> str:
        """Renderiza relatorio textual para o terminal."""
        data = self.scan()
        lines = [
            "========================================",
            "   THSYR // SENTINELA DE WORKSPACE      ",
            "========================================",
            f"Saude Global:        {data['overall_health']}",
            f"Workspaces Ativos:   {data['total_workspaces']}",
            f"Com Alteracoes:      {data['dirty_count']}",
            f"Pendentes de Push:   {data['ahead_count']}",
            "----------------------------------------"
        ]

        for ws in data["workspaces"]:
            if not ws["is_git"]:
                continue
            name = ws["name"]
            status = ws["status_label"]
            branch = ws["branch"]
            mod = ws["modified_count"]
            untracked = ws["untracked_count"]
            ahead = ws["ahead_commits"]

            lines.append(f"[{name}] (Branch: {branch}) -> {status}")
            details = []
            if mod > 0:
                details.append(f"Modificados: {mod}")
            if untracked > 0:
                details.append(f"Untracked: {untracked}")
            if ahead > 0:
                details.append(f"Ahead: {ahead} commits")
            if details:
                lines.append(f"   Detalhes: {', '.join(details)}")
            if ws["sample_files"]:
                lines.append(f"   Amostra: {', '.join(ws['sample_files'][:3])}")
            lines.append("")

        lines.append("========================================")
        return "\n".join(lines)
