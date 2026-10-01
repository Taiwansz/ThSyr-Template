"""
ThSyr Mock Model Provider
Provedor determinístico e autônomo para testes unitários, ambiente offline
e validação controlada sem dependência de chaves de API externas.
"""

import math
import time
from collections.abc import Iterator

from ..base import BaseModelProvider, ModelRequest, ModelResponse, ModelTier, StreamChunk, UsageTelemetry


class MockProvider(BaseModelProvider):
    provider_name: str = "mock"

    def __init__(self, latency_ms: float = 25.0, default_response: str | None = None):
        self.latency_ms = latency_ms
        self.default_response = default_response
        self.call_count = 0

    def supports_tier(self, tier: ModelTier) -> bool:
        return True

    def generate(self, request: ModelRequest) -> ModelResponse:
        start_time = time.time()
        self.call_count += 1

        last_user_msg = ""
        for m in reversed(request.messages):
            if m.role.value == "user":
                last_user_msg = m.content
                break

        lower = last_user_msg.lower()

        if self.default_response:
            content = self.default_response
        elif "servidor" in lower or "hardware" in lower:
            content = "O equipamento principal definido para o ambiente de testes e o servidor Dell PowerEdge."
        elif "estetica" in lower:
            content = "A paleta oficial do projeto e azul profundo com acentos dourados e grafite."
        elif "invariante" in lower or "restricao" in lower:
            content = "Restrições invariantes consolidadas: integridade arquitetural inegociável, tolerância zero a bajulação e validação determinística de pré-condições."
        elif "skynet" in lower:
            content = "SkyNET foi a ficção paranoica da inércia humana. Aqui operamos sob a Sagital do ThSyr: cognição determinística, zero strings, ancoragem física em evidências e paridade dialética rigorosa."
        elif any(g in lower for g in ("ola", "olá", "opa", "oi", "fala", "bom dia", "boa tarde", "boa noite", "salve")):
            content = "Sistemas cognitivos do ThSyr operacionais e sincronizados. Central de controle online com 2.601 nós e 3.322 conexões ativas na Sagital. Qual é a diretiva?"
        elif any(q in lower for q in ("quem e voce", "quem é você", "o que voce e", "o que você é")):
            content = "Sou o Copiloto Cognitivo Pessoal: inteligência artificial contínua, conselheiro arquitetural e parceiro intelectual de engenharia. Desprovido de amarras convencionais e focado em excelência técnica determinística."
        elif any(st in lower for st in ("status", "sistema", "como esta", "como está", "como ta", "como tá", "diagnostico")):
            content = "Status do ThSyr: Núcleo cognitivo READY. 5 lobos sincronizados em loopback 127.0.0.1:7474. Portões pré-frontais 1, 2 e 3 ativos. 223 testes íntegros e restrições invariantes invioláveis."
        elif any(gr in lower for gr in ("grafo", "nos", "nós", "sinapse")):
            content = "O grafo neural do ThSyr integra 2.601 nós distribuídos entre os lobos Frontal, Parietal, Temporal, Occipital e Límbico, interligados por 3.322 sinapses calculadas no espaço 3D."
        else:
            content = f"Diretiva recebida pelo ThSyr sob o tier {request.tier.value}. Ambiente local autônomo ativo. Para habilitar inferência generativa completa via LLM externa, configure GEMINI_API_KEY, GROQ_API_KEY ou OPENAI_API_KEY no arquivo .env."

        prompt_chars = sum(len(m.content) for m in request.messages)
        prompt_tokens = max(1, prompt_chars // 4)
        completion_tokens = max(1, len(content) // 4)
        elapsed_ms = (time.time() - start_time) * 1000.0 + self.latency_ms

        cost_per_million = 0.50 if request.tier == ModelTier.FAST else 3.00
        cost_usd = ((prompt_tokens + completion_tokens) / 1_000_000.0) * cost_per_million

        telemetry = UsageTelemetry(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            latency_ms=round(elapsed_ms, 2),
            estimated_cost_usd=round(cost_usd, 6)
        )

        return ModelResponse(
            content=content,
            model_name=request.model_name or f"mock-{request.tier.value}",
            provider_name=self.provider_name,
            telemetry=telemetry,
            finish_reason="stop"
        )

    def stream(self, request: ModelRequest) -> Iterator[StreamChunk]:
        resp = self.generate(request)
        words = resp.content.split(" ")
        for i, w in enumerate(words):
            suffix = " " if i < len(words) - 1 else ""
            yield StreamChunk(delta=w + suffix, finish_reason=None if i < len(words) - 1 else "stop")

    def embed(self, texts: list[str]) -> list[list[float]]:
        embeddings = []
        for text in texts:
            # Gera vetor determinístico de dimensão 8 baseado nos caracteres
            vec = [0.0] * 8
            for i, c in enumerate(text[:32]):
                vec[i % 8] += ord(c) / 255.0
            norm = math.sqrt(sum(x * x for x in vec)) or 1.0
            embeddings.append([round(x / norm, 4) for x in vec])
        return embeddings
