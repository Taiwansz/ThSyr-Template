"""
Memoria de gosto visual do operador.

Nao "treina" o modelo. Ela cria memoria explicita, auditavel e reversivel de
aprovacoes e rejeicoes para ser injetada nos briefs futuros.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from ..config import settings


@dataclass
class TasteEntry:
    id: str
    verdict: str
    artifact_kind: str
    reference: str
    notes: str
    tags: list[str]
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class TasteMemory:
    VALID_VERDICTS = {"approved", "rejected"}

    def __init__(self, storage_path: str | Path | None = None):
        self.storage_path = Path(storage_path) if storage_path else settings.brain.state_dir / "visual_taste_memory.json"

    def _empty(self) -> dict[str, Any]:
        return {"version": 1, "entries": []}

    def load(self) -> dict[str, Any]:
        if not self.storage_path.exists():
            return self._empty()
        try:
            data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return self._empty()
        if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
            return self._empty()
        return data

    def _save(self, data: dict[str, Any]) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def record(
        self,
        verdict: str,
        artifact_kind: str,
        reference: str,
        notes: str = "",
        tags: list[str] | None = None,
    ) -> TasteEntry:
        normalized = verdict.strip().lower()
        if normalized not in self.VALID_VERDICTS:
            raise ValueError(f"verdict deve ser um de: {sorted(self.VALID_VERDICTS)}")
        if not reference.strip():
            raise ValueError("reference nao pode ser vazia")

        entry = TasteEntry(
            id=str(uuid4()),
            verdict=normalized,
            artifact_kind=artifact_kind.strip().lower() or "other",
            reference=reference.strip(),
            notes=notes.strip(),
            tags=sorted({tag.strip().lower() for tag in (tags or []) if tag.strip()}),
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        data = self.load()
        entries = data["entries"]
        # Evita inflar a memoria com o mesmo exemplo repetido.
        entries = [
            old for old in entries
            if not (
                old.get("verdict") == entry.verdict
                and old.get("artifact_kind") == entry.artifact_kind
                and old.get("reference") == entry.reference
                and old.get("notes") == entry.notes
            )
        ]
        entries.append(entry.to_dict())
        data["entries"] = entries[-500:]
        self._save(data)
        return entry

    def entries_for(self, artifact_kind: str, limit: int = 12) -> list[dict[str, Any]]:
        target = artifact_kind.strip().lower()
        entries = self.load()["entries"]
        filtered = [e for e in entries if e.get("artifact_kind") in {target, "other"}]
        return filtered[-max(1, limit):]

    def build_context(self, artifact_kind: str, limit: int = 12) -> str:
        entries = self.entries_for(artifact_kind, limit=limit)
        approved = [e for e in entries if e.get("verdict") == "approved"]
        rejected = [e for e in entries if e.get("verdict") == "rejected"]

        lines = [
            "MEMORIA DE GOSTO DO OPERADOR",
            "Use estes exemplos como evidencia de preferencia, nao como template para copiar.",
            "",
            "APROVADOS:",
        ]
        if approved:
            for e in approved:
                lines.append(f"- {e.get('reference')}: {e.get('notes') or 'aprovado sem nota adicional'}")
        else:
            lines.append("- Nenhum exemplo aprovado registrado para este tipo.")

        lines.extend(["", "REJEITADOS:"])
        if rejected:
            for e in rejected:
                lines.append(f"- {e.get('reference')}: {e.get('notes') or 'rejeitado sem nota adicional'}")
        else:
            lines.append("- Nenhum exemplo rejeitado registrado para este tipo.")

        return "\n".join(lines)

    def stats(self) -> dict[str, int]:
        entries = self.load()["entries"]
        return {
            "total": len(entries),
            "approved": sum(1 for e in entries if e.get("verdict") == "approved"),
            "rejected": sum(1 for e in entries if e.get("verdict") == "rejected"),
        }
