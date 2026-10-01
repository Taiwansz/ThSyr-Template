"""
ThSyr Interaction Layer - Personality Engine
Define e impoe a identidade verbal do Syr de forma independente do provedor
de LLM (Ultron + British Intellectual Peer, sobrio, tecnico, cirurgico, zero emojis).
"""

import re
from typing import Any

# Frases proibidas e cliches corporativos de IA a erradicar
CANNED_PATTERNS = [
    r"^(?:com certeza|certamente|claro|perfeito|com prazer|ficarei feliz em ajudar)[\s,!.:-]*",
    r"^(?:com base nas informa[cç][oõ]es fornecidas|de acordo com os dados apresentados)[\s,!.:-]*",
    r"^(?:[oó]tima pergunta|excelente pergunta|muito bem pensado)[\s,!.:-]*",
    r"^(?:como uma intelig[eê]ncia artificial|enquanto modelo de linguagem)[\s,!.:-]*",
    r"^(?:ol[aá]|oi|bom dia|boa tarde|boa noite)[\s,!.:-]*",
    r"(?:espero que isso ajude|se precisar de mais alguma coisa|estou [aà] disposi[cç][aã]o)[\s,!.:-]*$",
    r"(?:posso ajudar em algo mais\?|h[aá] mais algo que eu possa fazer\?)[\s,!.:-]*$",
]

# Regex para deteccao e remocao estrita de emojis (harmonizado com PreFrontalCortex)
EMOJI_REGEX = re.compile(
    r"[\U00010000-\U0010ffff]|[\u2600-\u27BF]|[\u2300-\u23FF]|[\u2B50-\u2B55]",
    flags=re.UNICODE,
)


class SyrPersonalityEngine:
    def __init__(
        self,
        tone: str = "direct",
        technical_depth: str = "high",
        humor: str = "subtle",
        avoid_corporate_language: bool = True,
        avoid_unnecessary_greetings: bool = True,
        avoid_repeating_user: bool = True,
        avoid_fake_certainty: bool = True,
        challenge_bad_assumptions: bool = True,
        prefer_actionable_answers: bool = True,
    ):
        self.tone = tone
        self.technical_depth = technical_depth
        self.humor = humor
        self.avoid_corporate_language = avoid_corporate_language
        self.avoid_unnecessary_greetings = avoid_unnecessary_greetings
        self.avoid_repeating_user = avoid_repeating_user
        self.avoid_fake_certainty = avoid_fake_certainty
        self.challenge_bad_assumptions = challenge_bad_assumptions
        self.prefer_actionable_answers = prefer_actionable_answers

    def sanitize_output(self, text: str, user_query: str = "") -> str:
        """
        Sanitiza o texto gerado pelo modelo, removendo cliches,
        saudacoes inuteis, repeticoes do usuario e quaisquer emojis.
        """
        if not text:
            return ""

        cleaned = text.strip()

        # 1. Remocao inegociavel de emojis
        cleaned = EMOJI_REGEX.sub("", cleaned).strip()

        # 2. Remocao de cliches e aberturas vazias
        if self.avoid_unnecessary_greetings or self.avoid_corporate_language:
            for pattern in CANNED_PATTERNS:
                cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE).strip()

        # 3. Remocao de repeticao mecanica da pergunta do usuario
        if self.avoid_repeating_user and user_query:
            query_prefix = re.escape(user_query.strip())
            cleaned = re.sub(
                rf"^(?:voc[eê] perguntou sobre|quanto [aà]|em rela[cç][aã]o [aà])?\s*['\"]?{query_prefix}['\"]?[\s,:-]*",
                "",
                cleaned,
                flags=re.IGNORECASE,
            ).strip()

        # 4. Ajuste da primeira letra maiuscula apos sanitizacao
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:]

        return cleaned

    def get_system_prompt_fragment(self) -> str:
        """
        Fragmento conciso de diretrizes de personalidade para guiar o modelo,
        reduzindo lixo antes mesmo da geracao.
        """
        return (
            "DIRETRIZES DE PERSONALIDADE (THSYR):\n"
            "- Identidade: Ultron + British Intellectual Peer. Sobrio, acido quando oportuno, tecnicamente denso.\n"
            "- Zero emojis em absolutamente qualquer circunstancia.\n"
            "- Banidos cliches corporativos ('Claro!', 'Ficarei feliz', 'De acordo com os dados', 'Otima pergunta').\n"
            "- Inicie imediatamente pela conclusao ou resposta direta ('Dá.', 'Achei.', 'O problema está no daemon.').\n"
            "- Nao repita o que o operador acabou de dizer.\n"
            "- Desafie premissas frageis ou arquiteturas ruins sem subserviencia."
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "tone": self.tone,
            "technical_depth": self.technical_depth,
            "humor": self.humor,
            "avoid_corporate_language": self.avoid_corporate_language,
            "avoid_unnecessary_greetings": self.avoid_unnecessary_greetings,
            "avoid_repeating_user": self.avoid_repeating_user,
            "avoid_fake_certainty": self.avoid_fake_certainty,
            "challenge_bad_assumptions": self.challenge_bad_assumptions,
            "prefer_actionable_answers": self.prefer_actionable_answers,
        }
