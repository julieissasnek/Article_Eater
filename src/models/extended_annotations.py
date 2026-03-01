"""
Extended Annotation Types A9-A18 — QA-Enabling Annotations
============================================================

Extends the base CVA annotation system (A1-A8) with 10 new types
designed to enable richer QA queries:

  A9:  Surprise Flag      — counterintuitive findings
  A10: Design Implication  — actionable recommendations
  A11: Controversy/Dispute — where researchers disagree
  A12: Analogical Bridge   — everyday explanations
  A13: Replication Status  — evidence reliability
  A14: Effect Magnitude    — human-scale effect sizes
  A15: Cross-Domain Link   — connections to other fields
  A16: Historical Context  — evolution of ideas over time
  A17: Narrative Hook      — compelling opening lines
  A18: Unanswered Question — knowledge frontiers

Panel review (Merlin Sheldrake, Anil Seth, Robin Wall Kimmerer,
Ed Yong, Hanya Yanagihara, Katherine May):
- Each type should enable at least one new QA question pattern
- Progressive disclosure L0→L4 requires A17→A10→A12→theory→A11
- Writing guidelines: lead with human, give scale, show the seam

Usage:
    from src.models.extended_annotations import SurpriseFlag, DesignImplication
    
    surprise = SurpriseFlag(
        finding_id="...",
        common_assumption="Nature always reduces stress",
        actual_finding="Dense vegetation increases anxiety near crime hotspots",
        surprise_level=0.8,
    )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import json


class ExtendedAnnotationType(Enum):
    """Extended annotation types A9–A18."""
    SURPRISE_FLAG = "surprise_flag"
    DESIGN_IMPLICATION = "design_implication"
    DISPUTE = "dispute"
    ANALOGICAL_BRIDGE = "analogical_bridge"
    REPLICATION_STATUS = "replication_status"
    EFFECT_MAGNITUDE = "effect_magnitude"
    CROSS_DOMAIN = "cross_domain"
    HISTORICAL_CONTEXT = "historical_context"
    NARRATIVE_HOOK = "narrative_hook"
    UNANSWERED_QUESTION = "unanswered_question"


# =============================================================================
# A9: Surprise Flag
# =============================================================================

@dataclass
class SurpriseFlag:
    """A9: Marks counterintuitive findings that challenge common assumptions."""
    finding_id: str
    common_assumption: str         # What most people would expect
    actual_finding: str            # What the evidence actually shows
    surprise_level: float = 0.5   # 0-1, how counterintuitive
    why_surprising: str = ""       # Brief explanation of what this overturns
    domain: str = ""               # Which domain this surprises in
    
    def to_dict(self) -> Dict:
        return {
            "type": ExtendedAnnotationType.SURPRISE_FLAG.value,
            "finding_id": self.finding_id,
            "common_assumption": self.common_assumption,
            "actual_finding": self.actual_finding,
            "surprise_level": self.surprise_level,
            "why_surprising": self.why_surprising,
            "domain": self.domain,
        }


# =============================================================================
# A10: Design Implication
# =============================================================================

class CostTier(Enum):
    ZERO = "zero"        # No cost (behavioral change)
    LOW = "low"          # Under $1k (paint, plants, blinds)
    MEDIUM = "medium"    # $1k-10k (lighting, furniture)
    HIGH = "high"        # $10k+ (structural, HVAC)


@dataclass
class DesignImplication:
    """A10: Translates a finding into actionable design guidance."""
    finding_id: str
    recommendation: str            # Clear, actionable statement
    parameter: Optional[Dict] = None  # {"name": "CCT", "value": "2700-3000K", "unit": "Kelvin"}
    confidence: float = 0.5
    caveats: List[str] = field(default_factory=list)
    cost_tier: str = "medium"
    population_scope: str = ""     # Who this applies to
    space_scope: str = ""          # What kind of space
    
    def to_dict(self) -> Dict:
        return {
            "type": ExtendedAnnotationType.DESIGN_IMPLICATION.value,
            "finding_id": self.finding_id,
            "recommendation": self.recommendation,
            "parameter": self.parameter,
            "confidence": self.confidence,
            "caveats": self.caveats,
            "cost_tier": self.cost_tier,
            "population_scope": self.population_scope,
            "space_scope": self.space_scope,
        }


# =============================================================================
# A11: Controversy / Dispute
# =============================================================================

@dataclass
class DisputePosition:
    """One side of an active dispute."""
    position: str
    proponents: List[str]
    evidence_strength: float = 0.5
    key_evidence: str = ""


@dataclass
class Dispute:
    """A11: Marks where researchers actively disagree."""
    claim: str
    positions: List[DisputePosition] = field(default_factory=list)
    status: str = "active"  # active | leaning | resolved
    what_would_resolve: str = ""  # What experiment/evidence would settle it
    domain: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "type": ExtendedAnnotationType.DISPUTE.value,
            "claim": self.claim,
            "positions": [
                {"position": p.position, "proponents": p.proponents,
                 "evidence_strength": p.evidence_strength, "key_evidence": p.key_evidence}
                for p in self.positions
            ],
            "status": self.status,
            "what_would_resolve": self.what_would_resolve,
            "domain": self.domain,
        }


# =============================================================================
# A12: Analogical Bridge
# =============================================================================

@dataclass
class AnalogicalBridge:
    """A12: Connects technical concepts to everyday experience."""
    technical_concept: str
    everyday_analogy: str
    analogy_quality: float = 0.5     # How well does it actually map
    where_analogy_breaks: str = ""   # Intellectual honesty
    target_audience: str = "general"  # general | designer | student | researcher
    
    def to_dict(self) -> Dict:
        return {
            "type": ExtendedAnnotationType.ANALOGICAL_BRIDGE.value,
            "technical_concept": self.technical_concept,
            "everyday_analogy": self.everyday_analogy,
            "analogy_quality": self.analogy_quality,
            "where_analogy_breaks": self.where_analogy_breaks,
            "target_audience": self.target_audience,
        }


# =============================================================================
# A13: Replication Status
# =============================================================================

@dataclass
class ReplicationEntry:
    """One replication attempt."""
    doi: str = ""
    n: int = 0
    year: int = 0
    result: str = "unknown"  # full | partial | failed | conceptual
    note: str = ""


@dataclass
class ReplicationStatus:
    """A13: Tracks replication history for key findings."""
    finding_id: str
    original_study: Dict = field(default_factory=dict)  # {doi, n, year}
    replications: List[ReplicationEntry] = field(default_factory=list)
    overall_status: str = "unreplicated"  # unreplicated | partially | fully | failed
    robustness_score: float = 0.5     # 0-1 composite
    
    def to_dict(self) -> Dict:
        return {
            "type": ExtendedAnnotationType.REPLICATION_STATUS.value,
            "finding_id": self.finding_id,
            "original_study": self.original_study,
            "replications": [
                {"doi": r.doi, "n": r.n, "year": r.year, "result": r.result, "note": r.note}
                for r in self.replications
            ],
            "overall_status": self.overall_status,
            "robustness_score": self.robustness_score,
        }


# =============================================================================
# A14: Effect Magnitude
# =============================================================================

@dataclass
class EffectMagnitude:
    """A14: Human-interpretable effect size."""
    finding_id: str
    cohens_d: Optional[float] = None
    odds_ratio: Optional[float] = None
    r_squared: Optional[float] = None
    human_scale: str = ""           # "Like the difference between a library and a café"
    nnt: Optional[int] = None       # Number needed to treat
    nnt_explanation: str = ""
    practical_significance: str = "unknown"  # trivial | small | medium | large | transformative
    
    def to_dict(self) -> Dict:
        return {
            "type": ExtendedAnnotationType.EFFECT_MAGNITUDE.value,
            "finding_id": self.finding_id,
            "cohens_d": self.cohens_d,
            "odds_ratio": self.odds_ratio,
            "r_squared": self.r_squared,
            "human_scale": self.human_scale,
            "nnt": self.nnt,
            "nnt_explanation": self.nnt_explanation,
            "practical_significance": self.practical_significance,
        }


# =============================================================================
# A15: Cross-Domain Connection
# =============================================================================

@dataclass
class CrossDomainLink:
    """A15: Connects findings across disciplinary boundaries."""
    home_domain: str                 # e.g. "environmental_psychology"
    connected_domain: str            # e.g. "neuroscience"
    connection: str                  # What's the bridge?
    connection_strength: float = 0.5
    implication: str = ""            # What does this connection mean?
    reference_doi: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "type": ExtendedAnnotationType.CROSS_DOMAIN.value,
            "home_domain": self.home_domain,
            "connected_domain": self.connected_domain,
            "connection": self.connection,
            "connection_strength": self.connection_strength,
            "implication": self.implication,
            "reference_doi": self.reference_doi,
        }


# =============================================================================
# A16: Historical Context
# =============================================================================

@dataclass
class TimelineEvent:
    """One event in a concept's history."""
    year: int
    event: str
    significance: str = ""


@dataclass
class HistoricalContext:
    """A16: Tracks how ideas evolved over time."""
    concept: str
    timeline: List[TimelineEvent] = field(default_factory=list)
    paradigm_shifts: List[str] = field(default_factory=list)
    current_status: str = ""  # Where things stand now
    
    def to_dict(self) -> Dict:
        return {
            "type": ExtendedAnnotationType.HISTORICAL_CONTEXT.value,
            "concept": self.concept,
            "timeline": [
                {"year": e.year, "event": e.event, "significance": e.significance}
                for e in self.timeline
            ],
            "paradigm_shifts": self.paradigm_shifts,
            "current_status": self.current_status,
        }


# =============================================================================
# A17: Narrative Hook
# =============================================================================

class HookType(Enum):
    ORIGIN_STORY = "origin_story"      # How the idea was born
    SURPRISING_FACT = "surprising_fact"  # Counterintuitive opener
    HUMAN_MOMENT = "human_moment"       # A person's experience
    QUESTION = "question"               # Opens with a puzzle
    CONTRAST = "contrast"               # Before/after, old/new
    SENSORY = "sensory"                 # Puts you in the scene


@dataclass
class NarrativeHook:
    """A17: Compelling opening line for progressive disclosure."""
    hook: str                          # The actual text
    finding_id: str = ""
    hook_type: str = "surprising_fact"
    engagement_score: float = 0.5      # Predicted reader engagement
    target_audience: str = "general"
    
    def to_dict(self) -> Dict:
        return {
            "type": ExtendedAnnotationType.NARRATIVE_HOOK.value,
            "hook": self.hook,
            "finding_id": self.finding_id,
            "hook_type": self.hook_type,
            "engagement_score": self.engagement_score,
            "target_audience": self.target_audience,
        }


# =============================================================================
# A18: Unanswered Question
# =============================================================================

@dataclass
class UnansweredQuestion:
    """A18: Knowledge frontiers — what we don't know yet."""
    domain: str
    question: str
    why_important: str = ""
    what_would_it_take: str = ""       # What study/data would answer this
    estimated_difficulty: str = "medium"  # easy | medium | hard | moonshot
    related_theories: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "type": ExtendedAnnotationType.UNANSWERED_QUESTION.value,
            "domain": self.domain,
            "question": self.question,
            "why_important": self.why_important,
            "what_would_it_take": self.what_would_it_take,
            "estimated_difficulty": self.estimated_difficulty,
            "related_theories": self.related_theories,
        }


# =============================================================================
# Extended Annotation Set
# =============================================================================

@dataclass
class ExtendedAnnotationSet:
    """Complete set of A9-A18 annotations for a finding or template."""
    target_id: str
    surprises: List[SurpriseFlag] = field(default_factory=list)
    design_implications: List[DesignImplication] = field(default_factory=list)
    disputes: List[Dispute] = field(default_factory=list)
    analogies: List[AnalogicalBridge] = field(default_factory=list)
    replication: Optional[ReplicationStatus] = None
    effect_magnitude: Optional[EffectMagnitude] = None
    cross_domain: List[CrossDomainLink] = field(default_factory=list)
    history: Optional[HistoricalContext] = None
    hooks: List[NarrativeHook] = field(default_factory=list)
    unanswered: List[UnansweredQuestion] = field(default_factory=list)
    
    def to_json(self) -> str:
        data = {"target_id": self.target_id}
        if self.surprises:
            data["surprises"] = [s.to_dict() for s in self.surprises]
        if self.design_implications:
            data["design_implications"] = [d.to_dict() for d in self.design_implications]
        if self.disputes:
            data["disputes"] = [d.to_dict() for d in self.disputes]
        if self.analogies:
            data["analogies"] = [a.to_dict() for a in self.analogies]
        if self.replication:
            data["replication"] = self.replication.to_dict()
        if self.effect_magnitude:
            data["effect_magnitude"] = self.effect_magnitude.to_dict()
        if self.cross_domain:
            data["cross_domain"] = [c.to_dict() for c in self.cross_domain]
        if self.history:
            data["history"] = self.history.to_dict()
        if self.hooks:
            data["hooks"] = [h.to_dict() for h in self.hooks]
        if self.unanswered:
            data["unanswered"] = [u.to_dict() for u in self.unanswered]
        return json.dumps(data, indent=2)
    
    @property
    def annotation_count(self) -> int:
        """Count total annotations in this set."""
        return (
            len(self.surprises) + len(self.design_implications) +
            len(self.disputes) + len(self.analogies) +
            (1 if self.replication else 0) + (1 if self.effect_magnitude else 0) +
            len(self.cross_domain) + (1 if self.history else 0) +
            len(self.hooks) + len(self.unanswered)
        )
    
    @property
    def disclosure_levels_available(self) -> List[str]:
        """Which progressive disclosure levels can be served."""
        levels = []
        if self.hooks:
            levels.append("L0_hook")
        if self.design_implications or self.effect_magnitude:
            levels.append("L1_finding")
        if self.analogies:
            levels.append("L2_mechanism")
        if self.disputes or self.unanswered:
            levels.append("L4_frontier")
        return levels
