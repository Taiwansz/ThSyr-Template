"""
ThSyr Desktop Session Registry
Gerencia instancias ativas de SyrConversationSession na memoria para o Desktop Control Center,
garantindo persistencia de contexto por session_id e exclusao mutua por sessao.
"""

from __future__ import annotations

import threading
from typing import Callable, Optional

from ..cognitive_router import CognitiveRouter
from ..config import setup_logger
from ..executive import ExecutiveRunner
from ..interaction.conversation_state import ConversationState
from ..interaction.session_orchestrator import SyrConversationSession

logger = setup_logger("desktop_session_registry")


class DesktopSessionRegistry:
    def __init__(
        self,
        session_factory: Optional[Callable[[str], SyrConversationSession]] = None,
        router: Optional[CognitiveRouter] = None,
        runner: Optional[ExecutiveRunner] = None,
    ):
        self._sessions: dict[str, SyrConversationSession] = {}
        self._locks: dict[str, threading.Lock] = {}
        self._registry_lock = threading.Lock()
        self.router = router
        self.runner = runner
        self._session_factory = session_factory or self._default_factory

    def _default_factory(self, session_id: str) -> SyrConversationSession:
        state = ConversationState(session_id=session_id)
        shared_router = self.router or CognitiveRouter()
        shared_runner = self.runner or ExecutiveRunner(router=shared_router)
        session = SyrConversationSession(
            router=shared_router,
            runner=shared_runner,
            state=state,
        )
        session.state.session_id = session_id
        return session

    def get_or_create(self, session_id: str) -> SyrConversationSession:
        """Obtem uma sessao existente ou instancia uma nova conectada ao core."""
        with self._registry_lock:
            if session_id not in self._sessions:
                logger.info(f"Instanciando nova sessao desktop: '{session_id}'")
                self._sessions[session_id] = self._session_factory(session_id)
                self._locks[session_id] = threading.Lock()
            return self._sessions[session_id]

    def get(self, session_id: str) -> Optional[SyrConversationSession]:
        with self._registry_lock:
            return self._sessions.get(session_id)

    def get_lock(self, session_id: str) -> threading.Lock:
        with self._registry_lock:
            if session_id not in self._locks:
                self._locks[session_id] = threading.Lock()
            return self._locks[session_id]

    def close(self, session_id: str) -> bool:
        with self._registry_lock:
            session = self._sessions.pop(session_id, None)
            self._locks.pop(session_id, None)
            if session:
                try:
                    session.state.save_handoff()
                except Exception as e:
                    logger.warning(f"Erro ao salvar handoff no encerramento da sessao '{session_id}': {e}")
                logger.info(f"Sessao desktop '{session_id}' encerrada e persistida.")
                return True
            return False

    def list_active(self) -> list[str]:
        with self._registry_lock:
            return list(self._sessions.keys())

    def clear(self) -> None:
        with self._registry_lock:
            for session in self._sessions.values():
                try:
                    session.state.save_handoff()
                except Exception:
                    pass
            self._sessions.clear()
            self._locks.clear()
