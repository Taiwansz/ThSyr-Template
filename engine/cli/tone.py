"""
ThSyr CLI - Módulo Tone & Prefrontal Audit Engine
Auditoria algorítmica compulsória de tom, soberania de bancada e anti-mediocridade.
Zero emojis.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from ..prefrontal_cortex import PreFrontalCortex


def register_tone_subcommands(subparsers: argparse._SubParsersAction[Any]) -> None:
    # audit-tone
    tone_parser = subparsers.add_parser(
        "audit-tone",
        help="Audita texto ou arquivo contra mediocridade, subserviencia e polidez de chatbot."
    )
    tone_parser.add_argument("text", nargs="?", default="", help="Texto a ser auditado")
    tone_parser.add_argument("-f", "--file", help="Caminho do arquivo a ser lido e auditado")
    tone_parser.add_argument("--json", action="store_true", help="Emite saida em formato JSON puro")

    # audit-prefrontal
    pf_parser = subparsers.add_parser(
        "audit-prefrontal",
        help="Executa auditoria compulsoria do Portao Pre-Frontal completo (integridade, restricoes, tom e zero erros)."
    )
    pf_parser.add_argument("text", nargs="?", default="", help="Texto a ser auditado")
    pf_parser.add_argument("-f", "--file", help="Caminho do arquivo a ser lido e auditado")
    pf_parser.add_argument("--query", default="", help="Query do operador para calibracao de contexto")
    pf_parser.add_argument("--strict", action="store_true", help="Ativa modo estrito (Protocolo Nao Cometa Erros)")
    pf_parser.add_argument("--json", action="store_true", help="Emite saida em formato JSON puro")


def _get_target_text(args: Any) -> str:
    if getattr(args, "file", None):
        target = Path(args.file)
        if not target.exists():
            print(f"Erro: Arquivo '{args.file}' nao encontrado.")
            sys.exit(1)
        return target.read_text(encoding="utf-8", errors="replace")
    if getattr(args, "text", None):
        return str(args.text)
    print("Erro: Forneca um texto como argumento ou um arquivo via --file.")
    sys.exit(1)


def dispatch_tone(args: Any) -> bool:
    if args.command == "audit-tone":
        cortex = PreFrontalCortex()
        content = _get_target_text(args)
        result = cortex.audit_tone(content)

        if getattr(args, "json", False):
            print(json.dumps(result, indent=2, ensure_ascii=False))
            sys.exit(0 if result["passed"] else 1)

        print("================================================================================")
        print("                THSYR // AUDITORIA DE TOM & ANTI-MEDIOCRIDADE                   ")
        print("================================================================================")
        print(f"Status do Portão:      {result['status']}")
        print(f"Aprovado:              {'SIM' if result['passed'] else 'NAO'}")
        print(f"Score de Soberania:    {result['tone_score'] * 100:.1f}%")
        print(f"Arquétipo Requerido:   {result['archetype']}")
        print(f"Veredito Executivo:    {result['verdict']}")
        print("--------------------------------------------------------------------------------")

        if result["violations"]:
            print("VIOLACOES DE MEDIOCRIDADE / SUBSERVIENCIA IDENTIFICADAS:")
            for idx, v in enumerate(result["violations"], 1):
                print(f"  [{idx}] {v}")
            print("--------------------------------------------------------------------------------")
            print("DIRETRIZ DE CORRECAO:")
            print("  Destrua o viés corporativo. Assuma paridade técnica de aço, postura Ultron")
            print("  e cadência intelectual britânica. Zero subserviência e zero salamaleques.")
        else:
            print("Conformidade absoluta. Nenhuma contaminação por mediocridade ou subserviência.")

        print("================================================================================")
        sys.exit(0 if result["passed"] else 1)

    if args.command == "audit-prefrontal":
        cortex = PreFrontalCortex()
        content = _get_target_text(args)
        query = getattr(args, "query", "")
        strict = getattr(args, "strict", False)
        result = cortex.audit(content, query=query, force_strict=strict)

        if getattr(args, "json", False):
            print(json.dumps(result, indent=2, ensure_ascii=False))
            sys.exit(0 if result["passed"] else 1)

        print("================================================================================")
        print("                THSYR // AUDITORIA DO CORTE PRE-FRONTAL COMPLETO                ")
        print("================================================================================")
        print(f"Status do Córtex:      {result['status']}")
        print(f"Aprovado:              {'SIM' if result['passed'] else 'NAO'}")
        print(f"Gate Score:            {result['gate_score'] * 100:.1f}%")
        print(f"Modo Estrito:          {'ATIVO' if result['strict_mode'] else 'INATIVO'}")
        print("--------------------------------------------------------------------------------")

        if result["violations"]:
            print("VIOLACOES IDENTIFICADAS PELO CORTE PRE-FRONTAL:")
            for idx, v in enumerate(result["violations"], 1):
                print(f"  [{idx}] {v}")
            print("--------------------------------------------------------------------------------")
            print("ACAO: Saida bloqueada pelo filtro pre-frontal. O texto deve ser refatorado.")
        else:
            print("Todas as restricoes canônicas e portoes foram respeitados.")

        print("================================================================================")
        sys.exit(0 if result["passed"] else 1)

    return False
