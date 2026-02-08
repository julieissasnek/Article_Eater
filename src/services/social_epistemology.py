"""
Article Eater - Social Epistemology Module
==========================================

Sprint 2.5: Social Epistemology Constructs

This module extends the Quinean Web of Belief with social epistemology constructs.
Scientific knowledge is produced by communities, not isolated individuals. This module
provides:

1. EpistemicCommunity — Groups sharing theoretical commitments, methods, journals
2. BeliefProvenance — Tracks which labs/methods/communities produced beliefs
3. CommunityRelativeCredence — Credence that varies by community perspective
4. ContestationTracker — Tracks methodological and theoretical disputes
5. MethodologicalDiversityAssessor — Finds single-method vulnerabilities

Philosophical Foundations (P-SE Panel):
- Dr. Helen Longino — Social epistemology, objectivity
- Dr. Philip Kitcher — Science and values, well-ordered science
- Dr. Karin Knorr Cetina — Laboratory studies, epistemic cultures
- Dr. Harry Collins — Sociology of scientific knowledge
- Dr. Thomas Kuhn — Paradigms, scientific revolutions

Panel Decisions:
- SE-1: Community identification by theory commitment (0.35), exemplars (0.25),
        methods (0.25), citations (0.15)
- SE-2: Report disagreement by default; average only for empirical, within-paradigm
- SE-3: Track institutional power separately; use domain-specific track record
- SE-4: Snapshot-based tracking with event annotations
- SE-5: Three-tier hierarchy: Field > Paradigm > Lab

Date: February 8, 2026
Lane: B (Implementation)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, Set, TYPE_CHECKING
from enum import Enum
from datetime import datetime, timezone
from collections import defaultdict
import math
import logging

if TYPE_CHECKING:
    from src.services.web_of_belief import WebOfBelief, Belief

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS (from Sprint 2.5 Schema Design)
# =============================================================================

class CommunityType(Enum):
    """
    How the community is primarily defined.

    Per panel synthesis for SE-1: Communities can be identified by multiple
    criteria, but one is typically primary.
    """
    JOURNAL_CLUSTER = "journal_cluster"       # Who publishes where
    CITATION_NETWORK = "citation_network"     # Who cites whom
    THEORY_COMMITMENT = "theory_commitment"   # Who commits to which theories (primary)
    METHODOLOGICAL = "methodological"         # Who uses which methods
    INSTITUTIONAL = "institutional"           # University/lab affiliation
    PARADIGM = "paradigm"                     # Shared exemplars (Kuhn)


class ContestationType(Enum):
    """
    Type of disagreement between communities.

    Per panel synthesis for SE-2: Different types require different aggregation
    approaches.
    """
    EMPIRICAL = "empirical"                   # Different data/interpretations
    METHODOLOGICAL = "methodological"         # Different methods
    THEORETICAL = "theoretical"               # Different frameworks
    SCOPE = "scope"                           # Different generalization claims
    VALUE = "value"                           # Different value commitments
    INCOMMENSURABLE = "incommensurable"       # Kuhnian paradigm difference


class DisagreementResolution(Enum):
    """
    How to handle community disagreement.

    Per panel synthesis for SE-2:
    - AVERAGE: Only for within-paradigm, same-method, empirical disagreements
    - REPORT_SEPARATELY: Default for theoretical/methodological disagreements
    - FLAG_INCOMMENSURABLE: When paradigms cannot be compared
    """
    AVERAGE = "average"
    REPORT_SEPARATELY = "report_separately"
    FLAG_INCOMMENSURABLE = "flag_incommensurable"


class CommunityLevel(Enum):
    """
    Hierarchical level of community.

    Per panel synthesis for SE-5: Three-tier hierarchy with flexible assignment.
    """
    FIELD = "field"             # e.g., "environmental psychology"
    PARADIGM = "paradigm"       # e.g., "attention restoration theory"
    SUBFIELD = "subfield"       # e.g., "nature-based stress recovery"
    LAB = "lab"                 # e.g., "Kaplan Lab, U Michigan"


# =============================================================================
# COMMUNITY HISTORY EVENT
# =============================================================================

@dataclass
class CommunityHistoryEvent:
    """
    A significant event in community history.

    Per Kitcher: Focus on significant transitions, not continuous tracking.
    Per Collins: Infer from bibliometrics, not retrospective accounts.

    Event Types:
    - credence_shift: Major change in community credence for a belief
    - theory_adoption: Community adopts a new theoretical commitment
    - method_change: Community changes preferred methodology
    - paradigm_shift: Major restructuring of community commitments
    """
    event_id: str
    timestamp: datetime
    event_type: str  # "credence_shift", "theory_adoption", "method_change", "paradigm_shift"
    description: str

    # What changed
    affected_beliefs: List[str] = field(default_factory=list)
    magnitude: float = 0.0  # Size of change (e.g., credence delta)

    # Causal annotation per Knorr Cetina
    causal_tags: List[str] = field(default_factory=list)  # "new_evidence", "methodology_change", etc.
    triggering_papers: List[str] = field(default_factory=list)  # DOIs that triggered the change

    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'description': self.description,
            'affected_beliefs': self.affected_beliefs.copy(),
            'magnitude': self.magnitude,
            'causal_tags': self.causal_tags.copy(),
            'triggering_papers': self.triggering_papers.copy(),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'CommunityHistoryEvent':
        ts = d.get('timestamp')
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        elif ts is None:
            ts = datetime.now(timezone.utc)

        return cls(
            event_id=d.get('event_id', ''),
            timestamp=ts,
            event_type=d.get('event_type', ''),
            description=d.get('description', ''),
            affected_beliefs=d.get('affected_beliefs', []),
            magnitude=d.get('magnitude', 0.0),
            causal_tags=d.get('causal_tags', []),
            triggering_papers=d.get('triggering_papers', []),
        )


# =============================================================================
# EPISTEMIC COMMUNITY
# =============================================================================

@dataclass
class EpistemicCommunity:
    """
    A community that shares epistemic standards and practices.

    Per Longino: Communities are defined by shared standards of evaluation,
    not just publication venues.

    Per Kuhn: Communities form around paradigms—shared exemplars and standards.

    Attributes:
        community_id: Unique identifier (e.g., "comm:art" for Attention Restoration Theory)
        name: Human-readable name
        community_type: Primary organizing criterion
        level: Hierarchical level (FIELD, PARADIGM, SUBFIELD, LAB)
        foundational_works: DOIs of exemplary papers per Kuhn
        core_theories: Theory IDs the community commits to
        preferred_methods: Methodological preferences per Knorr Cetina
        characteristic_vocabulary: Per Collins, shared technical terms
        institutional_power: 0-1, tracked but NOT used for credence weighting (SE-3)
        domain_track_records: Domain → accuracy, used for credence weighting
        contestation_level: 0-1, reduces track record weight during disputes
    """
    community_id: str
    name: str

    # Type and level
    community_type: CommunityType
    level: CommunityLevel

    # Defining characteristics
    foundational_works: List[str] = field(default_factory=list)   # DOIs of exemplary papers
    core_theories: List[str] = field(default_factory=list)        # Theory IDs
    preferred_methods: List[str] = field(default_factory=list)    # Method preferences
    characteristic_vocabulary: Set[str] = field(default_factory=set)  # Shared terms

    # Membership
    member_authors: List[str] = field(default_factory=list)       # Author IDs
    associated_journals: List[str] = field(default_factory=list)  # ISSN or journal names
    associated_institutions: List[str] = field(default_factory=list)  # University affiliations

    # Hierarchy
    parent_community_id: Optional[str] = None   # For Lab→Subfield→Field hierarchy
    child_community_ids: List[str] = field(default_factory=list)  # Sub-communities

    # Metrics (per panel synthesis for SE-3)
    institutional_power: float = 0.5            # 0-1, tracked but NOT used for credence
    domain_track_records: Dict[str, float] = field(default_factory=dict)  # domain → accuracy
    contestation_level: float = 0.0             # 0-1, reduces track record weight

    # Temporal tracking (per SE-4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    history_events: List[CommunityHistoryEvent] = field(default_factory=list)

    def track_record_weight(self, domain: str) -> float:
        """
        Compute effective track record weight for a domain.

        Per panel synthesis for SE-3:
        - Apply domain-specific track record
        - Apply contestation discount (reduces weight during high-contestation periods)

        Args:
            domain: The domain/topic to get track record for

        Returns:
            Effective weight (0-1) for this community's credence in this domain
        """
        base_accuracy = self.domain_track_records.get(domain, 0.5)
        contestation_discount = 1.0 - (self.contestation_level * 0.5)
        return base_accuracy * contestation_discount

    def add_history_event(
        self,
        event_type: str,
        description: str,
        affected_beliefs: Optional[List[str]] = None,
        magnitude: float = 0.0,
        causal_tags: Optional[List[str]] = None,
        triggering_papers: Optional[List[str]] = None
    ) -> CommunityHistoryEvent:
        """
        Record a significant event in community history.

        Per Kitcher: Focus on significant transitions (>0.15 credence shift,
        new theory, methodology change).

        Returns:
            The created history event
        """
        import uuid
        event = CommunityHistoryEvent(
            event_id=f"event:{uuid.uuid4().hex[:12]}",
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            description=description,
            affected_beliefs=affected_beliefs or [],
            magnitude=magnitude,
            causal_tags=causal_tags or [],
            triggering_papers=triggering_papers or [],
        )
        self.history_events.append(event)
        return event

    def vocabulary_overlap(self, other: 'EpistemicCommunity') -> float:
        """
        Compute vocabulary overlap with another community.

        Per Collins: Mutual intelligibility is indicated by shared vocabulary.

        Returns:
            Jaccard similarity coefficient (0-1)
        """
        if not self.characteristic_vocabulary or not other.characteristic_vocabulary:
            return 0.0

        intersection = len(self.characteristic_vocabulary & other.characteristic_vocabulary)
        union = len(self.characteristic_vocabulary | other.characteristic_vocabulary)

        if union == 0:
            return 0.0
        return intersection / union

    def to_dict(self) -> Dict[str, Any]:
        return {
            'community_id': self.community_id,
            'name': self.name,
            'community_type': self.community_type.value,
            'level': self.level.value,
            'foundational_works': self.foundational_works.copy(),
            'core_theories': self.core_theories.copy(),
            'preferred_methods': self.preferred_methods.copy(),
            'characteristic_vocabulary': list(self.characteristic_vocabulary),
            'member_authors': self.member_authors.copy(),
            'associated_journals': self.associated_journals.copy(),
            'associated_institutions': self.associated_institutions.copy(),
            'parent_community_id': self.parent_community_id,
            'child_community_ids': self.child_community_ids.copy(),
            'institutional_power': self.institutional_power,
            'domain_track_records': self.domain_track_records.copy(),
            'contestation_level': self.contestation_level,
            'created_at': self.created_at.isoformat(),
            'history_events': [h.to_dict() for h in self.history_events],
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'EpistemicCommunity':
        # Parse created_at
        created_at = d.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now(timezone.utc)

        # Parse history events
        history_events = [
            CommunityHistoryEvent.from_dict(h)
            for h in d.get('history_events', [])
        ]

        # Parse enums
        try:
            community_type = CommunityType(d.get('community_type', 'theory_commitment'))
        except ValueError:
            community_type = CommunityType.THEORY_COMMITMENT

        try:
            level = CommunityLevel(d.get('level', 'paradigm'))
        except ValueError:
            level = CommunityLevel.PARADIGM

        return cls(
            community_id=d.get('community_id', ''),
            name=d.get('name', ''),
            community_type=community_type,
            level=level,
            foundational_works=d.get('foundational_works', []),
            core_theories=d.get('core_theories', []),
            preferred_methods=d.get('preferred_methods', []),
            characteristic_vocabulary=set(d.get('characteristic_vocabulary', [])),
            member_authors=d.get('member_authors', []),
            associated_journals=d.get('associated_journals', []),
            associated_institutions=d.get('associated_institutions', []),
            parent_community_id=d.get('parent_community_id'),
            child_community_ids=d.get('child_community_ids', []),
            institutional_power=d.get('institutional_power', 0.5),
            domain_track_records=d.get('domain_track_records', {}),
            contestation_level=d.get('contestation_level', 0.0),
            created_at=created_at,
            history_events=history_events,
        )


# =============================================================================
# BELIEF PROVENANCE
# =============================================================================

@dataclass
class BeliefProvenance:
    """
    Tracks the social origins of a belief.

    Answers: Who produced this belief? With what methods? In what context?

    Per panel synthesis for SE-2: Community credences are tracked separately
    and aggregation depends on contestation type.

    Attributes:
        belief_id: The belief this provenance describes
        producing_communities: Community IDs that produced this belief
        producing_labs: Lab-level IDs (more specific than community)
        producing_authors: Primary author IDs
        methods_used: e.g., "lab_experiment", "field_study"
        instruments_used: e.g., "POMS", "cortisol_assay"
        community_credences: community_id → credence (per SE-2)
        endorsing_communities: Communities that accept this
        contesting_communities: Communities that dispute this
    """
    belief_id: str

    # Production context
    producing_communities: List[str] = field(default_factory=list)
    producing_labs: List[str] = field(default_factory=list)
    producing_authors: List[str] = field(default_factory=list)

    # Methodological context
    methods_used: List[str] = field(default_factory=list)
    instruments_used: List[str] = field(default_factory=list)

    # Community reception
    community_credences: Dict[str, float] = field(default_factory=dict)
    endorsing_communities: List[str] = field(default_factory=list)
    contesting_communities: List[str] = field(default_factory=list)

    # Contestation details (per SE-2)
    contestation_type: Optional[ContestationType] = None
    contestation_details: Optional[str] = None

    # Aggregation decision
    aggregation_approach: DisagreementResolution = DisagreementResolution.REPORT_SEPARATELY
    aggregated_credence: Optional[float] = None

    def get_community_credence(self, community_id: str) -> Optional[float]:
        """Get credence from specific community's perspective."""
        return self.community_credences.get(community_id)

    def set_community_credence(self, community_id: str, credence: float) -> None:
        """
        Set credence for a specific community.

        Args:
            community_id: The community assigning credence
            credence: Credence value (0-1)
        """
        self.community_credences[community_id] = max(0.01, min(0.99, credence))

    def is_contested(self) -> bool:
        """
        Check if belief is contested across communities.

        Per panel: Contestation indicated by credence spread > 0.2
        """
        if len(self.community_credences) < 2:
            return False
        values = list(self.community_credences.values())
        return max(values) - min(values) > 0.2

    def compute_aggregated_credence(
        self,
        communities: Dict[str, EpistemicCommunity],
        domain: str
    ) -> Tuple[Optional[float], DisagreementResolution]:
        """
        Compute aggregated credence if appropriate.

        Per panel synthesis for SE-2:
        - Only average for within-paradigm, same-method, empirical disagreements
        - Otherwise report separately or flag as incommensurable

        Args:
            communities: Dictionary of community_id → EpistemicCommunity
            domain: The domain for track record lookup

        Returns:
            Tuple of (aggregated_credence or None, resolution approach)
        """
        # Incommensurable or value-laden: cannot aggregate
        if self.contestation_type in [ContestationType.THEORETICAL,
                                       ContestationType.INCOMMENSURABLE,
                                       ContestationType.VALUE]:
            self.aggregation_approach = DisagreementResolution.FLAG_INCOMMENSURABLE
            self.aggregated_credence = None
            return (None, DisagreementResolution.FLAG_INCOMMENSURABLE)

        # Methodological disagreement: report separately
        if self.contestation_type == ContestationType.METHODOLOGICAL:
            self.aggregation_approach = DisagreementResolution.REPORT_SEPARATELY
            self.aggregated_credence = None
            return (None, DisagreementResolution.REPORT_SEPARATELY)

        # Empirical disagreement: weighted average by track record
        if self.contestation_type == ContestationType.EMPIRICAL:
            total_weight = 0.0
            weighted_sum = 0.0

            for comm_id, credence in self.community_credences.items():
                if comm_id in communities:
                    weight = communities[comm_id].track_record_weight(domain)
                    weighted_sum += credence * weight
                    total_weight += weight

            if total_weight > 0:
                self.aggregated_credence = weighted_sum / total_weight
                self.aggregation_approach = DisagreementResolution.AVERAGE
                return (self.aggregated_credence, DisagreementResolution.AVERAGE)

        # Default: report separately
        self.aggregation_approach = DisagreementResolution.REPORT_SEPARATELY
        return (None, DisagreementResolution.REPORT_SEPARATELY)

    def credence_spread(self) -> float:
        """
        Compute the spread of credences across communities.

        Returns:
            max - min of community credences, or 0 if < 2 communities
        """
        if len(self.community_credences) < 2:
            return 0.0
        values = list(self.community_credences.values())
        return max(values) - min(values)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'belief_id': self.belief_id,
            'producing_communities': self.producing_communities.copy(),
            'producing_labs': self.producing_labs.copy(),
            'producing_authors': self.producing_authors.copy(),
            'methods_used': self.methods_used.copy(),
            'instruments_used': self.instruments_used.copy(),
            'community_credences': self.community_credences.copy(),
            'endorsing_communities': self.endorsing_communities.copy(),
            'contesting_communities': self.contesting_communities.copy(),
            'contestation_type': self.contestation_type.value if self.contestation_type else None,
            'contestation_details': self.contestation_details,
            'aggregation_approach': self.aggregation_approach.value,
            'aggregated_credence': self.aggregated_credence,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'BeliefProvenance':
        # Parse contestation type
        contestation_type = None
        ct_str = d.get('contestation_type')
        if ct_str:
            try:
                contestation_type = ContestationType(ct_str)
            except ValueError:
                pass

        # Parse aggregation approach
        try:
            aggregation_approach = DisagreementResolution(
                d.get('aggregation_approach', 'report_separately')
            )
        except ValueError:
            aggregation_approach = DisagreementResolution.REPORT_SEPARATELY

        return cls(
            belief_id=d.get('belief_id', ''),
            producing_communities=d.get('producing_communities', []),
            producing_labs=d.get('producing_labs', []),
            producing_authors=d.get('producing_authors', []),
            methods_used=d.get('methods_used', []),
            instruments_used=d.get('instruments_used', []),
            community_credences=d.get('community_credences', {}),
            endorsing_communities=d.get('endorsing_communities', []),
            contesting_communities=d.get('contesting_communities', []),
            contestation_type=contestation_type,
            contestation_details=d.get('contestation_details'),
            aggregation_approach=aggregation_approach,
            aggregated_credence=d.get('aggregated_credence'),
        )


# =============================================================================
# CONTESTATION TRACKER
# =============================================================================

@dataclass
class Contestation:
    """
    A specific contestation between communities on a belief.

    Per Longino: Track the structure of disagreement, not just the fact of it.
    Per Collins: Note when communities can't agree on what would settle the dispute
    (experimenter's regress).
    """
    contestation_id: str
    belief_id: str

    # Parties
    contesting_community_id: str   # Who is contesting
    target_community_id: str       # Whose position is being contested

    # Type and details
    contestation_type: ContestationType
    description: str

    # Evidence for the contestation
    contesting_papers: List[str] = field(default_factory=list)  # DOIs that challenge
    target_papers: List[str] = field(default_factory=list)       # DOIs being challenged

    # Resolution status
    is_resolved: bool = False
    resolution_date: Optional[datetime] = None
    resolution_description: Optional[str] = None

    # Per Collins: Can they agree on what would settle it?
    agreed_resolution_criteria: Optional[str] = None
    experimenter_regress: bool = False  # True if no agreed criteria

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            'contestation_id': self.contestation_id,
            'belief_id': self.belief_id,
            'contesting_community_id': self.contesting_community_id,
            'target_community_id': self.target_community_id,
            'contestation_type': self.contestation_type.value,
            'description': self.description,
            'contesting_papers': self.contesting_papers.copy(),
            'target_papers': self.target_papers.copy(),
            'is_resolved': self.is_resolved,
            'resolution_date': self.resolution_date.isoformat() if self.resolution_date else None,
            'resolution_description': self.resolution_description,
            'agreed_resolution_criteria': self.agreed_resolution_criteria,
            'experimenter_regress': self.experimenter_regress,
            'created_at': self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'Contestation':
        # Parse dates
        created_at = d.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now(timezone.utc)

        resolution_date = d.get('resolution_date')
        if isinstance(resolution_date, str):
            resolution_date = datetime.fromisoformat(resolution_date)

        # Parse contestation type
        try:
            contestation_type = ContestationType(d.get('contestation_type', 'empirical'))
        except ValueError:
            contestation_type = ContestationType.EMPIRICAL

        return cls(
            contestation_id=d.get('contestation_id', ''),
            belief_id=d.get('belief_id', ''),
            contesting_community_id=d.get('contesting_community_id', ''),
            target_community_id=d.get('target_community_id', ''),
            contestation_type=contestation_type,
            description=d.get('description', ''),
            contesting_papers=d.get('contesting_papers', []),
            target_papers=d.get('target_papers', []),
            is_resolved=d.get('is_resolved', False),
            resolution_date=resolution_date,
            resolution_description=d.get('resolution_description'),
            agreed_resolution_criteria=d.get('agreed_resolution_criteria'),
            experimenter_regress=d.get('experimenter_regress', False),
            created_at=created_at,
        )


class ContestationTracker:
    """
    Tracks contestations across the web.

    Per panel: Essential for understanding the social structure of knowledge.
    Provides methods to find contestations by belief or community, and to
    compute contestation levels for track record discounting.
    """

    def __init__(self):
        self.contestations: Dict[str, Contestation] = {}
        self.by_belief: Dict[str, List[str]] = defaultdict(list)
        self.by_community: Dict[str, List[str]] = defaultdict(list)

    def add_contestation(self, contestation: Contestation) -> None:
        """Add a contestation to the tracker."""
        self.contestations[contestation.contestation_id] = contestation
        self.by_belief[contestation.belief_id].append(contestation.contestation_id)
        self.by_community[contestation.contesting_community_id].append(contestation.contestation_id)
        self.by_community[contestation.target_community_id].append(contestation.contestation_id)

    def remove_contestation(self, contestation_id: str) -> bool:
        """Remove a contestation from the tracker."""
        if contestation_id not in self.contestations:
            return False

        contestation = self.contestations[contestation_id]

        # Remove from indices
        if contestation.belief_id in self.by_belief:
            self.by_belief[contestation.belief_id] = [
                cid for cid in self.by_belief[contestation.belief_id]
                if cid != contestation_id
            ]

        for comm_id in [contestation.contesting_community_id, contestation.target_community_id]:
            if comm_id in self.by_community:
                self.by_community[comm_id] = [
                    cid for cid in self.by_community[comm_id]
                    if cid != contestation_id
                ]

        del self.contestations[contestation_id]
        return True

    def get_contestation(self, contestation_id: str) -> Optional[Contestation]:
        """Get a contestation by ID."""
        return self.contestations.get(contestation_id)

    def get_contestations_for_belief(self, belief_id: str) -> List[Contestation]:
        """Get all contestations affecting a belief."""
        ids = self.by_belief.get(belief_id, [])
        return [self.contestations[cid] for cid in ids if cid in self.contestations]

    def get_community_contestations(self, community_id: str) -> List[Contestation]:
        """Get all contestations involving a community (as contester or target)."""
        ids = self.by_community.get(community_id, [])
        return [self.contestations[cid] for cid in ids if cid in self.contestations]

    def compute_contestation_level(self, community_id: str) -> float:
        """
        Compute how contested a community's positions are.

        Used for SE-3 track record discounting. Higher values mean the
        community's positions are more contested, reducing their weight.

        Returns:
            Contestation level (0-1)
        """
        contestations = self.get_community_contestations(community_id)
        if not contestations:
            return 0.0

        # Weight by type (per panel: theoretical disagreements are more serious)
        total_weight = 0.0
        for c in contestations:
            if c.is_resolved:
                continue

            type_weight = {
                ContestationType.EMPIRICAL: 0.3,
                ContestationType.METHODOLOGICAL: 0.5,
                ContestationType.THEORETICAL: 0.8,
                ContestationType.SCOPE: 0.4,
                ContestationType.VALUE: 0.6,
                ContestationType.INCOMMENSURABLE: 1.0,
            }.get(c.contestation_type, 0.5)

            total_weight += type_weight

        # Normalize to 0-1
        return min(1.0, total_weight / 5.0)

    def identify_experimenter_regress(self, belief_id: str) -> List[Contestation]:
        """
        Find contestations where communities can't agree on resolution criteria.

        Per Collins: These are the deep disagreements.
        """
        contestations = self.get_contestations_for_belief(belief_id)
        return [c for c in contestations if c.experimenter_regress]

    def get_unresolved_count(self) -> int:
        """Get count of unresolved contestations."""
        return sum(1 for c in self.contestations.values() if not c.is_resolved)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'contestations': [c.to_dict() for c in self.contestations.values()],
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'ContestationTracker':
        tracker = cls()
        for c_dict in d.get('contestations', []):
            contestation = Contestation.from_dict(c_dict)
            tracker.add_contestation(contestation)
        return tracker


# =============================================================================
# METHODOLOGICAL DIVERSITY ASSESSOR
# =============================================================================

@dataclass
class MethodologicalProfile:
    """
    Profile of methods used to support a belief.

    Used to identify single-method vulnerabilities and suggest diversification.
    """
    belief_id: str
    methods: Dict[str, int] = field(default_factory=dict)      # method → count
    instruments: Dict[str, int] = field(default_factory=dict)  # instrument → count
    settings: Dict[str, int] = field(default_factory=dict)     # setting → count
    populations: Dict[str, int] = field(default_factory=dict)  # population → count

    def diversity_index(self) -> float:
        """
        Compute methodological diversity using entropy.

        Per Knorr Cetina: Different methods = different ways of knowing.
        Per Longino: Diverse methods increase objectivity.

        Returns:
            Normalized diversity index (0-1)
        """
        def entropy(counts: Dict[str, int]) -> float:
            total = sum(counts.values())
            if total == 0:
                return 0.0
            probs = [c / total for c in counts.values() if c > 0]
            return -sum(p * math.log2(p) for p in probs if p > 0)

        # Compute entropy for each category, normalized by max possible
        def normalized_entropy(counts: Dict[str, int]) -> float:
            if not counts:
                return 0.0
            max_entropy = math.log2(len(counts)) if len(counts) > 1 else 1.0
            if max_entropy == 0:
                return 0.0
            return entropy(counts) / max_entropy

        method_entropy = normalized_entropy(self.methods)
        setting_entropy = normalized_entropy(self.settings)
        population_entropy = normalized_entropy(self.populations)

        # Weighted combination
        return 0.4 * method_entropy + 0.3 * setting_entropy + 0.3 * population_entropy

    def identify_vulnerabilities(self) -> List[str]:
        """
        Identify single-method or single-context vulnerabilities.

        Returns:
            List of vulnerability descriptions
        """
        vulnerabilities = []

        # Single category vulnerabilities
        if len(self.methods) == 1 and sum(self.methods.values()) > 0:
            vulnerabilities.append(f"Single method: {list(self.methods.keys())[0]}")

        if len(self.settings) == 1 and sum(self.settings.values()) > 0:
            vulnerabilities.append(f"Single setting: {list(self.settings.keys())[0]}")

        if len(self.populations) == 1 and sum(self.populations.values()) > 0:
            vulnerabilities.append(f"Single population: {list(self.populations.keys())[0]}")

        # Check for dominance (>80% from one source)
        for category_name, counts in [('method', self.methods),
                                       ('setting', self.settings),
                                       ('population', self.populations)]:
            total = sum(counts.values())
            if total > 0:
                for name, count in counts.items():
                    if count / total > 0.8 and len(counts) > 1:
                        vulnerabilities.append(
                            f"Dominant {category_name}: {name} ({count}/{total})"
                        )

        return vulnerabilities

    def to_dict(self) -> Dict[str, Any]:
        return {
            'belief_id': self.belief_id,
            'methods': self.methods.copy(),
            'instruments': self.instruments.copy(),
            'settings': self.settings.copy(),
            'populations': self.populations.copy(),
            'diversity_index': self.diversity_index(),
            'vulnerabilities': self.identify_vulnerabilities(),
        }


class MethodologicalDiversityAssessor:
    """
    Assesses methodological diversity of evidence for beliefs.

    Per Longino: Objectivity requires diverse methods and perspectives.
    Per Knorr Cetina: Different methods produce different knowledge.

    Usage:
        assessor = MethodologicalDiversityAssessor(web)
        profile = assessor.assess_belief("belief:123")
        vulnerables = assessor.find_vulnerable_beliefs()
    """

    def __init__(self, web: Optional['WebOfBelief'] = None):
        """
        Initialize assessor.

        Args:
            web: Optional WebOfBelief instance for belief lookup
        """
        self.web = web
        self.profiles: Dict[str, MethodologicalProfile] = {}

    def set_web(self, web: 'WebOfBelief') -> None:
        """Set or update the web reference."""
        self.web = web
        self.profiles.clear()  # Clear cached profiles

    def assess_belief(self, belief_id: str) -> MethodologicalProfile:
        """
        Compute methodological profile for a belief.

        Args:
            belief_id: The belief to assess

        Returns:
            MethodologicalProfile with diversity metrics
        """
        if belief_id in self.profiles:
            return self.profiles[belief_id]

        # Default empty profile
        profile = MethodologicalProfile(belief_id=belief_id)

        if self.web is None:
            return profile

        belief = self.web.beliefs.get(belief_id)
        if not belief:
            return profile

        # Aggregate from scope conditions (if available)
        methods = defaultdict(int)
        instruments = defaultdict(int)
        settings = defaultdict(int)
        populations = defaultdict(int)

        # Use scope as proxy for methodology
        if belief.scope:
            if belief.scope.setting:
                settings[belief.scope.setting] += 1
            if belief.scope.population:
                populations[belief.scope.population] += 1
            if belief.scope.measurement:
                methods[belief.scope.measurement] += 1

        # If belief has provenance, use methods from there
        if hasattr(belief, 'provenance') and belief.provenance:
            for method in belief.provenance.methods_used:
                methods[method] += 1
            for instrument in belief.provenance.instruments_used:
                instruments[instrument] += 1

        profile = MethodologicalProfile(
            belief_id=belief_id,
            methods=dict(methods),
            instruments=dict(instruments),
            settings=dict(settings),
            populations=dict(populations)
        )

        self.profiles[belief_id] = profile
        return profile

    def find_vulnerable_beliefs(
        self,
        diversity_threshold: float = 0.3
    ) -> List[Tuple[str, MethodologicalProfile, List[str]]]:
        """
        Find beliefs with low methodological diversity.

        Args:
            diversity_threshold: Beliefs below this diversity are flagged

        Returns:
            List of (belief_id, profile, vulnerabilities) tuples
        """
        if self.web is None:
            return []

        vulnerables = []
        for belief_id in self.web.beliefs:
            profile = self.assess_belief(belief_id)
            if profile.diversity_index() < diversity_threshold:
                vulns = profile.identify_vulnerabilities()
                if vulns:
                    vulnerables.append((belief_id, profile, vulns))

        return vulnerables

    def suggest_diversification(
        self,
        belief_id: str
    ) -> Dict[str, List[str]]:
        """
        Suggest methodological diversification for a belief.

        Per Longino: Suggests what additional perspectives would help.

        Returns:
            Dictionary of category → suggested alternatives
        """
        profile = self.assess_belief(belief_id)
        suggestions = {}

        # Common method alternatives
        method_alternatives = {
            'self_report': ['physiological', 'behavioral', 'observational'],
            'physiological': ['self_report', 'behavioral', 'cognitive'],
            'behavioral': ['self_report', 'physiological', 'neuroimaging'],
            'lab_experiment': ['field_experiment', 'quasi_experiment', 'observational'],
            'field_experiment': ['lab_experiment', 'longitudinal', 'cross_sectional'],
            'survey': ['interview', 'observation', 'behavioral'],
        }

        for method in profile.methods:
            if method in method_alternatives:
                alts = [m for m in method_alternatives[method] if m not in profile.methods]
                if alts:
                    suggestions[f"alternative_to_{method}"] = alts

        # Setting diversification
        if 'lab' in profile.settings and 'field' not in profile.settings:
            suggestions['setting'] = ['field_study', 'naturalistic_observation']
        elif 'field' in profile.settings and 'lab' not in profile.settings:
            suggestions['setting'] = ['lab_experiment', 'controlled_study']

        # Population diversification
        pop_str = str(profile.populations).lower()
        if 'adult' in pop_str and 'child' not in pop_str:
            suggestions['population'] = ['children', 'adolescents', 'elderly']
        if 'healthy' in pop_str and 'clinical' not in pop_str:
            suggestions['population'] = suggestions.get('population', []) + ['clinical_sample']
        if 'western' in pop_str:
            suggestions['population'] = suggestions.get('population', []) + ['non_western', 'cross_cultural']

        return suggestions


# =============================================================================
# COMMUNITY REGISTRY
# =============================================================================

class CommunityRegistry:
    """
    Registry for managing epistemic communities.

    Provides CRUD operations and lookup by various criteria.
    """

    def __init__(self):
        self.communities: Dict[str, EpistemicCommunity] = {}
        self.by_level: Dict[CommunityLevel, List[str]] = defaultdict(list)
        self.by_type: Dict[CommunityType, List[str]] = defaultdict(list)

    def add_community(self, community: EpistemicCommunity) -> None:
        """Add a community to the registry."""
        self.communities[community.community_id] = community
        self.by_level[community.level].append(community.community_id)
        self.by_type[community.community_type].append(community.community_id)

    def get_community(self, community_id: str) -> Optional[EpistemicCommunity]:
        """Get a community by ID."""
        return self.communities.get(community_id)

    def get_communities_by_level(self, level: CommunityLevel) -> List[EpistemicCommunity]:
        """Get all communities at a hierarchical level."""
        ids = self.by_level.get(level, [])
        return [self.communities[cid] for cid in ids if cid in self.communities]

    def get_communities_by_type(self, community_type: CommunityType) -> List[EpistemicCommunity]:
        """Get all communities of a given type."""
        ids = self.by_type.get(community_type, [])
        return [self.communities[cid] for cid in ids if cid in self.communities]

    def get_children(self, community_id: str) -> List[EpistemicCommunity]:
        """Get child communities."""
        community = self.get_community(community_id)
        if not community:
            return []
        return [
            self.communities[cid]
            for cid in community.child_community_ids
            if cid in self.communities
        ]

    def get_parent(self, community_id: str) -> Optional[EpistemicCommunity]:
        """Get parent community."""
        community = self.get_community(community_id)
        if not community or not community.parent_community_id:
            return None
        return self.get_community(community.parent_community_id)

    def find_by_vocabulary(
        self,
        terms: Set[str],
        min_overlap: float = 0.3
    ) -> List[Tuple[EpistemicCommunity, float]]:
        """
        Find communities that share vocabulary with given terms.

        Per Collins: Vocabulary overlap indicates mutual intelligibility.

        Args:
            terms: Set of terms to match
            min_overlap: Minimum Jaccard overlap to include

        Returns:
            List of (community, overlap_score) tuples, sorted by overlap
        """
        results = []
        for community in self.communities.values():
            if not community.characteristic_vocabulary:
                continue

            intersection = len(terms & community.characteristic_vocabulary)
            union = len(terms | community.characteristic_vocabulary)

            if union > 0:
                overlap = intersection / union
                if overlap >= min_overlap:
                    results.append((community, overlap))

        # Sort by overlap descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def all_communities(self) -> List[EpistemicCommunity]:
        """Get all communities."""
        return list(self.communities.values())

    def to_dict(self) -> Dict[str, Any]:
        return {
            'communities': [c.to_dict() for c in self.communities.values()],
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'CommunityRegistry':
        registry = cls()
        for c_dict in d.get('communities', []):
            community = EpistemicCommunity.from_dict(c_dict)
            registry.add_community(community)
        return registry


# =============================================================================
# SEED DATA: CNFA COMMUNITIES
# =============================================================================

def create_cnfa_seed_communities() -> List[EpistemicCommunity]:
    """
    Create seed communities for CNfA (Cognition, Nature, and the Built Environment).

    These are initial communities to bootstrap the system based on the
    major theoretical orientations in environmental psychology.

    Returns:
        List of EpistemicCommunity objects
    """
    return [
        EpistemicCommunity(
            community_id="comm:art",
            name="Attention Restoration Theory",
            community_type=CommunityType.THEORY_COMMITMENT,
            level=CommunityLevel.PARADIGM,
            foundational_works=["10.1016/0272-4944(89)90016-1"],  # Kaplan & Kaplan 1989
            core_theories=["theory:art"],
            preferred_methods=["cognitive_testing", "self_report"],
            characteristic_vocabulary={
                "directed_attention", "fascination", "being_away", "extent",
                "compatibility", "soft_fascination", "attentional_fatigue",
                "restorative_environment"
            },
            associated_journals=[
                "Environment and Behavior",
                "Journal of Environmental Psychology"
            ],
            parent_community_id="comm:env_psych",
        ),
        EpistemicCommunity(
            community_id="comm:srt",
            name="Stress Recovery Theory",
            community_type=CommunityType.THEORY_COMMITMENT,
            level=CommunityLevel.PARADIGM,
            foundational_works=["10.1126/science.6143402"],  # Ulrich 1984
            core_theories=["theory:srt"],
            preferred_methods=["physiological", "behavioral"],
            characteristic_vocabulary={
                "psychophysiological", "stress_recovery", "affective",
                "parasympathetic", "cortisol", "autonomic",
                "biophilic_response"
            },
            associated_journals=[
                "Health & Place",
                "Environment and Behavior"
            ],
            parent_community_id="comm:env_psych",
        ),
        EpistemicCommunity(
            community_id="comm:env_psych",
            name="Environmental Psychology",
            community_type=CommunityType.JOURNAL_CLUSTER,
            level=CommunityLevel.FIELD,
            characteristic_vocabulary={
                "restorative", "nature_exposure", "built_environment",
                "environmental_preference", "place_attachment"
            },
            associated_journals=[
                "Environment and Behavior",
                "Journal of Environmental Psychology",
                "Landscape and Urban Planning"
            ],
            child_community_ids=["comm:art", "comm:srt", "comm:biophilia"],
        ),
        EpistemicCommunity(
            community_id="comm:biophilia",
            name="Biophilia Hypothesis",
            community_type=CommunityType.THEORY_COMMITMENT,
            level=CommunityLevel.PARADIGM,
            foundational_works=["10.1073/pnas.1800970115"],  # Kellert & Wilson
            core_theories=["theory:biophilia"],
            characteristic_vocabulary={
                "biophilia", "innate", "evolutionary", "affiliation",
                "biophilic_design", "nature_connection", "topophilia"
            },
            associated_journals=[
                "Frontiers in Psychology",
                "Environment and Behavior"
            ],
            parent_community_id="comm:env_psych",
        ),
    ]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def identify_community_for_belief(
    belief: 'Belief',
    registry: CommunityRegistry
) -> List[Tuple[str, float]]:
    """
    Identify which communities a belief likely belongs to.

    Per panel synthesis for SE-1: Use theory commitment (0.35),
    foundational works (0.25), methods (0.25), citations (0.15).

    Args:
        belief: The belief to classify
        registry: Community registry to search

    Returns:
        List of (community_id, confidence) tuples, sorted by confidence
    """
    results = []

    for community in registry.all_communities():
        score = 0.0

        # Theory commitment match (weight: 0.35)
        if belief.theory_id and belief.theory_id in community.core_theories:
            score += 0.35

        # Vocabulary match (weight: 0.25)
        if community.characteristic_vocabulary and belief.content:
            content_lower = belief.content.lower()
            matches = sum(
                1 for term in community.characteristic_vocabulary
                if term.lower() in content_lower
            )
            if matches > 0:
                vocab_score = min(1.0, matches / 3)  # Cap at 3 matches
                score += 0.25 * vocab_score

        # Method match (weight: 0.25)
        if hasattr(belief, 'provenance') and belief.provenance:
            for method in belief.provenance.methods_used:
                if method in community.preferred_methods:
                    score += 0.25
                    break

        # Paper match (weight: 0.15)
        if belief.paper_ids:
            for paper_id in belief.paper_ids:
                if paper_id in community.foundational_works:
                    score += 0.15
                    break

        if score > 0.1:  # Threshold for inclusion
            results.append((community.community_id, score))

    # Sort by score descending
    results.sort(key=lambda x: x[1], reverse=True)
    return results
