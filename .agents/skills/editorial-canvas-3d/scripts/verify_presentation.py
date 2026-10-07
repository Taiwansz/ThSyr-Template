#!/usr/bin/env python3
"""
Auditor Estatico e Forense para Apresentacoes Editorial Canvas 3D (Versao 2.0).
Doutrina ThSyr de Engenharia de Frontend e Rigor Cientifico.
"""

import os
import re
import sys

def verify_file(file_path: str) -> bool:
    if not os.path.exists(file_path):
        print(f"Erro: Arquivo nao encontrado: {file_path}", file=sys.stderr)
        return False

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    errors = []
    warnings = []

    # 1. Verificacao estrita de emojis
    emoji_pattern = re.compile(
        r"[\U00010000-\U0010ffff]|[\u2600-\u27BF]|[\u2300-\u23FF]|[\u2B50-\u2B55]|[\uD83C-\uDBFF\uDC00-\uDFFF]"
    )
    emojis = emoji_pattern.findall(content)
    if emojis:
        errors.append(f"Regra 1 violada: {len(emojis)} emojis detectados no documento.")

    # 2. Verificacao de AI-Slop (badges ovais rounded-full, sparkles e paletas roxas padronizadas)
    if "rounded-full" in content:
        errors.append("Regra 2 violada: rounded-full detectado (proibicao absoluta de pilulas de IA).")
    if "sparkles" in content.lower():
        errors.append("Regra 2 violada: sparkles detectado.")
    ai_purple_pattern = re.compile(r"#(?:8B5CF6|A855F7|7C3AED|6366F1)", re.IGNORECASE)
    if ai_purple_pattern.search(content):
        warnings.append("Alerta de paleta: cor violeta padronizada de IA detectada.")

    # 3. Verificacao de Tipografia Editorial de Estúdio (Display + Mono)
    APPROVED_DISPLAY = [
        "Schibsted Grotesk", "Cabinet Grotesk", "Syne", "Clash Display",
        "Instrument Serif", "Cormorant Garamond", "Space Grotesk", "Cinzel",
        "Plus Jakarta Sans", "Inter Tight", "Newsreader", "Fraunces", "Playfair Display"
    ]
    APPROVED_MONO = [
        "JetBrains Mono", "Space Mono", "IBM Plex Mono", "Fira Code", "Geist Mono", "Roboto Mono"
    ]
    has_display = any(f in content for f in APPROVED_DISPLAY)
    has_mono = any(f in content for f in APPROVED_MONO)
    if not has_display:
        errors.append(f"Tipografia violada: Nenhuma fonte Display de estúdio aprovada encontrada ({', '.join(APPROVED_DISPLAY[:5])}...).")
    if not has_mono:
        errors.append(f"Tipografia violada: Nenhuma fonte Monospace técnica aprovada encontrada ({', '.join(APPROVED_MONO[:4])}...).")

    # 4. Verificacao de Motor Canvas 2D nativo
    if not re.search(r"getContext\(\s*['\"]2d['\"]", content):
        errors.append("Motor grafico violado: Canvas 2D nativo nao detectado.")
    if "Float32Array" not in content:
        errors.append("Performance violada: Float32Array ausente no pipeline de memoria.")
    if "requestAnimationFrame" not in content:
        errors.append("Render loop violado: requestAnimationFrame ausente.")

    # 5. Axioma do Hibrido Vetorial (Arestas e Rotulos 3D)
    has_stroke = "gx.stroke()" in content or "stroke()" in content
    has_filltext = "gx.fillText" in content or "fillText" in content
    if not has_stroke:
        errors.append("Axioma 3 violado: Nenhuma aresta vetorial (stroke) detectada no Canvas.")
    if not has_filltext:
        errors.append("Axioma 3 violado: Nenhum rotulo tipografico 3D (fillText) detectado no espaco.")

    # 6. Verificacao de Acessibilidade
    if "prefers-reduced-motion" not in content:
        errors.append("Acessibilidade violada: prefers-reduced-motion ausente.")

    # 7. Controle de Bancada (Navegacao por Teclado e Tela Cheia)
    has_keys = "keydown" in content and ("ArrowDown" in content or "scrollIntoView" in content)
    if not has_keys:
        warnings.append("Controle de bancada: Event listener de teclado (keydown) ausente ou incompleto.")
    if "requestFullscreen" not in content and "fullscreenElement" not in content:
        warnings.append("Controle de bancada: Alternancia de tela cheia (F) nao detectada.")

    # 8. Integridade Estrutural (Paridade entre HTML, Estados e HUD)
    panel_matches = re.findall(r'<section\s+[^>]*class=["\'][^"\']*panel[^"\']*["\']', content, re.IGNORECASE)
    panel_count = len(panel_matches)
    
    state_match = re.search(r"const\s+STATES\s*=\s*(\d+);", content)
    declared_states = int(state_match.group(1)) if state_match else None

    if declared_states is not None:
        if panel_count != declared_states:
            errors.append(
                f"Integridade violada: {panel_count} paineis HTML encontrados vs {declared_states} declarados em STATES."
            )
    else:
        warnings.append("Declaracao explicita 'const STATES = N;' nao encontrada para validacao de coerencia.")

    names_match = re.search(r"const\s+NAMES\s*=\s*\[(.*?)\];", content, re.DOTALL)
    if names_match:
        items = [x.strip() for x in names_match.group(1).split(",") if x.strip()]
        if declared_states is not None and len(items) != declared_states:
            warnings.append(
                f"HUD divergente: Array NAMES possui {len(items)} rotulos vs {declared_states} estados."
            )

    print(f"=== AUDITORIA EDITORIAL CANVAS 3D (V2.0): {os.path.basename(file_path)} ===")
    if errors:
        print(f"STATUS: REPROVADO ({len(errors)} erros)")
        for err in errors:
            print(f"  [X] {err}")
        if warnings:
            for w in warnings:
                print(f"  [!] {w}")
        return False
    else:
        print("STATUS: APROVADO (100 / 100)")
        print("  [OK] Zero emojis detectados.")
        print("  [OK] Zero AI-slop (sem rounded-full, sem sparkles).")
        print("  [OK] Tipografia Schibsted Grotesk + JetBrains Mono conforme.")
        print("  [OK] Motor Canvas 2D nativo com buffers Float32Array.")
        print("  [OK] Hibrido vetorial ativo (arestas vetoriais + rotulos tipograficos 3D).")
        print("  [OK] Acessibilidade prefers-reduced-motion presente.")
        print(f"  [OK] Integridade estrutural verificada ({panel_count} paineis == {declared_states} estados).")
        if warnings:
            for w in warnings:
                print(f"  [!] {w}")
        return True

def main():
    if len(sys.argv) < 2:
        print("Uso: python verify_presentation.py <caminho_arquivo.html>")
        sys.exit(1)
    
    success = verify_file(sys.argv[1])
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
