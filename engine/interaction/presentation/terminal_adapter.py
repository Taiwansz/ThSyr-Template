"""
ThSyr Interaction Layer - Terminal Presentation Adapter
Adaptador de apresentacao para linha de comando e terminais ANSI/ASCII.
"""

import sys
from typing import Optional

from ..interaction_events import EventType, InteractionEvent
from ..progress import ProgressTracker
from ..response_models import StructuredResponse
from ..terminal_renderer import TerminalRenderer
from .base import BasePresentationAdapter


class TerminalAdapter(BasePresentationAdapter):
    def __init__(
        self,
        renderer: Optional[TerminalRenderer] = None,
        progress: Optional[ProgressTracker] = None,
        stream=sys.stdout,
    ):
        self.stream = stream
        self.renderer = renderer or TerminalRenderer(stream=stream)
        self.progress = progress or ProgressTracker(stream=stream)

    def display_response(self, response: StructuredResponse) -> None:
        rendered = self.renderer.render_response(response)
        self.stream.write(f"\n{rendered}\n\n")
        self.stream.flush()

    def display_event(self, event: InteractionEvent) -> None:
        if event.type == EventType.PROGRESS_UPDATED:
            self.progress.update(event.message)
        elif event.type in (EventType.TASK_COMPLETED, EventType.VERIFICATION_COMPLETED):
            self.progress.finish(event.message, success=True)
        elif event.type == EventType.TASK_FAILED:
            self.progress.finish(event.message, success=False)
        elif event.type in (EventType.APPROVAL_REQUIRED, EventType.WARNING):
            self.stream.write(f"\nSyr › [ALERTA] {event.message}\n")
            self.stream.flush()

    def prompt_user(self, prompt_text: str = "Operador › ") -> str:
        try:
            return input(prompt_text)
        except (EOFError, KeyboardInterrupt):
            return "/cancel"
