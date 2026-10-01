"""
ThSyr Interaction Layer - Mock Presentation Adapter
Adaptador hermetico para testes e validacao de UI sem terminal real.
"""

from ..interaction_events import InteractionEvent
from ..response_models import StructuredResponse
from .base import BasePresentationAdapter


class MockPresentationAdapter(BasePresentationAdapter):
    def __init__(self, scripted_inputs: list[str] | None = None):
        self.displayed_responses: list[StructuredResponse] = []
        self.displayed_events: list[InteractionEvent] = []
        self.scripted_inputs: list[str] = scripted_inputs or []
        self._input_idx = 0

    def display_response(self, response: StructuredResponse) -> None:
        self.displayed_responses.append(response)

    def display_event(self, event: InteractionEvent) -> None:
        self.displayed_events.append(event)

    def prompt_user(self, prompt_text: str = "Operador › ") -> str:
        if self._input_idx < len(self.scripted_inputs):
            res = self.scripted_inputs[self._input_idx]
            self._input_idx += 1
            return res
        return "/cancel"
