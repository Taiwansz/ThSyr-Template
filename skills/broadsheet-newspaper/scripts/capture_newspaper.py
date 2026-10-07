#!/usr/bin/env python3
"""
Broadsheet Newspaper High-Resolution Visual Capture
Renderiza o arquivo HTML em resolução de 1440px e grava captura PNG de página inteira.
Zero dependências obrigatórias (Playwright opcional com detecção suave).
Zero emojis.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def capture_newspaper_screenshot(
    html_path: Path,
    output_png: Path,
    viewport_width: int = 1440,
    viewport_height: int = 2400,
) -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[AVISO] Playwright nao encontrado no ambiente Python.")
        print("        Para captura automatizada de screenshots, instale via: pip install playwright && playwright install chromium")
        return False

    if not html_path.is_file():
        print(f"[ERRO] Arquivo HTML nao encontrado: {html_path}", file=sys.stderr)
        return False

    abs_url = html_path.resolve().as_uri()
    output_png.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": viewport_width, "height": viewport_height},
            device_scale_factor=2,  # Captura em alta densidade Retina
        )
        page = context.new_page()
        page.goto(abs_url, wait_until="networkidle")
        page.screenshot(path=str(output_png), full_page=True)
        browser.close()

    print(f"[OK] Captura broadsheet gravada com sucesso em: {output_png}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Captura visual em alta resolucao de broadsheet historico via Playwright."
    )
    parser.add_argument("html_file", type=str, help="Caminho do arquivo HTML a ser renderizado.")
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="broadsheet_preview.png",
        help="Caminho do arquivo PNG de destino.",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1440,
        help="Largura da viewport em pixels (padrao 1440).",
    )
    args = parser.parse_args()

    html_file = Path(args.html_file).resolve()
    output_file = Path(args.output).resolve()

    success = capture_newspaper_screenshot(html_file, output_file, viewport_width=args.width)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
