"""
ThSyr Interaction Layer - Session Orchestrator
Orquestra o loop conversacional e operacional do Syr no terminal,
garantindo persistencia de contexto, resolucao de referencias e desacoplamento.
"""

from typing import Any, Optional

from ..cognitive_router import CognitiveRouter
from ..config import setup_logger
from ..executive import ExecutiveRunner
from .approval_ui import ApprovalUI
from .command_router import CommandRouter
from .context_budget import ContextBudgetManager
from .conversation_state import ConversationState
from .interaction_events import EventBroadcaster
from .interaction_profile import InteractionProfile
from .interruption import InterruptionController
from .metrics import InteractionMetricsCollector
from .personality import SyrPersonalityEngine
from .presentation import BasePresentationAdapter, TerminalAdapter
from .reference_resolver import ReferenceResolver
from .response_engine import ResponseEngine
from .response_models import ResponseKind, StructuredResponse
from .response_policy import ResponsePolicy
from .terminal_renderer import TerminalRenderer
from .verbosity import VerbosityManager

logger = setup_logger("interaction_session")


class SyrConversationSession:
    def __init__(
        self,
        router: Optional[CognitiveRouter] = None,
        runner: Optional[ExecutiveRunner] = None,
        adapter: Optional[BasePresentationAdapter] = None,
        state: Optional[ConversationState] = None,
        profile: Optional[InteractionProfile] = None,
    ):
        self.router = router or CognitiveRouter()
        self.runner = runner or ExecutiveRunner(router=self.router)
        self.state = state or ConversationState()
        self.state.load_handoff()  # Restaura contexto anterior se existir

        self.profile = profile or InteractionProfile.load()
        self.verbosity = VerbosityManager()
        self.renderer = TerminalRenderer()
        self.personality = SyrPersonalityEngine()
        self.policy = ResponsePolicy(progressive_disclosure=True)

        self.response_engine = ResponseEngine(
            personality=self.personality,
            policy=self.policy,
            verbosity=self.verbosity,
            profile=self.profile,
            state=self.state,
        )

        self.resolver = ReferenceResolver(
            registry=self.state.object_registry,
            state=self.state,
        )

        self.command_router = CommandRouter(
            state=self.state,
            renderer=self.renderer,
            verbosity=self.verbosity,
            reference_resolver=self.resolver,
        )

        self.budget_manager = ContextBudgetManager()
        self.broadcaster = EventBroadcaster()
        self.interruption = InterruptionController()
        self.approval_ui = ApprovalUI()
        self.metrics = InteractionMetricsCollector()

        self.adapter = adapter or TerminalAdapter(renderer=self.renderer)

    def process_turn(self, user_input: str) -> StructuredResponse:
        """Processa um turno de entrada do operador e retorna o StructuredResponse correspondente."""
        raw_input = user_input.strip()
        if not raw_input:
            return StructuredResponse(summary="", answer="", kind=ResponseKind.CHAT)

        # 1. Verificar comandos universais e aliases de barra
        if self.command_router.is_command(raw_input):
            cmd_resp = self.command_router.handle(raw_input)
            if cmd_resp:
                self.metrics.record_command(raw_input.split()[0].lower())
                self.state.add_message("user", raw_input)
                self.state.add_message("assistant", cmd_resp.answer)
                self.state.last_response = cmd_resp
                self.state.save_handoff()
                return cmd_resp

        # 2. Resolucao contextual de referencias e intencoes
        resolution = self.resolver.resolve(raw_input)
        if resolution.resolved:
            if resolution.intent == "CONSTRAINT_EXCLUDE" and resolution.extracted_param:
                entity = resolution.extracted_param
                self.interruption.add_excluded_entity(entity)
                resp = StructuredResponse(
                    summary=f"Restricao registrada: '{entity}' fora do plano.",
                    answer=f"Entendido. '{entity}' sera mantido intacto e excluido de qualquer acao.",
                    kind=ResponseKind.OPERATIONAL,
                )
                self.state.add_message("user", raw_input)
                self.state.add_message("assistant", resp.answer)
                self.state.save_handoff()
                return resp

            elif resolution.intent == "REVERT_OR_REJECT":
                self.state.record_rejection(
                    solution_id=self.state.active_plan or "last_action",
                    description="Rejeitado pelo operador",
                    reason=raw_input,
                )
                resp = StructuredResponse(
                    summary="Acao desfeita ou rejeitada.",
                    answer="Solucao anterior descartada. Registrei a rejeicao no historico para nao repetir essa abordagem.",
                    kind=ResponseKind.OPERATIONAL,
                )
                self.state.add_message("user", raw_input)
                self.state.add_message("assistant", resp.answer)
                self.state.save_handoff()
                return resp

            elif resolution.intent == "SELECT_OPTION" and resolution.target_object:
                opt = resolution.target_object
                # Tratar como selecao da alternativa
                raw_input = f"Executar opcao {opt.shortcut}: {opt.value}"

        # 3. Processamento cognitivo normal
        self.state.add_message("user", raw_input)

        # Atualizar sujeito ativo caso identificado
        self._detect_and_update_subject(raw_input)

        # Geracao via CognitiveRouter
        try:
            gen_res = self.router.think_and_generate(
                raw_input,
                conversation_state=self.state,
            )
            raw_answer = gen_res["response"]
            meta = {
                "model": gen_res.get("model"),
                "provider": gen_res.get("provider"),
                "tier": gen_res.get("tier"),
                "tokens": gen_res.get("telemetry", {}).get("total_tokens"),
            }
            evidence: list[dict[str, Any]] = []
            if "retrieved" in gen_res.get("route", {}):
                sources = [
                    {
                        "kind": "retrieved",
                        "identifier": r.get("title", "Memoria"),
                        "description": r.get("item", {}).get("title", ""),
                        "location": r.get("item", {}).get("filepath"),
                    }
                    for r in gen_res["route"]["retrieved"][:3]
                ]
            else:
                sources = []

            structured = self.response_engine.process_raw_generation(
                raw_text=raw_answer,
                user_query=raw_input,
                kind=ResponseKind.CHAT,
                evidence=evidence,
                sources=sources,
                metadata=meta,
            )

        except Exception as e:
            logger.error(f"Erro durante processamento cognitivo: {e}")
            structured = StructuredResponse(
                summary="Falha no motor de inferencia.",
                answer=f"Nao foi possivel concluir o raciocinio devido a uma falha de execucao: {str(e)[:150]}.",
                kind=ResponseKind.ERROR,
                details=str(e),
            )

        self.state.add_message("assistant", structured.answer)
        self.metrics.record_turn(structured.answer)
        self.state.save_handoff()
        return structured

    def _detect_and_update_subject(self, text: str) -> None:
        lower = text.lower()
        if "toklang" in lower:
            self.state.set_active_context(subject="TokLang", project="TokLang")
        elif "daemon" in lower:
            self.state.set_active_context(subject="Daemon Supervisor", project="ThSyr")
        elif "ci" in lower or "github actions" in lower:
            self.state.set_active_context(subject="CI Gates", project="ThSyr")

    def run_interactive_loop(self) -> None:
        """Loop conversacional persistente no terminal."""
        welcome_info = self.state.get_git_revision()
        active_goal = self.state.active_goal or "Nenhuma"
        print("==================================================")
        print("               THSYR // SYR INTERFACE             ")
        print("==================================================")
        print(f"Versao:      0.4.0 | Git: {welcome_info}")
        print(f"Meta Ativa:  {active_goal}")
        print("Digite comandos (/help, /status, /v, etc.) ou converse diretamente.")
        print("Para sair, use /cancel ou Ctrl+C.")
        print("==================================================\n")

        while True:
            try:
                user_input = self.adapter.prompt_user("Operador › ")
                if not user_input or user_input.strip() in ("/exit", "/quit", "sair"):
                    print("\nSyr › Encerrando sessao interativa. Estado preservado em handoff.")
                    break
                if user_input.strip() == "/cancel":
                    print("\nSyr › Interrupcao recebida.")
                    continue

                resp = self.process_turn(user_input)
                self.adapter.display_response(resp)

            except (KeyboardInterrupt, EOFError):
                print("\nSyr › Sessao encerrada pelo operador.")
                break
