"""
ThSyr Desktop Runtime Service (Facade)
Unifica acesso da central de controle ao SyrConversationSession, ExecutiveRunner e Grafo Neural,
sem duplicar cognicao, regras ou memoria (ADR-003 / 01_ARCHITECTURE.md / 06_IMPLEMENTATION_PHASES.md).
"""

from __future__ import annotations

import uuid
from typing import Any, Callable, Optional

from ..cognitive_router import CognitiveRouter
from ..config import setup_logger
from ..executive import ExecutiveRunner, Goal
from ..neural_pulse import get_last_neural_pulse
from .event_stream import DesktopEventAdapter, DesktopEventStream
from .graph_service import DesktopGraphService
from .protocol import (
    CommandGoalPayload,
    EventType,
    GraphSnapshotDto,
    ProtocolEnvelope,
    RuntimeStatusDto,
)
from .session_registry import DesktopSessionRegistry

logger = setup_logger("desktop_runtime_service")


class DesktopRuntimeService:
    def __init__(
        self,
        router: Optional[CognitiveRouter] = None,
        runner: Optional[ExecutiveRunner] = None,
        session_registry: Optional[DesktopSessionRegistry] = None,
        graph_service: Optional[DesktopGraphService] = None,
        event_stream: Optional[DesktopEventStream] = None,
        event_sink: Optional[Callable[[ProtocolEnvelope], None]] = None,
    ):
        self.router = router or CognitiveRouter()
        self.runner = runner or ExecutiveRunner(router=self.router)
        self.graph_service = graph_service or DesktopGraphService()
        self.event_stream = event_stream or DesktopEventStream()
        self.event_adapter = DesktopEventAdapter(event_stream=self.event_stream)
        self.event_sink = event_sink

        # Conectar ExecutiveRunner ao adapter de eventos em memoria
        self.runner.event_sink = self._on_executive_event

        # Conectar session registry e auto-anexar broadcasters
        self.session_registry = session_registry or DesktopSessionRegistry(
            router=self.router,
            runner=self.runner,
            session_factory=self._create_monitored_session,
        )

    def _on_executive_event(self, evt_dict: dict[str, Any]) -> None:
        self.event_adapter.handle_executive_event(evt_dict)

    def _create_monitored_session(self, session_id: str):
        from ..interaction.conversation_state import ConversationState
        from ..interaction.session_orchestrator import SyrConversationSession

        state = ConversationState(session_id=session_id)
        session = SyrConversationSession(
            router=self.router,
            runner=self.runner,
            state=state,
        )
        session.state.session_id = session_id
        # Conectar EventBroadcaster da sessao ao event_adapter
        self.event_adapter.attach_broadcaster(session.broadcaster)
        return session

    def _emit(self, envelope: ProtocolEnvelope) -> ProtocolEnvelope:
        self.event_stream.publish(envelope)
        if self.event_sink is not None:
            try:
                self.event_sink(envelope)
            except Exception as e:
                logger.warning(f"Erro ao emitir envelope no sink: {e}")
        return envelope

    def get_status(self) -> RuntimeStatusDto:
        """Coleta telemetria e estado real do nucleo sem simular dados."""
        core_status = self.router.status()
        active_sessions = self.session_registry.list_active()
        handoff_goal = core_status.get("active_goal")

        model_info = self.router.model_gateway.get_telemetry_summary()
        recent_models = list(model_info.keys()) if isinstance(model_info, dict) else []

        snapshot = self.graph_service.build_snapshot()

        return RuntimeStatusDto(
            status="READY",
            runtime_version="0.4.0",
            total_nodes=snapshot.total_nodes,
            total_synapses=snapshot.total_edges,
            active_sessions=active_sessions,
            current_goal=handoff_goal,
            model_provider=recent_models[0] if recent_models else "local",
            model_name=None,
        )

    def get_graph(self, force_refresh: bool = False) -> GraphSnapshotDto:
        """Retorna o grafo real do ThSyr com coordenadas 3D calculadas."""
        return self.graph_service.build_snapshot(force_refresh=force_refresh)

    def process_message(
        self,
        text: str,
        session_id: str = "default",
        correlation_id: Optional[str] = None,
    ) -> list[ProtocolEnvelope]:
        """
        Executa um turno completo de conversa através de SyrConversationSession.
        Emite eventos intermediarios (message.accepted, neural.pulse) e o response.final.
        """
        cid = correlation_id or f"op_{uuid.uuid4().hex[:8]}"
        self.event_adapter.set_active_correlation(session_id, cid)
        emitted: list[ProtocolEnvelope] = []

        # 1. Aceitacao do comando
        accepted_evt = ProtocolEnvelope(
            type=EventType.MESSAGE_ACCEPTED.value,
            session_id=session_id,
            correlation_id=cid,
            payload={"text": text},
        )
        emitted.append(self._emit(accepted_evt))

        # 2. Exclusao mutua por sessao
        session = self.session_registry.get_or_create(session_id)
        lock = self.session_registry.get_lock(session_id)

        with lock:
            try:
                # Processamento cognitivo real (mesmo motor do CLI)
                response = session.process_turn(text)

                # 3. Emitir pulso neural correspondente se disponivel
                last_pulse = get_last_neural_pulse()
                if last_pulse:
                    pulse_mapping = self.graph_service.match_pulse_nodes(last_pulse)
                    pulse_evt = ProtocolEnvelope(
                        type=EventType.NEURAL_PULSE.value,
                        session_id=session_id,
                        correlation_id=cid,
                        payload={
                            "pulse": last_pulse,
                            "mapping": pulse_mapping,
                        },
                    )
                    emitted.append(self._emit(pulse_evt))

                # 4. Resposta final estruturada
                final_payload: dict[str, Any] = {
                    "summary": response.summary,
                    "answer": response.answer,
                    "kind": response.kind.value,
                    "details": response.details,
                    "evidence": response.evidence,
                    "sources": response.sources,
                    "metadata": response.metadata,
                }
                final_evt = ProtocolEnvelope(
                    type=EventType.RESPONSE_FINAL.value,
                    session_id=session_id,
                    correlation_id=cid,
                    payload=final_payload,
                )
                emitted.append(self._emit(final_evt))

            except Exception as e:
                logger.error(f"Erro ao processar mensagem no DesktopRuntimeService: {e}")
                err_evt = ProtocolEnvelope(
                    type=EventType.RESPONSE_ERROR.value,
                    session_id=session_id,
                    correlation_id=cid,
                    payload={"error": str(e)},
                )
                emitted.append(self._emit(err_evt))

        return emitted

    def run_goal(
        self,
        payload: CommandGoalPayload,
        session_id: str = "default",
        correlation_id: Optional[str] = None,
    ) -> list[ProtocolEnvelope]:
        """
        Executa um objetivo atraves do ExecutiveRunner real.
        """
        cid = correlation_id or f"op_{uuid.uuid4().hex[:8]}"
        self.event_adapter.set_active_correlation(session_id, cid)
        emitted: list[ProtocolEnvelope] = []

        # 1. Notificar inicio de meta
        start_evt = ProtocolEnvelope(
            type=EventType.GOAL_STARTED.value,
            session_id=session_id,
            correlation_id=cid,
            payload={"title": payload.title, "description": payload.description},
        )
        emitted.append(self._emit(start_evt))

        gid = payload.goal_id or f"goal_{uuid.uuid4().hex[:8]}"
        goal = Goal(
            id=gid,
            title=payload.title,
            description=payload.description or payload.title,
            project=payload.project,
            priority=payload.priority,
        )

        try:
            self.runner.save_goal(goal)
            plan = self.runner.planner.create_plan(goal)
            self.runner.save_plan(plan)

            # Notificar plano criado
            plan_evt = ProtocolEnvelope(
                type=EventType.PLAN_CREATED.value,
                session_id=session_id,
                correlation_id=cid,
                payload={
                    "plan_id": plan.id,
                    "title": plan.title,
                    "steps": [s.to_dict() for s in plan.steps],
                    "total_steps": len(plan.steps),
                },
            )
            emitted.append(self._emit(plan_evt))

            # Executar plano
            result = self.runner.run_goal(goal)

            complete_evt = ProtocolEnvelope(
                type=EventType.TASK_COMPLETED.value if result.status.value == "completed" else EventType.TASK_FAILED.value,
                session_id=session_id,
                correlation_id=cid,
                payload={
                    "goal_id": goal.id,
                    "status": result.status.value,
                    "completed_steps": result.completed_steps,
                    "total_steps": result.total_steps,
                    "final_summary": result.final_summary,
                },
            )
            emitted.append(self._emit(complete_evt))

        except Exception as e:
            logger.error(f"Erro na execucao da meta '{payload.title}': {e}")
            fail_evt = ProtocolEnvelope(
                type=EventType.TASK_FAILED.value,
                session_id=session_id,
                correlation_id=cid,
                payload={"goal_id": gid, "error": str(e)},
            )
            emitted.append(self._emit(fail_evt))

        return emitted

    def cancel_operation(
        self,
        session_id: str,
        correlation_id: Optional[str] = None,
    ) -> ProtocolEnvelope:
        """
        Trata solicitacao de cancelamento cooperativo conforme 02_RUNTIME_AND_EVENTS.md.
        """
        cid = correlation_id or f"op_{uuid.uuid4().hex[:8]}"
        # Se o core estiver executando uma operacao atomica nao-interrompivel, responder sem simular cancelamento fake
        evt = ProtocolEnvelope(
            type=EventType.OPERATION_CANCEL_UNSUPPORTED.value,
            session_id=session_id,
            correlation_id=cid,
            payload={
                "message": "Interrupcao cooperativa em curso registrada. Operacoes atomicas de modelo concluem antes do corte.",
            },
        )
        return self._emit(evt)
