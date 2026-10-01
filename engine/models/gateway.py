"""
ThSyr Model Gateway (Fase 3 - Model Gateway)
Gerencia multiplos provedores de IA com:
1. Fallback automatico transparente em caso de falha de rede ou cota
2. Rastreamento continuo de telemetria (latencia, tokens e custo estimado em USD)
3. Persistencia de metricas em state/model_telemetry.json
4. Interfaces unificadas para generate, stream e embed
5. Fronteira estrita de ambiente: MockProvider estritamente proibido em producao
"""

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..config import settings, setup_logger
from .base import BaseModelProvider, ModelRequest, ModelResponse, ModelTier, StreamChunk
from .providers.agy_provider import AgyCliProvider
from .providers.http_provider import GenericHttpProvider
from .providers.mock import MockProvider

logger = setup_logger("model_gateway")


class ModelUnavailableError(RuntimeError):
    """Lancada quando nenhum provedor de producao valido esta disponivel."""
    pass


class ModelGateway:
    def __init__(
        self,
        providers: Optional[List[BaseModelProvider]] = None,
        telemetry_file: Optional[Path] = None,
        allow_mock: Optional[bool] = None
    ):
        self.telemetry_file = telemetry_file or (settings.brain.state_dir / "model_telemetry.json")
        self.providers: List[BaseModelProvider] = providers or []

        # Determinar permissao de MockProvider conforme ambiente
        mock_permitted = allow_mock if allow_mock is not None else (settings.env in ("test", "development"))

        # Se nenhum provedor foi fornecido, inicializa provedores disponiveis
        if not self.providers:
            # 1. Provedor Local Antigravity CLI / Windows Credential
            if settings.env != "test":
                agy_prov = AgyCliProvider()
                if agy_prov.is_available():
                    self.providers.append(agy_prov)

            # 2. Provedor HTTP generico (caso haja chave configurada explicitamente)
            http_prov = GenericHttpProvider()
            if http_prov.is_configured():
                self.providers.append(http_prov)

            # 3. MockProvider apenas se permitido em dev/test
            if mock_permitted:
                self.providers.append(MockProvider())

        self.telemetry: Dict[str, Any] = {
            "total_requests": 0,
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_tokens": 0,
            "total_cost_usd": 0.0,
            "total_latency_ms": 0.0,
            "requests_by_tier": {t.value: 0 for t in ModelTier},
            "requests_by_provider": {},
            "fallback_count": 0
        }
        self._load_telemetry()

    def _load_telemetry(self) -> None:
        if self.telemetry_file.exists():
            try:
                data = json.loads(self.telemetry_file.read_text(encoding="utf-8"))
                for k, v in data.items():
                    if k in self.telemetry:
                        self.telemetry[k] = v
            except Exception as e:
                logger.warning(f"Erro ao carregar telemetria: {e}")

    def _persist_telemetry(self) -> None:
        try:
            self.telemetry_file.parent.mkdir(parents=True, exist_ok=True)
            self.telemetry_file.write_text(
                json.dumps(self.telemetry, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
        except Exception as e:
            logger.warning(f"Falha ao persistir telemetria: {e}")

    def register_provider(self, provider: BaseModelProvider, prepend: bool = False) -> None:
        if prepend:
            self.providers.insert(0, provider)
        else:
            self.providers.append(provider)

    def _record_telemetry(self, resp: ModelResponse, tier: ModelTier, was_fallback: bool = False) -> None:
        t = resp.telemetry
        self.telemetry["total_requests"] = int(self.telemetry["total_requests"]) + 1
        self.telemetry["total_prompt_tokens"] = int(self.telemetry["total_prompt_tokens"]) + t.prompt_tokens
        self.telemetry["total_completion_tokens"] = int(self.telemetry["total_completion_tokens"]) + t.completion_tokens
        self.telemetry["total_tokens"] = int(self.telemetry["total_tokens"]) + t.total_tokens
        self.telemetry["total_cost_usd"] = round(float(self.telemetry["total_cost_usd"]) + t.estimated_cost_usd, 6)
        self.telemetry["total_latency_ms"] = round(float(self.telemetry["total_latency_ms"]) + t.latency_ms, 2)

        tier_key = tier.value if isinstance(tier, ModelTier) else str(tier)
        by_tier = self.telemetry.setdefault("requests_by_tier", {})
        if isinstance(by_tier, dict):
            by_tier[tier_key] = int(by_tier.get(tier_key, 0)) + 1

        prov = resp.provider_name
        by_prov = self.telemetry.setdefault("requests_by_provider", {})
        if isinstance(by_prov, dict):
            by_prov[prov] = int(by_prov.get(prov, 0)) + 1

        if was_fallback:
            self.telemetry["fallback_count"] = int(self.telemetry.get("fallback_count", 0)) + 1

        self._persist_telemetry()

    def generate(self, request: ModelRequest) -> ModelResponse:
        if not self.providers:
            raise ModelUnavailableError(
                "MODEL_UNAVAILABLE: Nenhum provedor de modelo configurado no Model Gateway. "
                "Configure OPENAI_API_KEY, OPENROUTER_API_KEY ou defina THSYR_ENV=development para operacao offline/local."
            )
        errors = []
        for i, provider in enumerate(self.providers):
            if not provider.supports_tier(request.tier):
                continue
            try:
                response = provider.generate(request)
                self._record_telemetry(response, request.tier, was_fallback=(i > 0))
                return response
            except Exception as e:
                logger.warning(f"Provedor '{provider.provider_name}' falhou: {e}. Tentando fallback...")
                errors.append(f"{provider.provider_name}: {e!s}")

        raise ModelUnavailableError(
            f"MODEL_UNAVAILABLE: Todos os provedores do Model Gateway falharam. Detalhes: {'; '.join(errors)}"
        )

    def stream(self, request: ModelRequest) -> Iterator[StreamChunk]:
        if not self.providers:
            raise ModelUnavailableError(
                "MODEL_UNAVAILABLE: Nenhum provedor de modelo configurado no Model Gateway. "
                "Configure OPENAI_API_KEY, OPENROUTER_API_KEY ou defina THSYR_ENV=development para operacao offline/local."
            )
        errors = []
        for i, provider in enumerate(self.providers):
            if not provider.supports_tier(request.tier):
                continue
            try:
                # Se o stream iniciar sem erros, consome o gerador
                yield from provider.stream(request)
                return
            except Exception as e:
                logger.warning(f"Stream do provedor '{provider.provider_name}' falhou: {e}. Tentando fallback...")
                errors.append(f"{provider.provider_name}: {e!s}")

        raise ModelUnavailableError(
            f"MODEL_UNAVAILABLE: Todos os provedores falharam no streaming: {'; '.join(errors)}"
        )

    def embed(self, texts: List[str]) -> List[List[float]]:
        for provider in self.providers:
            try:
                return provider.embed(texts)
            except Exception as e:
                logger.warning(f"Embedding com '{provider.provider_name}' falhou: {e}")

        # Fallback deterministico
        if settings.env in ("test", "development"):
            fallback = MockProvider()
            return fallback.embed(texts)

        raise ModelUnavailableError("MODEL_UNAVAILABLE: Provedores de embedding indisponiveis em producao.")

    def get_telemetry_summary(self) -> Dict[str, Any]:
        return dict(self.telemetry)
