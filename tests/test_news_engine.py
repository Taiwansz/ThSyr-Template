"""
ThSyr Test Suite - News Engine (A Gazeta Tecnológica Global)
Valida:
- Modelos estruturados de dados (NewsBundle, LeadStory, WireDispatch, MarketQuote)
- Coletor RSS/Atom nativo, resiliencia a falhas de rede e pools de contingencia
- Compilador HTML broadsheet historico (tipografia, datas em portugues, layout)
- Arquivador de edicoes e sincronizacao do index.html
- Pipeline orquestradora de publicacao autonoma
- NewsWorker do Continuous Runtime
- Roteamento e despacho do CLI (thsyr news)
Zero dependencias externas frageis e zero emojis.
"""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch
import urllib.error

from engine.cli.news import (
    cmd_news_compile,
    cmd_news_fetch,
    cmd_news_publish,
    cmd_news_status,
    dispatch_news,
    parse_iso_date,
)
from engine.news import (
    EarBox,
    FeatureCard,
    LeadStory,
    MarketQuote,
    NewsArchiver,
    NewsBundle,
    NewsCollector,
    NewsCompiler,
    NewsEngine,
    NewsPipeline,
    RawFeedItem,
    SecondaryLead,
    WireDispatch,
)
from engine.news.collector import clean_html_text, parse_xml_feed
from engine.news.compiler import apply_drop_cap, format_date_portuguese, format_edition_number
from engine.runtime.workers import NewsWorker


SAMPLE_RSS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Hacker News</title>
    <link>https://news.ycombinator.com/</link>
    <description>Links for the intellectually curious</description>
    <item>
      <title>ASML Ships First High-NA EUV Scanner</title>
      <link>https://example.com/asml-high-na</link>
      <description>&lt;p&gt;ASML has officially shipped its Twinscan EXE:5000 machine.&lt;/p&gt;</description>
      <pubDate>Mon, 29 Sep 2026 12:00:00 GMT</pubDate>
    </item>
    <item>
      <title>TSMC 2nm Process Qualification Complete</title>
      <link>https://example.com/tsmc-2nm</link>
      <description>Yield rates have crossed 80 percent on preliminary runs.</description>
      <pubDate>Mon, 29 Sep 2026 14:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>
"""

SAMPLE_ATOM_XML = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>GitHub Blog</title>
  <link href="https://github.blog/"/>
  <updated>2026-09-29T12:00:00Z</updated>
  <entry>
    <title>Scaling Git Monorepos for High Density AI</title>
    <link href="https://github.blog/scaling-git/"/>
    <summary>Engineering optimizations for enterprise scale repositories.</summary>
    <updated>2026-09-29T10:00:00Z</updated>
  </entry>
</feed>
"""


class TestNewsModels(unittest.TestCase):
    def test_bundle_serialization(self):
        d = date(2026, 9, 29)
        bundle = NewsBundle(
            date=d,
            edition_number=60830,
            left_ear=EarBox(kicker="INFRAESTRUTURA", text="Texto da orelha"),
            right_ear=EarBox(kicker="LITOGRAFIA", text="Texto da direita"),
            lead_story=LeadStory(
                kicker="// TESTE",
                headline="TITULO DA MANCHETE",
                subheadline="Subtitulo explicativo",
                byline="BUREAU TESTE",
                dateline="LOCAL",
                date_str="29 DE SETEMBRO DE 2026",
                paragraphs=["Primeiro paragrafo.", "Segundo paragrafo."],
                pull_quote="Citacao central.",
                source_note="Fonte oficial",
            ),
            secondary_lead=SecondaryLead(
                kicker="// SECUNDARIO",
                headline="SEGUNDO ARTIGO",
                subheadline="Subtitulo secundario",
                paragraphs=["Texto secundario."],
            ),
            features=[
                FeatureCard(
                    kicker="// FEATURE",
                    headline="ARTIGO DE LITOGRAFIA",
                    subheadline="Subtitulo feature",
                    paragraphs=["Corpo da feature."],
                )
            ],
            wire_dispatches=[
                WireDispatch(
                    timestamp_str="[12:00 GMT] LOCAL // CATEGORIA",
                    title="Despacho telegrafico",
                    description="Descricao do despacho.",
                )
            ],
            market_quotes=[
                MarketQuote(name="TESTE (TST)", price="US$ 100,00", change="+1,5%", is_positive=True)
            ],
        )

        b_dict = bundle.to_dict()
        self.assertEqual(b_dict["date"], "2026-09-29")
        self.assertEqual(b_dict["edition_number"], 60830)
        self.assertEqual(b_dict["left_ear"]["kicker"], "INFRAESTRUTURA")
        self.assertEqual(b_dict["lead_story"]["headline"], "TITULO DA MANCHETE")
        self.assertEqual(len(b_dict["features"]), 1)
        self.assertEqual(len(b_dict["wire_dispatches"]), 1)
        self.assertEqual(len(b_dict["market_quotes"]), 1)


class TestNewsCollector(unittest.TestCase):
    def test_clean_html_text(self):
        raw = "<p>Texto com <b>tags</b> &amp; espa&ccedil;os   duplos</p>"
        cleaned = clean_html_text(raw)
        self.assertEqual(cleaned, "Texto com tags & espaços duplos")
        self.assertEqual(clean_html_text(None), "")

    def test_parse_rss_feed(self):
        items = parse_xml_feed(SAMPLE_RSS_XML, source_name="Hacker News")
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].title, "ASML Ships First High-NA EUV Scanner")
        self.assertEqual(items[0].link, "https://example.com/asml-high-na")
        self.assertIn("Twinscan EXE:5000", items[0].summary)
        self.assertEqual(items[0].source, "Hacker News")
        self.assertEqual(items[1].title, "TSMC 2nm Process Qualification Complete")

    def test_parse_atom_feed(self):
        items = parse_xml_feed(SAMPLE_ATOM_XML, source_name="GitHub Blog")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "Scaling Git Monorepos for High Density AI")
        self.assertEqual(items[0].link, "https://github.blog/scaling-git/")
        self.assertIn("Engineering optimizations", items[0].summary)
        self.assertEqual(items[0].source, "GitHub Blog")

    def test_parse_malformed_xml(self):
        items = parse_xml_feed("<invalid xml >>", source_name="Broken")
        self.assertEqual(items, [])
        empty_items = parse_xml_feed("", source_name="Empty")
        self.assertEqual(empty_items, [])

    def test_calculate_edition_number(self):
        collector = NewsCollector()
        self.assertEqual(collector.calculate_edition_number(date(2026, 9, 20)), 60821)
        self.assertEqual(collector.calculate_edition_number(date(2026, 9, 24)), 60825)
        self.assertEqual(collector.calculate_edition_number(date(2026, 9, 29)), 60830)

    def test_offline_collect_produces_full_bundle(self):
        collector = NewsCollector()
        d = date(2026, 9, 29)
        bundle = collector.collect(target_date=d, offline=True)

        self.assertIsInstance(bundle, NewsBundle)
        self.assertEqual(bundle.date, d)
        self.assertEqual(bundle.edition_number, 60830)
        self.assertTrue(len(bundle.lead_story.headline) > 10)
        self.assertGreaterEqual(len(bundle.lead_story.paragraphs), 3)
        self.assertGreaterEqual(len(bundle.features), 2)
        self.assertGreaterEqual(len(bundle.wire_dispatches), 4)
        self.assertGreaterEqual(len(bundle.market_quotes), 6)

    def test_network_failure_resilience(self):
        collector = NewsCollector(feeds=[{"name": "FailFeed", "url": "http://invalid-test-domain-999.xyz/rss"}])
        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("Network unreachable")):
            items = collector.fetch_all_feeds()
            self.assertEqual(items, [])

            # A coleta nao deve falhar mesmo com rede inacessivel
            bundle = collector.collect(target_date=date(2026, 9, 24), offline=False)
            self.assertIsInstance(bundle, NewsBundle)
            self.assertEqual(bundle.edition_number, 60825)

    def test_live_feed_injection(self):
        collector = NewsCollector()
        mock_raw = [
            RawFeedItem(
                title="Novo cluster de 100k GPUs ativado",
                link="https://example.com/cluster",
                summary="Descricao tecnica do cluster.",
                published="Hoje",
                source="Hacker News",
            )
        ]
        with patch.object(collector, "fetch_all_feeds", return_value=mock_raw):
            bundle = collector.collect(target_date=date(2026, 9, 24), offline=False)
            self.assertTrue(any("Novo cluster de 100k GPUs ativado" in w.title for w in bundle.wire_dispatches))


class TestNewsCompiler(unittest.TestCase):
    def test_format_date_portuguese(self):
        full, center, byline = format_date_portuguese(date(2026, 9, 24))
        self.assertEqual(full, "Quinta-feira, 24 de Setembro de 2026")
        self.assertEqual(center, "QUINTA-FEIRA, 24 DE SETEMBRO DE 2026")
        self.assertEqual(byline, "24 DE SETEMBRO DE 2026")

        full2, center2, byline2 = format_date_portuguese(date(2026, 9, 29))
        self.assertEqual(full2, "Terça-feira, 29 de Setembro de 2026")
        self.assertEqual(center2, "TERÇA-FEIRA, 29 DE SETEMBRO DE 2026")
        self.assertEqual(byline2, "29 DE SETEMBRO DE 2026")

    def test_format_edition_number(self):
        self.assertEqual(format_edition_number(60825), "60.825")
        self.assertEqual(format_edition_number(60830), "60.830")

    def test_apply_drop_cap(self):
        p = "TOQUIO — Em uma das maiores movimentacoes..."
        p_cap = apply_drop_cap(p)
        self.assertIn('<span class="drop-cap">T</span>OQUIO', p_cap)
        self.assertEqual(apply_drop_cap(""), "")

    def test_compile_html_integrity(self):
        collector = NewsCollector()
        compiler = NewsCompiler()
        bundle = collector.collect(target_date=date(2026, 9, 24), offline=True)
        html_out = compiler.compile(bundle)

        # 1. Estrutura basica do documento
        self.assertTrue(html_out.startswith("<!DOCTYPE html>"))
        self.assertIn('<html lang="pt-BR">', html_out)
        self.assertIn("A Gazeta Tecnológica Global — Quinta-feira, 24 de Setembro de 2026", html_out)

        # 2. Tipografia e estilos de broadsheet
        self.assertIn("UnifrakturMaguntia", html_out)
        self.assertIn("Playfair Display", html_out)
        self.assertIn("Old Standard TT", html_out)
        self.assertIn("Cinzel", html_out)
        self.assertIn("JetBrains Mono", html_out)
        self.assertIn("--newsprint-base: #f3ede2", html_out)
        self.assertIn("newspaper-broadsheet", html_out)

        # 3. Elementos editoriais
        self.assertIn("masthead-ears-grid", html_out)
        self.assertIn("CIRCULAÇÃO Nº 60.825", html_out)
        self.assertIn('class="drop-cap"', html_out)
        self.assertIn('class="pull-quote-box"', html_out)
        self.assertIn("O TELÉGRAFO DE NOTÍCIAS", html_out)
        self.assertIn("COTAÇÕES GLOBAIS DE TECNOLOGIA", html_out)
        self.assertIn("NOTA DE REGISTRO EDITORIAL", html_out)
        self.assertIn("VOLUME CLXXV &bull; NÚMERO 60.825", html_out)

        # 4. Rigor absoluto: Zero emojis
        for char in html_out:
            # Intervalos unicode tipicos de emojis
            cp = ord(char)
            self.assertFalse(
                0x1F600 <= cp <= 0x1F64F or 0x1F300 <= cp <= 0x1F5FF or 0x1F680 <= cp <= 0x1F6FF or 0x2600 <= cp <= 0x26FF,
                f"Emoji detectado no HTML compilado: {char!r} (U+{cp:04X})"
            )


class TestNewsArchiver(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.news_dir = Path(self.temp_dir.name)
        self.archiver = NewsArchiver(news_dir=self.news_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_edition_and_sync_index(self):
        d = date(2026, 9, 29)
        content = "<html><body>Edicao de Teste 2026-09-29</body></html>"
        saved = self.archiver.save_edition(d, content)

        self.assertTrue(saved.is_file())
        self.assertEqual(saved.name, "2026-09-29_a_gazeta_tecnologica.html")
        self.assertEqual(saved.read_text(encoding="utf-8"), content)

        # index.html deve ter sido atualizado identicamente
        self.assertTrue(self.archiver.index_path.is_file())
        self.assertEqual(self.archiver.index_path.read_text(encoding="utf-8"), content)

    def test_list_and_get_latest_edition(self):
        d1 = date(2026, 9, 20)
        d2 = date(2026, 9, 24)
        d3 = date(2026, 9, 29)

        self.archiver.save_edition(d1, "Edicao 1")
        self.archiver.save_edition(d3, "Edicao 3")
        self.archiver.save_edition(d2, "Edicao 2")

        editions = self.archiver.list_editions()
        self.assertEqual(len(editions), 3)
        # Ordenacao decrescente por data
        self.assertEqual(editions[0]["date"], "2026-09-29")
        self.assertEqual(editions[1]["date"], "2026-09-24")
        self.assertEqual(editions[2]["date"], "2026-09-20")

        latest = self.archiver.get_latest_edition()
        self.assertIsNotNone(latest)
        self.assertEqual(latest["date"], "2026-09-29")

        found_path = self.archiver.get_edition_by_date(d2)
        self.assertIsNotNone(found_path)
        self.assertEqual(found_path.name, "2026-09-24_a_gazeta_tecnologica.html")

        not_found = self.archiver.get_edition_by_date(date(2025, 1, 1))
        self.assertIsNone(not_found)


class TestNewsPipeline(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.news_dir = Path(self.temp_dir.name)
        self.collector = NewsCollector()
        self.compiler = NewsCompiler()
        self.archiver = NewsArchiver(news_dir=self.news_dir)
        self.pipeline = NewsPipeline(
            collector=self.collector,
            compiler=self.compiler,
            archiver=self.archiver,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_pipeline_run_success(self):
        d = date(2026, 9, 29)
        res = self.pipeline.run(target_date=d, force=False, offline=True)

        self.assertEqual(res["status"], "success")
        self.assertEqual(res["action_taken"], "published")
        self.assertEqual(res["date"], "2026-09-29")
        self.assertEqual(res["edition_number"], 60830)
        self.assertTrue(Path(res["edition_path"]).is_file())
        self.assertTrue(Path(res["index_path"]).is_file())

        # Execucao subsequente sem force deve pular
        res2 = self.pipeline.run(target_date=d, force=False, offline=True)
        self.assertEqual(res2["status"], "already_exists")
        self.assertEqual(res2["action_taken"], "skipped")

        # Execucao com force=True deve republicar
        res3 = self.pipeline.run(target_date=d, force=True, offline=True)
        self.assertEqual(res3["status"], "success")
        self.assertEqual(res3["action_taken"], "published")


class TestNewsEngineFacade(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.news_dir = Path(self.temp_dir.name)
        self.archiver = NewsArchiver(news_dir=self.news_dir)
        self.engine = NewsEngine(archiver=self.archiver)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_engine_operations(self):
        d = date(2026, 9, 29)
        # 1. Fetch
        bundle = self.engine.fetch(offline=True, target_date=d)
        self.assertEqual(bundle.edition_number, 60830)

        # 2. Compile
        html_out = self.engine.compile(bundle=bundle)
        self.assertIn("A Gazeta Tecnológica Global", html_out)

        # 3. Publish
        pub_res = self.engine.publish(target_date=d, force=True, offline=True)
        self.assertEqual(pub_res["status"], "success")

        # 4. Status
        stat = self.engine.status()
        self.assertEqual(stat["total_editions"], 1)
        self.assertTrue(stat["index_exists"])
        self.assertEqual(stat["latest_edition"]["date"], "2026-09-29")


class TestNewsWorker(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.news_dir = Path(self.temp_dir.name)
        self.archiver = NewsArchiver(news_dir=self.news_dir)
        self.engine = NewsEngine(archiver=self.archiver)
        self.worker = NewsWorker(news_engine=self.engine)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_worker_cycle_publishes_when_missing(self):
        today = datetime.now().date()
        # Inicialmente nao ha edicao de hoje no temp_dir
        res = self.worker.run_cycle()
        self.assertEqual(res["action_taken"], "edition_published")
        self.assertEqual(res["status"], "published")
        self.assertEqual(res["today"], today.isoformat())

        # Segundo ciclo deve reconhecer que a edicao ja esta fresca
        res2 = self.worker.run_cycle()
        self.assertEqual(res2["action_taken"], "none")
        self.assertEqual(res2["status"], "fresh")


class TestNewsCLI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.news_dir = Path(self.temp_dir.name)
        self.archiver = NewsArchiver(news_dir=self.news_dir)
        self.engine = NewsEngine(archiver=self.archiver)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_parse_iso_date(self):
        self.assertEqual(parse_iso_date("2026-09-24"), date(2026, 9, 24))
        self.assertIsNone(parse_iso_date(None))
        self.assertIsNone(parse_iso_date(""))

    def test_cli_status_and_publish(self):
        # 1. Status antes da publicacao
        args_status = MagicMock(command="news", news_action="status")
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            cmd_news_status(args_status, engine=self.engine)
        self.assertIn("A GAZETA TECNOLOGICA GLOBAL", stdout.getvalue())

        # 2. Publish
        args_pub = MagicMock(command="news", news_action="publish", date="2026-09-24", force=True, offline=True)
        stdout_pub = io.StringIO()
        with patch("sys.stdout", stdout_pub):
            cmd_news_publish(args_pub, engine=self.engine)
        self.assertIn("PUBLICADA COM SUCESSO", stdout_pub.getvalue())

        # 3. Fetch
        args_fetch = MagicMock(command="news", news_action="fetch", date="2026-09-24", offline=True, json=False)
        stdout_fetch = io.StringIO()
        with patch("sys.stdout", stdout_fetch):
            cmd_news_fetch(args_fetch, engine=self.engine)
        self.assertIn("PACOTE EDITORIAL COLETADO", stdout_fetch.getvalue())

        # 4. Compile
        out_compile = self.news_dir / "preview.html"
        args_compile = MagicMock(command="news", news_action="compile", date="2026-09-24", offline=True, output=str(out_compile))
        stdout_compile = io.StringIO()
        with patch("sys.stdout", stdout_compile):
            cmd_news_compile(args_compile, engine=self.engine)
        self.assertTrue(out_compile.is_file())

        # 5. Dispatch news router
        dispatched = dispatch_news(args_status, engine=self.engine)
        self.assertTrue(dispatched)

        non_news_args = MagicMock(command="status")
        self.assertFalse(dispatch_news(non_news_args, engine=self.engine))


if __name__ == "__main__":
    unittest.main()
