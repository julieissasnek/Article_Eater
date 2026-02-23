"""Core enum types extracted from web_of_belief monolith (ARCH-5d)."""

from __future__ import annotations

from enum import Enum


class EpistemicLevel(Enum):
    """Levels in the web of belief, from center to periphery."""

    THEORETICAL = "theoretical"
    INTERMEDIATE = "intermediate"
    EMPIRICAL = "empirical"
    OBSERVATIONAL = "observational"


class BeliefStatus(Enum):
    """Status of a belief in the web."""

    STUB = "stub"
    TENTATIVE = "tentative"
    ESTABLISHED = "established"
    ENTRENCHED = "entrenched"
    ANOMALOUS = "anomalous"


class InferenceType(Enum):
    """Inferential origin of a belief."""

    INDUCTIVE = "inductive"
    DEDUCTIVE = "deductive"
    ABDUCTIVE = "abductive"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class BeliefKind(Enum):
    """Functional role of a belief."""

    MECHANISTIC = "mechanistic"
    EVIDENTIAL = "evidential"
    THEORETICAL = "theoretical"
    METHODOLOGICAL = "methodological"
    BRIDGE = "bridge"


class CausalDirection(Enum):
    """Causal direction for constraint relationships."""

    UNKNOWN = "unknown"
    CORRELATIONAL = "correlational"
    FORWARD = "forward"
    REVERSE = "reverse"
    BIDIRECTIONAL = "bidirectional"
    COMMON_CAUSE = "common_cause"
    MEDIATED = "mediated"


class SourceDepth(Enum):
    """Depth of source material used for extraction."""

    FULL_TEXT = "full_text"
    ABSTRACT = "abstract"
    METADATA = "metadata"


class NodeDomain(str, Enum):
    """Knowledge domain for nodes in the web."""

    BASIC_SCIENCE = "basic_science"
    ENVIRONMENTAL_PSYCHOLOGY = "environmental_psychology"
    METHODOLOGY = "methodology"
    CNFA = "cnfa"
    EPISTEMIC = "epistemic"


class EpistemicNodeSubtype(str, Enum):
    """Subtypes for EPISTEMIC domain nodes."""

    E1_COHERENCE_BELIEF_MAINTENANCE = "e1_coherence_belief_maintenance"
    E2_SOCIAL_EPISTEMICS = "e2_social_epistemics"
    E3_EPISTEMIC_EMOTIONS = "e3_epistemic_emotions"
    E4_REFLECTIVE_EQUILIBRIUM = "e4_reflective_equilibrium"


class PathwayType(str, Enum):
    """Effect pathway classification for causal edges."""

    SUBPERSONAL = "subpersonal"
    PERSONAL_EPISTEMIC = "personal_epistemic"
    MIXED = "mixed"


class ReplicationStatus(str, Enum):
    """Replication status of empirical claims."""

    REPLICATED = "replicated"
    PARTIALLY_REPLICATED = "partially_replicated"
    UNREPLICATED = "unreplicated"
    FAILED_REPLICATION = "failed_replication"


class PESubtype(str, Enum):
    """Subtypes of prediction error in environmental cognition."""

    FUNCTIONAL_PE = "functional_pe"
    NAVIGATIONAL_PE = "navigational_pe"
    SOCIAL_PE = "social_pe"


class StudyDesign(str, Enum):
    """ARCH-6a: Study design quality classification (Mayo).

    Ordered from strongest to weakest severe-testing potential.
    RCTs can rule out confounds that observational studies cannot.
    """

    RCT = "rct"                           # Randomized controlled trial
    META_ANALYSIS = "meta_analysis"       # Systematic meta-analysis of multiple studies
    QUASI_EXPERIMENTAL = "quasi_experimental"  # Non-randomized but controlled
    OBSERVATIONAL = "observational"       # Correlational / cross-sectional / cohort
    CASE_STUDY = "case_study"             # Single case, clinical, or design post-occupancy
    QUALITATIVE = "qualitative"           # Interviews, ethnography, phenomenological
    THEORETICAL = "theoretical"           # No empirical data — modelling or argument only
    UNKNOWN = "unknown"                   # Not classified


class EvidenceQuality(str, Enum):
    """ARCH-6d: Distinguish 'consistent with' vs 'severely tested by' (Mayo).

    A belief that is CONSISTENT WITH evidence has not been tested against
    plausible alternatives. A belief that has been SEVERELY TESTED survived
    a study designed to detect failure if the hypothesis were false.
    """

    SEVERELY_TESTED = "severely_tested"           # Passed a test that would likely have failed if H false
    MODERATELY_TESTED = "moderately_tested"       # Partial control for alternatives
    CONSISTENT_ONLY = "consistent_only"           # Compatible with evidence but alternatives not ruled out
    UNTESTED = "untested"                         # No empirical confrontation


# ---- severity weights for StudyDesign ----
STUDY_DESIGN_SEVERITY_WEIGHT: dict[str, float] = {
    StudyDesign.RCT.value: 1.0,
    StudyDesign.META_ANALYSIS.value: 0.95,
    StudyDesign.QUASI_EXPERIMENTAL.value: 0.70,
    StudyDesign.OBSERVATIONAL.value: 0.45,
    StudyDesign.CASE_STUDY.value: 0.25,
    StudyDesign.QUALITATIVE.value: 0.15,
    StudyDesign.THEORETICAL.value: 0.05,
    StudyDesign.UNKNOWN.value: 0.30,
}


__all__ = [
    "EpistemicLevel",
    "BeliefStatus",
    "InferenceType",
    "BeliefKind",
    "CausalDirection",
    "SourceDepth",
    "NodeDomain",
    "EpistemicNodeSubtype",
    "PathwayType",
    "ReplicationStatus",
    "PESubtype",
    "StudyDesign",
    "EvidenceQuality",
    "STUDY_DESIGN_SEVERITY_WEIGHT",
]
