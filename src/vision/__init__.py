"""Vision attribute computation module for causal-theoretic image analysis.

This module provides implementations of vision algorithms for computing
causally active environmental attributes from images. All 12 NEW attributes
from the Kirsh Decision Tree analysis are implemented across three files.

Attributes implemented:
- NEW-01: Vegetation Segmentation Ratio (batch3)
- NEW-02: Scene Depth Estimation - Monocular Cues (batch3)
- NEW-03: Sky Proportion and Horizon Ratio (new_attributes)
- NEW-04: Visual Complexity Score (batch2)
- NEW-05: Regularity/Repetition Index (batch2)
- NEW-06: Figure-Ground Clarity (batch2)
- NEW-07: Material Diversity Index (new_attributes)
- NEW-08: Illumination Uniformity (batch2)
- NEW-09: Acoustic Privacy Proxy (batch3)
- NEW-10: Person/Face Density Estimation (new_attributes)
- NEW-11: Visual Privacy (batch3)
- NEW-12: Biomorphic Curvature Index (batch2)

All functions follow a consistent interface:
    func(image_path: str, verbose: bool = False) -> Dict[str, Any]
"""

from .new_attributes import (
    compute_sky_proportion,
    compute_material_diversity,
    compute_person_density,
)

from .new_attributes_batch2 import (
    compute_visual_complexity,
    compute_regularity_index,
    compute_figure_ground_clarity,
    compute_illumination_uniformity,
    compute_biomorphic_curvature,
)

from .new_attributes_batch3 import (
    compute_vegetation_segmentation,
    compute_depth_estimation_monocular,
    compute_acoustic_privacy_proxy,
    compute_visual_privacy,
)

from .new_attributes_batch4 import (
    compute_temporal_lighting_variation,
    compute_prospect_refuge_balance,
    compute_focal_point_density,
)

__all__ = [
    # NEW-01
    "compute_vegetation_segmentation",
    # NEW-02
    "compute_depth_estimation_monocular",
    # NEW-03
    "compute_sky_proportion",
    # NEW-04
    "compute_visual_complexity",
    # NEW-05
    "compute_regularity_index",
    # NEW-06
    "compute_figure_ground_clarity",
    # NEW-07
    "compute_material_diversity",
    # NEW-08
    "compute_illumination_uniformity",
    # NEW-09
    "compute_acoustic_privacy_proxy",
    # NEW-10
    "compute_person_density",
    # NEW-11
    "compute_visual_privacy",
    # NEW-12
    "compute_biomorphic_curvature",
    # NEW-13
    "compute_temporal_lighting_variation",
    # NEW-14
    "compute_prospect_refuge_balance",
    # NEW-15
    "compute_focal_point_density",
]
