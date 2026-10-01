"""
ThSyr CLI - Brand & Logo Design Commands (Occipital Lobe)
Comandos operacionais de busca no acervo de 1.400+ logos, auditoria geometrica,
geracao de folhas de teste, pranchas de conceito e briefs de identidade visual.
"""

import json
import sys
from pathlib import Path

from ..brand import (
    INDUSTRY_CLICHES,
    MARK_TYPES,
    OPTICAL_REFINEMENT_RULES,
    VISUAL_TECHNIQUES,
    BrandEngine,
)


def cmd_logo(args):
    action = getattr(args, "logo_action", None)
    if not action:
        print("Uso: thsyr logo {search,audit,stats,brief,principles,preview,sheet,variants,board} [opcoes]")
        return

    engine = BrandEngine()

    if action == "stats":
        stats = engine.get_stats()
        print("==================================================")
        print("        THSYR // ACERVO DE LOGOS E MARCAS        ")
        print("==================================================")
        print(f"Total de Logos Cadastrados: {stats.get('total_logos', 0)}")
        print(f"Exemplares Pedagogicos:     {stats.get('exemplary_count', 0)}")
        print(f"Diretorio do Acervo:        {stats.get('library_path', '')}")
        print("--------------------------------------------------")
        types = stats.get("mark_types", {})
        if types:
            print("Distribuicao por Tipo de Marca:")
            for t_name, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {t_name:<16} : {count:>4} logos")
        print("==================================================")

    elif action == "search":
        exemplary = getattr(args, "exemplary", False)
        limit = getattr(args, "limit", 15)
        results = engine.search_references(
            query=getattr(args, "query", None),
            mark_type=getattr(args, "type", None),
            technique=getattr(args, "technique", None),
            geometry=getattr(args, "geometry", None),
            industry=getattr(args, "industry", None),
            exemplary=exemplary,
            limit=limit,
        )

        fmt = getattr(args, "format", "table")
        if fmt == "json":
            print(json.dumps([r.to_dict() for r in results], indent=2, ensure_ascii=False))
            return

        if fmt == "paths":
            for r in results:
                print(r.path)
            return

        print(f"Encontrados {len(results)} logos (exibindo ate {limit}):")
        for r in results:
            star = "[*]" if r.exemplary else "   "
            print(f"{star} {r.filename:<30} {r.mark_type:<14} {r.colors}c | {r.subject}")
            if r.note:
                print(f"      Nota: {r.note}")

    elif action == "audit":
        files = getattr(args, "files", [])
        if not files:
            print("Erro: Nenhum arquivo SVG informado para auditoria.")
            return

        bg = getattr(args, "bg", None)
        as_json = getattr(args, "json", False)

        all_reports = []
        for f in files:
            report = engine.audit_svg(f, bg_color=bg)
            all_reports.append(report.to_dict())
            if not as_json:
                status_str = "APROVADO" if report.passed else "FALHA / REVISAO NECESSARIA"
                print(f"\n[AUDITORIA] {report.filename} — {status_str} ({report.bytes_count} bytes)")
                if report.viewbox:
                    print(f"  viewBox: {report.viewbox} (proporcao: {report.aspect_ratio})")
                if report.colors_detected:
                    print(f"  Cores detectadas: {', '.join(report.colors_detected)}")
                for finding in report.findings:
                    print(f"  [{finding.level}] {finding.code}: {finding.message}")

        if as_json:
            print(json.dumps(all_reports, indent=2, ensure_ascii=False))

    elif action == "brief":
        name = getattr(args, "name", "NovaMarca")
        ind = getattr(args, "industry", "tech")
        adjectives = getattr(args, "adjectives", None)
        offering = getattr(args, "offering", "")
        promise = getattr(args, "promise", "")

        brief = engine.create_brief(
            brand_name=name,
            industry=ind,
            adjectives=adjectives.split(",") if adjectives else None,
            offering=offering,
            promise=promise,
        )
        print(brief.render_markdown())

    elif action == "principles":
        print("==================================================")
        print("     THSYR // REGRAS CANONICAS DE IDENTIDADE     ")
        print("==================================================")
        print("\n--- 8 TIPOS DE MARCA ---")
        for k, v in MARK_TYPES.items():
            print(f"[{k.upper()}] {v['name']}")
            print(f"  Definicao: {v['description']}")
            print(f"  Ideal para: {v['best_for']}")
            print(f"  Regra optica: {v['optical_rule']}\n")

        print("\n--- 14 TECNICAS VISUAIS MATRIZ ---")
        for k, v in VISUAL_TECHNIQUES.items():
            print(f"[{k}] {v['name']}: {v['description']} (Efeito: {v['effect']})")

        print("\n--- REGRAS DE REFINAMENTO OPTICO ---")
        for r in OPTICAL_REFINEMENT_RULES:
            print(f"- {r['rule']}: {r['explanation']}")
        print("==================================================")

    elif action == "preview":
        files = getattr(args, "files", [])
        output = getattr(args, "output", "preview.html")
        ind = getattr(args, "industry", None)
        res = engine.generator.generate_preview_sheet(files, output, industry=ind)
        if res["success"]:
            print(f"[OK] Folha de teste gerada em: {output}")
        else:
            print(f"[ERRO] Falha ao gerar preview: {res.get('stderr') or res.get('error')}")

    elif action == "sheet":
        symbols = getattr(args, "symbols", [])
        output = getattr(args, "output", "concepts.png")
        lockups = getattr(args, "lockups", None)
        names = getattr(args, "names", None)
        notes = getattr(args, "notes", None)
        recommend = getattr(args, "recommend", 1)
        greyscale = getattr(args, "greyscale", False)

        res = engine.generator.generate_concept_sheet(
            symbol_files=symbols,
            output_png=output,
            lockup_files=lockups,
            names=names,
            notes=notes,
            recommend_idx=recommend,
            greyscale=greyscale,
        )
        if res["success"]:
            print(f"[OK] Prancha comparativa gerada em: {output}")
        else:
            print(f"[ERRO] Falha ao gerar concept sheet: {res.get('stderr') or res.get('error')}")

    elif action == "variants":
        target = getattr(args, "file", None)
        title = getattr(args, "title", "Brand Logo")
        mono = getattr(args, "mono", None)
        icon_bg = getattr(args, "icon_bg", None)
        web_icons = getattr(args, "web_icons", False)
        out_dir = getattr(args, "out_dir", None)

        res = engine.generator.export_variants(
            svg_file=target,
            title=title,
            mono_color=mono,
            icon_bg=icon_bg,
            web_icons=web_icons,
            out_dir=out_dir,
        )
        if res["success"]:
            print(f"[OK] Variantes geradas no diretorio: {res['target_dir']}")
            if res.get("stdout"):
                print(res["stdout"])
        else:
            print(f"[ERRO] Falha ao exportar variantes: {res.get('stderr') or res.get('error')}")

    elif action == "board":
        spec = getattr(args, "spec", None)
        output = getattr(args, "output", "presentation.html")
        png_dir = getattr(args, "png_dir", None)

        res = engine.generator.generate_presentation_board(spec_json=spec, output_html=output, png_dir=png_dir)
        if res["success"]:
            print(f"[OK] Prancha de apresentacao gerada em: {output}")
        else:
            print(f"[ERRO] Falha ao gerar presentation board: {res.get('stderr') or res.get('error')}")
