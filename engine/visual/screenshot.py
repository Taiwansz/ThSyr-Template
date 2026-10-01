"""
ThSyr Visual Studio & Frontend Craft Engine - Screenshot Renderer
Renderizador headless baseado em Playwright para inspeção visual em resolução real de estúdio.
"""

from pathlib import Path


def capture_screenshot(
    html_file_or_url: str | Path,
    output_path: str | Path,
    width: int = 1440,
    height: int = 900,
    full_page: bool = False,
    wait_time_ms: int = 1500
) -> Path:
    """
    Renderiza o arquivo HTML ou URL em resolução de estúdio e salva screenshot em disco.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Playwright nao esta instalado. Execute 'pip install -e .[visual]' "
            "e depois 'playwright install chromium'."
        ) from exc

    target = str(html_file_or_url)
    if not target.startswith("http://") and not target.startswith("https://") and not target.startswith("file://"):
        target = Path(target).resolve().as_uri()

    out_file = Path(output_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": width, "height": height},
            device_scale_factor=2
        )
        page = context.new_page()
        page.goto(target, wait_until="networkidle")
        page.wait_for_timeout(wait_time_ms)
        page.screenshot(path=str(out_file), full_page=full_page)
        browser.close()

    return out_file
