"""Extracted ECB modules — compatibility layer (ARCH-5e).

Provides re-exports so that all types previously imported from
``epistemic_causal_bridge`` can also be imported from this package.

Usage::

    from src.services.ecb_modules import ContrastClass, StructuralEquation
    from src.services.ecb_modules.contrast_classes import TemporalSpec
    from src.services.ecb_modules.causal_models import Variable
    from src.services.ecb_modules.counterfactuals import CounterfactualQuery
"""

from .contrast_classes import (
    BaselineSpec,
    BeliefScope,
    ConditionSpec,
    ContrastClass,
    ContrastTransferType,
    ContrastType,
    CONTRAST_TRANSFER_THRESHOLDS,
    CulturalMeaning,
    DistributionSpec,
    PopulationContext,
    SelectionVariable,
    TemporalSpec,
    TransportabilityAssessment,
)
from .causal_models import (
    MultiTheoryModel,
    StructuralEquation,
    TheoryRelativeModel,
    Variable,
)
from .counterfactuals import (
    BeliefChange,
    CoherenceAssessment,
    CoherenceViolation,
    ContrastAssessment,
    CounterfactualQuery,
    EpistemicCounterfactualResult,
    EpistemicGap,
    ExcludedBelief,
    GeneralizationAssessment,
    QuineanCounterfactualResult,
    RobustnessAnalysis,
    ScopeAssessment,
    TheoryCounterfactual,
    TheoryImpact,
)

__all__ = [
    # contrast_classes
    "BaselineSpec",
    "BeliefScope",
    "ConditionSpec",
    "ContrastClass",
    "ContrastTransferType",
    "ContrastType",
    "CONTRAST_TRANSFER_THRESHOLDS",
    "CulturalMeaning",
    "DistributionSpec",
    "PopulationContext",
    "SelectionVariable",
    "TemporalSpec",
    "TransportabilityAssessment",
    # causal_models
    "MultiTheoryModel",
    "StructuralEquation",
    "TheoryRelativeModel",
    "Variable",
    # counterfactuals
    "BeliefChange",
    "CoherenceAssessment",
    "CoherenceViolation",
    "ContrastAssessment",
    "CounterfactualQuery",
    "EpistemicCounterfactualResult",
    "EpistemicGap",
    "ExcludedBelief",
    "GeneralizationAssessment",
    "QuineanCounterfactualResult",
    "RobustnessAnalysis",
    "ScopeAssessment",
    "TheoryCounterfactual",
    "TheoryImpact",
]
