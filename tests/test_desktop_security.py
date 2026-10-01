"""
Testes unitarios para a camada de seguranca do desktop runtime bridge (Fase 3).
"""

from engine.desktop.security import MAX_PAYLOAD_BYTES, DesktopSecurityManager


def test_security_manager_token_validation():
    sec = DesktopSecurityManager(token="test_secret_token_123")
    assert sec.auth_token == "test_secret_token_123"

    # Token correto
    assert sec.validate_token("test_secret_token_123") is True
    # Com prefixo Bearer
    assert sec.validate_token("Bearer test_secret_token_123") is True
    assert sec.validate_token("bearer  test_secret_token_123 ") is True

    # Tokens invalidos
    assert sec.validate_token("wrong_token") is False
    assert sec.validate_token("") is False
    assert sec.validate_token(None) is False

    # Dev mode permite token vazio no loopback
    sec_dev = DesktopSecurityManager(token="test_tok", dev_mode=True)
    assert sec_dev.validate_token("") is True
    assert sec_dev.validate_token(None) is True
    assert sec_dev.validate_token("wrong_token") is False
    assert sec_dev.validate_token("test_tok") is True


def test_security_manager_origin_validation():
    sec = DesktopSecurityManager(token="test_tok")

    # Origens validas
    assert sec.validate_origin("http://127.0.0.1") is True
    assert sec.validate_origin("http://127.0.0.1:5173") is True
    assert sec.validate_origin("http://localhost:3000") is True
    assert sec.validate_origin("tauri://localhost") is True
    assert sec.validate_origin("null") is True
    assert sec.validate_origin(None) is True

    # Origens externas invalidas
    assert sec.validate_origin("http://malicious-site.com") is False
    assert sec.validate_origin("https://evil.org") is False


def test_security_manager_payload_size_limit():
    sec = DesktopSecurityManager()
    assert sec.validate_payload_size(1024) is True
    assert sec.validate_payload_size(MAX_PAYLOAD_BYTES) is True
    assert sec.validate_payload_size(MAX_PAYLOAD_BYTES + 1) is False
