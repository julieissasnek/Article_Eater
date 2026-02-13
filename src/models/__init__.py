"""
Article Eater - Models Module

Data models for the theory system and epistemic calculus.

V24.0.0: Added ARCH-4 formal epistemic calculus models:
- PropositionalContent: What is believed (content separate from status)
- EpistemicStatus: How strongly believed (Spohn ranks + Pollock warrant)
- Provenance: Where it comes from (Haack grounding + sources)
- ExperientialClaim: Grounding anchors for foundherentist justification
"""

# ARCH-4 Epistemic Calculus Models
from src.models.propositional_content import (
    # Enums
    ContentType,
    Polarity,
    # Data classes
    Variables,
    ScopeCondition,
    PropositionalContent,
    # Functions
    generate_proposition_id,
    generate_edge_id,
)

from src.models.epistemic_status import (
    # Enums
    WarrantStatus,
    DefeatType,
    # Data classes
    RankPair,
    RankHistoryEntry,
    DefeatInfo,
    EpistemicStatus,
    # Functions
    conditionalize,
    conditional_rank,
)

from src.models.provenance import (
    # Enums
    SourceType,
    StudyType,
    Directness,
    JustificationStatus,
    ObservationType,
    ObservationDirectness,
    Revisability,
    # Data classes
    ConfidenceInterval,
    Observer,
    QuantitativeResult,
    ExperientialClaim,
    Source,
    CrosswordPosition,
    Provenance,
    # Registry
    ExperientialClaimRegistry,
)

# Theory System Models (existing)
from src.models.theory_models import (
    # Enums
    TheoryLevel,
    Necessity,
    Testability,
    PredictionType,
    Direction,
    Magnitude,
    RelationType,
    Generality,
    TestingStatus,
    SupportLevel,
    TestType,
    TestResult,
    TestStrength,
    ReplicationStatus,
    ContributionType,
    UncertaintyType,
    
    # Data classes
    Originator,
    TheoryClaim,
    TheoryAssumption,
    TheoryBoundary,
    DerivationStep,
    QuantitativePrediction,
    Prediction,
    PredictionEvidence,
    Theory,
    
    # Functions
    generate_theory_id,
    generate_prediction_id,
    generate_claim_id,
    compute_derivation_confidence,
)

__all__ = [
    # ========================================
    # ARCH-4 Epistemic Calculus (V24.0.0)
    # ========================================

    # PropositionalContent
    'ContentType',
    'Polarity',
    'Variables',
    'ScopeCondition',
    'PropositionalContent',
    'generate_proposition_id',
    'generate_edge_id',

    # EpistemicStatus
    'WarrantStatus',
    'DefeatType',
    'RankPair',
    'RankHistoryEntry',
    'DefeatInfo',
    'EpistemicStatus',
    'conditionalize',
    'conditional_rank',

    # Provenance
    'SourceType',
    'StudyType',
    'Directness',
    'JustificationStatus',
    'ObservationType',
    'ObservationDirectness',
    'Revisability',
    'ConfidenceInterval',
    'Observer',
    'QuantitativeResult',
    'ExperientialClaim',
    'Source',
    'CrosswordPosition',
    'Provenance',
    'ExperientialClaimRegistry',

    # ========================================
    # Theory System (existing)
    # ========================================

    # Enums
    'TheoryLevel',
    'Necessity',
    'Testability',
    'PredictionType',
    'Direction',
    'Magnitude',
    'RelationType',
    'Generality',
    'TestingStatus',
    'SupportLevel',
    'TestType',
    'TestResult',
    'TestStrength',
    'ReplicationStatus',
    'ContributionType',
    'UncertaintyType',

    # Data classes
    'Originator',
    'TheoryClaim',
    'TheoryAssumption',
    'TheoryBoundary',
    'DerivationStep',
    'QuantitativePrediction',
    'Prediction',
    'PredictionEvidence',
    'Theory',

    # Functions
    'generate_theory_id',
    'generate_prediction_id',
    'generate_claim_id',
    'compute_derivation_confidence',
]
