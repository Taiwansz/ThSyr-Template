"""
ThSyr Tool Bus - Central Registry & Dispatcher (Fase 5)
Gerencia o ciclo de vida e a execucao governada de ferramentas:
- Registro tipado com schemas e niveis de risco
- Avaliacao pelo Permission Cortex antes de cada invocacao
- Registro de auditoria operacional estruturado em state/events/
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..config import get_state_dir, setup_logger
from .adapters.filesystem import ListDirTool, ReadFileTool, WriteFileTool
from .adapters.git_tool import GitLogTool, GitStatusTool
from .adapters.logo_tool import LogoAuditTool, LogoSearchTool, LogoStatsTool
from .adapters.maps_tool import GoogleMapsSearchTool
from .adapters.memory_tool import SearchMemoryTool, WriteEpisodicMemoryTool
from .adapters.shell import ShellCommandTool
from .adapters.unreal_tool import UnrealSearchAssetsTool, UnrealStatusTool
from .base import BaseTool, ToolMetadata, ToolResult
from .permission import PermissionCortex, PermissionDecision

logger = setup_logger("tool_bus")


class ToolBus:
    def __init__(
        self,
        permission_cortex: PermissionCortex | None = None,
        state_dir: Path | None = None,
        register_defaults: bool = True
    ):
        self.permission_cortex = permission_cortex or PermissionCortex()
        self.state_dir = state_dir or get_state_dir()
        self.events_dir = self.state_dir / "events"
        self.events_dir.mkdir(parents=True, exist_ok=True)

        self._tools: dict[str, BaseTool] = {}

        if register_defaults:
            self._register_default_tools()

    def _register_default_tools(self) -> None:
        self.register(ReadFileTool())
        self.register(WriteFileTool())
        self.register(ListDirTool())
        self.register(GitStatusTool())
        self.register(GitLogTool())
        self.register(ShellCommandTool())
        self.register(SearchMemoryTool())
        self.register(WriteEpisodicMemoryTool())
        self.register(UnrealStatusTool())
        self.register(UnrealSearchAssetsTool())
        self.register(GoogleMapsSearchTool())
        self.register(LogoSearchTool())
        self.register(LogoAuditTool())
        self.register(LogoStatsTool())

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool
        logger.debug(f"Ferramenta registrada: {tool.name} (Risco {tool.metadata.risk_level})")

    def get_tool(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[ToolMetadata]:
        return [t.metadata for t in self._tools.values()]

    def emit_tool_event(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        decision: PermissionDecision,
        result: ToolResult | None = None
    ) -> None:
        event_id = f"evt_tool_{uuid.uuid4().hex[:10]}"
        now = datetime.now(timezone.utc).isoformat()
        payload = {
            "id": event_id,
            "timestamp": now,
            "type": "tool_call",
            "tool_name": tool_name,
            "permission_decision": decision.value,
            "arguments": {k: str(v)[:200] for k, v in arguments.items()},
            "success": result.success if result else False,
            "duration_ms": result.duration_ms if result else 0.0,
            "error": result.error if result else None
        }
        event_file = self.events_dir / f"{now.replace(':', '-')}_{event_id}.json"
        try:
            with open(event_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Falha ao persistir evento de ferramenta {event_id}: {e}")

    def execute(self, tool_name: str, **kwargs) -> ToolResult:
        """
        Executa uma ferramenta registrada apos avaliacao do Permission Cortex.
        """
        tool = self.get_tool(tool_name)
        if not tool:
            err = f"Ferramenta '{tool_name}' nao encontrada no Tool Bus."
            logger.warning(err)
            return ToolResult(
                tool_name=tool_name,
                success=False,
                error=err,
                raw_output=err
            )

        # Avaliar permissao
        decision, reason = self.permission_cortex.evaluate(tool.metadata, kwargs)
        if decision == PermissionDecision.DENY:
            logger.warning(f"Execucao negada para {tool_name}: {reason}")
            res = ToolResult(
                tool_name=tool_name,
                success=False,
                error=f"Acesso negado: {reason}",
                raw_output=reason
            )
            self.emit_tool_event(tool_name, kwargs, decision, res)
            return res

        if decision == PermissionDecision.REQUIRE_CONFIRMATION:
            logger.warning(f"Execucao pendente de confirmacao para {tool_name}: {reason}")
            res = ToolResult(
                tool_name=tool_name,
                success=False,
                error=f"Confirmacao requerida: {reason}",
                raw_output=reason
            )
            self.emit_tool_event(tool_name, kwargs, decision, res)
            return res

        # Executar ferramenta
        result = tool.run(**kwargs)
        self.emit_tool_event(tool_name, kwargs, decision, result)
        return result
