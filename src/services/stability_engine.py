"""
Stability Engine
================

Stability detection and reporting for belief systems.

Tier 1 implementation per expert panel feedback:
- Credence stability tracking (Simon)
- Oscillation detection for contested beliefs (Epistemologist)
- Publication bias estimation (Cartwright)
- VOI gap cross-reference (Simon)
- Satisficing coherence framing (Epistemologist)

Date: January 20, 2026
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from datetime import datetime, timezone
import logging

from src.services.web_of_belief import (
    WebOfBelief,
    Belief
)

logger = logging.getLogger(__name__)


# =============================================================================
# Data Structures
# =============================================================================

class StabilityLevel(Enum):
    """Overall stability classification."""
    STABLE = "stable"                  # All beliefs within threshold
    CONVERGING = "converging"          # Trending toward stability
    UNSTABLE = "unstable"              # Significant changes ongoing
    CONTESTED = "contested"            # Genuine disagreement in literature


class PublicationBiasRisk(Enum):
    """Publication bias risk level."""
    LOW = "low"           # Good null result representation
    MODERATE = "moderate"  # Some concern
    HIGH = "high"         # Likely biased toward positive results
    UNKNOWN = "unknown"   # Insufficient data


@dataclass
class BeliefStabilityInfo:
    """Stability information for a single belief."""
    belief_id: str
    content: str
    credence: float
    max_delta_in_window: float
    is_stable: bool
    is_contested: bool
    history_length: int
    credence_range: Optional[Tuple[float, float]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'belief_id': self.belief_id,
            'content': self.content,
            'credence': self.credence,
            'max_delta_in_window': self.max_delta_in_window,
            'is_stable': self.is_stable,
            'is_contested': self.is_contested,
            'history_length': self.history_length,
            'credence_range': list(self.credence_range) if self.credence_range else None
        }


@dataclass
class GapInfo:
    """Information about an epistemic gap."""
    gap_id: str
    description: str
    gap_type: str  # 'uncertain' or 'unexplored'
    related_beliefs: List[str]
    voi_score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            'gap_id': self.gap_id,
            'description': self.description,
            'gap_type': self.gap_type,
            'related_beliefs': self.related_beliefs,
            'voi_score': self.voi_score
        }


@dataclass
class PublicationBiasInfo:
    """Publication bias assessment."""
    risk_level: PublicationBiasRisk
    null_result_ratio: float  # Proportion of null/negative results
    total_studies: int
    null_studies: int
    confidence: float  # Confidence in the assessment
    warning_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'risk_level': self.risk_level.value,
            'null_result_ratio': self.null_result_ratio,
            'total_studies': self.total_studies,
            'null_studies': self.null_studies,
            'confidence': self.confidence,
            'warning_message': self.warning_message
        }


@dataclass
class StabilityReport:
    """
    Complete stability report.

    Per expert panel (Epistemologist): Frame stability as "given current
    evidence" not "the web is done." New evidence can always cause revision.
    """
    # Overall status
    stability_level: StabilityLevel
    papers_processed: int
    stable_for_last_n: int

    # Metrics
    max_credence_change: float
    coherence_score: float
    convergence_achieved: bool

    # Belief breakdown
    total_beliefs: int
    stable_beliefs: int
    unstable_beliefs: int
    contested_beliefs: int

    # Detailed lists
    stable_belief_list: List[BeliefStabilityInfo]
    unstable_belief_list: List[BeliefStabilityInfo]
    contested_belief_list: List[BeliefStabilityInfo]

    # Publication bias
    publication_bias: PublicationBiasInfo

    # Gap analysis
    remaining_gaps: List[GapInfo]
    high_voi_gaps: List[GapInfo]

    # Recommendations
    recommendation: str
    can_stop: bool

    # Timestamp
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            'stability_level': self.stability_level.value,
            'papers_processed': self.papers_processed,
            'stable_for_last_n': self.stable_for_last_n,
            'max_credence_change': self.max_credence_change,
            'coherence_score': self.coherence_score,
            'convergence_achieved': self.convergence_achieved,
            'total_beliefs': self.total_beliefs,
            'stable_beliefs': self.stable_beliefs,
            'unstable_beliefs': self.unstable_beliefs,
            'contested_beliefs': self.contested_beliefs,
            'stable_belief_list': [b.to_dict() for b in self.stable_belief_list],
            'unstable_belief_list': [b.to_dict() for b in self.unstable_belief_list],
            'contested_belief_list': [b.to_dict() for b in self.contested_belief_list],
            'publication_bias': self.publication_bias.to_dict(),
            'remaining_gaps': [g.to_dict() for g in self.remaining_gaps],
            'high_voi_gaps': [g.to_dict() for g in self.high_voi_gaps],
            'recommendation': self.recommendation,
            'can_stop': self.can_stop,
            'timestamp': self.timestamp.isoformat()
        }


# =============================================================================
# Stability Engine
# =============================================================================

class StabilityEngine:
    """
    Engine for tracking and reporting belief stability.

    Per expert panel:
    - Simon: Belief-stability stopping rules, not budget-based
    - Epistemologist: Oscillation detection, contested flag
    - Cartwright: Publication bias warning in stability report
    """

    def __init__(
        self,
        web: WebOfBelief,
        stability_threshold: float = 0.01,
        stability_window: int = 5,
        voi_threshold: float = 0.3
    ):
        """
        Initialize the stability engine.

        Args:
            web: The web of belief to analyze
            stability_threshold: Max delta for stability (default 0.01)
            stability_window: Number of papers to consider (default 5)
            voi_threshold: VOI score threshold for "high" gaps
        """
        self.web = web
        self.stability_threshold = stability_threshold
        self.stability_window = stability_window
        self.voi_threshold = voi_threshold

        # Track papers processed
        self.papers_processed = 0
        self.stable_streak = 0

    def record_paper_processed(self) -> None:
        """Record that a paper was processed."""
        self.papers_processed += 1

    def check_stability(self) -> StabilityLevel:
        """
        Check overall stability of the web.

        Returns:
            StabilityLevel enum value
        """
        beliefs = list(self.web.beliefs.values())
        if not beliefs:
            return StabilityLevel.STABLE

        stable_count = 0
        contested_count = 0

        for belief in beliefs:
            if belief.contested:
                contested_count += 1
            elif belief.is_stable(self.stability_threshold, self.stability_window):
                stable_count += 1

        # Determine overall level
        total = len(beliefs)
        stable_ratio = stable_count / total if total > 0 else 0
        contested_ratio = contested_count / total if total > 0 else 0

        if contested_ratio > 0.2:
            return StabilityLevel.CONTESTED
        elif stable_ratio >= 0.9:
            return StabilityLevel.STABLE
        elif stable_ratio >= 0.7:
            return StabilityLevel.CONVERGING
        else:
            return StabilityLevel.UNSTABLE

    def estimate_publication_bias(self) -> PublicationBiasInfo:
        """
        Estimate publication bias risk.

        Per expert panel (Cartwright): Stability may reflect publication
        bias—we've seen all positive results, null results unpublished.

        Uses null result ratio as primary indicator.
        """
        beliefs = list(self.web.beliefs.values())
        if len(beliefs) < 5:
            return PublicationBiasInfo(
                risk_level=PublicationBiasRisk.UNKNOWN,
                null_result_ratio=0.0,
                total_studies=len(beliefs),
                null_studies=0,
                confidence=0.0,
                warning_message="Insufficient data to assess publication bias"
            )

        # Count null/negative results
        # Look for beliefs with low credence or explicit null indicators
        null_count = 0
        for belief in beliefs:
            content_lower = belief.content.lower()
            # Check for null result indicators
            null_indicators = [
                'no effect', 'no significant', 'null result',
                'no difference', 'no relationship', 'failed to replicate',
                'did not replicate', 'not significant', 'no association'
            ]
            if any(ind in content_lower for ind in null_indicators):
                null_count += 1
            # Also count low-credence beliefs as potential negatives
            elif belief.credence.value < 0.3:
                null_count += 1

        total = len(beliefs)
        null_ratio = null_count / total if total > 0 else 0

        # Assess risk based on null ratio
        # Per Cartwright: If < 10% null results, flag as likely biased
        if null_ratio < 0.05:
            risk = PublicationBiasRisk.HIGH
            warning = ("Stability may reflect publication bias. Only {:.0%} of "
                      "findings report null or negative results. Consider searching "
                      "grey literature, preprint servers, or registered reports.").format(null_ratio)
        elif null_ratio < 0.15:
            risk = PublicationBiasRisk.MODERATE
            warning = ("Some concern about publication bias. {:.0%} of findings "
                      "report null or negative results.").format(null_ratio)
        else:
            risk = PublicationBiasRisk.LOW
            warning = None

        # Confidence based on sample size
        confidence = min(1.0, total / 30)  # Full confidence at 30+ studies

        return PublicationBiasInfo(
            risk_level=risk,
            null_result_ratio=null_ratio,
            total_studies=total,
            null_studies=null_count,
            confidence=confidence,
            warning_message=warning
        )

    def get_belief_stability_info(self, belief: Belief) -> BeliefStabilityInfo:
        """Get stability information for a single belief."""
        max_delta = belief.credence_stability(self.stability_window)
        is_stable = max_delta < self.stability_threshold
        credence_range = belief.credence_range() if belief.contested else None

        return BeliefStabilityInfo(
            belief_id=belief.belief_id,
            content=belief.content[:100],  # Truncate for report
            credence=belief.credence.value,
            max_delta_in_window=max_delta,
            is_stable=is_stable,
            is_contested=belief.contested,
            history_length=len(belief.credence_history),
            credence_range=credence_range
        )

    def identify_gaps(self) -> Tuple[List[GapInfo], List[GapInfo]]:
        """
        Identify epistemic gaps in the web.

        Returns:
            Tuple of (all_gaps, high_voi_gaps)
        """
        gaps = []

        # Identify uncertain beliefs (high variance)
        for belief in self.web.beliefs.values():
            if belief.credence.uncertainty > 0.3:
                gap = GapInfo(
                    gap_id=f"uncertain:{belief.belief_id}",
                    description=f"High uncertainty: {belief.content[:50]}...",
                    gap_type="uncertain",
                    related_beliefs=[belief.belief_id],
                    voi_score=belief.credence.uncertainty
                )
                gaps.append(gap)

        # Identify contested beliefs
        for belief in self.web.beliefs.values():
            if belief.contested:
                gap = GapInfo(
                    gap_id=f"contested:{belief.belief_id}",
                    description=f"Contested finding: {belief.content[:50]}...",
                    gap_type="uncertain",
                    related_beliefs=[belief.belief_id],
                    voi_score=0.8  # High VOI for contested beliefs
                )
                gaps.append(gap)

        # Sort by VOI score
        gaps.sort(key=lambda g: g.voi_score, reverse=True)

        # Filter high-VOI gaps
        high_voi = [g for g in gaps if g.voi_score >= self.voi_threshold]

        return gaps, high_voi

    def generate_report(self) -> StabilityReport:
        """
        Generate a comprehensive stability report.

        Per expert panel (Epistemologist): Frame stability as "given
        current evidence"—not as absolute certainty.
        """
        beliefs = list(self.web.beliefs.values())

        # Categorize beliefs
        stable_list = []
        unstable_list = []
        contested_list = []

        max_change = 0.0

        for belief in beliefs:
            info = self.get_belief_stability_info(belief)
            max_change = max(max_change, info.max_delta_in_window)

            if belief.contested:
                contested_list.append(info)
            elif info.is_stable:
                stable_list.append(info)
            else:
                unstable_list.append(info)

        # Check overall stability
        stability_level = self.check_stability()

        # Track stable streak
        if stability_level == StabilityLevel.STABLE:
            self.stable_streak += 1
        else:
            self.stable_streak = 0

        # Get coherence score
        coherence_score = getattr(self.web, 'coherence_score', 0.0)
        if callable(coherence_score):
            coherence_score = 0.0

        # Get publication bias
        pub_bias = self.estimate_publication_bias()

        # Get gaps
        all_gaps, high_voi_gaps = self.identify_gaps()

        # Determine if we can stop
        convergence = stability_level in (StabilityLevel.STABLE, StabilityLevel.CONVERGING)
        no_critical_gaps = len(high_voi_gaps) == 0
        can_stop = convergence and no_critical_gaps

        # Generate recommendation
        recommendation = self._generate_recommendation(
            stability_level, pub_bias, high_voi_gaps, contested_list
        )

        return StabilityReport(
            stability_level=stability_level,
            papers_processed=self.papers_processed,
            stable_for_last_n=self.stable_streak,
            max_credence_change=max_change,
            coherence_score=coherence_score,
            convergence_achieved=convergence,
            total_beliefs=len(beliefs),
            stable_beliefs=len(stable_list),
            unstable_beliefs=len(unstable_list),
            contested_beliefs=len(contested_list),
            stable_belief_list=stable_list[:10],  # Limit for report size
            unstable_belief_list=unstable_list[:10],
            contested_belief_list=contested_list[:10],
            publication_bias=pub_bias,
            remaining_gaps=all_gaps[:10],
            high_voi_gaps=high_voi_gaps[:5],
            recommendation=recommendation,
            can_stop=can_stop
        )

    def _generate_recommendation(
        self,
        stability: StabilityLevel,
        pub_bias: PublicationBiasInfo,
        high_voi_gaps: List[GapInfo],
        contested: List[BeliefStabilityInfo]
    ) -> str:
        """
        Generate a human-readable recommendation.

        Per expert panel (Epistemologist): Always frame as conditional
        on current evidence, not absolute.
        """
        parts = []

        # Base recommendation based on stability
        if stability == StabilityLevel.STABLE:
            parts.append(
                "The web has reached equilibrium with the evidence currently available. "
                "This does not mean beliefs are certain—only that additional papers from "
                "the same literature are unlikely to change them significantly."
            )
        elif stability == StabilityLevel.CONVERGING:
            parts.append(
                "The web is converging toward stability. Recent papers have caused "
                "smaller changes than earlier ones. A few more papers may be sufficient."
            )
        elif stability == StabilityLevel.CONTESTED:
            parts.append(
                "Several beliefs show genuine disagreement in the literature. "
                "This likely reflects real scientific controversy rather than "
                "insufficient evidence."
            )
        else:
            parts.append(
                "The web is still evolving significantly. Continue adding papers "
                "until changes diminish."
            )

        # Publication bias warning
        if pub_bias.risk_level == PublicationBiasRisk.HIGH:
            parts.append(
                "\n\nWARNING: Publication bias detected. Consider searching "
                "grey literature, preprint servers, or registered reports."
            )
        elif pub_bias.risk_level == PublicationBiasRisk.MODERATE:
            parts.append(
                "\n\nNote: Some concern about publication bias. "
                "Consider diversifying sources."
            )

        # High-VOI gaps
        if high_voi_gaps:
            gap_desc = ", ".join(g.description[:30] for g in high_voi_gaps[:3])
            parts.append(
                f"\n\nRemaining high-value gaps: {gap_desc}"
            )

        # Contested beliefs
        if contested:
            parts.append(
                f"\n\n{len(contested)} beliefs are contested due to conflicting evidence. "
                "These represent genuine uncertainty that additional papers may not resolve."
            )

        # Final note
        parts.append(
            "\n\nGenuinely new evidence (different methods, populations, or paradigms) "
            "could still cause substantial revision."
        )

        return "".join(parts)

    def should_stop_searching(self) -> Tuple[bool, str]:
        """
        Determine if searching should stop.

        Per expert panel (Simon): Stop based on belief stability,
        not arbitrary paper counts.

        Returns:
            Tuple of (should_stop, reason)
        """
        stability = self.check_stability()

        if stability == StabilityLevel.STABLE:
            if self.stable_streak >= self.stability_window:
                return True, "Beliefs have stabilized for sufficient papers"
            else:
                return False, f"Stable but need {self.stability_window - self.stable_streak} more papers to confirm"

        elif stability == StabilityLevel.CONTESTED:
            # Contested means genuine disagreement—more papers won't help
            contested_count = sum(1 for b in self.web.beliefs.values() if b.contested)
            if contested_count > len(self.web.beliefs) * 0.3:
                return True, "Many beliefs contested—genuine disagreement, more papers unlikely to help"
            return False, "Some contested beliefs, continue to see if resolution emerges"

        elif stability == StabilityLevel.CONVERGING:
            return False, "Converging but not yet stable"

        else:
            return False, "Web still evolving, continue searching"
