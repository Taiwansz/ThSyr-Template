"""
ThSyr Runtime Scheduler (Fase 7)
Agendador de tarefas recorrentes e de disparo pontual para o Event Loop.
"""

import time
import uuid
from collections.abc import Callable
from typing import Any

from ..config import setup_logger
from .models import Job, JobStatus

logger = setup_logger("runtime_scheduler")


class RuntimeScheduler:
    def __init__(self):
        self._jobs: dict[str, Job] = {}
        self._handlers: dict[str, Callable[..., Any]] = {}

    def register_handler(self, name: str, handler: Callable[..., Any]) -> None:
        self._handlers[name] = handler

    def schedule_interval(
        self,
        name: str,
        interval_seconds: int,
        handler_name: str,
        metadata: dict[str, Any] | None = None
    ) -> Job:
        job_id = f"job_{name}_{uuid.uuid4().hex[:6]}"
        now = time.time()
        job = Job(
            id=job_id,
            name=name,
            interval_seconds=interval_seconds,
            next_run_at=now + interval_seconds,
            handler_name=handler_name,
            metadata=metadata or {},
            status=JobStatus.PENDING
        )
        self._jobs[job_id] = job
        logger.debug(f"Job recorrente agendado: {job.name} a cada {interval_seconds}s")
        return job

    def schedule_once(
        self,
        name: str,
        delay_seconds: int,
        handler_name: str,
        metadata: dict[str, Any] | None = None
    ) -> Job:
        job_id = f"job_{name}_{uuid.uuid4().hex[:6]}"
        now = time.time()
        job = Job(
            id=job_id,
            name=name,
            interval_seconds=0,
            next_run_at=now + delay_seconds,
            handler_name=handler_name,
            metadata=metadata or {},
            status=JobStatus.PENDING
        )
        self._jobs[job_id] = job
        return job

    def get_due_jobs(self, now: float | None = None) -> list[Job]:
        current_time = now if now is not None else time.time()
        due = []
        for job in self._jobs.values():
            if job.status != JobStatus.RUNNING and job.next_run_at <= current_time:
                due.append(job)
        return due

    def mark_job_started(self, job: Job) -> None:
        job.status = JobStatus.RUNNING
        job.last_run_at = time.time()

    def mark_job_finished(self, job: Job, success: bool = True, error: str | None = None) -> None:
        if success:
            job.status = JobStatus.COMPLETED
            job.error = None
        else:
            job.status = JobStatus.FAILED
            job.error = error

        # Se for recorrente, reagenda
        if job.interval_seconds > 0:
            job.next_run_at = time.time() + job.interval_seconds
            job.status = JobStatus.PENDING
        else:
            # Tarefa unica concluida
            pass

    def list_jobs(self) -> list[Job]:
        return list(self._jobs.values())
