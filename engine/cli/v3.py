"""CLI commands introduced by Cognitive Expansion V3.

New commands live here instead of expanding the legacy thsyr.py command module.
"""

from __future__ import annotations

import json
from argparse import _SubParsersAction
from pathlib import Path
from typing import Any

from ..evolution_lab import EvolutionCandidate, EvolutionLab
from ..memory_adaptation import MemoryAdaptationStore
from ..security_scanner import RepositorySecretScanner


def register_v3_subcommands(subparsers: _SubParsersAction) -> None:
    subparsers.add_parser(
        "self-model",
        help="Exibe capacidades, ferramentas, providers e limitacoes observaveis do Syr",
    )

    security = subparsers.add_parser(
        "security-scan",
        help="Procura possiveis credenciais no repositorio sem revelar os valores",
    )
    security.add_argument("--json", action="store_true", help="Imprime achados em JSON redigido")

    feedback = subparsers.add_parser(
        "memory-feedback",
        help="Reforca ou enfraquece memorias com base em utilidade observada",
    )
    feedback.add_argument("memory_ids", nargs="+", help="IDs de memoria recuperada")
    group = feedback.add_mutually_exclusive_group(required=True)
    group.add_argument("--helpful", action="store_true", help="Marca as memorias como uteis")
    group.add_argument("--not-helpful", action="store_true", help="Marca as memorias como pouco uteis")

    lab = subparsers.add_parser(
        "evolution-lab",
        help="Avalia um unified diff em worktree descartavel antes de qualquer promocao",
    )
    lab.add_argument("patch_file", help="Arquivo .diff/.patch a avaliar")
    lab.add_argument("--objective", default="Improve ThSyr without regressions")


def dispatch_v3(args: Any, memory: Any, router: Any) -> bool:
    if args.command == "self-model":
        print(json.dumps(router.self_model.snapshot(), indent=2, ensure_ascii=False))
        return True

    if args.command == "security-scan":
        findings = RepositorySecretScanner().scan()
        if args.json:
            print(json.dumps([finding.to_dict() for finding in findings], indent=2, ensure_ascii=False))
        else:
            print("==================================================")
            print("       THSYR // REDACTED SECURITY SCAN            ")
            print("==================================================")
            print(f"Achados potenciais: {len(findings)}")
            for finding in findings[:100]:
                print(f"- {finding.path}:{finding.line} [{finding.kind}] {finding.preview}")
            print("==================================================")
        return True

    if args.command == "memory-feedback":
        store = MemoryAdaptationStore()
        helpful = bool(args.helpful)
        for memory_id in args.memory_ids:
            result = store.record_feedback(memory_id, helpful=helpful)
            print(
                f"{memory_id}: utility={result['utility_score']:.3f} "
                f"accesses={result['access_count']}"
            )
        return True

    if args.command == "evolution-lab":
        patch_path = Path(args.patch_file)
        if not patch_path.is_file():
            raise SystemExit(f"Patch nao encontrado: {patch_path}")
        candidate = EvolutionCandidate(
            id=f"cli_{patch_path.stem}",
            objective=args.objective,
            patch_text=patch_path.read_text(encoding="utf-8"),
            source="cli",
        )
        verdict = EvolutionLab(gateway=router.model_gateway).evaluate_candidate(candidate)
        print(json.dumps(verdict.to_dict(), indent=2, ensure_ascii=False))
        return True

    return False
