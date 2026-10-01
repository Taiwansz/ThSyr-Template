"""
ThSyr Proactive Engine (Fase 8)
Decide quando interromper o operador com base em calculo ponderado de custo-beneficio:
proactivity_score = importance + urgency + actionability + confidence - interruption_cost
"""

from typing import Any

from ..config import setup_logger
from .models import ProactivityEvaluation, RuntimeNotification

logger = setup_logger("proactive_engine")


class ProactiveEngine:
    def __init__(self, threshold: float = 1.2):
        self.threshold = threshold
        self.notifications_history: list[RuntimeNotification] = []

    def evaluate(
        self,
        observation: str,
        importance: float,
        urgency: float,
        actionability: float,
        confidence: float,
        interruption_cost: float
    ) -> ProactivityEvaluation:
        """
        Avalia se a observacao justifica interrupcao imediata do operador.
        """
        eval_res = ProactivityEvaluation(
            observation=observation,
            importance=min(1.0, max(0.0, importance)),
            urgency=min(1.0, max(0.0, urgency)),
            actionability=min(1.0, max(0.0, actionability)),
            confidence=min(1.0, max(0.0, confidence)),
            interruption_cost=min(1.0, max(0.0, interruption_cost))
        )
        eval_res.calculate(threshold=self.threshold)
        logger.debug(
            f"[ProactiveEngine] '{observation[:40]}...' Score: {eval_res.score} -> "
            f"{'INTERROMPER' if eval_res.should_interrupt else 'SILENCIOSO'}"
        )
        if eval_res.should_interrupt:
            try:
                from ..desktop_notifier import notify_desktop
                notify_desktop("ThSyr // Alerta Proativo", observation, priority="high")
            except Exception as e:
                logger.debug(f"Falha ao disparar notificacao desktop: {e}")
        return eval_res

    def check_academic_deadlines(self, events: list[dict[str, Any]]) -> list[ProactivityEvaluation]:
        """
        Examina datas e prazos do radar academico gerando avaliacoes proativas.
        """
        evaluations = []
        for ev in events:
            days_left = ev.get("dias_restantes", ev.get("days_left", 999))
            title = ev.get("tipo", ev.get("title", "Evento Academico"))
            disciplina = ev.get("disciplina", "")
            full_title = f"{title} ({disciplina})" if disciplina else title

            if days_left <= 2:
                # Altissima urgencia
                evaluation = self.evaluate(
                    observation=f"Prazo iminente ({days_left} dias): {full_title}",
                    importance=0.95,
                    urgency=0.95,
                    actionability=0.8,
                    confidence=1.0,
                    interruption_cost=0.2
                )
                evaluations.append(evaluation)
            elif days_left <= 7:
                # Media urgencia
                evaluation = self.evaluate(
                    observation=f"Prazo se aproximando ({days_left} dias): {full_title}",
                    importance=0.8,
                    urgency=0.6,
                    actionability=0.7,
                    confidence=0.9,
                    interruption_cost=0.3
                )
                evaluations.append(evaluation)

        return evaluations
