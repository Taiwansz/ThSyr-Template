"""
ThSyr Generic HTTP Model Provider
Provedor REST baseado puramente na biblioteca padrão (urllib.request)
compatível com APIs no padrão OpenAI, OpenRouter, Local Ollama ou vLLM.
"""

import base64
import json
import mimetypes
import os
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from ...config import setup_logger
from ..base import BaseModelProvider, ModelRequest, ModelResponse, ModelTier, StreamChunk, UsageTelemetry

logger = setup_logger("http_provider")


class GenericHttpProvider(BaseModelProvider):
    provider_name: str = "openai_compatible"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout_seconds: int = 25,
        default_model: str | None = None
    ):
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        groq_key = os.getenv("GROQ_API_KEY")
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        if api_key:
            self.api_key = api_key
            self.base_url = (base_url or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
        elif gemini_key:
            self.api_key = gemini_key
            self.base_url = (base_url or os.getenv("OPENAI_BASE_URL") or "https://generativelanguage.googleapis.com/v1beta/openai").rstrip("/")
            self.provider_name = "gemini"
        elif groq_key:
            self.api_key = groq_key
            self.base_url = (base_url or os.getenv("OPENAI_BASE_URL") or "https://api.groq.com/openai/v1").rstrip("/")
            self.provider_name = "groq"
        elif openrouter_key:
            self.api_key = openrouter_key
            self.base_url = (base_url or os.getenv("OPENAI_BASE_URL") or "https://openrouter.ai/api/v1").rstrip("/")
            self.provider_name = "openrouter"
        elif deepseek_key:
            self.api_key = deepseek_key
            self.base_url = (base_url or os.getenv("OPENAI_BASE_URL") or "https://api.deepseek.com").rstrip("/")
            self.provider_name = "deepseek"
        else:
            self.api_key = openai_key
            self.base_url = (base_url or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")

        self.timeout = timeout_seconds
        self.default_model = default_model

    def is_configured(self) -> bool:
        return bool(self.api_key) or "localhost" in self.base_url or "127.0.0.1" in self.base_url

    def supports_tier(self, tier: ModelTier) -> bool:
        return self.is_configured()

    @staticmethod
    def _image_to_url(image_ref: str) -> str:
        """Converte arquivo local em data URI ou preserva URLs remotas/data URI."""
        if image_ref.startswith(("http://", "https://", "data:")):
            return image_ref

        path = Path(image_ref)
        if not path.is_file():
            raise FileNotFoundError(f"Imagem multimodal nao encontrada: {path}")

        mime_type = mimetypes.guess_type(path.name)[0] or "image/png"
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:{mime_type};base64,{encoded}"

    def _build_messages_payload(self, request: ModelRequest) -> list[dict[str, Any]]:
        messages_payload = [message.to_dict() for message in request.messages]
        if not request.images:
            return messages_payload

        user_indexes = [
            index for index, message in enumerate(messages_payload)
            if message.get("role") == "user"
        ]
        if not user_indexes:
            raise ValueError("Requisicao multimodal precisa conter ao menos uma mensagem de usuario.")

        last_user_index = user_indexes[-1]
        original_content = messages_payload[last_user_index].get("content", "")
        multimodal_content: list[dict[str, Any]] = [
            {"type": "text", "text": str(original_content)}
        ]
        for image_ref in request.images:
            multimodal_content.append({
                "type": "image_url",
                "image_url": {"url": self._image_to_url(image_ref)},
            })
        messages_payload[last_user_index]["content"] = multimodal_content
        return messages_payload

    def _resolve_model(self, request: ModelRequest) -> str:
        if request.model_name:
            return request.model_name
        if self.default_model:
            return self.default_model

        if "generativelanguage.googleapis.com" in self.base_url:
            if request.tier == ModelTier.FAST:
                return "gemini-2.5-flash"
            elif request.tier == ModelTier.REASONING:
                return "gemini-2.5-pro"
            elif request.tier == ModelTier.VISION:
                return "gemini-2.5-flash"
            elif request.tier == ModelTier.EMBEDDING:
                return "text-embedding-004"
            return "gemini-2.5-flash"

        if "api.groq.com" in self.base_url:
            if request.tier == ModelTier.FAST:
                return "llama-3.1-8b-instant"
            elif request.tier == ModelTier.REASONING:
                return "llama-3.3-70b-versatile"
            return "llama-3.1-8b-instant"

        if "openrouter.ai" in self.base_url:
            if request.tier == ModelTier.FAST:
                return "google/gemini-2.5-flash"
            elif request.tier == ModelTier.REASONING:
                return "anthropic/claude-3.5-sonnet"
            return "google/gemini-2.5-flash"

        if "deepseek.com" in self.base_url:
            if request.tier == ModelTier.REASONING:
                return "deepseek-reasoner"
            return "deepseek-chat"

        # Modelos padrao por tier (OpenAI ou compativeis locais)
        if request.tier == ModelTier.FAST:
            return "gpt-4o-mini"
        elif request.tier == ModelTier.REASONING:
            return "o1-mini"
        elif request.tier == ModelTier.VISION:
            return "gpt-4o"
        elif request.tier == ModelTier.EMBEDDING:
            return "text-embedding-3-small"
        return "gpt-4o-mini"

    def generate(self, request: ModelRequest) -> ModelResponse:
        if not self.is_configured():
            raise RuntimeError("GenericHttpProvider nao configurado com API Key ou URL valida.")

        model = self._resolve_model(request)
        endpoint = f"{self.base_url}/chat/completions"

        messages_payload = self._build_messages_payload(request)
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages_payload,
            "temperature": request.temperature
        }
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "ThSyr-Cognitive-Gateway/1.0"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(endpoint, data=data_bytes, headers=headers, method="POST")

        start_time = time.time()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            raise RuntimeError(f"Erro HTTP {e.code} da API: {err_body}")
        except Exception as e:
            raise RuntimeError(f"Falha de comunicacao com endpoint {endpoint}: {e}")

        elapsed_ms = (time.time() - start_time) * 1000.0

        choice = body.get("choices", [{}])[0]
        content = choice.get("message", {}).get("content", "") or ""
        finish_reason = choice.get("finish_reason", "stop")

        usage = body.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)

        telemetry = UsageTelemetry(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=round(elapsed_ms, 2),
            estimated_cost_usd=round((total_tokens / 1_000_000.0) * 1.5, 6)
        )

        return ModelResponse(
            content=content,
            model_name=model,
            provider_name=self.provider_name,
            telemetry=telemetry,
            finish_reason=finish_reason
        )

    def stream(self, request: ModelRequest) -> Iterator[StreamChunk]:
        # Implementação básica com geração de bloco para fallback
        resp = self.generate(request)
        yield StreamChunk(delta=resp.content, finish_reason=resp.finish_reason)

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not self.is_configured():
            raise RuntimeError("GenericHttpProvider nao configurado para embeddings.")

        endpoint = f"{self.base_url}/embeddings"
        payload = {
            "model": "text-embedding-3-small",
            "input": texts
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
        }
        req = urllib.request.Request(endpoint, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")

        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        embeddings = [d["embedding"] for d in body.get("data", [])]
        return embeddings
