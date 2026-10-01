"""
ThSyr News Engine Models
Modelos de dados estruturados para a publicacao da Gazeta Tecnologica Global.
Formato broadsheet historico puro, sem dependencias externas frageis e com zero emojis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass
class RawFeedItem:
    """Item bruto extraido de feed RSS ou Atom."""
    title: str
    link: str
    summary: str
    published: str
    source: str


@dataclass
class EarBox:
    """Caixa de destaque lateral do masthead (orelhas do jornal)."""
    kicker: str
    text: str

    def to_dict(self) -> dict[str, Any]:
        return {"kicker": self.kicker, "text": self.text}


@dataclass
class LeadStory:
    """Manchete e artigo principal do broadsheet."""
    kicker: str
    headline: str
    subheadline: str
    byline: str
    dateline: str
    date_str: str
    paragraphs: list[str]
    pull_quote: str
    source_note: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "kicker": self.kicker,
            "headline": self.headline,
            "subheadline": self.subheadline,
            "byline": self.byline,
            "dateline": self.dateline,
            "date_str": self.date_str,
            "paragraphs": self.paragraphs,
            "pull_quote": self.pull_quote,
            "source_note": self.source_note,
        }


@dataclass
class SecondaryLead:
    """Artigo de segundo impacto da coluna principal."""
    kicker: str
    headline: str
    subheadline: str
    paragraphs: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "kicker": self.kicker,
            "headline": self.headline,
            "subheadline": self.subheadline,
            "paragraphs": self.paragraphs,
        }


@dataclass
class FeatureCard:
    """Artigo aprofundado para as colunas de litografia, EDA e fabricacao."""
    kicker: str
    headline: str
    subheadline: str
    paragraphs: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "kicker": self.kicker,
            "headline": self.headline,
            "subheadline": self.subheadline,
            "paragraphs": self.paragraphs,
        }


@dataclass
class WireDispatch:
    """Despacho telegráfico sucinto de agência global."""
    timestamp_str: str
    title: str
    description: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp_str": self.timestamp_str,
            "title": self.title,
            "description": self.description,
        }


@dataclass
class MarketQuote:
    """Cotacao financeira ou telemetria de mercado de capitais."""
    name: str
    price: str
    change: str
    is_positive: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "price": self.price,
            "change": self.change,
            "is_positive": self.is_positive,
        }


@dataclass
class NewsBundle:
    """Pacote editorial consolidado para diagramacao do broadsheet."""
    date: date
    edition_number: int
    volume: str = "VOLUME CLXXV"
    price_cents: int = 25
    circulation_str: str = "EDIÇÃO INTERNACIONAL &bull; DISTRIBUIÇÃO CONJUNTA"
    left_ear: EarBox = field(default_factory=lambda: EarBox(
        kicker="INFRAESTRUTURA & CAPITAL",
        text="Aportes globais em capacidade computacional e energia ininterrupta aceleram expansao de hiperscalers."
    ))
    right_ear: EarBox = field(default_factory=lambda: EarBox(
        kicker="LITOGRAFIA & ESCALA",
        text="Avanco em nos sub-2nm e maquinas High-NA consolida hegemonia de fundicoes avancadas."
    ))
    lead_story: LeadStory = field(default_factory=lambda: LeadStory(
        kicker="// FRONTEIRA DA INFRAESTRUTURA COMPUTACIONAL",
        headline="SUPERCICLO DE IA ELEVA INVESTIMENTOS GLOBAIS EM CHIPS AO PATAMAR DE UM TRILHAO DE DOLARES",
        subheadline="Conglomerados globais ampliam captacoes para assegurar silicio avancado e matrizes energeticas continuas.",
        byline="BUREAU GLOBAL DE FINANCAS E CHIPS",
        dateline="TOQUIO & NOVA YORK",
        date_str="",
        paragraphs=[],
        pull_quote="",
        source_note="Bureau Global / Reuters & Nikkei Asia",
    ))
    secondary_lead: SecondaryLead = field(default_factory=lambda: SecondaryLead(
        kicker="// ENERGIA & MATRIZ ELETRICA",
        headline="REATOR NUCLEAR DEDICADO E REATIVADO PARA SUPRIR CLUSTERS DE ALTA DENSIDADE",
        subheadline="Contratos bilaterais de compra de energia garantem gigawatts estaveis para hiperescala.",
        paragraphs=[],
    ))
    features: list[FeatureCard] = field(default_factory=list)
    wire_dispatches: list[WireDispatch] = field(default_factory=list)
    market_quotes: list[MarketQuote] = field(default_factory=list)
    editorial_note: str = (
        "A Gazeta Tecnologica Global e impressa diariamente a partir de despachos telegraficos "
        "transmitidos pelos bureaux de Toquio, Hsinchu, Veldhoven, Santa Clara e Washington. "
        "Todas as informacoes publicadas atendem a rigorosos padroes de verificacao tecnica, "
        "custodia criptografica de fontes e independencia factual absoluta."
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "date": self.date.isoformat(),
            "edition_number": self.edition_number,
            "volume": self.volume,
            "price_cents": self.price_cents,
            "left_ear": self.left_ear.to_dict(),
            "right_ear": self.right_ear.to_dict(),
            "lead_story": self.lead_story.to_dict(),
            "secondary_lead": self.secondary_lead.to_dict(),
            "features": [f.to_dict() for f in self.features],
            "wire_dispatches": [w.to_dict() for w in self.wire_dispatches],
            "market_quotes": [m.to_dict() for m in self.market_quotes],
            "editorial_note": self.editorial_note,
        }
