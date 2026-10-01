"""Synchronize generated neural graph metrics into the project README."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

START = "<!-- THSYR_GRAPH_STATS:START -->"
END = "<!-- THSYR_GRAPH_STATS:END -->"


def update_readme_graph_stats(
    graph: dict[str, Any],
    readme_path: Path,
    source_label: str = "brain/knowledge_ecosystem.json",
) -> Path:
    """Replace the delimited graph metrics block without touching other README text."""
    content = readme_path.read_text(encoding="utf-8")
    block = (
        f"{START}\n"
        f"**Estado atual do cérebro:** `{len(graph.get('nodes', [])):,}` nós e "
        f"`{len(graph.get('links', [])):,}` sinapses.\n\n"
        f"_Fonte gerada em `{source_label}`._\n"
        f"{END}"
    ).replace(",", ".")
    replacement = f"{START}\n{block.splitlines()[1]}\n{block.splitlines()[2]}\n{END}"
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    if pattern.search(content):
        updated = pattern.sub(replacement, content, count=1)
    else:
        marker = "### Cerebro Neural 3D"
        if marker not in content:
            raise ValueError(f"README nao possui o marcador de insercao: {marker}")
        updated = content.replace(marker, f"{replacement}\n\n{marker}", 1)
    if updated != content:
        readme_path.write_text(updated, encoding="utf-8")
    return readme_path
