"""
ThSyr Operator Intelligence Engine.

Transforms each interaction into a small, auditable and revisable model of the
operator. It is intentionally separate from authentication/security. The goal
is personalization and continuity, not behavioral access control.

Design principles:
- explicit statements outrank inference;
- corrections outrank old beliefs;
- hypotheses are never promoted to facts without evidence;
- confidence decays with age;
- contradictions remain visible instead of being overwritten silently;
- sensitive personal domains and likely secrets are not learned here;
- only compact evidence snippets are persisted, never full conversations.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid4, uuid5

from .config import settings

SENSITIVE_TERMS = {
    "politica", "política", "politico", "político", "partido", "eleicao", "eleição", "voto",
    "bolsonaro", "lula", "religiao", "religião", "religioso", "igreja", "templo",
    "catolico", "católico", "evangelico", "evangélico", "saude", "saúde", "medico",
    "médico", "doenca", "doença", "diagnostico", "diagnóstico", "remedio", "remédio",
    "medicamento", "sexualidade", "orientacao sexual", "orientação sexual", "sexo",
    "sindicato", "etnia", "raca", "raça",
    "criminal", "antecedente",
}

SECRET_PATTERNS = (
    re.compile(r"(?i)\b(?:api[_ -]?key|token|password|senha|secret|credencial)\s*[:=]\s*\S+"),
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    re.compile(r"\b\d{11}\b"),
    re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
)


@dataclass
class OperatorSignal:
    id: str
    category: str
    subject: str
    stance: str
    confidence: float
    explicit: bool
    evidence: str
    source: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class OperatorBelief:
    key: str
    category: str
    subject: str
    stance: str
    confidence: float
    status: str
    support_weight: float
    oppose_weight: float
    evidence_count: int
    explicit_count: int
    first_seen: str
    last_seen: str
    evidence: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CuriosityGap:
    key: str
    question: str
    priority: float
    reason: str
    created_at: str
    updated_at: str
    status: str = "open"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class OperatorIntelligence:
    """Persistent operator model driven by evidence from real interactions."""

    VERSION = 1

    _explicit_patterns = (
        ("preference", "positive", 0.94, re.compile(
            r"(?i)\b(?:eu\s+)?(?<!n[aã]o\s)(?:prefiro|gosto|curto|adoro)\s+(?:de\s+)?(.{3,140})"
        )),
        ("preference", "negative", 0.96, re.compile(
            r"(?i)\b(?:eu\s+)?(?:n[aã]o\s+gosto|n[aã]o\s+curto|detesto|odeio)\s+(?:de\s+)?(.{3,140})"
        )),
        ("desire", "positive", 0.90, re.compile(
            r"(?i)\b(?:eu\s+)?(?<!n[aã]o\s)(?:quero|gostaria\s+de|eu\s+queria)\s+(.{3,140})"
        )),
        ("desire", "negative", 0.94, re.compile(
            r"(?i)\b(?:eu\s+)?(?:n[aã]o\s+quero|evite|n[aã]o\s+use)\s+(.{3,140})"
        )),
        ("tooling", "positive", 0.92, re.compile(
            r"(?i)\b(?:eu\s+)?uso\s+(?:hoje\s+)?(.{3,120})"
        )),
        ("routine", "positive", 0.88, re.compile(
            r"(?i)\b(?:eu\s+)?(?:trabalho|estudo|fa[çc]o)\s+(.{3,120})"
        )),
    )

    _working_style_patterns = (
        ("autonomy", "prefere execucao ponta a ponta sem confirmacoes triviais", 0.62,
         re.compile(r"(?i)\b(?:manda\s+bala|faz\s+completo|end\s*to\s*end|sem\s+ficar\s+perguntando)\b")),
        ("continuity", "valoriza continuidade, registro e reaproveitamento futuro", 0.64,
         re.compile(r"(?i)\b(?:deixa\s+registrado|documenta|documente|markdown|pra\s+depois|para\s+depois)\b")),
        ("verification", "prefere verificacao real antes de afirmacoes", 0.60,
         re.compile(r"(?i)\b(?:pesquise|verifique|confira|olhe\s+o\s+repo|analise\s+o\s+repo)\b")),
        ("quality_bar", "rejeita resultado generico e exige acabamento profissional", 0.68,
         re.compile(r"(?i)\b(?:gen[eé]rico|horr[ií]vel|profissional\s+de\s+verdade|n[ií]vel\s+master|bem\s+feito\s+mesmo)\b")),
    )

    _positive_feedback = re.compile(
        r"(?i)\b(?:gostei|ficou\s+(?:muito\s+)?bom|ficou\s+legal|perfeito|excelente|boa(?:z+)?|top)\b"
    )
    _negative_feedback = re.compile(
        r"(?i)\b(?:n[aã]o\s+gostei|ficou\s+ruim|horr[ií]vel|p[eé]ssimo|gen[eé]rico|bugado|errado|melhore)\b"
    )
    _correction = re.compile(
        r"(?i)(?:^|[.!?]\s*)\s*(?:n[aã]o[, ]|errado|n[aã]o\s+[eé]\s+isso|dnv|de\s+novo)"
    )

    def __init__(self, storage_path: str | Path | None = None):
        self.storage_path = (
            Path(storage_path)
            if storage_path
            else settings.brain.state_dir / "operator_intelligence.json"
        )

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @classmethod
    def _empty_state(cls) -> dict[str, Any]:
        return {
            "version": cls.VERSION,
            "beliefs": {},
            "signals": [],
            "curiosity": {},
            "metrics": {
                "interactions_observed": 0,
                "signals_extracted": 0,
                "surprises": 0,
                "sensitive_skips": 0,
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
        for key, default in self._empty_state().items():
            data.setdefault(key, default)
        return data

    def _save(self, state: dict[str, Any]) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    @staticmethod
    def _normalize_subject(value: str) -> str:
        subject = value.strip()
        subject = re.split(r"[\n.!?;]", subject, maxsplit=1)[0]
        subject = re.split(r"(?i)\s+(?:mas|por[eé]m|s[oó]\s+que)\s+", subject, maxsplit=1)[0]
        subject = re.sub(r"\s+", " ", subject).strip(" ,:-")
        return subject[:140]

    @staticmethod
    def _normalize_key(category: str, subject: str) -> str:
        key_subject = re.sub(r"[^a-z0-9]+", "_", subject.lower())
        return f"{category}:{key_subject.strip('_')[:100]}"

    @classmethod
    def _is_sensitive(cls, text: str) -> bool:
        lowered = text.lower()
        return any(term in lowered for term in SENSITIVE_TERMS)

    @classmethod
    def is_sensitive(cls, text: str) -> bool:
        """Public privacy gate shared by higher-order learning modules."""
        return cls._is_sensitive(text)

    @staticmethod
    def _redact(text: str) -> str:
        safe = text
        for pattern in SECRET_PATTERNS:
            safe = pattern.sub("[REDACTED]", safe)
        return safe[:180]

    def _make_signal(
        self,
        category: str,
        subject: str,
        stance: str,
        confidence: float,
        explicit: bool,
        evidence: str,
        source: str = "conversation",
    ) -> OperatorSignal | None:
        normalized = self._normalize_subject(subject)
        if len(normalized) < 3:
            return None
        combined = f"{category} {normalized} {evidence}"
        if self._is_sensitive(combined):
            return None
        return OperatorSignal(
            id=f"sig_{uuid4().hex[:12]}",
            category=category,
            subject=self._redact(normalized),
            stance=stance,
            confidence=max(0.0, min(1.0, confidence)),
            explicit=explicit,
            evidence=self._redact(evidence),
            source=source,
            created_at=self._now(),
        )

    def _extract_signals(
        self,
        message: str,
        context_subject: str | None = None,
        context_project: str | None = None,
    ) -> tuple[list[OperatorSignal], int]:
        signals: list[OperatorSignal] = []
        sensitive_skips = 0

        for category, stance, confidence, pattern in self._explicit_patterns:
            match = pattern.search(message)
            if not match:
                continue
            subject = self._normalize_subject(match.group(1))
            candidate = self._make_signal(
                category=category,
                subject=subject,
                stance=stance,
                confidence=confidence,
                explicit=True,
                evidence=match.group(0),
            )
            if candidate is None:
                sensitive_skips += 1
            else:
                signals.append(candidate)

        for key, summary, confidence, pattern in self._working_style_patterns:
            if not pattern.search(message):
                continue
            candidate = self._make_signal(
                category="working_style",
                subject=summary,
                stance="positive",
                confidence=confidence,
                explicit=False,
                evidence=pattern.search(message).group(0),
            )
            if candidate:
                signals.append(candidate)

        positive_feedback = self._positive_feedback.search(message)
        negative_feedback = self._negative_feedback.search(message)

        if positive_feedback:
            signal = self._make_signal(
                category="feedback_style",
                subject="fornece aprovacao curta quando o resultado atende a expectativa",
                stance="positive",
                confidence=0.52,
                explicit=False,
                evidence=positive_feedback.group(0),
            )
            if signal:
                signals.append(signal)

        if negative_feedback:
            signal = self._make_signal(
                category="feedback_style",
                subject="corrige diretamente quando o resultado fica abaixo da expectativa",
                stance="positive",
                confidence=0.58,
                explicit=False,
                evidence=negative_feedback.group(0),
            )
            if signal:
                signals.append(signal)

        context_target = context_subject or context_project
        if context_target and (positive_feedback or negative_feedback):
            verdict_signal = self._make_signal(
                category="context_feedback",
                subject=context_target,
                stance="negative" if negative_feedback else "positive",
                confidence=0.82,
                explicit=True,
                evidence=(negative_feedback or positive_feedback).group(0),
                source="contextual_feedback",
            )
            if verdict_signal:
                signals.append(verdict_signal)

        if self._correction.search(message):
            signal = self._make_signal(
                category="working_style",
                subject="correcoes explicitas devem sobrescrever inferencias anteriores",
                stance="positive",
                confidence=0.72,
                explicit=False,
                evidence=self._correction.search(message).group(0),
            )
            if signal:
                signals.append(signal)

        unique: dict[tuple[str, str, str], OperatorSignal] = {}
        for signal in signals:
            unique[(signal.category, signal.subject.lower(), signal.stance)] = signal
        return list(unique.values()), sensitive_skips

    @staticmethod
    def _effective_confidence(belief: dict[str, Any], now: datetime | None = None) -> float:
        now = now or datetime.now(timezone.utc)
        try:
            last_seen = datetime.fromisoformat(str(belief["last_seen"]))
            if last_seen.tzinfo is None:
                last_seen = last_seen.replace(tzinfo=timezone.utc)
        except (KeyError, TypeError, ValueError):
            return float(belief.get("confidence", 0.0))

        age_days = max(0.0, (now - last_seen).total_seconds() / 86400)
        explicit_count = int(belief.get("explicit_count", 0))
        half_life = 365.0 if explicit_count else 120.0
        decay = math.pow(0.5, age_days / half_life)
        floor = 0.45 if explicit_count else 0.20
        return max(floor, float(belief.get("confidence", 0.0)) * decay)

    @staticmethod
    def _recompute_belief(belief: dict[str, Any]) -> None:
        support = float(belief.get("support_weight", 0.0))
        oppose = float(belief.get("oppose_weight", 0.0))
        total = support + oppose
        evidence_count = int(belief.get("evidence_count", 0))
        explicit_count = int(belief.get("explicit_count", 0))

        if total <= 0:
            belief["confidence"] = 0.0
            belief["status"] = "hypothesis"
            return

        margin = abs(support - oppose) / total
        evidence_bonus = min(0.24, max(0, evidence_count - 1) * 0.04)
        explicit_bonus = min(0.22, explicit_count * 0.11)
        confidence = min(0.99, 0.42 + (0.28 * margin) + evidence_bonus + explicit_bonus)

        if support > oppose:
            belief["stance"] = "positive"
        elif oppose > support:
            belief["stance"] = "negative"
        else:
            belief["stance"] = "contested"

        conflict_ratio = min(support, oppose) / max(total, 0.001)
        if conflict_ratio >= 0.30:
            belief["status"] = "contested"
            confidence = min(confidence, 0.64)
        elif explicit_count >= 1 and confidence >= 0.78:
            belief["status"] = "confirmed"
        elif evidence_count >= 3 and confidence >= 0.72:
            belief["status"] = "probable"
        else:
            belief["status"] = "hypothesis"

        belief["confidence"] = round(confidence, 3)

    def _upsert_belief(
        self,
        state: dict[str, Any],
        signal: OperatorSignal,
    ) -> tuple[dict[str, Any], bool, bool]:
        key = self._normalize_key(signal.category, signal.subject)
        beliefs = state["beliefs"]
        now = signal.created_at
        existing = beliefs.get(key)
        is_new = existing is None
        surprise = False

        if existing is None:
            existing = OperatorBelief(
                key=key,
                category=signal.category,
                subject=signal.subject,
                stance=signal.stance,
                confidence=signal.confidence,
                status="confirmed" if signal.explicit and signal.confidence >= 0.90 else "hypothesis",
                support_weight=0.0,
                oppose_weight=0.0,
                evidence_count=0,
                explicit_count=0,
                first_seen=now,
                last_seen=now,
                evidence=[],
            ).to_dict()

        previous_stance = existing.get("stance")
        weight = signal.confidence * (1.25 if signal.explicit else 1.0)
        if signal.stance == "negative":
            existing["oppose_weight"] = float(existing.get("oppose_weight", 0.0)) + weight
        else:
            existing["support_weight"] = float(existing.get("support_weight", 0.0)) + weight

        existing["evidence_count"] = int(existing.get("evidence_count", 0)) + 1
        if signal.explicit:
            existing["explicit_count"] = int(existing.get("explicit_count", 0)) + 1
        existing["last_seen"] = now
        existing.setdefault("evidence", [])
        existing["evidence"].append({
            "signal_id": signal.id,
            "snippet": signal.evidence,
            "created_at": signal.created_at,
            "stance": signal.stance,
        })
        existing["evidence"] = existing["evidence"][-8:]

        self._recompute_belief(existing)
        if previous_stance in {"positive", "negative"} and existing["stance"] != previous_stance:
            surprise = True
        if existing["status"] == "contested":
            surprise = True

        beliefs[key] = existing
        self._update_curiosity(state, existing, surprise)
        return existing, is_new, surprise

    def _update_curiosity(
        self,
        state: dict[str, Any],
        belief: dict[str, Any],
        surprise: bool,
    ) -> None:
        curiosity = state["curiosity"]
        key = belief["key"]
        now = self._now()

        if belief["status"] == "confirmed" and not surprise:
            if key in curiosity:
                curiosity[key]["status"] = "resolved"
                curiosity[key]["updated_at"] = now
            return

        if belief["status"] == "contested":
            question = (
                f"Ha sinais conflitantes sobre '{belief['subject']}'. "
                "Priorizar a proxima evidencia explicita e contextual antes de personalizar com isso."
            )
            priority = 0.95
            reason = "contradiction"
        elif belief["status"] == "hypothesis":
            question = (
                f"Observar se '{belief['subject']}' e um padrao estavel ou apenas contextual. "
                "Nao perguntar sem necessidade; confirmar organicamente por repeticao."
            )
            priority = 0.55
            reason = "low_confidence"
        else:
            return

        existing = curiosity.get(key)
        created_at = existing.get("created_at", now) if existing else now
        curiosity[key] = CuriosityGap(
            key=key,
            question=question,
            priority=priority,
            reason=reason,
            created_at=created_at,
            updated_at=now,
        ).to_dict()

    def observe(
        self,
        message: str,
        source: str = "conversation",
        context_subject: str | None = None,
        context_project: str | None = None,
    ) -> dict[str, Any]:
        state = self.load()
        state["metrics"]["interactions_observed"] += 1

        signals, sensitive_skips = self._extract_signals(
            message,
            context_subject=context_subject,
            context_project=context_project,
        )
        state["metrics"]["sensitive_skips"] += sensitive_skips

        new_beliefs = 0
        updated_beliefs = 0
        surprises = 0
        touched: list[dict[str, Any]] = []

        for signal in signals:
            signal.source = source
            belief, is_new, surprise = self._upsert_belief(state, signal)
            state["signals"].append(signal.to_dict())
            new_beliefs += int(is_new)
            updated_beliefs += int(not is_new)
            surprises += int(surprise)
            touched.append({
                "key": belief["key"],
                "status": belief["status"],
                "confidence": belief["confidence"],
                "subject": belief["subject"],
            })

        state["signals"] = state["signals"][-1000:]
        state["metrics"]["signals_extracted"] += len(signals)
        state["metrics"]["surprises"] += surprises
        self._save(state)

        information_gain = min(
            1.0,
            (new_beliefs * 0.30)
            + (updated_beliefs * 0.08)
            + (surprises * 0.35)
            + min(0.20, len(signals) * 0.04),
        )
        return {
            "signals": len(signals),
            "new_beliefs": new_beliefs,
            "updated_beliefs": updated_beliefs,
            "surprises": surprises,
            "sensitive_skips": sensitive_skips,
            "information_gain": round(information_gain, 3),
            "touched": touched,
        }

    def record_feedback(
        self,
        subject: str,
        verdict: str,
        reason: str = "",
        category: str = "preference",
    ) -> dict[str, Any]:
        normalized = verdict.strip().lower()
        if normalized not in {"approved", "rejected"}:
            raise ValueError("verdict deve ser 'approved' ou 'rejected'")
        stance = "positive" if normalized == "approved" else "negative"
        evidence = f"{normalized}: {subject}" + (f" - {reason}" if reason else "")
        signal = self._make_signal(
            category=category,
            subject=subject,
            stance=stance,
            confidence=0.98,
            explicit=True,
            evidence=evidence,
            source="explicit_feedback",
        )
        if signal is None:
            return {"recorded": False, "reason": "sensitive_or_invalid"}

        state = self.load()
        belief, is_new, surprise = self._upsert_belief(state, signal)
        state["signals"].append(signal.to_dict())
        state["signals"] = state["signals"][-1000:]
        state["metrics"]["signals_extracted"] += 1
        state["metrics"]["surprises"] += int(surprise)
        self._save(state)
        return {
            "recorded": True,
            "new_belief": is_new,
            "surprise": surprise,
            "belief": belief,
        }

    def record_inference(
        self,
        category: str,
        subject: str,
        stance: str,
        confidence: float,
        reason: str,
        supporting_signal_ids: list[str],
        counter_signal_ids: list[str] | None = None,
        source: str = "deep_reflection",
    ) -> dict[str, Any]:
        """Record a model-derived hypothesis without allowing it to masquerade as fact."""
        if stance not in {"positive", "negative"}:
            return {"recorded": False, "reason": "invalid_stance"}
        if not supporting_signal_ids or len(set(supporting_signal_ids)) < 2:
            return {"recorded": False, "reason": "insufficient_support"}

        state = self.load()
        known_ids = {str(signal.get("id")) for signal in state.get("signals", [])}
        support = [signal_id for signal_id in dict.fromkeys(supporting_signal_ids) if signal_id in known_ids]
        counters = [
            signal_id
            for signal_id in dict.fromkeys(counter_signal_ids or [])
            if signal_id in known_ids
        ]
        if len(support) < 2:
            return {"recorded": False, "reason": "unknown_support"}

        evidence = (
            f"reflection based on {', '.join(support[:6])}"
            + (f"; counters: {', '.join(counters[:4])}" if counters else "")
            + (f"; reason: {reason}" if reason else "")
        )
        signal = self._make_signal(
            category=category,
            subject=subject,
            stance=stance,
            confidence=min(0.68, max(0.35, confidence)),
            explicit=False,
            evidence=evidence,
            source=source,
        )
        if signal is None:
            return {"recorded": False, "reason": "sensitive_or_invalid"}

        belief, is_new, surprise = self._upsert_belief(state, signal)
        state["signals"].append(signal.to_dict())
        state["signals"] = state["signals"][-1000:]
        state["metrics"]["signals_extracted"] += 1
        state["metrics"]["surprises"] += int(surprise)
        self._save(state)
        return {
            "recorded": True,
            "new_belief": is_new,
            "surprise": surprise,
            "belief": belief,
            "signal_id": signal.id,
        }

    def record_curiosity_gap(
        self,
        question: str,
        reason: str,
        priority: float = 0.5,
    ) -> bool:
        """Persist a safe observation gap proposed by deep reflection."""
        normalized = re.sub(r"\s+", " ", question).strip()
        if len(normalized) < 8 or self._is_sensitive(f"{normalized} {reason}"):
            return False
        digest = uuid5(NAMESPACE_URL, normalized.lower()).hex[:16]
        key = f"reflection_gap:{digest}"
        state = self.load()
        now = self._now()
        existing = state["curiosity"].get(key)
        state["curiosity"][key] = CuriosityGap(
            key=key,
            question=self._redact(normalized),
            priority=max(0.0, min(1.0, float(priority))),
            reason=self._redact(reason or "deep_reflection"),
            created_at=existing.get("created_at", now) if existing else now,
            updated_at=now,
            status="open",
        ).to_dict()
        self._save(state)
        return True

    def forget(self, belief_key: str) -> bool:
        state = self.load()
        removed = state["beliefs"].pop(belief_key, None) is not None
        state["curiosity"].pop(belief_key, None)
        if removed:
            state["signals"] = [
                signal for signal in state["signals"]
                if self._normalize_key(
                    str(signal.get("category", "")),
                    str(signal.get("subject", "")),
                ) != belief_key
            ]
            self._save(state)
        return removed

    @staticmethod
    def _query_terms(query: str) -> set[str]:
        return {
            token
            for token in re.findall(r"[a-zA-Z0-9À-ÿ]{3,}", query.lower())
            if token not in {"para", "com", "uma", "que", "isso", "como", "mais", "por"}
        }

    def relevant_beliefs(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        state = self.load()
        q_terms = self._query_terms(query)
        ranked: list[tuple[float, dict[str, Any]]] = []

        for belief in state["beliefs"].values():
            if belief.get("status") == "contested":
                continue
            effective = self._effective_confidence(belief)
            if effective < 0.45:
                continue
            text = f"{belief.get('category', '')} {belief.get('subject', '')}".lower()
            overlap = sum(1 for term in q_terms if term in text)
            if (
                str(belief.get("category", "")).startswith("reflection_")
                and belief.get("status") == "hypothesis"
                and overlap == 0
            ):
                continue
            relevance = effective + min(0.45, overlap * 0.15)
            if belief.get("status") == "confirmed":
                relevance += 0.12
            ranked.append((relevance, {**belief, "effective_confidence": round(effective, 3)}))

        ranked.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in ranked[: max(1, limit)]]

    def build_context(self, query: str, limit: int = 8) -> str:
        beliefs = self.relevant_beliefs(query, limit=limit)
        state = self.load()
        q_terms = self._query_terms(query)
        open_gaps = []
        for gap in state["curiosity"].values():
            if gap.get("status") != "open":
                continue
            key = str(gap.get("key", ""))
            if key.startswith("reflection_"):
                gap_text = f"{gap.get('question', '')} {gap.get('reason', '')}".lower()
                if not any(term in gap_text for term in q_terms):
                    continue
            open_gaps.append(gap)
        open_gaps.sort(key=lambda gap: float(gap.get("priority", 0.0)), reverse=True)

        lines = [
            "# OPERATOR INTELLIGENCE — MODELO DINAMICO E REVISAVEL",
            "Use somente como personalizacao contextual. Nao trate hipotese como fato.",
            "Declaracoes explicitas e correcoes recentes vencem inferencias antigas.",
            "Nao use este modelo para autenticacao, controle de acesso ou inferencia sensivel.",
        ]

        if beliefs:
            lines.append("\n## SINAIS RELEVANTES")
            for belief in beliefs:
                stance = "favorece" if belief["stance"] == "positive" else "evita"
                lines.append(
                    f"- [{belief['status']} | conf {belief['effective_confidence']:.2f}] "
                    f"{belief['category']}: {stance} {belief['subject']}"
                )
        else:
            lines.append("\n## SINAIS RELEVANTES\n- Nenhum sinal dinamico suficientemente confiavel para esta consulta.")

        if open_gaps:
            lines.append("\n## LACUNAS DE CURIOSIDADE")
            lines.append("Observe estas lacunas silenciosamente; pergunte apenas se forem essenciais para a tarefa.")
            for gap in open_gaps[:3]:
                lines.append(f"- {gap['question']}")

        return "\n".join(lines)

    def status(self) -> dict[str, Any]:
        state = self.load()
        beliefs = list(state["beliefs"].values())
        open_gaps = [
            gap for gap in state["curiosity"].values()
            if gap.get("status") == "open"
        ]
        return {
            "version": state["version"],
            "storage": str(self.storage_path),
            "beliefs_total": len(beliefs),
            "confirmed": sum(1 for b in beliefs if b.get("status") == "confirmed"),
            "probable": sum(1 for b in beliefs if b.get("status") == "probable"),
            "hypotheses": sum(1 for b in beliefs if b.get("status") == "hypothesis"),
            "contested": sum(1 for b in beliefs if b.get("status") == "contested"),
            "open_curiosity_gaps": len(open_gaps),
            "metrics": dict(state["metrics"]),
        }

    def snapshot(self) -> dict[str, Any]:
        state = self.load()
        beliefs = list(state["beliefs"].values())
        beliefs.sort(
            key=lambda belief: self._effective_confidence(belief),
            reverse=True,
        )
        return {
            "status": self.status(),
            "beliefs": beliefs,
            "curiosity": list(state["curiosity"].values()),
        }
