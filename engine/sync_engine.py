"""
ThSyr Git Sync Engine V2
Implementa a infraestrutura de sincronização contínua e autônoma do cérebro e estado do ThSyr,
garantindo persistência distribuída cross-device conforme especificado no Master Plan.
"""

import subprocess
from pathlib import Path
from typing import Any

from .config import settings, setup_logger

logger = setup_logger("sync_engine")


class GitSyncEngine:
    def __init__(self, repo_root: Path | None = None):
        self.repo_root = repo_root or settings.project_root

    def _run_git(self, args: list[str], timeout: int | None = None) -> subprocess.CompletedProcess:
        cmd = ["git"] + args
        timeout = timeout or settings.sync.git_timeout_seconds
        return subprocess.run(
            cmd,
            cwd=str(self.repo_root),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )

    def is_dirty(self) -> bool:
        proc = self._run_git(["status", "--porcelain"])
        return proc.returncode == 0 and bool(proc.stdout.strip())

    def get_status(self) -> dict[str, Any]:
        proc_status = self._run_git(["status", "--porcelain"])
        proc_branch = self._run_git(["branch", "--show-current"])
        proc_commit = self._run_git(["rev-parse", "--short", "HEAD"])

        dirty_lines = [line.strip() for line in proc_status.stdout.splitlines() if line.strip()]

        return {
            "branch": proc_branch.stdout.strip() or "main",
            "commit": proc_commit.stdout.strip() or "unknown",
            "is_dirty": len(dirty_lines) > 0,
            "changed_files_count": len(dirty_lines),
            "changed_files": dirty_lines[:15],
            "remote": settings.sync.remote_name
        }

    def fetch_remote(self) -> bool:
        try:
            proc = self._run_git(["fetch", settings.sync.remote_name])
            return proc.returncode == 0
        except Exception as e:
            logger.warning(f"Falha ao executar git fetch: {e}")
            return False

    def pull_rebase(self) -> bool:
        try:
            proc = self._run_git(["pull", "--rebase", settings.sync.remote_name, settings.sync.branch_name])
            if proc.returncode != 0:
                logger.warning(f"Rebase retornou erro: {proc.stderr.strip()}")
                return False
            return True
        except Exception as e:
            logger.warning(f"Excecao no pull rebase: {e}")
            return False

    def checkpoint(self, scope: str, summary: str, auto_push: bool | None = None) -> dict[str, Any]:
        """
        Cria um checkpoint atômico com mensagem semântica padronizada.
        Exemplo: brain(memory): consolidacao de sessao
        """
        if not self.is_dirty():
            return {"status": "clean", "committed": False, "pushed": False, "message": "Nenhuma alteracao detectada."}

        # 1. Stage de arquivos relevantes
        self._run_git(["add", "-A"])

        commit_msg = f"{scope}: {summary}"
        proc_commit = self._run_git(["commit", "-m", commit_msg])

        if proc_commit.returncode != 0:
            return {
                "status": "commit_failed",
                "committed": False,
                "pushed": False,
                "error": proc_commit.stderr.strip()
            }

        committed_sha = self._run_git(["rev-parse", "--short", "HEAD"]).stdout.strip()
        logger.info(f"Checkpoint criado: {committed_sha} [{commit_msg}]")

        should_push = auto_push if auto_push is not None else settings.sync.auto_push
        pushed = False
        push_error = None

        if should_push:
            try:
                proc_push = self._run_git(["push", settings.sync.remote_name, settings.sync.branch_name])
                if proc_push.returncode == 0:
                    pushed = True
                    logger.info("Push executado com sucesso.")
                else:
                    push_error = proc_push.stderr.strip()
                    logger.warning(f"Falha no git push: {push_error}")
            except Exception as e:
                push_error = str(e)
                logger.warning(f"Excecao ao realizar git push: {push_error}")

        return {
            "status": "success",
            "committed": True,
            "sha": committed_sha,
            "message": commit_msg,
            "pushed": pushed,
            "push_error": push_error
        }
