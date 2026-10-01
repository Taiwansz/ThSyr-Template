"""
ThSyr Interaction Layer - V0.3.0
Camada desacoplada de experiencia conversacional e operacional.
Transforma o ThSyr de mero wrapper de LLM em entidade operacional persistente.
"""

from .approval_ui import ApprovalDecision, ApprovalRequest, ApprovalUI
from .command_router import CommandRouter
from .context_budget import ContextBudgetManager
from .conversation_objects import ConversationObject, ConversationObjectRegistry
from .conversation_state import ConversationState
from .interaction_events import EventBroadcaster, EventLevel, EventType, InteractionEvent
from .interaction_profile import InteractionProfile
from .interruption import InterruptionController, InterruptionType
from .metrics import InteractionMetrics, InteractionMetricsCollector
from .personality import SyrPersonalityEngine
from .presentation import BasePresentationAdapter, MockPresentationAdapter, TerminalAdapter
from .progress import ProgressTracker
from .reference_resolver import ReferenceResolver, ResolutionResult
from .response_engine import ResponseEngine
from .response_models import ResponseAction, ResponseKind, ResponseSource, SourceType, StructuredResponse
from .response_policy import ResponsePolicy
from .session_orchestrator import SyrConversationSession
from .stream_renderer import StreamRenderer
from .terminal_renderer import TerminalRenderer
from .verbosity import VerbosityLevel, VerbosityManager

__all__ = [
    "ResponseKind",
    "SourceType",
    "ResponseSource",
    "ResponseAction",
    "StructuredResponse",
    "InteractionProfile",
    "VerbosityLevel",
    "VerbosityManager",
    "SyrPersonalityEngine",
    "ResponsePolicy",
    "ResponseEngine",
    "ConversationObject",
    "ConversationObjectRegistry",
    "ConversationState",
    "ReferenceResolver",
    "ResolutionResult",
    "EventType",
    "EventLevel",
    "InteractionEvent",
    "EventBroadcaster",
    "ProgressTracker",
    "StreamRenderer",
    "TerminalRenderer",
    "CommandRouter",
    "ApprovalDecision",
    "ApprovalRequest",
    "ApprovalUI",
    "InterruptionType",
    "InterruptionController",
    "InteractionMetrics",
    "InteractionMetricsCollector",
    "BasePresentationAdapter",
    "TerminalAdapter",
    "MockPresentationAdapter",
    "ContextBudgetManager",
    "SyrConversationSession",
]
