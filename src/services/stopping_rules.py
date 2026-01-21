"""
Stopping Rules Service
======================

Determines when evidence gathering or analysis can stop.

Per expert panel:
- Define clear stopping criteria (Simon)
- Saturation detection for qualitative sufficiency (Bates)
- Cost-benefit analysis for additional search (Pearl)

Date: January 21, 2026
Phase D Sprint D1
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Set
from enum import Enum
import math

from src.services.web_of_belief import WebOfBelief, Belief


# =============================================================================
# Stopping Criteria
# =============================================================================

class StoppingReason(Enum):
    """Reasons why we might stop searching."""
    SATURATION = "saturation"            # No new information being found
    CONFIDENCE_THRESHOLD = "confidence"  # Sufficient confidence reached
    EVIDENCE_COUNT = "count"             # Enough evidence gathered
    TIME_BUDGET = "time"                 # Search time exceeded
    COST_BENEFIT = "cost_benefit"        # Marginal value too low
    MANUAL = "manual"                    # User stopped manually
    COVERAGE = "coverage"                # All relevant areas covered
    CONTRADICTION_STABLE = "stable"      # Contradictions have stabilized


@dataclass
class StoppingCriterion:
    """A single stopping criterion and its status."""
    name: str
    description: str
    threshold: float
    current_value: float
    is_met: bool
    reason: StoppingReason


@dataclass
class StoppingDecision:
    """Overall decision about whether to stop."""
    should_stop: bool
    primary_reason: Optional[StoppingReason]
    confidence: float  # 0-1 confidence in the stop decision
    criteria_met: List[StoppingCriterion]
    criteria_not_met: List[StoppingCriterion]
    recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            'should_stop': self.should_stop,
            'primary_reason': self.primary_reason.value if self.primary_reason else None,
            'confidence': self.confidence,
            'criteria_met': [
                {
                    'name': c.name,
                    'description': c.description,
                    'threshold': c.threshold,
                    'current_value': c.current_value,
                    'reason': c.reason.value
                }
                for c in self.criteria_met
            ],
            'criteria_not_met': [
                {
                    'name': c.name,
                    'description': c.description,
                    'threshold': c.threshold,
                    'current_value': c.current_value,
                    'reason': c.reason.value
                }
                for c in self.criteria_not_met
            ],
            'recommendation': self.recommendation
        }


# =============================================================================
# Stopping Rules Engine
# =============================================================================

class StoppingRulesEngine:
    """
    Engine for determining when to stop evidence gathering.

    Uses multiple criteria to make a balanced decision about
    when sufficient evidence has been gathered.
    """

    def __init__(
        self,
        web: WebOfBelief,
        min_beliefs: int = 5,
        confidence_threshold: float = 0.7,
        saturation_window: int = 10,
        saturation_threshold: float = 0.8
    ):
        """
        Initialize stopping rules engine.

        Args:
            web: The web of belief to analyze
            min_beliefs: Minimum beliefs before considering stop
            confidence_threshold: Credence threshold for high confidence
            saturation_window: Number of recent additions to check
            saturation_threshold: Proportion of duplicates for saturation
        """
        self.web = web
        self.min_beliefs = min_beliefs
        self.confidence_threshold = confidence_threshold
        self.saturation_window = saturation_window
        self.saturation_threshold = saturation_threshold

        # Track recent additions for saturation detection
        self._recent_additions: List[str] = []
        self._seen_content_hashes: Set[str] = set()

    def evaluate(self, topic: Optional[str] = None) -> StoppingDecision:
        """
        Evaluate whether to stop searching.

        Args:
            topic: Optional topic to focus evaluation on

        Returns:
            StoppingDecision with recommendation
        """
        criteria_met = []
        criteria_not_met = []

        # Get relevant beliefs
        if topic:
            beliefs = self._get_beliefs_for_topic(topic)
        else:
            beliefs = list(self.web.beliefs.values())

        # Evaluate each criterion
        saturation = self._check_saturation(beliefs)
        if saturation.is_met:
            criteria_met.append(saturation)
        else:
            criteria_not_met.append(saturation)

        confidence = self._check_confidence(beliefs)
        if confidence.is_met:
            criteria_met.append(confidence)
        else:
            criteria_not_met.append(confidence)

        count = self._check_evidence_count(beliefs)
        if count.is_met:
            criteria_met.append(count)
        else:
            criteria_not_met.append(count)

        coverage = self._check_coverage(beliefs)
        if coverage.is_met:
            criteria_met.append(coverage)
        else:
            criteria_not_met.append(coverage)

        stability = self._check_contradiction_stability(beliefs)
        if stability.is_met:
            criteria_met.append(stability)
        else:
            criteria_not_met.append(stability)

        # Make decision
        return self._make_decision(criteria_met, criteria_not_met, beliefs)

    def _get_beliefs_for_topic(self, topic: str) -> List[Belief]:
        """Get beliefs related to a topic."""
        topic_lower = topic.lower()
        return [
            b for b in self.web.beliefs.values()
            if topic_lower in b.content.lower()
        ]

    def _check_saturation(self, beliefs: List[Belief]) -> StoppingCriterion:
        """Check if we've reached information saturation."""
        if len(beliefs) < self.saturation_window:
            return StoppingCriterion(
                name="Information Saturation",
                description="No new unique information being found",
                threshold=self.saturation_threshold,
                current_value=0.0,
                is_met=False,
                reason=StoppingReason.SATURATION
            )

        # Check recent additions for duplicates/similar content
        recent = beliefs[-self.saturation_window:]
        unique_themes = set()

        for belief in recent:
            # Simple theme extraction (would be more sophisticated in production)
            words = set(belief.content.lower().split())
            theme_key = frozenset(list(words)[:5])  # First 5 words as theme key
            unique_themes.add(theme_key)

        saturation_ratio = 1 - (len(unique_themes) / len(recent))

        return StoppingCriterion(
            name="Information Saturation",
            description="No new unique information being found",
            threshold=self.saturation_threshold,
            current_value=saturation_ratio,
            is_met=saturation_ratio >= self.saturation_threshold,
            reason=StoppingReason.SATURATION
        )

    def _check_confidence(self, beliefs: List[Belief]) -> StoppingCriterion:
        """Check if we've reached sufficient confidence."""
        if not beliefs:
            return StoppingCriterion(
                name="Confidence Threshold",
                description="Average credence meets threshold",
                threshold=self.confidence_threshold,
                current_value=0.0,
                is_met=False,
                reason=StoppingReason.CONFIDENCE_THRESHOLD
            )

        avg_credence = sum(b.credence.value for b in beliefs) / len(beliefs)

        return StoppingCriterion(
            name="Confidence Threshold",
            description="Average credence meets threshold",
            threshold=self.confidence_threshold,
            current_value=avg_credence,
            is_met=avg_credence >= self.confidence_threshold,
            reason=StoppingReason.CONFIDENCE_THRESHOLD
        )

    def _check_evidence_count(self, beliefs: List[Belief]) -> StoppingCriterion:
        """Check if we have minimum evidence count."""
        return StoppingCriterion(
            name="Minimum Evidence",
            description="Sufficient evidence quantity gathered",
            threshold=float(self.min_beliefs),
            current_value=float(len(beliefs)),
            is_met=len(beliefs) >= self.min_beliefs,
            reason=StoppingReason.EVIDENCE_COUNT
        )

    def _check_coverage(self, beliefs: List[Belief]) -> StoppingCriterion:
        """Check if we have coverage across epistemic levels."""
        if not beliefs:
            return StoppingCriterion(
                name="Epistemic Coverage",
                description="Evidence across different epistemic levels",
                threshold=0.5,
                current_value=0.0,
                is_met=False,
                reason=StoppingReason.COVERAGE
            )

        # Count unique epistemic levels
        levels = set()
        for belief in beliefs:
            if belief.level:
                levels.add(belief.level.value)

        # We want at least 2 different levels for good coverage
        coverage = len(levels) / 4  # 4 possible levels

        return StoppingCriterion(
            name="Epistemic Coverage",
            description="Evidence across different epistemic levels",
            threshold=0.5,  # At least 2 of 4 levels
            current_value=coverage,
            is_met=coverage >= 0.5,
            reason=StoppingReason.COVERAGE
        )

    def _check_contradiction_stability(self, beliefs: List[Belief]) -> StoppingCriterion:
        """Check if contradictions have stabilized."""
        if len(beliefs) < 5:
            return StoppingCriterion(
                name="Contradiction Stability",
                description="Contradiction rate has stabilized",
                threshold=0.8,
                current_value=0.0,
                is_met=False,
                reason=StoppingReason.CONTRADICTION_STABLE
            )

        # Check contradiction rate in recent vs older beliefs
        midpoint = len(beliefs) // 2
        older = beliefs[:midpoint]
        recent = beliefs[midpoint:]

        older_contested = sum(1 for b in older if b.contested) / len(older) if older else 0
        recent_contested = sum(1 for b in recent if b.contested) / len(recent) if recent else 0

        # Stability = how similar the rates are
        if older_contested + recent_contested == 0:
            stability = 1.0  # No contradictions = stable
        else:
            diff = abs(older_contested - recent_contested)
            max_rate = max(older_contested, recent_contested)
            stability = 1 - (diff / max_rate) if max_rate > 0 else 1.0

        return StoppingCriterion(
            name="Contradiction Stability",
            description="Contradiction rate has stabilized",
            threshold=0.8,
            current_value=stability,
            is_met=stability >= 0.8,
            reason=StoppingReason.CONTRADICTION_STABLE
        )

    def _make_decision(
        self,
        criteria_met: List[StoppingCriterion],
        criteria_not_met: List[StoppingCriterion],
        beliefs: List[Belief]
    ) -> StoppingDecision:
        """Make overall stopping decision."""
        # Count how many criteria are met
        total = len(criteria_met) + len(criteria_not_met)
        met_ratio = len(criteria_met) / total if total > 0 else 0

        # Decision logic
        # - Must have minimum evidence
        # - At least 3 of 5 criteria should be met
        has_min_evidence = any(
            c.reason == StoppingReason.EVIDENCE_COUNT and c.is_met
            for c in criteria_met
        )

        should_stop = has_min_evidence and met_ratio >= 0.6

        # Determine primary reason
        primary_reason = None
        if criteria_met:
            # Pick the most significant met criterion
            priority = [
                StoppingReason.SATURATION,
                StoppingReason.CONFIDENCE_THRESHOLD,
                StoppingReason.COVERAGE,
                StoppingReason.EVIDENCE_COUNT,
                StoppingReason.CONTRADICTION_STABLE
            ]
            for reason in priority:
                for c in criteria_met:
                    if c.reason == reason:
                        primary_reason = reason
                        break
                if primary_reason:
                    break

        # Calculate confidence in decision
        confidence = met_ratio

        # Generate recommendation
        if should_stop:
            recommendation = self._generate_stop_recommendation(criteria_met, beliefs)
        else:
            recommendation = self._generate_continue_recommendation(criteria_not_met)

        return StoppingDecision(
            should_stop=should_stop,
            primary_reason=primary_reason,
            confidence=confidence,
            criteria_met=criteria_met,
            criteria_not_met=criteria_not_met,
            recommendation=recommendation
        )

    def _generate_stop_recommendation(
        self,
        criteria_met: List[StoppingCriterion],
        beliefs: List[Belief]
    ) -> str:
        """Generate recommendation for stopping."""
        reasons = []
        for c in criteria_met[:3]:  # Top 3 reasons
            if c.reason == StoppingReason.SATURATION:
                reasons.append("no new information being found")
            elif c.reason == StoppingReason.CONFIDENCE_THRESHOLD:
                reasons.append(f"confidence level of {c.current_value:.0%}")
            elif c.reason == StoppingReason.COVERAGE:
                reasons.append("good coverage across epistemic levels")
            elif c.reason == StoppingReason.EVIDENCE_COUNT:
                reasons.append(f"{int(c.current_value)} pieces of evidence")
            elif c.reason == StoppingReason.CONTRADICTION_STABLE:
                reasons.append("contradictions have stabilized")

        reason_text = ", ".join(reasons)
        return f"Evidence gathering appears sufficient: {reason_text}. Consider finalizing conclusions."

    def _generate_continue_recommendation(
        self,
        criteria_not_met: List[StoppingCriterion]
    ) -> str:
        """Generate recommendation for continuing."""
        gaps = []
        for c in criteria_not_met[:3]:  # Top 3 gaps
            if c.reason == StoppingReason.EVIDENCE_COUNT:
                needed = int(c.threshold - c.current_value)
                gaps.append(f"gather {needed} more pieces of evidence")
            elif c.reason == StoppingReason.CONFIDENCE_THRESHOLD:
                gaps.append("seek higher-quality sources")
            elif c.reason == StoppingReason.COVERAGE:
                gaps.append("expand to different epistemic levels")
            elif c.reason == StoppingReason.SATURATION:
                gaps.append("explore additional sources")

        gap_text = "; ".join(gaps) if gaps else "continue gathering evidence"
        return f"Consider: {gap_text}."


# =============================================================================
# Convenience Functions
# =============================================================================

def evaluate_stopping(
    web: WebOfBelief,
    topic: Optional[str] = None,
    min_beliefs: int = 5,
    confidence_threshold: float = 0.7
) -> StoppingDecision:
    """
    Convenience function to evaluate stopping criteria.

    Args:
        web: The web of belief
        topic: Optional topic to focus on
        min_beliefs: Minimum beliefs before stopping
        confidence_threshold: Required confidence level

    Returns:
        StoppingDecision with recommendation
    """
    engine = StoppingRulesEngine(
        web,
        min_beliefs=min_beliefs,
        confidence_threshold=confidence_threshold
    )
    return engine.evaluate(topic)
