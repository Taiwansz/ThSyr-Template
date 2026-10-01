"""
ThSyr Interaction Layer - Progress Tracker
Gerencia updates de progresso compactos e atualizaveis em linha unica (via \\r),
eliminando narracao trivial e poluicao visual no terminal.
"""

import sys
import time


class ProgressTracker:
    def __init__(self, prefix: str = "Syr › ", stream=sys.stdout):
        self.prefix = prefix
        self.stream = stream
        self.is_tty = hasattr(stream, "isatty") and stream.isatty()
        self._last_message: str = ""
        self._is_active: bool = False
        self._last_update_time: float = 0.0
        self._min_interval_sec: float = 0.3  # Evita piscar excessivo no terminal

    def start(self, initial_message: str) -> None:
        self._is_active = True
        self._last_message = initial_message
        self._last_update_time = time.time()
        self._render(f"{self.prefix}{initial_message}...")

    def update(self, message: str, force: bool = False) -> None:
        if not self._is_active:
            self.start(message)
            return

        now = time.time()
        # Filtra atualizacoes insignificantes que ocorram em menos de min_interval_sec, a menos que force=True
        if not force and (now - self._last_update_time < self._min_interval_sec):
            return

        self._last_message = message
        self._last_update_time = now
        self._render(f"{self.prefix}{message}...")

    def finish(self, final_message: str, success: bool = True) -> None:
        if not self._is_active:
            return
        status_tag = "[OK]" if success else "[FALHA]"
        line = f"{self.prefix}{final_message} {status_tag}"
        if self.is_tty:
            # Sobrescreve a linha atual completamente e encerra com \n
            self.stream.write(f"\r\033[K{line}\n")
            self.stream.flush()
        else:
            self.stream.write(f"{line}\n")
            self.stream.flush()
        self._is_active = False
        self._last_message = ""

    def _render(self, text: str) -> None:
        if self.is_tty:
            # \r volta para o inicio da linha, \033[K limpa ate o fim
            self.stream.write(f"\r\033[K{text}")
            self.stream.flush()
        # Em modo nao-interativo (CI/pipe), nao imprime atualizacoes intermediarias para evitar poluir logs
