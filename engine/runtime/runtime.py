"""
ThSyr Continuous Runtime (Fase 7 e Fase 8)
Orquestrador central do ciclo contínuo de background:
Event Loop, Scheduler, Workers de Sincronizacao/Memoria e Motor Proativo.
"""

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..config import get_state_dir, settings, setup_logger
from ..working_memory import WorkingMemory
from ..workspace_observer import discover_workspaces
from .events import RuntimeEventBus
from .proactive import ProactiveEngine
from .rem import REMConsolidator
from .scheduler import RuntimeScheduler
from .watcher import EventStore, WorkspaceMutationWorker, create_watcher
from .workers import MemoryWorker, NewsWorker, OperatorReflectionWorker, SwarmWorker, SyncWorker

logger = setup_logger("syr_runtime")


class SyrRuntime:
    def __init__(
        self,
        scheduler: RuntimeScheduler | None = None,
        sync_worker: SyncWorker | None = None,
        memory_worker: MemoryWorker | None = None,
        swarm_worker: SwarmWorker | None = None,
        news_worker: NewsWorker | None = None,
        operator_reflection_worker: OperatorReflectionWorker | None = None,
        proactive_engine: ProactiveEngine | None = None,
        mutation_worker: WorkspaceMutationWorker | None = None,
        state_dir: Path | None = None,
        event_bus: RuntimeEventBus | None = None,
        rem_consolidator: REMConsolidator | None = None,
    ):
        self.state_dir = state_dir or get_state_dir()
        self.scheduler = scheduler or RuntimeScheduler()
        self.sync_worker = sync_worker or SyncWorker()
        self.memory_worker = memory_worker or MemoryWorker()
        self.swarm_worker = swarm_worker or SwarmWorker()
        self.news_worker = news_worker or NewsWorker()
        self.operator_reflection_worker = operator_reflection_worker or OperatorReflectionWorker()
        self.proactive_engine = proactive_engine or ProactiveEngine()
        self.event_bus = event_bus or RuntimeEventBus()
        self.rem_consolidator = rem_consolidator or REMConsolidator(self.event_bus)
        from ..desktop_notifier import notify_desktop
        self.mutation_worker = mutation_worker or WorkspaceMutationWorker(
            create_watcher(discover_workspaces(), debounce_seconds=5.0),
            EventStore(self.state_dir),
            WorkingMemory(self.state_dir),
            notifier=lambda title, message: notify_desktop(title, message, priority="high"),
            event_bus=self.event_bus,
        )
        self.is_running = False

        self._init_default_jobs()

    def _init_default_jobs(self) -> None:
        # Registrar handlers
        self.scheduler.register_handler("sync_check", lambda: self.sync_worker.run_cycle(auto_checkpoint_if_dirty=False))
        self.scheduler.register_handler("memory_check", lambda: self.memory_worker.run_cycle())
        self.scheduler.register_handler("swarm_check", lambda: self.swarm_worker.run_cycle())
        self.scheduler.register_handler("workspace_mutation_check", lambda: self.mutation_worker.run_cycle())
        self.scheduler.register_handler("rem_consolidation", lambda: self.rem_consolidator.run_cycle())
        self.scheduler.register_handler("news_check", lambda: self.news_worker.run_cycle())
        self.scheduler.register_handler(
            "operator_reflection_check",
            lambda: self.operator_reflection_worker.run_cycle(force=False),
        )

        # Agendar jobs padrao
        self.scheduler.schedule_interval("sync_worker", 60, "sync_check")
        self.scheduler.schedule_interval("memory_worker", 120, "memory_check")
        self.scheduler.schedule_interval("swarm_worker", 180, "swarm_check")
        self.scheduler.schedule_interval("workspace_mutation_worker", 5, "workspace_mutation_check")
        self.scheduler.schedule_interval("rem_consolidator", 10, "rem_consolidation")
        self.scheduler.schedule_interval("news_worker", 3600, "news_check")
        self.scheduler.schedule_interval(
            "operator_reflection_worker",
            settings.operator_intelligence.reflection_poll_seconds,
            "operator_reflection_check",
        )

    def step_tick(self, now: float | None = None) -> dict[str, Any]:
        """
        Executa um unico ciclo de processamento do Event Loop:
        1. Identifica jobs prontos para execucao
        2. Executa os handlers registrados
        3. Registra telemetria do tick
        """
        current_time = now if now is not None else time.time()
        due_jobs = self.scheduler.get_due_jobs(now=current_time)

        executed = []
        for job in due_jobs:
            self.scheduler.mark_job_started(job)
            handler = self.scheduler._handlers.get(job.handler_name)
            if handler:
                try:
                    res = handler()
                    self.scheduler.mark_job_finished(job, success=True)
                    executed.append({"job": job.name, "success": True, "result": str(res)[:100]})
                except Exception as e:
                    logger.error(f"Erro ao executar job {job.name}: {e}")
                    self.scheduler.mark_job_finished(job, success=False, error=str(e))
                    executed.append({"job": job.name, "success": False, "error": str(e)})
            else:
                logger.warning(f"Handler '{job.handler_name}' nao encontrado para o job {job.name}.")
                self.scheduler.mark_job_finished(job, success=False, error="Handler not found")

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "due_count": len(due_jobs),
            "executed": executed
        }

    def run_once(self) -> dict[str, Any]:
        """
        Dispara um ciclo completo de manutencao imediata:
        memoria, sincronizacao, convergencia de enxame e avaliacao proativa.
        """
        mem_res = self.memory_worker.run_cycle()
        sync_res = self.sync_worker.run_cycle(auto_checkpoint_if_dirty=False)
        swarm_res = self.swarm_worker.run_cycle()
        news_res = self.news_worker.run_cycle()
        reflection_res = self.operator_reflection_worker.run_cycle(force=False)

        # Avaliacao proativa padrao do radar academico
        from ..academic_sync import AcademicMonitor
        monitor = AcademicMonitor()
        events = monitor.get_upcoming_deadlines()
        proactive_evals = self.proactive_engine.check_academic_deadlines(events)

        urgent_alerts = [e for e in proactive_evals if e.should_interrupt]

        return {
            "memory": mem_res,
            "sync": sync_res,
            "swarm": swarm_res,
            "news": news_res,
            "operator_reflection": reflection_res,
            "proactive_evaluations_count": len(proactive_evals),
            "urgent_alerts": [a.to_dict() for a in urgent_alerts]
        }

    def run_loop(self, max_ticks: int | None = None, tick_interval: float = 1.0) -> None:
        """
        Inicia a execucao contínua do Syr Runtime.
        """
        self.is_running = True
        logger.info(f"Syr Runtime iniciado. Tick interval: {tick_interval}s")
        ticks = 0

        try:
            while self.is_running:
                _ = self.step_tick()
                ticks += 1
                if max_ticks and ticks >= max_ticks:
                    break
                time.sleep(tick_interval)
        except KeyboardInterrupt:
            logger.info("Interrupcao de teclado recebida. Encerrando Syr Runtime com seguranca...")
        finally:
            self.is_running = False
            logger.info("Syr Runtime encerrado.")
