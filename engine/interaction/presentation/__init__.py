"""
ThSyr Interaction Layer - Presentation Adapters
Exporta adaptadores de apresentacao (Terminal, Mock).
"""

from .base import BasePresentationAdapter
from .mock_adapter import MockPresentationAdapter
from .terminal_adapter import TerminalAdapter

__all__ = [
    "BasePresentationAdapter",
    "TerminalAdapter",
    "MockPresentationAdapter",
]
