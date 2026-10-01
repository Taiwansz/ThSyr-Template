"""
ThSyr Desktop Notifier (Fase 9)
Dispara notificacoes nativas no desktop do Windows para alertas cognitivos,
prazos iminentes e deteccao de desvios operacionais.
Garante: Zero Emojis, execucao assincrona desacoplada e conformidade de plataforma.
"""

import re
import subprocess
import sys
import threading
from pathlib import Path

from .config import setup_logger

logger = setup_logger("desktop_notifier")

SCRIPT_PATH = Path(__file__).resolve().parent / "scripts" / "notify.ps1"


class DesktopNotifier:
    """
    Despachante de notificacoes nativas para o sistema operacional.
    No Windows, utiliza script auxiliar em PowerShell com WinForms NotifyIcon.
    """

    def __init__(self, script_path: Path | None = None):
        self.script_path = script_path or SCRIPT_PATH
        self.emoji_pattern = re.compile(r"[\U00010000-\U0010ffff]|[\u2600-\u27BF]|[\u2300-\u23FF]|[\u2B50-\u2B55]")

    def sanitize_text(self, text: str) -> str:
        """Remove emojis e caracteres graficos proibidos."""
        cleaned = self.emoji_pattern.sub("", text)
        return cleaned.strip()

    def notify(
        self,
        title: str,
        message: str,
        priority: str = "normal",
        async_dispatch: bool = True
    ) -> bool:
        """
        Emite a notificacao nativa no desktop.
        Se async_dispatch=True, executa em thread separada para nao bloquear o agente.
        """
        clean_title = self.sanitize_text(title) or "ThSyr // Alerta"
        clean_msg = self.sanitize_text(message)

        if not clean_msg:
            return False

        if async_dispatch:
            t = threading.Thread(
                target=self._dispatch_sync,
                args=(clean_title, clean_msg, priority),
                daemon=True
            )
            t.start()
            return True
        else:
            return self._dispatch_sync(clean_title, clean_msg, priority)

    def _dispatch_sync(self, title: str, message: str, priority: str) -> bool:
        """Execucao sincronizada do despacho de notificacao."""
        try:
            if sys.platform.startswith("win"):
                # Som sutil opcional se for urgente
                if priority == "high":
                    try:
                        import winsound
                        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                    except Exception:
                        pass

                if self.script_path.exists():
                    cmd = [
                        "powershell",
                        "-NoProfile",
                        "-ExecutionPolicy",
                        "Bypass",
                        "-File",
                        str(self.script_path),
                        "-Title",
                        title,
                        "-Message",
                        message
                    ]
                    flags = 0x08000000 | 0x00000200  # CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP
                    subprocess.run(
                        cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        creationflags=flags,
                        timeout=8
                    )
                    logger.info(f"[DesktopNotifier] Notificacao enviada: '{title}' - '{message[:50]}...'")
                    return True
                else:
                    logger.warning(f"[DesktopNotifier] Script {self.script_path} nao localizado.")
                    return False
            else:
                logger.debug(f"[DesktopNotifier] Notificacao ignorada em plataforma nao-Windows: {title}")
                return True
        except Exception as e:
            logger.error(f"[DesktopNotifier] Falha ao despachar notificacao: {e}")
            return False


# Singleton para uso geral
_notifier_instance: DesktopNotifier | None = None


def get_notifier() -> DesktopNotifier:
    global _notifier_instance
    if _notifier_instance is None:
        _notifier_instance = DesktopNotifier()
    return _notifier_instance


def notify_desktop(title: str, message: str, priority: str = "normal", async_dispatch: bool = True) -> bool:
    """Funcao publica rapida para despacho de notificacao nativa."""
    return get_notifier().notify(title, message, priority=priority, async_dispatch=async_dispatch)
