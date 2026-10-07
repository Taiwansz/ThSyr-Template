#!/usr/bin/env python3
"""
Broadsheet Newspaper Forensic Verifier CLI
Audita arquivos HTML de jornais impressos históricos contra 8 critérios inegociáveis.
Zero dependências externas e zero emojis.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # símbolos & pictogramas
    "\U0001F680-\U0001F6FF"  # transporte & mapas
    "\U0001F1E0-\U0001F1FF"  # bandeiras
    "\U00002702-\U000027B0"  # dingbats
    "\U000024C2-\U0001F251"
    "\U0001F900-\U0001F9FF"  # suplemento
    "\U0001FA70-\U0001FAFF"  # novos símbolos
    "]+",
    flags=re.UNICODE,
)

FORBIDDEN_TAGS = [
    "<button",
    "<input",
    "<textarea",
    "<select",
    "<dialog",
]

FORBIDDEN_CLASSES = [
    "modal",
    "carousel",
    "rounded-full",
    "rounded-3xl",
    "rounded-2xl",
    "theme-toggle",
    "dark-mode-switch",
    "navbar-toggle",
]


def audit_newspaper_html(html_path: Path) -> dict[str, any]:
    if not html_path.is_file():
        return {
            "passed": False,
            "score": 0,
            "errors": [f"Arquivo nao encontrado: {html_path}"],
            "checks": {},
        }

    content = html_path.read_text(encoding="utf-8", errors="replace")
    errors = []
    checks = {}
    score = 0

    # 1. Checagem de Emojis (15 pontos)
    found_emojis = EMOJI_PATTERN.findall(content)
    if not found_emojis:
        checks["no_emojis"] = True
        score += 15
    else:
        checks["no_emojis"] = False
        errors.append(f"Detectados {len(found_emojis)} emojis no documento (proibicao absoluta).")

    # 2. Ausencia de Elementos de Interface Digital Moderna (15 pontos)
    digital_violations = []
    lower_content = content.lower()
    for tag in FORBIDDEN_TAGS:
        if tag in lower_content:
            digital_violations.append(f"Tag proibida '{tag}' detectada.")
    for cls in FORBIDDEN_CLASSES:
        if cls in lower_content:
            digital_violations.append(f"Classe/termo proibido '{cls}' detectado.")

    if not digital_violations:
        checks["no_digital_ui"] = True
        score += 15
    else:
        checks["no_digital_ui"] = False
        errors.extend(digital_violations)

    # 3. Tipografia Historica de Linotipia e Imprensa (15 pontos)
    has_playfair = "playfair display" in lower_content
    has_old_std = "old standard tt" in lower_content or "garamond" in lower_content
    has_cinzel = "cinzel" in lower_content
    has_blackletter = "unifrakturmaguntia" in lower_content or "blackletter" in lower_content or "old english" in lower_content

    if has_playfair and has_old_std and has_cinzel and has_blackletter:
        checks["historical_typography"] = True
        score += 15
    else:
        checks["historical_typography"] = False
        missing = []
        if not has_playfair: missing.append("Playfair Display")
        if not has_old_std: missing.append("Old Standard TT / Garamond")
        if not has_cinzel: missing.append("Cinzel")
        if not has_blackletter: missing.append("UnifrakturMaguntia / Blackletter")
        errors.append(f"Fontes historicas ausentes ou incompletas: {', '.join(missing)}.")

    # 4. Folha Fisica Broadsheet (15 pontos)
    has_broadsheet_class = "newspaper-broadsheet" in lower_content
    has_max_width = "max-width" in lower_content
    has_box_shadow = "box-shadow" in lower_content

    if has_broadsheet_class and has_max_width and has_box_shadow:
        checks["broadsheet_sheet"] = True
        score += 15
    else:
        checks["broadsheet_sheet"] = False
        errors.append("Estrutura .newspaper-broadsheet com limites fisicos e sombras ausente.")

    # 5. Vinco Central da Dobra Fisica (10 pontos)
    has_crease = "::before" in lower_content and "left: 50%" in lower_content and "linear-gradient" in lower_content
    if has_crease:
        checks["center_crease"] = True
        score += 10
    else:
        checks["center_crease"] = False
        errors.append("Vinco vertical central da dobra fisica (::before com left: 50%) nao detectado.")

    # 6. Capitular Historica (Drop Cap) (10 pontos)
    has_dropcap = "::first-letter" in lower_content or "drop-cap" in lower_content
    if has_dropcap:
        checks["drop_cap"] = True
        score += 10
    else:
        checks["drop_cap"] = False
        errors.append("Capitular (drop-cap / ::first-letter) da materia principal ausente.")

    # 7. Componentes Editoriais Obrigatorios (10 pontos)
    has_masthead = "masthead" in lower_content
    has_datebar = "date-bar" in lower_content or "folio" in lower_content
    has_colophon = "footer" in lower_content or "expediente" in lower_content or "colofao" in lower_content
    has_wire = "telegrafo" in lower_content or "wire" in lower_content or "despacho" in lower_content

    if has_masthead and has_datebar and has_colophon and has_wire:
        checks["editorial_components"] = True
        score += 10
    else:
        checks["editorial_components"] = False
        errors.append("Componentes obrigatorios ausentes (masthead, date-bar, colofao ou telegrafo).")

    # 8. Paleta Mineral de Celulose e Tinta (10 pontos)
    has_newsprint_var = "--newsprint" in lower_content or "#f3ede2" in lower_content or "#f7e6d2" in lower_content
    has_ink_var = "--ink" in lower_content or "#121110" in lower_content or "#181513" in lower_content

    if has_newsprint_var and has_ink_var:
        checks["mineral_palette"] = True
        score += 10
    else:
        checks["mineral_palette"] = False
        errors.append("Variaveis de cor mineral de papel e tinta tipografica ausentes.")

    passed = score >= 90 and len(digital_violations) == 0 and len(found_emojis) == 0

    return {
        "passed": passed,
        "score": score,
        "checks": checks,
        "errors": errors,
        "file": str(html_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audita arquivos HTML de broadsheet historico com criterios forenses de imprensa."
    )
    parser.add_argument("html_file", type=str, help="Caminho do arquivo HTML a ser auditado.")
    args = parser.parse_args()

    target_path = Path(args.html_file).resolve()
    result = audit_newspaper_html(target_path)

    print("=" * 70)
    print("RELATORIO FORENSE DE CONFORMIDADE — BROADSHEET NEWSPAPER")
    print("=" * 70)
    print(f"Arquivo Auditado : {result['file']}")
    print(f"Pontuacao Total  : {result['score']}/100")
    print(f"Status           : {'APROVADO (100% CONFORME)' if result['passed'] else 'REPROVADO / INIBIDO'}")
    print("-" * 70)
    print("Checagens Individuais:")
    for check_name, status in result.get("checks", {}).items():
        print(f"  - {check_name.ljust(25)}: {'[OK]' if status else '[FALHA]'}")

    if result["errors"]:
        print("-" * 70)
        print("Infracoes Detectadas:")
        for err in result["errors"]:
            print(f"  [!] {err}")

    print("=" * 70)

    if not result["passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
