#!/usr/bin/env python3
"""
Capturador visual com Playwright para apresentacoes Editorial Canvas 3D.
Doutrina ThSyr de Engenharia de Frontend.
"""

import argparse
import asyncio
import os
import sys

async def capture_panels(html_path: str, out_dir: str, width: int = 1440, height: int = 900):
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("Erro: Playwright nao instalado. Execute: pip install playwright", file=sys.stderr)
        sys.exit(1)

    abs_html = os.path.abspath(html_path)
    if not os.path.exists(abs_html):
        print(f"Erro: Arquivo nao encontrado: {abs_html}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(out_dir, exist_ok=True)
    file_uri = f"file:///{abs_html.replace(os.sep, '/')}"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": width, "height": height})
        await page.goto(file_uri)
        await page.wait_for_timeout(1000)

        # Detectar quantidade de paineis
        panel_count = await page.evaluate("document.querySelectorAll('.panel').length")
        print(f"Detectados {panel_count} paineis na apresentacao.")

        for idx in range(panel_count):
            await page.evaluate(f"window.scrollTo(0, window.innerHeight * {idx});")
            await page.wait_for_timeout(700)
            shot_name = f"painel_{idx:02d}.png"
            shot_path = os.path.join(out_dir, shot_name)
            await page.screenshot(path=shot_path)
            print(f"  [+] Capturado Painel {idx} -> {shot_path}")

        await browser.close()
    print(f"Todas as capturas foram salvas com sucesso em: {out_dir}")

def main():
    parser = argparse.ArgumentParser(description="Captura de Paineis de Apresentacao via Playwright")
    parser.add_argument("html_file", help="Caminho do arquivo HTML da apresentacao")
    parser.add_argument("--output-dir", "-o", default="capturas", help="Diretorio de destino dos screenshots")
    parser.add_argument("--width", type=int, default=1440, help="Largura da viewport (padrao 1440)")
    parser.add_argument("--height", type=int, default=900, help="Altura da viewport (padrao 900)")

    args = parser.parse_args()
    asyncio.run(capture_panels(args.html_file, args.output_dir, args.width, args.height))

if __name__ == "__main__":
    main()
