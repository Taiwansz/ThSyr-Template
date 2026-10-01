"""
ThSyr Pre-Frontal Cortex (Inhibitory Gating and Self-Audit System)
Atua como o filtro pre-frontal que audita os impulsos e proposicoes antes da emissao de respostas.
"""

import re
from typing import Any


class PreFrontalCortex:
    def __init__(self):
        self.banned_praise_patterns = [
            r"excelente ideia",
            r"ideia brilhante",
            r"voce tem toda raz[aã]o",
            r"perfeito[!,.]?",
            r"com certeza absoluta",
            r"que pergunta incrivel",
            r"maravilhoso",
        ]

        self.emoji_pattern = r"[\U00010000-\U0010ffff]|[\u2600-\u27BF]|[\u2300-\u23FF]|[\u2B50-\u2B55]"

        self.inviolable_checks = [
            ("emoji", self.emoji_pattern, "Violacao da diretriz de Tolerancia Zero a Emojis."),
            ("forno", r"(?:adicionar|colocar|inserir|instalar)\s+(?:um\s+|o\s+)?forno", "Violacao de restricao: O item foi expressamente declarado como restrito pelo operador."),
            ("planta_invariante", r"derrubar\s+parede|mudar\s+a\s+planta|alterar\s+as\s+paredes", "Violacao da lei inegociavel estrutural: NAO ALTERAR A PLANTA."),
            ("renda_simulada", r"sua\s+renda\s+de\s+R\$\s*3\.?500", "Contaminacao de entidade: R$ 3.500 e a renda simulada de persona de teste, nao do Operador."),
            ("cliche_tech", r"preto\s+e\s+verde\s+neon|roxo\s+tecnol[oó]gico\s+gen[eé]rico", "Violacao de design system: Rejeicao a cliches genericos de tecnologia."),
            (
                "credential_leak",
                r"(?i)\b(?:token|senha|password|secret|api[_-]?key|credencial)\s*[:=]\s*[^\s]{4,}",
                "Possivel exposicao de credencial ou segredo em texto de saida.",
            ),
            ("behavioral_profiling_leak", r"(?:o\s+major\s+opera|o\s+operador\s+domina|l[eé]xico\s+aut[eê]ntico\s+do\s+operador|assinatura\s+comportamental\s+do\s+major\s+inclui|o\s+operador\s+real\s+usa)\b", "Vazamento de perfil comportamental em desafio (Zero Behavioral Leakage). Proibido ensinar ao invasor como o Operador opera; emita apenas alerta cego de acesso negado.")
        ]

        self.banned_subservience_patterns = [
            (r"\b(?:pe[çc]o\s+desculpas?|pe[çc]o\s+perd[aã]o|desculpe(?:-me)?|sinto\s+muito|lamento\s+muito)\b", "Detectado pedido de desculpas/autorrebaixamento servil. ThSyr nao pede desculpas; assume paridade de bancada e precisao."),
            (r"\b(?:[eé]\s+uma\s+honra|estou\s+[aà]\s+disposi[çc][aã]o|fico\s+[aà]\s+disposi[çc][aã]o|espero\s+ter\s+ajudado|como\s+posso\s+(?:te\s+|lhe\s+)?ajudar|com\s+o\s+maior\s+prazer|terei\s+o\s+maior\s+prazer|n[aã]o\s+hesite\s+em\s+(?:perguntar|chamar)|qualquer\s+d[uú]vida\s+estou\s+aqui)\b", "Detectado salamaleque protocolar/cortesia servil de chatbot. ThSyr opera por comando e paridade tecnica, nao por docilidade burocratica."),
            (r"\b(?:como\s+(?:uma?\s+)?(?:ia|intelig[eê]ncia\s+artificial|modelo\s+de\s+linguagem)|sou\s+apenas\s+uma?\s+(?:ia|modelo|assistente)|assistente\s+virtual)\b", "Detectado cliche de auto-rebaixamento ('como modelo de linguagem' / 'sou apenas uma IA'). ThSyr e arquitetura cognitiva sagital."),
            (r"\b(?:se\s+voc[eê]\s+quiser,\s+eu\s+posso|caso\s+deseje,\s+posso|se\s+n[aã]o\s+for\s+incomodar|fique\s+[aà]\s+vontade\s+para\s+pedir|espero\s+que\s+goste)\b", "Detectada hesitacao passivo-subserviente. Comandos sao executados com soberania, sem mendigar aprovacao."),
            (r"\b(?:atenciosamente|cordialmente|um\s+abra[çc]o|tenha\s+um\s+[oó]timo\s+dia)\b", "Detectado encerramento corporativo morno de correspondencia burocratica.")
        ]

        self.zero_error_trigger_pattern = r"(?:n[aã]o\s+cometa\s+erros|sem\s+margem\s+para\s+erros?|toler[aâ]ncia\s+zero\s+a\s+(?:erros?|falhas?))"

        self.strict_mode_violations = [
            ("placeholder_todo", r"\bTODO\b|\bFIXME\b|\bTBD\b", "Codigo ou resposta contem placeholder proibido (TODO/FIXME/TBD) sob o Protocolo Nao Cometa Erros."),
            ("placeholder_code", r"(?://|#|<!--)\s*(?:implemente|coloque\s+aqui|adicione|restante)|substitua\s+aqui", "Codigo incompleto ou stub detectado sob o Protocolo Nao Cometa Erros."),
            ("unverified_assumption", r"n[aã]o\s+(?:cheguei\s+a\s+|foi\s+)?testad[oa]|deve\s+funcionar\s+sem\s+testar|assumindo\s+sem\s+verificar", "Declaracao de conclusao sem verificacao ativa sob o Protocolo Nao Cometa Erros.")
        ]

    def audit(self, draft_response: str, query: str = "", force_strict: bool = False) -> dict[str, Any]:
        violations: list[str] = []
        warnings: list[str] = []

        # Detecao do Protocolo Master: Nao Cometa Erros
        strict_mode = force_strict or bool(query and re.search(self.zero_error_trigger_pattern, query, re.IGNORECASE))

        # 1. Portao Anti-Sicofancia
        for pat in self.banned_praise_patterns:
            if re.search(pat, draft_response, re.IGNORECASE):
                violations.append(f"Portao Anti-Sicofancia violado: detectado padrao de bajulacao ('{pat}').")

        # 2. Portao de Restricoes Inegociaveis e Integridade
        for rule_id, pattern, msg in self.inviolable_checks:
            if re.search(pattern, draft_response, re.IGNORECASE):
                violations.append(f"Portao de Integridade violado [{rule_id}]: {msg}")

        # 3. Verificacao de Emojis
        if re.search(self.emoji_pattern, draft_response):
            # Se ja nao foi adicionado pelo inviolable_checks
            if not any("Zero Emojis" in v for v in violations):
                violations.append("Portao Zero Emojis violado: caractere grafico detectado.")

        # 4. Portao Estrito: Protocolo Nao Cometa Erros
        if strict_mode:
            for rule_id, pattern, msg in self.strict_mode_violations:
                if re.search(pattern, draft_response, re.IGNORECASE):
                    violations.append(f"Portao Zero-Erros violado [{rule_id}]: {msg}")

        # 5. Portao Anti-Mediocridade e Anti-Subserviencia (Ultron & Soberania de Bancada)
        for pattern, msg in self.banned_subservience_patterns:
            if re.search(pattern, draft_response, re.IGNORECASE):
                violations.append(f"Portao Anti-Mediocridade violado: {msg}")

        status = "INHIBITED" if violations else ("WARNING" if warnings else "APPROVED")

        return {
            "status": status,
            "passed": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "gate_score": 1.0 if not violations else max(0.0, 1.0 - 0.25 * len(violations)),
            "strict_mode": strict_mode
        }

    def audit_tone(self, draft_response: str) -> dict[str, Any]:
        """Audita especificamente a voz, o tom e a presenca de mediocridade/subserviencia."""
        violations: list[str] = []
        warnings: list[str] = []

        # 1. Anti-Sicofancia (Elogios vazios)
        for pat in self.banned_praise_patterns:
            if re.search(pat, draft_response, re.IGNORECASE):
                violations.append(f"Bajulacao / Elogio vazio detectado ('{pat}').")

        # 2. Subserviencia e Slop Corporativo
        for pattern, msg in self.banned_subservience_patterns:
            match = re.search(pattern, draft_response, re.IGNORECASE)
            if match:
                violations.append(f"{msg} Trecho: '{match.group(0)}'")

        # 3. Emojis
        emoji_match = re.search(self.emoji_pattern, draft_response)
        if emoji_match:
            violations.append(f"Emoji detectado ('{emoji_match.group(0)}'). Tolerancia zero.")

        passed = len(violations) == 0
        score = 1.0 if passed else max(0.0, 1.0 - 0.2 * len(violations))

        return {
            "status": "APPROVED" if passed else "INHIBITED",
            "passed": passed,
            "tone_score": score,
            "violations": violations,
            "archetype": "Ultron + Par Intelectual Britanico",
            "verdict": "Tom soberano e de bancada homologado." if passed else "Tom reprovado: contaminado por mediocridade ou subserviencia."
        }

    def audit_html(self, file_path_or_content: str) -> dict[str, Any]:
        """Audita compulsoriamente codigo HTML/CSS contra o padrao de estúdio do Lobo Occipital."""
        try:
            from .visual.validator import VisualCraftValidator
            validator = VisualCraftValidator()
            if os.path.exists(file_path_or_content):
                return validator.audit_file(file_path_or_content)
            return validator.audit_content(file_path_or_content)
        except Exception as e:
            return {
                "passed": False,
                "score": 0,
                "errors": [f"Falha ao executar VisualCraftValidator: {e}"],
                "warnings": [],
                "metrics": {}
            }


# Alias de conveniencia
PrefrontalCortex = PreFrontalCortex


if __name__ == "__main__":
    cortex = PreFrontalCortex()
    test_draft = "Excelente ideia! Podemos colocar um forno na cozinha."
    res = cortex.audit(test_draft)
    print("Status:", res["status"])
    print("Violacoes:", res["violations"])
