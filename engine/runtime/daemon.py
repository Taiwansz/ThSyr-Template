"""
ThSyr Autonomous Daemon & Background Supervisor
Gerencia o ciclo de vida do processo residente em background do ThSyr:
- Gravacao e auditoria de PID em state/daemon.pid
- Disparo desacoplado do SyrRuntime via terminal nativo
- Interrupcao segura de processos e verificacao de batimentos cardiacos (heartbeat)
- Integracao com ProcessSupervisor para isolamento cross-platform estrito
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..config import settings, setup_logger
from .process_supervisor import BaseProcessSupervisor, get_process_supervisor

logger = setup_logger("daemon_manager")


class SyrDaemonManager:
    """Gerenciador de ciclo de vida e supervisao do daemon autonomo do ThSyr."""

    def __init__(
        self,
        pid_file: Path | None = None,
        repo_root: Path | None = None,
        supervisor: BaseProcessSupervisor | None = None,
        heartbeat_file: Path | None = None
    ):
        self.repo_root = repo_root or settings.project_root
        self.state_dir = settings.brain.state_dir
        self.pid_file = pid_file or (self.state_dir / "daemon.pid")
        self.heartbeat_file = heartbeat_file or (self.state_dir / "daemon_heartbeat.json")
        self.supervisor: BaseProcessSupervisor = supervisor or get_process_supervisor()

    def read_pid(self) -> int | None:
        """Le o PID registrado do daemon se o arquivo existir."""
        if not self.pid_file.exists():
            return None
        try:
            content = self.pid_file.read_text(encoding="utf-8").strip()
            return int(content) if content.isdigit() else None
        except Exception:
            return None

    def write_pid(self, pid: int) -> None:
        """Persiste o PID do processo em state/daemon.pid de forma atomica."""
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)
        temp_pid = self.pid_file.with_suffix(".tmp")
        temp_pid.write_text(str(pid), encoding="utf-8")
        temp_pid.replace(self.pid_file)

    def clear_pid(self) -> None:
        """Remove o arquivo de PID ao encerrar."""
        if self.pid_file.exists():
            try:
                self.pid_file.unlink()
            except Exception:
                pass

    def record_heartbeat(self, status: str = "ALIVE", meta: dict[str, Any] | None = None) -> None:
        """Registra pulso cardiaco (heartbeat) do daemon para deteccao de travamento."""
        self.heartbeat_file.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "pid": self.read_pid(),
            "metadata": meta or {}
        }
        temp_hb = self.heartbeat_file.with_suffix(".tmp")
        temp_hb.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        temp_hb.replace(self.heartbeat_file)

    def get_heartbeat(self) -> dict[str, Any] | None:
        """Le o ultimo pulso registrado do daemon."""
        if not self.heartbeat_file.exists():
            return None
        try:
            return json.loads(self.heartbeat_file.read_text(encoding="utf-8"))
        except Exception:
            return None

    def is_running(self) -> bool:
        """Verifica se o processo registrado no PID esta ativo no sistema operacional."""
        pid = self.read_pid()
        if not pid:
            return False
        return self.supervisor.is_running(pid)

    def start(self) -> tuple[bool, str]:
        """Inicia o runtime do ThSyr em processo desacoplado de fundo."""
        if self.is_running():
            pid = self.read_pid()
            return False, f"Daemon ja esta em execucao ativa sob o PID {pid}."

        import sys
        python_exe = sys.executable
        if sys.platform.startswith("win"):
            pythonw = Path(python_exe).parent / "pythonw.exe"
            if pythonw.is_file():
                python_exe = str(pythonw)

        thsyr_script = self.repo_root / "thsyr.py"
        cmd = [python_exe, str(thsyr_script), "runtime", "--daemon"]

        try:
            pid = self.supervisor.spawn(cmd, cwd=self.repo_root)
            self.write_pid(pid)
            self.record_heartbeat("INITIALIZED", {"started_at": datetime.now(timezone.utc).isoformat()})
            logger.info(f"Daemon do ThSyr disparado com sucesso no PID {pid}")
            return True, f"Daemon do ThSyr iniciado com sucesso no PID {pid}."
        except Exception as e:
            msg = f"Falha ao iniciar daemon: {e}"
            logger.error(msg)
            return False, msg

    def stop(self, timeout: float = 5.0) -> tuple[bool, str]:
        """Interrompe o processo do daemon em execucao."""
        pid = self.read_pid()
        if not pid:
            return False, "Nenhum daemon registrado em execucao."

        if not self.is_running():
            self.clear_pid()
            return True, f"Arquivo de PID stale ({pid}) removido. O processo nao estava mais ativo."

        try:
            success = self.supervisor.terminate(pid, timeout=timeout)
            self.clear_pid()
            self.record_heartbeat("STOPPED")
            if success:
                logger.info(f"Daemon (PID {pid}) encerrado.")
                return True, f"Daemon (PID {pid}) encerrado com sucesso."
            return False, f"Falha ao confirmar encerramento do daemon (PID {pid})."
        except Exception as e:
            return False, f"Falha ao encerrar daemon (PID {pid}): {e}"

    def status(self) -> dict[str, Any]:
        """Gera relatorio diagnostico de status do daemon."""
        pid = self.read_pid()
        running = self.is_running()
        hb = self.get_heartbeat()

        return {
            "status": "RUNNING" if running else "STOPPED",
            "is_running": running,
            "pid": pid if running else None,
            "pid_file": str(self.pid_file),
            "heartbeat": hb,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
