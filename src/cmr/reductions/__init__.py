"""
Tier 2 Theory Reductions Module.

Maps Tier 2 domain theories (ART, SRT, Biophilia, etc.) to Tier 1 template mechanisms.
Each reduction specifies which templates implement a theory construct and what
irreducible residual remains.

Sprint 12 Tasks 12.1-12.3.
"""

from src.cmr.reductions.art_reduction import (
    ART_REDUCTIONS,
    reduce_art_construct,
    get_art_template_coverage,
)
from src.cmr.reductions.srt_reduction import (
    SRT_REDUCTIONS,
    reduce_srt_construct,
    get_srt_template_coverage,
)
from src.cmr.reductions.biophilia_reduction import (
    BIOPHILIA_REDUCTIONS,
    reduce_biophilia_construct,
    get_biophilia_template_coverage,
)

__all__ = [
    "ART_REDUCTIONS",
    "reduce_art_construct",
    "get_art_template_coverage",
    "SRT_REDUCTIONS",
    "reduce_srt_construct",
    "get_srt_template_coverage",
    "BIOPHILIA_REDUCTIONS",
    "reduce_biophilia_construct",
    "get_biophilia_template_coverage",
]
