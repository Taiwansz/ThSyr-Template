"""
ThSyr Interaction Layer - Base Presentation Adapter
Contrato abstrato para adaptadores de apresentacao (Terminal, TUI, Web, Mobile).
"""

from abc import ABC, abstractmethod

from ..interaction_events import InteractionEvent
from ..response_models import StructuredResponse


class BasePresentationAdapter(ABC):
    @abstractmethod
    def display_response(self, response: StructuredResponse) -> None:
        """Exibe uma resposta estruturada final ao usuario."""
        pass

    @abstractmethod
    def display_event(self, event: InteractionEvent) -> None:
        """Exibe um evento operacional ou update de progresso."""
        pass

    @abstractmethod
    def prompt_user(self, prompt_text: str = "Operador › ") -> str:
        """Solicita entrada textual do operador."""
        pass
