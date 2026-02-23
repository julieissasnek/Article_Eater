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
]
