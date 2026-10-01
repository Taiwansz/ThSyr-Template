"""
ThSyr Desktop Runtime Package
Facade, Event Bridge e Endpoints para a Central de Controle Desktop.
"""

from .app import create_desktop_app
from .event_stream import DesktopEventAdapter, DesktopEventStream
from .graph_service import DesktopGraphService
from .protocol import (
    CommandGoalPayload,
    CommandMessagePayload,
    CommandType,
    EventType,
    GraphEdgeDto,
    GraphNodeDto,
    GraphSnapshotDto,
    ProtocolEnvelope,
    RuntimeStatusDto,
)
from .runtime_service import DesktopRuntimeService
from .security import DesktopSecurityManager
from .session_registry import DesktopSessionRegistry

__all__ = [
    "CommandGoalPayload",
    "CommandMessagePayload",
    "CommandType",
    "DesktopEventAdapter",
    "DesktopEventStream",
    "DesktopGraphService",
    "DesktopRuntimeService",
    "DesktopSecurityManager",
    "DesktopSessionRegistry",
    "create_desktop_app",
    "EventType",
    "GraphEdgeDto",
    "GraphNodeDto",
    "GraphSnapshotDto",
    "ProtocolEnvelope",
    "RuntimeStatusDto",
]
