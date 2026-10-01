"""
ThSyr Process Supervisor & Cross-Platform Process Abstraction
Camada unificada de gerenciamento de processos e supervisao de runtime para o ThSyr.
Isola chamadas de sistema entre Windows, POSIX e Mock para execucao hermetica.
"""

import os
import signal
import subprocess
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from ..config import setup_logger

logger = setup_logger("process_supervisor")


class BaseProcessSupervisor(ABC):
    """Interface abstrata para supervisao e controle de processos do sistema."""

    @abstractmethod
    def is_running(self, pid: int) -> bool:
        """Determina se o processo com o PID especificado esta ativo."""

    @abstractmethod
    def spawn(self, cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> int:
        """Inicia um processo em background desacoplado e retorna o PID."""

    @abstractmethod
    def terminate(self, pid: int, timeout: float = 5.0) -> bool:
        """Encerra um processo de forma segura."""

    @abstractmethod
    def get_fingerprint(self, pid: int) -> dict[str, Any] | None:
        """Captura diagnosticos e metadados de execucao do processo."""


class WindowsProcessSupervisor(BaseProcessSupervisor):
    """Supervisor de processos otimizado para o subsistema Microsoft Windows."""

    def is_running(self, pid: int) -> bool:
        if pid <= 0:
            return False
        try:
            cmd = ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"]
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
            out = subprocess.check_output(
                cmd,
                stderr=subprocess.DEVNULL,
                text=True,
                creationflags=creationflags
            )
            return f'"{pid}"' in out or str(pid) in out
        except Exception as e:
            logger.debug(f"Falha ao checar PID {pid} via tasklist: {e}")
            return False

    def spawn(self, cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> int:
        DETACHED_PROCESS = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        CREATE_NO_WINDOW = 0x08000000
        flags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW

        log_dir = cwd / "state"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = open(log_dir / "daemon.log", "a", encoding="utf-8")

        proc = subprocess.Popen(
            cmd,
            cwd=str(cwd),
            env=env or os.environ.copy(),
            creationflags=flags,
            stdout=log_file,
            stderr=log_file,
            stdin=subprocess.DEVNULL
        )
        return proc.pid

    def terminate(self, pid: int, timeout: float = 5.0) -> bool:
        if not self.is_running(pid):
            return True
        try:
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
            res = subprocess.run(
                ["taskkill", "/F", "/PID", str(pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=timeout,
                creationflags=creationflags
            )
            return res.returncode == 0 or not self.is_running(pid)
        except Exception as e:
            logger.error(f"Erro ao terminar PID {pid} no Windows: {e}")
            return False

    def get_fingerprint(self, pid: int) -> dict[str, Any] | None:
        if not self.is_running(pid):
            return None
        return {
            "platform": "windows",
            "pid": pid,
            "supervisor": "WindowsProcessSupervisor"
        }


class PosixProcessSupervisor(BaseProcessSupervisor):
    """Supervisor de processos para padroes POSIX (Linux, macOS, BSD)."""

    def is_running(self, pid: int) -> bool:
        if pid <= 0:
            return False
        try:
            os.kill(pid, 0)
            return True
        except (ProcessLookupError, OSError):
            return False

    def spawn(self, cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> int:
        proc = subprocess.Popen(
            cmd,
            cwd=str(cwd),
            env=env or os.environ.copy(),
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL
        )
        return proc.pid

    def terminate(self, pid: int, timeout: float = 5.0) -> bool:
        if not self.is_running(pid):
            return True
        try:
            os.kill(pid, signal.SIGTERM)
            return True
        except (ProcessLookupError, OSError):
            return not self.is_running(pid)

    def get_fingerprint(self, pid: int) -> dict[str, Any] | None:
        if not self.is_running(pid):
            return None
        return {
            "platform": "posix",
            "pid": pid,
            "supervisor": "PosixProcessSupervisor"
        }


class MockProcessSupervisor(BaseProcessSupervisor):
    """Supervisor em memoria para testes unitarios hermeticos e determinismo estrito."""

    def __init__(self, initial_pids: list[int] | None = None):
        self.active_pids: dict[int, dict[str, Any]] = {}
        self.spawn_history: list[dict[str, Any]] = []
        self.next_pid: int = 10000
        if initial_pids:
            for p in initial_pids:
                self.active_pids[p] = {"cmd": ["mock_process"], "cwd": Path(".")}

    def is_running(self, pid: int) -> bool:
        return pid in self.active_pids

    def spawn(self, cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> int:
        pid = self.next_pid
        self.next_pid += 1
        record = {"cmd": cmd, "cwd": cwd, "env": env}
        self.active_pids[pid] = record
        self.spawn_history.append({"pid": pid, **record})
        return pid

    def terminate(self, pid: int, timeout: float = 5.0) -> bool:
        if pid in self.active_pids:
            del self.active_pids[pid]
            return True
        return False

    def get_fingerprint(self, pid: int) -> dict[str, Any] | None:
        if pid not in self.active_pids:
            return None
        return {
            "platform": "mock",
            "pid": pid,
            "meta": self.active_pids[pid]
        }


def get_process_supervisor(backend: str | None = None) -> BaseProcessSupervisor:
    """Fabrica de selecao automatica ou explicita do supervisor de processos."""
    if backend == "mock":
        return MockProcessSupervisor()
    if backend == "windows":
        return WindowsProcessSupervisor()
    if backend == "posix":
        return PosixProcessSupervisor()

    if sys.platform.startswith("win"):
        return WindowsProcessSupervisor()
    return PosixProcessSupervisor()
