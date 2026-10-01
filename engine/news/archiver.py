"""
ThSyr News Archiver
Gerenciamento de acervo histórico de edições da Gazeta Tecnológica Global.
Preserva as publicações diárias em news/editions/YYYY-MM-DD_a_gazeta_tecnologica.html
e sincroniza o ponto de entrada canônico em news/index.html. Zero emojis.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

from ..config import PROJECT_ROOT, setup_logger

logger = setup_logger("news_archiver")

DEFAULT_NEWS_DIR = PROJECT_ROOT / "news"


class NewsArchiver:
    """Gerenciador de acervo e arquivos da Gazeta Tecnológica Global."""

    def __init__(self, news_dir: Path | None = None):
        self.news_dir = Path(news_dir) if news_dir else DEFAULT_NEWS_DIR
        self.editions_dir = self.news_dir / "editions"
        self.index_path = self.news_dir / "index.html"
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Garante a existencia dos diretorios de destino."""
        self.news_dir.mkdir(parents=True, exist_ok=True)
        self.editions_dir.mkdir(parents=True, exist_ok=True)

    def get_edition_filename(self, target_date: date) -> str:
        """Gera o nome de arquivo padronizado para a edicao."""
        return f"{target_date.isoformat()}_a_gazeta_tecnologica.html"

    def get_edition_by_date(self, target_date: date) -> Path | None:
        """Retorna o caminho da edicao se ela ja existir no acervo, ou None."""
        filename = self.get_edition_filename(target_date)
        file_path = self.editions_dir / filename
        return file_path if file_path.is_file() else None

    def save_edition(self, target_date: date, html_content: str) -> Path:
        """
        Salva o arquivo da edicao no acervo historico e sincroniza
        imediatamente o arquivo mestre news/index.html.
        """
        self._ensure_directories()
        filename = self.get_edition_filename(target_date)
        edition_path = self.editions_dir / filename

        # 1. Grava no acervo historico com codificacao UTF-8
        edition_path.write_text(html_content, encoding="utf-8")
        logger.info(f"Edicao arquivada com sucesso: {edition_path}")

        # 2. Sincroniza o arquivo mestre index.html
        self.index_path.write_text(html_content, encoding="utf-8")
        logger.info(f"Ponto de entrada mestre sincronizado: {self.index_path}")

        return edition_path

    def list_editions(self) -> list[dict[str, Any]]:
        """
        Lista todas as edicoes presentes no acervo em ordem cronologica decrescente.
        """
        if not self.editions_dir.is_dir():
            return []

        editions: list[dict[str, Any]] = []
        pattern = re.compile(r"^(\d{4}-\d{2}-\d{2})_a_gazeta_tecnologica\.html$")

        for item in self.editions_dir.glob("*_a_gazeta_tecnologica.html"):
            match = pattern.match(item.name)
            if match:
                date_str = match.group(1)
                stat = item.stat()
                editions.append(
                    {
                        "date": date_str,
                        "filename": item.name,
                        "path": str(item),
                        "size": stat.st_size,
                        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    }
                )

        # Ordenar da mais recente para a mais antiga
        editions.sort(key=lambda x: x["date"], reverse=True)
        return editions

    def get_latest_edition(self) -> dict[str, Any] | None:
        """Retorna os metadados da edicao mais recente arquivada."""
        editions = self.list_editions()
        return editions[0] if editions else None
