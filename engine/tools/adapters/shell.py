"""
ThSyr Tool Bus - Shell Adapter
Executa comandos shell controlados com filtro pre-frontal anti-destruicao:
- ShellCommandTool (Risco 3)
"""

import subprocess
from typing import Any

from ...config import PROJECT_ROOT
from ..base import BaseTool, RiskLevel, ToolMetadata, ToolResult

BANNED_SHELL_PATTERNS = [
    "rm -rf", "drop database", "delete from", "truncate", "mkfs",
    ":(){ :|:& };:", "> /dev/sda", "chmod -R 777 /"
]


class ShellCommandTool(BaseTool):
    def __init__(self):
        super().__init__(ToolMetadata(
            name="shell_command",
            description="Executa um comando de linha de comando seguro no workspace",
            input_schema={
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Comando a ser executado"}
                },
                "required": ["command"]
            },
            output_schema={"type": "object", "properties": {"stdout": {"type": "string"}}},
            risk_level=RiskLevel.LEVEL_3_EDIT_PROJECT,
            requires_confirmation=False,
            timeout=20,
            reversible=False
        ))

    def execute(self, command: str = "", **kwargs: Any) -> ToolResult:
        cmd_clean = command.strip()
        cmd_lower = cmd_clean.lower()

        # Auditoria de seguranca
        for pat in BANNED_SHELL_PATTERNS:
            if pat in cmd_lower:
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    data=None,
                    raw_output=f"Comando bloqueado pelo filtro de seguranca: '{pat}' detectado.",
                    error=f"Padrao proibido: '{pat}'"
                )

        try:
            res = subprocess.run(
                cmd_clean,
                shell=True,
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=self.metadata.timeout
            )
            out = res.stdout.strip()
            err = res.stderr.strip()
            return ToolResult(
                tool_name=self.name,
                success=(res.returncode == 0),
                data={"returncode": res.returncode, "stderr": err},
                raw_output=out if out else (err or "Comando executado sem saida."),
                error=err if res.returncode != 0 else None
            )
        except subprocess.TimeoutExpired:
            return ToolResult(
                tool_name=self.name,
                success=False,
                data=None,
                raw_output=f"Comando excedeu o limite de tempo de {self.metadata.timeout}s.",
                error="TimeoutExpired"
            )
