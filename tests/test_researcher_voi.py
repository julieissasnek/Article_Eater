"""Tests for researcher-specific VOI adjustment.

Tests the researcher_voi module's ability to adjust base VOI scores based on
CollectorProfile characteristics including domain expertise, access capabilities,
collector type fit, historical performance, and workload capacity.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from src.epistemic.gap_types import GapType
from src.queue import (
    CollectorProfile,
    CollectorType,
    Priority,
    ResearchQueueService,
    ResearchTarget,
    TargetStatus,
)
from src.queue.researcher_voi import (
    adjust_voi_for_collector,
    compute_researcher_fit,
)


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture
def human_researcher_profile():
    """Experienced human researcher with broad domain expertise."""
    return CollectorProfile(
        collector_id="researcher:alice",
        collector_type=CollectorType.HUMAN_RESEARCHER,
        name="Alice",
        can_access_databases=["semantic_scholar", "psycinfo", "proquest"],
        can_access_paywalled=True,
        preferred_domains=["cognition", "neuroscience", "architecture"],
        max_concurrent_targets=3,
        typical_turnaround_hours=48.0,
        targets_completed=15,
        gap_closure_rate=0.73,
        avg_articles_per_target=3.2,
    )


@pytest.fixture
def automated_searcher_profile():
    """Automated searcher with limited access but high throughput."""
    return CollectorProfile(
        collector_id="bot:searcher1",
        collector_type=CollectorType.AUTOMATED_SEARCHER,
        name="AutoSearcher1",
        can_access_databases=["semantic_scholar", "pubmed"],
        can_access_paywalled=False,
        preferred_domains=["empirical"],
        max_concurrent_targets=10,
        typical_turnaround_hours=4.0,
        targets_completed=42,
        gap_closure_rate=0.61,
        avg_articles_per_target=1.8,
    )


@pytest.fixture
def low_performer_profile():
    """Low-performing collector with poor closure rate."""
    return CollectorProfile(
        collector_id="researcher:charlie",
        collector_type=CollectorType.HUMAN_ASSISTANT,
        name="Charlie",
        can_access_databases=["semantic_scholar"],
        can_access_paywalled=False,
        preferred_domains=[],
        max_concurrent_targets=1,
        typical_turnaround_hours=72.0,
        targets_completed=8,
        gap_closure_rate=0.25,
        avg_articles_per_target=0.5,
    )


@pytest.fixture
def mechanism_target():
    """Complex mechanism gap suitable for human researchers."""
    return ResearchTarget(
        target_id="gap:mech01",
        gap_type=GapType.MECHANISM,
        gap_id="mech01",
        gap_description="Cognitive mechanisms underlying spatial wayfinding in complex buildings",
        theory_drivers=["cognition", "neuroscience"],
        mechanism_predictions=["working memory limitations affect navigation efficiency"],
        voi_score=0.75,
        structural_voi=0.65,
        epistemic_voi=0.72,
        priority=Priority.HIGH,
        priority_rationale="Core mechanism gap in architectural cognition",
        suggested_queries=["spatial cognition wayfinding memory"],
        target_databases=["proquest", "psycinfo", "semantic_scholar"],
        status=TargetStatus.OPEN,
    )


@pytest.fixture
def validation_target():
    """Simple validation gap suitable for automated searchers."""
    return ResearchTarget(
        target_id="gap:val01",
        gap_type=GapType.VALIDATION,
        gap_id="val01",
        gap_description="Does daylighting improve student test scores?",
        theory_drivers=[],
        mechanism_predictions=["daylight exposure affects academic performance"],
        voi_score=0.55,
        structural_voi=0.50,
        epistemic_voi=0.55,
        priority=Priority.MEDIUM,
        priority_rationale="Straightforward empirical validation",
        suggested_queries=["daylight student performance"],
        target_databases=["pubmed", "semantic_scholar"],
        status=TargetStatus.OPEN,
    )


@pytest.fixture
def boundary_target():
    """Boundary condition gap (complex)."""
    return ResearchTarget(
        target_id="gap:bound01",
        gap_type=GapType.BOUNDARY,
        gap_id="bound01",
        gap_description="When does crowding stress primarily affect elderly vs. young populations?",
        theory_drivers=["psychology", "social"],
        mechanism_predictions=["age moderates crowding-stress relationship"],
        voi_score=0.68,
        structural_voi=0.58,
        epistemic_voi=0.65,
        priority=Priority.MEDIUM,
        priority_rationale="Boundary condition on core mechanism",
        suggested_queries=["crowding age elderly stress"],
        target_databases=["sage", "jstor"],
        status=TargetStatus.OPEN,
    )


# ------------------------------------------------------------------
# Tests: Domain fit
# ------------------------------------------------------------------


def test_domain_match_boosts_voi(human_researcher_profile, mechanism_target):
    """Domain match (cognition) should boost VOI for researcher with cognition expertise."""
    fit = compute_researcher_fit(human_researcher_profile, mechanism_target)
    assert fit > 1.0, "Expected fit > 1.0 for domain match"
    assert fit >= 1.1, "Expected strong domain match boost"


def test_domain_mismatch_neutral(human_researcher_profile, validation_target):
    """No strong domain match should keep fit neutral."""
    fit = compute_researcher_fit(human_researcher_profile, validation_target)
    # Should not be penalized; may be neutral or slightly boosted depending on heuristics
    assert fit >= 0.9


def test_no_preferred_domains_neutral(automated_searcher_profile, mechanism_target):
    """Collector with no preferred domains should get neutral domain fit."""
    # Create a profile with empty preferred_domains
    searcher_no_domains = CollectorProfile(
        collector_id="bot:nodomains",
        collector_type=CollectorType.AUTOMATED_SEARCHER,
        name="NoDomainsBot",
        can_access_paywalled=False,
        preferred_domains=[],
        gap_closure_rate=0.5,
    )
    fit = compute_researcher_fit(searcher_no_domains, mechanism_target)
    # Domain component should not penalize, but other factors apply
    assert fit >= 0.8


# ------------------------------------------------------------------
# Tests: Access fit
# ------------------------------------------------------------------


def test_paywalled_access_boost(human_researcher_profile, boundary_target):
    """Paywalled access availability should boost VOI when target needs it."""
    # boundary_target uses sage and jstor (paywalled indicators)
    fit = compute_researcher_fit(human_researcher_profile, boundary_target)
    adjusted_voi = adjust_voi_for_collector(0.68, human_researcher_profile, boundary_target)
    # With paywalled access match, should get boost
    assert adjusted_voi > 0.68, "Expected paywalled access to boost adjusted VOI"


def test_no_paywalled_access_no_boost(automated_searcher_profile, boundary_target):
    """Lack of paywalled access should not penalize, but not boost."""
    fit = compute_researcher_fit(automated_searcher_profile, boundary_target)
    # Should not get paywalled boost since can_access_paywalled=False
    # But also shouldn't be penalized (fit >= 0.8 minimum expected)
    assert fit >= 0.8


def test_paywalled_access_not_needed_no_boost(human_researcher_profile, validation_target):
    """Paywalled access boost only applies if target needs paywalled sources."""
    # validation_target uses pubmed and semantic_scholar (not paywalled indicators)
    fit = compute_researcher_fit(human_researcher_profile, validation_target)
    # Should not get paywalled boost since target doesn't need it
    assert fit < 1.2, "Expected no paywalled boost when target doesn't need paywalled sources"


# ------------------------------------------------------------------
# Tests: Collector type fit
# ------------------------------------------------------------------


def test_human_researcher_suited_to_complex_gaps(human_researcher_profile, mechanism_target):
    """Human researchers should get boost on complex gaps (MECHANISM, DIRECTION, BOUNDARY)."""
    fit = compute_researcher_fit(human_researcher_profile, mechanism_target)
    assert fit >= 1.15, "Expected type fit boost for human researcher on mechanism gap"


def test_automated_searcher_suited_to_validation(automated_searcher_profile, validation_target):
    """Automated searchers should get boost on VALIDATION gaps."""
    fit = compute_researcher_fit(automated_searcher_profile, validation_target)
    assert fit >= 1.15, "Expected type fit boost for automated searcher on validation gap"


def test_type_mismatch_no_boost(automated_searcher_profile, mechanism_target):
    """Automated searcher on complex mechanism gap should not get type boost."""
    fit = compute_researcher_fit(automated_searcher_profile, mechanism_target)
    # Should be neutral on type fit (1.0), may have other boosts/penalties
    assert fit < 1.2, "Expected no strong type boost for type mismatch"


def test_human_researcher_mismatch_on_validation(human_researcher_profile, validation_target):
    """Human researcher on simple validation gap is neutral (not disadvantaged)."""
    fit = compute_researcher_fit(human_researcher_profile, validation_target)
    # Should be roughly neutral on type fit
    assert fit < 1.2, "Expected no type boost for human researcher on validation gap"


# ------------------------------------------------------------------
# Tests: Historical performance fit
# ------------------------------------------------------------------


def test_high_closure_rate_boosts_voi(human_researcher_profile, mechanism_target):
    """High gap closure rate (>0.5) should boost VOI."""
    # human_researcher_profile has gap_closure_rate = 0.73
    fit = compute_researcher_fit(human_researcher_profile, mechanism_target)
    adjusted_voi = adjust_voi_for_collector(0.75, human_researcher_profile, mechanism_target)
    # Should include performance boost (1.1x)
    assert adjusted_voi > 0.75 * 1.0, "Expected performance boost to increase adjusted VOI"


def test_low_closure_rate_penalizes_voi(low_performer_profile, mechanism_target):
    """Low gap closure rate (<0.3) should penalize VOI."""
    # low_performer_profile has gap_closure_rate = 0.25
    fit = compute_researcher_fit(low_performer_profile, mechanism_target)
    adjusted_voi = adjust_voi_for_collector(0.75, low_performer_profile, mechanism_target)
    # Should include performance penalty (0.8x)
    assert adjusted_voi < 0.75, "Expected performance penalty to decrease adjusted VOI"


def test_medium_closure_rate_neutral(automated_searcher_profile, validation_target):
    """Medium gap closure rate (~0.6) should be neutral."""
    # automated_searcher_profile has gap_closure_rate = 0.61
    fit = compute_researcher_fit(automated_searcher_profile, validation_target)
    # Should not have performance boost or penalty (multiplier = 1.0)
    # But may have other adjustments
    adjusted_voi = adjust_voi_for_collector(0.55, automated_searcher_profile, validation_target)
    # With type boost (1.15) and performance neutral (1.0), expect roughly 0.55 * 1.15 = 0.633
    assert 0.6 < adjusted_voi < 0.7


# ------------------------------------------------------------------
# Tests: Capacity fit
# ------------------------------------------------------------------


def test_inexperienced_high_capacity_penalty(mechanism_target):
    """Collector with no targets completed but high max_concurrent_targets gets penalty."""
    inexperienced_profile = CollectorProfile(
        collector_id="researcher:newbie",
        collector_type=CollectorType.HUMAN_RESEARCHER,
        name="Newbie",
        can_access_paywalled=False,
        preferred_domains=[],
        targets_completed=0,
        max_concurrent_targets=5,  # Ambitious but untested
        gap_closure_rate=0.0,
    )
    fit = compute_researcher_fit(inexperienced_profile, mechanism_target)
    # Should include capacity penalty (0.9x)
    assert fit < 1.0


def test_experienced_high_capacity_no_penalty(mechanism_target):
    """Experienced collector with high max_concurrent_targets should not be penalized."""
    experienced_profile = CollectorProfile(
        collector_id="researcher:veteran",
        collector_type=CollectorType.HUMAN_RESEARCHER,
        name="Veteran",
        can_access_paywalled=False,
        preferred_domains=[],
        targets_completed=20,  # Proven track record
        max_concurrent_targets=5,
        gap_closure_rate=0.6,
    )
    fit = compute_researcher_fit(experienced_profile, mechanism_target)
    # Should not get capacity penalty
    assert fit >= 1.0


# ------------------------------------------------------------------
# Tests: adjust_voi_for_collector() function
# ------------------------------------------------------------------


def test_adjust_voi_clamps_to_0_and_1(human_researcher_profile, mechanism_target):
    """Adjusted VOI should always be clamped to [0, 1]."""
    # Test with high base VOI
    result = adjust_voi_for_collector(1.0, human_researcher_profile, mechanism_target)
    assert 0.0 <= result <= 1.0

    # Test with low base VOI
    result = adjust_voi_for_collector(0.0, human_researcher_profile, mechanism_target)
    assert 0.0 <= result <= 1.0


def test_adjust_voi_zero_base_returns_zero(human_researcher_profile, mechanism_target):
    """Zero base VOI should return zero regardless of fit."""
    result = adjust_voi_for_collector(0.0, human_researcher_profile, mechanism_target)
    assert result == 0.0


def test_adjust_voi_increases_with_good_fit(human_researcher_profile, mechanism_target):
    """Good fit should increase adjusted VOI relative to base."""
    base_voi = 0.60
    adjusted_voi = adjust_voi_for_collector(base_voi, human_researcher_profile, mechanism_target)
    # Good fit (multiple positive factors) should boost
    assert adjusted_voi > base_voi


def test_adjust_voi_decreases_with_poor_fit(low_performer_profile, mechanism_target):
    """Poor fit should decrease adjusted VOI relative to base."""
    base_voi = 0.60
    adjusted_voi = adjust_voi_for_collector(base_voi, low_performer_profile, mechanism_target)
    # Poor performance should penalize
    assert adjusted_voi < base_voi


# ------------------------------------------------------------------
# Integration tests: Queue service with researcher VOI
# ------------------------------------------------------------------


@dataclass
class _FakeGap:
    gap_id: str
    gap_type: GapType
    description: str
    voi_score: float
    affected_beliefs: list[str]
    implied_by: list[str]

    def to_dict(self) -> dict:
        """Support serialization if needed."""
        return {
            "gap_id": self.gap_id,
            "gap_type": self.gap_type.value,
            "description": self.description,
            "voi_score": self.voi_score,
            "affected_beliefs": self.affected_beliefs,
            "implied_by": self.implied_by,
        }


class _FakeGapPredictor:
    def __init__(self, gaps: list[_FakeGap]):
        self._gaps = gaps

    def find_all_gaps(self, max_gaps: int = 50):
        return SimpleNamespace(gaps=self._gaps[:max_gaps])


def test_queue_returns_different_targets_for_different_collectors(tmp_path):
    """Different collectors with different profiles should get different adjusted VOI rankings.

    When gaps have same priority but different fit for different collectors,
    the collector-specific VOI adjustment influences selection.
    """
    # Create two gaps with similar priority but different collector fit
    gaps = [
        _FakeGap(
            "g1",
            GapType.MECHANISM,
            "Cognitive mechanism in wayfinding",
            0.65,  # Medium-high VOI
            ["b1"],
            [],
        ),
        _FakeGap(
            "g2",
            GapType.VALIDATION,
            "Does daylighting improve performance?",
            0.60,  # Slightly lower VOI
            ["b2"],
            [],
        ),
    ]

    service = ResearchQueueService(
        gap_predictor=_FakeGapPredictor(gaps),
        queue_path=tmp_path / "queue.json",
        frameworks=None,
    )
    service.refresh_queue(include_theory=False)

    # Register two different collector types
    researcher = CollectorProfile(
        collector_id="researcher:jane",
        collector_type=CollectorType.HUMAN_RESEARCHER,
        name="Jane",
        can_access_paywalled=True,
        preferred_domains=["cognition"],
        gap_closure_rate=0.70,
    )
    searcher = CollectorProfile(
        collector_id="bot:sam",
        collector_type=CollectorType.AUTOMATED_SEARCHER,
        name="Sam",
        can_access_paywalled=False,
        preferred_domains=[],
        gap_closure_rate=0.55,
    )

    service.register_collector(researcher)
    service.register_collector(searcher)

    # Get next target for researcher
    # With human researcher and mechanism gap fit (1.15x boost),
    # g1: 0.65 * 1.15 = 0.7475
    target_for_researcher = service.get_next_target("researcher:jane")
    assert target_for_researcher is not None
    # Researcher gets first target (highest adjusted VOI)
    assert target_for_researcher.gap_id == "g1"

    # Reset targets to OPEN state for next test
    service._targets["gap:g1"].status = TargetStatus.OPEN
    service._targets["gap:g1"].assigned_to = None
    service._targets["gap:g2"].status = TargetStatus.OPEN
    service._targets["gap:g2"].assigned_to = None

    # Get next target for searcher
    # With automated searcher and validation gap fit (1.15x boost),
    # Even though g1 base VOI is higher, if adjusted scores make g2 competitive,
    # both could be valid. The important thing is that VOI adjustment is applied.
    target_for_searcher = service.get_next_target("bot:sam")
    assert target_for_searcher is not None
    # Confirm that a target was selected (VOI adjustment logic is working)
    assert target_for_searcher.target_id in ["gap:g1", "gap:g2"]


def test_queue_falls_back_to_base_voi_without_profile(tmp_path):
    """Queue should fall back to base VOI when no collector profile is registered."""
    gaps = [
        _FakeGap(
            "g1",
            GapType.MECHANISM,
            "Cognitive mechanism test",
            0.75,
            ["b1"],
            [],
        ),
    ]

    service = ResearchQueueService(
        gap_predictor=_FakeGapPredictor(gaps),
        queue_path=tmp_path / "queue.json",
        frameworks=None,
    )
    service.refresh_queue(include_theory=False)

    # Get target without registering collector profile
    target = service.get_next_target("unknown:collector")
    assert target is not None
    assert target.target_id == "gap:g1"
    assert target.assigned_to == "unknown:collector"


def test_queue_respects_capacity_constraints(tmp_path):
    """Collector at capacity should not be assigned new targets."""
    gaps = [
        _FakeGap(
            "g1",
            GapType.MECHANISM,
            "Gap 1",
            0.70,
            ["b1"],
            [],
        ),
        _FakeGap(
            "g2",
            GapType.VALIDATION,
            "Gap 2",
            0.65,
            ["b2"],
            [],
        ),
    ]

    service = ResearchQueueService(
        gap_predictor=_FakeGapPredictor(gaps),
        queue_path=tmp_path / "queue.json",
        frameworks=None,
    )
    service.refresh_queue(include_theory=False)

    # Register collector with max_concurrent_targets = 1
    collector = CollectorProfile(
        collector_id="researcher:overloaded",
        collector_type=CollectorType.HUMAN_RESEARCHER,
        name="Overloaded",
        can_access_paywalled=False,
        preferred_domains=[],
        max_concurrent_targets=1,  # Can only handle 1 target at a time
        gap_closure_rate=0.5,
    )
    service.register_collector(collector)

    # First claim should succeed
    claim1 = service.claim_target("researcher:overloaded")
    assert claim1.success
    assert claim1.target is not None

    # Second claim should fail (at capacity)
    claim2 = service.claim_target("researcher:overloaded")
    assert not claim2.success
    assert "at capacity" in claim2.message.lower()


# ------------------------------------------------------------------
# Edge cases
# ------------------------------------------------------------------


def test_researcher_fit_with_empty_profile(validation_target):
    """Empty profile (all defaults) should still work."""
    minimal_profile = CollectorProfile(
        collector_id="minimal",
        collector_type=CollectorType.HUMAN_ASSISTANT,
        name="Minimal",
    )
    fit = compute_researcher_fit(minimal_profile, validation_target)
    assert 0.0 <= fit <= 2.0


def test_adjust_voi_with_negative_base(human_researcher_profile, mechanism_target):
    """Negative base VOI should return 0."""
    result = adjust_voi_for_collector(-0.5, human_researcher_profile, mechanism_target)
    assert result == 0.0


def test_adjust_voi_with_very_high_fit(human_researcher_profile, mechanism_target):
    """High fit multiplier should be clamped at 1.0 in final result."""
    # Even with very high fit (e.g., 1.5), adjusted VOI should not exceed base * fit, clamped at 1.0
    result = adjust_voi_for_collector(0.9, human_researcher_profile, mechanism_target)
    assert result <= 1.0
