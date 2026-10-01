"""
Testes end-to-end para FastAPI e WebSocket do ThSyr Desktop Control Center (Fase 3).
Valida endpoints HTTP, autenticacao por token, handshake WebSocket e despacho de comandos.
"""

import json

import pytest
from fastapi.testclient import TestClient

from engine.desktop.app import create_desktop_app
from engine.desktop.protocol import CommandType, EventType, ProtocolEnvelope
from engine.desktop.runtime_service import DesktopRuntimeService
from engine.desktop.security import DesktopSecurityManager


@pytest.fixture
def test_setup():
    security = DesktopSecurityManager(token="test_secret_key_42")
    service = DesktopRuntimeService()
    app = create_desktop_app(runtime_service=service, security_manager=security)
    client = TestClient(app)
    return client, security, service


def test_health_endpoint(test_setup):
    client, _, _ = test_setup
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["runtime"] == "ready"
    assert data["protocol"] == 1
    assert data["version"] == "0.4.0"


def test_status_endpoint_auth(test_setup):
    client, security, _ = test_setup

    # Sem autenticacao -> 401
    unauth = client.get("/status")
    assert unauth.status_code == 401

    # Com token invalido -> 401
    bad_token = client.get("/status", headers={"Authorization": "Bearer wrong_token"})
    assert bad_token.status_code == 401

    # Com token valido -> 200
    auth = client.get("/status", headers={"Authorization": f"Bearer {security.auth_token}"})
    assert auth.status_code == 200
    data = auth.json()
    assert data["status"] == "READY"
    assert data["total_nodes"] > 0


def test_graph_endpoint_auth(test_setup):
    client, security, _ = test_setup

    unauth = client.get("/graph")
    assert unauth.status_code == 401

    auth = client.get("/graph", headers={"Authorization": f"Bearer {security.auth_token}"})
    assert auth.status_code == 200
    data = auth.json()
    assert "nodes" in data
    assert "edges" in data
    assert data["total_nodes"] > 0


def test_websocket_invalid_token_rejected(test_setup):
    client, _, _ = test_setup
    with pytest.raises(Exception):
        with client.websocket_connect("/ws?token=invalid_token") as ws:
            ws.receive_text()


def test_websocket_end_to_end_command_message(test_setup):
    """Gate da Fase 3: conexao WebSocket end-to-end, handshake autenticado e fluxo completo."""
    client, security, _ = test_setup

    with client.websocket_connect(f"/ws?token={security.auth_token}") as ws:
        # 1. Primeiro frame recebido deve ser runtime.ready
        initial_raw = ws.receive_text()
        initial_frame = json.loads(initial_raw)
        assert initial_frame["type"] == EventType.RUNTIME_READY.value
        assert initial_frame["payload"]["status"] == "READY"

        # 2. Enviar command.message
        cmd = ProtocolEnvelope(
            type=CommandType.COMMAND_MESSAGE.value,
            session_id="ws_sess_1",
            correlation_id="op_ws_101",
            payload={"text": "/help"},
        )
        ws.send_text(json.dumps(cmd.to_dict()))

        # 3. Coletar respostas e eventos intermediarios
        received_types = []
        final_answer = None

        # Aguardar ate o frame response.final
        for _ in range(6):
            frame_raw = ws.receive_text()
            frame = json.loads(frame_raw)
            received_types.append(frame["type"])
            assert frame["correlation_id"] == "op_ws_101"
            assert frame["session_id"] == "ws_sess_1"

            if frame["type"] == EventType.RESPONSE_FINAL.value:
                final_answer = frame["payload"]["answer"]
                break

        assert EventType.MESSAGE_ACCEPTED.value in received_types
        assert EventType.RESPONSE_FINAL.value in received_types
        assert final_answer is not None
        assert "Comandos Universais do Syr" in final_answer or "help" in final_answer.lower()
