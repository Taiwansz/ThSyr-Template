"""
ThSyr Interaction Layer - Verbosity Management
Controla niveis de verbosidade persistentes e adaptativos para respostas.
"""

from enum import IntEnum
from typing import Optional


class VerbosityLevel(IntEnum):
    COMPACT = 1
    DIRECT = 2
    NORMAL = 3
    DETAILED = 4
    DEEP = 5

    @classmethod
    def from_input(cls, val: str | int) -> "VerbosityLevel":
        if isinstance(val, int):
            if val <= 1:
                return cls.COMPACT
            elif val == 2:
                return cls.DIRECT
            elif val == 3:
                return cls.NORMAL
            elif val == 4:
                return cls.DETAILED
            else:
                return cls.DEEP

        cleaned = str(val).strip().lower()
        if cleaned in ("1", "compact", "c", "min", "curto"):
            return cls.COMPACT
        elif cleaned in ("2", "direct", "d", "direto"):
            return cls.DIRECT
        elif cleaned in ("3", "normal", "n", "padrao"):
            return cls.NORMAL
        elif cleaned in ("4", "detailed", "detalhado", "detalhes"):
            return cls.DETAILED
        elif cleaned in ("5", "deep", "profundo", "max"):
            return cls.DEEP
        return cls.NORMAL


class VerbosityManager:
    def __init__(self, default_level: VerbosityLevel = VerbosityLevel.NORMAL):
        self.global_level: VerbosityLevel = default_level
        self._override_level: Optional[VerbosityLevel] = None
        self.adaptive_enabled: bool = True

    @property
    def current_level(self) -> VerbosityLevel:
        if self._override_level is not None:
            return self._override_level
        return self.global_level

    def set_global_level(self, level: VerbosityLevel | str | int) -> VerbosityLevel:
        if not isinstance(level, VerbosityLevel):
            level = VerbosityLevel.from_input(level)
        self.global_level = level
        return self.global_level

    def set_override(self, level: VerbosityLevel | str | int) -> VerbosityLevel:
        if not isinstance(level, VerbosityLevel):
            level = VerbosityLevel.from_input(level)
        self._override_level = level
        return self._override_level

    def clear_override(self) -> None:
        self._override_level = None

    def calculate_effective_level(
        self,
        query: str,
        operation_risk: int = 0,
        ambiguity_score: float = 0.0,
        user_explicit_override: Optional[VerbosityLevel] = None,
    ) -> VerbosityLevel:
        """
        Determina o nivel de verbosidade efetivo respeitando overrides explicitos
        e adaptando heuristicamente caso habilitado.
        """
        if user_explicit_override is not None:
            return user_explicit_override

        if self._override_level is not None:
            return self._override_level

        # Se o usuario definiu explicitamente algo diferente de NORMAL, honrar
        if self.global_level != VerbosityLevel.NORMAL or not self.adaptive_enabled:
            return self.global_level

        # Adaptacao heuristica:
        # Alto risco operacional (ex: risco >= 4) exige explicacao suficiente
        if operation_risk >= 4:
            return VerbosityLevel.DETAILED

        # Ambiguidade alta (score > 0.6) exige precisao e opcoes
        if ambiguity_score > 0.6:
            return VerbosityLevel.DIRECT

        q_len = len(query.strip().split())
        q_lower = query.lower()

        # Comandos curtos/diretos ("sim", "manda", "qual status?", "vai") -> COMPACT
        if q_len <= 3 or q_lower in ("status", "e ai", "qual o status", "continua", "manda"):
            return VerbosityLevel.COMPACT

        # Pedidos explicitos de analise/arquitetura/por que -> DETAILED ou DEEP
        if any(w in q_lower for w in ("analise profunda", "arquitetura", "por que", "why", "explique em detalhes", "tradeoffs")):
            return VerbosityLevel.DEEP

        return VerbosityLevel.DIRECT
