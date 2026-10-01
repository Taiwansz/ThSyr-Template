"""Traceable multi-repository knowledge index for the ThSyr neural graph."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from .neural_graph import extract_graph_data
from .workspace_observer import discover_workspaces

IGNORED_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".next", "dist", "build", "coverage"}
IGNORED_FILES = {".env", ".env.local", ".env.production", "id_rsa"}
TEXT_EXTENSIONS = {
    ".md": "documentation",
    ".py": "source",
    ".ts": "source",
    ".tsx": "source",
    ".js": "source",
    ".jsx": "source",
    ".java": "source",
    ".go": "source",
    ".rs": "source",
    ".sql": "data",
    ".json": "configuration",
    ".yaml": "configuration",
    ".yml": "configuration",
    ".toml": "configuration",
}


def _git_head(root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return result.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def ingest_workspaces(
    workspaces: list[Path] | None = None,
    output_path: Path | None = None,
    max_files_per_workspace: int = 1200,
) -> dict[str, Any]:
    """Index real project and file nodes without persisting file contents."""
    roots = [path.resolve() for path in (workspaces or discover_workspaces()) if path.is_dir()]
    nodes: list[dict[str, Any]] = []
    links: list[dict[str, str]] = []
    seen: set[str] = set()

    def add_node(node: dict[str, Any]) -> None:
        if node["id"] not in seen:
            seen.add(node["id"])
            nodes.append(node)

    for root in roots:
        project_id = f"project:{root.name}"
        add_node(
            {
                "id": project_id,
                "label": root.name,
                "group": "projeto",
                "kind": "project",
                "path": str(root),
                "source": "local_workspace",
                "git_head": _git_head(root),
            }
        )
        scanned = 0
        for path in sorted(root.rglob("*")):
            if scanned >= max_files_per_workspace:
                break
            if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            if any(part in IGNORED_DIRS for part in path.relative_to(root).parts):
                continue
            if path.name.lower() in IGNORED_FILES or path.suffix.lower() in {".pem", ".key", ".p12", ".pfx"}:
                continue
            relative = path.relative_to(root).as_posix()
            file_id = f"file:{root.name}:{relative}"
            kind = TEXT_EXTENSIONS[path.suffix.lower()]
            group = "design" if "design" in relative.lower() else ("tech" if kind == "source" else "conceito")
            parts = path.relative_to(root).parts[:-1]
            parent_id = project_id
            for depth, part in enumerate(parts, start=1):
                directory = root.joinpath(*parts[:depth])
                directory_id = f"directory:{root.name}:{directory.relative_to(root).as_posix()}"
                add_node(
                    {
                        "id": directory_id,
                        "label": directory.relative_to(root).as_posix(),
                        "group": "projeto",
                        "kind": "directory",
                        "path": str(directory),
                        "source": "local_workspace",
                        "workspace": root.name,
                        "parent_id": parent_id,
                        "depth": depth,
                    }
                )
                if not any(link["source"] == parent_id and link["target"] == directory_id for link in links):
                    links.append({"source": parent_id, "target": directory_id, "relation": "contains"})
                parent_id = directory_id
            add_node(
                {
                    "id": file_id,
                    "label": relative,
                    "group": group,
                    "kind": kind,
                    "path": str(path),
                    "source": "local_workspace",
                    "workspace": root.name,
                    "bytes": path.stat().st_size,
                    "parent_id": parent_id,
                    "depth": len(parts) + 1,
                }
            )
            links.append({"source": parent_id, "target": file_id, "relation": "contains"})
            scanned += 1

    graph = {
        "version": 1,
        "source": "multi_repository_ingestor",
        "workspaces": [str(root) for root in roots],
        "nodes": nodes,
        "links": links,
        "total_nodes": len(nodes),
        "total_edges": len(links),
    }
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    return graph


def extract_ecosystem_graph(brain_dir: Path, index_path: Path | None = None) -> dict[str, Any]:
    """Combine the canonical brain graph with the traceable workspace index."""
    graph = extract_graph_data(brain_dir)
    if not index_path or not index_path.exists():
        return graph
    external = json.loads(index_path.read_text(encoding="utf-8"))
    known = {node["id"] for node in graph["nodes"]}
    for node in external.get("nodes", []):
        if node["id"] not in known:
            graph["nodes"].append(node)
            known.add(node["id"])
    graph["links"].extend(external.get("links", []))
    degrees: dict[str, int] = {}
    for link in graph["links"]:
        degrees[link["source"]] = degrees.get(link["source"], 0) + 1
        degrees[link["target"]] = degrees.get(link["target"], 0) + 1
    for node in graph["nodes"]:
        node["degree"] = degrees.get(node["id"], 0)
        node["is_hub"] = node["degree"] >= 4
    return graph
