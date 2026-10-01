"""
ThSyr News Pipeline
Orquestradora central do ciclo autonomo de publicacao da Gazeta Tecnologica Global:
Coleta (RSS/Atom/Sintese) -> Compilacao (Broadsheet HTML) -> Arquivamento (Edicoes e Index).
Zero dependencias externas frageis e zero emojis.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from ..config import setup_logger
from .archiver import NewsArchiver
from .collector import NewsCollector
from .compiler import NewsCompiler

logger = setup_logger("news_pipeline")


class NewsPipeline:
    """Pipeline orquestradora do ciclo editorial."""

    def __init__(
        self,
        collector: NewsCollector | None = None,
        compiler: NewsCompiler | None = None,
        archiver: NewsArchiver | None = None,
    ):
        self.collector = collector or NewsCollector()
        self.compiler = compiler or NewsCompiler()
        self.archiver = archiver or NewsArchiver()

    def run(
        self,
        target_date: date | None = None,
        force: bool = False,
        offline: bool = False,
    ) -> dict[str, Any]:
        """
        Executa o ciclo completo de publicacao.
        Se force=False e a edicao do dia ja existir, pula a geracao para evitar reescrita desnecessaria.
        """
        ed_date = target_date or datetime.now().date()
        date_str = ed_date.isoformat()

        # Verificar se a edicao ja esta publicada
        existing_path = self.archiver.get_edition_by_date(ed_date)
        if existing_path and not force:
            logger.info(f"Edicao de {date_str} ja existente em {existing_path}. Pulando ciclo.")
            return {
                "status": "already_exists",
                "action_taken": "skipped",
                "date": date_str,
                "edition_path": str(existing_path),
                "index_path": str(self.archiver.index_path),
            }

        logger.info(f"Iniciando ciclo de publicacao para {date_str} (offline={offline}, force={force})...")

        # 1. Coleta e sintese estruturada
        bundle = self.collector.collect(target_date=ed_date, offline=offline)

        # 2. Compilacao do broadsheet em HTML puro
        html_content = self.compiler.compile(bundle)

        # 3. Arquivamento e sincronizacao do index
        saved_path = self.archiver.save_edition(ed_date, html_content)

        stories_count = 2 + len(bundle.features) + len(bundle.wire_dispatches)
        size_bytes = len(html_content.encode("utf-8"))

        logger.info(
            f"Publicacao concluida com exito. Edicao Nº {bundle.edition_number}, "
            f"Historias: {stories_count}, Bytes: {size_bytes}."
        )

        return {
            "status": "success",
            "action_taken": "published",
            "date": date_str,
            "edition_number": bundle.edition_number,
            "edition_path": str(saved_path),
            "index_path": str(self.archiver.index_path),
            "headline": bundle.lead_story.headline,
            "stories_count": stories_count,
            "size_bytes": size_bytes,
        }
