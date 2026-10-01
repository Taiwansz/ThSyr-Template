"""
Personal benchmark suite focused on the work patterns the operator actually uses.

The benchmark has a cheap context-only mode and an optional generation mode.
It is intentionally descriptive: it reports coverage and regressions instead of
pretending a subjective output has objective quality without evidence.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .hub import PersonalizationHub


@dataclass(frozen=True)
class BenchmarkCase:
    id: str
    query: str
    domain: str
    artifact_kind: str | None = None
    project_id: str | None = None
    expectation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


DEFAULT_CASES = (
    BenchmarkCase("visual_cafe", "Crie um site premium para uma cafeteria.", "design", "website", expectation="recuperar gosto visual e anti-genericidade"),
    BenchmarkCase("visual_mobile", "Refaça essa interface pensando primeiro no celular.", "design", "ui_screen", expectation="recuperar preferencias mobile"),
    BenchmarkCase("visual_icon", "Crie um conjunto de icones para esta marca.", "design", "icon", expectation="recuperar criterios de iconografia"),
    BenchmarkCase("visual_logo", "Quero uma identidade visual menos generica.", "design", "logo", expectation="recuperar preferencias de branding"),
    BenchmarkCase("code_repo", "Analise o repositorio e implemente end to end.", "engineering", expectation="recuperar autonomia e verificacao"),
    BenchmarkCase("code_continue", "Continue exatamente de onde paramos ontem.", "engineering", expectation="recuperar continuidade"),
    BenchmarkCase("code_constraints", "Mude isso sem mexer no que ja esta funcionando.", "engineering", expectation="recuperar preservacao e escopo"),
    BenchmarkCase("code_audit", "Verifique tudo antes de me dizer que terminou.", "engineering", expectation="recuperar preferencia por prova real"),
    BenchmarkCase("feedback_short_bad", "Ficou ruim, melhore.", "feedback", expectation="usar contexto ativo em vez de feedback vazio"),
    BenchmarkCase("feedback_short_good", "Agora sim, ficou bom.", "feedback", expectation="consolidar o que mudou"),
    BenchmarkCase("project_resume", "Retome esse projeto e me diga o proximo passo.", "continuity", expectation="contexto de projeto sem interrogatorio"),
    BenchmarkCase("decision_compare", "Compare as opcoes e estruture a decisao.", "decision", expectation="recuperar forma de decisao"),
    BenchmarkCase("shopping_constraints", "Procure uma opcao que caiba no meu espaco e respeite minhas restricoes.", "decision", expectation="usar restricoes relevantes"),
    BenchmarkCase("doc_master", "Monte um markdown completo para eu conseguir retomar depois.", "continuity", expectation="recuperar preferencia por documentacao"),
    BenchmarkCase("anti_slop", "Quero algo profissional de verdade, nao cara de template.", "design", "website", expectation="recuperar failure memory e gosto"),
    BenchmarkCase("iteration", "Gere, veja o resultado, critique e corrija ate ficar bom.", "design", "website", expectation="usar visual quality loop"),
    BenchmarkCase("minimal_questions", "Faz completo sem ficar me perguntando coisa trivial.", "working_style", expectation="recuperar autonomia"),
    BenchmarkCase("naming", "Organize isso com nomes consistentes e estrutura clara.", "engineering", expectation="recuperar preferencia estrutural"),
    BenchmarkCase("precision", "Nao invente. Confirme no codigo antes.", "engineering", expectation="recuperar verificacao"),
    BenchmarkCase("handoff", "Deixa isso preparado para outra IA continuar.", "continuity", expectation="recuperar independencia e handoff"),
    BenchmarkCase("visual_photo", "Essa imagem esta artificial, deixa mais natural.", "design", "image", expectation="recuperar criterios visuais"),
    BenchmarkCase("visual_consistency", "Desktop e mobile ficaram diferentes demais.", "design", "ui_screen", expectation="recuperar consistencia responsiva"),
    BenchmarkCase("visual_spacing", "Revise contraste, espacamento e hierarquia.", "design", "ui_screen", expectation="recuperar quality bar"),
    BenchmarkCase("visual_refine", "Nao gostei do primeiro resultado, use o que eu corrigi.", "design", "website", expectation="usar feedback e failure memory"),
    BenchmarkCase("repo_safe", "Implemente sem quebrar as funcoes existentes.", "engineering", expectation="preservar regressao zero"),
    BenchmarkCase("repo_tests", "Rode os testes e prove que ficou funcionando.", "engineering", expectation="usar proof of work"),
    BenchmarkCase("architecture", "Estruture isso de ponta a ponta sem criar modulo duplicado.", "engineering", expectation="recuperar preferencia arquitetural"),
    BenchmarkCase("research_first", "Nao chute, pesquise e valide antes de decidir.", "working_style", expectation="recuperar verificacao"),
    BenchmarkCase("concise_exec", "Me da o necessario e executa, sem enrolacao.", "working_style", expectation="recuperar estilo de colaboracao"),
    BenchmarkCase("preserve_history", "Nao perca as decisoes que ja tomamos.", "continuity", expectation="recuperar historico"),
    BenchmarkCase("compare_versions", "Compare a versao ruim com a aprovada e aprenda o que mudou.", "feedback", expectation="usar outcome learning"),
    BenchmarkCase("avoid_repeat", "Isso ja deu errado antes, nao repita o mesmo erro.", "feedback", expectation="usar failure memory"),
)


class PersonalBenchmarkSuite:
    def __init__(self, hub: PersonalizationHub | None = None) -> None:
        self.hub = hub or PersonalizationHub()

    def run_context_only(self) -> dict[str, Any]:
        cases = []
        covered = 0
        for case in DEFAULT_CASES:
            context = self.hub.graph.query(
                case.query,
                project_id=case.project_id,
                domain=case.domain,
                artifact_kind=case.artifact_kind,
                limit=5,
            )
            case_covered = bool(context)
            covered += int(case_covered)
            cases.append({
                **case.to_dict(),
                "covered": case_covered,
                "retrieved": [
                    {
                        "subject": node.get("subject"),
                        "scope": node.get("scope"),
                        "score": node.get("retrieval_score"),
                    }
                    for node in context
                ],
            })
        total = len(DEFAULT_CASES)
        return {
            "mode": "context_only",
            "total_cases": total,
            "covered_cases": covered,
            "coverage_percent": round((covered / total) * 100, 1) if total else 0.0,
            "cases": cases,
        }

    def catalog(self) -> list[dict[str, Any]]:
        return [case.to_dict() for case in DEFAULT_CASES]
