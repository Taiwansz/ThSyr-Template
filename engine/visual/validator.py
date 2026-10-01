"""
ThSyr Visual Craft Validator & Static Inspector
Auditor estático e determinístico de interfaces HTML/CSS contra mediocridade, AI-slop e violações de diretrizes.
"""

import os
import re
from pathlib import Path
from typing import Any


class VisualCraftValidator:
    def __init__(self):
        # Regex de emojis estrita
        self.emoji_pattern = re.compile(
            r"[\U00010000-\U0010ffff]|[\u2600-\u27BF]|[\u2300-\u23FF]|[\u2B50-\u2B55]|[\uD83C-\uDBFF\uDC00-\uDFFF]"
        )
        
        # Fontes de display de prestígio autorizadas
        self.allowed_display_fonts = [
            "syne", "clash display", "cabinet grotesk", "space grotesk",
            "fraunces", "playfair display", "instrument serif", "general sans",
            "plus jakarta sans", "dm sans", "satoshi"
        ]

    def audit_file(self, file_path: str | Path) -> dict[str, Any]:
        """Audita um arquivo HTML no sistema de arquivos."""
        path = Path(file_path)
        if not path.exists():
            return {
                "passed": False,
                "score": 0,
                "file": str(path),
                "errors": [f"Arquivo nao encontrado: {path}"],
                "warnings": [],
                "metrics": {}
            }
            
        content = path.read_text(encoding="utf-8", errors="ignore")
        return self.audit_content(content, source_name=str(path.name))

    def audit_content(self, html_content: str, source_name: str = "raw_content") -> dict[str, Any]:
        """Audita o conteúdo bruto HTML/CSS."""
        errors: list[str] = []
        warnings: list[str] = []
        score = 100

        # 1. Regra Inegociável: Tolerância Zero a Emojis
        emojis_found = self.emoji_pattern.findall(html_content)
        if emojis_found:
            errors.append(f"Tolerancia Zero a Emojis violada: encontrados {len(emojis_found)} emojis no arquivo.")
            score -= 40

        # 2. Diretriz Anti-Slop: Fontes com Identidade
        lower_content = html_content.lower()
        has_display_font = any(f in lower_content for f in self.allowed_display_fonts)
        if not has_display_font:
            errors.append("Anti-Slop: Nenhuma fonte expressiva de display identificada. Proibido uso exclusivo de fontes de sistema ou Inter/Roboto padroes.")
            score -= 25

        # 3. Apple Design: Resposta de Latência Zero no :active ou pointerdown
        has_active_feedback = (
            ":active" in html_content and ("scale" in html_content or "transform" in html_content)
        ) or "pointerdown" in html_content
        if not has_active_feedback:
            warnings.append("Apple Design: Nao foi detectada microinteracao tatil com compressao em :active (scale) ou listener pointerdown.")
            score -= 10

        # 4. Apple Design: Física de Transição / Molas
        has_spring_or_cubic = "cubic-bezier" in html_content or "spring" in html_content or "transition:" in html_content
        if not has_spring_or_cubic:
            warnings.append("Apple Design: Nao foi detectada curva de aceleracao fisica (cubic-bezier ou spring).")
            score -= 10

        # 5. Acessibilidade: prefers-reduced-motion
        has_reduced_motion = "prefers-reduced-motion" in html_content
        if not has_reduced_motion:
            warnings.append("Acessibilidade: Suporte mandatorio a 'prefers-reduced-motion' ausente.")
            score -= 10

        # 6. Anti-Slop: Detecção do Trio de Cards Simétricos Preguiçosos
        # Verifica se há repetição exata de classes de 3 colunas sem variação assimetrica (ex: grid-cols-3 repetindo 3 divs identicas)
        card_trio_pattern = re.findall(r'<div[^>]*class="[^"]*(?:col-span|card|feature|item)[^"]*"', html_content, re.IGNORECASE)
        # Se contiver a classe cliché "grid grid-cols-3" sem elementos de span diferenciado (como col-span-2, col-span-7, col-span-8)
        has_asymmetric_span = any(span in html_content for span in ["col-span-2", "col-span-3", "col-span-7", "col-span-8", "col-span-5", "col-span-4"])
        if "grid-cols-3" in html_content and not has_asymmetric_span:
            warnings.append("Anti-Slop: Detectado layout simetrico convencional de 3 colunas sem âncora bento (60/40). Recomenda-se assimetria intencional.")
            score -= 10

        # 7. Anti-Slop: Proibição Estrita de Pílulas/Cápsulas de Texto de IA (AI Badges / Capsules)
        pill_capsule_pattern = re.findall(
            r'<span[^>]*class="[^"]*rounded-full[^"]*(?:px-|py-|border|bg-)[^"]*"[^>]*>[^<]+</span>',
            html_content,
            re.IGNORECASE
        )
        if pill_capsule_pattern:
            errors.append(
                f"Anti-Slop: Detectada(s) {len(pill_capsule_pattern)} pilula(s)/capsula(s) de texto de IA ('rounded-full'). "
                "E expressamente proibido encapsular textos em capsulas. Use tipografia editorial pura com tracking."
            )
            score -= 30

        # 8. Anti-Slop: Proibição de Ícones Sparkles / Varinha Mágica de IA
        has_sparkles = re.search(r'data-lucide=["\'](?:sparkles|wand|magic)["\']|class=["\'][^"\']*(?:sparkles|ai-badge)[^"\']*["\']', html_content, re.IGNORECASE)
        if has_sparkles:
            errors.append("Anti-Slop: Detectado icone de brilho/varinha magica de IA ('sparkles'). Banido pelo protocolo de pureza visual.")
            score -= 25

        # 9. Stack Ágil & Moderno: Tailwind CDN ou CSS Variables estruturadas
        has_tailwind = "cdn.tailwindcss.com" in html_content or "tailwindcss" in html_content
        has_css_vars = ":root" in html_content and "--" in html_content
        if not (has_tailwind or has_css_vars):
            warnings.append("Arquitetura: Recomenda-se o uso de Tailwind CSS via CDN ou CSS variaveis estruturadas para acelerar acabamento.")
            score -= 5

        # Normalização do score
        score = max(0, min(100, score))
        passed = len(errors) == 0 and score >= 75

        return {
            "passed": passed,
            "score": score,
            "source": source_name,
            "errors": errors,
            "warnings": warnings,
            "metrics": {
                "length_bytes": len(html_content.encode("utf-8")),
                "emojis_count": len(emojis_found),
                "has_tailwind": has_tailwind,
                "has_css_variables": has_css_vars,
                "has_display_font": has_display_font,
                "has_active_feedback": has_active_feedback,
                "has_spring_physics": has_spring_or_cubic,
                "has_reduced_motion": has_reduced_motion,
            }
        }
