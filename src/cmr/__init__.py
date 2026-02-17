"""
Compositional Mechanistic Reasoning (CMR) module (Sprint 8).

This module implements the 6-step CMR pipeline for generating
theory-driven predictions from framework templates.

Key components (to be implemented):
- Template library
- Prediction grammar
- Mechanism chaining
- Evidence integration
"""

from src.cmr.wis import (
    aggregate_domain_wis,
    aggregate_overall_wis,
    cohens_d_to_wis,
    goldilocks_to_wis,
    threshold_to_wis,
)
from src.cmr.models import (
    Base,
    CMRDomainScore,
    CMREvaluation,
    CMROverallScore,
    CMRTemplateActivation,
    ReductionClaim,
    TemplateRecord,
)
from src.cmr.interactions import apply_all_interactions, get_interaction
from src.cmr.building_eval import evaluate_building

__all__ = [
    "cohens_d_to_wis",
    "goldilocks_to_wis",
    "threshold_to_wis",
    "aggregate_domain_wis",
    "aggregate_overall_wis",
    "Base",
    "TemplateRecord",
    "CMREvaluation",
    "CMRTemplateActivation",
    "CMRDomainScore",
    "CMROverallScore",
    "ReductionClaim",
    "get_interaction",
    "apply_all_interactions",
    "evaluate_building",
]
