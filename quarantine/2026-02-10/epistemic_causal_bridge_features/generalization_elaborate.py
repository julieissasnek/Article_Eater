"""
ARCHIVED: Elaborate Generalization Assessment
==============================================

Date Archived: 2026-02-10
Reason: Simplification sprint - stabilizing core bridge before adding complexity
Original Location: src/services/epistemic_causal_bridge.py (lines 811-850)

This module contains the full-featured GeneralizationAssessment class for
determining whether findings transfer to new contexts.

WHY IT'S VALUABLE:
- Explicit uncertainty about transfer (lab→field, population→population)
- Practitioner-facing: "Will this work for MY project?"
- Combines contrast + scope + individual difference assessments

DEPENDENCIES FOR REINTEGRATION:
- Simpler ScopeAssessment working first
- PopulationContext populated with real baseline data
- Individual difference system reintegrated
- Adjustment algorithms for generalization penalties

NOTE: This overlaps with the simpler ScopeAssessment class that is being kept.
The elaborate version should be reintegrated once the simpler version is proven.

FUTURE TODOs:
- GEN-1: Validate simpler ScopeAssessment first
- GEN-2: Add generalization_type classification
- GEN-3: Implement adjustment algorithms
- GEN-4: Integrate with individual differences

See: docs/ARCHIVED_FEATURES_EPISTEMIC_CAUSAL_BRIDGE_2026-02-10.md for full documentation.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Any


@dataclass
class GeneralizationAssessment:
    """
    Full assessment of belief generalization across contexts.

    This is the elaborate version that combines:
    - Contrast class comparison
    - Population context comparison
    - Individual difference adjustment
    - Uncertainty quantification

    Use ScopeAssessment (kept in bridge) for simpler scope checking.
    Use this for full practitioner-facing "will it work for me?" questions.
    """
    belief_id: str
    source_context: Any  # PopulationContext when reintegrated
    target_context: Any  # PopulationContext when reintegrated
    target_individual: Optional[Any]  # IndividualDifferenceProfile when reintegrated

    source_contrast: Any  # ContrastClass when reintegrated
    target_contrast: Any  # ContrastClass when reintegrated

    # Classification of the generalization
    generalization_type: str  # e.g., "direct", "population_shift", "meaning_shift"
    adjustment_factor: float  # 0.0 to 1.0 multiplier on effect size

    # Effect estimates
    original_estimate: float  # Effect in source context
    generalized_estimate: float  # Expected effect in target context
    generalization_uncertainty: float  # Additional uncertainty from transfer

    # Guidance
    warnings: List[str]  # Specific concerns about the transfer
    recommendations: List[str]  # Actions to improve confidence

    def summary(self) -> str:
        """Generate human-readable summary of assessment."""
        lines = [
            f"=== Generalization Assessment ===",
            f"Belief: {self.belief_id}",
            f"Source: {getattr(self.source_context, 'population_id', 'unknown')}",
            f"Target: {getattr(self.target_context, 'population_id', 'unknown')}",
            f"Type: {self.generalization_type}",
            f"",
            f"Original estimate: {self.original_estimate:.2f}",
            f"Generalized: {self.generalized_estimate:.2f} ± {self.generalization_uncertainty:.2f}",
            f"Adjustment factor: {self.adjustment_factor:.2f}",
        ]

        if self.target_individual:
            lines.append(f"\nIndividualized for: {self.target_individual}")

        if self.warnings:
            lines.append("\nWarnings:")
            for w in self.warnings:
                lines.append(f"  - {w}")

        if self.recommendations:
            lines.append("\nRecommendations:")
            for r in self.recommendations:
                lines.append(f"  - {r}")

        return "\n".join(lines)

    def is_transferable(self) -> bool:
        """Check if generalization is reasonable."""
        return (
            self.adjustment_factor > 0.3 and
            self.generalization_type != "meaning_shift"
        )


# Example usage:
"""
assessment = GeneralizationAssessment(
    belief_id="belief:nature_reduces_stress",
    source_context=PopulationContext(population_id="US_office_workers"),
    target_context=PopulationContext(population_id="JP_office_workers"),
    target_individual=IndividualDifferenceProfile(nature_connectedness=4.5),

    source_contrast=nature_vs_office_contrast,
    target_contrast=nature_vs_office_contrast_jp,

    generalization_type="population_shift",
    adjustment_factor=0.7,

    original_estimate=0.45,  # Cohen's d in source
    generalized_estimate=0.32,  # Adjusted for population
    generalization_uncertainty=0.15,  # Additional uncertainty

    warnings=[
        "Cultural meaning of 'nature exposure' differs (shinrin-yoku vs casual)",
        "Baseline nature exposure lower in target population",
        "Individual has high nature connectedness (may amplify effect)"
    ],
    recommendations=[
        "Consider shinrin-yoku protocol rather than passive exposure",
        "Seek Japanese-context studies for direct evidence",
        "Individual adjustment suggests +15% effect size"
    ]
)

print(assessment.summary())
"""
