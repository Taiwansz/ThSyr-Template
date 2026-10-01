"""
ThSyr Tool Bus - Base Models & Contracts (Fase 5)
Define o contrato tipado e esquemas de ferramentas:
- name, description, input_schema, output_schema
- risk_level (0 a 6), requires_confirmation, timeout, reversible, rollback_strategy
- ToolResult padronizado com duracao, dados e telemetria
"""

import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from enum import IntEnum
from typing import Any


class RiskLevel(IntEnum):
    LEVEL_0_SEARCH = 0        # Pesquisa de memoria / consultas seguras (automatico)
    LEVEL_1_READ = 1          # Leitura de arquivos / status git / telemetria (automatico)
    LEVEL_2_CREATE_LOCAL = 2  # Criacao de arquivos locais reversiveis (automatico)
    LEVEL_3_EDIT_PROJECT = 3  # Edicao de projeto / compilacao (configuravel)
    LEVEL_4_EXTERNAL_MSG = 4  # Envio de mensagens / notificacoes externas (confirmacao)
    LEVEL_5_DELETE_DATA = 5   # Exclusao de dados ou alteracao destrutiva (confirmacao forte)
    LEVEL_6_CRITICAL = 6      # Credenciais / operacao critica de sistema (bloqueio ou politica especial)


@dataclass
class ToolMetadata:
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    risk_level: RiskLevel = RiskLevel.LEVEL_1_READ
    requires_confirmation: bool = False
    timeout: int = 15
    reversible: bool = True
    rollback_strategy: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["risk_level"] = int(self.risk_level)
        return d


@dataclass
class ToolResult:
    tool_name: str
    success: bool
    data: Any = None
    raw_output: str = ""
    duration_ms: float = 0.0
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class BaseTool(ABC):
    def __init__(self, metadata: ToolMetadata):
        self.metadata = metadata

    @property
    def name(self) -> str:
        return self.metadata.name

    def validate_inputs(self, kwargs: dict[str, Any]) -> tuple[bool, str | None]:
        """
        Valida argumentos basicos conforme o schema de entrada.
        """
        required = self.metadata.input_schema.get("required", [])
        for field_name in required:
            if field_name not in kwargs or kwargs[field_name] is None:
                return False, f"Parametro obrigatorio ausente: '{field_name}'"
        return True, None

    def run(self, **kwargs) -> ToolResult:
        """
        Executa a ferramenta com cronometragem e captura de excecoes.
        """
        ok, err = self.validate_inputs(kwargs)
        if not ok:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=err,
                raw_output=err or ""
            )

        start_t = time.perf_counter()
        try:
            res = self.execute(**kwargs)
            duration_ms = (time.perf_counter() - start_t) * 1000.0
            res.duration_ms = round(duration_ms, 2)
            return res
        except Exception as e:
            duration_ms = (time.perf_counter() - start_t) * 1000.0
            return ToolResult(
                tool_name=self.name,
                success=False,
                data=None,
                raw_output=str(e),
                duration_ms=round(duration_ms, 2),
                error=str(e)
            )

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """
        Implementacao concreta da acao da ferramenta.
        """
