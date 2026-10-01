"""Adaptador governado para uma instancia local do Google Maps Scraper Kit.

O ThSyr nao inicia scraping por conta propria. A instancia deve ser explicitamente
habilitada pelo operador e permanecer local; o adaptador limita a consulta a um
keyword por chamada e nao aceita proxies ou jobs em lote.
"""

from __future__ import annotations

import csv
import io
import json
import os
import time
import urllib.error
import urllib.request
from typing import Any

from ..base import BaseTool, RiskLevel, ToolMetadata, ToolResult


class GoogleMapsSearchTool(BaseTool):
    """Consulta um job local autorizado e retorna campos mínimos de lead."""

    def __init__(self) -> None:
        super().__init__(ToolMetadata(
            name="google_maps_search",
            description=(
                "Consulta uma instancia local autorizada do Google Maps Scraper Kit "
                "para uma busca pontual de estabelecimentos"
            ),
            input_schema={
                "type": "object",
                "required": ["keyword", "lat", "lon"],
                "properties": {
                    "keyword": {"type": "string", "description": "Uma consulta, sem lote"},
                    "lat": {"type": "string", "description": "Latitude do centro da busca"},
                    "lon": {"type": "string", "description": "Longitude do centro da busca"},
                    "depth": {"type": "integer", "default": 5, "maximum": 5},
                    "max_time": {"type": "integer", "default": 300, "maximum": 600},
                },
            },
            output_schema={
                "type": "object",
                "properties": {
                    "job_id": {"type": "string"},
                    "count": {"type": "integer"},
                    "results": {"type": "array"},
                },
            },
            risk_level=RiskLevel.LEVEL_4_EXTERNAL_MSG,
            requires_confirmation=True,
            timeout=660,
            reversible=True,
        ))

    @staticmethod
    def _enabled() -> bool:
        return os.getenv("THSYR_MAPS_SCRAPER_ENABLED", "").lower() in {"1", "true", "yes"}

    @staticmethod
    def _base_url() -> str:
        return os.getenv("THSYR_MAPS_SCRAPER_URL", "http://127.0.0.1:8080").rstrip("/")

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        timeout: int = 15,
    ) -> dict[str, Any] | str:
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {"User-Agent": "ThSyr/GoogleMapsAdapter", "Content-Type": "application/json"}
        api_key = os.getenv("THSYR_MAPS_SCRAPER_API_KEY")
        if api_key:
            headers["X-API-Key"] = api_key
        request = urllib.request.Request(
            f"{self._base_url()}{path}",
            data=data,
            headers=headers,
            method=method,
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw

    def execute(self, **kwargs: Any) -> ToolResult:
        keyword = str(kwargs.get("keyword", ""))
        lat = str(kwargs.get("lat", ""))
        lon = str(kwargs.get("lon", ""))
        depth = int(kwargs.get("depth", 5))
        max_time = int(kwargs.get("max_time", 300))
        if not self._enabled():
            return ToolResult(
                tool_name=self.name,
                success=False,
                error="MAPS_SCRAPER_DISABLED: defina THSYR_MAPS_SCRAPER_ENABLED=true para habilitar.",
            )
        keyword = keyword.strip()
        if not keyword:
            return ToolResult(tool_name=self.name, success=False, error="KEYWORD_REQUIRED")
        if not 1 <= depth <= 5:
            return ToolResult(tool_name=self.name, success=False, error="DEPTH_LIMIT_EXCEEDED")
        if not 1 <= max_time <= 600:
            return ToolResult(tool_name=self.name, success=False, error="MAX_TIME_LIMIT_EXCEEDED")

        try:
            created = self._request(
                "POST",
                "/api/v1/jobs",
                {
                    "name": "thsyr-single-search",
                    "keywords": [keyword],
                    "lang": "pt",
                    "zoom": 15,
                    "lat": str(lat),
                    "lon": str(lon),
                    "fast_mode": False,
                    "radius": 10000,
                    "depth": depth,
                    "email": False,
                    "max_time": max_time,
                },
                timeout=15,
            )
            if not isinstance(created, dict) or not created.get("id"):
                return ToolResult(tool_name=self.name, success=False, error="MAPS_JOB_ID_MISSING")

            job_id = str(created["id"])
            deadline = time.monotonic() + max_time
            status: str | None = None
            while time.monotonic() < deadline:
                state = self._request("GET", f"/api/v1/jobs/{job_id}", timeout=15)
                status = str(state.get("Status", "")) if isinstance(state, dict) else ""
                if status == "ok":
                    break
                if status == "failed":
                    return ToolResult(tool_name=self.name, success=False, error="MAPS_JOB_FAILED")
                time.sleep(5)
            else:
                return ToolResult(tool_name=self.name, success=False, error="MAPS_JOB_TIMEOUT")

            downloaded = self._request("GET", f"/api/v1/jobs/{job_id}/download", timeout=30)
            if isinstance(downloaded, str):
                rows = list(csv.DictReader(io.StringIO(downloaded)))
            elif isinstance(downloaded, list):
                rows = downloaded
            else:
                rows = []
            fields = ("title", "phone", "website", "category", "address", "review_rating", "review_count")
            results = [{field: row.get(field, "") for field in fields} for row in rows if isinstance(row, dict)]
            return ToolResult(
                tool_name=self.name,
                success=True,
                data={"job_id": job_id, "count": len(results), "results": results},
                raw_output=f"Consulta local concluída: {len(results)} resultados.",
            )
        except urllib.error.URLError as error:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=f"MAPS_SCRAPER_UNREACHABLE: {error.reason}",
            )
