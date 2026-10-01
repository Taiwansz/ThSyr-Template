"""
ThSyr Interaction Layer - Interruption Controller
Gerencia interrupcoes operacionais e mudancas de plano pelo operador
durante a execucao de tarefas longas ou planos executivos.
"""

import threading
from enum import Enum
from typing import Optional


class InterruptionType(str, Enum):
    CANCEL = "cancel"
    PAUSE = "pause"
    MODIFY_PLAN = "modify_plan"
    NEW_MESSAGE = "new_message"


class InterruptionController:
    def __init__(self):
        self._lock = threading.Lock()
        self._interrupted: bool = False
        self._interruption_type: Optional[InterruptionType] = None
        self._reason: Optional[str] = None
        self._excluded_entities: set[str] = set()

    def classify_user_input(self, text: str) -> tuple[InterruptionType, Optional[str]]:
        cleaned = text.strip().lower()

        # 1. Cancelamento imediato
        if cleaned in ("para", "cancela", "abortar", "stop", "abort", "cancelar"):
            return InterruptionType.CANCEL, "Operador solicitou cancelamento imediato."

        # 2. Pausa
        if cleaned in ("pausa", "espera", "aguarda", "pause"):
            return InterruptionType.PAUSE, "Operador solicitou pausa da execucao."

        # 3. Modificacao de plano / exclusao de entidade
        if any(w in cleaned for w in ("nao mexe", "não mexe", "ignora", "pula", "faz diferente", "muda o plano", "sem alterar")):
            return InterruptionType.MODIFY_PLAN, text.strip()

        return InterruptionType.NEW_MESSAGE, text.strip()

    def signal_interruption(self, itype: InterruptionType, reason: str) -> None:
        with self._lock:
            self._interrupted = True
            self._interruption_type = itype
            self._reason = reason

    def should_abort(self) -> bool:
        with self._lock:
            return self._interrupted and self._interruption_type in (
                InterruptionType.CANCEL,
                InterruptionType.MODIFY_PLAN,
            )

    def is_paused(self) -> bool:
        with self._lock:
            return self._interrupted and self._interruption_type == InterruptionType.PAUSE

    def get_status(self) -> tuple[bool, Optional[InterruptionType], Optional[str]]:
        with self._lock:
            return self._interrupted, self._interruption_type, self._reason

    def reset(self) -> None:
        with self._lock:
            self._interrupted = False
            self._interruption_type = None
            self._reason = None

    def add_excluded_entity(self, entity: str) -> None:
        with self._lock:
            self._excluded_entities.add(entity.lower().strip())

    def is_entity_excluded(self, entity: str) -> bool:
        with self._lock:
            return entity.lower().strip() in self._excluded_entities
