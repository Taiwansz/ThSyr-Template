"""
ThSyr Local Vector Store & Embedded Dense Index
Implementa busca semantica vetorial local embutida via SQLite:
- Geracao e normalizacao de embeddings densos offline (n-gram semantic hashing + TF-IDF)
- Suporte a injecao de vetores externos de modelos neurais
- Calculo de similaridade de cosseno em tempo de consulta
- Persistencia local ACID sem dependencia de servicos externos de nuvem
"""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator

from .config import settings, setup_logger
from .embeddings import LayeredEmbeddingEngine

logger = setup_logger("vector_store")


class LocalVectorStore:
    DEFAULT_DIM = 128

    def __init__(
        self,
        db_path: Path | None = None,
        dim: int = DEFAULT_DIM,
        embedding_engine: LayeredEmbeddingEngine | None = None,
    ):
        self.db_path = db_path or (settings.brain.state_dir / "vector_index.db")
        self.dim = dim
        self.embedding_engine = embedding_engine or LayeredEmbeddingEngine(dim=dim)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(str(self.db_path))

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = self._get_connection()
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Cria tabelas do indice vetorial."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    id TEXT PRIMARY KEY,
                    text TEXT NOT NULL,
                    metadata_json TEXT,
                    vector_json TEXT NOT NULL,
                    dim INTEGER NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def compute_embedding(self, text: str) -> list[float]:
        """Generate a normalized vector using the configured layered backend."""
        return self.embedding_engine.embed(text)

    def embedding_status(self) -> dict[str, Any]:
        return self.embedding_engine.status()

    @staticmethod
    def cosine_similarity(v1: list[float], v2: list[float]) -> float:
        """Calcula a similaridade de cosseno entre dois vetores normalizados."""
        if len(v1) != len(v2) or not v1:
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        return round(float(dot), 6)

    def upsert(
        self,
        doc_id: str,
        text: str,
        metadata: dict[str, Any] | None = None,
        vector: list[float] | None = None
    ) -> None:
        """Insere ou atualiza um documento no indice vetorial."""
        v = vector if (vector and len(vector) == self.dim) else self.compute_embedding(text)
        meta_json = json.dumps(metadata or {}, ensure_ascii=False)
        vec_json = json.dumps(v)
        now = datetime.now(timezone.utc).isoformat()

        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO embeddings (id, text, metadata_json, vector_json, dim, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (doc_id, text, meta_json, vec_json, self.dim, now))
            conn.commit()

    def search(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.0
    ) -> list[dict[str, Any]]:
        """Busca os documentos mais similares a query por distancia de cosseno."""
        q_vec = self.compute_embedding(query)
        results: list[tuple[float, str, str, dict[str, Any]]] = []

        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, text, metadata_json, vector_json FROM embeddings WHERE dim = ?", (self.dim,))
            rows = cursor.fetchall()

            for doc_id, text, meta_raw, vec_raw in rows:
                try:
                    vec = json.loads(vec_raw)
                    sim = self.cosine_similarity(q_vec, vec)
                    if sim >= min_score:
                        meta = json.loads(meta_raw)
                        results.append((sim, doc_id, text, meta))
                except Exception:
                    continue

        # Ordenar por similaridade decrescente
        results.sort(key=lambda r: r[0], reverse=True)

        return [
            {
                "id": r[1],
                "score": r[0],
                "text": r[2],
                "metadata": r[3]
            }
            for r in results[:top_k]
        ]

    def count(self) -> int:
        """Retorna o numero total de documentos vetorizados."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM embeddings")
            return int(cursor.fetchone()[0])

    def clear(self) -> None:
        """Remove todos os documentos indexados."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM embeddings")
            conn.commit()

    def ingest_markdown_knowledge(self, paths: list[Path] | None = None) -> int:
        """Ingere e vetoriza notas markdown do cerebro e do cofre academico."""
        if paths is None:
            brain_dir = settings.brain.brain_dir
            vault_dir = settings.academic.vault_path
            paths = [
                brain_dir / "nodes",
                brain_dir / "lobes",
                brain_dir / "standards",
                vault_dir / "01 - Disciplinas"
            ]

        count = 0
        for base in paths:
            if not base or not base.exists():
                continue
            for md_file in base.rglob("*.md"):
                if md_file.name.startswith("."):
                    continue
                try:
                    content = md_file.read_text(encoding="utf-8", errors="ignore").strip()
                    if not content or len(content) < 20:
                        continue
                    doc_id = f"doc:{md_file.stem}"
                    meta = {
                        "path": str(md_file),
                        "filename": md_file.name,
                        "source": base.name
                    }
                    self.upsert(doc_id=doc_id, text=content[:4000], metadata=meta)
                    count += 1
                except Exception as e:
                    logger.warning(f"Falha ao vetorizar {md_file}: {e}")
        return count
