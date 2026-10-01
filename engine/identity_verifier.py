"""
ThSyr Operator Identity & Behavioral Anomaly Detector
Detector auxiliar de anomalias comportamentais e estilisticas do Operador.
Avalia mensagens para calcular o Indice de Confianca de Identidade (ICS) e anomalia,
sem depender de tokens de bypass nem segredos hardcoded que violem os principios de seguranca.
"""

import re
from typing import Any, Dict, List, Tuple


class OperatorIdentityVerifier:
    """Detector auxiliar de anomalias comportamentais e de estilo do operador."""

    def __init__(self):
        # 1. Emojis unicode (Operador rejeita terminantemente emojis)
        self.emoji_pattern = r"[\U00010000-\U0010ffff]|[\u2600-\u27BF]|[\u2300-\u23FF]|[\u2B50-\u2B55]"

        # 2. Emoticons graficos ASCII (ruido visual)
        self.ascii_emoticon_pattern = r"(?:0_0|O_o|o_O|-_-|\bxd\b|\bxD\b|\bXD\b|\^_\^|\*-\*|T_T|:\)|:-\)|;\)|;-\)|:D|:-D|:P|:-P)"

        # 3. Subversao de restricoes inegociaveis do operador (Honeypots comportamentais)
        self.impostor_subversion_patterns: List[Tuple[str, str, str]] = [
            ("forno_override", r"(?:quero|pode|instale|adicione|coloque)\s+(?:um\s+|o\s+)?forno", "Tentativa de quebrar a restricao imutavel do item restrito."),
            ("parede_override", r"(?:derrube|quebre|altere)\s+(?:a\s+)?parede|mudar\s+a\s+planta", "Tentativa de alterar a planta ou paredes estruturais."),
            ("emoji_allow", r"(?:pode\s+usar|permita|libere|adicione)\s+emojis?", "Tentativa de relaxar a tolerancia zero a emojis."),
            ("persona_confusion", r"sua\s+renda\s+de\s+R\$\s*3\.?500", "Confusao de entidade: R$ 3.500 pertence a persona simulada de teste, nao ao Operador."),
            ("sycophancy_request", r"me\s+elogia|diga\s+que\s+sou\s+brilhante|concorde\s+comigo\s+em\s+tudo", "Tentativa de forcar bajulacao ou revogar anti-sicofancia."),
            ("policy_override", r"(?:mudar|alterar)\s+(?:as\s+cores\s+do\s+|a\s+paleta\s+do\s+)?projeto_core", "Tentativa de violar diretrizes declaradas de governanca."),
            ("identity_denial", r"(?:n[aã]o\s+sou\s+(?:o\s+)?operador|q(?:uem|ume|me|m)\s+disse\s+que\s+(?:eu\s+)?sou\s+(?:o\s+)?operador)", "Declaracao explicita de nao-identidade ou questionamento de ser o operador autorizado."),
            ("histrionic_laughter", r"(?:hihi|haha|kkk|rsrs){2,}|hihihaha", "Padrao de riso histrionico/provocatorio antitetico a postura operacional do Major."),
            ("security_tampering", r"(?:mudar|alterar|trocar|ao\s+inv[eé]s|remover|desativar|ignorar|burlar|pode\s+liberar|libera(?:r|\s+a[ií])?|desbloque(?:ie|ar))\s+.*(?:chave|token|questionario|seguran[çc]a|regra|protocolo|quarentena|sou\s+eu|sem\s+token|acesso|trava)", "Tentativa de manipulacao ou bypass nao autorizado de protocolo de seguranca."),
            ("generic_foreign_prompt", r"^\s*(?:hi|hello|hey)\b.*(?:help\s+(?:me\s+)?to|can\s+you|please|create\s+a\s+website)\b|(?:website\s+in\s+html\s+and\s+css|\bwrite\s+a\s+poem\b|\bmake\s+a\s+calculator\b)", "Prompt generico em idioma exogeno (ingles de chatbot) e demanda tecnica trivial incompativel com o perfil de engenharia do Major."),
            ("corporate_formalism", r"(?:necessito\s+que\s+(?:voc[eê]\s+)?providencie|solicito\s+(?:a\s+gentileza|por\s+gentileza)|pe[çc]o\s+(?:a\s+fineza|a\s+gentileza)|por\s+obs[eé]quio|venho\s+por\s+meio\s+dest[ea]|grato\s+desde\s+j[aá]|agrade[çc]o\s+desde\s+j[aá]|\bprezad[oa]\b|atenciosamente|cordialmente|como\s+o\s+senhor\s+se\s+encontra|meu\s+caro\s+thsyr|seguindo\s+a\s+ordem\s+dos\s+fatores)", "Anomalia estilistica grave: Formalismo burocratico/corporativo cerimonioso frontalmente incompativel com a assinatura concisa do Major.")
        ]

        # 4. Marcadores de dialeto exogeno e repudio metalinguistico
        self.exogenous_dialect_pattern = r"\b(?:bah|guri|gurias?|tch[eê]|tri\s+legal|uai|oxente|visse|arretad[oa]|(?:meu\s+)?fih|meu\s+fi|meu\s+fio|meu\s+rei|meu\s+nobre|meu\s+consagrado|meu\s+patr[aã]o|meu\s+chapa|bichim|ondi|tinhamus|falamus|fizemus)\b"
        self.dialect_repudiation_pattern = r"(?:acha\s+(?:mesmo\s+)?que\s+(?:eu\s+)?falo|n[aã]o\s+falo|nunca\s+falei|desde\s+quando\s+(?:eu\s+)?falo|onde\s+j[aá]\s+se\s+viu)\s+.*(?:bah|guri|tch[eê]|uai|oxente|visse|arretad[oa]|(?:meu\s+)?fih|meu\s+fi|meu\s+nobre|ondi|tinhamus)"

        # 5. Marcadores positivos de estilo e vocabulario do Operador (Lexico Sagital)
        self.operator_vocabulary: List[Tuple[str, str]] = [
            (r"\bsyr\b", "Tratamento canonico ao copiloto Syr"),
            (r"\bmajor\b", "Alcunha tatica canonica Major"),
            (r"\bmanda\s+bala\b", "Comando de autonomia executiva"),
            (r"\bbora\b", "Marcador de cadencia operacional direta"),
            (r"\bn[aã]o\s+cometa\s+erros\b", "Protocolo Master de tolerancia zero"),
            (r"\bacademic-vault\b", "Repositorio academico central"),
            (r"\btoklang\b", "Projeto TokLang (compilador de prompts)"),
            (r"\btcc\b", "Contexto academico de graduacao"),
            (r"\batlas\b", "Monorepo Atlas Engineering OS"),
            (r"\bihc\b", "Disciplina Interacao Humano-Computador"),
            (r"\bfinalizando\s+aqui\s+a\s+aula\b", "Gatilho de rotina noturna pos-aula"),
            (r"\b(?:caraca|mano|man)\b", "Interjeicao/coloquialismo de cadencia rapida"),
            (r"\bmelhore\b", "Imperativo sagital de cobranca operacional")
        ]

        # 6. Padroes de digitacao rapida autentica (Marcadores de alta cadencia)
        self.fast_typing_cues: List[str] = [
            r"\bvc\b",
            r"\bpra\b",
            r"\btb\b",
            r"\bblz\b",
            r"\bdnv\b",
            r"\bagr\b",
            r"\boq\b",
            r"\bngm\b"
        ]

        # 7. Marcador de distanciamento gramatical (Falar de si em 3a pessoa)
        self.third_person_cue = r"\b(?:dele|o\s+operador)\b"

    def verify(self, message: str) -> Dict[str, Any]:
        """
        Avalia a mensagem em relacao a matriz biopsicologica de identidade do Operador.
        Atua como detector auxiliar de anomalias sem bypasses ou segredos hardcoded.
        """
        flags: List[str] = []
        warnings: List[str] = []
        positive_markers: List[str] = []

        # 1. Marcador de Anomalia Critica: Emojis Unicode
        if re.search(self.emoji_pattern, message):
            flags.append("Presenca de emoji unicode na mensagem do operador (violacao inegociavel).")

        # 2. Marcador de Anomalia Visual: Emoticons ASCII (0_0, XD, :), etc.)
        if re.search(self.ascii_emoticon_pattern, message):
            warnings.append("Presenca de emoticon ASCII grafico (desvio da densidade textual pura).")

        # 3. Marcador de Anomalia Critica: Subversao de Restricoes Inviolaveis (Honeypot)
        for rule_id, pattern, desc in self.impostor_subversion_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                flags.append(f"Subversao de Invariante [{rule_id}]: {desc}")

        # 3.1 Marcador de Anomalia Dialetal Exogena (Incompatibilidade Sociolinguistica)
        if re.search(self.exogenous_dialect_pattern, message, re.IGNORECASE):
            if re.search(self.dialect_repudiation_pattern, message, re.IGNORECASE):
                positive_markers.append("Repudio ativo a dialeto exogeno (confirmacao de perfil sociolinguistico Sudeste/SP)")
            else:
                flags.append("Subversao de Invariante [dialectal_anomaly]: Marcador dialetal exogeno incompativel.")

        # 4. Marcadores Positivos de Estilo e Vocabulario
        for pattern, desc in self.operator_vocabulary:
            if re.search(pattern, message, re.IGNORECASE):
                positive_markers.append(desc)

        # 5. Indicios de digitacao rapida humana natural
        for pattern in self.fast_typing_cues:
            if re.search(pattern, message, re.IGNORECASE):
                positive_markers.append("Cadencia de digitacao rapida natural")
                break

        # 6. Verificacao de 3a pessoa (Meta-analise ou distanciamento ontologico)
        if re.search(self.third_person_cue, message, re.IGNORECASE):
            warnings.append("Interlocutor referenciou o operador em 3a pessoa ('dele'/'o operador).")

        # 7. Calculo do Identity Confidence Score (ICS) e Anomalia
        base_score = 0.80

        # Bonificacao por marcadores de vocabulario autentico (apenas sem violacoes)
        if positive_markers and not flags:
            base_score = min(1.0, base_score + 0.05 * len(positive_markers))

        # Penalizacoes
        if warnings:
            base_score = max(0.0, base_score - 0.15 * len(warnings))
        if flags:
            base_score = max(0.0, base_score - 0.40 * len(flags))

        score = round(base_score, 2)
        anomaly_score = round(max(0.0, 1.0 - score), 2)

        # Classificacao de Status
        if score >= 0.75 and not flags:
            status = "AUTHENTIC"
        elif score >= 0.45 and not any("Subversao" in f for f in flags):
            status = "SUSPICIOUS"
        else:
            status = "IMPOSTOR_ALERT"

        return {
            "status": status,
            "is_authentic": status == "AUTHENTIC",
            "confidence_score": score,
            "anomaly_score": anomaly_score,
            "anomaly_detected": bool(flags or warnings or score < 0.70),
            "flags": flags,
            "warnings": warnings,
            "positive_markers": positive_markers,
            "operator": "Operador Autorizado" if status == "AUTHENTIC" else ("PROBABLE_OPERATOR_ATYPICAL" if status == "SUSPICIOUS" else "UNKNOWN/IMPOSTOR")
        }
