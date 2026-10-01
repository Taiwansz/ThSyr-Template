"""Advanced CLI command handlers extracted from the legacy entrypoint."""

from __future__ import annotations

import json
import sys

from ..cognitive_router import CognitiveRouter
from ..memory_manager import MemoryManager
from ..sync_engine import GitSyncEngine


def cmd_gods_eye(args):
    from engine.gods_eye_bridge import GodsEyeBridge
    bridge = GodsEyeBridge()

    action = getattr(args, "action", "status") or "status"

    if action == "start":
        res = bridge.launch()
        if res["success"]:
            print(f"[SUCESSO] Console 3D Gods Eye View iniciado em segundo plano (PID: {res['pid']}).")
            print(f"Acesse no navegador: {res['url']}")
        else:
            print(f"[FALHA] Nao foi possivel iniciar o console: {res.get('error')}")
        return

    status = bridge.get_status()
    deps_label = "INSTALADAS" if status.get("dependencies_installed") else "PENDENTES (npm install necessario)"

    print("================================================================================")
    print("                THSYR // APARATO SENSORIAL: GOD'S EYE VIEW                      ")
    print("================================================================================")
    print(f"Status do Console:   {status['status']}")
    print(f"Caminho no Disco:    {status['path']}")
    print(f"Versao do Modulo:    {status['version']}")
    print(f"Motor de Telemetria: {status['telemetry_engine']}")
    print(f"Dependencias:        {deps_label}")
    print(f"Camadas Sensoriais:  {status['total_layers']} ativas")
    print("--------------------------------------------------------------------------------")
    print("CAMADAS MAPEADAS:")
    for layer in status["layers"]:
        print(f"  * [{layer['layer_id']}] {layer['name']}: {layer['source']}")
    print("================================================================================")
    print("COMANDOS DISPONIVEIS:")
    print("  thsyr gods-eye          -> Exibe o diagnostico do aparato sensorial")
    print("  thsyr gods-eye start    -> Inicia o console visual 3D em http://localhost:4173")
    print("================================================================================")


def cmd_hardware(args):
    from engine.host_telemetry import HostTelemetryObserver
    obs = HostTelemetryObserver()
    print(obs.render_report())


def cmd_daemon(args):
    from engine.runtime.daemon import SyrDaemonManager
    dm = SyrDaemonManager()
    action = getattr(args, "action", "status") or "status"

    if action == "start":
        ok, msg = dm.start()
        print(f"[{'SUCESSO' if ok else 'AVISO'}] {msg}")
    elif action == "stop":
        ok, msg = dm.stop()
        print(f"[{'SUCESSO' if ok else 'AVISO'}] {msg}")
    else:
        stat = dm.status()
        print("==================================================")
        print("           THSYR // DAEMON SUPERVISOR             ")
        print("==================================================")
        print(f"Estado do Daemon:    {stat['status']}")
        print(f"PID Ativo:           {stat['pid'] or 'Nenhum'}")
        print(f"Arquivo de Trava:    {stat['pid_file']}")
        print(f"Ultima Verificacao:  {stat['timestamp']}")
        print("==================================================")


def cmd_toklang(args):
    from engine.toklang import CompressionEstimator, TokLangCompiler, TokLangLexer, TokLangParser
    code_raw = getattr(args, "code_flag", None) or getattr(args, "code", None)
    if not code_raw:
        print("[ERRO] Informe o codigo TokLang ou texto para analise.")
        return
    code = " ".join(code_raw) if isinstance(code_raw, list) else str(code_raw)

    lexer = TokLangLexer(code)
    tokens = lexer.tokenize()
    parser = TokLangParser(tokens)
    doc = parser.parse()
    compiled = TokLangCompiler().compile(doc)

    metrics = CompressionEstimator.estimate_metrics(code, doc)
    print("==================================================")
    print("           THSYR // TOKLANG COMPILER CORE         ")
    print("==================================================")
    print(f"Documento AST:       {doc.name}")
    print(f"Diretiva Compressao: {doc.compression.level if doc.compression else 'Nenhuma'}")
    print(f"Diretiva Budget:     {doc.budget.max_tokens if doc.budget else 'Nenhum'} tokens")
    print(f"Restricoes Ativas:   {len(doc.constraints)}")
    print(f"Blocos de Contexto:  {len(doc.contexts)}")
    print("--------------------------------------------------")
    print("METRICAS DE EFICIENCIA (BENCHMARK DE COMPRESSAO):")
    print(f"  Tokens Brutos:     {metrics['raw_tokens']}")
    print(f"  Tokens Compilados: {metrics['compiled_tokens']}")
    print(f"  Economia Tokens:   {metrics['tokens_saved']} ({metrics['compression_ratio_percent']}%)")
    print(f"  Reducao FLOPs O(N^2)->O(K^2): {metrics['attention_flops_reduction_percent']}%")
    print(f"  Aceleracao Teorica:          {metrics['theoretical_speedup_factor']}x")
    print(f"  Prompt Compilado:             {compiled.token_count}/{compiled.max_tokens} tokens")
    print(f"  Truncado por Budget:          {'SIM' if compiled.truncated else 'NAO'}")
    print("--------------------------------------------------")
    print(compiled.text)
    print("==================================================")


def cmd_vector(args):
    from engine.vector_store import LocalVectorStore
    store = LocalVectorStore()
    action = getattr(args, "action", "search") or "search"

    if action == "count":
        print(f"Total de documentos vetorizados: {store.count()}")
    elif action == "ingest":
        print("Iniciando ingestao e vetorizacao semantica do acervo...")
        total = store.ingest_markdown_knowledge()
        print(f"[SUCESSO] {total} documentos vetorizados no indice neural local.")
    else:
        query = getattr(args, "query", "")
        if not query:
            print("[ERRO] Forneca uma consulta semantica para busca.")
            return
        results = store.search(query, top_k=getattr(args, "limit", 5))
        print("==================================================")
        print("       THSYR // BUSCA VETORIAL DENSA LOCAL        ")
        print("==================================================")
        print(f"Consulta:     '{query}'")
        print(f"Resultados:   {len(results)}")
        print("--------------------------------------------------")
        for i, r in enumerate(results, 1):
            print(f"[{i}] Score: {r['score']:.4f} | ID: {r['id']}")
            print(f"    Texto: {r['text'][:120]}...")
        print("==================================================")


def cmd_doctor(args, memory: MemoryManager, router: CognitiveRouter, sync: GitSyncEngine):
    import platform

    from engine.runtime import get_codenotch_status
    from engine.runtime.daemon import SyrDaemonManager
    from engine.vector_store import LocalVectorStore

    dm = SyrDaemonManager()
    daemon_stat = dm.status()
    notch_stat = get_codenotch_status()
    vec_store = LocalVectorStore()

    print("==================================================")
    print("           THSYR // SYSTEM HEALTH DOCTOR          ")
    print("==================================================")
    py_ok = sys.version_info >= (3, 10)
    print(f"Runtime Python:      {platform.python_version()} [{'OK' if py_ok else 'DESATUALIZADO'}]")
    print(f"Sistema Operacional: {platform.system()} {platform.release()}")

    sync_stat = sync.get_status()
    dirty_tag = 'MODIFICADO (' + str(sync_stat['changed_files_count']) + ' arquivos)' if sync_stat['is_dirty'] else 'LIMPO'
    print(f"Git Integridade:     Branch {sync_stat['branch']} ({sync_stat['commit'][:7]}) [{dirty_tag}]")

    print(f"Daemon Supervisor:   {daemon_stat['status'].upper()} (PID: {daemon_stat['pid'] or 'Nenhum'})")
    print(f"Codenotch Monitor:   {'ATIVO' if notch_stat['running'] else 'INATIVO'}")
    print(f"Cerebro / Nos:       {len(router.synaptic.nodes)} nos, {len(router.synaptic.edges)} sinapses")
    print(f"Memoria Semantica:   {len(memory.get_semantic_memories())} categorias")
    print(f"Indice Vetorial:     {vec_store.count()} documentos vetorizados")
    print("--------------------------------------------------")
    print("Diagnostico: Sistema operacional, estavel e integro.")
    print("==================================================")


def cmd_eval(args):
    import subprocess
    from pathlib import Path

    from engine.evaluation import CognitiveBenchmark

    print("==================================================")
    print("           THSYR // EVALUATION BENCHMARK          ")
    print("==================================================")
    print("Executando benchmark cognitivo de recuperacao...")
    report = CognitiveBenchmark().run()
    report_path = getattr(args, "report", None)
    if report_path:
        output_path = Path(report_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"[RELATORIO] {report_path}")
    print(
        f"[COGNITIVO] {report['passed']}/{report['total']} casos passaram "
        f"({report['pass_rate']:.0%})."
    )
    if getattr(args, "json", False):
        print(json.dumps(report, indent=2, ensure_ascii=False))

    print("Executando suite unitária...")
    res = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], capture_output=True, text=True)
    if res.returncode == 0:
        print("[UNIT] Suite de testes passou.")
        summary_line = [line for line in res.stderr.splitlines() if "Ran " in line]
        if summary_line:
            print(summary_line[0])
    else:
        print("[UNIT] Falha detectada na execucao:")
        print(res.stderr.strip() or res.stdout.strip())
    print("==================================================")


def cmd_chat(args, router: CognitiveRouter):
    from engine.interaction import SyrConversationSession
    session = SyrConversationSession(router=router)
    session.run_interactive_loop()


def cmd_swarm(args):
    from engine.swarm import UltronSwarm
    swarm = UltronSwarm()
    if getattr(args, "agent", None):
        rep = swarm.dispatch(args.agent)
        print(f"[{rep.name}] Status: {rep.status.value}")
        for diag in rep.diagnostics:
            print(f" - {diag}")
        if rep.recommendations:
            print(" Recomendacoes:")
            for rec in rep.recommendations:
                print(f"   * {rec}")
    else:
        report = swarm.converge()
        print(report.render_markdown())


def cmd_evolve(args):
    from engine.auto_evolution import AutoEvolutionEngine
    eng = AutoEvolutionEngine()
    if getattr(args, "optimize", False):
        print("Disparando ciclo de auto-evolucao e otimizacao...")
        res = eng.trigger_evolution(auto_apply=True)
        print(f"[SUCESSO] Salto evolutivo concluido -> Geracao {res['generation']}")
        for act in res.get("actions", []):
            print(f" • {act}")
    else:
        print(eng.render_report())


def cmd_war_room(args):
    from engine.war_room import WarRoomServer

    port = getattr(args, "port", 8080)
    lan = bool(getattr(args, "lan", False))
    host = "0.0.0.0" if lan else "127.0.0.1"
    server = WarRoomServer(host=host, port=port)
    print("==================================================")
    print("        THSYR // ULTRON WAR ROOM INICIADO         ")
    print("==================================================")
    print(f"Modo:                 {'LAN AUTENTICADA' if lan else 'LOCAL LOOPBACK'}")
    print(f"Interface:            {server.access_url()}")
    print("Pressione Ctrl + C para encerrar o servidor.")
    print("==================================================")
    server.start(background=False)

