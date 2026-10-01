"""
ThSyr Filesystem Tool Adapters
Operacoes de leitura, escrita atomica e listagem com contencao estrita em sandbox
e prevencao de path traversal.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, List, Optional

from ...config import PROJECT_ROOT, settings
from ..base import BaseTool, RiskLevel, ToolMetadata, ToolResult


def is_safe_workspace_path(p: Path, allowed_roots: Optional[List[Path]] = None) -> bool:
    """Verifica se o caminho esta contido nas raizes autorizadas do workspace."""
    try:
        resolved = p.resolve()
        roots = allowed_roots or [
            PROJECT_ROOT.resolve(),
            settings.brain.state_dir.resolve(),
            settings.brain.brain_dir.resolve(),
            Path(tempfile.gettempdir()).resolve(),
        ]
        return any(resolved == r or r in resolved.parents for r in roots)
    except Exception:
        return False


class ReadFileTool(BaseTool):
    def __init__(self):
        super().__init__(ToolMetadata(
            name="read_file",
            description="Le o conteudo de um arquivo local com limitacao de tamanho",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Caminho do arquivo a ler"},
                    "max_chars": {"type": "integer", "default": 2000, "description": "Limite maximo de caracteres"}
                },
                "required": ["path"]
            },
            output_schema={"type": "object", "properties": {"content": {"type": "string"}}},
            risk_level=RiskLevel.LEVEL_1_READ,
            requires_confirmation=False,
            timeout=5,
            reversible=True
        ))

    def execute(self, path: str = "", max_chars: int = 2000, **kwargs: Any) -> ToolResult:
        if not path:
            return ToolResult(tool_name=self.name, success=False, error="Caminho do arquivo nao fornecido.")

        p = Path(path)
        if not p.is_absolute():
            p = PROJECT_ROOT / p

        if not is_safe_workspace_path(p):
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=f"Acesso negado por sandbox: caminho '{p}' fora do escopo do workspace."
            )

        if not p.exists():
            return ToolResult(tool_name=self.name, success=False, error=f"Arquivo '{p}' nao encontrado.")

        if not p.is_file():
            return ToolResult(tool_name=self.name, success=False, error=f"Caminho '{p}' nao e um arquivo.")

        content = p.read_text(encoding="utf-8", errors="replace")[:max_chars]
        return ToolResult(
            tool_name=self.name,
            success=True,
            data={"path": str(p), "size_chars": len(content)},
            raw_output=content
        )


class WriteFileTool(BaseTool):
    def __init__(self):
        super().__init__(ToolMetadata(
            name="write_file",
            description="Escreve ou atualiza um arquivo local com backup automatico e escrita atomica",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Caminho do arquivo"},
                    "content": {"type": "string", "description": "Conteudo a gravar"}
                },
                "required": ["path", "content"]
            },
            output_schema={"type": "object", "properties": {"bytes_written": {"type": "integer"}}},
            risk_level=RiskLevel.LEVEL_2_CREATE_LOCAL,
            requires_confirmation=False,
            timeout=5,
            reversible=True,
            rollback_strategy="restore_backup_file"
        ))

    def execute(self, path: str = "", content: str = "", **kwargs: Any) -> ToolResult:
        if not path:
            return ToolResult(tool_name=self.name, success=False, error="Caminho do arquivo nao fornecido.")

        p = Path(path)
        if not p.is_absolute():
            p = PROJECT_ROOT / p

        if not is_safe_workspace_path(p):
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=f"Acesso negado por sandbox: caminho '{p}' fora do escopo do workspace."
            )

        try:
            p.parent.mkdir(parents=True, exist_ok=True)

            # Criar snapshot de backup se o arquivo ja existir para rollback confiavel
            backup_path = None
            if p.exists() and p.is_file():
                backup_dir = settings.brain.state_dir / "backups"
                backup_dir.mkdir(parents=True, exist_ok=True)
                backup_path = backup_dir / f"{p.name}.{os.getpid()}.bak"
                shutil.copy2(p, backup_path)

            # Escrita atomica: temporario no mesmo diretorio e replace atomico
            tmp_target = p.with_name(f".tmp_{p.name}_{os.getpid()}")
            tmp_target.write_text(content, encoding="utf-8")
            tmp_target.replace(p)

            return ToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "path": str(p),
                    "bytes_written": len(content.encode("utf-8")),
                    "backup_path": str(backup_path) if backup_path else None
                },
                raw_output=f"Arquivo '{p.name}' gravado com sucesso de forma atomica ({len(content)} caracteres)."
            )
        except Exception as e:
            return ToolResult(tool_name=self.name, success=False, error=f"Falha na escrita atomica: {e}")


class ListDirTool(BaseTool):
    def __init__(self):
        super().__init__(ToolMetadata(
            name="list_dir",
            description="Lista o conteudo de um diretorio com protecao de contencao",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "default": ".", "description": "Caminho do diretorio"}
                }
            },
            output_schema={"type": "object", "properties": {"entries": {"type": "array"}}},
            risk_level=RiskLevel.LEVEL_1_READ,
            requires_confirmation=False,
            timeout=5,
            reversible=True
        ))

    def execute(self, path: str = ".", **kwargs: Any) -> ToolResult:
        p = Path(path)
        if not p.is_absolute():
            p = PROJECT_ROOT / p

        if not is_safe_workspace_path(p):
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=f"Acesso negado por sandbox: caminho '{p}' fora do escopo do workspace."
            )

        if not p.exists() or not p.is_dir():
            return ToolResult(tool_name=self.name, success=False, error=f"Diretorio '{p}' nao encontrado.")

        entries = sorted([item.name + ("/" if item.is_dir() else "") for item in p.iterdir()])
        return ToolResult(
            tool_name=self.name,
            success=True,
            data={"path": str(p), "count": len(entries), "entries": entries},
            raw_output="\n".join(entries[:50])
        )
