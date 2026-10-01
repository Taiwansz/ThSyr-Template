"""
ThSyr Tool Bus - Memory Adapters
Ferramentas para interagir diretamente com a memoria do Syr:
- SearchMemoryTool (Risco 0)
- WriteEpisodicMemoryTool (Risco 2)
"""

from typing import Any

from ...memory_manager import MemoryManager
from ...retriever import MemoryRetriever
from ..base import BaseTool, RiskLevel, ToolMetadata, ToolResult


class SearchMemoryTool(BaseTool):
    def __init__(self, memory_manager: MemoryManager | None = None):
        self.memory_manager = memory_manager or MemoryManager()
        self.retriever = MemoryRetriever(memory_manager=self.memory_manager)
        super().__init__(ToolMetadata(
            name="search_memory",
            description="Pesquisa memorias hibridas (lexica + semantica + grafo)",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Termo ou pergunta a consultar"},
                    "limit": {"type": "integer", "default": 3, "description": "Quantidade maxima"}
                },
                "required": ["query"]
            },
            output_schema={"type": "object", "properties": {"results": {"type": "array"}}},
            risk_level=RiskLevel.LEVEL_0_SEARCH,
            requires_confirmation=False,
            timeout=5,
            reversible=True
        ))

    def execute(self, query: str = "", limit: int = 3, **kwargs: Any) -> ToolResult:
        results = self.retriever.retrieve(query, limit=limit)
        items = [
            {"title": r.item.title, "type": r.item.metadata.type, "score": round(r.score, 3)}
            for r in results
        ]
        return ToolResult(
            tool_name=self.name,
            success=True,
            data={"count": len(results), "items": items},
            raw_output=f"{len(results)} memorias recuperadas para '{query}'."
        )


class WriteEpisodicMemoryTool(BaseTool):
    def __init__(self, memory_manager: MemoryManager | None = None):
        self.memory_manager = memory_manager or MemoryManager()
        super().__init__(ToolMetadata(
            name="write_episodic_memory",
            description="Registra um novo log episodico na memoria de longo prazo",
            input_schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Titulo da sessao"},
                    "content": {"type": "string", "description": "Conteudo da memoria"}
                },
                "required": ["title", "content"]
            },
            output_schema={"type": "object", "properties": {"filepath": {"type": "string"}}},
            risk_level=RiskLevel.LEVEL_2_CREATE_LOCAL,
            requires_confirmation=False,
            timeout=5,
            reversible=True
        ))

    def execute(self, title: str = "", content: str = "", **kwargs: Any) -> ToolResult:
        path = self.memory_manager.append_episodic_log(title, content)
        return ToolResult(
            tool_name=self.name,
            success=True,
            data={"filepath": str(path)},
            raw_output=f"Episodio registrado em {path.name}"
        )
