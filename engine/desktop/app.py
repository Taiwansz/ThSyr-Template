"""
ThSyr Desktop FastAPI & WebSocket Local Bridge
Servidor HTTP/WebSocket exclusivamente em loopback (127.0.0.1) com autenticacao
por token efemero, streaming de eventos e despacho de comandos (Fase 3 / 02_RUNTIME_AND_EVENTS.md).
"""

from __future__ import annotations

import asyncio
import json
from contextlib import asynccontextmanager
from typing import Any, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Security, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..config import setup_logger
from .protocol import (
    CommandGoalPayload,
    CommandMessagePayload,
    CommandType,
    EventType,
    ProtocolEnvelope,
)
from .runtime_service import DesktopRuntimeService
from .security import ALLOWED_ORIGINS, MAX_PAYLOAD_BYTES, DesktopSecurityManager

logger = setup_logger("desktop_app")

bearer_scheme = HTTPBearer(auto_error=False)


def create_desktop_app(
    runtime_service: Optional[DesktopRuntimeService] = None,
    security_manager: Optional[DesktopSecurityManager] = None,
) -> FastAPI:
    service = runtime_service or DesktopRuntimeService()
    security = security_manager or DesktopSecurityManager()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("ThSyr Desktop Bridge iniciando em 127.0.0.1...")
        # Emitir runtime.ready no stream
        ready_evt = ProtocolEnvelope(
            type=EventType.RUNTIME_READY.value,
            session_id="system",
            correlation_id="boot",
            payload={"status": "READY", "runtime_version": "0.4.0"},
        )
        service.event_stream.publish(ready_evt)
        yield
        logger.info("ThSyr Desktop Bridge encerrando...")
        stopping_evt = ProtocolEnvelope(
            type=EventType.RUNTIME_STOPPING.value,
            session_id="system",
            correlation_id="shutdown",
            payload={"status": "STOPPING"},
        )
        service.event_stream.publish(stopping_evt)
        service.session_registry.clear()

    app = FastAPI(
        title="ThSyr Desktop Control Center Bridge",
        version="0.4.0",
        lifespan=lifespan,
    )

    # Restringir CORS estritamente a origens autorizadas locais
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(ALLOWED_ORIGINS),
        allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Dependencia de autenticacao para endpoints HTTP
    async def verify_auth(credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme)) -> None:
        token = credentials.credentials if credentials else None
        if not security.validate_token(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de autenticacao invalido ou ausente.",
            )

    @app.get("/health")
    async def health() -> dict[str, Any]:
        """Endpoint publico de prontidao/health check para o Tauri bootstrap."""
        return {
            "status": "ok",
            "runtime": "ready",
            "protocol": 1,
            "version": "0.4.0",
        }

    @app.get("/status", dependencies=[Depends(verify_auth)])
    async def get_status() -> dict[str, Any]:
        """Retorna telemetria e estado estruturado do nucleo cognitivo."""
        return service.get_status().to_dict()

    @app.get("/graph", dependencies=[Depends(verify_auth)])
    async def get_graph(force_refresh: bool = False) -> dict[str, Any]:
        """Retorna o grafo neural 3D do ThSyr com coordenadas normalizadas."""
        return service.get_graph(force_refresh=force_refresh).to_dict()

    @app.websocket("/ws")
    async def websocket_endpoint(
        websocket: WebSocket,
        token: Optional[str] = Query(None),
    ):
        # 1. Validar Origem
        origin = websocket.headers.get("origin")
        if not security.validate_origin(origin):
            logger.warning(f"Conexao WebSocket rejeitada: origem invalida '{origin}'")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # 2. Validar Token (via Query ou Header)
        auth_header = websocket.headers.get("authorization")
        candidate_token = token or (auth_header[7:].strip() if auth_header and auth_header.lower().startswith("bearer ") else auth_header)

        if not security.validate_token(candidate_token):
            logger.warning("Conexao WebSocket rejeitada: token invalido ou ausente")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        await websocket.accept()
        logger.info("Cliente Desktop conectado via WebSocket autenticado.")

        # Fila assincrona para transmitir eventos do stream para o socket
        loop = asyncio.get_running_loop()
        ws_queue: asyncio.Queue[ProtocolEnvelope] = asyncio.Queue()

        def stream_listener(envelope: ProtocolEnvelope):
            loop.call_soon_threadsafe(ws_queue.put_nowait, envelope)

        service.event_stream.subscribe(stream_listener)

        # Enviar frame inicial runtime.ready conforme especificacao
        status_dto = service.get_status()
        initial_ready = ProtocolEnvelope(
            type=EventType.RUNTIME_READY.value,
            session_id="default",
            correlation_id="init",
            payload=status_dto.to_dict(),
        )
        await websocket.send_text(json.dumps(initial_ready.to_dict(), ensure_ascii=False))

        # Tarefa de envio de eventos do stream para o cliente
        async def send_events():
            try:
                while True:
                    env = await ws_queue.get()
                    await websocket.send_text(json.dumps(env.to_dict(), ensure_ascii=False))
            except (asyncio.CancelledError, WebSocketDisconnect):
                pass
            except Exception as e:
                logger.warning(f"Erro no envio WebSocket: {e}")

        send_task = asyncio.create_task(send_events())

        try:
            while True:
                raw_text = await websocket.receive_text()
                if len(raw_text.encode("utf-8")) > MAX_PAYLOAD_BYTES:
                    err_env = ProtocolEnvelope(
                        type=EventType.RESPONSE_ERROR.value,
                        session_id="system",
                        correlation_id="error",
                        payload={"error": f"Payload excede o limite permitido de {MAX_PAYLOAD_BYTES} bytes."},
                    )
                    await websocket.send_text(json.dumps(err_env.to_dict(), ensure_ascii=False))
                    continue

                try:
                    frame = json.loads(raw_text)
                    envelope = ProtocolEnvelope.from_dict(frame)
                except Exception as e:
                    err_env = ProtocolEnvelope(
                        type=EventType.RESPONSE_ERROR.value,
                        session_id="system",
                        correlation_id="error",
                        payload={"error": f"Payload malformado: {e}"},
                    )
                    await websocket.send_text(json.dumps(err_env.to_dict(), ensure_ascii=False))
                    continue

                # Processar comandos recebidos
                cmd_type = envelope.type
                sid = envelope.session_id
                cid = envelope.correlation_id

                if cmd_type == CommandType.COMMAND_MESSAGE.value:
                    try:
                        msg_payload = CommandMessagePayload.from_dict(envelope.payload)
                        # Executar de forma concorrente fora da thread do loop
                        await asyncio.to_thread(service.process_message, msg_payload.text, sid, cid)
                    except Exception as e:
                        err_env = ProtocolEnvelope(
                            type=EventType.RESPONSE_ERROR.value,
                            session_id=sid,
                            correlation_id=cid,
                            payload={"error": str(e)},
                        )
                        service.event_stream.publish(err_env)

                elif cmd_type == CommandType.COMMAND_GOAL.value:
                    try:
                        goal_payload = CommandGoalPayload.from_dict(envelope.payload)
                        await asyncio.to_thread(service.run_goal, goal_payload, sid, cid)
                    except Exception as e:
                        err_env = ProtocolEnvelope(
                            type=EventType.TASK_FAILED.value,
                            session_id=sid,
                            correlation_id=cid,
                            payload={"error": str(e)},
                        )
                        service.event_stream.publish(err_env)

                elif cmd_type == CommandType.COMMAND_CANCEL.value:
                    cancel_evt = service.cancel_operation(sid, cid)
                    service.event_stream.publish(cancel_evt)

                elif cmd_type == CommandType.COMMAND_STATUS.value:
                    st = service.get_status()
                    st_env = ProtocolEnvelope(
                        type="status.snapshot",
                        session_id=sid,
                        correlation_id=cid,
                        payload=st.to_dict(),
                    )
                    service.event_stream.publish(st_env)

                else:
                    logger.info(f"Comando generico ou pass-through recebido: {cmd_type}")

        except WebSocketDisconnect:
            logger.info("Cliente Desktop desconectou do WebSocket.")
        finally:
            send_task.cancel()
            service.event_stream.unsubscribe(stream_listener)

    # Armazenar referencias de runtime no app para conveniencia
    app.state.runtime_service = service
    app.state.security_manager = security
    return app
