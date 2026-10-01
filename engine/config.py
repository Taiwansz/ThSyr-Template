"""
ThSyr Configuration Layer
Fornece caminhos portaveis, variaveis de ambiente e configuracoes estruturadas
para garantir que o sistema nao dependa de caminhos absolutos ou maquinas especificas.
Isolamento garantido para ambiente de testes (THSYR_ENV=test).
"""

import logging
import os
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path


def is_test_environment() -> bool:
    env_val = os.getenv("THSYR_ENV")
    if env_val:
        return env_val.lower() == "test"
    if "unittest" in sys.modules:
        return True
    if any("unittest" in arg or "pytest" in arg for arg in sys.argv):
        return True
    return False


def get_default_project_root() -> Path:
    env_root = os.getenv("THSYR_ROOT")
    if env_root:
        return Path(env_root).resolve()
    return Path(__file__).resolve().parent.parent


def _load_env_file(path: Path) -> None:
    if not path.is_file():
        return
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k and k not in os.environ:
                    os.environ[k] = v
    except Exception:
        pass


PROJECT_ROOT = get_default_project_root()
_load_env_file(PROJECT_ROOT / ".env")


def get_default_state_dir() -> Path:
    env_state = os.getenv("THSYR_STATE_DIR")
    if env_state:
        return Path(env_state).resolve()
    if is_test_environment():
        test_dir = Path(tempfile.gettempdir()) / f"thsyr_test_state_{os.getpid()}"
        test_dir.mkdir(parents=True, exist_ok=True)
        return test_dir
    return PROJECT_ROOT / "state"


@dataclass
class AcademicSettings:
    vault_path: Path = field(default_factory=lambda: Path(
        os.getenv("CS_VAULT_PATH", str(PROJECT_ROOT / "cs_vault_mirror"))
    ))
    enable_dual_write: bool = True


@dataclass
class SyncSettings:
    auto_push: bool = True
    remote_name: str = "origin"
    branch_name: str = "main"
    git_timeout_seconds: int = 15


@dataclass
class BrainSettings:
    brain_dir: Path = field(default_factory=lambda: Path(
        os.getenv("THSYR_BRAIN_DIR", str(PROJECT_ROOT / "brain"))
    ))
    state_dir: Path = field(default_factory=get_default_state_dir)


@dataclass
class CodenotchSettings:
    enabled: bool = field(default_factory=lambda: os.getenv("THSYR_CODENOTCH_ENABLED", "true").lower() in ("true", "1", "yes"))
    custom_path: str | None = field(default_factory=lambda: os.getenv("THSYR_CODENOTCH_PATH"))
    auto_launch: bool = True


@dataclass
class OperatorIntelligenceSettings:
    reflection_enabled: bool = field(
        default_factory=lambda: os.getenv("THSYR_OPERATOR_REFLECTION_ENABLED", "true").lower()
        in ("true", "1", "yes")
    )
    reflection_poll_seconds: int = field(
        default_factory=lambda: int(os.getenv("THSYR_OPERATOR_REFLECTION_POLL_SECONDS", "1800"))
    )
    reflection_min_signals: int = field(
        default_factory=lambda: int(os.getenv("THSYR_OPERATOR_REFLECTION_MIN_SIGNALS", "8"))
    )
    reflection_cooldown_seconds: int = field(
        default_factory=lambda: int(os.getenv("THSYR_OPERATOR_REFLECTION_COOLDOWN_SECONDS", "14400"))
    )
    reflection_max_signals: int = field(
        default_factory=lambda: int(os.getenv("THSYR_OPERATOR_REFLECTION_MAX_SIGNALS", "60"))
    )


@dataclass
class Settings:
    project_root: Path = PROJECT_ROOT
    env: str = field(default_factory=lambda: "test" if is_test_environment() else os.getenv("THSYR_ENV", "production"))
    academic: AcademicSettings = field(default_factory=AcademicSettings)
    sync: SyncSettings = field(default_factory=SyncSettings)
    brain: BrainSettings = field(default_factory=BrainSettings)
    codenotch: CodenotchSettings = field(default_factory=CodenotchSettings)
    operator_intelligence: OperatorIntelligenceSettings = field(
        default_factory=OperatorIntelligenceSettings
    )

    def __post_init__(self) -> None:
        if (self.env == "test" or is_test_environment()) and "THSYR_STATE_DIR" not in os.environ:
            test_dir = Path(tempfile.gettempdir()) / f"thsyr_test_state_{os.getpid()}"
            test_dir.mkdir(parents=True, exist_ok=True)
            self.brain.state_dir = test_dir

    def ensure_directories(self) -> None:
        self.brain.brain_dir.mkdir(parents=True, exist_ok=True)
        self.brain.state_dir.mkdir(parents=True, exist_ok=True)
        (self.brain.state_dir / "sessions").mkdir(parents=True, exist_ok=True)
        (self.brain.state_dir / "events").mkdir(parents=True, exist_ok=True)
        (self.brain.state_dir / "goals").mkdir(parents=True, exist_ok=True)
        (self.brain.state_dir / "plans").mkdir(parents=True, exist_ok=True)
        (self.brain.brain_dir / "memories" / "episodic").mkdir(parents=True, exist_ok=True)
        (self.brain.brain_dir / "memories" / "semantic").mkdir(parents=True, exist_ok=True)


settings = Settings()


def get_state_dir() -> Path:
    return settings.brain.state_dir


def get_brain_dir() -> Path:
    return settings.brain.brain_dir


def setup_logger(name: str = "thsyr", level: int | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    target_level = level if level is not None else (logging.DEBUG if settings.env == "development" else logging.INFO)
    logger.setLevel(target_level)
    return logger
