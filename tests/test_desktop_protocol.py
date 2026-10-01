"""
Testes unitarios para o protocolo e DTOs do ThSyr Desktop Control Center.
"""

import pytest

from engine.desktop.protocol import (
    PROTOCOL_VERSION,
    CommandGoalPayload,
    CommandMessagePayload,
    EventType,
    GraphEdgeDto,
    GraphNodeDto,
    GraphSnapshotDto,
    ProtocolEnvelope,
    RuntimeStatusDto,
)


def test_protocol_envelope_roundtrip():
    env = ProtocolEnvelope(
        type=EventType.MESSAGE_ACCEPTED.value,
        session_id="sess_123",
        correlation_id="op_456",
        payload={"text": "teste de mensagem"},
    )
    d = env.to_dict()
    assert d["protocol"] == PROTOCOL_VERSION
    assert d["type"] == "message.accepted"
    assert d["session_id"] == "sess_123"
    assert d["correlation_id"] == "op_456"
    assert d["payload"]["text"] == "teste de mensagem"

    restored = ProtocolEnvelope.from_dict(d)
    assert restored.protocol == env.protocol
    assert restored.type == env.type
    assert restored.id == env.id
    assert restored.session_id == env.session_id
    assert restored.correlation_id == env.correlation_id
    assert restored.payload == env.payload


def test_protocol_envelope_validation_errors():
    with pytest.raises(ValueError, match="deve ser um dicionario"):
        ProtocolEnvelope.from_dict("invalid")

    with pytest.raises(ValueError, match="Versao de protocolo nao suportada"):
        ProtocolEnvelope.from_dict({"protocol": 999, "type": "some.event"})

    with pytest.raises(ValueError, match="Campo 'type' obrigatorio"):
        ProtocolEnvelope.from_dict({"protocol": PROTOCOL_VERSION})

    with pytest.raises(ValueError, match="Campo 'payload' deve ser um objeto"):
        ProtocolEnvelope.from_dict({"protocol": PROTOCOL_VERSION, "type": "some.event", "payload": "not_a_dict"})


def test_command_message_payload():
    valid = CommandMessagePayload.from_dict({"text": " Ola Syr "})
    assert valid.text == "Ola Syr"

    with pytest.raises(ValueError, match="Texto da mensagem deve ser string nao vazia"):
        CommandMessagePayload.from_dict({"text": "   "})

    with pytest.raises(ValueError, match="Texto da mensagem deve ser string nao vazia"):
        CommandMessagePayload.from_dict({"text": 123})


def test_command_goal_payload():
    valid = CommandGoalPayload.from_dict({
        "title": "Refatorar Testes",
        "description": "Detalhes",
        "priority": 1,
        "project": "ThSyr",
    })
    assert valid.title == "Refatorar Testes"
    assert valid.description == "Detalhes"
    assert valid.priority == 1
    assert valid.project == "ThSyr"

    with pytest.raises(ValueError, match="Titulo do objetivo deve ser string nao vazia"):
        CommandGoalPayload.from_dict({"title": ""})


def test_graph_snapshot_dto():
    node = GraphNodeDto(
        id="node_a",
        label="Node A",
        group="tech",
        lobe="parietal",
        kind="concept",
        degree=4,
        is_hub=False,
    )
    edge = GraphEdgeDto(
        source="node_a",
        target="node_b",
        weight=2.5,
    )
    snapshot = GraphSnapshotDto(
        version=1,
        total_nodes=1,
        total_edges=1,
        nodes=[node],
        edges=[edge],
    )
    d = snapshot.to_dict()
    assert d["total_nodes"] == 1
    assert d["total_edges"] == 1
    assert d["nodes"][0]["id"] == "node_a"
    assert d["edges"][0]["source"] == "node_a"


def test_runtime_status_dto():
    status = RuntimeStatusDto(
        status="READY",
        runtime_version="0.4.0",
        total_nodes=100,
        total_synapses=200,
        active_sessions=["sess_01"],
    )
    d = status.to_dict()
    assert d["status"] == "READY"
    assert d["runtime_version"] == "0.4.0"
    assert d["total_nodes"] == 100
    assert d["active_sessions"] == ["sess_01"]
