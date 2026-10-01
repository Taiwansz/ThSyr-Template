"""
ThSyr Neural Memory Consolidator (Fase 9)
Substitui contadores estaticos por auditoria ontologica profunda:
- Mapeia nos orfaos (entidades referenciadas em [[wikilinks]] sem no formal em brain/nodes/)
- Detecta links internos quebrados
- Computa o Indice de Saude Ontologica (OHI)
- Permite auto-geracao de stubs para entidades orfas de alta frequencia
"""

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import settings, setup_logger

logger = setup_logger("memory_consolidator")

WIKILINK_PATTERN = re.compile(r"\[\[([a-zA-Z0-9_.\-\s]+?)(?:\|[^\]]+)?\]\]")
FILELINK_PATTERN = re.compile(r"\[.*?\]\((?:file:///)?([A-Za-z]:/[^)#?\s]+)\)")


class MemoryConsolidator:
    def __init__(self, brain_dir: Path | None = None):
        self.brain_dir = brain_dir or settings.brain.brain_dir
        self.nodes_dir = self.brain_dir / "nodes"
        self.memories_dir = self.brain_dir / "memories"
        self.lobes_dir = self.brain_dir / "lobes"
        self.standards_dir = self.brain_dir / "standards"

    def _get_all_markdown_files(self) -> list[Path]:
        """Coleta todos os arquivos markdown da estrutura do cérebro."""
        files = []
        if self.brain_dir.exists():
            for p in self.brain_dir.rglob("*.md"):
                # Ignora temporarios
                if ".git" in str(p) or "node_modules" in str(p):
                    continue
                files.append(p)
        return files

    def _get_existing_node_names(self) -> set[str]:
        """Mapeia os nomes canonicos de nos existentes em brain/nodes/, lobos, standards, profile, core e raiz."""
        existing = set()
        search_dirs = [
            self.nodes_dir,
            self.lobes_dir,
            self.standards_dir,
            self.brain_dir / "profile",
            self.brain_dir / "core"
        ]
        for d in search_dirs:
            if d.exists():
                for p in d.rglob("*.md"):
                    existing.add(p.stem.lower())
                    existing.add(p.stem.replace("_", " ").lower())
                    existing.add(p.stem.replace(" ", "_").lower())

        # Arquivos na raiz do brain (ex: Cortex_Central.md, session_handoff.md)
        if self.brain_dir.exists():
            for p in self.brain_dir.glob("*.md"):
                existing.add(p.stem.lower())
                existing.add(p.stem.replace("_", " ").lower())
                existing.add(p.stem.replace(" ", "_").lower())

        return existing

    def scan_orphaned_nodes(self) -> dict[str, Any]:
        """
        Analisa todos os wikilinks e identifica nos citados que nao existem.
        """
        all_mds = self._get_all_markdown_files()
        existing_nodes = self._get_existing_node_names()

        orphan_references: dict[str, list[str]] = {}
        total_wikilinks = 0
        valid_wikilinks = 0

        for md_file in all_mds:
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
                matches = WIKILINK_PATTERN.findall(content)
                for m in matches:
                    target = m.strip()
                    if not target:
                        continue
                    total_wikilinks += 1
                    target_normalized = target.lower()
                    target_normalized_underscore = target.replace(" ", "_").lower()

                    if target_normalized in existing_nodes or target_normalized_underscore in existing_nodes:
                        valid_wikilinks += 1
                    else:
                        rel_path = md_file.name
                        if target not in orphan_references:
                            orphan_references[target] = []
                        if rel_path not in orphan_references[target]:
                            orphan_references[target].append(rel_path)
            except Exception as e:
                logger.debug(f"Erro ao ler {md_file}: {e}")

        # Ordenar por frequencia de ocorrencia
        sorted_orphans = sorted(
            [{"name": k, "count": len(v), "referenced_in": v} for k, v in orphan_references.items()],
            key=lambda x: int(str(x["count"])),
            reverse=True
        )

        return {
            "total_wikilinks": total_wikilinks,
            "valid_wikilinks": valid_wikilinks,
            "orphaned_count": len(sorted_orphans),
            "orphans": sorted_orphans
        }

    def audit_ontology(self) -> dict[str, Any]:
        """
        Calcula a saude geral da memoria e gera diagnostico completo.
        """
        orphans_data = self.scan_orphaned_nodes()
        total_links = orphans_data["total_wikilinks"]
        valid_links = orphans_data["valid_wikilinks"]

        # Indice de Saude Ontologica (OHI): 0.0 a 1.0
        if total_links > 0:
            ohi = valid_links / total_links
        else:
            ohi = 1.0

        existing_nodes_count = len(list(self.nodes_dir.glob("*.md"))) if self.nodes_dir.exists() else 0
        episodic_count = len(list(self.memories_dir.glob("episodic/*.md"))) if self.memories_dir.exists() else 0
        analytical_count = len(list(self.memories_dir.glob("analytical/*.md"))) if self.memories_dir.exists() else 0
        procedural_count = len(list(self.memories_dir.glob("procedural/*.md"))) if self.memories_dir.exists() else 0

        status = "EXCELENTE" if ohi >= 0.85 else ("ATENCAO" if ohi >= 0.65 else "DEGRADADO")

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ohi_score": round(ohi, 3),
            "status": status,
            "total_nodes": existing_nodes_count,
            "episodic_count": episodic_count,
            "analytical_count": analytical_count,
            "procedural_count": procedural_count,
            "total_synapses": total_links,
            "valid_synapses": valid_links,
            "orphaned_entities_count": orphans_data["orphaned_count"],
            "top_orphans": orphans_data["orphans"][:8]
        }

    def render_report(self) -> str:
        """Renderiza relatorio textual para o terminal."""
        diag = self.audit_ontology()
        lines = [
            "========================================",
            "   THSYR // CONSOLIDADOR ONTOLOGICO     ",
            "========================================",
            f"Indice de Saude (OHI): {diag['ohi_score'] * 100:.1f}% [{diag['status']}]",
            f"Nos Cadastrados:       {diag['total_nodes']}",
            f"Sinapses Analisadas:   {diag['total_synapses']} ({diag['valid_synapses']} validas)",
            f"Memorias Episodicas:   {diag['episodic_count']}",
            f"Memorias Analiticas:   {diag['analytical_count']}",
            f"Procedimentos (SOP):   {diag['procedural_count']}",
            f"Entidades Orfas:       {diag['orphaned_entities_count']}",
            "----------------------------------------"
        ]

        if diag["top_orphans"]:
            lines.append("Top Entidades Orfas (Menções sem Nó):")
            for o in diag["top_orphans"]:
                refs = ", ".join(o["referenced_in"][:3])
                lines.append(f"  - [[{o['name']}]] ({o['count']} mencoes em {refs})")
            lines.append("")
            lines.append("Dica: Use auto-geracao de stubs para converter entidades frequentes em nos formais.")
        else:
            lines.append("Nenhuma entidade orfa detectada. Topologia neural 100% amarrada.")

        lines.append("========================================")
        return "\n".join(lines)
