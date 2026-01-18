"""
Article Eater - Models Module

Data models for the theory system.
"""

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
