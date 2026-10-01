"""
ThSyr Tool Bus Adapter - Unreal Engine 5 Remote Control Integration
Conecta o ThSyr diretamente a instancia ativa do Unreal Engine 5.8 via Web Remote Control API (HTTP :30010).
"""

import json
import urllib.error
import urllib.request
from typing import Any, Optional

from ..base import BaseTool, RiskLevel, ToolMetadata, ToolResult

UNREAL_HTTP_BASE = "http://127.0.0.1:30010"


def _request_ue(path: str, method: str = "GET", payload: Optional[dict[str, Any]] = None, timeout: int = 5) -> dict[str, Any]:
    url = f"{UNREAL_HTTP_BASE}{path}"
    data = json.dumps(payload).encode("utf-8") if payload else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
        method=method
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        content = resp.read().decode("utf-8")
        return json.loads(content) if content else {}


class UnrealStatusTool(BaseTool):
    def __init__(self):
        super().__init__(ToolMetadata(
            name="unreal_status",
            description="Inspeciona o status da conexao em tempo real com o Unreal Engine 5.8 via Remote Control API",
            input_schema={
                "type": "object",
                "properties": {}
            },
            output_schema={
                "type": "object",
                "properties": {
                    "online": {"type": "boolean"},
                    "engine_version": {"type": "string"},
                    "http_routes_count": {"type": "integer"}
                }
            },
            risk_level=RiskLevel.LEVEL_1_READ,
            timeout=5
        ))

    def execute(self, **kwargs) -> ToolResult:
        try:
            info = _request_ue("/remote/info", method="GET", timeout=3)
            routes = info.get("HttpRoutes", [])
            return ToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "online": True,
                    "engine_version": "5.8",
                    "http_port": 30010,
                    "websocket_port": 30020,
                    "available_routes_count": len(routes),
                    "active_preset": info.get("ActivePreset", {})
                },
                raw_output=f"Unreal Engine 5.8 Remote Control ONLINE ({len(routes)} rotas ativas)."
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=f"Falha ao conectar com Unreal Engine Remote Control (127.0.0.1:30010): {e!s}"
            )


class UnrealSearchAssetsTool(BaseTool):
    def __init__(self):
        super().__init__(ToolMetadata(
            name="unreal_search_assets",
            description="Pesquisa assets (StaticMeshes, Materiais, Blueprints) carregados no projeto ativo da Unreal Engine",
            input_schema={
                "type": "object",
                "properties": {
                    "package_path": {
                        "type": "string",
                        "description": "Caminho do pacote a pesquisar, ex: /Game ou /Game/Prisma",
                        "default": "/Game"
                    },
                    "query": {
                        "type": "string",
                        "description": "Termo de busca opcional",
                        "default": ""
                    }
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "total_assets": {"type": "integer"},
                    "assets": {"type": "array"}
                }
            },
            risk_level=RiskLevel.LEVEL_1_READ,
            timeout=10
        ))

    def execute(self, package_path: str = "/Game", query: str = "", **kwargs) -> ToolResult:
        try:
            payload = {
                "Query": query,
                "Filter": {
                    "PackagePaths": [package_path],
                    "RecursivePaths": True
                }
            }
            res = _request_ue("/remote/search/assets", method="PUT", payload=payload, timeout=8)
            assets = res.get("Assets", [])
            formatted = [
                {
                    "name": a.get("Name"),
                    "class": a.get("Class"),
                    "path": a.get("Path")
                }
                for a in assets
            ]
            return ToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "total_assets": len(formatted),
                    "assets": formatted
                },
                raw_output=f"Encontrados {len(formatted)} assets em '{package_path}'."
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=f"Erro ao buscar assets no Unreal Engine: {e!s}"
            )
