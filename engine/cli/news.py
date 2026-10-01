"""
ThSyr CLI - Módulo da Gazeta Tecnológica Global
Comandos executivos para coleta, compilação, arquivamento e inspeção de status
do periódico diário em formato broadsheet histórico. Zero emojis.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

from ..news import NewsEngine


def parse_iso_date(date_str: str | None) -> date | None:
    """Valida e converte uma string YYYY-MM-DD em objeto date."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except ValueError:
        print(f"[ERRO] Formato de data invalido: '{date_str}'. Utilize o padrao AAAA-MM-DD (ex: 2026-09-24).")
        sys.exit(1)


def cmd_news_status(args: Any, engine: NewsEngine | None = None) -> None:
    """Exibe o diagnostico completo do acervo e da edicao ativa."""
    eng = engine or NewsEngine()
    stat = eng.status()

    print("================================================================================")
    print("                A GAZETA TECNOLOGICA GLOBAL // DIAGNOSTICO                     ")
    print("================================================================================")
    print(f"Periodico:             {stat['name']}")
    print(f"Arquivo Mestre:        {stat['active_edition_path']}")
    print(f"Estado do Index:       {'PRESENTE (' + str(stat['index_size_bytes']) + ' bytes)' if stat['index_exists'] else 'AUSENTE'}")
    print(f"Edicoes no Acervo:     {stat['total_editions']}")
    print(f"Feeds Configurados:    {stat['configured_feeds_count']}")
    print(f"Data Corrente:         {stat['today']}")
    print(f"Publicacao de Hoje:    {'CONCLUIDA' if stat['today_published'] else 'PENDENTE'}")
    if stat["today_edition_path"]:
        print(f"Caminho Hoje:          {stat['today_edition_path']}")
    print("--------------------------------------------------------------------------------")

    latest = stat.get("latest_edition")
    if latest:
        print("ULTIMA EDICAO PUBLICADA:")
        print(f"  * Data:              {latest['date']}")
        print(f"  * Arquivo:           {latest['filename']}")
        print(f"  * Tamanho:           {latest['size']} bytes")
        print(f"  * Modificado em:     {latest['modified_at']}")
    else:
        print("Nenhuma edicao encontrada no acervo historico.")
    print("================================================================================")


def cmd_news_fetch(args: Any, engine: NewsEngine | None = None) -> None:
    """Coleta os despachos e exibe o pacote editorial estruturado."""
    eng = engine or NewsEngine()
    target_date = parse_iso_date(getattr(args, "date", None))
    offline = bool(getattr(args, "offline", False))

    print(f"Coletando despachos para a Gazeta Tecnologica Global (offline={offline})...")
    bundle = eng.fetch(offline=offline, target_date=target_date)

    if getattr(args, "json", False):
        print(json.dumps(bundle.to_dict(), indent=2, ensure_ascii=False))
        return

    print("================================================================================")
    print("         A GAZETA TECNOLOGICA GLOBAL // PACOTE EDITORIAL COLETADO               ")
    print("================================================================================")
    print(f"Data:                  {bundle.date.isoformat()}")
    print(f"Edicao Canônica Nº:    {bundle.edition_number}")
    print(f"Orelha Esquerda:       [{bundle.left_ear.kicker}] {bundle.left_ear.text}")
    print(f"Orelha Direita:        [{bundle.right_ear.kicker}] {bundle.right_ear.text}")
    print("--------------------------------------------------------------------------------")
    print(f"MANCHETE PRINCIPAL:    {bundle.lead_story.headline}")
    print(f"Subtitulo:             {bundle.lead_story.subheadline}")
    print(f"Byline / Dateline:     POR {bundle.lead_story.byline} | {bundle.lead_story.dateline}")
    print(f"Paragrafos:            {len(bundle.lead_story.paragraphs)} blocos")
    print(f"Citacao Pull-Quote:    \"{bundle.lead_story.pull_quote}\"")
    print("--------------------------------------------------------------------------------")
    print(f"ARTIGO SECUNDARIO:     {bundle.secondary_lead.headline}")
    print(f"Subtitulo:             {bundle.secondary_lead.subheadline}")
    print("--------------------------------------------------------------------------------")
    print(f"ARTIGOS TEMATICOS (FEATURES): {len(bundle.features)}")
    for i, feat in enumerate(bundle.features, 1):
        print(f"  [{i}] {feat.kicker} -> {feat.headline}")
    print("--------------------------------------------------------------------------------")
    print(f"TELEGRAFO DE DESPACHOS: {len(bundle.wire_dispatches)} itens")
    for wire in bundle.wire_dispatches[:5]:
        print(f"  * {wire.timestamp_str} | {wire.title}")
    print("--------------------------------------------------------------------------------")
    print(f"COTACOES GLOBAIS:      {len(bundle.market_quotes)} papeis")
    for quote in bundle.market_quotes[:6]:
        print(f"  * {quote.name}: {quote.price} ({quote.change})")
    print("================================================================================")


def cmd_news_compile(args: Any, engine: NewsEngine | None = None) -> None:
    """Compila o broadsheet em HTML sem obrigatoriamente persistir no acervo mestre."""
    eng = engine or NewsEngine()
    target_date = parse_iso_date(getattr(args, "date", None))
    offline = bool(getattr(args, "offline", False))
    output_path = getattr(args, "output", None)

    bundle = eng.fetch(offline=offline, target_date=target_date)
    html_content = eng.compile(bundle=bundle)
    size_bytes = len(html_content.encode("utf-8"))

    if output_path:
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(html_content, encoding="utf-8")
        print(f"[OK] Broadsheet compilado e salvo com sucesso em: {out_file.resolve()}")
    else:
        print("[OK] Broadsheet compilado com sucesso em memoria.")

    print("--------------------------------------------------------------------------------")
    print(f"Data Alvo:             {bundle.date.isoformat()}")
    print(f"Edicao Nº:             {bundle.edition_number}")
    print(f"Manchete:              {bundle.lead_story.headline}")
    print(f"Tamanho do HTML:       {size_bytes} bytes")
    print(f"Padrão Tipografico:    Fraktur / Playfair / Old Standard TT / Cinzel / JetBrains Mono")
    print("================================================================================")


def cmd_news_publish(args: Any, engine: NewsEngine | None = None) -> None:
    """Executa a pipeline completa de publicacao (coleta, compilacao, arquivamento)."""
    eng = engine or NewsEngine()
    target_date = parse_iso_date(getattr(args, "date", None))
    force = bool(getattr(args, "force", False))
    offline = bool(getattr(args, "offline", False))

    res = eng.publish(target_date=target_date, force=force, offline=offline)

    print("================================================================================")
    print("             A GAZETA TECNOLOGICA GLOBAL // PUBLICACAO DIARIA                   ")
    print("================================================================================")
    if res["action_taken"] == "skipped":
        print(f"Status:                EDICAO JA EXISTENTE (PULADA)")
        print(f"Data:                  {res['date']}")
        print(f"Arquivo Historico:     {res['edition_path']}")
        print(f"Arquivo Mestre:        {res['index_path']}")
        print("Dica: Use --force para sobrescrever a publicacao existente do dia.")
    else:
        print(f"Status:                PUBLICADA COM SUCESSO")
        print(f"Data da Edicao:        {res['date']}")
        print(f"Edicao Nº:             {res['edition_number']}")
        print(f"Manchete:              {res['headline']}")
        print(f"Materias Publicadas:   {res['stories_count']}")
        print(f"Tamanho do Broadsheet: {res['size_bytes']} bytes")
        print(f"Acervo Gravado:        {res['edition_path']}")
        print(f"Ponto de Entrada:      {res['index_path']}")
    print("================================================================================")


def register_news_subcommands(subparsers: argparse._SubParsersAction) -> None:
    """Registra os subcomandos do motor de jornalismo tecnologico no CLI principal."""
    news_parser = subparsers.add_parser(
        "news",
        help="Motor autonomo de publicacao da Gazeta Tecnologica Global",
    )
    news_subs = news_parser.add_subparsers(dest="news_action")

    # thsyr news status
    news_subs.add_parser("status", help="Exibe o diagnostico do acervo e da publicacao ativa")

    # thsyr news fetch
    fetch_parser = news_subs.add_parser("fetch", help="Coleta e sintetiza despachos de alta densidade tecnologica")
    fetch_parser.add_argument("--date", help="Data alvo no formato AAAA-MM-DD")
    fetch_parser.add_argument("--offline", action="store_true", help="Utiliza contingencia autonoma sem conexao externa")
    fetch_parser.add_argument("--json", action="store_true", help="Emite o pacote editorial bruto em JSON")

    # thsyr news compile
    compile_parser = news_subs.add_parser("compile", help="Compila o broadsheet em HTML puro")
    compile_parser.add_argument("--date", help="Data alvo no formato AAAA-MM-DD")
    compile_parser.add_argument("--offline", action="store_true", help="Utiliza contingencia autonoma")
    compile_parser.add_argument("-o", "--output", help="Caminho do arquivo de destino para inspecao")

    # thsyr news publish
    publish_parser = news_subs.add_parser("publish", help="Executa o ciclo completo de publicacao no acervo")
    publish_parser.add_argument("--date", help="Data da edicao no formato AAAA-MM-DD")
    publish_parser.add_argument("--force", action="store_true", help="Forca a sobrescrita de edicao ja existente")
    publish_parser.add_argument("--offline", action="store_true", help="Publica utilizando contingencia autonoma")


def dispatch_news(args: Any, engine: NewsEngine | None = None) -> bool:
    """Roteia a execucao caso o comando seja 'news'."""
    if getattr(args, "command", None) != "news":
        return False

    action = getattr(args, "news_action", None)
    if action == "status" or not action:
        cmd_news_status(args, engine=engine)
    elif action == "fetch":
        cmd_news_fetch(args, engine=engine)
    elif action == "compile":
        cmd_news_compile(args, engine=engine)
    elif action == "publish":
        cmd_news_publish(args, engine=engine)
    else:
        print(f"[ERRO] Acao de jornalismo desconhecida: '{action}'. Opcoes: status, fetch, compile, publish.")
        sys.exit(1)

    return True
