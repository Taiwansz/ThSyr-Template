"""
ThSyr Desktop Security & Handshake Governance
Gerencia tokens efemeros, validacao de handshake WebSocket, limites de payload e bind seguro
(Fase 3 / ADR-010 / 08_SECURITY_AND_GOVERNANCE.md).
"""

from __future__ import annotations

import hmac
import os
import secrets
from typing import Optional

from ..config import setup_logger

logger = setup_logger("desktop_security")

# Limite de tamanho de frame WebSocket para evitar saturacao de memoria
MAX_PAYLOAD_BYTES = 512 * 1024  # 512 KB

# Origens autorizadas para comunicacao com a central de controle local
ALLOWED_ORIGINS = {
    "http://127.0.0.1",
    "http://localhost",
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:4173",
    "http://localhost:4173",
    "tauri://localhost",
    "http://tauri.localhost",
    "https://tauri.localhost",
}


class DesktopSecurityManager:
    def __init__(self, token: Optional[str] = None, dev_mode: Optional[bool] = None):
        # Permite injecao via env var (passada pelo launcher do Tauri) ou gera token seguro por boot
        env_token = os.environ.get("THSYR_DESKTOP_TOKEN")
        self._auth_token: str = token or env_token or secrets.token_urlsafe(32)
        if dev_mode is not None:
            self._dev_mode = dev_mode
        else:
            self._dev_mode = os.environ.get("THSYR_DESKTOP_DEV", "0") == "1"

    @property
    def auth_token(self) -> str:
        """Retorna o token ativo (nunca persistido em disco)."""
        return self._auth_token

    @property
    def dev_mode(self) -> bool:
        return self._dev_mode

    def validate_token(self, candidate_token: Optional[str]) -> bool:
        """Valida o token candidate em tempo constante contra ataques de timing."""
        if self._dev_mode and not candidate_token:
            return True
        if not candidate_token:
            return False
        # Remove prefixo 'Bearer ' caso presente
        clean_candidate = candidate_token.strip()
        if clean_candidate.lower().startswith("bearer "):
            clean_candidate = clean_candidate[7:].strip()

        return hmac.compare_digest(clean_candidate, self._auth_token)

    def validate_origin(self, origin: Optional[str]) -> bool:
        """Valida que a requisicao/conexao parte exclusivamente de WebView local ou loopback dev."""
        if not origin or origin == "null":
            # Webviews locais nativas do Tauri frequentemente enviam origin null ou tauri://
            return True

        normalized = origin.strip().rstrip("/")
        # Checa presenca na lista permitida ou loopback com porta variavel
        if normalized in ALLOWED_ORIGINS:
            return True

        for allowed in ALLOWED_ORIGINS:
            if normalized.startswith(allowed):
                return True

        logger.warning(f"Origem nao autorizada rejeitada pelo gate de seguranca: {origin}")
        return False

    def validate_payload_size(self, payload_size: int) -> bool:
        return payload_size <= MAX_PAYLOAD_BYTES
