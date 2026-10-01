"""
Testes unitarios e de integracao para o DesktopRuntimeService e DesktopSessionRegistry.
Valida equivalencia de resposta entre CLI e Desktop e integracao real com o core.
"""

from engine.desktop.protocol import EventType
from engine.desktop.runtime_service import DesktopRuntimeService
from engine.desktop.session_registry import DesktopSessionRegistry
from engine.interaction.conversation_state import ConversationState
from engine.interaction.session_orchestrator import SyrConversationSession


def test_session_registry_lifecycle():
    registry = DesktopSessionRegistry()
    sess1 = registry.get_or_create("sess_test_1")
    assert isinstance(sess1, SyrConversationSession)
    assert sess1.state.session_id == "sess_test_1"

    # Reobter mesma instancia
    sess1_again = registry.get_or_create("sess_test_1")
    assert sess1 is sess1_again

    assert "sess_test_1" in registry.list_active()

    # Fechar sessao
    closed = registry.close("sess_test_1")
    assert closed is True
    assert "sess_test_1" not in registry.list_active()


def test_runtime_service_status():
    service = DesktopRuntimeService()
    status = service.get_status()
    assert status.status == "READY"
    assert status.runtime_version == "0.4.0"
    assert status.total_nodes > 0


def test_runtime_service_process_message_equivalence():
    """Valida que o RuntimeService chama o mesmo core que o SyrConversationSession."""
    session_id = "test_equivalence_sess"
    service = DesktopRuntimeService()

    # Interceptar eventos emitidos no sink
    emitted_events = []
    service.event_sink = lambda evt: emitted_events.append(evt)

    query = "/help"
    events = service.process_message(text=query, session_id=session_id)

    assert len(events) >= 2  # message.accepted e response.final
    assert events[0].type == EventType.MESSAGE_ACCEPTED.value
    assert events[-1].type == EventType.RESPONSE_FINAL.value

    final_payload = events[-1].payload
    assert "Comandos Universais do Syr" in final_payload["answer"] or "help" in final_payload["answer"].lower()

    # Comparar com chamada direta ao SyrConversationSession
    direct_session = SyrConversationSession(state=ConversationState(session_id="direct_test"))
    direct_response = direct_session.process_turn(query)

    # Ambos usam o mesmo CommandRouter e produzem a mesma resposta
    assert final_payload["answer"] == direct_response.answer


def test_runtime_service_cancel_operation():
    service = DesktopRuntimeService()
    evt = service.cancel_operation(session_id="sess_cancel", correlation_id="op_cancel_1")
    assert evt.type == EventType.OPERATION_CANCEL_UNSUPPORTED.value
    assert evt.correlation_id == "op_cancel_1"
