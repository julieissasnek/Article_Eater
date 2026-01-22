"""
Article Eater - Bridge Warrants
===============================

Sprint 3: Bridge Warrant Implementation (Post-Expert Panel Review 2026-01-18)

Bridge warrants are explicit assumptions that license the transfer of knowledge
from one domain to another. They are load-bearing epistemic structures that
determine whether evidence transfers across domains.

The term originates in Cartwright's work on nomological machines (1999) and
has been developed in the context of evidence-based policy (Cartwright & Hardie, 2012).

Bridge Types (from Cartwright's typology, extended):
- MECHANISM: Same causal pathway operates in both domains
  Example: Amygdala activation for angular objects -> angular rooms
- FUNCTIONAL: Same functional outcome despite different mechanisms
  Example: Objects and rooms both evoke negative affect, but via different pathways
- ANALOGICAL: Structural similarity suggests similar effects
  Example: Fractal patterns in nature -> fractal patterns in architecture
- CONSTITUTIVE: Target domain is literally composed of source domain
  Example: Room corners are composed of angular objects
- CAPACITY: Entity has stable capacity independent of mechanism (F2.1 per Cartwright)
  Example: "Plants have the capacity to reduce stress" - doesn't specify mechanism

Bridge-Weighted Credence Formula:
    P(CNFA effect) = P(parent theory) x P(bridge) x P(CNFA-specific)

Default P(bridge) values:
- Constitutive: 0.85 (target literally contains source; transfer near-certain)
- Mechanism: 0.60 (mechanisms often conserved, but scale/context can disrupt)
- Functional: 0.50 (functions often achieved by different mechanisms)
- Analogical: 0.35 (analogies suggestive but frequently fail under scrutiny)

Bridge Lifecycle:
    hypothesized -> supported (if evidence_for grows)
                 -> contested (if evidence_for AND evidence_against)
                 -> failed (if disconfirming evidence strong)
                 -> revised (if downgraded to different type)

References:
- Cartwright, N. (1999). The Dappled World. Cambridge University Press.
- Cartwright, N., & Hardie, J. (2012). Evidence-Based Policy. Oxford University Press.
- Pearl, J., & Bareinboim, E. (2014). External validity: From do-calculus to
  transportability across populations. Statistical Science, 29(4), 579-595.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Set
from enum import Enum
from datetime import datetime, timezone
from pathlib import Path
import json
import logging
import uuid

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================

class BridgeType(Enum):
    """Types of bridge warrants."""
    MECHANISM = "mechanism"        # Same causal pathway in both domains
    FUNCTIONAL = "functional"      # Same outcome, different mechanisms
    ANALOGICAL = "analogical"      # Structural similarity
    CONSTITUTIVE = "constitutive"  # Target contains source
    # F2.1: Capacity bridge type per Cartwright (ruthless review 2026-01-22)
    CAPACITY = "capacity"          # Entity has stable capacity (not mechanism-based)
    EMPIRICAL_COVARIANCE = "empirical_covariance"  # Sprint 8: Co-tested in same study


class BridgeStatus(Enum):
    """Status of a bridge warrant in its lifecycle."""
    HYPOTHESIZED = "hypothesized"  # Machine-proposed, unconfirmed
    SUPPORTED = "supported"        # Evidence_for > evidence_against
    CONTESTED = "contested"        # Both evidence_for AND evidence_against
    FAILED = "failed"              # Disconfirming evidence strong
    REVISED = "revised"            # Downgraded to different type


class ConfidenceSource(Enum):
    """How confidence was determined."""
    DEFAULT = "default"                # From bridge type defaults
    LLM_INFERRED = "llm_inferred"      # LLM proposed the confidence
    HUMAN_ASSIGNED = "human_assigned"  # HITL review
    EVIDENCE_UPDATED = "evidence_updated"  # Updated based on evidence


# Default P(bridge) values per expert panel (2026-01-18)
# F2.1: Updated per Cartwright (ruthless review 2026-01-22):
#   - CONSTITUTIVE reduced from 0.85 to 0.75 (definitional bridges can be contested)
#   - CAPACITY added at 0.45 (entities have stable capacities, but often unfalsifiable)
# Panel validation (2026-01-22): CAPACITY reduced from 0.55 to 0.45 per Cartwright
DEFAULT_BRIDGE_CONFIDENCE: Dict[BridgeType, float] = {
    BridgeType.CONSTITUTIVE: 0.75,  # Target literally contains source (reduced per Cartwright)
    BridgeType.MECHANISM: 0.60,     # Mechanisms often conserved
    BridgeType.CAPACITY: 0.45,      # Entity has stable capacity - reduced per Cartwright panel validation
    BridgeType.FUNCTIONAL: 0.50,    # Functions via different mechanisms
    BridgeType.ANALOGICAL: 0.35,    # Suggestive but often fail
    BridgeType.EMPIRICAL_COVARIANCE: 0.60,  # Sprint 8: Co-tested in same study
}


# =============================================================================
# BRIDGE WARRANT DATA CLASS
# =============================================================================

@dataclass
class FailureRecord:
    """Record of bridge failure."""
    failed_at: datetime
    disconfirming_evidence: List[str]
    failure_type: str
    suggested_revision: Optional[BridgeType] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "failed_at": self.failed_at.isoformat(),
            "disconfirming_evidence": self.disconfirming_evidence,
            "failure_type": self.failure_type,
            "suggested_revision": self.suggested_revision.value if self.suggested_revision else None
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'FailureRecord':
        return cls(
            failed_at=datetime.fromisoformat(d["failed_at"]),
            disconfirming_evidence=d.get("disconfirming_evidence", []),
            failure_type=d.get("failure_type", "unknown"),
            suggested_revision=BridgeType(d["suggested_revision"]) if d.get("suggested_revision") else None
        )


@dataclass
class Provenance:
    """Tracking information for the bridge warrant."""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "system:bridge_detector"
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "last_updated": self.last_updated.isoformat(),
            "version": self.version
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'Provenance':
        return cls(
            created_at=datetime.fromisoformat(d["created_at"]) if d.get("created_at") else datetime.now(timezone.utc),
            created_by=d.get("created_by", "system:bridge_detector"),
            last_updated=datetime.fromisoformat(d["last_updated"]) if d.get("last_updated") else datetime.now(timezone.utc),
            version=d.get("version", 1)
        )


@dataclass
class BridgeWarrant:
    """
    A bridge warrant licensing transfer of knowledge between domains.

    Bridge warrants are first-class entities in the epistemic system,
    not annotations on existing schemas. They reference beliefs by ID
    but are stored separately.
    """
    bridge_id: str
    source_domain: str
    target_domain: str
    bridge_type: BridgeType
    warrant_statement: str
    confidence: float
    status: BridgeStatus = BridgeStatus.HYPOTHESIZED

    # Optional fields
    assumed_mechanism: Optional[str] = None
    confidence_source: ConfidenceSource = ConfidenceSource.DEFAULT
    source_beliefs: List[str] = field(default_factory=list)
    target_beliefs: List[str] = field(default_factory=list)
    evidence_for: List[str] = field(default_factory=list)
    evidence_against: List[str] = field(default_factory=list)
    failure_record: Optional[FailureRecord] = None
    provenance: Provenance = field(default_factory=Provenance)
    voi_flag: bool = False
    bridged_credence_cache: Optional[float] = None

    def __post_init__(self):
        """Validate and normalize fields."""
        self.confidence = max(0.0, min(1.0, self.confidence))
        if not self.bridge_id.startswith("bridge:"):
            self.bridge_id = f"bridge:{self.bridge_id}"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary matching ae.bridge.v1 schema."""
        return {
            "schema": "ae.bridge.v1",
            "bridge_id": self.bridge_id,
            "source_domain": self.source_domain,
            "target_domain": self.target_domain,
            "bridge_type": self.bridge_type.value,
            "warrant_statement": self.warrant_statement,
            "assumed_mechanism": self.assumed_mechanism,
            "confidence": self.confidence,
            "confidence_source": self.confidence_source.value,
            "status": self.status.value,
            "source_beliefs": self.source_beliefs,
            "target_beliefs": self.target_beliefs,
            "evidence_for": self.evidence_for,
            "evidence_against": self.evidence_against,
            "failure_record": self.failure_record.to_dict() if self.failure_record else None,
            "provenance": self.provenance.to_dict(),
            "voi_flag": self.voi_flag,
            "bridged_credence_cache": self.bridged_credence_cache
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'BridgeWarrant':
        """Deserialize from dictionary."""
        failure_record = None
        if d.get("failure_record"):
            failure_record = FailureRecord.from_dict(d["failure_record"])

        provenance = Provenance()
        if d.get("provenance"):
            provenance = Provenance.from_dict(d["provenance"])

        return cls(
            bridge_id=d["bridge_id"],
            source_domain=d["source_domain"],
            target_domain=d["target_domain"],
            bridge_type=BridgeType(d["bridge_type"]),
            warrant_statement=d["warrant_statement"],
            assumed_mechanism=d.get("assumed_mechanism"),
            confidence=d["confidence"],
            confidence_source=ConfidenceSource(d.get("confidence_source", "default")),
            status=BridgeStatus(d.get("status", "hypothesized")),
            source_beliefs=d.get("source_beliefs", []),
            target_beliefs=d.get("target_beliefs", []),
            evidence_for=d.get("evidence_for", []),
            evidence_against=d.get("evidence_against", []),
            failure_record=failure_record,
            provenance=provenance,
            voi_flag=d.get("voi_flag", False),
            bridged_credence_cache=d.get("bridged_credence_cache")
        )

    def is_failed(self) -> bool:
        """Check if bridge has failed."""
        return self.status == BridgeStatus.FAILED

    def is_contested(self) -> bool:
        """Check if bridge is contested."""
        return self.status == BridgeStatus.CONTESTED

    def copy(self) -> 'BridgeWarrant':
        """Create a deep copy of this bridge."""
        return BridgeWarrant.from_dict(self.to_dict())


# =============================================================================
# BRIDGE REGISTRY
# =============================================================================

class BridgeRegistry:
    """
    Manages bridge warrant instances.

    Similar to TheoryRegistry, this provides CRUD operations for bridge
    warrants with indexing for efficient lookup.
    """

    def __init__(self):
        self.bridges: Dict[str, BridgeWarrant] = {}
        self._by_source_domain: Dict[str, List[str]] = {}
        self._by_target_domain: Dict[str, List[str]] = {}
        self._by_type: Dict[BridgeType, List[str]] = {bt: [] for bt in BridgeType}
        self._by_status: Dict[BridgeStatus, List[str]] = {bs: [] for bs in BridgeStatus}

    def add(self, bridge: BridgeWarrant) -> None:
        """Add a bridge to the registry."""
        if bridge.bridge_id in self.bridges:
            # Update existing
            self.remove(bridge.bridge_id)

        self.bridges[bridge.bridge_id] = bridge

        # Index by source domain
        if bridge.source_domain not in self._by_source_domain:
            self._by_source_domain[bridge.source_domain] = []
        self._by_source_domain[bridge.source_domain].append(bridge.bridge_id)

        # Index by target domain
        if bridge.target_domain not in self._by_target_domain:
            self._by_target_domain[bridge.target_domain] = []
        self._by_target_domain[bridge.target_domain].append(bridge.bridge_id)

        # Index by type and status
        self._by_type[bridge.bridge_type].append(bridge.bridge_id)
        self._by_status[bridge.status].append(bridge.bridge_id)

        logger.debug(f"Added bridge: {bridge.bridge_id} ({bridge.bridge_type.value})")

    def remove(self, bridge_id: str) -> Optional[BridgeWarrant]:
        """Remove a bridge from the registry."""
        if bridge_id not in self.bridges:
            return None

        bridge = self.bridges.pop(bridge_id)

        # Remove from indices
        if bridge.source_domain in self._by_source_domain:
            self._by_source_domain[bridge.source_domain] = [
                bid for bid in self._by_source_domain[bridge.source_domain]
                if bid != bridge_id
            ]
        if bridge.target_domain in self._by_target_domain:
            self._by_target_domain[bridge.target_domain] = [
                bid for bid in self._by_target_domain[bridge.target_domain]
                if bid != bridge_id
            ]
        self._by_type[bridge.bridge_type] = [
            bid for bid in self._by_type[bridge.bridge_type]
            if bid != bridge_id
        ]
        self._by_status[bridge.status] = [
            bid for bid in self._by_status[bridge.status]
            if bid != bridge_id
        ]

        return bridge

    def get(self, bridge_id: str) -> Optional[BridgeWarrant]:
        """Get a bridge by ID."""
        return self.bridges.get(bridge_id)

    def get_by_source_domain(self, domain: str) -> List[BridgeWarrant]:
        """Get all bridges originating from a domain."""
        bridge_ids = self._by_source_domain.get(domain, [])
        return [self.bridges[bid] for bid in bridge_ids if bid in self.bridges]

    def get_by_target_domain(self, domain: str) -> List[BridgeWarrant]:
        """Get all bridges targeting a domain."""
        bridge_ids = self._by_target_domain.get(domain, [])
        return [self.bridges[bid] for bid in bridge_ids if bid in self.bridges]

    def get_by_type(self, bridge_type: BridgeType) -> List[BridgeWarrant]:
        """Get all bridges of a given type."""
        bridge_ids = self._by_type.get(bridge_type, [])
        return [self.bridges[bid] for bid in bridge_ids if bid in self.bridges]

    def get_by_status(self, status: BridgeStatus) -> List[BridgeWarrant]:
        """Get all bridges with a given status."""
        bridge_ids = self._by_status.get(status, [])
        return [self.bridges[bid] for bid in bridge_ids if bid in self.bridges]

    def get_failed(self) -> List[BridgeWarrant]:
        """Get all failed bridges."""
        return self.get_by_status(BridgeStatus.FAILED)

    def get_contested(self) -> List[BridgeWarrant]:
        """Get all contested bridges."""
        return self.get_by_status(BridgeStatus.CONTESTED)

    def update_status(self, bridge_id: str, new_status: BridgeStatus) -> None:
        """Update the status of a bridge."""
        if bridge_id not in self.bridges:
            raise ValueError(f"Bridge not found: {bridge_id}")

        bridge = self.bridges[bridge_id]
        old_status = bridge.status

        # Update status indices
        self._by_status[old_status] = [
            bid for bid in self._by_status[old_status] if bid != bridge_id
        ]
        self._by_status[new_status].append(bridge_id)

        bridge.status = new_status
        bridge.provenance.last_updated = datetime.now(timezone.utc)
        bridge.provenance.version += 1

    def all(self) -> List[BridgeWarrant]:
        """Get all bridges."""
        return list(self.bridges.values())

    def to_jsonl(self, path: Path) -> int:
        """Export all bridges to JSONL file."""
        with open(path, 'w') as f:
            for bridge in self.bridges.values():
                f.write(json.dumps(bridge.to_dict()) + "\n")
        return len(self.bridges)

    @classmethod
    def from_jsonl(cls, path: Path) -> 'BridgeRegistry':
        """Load registry from JSONL file."""
        registry = cls()
        if not path.exists():
            return registry

        with open(path) as f:
            for line in f:
                if line.strip():
                    d = json.loads(line)
                    bridge = BridgeWarrant.from_dict(d)
                    registry.add(bridge)
        return registry


# =============================================================================
# BRIDGE CREATION AND MANAGEMENT FUNCTIONS
# =============================================================================

def create_bridge(
    source_domain: str,
    target_domain: str,
    bridge_type: BridgeType,
    warrant_statement: str,
    source_beliefs: Optional[List[str]] = None,
    target_beliefs: Optional[List[str]] = None,
    assumed_mechanism: Optional[str] = None,
    confidence: Optional[float] = None,
    confidence_source: ConfidenceSource = ConfidenceSource.DEFAULT,
    created_by: str = "system:bridge_detector"
) -> BridgeWarrant:
    """
    Create a new bridge warrant.

    Args:
        source_domain: Domain from which evidence originates
        target_domain: Domain to which evidence transfers
        bridge_type: Type of bridging assumption
        warrant_statement: Natural language statement of the bridge
        source_beliefs: Belief IDs from source domain
        target_beliefs: Belief IDs in target domain
        assumed_mechanism: For mechanism bridges, the conserved pathway
        confidence: Override default confidence (0-1)
        confidence_source: How confidence was determined
        created_by: Creator identifier

    Returns:
        BridgeWarrant instance
    """
    # Generate unique ID
    bridge_id = f"bridge:{source_domain}_{target_domain}_{uuid.uuid4().hex[:8]}"

    # Use default confidence if not specified
    if confidence is None:
        confidence = DEFAULT_BRIDGE_CONFIDENCE[bridge_type]
        confidence_source = ConfidenceSource.DEFAULT

    bridge = BridgeWarrant(
        bridge_id=bridge_id,
        source_domain=source_domain,
        target_domain=target_domain,
        bridge_type=bridge_type,
        warrant_statement=warrant_statement,
        assumed_mechanism=assumed_mechanism,
        confidence=confidence,
        confidence_source=confidence_source,
        status=BridgeStatus.HYPOTHESIZED,
        source_beliefs=source_beliefs or [],
        target_beliefs=target_beliefs or [],
        evidence_for=[],
        evidence_against=[],
        provenance=Provenance(
            created_by=created_by,
            version=1
        )
    )

    logger.info(f"Created bridge: {bridge_id} ({bridge_type.value}) confidence={confidence:.2f}")
    return bridge


def evaluate_bridge(
    bridge: BridgeWarrant,
    new_evidence_id: str,
    supports: bool,
    evidence_strength: float = 0.5
) -> BridgeWarrant:
    """
    Update bridge confidence based on new evidence.

    Args:
        bridge: Bridge to evaluate
        new_evidence_id: ID of the new evidence
        supports: Whether evidence supports (True) or contradicts (False) the bridge
        evidence_strength: How strong the evidence is (0-1)

    Returns:
        Updated BridgeWarrant
    """
    updated = bridge.copy()

    if supports:
        if new_evidence_id not in updated.evidence_for:
            updated.evidence_for.append(new_evidence_id)
        # Increase confidence using diminishing returns
        boost = evidence_strength * (1 - updated.confidence) * 0.3
        updated.confidence = min(0.95, updated.confidence + boost)
    else:
        if new_evidence_id not in updated.evidence_against:
            updated.evidence_against.append(new_evidence_id)
        # Decrease confidence
        penalty = evidence_strength * updated.confidence * 0.3
        updated.confidence = max(0.05, updated.confidence - penalty)

    updated.confidence_source = ConfidenceSource.EVIDENCE_UPDATED
    updated.bridged_credence_cache = None  # Invalidate cache

    # Update status based on evidence balance
    n_for = len(updated.evidence_for)
    n_against = len(updated.evidence_against)

    if n_against > 0 and updated.confidence < 0.2:
        updated.status = BridgeStatus.FAILED
        updated.voi_flag = True  # Failed bridges are high-value investigation targets
    elif n_for > 0 and n_against > 0:
        updated.status = BridgeStatus.CONTESTED
    elif n_for > 0 and n_against == 0:
        updated.status = BridgeStatus.SUPPORTED

    # Update provenance
    updated.provenance.last_updated = datetime.now(timezone.utc)
    updated.provenance.version += 1

    logger.info(f"Evaluated bridge {bridge.bridge_id}: confidence {bridge.confidence:.2f} -> {updated.confidence:.2f}")
    return updated


def record_failure(
    bridge: BridgeWarrant,
    disconfirming_evidence: List[str],
    failure_type: str,
    suggested_revision: Optional[BridgeType] = None
) -> BridgeWarrant:
    """
    Record bridge failure with full audit trail.

    Per expert panel (2026-01-18), failed bridges should:
    1. Be marked as failed (not deleted)
    2. Have a failure record with disconfirming evidence
    3. Set VOI flag for investigation priority
    4. Optionally suggest a revision (e.g., mechanism -> functional)

    Args:
        bridge: Bridge that failed
        disconfirming_evidence: Belief IDs that disconfirmed the bridge
        failure_type: Type of failure (e.g., 'mechanism_not_conserved')
        suggested_revision: Optional downgrade to a different bridge type

    Returns:
        Updated BridgeWarrant with failure record
    """
    updated = bridge.copy()

    updated.failure_record = FailureRecord(
        failed_at=datetime.now(timezone.utc),
        disconfirming_evidence=disconfirming_evidence,
        failure_type=failure_type,
        suggested_revision=suggested_revision
    )

    updated.status = BridgeStatus.FAILED
    updated.voi_flag = True  # Failed bridges are high-value investigation targets
    updated.confidence = max(0.05, updated.confidence * 0.3)  # Dramatically reduce confidence

    # Add disconfirming evidence to evidence_against
    for eid in disconfirming_evidence:
        if eid not in updated.evidence_against:
            updated.evidence_against.append(eid)

    # Update provenance
    updated.provenance.last_updated = datetime.now(timezone.utc)
    updated.provenance.version += 1

    logger.warning(f"Bridge failure recorded: {bridge.bridge_id} - {failure_type}")
    return updated


def revise_bridge(
    failed_bridge: BridgeWarrant,
    new_type: BridgeType,
    new_warrant_statement: Optional[str] = None,
    new_assumed_mechanism: Optional[str] = None
) -> BridgeWarrant:
    """
    Create a revised bridge after failure.

    When a mechanism bridge fails, it may be possible to downgrade to a
    functional bridge that still holds. This creates a new bridge while
    preserving the lineage.

    Args:
        failed_bridge: The bridge that failed
        new_type: The revised bridge type (typically a downgrade)
        new_warrant_statement: Optional new warrant statement
        new_assumed_mechanism: Optional new mechanism description

    Returns:
        New BridgeWarrant with REVISED status
    """
    # Generate new ID preserving lineage
    revision_id = f"bridge:{failed_bridge.source_domain}_{failed_bridge.target_domain}_rev_{uuid.uuid4().hex[:8]}"

    revised = BridgeWarrant(
        bridge_id=revision_id,
        source_domain=failed_bridge.source_domain,
        target_domain=failed_bridge.target_domain,
        bridge_type=new_type,
        warrant_statement=new_warrant_statement or failed_bridge.warrant_statement,
        assumed_mechanism=new_assumed_mechanism,
        confidence=DEFAULT_BRIDGE_CONFIDENCE[new_type],
        confidence_source=ConfidenceSource.DEFAULT,
        status=BridgeStatus.REVISED,
        source_beliefs=failed_bridge.source_beliefs.copy(),
        target_beliefs=failed_bridge.target_beliefs.copy(),
        evidence_for=[],  # Fresh start for evidence
        evidence_against=[],
        provenance=Provenance(
            created_by=f"system:revision_of:{failed_bridge.bridge_id}",
            version=1
        )
    )

    logger.info(f"Revised bridge: {failed_bridge.bridge_id} -> {revision_id} ({new_type.value})")
    return revised


# =============================================================================
# BRIDGED CREDENCE COMPUTATION
# =============================================================================

def compute_bridged_credence(
    parent_theory_credence: float,
    bridge_confidence: float,
    cnfa_specific_confidence: float
) -> float:
    """
    Compute credence for a CNFA-specific claim derived via bridge warrant.

    Formula: P(CNFA effect) = P(parent theory) x P(bridge) x P(CNFA-specific)

    This formula assumes independence between the three terms, which is
    known to be a simplification. However, it has the right qualitative
    properties:
    - If parent theory is weak, CNFA predictions inherit that weakness
    - If bridge is uncertain, CNFA predictions inherit that uncertainty
    - CNFA-specific factors further attenuate

    Args:
        parent_theory_credence: P(parent theory is correct), 0-1
        bridge_confidence: P(bridge transfers), 0-1, defaults by bridge type
        cnfa_specific_confidence: P(no CNFA-specific confounds), 0-1

    Returns:
        Bridged credence, 0-1

    Example:
        >>> compute_bridged_credence(0.8, 0.6, 0.9)  # Mechanism bridge
        0.432
    """
    # Validate inputs
    parent_theory_credence = max(0.0, min(1.0, parent_theory_credence))
    bridge_confidence = max(0.0, min(1.0, bridge_confidence))
    cnfa_specific_confidence = max(0.0, min(1.0, cnfa_specific_confidence))

    return parent_theory_credence * bridge_confidence * cnfa_specific_confidence


def compute_bridged_credence_for_belief(
    bridge: BridgeWarrant,
    web,  # WebOfBelief - type hint omitted to avoid circular import
    cnfa_specific_confidence: float = 0.8
) -> float:
    """
    Compute bridged credence using a bridge and web context.

    This function looks up the parent theory credence from the web and
    computes the bridged credence using the stored bridge confidence.

    Args:
        bridge: The bridge warrant
        web: WebOfBelief instance for looking up theory credence
        cnfa_specific_confidence: P(no CNFA-specific confounds)

    Returns:
        Bridged credence value
    """
    # Find parent theory credence from source beliefs
    parent_credence = 0.5  # Default if no source beliefs

    if bridge.source_beliefs and hasattr(web, 'beliefs'):
        for belief_id in bridge.source_beliefs:
            if belief_id in web.beliefs:
                belief = web.beliefs[belief_id]
                if hasattr(belief.credence, 'value'):
                    parent_credence = max(parent_credence, belief.credence.value)

    bridged = compute_bridged_credence(
        parent_theory_credence=parent_credence,
        bridge_confidence=bridge.confidence,
        cnfa_specific_confidence=cnfa_specific_confidence
    )

    # Cache the result
    bridge.bridged_credence_cache = bridged

    return bridged


# =============================================================================
# BRIDGE SUGGESTION
# =============================================================================

# Domain keywords for inference
DOMAIN_KEYWORDS: Dict[str, List[str]] = {
    "object_perception": ["object", "shape", "angular", "curved", "geometry", "visual"],
    "architectural_perception": ["room", "building", "space", "interior", "architecture", "ceiling"],
    "basic_neuroscience": ["amygdala", "cortex", "neural", "brain", "fmri", "activation"],
    "environmental_psychology": ["nature", "green", "outdoor", "environment", "restoration"],
    "affect": ["emotion", "stress", "anxiety", "mood", "arousal", "valence"],
    "cognition": ["attention", "memory", "cognitive", "processing", "perception"],
}

# F2.1: Capacity bridge detection patterns per Cartwright (ruthless review 2026-01-22)
# Capacity bridges assert that an entity has a stable capacity, not dependent on mechanism
# Panel validation (2026-01-22): Removed "tends to" and "able to" - too broad, could be
# statistical tendencies or possibility claims rather than true capacity assertions.
# True capacity language asserts stable causal power without specifying mechanism.
CAPACITY_KEYWORDS: List[str] = [
    "has the capacity",      # True capacity claim
    "possesses the capacity", # True capacity claim
    "inherent capacity",     # Stable intrinsic property
    "intrinsic ability",     # Dispositional property
    "dispositional property", # Philosophical capacity language
    "natural capacity",      # Inherent stable power
    "capacity for",          # True capacity claim
    "capable of",            # Moderate capacity indicator (kept per panel)
    "propensity to",         # Dispositional language
    "disposition",           # Dispositional language
]


def suggest_bridges(
    source_domain: str,
    target_domain: str,
    source_statements: Optional[List[str]] = None
) -> List[BridgeWarrant]:
    """
    Suggest possible bridge warrants between two domains.

    This function proposes bridges based on domain relationships and
    heuristics. All suggested bridges start with HYPOTHESIZED status.

    Args:
        source_domain: Domain from which evidence originates
        target_domain: Domain to which evidence might transfer
        source_statements: Optional statements to analyze for bridge type hints

    Returns:
        List of proposed BridgeWarrant candidates
    """
    suggestions = []

    # Heuristic: If domains share a prefix, more likely to have bridges
    source_parts = source_domain.split(".")
    target_parts = target_domain.split(".")

    # Check for constitutive relationship (target contains source)
    if any(sp in target_domain.lower() for sp in source_parts):
        suggestions.append(create_bridge(
            source_domain=source_domain,
            target_domain=target_domain,
            bridge_type=BridgeType.CONSTITUTIVE,
            warrant_statement=f"The domain '{target_domain}' is composed of elements from '{source_domain}'",
            created_by="system:bridge_suggester"
        ))

    # Check statements for mechanism keywords
    if source_statements:
        statements_text = " ".join(source_statements).lower()

        # Mechanism indicators
        mechanism_keywords = ["pathway", "circuit", "mechanism", "mediates", "causes", "activates"]
        if any(kw in statements_text for kw in mechanism_keywords):
            suggestions.append(create_bridge(
                source_domain=source_domain,
                target_domain=target_domain,
                bridge_type=BridgeType.MECHANISM,
                warrant_statement=f"The causal mechanism from '{source_domain}' is conserved in '{target_domain}'",
                created_by="system:bridge_suggester"
            ))

        # Functional indicators
        functional_keywords = ["effect", "outcome", "result", "produces", "leads to"]
        if any(kw in statements_text for kw in functional_keywords):
            suggestions.append(create_bridge(
                source_domain=source_domain,
                target_domain=target_domain,
                bridge_type=BridgeType.FUNCTIONAL,
                warrant_statement=f"The functional outcome from '{source_domain}' occurs in '{target_domain}' via potentially different mechanisms",
                created_by="system:bridge_suggester"
            ))

    # Default: always suggest an analogical bridge (weakest form)
    suggestions.append(create_bridge(
        source_domain=source_domain,
        target_domain=target_domain,
        bridge_type=BridgeType.ANALOGICAL,
        warrant_statement=f"Structural similarity between '{source_domain}' and '{target_domain}' suggests analogous effects",
        created_by="system:bridge_suggester"
    ))

    logger.info(f"Suggested {len(suggestions)} bridges from {source_domain} to {target_domain}")
    return suggestions


def detect_bridge_from_claim(
    claim: Dict[str, Any],
    target_domain: str = "architectural_perception"
) -> Optional[BridgeWarrant]:
    """
    Detect if a claim implies a bridge warrant.

    This function analyzes a claim for signals that suggest knowledge
    transfer across domains.

    Args:
        claim: Dictionary conforming to ae.claim.v1
        target_domain: The target domain for CNFA

    Returns:
        BridgeWarrant if bridge is detected, None otherwise
    """
    statement = claim.get("statement", "").lower()
    constructs = claim.get("constructs", {})
    outcomes = constructs.get("outcomes", [])

    # Infer source domain from outcomes
    source_domain = None
    for outcome in outcomes:
        outcome_id = outcome.get("id", "").lower()
        for domain, keywords in DOMAIN_KEYWORDS.items():
            if any(kw in outcome_id for kw in keywords):
                source_domain = domain
                break
        if source_domain:
            break

    if not source_domain:
        # Try statement keywords
        for domain, keywords in DOMAIN_KEYWORDS.items():
            if any(kw in statement for kw in keywords):
                source_domain = domain
                break

    if not source_domain or source_domain == target_domain:
        return None

    # Determine bridge type from statement
    bridge_type = BridgeType.ANALOGICAL  # Default
    assumed_mechanism = None

    if any(kw in statement for kw in ["amygdala", "neural", "cortex", "brain"]):
        bridge_type = BridgeType.MECHANISM
        assumed_mechanism = "neural pathway"
    elif any(kw in statement for kw in ["stress", "anxiety", "arousal", "affect"]):
        bridge_type = BridgeType.FUNCTIONAL
    elif any(kw in statement for kw in ["component", "part of", "consists of"]):
        bridge_type = BridgeType.CONSTITUTIVE
    # F2.1: Capacity bridge detection per Cartwright (ruthless review 2026-01-22)
    elif any(kw in statement for kw in CAPACITY_KEYWORDS):
        bridge_type = BridgeType.CAPACITY

    bridge = create_bridge(
        source_domain=source_domain,
        target_domain=target_domain,
        bridge_type=bridge_type,
        warrant_statement=f"Finding from {source_domain} may transfer to {target_domain}",
        source_beliefs=[claim.get("claim_id", "")],
        assumed_mechanism=assumed_mechanism,
        created_by="system:claim_analyzer"
    )

    logger.debug(f"Detected bridge from claim {claim.get('claim_id')}: {bridge.bridge_id}")
    return bridge


# =============================================================================
# ANOMALY GENERATION
# =============================================================================

@dataclass
class Anomaly:
    """Record of an epistemic anomaly (e.g., bridge failure)."""
    anomaly_id: str
    anomaly_type: str
    source_entity_id: str
    description: str
    severity: str  # "low", "medium", "high"
    voi_score: float  # Value of information for resolving
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    related_beliefs: List[str] = field(default_factory=list)
    suggested_actions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema": "ae.anomaly.v1",
            "anomaly_id": self.anomaly_id,
            "anomaly_type": self.anomaly_type,
            "source_entity_id": self.source_entity_id,
            "description": self.description,
            "severity": self.severity,
            "voi_score": self.voi_score,
            "created_at": self.created_at.isoformat(),
            "related_beliefs": self.related_beliefs,
            "suggested_actions": self.suggested_actions
        }


def create_anomaly_from_bridge_failure(
    bridge: BridgeWarrant
) -> Anomaly:
    """
    Create an anomaly record from a failed bridge.

    Per expert panel (2026-01-18), bridge failures should generate
    anomaly records for visibility and investigation priority.
    """
    failure_type = "unknown"
    if bridge.failure_record:
        failure_type = bridge.failure_record.failure_type

    # Calculate VOI score (failed bridges with more evidence are higher priority)
    voi_score = min(1.0, 0.3 + len(bridge.evidence_against) * 0.1 + len(bridge.source_beliefs) * 0.05)

    suggested_actions = ["Investigate boundary conditions"]
    if bridge.failure_record and bridge.failure_record.suggested_revision:
        suggested_actions.append(f"Consider revising to {bridge.failure_record.suggested_revision.value} bridge")

    return Anomaly(
        anomaly_id=f"anomaly:bridge_failure:{bridge.bridge_id.replace('bridge:', '')}",
        anomaly_type="bridge_failure",
        source_entity_id=bridge.bridge_id,
        description=f"Bridge {bridge.bridge_id} failed: {failure_type}. "
                    f"Transfer from {bridge.source_domain} to {bridge.target_domain} not supported.",
        severity="high" if bridge.bridge_type == BridgeType.MECHANISM else "medium",
        voi_score=voi_score,
        related_beliefs=bridge.source_beliefs + bridge.target_beliefs + bridge.evidence_against,
        suggested_actions=suggested_actions
    )


# =============================================================================
# EXPORT FUNCTIONS
# =============================================================================

def export_bridges_jsonl(registry: BridgeRegistry, path: Path) -> int:
    """Export all bridges to JSONL file."""
    return registry.to_jsonl(path)


def export_anomalies_jsonl(anomalies: List[Anomaly], path: Path) -> int:
    """Export anomalies to JSONL file."""
    with open(path, 'w') as f:
        for anomaly in anomalies:
            f.write(json.dumps(anomaly.to_dict()) + "\n")
    return len(anomalies)


# =============================================================================
# MAIN (Demo/Test)
# =============================================================================

if __name__ == "__main__":
    # Demo: Create and manipulate bridges

    # Create a mechanism bridge (Bar & Neta -> Vartanian case)
    bridge = create_bridge(
        source_domain="object_perception",
        target_domain="architectural_perception",
        bridge_type=BridgeType.MECHANISM,
        warrant_statement="Angular geometry activates a domain-general threat detection mechanism (amygdala pathway) regardless of scale",
        assumed_mechanism="amygdala threat detection",
        source_beliefs=["belief:bar_neta_2006_angular_objects"],
        target_beliefs=["belief:vartanian_2013_angular_rooms"],
        created_by="demo:manual"
    )

    print("=== Created Bridge ===")
    print(json.dumps(bridge.to_dict(), indent=2))

    # Test bridged credence computation
    print("\n=== Bridged Credence Test ===")
    credence = compute_bridged_credence(
        parent_theory_credence=0.8,
        bridge_confidence=0.6,  # Mechanism default
        cnfa_specific_confidence=0.9
    )
    print(f"Computed bridged credence: {credence:.3f}")
    print(f"Expected: 0.432")

    # Simulate bridge failure (Vartanian found ACC, not amygdala)
    print("\n=== Bridge Failure Test ===")
    failed_bridge = record_failure(
        bridge=bridge,
        disconfirming_evidence=["belief:vartanian_2013_acc_activation"],
        failure_type="mechanism_not_conserved",
        suggested_revision=BridgeType.FUNCTIONAL
    )
    print(f"Status after failure: {failed_bridge.status.value}")
    print(f"VOI flag: {failed_bridge.voi_flag}")
    print(f"Suggested revision: {failed_bridge.failure_record.suggested_revision.value}")

    # Create anomaly record
    anomaly = create_anomaly_from_bridge_failure(failed_bridge)
    print("\n=== Anomaly Record ===")
    print(json.dumps(anomaly.to_dict(), indent=2))

    # Test bridge revision
    print("\n=== Bridge Revision Test ===")
    revised_bridge = revise_bridge(
        failed_bridge=failed_bridge,
        new_type=BridgeType.FUNCTIONAL,
        new_warrant_statement="Angular geometry evokes negative affect regardless of scale, though via different neural mechanisms"
    )
    print(f"Revised bridge ID: {revised_bridge.bridge_id}")
    print(f"Revised type: {revised_bridge.bridge_type.value}")
    print(f"Revised confidence: {revised_bridge.confidence:.2f}")

    # Test registry
    print("\n=== Registry Test ===")
    registry = BridgeRegistry()
    registry.add(bridge)
    registry.add(revised_bridge)
    print(f"Bridges in registry: {len(registry.all())}")
    print(f"Failed bridges: {len(registry.get_failed())}")
    print(f"Mechanism bridges: {len(registry.get_by_type(BridgeType.MECHANISM))}")
