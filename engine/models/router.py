"""
ThSyr Model Router (Fase 3 - Model Gateway)
Classifica tarefas e seleciona dinamicamente a categoria e modelo ideais:
- Pergunta simples / consulta rápida -> Fast Model
- Arquitetura complexa / código / raciocínio -> Reasoning Model
- Imagem / diagrama / tela -> Vision Model
- Vetorização de texto -> Embedding Model
- Processamento em lote -> Batch Model
"""

import re

from ..config import setup_logger
from .base import ChatMessage, ModelRequest, ModelRole, ModelTier

logger = setup_logger("model_router")

REASONING_KEYWORDS = {
    "arquitetura", "planeje", "planejamento", "analise", "refatore", "refatoracao",
    "complexo", "resolva", "implemente", "prova", "tradeoff", "trade-off",
    "algoritmo", "concorrencia", "banco de dados", "otimizacao", "benchmark"
}

VISION_KEYWORDS = {
    "imagem", "screenshot", "printscreen", "captura de tela", "foto", "canvas", "diagrama visual", "mockup", "ui", "layout"
}


class ModelRouter:
    def __init__(self):
        pass

    def classify_task(
        self,
        query: str,
        has_images: bool = False,
        is_batch: bool = False
    ) -> ModelTier:
        if has_images:
            return ModelTier.VISION

        if is_batch:
            return ModelTier.BATCH

        # Deteccao de codigo markdown ou blocos de codigo prioritario
        if "```" in query or len(query.splitlines()) > 15:
            return ModelTier.REASONING

        q_lower = query.lower()

        # Deteccao de visao por palavras-chave
        if any(re.search(rf"\b{re.escape(w)}\b", q_lower) for w in VISION_KEYWORDS):
            return ModelTier.VISION

        # Deteccao de palavras-chave de raciocinio profundo
        if any(re.search(rf"\b{re.escape(kw)}\b", q_lower) for kw in REASONING_KEYWORDS):
            return ModelTier.REASONING

        # Perguntas simples / padrao
        return ModelTier.FAST

    def build_request(
        self,
        query: str,
        context: str | None = None,
        system_prompt: str | None = None,
        forced_tier: ModelTier | None = None,
        has_images: bool = False,
        images: list[str] | None = None,
    ) -> ModelRequest:
        effective_has_images = has_images or bool(images)
        tier = forced_tier or self.classify_task(query, has_images=effective_has_images)

        messages = []
        if system_prompt:
            messages.append(ChatMessage(role=ModelRole.SYSTEM, content=system_prompt))
        elif context:
            messages.append(ChatMessage(role=ModelRole.SYSTEM, content=context))

        messages.append(ChatMessage(role=ModelRole.USER, content=query))

        logger.debug(f"Request roteado para o tier: {tier.value}")
        return ModelRequest(
            messages=messages,
            tier=tier,
            images=images,
        )
