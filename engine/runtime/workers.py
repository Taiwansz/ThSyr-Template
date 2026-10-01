"""
ThSyr Runtime Workers (Fase 7)
Workers autonomos em background para manutencao de memoria e sincronizacao:
- MemoryWorker: Auditoria e consolidacao periodica da memoria
- SyncWorker: Monitoramento e checkpoints autonomos do Git
"""

from datetime import datetime, timezone
from typing import Any

from ..config import is_test_environment, setup_logger
from ..memory_manager import MemoryManager
from ..session_state import HandoffManager
from ..sync_engine import GitSyncEngine

logger = setup_logger("runtime_workers")


class MemoryWorker:
    def __init__(
        self,
        memory_manager: MemoryManager | None = None,
        handoff_manager: HandoffManager | None = None,
        consolidator: Any | None = None
    ):
        self.memory = memory_manager or MemoryManager()
        self.handoff = handoff_manager or HandoffManager()
        from ..memory_consolidator import MemoryConsolidator
        self.consolidator = consolidator or MemoryConsolidator()

    def run_cycle(self) -> dict[str, Any]:
        """
        Executa auditoria ontologica profunda e consolidacao de memoria.
        """
        active = self.handoff.load_handoff()
        audit = self.consolidator.audit_ontology()

        status = {
            "status": "healthy" if audit["status"] != "DEGRADADO" else "degraded",
            "active_session": active.session_id if active else None,
            "total_episodes": audit["episodic_count"],
            "total_semantics": audit["total_nodes"],
            "ohi_score": audit["ohi_score"],
            "orphaned_count": audit["orphaned_entities_count"],
            "top_orphans": [o["name"] for o in audit.get("top_orphans", [])[:3]],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        logger.debug(f"[MemoryWorker] Ciclo ontologico executado: OHI={audit['ohi_score']*100:.1f}%, Orfaos={audit['orphaned_entities_count']}.")
        return status


class OperatorReflectionWorker:
    def __init__(self, reflection_engine: Any | None = None):
        if reflection_engine is None:
            from ..operator_reflection import OperatorReflectionEngine
            reflection_engine = OperatorReflectionEngine()
        self.reflection = reflection_engine

    def run_cycle(self, force: bool = False) -> dict[str, Any]:
        """Executa uma reflexao profunda somente quando ha evidencia nova suficiente."""
        return self.reflection.run(force=force)


class SyncWorker:
    def __init__(self, sync_engine: GitSyncEngine | None = None):
        self.sync = sync_engine or GitSyncEngine()

    def run_cycle(self, auto_checkpoint_if_dirty: bool = True) -> dict[str, Any]:
        """
        Inspeciona o status do repositorio. Se houver mudancas no brain/state,
        cria um checkpoint autonomo e sincroniza com o remoto.
        """
        git_status = self.sync.get_status()
        changed = git_status.get("changed_files_count", 0)

        result = {
            "branch": git_status.get("branch"),
            "commit": git_status.get("commit"),
            "changed_files_count": changed,
            "action_taken": "none"
        }

        if changed > 0 and auto_checkpoint_if_dirty:
            logger.info(f"[SyncWorker] Detectadas {changed} alteracoes pendentes. Criando checkpoint autonomo...")
            res = self.sync.checkpoint("state(auto-sync)", f"ciclo de sincronizacao continua ({changed} arquivos)")
            result["action_taken"] = "checkpoint_created"
            result["checkpoint_res"] = res

        return result


class SwarmWorker:
    def __init__(self, swarm: Any | None = None):
        from ..swarm import UltronSwarm
        self.swarm = swarm or UltronSwarm()

    def run_cycle(self) -> dict[str, Any]:
        """
        Executa um ciclo de convergencia do Enxame Ultron,
        gerando telemetria unificada e detectando anomalias criticas.
        """
        report = self.swarm.converge()
        return report.to_dict()


class NewsWorker:
    def __init__(self, news_engine: Any | None = None):
        from ..news import NewsEngine
        self.engine = news_engine or NewsEngine()

    def run_cycle(self) -> dict[str, Any]:
        """
        Inspeciona a publicacao diaria da Gazeta Tecnologica Global.
        Se a edicao do dia corrente ainda nao foi publicada, executa a publicacao autonoma.
        """
        today = datetime.now().date()
        status = self.engine.status()
        latest = status.get("latest_edition")

        result: dict[str, Any] = {
            "today": today.isoformat(),
            "latest_edition": latest["date"] if latest else None,
            "action_taken": "none",
            "status": "fresh" if (latest and latest.get("date") == today.isoformat()) else "pending",
        }

        if not latest or latest.get("date") != today.isoformat():
            logger.info(f"[NewsWorker] Edicao de {today} nao encontrada. Publicando autonomamente...")
            pub_res = self.engine.publish(target_date=today, offline=is_test_environment())
            result["action_taken"] = "edition_published"
            result["publication"] = pub_res
            result["status"] = "published"
        else:
            logger.debug(f"[NewsWorker] Edicao de {today} ja publicada e atualizada.")

        return result


