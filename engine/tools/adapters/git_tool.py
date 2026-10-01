"""
ThSyr Tool Bus - Git Adapters
Ferramentas para inspecao de estado do Git:
- GitStatusTool (Risco 1)
- GitLogTool (Risco 1)
- GitDiffTool (Risco 1)
"""

import subprocess
import time

from ...config import PROJECT_ROOT
from ..base import BaseTool, RiskLevel, ToolMetadata, ToolResult


class GitStatusTool(BaseTool):
    def __init__(self):
        super().__init__(ToolMetadata(
            name="git_status",
            description="Exibe o status do repositorio local git (branch, arquivos modificados)",
            input_schema={"type": "object", "properties": {}},
            output_schema={"type": "object", "properties": {"status": {"type": "string"}}},
            risk_level=RiskLevel.LEVEL_1_READ,
            requires_confirmation=False,
            timeout=10,
            reversible=True
        ))

    def execute(self, **kwargs) -> ToolResult:
        res = None
        for attempt in range(3):
            res = subprocess.run(
                ["git", "status", "--short", "--branch"],
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                check=False
            )
            if res.returncode == 0 or attempt == 2:
                break
            time.sleep(0.1 * (attempt + 1))
        assert res is not None
        return ToolResult(
            tool_name=self.name,
            success=(res.returncode == 0),
            data={"returncode": res.returncode},
            raw_output=res.stdout.strip() or "Repositorio limpo.",
            error=res.stderr.strip() if res.returncode != 0 else None
        )


class GitLogTool(BaseTool):
    def __init__(self):
        super().__init__(ToolMetadata(
            name="git_log",
            description="Exibe os commits recentes do repositorio",
            input_schema={
                "type": "object",
                "properties": {
                    "count": {"type": "integer", "default": 5, "description": "Numero de commits"}
                }
            },
            output_schema={"type": "object", "properties": {"commits": {"type": "array"}}},
            risk_level=RiskLevel.LEVEL_1_READ,
            requires_confirmation=False,
            timeout=10,
            reversible=True
        ))

    def execute(self, count: int = 5, **kwargs) -> ToolResult:
        res = subprocess.run(
            ["git", "log", f"-n{count}", "--oneline"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            check=False
        )
        commits = res.stdout.strip().splitlines()
        return ToolResult(
            tool_name=self.name,
            success=(res.returncode == 0),
            data={"count": len(commits), "commits": commits},
            raw_output=res.stdout.strip(),
            error=res.stderr.strip() if res.returncode != 0 else None
        )
