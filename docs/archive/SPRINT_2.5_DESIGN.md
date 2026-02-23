# Sprint 2.5: Social Epistemology Design

**Date**: February 8, 2026
**Status**: DESIGN PHASE
**Lane**: A (Schema Design)
**Panel**: P-SE (Social Epistemology)

---

## Overview

Sprint 2.5 extends the Quinean Web of Belief with social epistemology constructs. Scientific knowledge is produced by communities, not isolated individuals. This sprint adds:

1. **EpistemicCommunity** — Groups sharing theoretical commitments, methods, journals
2. **BeliefProvenance** — Tracks which labs/methods/communities produced beliefs
3. **CommunityRelativeCredence** — Credence that varies by community perspective
4. **ContestationTracker** — Tracks methodological and theoretical disputes
5. **MethodologicalDiversityAssessor** — Finds single-method vulnerabilities

---

## Panel P-SE: Social Epistemology

### Panel Members

| Expert | Expertise | Key Works |
|--------|-----------|-----------|
| Dr. Helen Longino | Social epistemology, objectivity | *Science as Social Knowledge* (1990) |
| Dr. Philip Kitcher | Science and values, well-ordered science | *Science, Truth, and Democracy* (2001) |
| Dr. Karin Knorr Cetina | Laboratory studies, epistemic cultures | *Epistemic Cultures* (1999) |
| Dr. Harry Collins | Sociology of scientific knowledge | *Changing Order* (1985), *The Golem* (1993) |
| Dr. Thomas Kuhn | Paradigms, scientific revolutions | *Structure of Scientific Revolutions* (1962) |

---

## Panel Questions and Responses

### SE-1: How to Identify Communities?

**Question**: How should the system identify epistemic communities in the CNfA literature?

**Options**:
- Journal clusters (who publishes where)
- Citation networks (who cites whom)
- Theory commitment (who commits to which theories)

#### Dr. Helen Longino (Social Epistemology):

Communities are constituted by **shared standards of evaluation**, not just publication venues or citation patterns. In scientific practice, what makes a community is:

1. Shared background assumptions
2. Agreed-upon methods for generating and evaluating evidence
3. Recognized venues for criticism and response
4. Equality of intellectual authority (in principle)

For CNfA specifically, I'd recommend identifying communities by **theory commitment + methodology**. The ART community and the SRT community aren't distinguished by journals—they often publish in the same places—but by their theoretical commitments and the measures they privilege.

**Recommendation**: Primary criterion = theory commitment. Secondary = preferred methodologies. Tertiary = publication/citation patterns.

#### Dr. Philip Kitcher (Science and Values):

The "community" concept should be operationalized functionally: a community is a group whose members' work affects one another's credences. This is fundamentally a **citation network** definition, but enriched with semantic content.

Two researchers are in the same community if:
1. They cite each other (directly or via intermediaries)
2. Their work addresses overlapping phenomena
3. They respond to each other's challenges

**Recommendation**: Citation network as foundation, filtered by semantic overlap in research questions.

#### Dr. Karin Knorr Cetina (Laboratory Studies):

From laboratory studies, we know that "epistemic cultures" differ fundamentally in how they produce knowledge. High-energy physics and molecular biology have radically different cultures despite both being "science."

For CNfA, I'd ask: what are the **material practices** that distinguish communities? The lab-based experimental psychologists have different practices than the field researchers doing ecological momentary assessment. These aren't just methodological preferences—they're different ways of knowing.

**Recommendation**: Cluster by **methodological practices**: lab experimental, field experimental, observational, computational/modeling.

#### Dr. Harry Collins (Sociology of Knowledge):

The crucial question is: who has **interactional expertise** with whom? Who can talk fluently across community boundaries? These boundary-spanners are rare but important.

Communities should be identified by **mutual intelligibility**. If you can read another researcher's work and immediately understand what they're doing and why, you're in the same community. If you need translation, you're not.

For computational purposes, this could be operationalized as: shared technical vocabulary, shared reference set, shared methodological assumptions.

**Recommendation**: Vocabulary overlap + shared reference set + methodological alignment.

#### Dr. Thomas Kuhn (Paradigms):

Communities form around **paradigms**—shared exemplars of good work, shared problems worth solving, and shared standards of solution. The paradigm is more fundamental than theory or method; it's the tacit knowledge of what it means to do good work in this field.

For CNfA, I'd identify paradigms by asking: which papers serve as exemplars? Who treats Ulrich (1984) or Kaplan & Kaplan (1989) as foundational? Who treats them as outdated?

**Recommendation**: Identify communities by which **foundational works** they treat as exemplary.

### Panel Synthesis for SE-1

| Criterion | Weight | Rationale |
|-----------|--------|-----------|
| Theory commitment | 0.35 | Primary organizer per Longino, Kuhn |
| Foundational works cited | 0.25 | Paradigm identification per Kuhn |
| Methodological practices | 0.25 | Epistemic culture per Knorr Cetina |
| Citation network | 0.15 | Background validation per Kitcher |

**Decision**: Use multi-criteria community identification with theory commitment as primary.

---

### SE-2: How to Aggregate Disagreeing Communities?

**Question**: When communities disagree about a belief, how should the system represent/aggregate this?

**Options**:
- Weighted average (combine into single credence)
- Report disagreement (keep separate credences)
- Both (average + disagreement flag)

#### Dr. Helen Longino:

Aggregating is **epistemically inappropriate** when disagreement reflects genuine methodological or theoretical differences. The ART and SRT communities might assign different credences to "attention restoration is the primary mechanism" not because one is wrong, but because they're asking different questions with different methods.

**Report disagreement explicitly.** A single number hides crucial information about the structure of scientific knowledge.

However, for *beliefs both communities address with similar methods*, averaging might be appropriate. The key is whether the disagreement is **substantive** (different theories, methods, questions) or **empirical** (same question, different data).

**Recommendation**: Report disagreement for substantive differences. Cautious averaging for purely empirical differences.

#### Dr. Philip Kitcher:

I'd distinguish between:
1. **Cognitive disagreement** — Different interpretations of shared evidence
2. **Social disagreement** — Different values, interests, or institutional pressures

For cognitive disagreement, weighted averaging by track record makes sense. For social disagreement, we need to identify and discount distorting factors.

**Recommendation**: Weighted average for cognitive disagreement, track record weights. Report explicitly for value-laden disagreement.

#### Dr. Karin Knorr Cetina:

Different epistemic cultures aren't trying to establish the same facts—they're producing different kinds of knowledge. Averaging their outputs is like averaging an apple and an orange.

**Report disagreement** with annotation about what kind of knowledge each community produces. A lab study and a field study aren't competing answers to the same question—they're answers to related but distinct questions.

**Recommendation**: Report disagreement with methodological context.

#### Dr. Harry Collins:

The crucial question is whether the disagreement is **resolvable in principle**. If communities could agree on an experiment that would settle it, average their priors. If they can't even agree on what would count as evidence, report the disagreement.

Look for **experimenter's regress**: when communities disagree about what counts as a proper test, aggregation is meaningless.

**Recommendation**: Check for shared evidential standards before aggregating.

#### Dr. Thomas Kuhn:

Communities in different paradigms are often talking past each other—**incommensurability**. Averaging their credences produces a number that neither community would recognize as meaningful.

Within a paradigm, disagreement is about puzzle-solving and can be aggregated. Across paradigms, disagreement is about fundamental worldview and should not be averaged.

**Recommendation**: Aggregate within-paradigm; report across-paradigm.

### Panel Synthesis for SE-2

| Scenario | Approach |
|----------|----------|
| Same paradigm, same methods, different data | Weighted average by track record |
| Same paradigm, different methods | Report disagreement with method annotation |
| Different paradigms | Report disagreement, flag as incommensurable |
| Value-laden disagreement | Report disagreement, flag as value-dependent |

**Decision**: Report disagreement by default. Allow averaging only for within-paradigm, same-method, empirical disagreements.

---

### SE-3: How to Represent Power Asymmetries?

**Question**: How should the system represent that some communities have more institutional power than others?

**Options**:
- Separate power from correctness (track but don't weight by power)
- Weight by track record (historical accuracy predicts future accuracy)

#### Dr. Helen Longino:

**Separate power from correctness.** Power asymmetries often reflect social factors (funding, prestige, gatekeeping) rather than epistemic merit. The history of science shows that marginalized perspectives sometimes turn out to be right.

However, track record *on specific kinds of questions* is epistemically relevant. A community that has consistently produced replicable findings on attention tasks has earned higher weight for attention claims.

**Recommendation**: Track power separately. Weight by domain-specific track record, not general prestige.

#### Dr. Philip Kitcher:

Track record is epistemically relevant, but we need to be careful about:
1. **Survivorship bias** — We only see successful paradigms
2. **Self-fulfilling prophecy** — Powerful communities get resources to validate their views
3. **Scope creep** — Good track record in one area doesn't transfer to others

**Recommendation**: Weight by track record, but with domain restrictions and recency weighting.

#### Dr. Karin Knorr Cetina:

Institutional power affects what counts as "successful" research. High-status journals publish certain kinds of work; funding goes to established approaches. This creates a feedback loop that has nothing to do with truth.

**Recommendation**: Track institutional power as a separate variable. Make it visible but don't use it to weight credence.

#### Dr. Harry Collins:

The "core set" of researchers who can actually evaluate evidence is often small. Power and credibility are different things but both matter.

**Recommendation**: Distinguish "core set credibility" (expert judgment within the field) from "institutional power" (external resources and prestige).

#### Dr. Thomas Kuhn:

During normal science, track record is a good guide. During revolutionary periods, the established community is often wrong.

**Recommendation**: Track record with a multiplier that decreases during periods of high contestation.

### Panel Synthesis for SE-3

**Decision**:
- Track institutional power as separate metadata (not used for credence weighting)
- Track domain-specific track record (used for credence weighting)
- Apply recency weighting to track record
- Reduce track record weight during high-contestation periods

Schema additions:
```python
@dataclass
class CommunityMetrics:
    institutional_power: float      # 0-1, not used for credence
    domain_track_record: Dict[str, float]  # domain → accuracy
    recency_weighted_accuracy: float
    contestation_discount: float    # Reduces track record weight
```

---

### SE-4: Track Historical Changes?

**Question**: Should the system track how communities' positions have changed over time?

**Options**:
- Yes (full temporal modeling, expensive)
- No (current snapshot only)
- Snapshots only (periodic checkpoints)

#### Dr. Helen Longino:

Historical tracking is **essential for understanding scientific progress**. Current credences without history hide:
- Whether a view is gaining or losing support
- Whether changes came from new evidence or social shifts
- Whether the field is converging or fragmenting

**Recommendation**: Track history, at least key transitions.

#### Dr. Philip Kitcher:

Full temporal modeling is ideal but costly. Focus on **significant transitions**:
- Major credence shifts (>0.2)
- Theory introductions/abandonments
- Methodology changes
- Key publication events

**Recommendation**: Event-based history rather than continuous tracking.

#### Dr. Karin Knorr Cetina:

The interesting question is: what explains the transitions? New data? New instruments? New funding priorities? Generational change?

**Recommendation**: Track transitions with causal annotation.

#### Dr. Harry Collins:

Beware **reconstructed rationality**. Scientists' accounts of why they changed positions often differ from what actually happened. Use bibliometric data rather than retrospective accounts.

**Recommendation**: Infer history from publications, don't rely on stated rationales.

#### Dr. Thomas Kuhn:

Revolutionary changes look different from normal science changes. The system should detect paradigm shifts by looking for:
- Vocabulary changes
- Changed exemplars
- Changed problem priorities

**Recommendation**: Detect qualitative transitions, not just quantitative shifts.

### Panel Synthesis for SE-4

**Decision**: Snapshot-based tracking with event annotations.

Implementation:
- Annual snapshots of community structure and credences
- Event log for significant transitions (>0.15 credence shift, new theory, methodology change)
- Causal tags for events (new_evidence, methodology_change, generational, funding_shift)
- Paradigm shift detection based on vocabulary and exemplar changes

---

### SE-5: What Granularity?

**Question**: At what granularity should communities be defined?

**Options**:
- Field (e.g., "environmental psychology")
- Subfield (e.g., "attention restoration research")
- Lab (e.g., "Kaplan lab")

#### Dr. Helen Longino:

The appropriate granularity depends on the question. For broad claims, field-level is fine. For specific mechanistic claims, lab-level matters because different labs have different tacit knowledge.

**Recommendation**: Hierarchical structure: Field > Subfield > Lab. Aggregate up as needed.

#### Dr. Philip Kitcher:

Granularity should match the **size of the claim's implications**. Claims with broad implications need field-level consensus. Narrow technical claims can rest on lab-level evidence.

**Recommendation**: Match granularity to claim scope.

#### Dr. Karin Knorr Cetina:

Labs are where knowledge is actually made. But labs don't exist in isolation—they're embedded in larger networks. Model both the lab level and the inter-lab network.

**Recommendation**: Lab as fundamental unit, with explicit network structure.

#### Dr. Harry Collins:

The core set for any claim is usually quite small—maybe 5-20 people who really understand the issues. Identify these core sets rather than using coarse institutional boundaries.

**Recommendation**: Core set identification per claim, not fixed communities.

#### Dr. Thomas Kuhn:

Paradigms often cut across institutional boundaries. The relevant community for ART might span multiple universities and include non-academics. Institutional granularity can miss this.

**Recommendation**: Intellectual communities based on shared commitments, not institutional affiliation.

### Panel Synthesis for SE-5

**Decision**: Three-tier hierarchy with flexible assignment:

| Level | Definition | Use Case |
|-------|------------|----------|
| Field | Broad disciplinary identity | Background context |
| Paradigm/Subfield | Shared theoretical commitments | Primary community identification |
| Lab/Research Group | Production unit | Provenance tracking, core set identification |

Implementation:
- Beliefs can be associated with multiple communities at different levels
- Community assignment is probabilistic (belief has 0.8 association with ART community)
- Core sets are identified dynamically based on citation patterns for specific claims

---

## Schema Design

### Core Enums

```python
# Location: src/services/social_epistemology.py

class CommunityType(Enum):
    """How the community is primarily defined."""
    JOURNAL_CLUSTER = "journal_cluster"
    CITATION_NETWORK = "citation_network"
    THEORY_COMMITMENT = "theory_commitment"
    METHODOLOGICAL = "methodological"
    INSTITUTIONAL = "institutional"
    PARADIGM = "paradigm"


class ContestationType(Enum):
    """Type of disagreement between communities."""
    EMPIRICAL = "empirical"          # Different data/interpretations
    METHODOLOGICAL = "methodological" # Different methods
    THEORETICAL = "theoretical"       # Different frameworks
    SCOPE = "scope"                   # Different generalization claims
    VALUE = "value"                   # Different value commitments
    INCOMMENSURABLE = "incommensurable"  # Kuhnian paradigm difference


class DisagreementResolution(Enum):
    """How to handle community disagreement."""
    AVERAGE = "average"               # Weight and average (empirical only)
    REPORT_SEPARATELY = "report_separately"  # Keep distinct (theoretical)
    FLAG_INCOMMENSURABLE = "flag_incommensurable"  # Cannot aggregate


class CommunityLevel(Enum):
    """Hierarchical level of community."""
    FIELD = "field"           # e.g., "environmental psychology"
    PARADIGM = "paradigm"     # e.g., "attention restoration theory"
    SUBFIELD = "subfield"     # e.g., "nature-based stress recovery"
    LAB = "lab"               # e.g., "Kaplan Lab, U Michigan"
```

### EpistemicCommunity Class

```python
@dataclass
class EpistemicCommunity:
    """
    A community that shares epistemic standards and practices.

    Per Longino: Communities are defined by shared standards of evaluation,
    not just publication venues.

    Per Kuhn: Communities form around paradigms—shared exemplars and standards.
    """
    community_id: str
    name: str

    # Type and level
    community_type: CommunityType
    level: CommunityLevel

    # Defining characteristics
    foundational_works: List[str]        # DOIs of exemplary papers per Kuhn
    core_theories: List[str]             # Theory IDs the community commits to
    preferred_methods: List[str]         # Methodological preferences per Knorr Cetina
    characteristic_vocabulary: Set[str]  # Per Collins: shared technical terms

    # Membership
    member_authors: List[str]            # Author IDs (approximate)
    associated_journals: List[str]       # ISSN or journal names
    associated_institutions: List[str]   # University affiliations

    # Hierarchy
    parent_community_id: Optional[str]   # For Lab→Subfield→Field hierarchy
    child_community_ids: List[str]       # Sub-communities

    # Metrics (per panel synthesis for SE-3)
    institutional_power: float = 0.5     # 0-1, tracked but not used for credence
    domain_track_records: Dict[str, float] = field(default_factory=dict)  # domain → accuracy
    contestation_level: float = 0.0      # 0-1, reduces track record weight

    # Temporal tracking (per SE-4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    history_events: List['CommunityHistoryEvent'] = field(default_factory=list)

    def track_record_weight(self, domain: str) -> float:
        """
        Compute effective track record weight for a domain.

        Per panel: Apply recency weighting and contestation discount.
        """
        base_accuracy = self.domain_track_records.get(domain, 0.5)
        contestation_discount = 1.0 - (self.contestation_level * 0.5)
        return base_accuracy * contestation_discount

    def to_dict(self) -> Dict[str, Any]:
        return {
            'community_id': self.community_id,
            'name': self.name,
            'community_type': self.community_type.value,
            'level': self.level.value,
            'foundational_works': self.foundational_works,
            'core_theories': self.core_theories,
            'preferred_methods': self.preferred_methods,
            'characteristic_vocabulary': list(self.characteristic_vocabulary),
            'member_authors': self.member_authors,
            'associated_journals': self.associated_journals,
            'associated_institutions': self.associated_institutions,
            'parent_community_id': self.parent_community_id,
            'child_community_ids': self.child_community_ids,
            'institutional_power': self.institutional_power,
            'domain_track_records': self.domain_track_records,
            'contestation_level': self.contestation_level,
            'created_at': self.created_at.isoformat(),
        }


@dataclass
class CommunityHistoryEvent:
    """
    A significant event in community history.

    Per Kitcher: Focus on significant transitions, not continuous tracking.
    Per Collins: Infer from bibliometrics, not retrospective accounts.
    """
    event_id: str
    timestamp: datetime
    event_type: str  # "credence_shift", "theory_adoption", "method_change", "paradigm_shift"
    description: str

    # What changed
    affected_beliefs: List[str]
    magnitude: float  # Size of change (e.g., credence delta)

    # Causal annotation per Knorr Cetina
    causal_tags: List[str]  # "new_evidence", "methodology_change", "generational", etc.
    triggering_papers: List[str]  # DOIs that triggered the change
```

### BeliefProvenance Class

```python
@dataclass
class BeliefProvenance:
    """
    Tracks the social origins of a belief.

    Answers: Who produced this belief? With what methods? In what context?
    """
    belief_id: str

    # Production context
    producing_communities: List[str]     # Community IDs
    producing_labs: List[str]            # Lab-level IDs (more specific)
    producing_authors: List[str]         # Primary author IDs

    # Methodological context
    methods_used: List[str]              # e.g., "lab_experiment", "field_study"
    instruments_used: List[str]          # e.g., "POMS", "cortisol_assay"

    # Community reception
    community_credences: Dict[str, float]  # community_id → credence (per SE-2)
    endorsing_communities: List[str]       # Communities that accept this
    contesting_communities: List[str]      # Communities that dispute this

    # Contestation details (per SE-2)
    contestation_type: Optional[ContestationType] = None
    contestation_details: Optional[str] = None

    # Aggregation decision
    aggregation_approach: DisagreementResolution = DisagreementResolution.REPORT_SEPARATELY
    aggregated_credence: Optional[float] = None  # Only if AVERAGE

    def get_community_credence(self, community_id: str) -> Optional[float]:
        """Get credence from specific community's perspective."""
        return self.community_credences.get(community_id)

    def is_contested(self) -> bool:
        """Check if belief is contested across communities."""
        if len(self.community_credences) < 2:
            return False
        values = list(self.community_credences.values())
        return max(values) - min(values) > 0.2

    def compute_aggregated_credence(
        self,
        communities: Dict[str, 'EpistemicCommunity'],
        domain: str
    ) -> Tuple[float, DisagreementResolution]:
        """
        Compute aggregated credence if appropriate.

        Per panel synthesis for SE-2:
        - Only average for within-paradigm, same-method, empirical disagreements
        - Otherwise report separately
        """
        if self.contestation_type in [ContestationType.THEORETICAL,
                                       ContestationType.INCOMMENSURABLE,
                                       ContestationType.VALUE]:
            return (None, DisagreementResolution.FLAG_INCOMMENSURABLE)

        if self.contestation_type == ContestationType.METHODOLOGICAL:
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
                return (weighted_sum / total_weight, DisagreementResolution.AVERAGE)

        return (None, DisagreementResolution.REPORT_SEPARATELY)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'belief_id': self.belief_id,
            'producing_communities': self.producing_communities,
            'producing_labs': self.producing_labs,
            'producing_authors': self.producing_authors,
            'methods_used': self.methods_used,
            'instruments_used': self.instruments_used,
            'community_credences': self.community_credences,
            'endorsing_communities': self.endorsing_communities,
            'contesting_communities': self.contesting_communities,
            'contestation_type': self.contestation_type.value if self.contestation_type else None,
            'contestation_details': self.contestation_details,
            'aggregation_approach': self.aggregation_approach.value,
            'aggregated_credence': self.aggregated_credence,
        }
```

### ContestationTracker Class

```python
@dataclass
class Contestation:
    """
    A specific contestation between communities on a belief.

    Per Longino: Track the structure of disagreement, not just the fact of it.
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
    contesting_papers: List[str]   # DOIs that challenge
    target_papers: List[str]       # DOIs being challenged

    # Resolution status
    is_resolved: bool = False
    resolution_date: Optional[datetime] = None
    resolution_description: Optional[str] = None

    # Per Collins: Can they agree on what would settle it?
    agreed_resolution_criteria: Optional[str] = None
    experimenter_regress: bool = False  # True if no agreed criteria

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ContestationTracker:
    """
    Tracks contestations across the web.

    Per panel: Essential for understanding the social structure of knowledge.
    """

    def __init__(self):
        self.contestations: Dict[str, Contestation] = {}
        self.by_belief: Dict[str, List[str]] = defaultdict(list)
        self.by_community: Dict[str, List[str]] = defaultdict(list)

    def add_contestation(self, contestation: Contestation) -> None:
        self.contestations[contestation.contestation_id] = contestation
        self.by_belief[contestation.belief_id].append(contestation.contestation_id)
        self.by_community[contestation.contesting_community_id].append(contestation.contestation_id)
        self.by_community[contestation.target_community_id].append(contestation.contestation_id)

    def get_contestations_for_belief(self, belief_id: str) -> List[Contestation]:
        ids = self.by_belief.get(belief_id, [])
        return [self.contestations[cid] for cid in ids]

    def get_community_contestations(self, community_id: str) -> List[Contestation]:
        ids = self.by_community.get(community_id, [])
        return [self.contestations[cid] for cid in ids]

    def compute_contestation_level(self, community_id: str) -> float:
        """
        Compute how contested a community's positions are.

        Used for SE-3 track record discounting.
        """
        contestations = self.get_community_contestations(community_id)
        if not contestations:
            return 0.0

        # Weight by recency and type
        total_weight = 0.0
        for c in contestations:
            if c.is_resolved:
                continue
            type_weight = {
                ContestationType.EMPIRICAL: 0.3,
                ContestationType.METHODOLOGICAL: 0.5,
                ContestationType.THEORETICAL: 0.8,
                ContestationType.INCOMMENSURABLE: 1.0,
                ContestationType.VALUE: 0.6,
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
```

### MethodologicalDiversityAssessor Class

```python
@dataclass
class MethodologicalProfile:
    """Profile of methods used to support a belief."""
    belief_id: str
    methods: Dict[str, int]          # method → count of papers using it
    instruments: Dict[str, int]      # instrument → count
    settings: Dict[str, int]         # setting → count (lab, field, etc.)
    populations: Dict[str, int]      # population → count

    def diversity_index(self) -> float:
        """
        Compute methodological diversity using entropy.

        Per Knorr Cetina: Different methods = different ways of knowing.
        Per Longino: Diverse methods increase objectivity.
        """
        def entropy(counts: Dict[str, int]) -> float:
            total = sum(counts.values())
            if total == 0:
                return 0.0
            probs = [c / total for c in counts.values()]
            return -sum(p * math.log2(p) for p in probs if p > 0)

        # Combine entropies (max possible varies by category)
        method_entropy = entropy(self.methods) / max(1, math.log2(len(self.methods) + 1))
        setting_entropy = entropy(self.settings) / max(1, math.log2(len(self.settings) + 1))
        population_entropy = entropy(self.populations) / max(1, math.log2(len(self.populations) + 1))

        # Weighted combination
        return 0.4 * method_entropy + 0.3 * setting_entropy + 0.3 * population_entropy

    def identify_vulnerabilities(self) -> List[str]:
        """Identify single-method or single-context vulnerabilities."""
        vulnerabilities = []

        if len(self.methods) == 1:
            vulnerabilities.append(f"Single method: {list(self.methods.keys())[0]}")

        if len(self.settings) == 1:
            vulnerabilities.append(f"Single setting: {list(self.settings.keys())[0]}")

        if len(self.populations) == 1:
            vulnerabilities.append(f"Single population: {list(self.populations.keys())[0]}")

        # Check for dominance (>80% from one source)
        for category, counts in [('method', self.methods),
                                  ('setting', self.settings),
                                  ('population', self.populations)]:
            total = sum(counts.values())
            if total > 0:
                for name, count in counts.items():
                    if count / total > 0.8:
                        vulnerabilities.append(f"Dominant {category}: {name} ({count}/{total})")

        return vulnerabilities


class MethodologicalDiversityAssessor:
    """
    Assesses methodological diversity of evidence for beliefs.

    Per Longino: Objectivity requires diverse methods and perspectives.
    Per Knorr Cetina: Different methods produce different knowledge.
    """

    def __init__(self, web: 'WebOfBelief'):
        self.web = web
        self.profiles: Dict[str, MethodologicalProfile] = {}

    def assess_belief(self, belief_id: str) -> MethodologicalProfile:
        """Compute methodological profile for a belief."""
        if belief_id in self.profiles:
            return self.profiles[belief_id]

        belief = self.web.beliefs.get(belief_id)
        if not belief:
            return MethodologicalProfile(belief_id, {}, {}, {}, {})

        # Aggregate from supporting papers
        methods = defaultdict(int)
        instruments = defaultdict(int)
        settings = defaultdict(int)
        populations = defaultdict(int)

        for paper_id in belief.paper_ids:
            # Would need paper metadata to fill these
            # For now, use scope conditions as proxy
            if belief.scope:
                if belief.scope.setting:
                    settings[belief.scope.setting] += 1
                if belief.scope.population:
                    populations[belief.scope.population] += 1
                if belief.scope.measurement:
                    methods[belief.scope.measurement] += 1

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

        Returns list of (belief_id, profile, vulnerabilities).
        """
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
        """
        profile = self.assess_belief(belief_id)
        suggestions = {}

        # Common method alternatives
        method_alternatives = {
            'self_report': ['physiological', 'behavioral', 'observational'],
            'physiological': ['self_report', 'behavioral', 'cognitive'],
            'behavioral': ['self_report', 'physiological', 'neuroimaging'],
            'lab_experiment': ['field_experiment', 'quasi_experiment', 'observational'],
        }

        for method in profile.methods:
            if method in method_alternatives:
                alts = [m for m in method_alternatives[method] if m not in profile.methods]
                if alts:
                    suggestions[f"alternative_to_{method}"] = alts

        # Setting diversification
        if 'lab' in profile.settings and 'field' not in profile.settings:
            suggestions['setting'] = ['field_study', 'naturalistic_observation']

        # Population diversification
        if 'adult' in str(profile.populations) and 'child' not in str(profile.populations):
            suggestions['population'] = ['children', 'elderly', 'clinical']

        return suggestions
```

---

## Integration with Belief Class

The existing `Belief` class needs extension to support provenance:

```python
# Extension to Belief class (to be added by Lane B)

@dataclass
class Belief:
    # ... existing fields ...

    # Sprint 2.5: Social epistemology additions
    provenance: Optional[BeliefProvenance] = None
    community_associations: Dict[str, float] = field(default_factory=dict)  # community_id → strength

    def get_community_credence(self, community_id: str) -> Optional[float]:
        """Get credence from specific community's perspective."""
        if self.provenance:
            return self.provenance.get_community_credence(community_id)
        return None

    def is_community_contested(self) -> bool:
        """Check if belief is contested across communities."""
        if self.provenance:
            return self.provenance.is_contested()
        return False
```

---

## JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://article-eater.ucsd.edu/schemas/social_epistemology.v1.schema.json",
  "title": "Social Epistemology Schema",
  "description": "Schema for social epistemology constructs in Article Eater",

  "definitions": {
    "CommunityType": {
      "type": "string",
      "enum": ["journal_cluster", "citation_network", "theory_commitment",
               "methodological", "institutional", "paradigm"]
    },

    "CommunityLevel": {
      "type": "string",
      "enum": ["field", "paradigm", "subfield", "lab"]
    },

    "ContestationType": {
      "type": "string",
      "enum": ["empirical", "methodological", "theoretical",
               "scope", "value", "incommensurable"]
    },

    "EpistemicCommunity": {
      "type": "object",
      "required": ["community_id", "name", "community_type", "level"],
      "properties": {
        "community_id": { "type": "string" },
        "name": { "type": "string" },
        "community_type": { "$ref": "#/definitions/CommunityType" },
        "level": { "$ref": "#/definitions/CommunityLevel" },
        "foundational_works": {
          "type": "array",
          "items": { "type": "string" }
        },
        "core_theories": {
          "type": "array",
          "items": { "type": "string" }
        },
        "preferred_methods": {
          "type": "array",
          "items": { "type": "string" }
        },
        "characteristic_vocabulary": {
          "type": "array",
          "items": { "type": "string" }
        },
        "institutional_power": {
          "type": "number",
          "minimum": 0,
          "maximum": 1
        },
        "domain_track_records": {
          "type": "object",
          "additionalProperties": { "type": "number" }
        },
        "contestation_level": {
          "type": "number",
          "minimum": 0,
          "maximum": 1
        }
      }
    },

    "BeliefProvenance": {
      "type": "object",
      "required": ["belief_id"],
      "properties": {
        "belief_id": { "type": "string" },
        "producing_communities": {
          "type": "array",
          "items": { "type": "string" }
        },
        "producing_labs": {
          "type": "array",
          "items": { "type": "string" }
        },
        "methods_used": {
          "type": "array",
          "items": { "type": "string" }
        },
        "community_credences": {
          "type": "object",
          "additionalProperties": { "type": "number" }
        },
        "contestation_type": { "$ref": "#/definitions/ContestationType" },
        "aggregated_credence": { "type": "number" }
      }
    },

    "Contestation": {
      "type": "object",
      "required": ["contestation_id", "belief_id", "contesting_community_id",
                   "target_community_id", "contestation_type"],
      "properties": {
        "contestation_id": { "type": "string" },
        "belief_id": { "type": "string" },
        "contesting_community_id": { "type": "string" },
        "target_community_id": { "type": "string" },
        "contestation_type": { "$ref": "#/definitions/ContestationType" },
        "description": { "type": "string" },
        "is_resolved": { "type": "boolean" },
        "experimenter_regress": { "type": "boolean" }
      }
    }
  }
}
```

---

## Implementation Priority

### High Priority (Lane B should implement first)
1. `EpistemicCommunity` class — Core data structure
2. `BeliefProvenance` class — Tracks origins
3. Integration with `Belief` class — Add provenance field

### Medium Priority
4. `ContestationTracker` — Track disputes
5. `MethodologicalDiversityAssessor` — Find vulnerabilities

### Low Priority (Enhancement)
6. Historical tracking — Snapshots and events
7. Core set identification — Dynamic per-claim communities

---

## Seed Data: CNfA Communities

Initial communities to bootstrap the system:

```python
CNFA_COMMUNITIES = [
    EpistemicCommunity(
        community_id="comm:art",
        name="Attention Restoration Theory",
        community_type=CommunityType.THEORY_COMMITMENT,
        level=CommunityLevel.PARADIGM,
        foundational_works=["10.1016/0272-4944(89)90016-1"],  # Kaplan & Kaplan 1989
        core_theories=["theory:art"],
        preferred_methods=["cognitive_testing", "self_report"],
        characteristic_vocabulary={"directed_attention", "fascination", "being_away", "extent"},
        parent_community_id="comm:env_psych"
    ),
    EpistemicCommunity(
        community_id="comm:srt",
        name="Stress Recovery Theory",
        community_type=CommunityType.THEORY_COMMITMENT,
        level=CommunityLevel.PARADIGM,
        foundational_works=["10.1126/science.6143402"],  # Ulrich 1984
        core_theories=["theory:srt"],
        preferred_methods=["physiological", "behavioral"],
        characteristic_vocabulary={"psychophysiological", "stress_recovery", "affective"},
        parent_community_id="comm:env_psych"
    ),
    EpistemicCommunity(
        community_id="comm:env_psych",
        name="Environmental Psychology",
        community_type=CommunityType.JOURNAL_CLUSTER,
        level=CommunityLevel.FIELD,
        associated_journals=["Environment and Behavior", "Journal of Environmental Psychology"],
        child_community_ids=["comm:art", "comm:srt", "comm:biophilia"]
    ),
    EpistemicCommunity(
        community_id="comm:biophilia",
        name="Biophilia Hypothesis",
        community_type=CommunityType.THEORY_COMMITMENT,
        level=CommunityLevel.PARADIGM,
        foundational_works=["10.1073/pnas.1800970115"],  # Kellert & Wilson
        core_theories=["theory:biophilia"],
        characteristic_vocabulary={"biophilia", "innate", "evolutionary", "affiliation"},
        parent_community_id="comm:env_psych"
    ),
]
```

---

## Panel Verdict Summary

| Question | Decision | Rationale |
|----------|----------|-----------|
| SE-1: Community identification | Multi-criteria: theory (0.35), exemplars (0.25), methods (0.25), citations (0.15) | Per Longino, Kuhn, Knorr Cetina |
| SE-2: Aggregating disagreement | Report separately by default; average only for empirical, within-paradigm | Per Longino, Kuhn |
| SE-3: Power asymmetries | Track separately from credence; use domain-specific track record | Per Longino, Kitcher |
| SE-4: Historical changes | Snapshot-based with event annotations | Per Kitcher, Collins |
| SE-5: Granularity | Three-tier hierarchy: Field > Paradigm > Lab | Per Longino, Knorr Cetina |

---

*Design document created: February 8, 2026*
*Panel: P-SE (Social Epistemology)*
*Lane: A (Schema Design)*
*Status: Ready for Lane B implementation*
