"""
ThSyr News Engine (A Gazeta Tecnológica Global)
Fachada principal e orquestrador de publicação do periódico diário.
Zero dependencias externas frageis e zero emojis.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from .archiver import NewsArchiver
from .collector import NewsCollector
from .compiler import NewsCompiler
from .models import (
    EarBox,
    FeatureCard,
    LeadStory,
    MarketQuote,
    NewsBundle,
    RawFeedItem,
    SecondaryLead,
    WireDispatch,
)
from .pipeline import NewsPipeline


class NewsEngine:
    """
    Fachada executiva do motor autônomo de publicação da Gazeta Tecnológica Global.
    """

    def __init__(
        self,
        collector: NewsCollector | None = None,
        compiler: NewsCompiler | None = None,
        archiver: NewsArchiver | None = None,
        pipeline: NewsPipeline | None = None,
    ):
        self.collector = collector or NewsCollector()
        self.compiler = compiler or NewsCompiler()
        self.archiver = archiver or NewsArchiver()
        self.pipeline = pipeline or NewsPipeline(
            collector=self.collector,
            compiler=self.compiler,
            archiver=self.archiver,
        )

    def fetch(self, offline: bool = False, target_date: date | None = None) -> NewsBundle:
        """Coleta despachos e constroi o pacote editorial estruturado."""
        return self.collector.collect(target_date=target_date, offline=offline)

    def compile(
        self,
        bundle: NewsBundle | None = None,
        target_date: date | None = None,
        offline: bool = False,
    ) -> str:
        """Compila o broadsheet em HTML puro."""
        if bundle is None:
            bundle = self.fetch(offline=offline, target_date=target_date)
        return self.compiler.compile(bundle)

    def publish(
        self,
        target_date: date | None = None,
        force: bool = False,
        offline: bool = False,
    ) -> dict[str, Any]:
        """Executa a pipeline completa e publica a edicao no acervo."""
        return self.pipeline.run(target_date=target_date, force=force, offline=offline)

    def list_editions(self) -> list[dict[str, Any]]:
        """Lista todas as edicoes historicas preservadas."""
        return self.archiver.list_editions()

    def status(self) -> dict[str, Any]:
        """Retorna o diagnostico do acervo e da edicao ativa."""
        editions = self.list_editions()
        latest = self.archiver.get_latest_edition()
        index_exists = self.archiver.index_path.is_file()
        index_size = self.archiver.index_path.stat().st_size if index_exists else 0

        today = datetime.now().date()
        today_edition_path = self.archiver.get_edition_by_date(today)

        return {
            "name": "A Gazeta Tecnológica Global",
            "active_edition_path": str(self.archiver.index_path),
            "index_exists": index_exists,
            "index_size_bytes": index_size,
            "total_editions": len(editions),
            "latest_edition": latest,
            "today": today.isoformat(),
            "today_published": today_edition_path is not None,
            "today_edition_path": str(today_edition_path) if today_edition_path else None,
            "configured_feeds_count": len(self.collector.feeds),
        }


__all__ = [
    "EarBox",
    "FeatureCard",
    "LeadStory",
    "MarketQuote",
    "NewsArchiver",
    "NewsBundle",
    "NewsCollector",
    "NewsCompiler",
    "NewsEngine",
    "NewsPipeline",
    "RawFeedItem",
    "SecondaryLead",
    "WireDispatch",
]
