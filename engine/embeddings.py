"""Layered embedding engine.

Resolution order is explicit and observable:
- provider: ModelGateway embeddings when explicitly requested/configured
- local: optional sentence-transformers model when installed
- hash: deterministic dependency-free fallback

All vectors are projected to the configured store dimension so the SQLite
index remains compatible across backends.
"""

from __future__ import annotations

import hashlib
import math
import os
from typing import Any

from .models.gateway import ModelGateway


class LayeredEmbeddingEngine:
    def __init__(
        self,
        dim: int = 128,
        gateway: ModelGateway | None = None,
        mode: str | None = None,
    ) -> None:
        self.dim = dim
        self.gateway = gateway
        resolved_mode = mode if mode is not None else os.getenv("THSYR_EMBEDDING_MODE", "auto")
        self.mode = (resolved_mode or "auto").lower()
        self.last_backend = "hash"
        self._local_model: Any | None = None
        self._local_model_loaded = False

    def _normalise(self, vector: list[float]) -> list[float]:
        norm = math.sqrt(sum(value * value for value in vector))
        if norm <= 0:
            return [0.0] * self.dim
        return [round(value / norm, 6) for value in vector]

    def _project(self, vector: list[float]) -> list[float]:
        if len(vector) == self.dim:
            return self._normalise(vector)
        projected = [0.0] * self.dim
        for index, value in enumerate(vector):
            digest = hashlib.sha256(str(index).encode("utf-8")).digest()
            target = int.from_bytes(digest[:2], "big") % self.dim
            sign = 1.0 if digest[2] % 2 == 0 else -1.0
            projected[target] += float(value) * sign
        return self._normalise(projected)

    def _hash_embedding(self, text: str) -> list[float]:
        if not text:
            return [0.0] * self.dim
        vector = [0.0] * self.dim
        tokens = text.lower().split()
        features = list(tokens)
        for token in tokens:
            if len(token) >= 3:
                features.extend(token[index:index + 3] for index in range(len(token) - 2))
        for feature in features:
            digest = hashlib.sha256(feature.encode("utf-8")).digest()
            target = int.from_bytes(digest[:2], "big") % self.dim
            sign = 1.0 if digest[2] % 2 == 0 else -1.0
            vector[target] += sign * (1.0 + digest[3] / 255.0)
        return self._normalise(vector)

    def _local_embedding(self, text: str) -> list[float] | None:
        if not self._local_model_loaded:
            self._local_model_loaded = True
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore
            except ImportError:
                return None
            model_name = os.getenv(
                "THSYR_LOCAL_EMBEDDING_MODEL",
                "sentence-transformers/all-MiniLM-L6-v2",
            )
            try:
                self._local_model = SentenceTransformer(model_name)
            except Exception:
                self._local_model = None
        if self._local_model is None:
            return None
        try:
            raw: Any = self._local_model.encode([text], normalize_embeddings=True)[0]
            return self._project([float(value) for value in raw])
        except Exception:
            return None

    def _provider_embedding(self, text: str) -> list[float] | None:
        gateway = self.gateway
        if gateway is None:
            gateway = ModelGateway()
        if not gateway.providers:
            return None
        try:
            vectors = gateway.embed([text])
        except Exception:
            return None
        if not vectors:
            return None
        return self._project([float(value) for value in vectors[0]])

    def embed(self, text: str) -> list[float]:
        if self.mode == "provider":
            provider = self._provider_embedding(text)
            if provider is not None:
                self.last_backend = "provider"
                return provider
        elif self.mode == "local":
            local = self._local_embedding(text)
            if local is not None:
                self.last_backend = "local"
                return local
        elif self.mode == "auto":
            if os.getenv("THSYR_ALLOW_LOCAL_EMBEDDINGS", "").lower() in {"1", "true", "yes"}:
                local = self._local_embedding(text)
                if local is not None:
                    self.last_backend = "local"
                    return local
            if os.getenv("THSYR_ALLOW_PROVIDER_EMBEDDINGS", "").lower() in {"1", "true", "yes"}:
                provider = self._provider_embedding(text)
                if provider is not None:
                    self.last_backend = "provider"
                    return provider

        self.last_backend = "hash"
        return self._hash_embedding(text)

    def status(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "last_backend": self.last_backend,
            "dimension": self.dim,
            "local_optional_dependency": "sentence-transformers",
            "local_opt_in": os.getenv("THSYR_ALLOW_LOCAL_EMBEDDINGS", "").lower()
            in {"1", "true", "yes"},
            "provider_opt_in": os.getenv("THSYR_ALLOW_PROVIDER_EMBEDDINGS", "").lower()
            in {"1", "true", "yes"},
        }
