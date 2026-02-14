"""
Method Registry and Task-Ecological Validity (Sprint 4b).

Provides methodological validity assessment infrastructure:
- Task 4b.1: MethodRegistry data structure
- Task 4b.2: Seed entries for common CNFA instruments
- Task 4b.3: Task-ecological validity scoring
- Task 4b.4: Claim type bifurcation
- Task 4b.5: Method identification
- Task 4b.6: Per-claim validity computation
"""

from src.methods.registry import (
    MethodEntry,
    MethodRegistry,
    MethodType,
    MovementCompatibility,
    ProfileStatus,
)

from src.methods.task_ecology import (
    TaskClass,
    EffectPathway,
    ClaimType,
    StateCharacterization,
    TASK_AUTHENTICITY_SCORES,
    compute_task_ecological_validity,
)

from src.methods.validity_scorer import (
    compute_claim_validity,
    ClaimValidityResult,
)

from src.methods.method_identifier import (
    identify_methods,
    MethodIdentificationResult,
)

__all__ = [
    # Registry
    "MethodEntry",
    "MethodRegistry",
    "MethodType",
    "MovementCompatibility",
    "ProfileStatus",
    # Task ecology
    "TaskClass",
    "EffectPathway",
    "ClaimType",
    "StateCharacterization",
    "TASK_AUTHENTICITY_SCORES",
    "compute_task_ecological_validity",
    # Validity scoring
    "compute_claim_validity",
    "ClaimValidityResult",
    # Method identification
    "identify_methods",
    "MethodIdentificationResult",
]
