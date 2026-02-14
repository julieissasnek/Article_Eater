"""
Reflexive Monitoring Module (Sprint 3).

Provides algorithms for detecting epistemic vulnerabilities in the web of belief:
- Coherence audit: Detects entrenchment changes from coherence settling
- Asymmetry monitor: Identifies high entrenchment with weak direct evidence
- Bias detection: Checks evidence diversity (lab, paradigm, method)
- Adversarial review: Stress-tests entrenched claims
"""

from src.epistemic.monitors.coherence_audit import (
    run_coherence_audit,
    CoherenceAuditResult,
    FlaggedNode,
    FlagType,
)

from src.epistemic.monitors.asymmetry_monitor import (
    run_asymmetry_monitor,
    AsymmetryResult,
    AsymmetryFlag,
)

from src.epistemic.monitors.bias_detection import (
    run_structural_bias_detection,
    BiasDetectionResult,
    BiasFlag,
)

from src.epistemic.monitors.adversarial_review import (
    run_adversarial_review,
    AdversarialReviewResult,
    ReviewedNode,
)

__all__ = [
    # Coherence audit
    "run_coherence_audit",
    "CoherenceAuditResult",
    "FlaggedNode",
    "FlagType",
    # Asymmetry monitor
    "run_asymmetry_monitor",
    "AsymmetryResult",
    "AsymmetryFlag",
    # Bias detection
    "run_structural_bias_detection",
    "BiasDetectionResult",
    "BiasFlag",
    # Adversarial review
    "run_adversarial_review",
    "AdversarialReviewResult",
    "ReviewedNode",
]
