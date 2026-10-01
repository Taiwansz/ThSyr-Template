"""
ThSyr CLI - Módulo Graphify & Code Graph Architecture
Comandos para construcao, consulta deterministica GraphRAG e visualizacao 3D de grafos de codigo.
Zero emojis.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from ..code_graph import GraphifyEngine


def _get_default_paths() -> list[str]:
    return ["engine"]


def cmd_graphify_status(args: Any, engine: GraphifyEngine | None = None) -> None:
    eng = engine or GraphifyEngine()
    cache_file = Path("state/code_graph.json")

    print("================================================================================")
    print("                THSYR // GRAPHIFY CODE GRAPH STATUS                             ")
    print("================================================================================")
    if not cache_file.exists():
        print(f"Estado do Cache:       INEXISTENTE ({cache_file})")
        print("Execute 'thsyr graphify build' para escanear a base de codigo.")
        print("================================================================================")
        return

    try:
        graph = eng.load_cache(cache_file)
        summary = graph.summary()
        print(f"Estado do Cache:       ATIVO ({cache_file} | {cache_file.stat().st_size} bytes)")
        print(f"Total de Nós:          {summary['total_nodes']}")
        print(f"Total de Sinapses:     {summary['total_edges']}")
        print("--------------------------------------------------------------------------------")
        print("DISTRIBUICAO POR LINGUAGEM:")
        for lang, count in summary.get("nodes_by_language", {}).items():
            print(f"  * {lang.upper():<12}: {count} nós")
        print("--------------------------------------------------------------------------------")
        print("DISTRIBUICAO POR SIMBOLO:")
        for stype, count in summary.get("nodes_by_type", {}).items():
            print(f"  * {stype.upper():<12}: {count} símbolos")
        print("--------------------------------------------------------------------------------")
        print("RELACOES ESTRUTURAIS:")
        for rel, count in summary.get("edges_by_relationship", {}).items():
            print(f"  * {rel.upper():<16}: {count} arestas")
    except Exception as exc:
        print(f"[ERRO] Falha ao inspecionar cache de grafo: {exc}")
    print("================================================================================")


def cmd_graphify_build(args: Any, engine: GraphifyEngine | None = None) -> None:
    eng = engine or GraphifyEngine()
    target_paths = getattr(args, "paths", None) or _get_default_paths()

    print(f"Iniciando escaneamento deterministico Graphify...")
    for p in target_paths:
        print(f"  * Rota alvo: {p}")

    graph = eng.build(target_paths, persist=True)
    summary = graph.summary()

    print("================================================================================")
    print("                THSYR // GRAPHIFY COMPILACAO CONCLUIDA                          ")
    print("================================================================================")
    print(f"Total de Nós Extraídos:    {summary['total_nodes']}")
    print(f"Total de Sinapses:         {summary['total_edges']}")
    print("Por Linguagem:")
    for lang, cnt in summary.get("nodes_by_language", {}).items():
        print(f"  * {lang.upper()}: {cnt}")
    print("Por Tipo:")
    for st, cnt in summary.get("nodes_by_type", {}).items():
        print(f"  * {st.upper()}: {cnt}")
    print(f"Persistencia em Disco:     state/code_graph.json")
    print("================================================================================")


def cmd_graphify_query(args: Any, engine: GraphifyEngine | None = None) -> None:
    eng = engine or GraphifyEngine()
    cache_file = Path("state/code_graph.json")
    if cache_file.exists():
        eng.load_cache(cache_file)
    else:
        eng.build(_get_default_paths())

    query_str = getattr(args, "query", "")
    if not query_str:
        print("[ERRO] Informe o termo de busca (ex: 'thsyr graphify query MemoryManager').")
        return

    matches = eng.query(query_str)
    print("================================================================================")
    print(f"         THSYR // CONSULTA DETERMINISTICA: '{query_str}' ({len(matches)} encontrados)")
    print("================================================================================")
    for m in matches[:20]:
        print(f"[{m.language.upper()}] {m.symbol_type.value.upper()}: {m.name} ({m.id})")
        print(f"  Arquivo: {m.filepath} (Linha {m.line_number})")
        if m.docstring:
            first_line = m.docstring.strip().splitlines()[0]
            print(f"  Doc: {first_line[:80]}")
        print("  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    if len(matches) > 20:
        print(f"... e mais {len(matches) - 20} resultados truncados.")
    print("================================================================================")


def cmd_graphify_impact(args: Any, engine: GraphifyEngine | None = None) -> None:
    eng = engine or GraphifyEngine()
    cache_file = Path("state/code_graph.json")
    if cache_file.exists():
        eng.load_cache(cache_file)
    else:
        eng.build(_get_default_paths())

    symbol_id = getattr(args, "symbol_id", "")
    if not symbol_id:
        print("[ERRO] Forneca o ID exato ou prefixo do simbolo (ex: 'sql:table:vendas').")
        return

    # Se for passado apenas o nome, tentar resolver o id exato
    if ":" not in symbol_id:
        matches = eng.query(symbol_id)
        if matches:
            symbol_id = matches[0].id
            print(f"[INFO] Resolvido '{args.symbol_id}' para nó exato: '{symbol_id}'")

    res = eng.impact(symbol_id)
    print("================================================================================")
    print(f"              THSYR // ANALISE DE IMPACTO DE CODIGO                             ")
    print("================================================================================")
    print(f"Simbolo Alvo:             {res['symbol_id']}")
    print(f"Total de Dependentes:     {res['total_dependents']}")
    print("--------------------------------------------------------------------------------")
    print(f"Chamadores Diretos ({len(res['direct_callers'])}):")
    for c in res['direct_callers']:
        print(f"  <- {c}")
    print(f"Referencias de FK / Schemas ({len(res['referencing_foreign_keys'])}):")
    for fk in res['referencing_foreign_keys']:
        print(f"  <- {fk}")
    print(f"Herdeiros ou Implementacoes ({len(res['inheritors_or_implementers'])}):")
    for inh in res['inheritors_or_implementers']:
        print(f"  <- {inh}")
    print("================================================================================")


def cmd_graphify_3d(args: Any, engine: GraphifyEngine | None = None) -> None:
    eng = engine or GraphifyEngine()
    cache_file = Path("state/code_graph.json")
    if cache_file.exists():
        eng.load_cache(cache_file)
    else:
        print("Grafo nao carregado em cache. Construindo...")
        eng.build(_get_default_paths())

    no_open = getattr(args, "no_open", False)
    out_path = getattr(args, "output", None) or Path("brain/code_canvas_3d.html")

    res_path = eng.render_3d(output_path=out_path, open_browser=not no_open)
    print(f"[OK] Visualizacao Holografica 3D gerada com sucesso: {res_path.resolve()}")


def register_code_graph_subcommands(subparsers: argparse._SubParsersAction) -> None:
    """Registra os comandos graphify no parser CLI principal."""
    graph_parser = subparsers.add_parser(
        "graphify",
        help="Motor deterministico de grafos de codigo AST (Python, Java, SQL) e GraphRAG",
    )
    graph_subs = graph_parser.add_subparsers(dest="graphify_action")

    # thsyr graphify status
    graph_subs.add_parser("status", help="Exibe o diagnostico do grafo estrutural de codigo em cache")

    # thsyr graphify build
    build_parser = graph_subs.add_parser("build", help="Varre codigo-fonte e compila o grafo AST unificado")
    build_parser.add_argument("--paths", nargs="*", help="Diretorios especificos para varredura")

    # thsyr graphify query
    query_parser = graph_subs.add_parser("query", help="Pesquisa simbolos, classes, tabelas e funcoes no grafo")
    query_parser.add_argument("query", help="Nome do simbolo ou trecho a consultar")

    # thsyr graphify impact
    impact_parser = graph_subs.add_parser("impact", help="Mapeia o raio de impacto de alteracao de um simbolo")
    impact_parser.add_argument("symbol_id", help="ID do simbolo ou nome da entidade")

    # thsyr graphify 3d
    render_parser = graph_subs.add_parser("3d", help="Gera e abre o canvas 3D WebGL dos nos de codigo")
    render_parser.add_argument("--no-open", action="store_true", help="Nao abrir navegador automaticamente")
    render_parser.add_argument("-o", "--output", help="Caminho do arquivo HTML de destino")


def dispatch_code_graph(args: Any, engine: GraphifyEngine | None = None) -> bool:
    """Roteia comandos 'graphify'."""
    if getattr(args, "command", None) != "graphify":
        return False

    action = getattr(args, "graphify_action", None)
    if action == "status" or not action:
        cmd_graphify_status(args, engine=engine)
    elif action == "build":
        cmd_graphify_build(args, engine=engine)
    elif action == "query":
        cmd_graphify_query(args, engine=engine)
    elif action == "impact":
        cmd_graphify_impact(args, engine=engine)
    elif action == "3d":
        cmd_graphify_3d(args, engine=engine)
    else:
        print(f"[ERRO] Acao graphify desconhecida: '{action}'. Opcoes: status, build, query, impact, 3d.")
        sys.exit(1)

    return True
