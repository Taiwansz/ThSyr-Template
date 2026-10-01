"""
ThSyr Codenotch Launcher & Supervisor
Garante a ativacao automatica e monitoramento do aplicativo Codenotch no ambiente
do operador (Windows, macOS ou Linux) sempre que o ThSyr e invocado.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from ..config import settings, setup_logger

logger = setup_logger("codenotch_launcher")


class CodenotchLauncher:
    """
    Supervisor do executavel Codenotch.
    Detecta status do processo e realiza o start desacoplado (detached).
    """

    def __init__(self, custom_path: str | None = None):
        self.custom_path = custom_path or settings.codenotch.custom_path
        self.platform = self._detect_platform()

    def _detect_platform(self) -> str:
        if sys.platform.startswith("win"):
            return "windows"
        elif sys.platform.startswith("darwin"):
            return "darwin"
        return "linux"

    def find_executable(self) -> Path | None:
        """Localiza o binario do Codenotch no sistema."""
        # 1. Caminho customizado configurado
        if self.custom_path:
            p = Path(os.path.expandvars(os.path.expanduser(self.custom_path)))
            if p.is_file() and os.access(p, os.X_OK):
                return p

        # 2. Windows default paths
        if self.platform == "windows":
            local_appdata = os.getenv("LOCALAPPDATA", "")
            appdata = os.getenv("APPDATA", "")
            prog_files = os.getenv("ProgramFiles", "")
            prog_files_x86 = os.getenv("ProgramFiles(x86)", "")

            candidates = [
                Path(local_appdata) / "Programs" / "Codenotch" / "Codenotch.exe",
                Path(local_appdata) / "Programs" / "Codenotch" / "codenotch.exe",
                Path(local_appdata) / "codenotch" / "Codenotch.exe",
                Path(local_appdata) / "codenotch" / "codenotch.exe",
                Path(appdata) / "Local" / "Programs" / "Codenotch" / "Codenotch.exe",
                Path(prog_files) / "Codenotch" / "Codenotch.exe",
                Path(prog_files_x86) / "Codenotch" / "Codenotch.exe",
            ]
            for cand in candidates:
                if cand.is_file():
                    return cand

            # Checar PATH no Windows
            for name in ["Codenotch.exe", "codenotch.exe", "codenotch"]:
                w = shutil.which(name)
                if w:
                    return Path(w)

        # 3. macOS default paths
        elif self.platform == "darwin":
            mac_candidates = [
                Path("/Applications/Codenotch.app/Contents/MacOS/Codenotch"),
                Path.home() / "Applications/Codenotch.app/Contents/MacOS/Codenotch",
            ]
            for cand in mac_candidates:
                if cand.is_file() and os.access(cand, os.X_OK):
                    return cand

            w = shutil.which("codenotch")
            if w:
                return Path(w)

        # 4. Linux default paths
        else:
            linux_candidates = [
                Path.home() / ".local" / "bin" / "codenotch",
                Path("/usr/local/bin/codenotch"),
                Path("/usr/bin/codenotch"),
                Path("/opt/codenotch/codenotch"),
            ]
            for cand in linux_candidates:
                if cand.is_file() and os.access(cand, os.X_OK):
                    return cand

            w = shutil.which("codenotch")
            if w:
                return Path(w)

        return None

    def is_running(self) -> bool:
        """Verifica se o processo do Codenotch esta em execucao."""
        # 1. Tentar via psutil se disponivel
        try:
            import psutil
            for proc in psutil.process_iter(["name", "cmdline"]):
                try:
                    pname = (proc.info.get("name") or "").lower()
                    if "codenotch" in pname:
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except ImportError:
            pass

        # 2. Fallback via comandos nativos do sistema operacional
        try:
            if self.platform == "windows":
                out = subprocess.check_output(
                    ["tasklist", "/NH", "/FO", "CSV"],
                    stderr=subprocess.DEVNULL,
                    text=True,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
                )
                return "codenotch" in out.lower()
            else:
                ret = subprocess.run(
                    ["pgrep", "-f", "codenotch"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return ret.returncode == 0
        except Exception as e:
            logger.debug(f"Falha ao verificar processo Codenotch: {e}")
            return False

    def launch(self) -> tuple[bool, str]:
        """Dispara o Codenotch em segundo plano desacoplado."""
        if not settings.codenotch.enabled:
            return False, "Codenotch desabilitado nas configuracoes do ThSyr."

        if self.is_running():
            return True, "Codenotch ja se encontra ativo em segundo plano."

        exe = self.find_executable()
        if not exe:
            return False, "Executavel do Codenotch nao localizado nos caminhos padroes de instalacao."

        try:
            if self.platform == "windows":
                # No Windows, prefere os.startfile (ShellExecute) para inicializacao visual no desktop
                try:
                    startfile = getattr(os, "startfile", None)
                    if not callable(startfile):
                        raise OSError("os.startfile indisponivel")
                    startfile(str(exe))
                except Exception:
                    DETACHED_PROCESS = 0x00000008
                    CREATE_NEW_PROCESS_GROUP = 0x00000200
                    flags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
                    subprocess.Popen(
                        [str(exe)],
                        creationflags=flags,
                        close_fds=True
                    )
            else:
                # Linux / macOS: nova sessao desacoplada
                subprocess.Popen(
                    [str(exe)],
                    start_new_session=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL
                )

            logger.info(f"Codenotch iniciado com sucesso a partir de: {exe}")
            return True, f"Codenotch iniciado com sucesso a partir de {exe}"

        except Exception as e:
            msg = f"Falha ao disparar Codenotch: {e}"
            logger.error(msg)
            return False, msg

    def ensure_running(self) -> dict[str, Any]:
        """
        Garante que o Codenotch esteja em execucao.
        Retorna dicionario de status estruturado para a mente do ThSyr.
        """
        if not settings.codenotch.enabled:
            return {
                "running": False,
                "action_taken": "disabled",
                "executable": None,
                "platform": self.platform,
                "message": "Codenotch desativado em configuracao."
            }

        exe = self.find_executable()

        if self.is_running():
            return {
                "running": True,
                "action_taken": "already_running",
                "executable": str(exe) if exe else None,
                "platform": self.platform,
                "message": "Codenotch ativo e operacional."
            }

        success, msg = self.launch()
        return {
            "running": success,
            "action_taken": "launched" if success else "failed_to_launch",
            "executable": str(exe) if exe else None,
            "platform": self.platform,
            "message": msg
        }


# Instancia singleton para uso rapido
_launcher_instance: CodenotchLauncher | None = None


def get_codenotch_launcher() -> CodenotchLauncher:
    global _launcher_instance
    if _launcher_instance is None:
        _launcher_instance = CodenotchLauncher()
    return _launcher_instance


def ensure_codenotch_running() -> dict[str, Any]:
    """Funcao publica de conveniencia para invocacao no ciclo de vida do ThSyr."""
    launcher = get_codenotch_launcher()
    return launcher.ensure_running()


def get_codenotch_status() -> dict[str, Any]:
    """Retorna informacoes detalhadas de diagnostico do Codenotch."""
    launcher = get_codenotch_launcher()
    exe = launcher.find_executable()
    running = launcher.is_running()
    return {
        "installed": exe is not None,
        "running": running,
        "executable": str(exe) if exe else None,
        "platform": launcher.platform,
        "enabled": settings.codenotch.enabled
    }
