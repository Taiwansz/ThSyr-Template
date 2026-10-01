"""
ThSyr Interaction Layer - Stream Renderer
Renderiza streaming textual inteligente, separando operacoes internas
de conteudo semantico real e filtrando raciocinio/pensamento interno.
"""

import re
import sys
import time
from typing import Callable, Optional

# Tags de pensamento interno a filtrar completamente do stream
THINK_TAG_REGEX = re.compile(r"<think>.*?</think>", flags=re.DOTALL | re.IGNORECASE)


class StreamRenderer:
    def __init__(self, stream=sys.stdout, pace_delay: float = 0.005):
        self.stream = stream
        self.pace_delay = pace_delay
        self.is_tty = hasattr(stream, "isatty") and stream.isatty()

    def filter_internal_thought(self, text: str) -> str:
        """Remove blocos <think>...</think> ou pensamentos internos do stream."""
        return THINK_TAG_REGEX.sub("", text).strip()

    def stream_text(
        self,
        text: str,
        prefix: str = "Syr › ",
        on_chunk: Optional[Callable[[str], None]] = None,
        should_abort: Optional[Callable[[], bool]] = None,
    ) -> bool:
        """
        Transmite o texto filtrado ao stream com cadencia suave.
        Retorna True se concluido ou False se interrompido.
        """
        filtered = self.filter_internal_thought(text)
        if not filtered:
            return True

        if prefix:
            self.stream.write(prefix)
            self.stream.flush()

        words = filtered.split(" ")
        for i, word in enumerate(words):
            if should_abort and should_abort():
                self.stream.write(" [INTERROMPIDO]\n")
                self.stream.flush()
                return False

            chunk = word + (" " if i < len(words) - 1 else "")
            self.stream.write(chunk)
            self.stream.flush()

            if on_chunk:
                on_chunk(chunk)

            if self.is_tty and self.pace_delay > 0:
                time.sleep(self.pace_delay)

        self.stream.write("\n")
        self.stream.flush()
        return True
