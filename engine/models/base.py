"""
ThSyr Model Gateway Base Types and Abstract Interfaces
Define contratos tipados para requisições, respostas, telemetria e provedores.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class ModelTier(str, Enum):
    FAST = "fast"                  # Baixa latência, triagem, sumários, consultas diretas
    REASONING = "reasoning"        # Raciocínio profundo, arquitetura, refatoração pesada
    VISION = "vision"              # Percepção multimodal e análise de imagens/telas
    EMBEDDING = "embedding"        # Vetorização de texto para busca semântica
    BATCH = "batch"                # Processamento em lote de baixo custo


class ModelRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class ChatMessage:
    role: ModelRole
    content: str
    name: str | None = None
    tool_call_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d = {"role": self.role.value if isinstance(self.role, ModelRole) else str(self.role), "content": self.content}
        if self.name:
            d["name"] = self.name
        if self.tool_call_id:
            d["tool_call_id"] = self.tool_call_id
        return d


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class UsageTelemetry:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0
    estimated_cost_usd: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ModelRequest:
    messages: list[ChatMessage]
    tier: ModelTier = ModelTier.FAST
    model_name: str | None = None
    temperature: float = 0.7
    max_tokens: int | None = None
    tools: list[ToolDefinition] | None = None
    images: list[str] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelResponse:
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    model_name: str = "unknown"
    provider_name: str = "unknown"
    telemetry: UsageTelemetry = field(default_factory=UsageTelemetry)
    finish_reason: str = "stop"

    def to_dict(self) -> dict[str, Any]:
        return {
            "content": self.content,
            "tool_calls": [tc.to_dict() for tc in self.tool_calls],
            "model_name": self.model_name,
            "provider_name": self.provider_name,
            "telemetry": self.telemetry.to_dict(),
            "finish_reason": self.finish_reason
        }


@dataclass
class StreamChunk:
    delta: str
    finish_reason: str | None = None


class BaseModelProvider(ABC):
    provider_name: str = "base"

    @abstractmethod
    def generate(self, request: ModelRequest) -> ModelResponse:
        """Gera resposta completa para a requisição."""

    @abstractmethod
    def stream(self, request: ModelRequest) -> Iterator[StreamChunk]:
        """Gera fluxo contínuo de tokens para a requisição."""

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Gera vetores densos (embeddings) para a lista de textos."""

    @abstractmethod
    def supports_tier(self, tier: ModelTier) -> bool:
        """Verifica se o provedor atende a um determinado tier de execução."""
