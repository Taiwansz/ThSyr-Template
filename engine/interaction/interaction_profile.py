"""
ThSyr Interaction Layer - Interaction Profile
Armazena e versiona preferencias de comunicacao do operador de forma
desacoplada de memorias gerais e mecanismos de autenticacao.
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

from ..config import get_state_dir, setup_logger

logger = setup_logger("interaction_profile")


@dataclass
class InteractionProfile:
    language: str = "pt-BR"
    technical_depth: str = "high"
    direct_answers: bool = True
    tolerance_for_explanations: str = "low"
    update_frequency: str = "important_only"
    use_examples: bool = False
    prefer_commands: bool = True
    confirmation_style: str = "informative"
    code_format: str = "concise"
    version: int = 1

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InteractionProfile":
        valid_keys = {
            "language",
            "technical_depth",
            "direct_answers",
            "tolerance_for_explanations",
            "update_frequency",
            "use_examples",
            "prefer_commands",
            "confirmation_style",
            "code_format",
            "version",
        }
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)

    def save(self, target_path: Optional[Path] = None) -> Path:
        path = target_path or (get_state_dir() / "interaction_profile.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        return path

    @classmethod
    def load(cls, source_path: Optional[Path] = None) -> "InteractionProfile":
        path = source_path or (get_state_dir() / "interaction_profile.json")
        if not path.exists():
            profile = cls()
            profile.save(path)
            return profile
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            logger.warning(f"Erro ao carregar perfil de interacao ({e}). Usando perfil padrao.")
            return cls()
