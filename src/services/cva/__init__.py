"""
src/services/cva/ — CVA Sprint Series Modules
==============================================

Sprint-specific CVA implementations:
  CVA-3: activity_frame_registry — Canonical frames with goal activation
  CVA-5: epistemic_projection_cva — Goal-modulated projection
"""

from src.services.cva.activity_frame_registry import (
    CanonicalFrame,
    ActivityFrameRegistry,
    CANONICAL_FRAMES,
    VALUATION_AXES,
    CONSTRAINT_NAMES,
)

from src.services.cva.epistemic_projection_cva import (
    GOAL_WARRANT_ALIGNMENT,
    FRAME_WARRANT_ALIGNMENT,
    d_goal,
    d_frame,
    compute_d_cva,
    project_goal_modulated,
    aggregate_projections_goal_modulated,
    compose_path_discounts_goal_modulated,
    project_comparison,
    project_with_full_diagnostic,
    ProjectionComparison,
)

__all__ = [
    "CanonicalFrame",
    "ActivityFrameRegistry",
    "CANONICAL_FRAMES",
    "VALUATION_AXES",
    "CONSTRAINT_NAMES",
    "GOAL_WARRANT_ALIGNMENT",
    "FRAME_WARRANT_ALIGNMENT",
    "d_goal",
    "d_frame",
    "compute_d_cva",
    "project_goal_modulated",
    "aggregate_projections_goal_modulated",
    "compose_path_discounts_goal_modulated",
    "project_comparison",
    "project_with_full_diagnostic",
    "ProjectionComparison",
]
