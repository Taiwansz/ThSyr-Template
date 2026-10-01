"""
ThSyr Brand & Logo Reference Library Interface
Acesso programatico de alta performance ao catalogo de 1.400+ logos SVG reais
classificados por geometria, tecnica, industria, sujeito e paleta cromatica.
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..config import PROJECT_ROOT


@dataclass
class LogoRecord:
    filename: str
    mark_type: str
    colors: int
    subject: str
    note: str
    exemplary: bool
    path: Path
    industry: Optional[str] = None
    technique: Optional[str] = None
    geometry: Optional[str] = None
    mood: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "filename": self.filename,
            "mark_type": self.mark_type,
            "colors": self.colors,
            "subject": self.subject,
            "note": self.note,
            "exemplary": self.exemplary,
            "path": str(self.path),
            "industry": self.industry,
            "technique": self.technique,
            "geometry": self.geometry,
            "mood": self.mood,
        }


class LogoLibrary:
    """Interface para consulta analitica do acervo canonico de logos SVG."""

    _instance: Optional["LogoLibrary"] = None

    def __init__(self, library_dir: Optional[Path] = None):
        self.library_dir = self._resolve_library_dir(library_dir)
        self.svg_dir = self.library_dir / "svg"
        self.catalog_file = self.library_dir / "catalog.json"
        self.classifications_file = self.library_dir / "classifications.json"
        self.stats_file = self.library_dir / "stats.json"

        self._catalog: Dict[str, Any] = {}
        self._classifications: Dict[str, Any] = {}
        self._stats: Dict[str, Any] = {}
        self._loaded = False

    @classmethod
    def get_instance(cls) -> "LogoLibrary":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _resolve_library_dir(self, override: Optional[Path]) -> Path:
        if override and override.exists():
            return override

        candidates = [
            PROJECT_ROOT / ".agents" / "skills" / "logo-design" / "assets" / "library",
            Path("/root/.gemini/config/skills/logo-design/assets/library"),
            Path("/tmp/logo-design-skill/skills/logo-design/assets/library"),
            PROJECT_ROOT / "assets" / "logo_library",
        ]
        for c in candidates:
            if c.exists() and (c / "catalog.json").exists():
                return c

        return candidates[0]

    def _load_data(self) -> None:
        if self._loaded:
            return

        if self.catalog_file.exists():
            try:
                with open(self.catalog_file, "r", encoding="utf-8") as f:
                    raw_cat = json.load(f)
                    if isinstance(raw_cat, list):
                        self._catalog = {item["file"]: item for item in raw_cat if isinstance(item, dict) and "file" in item}
                    elif isinstance(raw_cat, dict):
                        self._catalog = raw_cat
            except Exception:
                self._catalog = {}

        if self.classifications_file.exists():
            try:
                with open(self.classifications_file, "r", encoding="utf-8") as f:
                    raw_cls = json.load(f)
                    if isinstance(raw_cls, list):
                        self._classifications = {item["file"]: item for item in raw_cls if isinstance(item, dict) and "file" in item}
                    elif isinstance(raw_cls, dict):
                        self._classifications = raw_cls
            except Exception:
                self._classifications = {}

        if self.stats_file.exists():
            try:
                with open(self.stats_file, "r", encoding="utf-8") as f:
                    self._stats = json.load(f)
            except Exception:
                self._stats = {}

        self._loaded = True

    @property
    def is_available(self) -> bool:
        self._load_data()
        return bool(self._catalog) and self.svg_dir.exists()

    def get_stats(self) -> Dict[str, Any]:
        self._load_data()
        total = self._stats.get("count", len(self._catalog))
        mark_types_raw = self._stats.get("mark_types")
        if isinstance(mark_types_raw, list):
            types = {str(k): int(v) for k, v in mark_types_raw}
        elif isinstance(mark_types_raw, dict):
            types = {str(k): int(v) for k, v in mark_types_raw.items()}
        else:
            types = {}
            for entry in self._catalog.values():
                t = entry.get("mark_type") or entry.get("type", "unknown")
                types[t] = types.get(t, 0) + 1

        exemplary = sum(1 for entry in self._catalog.values() if entry.get("exemplary"))

        return {
            "total_logos": total,
            "exemplary_count": exemplary,
            "mark_types": types,
            "library_path": str(self.library_dir),
            "primary_family": self._stats.get("primary_family", []),
            "gradient_share": self._stats.get("gradient_share", 0.0),
        }

    def search(
        self,
        query: Optional[str] = None,
        mark_type: Optional[str] = None,
        technique: Optional[str] = None,
        geometry: Optional[str] = None,
        industry: Optional[str] = None,
        color: Optional[str] = None,
        mood: Optional[str] = None,
        subject: Optional[str] = None,
        exemplary: bool = False,
        limit: int = 20,
    ) -> List[LogoRecord]:
        self._load_data()
        if not self._catalog:
            return []

        results: List[LogoRecord] = []
        q_tokens = [t.lower() for t in query.split()] if query else []

        for filename, item in self._catalog.items():
            if exemplary and not item.get("exemplary"):
                continue

            item_type = item.get("mark_type") or item.get("type", "")
            if mark_type and item_type.lower() != mark_type.lower():
                continue

            # Classificacao enriquecida
            c_info = self._classifications.get(filename, {})
            item_industry = item.get("industry") or c_info.get("industry")
            item_technique = item.get("techniques") or c_info.get("technique")
            item_geometry = item.get("geometry") or c_info.get("geometry")
            item_mood = item.get("mood") or c_info.get("mood")

            if industry:
                ind_list = item_industry if isinstance(item_industry, list) else [item_industry]
                if not any(industry.lower() in str(i).lower() for i in ind_list if i):
                    continue

            if technique:
                tech_list = item_technique if isinstance(item_technique, list) else [item_technique]
                if not any(technique.lower() in str(t).lower() for t in tech_list if t):
                    continue

            if geometry:
                geo_list = item_geometry if isinstance(item_geometry, list) else [item_geometry]
                if not any(geometry.lower() in str(g).lower() for g in geo_list if g):
                    continue

            if mood:
                m_list = item_mood if isinstance(item_mood, list) else [item_mood]
                if not any(mood.lower() in str(m).lower() for m in m_list if m):
                    continue

            if subject:
                s_str = str(item.get("subject", "")).lower()
                if subject.lower() not in s_str:
                    continue

            if color:
                c_colors = item.get("colors") or item.get("colors_list") or []
                c_fams = item.get("color_families") or []
                all_c = [str(x).lower() for x in c_colors] + [str(x).lower() for x in c_fams]
                if not any(color.lower() in c for c in all_c):
                    continue

            if q_tokens:
                text_corpus = f"{filename} {item.get('brand', '')} {item.get('subject', '')} {item.get('note', '')} {item_industry} {item_technique} {item_geometry} {item_mood}".lower()
                if not all(t in text_corpus for t in q_tokens):
                    continue

            svg_path = self.svg_dir / filename
            n_colors = item.get("n_colors")
            if n_colors is None:
                n_colors = len(item.get("colors", [])) if isinstance(item.get("colors"), list) else 1

            record = LogoRecord(
                filename=filename,
                mark_type=item_type,
                colors=int(n_colors),
                subject=item.get("subject", ""),
                note=item.get("note", ""),
                exemplary=bool(item.get("exemplary")),
                path=svg_path,
                industry=str(item_industry) if item_industry else None,
                technique=", ".join(item_technique) if isinstance(item_technique, list) else (str(item_technique) if item_technique else None),
                geometry=", ".join(item_geometry) if isinstance(item_geometry, list) else (str(item_geometry) if item_geometry else None),
                mood=", ".join(item_mood) if isinstance(item_mood, list) else (str(item_mood) if item_mood else None),
            )
            results.append(record)
            if len(results) >= limit:
                break

        return results

    def get_svg_content(self, filename: str) -> Optional[str]:
        p = self.svg_dir / filename
        if not p.exists() and not filename.endswith(".svg"):
            p = self.svg_dir / f"{filename}.svg"
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                return None
        return None

    def get_svg_path(self, filename: str) -> Optional[Path]:
        p = self.svg_dir / filename
        if not p.exists() and not filename.endswith(".svg"):
            p = self.svg_dir / f"{filename}.svg"
        return p if p.exists() else None
