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
    Two-category initial system (per Lampson critique).

    Start simple, add categories only when needed.
    ACCEPT is implicit (no flags = accept).
    """
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
    """
    article_id: str
    timestamp: datetime
    flags: List[CredibilityFlag] = field(default_factory=list)
    overall_decision: Decision = Decision.REVIEW  # Default to review if any flags

    def add_flag(self, flag: CredibilityFlag) -> None:
        """Add a flag and update overall decision."""
        self.flags.append(flag)
        # BLOCK wins over REVIEW
        if flag.decision == Decision.BLOCK:
            self.overall_decision = Decision.BLOCK
        elif self.overall_decision != Decision.BLOCK:
            self.overall_decision = Decision.REVIEW

    @property
    def is_clean(self) -> bool:
        """Returns True if no flags were raised."""
        return len(self.flags) == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'article_id': self.article_id,
            'timestamp': self.timestamp.isoformat(),
            'flags': [f.to_dict() for f in self.flags],
            'overall_decision': self.overall_decision.value if self.flags else 'accept',
            'n_flags': len(self.flags),
        }

    def to_explanation_context(self) -> Dict[str, Any]:
        """
        Interface for TODO 2 integration.
        Per Phase D: Define integration interfaces.
        """
        return {
            'article_id': self.article_id,
            'decision': self.overall_decision.value if self.flags else 'accept',
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
        """
        flags = []
        meta = metadata or {}

        # Check credence values
        for belief in beliefs:
            if belief.credence.value <= 0 or belief.credence.value >= 1:
                flags.append(CredibilityFlag(
                    decision=Decision.BLOCK,
                    reason=f"Credence outside (0,1): {belief.credence.value}",
                    confidence=1.0,
                    field_name="credence",
                    expected="(0, 1)",
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
