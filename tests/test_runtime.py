"""
ThSyr Test Suite - Continuous Runtime & Proactive Engine (Fase 7 e Fase 8)
Valida:
- Agendamento de tarefas periodicas e pontuais (RuntimeScheduler)
- Ciclos dos workers autonomos (MemoryWorker, SyncWorker)
- Calculo da pontuacao proativa e decisoes de interrupcao (ProactiveEngine)
- Orquestracao do SyrRuntime (step_tick, run_once, run_loop)
"""

import unittest

from engine.runtime.models import JobStatus
from engine.runtime.proactive import ProactiveEngine
from engine.runtime.runtime import SyrRuntime
from engine.runtime.scheduler import RuntimeScheduler
from engine.runtime.workers import MemoryWorker, SyncWorker


class TestContinuousRuntime(unittest.TestCase):
    def test_scheduler_jobs_execution(self):
        scheduler = RuntimeScheduler()
        counter = {"runs": 0}

        def sample_handler():
            counter["runs"] += 1
            return "ok"

        scheduler.register_handler("increment", sample_handler)

        # Agenda para rodar imediatamente (delay 0)
        job = scheduler.schedule_once("test_job", 0, "increment")
        self.assertEqual(job.status, JobStatus.PENDING)

        # Deve estar pronto para execucao
        due = scheduler.get_due_jobs()
        self.assertEqual(len(due), 1)
        self.assertEqual(due[0].id, job.id)

        # Executar
        scheduler.mark_job_started(due[0])
        self.assertEqual(due[0].status, JobStatus.RUNNING)
        handler = scheduler._handlers[due[0].handler_name]
        res = handler()
        self.assertEqual(res, "ok")
        scheduler.mark_job_finished(due[0], success=True)

        self.assertEqual(counter["runs"], 1)
        self.assertEqual(due[0].status, JobStatus.COMPLETED)

    def test_proactive_engine_scoring(self):
        engine = ProactiveEngine(threshold=1.2)

        # Caso 1: Alta urgencia e alta importancia -> deve interromper
        # score = 0.9 + 0.95 + 0.8 + 1.0 - 0.3 = 3.35 >= 1.2
        eval_urgent = engine.evaluate(
            observation="Prova de Compiladores amanha",
            importance=0.9,
            urgency=0.95,
            actionability=0.8,
            confidence=1.0,
            interruption_cost=0.3
        )
        self.assertTrue(eval_urgent.should_interrupt)
        self.assertGreater(eval_urgent.score, 1.2)

        # Caso 2: Baixa urgencia e alto custo de interrupcao -> silencioso
        # score = 0.3 + 0.1 + 0.2 + 0.5 - 0.9 = 0.2 < 1.2
        eval_quiet = engine.evaluate(
            observation="Artigo salvo para leitura futura",
            importance=0.3,
            urgency=0.1,
            actionability=0.2,
            confidence=0.5,
            interruption_cost=0.9
        )
        self.assertFalse(eval_quiet.should_interrupt)
        self.assertLess(eval_quiet.score, 1.2)

    def test_workers_execution(self):
        mem_worker = MemoryWorker()
        mem_status = mem_worker.run_cycle()
        self.assertEqual(mem_status["status"], "healthy")
        self.assertGreater(mem_status["total_episodes"], 0)

        sync_worker = SyncWorker()
        sync_status = sync_worker.run_cycle(auto_checkpoint_if_dirty=False)
        self.assertIn("branch", sync_status)

    def test_syr_runtime_orchestration(self):
        runtime = SyrRuntime()

        # Execucao pontual de um ciclo completo
        summary = runtime.run_once()
        self.assertIn("memory", summary)
        self.assertIn("sync", summary)
        self.assertIn("operator_reflection", summary)
        self.assertIn("proactive_evaluations_count", summary)

        # Execucao controlada de 2 ticks
        job_names = {job.name for job in runtime.scheduler.list_jobs()}
        self.assertIn("operator_reflection_worker", job_names)

        runtime.run_loop(max_ticks=2, tick_interval=0.01)
        self.assertFalse(runtime.is_running)


if __name__ == "__main__":
    unittest.main()
