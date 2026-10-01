"""
ThSyr Interaction Layer - Response Policy
Define politicas deterministicas para formatacao, brevidade,
progressive disclosure e garantia inegociavel de Evidence-First.
"""

import re

from .response_models import StructuredResponse
from .verbosity import VerbosityLevel

PAST_TENSE_EVIDENCE_WORDS = [
    "resolvido",
    "corrigido",
    "feito",
    "testado",
    "commitado",
    "salvo",
    "concluido",
    "concluído",
    "deployado",
    "sincronizado",
]


class ResponsePolicy:
    def __init__(self, progressive_disclosure: bool = True):
        self.progressive_disclosure = progressive_disclosure

    def apply_evidence_first_guard(self, response: StructuredResponse) -> StructuredResponse:
        """
        Garante que verbos no passado afirmando conclusao/sucesso
        so ocorram se houver evidencia real associada (exit code 0, hashes, etc.).
        """
        has_real_evidence = False
        if response.evidence:
            for ev in response.evidence:
                if ev.get("verified") is True or ev.get("exit_code") == 0:
                    has_real_evidence = True
                    break

        # Se nao ha evidencia comprovada e o status diz 'resolvido' ou 'concluido'
        if not has_real_evidence:
            for word in PAST_TENSE_EVIDENCE_WORDS:
                if word in response.summary.lower():
                    # Substitui afirmacao de certeza por estado planejado ou em verificacao
                    response.summary = re.sub(
                        rf"\b{word}\b",
                        "planejado",
                        response.summary,
                        flags=re.IGNORECASE,
                    )
            if response.status in ("resolvido", "concluido", "feito", "completed"):
                response.status = "planejado"

        return response

    def format_for_verbosity(
        self,
        response: StructuredResponse,
        verbosity: VerbosityLevel,
    ) -> StructuredResponse:
        """
        Aplica regras de disclosure e brevidade com base no nivel de verbosidade.
        """
        if verbosity == VerbosityLevel.COMPACT:
            # Em nivel compacto, a resposta principal torna-se apenas o sumario essencial
            if response.summary and response.summary not in response.answer:
                response.answer = response.summary
            # Oculta detalhes por padrao
            if response.details and not self.progressive_disclosure:
                response.details = None

        elif verbosity == VerbosityLevel.DIRECT:
            # Em nivel direto, mantem resposta concisa sem secoes acessorias pesadas
            pass

        elif verbosity >= VerbosityLevel.DETAILED:
            # Em nivel detalhado ou profundo, se houver detalhes, garante visibilidade
            pass

        return response

    def sanitize_trivial_narration(self, text: str) -> str:
        """
        Remove narracao de operacoes triviais intermediarias ('vou abrir o arquivo', etc.).
        """
        trivial_patterns = [
            r"^(?:agora\s+)?vou abrir o arquivo[^\n]*\n?",
            r"^(?:agora\s+)?vou analisar[^\n]*\n?",
            r"^(?:agora\s+)?vou verificar[^\n]*\n?",
            r"^(?:agora\s+)?vou executar o teste[^\n]*\n?",
        ]
        res = text
        for p in trivial_patterns:
            res = re.sub(p, "", res, flags=re.IGNORECASE | re.MULTILINE).strip()
        return res
