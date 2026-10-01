"""
Testes unitarios e de integracao para o DesktopEventStream e DesktopEventAdapter (Fase 2).
Garante ordenacao estrita de eventos, consistencia de correlation_id e ausencia de eventos fake.
"""

from engine.desktop.event_stream import DesktopEventAdapter, DesktopEventStream
from engine.desktop.protocol import EventType, ProtocolEnvelope
from engine.desktop.runtime_service import DesktopRuntimeService
from engine.interaction.interaction_events import (
    EventBroadcaster,
    EventLevel,
)
from engine.interaction.interaction_events import (
    EventType as InteractionEventType,
)


def test_event_stream_publish_and_subscribe():
    stream = DesktopEventStream(max_buffer_size=10)
    received = []

    def subscriber(envelope: ProtocolEnvelope):
        received.append(envelope)

    stream.subscribe(subscriber)

    env1 = ProtocolEnvelope(
        type=EventType.MESSAGE_ACCEPTED.value,
        session_id="s1",
        correlation_id="op1",
        payload={"msg": 1},
    )
    env2 = ProtocolEnvelope(
        type=EventType.RESPONSE_FINAL.value,
        session_id="s1",
        correlation_id="op1",
        payload={"msg": 2},
    )

    stream.publish(env1)
    stream.publish(env2)

    assert len(received) == 2
    assert received[0].payload["msg"] == 1
    assert received[1].payload["msg"] == 2

    # Unsubscribe
    stream.unsubscribe(subscriber)
    env3 = ProtocolEnvelope(
        type=EventType.NEURAL_PULSE.value,
        session_id="s1",
        correlation_id="op1",
    )
    stream.publish(env3)

    assert len(received) == 2


def test_event_stream_circular_buffer_and_filtering():
    stream = DesktopEventStream(max_buffer_size=5)

    for i in range(8):
        stream.publish(
            ProtocolEnvelope(
                type="test.event",
                session_id="sess_a" if i % 2 == 0 else "sess_b",
                correlation_id=f"op_{i}",
                payload={"index": i},
            )
        )

    # Buffer deve conter no maximo 5 itens
    recent = stream.get_recent(limit=10)
    assert len(recent) == 5
    assert recent[0].payload["index"] == 3
    assert recent[-1].payload["index"] == 7

    # Filtro por sessao
    sess_a_events = stream.get_recent(limit=10, session_id="sess_a")
    for e in sess_a_events:
        assert e.session_id == "sess_a"


def test_adapter_handle_interaction_event():
    stream = DesktopEventStream()
    adapter = DesktopEventAdapter(event_stream=stream, default_session_id="sess_core")
    adapter.set_active_correlation("sess_core", "op_corr_99")

    broadcaster = EventBroadcaster()
    adapter.attach_broadcaster(broadcaster)

    # Emitir evento no broadcaster do core
    ie = broadcaster.emit(
        event_type=InteractionEventType.TOOL_STARTED,
        message="Iniciando execucao de ferramenta",
        level=EventLevel.INFO,
        payload={"tool": "git_status"},
    )

    recent = stream.get_recent(limit=1)
    assert len(recent) == 1
    env = recent[0]
    assert env.type == InteractionEventType.TOOL_STARTED.value
    assert env.session_id == "sess_core"
    assert env.correlation_id == "op_corr_99"
    assert env.payload["tool"] == "git_status"
    assert env.payload["message"] == ie.message


def test_adapter_handle_executive_event():
    stream = DesktopEventStream()
    adapter = DesktopEventAdapter(event_stream=stream, default_session_id="sess_exec")
    adapter.set_active_correlation("sess_exec", "op_exec_1")

    exec_dict = {
        "id": "evt_exec_123",
        "timestamp": "2026-09-25T20:00:00Z",
        "type": "step_end",
        "source": "executive_runner",
        "project": "ThSyr",
        "payload": {"step_order": 1, "success": True},
    }

    env = adapter.handle_executive_event(exec_dict, session_id="sess_exec")
    assert env.type == EventType.STEP_COMPLETED.value
    assert env.session_id == "sess_exec"
    assert env.correlation_id == "op_exec_1"
    assert env.payload["step_order"] == 1


def test_runtime_service_ordered_events_and_correlation_gate():
    """Valida o Gate da Fase 2: eventos ordenados com correlation_id consistente e sem fakes."""
    service = DesktopRuntimeService()
    session_id = "sess_gate_phase2"
    correlation_id = "op_gate_phase2_42"

    events = service.process_message(
        text="/status",
        session_id=session_id,
        correlation_id=correlation_id,
    )

    assert len(events) >= 2
    # 1. message.accepted
    assert events[0].type == EventType.MESSAGE_ACCEPTED.value
    # Ultimo: response.final
    assert events[-1].type == EventType.RESPONSE_FINAL.value

    # Todos os eventos da operacao compartilham rigorosamente o mesmo correlation_id
    for evt in events:
        assert evt.correlation_id == correlation_id
        assert evt.session_id == session_id
        assert evt.protocol == 1
        assert evt.timestamp != ""

    # Validar que eventos foram persistidos ordenados no buffer do stream
    stream_events = service.event_stream.get_recent(limit=10, correlation_id=correlation_id)
    assert len(stream_events) == len(events)
    for expected, actual in zip(events, stream_events):
        assert expected.id == actual.id
        assert expected.type == actual.type
