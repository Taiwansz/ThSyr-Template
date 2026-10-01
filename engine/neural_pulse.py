"""
ThSyr Neural Pulse & Trace Recorder
Gerencia o estado de pulso e ativacao sinaptica em tempo real para o Neural Canvas (HUD e grafo D3).
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import settings, setup_logger

logger = setup_logger("neural_pulse")


def record_neural_pulse(
    query: str,
    seeds: list[str],
    top_activated: list[dict[str, Any]],
    constraints: list[str] | None = None,
    retrieved: list[dict[str, Any]] | None = None,
    state_dir: Path | None = None,
    brain_dir: Path | None = None
) -> dict[str, Any]:
    """
    Grava o estado do pulso sinaptico atômico em JSON (para servidores/APIs)
    e em JS (para execucao local direta via file:/// no canvas D3 sem bloqueio de CORS).
    """
    s_dir = state_dir or settings.brain.state_dir
    b_dir = brain_dir or (s_dir if settings.env == "test" else settings.brain.brain_dir)
    s_dir.mkdir(parents=True, exist_ok=True)
    b_dir.mkdir(parents=True, exist_ok=True)

    pulse_data = {
        "id": f"pulse_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')[:19]}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "seeds": seeds,
        "top_activated": [
            {
                "id": str(item.get("node", item.get("id", ""))),
                "energy": float(item.get("energy", 1.0)),
                "lobe": str(item.get("lobe", "cortex"))
            }
            for item in top_activated
        ],
        "constraints": constraints or [],
        "retrieved": [
            {
                "id": str(r.get("id", "")),
                "title": str(r.get("title", "")),
                "type": str(r.get("type", "")),
                "score": float(r.get("score", 0.0))
            }
            for r in (retrieved or [])
        ]
    }

    # 1. Gravar em JSON no state
    json_path = s_dir / "active_synapses.json"
    try:
        json_path.write_text(json.dumps(pulse_data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        logger.warning(f"Falha ao gravar active_synapses.json: {e}")

    # 2. Gravar em JS no brain (garante recarregamento dinamico no browser local em file://)
    js_path = b_dir / "active_synapses.js"
    try:
        js_content = f"window.__THSYR_PULSE__ = {json.dumps(pulse_data, indent=2, ensure_ascii=False)};"
        js_path.write_text(js_content, encoding="utf-8")
    except Exception as e:
        logger.warning(f"Falha ao gravar active_synapses.js: {e}")

    logger.info(f"Pulso sinaptico registrado: {pulse_data['id']} ({len(pulse_data['top_activated'])} nos ativados)")
    return pulse_data


def get_last_neural_pulse(state_dir: Path | None = None) -> dict[str, Any] | None:
    s_dir = state_dir or settings.brain.state_dir
    json_path = s_dir / "active_synapses.json"
    if not json_path.exists():
        return None
    try:
        return json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning(f"Erro ao ler active_synapses.json: {e}")
        return None
