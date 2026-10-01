"""
ThSyr Model Gateway & Router Package (Fase 3 - Model Gateway)
Abstração formal de provedores de LLM, seleção contextual de modelos
e rastreamento de custos, latência e qualidade.
"""

from .base import (
    BaseModelProvider,
    ChatMessage,
    ModelRequest,
    ModelResponse,
    ModelRole,
    ModelTier,
    StreamChunk,
    ToolCall,
    ToolDefinition,
    UsageTelemetry,
)
from .gateway import ModelGateway
from .router import ModelRouter

__all__ = [
    "BaseModelProvider",
    "ChatMessage",
    "ModelGateway",
    "ModelRequest",
    "ModelResponse",
    "ModelRole",
    "ModelRouter",
    "ModelTier",
    "StreamChunk",
    "ToolCall",
    "ToolDefinition",
    "UsageTelemetry"
]
