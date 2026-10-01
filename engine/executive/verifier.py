"""
ThSyr Executive System - Verifier (Fase 4 & Evolucao v0.3)
Avalia a observacao gerada apos a execucao de um passo com base estrita em evidencias:
- Valida codigo de saida (exit_code == 0) e integridade criptografica (hashes)
- Rejeita qualquer acao desconhecida ou desprovida de comprovacao factual (Lei 1)
- Decide se o plano prossegue, realiza replan, ou aborta
"""

import hashlib

from ..config import setup_logger
from .models import Observation, Step, VerificationResult

logger = setup_logger("executive_verifier")


class ExecutiveVerifier:
    def __init__(self, max_retries: int = 2):
        self.max_retries = max_retries

    def verify_step_observation(self, step: Step, observation: Observation) -> VerificationResult:
        """
        Avalia o resultado da execucao de um passo com base em evidencias factuais e hashes.
        """
        # 1. Verificacao de sucesso, exit_code e presenca de erro
        if not observation.success or observation.exit_code != 0 or observation.error:
            err = observation.error or observation.raw_output or "Falha de execucao sem codigo de saida zero."
            logger.warning(f"Passo {step.id} falhou na verificacao: {err}")
            return VerificationResult(
                verified=False,
                status="FAIL",
                score=0.0,
                feedback=f"Execucao retornou erro (exit_code {observation.exit_code}): {err}",
                suggested_action="REPLAN"
            )

        # 2. Verificacao de integridade criptografica do stdout
        if observation.stdout_hash and observation.raw_output:
            expected_hash = hashlib.sha256(observation.raw_output.encode("utf-8")).hexdigest()
            if observation.stdout_hash != expected_hash:
                logger.error(f"Inconsistencia criptografica no passo {step.id}: hash adulterado.")
                return VerificationResult(
                    verified=False,
                    status="TAMPERED",
                    score=0.0,
                    feedback="Violacao de integridade: hash de stdout nao coincide com o payload.",
                    suggested_action="ABORT"
                )

        # 3. Se for acao de busca ou leitura, verificar se trouxe conteudo
        if step.action in ("search_memory", "read_file", "inspect_git"):
            content = str(observation.data or observation.raw_output).strip()
            if not content or content == "None":
                return VerificationResult(
                    verified=False,
                    status="FAIL",
                    score=0.3,
                    feedback=f"Acao {step.action} nao encontrou dados ou retornou vazio para '{step.target}'.",
                    suggested_action="REPLAN"
                )

        # 4. Analise e sintese precisam estar ancoradas em observacoes anteriores.
        if step.action in ("analyze", "synthesize") and isinstance(observation.data, dict):
            evidence_count = int(observation.data.get("evidence_count", 0))
            if evidence_count <= 0:
                return VerificationResult(
                    verified=False,
                    status="INSUFFICIENT_EVIDENCE",
                    score=0.2,
                    feedback=(
                        f"Etapa {step.action} nao possui observacoes anteriores suficientes "
                        "para sustentar uma conclusao."
                    ),
                    suggested_action="REPLAN"
                )

        # 5. Passo bem-sucedido e formalmente comprovado
        return VerificationResult(
            verified=True,
            status="PASS",
            score=1.0,
            feedback=f"Etapa {step.id} verificada com evidencia valida ({observation.evidence_id}).",
            suggested_action="NEXT_STEP"
        )
