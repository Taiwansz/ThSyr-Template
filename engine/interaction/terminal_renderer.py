"""
ThSyr Interaction Layer - Terminal Renderer
Renderizador de terminal com suporte a ANSI semantico, fallback limpo para NO_COLOR,
largura dinamica e formatacao de progressive disclosure com prefixo 'Syr ›'.
"""

import os
import shutil
import sys
import textwrap
from typing import Any

from .response_models import ResponseKind, StructuredResponse


class TerminalRenderer:
    # Cores ANSI semanticas
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    CYAN = "\033[36m"
    BLUE = "\033[34m"

    def __init__(self, prefix: str = "Syr › ", stream=sys.stdout):
        self.prefix = prefix
        self.stream = stream
        self.use_color = self._should_use_color()

    def _should_use_color(self) -> bool:
        if "NO_COLOR" in os.environ or os.environ.get("TERM") == "dumb":
            return False
        return hasattr(self.stream, "isatty") and self.stream.isatty()

    def _c(self, text: str, code: str) -> str:
        return f"{code}{text}{self.RESET}" if self.use_color else text

    def get_terminal_width(self) -> int:
        try:
            return shutil.get_terminal_size(fallback=(80, 24)).columns
        except Exception:
            return 80

    def render_response(self, response: StructuredResponse) -> str:
        """Renderiza a resposta primária com progressive disclosure."""
        lines: list[str] = []
        width = min(self.get_terminal_width(), 100)

        # 1. Prefixo de cabecalho ou erro/alerta se aplicavel
        if response.kind == ResponseKind.ERROR:
            lines.append(f"{self.prefix}{self._c('FALHA OPERACIONAL', self.RED + self.BOLD)}")
        elif response.kind == ResponseKind.WARNING:
            lines.append(f"{self.prefix}{self._c('ALERTA', self.YELLOW + self.BOLD)}")

        # 2. Resposta principal
        answer = response.answer.strip()
        if answer:
            # Envelopa com prefixo Syr › na primeira linha e identacao nas seguintes
            wrapped = textwrap.fill(
                answer,
                width=width,
                initial_indent=self.prefix,
                subsequent_indent=" " * len(self.prefix),
            )
            lines.append(wrapped)

        # 3. Avisos se houver
        if response.warnings:
            for w in response.warnings:
                lines.append(f"  {self._c('!', self.YELLOW)} {w}")

        # 4. Acoes contextuais rapidas (Shortcuts)
        if response.actions:
            action_badges = []
            for act in response.actions:
                sc = act.get("shortcut") or act.get("id")
                lbl = act.get("label", "")
                badge = f"[{self._c(str(sc), self.CYAN + self.BOLD)}] {lbl}"
                action_badges.append(badge)
            lines.append(f"\n  Acoes: {'  '.join(action_badges)}")

        # 5. Indicadores de Progressive Disclosure
        disclosures = []
        if response.has_details():
            disclosures.append("/details")
        if response.has_evidence():
            disclosures.append("/evidence")
        if response.has_sources():
            disclosures.append("/source")
        if response.has_changes():
            disclosures.append("/changes")

        if disclosures:
            hint = f"  {self._c('Expandir: ' + ' | '.join(disclosures), self.DIM)}"
            lines.append(hint)

        output = "\n".join(lines)
        return output

    def render_details(self, response: StructuredResponse) -> str:
        """Renderiza a visao expandida de detalhes (/details)."""
        lines = [f"{self.prefix}{self._c('DETALHES TECNICOS', self.BOLD)}"]
        if response.details:
            lines.append(response.details.strip())
        else:
            lines.append("Nenhum detalhe adicional registrado para esta resposta.")
        return "\n".join(lines)

    def render_evidence(self, response: StructuredResponse) -> str:
        """Renderiza evidencias concretas (/evidence)."""
        lines = [f"{self.prefix}{self._c('EVIDENCIAS DE EXECUCAO', self.BOLD)}"]
        if not response.evidence:
            lines.append("Nenhuma evidencia fisica registrada.")
            return "\n".join(lines)

        for i, ev in enumerate(response.evidence, 1):
            verified = ev.get("verified", False)
            v_tag = self._c("[VERIFICADO]", self.GREEN) if verified else self._c("[PENDENTE]", self.YELLOW)
            lines.append(f"\n[{i}] {ev.get('description', 'Evidencia')} {v_tag}")
            if "exit_code" in ev:
                lines.append(f"    Exit Code:   {ev['exit_code']}")
            if "stdout_hash" in ev:
                lines.append(f"    Stdout SHA:  {ev['stdout_hash']}")
            if "diff_hash" in ev:
                lines.append(f"    Diff SHA:    {ev['diff_hash']}")
            if "file" in ev:
                lines.append(f"    Arquivo:     {ev['file']}")
        return "\n".join(lines)

    def render_sources(self, response: StructuredResponse) -> str:
        """Renderiza fontes de dados e informacoes (/source)."""
        lines = [f"{self.prefix}{self._c('FONTES E PROVENIENCIA', self.BOLD)}"]
        if not response.sources:
            lines.append("Nenhuma fonte estruturada mapeada.")
            return "\n".join(lines)

        for i, s in enumerate(response.sources, 1):
            kind = s.get("kind", "observed").upper()
            color = self.GREEN if kind == "OBSERVED" else (self.CYAN if kind == "RETRIEVED" else self.YELLOW)
            lines.append(f"[{i}] {self._c(f'[{kind}]', color)} {s.get('identifier', '')}: {s.get('description', '')}")
            if s.get("location"):
                lines.append(f"    Local: {s['location']}")
        return "\n".join(lines)

    def render_changes(self, response: StructuredResponse) -> str:
        """Renderiza arquivos afetados e alteracoes (/changes)."""
        lines = [f"{self.prefix}{self._c('MUDANCAS NO WORKSPACE', self.BOLD)}"]
        if not response.changes:
            lines.append("Nenhuma alteracao de arquivo registrada nesta operacao.")
            return "\n".join(lines)

        for c in response.changes:
            status = c.get("status", "modified").upper()
            color = self.GREEN if status in ("CREATED", "ADDED") else (self.YELLOW if status == "MODIFIED" else self.RED)
            path = c.get("path", "arquivo")
            lines.append(f"  {self._c(f'[{status}]', color)} {path}")
        return "\n".join(lines)

    def render_status_line(self, info: dict[str, Any]) -> str:
        """Renderiza linha de status compacta e nao-poluente."""
        branch = info.get("branch", "main")
        dirty = info.get("dirty", False)
        dirty_tag = self._c("MODIFICADO", self.YELLOW) if dirty else self._c("LIMPO", self.GREEN)
        goal = info.get("goal") or "Nenhum"
        step = info.get("step") or ""
        step_part = f" | {step}" if step else ""

        line = f"ThSyr v0.4.0 | git:{branch} [{dirty_tag}] | meta:{goal}{step_part}"
        return self._c(line, self.DIM)
