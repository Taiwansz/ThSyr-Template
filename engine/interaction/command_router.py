"""
ThSyr Interaction Layer - Command Router
Roteia comandos universais (/help, /status, /why, /details, /source, /evidence,
/plan, /changes, /diff, /undo, /v, /context, /tools) e aliases naturais.
"""

from typing import Any, Optional

from .conversation_state import ConversationState
from .reference_resolver import ReferenceResolver
from .response_models import ResponseKind, StructuredResponse
from .terminal_renderer import TerminalRenderer
from .verbosity import VerbosityManager


class CommandRouter:
    def __init__(
        self,
        state: ConversationState,
        renderer: TerminalRenderer,
        verbosity: VerbosityManager,
        reference_resolver: ReferenceResolver,
    ):
        self.state = state
        self.renderer = renderer
        self.verbosity = verbosity
        self.resolver = reference_resolver

    def is_command(self, user_input: str) -> bool:
        cleaned = user_input.strip().lower()
        if cleaned.startswith("/"):
            return True
        # Aliases naturais para comandos conhecidos
        natural_aliases = {
            "detalhes",
            "por que",
            "por que?",
            "por quê",
            "por quê?",
            "fonte",
            "fontes",
            "evidencias",
            "evidências",
            "mudancas",
            "mudanças",
            "status",
            "plano",
            "ajuda",
            "help",
            "desfaz",
            "volta",
            "cancela",
        }
        if cleaned in natural_aliases:
            return True
        # Atalho numerico puro quando ha opcoes ativas
        if cleaned.isdigit() and self.state.object_registry.get_by_shortcut(cleaned):
            return True
        return False

    def handle(self, user_input: str, executor: Optional[Any] = None) -> Optional[StructuredResponse]:
        raw = user_input.strip()
        lower = raw.lower()

        # 1. Normalizacao de aliases naturais para comandos de barra
        cmd = self._normalize_command(lower)
        parts = cmd.split()
        root = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        if root in ("/help", "/ajuda"):
            return self._cmd_help()
        elif root == "/status":
            return self._cmd_status()
        elif root == "/details":
            return self._cmd_details()
        elif root in ("/why", "/por-que"):
            return self._cmd_why()
        elif root in ("/source", "/fonte", "/fontes"):
            return self._cmd_source()
        elif root in ("/evidence", "/evidencia", "/evidencias"):
            return self._cmd_evidence()
        elif root == "/plan":
            return self._cmd_plan()
        elif root in ("/changes", "/mudancas"):
            return self._cmd_changes()
        elif root == "/diff":
            return self._cmd_diff()
        elif root in ("/undo", "/desfaz"):
            return self._cmd_undo()
        elif root == "/v":
            return self._cmd_verbosity(args)
        elif root == "/context":
            return self._cmd_context()
        elif root == "/tools":
            return self._cmd_tools()
        elif root == "/clear-view":
            return self._cmd_clear_view()
        elif root in ("/cancel", "/cancela"):
            return StructuredResponse(
                summary="Operacao cancelada.",
                answer="Acao ou processo atual foi cancelado por ordem do operador.",
                kind=ResponseKind.OPERATIONAL,
            )

        # 2. Atalho numerico puro (1, 2, 3...)
        if raw.isdigit():
            obj = self.state.object_registry.get_by_shortcut(raw)
            if obj:
                return StructuredResponse(
                    summary=f"Opcao selecionada: {obj.label}",
                    answer=f"Executando alternativa [{obj.shortcut}] {obj.label}: {obj.value}",
                    kind=ResponseKind.OPERATIONAL,
                    actions=[{"id": "confirm", "label": "Prosseguir", "command": str(obj.value), "shortcut": "sim"}],
                )

        return None

    def _normalize_command(self, text: str) -> str:
        t = text.strip()
        if t in ("detalhes",):
            return "/details"
        if t in ("por que", "por que?", "por quê", "por quê?"):
            return "/why"
        if t in ("fonte", "fontes"):
            return "/source"
        if t in ("evidencia", "evidencias", "evidência", "evidências"):
            return "/evidence"
        if t in ("mudanca", "mudancas", "mudança", "mudanças"):
            return "/changes"
        if t in ("plano",):
            return "/plan"
        if t in ("status",):
            return "/status"
        if t in ("ajuda", "help"):
            return "/help"
        if t in ("desfaz", "volta"):
            return "/undo"
        if t in ("cancela",):
            return "/cancel"
        return t

    def _cmd_help(self) -> StructuredResponse:
        content = (
            "Comandos Universais do Syr:\n"
            "  /details      - Expande analise tecnica e detalhes da ultima resposta\n"
            "  /why          - Explica a causa e fatores que levaram a decisao\n"
            "  /evidence     - Exibe hashes criptograficos, exit codes e diffs\n"
            "  /source       - Exibe fontes e proveniencia de informacoes\n"
            "  /status       - Linha de status operacional do ambiente\n"
            "  /context      - Sujeito, projeto e arquivos em foco\n"
            "  /plan         - Exibe o plano ativo de execucao\n"
            "  /changes      - Exibe arquivos modificados no workspace\n"
            "  /diff         - Mostra o diff de alteracoes locais\n"
            "  /undo         - Reverte a ultima alteracao reversivel\n"
            "  /v <1-5>      - Ajusta verbosidade (1: compacto, 3: normal, 5: deep)\n"
            "  /tools        - Lista ferramentas operacionais disponiveis\n"
            "  /clear-view   - Limpa a tela do terminal"
        )
        return StructuredResponse(
            summary="Comandos disponiveis exibidos.",
            answer=content,
            kind=ResponseKind.OPERATIONAL,
        )

    def _cmd_status(self) -> StructuredResponse:
        rev = self.state.get_git_revision()
        active_goal = self.state.active_goal or "Nenhuma meta ativa"
        active_proj = self.state.active_project or "ThSyr"
        summary = f"ThSyr v0.4.0 | git:{rev} | proj:{active_proj} | meta:{active_goal}"
        return StructuredResponse(
            summary=summary,
            answer=f"Ambiente operacional ativo.\nGit: {rev}\nProjeto: {active_proj}\nMeta: {active_goal}\nVerbosidade: {self.verbosity.current_level.name}",
            kind=ResponseKind.OPERATIONAL,
        )

    def _cmd_details(self) -> StructuredResponse:
        last = self.state.last_response
        if not last or not last.has_details():
            return StructuredResponse(
                summary="Sem detalhes.",
                answer="Nenhum detalhe adicional registrado para a resposta anterior.",
                kind=ResponseKind.OPERATIONAL,
            )
        return StructuredResponse(
            summary="Detalhes expandidos.",
            answer=last.details or "",
            kind=ResponseKind.ANALYSIS,
        )

    def _cmd_why(self) -> StructuredResponse:
        last = self.state.last_response
        if not last:
            return StructuredResponse(
                summary="Sem contexto anterior.",
                answer="Nenhuma decisao recente registrada nesta sessao para justificar.",
                kind=ResponseKind.OPERATIONAL,
            )
        reason = last.metadata.get("reasoning_summary")
        if not reason and last.sources:
            reason = f"Conclusao baseada em {len(last.sources)} fontes mapeadas e evidencias fisicas."
        elif not reason:
            reason = f"Decisao estruturada derivada do objetivo ativo '{self.state.active_goal or 'geral'}': {last.summary}"

        return StructuredResponse(
            summary=f"Fator determinante: {reason}",
            answer=f"Justificativa operacional: {reason}",
            kind=ResponseKind.ANALYSIS,
            sources=last.sources,
        )

    def _cmd_source(self) -> StructuredResponse:
        last = self.state.last_response
        if not last or not last.has_sources():
            return StructuredResponse(
                summary="Sem fontes estruturadas.",
                answer="A resposta anterior nao registrou fontes documentais ou conceituais especificas.",
                kind=ResponseKind.OPERATIONAL,
            )
        rendered = self.renderer.render_sources(last)
        return StructuredResponse(
            summary=f"{len(last.sources)} fontes encontradas.",
            answer=rendered,
            kind=ResponseKind.OPERATIONAL,
            sources=last.sources,
        )

    def _cmd_evidence(self) -> StructuredResponse:
        last = self.state.last_response
        if not last or not last.has_evidence():
            return StructuredResponse(
                summary="Sem evidencias fisicas.",
                answer="Nenhuma evidencia fisica (exit code, hash, snapshot) registrada na resposta anterior.",
                kind=ResponseKind.OPERATIONAL,
            )
        rendered = self.renderer.render_evidence(last)
        return StructuredResponse(
            summary=f"{len(last.evidence)} evidencias registradas.",
            answer=rendered,
            kind=ResponseKind.OPERATIONAL,
            evidence=last.evidence,
        )

    def _cmd_plan(self) -> StructuredResponse:
        plan_id = self.state.active_plan
        if not plan_id:
            return StructuredResponse(
                summary="Nenhum plano ativo.",
                answer="Nao ha nenhum plano de execucao em andamento no momento.",
                kind=ResponseKind.OPERATIONAL,
            )
        return StructuredResponse(
            summary=f"Plano ativo: {plan_id}",
            answer=f"Plano operacional {plan_id} em execucao.",
            kind=ResponseKind.OPERATIONAL,
        )

    def _cmd_changes(self) -> StructuredResponse:
        last = self.state.last_response
        if not last or not last.has_changes():
            return StructuredResponse(
                summary="Nenhuma mudanca registrada.",
                answer="Nenhum arquivo modificado ou criado na ultima acao.",
                kind=ResponseKind.OPERATIONAL,
            )
        rendered = self.renderer.render_changes(last)
        return StructuredResponse(
            summary=f"{len(last.changes)} arquivos modificados.",
            answer=rendered,
            kind=ResponseKind.OPERATIONAL,
            changes=last.changes,
        )

    def _cmd_diff(self) -> StructuredResponse:
        import subprocess
        try:
            res = subprocess.run(["git", "diff", "--stat"], capture_output=True, text=True, check=False)
            diff_text = res.stdout.strip() or "Nenhuma diferenca no working tree."
        except Exception as e:
            diff_text = f"Erro ao obter diff: {e}"
        return StructuredResponse(
            summary="Diff do workspace local.",
            answer=diff_text,
            kind=ResponseKind.OPERATIONAL,
        )

    def _cmd_undo(self) -> StructuredResponse:
        return StructuredResponse(
            summary="Undo acionado.",
            answer="Reversao de alteracoes locais nao commitadas suportada via git restore.",
            kind=ResponseKind.OPERATIONAL,
            actions=[{"id": "confirm_undo", "label": "Confirmar git restore .", "command": "git restore .", "shortcut": "sim"}],
        )

    def _cmd_verbosity(self, args: list[str]) -> StructuredResponse:
        if not args:
            return StructuredResponse(
                summary=f"Nivel de verbosidade: {self.verbosity.current_level.name}",
                answer=f"Modo atual: {self.verbosity.current_level.name} (Nivel {int(self.verbosity.current_level)}). Use '/v <1-5>' para alterar.",
                kind=ResponseKind.OPERATIONAL,
            )
        new_level = self.verbosity.set_global_level(args[0])
        return StructuredResponse(
            summary=f"Verbosidade alterada para {new_level.name}.",
            answer=f"Novo nivel de comunicacao: {new_level.name} ({int(new_level)}/5).",
            kind=ResponseKind.OPERATIONAL,
        )

    def _cmd_context(self) -> StructuredResponse:
        info = (
            f"Contexto Operacional Ativo:\n"
            f"  Sujeito:  {self.state.active_subject or 'Nenhum'}\n"
            f"  Projeto:  {self.state.active_project or 'ThSyr'}\n"
            f"  Meta:     {self.state.active_goal or 'Nenhuma'}\n"
            f"  Arquivo:  {self.state.active_file or 'Nenhum'}\n"
            f"  Plano:    {self.state.active_plan or 'Nenhum'}\n"
            f"  Turno:    {self.state.turn_count}"
        )
        return StructuredResponse(
            summary="Contexto ativo exibido.",
            answer=info,
            kind=ResponseKind.OPERATIONAL,
        )

    def _cmd_tools(self) -> StructuredResponse:
        return StructuredResponse(
            summary="Tool Bus operacional.",
            answer="Ferramentas registradas: filesystem, git, shell, memory, unreal, codenotch.",
            kind=ResponseKind.OPERATIONAL,
        )

    def _cmd_clear_view(self) -> StructuredResponse:
        import os
        os.system("cls" if os.name == "nt" else "clear")
        return StructuredResponse(
            summary="Tela limpa.",
            answer="",
            kind=ResponseKind.OPERATIONAL,
        )
