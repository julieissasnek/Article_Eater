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

__all__ = [
    "cohens_d_to_wis",
    "goldilocks_to_wis",
    "threshold_to_wis",
    "aggregate_domain_wis",
    "aggregate_overall_wis",
]
