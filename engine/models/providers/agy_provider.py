"""
ThSyr Antigravity CLI Model Provider
Provedor de modelo generativo acoplado diretamente a infraestrutura local
da CLI Antigravity (agy.exe) e credenciais ativas do Windows Credential Manager.
Permite operacao real com modelos Gemini de ponta sem necessidade de chaves de API manuais.
"""

import json
import os
import shutil
import subprocess
import sys
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from ...config import settings, setup_logger
from ..base import (
    BaseModelProvider,
    ModelRequest,
    ModelResponse,
    ModelRole,
    ModelTier,
    StreamChunk,
    UsageTelemetry,
)
from .mock import MockProvider

logger = setup_logger("agy_provider")


def find_agy_binary() -> str | None:
    """Localiza o binario agy.exe no PATH ou nos diretorios padrao do sistema."""
    which_path = shutil.which("agy.exe") or shutil.which("agy")
    if which_path:
        return which_path

    appdata = os.getenv("LOCALAPPDATA")
    if appdata:
        cand = Path(appdata) / "agy" / "bin" / "agy.exe"
        if cand.is_file():
            return str(cand)

    cand2 = Path.home() / "AppData" / "Local" / "agy" / "bin" / "agy.exe"
    if cand2.is_file():
        return str(cand2)

    return None


def has_windows_gemini_credential() -> bool:
    """Verifica se ha uma credencial de sessao Antigravity registrada no Windows Credential Manager."""
    if sys.platform != "win32":
        return False
    try:
        import ctypes
        from ctypes import wintypes

        advapi32 = ctypes.windll.advapi32

        class CREDENTIAL(ctypes.Structure):
            _fields_ = [
                ("Flags", wintypes.DWORD),
                ("Type", wintypes.DWORD),
                ("TargetName", wintypes.LPWSTR),
                ("Comment", wintypes.LPWSTR),
                ("LastWritten", wintypes.FILETIME),
                ("CredentialBlobSize", wintypes.DWORD),
                ("CredentialBlob", ctypes.POINTER(ctypes.c_byte)),
                ("Persist", wintypes.DWORD),
                ("AttributeCount", wintypes.DWORD),
                ("Attributes", ctypes.c_void_p),
                ("TargetAlias", wintypes.LPWSTR),
                ("UserName", wintypes.LPWSTR),
            ]

        pcred = ctypes.POINTER(CREDENTIAL)()
        res = advapi32.CredReadW("gemini:antigravity", 1, 0, ctypes.byref(pcred))
        if res:
            advapi32.CredFree(pcred)
            return True
        return False
    except Exception:
        return False


class AgyCliProvider(BaseModelProvider):
    provider_name: str = "antigravity_cli"

    def __init__(
        self,
        binary_path: str | None = None,
        timeout_seconds: int = 45,
        default_model: str | None = None,
    ):
        self.agy_path = binary_path or find_agy_binary()
        self.timeout = timeout_seconds
        self.default_model = default_model
        self._fallback_embedder = MockProvider()

    def is_available(self) -> bool:
        """Indica se o binario e o contexto de autenticacao estao disponiveis."""
        if not self.agy_path or not Path(self.agy_path).is_file():
            return False
        return has_windows_gemini_credential() or bool(shutil.which("agy"))

    def supports_tier(self, tier: ModelTier) -> bool:
        if tier in (ModelTier.FAST, ModelTier.REASONING, ModelTier.VISION):
            return self.is_available()
        if tier == ModelTier.EMBEDDING:
            return True
        return False

    def _resolve_model(self, request: ModelRequest) -> str:
        if request.model_name:
            return request.model_name
        if self.default_model:
            return self.default_model

        if request.tier == ModelTier.REASONING:
            return "gemini-3.8-flash-high"
        elif request.tier == ModelTier.VISION:
            return "gemini-3.7-flash-low"
        elif request.tier == ModelTier.FAST:
            return "gemini-3.7-flash-low"
        return "gemini-3.7-flash-low"

    def _build_prompt_text(self, request: ModelRequest) -> str:
        parts: list[str] = []
        for m in request.messages:
            if m.role == ModelRole.SYSTEM:
                parts.append(f"[DIRETRIZES DE SISTEMA - THSYR SAGITAL]\n{m.content}\n")
            elif m.role == ModelRole.ASSISTANT:
                parts.append(f"[RESPOSTA PREVIA DO THSYR]\n{m.content}\n")
            elif m.role == ModelRole.USER:
                parts.append(f"[SOLICITACAO DO OPERADOR]\n{m.content}")
            else:
                parts.append(m.content)
        return "\n\n".join(parts)

    def generate(self, request: ModelRequest) -> ModelResponse:
        if not self.is_available():
            raise RuntimeError("AgyCliProvider indisponivel: binario agy ou credenciais ausentes.")

        if request.tier == ModelTier.VISION and request.images:
            raise RuntimeError(
                "AgyCliProvider recebeu uma requisicao VISION com imagens, mas este adapter nao possui "
                "transporte multimodal comprovado. Falha fechada para permitir fallback a um provider visual real."
            )

        model = self._resolve_model(request)
        prompt_text = self._build_prompt_text(request)

        cmd = [
            self.agy_path,
            "-p", "-",
            "--disable-slash-commands",
            "--model", model,
            "--output-format", "json",
        ]

        start_time = time.time()
        try:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                cwd=str(settings.project_root),
            )
            stdout, stderr = process.communicate(input=prompt_text, timeout=self.timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            raise TimeoutError(f"AgyCliProvider excedeu o limite de {self.timeout}s.")
        except Exception as e:
            raise RuntimeError(f"Falha de subprocesso no AgyCliProvider: {e}")

        elapsed_ms = (time.time() - start_time) * 1000.0

        if process.returncode != 0:
            err_msg = stderr.strip() or stdout.strip() or f"Codigo de saida: {process.returncode}"
            raise RuntimeError(f"Erro na execucao do agy: {err_msg}")

        try:
            data: dict[str, Any] = json.loads(stdout)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Falha ao interpretar resposta JSON do agy: {e} | Saida: {stdout[:200]}")

        content = data.get("response", "").strip()
        usage = data.get("usage", {})
        prompt_tokens = int(usage.get("input_tokens", 0))
        completion_tokens = int(usage.get("output_tokens", 0))
        total_tokens = int(usage.get("total_tokens", prompt_tokens + completion_tokens))

        telemetry = UsageTelemetry(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=round(elapsed_ms, 2),
            estimated_cost_usd=0.0,
        )

        return ModelResponse(
            content=content,
            model_name=model,
            provider_name=self.provider_name,
            telemetry=telemetry,
            finish_reason="stop",
        )

    def stream(self, request: ModelRequest) -> Iterator[StreamChunk]:
        resp = self.generate(request)
        # Emissao de blocos por paragrafo para fluidez no cliente
        paragraphs = resp.content.split("\n\n")
        for i, p in enumerate(paragraphs):
            suffix = "\n\n" if i < len(paragraphs) - 1 else ""
            yield StreamChunk(delta=p + suffix, finish_reason="stop" if i == len(paragraphs) - 1 else None)

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self._fallback_embedder.embed(texts)
