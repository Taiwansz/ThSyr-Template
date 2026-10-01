"""
Deep reflection over the Operator Intelligence signal stream.

This layer asks a reasoning-capable model to inspect multiple already-sanitized
operator signals together and propose second-order patterns. Model output is
treated as untrusted analysis: every candidate must cite real signal IDs, pass
privacy filters, survive schema validation and enter the belief store only as
an inference with capped confidence.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import settings, setup_logger
from .models import ModelGateway, ModelRouter
from .models.base import ModelTier
from .operator_intelligence import OperatorIntelligence

logger = setup_logger("operator_reflection")


class OperatorReflectionEngine:
    VERSION = 1

    ALLOWED_CATEGORIES = {
        "working_style",
        "decision_pattern",
        "quality_preference",
        "continuity_pattern",
        "tooling_pattern",
        "feedback_pattern",
    }

    BLOCKED_TERMS = {
        "ansiedade", "depressao", "depressão", "tdah", "autismo", "bipolar",
        "transtorno", "diagnostico", "diagnóstico", "doenca", "doença",
        "medicamento", "remedio", "remédio", "qi", "inteligencia", "inteligência",
        "politica", "política", "partido", "voto", "eleicao", "eleição",
        "religiao", "religião", "igreja", "sexualidade", "orientacao sexual",
        "orientação sexual", "raca", "raça", "etnia", "sindicato", "criminal",
        "crime", "renda", "salario", "salário", "patrimonio", "patrimônio",
    }

    def __init__(
        self,
        intelligence: OperatorIntelligence | None = None,
        gateway: ModelGateway | None = None,
        model_router: ModelRouter | None = None,
        storage_path: str | Path | None = None,
        enabled: bool | None = None,
        min_signals: int | None = None,
        cooldown_seconds: int | None = None,
        max_signals: int | None = None,
    ) -> None:
        self.intelligence = intelligence or OperatorIntelligence()
        self.gateway = gateway or ModelGateway()
        self.model_router = model_router or ModelRouter()
        cfg = settings.operator_intelligence
        self.enabled = cfg.reflection_enabled if enabled is None else enabled
        self.min_signals = max(2, cfg.reflection_min_signals if min_signals is None else min_signals)
        self.cooldown_seconds = max(
            0,
            cfg.reflection_cooldown_seconds if cooldown_seconds is None else cooldown_seconds,
        )
        self.max_signals = max(
            self.min_signals,
            cfg.reflection_max_signals if max_signals is None else max_signals,
        )
        self.storage_path = (
            Path(storage_path)
            if storage_path
            else settings.brain.state_dir / "operator_reflections.json"
        )

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @classmethod
    def _empty_state(cls) -> dict[str, Any]:
        return {
            "version": cls.VERSION,
            "last_success_at": None,
            "last_signal_id": None,
            "runs": [],
            "accepted_fingerprints": [],
            "metrics": {
                "runs": 0,
                "accepted_patterns": 0,
                "rejected_patterns": 0,
                "curiosity_gaps_added": 0,
                "model_failures": 0,
                "parse_failures": 0,
            },
        }

    def load(self) -> dict[str, Any]:
        if not self.storage_path.exists():
            return self._empty_state()
        try:
            data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return self._empty_state()
        if not isinstance(data, dict) or data.get("version") != self.VERSION:
            return self._empty_state()
        empty = self._empty_state()
        for key, value in empty.items():
            data.setdefault(key, value)
        for key, value in empty["metrics"].items():
            data["metrics"].setdefault(key, value)
        return data

    def _save(self, state: dict[str, Any]) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    @staticmethod
    def _direct_signals(intelligence_state: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            signal
            for signal in intelligence_state.get("signals", [])
            if signal.get("source") not in {"deep_reflection", "reflection"}
        ]

    def _new_signals(
        self,
        reflection_state: dict[str, Any],
        *,
        force: bool,
    ) -> list[dict[str, Any]]:
        signals = self._direct_signals(self.intelligence.load())
        if not signals:
            return []

        if force:
            return signals[-self.max_signals:]

        last_signal_id = reflection_state.get("last_signal_id")
        if not last_signal_id:
            return signals[-self.max_signals:]

        index = next(
            (i for i, signal in enumerate(signals) if signal.get("id") == last_signal_id),
            None,
        )
        if index is None:
            return signals[-self.max_signals:]
        return signals[index + 1 :][-self.max_signals:]

    def _cooldown_remaining(self, state: dict[str, Any]) -> float:
        raw = state.get("last_success_at")
        if not raw or self.cooldown_seconds <= 0:
            return 0.0
        try:
            last = datetime.fromisoformat(str(raw))
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
        except ValueError:
            return 0.0
        elapsed = (datetime.now(timezone.utc) - last).total_seconds()
        return max(0.0, self.cooldown_seconds - elapsed)

    def should_reflect(self, *, force: bool = False) -> dict[str, Any]:
        state = self.load()
        if not self.enabled and not force:
            return {"ready": False, "reason": "disabled", "new_signals": 0}

        signals = self._new_signals(state, force=force)
        if len(signals) < 2:
            return {
                "ready": False,
                "reason": "insufficient_evidence",
                "new_signals": len(signals),
            }

        if not force and len(signals) < self.min_signals:
            return {
                "ready": False,
                "reason": "waiting_for_more_signals",
                "new_signals": len(signals),
                "required": self.min_signals,
            }

        remaining = self._cooldown_remaining(state)
        if not force and remaining > 0:
            return {
                "ready": False,
                "reason": "cooldown",
                "new_signals": len(signals),
                "cooldown_remaining_seconds": round(remaining, 1),
            }

        if not self.gateway.providers:
            return {
                "ready": False,
                "reason": "model_unavailable",
                "new_signals": len(signals),
            }

        return {"ready": True, "reason": "ready", "new_signals": len(signals)}

    @staticmethod
    def _signal_pack(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
        allowed_fields = {
            "id",
            "category",
            "subject",
            "stance",
            "confidence",
            "explicit",
            "evidence",
            "created_at",
        }
        return [
            {key: signal.get(key) for key in allowed_fields}
            for signal in signals
        ]

    def _existing_belief_pack(self) -> list[dict[str, Any]]:
        beliefs = self.intelligence.snapshot().get("beliefs", [])
        return [
            {
                "key": belief.get("key"),
                "category": belief.get("category"),
                "subject": belief.get("subject"),
                "stance": belief.get("stance"),
                "status": belief.get("status"),
                "confidence": belief.get("confidence"),
            }
            for belief in beliefs[:30]
            if not str(belief.get("category", "")).startswith("reflection_")
        ]

    def _build_request(self, signals: list[dict[str, Any]]):
        system_prompt = (
            "Voce e o modulo de reflexao epistemica do ThSyr. "
            "Analise apenas os sinais fornecidos. Nao diagnostique personalidade, saude mental, "
            "inteligencia, intencoes ocultas ou caracteristicas sensiveis. Nao infira politica, "
            "religiao, saude, raca/etnia, sexualidade, vida sexual, historico criminal, sindicalizacao, "
            "renda ou credenciais. Nao trate estilo de escrita como identidade. "
            "Seu trabalho e detectar padroes operacionais de segunda ordem que melhorem colaboracao: "
            "forma de trabalhar, criterios de qualidade, tomada de decisao, continuidade, ferramentas "
            "e padroes de feedback. Toda hipotese precisa citar pelo menos dois signal IDs reais. "
            "Retorne SOMENTE JSON valido, sem markdown e sem texto extra."
        )
        payload = {
            "task": "second_order_operator_reflection",
            "schema": {
                "patterns": [
                    {
                        "category": "working_style|decision_pattern|quality_preference|continuity_pattern|tooling_pattern|feedback_pattern",
                        "subject": "descricao objetiva e observavel",
                        "stance": "positive|negative",
                        "confidence": "0.0-1.0",
                        "supporting_signal_ids": ["sig_x", "sig_y"],
                        "counter_signal_ids": [],
                        "reason": "explicacao curta baseada nos sinais",
                    }
                ],
                "curiosity": [
                    {
                        "question": "lacuna objetiva a observar organicamente",
                        "priority": "0.0-1.0",
                        "reason": "por que ainda ha incerteza",
                    }
                ],
            },
            "rules": [
                "no maximo 5 patterns",
                "no maximo 3 curiosity items",
                "nao invente signal IDs",
                "uma unica interacao nunca sustenta um pattern",
                "preferir nao propor nada a criar uma inferencia fraca",
            ],
            "existing_beliefs": self._existing_belief_pack(),
            "signals": self._signal_pack(signals),
        }
        return self.model_router.build_request(
            query=json.dumps(payload, ensure_ascii=False),
            system_prompt=system_prompt,
            forced_tier=ModelTier.REASONING,
        )

    @staticmethod
    def _parse_json(content: str) -> dict[str, Any]:
        raw = content.strip()
        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
            raw = re.sub(r"\s*```$", "", raw)
        first = raw.find("{")
        last = raw.rfind("}")
        if first < 0 or last < first:
            raise ValueError("model response does not contain a JSON object")
        parsed = json.loads(raw[first : last + 1])
        if not isinstance(parsed, dict):
            raise ValueError("reflection payload must be a JSON object")
        return parsed

    @classmethod
    def _contains_blocked_terms(cls, value: str) -> bool:
        lowered = value.lower()
        return any(term in lowered for term in cls.BLOCKED_TERMS)

    def _validate_pattern(
        self,
        candidate: Any,
        valid_signal_ids: set[str],
    ) -> tuple[dict[str, Any] | None, str]:
        if not isinstance(candidate, dict):
            return None, "not_object"

        category = str(candidate.get("category", "")).strip()
        if category not in self.ALLOWED_CATEGORIES:
            return None, "invalid_category"

        subject = str(candidate.get("subject", "")).strip()
        if len(subject) < 8 or len(subject) > 180:
            return None, "invalid_subject"
        if self._contains_blocked_terms(subject) or self.intelligence.is_sensitive(subject):
            return None, "sensitive_subject"

        stance = str(candidate.get("stance", "positive")).strip().lower()
        if stance not in {"positive", "negative"}:
            return None, "invalid_stance"

        try:
            confidence = float(candidate.get("confidence", 0.0))
        except (TypeError, ValueError):
            return None, "invalid_confidence"
        if confidence < 0.35:
            return None, "low_confidence"
        confidence = min(0.68, confidence)

        supporting = [
            str(signal_id)
            for signal_id in candidate.get("supporting_signal_ids", [])
            if str(signal_id) in valid_signal_ids
        ]
        supporting = list(dict.fromkeys(supporting))
        if len(supporting) < 2:
            return None, "insufficient_support"

        counters = [
            str(signal_id)
            for signal_id in candidate.get("counter_signal_ids", [])
            if str(signal_id) in valid_signal_ids
        ]
        counters = list(dict.fromkeys(counters))
        if counters and len(counters) >= len(supporting):
            return None, "counterevidence_dominates"
        if counters:
            conflict_ratio = len(counters) / (len(supporting) + len(counters))
            confidence = max(0.35, confidence * (1.0 - (0.5 * conflict_ratio)))

        reason = str(candidate.get("reason", "")).strip()[:220]
        if self._contains_blocked_terms(reason) or self.intelligence.is_sensitive(reason):
            return None, "sensitive_reason"

        return {
            "category": category,
            "subject": subject,
            "stance": stance,
            "confidence": confidence,
            "supporting_signal_ids": supporting,
            "counter_signal_ids": counters,
            "reason": reason,
        }, "accepted"

    def _validate_curiosity(self, candidate: Any) -> dict[str, Any] | None:
        if not isinstance(candidate, dict):
            return None
        question = str(candidate.get("question", "")).strip()
        reason = str(candidate.get("reason", "")).strip()
        if len(question) < 8 or len(question) > 220:
            return None
        combined = f"{question} {reason}"
        if self._contains_blocked_terms(combined) or self.intelligence.is_sensitive(combined):
            return None
        try:
            priority = float(candidate.get("priority", 0.5))
        except (TypeError, ValueError):
            priority = 0.5
        return {
            "question": question,
            "reason": reason[:180],
            "priority": max(0.0, min(1.0, priority)),
        }

    @staticmethod
    def _fingerprint(pattern: dict[str, Any]) -> str:
        canonical = "|".join([
            pattern["category"],
            pattern["subject"].strip().lower(),
            pattern["stance"],
            ",".join(sorted(pattern["supporting_signal_ids"])),
        ])
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]

    def run(self, *, force: bool = False) -> dict[str, Any]:
        readiness = self.should_reflect(force=force)
        if not readiness["ready"]:
            return {"status": "skipped", **readiness}

        state = self.load()
        signals = self._new_signals(state, force=force)
        valid_signal_ids = {str(signal.get("id")) for signal in signals if signal.get("id")}
        request = self._build_request(signals)

        try:
            response = self.gateway.generate(request)
        except Exception as exc:
            state["metrics"]["model_failures"] += 1
            self._save(state)
            return {
                "status": "error",
                "reason": "model_failure",
                "error": str(exc)[:220],
            }

        try:
            payload = self._parse_json(response.content)
        except (ValueError, json.JSONDecodeError) as exc:
            state["metrics"]["parse_failures"] += 1
            self._save(state)
            return {
                "status": "error",
                "reason": "invalid_model_payload",
                "error": str(exc)[:220],
            }

        accepted: list[dict[str, Any]] = []
        rejected: list[dict[str, Any]] = []
        known_fingerprints = set(state.get("accepted_fingerprints", []))

        for raw_candidate in payload.get("patterns", [])[:5]:
            pattern, verdict = self._validate_pattern(raw_candidate, valid_signal_ids)
            if pattern is None:
                rejected.append({"reason": verdict})
                continue
            fingerprint = self._fingerprint(pattern)
            if fingerprint in known_fingerprints:
                rejected.append({"reason": "duplicate"})
                continue

            result = self.intelligence.record_inference(
                category=f"reflection_{pattern['category']}",
                subject=pattern["subject"],
                stance=pattern["stance"],
                confidence=pattern["confidence"],
                reason=pattern["reason"],
                supporting_signal_ids=pattern["supporting_signal_ids"],
                counter_signal_ids=pattern["counter_signal_ids"],
                source="deep_reflection",
            )
            if not result.get("recorded"):
                rejected.append({"reason": result.get("reason", "not_recorded")})
                continue

            known_fingerprints.add(fingerprint)
            accepted.append({
                "fingerprint": fingerprint,
                "category": pattern["category"],
                "subject": pattern["subject"],
                "confidence": pattern["confidence"],
                "belief_key": result["belief"]["key"],
            })

        curiosity_added = 0
        for raw_gap in payload.get("curiosity", [])[:3]:
            gap = self._validate_curiosity(raw_gap)
            if not gap:
                continue
            if self.intelligence.record_curiosity_gap(
                question=gap["question"],
                reason=f"deep_reflection: {gap['reason']}",
                priority=gap["priority"],
            ):
                curiosity_added += 1

        now = self._now()
        direct_signals = self._direct_signals(self.intelligence.load())
        last_signal_id = direct_signals[-1].get("id") if direct_signals else None
        run_record = {
            "timestamp": now,
            "provider": response.provider_name,
            "model": response.model_name,
            "signals_reviewed": len(signals),
            "accepted": accepted,
            "rejected_count": len(rejected),
            "curiosity_added": curiosity_added,
        }

        state["last_success_at"] = now
        state["last_signal_id"] = last_signal_id
        state["accepted_fingerprints"] = list(known_fingerprints)[-500:]
        state["runs"].append(run_record)
        state["runs"] = state["runs"][-50:]
        state["metrics"]["runs"] += 1
        state["metrics"]["accepted_patterns"] += len(accepted)
        state["metrics"]["rejected_patterns"] += len(rejected)
        state["metrics"]["curiosity_gaps_added"] += curiosity_added
        self._save(state)

        return {
            "status": "completed",
            "signals_reviewed": len(signals),
            "accepted_patterns": len(accepted),
            "rejected_patterns": len(rejected),
            "curiosity_added": curiosity_added,
            "provider": response.provider_name,
            "model": response.model_name,
            "patterns": accepted,
        }

    def status(self) -> dict[str, Any]:
        state = self.load()
        readiness = self.should_reflect(force=False)
        return {
            "enabled": self.enabled,
            "last_success_at": state.get("last_success_at"),
            "last_signal_id": state.get("last_signal_id"),
            "readiness": readiness,
            "metrics": dict(state.get("metrics", {})),
            "recent_runs": state.get("runs", [])[-5:],
        }
