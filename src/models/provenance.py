"""
Article Eater - Provenance Model
ARCH-4 Sprint 1.2: Data Model Implementation

Provenance tracking for beliefs: sources, grounding chain, and experiential basis.
Per Haack's foundherentism - beliefs must be grounded in experience AND cohere.

Reference: contracts/schemas/provenance.v1.schema.json
Reference: contracts/schemas/experiential_claim.v1.schema.json
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import re


# ============================================================
# ENUMS
# ============================================================

class SourceType(Enum):
    """Type of source for a belief."""
    PAPER = "PAPER"
    OBSERVATION = "OBSERVATION"
    INFERENCE = "INFERENCE"
    THEORY = "THEORY"
    EXPERT_JUDGMENT = "EXPERT_JUDGMENT"
    META_ANALYSIS = "META_ANALYSIS"


class StudyType(Enum):
    """Study design type for empirical sources."""
    EXPERIMENTAL = "EXPERIMENTAL"
    OBSERVATIONAL = "OBSERVATIONAL"
    META_ANALYSIS = "META_ANALYSIS"
    THEORETICAL = "THEORETICAL"
    REVIEW = "REVIEW"


class Directness(Enum):
    """How directly a belief connects to experience."""
    DIRECT = "DIRECT"  # Observational - directly grounded
    ONE_HOP = "ONE_HOP"  # One inference step from observation
    MULTI_HOP = "MULTI_HOP"  # Multiple inference steps
    THEORETICAL = "THEORETICAL"  # No direct chain to observation


class JustificationStatus(Enum):
    """
    Haack justification status.

    WELL_JUSTIFIED: Both grounded in experience AND coherent with other beliefs
    GROUNDED_ONLY: Has experiential basis but low coherence
    COHERENT_ONLY: Coherent but poorly grounded (WARNING - per Haack this is dangerous)
    UNJUSTIFIED: Neither grounded nor coherent
    """
    WELL_JUSTIFIED = "WELL_JUSTIFIED"
    GROUNDED_ONLY = "GROUNDED_ONLY"
    COHERENT_ONLY = "COHERENT_ONLY"  # WARNING state per panel review
    UNJUSTIFIED = "UNJUSTIFIED"


class ObservationType(Enum):
    """Type of observation for experiential claims."""
    MEASUREMENT = "MEASUREMENT"
    BEHAVIORAL = "BEHAVIORAL"
    SELF_REPORT = "SELF_REPORT"
    PHYSIOLOGICAL = "PHYSIOLOGICAL"
    ENVIRONMENTAL = "ENVIRONMENTAL"
    DEMOGRAPHIC = "DEMOGRAPHIC"


class ObservationDirectness(Enum):
    """How directly something was observed."""
    DIRECT_OBSERVATION = "DIRECT_OBSERVATION"  # Seen/heard directly
    INSTRUMENT_MEDIATED = "INSTRUMENT_MEDIATED"  # Via measurement device
    INFERENCE_CLOSE = "INFERENCE_CLOSE"  # One inference step
    INFERENCE_DISTANT = "INFERENCE_DISTANT"  # Multiple inference steps


class Revisability(Enum):
    """How revisable an experiential claim is (per Haack: all are revisable)."""
    VERY_LOW = "VERY_LOW"  # Would require extraordinary evidence
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"


# ============================================================
# EXPERIENTIAL CLAIM
# ============================================================

@dataclass
class ConfidenceInterval:
    """Statistical confidence interval."""
    lower: float
    upper: float
    level: float = 0.95

    def to_dict(self) -> Dict[str, Any]:
        return {'lower': self.lower, 'upper': self.upper, 'level': self.level}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConfidenceInterval':
        return cls(
            lower=data['lower'],
            upper=data['upper'],
            level=data.get('level', 0.95)
        )


@dataclass
class Observer:
    """Who made an observation."""
    type: str  # RESEARCHER, PARTICIPANT, INSTRUMENT, THIRD_PARTY
    expertise: Optional[str] = None
    training: Optional[str] = None
    reliability: Optional[float] = None  # Inter-rater reliability if applicable

    def to_dict(self) -> Dict[str, Any]:
        result = {'type': self.type}
        if self.expertise:
            result['expertise'] = self.expertise
        if self.training:
            result['training'] = self.training
        if self.reliability is not None:
            result['reliability'] = self.reliability
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Observer':
        return cls(
            type=data.get('type', 'RESEARCHER'),
            expertise=data.get('expertise'),
            training=data.get('training'),
            reliability=data.get('reliability')
        )


@dataclass
class QuantitativeResult:
    """Quantitative result from an observation."""
    value: float
    statistic_type: str  # MEAN, MEDIAN, PROPORTION, CORRELATION, DIFFERENCE, EFFECT_SIZE
    confidence_interval: Optional[ConfidenceInterval] = None
    p_value: Optional[float] = None
    sample_size: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'value': self.value,
            'statistic_type': self.statistic_type
        }
        if self.confidence_interval:
            result['confidence_interval'] = self.confidence_interval.to_dict()
        if self.p_value is not None:
            result['p_value'] = self.p_value
        if self.sample_size is not None:
            result['sample_size'] = self.sample_size
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuantitativeResult':
        ci = None
        if 'confidence_interval' in data:
            ci = ConfidenceInterval.from_dict(data['confidence_interval'])
        return cls(
            value=data['value'],
            statistic_type=data['statistic_type'],
            confidence_interval=ci,
            p_value=data.get('p_value'),
            sample_size=data.get('sample_size')
        )


@dataclass
class ExperientialClaim:
    """
    A claim directly grounded in experience/observation.

    Per Haack's foundherentism: these form the anchors that prevent
    pure coherentism from floating free of reality. Not foundational
    in the classical sense (they can be revised), but they provide grounding.
    """
    claim_id: str
    content: str
    observation_type: ObservationType
    directness: ObservationDirectness
    observer: Optional[Observer] = None
    quantitative_result: Optional[QuantitativeResult] = None
    source_doi: Optional[str] = None
    source_citation: Optional[str] = None
    grounding_strength: float = 0.8  # How strongly this anchors to reality
    revisability: Revisability = Revisability.LOW
    contested: bool = False
    contesting_claims: List[str] = field(default_factory=list)

    # Validation pattern for claim_id
    CLAIM_ID_PATTERN = re.compile(r'^exp\.[a-z0-9_]+$')

    def __post_init__(self):
        """Validate and convert enums."""
        if isinstance(self.observation_type, str):
            self.observation_type = ObservationType(self.observation_type)
        if isinstance(self.directness, str):
            self.directness = ObservationDirectness(self.directness)
        if isinstance(self.revisability, str):
            self.revisability = Revisability(self.revisability)

        # Per panel review: DIRECT_OBSERVATION should have grounding >= 0.8
        if self.directness == ObservationDirectness.DIRECT_OBSERVATION:
            self.grounding_strength = max(0.8, self.grounding_strength)

    @property
    def is_anchor(self) -> bool:
        """
        Whether this claim serves as a grounding anchor.
        Per panel review: add explicit anchor designation.
        """
        return (
            self.directness in (
                ObservationDirectness.DIRECT_OBSERVATION,
                ObservationDirectness.INSTRUMENT_MEDIATED
            ) and
            self.grounding_strength >= 0.7 and
            not self.contested
        )

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'claim_id': self.claim_id,
            'content': self.content,
            'observation_type': self.observation_type.value,
            'directness': self.directness.value,
            'grounding_strength': self.grounding_strength,
            'revisability': self.revisability.value,
            'contested': self.contested,
            'is_anchor': self.is_anchor
        }
        if self.observer:
            result['observer'] = self.observer.to_dict()
        if self.quantitative_result:
            result['quantitative_result'] = self.quantitative_result.to_dict()
        if self.source_doi:
            result['source_doi'] = self.source_doi
        if self.source_citation:
            result['source_citation'] = self.source_citation
        if self.contesting_claims:
            result['contesting_claims'] = self.contesting_claims
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExperientialClaim':
        observer = None
        if 'observer' in data:
            observer = Observer.from_dict(data['observer'])

        quant_result = None
        if 'quantitative_result' in data:
            quant_result = QuantitativeResult.from_dict(data['quantitative_result'])

        return cls(
            claim_id=data['claim_id'],
            content=data['content'],
            observation_type=ObservationType(data['observation_type']),
            directness=ObservationDirectness(data['directness']),
            observer=observer,
            quantitative_result=quant_result,
            source_doi=data.get('source_doi'),
            source_citation=data.get('source_citation'),
            grounding_strength=data.get('grounding_strength', 0.8),
            revisability=Revisability(data.get('revisability', 'LOW')),
            contested=data.get('contested', False),
            contesting_claims=data.get('contesting_claims', [])
        )


# ============================================================
# SOURCE
# ============================================================

@dataclass
class Source:
    """A source from which a belief derives."""
    source_type: SourceType
    reference: str
    doi: Optional[str] = None
    reliability: Optional[float] = None
    study_type: Optional[StudyType] = None
    sample_size: Optional[int] = None
    effect_size: Optional[float] = None
    confidence_interval: Optional[ConfidenceInterval] = None

    def __post_init__(self):
        if isinstance(self.source_type, str):
            self.source_type = SourceType(self.source_type)
        if isinstance(self.study_type, str):
            self.study_type = StudyType(self.study_type)

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'source_type': self.source_type.value,
            'reference': self.reference
        }
        if self.doi:
            result['doi'] = self.doi
        if self.reliability is not None:
            result['reliability'] = self.reliability
        if self.study_type:
            result['study_type'] = self.study_type.value
        if self.sample_size is not None:
            result['sample_size'] = self.sample_size
        if self.effect_size is not None:
            result['effect_size'] = self.effect_size
        if self.confidence_interval:
            result['confidence_interval'] = self.confidence_interval.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Source':
        ci = None
        if 'confidence_interval' in data:
            ci = ConfidenceInterval.from_dict(data['confidence_interval'])

        study_type = None
        if 'study_type' in data:
            study_type = StudyType(data['study_type'])

        return cls(
            source_type=SourceType(data['source_type']),
            reference=data['reference'],
            doi=data.get('doi'),
            reliability=data.get('reliability'),
            study_type=study_type,
            sample_size=data.get('sample_size'),
            effect_size=data.get('effect_size'),
            confidence_interval=ci
        )


# ============================================================
# CROSSWORD POSITION (HAACK)
# ============================================================

@dataclass
class CrosswordPosition:
    """
    Position in Haack's crossword metaphor.

    Like a crossword puzzle, beliefs interlock: each belief both
    supports and is supported by others. Well-integrated beliefs
    (many crossing points) are more justified.
    """
    supports: List[str] = field(default_factory=list)  # Belief IDs this supports
    supported_by: List[str] = field(default_factory=list)  # Belief IDs supporting this
    integration_score: float = 0.0  # How well integrated (0-1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'supports': self.supports,
            'supported_by': self.supported_by,
            'integration_score': self.integration_score
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CrosswordPosition':
        return cls(
            supports=data.get('supports', []),
            supported_by=data.get('supported_by', []),
            integration_score=data.get('integration_score', 0.0)
        )

    def compute_integration(self) -> float:
        """Compute integration score from support links."""
        total_links = len(self.supports) + len(self.supported_by)
        # Diminishing returns: sqrt scaling
        self.integration_score = min(1.0, (total_links ** 0.5) / 4)
        return self.integration_score


# ============================================================
# PROVENANCE
# ============================================================

@dataclass
class Provenance:
    """
    Complete provenance for a belief.

    Tracks:
    - Sources (where the belief came from)
    - Grounding (how connected to experience)
    - Crossword position (how integrated with other beliefs)
    - Justification status (Haack's foundherentist categories)
    """
    sources: List[Source] = field(default_factory=list)
    grounding_score: float = 0.0  # 0-1, higher = more grounded
    grounding_chain: List[str] = field(default_factory=list)  # Belief IDs to experience
    experiential_claims: List[str] = field(default_factory=list)  # ExperientialClaim IDs
    directness: Directness = Directness.THEORETICAL
    coherence_contribution: float = 0.0  # How much this contributes to web coherence
    justification_status: JustificationStatus = JustificationStatus.UNJUSTIFIED
    crossword_position: Optional[CrosswordPosition] = None
    is_anchor: bool = False  # Per panel review: explicit anchor designation

    # Extraction metadata (Article Eater specific)
    extracted_from: Optional[str] = None
    extraction_date: Optional[datetime] = None
    extraction_confidence: Optional[float] = None
    human_verified: bool = False

    def __post_init__(self):
        """Convert enums and validate."""
        if isinstance(self.directness, str):
            self.directness = Directness(self.directness)
        if isinstance(self.justification_status, str):
            self.justification_status = JustificationStatus(self.justification_status)

        # Per panel review: COHERENT_ONLY should generate warning
        if self.justification_status == JustificationStatus.COHERENT_ONLY:
            # In production, this would trigger a system warning
            pass

    def compute_justification_status(self, coherence_threshold: float = 0.5,
                                     grounding_threshold: float = 0.3) -> JustificationStatus:
        """
        Compute Haack justification status from grounding and coherence.

        Per Haack: need BOTH grounding AND coherence for full justification.
        High coherence cannot compensate for zero grounding.
        """
        has_grounding = self.grounding_score >= grounding_threshold
        has_coherence = self.coherence_contribution >= coherence_threshold

        if has_grounding and has_coherence:
            self.justification_status = JustificationStatus.WELL_JUSTIFIED
        elif has_grounding and not has_coherence:
            self.justification_status = JustificationStatus.GROUNDED_ONLY
        elif has_coherence and not has_grounding:
            # WARNING: This is the dangerous state per Haack
            self.justification_status = JustificationStatus.COHERENT_ONLY
        else:
            self.justification_status = JustificationStatus.UNJUSTIFIED

        return self.justification_status

    def add_source(self, source: Source):
        """Add a source and update grounding if applicable."""
        self.sources.append(source)

        # Update grounding based on source type
        if source.source_type == SourceType.OBSERVATION:
            self.grounding_score = max(self.grounding_score, 0.9)
            self.directness = Directness.DIRECT
        elif source.source_type == SourceType.PAPER:
            if source.study_type == StudyType.EXPERIMENTAL:
                self.grounding_score = max(self.grounding_score, 0.7)
                if self.directness == Directness.THEORETICAL:
                    self.directness = Directness.ONE_HOP

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'sources': [s.to_dict() for s in self.sources],
            'grounding_score': self.grounding_score,
            'grounding_chain': self.grounding_chain,
            'experiential_claims': self.experiential_claims,
            'directness': self.directness.value,
            'coherence_contribution': self.coherence_contribution,
            'justification_status': self.justification_status.value,
            'is_anchor': self.is_anchor
        }

        if self.crossword_position:
            result['crossword_position'] = self.crossword_position.to_dict()
        if self.extracted_from:
            result['extraction_metadata'] = {
                'extracted_from': self.extracted_from,
                'extraction_date': self.extraction_date.isoformat() if self.extraction_date else None,
                'extraction_confidence': self.extraction_confidence,
                'human_verified': self.human_verified
            }

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Provenance':
        sources = [Source.from_dict(s) for s in data.get('sources', [])]

        crossword = None
        if 'crossword_position' in data:
            crossword = CrosswordPosition.from_dict(data['crossword_position'])

        extraction_date = None
        extracted_from = None
        extraction_confidence = None
        human_verified = False

        if 'extraction_metadata' in data:
            em = data['extraction_metadata']
            extracted_from = em.get('extracted_from')
            if em.get('extraction_date'):
                extraction_date = datetime.fromisoformat(em['extraction_date'])
            extraction_confidence = em.get('extraction_confidence')
            human_verified = em.get('human_verified', False)

        return cls(
            sources=sources,
            grounding_score=data.get('grounding_score', 0.0),
            grounding_chain=data.get('grounding_chain', []),
            experiential_claims=data.get('experiential_claims', []),
            directness=Directness(data.get('directness', 'THEORETICAL')),
            coherence_contribution=data.get('coherence_contribution', 0.0),
            justification_status=JustificationStatus(
                data.get('justification_status', 'UNJUSTIFIED')
            ),
            crossword_position=crossword,
            is_anchor=data.get('is_anchor', False),
            extracted_from=extracted_from,
            extraction_date=extraction_date,
            extraction_confidence=extraction_confidence,
            human_verified=human_verified
        )

    @classmethod
    def from_legacy_belief(cls, belief_data: Dict[str, Any],
                           level: str = None) -> 'Provenance':
        """
        Create Provenance from legacy belief format.
        Used for migration from v1 to v2.
        """
        # Map level to directness and grounding
        level_to_directness = {
            'OBSERVATIONAL': Directness.DIRECT,
            'EMPIRICAL': Directness.ONE_HOP,
            'INTERMEDIATE': Directness.MULTI_HOP,
            'THEORETICAL': Directness.THEORETICAL
        }

        level_to_grounding = {
            'OBSERVATIONAL': 1.0,
            'EMPIRICAL': 0.7,
            'INTERMEDIATE': 0.4,
            'THEORETICAL': 0.2
        }

        directness = level_to_directness.get(level, Directness.THEORETICAL)
        grounding = level_to_grounding.get(level, 0.2)

        # Extract source if available
        sources = []
        if 'source' in belief_data:
            sources.append(Source(
                source_type=SourceType.PAPER,
                reference=belief_data['source']
            ))

        return cls(
            sources=sources,
            grounding_score=grounding,
            directness=directness,
            justification_status=JustificationStatus.WELL_JUSTIFIED  # Assume for migration
        )


# ============================================================
# EXPERIENTIAL CLAIM REGISTRY
# ============================================================

class ExperientialClaimRegistry:
    """
    Registry for managing experiential claims.
    Provides lookup and conflict detection.
    """

    def __init__(self):
        self._claims: Dict[str, ExperientialClaim] = {}

    def register(self, claim: ExperientialClaim):
        """Register an experiential claim."""
        self._claims[claim.claim_id] = claim

    def get(self, claim_id: str) -> Optional[ExperientialClaim]:
        """Get a claim by ID."""
        return self._claims.get(claim_id)

    def find_anchors(self) -> List[ExperientialClaim]:
        """Find all claims that serve as grounding anchors."""
        return [c for c in self._claims.values() if c.is_anchor]

    def find_contested(self) -> List[ExperientialClaim]:
        """Find all contested claims."""
        return [c for c in self._claims.values() if c.contested]

    def mark_contested(self, claim_id: str, contesting_claim_id: str):
        """Mark a claim as contested by another claim."""
        if claim_id in self._claims:
            claim = self._claims[claim_id]
            claim.contested = True
            if contesting_claim_id not in claim.contesting_claims:
                claim.contesting_claims.append(contesting_claim_id)

    def to_dict(self) -> Dict[str, Any]:
        return {cid: c.to_dict() for cid, c in self._claims.items()}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExperientialClaimRegistry':
        registry = cls()
        for claim_data in data.values():
            registry.register(ExperientialClaim.from_dict(claim_data))
        return registry
