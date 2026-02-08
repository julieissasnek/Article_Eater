"""
Credibility Testing for Article Eater Post-Quinean.

Phase E: Implementation (Sprint B)
TODO 1: Credibility Testing Method

Per Phase D revised plan:
- Simplified two-category system (BLOCK, REVIEW)
- Minimal interfaces (3-5 fields per structure)
- Study design strength gradations (Pearl)
- Scope distance metric (Cartwright)
- Failure modes documented and handled

This module evaluates whether article additions to the Quinean web
produce epistemically appropriate updates.

Date: January 20, 2026
"""

import logging
import copy
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, Set, Callable
from enum import Enum
from datetime import datetime, timezone

from src.services.web_of_belief import (
    WebOfBelief,
    Belief,
    Constraint,
    Credence,
    EpistemicLevel,
    BeliefStatus,
    ConstraintType,
    CausalDirection,
    ScopeConditions,
)

logger = logging.getLogger(__name__)


# =============================================================================
# SIMPLIFIED DATA STRUCTURES (per Lampson)
# =============================================================================

class Decision(Enum):
    """
    Three-category system.

    Fix: Added explicit ACCEPT state (ChatGPT review 2026-02-08).
    Previously ACCEPT was implicit, causing semantic mismatch where
    overall_decision=REVIEW but serialization showed 'accept'.
    """
    ACCEPT = "accept"    # No issues found, can proceed automatically
    BLOCK = "block"      # Cannot proceed automatically (critical issue)
    REVIEW = "review"    # Flag for human review (needs attention)


@dataclass
class CredibilityFlag:
    """
    A single credibility concern.

    Minimal structure per Lampson: 3-5 fields.
    """
    decision: Decision
    reason: str
    confidence: float  # How sure are we this is a problem? (0-1)

    # Minimal details for review
    field_name: Optional[str] = None
    expected: Optional[str] = None
    observed: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'decision': self.decision.value,
            'reason': self.reason,
            'confidence': self.confidence,
            'field_name': self.field_name,
            'expected': self.expected,
            'observed': self.observed,
        }


@dataclass
class CredibilityReport:
    """
    Complete credibility assessment for an article.

    Minimal interface per Lampson.
    Fix: Default to ACCEPT, transition to REVIEW/BLOCK on flags (ChatGPT review 2026-02-08).
    """
    article_id: str
    timestamp: datetime
    flags: List[CredibilityFlag] = field(default_factory=list)
    overall_decision: Decision = Decision.ACCEPT  # Fix: Default to ACCEPT when clean

    def add_flag(self, flag: CredibilityFlag) -> None:
        """Add a flag and update overall decision."""
        self.flags.append(flag)
        # BLOCK wins over REVIEW wins over ACCEPT
        if flag.decision == Decision.BLOCK:
            self.overall_decision = Decision.BLOCK
        elif self.overall_decision == Decision.ACCEPT:
            self.overall_decision = Decision.REVIEW
        # If already BLOCK, stay BLOCK; if already REVIEW, stay REVIEW

    @property
    def is_clean(self) -> bool:
        """Returns True if no flags were raised."""
        return len(self.flags) == 0

    def to_dict(self) -> Dict[str, Any]:
        # Fix: Use overall_decision directly since ACCEPT is now explicit (ChatGPT review 2026-02-08)
        return {
            'article_id': self.article_id,
            'timestamp': self.timestamp.isoformat(),
            'flags': [f.to_dict() for f in self.flags],
            'overall_decision': self.overall_decision.value,
            'n_flags': len(self.flags),
        }

    def to_explanation_context(self) -> Dict[str, Any]:
        """
        Interface for TODO 2 integration.
        Per Phase D: Define integration interfaces.
        """
        # Fix: Use overall_decision directly since ACCEPT is now explicit (ChatGPT review 2026-02-08)
        return {
            'article_id': self.article_id,
            'decision': self.overall_decision.value,
            'reasons': [f.reason for f in self.flags],
            'n_flags': len(self.flags),
        }


# =============================================================================
# WEB SNAPSHOT (per Lampson: snapshot isolation)
# =============================================================================

@dataclass
class WebSnapshot:
    """
    Immutable snapshot of web state for consistent reads.

    Per Lampson: All read operations use snapshots.
    """
    snapshot_id: str
    timestamp: datetime
    beliefs: Dict[str, Belief]
    constraints: List[Constraint]

    @classmethod
    def from_web(cls, web: WebOfBelief) -> 'WebSnapshot':
        """Create snapshot from current web state."""
        return cls(
            snapshot_id=f"snap_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
            timestamp=datetime.now(timezone.utc),
            beliefs=copy.deepcopy(web.beliefs),
            constraints=copy.deepcopy(list(web.constraints.values())) if hasattr(web, 'constraints') and isinstance(web.constraints, dict) else []
        )


# =============================================================================
# STUDY DESIGN STRENGTH (per Pearl)
# =============================================================================

# Per Pearl: Don't reject correlational studies outright.
# Instead, check if claimed strength exceeds warranted strength.
DESIGN_STRENGTH: Dict[str, float] = {
    "correlational": 0.4,          # Can support weak associations
    "observational": 0.4,          # Same as correlational
    "cross_sectional": 0.35,       # Single timepoint, weaker
    "longitudinal": 0.5,           # Temporal precedence helps
    "quasi_experiment": 0.7,       # Partial control
    "natural_experiment": 0.8,     # Nature provides randomization
    "regression_discontinuity": 0.85,  # Strong quasi-experimental
    "instrumental_variable": 0.75,     # Causal identification strategy
    "rct": 1.0,                        # Gold standard
    "experiment": 0.95,                # Lab experiment
}


def get_design_strength(study_design: Optional[str]) -> float:
    """Get maximum warranted causal strength for a study design."""
    if not study_design:
        return 0.4  # Conservative default
    return DESIGN_STRENGTH.get(study_design.lower(), 0.4)


# =============================================================================
# SCOPE DISTANCE (per Cartwright)
# =============================================================================

# Per Cartwright: Scope overreach depends on distance, not binary.
# Categories ordered by specificity (1 = most specific, 5 = universal)
POPULATION_SPECIFICITY: Dict[str, int] = {
    "specific_clinical": 1,     # e.g., "ADHD children", "stroke patients"
    "clinical": 2,              # e.g., "clinical population", "patients"
    "demographic_subset": 3,    # e.g., "elderly", "students", "children"
    "cultural_specific": 4,     # e.g., "Japanese", "Western", "WEIRD"
    "general_adult": 5,         # e.g., "adults", "general population"
    "universal": 6,             # No population specified
}

# Keywords to detect population specificity
POPULATION_KEYWORDS: Dict[str, List[str]] = {
    "specific_clinical": ["adhd", "autism", "depression", "anxiety", "ptsd", "stroke", "dementia"],
    "clinical": ["patient", "clinical", "hospital", "therapy", "treatment"],
    "demographic_subset": ["children", "elderly", "students", "undergrad", "adolescent", "infant", "older adult"],
    "cultural_specific": ["western", "american", "japanese", "chinese", "european", "weird"],
    "general_adult": ["adult", "general population", "community sample"],
}


def classify_population(description: str) -> str:
    """Classify a population description by specificity."""
    desc_lower = description.lower()

    for category, keywords in POPULATION_KEYWORDS.items():
        if any(kw in desc_lower for kw in keywords):
            return category

    return "universal"  # Default if no keywords found


def scope_distance(sample_description: str, claimed_scope: Optional[str]) -> float:
    """
    Compute how far a claim extends beyond the sample.

    Returns 0-1, where higher = more overreach.
    Per Cartwright: Flag when distance > threshold.
    """
    sample_level = POPULATION_SPECIFICITY.get(
        classify_population(sample_description),
        3  # Default to demographic_subset
    )

    if claimed_scope:
        claim_level = POPULATION_SPECIFICITY.get(
            classify_population(claimed_scope),
            6  # Default to universal if not recognized
        )
    else:
        claim_level = 6  # No scope = universal claim

    distance = claim_level - sample_level
    # Normalize to 0-1 (max distance is 5)
    return max(0, distance) / 5


# =============================================================================
# SAFE CHECK WRAPPER (per Lampson: failure modes)
# =============================================================================

def safe_check(
    check_fn: Callable[..., List[CredibilityFlag]],
    *args,
    **kwargs
) -> List[CredibilityFlag]:
    """
    Wrapper that handles check failures gracefully.

    Per Lampson: Document failure modes.
    - If check throws exception: Catch, record as REVIEW flag, continue.
    """
    try:
        return check_fn(*args, **kwargs)
    except Exception as e:
        logger.error(f"Check {check_fn.__name__} failed: {e}", exc_info=True)
        return [CredibilityFlag(
            decision=Decision.REVIEW,
            reason=f"Check failed: {check_fn.__name__} ({type(e).__name__}: {str(e)[:50]})",
            confidence=0.3,
            field_name="system_error",
        )]


# =============================================================================
# CREDIBILITY CHECKS
# =============================================================================

class CredibilityChecks:
    """
    Collection of credibility checks.

    Sprint B implements core checks:
    - Numeric validity (BLOCK level)
    - Self-contradiction (BLOCK level)
    - Causal warrant (REVIEW level)
    - Scope overreach (REVIEW level)
    - Effect size plausibility (REVIEW level)
    """

    def __init__(self, web_snapshot: Optional[WebSnapshot] = None):
        """
        Initialize checks.

        Args:
            web_snapshot: Snapshot of web state for consistency
        """
        self.snapshot = web_snapshot

    # =========================================================================
    # BLOCK-LEVEL CHECKS (Critical issues)
    # =========================================================================

    def check_numeric_validity(
        self,
        beliefs: List[Belief],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[CredibilityFlag]:
        """
        Verify all numeric values are in valid ranges.

        Checks:
        - Credence in (0, 1)
        - Sample size positive (if provided)
        - P-value in [0, 1] (if provided)
        - Effect size reasonable (if provided)
        - Raw credence values from metadata (bypass Credence auto-clamping)
        """
        flags = []
        meta = metadata or {}

        # Check raw credence values from metadata (catches 0 and 1 before clamping)
        raw_credences = meta.get('raw_credences', [])
        for raw_c in raw_credences:
            if raw_c <= 0 or raw_c >= 1:
                flags.append(CredibilityFlag(
                    decision=Decision.BLOCK,
                    reason=f"Credence outside (0,1): {raw_c}",
                    confidence=1.0,
                    field_name="credence",
                    expected="(0, 1)",
                    observed=str(raw_c),
                ))

        # Check credence values from beliefs
        for belief in beliefs:
            # Flag credence at or beyond boundaries
            # Values == 0.01 or == 0.99 suggest clamping from invalid original
            # Values < 0.01 or > 0.99 are directly invalid
            if belief.credence.value <= 0.01 or belief.credence.value >= 0.99:
                flags.append(CredibilityFlag(
                    decision=Decision.BLOCK,
                    reason=f"Credence at boundary (likely invalid original): {belief.credence.value}",
                    confidence=0.9,
                    field_name="credence",
                    expected="(0.01, 0.99)",
                    observed=str(belief.credence.value),
                ))

            if belief.credence.uncertainty < 0 or belief.credence.uncertainty > 1:
                flags.append(CredibilityFlag(
                    decision=Decision.BLOCK,
                    reason=f"Uncertainty outside [0,1]: {belief.credence.uncertainty}",
                    confidence=1.0,
                    field_name="uncertainty",
                    expected="[0, 1]",
                    observed=str(belief.credence.uncertainty),
                ))

        # Check sample size (from metadata)
        sample_size = meta.get('sample_size')
        if sample_size is not None and sample_size <= 0:
            flags.append(CredibilityFlag(
                decision=Decision.BLOCK,
                reason=f"Sample size is non-positive: {sample_size}",
                confidence=1.0,
                field_name="sample_size",
                expected="> 0",
                observed=str(sample_size),
            ))

        # Check p-value (from metadata)
        p_value = meta.get('p_value')
        if p_value is not None and (p_value < 0 or p_value > 1):
            flags.append(CredibilityFlag(
                decision=Decision.BLOCK,
                reason=f"P-value outside [0,1]: {p_value}",
                confidence=1.0,
                field_name="p_value",
                expected="[0, 1]",
                observed=str(p_value),
            ))

        return flags

    def check_self_contradiction(
        self,
        beliefs: List[Belief],
        constraints: List[Constraint]
    ) -> List[CredibilityFlag]:
        """
        Check for contradictions within the same paper.

        A paper that asserts both X and not-X has an extraction error.
        """
        flags = []

        # Look for CONTRADICTS constraints between beliefs from same paper
        belief_ids = {b.belief_id for b in beliefs}

        for constraint in constraints:
            if constraint.constraint_type == ConstraintType.CONTRADICTS:
                if constraint.source_id in belief_ids and constraint.target_id in belief_ids:
                    # Both ends of contradiction are in this paper
                    source = next((b for b in beliefs if b.belief_id == constraint.source_id), None)
                    target = next((b for b in beliefs if b.belief_id == constraint.target_id), None)

                    if source and target:
                        flags.append(CredibilityFlag(
                            decision=Decision.BLOCK,
                            reason="Paper contains contradictory beliefs",
                            confidence=0.9,
                            field_name="self_contradiction",
                            expected="Consistent claims",
                            observed=f"'{source.content[:30]}...' contradicts '{target.content[:30]}...'",
                        ))

        return flags

    def check_duplicate_paper(
        self,
        article_id: str,
        existing_ids: Set[str]
    ) -> List[CredibilityFlag]:
        """Check if paper ID already exists in the web."""
        flags = []
        if article_id in existing_ids:
            flags.append(CredibilityFlag(
                decision=Decision.BLOCK,
                reason=f"Paper ID already exists: {article_id}",
                confidence=1.0,
                field_name="article_id",
                expected="Unique ID",
                observed=article_id,
            ))
        return flags

    # =========================================================================
    # REVIEW-LEVEL CHECKS (Likely problems)
    # =========================================================================

    def check_causal_warrant(
        self,
        constraints: List[Constraint],
        study_design: Optional[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[CredibilityFlag]:
        """
        Check if causal claims match study design warrant.

        Per Pearl: Check if claimed strength exceeds design's maximum.
        """
        flags = []
        max_warranted = get_design_strength(study_design)

        for constraint in constraints:
            # Only check causal constraints
            if constraint.causal_direction in [CausalDirection.FORWARD, CausalDirection.REVERSE]:
                strength = getattr(constraint, 'strength', 0.5)

                if strength > max_warranted + 0.1:  # 10% tolerance
                    flags.append(CredibilityFlag(
                        decision=Decision.REVIEW,
                        reason=f"Causal claim strength ({strength:.0%}) exceeds "
                               f"study design warrant ({max_warranted:.0%} for {study_design or 'unknown'})",
                        confidence=0.7,
                        field_name="causal_direction",
                        expected=f"≤{max_warranted:.0%}",
                        observed=f"{strength:.0%}",
                    ))

        return flags

    def check_scope_overreach(
        self,
        beliefs: List[Belief],
        sample_description: str,
        threshold: float = 0.5
    ) -> List[CredibilityFlag]:
        """
        Check if scope claims extend too far beyond sample.

        Per Cartwright: Most common failure is treating specific findings as universal.
        """
        flags = []

        for belief in beliefs:
            claimed_scope = None
            if belief.scope:
                claimed_scope = belief.scope.population

            distance = scope_distance(sample_description, claimed_scope)

            if distance > threshold:
                flags.append(CredibilityFlag(
                    decision=Decision.REVIEW,
                    reason=f"Scope may extend beyond sample (distance={distance:.2f})",
                    confidence=0.6 + 0.2 * distance,  # More confident for larger distances
                    field_name="scope",
                    expected=f"Scope matching sample: {sample_description[:50]}",
                    observed=f"Scope: {claimed_scope or 'universal'}",
                ))

        return flags

    def check_effect_size_plausibility(
        self,
        metadata: Dict[str, Any],
        study_type: Optional[str] = None
    ) -> List[CredibilityFlag]:
        """
        Check if effect sizes are within plausible ranges.

        Per Kaplan: d > 1.5 for environmental manipulation is suspicious.
        """
        flags = []

        # Effect size ranges by study type
        effect_ranges: Dict[str, Tuple[float, float]] = {
            "lab_experiment": (0.0, 1.5),
            "field_study": (0.0, 1.2),
            "survey": (0.0, 0.8),
            "meta_analysis": (0.0, 1.0),
            "default": (0.0, 2.0),
        }

        effect_size = metadata.get('effect_size')
        if effect_size is not None:
            d = abs(effect_size)
            range_key = study_type or "default"
            min_d, max_d = effect_ranges.get(range_key, effect_ranges["default"])

            if d > max_d:
                flags.append(CredibilityFlag(
                    decision=Decision.REVIEW,
                    reason=f"Effect size unusually large: d={d:.2f} (max expected: {max_d})",
                    confidence=0.6,
                    field_name="effect_size",
                    expected=f"d < {max_d}",
                    observed=f"d = {d:.2f}",
                ))

        return flags

    def check_credence_change(
        self,
        belief_id: str,
        pre_credence: float,
        post_credence: float,
        threshold: float = 0.3
    ) -> List[CredibilityFlag]:
        """
        Check if credence change is within expected range.

        Large changes from a single paper are suspicious.
        """
        flags = []
        change = abs(post_credence - pre_credence)

        if change > threshold:
            flags.append(CredibilityFlag(
                decision=Decision.REVIEW,
                reason=f"Large credence change: {change:.2f} (threshold: {threshold})",
                confidence=0.5 + 0.3 * (change - threshold) / (1 - threshold),
                field_name="credence_change",
                expected=f"Change < {threshold}",
                observed=f"Change = {change:.2f} ({pre_credence:.2f} → {post_credence:.2f})",
            ))

        return flags

    def check_causal_cycles(
        self,
        constraints: List[Constraint],
        existing_constraints: Optional[List[Constraint]] = None
    ) -> List[CredibilityFlag]:
        """
        Check if new constraints create causal cycles.

        Per Pearl: Cycles aren't always wrong (feedback loops exist)
        but should be reviewed.
        """
        flags = []

        # Build directed graph from constraints
        graph: Dict[str, Set[str]] = {}
        all_constraints = list(constraints)
        if existing_constraints:
            all_constraints.extend(existing_constraints)

        for constraint in all_constraints:
            # Only consider causal/explanatory constraints
            if constraint.causal_direction in [CausalDirection.FORWARD, CausalDirection.REVERSE]:
                source = constraint.source_id
                target = constraint.target_id

                if constraint.causal_direction == CausalDirection.REVERSE:
                    source, target = target, source

                if source not in graph:
                    graph[source] = set()
                graph[source].add(target)

            elif constraint.constraint_type == ConstraintType.EXPLAINS:
                source = constraint.source_id
                target = constraint.target_id
                if source not in graph:
                    graph[source] = set()
                graph[source].add(target)

        # Find cycles using DFS
        cycles = self._find_cycles(graph)

        for cycle in cycles:
            # Check if cycle involves new constraints
            new_ids = {c.source_id for c in constraints} | {c.target_id for c in constraints}
            if any(node in new_ids for node in cycle):
                flags.append(CredibilityFlag(
                    decision=Decision.REVIEW,
                    reason=f"Causal cycle detected: {' → '.join(cycle[:4])}{'...' if len(cycle) > 4 else ''}",
                    confidence=0.6,
                    field_name="causal_cycle",
                    expected="No causal cycles (or documented feedback loop)",
                    observed=f"Cycle of length {len(cycle)}",
                ))

        return flags

    def _find_cycles(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        """Find all cycles in a directed graph using DFS."""
        cycles = []
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node: str):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)

            path.pop()
            rec_stack.remove(node)

        for node in graph:
            if node not in visited:
                dfs(node)

        return cycles

    def check_missing_methodology(
        self,
        metadata: Dict[str, Any]
    ) -> List[CredibilityFlag]:
        """
        Check for missing critical methodology information.

        Per Mayo: Can't evaluate claims without knowing methodology.
        """
        flags = []

        # Check for missing sample size
        sample_size = metadata.get('sample_size')
        study_design = metadata.get('study_design')
        sample_description = metadata.get('sample_description', '')

        # Missing sample size is concerning for empirical claims
        if sample_size is None and study_design not in ['theory', 'theory_book', 'review', None]:
            flags.append(CredibilityFlag(
                decision=Decision.REVIEW,
                reason="Missing sample size for empirical study",
                confidence=0.6,
                field_name="sample_size",
                expected="Sample size reported",
                observed="Not reported",
            ))

        # No sample description
        if not sample_description and study_design not in ['theory', 'theory_book', 'review', None]:
            flags.append(CredibilityFlag(
                decision=Decision.REVIEW,
                reason="Missing sample description",
                confidence=0.5,
                field_name="sample_description",
                expected="Sample description (population, demographics)",
                observed="Not reported",
            ))

        return flags

    def check_subgroup_sample_size(
        self,
        beliefs: List[Belief],
        metadata: Dict[str, Any],
        min_subgroup_n: int = 50
    ) -> List[CredibilityFlag]:
        """
        Check if claims about subgroups have adequate sample sizes.

        Per Simon: Total N can be misleading when claims target specific subgroups.
        """
        flags = []

        subgroup_sizes = metadata.get('subgroup_sizes', {})
        if not subgroup_sizes:
            return flags

        for belief in beliefs:
            # Check if belief is scoped to a specific population
            if belief.scope and belief.scope.population:
                claimed_pop = belief.scope.population.lower()

                # Look for matching subgroup in metadata
                for subgroup_name, subgroup_n in subgroup_sizes.items():
                    if subgroup_name.lower() in claimed_pop or claimed_pop in subgroup_name.lower():
                        if subgroup_n < min_subgroup_n:
                            flags.append(CredibilityFlag(
                                decision=Decision.REVIEW,
                                reason=f"Claim about '{claimed_pop}' uses subgroup N={subgroup_n} "
                                       f"(below recommended {min_subgroup_n})",
                                confidence=0.65,
                                field_name="subgroup_sample_size",
                                expected=f"N ≥ {min_subgroup_n} for subgroup claims",
                                observed=f"N = {subgroup_n} for {subgroup_name}",
                            ))
                        break

        return flags

    def check_statistical_validity(
        self,
        metadata: Dict[str, Any]
    ) -> List[CredibilityFlag]:
        """
        Check for statistical interpretation issues.

        Catches: CI spanning zero, multiple comparison problems, etc.
        """
        flags = []

        # Check if CI spans zero
        ci = metadata.get('confidence_interval')
        p_value = metadata.get('p_value')

        if ci and len(ci) == 2:
            lower, upper = ci
            if lower < 0 < upper:
                # CI spans zero - always flag for review
                # This indicates the effect may not be real
                flags.append(CredibilityFlag(
                    decision=Decision.REVIEW,
                    reason=f"Confidence interval spans zero [{lower:.2f}, {upper:.2f}]",
                    confidence=0.7 if (p_value and p_value > 0.05) else 0.8,
                    field_name="confidence_interval",
                    expected="CI not spanning zero for claimed effect",
                    observed=f"[{lower:.2f}, {upper:.2f}]" + (f" (p={p_value})" if p_value else ""),
                ))

        # Check for multiple comparison issues
        n_comparisons = metadata.get('n_comparisons')
        n_significant = metadata.get('n_significant')
        correction_applied = metadata.get('correction_applied', False)

        if n_comparisons and n_significant is not None and not correction_applied:
            expected_by_chance = n_comparisons * 0.05
            # Flag if significant results are within 3x of what's expected by chance
            # E.g., 15 comparisons => ~0.75 expected, so flag if ≤2.25 significant
            # This catches cases where results might just be noise
            import math
            # Use binomial approximation: expected ± 2*SD covers ~95% of chance findings
            # SD = sqrt(n * p * (1-p)) ≈ sqrt(n * 0.05 * 0.95)
            sd = math.sqrt(n_comparisons * 0.05 * 0.95)
            upper_bound = expected_by_chance + 2.5 * sd  # ~99% upper bound by chance

            if n_significant <= upper_bound:
                flags.append(CredibilityFlag(
                    decision=Decision.REVIEW,
                    reason=f"Multiple comparison concern: {n_significant}/{n_comparisons} "
                           f"significant (expected ~{expected_by_chance:.1f}±{sd:.1f} by chance)",
                    confidence=0.6,
                    field_name="multiple_comparison",
                    expected="Correction for multiple comparisons or results well above chance",
                    observed=f"{n_significant} of {n_comparisons} without correction",
                ))

        return flags

    # =========================================================================
    # SEVERITY 3 CHECKS (Minor - unusual patterns)
    # =========================================================================

    def check_semantic_coherence(
        self,
        constraints: List[Constraint],
        beliefs: Optional[Dict[str, Belief]] = None,
        similarity_threshold: float = 0.15
    ) -> List[CredibilityFlag]:
        """
        Check if constraints connect semantically related beliefs.

        Per Bates: Use taxonomy distance, keyword overlap, or embeddings.

        This is a Severity 3 (Minor) check - unusual patterns that might be fine.

        Args:
            constraints: New constraints to check
            beliefs: Dict of belief_id -> Belief (from web or snapshot)
            similarity_threshold: Minimum similarity score (0-1)

        Returns:
            List of flags for semantically distant constraint pairs
        """
        flags = []

        if not beliefs:
            # Try to get from snapshot
            if self.snapshot:
                beliefs = self.snapshot.beliefs
            else:
                return flags  # Can't check without beliefs

        for constraint in constraints:
            source_belief = beliefs.get(constraint.source_id)
            target_belief = beliefs.get(constraint.target_id)

            if not source_belief or not target_belief:
                continue

            # Compute semantic similarity
            similarity = self._compute_semantic_similarity(source_belief, target_belief)

            if similarity < similarity_threshold:
                flags.append(CredibilityFlag(
                    decision=Decision.REVIEW,
                    reason=f"Constraint connects semantically distant beliefs (similarity={similarity:.2f})",
                    confidence=0.4 + 0.3 * (similarity_threshold - similarity),
                    field_name="semantic_coherence",
                    expected=f"Semantic similarity ≥ {similarity_threshold}",
                    observed=f"Similarity = {similarity:.2f}",
                ))

        return flags

    def _compute_semantic_similarity(
        self,
        belief1: Belief,
        belief2: Belief
    ) -> float:
        """
        Compute semantic similarity between two beliefs.

        Uses multiple methods per Bates:
        1. Environment taxonomy distance (if both have environment_id)
        2. Outcome taxonomy distance (if both have outcome_id)
        3. Keyword overlap (Jaccard similarity)
        4. Theory overlap (if both have theory_ids)

        Returns average of available methods (0-1, higher = more similar).
        """
        scores = []

        # 1. Environment taxonomy similarity
        env1 = getattr(belief1, 'environment_id', None)
        env2 = getattr(belief2, 'environment_id', None)
        if env1 and env2:
            # Simple matching for now (could use taxonomy distance)
            if env1 == env2:
                scores.append(1.0)
            elif self._share_taxonomy_prefix(env1, env2):
                scores.append(0.6)
            else:
                scores.append(0.2)

        # 2. Outcome taxonomy similarity
        out1 = getattr(belief1, 'outcome_id', None)
        out2 = getattr(belief2, 'outcome_id', None)
        if out1 and out2:
            if out1 == out2:
                scores.append(1.0)
            elif self._share_taxonomy_prefix(out1, out2):
                scores.append(0.6)
            else:
                scores.append(0.2)

        # 3. Keyword overlap (Jaccard)
        content1 = belief1.content.lower() if hasattr(belief1, 'content') else ""
        content2 = belief2.content.lower() if hasattr(belief2, 'content') else ""

        # Remove common stopwords
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                     'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                     'would', 'could', 'should', 'may', 'might', 'must', 'can',
                     'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
                     'as', 'into', 'through', 'during', 'before', 'after',
                     'above', 'below', 'between', 'under', 'and', 'but', 'or',
                     'nor', 'so', 'yet', 'both', 'either', 'neither', 'not',
                     'only', 'own', 'same', 'than', 'too', 'very', 'just',
                     'that', 'this', 'these', 'those', 'it', 'its'}

        words1 = {w for w in content1.split() if w not in stopwords and len(w) > 2}
        words2 = {w for w in content2.split() if w not in stopwords and len(w) > 2}

        if words1 and words2:
            jaccard = len(words1 & words2) / len(words1 | words2)
            scores.append(jaccard)

        # 4. Theory overlap
        theories1 = set(getattr(belief1, 'theory_ids', []) or [])
        theories2 = set(getattr(belief2, 'theory_ids', []) or [])
        if theories1 and theories2:
            theory_overlap = len(theories1 & theories2) / len(theories1 | theories2)
            scores.append(theory_overlap)

        # Return average or 0.5 if no scores available
        if scores:
            return sum(scores) / len(scores)
        return 0.5  # Neutral if we can't compute

    def _share_taxonomy_prefix(self, id1: str, id2: str, levels: int = 2) -> bool:
        """Check if two taxonomy IDs share a common prefix."""
        parts1 = id1.split('.')[:levels]
        parts2 = id2.split('.')[:levels]
        return parts1 == parts2 and len(parts1) > 0

    def check_new_stubs(
        self,
        beliefs: List[Belief]
    ) -> List[CredibilityFlag]:
        """
        Note when stubs are created (findings without theoretical home).

        Per Quinean principles: Stubs are expected but should be tracked.
        This is informational, not necessarily a problem.
        """
        flags = []

        for belief in beliefs:
            if getattr(belief, 'status', None) == BeliefStatus.STUB:
                flags.append(CredibilityFlag(
                    decision=Decision.REVIEW,
                    reason="New stub created (finding without theoretical home)",
                    confidence=0.3,  # Low confidence - stubs are often fine
                    field_name="stub_creation",
                    expected="Belief integrated with theory",
                    observed=f"Stub: {belief.content[:50]}...",
                ))

        return flags


# =============================================================================
# CALIBRATION (per Simon: explicit calibration procedure)
# =============================================================================

@dataclass
class CalibrationResult:
    """Result of calibrating thresholds from Gold Standard."""
    check_name: str
    optimal_threshold: float
    sensitivity: float
    specificity: float
    n_samples: int
    rationale: str


def calibrate_thresholds(
    gold_standard_reports: List[Tuple[CredibilityReport, bool]],
    target_sensitivity: float = 0.8
) -> Dict[str, CalibrationResult]:
    """
    Calibrate thresholds based on Gold Standard performance.

    Per Simon: Explicit calibration procedure.

    Args:
        gold_standard_reports: List of (report, is_actually_problem) tuples
        target_sensitivity: Target sensitivity level (default 80%)

    Returns:
        Dict mapping check names to calibration results
    """
    results = {}

    # Group by flag type
    flag_outcomes: Dict[str, List[Tuple[float, bool]]] = {}

    for report, is_problem in gold_standard_reports:
        for flag in report.flags:
            flag_type = flag.field_name or "unknown"
            if flag_type not in flag_outcomes:
                flag_outcomes[flag_type] = []
            flag_outcomes[flag_type].append((flag.confidence, is_problem))

    # For each flag type, find optimal threshold
    for flag_type, outcomes in flag_outcomes.items():
        if len(outcomes) < 5:
            # Not enough data
            results[flag_type] = CalibrationResult(
                check_name=flag_type,
                optimal_threshold=0.5,
                sensitivity=0.0,
                specificity=0.0,
                n_samples=len(outcomes),
                rationale="Insufficient data for calibration"
            )
            continue

        # Sort by confidence
        outcomes.sort(key=lambda x: x[0])

        # Find threshold achieving target sensitivity
        best_threshold = 0.5
        best_sens = 0.0
        best_spec = 0.0

        for threshold in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
            tp = sum(1 for conf, is_prob in outcomes if conf >= threshold and is_prob)
            fn = sum(1 for conf, is_prob in outcomes if conf < threshold and is_prob)
            tn = sum(1 for conf, is_prob in outcomes if conf < threshold and not is_prob)
            fp = sum(1 for conf, is_prob in outcomes if conf >= threshold and not is_prob)

            sens = tp / (tp + fn) if (tp + fn) > 0 else 0
            spec = tn / (tn + fp) if (tn + fp) > 0 else 0

            if sens >= target_sensitivity and spec > best_spec:
                best_threshold = threshold
                best_sens = sens
                best_spec = spec

        results[flag_type] = CalibrationResult(
            check_name=flag_type,
            optimal_threshold=best_threshold,
            sensitivity=best_sens,
            specificity=best_spec,
            n_samples=len(outcomes),
            rationale=f"Threshold {best_threshold} achieves {best_sens:.0%} sensitivity, {best_spec:.0%} specificity"
        )

    return results


# =============================================================================
# CREDIBILITY TESTER (Main Interface)
# =============================================================================

class CredibilityTester:
    """
    Main interface for credibility testing.

    Coordinates all checks and produces CredibilityReport.
    """

    def __init__(self, web: Optional[WebOfBelief] = None):
        """
        Initialize tester.

        Args:
            web: The web of belief (for duplicate checking, etc.)
        """
        self.web = web
        self.snapshot = WebSnapshot.from_web(web) if web else None

    def evaluate(
        self,
        article_id: str,
        beliefs: List[Belief],
        constraints: List[Constraint],
        metadata: Optional[Dict[str, Any]] = None
    ) -> CredibilityReport:
        """
        Evaluate credibility of an article's extraction.

        Args:
            article_id: Unique identifier for the article
            beliefs: Extracted beliefs
            constraints: Extracted constraints
            metadata: Additional metadata (sample_size, p_value, effect_size, etc.)

        Returns:
            CredibilityReport with flags and overall decision
        """
        report = CredibilityReport(
            article_id=article_id,
            timestamp=datetime.now(timezone.utc),
        )

        meta = metadata or {}
        checks = CredibilityChecks(self.snapshot)

        # Get existing paper IDs for duplicate check
        existing_ids: Set[str] = set()
        if self.web:
            for belief in self.web.beliefs.values():
                existing_ids.update(belief.paper_ids)

        # Run BLOCK-level checks
        for flag in safe_check(checks.check_numeric_validity, beliefs, meta):
            report.add_flag(flag)

        for flag in safe_check(checks.check_self_contradiction, beliefs, constraints):
            report.add_flag(flag)

        for flag in safe_check(checks.check_duplicate_paper, article_id, existing_ids):
            report.add_flag(flag)

        # Run REVIEW-level checks
        study_design = meta.get('study_design')
        sample_description = meta.get('sample_description', '')

        for flag in safe_check(checks.check_causal_warrant, constraints, study_design, meta):
            report.add_flag(flag)

        for flag in safe_check(checks.check_scope_overreach, beliefs, sample_description):
            report.add_flag(flag)

        for flag in safe_check(checks.check_effect_size_plausibility, meta, study_design):
            report.add_flag(flag)

        # Sprint C additions
        # Causal cycle detection
        existing_constraints = []
        if self.snapshot:
            existing_constraints = self.snapshot.constraints
        for flag in safe_check(checks.check_causal_cycles, constraints, existing_constraints):
            report.add_flag(flag)

        # Statistical validity checks
        for flag in safe_check(checks.check_statistical_validity, meta):
            report.add_flag(flag)

        # Missing methodology check (Sprint D)
        for flag in safe_check(checks.check_missing_methodology, meta):
            report.add_flag(flag)

        # Subgroup sample size check (Sprint D)
        for flag in safe_check(checks.check_subgroup_sample_size, beliefs, meta):
            report.add_flag(flag)

        # Severity 3 checks (Minor - unusual patterns)
        # Semantic coherence check
        beliefs_dict = {b.belief_id: b for b in beliefs} if beliefs else {}
        if self.snapshot:
            beliefs_dict.update(self.snapshot.beliefs)
        for flag in safe_check(checks.check_semantic_coherence, constraints, beliefs_dict):
            report.add_flag(flag)

        # Stub creation check
        for flag in safe_check(checks.check_new_stubs, beliefs):
            report.add_flag(flag)

        # Update overall decision based on flags
        if report.is_clean:
            # No flags = implicit accept
            pass
        elif any(f.decision == Decision.BLOCK for f in report.flags):
            report.overall_decision = Decision.BLOCK
        else:
            report.overall_decision = Decision.REVIEW

        logger.info(
            f"Credibility evaluation for {article_id}: "
            f"{len(report.flags)} flags, decision={report.overall_decision.value if report.flags else 'accept'}"
        )

        return report

    def evaluate_with_credence_tracking(
        self,
        article_id: str,
        beliefs: List[Belief],
        constraints: List[Constraint],
        metadata: Optional[Dict[str, Any]] = None,
        pre_credences: Optional[Dict[str, float]] = None,
        post_credences: Optional[Dict[str, float]] = None
    ) -> CredibilityReport:
        """
        Evaluate with additional credence change tracking.

        For use when we can compare before/after states.
        """
        # Run standard evaluation
        report = self.evaluate(article_id, beliefs, constraints, metadata)

        # Add credence change checks if provided
        if pre_credences and post_credences:
            checks = CredibilityChecks(self.snapshot)
            for belief_id in post_credences:
                if belief_id in pre_credences:
                    for flag in safe_check(
                        checks.check_credence_change,
                        belief_id,
                        pre_credences[belief_id],
                        post_credences[belief_id]
                    ):
                        report.add_flag(flag)

        return report


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_tester(web: Optional[WebOfBelief] = None) -> CredibilityTester:
    """Create a credibility tester instance."""
    return CredibilityTester(web)


def quick_check(
    beliefs: List[Belief],
    constraints: List[Constraint],
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Quick check without full report.

    Returns True if no BLOCK-level flags.
    """
    tester = CredibilityTester()
    report = tester.evaluate("quick_check", beliefs, constraints, metadata)
    return report.overall_decision != Decision.BLOCK
