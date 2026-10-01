"""
ThSyr Visual & Frontend Craft Engine.
Direcao de arte, memoria de gosto, renderizacao e quality gate multimodal.
"""

from .archetypes import NICHE_ARCHETYPES, get_niche_preset, list_available_niches
from .contracts import CritiqueIssue, IssueSeverity, VisualArtifactKind, VisualBrief, VisualCritique
from .critic import VisualCritic
from .failure_memory import VisualFailureMemory
from .refinement_loop import VisualRefinementLoop
from .scaffolder import generate_studio_scaffold
from .screenshot import capture_screenshot
from .studio import VisualStudio
from .taste_memory import TasteEntry, TasteMemory
from .tournament import DesignDirection, DesignTournament
from .validator import VisualCraftValidator

__all__ = [
    "NICHE_ARCHETYPES",
    "CritiqueIssue",
    "IssueSeverity",
    "TasteEntry",
    "TasteMemory",
    "VisualArtifactKind",
    "VisualBrief",
    "VisualCraftValidator",
    "VisualFailureMemory",
    "VisualRefinementLoop",
    "VisualCritic",
    "VisualCritique",
    "VisualStudio",
    "DesignDirection",
    "DesignTournament",
    "capture_screenshot",
    "generate_studio_scaffold",
    "get_niche_preset",
    "list_available_niches",
]
