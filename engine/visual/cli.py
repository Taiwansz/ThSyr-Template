"""
ThSyr Visual & Frontend Craft Engine CLI
Interface de comando para auditoria, inspeção e geração de interfaces de estúdio.
"""

import argparse
import json
import sys
from pathlib import Path

from .archetypes import NICHE_ARCHETYPES, get_niche_preset
from .contracts import VisualArtifactKind, VisualBrief
from .scaffolder import generate_studio_scaffold
from .studio import VisualStudio
from .taste_memory import TasteMemory
from .validator import VisualCraftValidator


def main():
    parser = argparse.ArgumentParser(description="ThSyr Visual Studio & Frontend Craft CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Comando: audit
    audit_parser = subparsers.add_parser("audit", help="Audita um arquivo HTML contra as regras anti-slop e Apple design")
    audit_parser.add_argument("file", help="Caminho para o arquivo HTML a auditar")
    audit_parser.add_argument("--json", action="store_true", help="Exibe resultado em formato JSON")

    # Comando: list
    subparsers.add_parser("list", help="Lista todos os nichos de mercado canônicos mapeados")

    # Comando: preset
    preset_parser = subparsers.add_parser("preset", help="Exibe os tokens de design de um nicho específico")
    preset_parser.add_argument("niche", help="Nome ou alias do nicho")

    # Comando: scaffold
    scaffold_parser = subparsers.add_parser("scaffold", help="Gera um esqueleto HTML pronto para o nicho")
    scaffold_parser.add_argument("--niche", required=True, help="Nicho de mercado (ex: saas_devtools, luxury_craft)")
    scaffold_parser.add_argument("--title", default="Studio Interface", help="Titulo da pagina")
    scaffold_parser.add_argument("--headline", default="Arquitetura Visual Sem Concessão", help="Headline do hero")
    scaffold_parser.add_argument("--output", help="Arquivo de destino para salvar o HTML")

    # Comando: prepare
    prepare_parser = subparsers.add_parser("prepare", help="Monta o contrato de direcao de arte antes da execucao")
    prepare_parser.add_argument("--objective", required=True, help="Objetivo visual do artefato")
    prepare_parser.add_argument("--kind", default="website", choices=[kind.value for kind in VisualArtifactKind])
    prepare_parser.add_argument("--niche", help="Nicho ou alias de mercado")
    prepare_parser.add_argument("--audience", help="Publico-alvo")
    prepare_parser.add_argument("--impression", help="Impressao visual desejada")
    prepare_parser.add_argument("--reference", action="append", default=[], help="Referencia positiva/benchmark, repetivel")
    prepare_parser.add_argument("--avoid", action="append", default=[], help="Elemento a evitar, repetivel")
    prepare_parser.add_argument("--project", help="Projeto ativo para escopo de preferencias")

    # Comando: review
    review_parser = subparsers.add_parser("review", help="Executa render + critica visual + quality gate")
    review_parser.add_argument("target", help="URL/HTML para web ou arquivo de imagem para assets")
    review_parser.add_argument("--objective", required=True, help="Objetivo visual do artefato")
    review_parser.add_argument("--kind", default="website", choices=[kind.value for kind in VisualArtifactKind])
    review_parser.add_argument("--niche", help="Nicho ou alias")
    review_parser.add_argument("--output-dir", default=".thsyr/visual-review", help="Diretorio de evidencias")
    review_parser.add_argument("--project", help="Projeto ativo para escopo de preferencias")
    review_parser.add_argument("--json", action="store_true", help="Exibe o relatorio em JSON")

    # Comando: taste-add
    taste_add_parser = subparsers.add_parser("taste-add", help="Registra aprovacao/rejeicao na memoria de gosto")
    taste_add_parser.add_argument("--verdict", required=True, choices=["approved", "rejected"])
    taste_add_parser.add_argument("--kind", required=True, choices=[kind.value for kind in VisualArtifactKind])
    taste_add_parser.add_argument("--reference", required=True)
    taste_add_parser.add_argument("--notes", default="")
    taste_add_parser.add_argument("--tag", action="append", default=[])

    # Comando: feedback
    feedback_parser = subparsers.add_parser(
        "feedback",
        help="Registra feedback visual e sincroniza TasteMemory, FailureMemory e PreferenceGraph",
    )
    feedback_parser.add_argument("--verdict", required=True, choices=["approved", "rejected"])
    feedback_parser.add_argument("--kind", required=True, choices=[kind.value for kind in VisualArtifactKind])
    feedback_parser.add_argument("--reference", required=True)
    feedback_parser.add_argument("--notes", default="")
    feedback_parser.add_argument("--project")
    feedback_parser.add_argument("--tag", action="append", default=[])

    # Comando: failure-context
    failure_parser = subparsers.add_parser(
        "failure-context",
        help="Mostra erros visuais conhecidos que nao devem se repetir",
    )
    failure_parser.add_argument("--kind", required=True, choices=[kind.value for kind in VisualArtifactKind])
    failure_parser.add_argument("--project")

    # Comando: taste-context
    taste_context_parser = subparsers.add_parser("taste-context", help="Mostra contexto de gosto para um tipo de artefato")
    taste_context_parser.add_argument("--kind", required=True, choices=[kind.value for kind in VisualArtifactKind])

    # Comando: capture
    capture_parser = subparsers.add_parser("capture", help="Captura screenshot em alta resolucao via Playwright")
    capture_parser.add_argument("target", help="Arquivo HTML ou URL a renderizar")
    capture_parser.add_argument("--output", "-o", required=True, help="Caminho do arquivo PNG de destino")
    capture_parser.add_argument("--width", type=int, default=1440, help="Largura da viewport (default: 1440)")
    capture_parser.add_argument("--height", type=int, default=900, help="Altura da viewport (default: 900)")
    capture_parser.add_argument("--full-page", action="store_true", help="Capturar pagina inteira")

    args = parser.parse_args()

    if args.command == "audit":
        validator = VisualCraftValidator()
        result = validator.audit_file(args.file)

        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            status = "APROVADO" if result["passed"] else "REPROVADO"
            print("\n==========================================")
            print(f"THSYR VISUAL CRAFT AUDITOR: {status} (Score: {result['score']}/100)")
            print(f"Arquivo: {result['source']}")
            print("==========================================")

            if result["errors"]:
                print("\n[ERROS CRITICOS]:")
                for err in result["errors"]:
                    print(f" - {err}")

            if result["warnings"]:
                print("\n[AVISOS DE MELHORIA]:")
                for warn in result["warnings"]:
                    print(f" - {warn}")

            print(f"\nMetricas: {result['metrics']}")
            print("==========================================\n")

        sys.exit(0 if result["passed"] else 1)

    elif args.command == "list":
        print("\nNichos de Mercado Canônicos do Lobo Occipital:")
        for key, data in NICHE_ARCHETYPES.items():
            print(f" - {key:25} | {data['name']}")
        print()

    elif args.command == "preset":
        preset = get_niche_preset(args.niche)
        print(json.dumps(preset, indent=2, ensure_ascii=False))

    elif args.command == "scaffold":
        html = generate_studio_scaffold(
            niche=args.niche,
            title=args.title,
            headline=args.headline,
        )
        if args.output:
            out_path = Path(args.output)
            out_path.write_text(html, encoding="utf-8")
            print(f"Esqueleto de estúdio salvo em: {out_path.resolve()}")
        else:
            print(html)

    elif args.command == "prepare":
        studio = VisualStudio()
        brief = VisualBrief(
            objective=args.objective,
            artifact_kind=VisualArtifactKind(args.kind),
            niche=args.niche,
            audience=args.audience,
            desired_impression=args.impression,
            references=args.reference,
            must_avoid=args.avoid,
            project_id=args.project,
        )
        prepared = studio.prepare_direction(brief)
        print(json.dumps(prepared, indent=2, ensure_ascii=False))

    elif args.command == "review":
        studio = VisualStudio()
        brief = VisualBrief(
            objective=args.objective,
            artifact_kind=VisualArtifactKind(args.kind),
            niche=args.niche,
            project_id=args.project,
        )
        report = studio.review(args.target, brief, output_dir=args.output_dir)
        if args.json:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            status = "APROVADO" if report["passed"] else "REPROVADO"
            print(f"THSYR VISUAL QUALITY GATE: {status}")
            for critique in report["critiques"]:
                print(f"- {critique['viewport']}: {critique['score']}/100 - {critique['summary']}")
            if not report["passed"]:
                print("\n" + report["refinement_prompt"])
        sys.exit(0 if report["passed"] else 1)

    elif args.command == "taste-add":
        memory = TasteMemory()
        entry = memory.record(
            verdict=args.verdict,
            artifact_kind=args.kind,
            reference=args.reference,
            notes=args.notes,
            tags=args.tag,
        )
        print(json.dumps(entry.to_dict(), indent=2, ensure_ascii=False))

    elif args.command == "feedback":
        studio = VisualStudio()
        brief = VisualBrief(
            objective=args.notes or args.reference,
            artifact_kind=VisualArtifactKind(args.kind),
            project_id=args.project,
        )
        result = studio.record_feedback(
            brief,
            verdict=args.verdict,
            reference=args.reference,
            notes=args.notes,
            tags=args.tag,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "failure-context":
        studio = VisualStudio()
        print(studio.failure_memory.build_context(
            project_id=args.project,
            artifact_kind=args.kind,
        ))

    elif args.command == "taste-context":
        memory = TasteMemory()
        print(memory.build_context(args.kind))

    elif args.command == "capture":
        from .screenshot import capture_screenshot
        out = capture_screenshot(
            html_file_or_url=args.target,
            output_path=args.output,
            width=args.width,
            height=args.height,
            full_page=args.full_page
        )
        print(f"Screenshot capturado com sucesso via Playwright: {out}")


if __name__ == "__main__":
    main()
