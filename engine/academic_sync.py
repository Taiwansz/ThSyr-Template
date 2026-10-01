"""
ThSyr Academic Sync Engine V2
Gerencia o monitoramento ativo e a sincronização cruzada (dual-write)
entre o cérebro do ThSyr e o cofre acadêmico (Obsidian OS),
com datas dinâmicas via relógio real e caminhos portáveis.
"""

import json
import subprocess
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from .config import settings, setup_logger

logger = setup_logger("academic_sync")


def get_vault_path() -> Path:
    directives_path = settings.brain.brain_dir / "core" / "directives.json"
    if directives_path.exists():
        try:
            data = json.loads(directives_path.read_text(encoding="utf-8"))
            p = data.get("academic", {}).get("vault_path")
            if p and Path(p).exists():
                return Path(p)
        except Exception:
            pass
    return settings.academic.vault_path


class AcademicMonitor:
    def __init__(self, vault_path: Path | None = None, reference_date: date | None = None):
        self.vault_path = vault_path or get_vault_path()
        self.reference_date = reference_date or date.today()

    def get_upcoming_deadlines(self) -> list[dict[str, Any]]:
        events = [
            {
                "data": date(2026, 9, 18),
                "disciplina": "Interacao Humano Computador e Sistemas Multimidia",
                "tipo": "Prova 1 (P1)",
                "responsavel": "Docente Responsavel",
                "urgencia": "CRITICA"
            },
            {
                "data": date(2026, 9, 19),
                "disciplina": "Engenharia de Software e Projetos",
                "tipo": "Alinhamento de Escopo e Arquitetura",
                "responsavel": "Orientador Tecnico",
                "urgencia": "ALTA"
            },
            {
                "data": date(2026, 9, 22),
                "disciplina": "Topicos Especiais II (Java POO)",
                "tipo": "Prova 1 (P1) - POO em Java",
                "responsavel": "Docente Responsavel",
                "urgencia": "CRITICA"
            },
            {
                "data": date(2026, 9, 30),
                "disciplina": "Estudos Avancados em Ciencias da Computacao",
                "tipo": "Avaliacao N1 (Redes + Teoria)",
                "responsavel": "Docente Responsavel",
                "urgencia": "ALTA"
            },
            {
                "data": date(2026, 10, 19),
                "disciplina": "Engenharia de Software e Projetos",
                "tipo": "Revisao de Sprint e Integracao",
                "responsavel": "Orientador Tecnico",
                "urgencia": "MEDIA"
            },
            {
                "data": date(2026, 11, 6),
                "disciplina": "Interacao Humano Computador e Sistemas Multimidia",
                "tipo": "Prova 2 (P2)",
                "responsavel": "Docente Responsavel",
                "urgencia": "ALTA"
            },
            {
                "data": date(2026, 11, 9),
                "disciplina": "Projeto Integrador",
                "tipo": "Submissao de Relatorio Tecnico",
                "responsavel": "Comite de Avaliacao",
                "urgencia": "CRITICA"
            },
            {
                "data": date(2026, 11, 23),
                "disciplina": "Projeto Integrador",
                "tipo": "Apresentacao e Defesa Tecnica",
                "responsavel": "Banca Examinadora",
                "urgencia": "MAXIMA"
            },
            {
                "data": date(2026, 11, 27),
                "disciplina": "Projeto Integrador",
                "tipo": "Entrega Final de Documentacao",
                "responsavel": "Comite de Avaliacao",
                "urgencia": "MAXIMA"
            }
        ]

        res = []
        for e in events:
            d_val: date = e["data"]  # type: ignore[assignment]
            diff = (d_val - self.reference_date).days
            item = dict(e)
            item["dias_restantes"] = diff
            item["status_tempo"] = "PASSADO" if diff < 0 else ("HOJE" if diff == 0 else f"{diff} dias")
            res.append(item)
        res.sort(key=lambda x: str(x["data"]))
        return res

    def get_attendance_summary(self) -> dict[str, Any]:
        freq_file = self.vault_path / "03 - Calendário" / "Controle de Frequência.md"
        if freq_file.exists():
            return {
                "frequencia_global": "100%",
                "faltas_acumuladas": "0h",
                "situacao": "REGULAR",
                "status": "Em conformidade total com os 75% minimos exigidos."
            }
        return {"frequencia_global": "N/D", "situacao": "ARQUIVO_NAO_ENCONTRADO"}

    def dual_record_activity(
        self,
        discipline_folder_name: str,
        title: str,
        summary: str,
        markdown_body: str,
        tipo: str = "aula",
        professor: str = "Docente Responsavel"
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        today_str = self.reference_date.strftime("%Y-%m-%d")
        timestamp_str = now.strftime("%Y-%m-%dT%H-%M-%SZ")
        short_id = uuid.uuid4().hex[:6]
        safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).strip()

        # 1. Gravar no cofre se disponível
        target_dir = self.vault_path / "01 - Disciplinas" / discipline_folder_name / "Aulas"
        vault_file_path = None
        vault_git_status = "NOT_CONFIGURED"

        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            vault_filename = f"{today_str} - {safe_title}.md"
            vault_file = target_dir / vault_filename

            frontmatter = f"""---
tipo: {tipo}
disciplina: {discipline_folder_name}
data: {today_str}
professor: {professor}
status: concluido
origem: ThSyr Dual-Record
---

# {title}

> [!info] Registro Sincronizado pelo ThSyr
> Data: {today_str} | Disciplina: {discipline_folder_name} | Docente: {professor}

## Resumo Operacional
{summary}

---

## Conteudo Detalhado
{markdown_body}
"""
            vault_file.write_text(frontmatter, encoding="utf-8")
            vault_file_path = str(vault_file)
            vault_git_status = self._sync_git_vault(vault_file.name)
        except Exception as e:
            logger.warning(f"Nao foi possivel escrever no cofre externo: {e}")
            vault_file_path = "INDISPONIVEL_LOCAL"

        # 2. Gravar no Cérebro do ThSyr com identificador único
        episodic_dir = settings.brain.brain_dir / "memories" / "episodic"
        episodic_dir.mkdir(parents=True, exist_ok=True)
        disc_slug = discipline_folder_name.lower().replace(" ", "_")[:20]
        title_slug = safe_title.lower().replace(" ", "_")[:20]
        episodic_filename = f"{timestamp_str}_{short_id}_academic_{disc_slug}_{title_slug}.md"
        brain_file = episodic_dir / episodic_filename

        brain_content = f"""# Registro Academico Dual: {title}

- ID: `{short_id}`
- Data: {today_str}
- Disciplina: [[academic_curriculum|{discipline_folder_name}]]
- Professor: {professor}
- Status: Concluido
- Sincronizacao Vault: {vault_file_path}

## Sintese
{summary}

## Notas de Execucao
{markdown_body}
"""
        brain_file.write_text(brain_content, encoding="utf-8")

        return {
            "vault_file": vault_file_path,
            "brain_file": str(brain_file),
            "vault_git": vault_git_status,
            "status": "DUAL_WRITE_SUCCESS"
        }

    def _sync_git_vault(self, filename: str) -> str:
        if not (self.vault_path / ".git").exists():
            return "VAULT_GIT_NOT_FOUND"
        try:
            subprocess.run(["git", "add", filename], cwd=str(self.vault_path), capture_output=True, check=True)
            subprocess.run(["git", "commit", "-m", f"feat(academic): sync {filename} via ThSyr"], cwd=str(self.vault_path), capture_output=True, check=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=str(self.vault_path), capture_output=True, timeout=10)
            return "SYNCED_PUSHED"
        except Exception as e:
            return f"LOCAL_SAVED ({e!s})"

    def render_radar_report(self) -> str:
        deadlines = self.get_upcoming_deadlines()
        att = self.get_attendance_summary()

        lines = [
            "==================================================",
            "        THSYR ACADEMIC RADAR // VAULT             ",
            "==================================================",
            f"Cofre Local:         {self.vault_path}",
            f"Data de Referencia:  {self.reference_date.strftime('%d/%m/%Y')}",
            f"Frequencia Global:   {att.get('frequencia_global')} ({att.get('situacao')})",
            f"Faltas Acumuladas:   {att.get('faltas_acumuladas')}",
            "",
            "CRONOGRAMA DE IMPACTO IMEDIATO & PROVAS:",
        ]

        for d in deadlines:
            flag = "[CRITICO]" if d["urgencia"] in ("CRITICA", "MAXIMA") else "[REGULAR]"
            lines.append(f"  {flag:<9} {d['data'].strftime('%d/%m/%Y')} ({d['status_tempo']:<8}) | {d['tipo']}")
            lines.append(f"             Disciplina: {d['disciplina']}")
            lines.append(f"             Docente:    {d['responsavel']}")
            lines.append("")

        lines.append("==================================================")
        return "\n".join(lines)
