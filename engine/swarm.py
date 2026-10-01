"""
ThSyr Ultron Swarm & Autonomous Subagent Orchestrator
Implementa a arquitetura de enxame distribuido do ThSyr inspirada no arquetipo Ultron:
- SystemsEngineer: Auditoria de infraestrutura, silicio, processos e sentinela de workspaces.
- CompilerArchitect: Analise de sintaxe, AST, sanidade de codigo e motor TokLang.
- CognitiveArchitect: Auditoria ontologica do cerebro, conformidade pre-frontal e grafo neural.
- UltronSwarm: Orquestrador unificado de convergencia e sintese executiva.
"""

import ast
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from .config import settings, setup_logger
from .host_telemetry import HostTelemetryObserver
from .workspace_observer import WorkspaceObserver

logger = setup_logger("ultron_swarm")


class SubagentStatus(str, Enum):
    OPTIMAL = "OPTIMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class SubagentRole(str, Enum):
    SYSTEMS_ENGINEER = "systems_engineer"
    COMPILER_ARCHITECT = "compiler_architect"
    COGNITIVE_ARCHITECT = "cognitive_architect"


@dataclass
class SubagentReport:
    role: str
    name: str
    status: SubagentStatus
    diagnostics: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d


@dataclass
class SwarmReport:
    overall_status: SubagentStatus
    timestamp: str
    reports: dict[str, SubagentReport]
    summary_lines: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall_status": self.overall_status.value,
            "timestamp": self.timestamp,
            "summary_lines": self.summary_lines,
            "subagents": {k: v.to_dict() for k, v in self.reports.items()}
        }

    def render_markdown(self) -> str:
        lines = [
            "==================================================",
            "        THSYR // ULTRON SWARM CONVERGENCE         ",
            "==================================================",
            f"Status do Enxame:    {self.overall_status.value}",
            f"Timestamp:           {self.timestamp}",
            "--------------------------------------------------"
        ]
        for line in self.summary_lines:
            lines.append(f"• {line}")

        lines.append("--------------------------------------------------")
        for role, rep in self.reports.items():
            lines.append(f"[{rep.name}] ({role.upper()}) -> Status: {rep.status.value}")
            for diag in rep.diagnostics:
                lines.append(f"   - {diag}")
            if rep.recommendations:
                for rec in rep.recommendations:
                    lines.append(f"   * Acao Recomendada: {rec}")
            lines.append("")

        lines.append("==================================================")
        return "\n".join(lines)


class BaseSubagent:
    """Contrato base para qualquer subagente operacional do enxame."""
    role: SubagentRole
    name: str

    def execute(self) -> SubagentReport:
        raise NotImplementedError


class SystemsEngineerSubagent(BaseSubagent):
    """
    Subagente SystemsEngineer:
    Inspeciona silicio, telemetria de hardware, sentinela de workspaces e saude de processos.
    """
    role = SubagentRole.SYSTEMS_ENGINEER
    name = "Systems Engineer (Sentry Alpha)"

    def __init__(
        self,
        telemetry_observer: HostTelemetryObserver | None = None,
        workspace_observer: WorkspaceObserver | None = None
    ):
        self.telemetry = telemetry_observer or HostTelemetryObserver()
        self.workspaces = workspace_observer or WorkspaceObserver()

    def execute(self) -> SubagentReport:
        diagnostics: list[str] = []
        recommendations: list[str] = []
        status = SubagentStatus.OPTIMAL

        # 1. Telemetria de Silicio
        telem = self.telemetry.get_telemetry()
        cpu = telem.get("cpu", {})
        ram = telem.get("ram", {})
        disk = telem.get("disk", {})

        diagnostics.append(
            f"Silicio: CPU {cpu.get('usage_percent', 0)}% ({cpu.get('cores_logical', 1)} cores) | "
            f"RAM {ram.get('used_gb', 0)}/{ram.get('total_gb', 0)} GB ({ram.get('percent', 0)}%) | "
            f"Disco {disk.get('used_gb', 0)}/{disk.get('total_gb', 0)} GB ({disk.get('percent', 0)}%)"
        )

        if ram.get("percent", 0) > 85.0:
            status = SubagentStatus.WARNING
            diagnostics.append("Alerta de pressao em RAM: utilizacao acima de 85%")
            recommendations.append("Purgar processos zumbis e otimizar buffers de memoria")

        if disk.get("percent", 0) > 90.0:
            status = SubagentStatus.WARNING
            diagnostics.append("Alerta de espaco em disco: utilizacao acima de 90%")
            recommendations.append("Limpar caches em .cache e artefatos de build temporarios")

        # 2. Sentinela de Workspaces Git
        ws_data = self.workspaces.scan()
        dirty = ws_data.get("dirty_count", 0)
        ahead = ws_data.get("ahead_count", 0)
        total_ws = ws_data.get("total_workspaces", 0)

        diagnostics.append(
            f"Workspaces: {total_ws} repositorios monitorados | {dirty} modificados | {ahead} pendentes de push"
        )

        if dirty > 0:
            if status != SubagentStatus.CRITICAL:
                status = SubagentStatus.WARNING
            diagnostics.append(f"Risco de perda de codigo: {dirty} workspaces com arvores de trabalho sujas")
            recommendations.append("Consolidar checkpoints git ou executar stash em repositorios pendentes")

        if ahead > 0:
            recommendations.append(f"Executar git push em {ahead} repositorios com commits locais pendentes")

        return SubagentReport(
            role=self.role.value,
            name=self.name,
            status=status,
            diagnostics=diagnostics,
            metrics={"telemetry": telem, "workspaces": ws_data},
            recommendations=recommendations
        )


class CompilerArchitectSubagent(BaseSubagent):
    """
    Subagente CompilerArchitect:
    Analisa sintaxe Python, integridade de AST, robustez do motor TokLang e detecta estagios frageis.
    """
    role = SubagentRole.COMPILER_ARCHITECT
    name = "Compiler Architect (Sentry Beta)"

    def __init__(self, repo_root: Path | None = None):
        self.repo_root = repo_root or settings.project_root

    def _audit_python_syntax(self) -> tuple[int, list[str]]:
        """Verifica sintaxe AST de todos os arquivos python sob engine/ e tests/."""
        valid_count = 0
        errors = []
        target_dirs = [self.repo_root / "engine", self.repo_root / "tests"]

        for target in target_dirs:
            if not target.exists():
                continue
            for py_file in target.rglob("*.py"):
                try:
                    code = py_file.read_text(encoding="utf-8", errors="replace")
                    ast.parse(code, filename=str(py_file))
                    valid_count += 1
                except SyntaxError as se:
                    errors.append(f"SyntaxError em {py_file.relative_to(self.repo_root)}: linha {se.lineno}")
                except Exception as e:
                    errors.append(f"Erro ao parsear {py_file.relative_to(self.repo_root)}: {e}")

        return valid_count, errors

    def _verify_toklang_core(self) -> dict[str, Any]:
        """Testa o nucleo do TokLang (lexer, parser e estimador)."""
        res: dict[str, Any] = {"operational": False, "contexts_parsed": 0, "flops_reduction": 0.0}
        try:
            from .toklang.estimator import CompressionEstimator
            from .toklang.lexer import TokLangLexer
            from .toklang.parser import TokLangParser

            sample_code = '''
            @compress(level="aggressive")
            @budget(max_tokens=500)
            context "system" {
                Reasoning flow architecture.
            }
            instruction {
                "Audit infrastructure"
            }
            '''
            lexer = TokLangLexer(sample_code)
            tokens = lexer.tokenize()
            parser = TokLangParser(tokens)
            ast_root = parser.parse()
            metrics = CompressionEstimator.estimate_metrics(sample_code, ast_root)

            res["operational"] = True
            res["contexts_parsed"] = len(getattr(ast_root, "contexts", []))
            res["flops_reduction"] = metrics.get("attention_flops_reduction_percent", 0.0)
        except Exception as e:
            res["error"] = str(e)

        return res

    def execute(self) -> SubagentReport:
        diagnostics: list[str] = []
        recommendations: list[str] = []
        status = SubagentStatus.OPTIMAL

        # 1. Auditoria AST Python
        valid_files, errors = self._audit_python_syntax()
        diagnostics.append(f"Auditoria AST: {valid_files} arquivos Python validados com sintaxe integra")

        if errors:
            status = SubagentStatus.CRITICAL
            diagnostics.append(f"Falha critica de compilacao: {len(errors)} erros de sintaxe detectados")
            for err in errors[:3]:
                diagnostics.append(f"   -> {err}")
            recommendations.append("Corrigir erros de sintaxe nos arquivos reportados antes do proximo commit")

        # 2. Verificacao TokLang
        toklang_res = self._verify_toklang_core()
        if toklang_res.get("operational"):
            diagnostics.append("Motor TokLang: Lexer, Parser e Estimador de FLOPs operacionais (AST validada)")
        else:
            status = SubagentStatus.WARNING
            diagnostics.append(f"Motor TokLang com degradacao: {toklang_res.get('error', 'desconhecido')}")
            recommendations.append("Inspecionar implementacao de engine/toklang/ e atualizar gramatica")

        return SubagentReport(
            role=self.role.value,
            name=self.name,
            status=status,
            diagnostics=diagnostics,
            metrics={"python_files_validated": valid_files, "toklang": toklang_res},
            recommendations=recommendations
        )


class CognitiveArchitectSubagent(BaseSubagent):
    """
    Subagente CognitiveArchitect:
    Audita integridade ontologica do hipocampo, conformidade pre-frontal e grafo neural.
    """
    role = SubagentRole.COGNITIVE_ARCHITECT
    name = "Cognitive Architect (Sentry Gamma)"

    # Regex para deteccao de emojis em textos e commits (Portao Pre-Frontal)
    EMOJI_PATTERN = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Simbolos e pictogramas
        "\U0001F680-\U0001F6FF"  # Transporte e mapas
        "\U0001F1E0-\U0001F1FF"  # Bandeiras
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )

    def __init__(self, brain_dir: Path | None = None):
        self.brain_dir = brain_dir or settings.brain.brain_dir

    def _check_vital_nodes(self) -> tuple[list[str], list[str]]:
        """Verifica existencia de nodulos vitais de governanca e memoria."""
        vital_files = [
            self.brain_dir / "core" / "personality.md",
            self.brain_dir / "core" / "directives.json",
            self.brain_dir / "profile" / "user.md",
            self.brain_dir / "profile" / "psychological_dossier.md",
            self.brain_dir / "session_handoff.md"
        ]
        present = []
        missing = []
        for vf in vital_files:
            if vf.exists():
                present.append(vf.name)
            else:
                missing.append(vf.name)
        return present, missing

    def _audit_prefrontal_hygiene(self) -> list[str]:
        """Audita arquivos cerebrais vitais em busca de violacao da regra zero emojis."""
        violations = []
        core_dir = self.brain_dir / "core"
        profile_dir = self.brain_dir / "profile"

        for directory in [core_dir, profile_dir]:
            if not directory.exists():
                continue
            for file_path in directory.glob("*.md"):
                try:
                    text = file_path.read_text(encoding="utf-8", errors="replace")
                    if self.EMOJI_PATTERN.search(text):
                        violations.append(f"Emoji detectado em {file_path.name}")
                except Exception:
                    pass
        return violations

    def _inspect_graph_stats(self) -> dict[str, Any]:
        """Le estatisticas do grafo de conhecimento em brain/knowledge_graph.json."""
        kg_path = self.brain_dir / "knowledge_graph.json"
        if not kg_path.exists():
            return {"total_nodes": 0, "total_edges": 0}
        try:
            import json
            data = json.loads(kg_path.read_text(encoding="utf-8"))
            return {
                "total_nodes": data.get("total_nodes", len(data.get("nodes", []))),
                "total_edges": data.get("total_edges", len(data.get("edges", []))),
                "version": data.get("version", "1.0.0")
            }
        except Exception:
            return {"total_nodes": 0, "total_edges": 0}

    def execute(self) -> SubagentReport:
        diagnostics: list[str] = []
        recommendations: list[str] = []
        status = SubagentStatus.OPTIMAL

        # 1. Checagem de nodulos vitais
        present, missing = self._check_vital_nodes()
        diagnostics.append(f"Nodulos Vitais: {len(present)}/{len(present) + len(missing)} ativos no cerebro")

        if missing:
            status = SubagentStatus.CRITICAL
            diagnostics.append(f"Nodulos ausentes no cortex: {', '.join(missing)}")
            recommendations.append("Regenerar nodulos vitais de personalidade e perfil do operador")

        # 2. Higiene Pre-Frontal (Zero Emojis)
        emoji_violations = self._audit_prefrontal_hygiene()
        if emoji_violations:
            status = SubagentStatus.WARNING
            diagnostics.append(f"Violacao de higiene pre-frontal: {len(emoji_violations)} arquivos com emojis")
            for viol in emoji_violations[:3]:
                diagnostics.append(f"   -> {viol}")
            recommendations.append("Sanear arquivos e expurgar caracteres graficos nao autorizados")
        else:
            diagnostics.append("Higiene Pre-Frontal: Zero emojis em conformidade estrita com o Protocolo Master")

        # 3. Topologia do Grafo
        graph_stats = self._inspect_graph_stats()
        nodes = graph_stats.get("total_nodes", 0)
        edges = graph_stats.get("total_edges", 0)
        diagnostics.append(f"Topologia Neural: {nodes} nos cognitivos e {edges} sinapses mapeadas")

        if nodes < 50:
            status = SubagentStatus.WARNING
            recommendations.append("Executar reindexacao do grafo neural via python thsyr.py graph")

        return SubagentReport(
            role=self.role.value,
            name=self.name,
            status=status,
            diagnostics=diagnostics,
            metrics={"graph": graph_stats, "vital_nodes_present": len(present)},
            recommendations=recommendations
        )


class UltronSwarm:
    """
    Orquestrador Mestre do Enxame Ultron (ThSyr Swarm).
    Coordena os subagentes especializados, unifica diagnosticos e sintetiza relatorio sagital.
    """

    def __init__(
        self,
        systems_engineer: SystemsEngineerSubagent | None = None,
        compiler_architect: CompilerArchitectSubagent | None = None,
        cognitive_architect: CognitiveArchitectSubagent | None = None
    ):
        self.systems = systems_engineer or SystemsEngineerSubagent()
        self.compiler = compiler_architect or CompilerArchitectSubagent()
        self.cognitive = cognitive_architect or CognitiveArchitectSubagent()

        self._agents: dict[str, BaseSubagent] = {
            SubagentRole.SYSTEMS_ENGINEER.value: self.systems,
            SubagentRole.COMPILER_ARCHITECT.value: self.compiler,
            SubagentRole.COGNITIVE_ARCHITECT.value: self.cognitive
        }

    def dispatch(self, role: SubagentRole | str) -> SubagentReport:
        """Dispara um unico subagente por papel."""
        role_str = role.value if isinstance(role, SubagentRole) else str(role)
        agent = self._agents.get(role_str)
        if not agent:
            raise ValueError(f"Subagente com papel '{role_str}' nao registrado no enxame.")
        logger.info(f"Disparando subagente autônomo: {agent.name}")
        return agent.execute()

    def converge(self) -> SwarmReport:
        """
        Dispara todos os subagentes do enxame e consolida a matriz executiva.
        """
        logger.info("Iniciando ciclo de convergencia do Enxame Ultron...")
        reports: dict[str, SubagentReport] = {}
        summary_lines: list[str] = []

        overall_status = SubagentStatus.OPTIMAL

        for role_key, agent in self._agents.items():
            rep = agent.execute()
            reports[role_key] = rep

            if rep.status == SubagentStatus.CRITICAL:
                overall_status = SubagentStatus.CRITICAL
                summary_lines.append(f"FALHA CRITICA em {rep.name}")
            elif rep.status == SubagentStatus.WARNING and overall_status != SubagentStatus.CRITICAL:
                overall_status = SubagentStatus.WARNING
                summary_lines.append(f"Atencao operacional requerida em {rep.name}")

        if overall_status == SubagentStatus.OPTIMAL:
            summary_lines.append("Todos os subsistemas operando em paridade e estabilidade absoluta.")

        report = SwarmReport(
            overall_status=overall_status,
            timestamp=datetime.now(timezone.utc).isoformat(),
            reports=reports,
            summary_lines=summary_lines
        )
        logger.info(f"Convergencia concluida. Status geral: {overall_status.value}")
        return report
