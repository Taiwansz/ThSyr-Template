"""
Orquestrador do ThSyr Visual Studio.

Fluxo:
brief -> personalizacao -> failure memory -> design tournament -> construcao
externa -> render real -> critica visual -> refinamento -> gate -> outcome
learning.
"""

import json
from pathlib import Path
from typing import Any, Callable

from ..personalization.hub import PersonalizationHub
from ..personalization.preference_graph import PreferenceScope
from .archetypes import get_niche_preset
from .behance_intelligence import get_behance_intelligence_for_branch
from .contracts import VisualArtifactKind, VisualBrief
from .critic import VisualCritic
from .failure_memory import VisualFailureMemory
from .refinement_loop import VisualRefinementLoop
from .taste_memory import TasteMemory
from .tournament import DesignTournament
from .validator import VisualCraftValidator


class VisualStudio:
    DEFAULT_VIEWPORTS = {
        "desktop": (1440, 900),
        "mobile": (390, 844),
    }

    def __init__(
        self,
        critic: VisualCritic | None = None,
        taste_memory: TasteMemory | None = None,
        validator: VisualCraftValidator | None = None,
        personalization: PersonalizationHub | None = None,
        failure_memory: VisualFailureMemory | None = None,
        tournament: DesignTournament | None = None,
    ):
        self.critic = critic or VisualCritic()
        self.taste_memory = taste_memory or TasteMemory()
        self.validator = validator or VisualCraftValidator()
        self.personalization = personalization or PersonalizationHub()
        self.failure_memory = failure_memory or VisualFailureMemory()
        self.tournament = tournament or DesignTournament(
            gateway=self.critic.gateway,
            critic=self.critic,
        )

    def _sync_taste_memory(self, brief: VisualBrief) -> int:
        synced = 0
        for entry in self.taste_memory.entries_for(brief.artifact_kind.value, limit=50):
            subject = entry.get("notes") or entry.get("reference")
            if not subject:
                continue
            result = self.personalization.graph.upsert(
                category="visual_preference",
                subject=str(subject),
                stance="positive" if entry.get("verdict") == "approved" else "negative",
                confidence=0.93,
                status="confirmed",
                source="taste_memory",
                scope=PreferenceScope.DOMAIN,
                domain=brief.domain,
                artifact_kind=brief.artifact_kind.value,
                evidence=str(entry.get("reference", "")),
            )
            synced += int(bool(result.get("recorded")))
        return synced

    def prepare_direction(
        self,
        brief: VisualBrief,
        *,
        tournament_count: int = 3,
    ) -> dict[str, Any]:
        taste_sync_count = self._sync_taste_memory(brief)
        niche_query = brief.niche or brief.objective
        niche = get_niche_preset(niche_query)
        commerce = get_behance_intelligence_for_branch(niche_query)
        taste = self.taste_memory.build_context(brief.artifact_kind.value)
        personalization = self.personalization.build_context(
            brief.objective,
            project_id=brief.project_id,
            domain=brief.domain,
            artifact_kind=brief.artifact_kind.value,
        )
        failures = self.failure_memory.build_context(
            project_id=brief.project_id,
            artifact_kind=brief.artifact_kind.value,
        )
        tournament = self.tournament.generate(
            brief,
            personalization_context=personalization,
            failure_context=failures,
            count=tournament_count,
        )

        contract = self._build_generation_contract(
            brief,
            niche=niche,
            commerce=commerce,
            taste=taste,
            personalization=personalization,
            failures=failures,
            tournament=tournament,
        )
        return {
            "brief": brief.to_dict(),
            "niche_direction": niche,
            "commerce_direction": commerce,
            "taste_context": taste,
            "taste_graph_sync_count": taste_sync_count,
            "personalization_context": personalization,
            "failure_context": failures,
            "tournament": tournament,
            "generation_contract": contract,
        }

    def _build_generation_contract(
        self,
        brief: VisualBrief,
        niche: dict[str, Any],
        commerce: dict[str, Any],
        taste: str,
        personalization: str,
        failures: str,
        tournament: dict[str, Any],
    ) -> str:
        anti_slop = niche.get("anti_slop_rules", [])
        brand_rules = brief.brand_constraints + brief.must_avoid
        references = brief.references or ["Nenhuma referencia explicita fornecida."]
        tournament_lines = []
        directions = tournament.get("directions", [])
        if directions:
            tournament_lines = [
                "DESIGN TOURNAMENT - DIRECOES CANDIDATAS:",
                *[
                    (
                        f"- {item.get('id')}: {item.get('name')} | tese={item.get('thesis')} | "
                        f"composicao={item.get('composition')} | tipografia={item.get('typography')} | "
                        f"imagem={item.get('imagery')} | anti-template={item.get('anti_template_move')}"
                    )
                    for item in directions
                ],
                (
                    "Antes de desenvolver a pagina inteira, materialize mini-renders das direcoes "
                    "candidatas e submeta ao tournament review. Nao escolha por conveniencia."
                ),
                "",
            ]

        return "\n".join([
            "THSYR VISUAL GENERATION CONTRACT",
            "",
            f"OBJETIVO: {brief.objective}",
            f"TIPO: {brief.artifact_kind.value}",
            f"PROJETO: {brief.project_id or 'nao informado'}",
            f"PUBLICO: {brief.audience or 'inferir do objetivo sem inventar fatos de marca'}",
            f"IMPRESSAO DESEJADA: {brief.desired_impression or 'profissional, especifica e nao-generica'}",
            "",
            "DIRECAO DO NICHO:",
            json.dumps({
                "name": niche.get("name"),
                "benchmarks": niche.get("benchmarks"),
                "fonts": niche.get("fonts"),
                "palette": niche.get("palette"),
                "spatial_composition": niche.get("spatial_composition"),
                "marketing_heuristics": niche.get("marketing_heuristics"),
            }, ensure_ascii=False, indent=2),
            "",
            "INTELIGENCIA DE RAMO:",
            json.dumps(commerce, ensure_ascii=False, indent=2),
            "",
            "REFERENCIAS EXPLICITAS:",
            *[f"- {ref}" for ref in references],
            "",
            "REGRAS DE MARCA E VETOS:",
            *[f"- {rule}" for rule in (brand_rules or ["Sem restricao adicional registrada."])],
            "",
            "ANTI-SLOP:",
            *[f"- {rule}" for rule in anti_slop],
            "",
            personalization,
            "",
            taste,
            "",
            failures,
            "",
            *tournament_lines,
            "PROCESSO OBRIGATORIO:",
            "1. Formular direcoes visuais realmente distintas; nao pequenas variacoes do mesmo template.",
            "2. Quando o tournament estiver disponivel, renderizar conceitos enxutos e selecionar somente por evidencia visual.",
            "3. Construir com assets coerentes com a direcao vencedora. Placeholder generico nao conta como acabamento.",
            "4. Renderizar o resultado real.",
            "5. Submeter desktop e mobile ao VisualCritic quando aplicavel.",
            "6. Corrigir issues blocker e major; nao maquiar sintomas.",
            "7. Repetir renderizacao e critica ate o gate passar ou atingir 4 iteracoes.",
            "8. Se nao houver visao real disponivel, declarar o gate inconclusivo. Nunca autoaprovar.",
            "9. Uma rejeicao humana deve alimentar TasteMemory, FailureMemory e PreferenceGraph.",
            "10. Uma versao aprovada depois de uma rejeitada deve registrar o delta no Outcome Learning.",
            "",
            f"GATE: score geral >= {brief.minimum_score}, cada dimensao >= {brief.minimum_dimension_score}, zero blocker.",
        ])

    def review(
        self,
        target: str | Path,
        brief: VisualBrief,
        output_dir: str | Path = ".thsyr/visual-review",
    ) -> dict[str, Any]:
        target_str = str(target)
        target_path = Path(target_str)
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        static_audit: dict[str, Any] | None = None
        critiques = []
        rendered_assets: dict[str, str] = {}

        is_web = brief.artifact_kind in {VisualArtifactKind.WEBSITE, VisualArtifactKind.UI_SCREEN}
        if is_web:
            if target_path.is_file() and target_path.suffix.lower() in {".html", ".htm"}:
                static_audit = self.validator.audit_file(target_path)

            from .screenshot import capture_screenshot

            for viewport, (width, height) in self.DEFAULT_VIEWPORTS.items():
                shot = out_dir / f"{viewport}.png"
                capture_screenshot(target, shot, width=width, height=height, full_page=False)
                rendered_assets[viewport] = str(shot.resolve())
                critiques.append(self.critic.critique(shot, brief, viewport=viewport))
        else:
            if not target_path.is_file():
                raise FileNotFoundError(f"Artefato visual nao encontrado: {target_path}")
            rendered_assets["asset"] = str(target_path.resolve())
            critiques.append(self.critic.critique(target_path, brief, viewport="asset"))

        static_passed = static_audit is None or bool(static_audit.get("passed"))
        vision_passed = bool(critiques) and all(c.passed for c in critiques)
        passed = static_passed and vision_passed

        report = {
            "passed": passed,
            "static_audit": static_audit,
            "rendered_assets": rendered_assets,
            "critiques": [c.to_dict() for c in critiques],
        }
        report["refinement_prompt"] = self.build_refinement_prompt(report, brief)

        if not passed:
            report["failure_patterns_recorded"] = self.failure_memory.ingest_report(
                report,
                project_id=brief.project_id,
                artifact_kind=brief.artifact_kind.value,
            )
        else:
            report["failure_patterns_recorded"] = 0
        return report

    def record_feedback(
        self,
        brief: VisualBrief,
        *,
        verdict: str,
        reference: str,
        notes: str = "",
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        if verdict not in {"approved", "rejected"}:
            raise ValueError("verdict deve ser approved ou rejected")
        taste = self.taste_memory.record(
            verdict=verdict,
            artifact_kind=brief.artifact_kind.value,
            reference=reference,
            notes=notes,
            tags=tags,
        )
        personalization = self.personalization.record_preference(
            subject=notes or reference,
            verdict=verdict,
            reason=f"visual feedback: {reference}",
            category="visual_preference",
            project_id=brief.project_id,
            domain=brief.domain,
            artifact_kind=brief.artifact_kind.value,
            source="visual_feedback",
        )
        failure = None
        if verdict == "rejected":
            failure = self.failure_memory.record_human_rejection(
                notes or reference,
                project_id=brief.project_id,
                artifact_kind=brief.artifact_kind.value,
            )
        return {
            "taste": taste.to_dict(),
            "personalization": personalization,
            "failure": failure,
        }

    def begin_outcome(self, brief: VisualBrief) -> str:
        return self.personalization.outcomes.begin(
            brief.objective,
            project_id=brief.project_id,
            domain=brief.domain,
            artifact_kind=brief.artifact_kind.value,
        )

    def record_outcome_version(
        self,
        outcome_id: str,
        *,
        label: str,
        artifact_ref: str,
        verdict: str = "unknown",
        review_report: dict[str, Any] | None = None,
        note: str = "",
    ) -> dict[str, Any]:
        return self.personalization.outcomes.record_version(
            outcome_id,
            label=label,
            artifact_ref=artifact_ref,
            verdict=verdict,
            review_report=review_report,
            note=note,
        )

    def resolve_outcome(
        self,
        outcome_id: str,
        *,
        rejected_label: str,
        approved_label: str,
        note: str = "",
    ) -> dict[str, Any]:
        return self.personalization.learn_outcome_resolution(
            outcome_id,
            rejected_label=rejected_label,
            approved_label=approved_label,
            note=note,
        )

    def review_tournament(
        self,
        brief: VisualBrief,
        renders: dict[str, str | Path],
    ) -> dict[str, Any]:
        return self.tournament.review_renders(brief, renders)

    def run_refinement_loop(
        self,
        brief: VisualBrief,
        *,
        executor: Callable[[str, int], Any],
        target_resolver: Callable[[int], str | Path],
        max_iterations: int = 4,
        output_root: str | Path = ".thsyr/visual-refinement",
    ) -> dict[str, Any]:
        prepared = self.prepare_direction(brief)
        loop = VisualRefinementLoop(self, max_iterations=max_iterations)
        return loop.run(
            brief=brief,
            initial_instruction=prepared["generation_contract"],
            executor=executor,
            target_resolver=target_resolver,
            output_root=output_root,
        )

    @staticmethod
    def build_refinement_prompt(report: dict[str, Any], brief: VisualBrief) -> str:
        issues: list[dict[str, Any]] = []
        for critique in report.get("critiques", []):
            issues.extend(critique.get("issues", []))

        static = report.get("static_audit") or {}
        static_errors = static.get("errors", [])
        static_warnings = static.get("warnings", [])

        lines = [
            "REFINAMENTO VISUAL OBRIGATORIO",
            f"Objetivo original: {brief.objective}",
            "Nao reescreva o projeto inteiro sem necessidade. Corrija causa raiz e preserve o que ja funciona.",
            "",
            "ISSUES DE VISAO:",
        ]
        if issues:
            for issue in issues:
                lines.append(
                    f"- [{issue.get('severity', 'major')}] {issue.get('category', 'visual')}: "
                    f"{issue.get('problem')} | evidencia: {issue.get('evidence')} | correcao: {issue.get('fix')}"
                )
        else:
            lines.append("- Nenhum issue visual retornado.")

        lines.extend(["", "ISSUES ESTATICOS:"])
        for item in [*static_errors, *static_warnings]:
            lines.append(f"- {item}")
        if not static_errors and not static_warnings:
            lines.append("- Nenhum issue estatico.")

        lines.extend([
            "",
            "Apos corrigir: renderize novamente, rode a critica em desktop/mobile e so finalize se o gate passar.",
            "Se o operador rejeitar o resultado, registre a causa na memoria de falhas antes da proxima tentativa.",
        ])
        return "\n".join(lines)
