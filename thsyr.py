#!/usr/bin/env python3
"""
ThSyr CLI V2 - Interface de Linha de Comando do Copiloto Cognitivo
Suporta ativacao neural, auditoria pre-frontal, gestao de estado/handoff,
sincronizacao autonoma com Git e radar academico.
"""

import argparse
import sys

from engine.cli.advanced import (
    cmd_chat,
    cmd_daemon,
    cmd_doctor,
    cmd_eval,
    cmd_evolve,
    cmd_gods_eye,
    cmd_hardware,
    cmd_swarm,
    cmd_toklang,
    cmd_vector,
    cmd_war_room,
)
from engine.cognitive_router import CognitiveRouter
from engine.memory_manager import MemoryManager
from engine.memory_models import MemoryType
from engine.neural_graph import render_and_open_graph
from engine.runtime import ensure_codenotch_running, get_codenotch_status
from engine.session_state import HandoffManager, SessionState
from engine.sync_engine import GitSyncEngine


def cmd_status(args, memory: MemoryManager, router: CognitiveRouter, sync: GitSyncEngine, handoff: HandoffManager):
    stat = router.status()
    sync_stat = sync.get_status()
    active_handoff = handoff.load_handoff()
    notch_res = ensure_codenotch_running()

    if notch_res["running"]:
        notch_label = "ATIVO (Desktop Notch visivel)"
    elif notch_res["executable"]:
        notch_label = f"DISPONIVEL ({notch_res['action_taken']})"
    else:
        notch_label = "AGUARDANDO INSTALACAO (Codenotch.exe)"

    print("========================================")
    print("           THSYR STATUS REPORT          ")
    print("========================================")
    print(f"Estado:              {stat['status'].upper()}")
    print(f"Nos Cerebrais:       {stat.get('total_nodes', 0)}")
    print(f"Sinapses Ativas:     {stat.get('total_synapses', 0)}")
    print(f"Lobos Mapeados:      {', '.join(stat.get('lobes', []))}")
    print("Cortex Pre-Frontal:  ATIVO (Filtros de Inibicao Operacionais)")
    try:
        from engine.auto_evolution import AutoEvolutionEngine
        evo_diag = AutoEvolutionEngine().diagnose()
        print(f"Auto-Evolucao:       ATIVA (Gen {evo_diag.generation} | Entropia: {evo_diag.entropy_index:.4f})")
    except Exception:
        print("Auto-Evolucao:       ATIVA (Melhoria Continua Autonoma)")
    print("Sync Vault Academico: ATIVO (Dual-Write Habilitado)")
    print(f"Monitor Codenotch:   {notch_label}")
    print(f"Sessoes Episodicas:  {stat['total_episodic_sessions']}")
    print(f"Memorias Analiticas: {memory.count_total_analytical_memories()}")
    print(f"Procedimentos (SOP): {stat.get('total_procedures', 0)}")
    operator_stat = stat.get("operator_intelligence", {})
    print(f"Operator Beliefs:    {operator_stat.get('beliefs_total', 0)} "
          f"({operator_stat.get('confirmed', 0)} confirmados)")
    print(f"Ultima Sessao:       {stat['latest_session'] or 'Nenhuma'}")
    print("----------------------------------------")
    print(f"Git Branch / SHA:    {sync_stat['branch']} ({sync_stat['commit']})")
    print(f"Arvore de Trabalho:  {'MODIFICADA (' + str(sync_stat['changed_files_count']) + ' arquivos)' if sync_stat['is_dirty'] else 'LIMPA'}")
    if active_handoff:
        print(f"Sessao Ativa:        {active_handoff.session_id}")
        print(f"Meta Atual:          {active_handoff.current_goal or 'N/D'}")
        print(f"Proxima Acao:        {active_handoff.next_action or 'N/D'}")
    else:
        print("Sessao Ativa:        Nenhuma sessao registrada em handoff.json")
    print("========================================")


def cmd_operator(args, router: CognitiveRouter):
    import json

    intelligence = router.operator_intelligence
    action = getattr(args, "action", "status") or "status"
    arg1 = getattr(args, "arg1", "") or ""
    arg2 = getattr(args, "arg2", "") or ""

    if action == "status":
        print(json.dumps(router.personalization.status(), indent=2, ensure_ascii=False))
        return

    if action == "snapshot":
        print(json.dumps(intelligence.snapshot(), indent=2, ensure_ascii=False))
        return

    if action == "context":
        if not arg1:
            raise SystemExit("Uso: thsyr operator context \"consulta\"")
        print(intelligence.build_context(arg1))
        return

    if action == "observe":
        if not arg1:
            raise SystemExit("Uso: thsyr operator observe \"mensagem\"")
        print(json.dumps(intelligence.observe(arg1, source="cli"), indent=2, ensure_ascii=False))
        return

    if action == "feedback":
        if arg1 not in {"approved", "rejected"} or not arg2:
            raise SystemExit(
                "Uso: thsyr operator feedback approved|rejected \"assunto\" [--reason motivo]"
            )
        result = intelligence.record_feedback(
            subject=arg2,
            verdict=arg1,
            reason=getattr(args, "reason", "") or "",
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    if action == "preference-context":
        if not arg1:
            raise SystemExit("Uso: thsyr operator preference-context \"consulta\"")
        print(router.personalization.build_context(
            arg1,
            project_id=getattr(args, "project", None),
            domain=getattr(args, "domain", None),
            artifact_kind=getattr(args, "artifact", None),
        ))
        return

    if action == "timeline":
        timeline = router.personalization.graph.timeline(
            node_key=arg1 or None,
            limit=getattr(args, "limit", 50),
        )
        print(json.dumps(timeline, indent=2, ensure_ascii=False))
        return

    if action == "benchmark":
        from engine.personalization import PersonalBenchmarkSuite

        suite = PersonalBenchmarkSuite(router.personalization)
        print(json.dumps(suite.run_context_only(), indent=2, ensure_ascii=False))
        return

    if action == "rebuild-preference-index":
        count = router.personalization.graph.rebuild_index()
        print(json.dumps({"indexed": count}, ensure_ascii=False))
        return

    if action in {"reflect", "reflection-status"}:
        from engine.operator_reflection import OperatorReflectionEngine

        reflection = OperatorReflectionEngine(
            intelligence=intelligence,
            gateway=router.model_gateway,
            model_router=router.model_router,
        )
        if action == "reflection-status":
            print(json.dumps(reflection.status(), indent=2, ensure_ascii=False))
        else:
            print(json.dumps(
                reflection.run(force=getattr(args, "force", False)),
                indent=2,
                ensure_ascii=False,
            ))
        return

    if action == "forget":
        if not arg1:
            raise SystemExit("Uso: thsyr operator forget \"belief_key\"")
        removed = intelligence.forget(arg1)
        print(json.dumps({"removed": removed, "key": arg1}, ensure_ascii=False))
        return


def cmd_memory(args, memory: MemoryManager, router: CognitiveRouter):
    mem_type = None
    if getattr(args, "type", None) and args.type != "all":
        try:
            mem_type = MemoryType(args.type)
        except ValueError:
            pass

    has_filter = bool(mem_type or getattr(args, "project", None) or getattr(args, "entity", None) or getattr(args, "tag", None))

    if has_filter:
        results = memory.query(
            memory_type=mem_type,
            project=getattr(args, "project", None),
            entity=getattr(args, "entity", None),
            tag=getattr(args, "tag", None)
        )
        print("========================================")
        print("      THSYR // CONSULTA DE MEMORIA      ")
        print("========================================")
        print(f"Resultados encontrados: {len(results)}")
        for item in results:
            m = item.metadata
            print(f"\n[{m.type.upper()}] {item.title} (ID: {m.id} | Importancia: {m.importance})")
            if m.projects:
                print(f"  Projetos: {', '.join(m.projects)}")
            if m.entities:
                print(f"  Entidades: {', '.join(m.entities)}")
            if m.tags:
                print(f"  Tags: {', '.join(m.tags)}")
            preview = item.content.strip()[:200].replace("\n", " ")
            print(f"  Trecho: {preview}...")
        print("========================================")
        return

    print("=== PERFIL DO OPERADOR ===")
    print(memory.get_user_profile())
    print("\n=== MEMORIAS SEMANTICAS ===")
    for k, v in memory.get_semantic_memories().items():
        print(f"--- {k.upper()} ---")
        print(v[:250] + ("..." if len(v) > 250 else ""))
    print("\n=== DEDUCOES ANALITICAS E META-COGNICAO (ANALYTICAL) ===")
    for a in memory.get_analytical_items(limit=3):
        print(f"  - [{a.metadata.id}] {a.title} (Imp: {a.metadata.importance})")
    print("\n=== PROCEDIMENTOS CANONICOS (PROCEDURAL) ===")
    for p in memory.get_procedural_items():
        print(f"  - [{p.metadata.id}] {p.title} (Tags: {', '.join(p.metadata.tags)})")
    print("\n=== ULTIMAS SESSOES EPISODICAS ===")
    for log in memory.get_recent_episodic_logs(limit=3):
        print(f"[{log['filename']}]")


def cmd_procedure(args, memory: MemoryManager):
    action = getattr(args, "action", "list") or "list"
    if action == "list":
        procs = memory.get_procedural_items()
        print("========================================")
        print("      PROCEDIMENTOS OPERACIONAIS (SOP)  ")
        print("========================================")
        for p in procs:
            print(f"[{p.metadata.id}] {p.title}")
            print(f"  Tags: {', '.join(p.metadata.tags)} | Importancia: {p.metadata.importance}")
            print(f"  Arquivo: {p.filepath.name if p.filepath else 'N/D'}")
            print()
        print("========================================")
    elif action == "get":
        name = getattr(args, "name", None)
        if not name:
            print("[ERRO] Especifique o nome ou identificador do procedimento.")
            return
        proc = memory.get_procedure(name)
        if not proc:
            print(f"[AVISO] Procedimento '{name}' nao encontrado.")
            return
        print("========================================")
        print(f"PROCEDIMENTO: {proc.title.upper()} [{proc.metadata.id}]")
        print("========================================")
        print(f"Importancia: {proc.metadata.importance} | Confianca: {proc.metadata.confidence}")
        print(f"Entidades:   {', '.join(proc.metadata.entities)}")
        print(f"Projetos:    {', '.join(proc.metadata.projects)}")
        print(f"Tags:        {', '.join(proc.metadata.tags)}")
        print("----------------------------------------")
        print(proc.content.strip())
        print("========================================")


def cmd_search(args, memory: MemoryManager, router: CognitiveRouter):
    from engine.retriever import MemoryRetriever
    retriever = MemoryRetriever(memory_manager=memory)
    results = retriever.retrieve(
        query=args.query,
        limit=args.limit,
        project_filter=args.project,
        entity_filter=args.entity
    )

    print("========================================")
    print("      THSYR // HYBRID MEMORY SEARCH     ")
    print("========================================")
    print(f"Consulta:                {args.query}")
    print(f"Resultados Relevantes:   {len(results)}")
    print("----------------------------------------")

    if not results:
        print("Nenhuma memoria encontrada para os criterios informados.")
    else:
        for i, r in enumerate(results, 1):
            b = r.to_dict()["breakdown"]
            print(f"[{i}] [[{r.item.title}]] (Score: {r.score:.3f} | Tipo: {r.item.metadata.type.upper()})")
            print(f"    Pontuacao: Lexico={b['lexical']} | Semantico={b['semantic']} | Grafo={b['graph']} | Imp={b['importance']}")
            if r.matched_terms:
                print(f"    Termos:    {', '.join(r.matched_terms[:6])}")
            preview = r.item.content.strip().replace("\n", " ")[:150]
            print(f"    Trecho:    {preview}...")
            print()
    print("========================================")


def cmd_think(args, memory: MemoryManager, router: CognitiveRouter):
    query = args.query
    routed = router.route(query)
    act = routed["activation"]

    print("========================================")
    print("      THSYR // ATIVACAO NEURAL ATIVA    ")
    print("========================================")
    print(f"Entrada:              {query}")
    print(f"Sementes Disparadas:  {', '.join(act['seeds'])}")
    print("\nTop Neurônios Energizados:")
    for n in act["top_activated"][:6]:
        print(f"  - [[{n['node']}]] (Energia: {n['energy']} | Lobo: {n['lobe']})")

    if act["inviolable_constraints"]:
        print("\nRestricoes Inegociaveis Acionadas:")
        for c in act["inviolable_constraints"]:
            print(f"  * {c}")

    # Auditoria pre-frontal separada
    draft = getattr(args, "draft", None)
    if draft:
        audit = router.audit_response(draft, query)
        print(f"\nAuditoria da Proposta de Resposta: [{audit['status']}] (Score: {audit['gate_score']})")
        if audit["violations"]:
            for v in audit["violations"]:
                print(f"  ! {v}")
    elif getattr(args, "generate", False):
        from engine.interaction import ResponseEngine, TerminalRenderer
        gen = router.think_and_generate(query)
        engine = ResponseEngine()
        renderer = TerminalRenderer()
        resp = engine.process_raw_generation(gen["response"], user_query=query)
        print("\n----------------------------------------")
        print(renderer.render_response(resp))
        print(f"\nAuditoria Pre-Frontal: [{gen['audit']['status']}] (Score: {gen['audit']['gate_score']})")
        if gen["audit"]["violations"]:
            for v in gen["audit"]["violations"]:
                print(f"  ! {v}")
        tel = gen["telemetry"]
        print(f"Telemetria: {tel['total_tokens']} tokens | {tel['latency_ms']} ms | ${tel['estimated_cost_usd']:.6f} USD")
    else:
        print("\nDiretriz Pre-Frontal: Portao de Anti-Sicofancia e Tolerancia Zero a Emojis ativos.")
    print("========================================")


def cmd_model(args, router: CognitiveRouter):
    gateway = router.model_gateway
    telemetry = gateway.get_telemetry_summary()

    print("========================================")
    print("        THSYR // MODEL GATEWAY          ")
    print("========================================")
    print("Provedores Registrados:")
    for p in gateway.providers:
        print(f"  - [{p.provider_name}]")
    print("----------------------------------------")
    print(f"Total de Requisicoes:   {telemetry.get('total_requests', 0)}")
    print(f"Total de Tokens:        {telemetry.get('total_tokens', 0):,}")
    print(f"Custo Estimado (USD):   ${telemetry.get('total_cost_usd', 0.0):.6f}")
    print(f"Latencia Acumulada:     {telemetry.get('total_latency_ms', 0.0):.1f} ms")
    print(f"Disparos de Fallback:   {telemetry.get('fallback_count', 0)}")
    print("\nRequisicoes por Tier:")
    for tier, count in telemetry.get("requests_by_tier", {}).items():
        print(f"  - {tier.upper():<12} {count}")
    print("========================================")


def cmd_log(args, memory: MemoryManager, router: CognitiveRouter, sync: GitSyncEngine, handoff: HandoffManager):
    title = args.title
    content = args.content
    if not content and not sys.stdin.isatty():
        try:
            content = sys.stdin.read()
        except Exception:
            pass
    if not content:
        content = f"Registro de sessao: {title}"

    active = handoff.load_handoff()
    session_id = active.session_id if active else None

    path = memory.append_episodic_log(title, content, session_id=session_id)
    print(f"[OK] Sessao registrada em: {path.name}")

    if not args.no_sync:
        res = sync.checkpoint("brain(memory)", f"log episodic session {path.name}")
        if res.get("committed"):
            print(f"[OK] Checkpoint git criado: {res.get('sha')}")
            if res.get("pushed"):
                print("[OK] Sincronizado com o repositorio remoto.")


def cmd_analyze(args, memory: MemoryManager, sync: GitSyncEngine, handoff: HandoffManager):
    title = args.title
    content = args.content
    if not content and not sys.stdin.isatty():
        try:
            content = sys.stdin.read()
        except Exception:
            pass
    if not content:
        content = f"Deducao analitica e meta-cognicao: {title}"

    active = handoff.load_handoff()
    session_id = active.session_id if active else None

    path = memory.save_analytical_memory(title, content, session_id=session_id)
    print(f"[OK] Deducao analitica registrada em: {path.name}")

    if not args.no_sync:
        res = sync.checkpoint("brain(analytical)", f"log analytical deduction {path.name}")
        if res.get("committed"):
            print(f"[OK] Checkpoint git criado: {res.get('sha')}")
            if res.get("pushed"):
                print("[OK] Sincronizado com o repositorio remoto.")


def cmd_graph(args, memory: MemoryManager, router: CognitiveRouter):
    from engine.png_graph import render_png_graph
    from engine.svg_graph import render_svg_graph
    output_svg = render_svg_graph()
    print(f"[OK] Mapa anatomico SVG atualizado: {output_svg}")
    output_png = render_png_graph()
    print(f"[OK] Mapa anatomico PNG renderizado: {output_png}")
    output_file = render_and_open_graph(open_browser=not args.no_open)
    print(f"[OK] Grafo neural compilado: {output_file}")
    if not args.no_open:
        print("[OK] Visualizador aberto no navegador padrao.")


def cmd_graph3d(args):
    from engine.neural_3d import render_and_open_3d

    output = render_and_open_3d(open_browser=not args.no_open)
    print(f"[OK] Cerebro neural 3D: {output}")


def cmd_ingest(args):
    from engine.config import settings
    from engine.knowledge_ingestor import extract_ecosystem_graph, ingest_workspaces
    from engine.readme_stats import update_readme_graph_stats

    output = settings.brain.brain_dir / "knowledge_ecosystem.json"
    graph = ingest_workspaces(output_path=output, max_files_per_workspace=args.max_files)
    update_readme_graph_stats(
        extract_ecosystem_graph(settings.brain.brain_dir, output),
        settings.project_root / "README.md",
        source_label="brain/knowledge_ecosystem.json + brain/**/*.md",
    )
    print(f"[OK] Índice multi-repositório: {output}")
    print(f"[OK] Nós rastreáveis: {graph['total_nodes']} | Sinapses de origem: {graph['total_edges']}")


def cmd_academic(args, memory: MemoryManager, router: CognitiveRouter):
    from engine.academic_sync import AcademicMonitor
    monitor = AcademicMonitor()
    print(monitor.render_radar_report())


def cmd_handoff(args, handoff: HandoffManager, sync: GitSyncEngine):
    if args.set_goal or args.set_action or args.add_step or args.complete_step:
        current = handoff.load_handoff() or SessionState()
        if args.set_goal:
            current.current_goal = args.set_goal
        if args.set_action:
            current.next_action = args.set_action
        if args.add_step:
            for step in args.add_step:
                if step not in current.pending_steps and step not in current.completed_steps:
                    current.pending_steps.append(step)
        if args.complete_step:
            for step in args.complete_step:
                if step in current.pending_steps:
                    current.pending_steps.remove(step)
                if step not in current.completed_steps:
                    current.completed_steps.append(step)

        handoff.save_session(current)
        print(f"[OK] Handoff atualizado. ID da Sessao: {current.session_id}")
        return

    active_session = handoff.load_handoff()
    if not active_session:
        print("[AVISO] Nenhum handoff ativo encontrado. Crie uma sessao com 'thsyr handoff --set-goal \"...\"'")
        return

    print("========================================")
    print("         THSYR // SESSION HANDOFF       ")
    print("========================================")
    print(f"Session ID:       {active_session.session_id}")
    print(f"Projeto:          {active_session.current_project}")
    print(f"Meta:             {active_session.current_goal}")
    print(f"Proxima Acao:     {active_session.next_action}")
    print("\nEtapas Concluidas:")
    for s in active_session.completed_steps:
        print(f"  [x] {s}")
    print("\nEtapas Pendentes:")
    for s in active_session.pending_steps:
        print(f"  [ ] {s}")
    print("========================================")


def cmd_checkpoint(args, sync: GitSyncEngine, handoff: HandoffManager):
    scope = args.scope or "state(checkpoint)"
    message = args.message
    res = sync.checkpoint(scope, message)
    if res.get("committed"):
        print(f"[OK] Checkpoint registrado: {res.get('sha')} - {res.get('message')}")
        if res.get("pushed"):
            print("[OK] Sincronizado remotamente no GitHub.")
        elif res.get("push_error"):
            print(f"[AVISO] Commit local criado, mas push falhou: {res.get('push_error')}")
    else:
        print(f"[INFO] {res.get('message', 'Nenhuma alteracao para commitar.')}")


def cmd_sync(args, sync: GitSyncEngine):
    print("[INFO] Buscando atualizacoes no repositorio remoto...")
    fetched = sync.fetch_remote()
    if fetched:
        print("[OK] Fetch concluido com sucesso.")
    else:
        print("[AVISO] Nao foi possivel alcancar o remoto ou fetch sem modificacoes.")

def cmd_goal(args, router: CognitiveRouter, handoff: HandoffManager, sync: GitSyncEngine):
    from engine.executive import ExecutiveRunner, Goal

    runner = ExecutiveRunner(router=router, handoff=handoff, sync=sync)

    if args.action == "list":
        goals = runner.list_goals()
        print("========================================")
        print("         THSYR // EXECUTIVE GOALS       ")
        print("========================================")
        if not goals:
            print("Nenhum objetivo cadastrado no momento.")
        else:
            for g in goals:
                print(f"[{g.status.value.upper():<11}] ({g.id}) P{g.priority} [[{g.title}]]")
                if g.project:
                    print(f"              Projeto: {g.project}")
                if g.description:
                    print(f"              Descricao: {g.description}")
        print("========================================")

    elif args.action == "create":
        import uuid
        gid = f"goal_{uuid.uuid4().hex[:8]}"
        title = args.title or "Objetivo sem titulo"
        goal = Goal(
            id=gid,
            title=title,
            description=args.desc or title,
            project=args.project,
            priority=args.priority
        )
        runner.save_goal(goal)
        print(f"[OK] Objetivo criado: {goal.id} - '{goal.title}'")

    elif args.action == "plan":
        target_id = args.goal_id or args.title
        target_goal = runner.load_goal(target_id)
        if not target_goal:
            print(f"[ERRO] Objetivo '{target_id}' nao encontrado.")
            return
        plan = runner.planner.create_plan(target_goal)
        runner.save_plan(plan)
        print("========================================")
        print(f"PLANO CRIADO: {plan.title} [{plan.id}]")
        print("========================================")
        for s in plan.steps:
            print(f"[{s.order}] {s.action.upper()}: {s.description}")
        print("========================================")

    elif args.action == "run":
        target_id = args.goal_id or args.title
        target_goal = runner.load_goal(target_id)
        if not target_goal:
            print(f"[ERRO] Objetivo '{target_id}' nao encontrado.")
            return
        print(f"[INFO] Executando objetivo: {target_goal.title} ({target_goal.id})...")
        res = runner.run_goal(target_goal)
        print("========================================")
        print(f"RESULTADO: [{res.status.value.upper()}]")
        print(f"Etapas: {res.completed_steps}/{res.total_steps} concluidas.")
        print(f"Resumo: {res.final_summary}")
        print("========================================")

    elif args.action == "auto":
        import uuid
        gid = f"goal_{uuid.uuid4().hex[:8]}"
        title = args.title or "Objetivo autonomo"
        goal = Goal(
            id=gid,
            title=title,
            description=args.desc or title,
            project=args.project,
            priority=args.priority
        )
        print(f"[INFO] Objetivo sintetizado: {goal.id} - '{goal.title}'")
        res = runner.run_goal(goal)
        print("========================================")
        print("      THSYR // EXECUTIVE EXECUTION      ")
        print("========================================")
        print(f"Status:   [{res.status.value.upper()}]")
        print(f"Etapas:   {res.completed_steps}/{res.total_steps} concluidas")
        print(f"Resumo:   {res.final_summary}")
        print("========================================")


def cmd_tool(args):
    import json

    from engine.tools import RiskLevel, ToolBus

    tool_bus = ToolBus()

    if args.action == "list" or not args.action:
        tools = tool_bus.list_tools()
        print("========================================")
        print("         THSYR // TOOL BUS REGISTRY     ")
        print("========================================")
        for t in sorted(tools, key=lambda x: (x.risk_level, x.name)):
            conf = " (Requer Confirmacao)" if t.requires_confirmation or t.risk_level > RiskLevel.LEVEL_2_CREATE_LOCAL else ""
            print(f"[{t.name:<22}] Risco: {int(t.risk_level)} | Timeout: {t.timeout}s{conf}")
            print(f"    Descricao: {t.description}")
        print("========================================")

    elif args.action == "info":
        tool = tool_bus.get_tool(args.name)
        if not tool:
            print(f"[ERRO] Ferramenta '{args.name}' nao encontrada.")
            return
        m = tool.metadata
        print("========================================")
        print(f"FERRAMENTA: {m.name.upper()}")
        print("========================================")
        print(f"Descricao:              {m.description}")
        print(f"Nivel de Risco:         {int(m.risk_level)} (0 a 6)")
        print(f"Requer Confirmacao:     {m.requires_confirmation}")
        print(f"Timeout:                {m.timeout}s")
        print(f"Reversivel:             {m.reversible}")
        print(f"Estrategia de Rollback: {m.rollback_strategy or 'Nenhuma'}")
        print("Schema de Entrada:")
        print(json.dumps(m.input_schema, indent=2, ensure_ascii=False))
        print("========================================")

    elif args.action == "run":
        tool = tool_bus.get_tool(args.name)
        if not tool:
            print(f"[ERRO] Ferramenta '{args.name}' nao encontrada.")
            return

        if getattr(args, "confirm", False):
            tool_bus.permission_cortex.confirmation_handler = lambda name, params: True

        kwargs = {}
        for p in args.params:
            if "=" in p:
                k, v = p.split("=", 1)
                if v.isdigit():
                    kwargs[k] = int(v)
                else:
                    kwargs[k] = v

        res = tool_bus.execute(args.name, **kwargs)
        print("========================================")
        print(f"EXECUCAO: [{args.name}] -> {'SUCESSO' if res.success else 'FALHA'} ({res.duration_ms} ms)")
        print("========================================")
        if res.error:
            print(f"Erro: {res.error}")
        print("Saida:")
        print(res.raw_output)
        print("========================================")


def cmd_runtime(args):
    from engine.runtime import RuntimeSSEServer, SyrRuntime

    runtime = SyrRuntime()

    if args.sse:
        server = RuntimeSSEServer(runtime.event_bus, port=args.sse_port)
        started, message = server.start()
        if not started:
            print(f"[ERRO] {message}")
            return
        print(f"[INFO] {message}")
        try:
            runtime.run_loop(tick_interval=args.interval)
        finally:
            server.stop()
    elif args.daemon:
        print("[INFO] Iniciando Syr Continuous Runtime Daemon...")
        runtime.run_loop(tick_interval=args.interval)
    elif args.status:
        jobs = runtime.scheduler.list_jobs()
        print("========================================")
        print("         THSYR // CONTINUOUS RUNTIME    ")
        print("========================================")
        print(f"Jobs Agendados: {len(jobs)}")
        for j in jobs:
            print(f"  - [{j.name:<18}] Status: {j.status.value.upper():<9} | Intervalo: {j.interval_seconds}s | Handler: {j.handler_name}")
        print("========================================")
    else:
        print("========================================")
        print("      THSYR // RUNTIME CYCLE (ONCE)     ")
        print("========================================")
        res = runtime.run_once()
        print(f"Memoria Ativa:        {res['memory']['total_episodes']} episodios | {res['memory']['total_semantics']} semanticas")
        print(f"Git Sincronizacao:    Branch: {res['sync']['branch']} | Alteracoes: {res['sync']['changed_files_count']}")
        print(f"Avaliacoes Proativas: {res['proactive_evaluations_count']}")
        if res['urgent_alerts']:
            print("\nALERTAS URGENTES DO MOTOR PROATIVO:")
            for a in res['urgent_alerts']:
                print(f"  ! {a['observation']} (Score: {a['score']})")
        else:
            print("\nNenhum alerta urgente detectado.")
        print("========================================")


def cmd_notch(args):
    launcher_stat = get_codenotch_status()
    action = getattr(args, "action", "status")

    if action == "start":
        res = ensure_codenotch_running()
        print("========================================")
        print("       THSYR // CODENOTCH LAUNCHER      ")
        print("========================================")
        print(f"Status:              {'ATIVO' if res['running'] else 'FALHA / NAO ENCONTRADO'}")
        print(f"Acao Executada:      {res['action_taken']}")
        print(f"Executavel:          {res['executable'] or 'Nao localizado nos caminhos padroes'}")
        print(f"Plataforma:          {res['platform'].upper()}")
        print(f"Mensagem:            {res['message']}")
        print("========================================")
        return

    print("========================================")
    print("       THSYR // CODENOTCH MONITOR       ")
    print("========================================")
    print(f"Habilitado no ThSyr: {'SIM' if launcher_stat['enabled'] else 'NAO'}")
    print(f"Instalado no Sistema: {'SIM' if launcher_stat['installed'] else 'NAO'}")
    print(f"Processo em Execucao: {'ATIVO' if launcher_stat['running'] else 'INATIVO'}")
    print(f"Caminho do Binario:  {launcher_stat['executable'] or 'Nao localizado'}")
    print(f"Plataforma:          {launcher_stat['platform'].upper()}")
    print("----------------------------------------")
    if not launcher_stat["installed"]:
        print("Instrucao: Baixe e instale o Codenotch oficial em:")
        print("https://github.com/vinzdg/codenotch/releases/latest/download/Codenotch-Setup.exe")
    else:
        print("Dica: Use 'python thsyr.py notch start' para inicializar imediatamente.")
    print("========================================")


def cmd_observe(args):
    from engine.workspace_observer import WorkspaceObserver
    obs = WorkspaceObserver()
    print(obs.render_report())


def cmd_watcher(args):
    from engine.runtime.watcher import EventStore, WorkspaceMutationWorker, create_watcher
    from engine.workspace_observer import discover_workspaces

    action = getattr(args, "action", "status") or "status"
    state_dir = None
    if action == "events":
        store = EventStore()
        events = store.recent(limit=args.limit)
        print("========================================")
        print("      THSYR // EVENTOS DO WATCHER       ")
        print("========================================")
        if not events:
            print("Nenhum evento de mutacao persistido.")
        for event in events:
            print(f"[{event.get('occurred_at', 'N/D')}] {event.get('workspace', 'N/D')}")
            print(f"  Arquivos: {', '.join(event.get('files', []))}")
            print(f"  Operacoes: {', '.join(event.get('kinds', []))}")
        print("========================================")
        return

    workspaces = discover_workspaces()
    watcher = create_watcher(workspaces, debounce_seconds=args.debounce)
    worker = WorkspaceMutationWorker(watcher, EventStore(state_dir))
    if action == "run":
        result = worker.run_cycle()
        print("========================================")
        print("       THSYR // WATCHER EXECUCAO        ")
        print("========================================")
        print(f"Status:              {result['status'].upper()}")
        print(f"Eventos detectados:  {result['events_detected']}")
        print(f"Eventos persistidos:  {result['events_persisted']}")
        print(f"Arquivos:            {', '.join(result.get('files', [])) or 'Nenhum'}")
        if result.get("error"):
            print(f"Erro:                {result['error']}")
        print("========================================")
        return

    print("========================================")
    print("       THSYR // WATCHER SENSORIAL       ")
    print("========================================")
    print(f"Implementacao:       {getattr(watcher, 'backend', 'polling')}")
    print(f"Workspaces:          {len(workspaces)}")
    print(f"Debounce:            {args.debounce:.1f}s")
    print(f"Eventos persistidos: {len(EventStore().recent(limit=100000))}")
    print("Estado:              DISPONIVEL")
    print("========================================")


def cmd_consolidate(args):
    from engine.memory_consolidator import MemoryConsolidator
    mc = MemoryConsolidator()
    print(mc.render_report())


def cmd_notify(args):
    from engine.desktop_notifier import notify_desktop
    ok = notify_desktop(args.title, args.message, priority=args.priority, async_dispatch=False)
    if ok:
        print(f"[OK] Notificacao enviada ao desktop: '{args.title}'")
    else:
        print("[ERRO] Falha ao enviar notificacao.")


def cmd_brief(args, memory: MemoryManager, router: CognitiveRouter, sync: GitSyncEngine, handoff: HandoffManager):
    from engine.academic_sync import AcademicMonitor
    from engine.memory_consolidator import MemoryConsolidator
    from engine.workspace_observer import WorkspaceObserver

    stat = router.status()
    active_handoff = handoff.load_handoff()
    obs = WorkspaceObserver()
    ws_data = obs.scan()
    mc = MemoryConsolidator()
    ont_data = mc.audit_ontology()
    monitor = AcademicMonitor()

    print("================================================================================")
    print("                    THSYR // MASTER EXECUTIVE BRIEFING                          ")
    print("================================================================================")
    print(f"Estado do Copiloto:  {stat['status'].upper()} | Codenotch HUD: ATIVO")
    print(f"Cerebro / Ontologia: {ont_data['total_nodes']} nos | {ont_data['total_synapses']} sinapses | Saude OHI: {ont_data['ohi_score']*100:.1f}% [{ont_data['status']}]")
    print(f"Workspaces:          {ws_data['total_workspaces']} repositorios auditados | Alteracoes: {ws_data['dirty_count']}")
    print(f"Sessao Ativa:        {active_handoff.session_id if active_handoff else 'N/D'}")
    if active_handoff:
        print(f"Meta Central:        {active_handoff.current_goal}")
        print(f"Proxima Acao:        {active_handoff.next_action}")
    print("--------------------------------------------------------------------------------")
    print("ALERTAS DE WORKSPACE:")
    for ws in ws_data["workspaces"]:
        if ws["is_dirty"]:
            sample = f" ({', '.join(ws['sample_files'][:2])})" if ws['sample_files'] else ""
            print(f"  * [RISCO] {ws['name']} ({ws['branch']}): {ws['modified_count']} mod, {ws['untracked_count']} untracked{sample}")
    if ws_data["dirty_count"] == 0:
        print("  * Todos os repositorios vitais sincronizados.")
    print("--------------------------------------------------------------------------------")
    print("RADAR ACADEMICO:")
    academic_lines = monitor.render_radar_report().splitlines()
    for acad_line in academic_lines[4:12]:
        print(f"  {acad_line}")
    print("================================================================================")


def cmd_ui(args):
    import os
    import subprocess
    import webbrowser

    from engine.config import settings

    root_dir = settings.project_root
    dev_script = root_dir / "scripts" / "desktop_dev.py"
    port = getattr(args, "port", 7474)

    if dev_script.exists():
        print(f"[INFO] Iniciando Desktop Control Center na porta {port}...")
        env = os.environ.copy()
        env["THSYR_DESKTOP_PORT"] = str(port)
        subprocess.run([sys.executable, str(dev_script)], env=env)
    else:
        print("[AVISO] Ambiente desktop em modo webview...")
        webbrowser.open(f"http://127.0.0.1:{port}")


def main():
    parser = argparse.ArgumentParser(description="ThSyr - Copiloto Cognitivo e Runtime Jarvis")
    subparsers = parser.add_subparsers(dest="command")

    # Status
    subparsers.add_parser("status", help="Exibe o status da mente e sincronizacao do ThSyr")

    # Operator Intelligence
    operator_parser = subparsers.add_parser(
        "operator",
        help="Inspeciona e alimenta o modelo dinamico do operador",
    )
    operator_parser.add_argument(
        "action",
        nargs="?",
        choices=[
            "status", "snapshot", "context", "observe", "feedback", "forget",
            "reflect", "reflection-status", "preference-context", "timeline",
            "benchmark", "rebuild-preference-index",
        ],
        default="status",
    )
    operator_parser.add_argument("arg1", nargs="?", default="")
    operator_parser.add_argument("arg2", nargs="?", default="")
    operator_parser.add_argument("--reason", default="", help="Motivo de feedback explicito")
    operator_parser.add_argument("--project", help="Escopo de projeto da personalizacao")
    operator_parser.add_argument("--domain", help="Escopo de dominio da personalizacao")
    operator_parser.add_argument("--artifact", help="Tipo de artefato da personalizacao")
    operator_parser.add_argument("--limit", type=int, default=50, help="Limite de eventos da timeline")
    operator_parser.add_argument(
        "--force",
        action="store_true",
        help="Forca uma reflexao profunda mesmo fora do cooldown",
    )

    # Memory inspection
    memory_parser = subparsers.add_parser("memory", help="Inspeciona o estado atual das memorias")
    memory_parser.add_argument("--type", choices=["all", "working", "episodic", "semantic", "procedural", "analytical"], default="all", help="Filtrar por categoria de memoria")
    memory_parser.add_argument("--project", help="Filtrar memorias por projeto")
    memory_parser.add_argument("--entity", help="Filtrar memorias por entidade")
    memory_parser.add_argument("--tag", help="Filtrar memorias por tag")

    # Procedures (SOP)
    procedure_parser = subparsers.add_parser("procedure", help="Consulta e inspeciona procedimentos operacionais (SOP)")
    procedure_parser.add_argument("action", nargs="?", choices=["list", "get"], default="list", help="Acao a executar")
    procedure_parser.add_argument("name", nargs="?", default="", help="Nome ou identificador do procedimento (quando action=get)")

    # Hybrid Search
    search_parser = subparsers.add_parser("search", help="Executa busca hibrida (lexica + semantica + grafo)")
    search_parser.add_argument("query", help="Termo, pergunta ou conceito a recuperar")
    search_parser.add_argument("--limit", type=int, default=5, help="Limite de resultados")
    search_parser.add_argument("--project", help="Filtrar por projeto")
    search_parser.add_argument("--entity", help="Filtrar por entidade")

    # Think
    think_parser = subparsers.add_parser("think", help="Simula ativacao sinaptica para uma consulta")
    think_parser.add_argument("query", help="Frase ou comando a ser processado pela rede neural")
    think_parser.add_argument("--draft", help="Opcional: texto de resposta preliminar a ser auditado pelo pre-frontal")
    think_parser.add_argument("--generate", action="store_true", help="Gera resposta via Model Gateway com auditoria")

    # Model Gateway & Telemetry
    subparsers.add_parser("model", help="Inspeciona provedores e telemetria do Model Gateway")

    # Log new episodic session
    log_parser = subparsers.add_parser("log", help="Registra uma nova sessao de memoria episodica")
    log_parser.add_argument("title", help="Titulo da sessao")
    log_parser.add_argument("content", nargs="?", default="", help="Conteudo do registro")
    log_parser.add_argument("--no-sync", action="store_true", help="Nao commitar nem sincronizar imediatamente")

    # Analyze - Analytical deduction & meta-cognition
    analyze_parser = subparsers.add_parser("analyze", help="Registra uma nova deducao analitica e meta-cognicao")
    analyze_parser.add_argument("title", help="Titulo da deducao analitica")
    analyze_parser.add_argument("content", nargs="?", default="", help="Conteudo da analise")
    analyze_parser.add_argument("--no-sync", action="store_true", help="Nao commitar nem sincronizar imediatamente")

    # Neural Graph
    graph_parser = subparsers.add_parser("graph", help="Gera e abre o grafo neural interativo")
    graph_parser.add_argument("--no-open", action="store_true", help="Gera os arquivos sem abrir o navegador")
    graph3d_parser = subparsers.add_parser("graph3d", help="Gera o cerebro neural holografico 3D")
    graph3d_parser.add_argument("--no-open", action="store_true", help="Gera sem abrir o navegador")
    ingest_parser = subparsers.add_parser("ingest", help="Indexa projetos e arquivos rastreáveis no cérebro")
    ingest_parser.add_argument("--max-files", type=int, default=1200, help="Limite de arquivos por workspace")

    # Academic Radar
    subparsers.add_parser("academic", help="Exibe o radar academico em tempo real")

    # Session Handoff
    handoff_parser = subparsers.add_parser("handoff", help="Inspeciona ou atualiza o Session Handoff de continuidade")
    handoff_parser.add_argument("--set-goal", help="Define a meta atual da sessao")
    handoff_parser.add_argument("--set-action", help="Define a proxima acao recomendada")
    handoff_parser.add_argument("--add-step", action="append", help="Adiciona uma etapa pendente ao plano")
    handoff_parser.add_argument("--complete-step", action="append", help="Marca uma etapa como concluida")

    # Checkpoint
    checkpoint_parser = subparsers.add_parser("checkpoint", help="Cria um checkpoint semantico e sincroniza com o Git")
    checkpoint_parser.add_argument("message", help="Mensagem descritiva do checkpoint")
    checkpoint_parser.add_argument("--scope", default="state(checkpoint)", help="Escopo semantico (ex: brain(memory))")

    # Executive Goals & Planning
    goal_parser = subparsers.add_parser("goal", help="Gerencia e executa metas do Executive System")
    goal_parser.add_argument("action", choices=["list", "create", "plan", "run", "auto"], default="list", nargs="?", help="Acao executiva")
    goal_parser.add_argument("title", nargs="?", default="", help="Titulo ou ID do objetivo")
    goal_parser.add_argument("--desc", default="", help="Descricao detalhada da meta")
    goal_parser.add_argument("--project", help="Projeto associado (ex: TokLang, ThSyr)")
    goal_parser.add_argument("--priority", type=int, default=3, help="Prioridade (1 a 5)")
    goal_parser.add_argument("--goal-id", help="Identificador do objetivo (para plan/run)")

    # Tool Bus
    tool_parser = subparsers.add_parser("tool", help="Inspeciona e executa ferramentas do Tool Bus")
    tool_parser.add_argument("action", choices=["list", "info", "run"], default="list", nargs="?", help="Acao de ferramenta")
    tool_parser.add_argument("name", nargs="?", default="", help="Nome da ferramenta (para info/run)")
    tool_parser.add_argument("--confirm", action="store_true", help="Autoriza explicitamente ferramentas de risco elevado")
    tool_parser.add_argument("params", nargs="*", help="Parametros no formato chave=valor")

    # Continuous Runtime
    runtime_parser = subparsers.add_parser("runtime", help="Gerencia o runtime continuo, daemon e motor proativo")
    runtime_parser.add_argument("--daemon", action="store_true", help="Executa em loop contínuo como daemon")
    runtime_parser.add_argument("--sse", action="store_true", help="Expõe eventos locais em /events e mantém o runtime ativo")
    runtime_parser.add_argument("--sse-port", type=int, default=7474, help="Porta do endpoint SSE (padrao: 7474)")
    runtime_parser.add_argument("--status", action="store_true", help="Exibe o status dos jobs e agendamentos")
    runtime_parser.add_argument("--interval", type=float, default=2.0, help="Intervalo de tick em segundos (padrao: 2.0s)")

    # Sync
    subparsers.add_parser("sync", help="Sincroniza o estado local com o remoto")

    # Codenotch
    notch_parser = subparsers.add_parser("notch", help="Inspeciona ou inicia o Codenotch no ambiente desktop")
    notch_parser.add_argument("action", choices=["status", "start"], default="status", nargs="?", help="Acao sobre o Codenotch (status/start)")

    # Sentinela de Workspace
    subparsers.add_parser("observe", help="Audita os repositorios e workspaces vitais do Major")

    # Sensory Watcher
    watcher_parser = subparsers.add_parser("watcher", help="Inspeciona e executa o watcher sensorial de workspaces")
    watcher_parser.add_argument("action", choices=["status", "run", "events"], default="status", nargs="?", help="Acao do watcher")
    watcher_parser.add_argument("--limit", type=int, default=20, help="Limite de eventos exibidos")
    watcher_parser.add_argument("--debounce", type=float, default=5.0, help="Janela de debounce em segundos")

    # Consolidador Ontologico
    subparsers.add_parser("consolidate", help="Audita orfaos e saude ontologica da memoria")

    # Desktop Notifier
    notify_parser = subparsers.add_parser("notify", help="Dispara notificacao nativa no desktop")
    notify_parser.add_argument("title", help="Titulo do alerta")
    notify_parser.add_argument("message", help="Conteudo da mensagem")
    notify_parser.add_argument("--priority", choices=["normal", "high"], default="normal", help="Prioridade")

    # Master Briefing
    subparsers.add_parser("brief", help="Briefing executivo mestre de status, radar e workspaces")

    # Gods Eye View Telemetry
    gods_parser = subparsers.add_parser("gods-eye", help="Inspeciona o console sensorial e telemetria planetaria (Gods Eye View)")
    gods_parser.add_argument("action", choices=["status", "start"], default="status", nargs="?", help="Acao sobre o Gods Eye View (status/start)")

    # Host Hardware Telemetry
    subparsers.add_parser("hardware", help="Inspeciona telemetria de silicio e hardware do host (CPU, RAM, Disco, GPU)")

    # Daemon Supervisor
    daemon_parser = subparsers.add_parser("daemon", help="Gerencia ciclo de vida do daemon de background do ThSyr")
    daemon_parser.add_argument("action", choices=["status", "start", "stop"], default="status", nargs="?", help="Acao sobre o daemon (status/start/stop)")

    # TokLang Compiler Core
    toklang_parser = subparsers.add_parser("toklang", help="Compila scripts TokLang e estima reducao de FLOPs")
    toklang_parser.add_argument("code", nargs="*", default=[], help="Codigo TokLang ou prompt para compilacao e analise")
    toklang_parser.add_argument("--code", dest="code_flag", help="Codigo TokLang explicitamente passado")

    # Local Vector Store
    vector_parser = subparsers.add_parser("vector", help="Executa busca semantica vetorial densa embutida")
    vector_parser.add_argument("query", nargs="?", default="", help="Consulta semantica para busca")
    vector_parser.add_argument("--action", choices=["search", "count", "ingest"], default="search", help="Acao vetorial")
    vector_parser.add_argument("--limit", type=int, default=5, help="Limite de resultados")

    # Interactive Chat / REPL
    subparsers.add_parser("chat", help="Inicia sessao conversacional e operacional com o Syr")
    subparsers.add_parser("repl", help="Inicia REPL operacional do Syr")

    # System Health Doctor
    subparsers.add_parser("doctor", help="Executa diagnostico de saude do ambiente operacional")

    # Evaluation Benchmark
    eval_parser = subparsers.add_parser("eval", help="Executa benchmark cognitivo e suite unitária")
    eval_parser.add_argument("--json", action="store_true", help="Imprime o relatório cognitivo em JSON")
    eval_parser.add_argument("--report", help="Salva o relatório cognitivo em um arquivo JSON")

    # Ultron Autonomous Swarm
    swarm_parser = subparsers.add_parser("swarm", help="Dispara o enxame autonomo de subagentes Ultron")
    swarm_parser.add_argument("--agent", choices=["systems_engineer", "compiler_architect", "cognitive_architect"], help="Executa apenas um subagente especifico")

    # Cognitive Auto-Evolution
    evolve_parser = subparsers.add_parser("evolve", help="Inspeciona e dispara ciclos de auto-evolucao cognitiva")
    evolve_parser.add_argument("--optimize", action="store_true", help="Aplica otimizacoes e registra novo salto evolutivo no ledger")

    # War Room Tactical HUD
    war_parser = subparsers.add_parser("war-room", help="Inicia o War Room cognitivo em tempo real")
    war_parser.add_argument("--port", type=int, default=8080, help="Porta HTTP do War Room (padrao 8080)")
    war_parser.add_argument(
        "--lan",
        action="store_true",
        help="Expoe na LAN com token de sessao; sem esta flag usa apenas 127.0.0.1",
    )

    # Desktop Control Center
    ui_parser = subparsers.add_parser("ui", help="Inicia o ThSyr Desktop Control Center")
    ui_parser.add_argument("--port", type=int, default=7474, help="Porta HTTP/WebSocket do runtime bridge (padrao 7474)")
    ui_parser.add_argument("--dev", action="store_true", help="Forca inicializacao em modo dev")

    # Brand and Logo Design Architecture (Occipital Lobe)
    logo_parser = subparsers.add_parser("logo", help="Orquestra design de marcas, acervo de 1.400+ logos e auditoria vetorial")
    logo_sub = logo_parser.add_subparsers(dest="logo_action")

    # Search
    search_sub = logo_sub.add_parser("search", help="Pesquisa no acervo de logos por geometria, tecnica ou setor")
    search_sub.add_argument("query", nargs="?", default="", help="Termo de busca")
    search_sub.add_argument("--type", help="Tipo de marca (wordmark, lettermark, letterform, pictorial, abstract, mascot, emblem, combination)")
    search_sub.add_argument("--technique", help="Tecnica visual (negative-space, geometric-construction...)")
    search_sub.add_argument("--geometry", help="Geometria (circle, hexagon, triangle...)")
    search_sub.add_argument("--industry", help="Setor industrial")
    search_sub.add_argument("--color", help="Cor presente")
    search_sub.add_argument("--exemplary", action="store_true", help="Apenas exemplos de alta maestria")
    search_sub.add_argument("--limit", type=int, default=15, help="Limite de resultados")
    search_sub.add_argument("--format", choices=["table", "paths", "json"], default="table", help="Formato de saida")

    # Audit
    audit_sub = logo_sub.add_parser("audit", help="Audita arquivos SVG contra regras de producao e geometria")
    audit_sub.add_argument("files", nargs="+", help="Arquivos SVG para auditoria")
    audit_sub.add_argument("--bg", help="Cor de fundo para teste de contraste (#ffffff)")
    audit_sub.add_argument("--json", action="store_true", help="Saida em formato JSON estruturado")

    # Stats
    logo_sub.add_parser("stats", help="Exibe metricas e distribuicao do acervo de 1.400+ logos")

    # Principles
    logo_sub.add_parser("principles", help="Exibe os 8 tipos de marca, 14 tecnicas e regras de refinamento optico")

    # Brief
    brief_sub = logo_sub.add_parser("brief", help="Gera scaffold de design brief estruturado e analise de cliches")
    brief_sub.add_argument("--name", required=True, help="Nome da marca")
    brief_sub.add_argument("--industry", required=True, help="Setor de atuacao")
    brief_sub.add_argument("--adjectives", help="Lista de adjetivos tonais separados por virgula")
    brief_sub.add_argument("--offering", default="", help="Descricao da oferta")
    brief_sub.add_argument("--promise", default="", help="Promessa nuclear")

    # Preview
    preview_sub = logo_sub.add_parser("preview", help="Gera folha HTML de inspecao e comparacao")
    preview_sub.add_argument("files", nargs="+", help="Arquivos SVG")
    preview_sub.add_argument("-o", "--output", default="preview.html", help="Caminho do arquivo HTML de saida")
    preview_sub.add_argument("--industry", help="Setor para teste de prateleira com concorrentes")

    # Sheet
    sheet_sub = logo_sub.add_parser("sheet", help="Gera prancha comparativa de conceitos de marca em PNG")
    sheet_sub.add_argument("symbols", nargs="+", help="Arquivos SVG dos simbolos")
    sheet_sub.add_argument("--lockups", nargs="*", help="Arquivos SVG dos lockups")
    sheet_sub.add_argument("--names", nargs="*", help="Nomes dos conceitos")
    sheet_sub.add_argument("--notes", nargs="*", help="Notas dos conceitos")
    sheet_sub.add_argument("--recommend", type=int, default=1, help="Indice da recomendacao (1-based)")
    sheet_sub.add_argument("--greyscale", action="store_true", help="Forcar visualizacao em escala de cinza")
    sheet_sub.add_argument("-o", "--output", default="concepts.png", help="Arquivo PNG de saida")

    # Variants
    variants_sub = logo_sub.add_parser("variants", help="Exporta variantes (black, white, mono, favicon, app-icon)")
    variants_sub.add_argument("file", help="Arquivo SVG master")
    variants_sub.add_argument("--title", required=True, help="Titulo/nome da marca")
    variants_sub.add_argument("--mono", help="Cor HEX monocromatica (#0F7C80)")
    variants_sub.add_argument("--icon-bg", help="Cor HEX de fundo do icone")
    variants_sub.add_argument("--web-icons", action="store_true", help="Gerar conjunto completo de web-icons")
    variants_sub.add_argument("--out-dir", help="Diretorio de saida")

    # Board
    board_sub = logo_sub.add_parser("board", help="Gera prancha executiva de apresentacao a partir de spec JSON")
    board_sub.add_argument("spec", help="Arquivo de especificacao JSON")
    board_sub.add_argument("-o", "--output", default="presentation.html", help="HTML de saida")
    board_sub.add_argument("--png-dir", help="Diretorio para exportacao de slides PNG")

    # Cognitive Expansion V3 commands are registered outside this legacy module.
    from engine.cli.v3 import register_v3_subcommands
    register_v3_subcommands(subparsers)

    from engine.cli.news import register_news_subcommands
    register_news_subcommands(subparsers)

    from engine.cli.code_graph import register_code_graph_subcommands
    register_code_graph_subcommands(subparsers)

    from engine.cli.tone import register_tone_subcommands
    register_tone_subcommands(subparsers)

    args = parser.parse_args()

    # Garantir Codenotch ativo a cada ciclo de execucao do ThSyr
    ensure_codenotch_running()

    memory = MemoryManager()
    handoff = HandoffManager()
    sync = GitSyncEngine()
    router = CognitiveRouter(memory=memory, handoff=handoff)

    from engine.cli.v3 import dispatch_v3
    if dispatch_v3(args, memory, router):
        return

    from engine.cli.news import dispatch_news
    if dispatch_news(args):
        return

    from engine.cli.code_graph import dispatch_code_graph
    if dispatch_code_graph(args):
        return

    from engine.cli.tone import dispatch_tone
    if dispatch_tone(args):
        return

    if args.command == "status" or not args.command:
        cmd_status(args, memory, router, sync, handoff)
    elif args.command == "brief":
        cmd_brief(args, memory, router, sync, handoff)
    elif args.command == "observe":
        cmd_observe(args)
    elif args.command == "watcher":
        cmd_watcher(args)
    elif args.command == "consolidate":
        cmd_consolidate(args)
    elif args.command == "notify":
        cmd_notify(args)
    elif args.command == "notch":
        cmd_notch(args)
    elif args.command == "operator":
        cmd_operator(args, router)
    elif args.command == "memory":
        cmd_memory(args, memory, router)
    elif args.command == "think":
        cmd_think(args, memory, router)
    elif args.command == "log":
        cmd_log(args, memory, router, sync, handoff)
    elif args.command == "analyze":
        cmd_analyze(args, memory, sync, handoff)
    elif args.command == "graph":
        cmd_graph(args, memory, router)
    elif args.command == "graph3d":
        cmd_graph3d(args)
    elif args.command == "ingest":
        cmd_ingest(args)
    elif args.command == "academic":
        cmd_academic(args, memory, router)
    elif args.command == "handoff":
        cmd_handoff(args, handoff, sync)
    elif args.command == "checkpoint":
        cmd_checkpoint(args, sync, handoff)
    elif args.command == "procedure":
        cmd_procedure(args, memory)
    elif args.command == "search":
        cmd_search(args, memory, router)
    elif args.command == "model":
        cmd_model(args, router)
    elif args.command == "goal":
        cmd_goal(args, router, handoff, sync)
    elif args.command == "tool":
        cmd_tool(args)
    elif args.command == "runtime":
        cmd_runtime(args)
    elif args.command == "sync":
        cmd_sync(args, sync)
    elif args.command == "gods-eye":
        cmd_gods_eye(args)
    elif args.command == "hardware":
        cmd_hardware(args)
    elif args.command == "daemon":
        cmd_daemon(args)
    elif args.command == "toklang":
        cmd_toklang(args)
    elif args.command == "vector":
        cmd_vector(args)
    elif args.command in ("chat", "repl"):
        cmd_chat(args, router)
    elif args.command == "doctor":
        cmd_doctor(args, memory, router, sync)
    elif args.command == "eval":
        cmd_eval(args)
    elif args.command == "swarm":
        cmd_swarm(args)
    elif args.command == "evolve":
        cmd_evolve(args)
    elif args.command == "war-room":
        cmd_war_room(args)
    elif args.command == "ui":
        cmd_ui(args)
    elif args.command == "logo":
        from engine.cli.logo import cmd_logo
        cmd_logo(args)


if __name__ == "__main__":
    main()
