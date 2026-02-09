"""
Tests for Evidence Summarizer — Sprint 3.0.4-A
2026-02-09
"""

import pytest
import json
from dataclasses import dataclass
from typing import List, Optional

from src.services.evidence_summarizer import (
    EvidenceSummarizer,
    EvidenceSummary,
    EvidenceSynthesis,
    SourceEvidence,
    ScopeMetadata,
    EvidenceCaveat,
    EvidenceStrength,
    TransferabilityLevel,
    CaveatType,
    create_evidence_summary,
    create_topic_summary,
    format_evidence_markdown,
    format_evidence_json,
)


# =============================================================================
# Mock Objects
# =============================================================================

@dataclass
class MockCredence:
    value: float
    uncertainty: float = 0.1


@dataclass
class MockScopeConditions:
    population: Optional[str] = None
    setting: Optional[str] = None
    duration: Optional[str] = None
    enabling_conditions: List[str] = None
    boundary_conditions: List[str] = None
    moderators: List[str] = None

    def __post_init__(self):
        self.enabling_conditions = self.enabling_conditions or []
        self.boundary_conditions = self.boundary_conditions or []
        self.moderators = self.moderators or []


@dataclass
class MockBelief:
    belief_id: str
    content: str
    credence: MockCredence
    paper_ids: List[str] = None
    scope_conditions: Optional[MockScopeConditions] = None

    def __post_init__(self):
        self.paper_ids = self.paper_ids or []


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def summarizer():
    return EvidenceSummarizer()


@pytest.fixture
def strong_belief():
    return MockBelief(
        belief_id="belief:001",
        content="Natural light reduces stress in office workers",
        credence=MockCredence(0.85, 0.08),
        paper_ids=["paper:ulrich:1984", "paper:kaplan:1989", "paper:kellert:2005"],
        scope_conditions=MockScopeConditions(
            population="Adults in office settings",
            setting="Indoor office environments",
            duration="8-hour workday"
        )
    )


@pytest.fixture
def weak_belief():
    return MockBelief(
        belief_id="belief:002",
        content="Plants improve productivity",
        credence=MockCredence(0.35, 0.25),
        paper_ids=["paper:single:2020"]
    )


@pytest.fixture
def scoped_belief():
    return MockBelief(
        belief_id="belief:003",
        content="Green views accelerate hospital recovery",
        credence=MockCredence(0.75, 0.12),
        paper_ids=["paper:ulrich:1984", "paper:diette:2003"],
        scope_conditions=MockScopeConditions(
            population="Post-surgical patients",
            setting="Hospital rooms with window views",
            duration="5-10 day recovery period",
            enabling_conditions=["Window present", "View of vegetation"],
            boundary_conditions=["Does not apply to ICU patients"],
            moderators=["View quality", "Patient mobility"]
        )
    )


# =============================================================================
# Basic Summarizer Tests
# =============================================================================

class TestEvidenceSummarizer:
    """Test the EvidenceSummarizer class."""

    def test_create_summarizer(self, summarizer):
        """Test summarizer can be created."""
        assert summarizer.min_sources_for_synthesis == 2
        assert summarizer.high_credence_threshold == 0.7

    def test_summarize_strong_belief(self, summarizer, strong_belief):
        """Test summarizing a strong belief."""
        summary = summarizer.summarize_belief(strong_belief)

        assert summary.claim_id == "belief:001"
        assert summary.claim_content == "Natural light reduces stress in office workers"
        assert summary.strength == EvidenceStrength.STRONG
        assert summary.synthesis is not None
        assert summary.synthesis.pooled_credence == 0.85
        assert len(summary.sources) == 3

    def test_summarize_weak_belief(self, summarizer, weak_belief):
        """Test summarizing a weak belief."""
        summary = summarizer.summarize_belief(weak_belief)

        assert summary.strength == EvidenceStrength.WEAK
        assert len(summary.sources) == 1

    def test_summarize_scoped_belief(self, summarizer, scoped_belief):
        """Test summarizing a belief with scope conditions."""
        summary = summarizer.summarize_belief(scoped_belief)

        assert summary.combined_scope is not None
        assert summary.combined_scope.population == "Post-surgical patients"
        assert "Window present" in summary.combined_scope.enabling_conditions
        assert summary.transferability == TransferabilityLevel.LOW

    def test_summarize_without_sources(self, summarizer, strong_belief):
        """Test summarizing without including source details."""
        summary = summarizer.summarize_belief(strong_belief, include_sources=False)

        assert len(summary.sources) == 0


class TestMultiBeliefSummary:
    """Test summarizing multiple beliefs."""

    def test_summarize_multiple_beliefs(self, summarizer, strong_belief, scoped_belief):
        """Test synthesizing multiple beliefs."""
        summary = summarizer.summarize_beliefs(
            [strong_belief, scoped_belief],
            topic="Nature and health"
        )

        assert summary.topic == "Nature and health"
        assert summary.synthesis is not None
        assert summary.synthesis.n_sources > 0

    def test_empty_beliefs_list(self, summarizer):
        """Test with empty beliefs list."""
        summary = summarizer.summarize_beliefs([], topic="Empty")

        assert summary.strength == EvidenceStrength.INSUFFICIENT

    def test_consistency_assessment(self, summarizer):
        """Test consistency assessment across beliefs."""
        beliefs = [
            MockBelief("b1", "Claim 1", MockCredence(0.8, 0.1), ["p1"]),
            MockBelief("b2", "Claim 2", MockCredence(0.82, 0.1), ["p2"]),
            MockBelief("b3", "Claim 3", MockCredence(0.78, 0.1), ["p3"]),
        ]

        summary = summarizer.summarize_beliefs(beliefs, topic="Consistent")

        assert summary.synthesis.consistency == "consistent"

    def test_heterogeneity_detection(self, summarizer):
        """Test detection of heterogeneous findings."""
        beliefs = [
            MockBelief("b1", "Claim 1", MockCredence(0.9, 0.1), ["p1"]),
            MockBelief("b2", "Claim 2", MockCredence(0.3, 0.1), ["p2"]),
            MockBelief("b3", "Claim 3", MockCredence(0.5, 0.1), ["p3"]),
        ]

        summary = summarizer.summarize_beliefs(beliefs, topic="Mixed")

        # Should detect inconsistency
        assert summary.synthesis.consistency in ["mixed", "conflicting"]


class TestScopeAnalysis:
    """Test scope-related functionality."""

    def test_combine_scopes(self, summarizer):
        """Test combining scope conditions."""
        belief1 = MockBelief(
            "b1", "C1", MockCredence(0.7),
            scope_conditions=MockScopeConditions(
                population="Adults",
                enabling_conditions=["Condition A"]
            )
        )
        belief2 = MockBelief(
            "b2", "C2", MockCredence(0.7),
            scope_conditions=MockScopeConditions(
                population="Elderly",
                enabling_conditions=["Condition B"]
            )
        )

        summary = summarizer.summarize_beliefs([belief1, belief2])

        assert summary.combined_scope is not None
        assert "Adults" in summary.combined_scope.population
        assert "Elderly" in summary.combined_scope.population
        assert len(summary.combined_scope.enabling_conditions) == 2

    def test_scope_gaps_identified(self, summarizer):
        """Test identification of scope gaps."""
        belief = MockBelief(
            "b1", "Content", MockCredence(0.7),
            scope_conditions=MockScopeConditions(population="Adults")
        )

        summary = summarizer.summarize_beliefs([belief])

        assert len(summary.scope_gaps) > 0
        assert any("Setting" in gap for gap in summary.scope_gaps)

    def test_transferability_high(self, summarizer):
        """Test high transferability assessment."""
        belief = MockBelief(
            "b1", "Universal claim", MockCredence(0.7),
            scope_conditions=MockScopeConditions(
                population="General population",
                setting="Various settings"
            )
        )

        summary = summarizer.summarize_belief(belief)

        assert summary.transferability in [TransferabilityLevel.HIGH, TransferabilityLevel.MODERATE]

    def test_transferability_low(self, summarizer, scoped_belief):
        """Test low transferability with many conditions."""
        summary = summarizer.summarize_belief(scoped_belief)

        assert summary.transferability == TransferabilityLevel.LOW


class TestCaveats:
    """Test caveat generation."""

    def test_replication_caveat(self, summarizer, weak_belief):
        """Test caveat for limited sources."""
        summary = summarizer.summarize_belief(weak_belief)

        caveat_types = [c.caveat_type for c in summary.caveats]
        assert CaveatType.REPLICATION in caveat_types

    def test_scope_caveat(self, summarizer, scoped_belief):
        """Test caveat for narrow scope."""
        summary = summarizer.summarize_belief(scoped_belief)

        caveat_types = [c.caveat_type for c in summary.caveats]
        assert CaveatType.SCOPE_LIMITATION in caveat_types

    def test_heterogeneity_caveat(self, summarizer):
        """Test caveat for heterogeneous results."""
        beliefs = [
            MockBelief("b1", "C1", MockCredence(0.9, 0.1), ["p1"]),
            MockBelief("b2", "C2", MockCredence(0.2, 0.1), ["p2"]),
        ]

        summary = summarizer.summarize_beliefs(beliefs)

        caveat_types = [c.caveat_type for c in summary.caveats]
        assert CaveatType.CONFLICTING_EVIDENCE in caveat_types


class TestOutputFormats:
    """Test output format generation."""

    def test_to_dict(self, summarizer, strong_belief):
        """Test dictionary conversion."""
        summary = summarizer.summarize_belief(strong_belief)
        d = summary.to_dict()

        assert d["claim_id"] == "belief:001"
        assert d["strength"] == "strong"
        assert "synthesis" in d
        assert "sources" in d

    def test_to_json(self, summarizer, strong_belief):
        """Test JSON serialization."""
        summary = summarizer.summarize_belief(strong_belief)
        json_str = summary.to_json()

        parsed = json.loads(json_str)
        assert parsed["claim_id"] == "belief:001"

    def test_to_markdown(self, summarizer, strong_belief):
        """Test markdown generation."""
        summary = summarizer.summarize_belief(strong_belief)
        md = summary.to_markdown()

        assert "# Evidence Summary" in md
        assert "Natural light" in md
        assert "Strength" in md
        assert "Sources" in md

    def test_markdown_with_caveats(self, summarizer, scoped_belief):
        """Test markdown includes caveats."""
        summary = summarizer.summarize_belief(scoped_belief)
        md = summary.to_markdown()

        assert "Caveats" in md

    def test_markdown_with_scope(self, summarizer, scoped_belief):
        """Test markdown includes scope conditions."""
        summary = summarizer.summarize_belief(scoped_belief)
        md = summary.to_markdown()

        assert "Scope Conditions" in md
        assert "Population" in md


class TestQueryResultsSummary:
    """Test summarizing query results."""

    def test_summarize_query_results(self, summarizer):
        """Test summarizing query result dicts."""
        results = [
            {"belief_id": "b1", "content": "Finding 1", "credence": {"value": 0.8}},
            {"belief_id": "b2", "content": "Finding 2", "credence": {"value": 0.7}},
            {"belief_id": "b3", "content": "Finding 3", "credence": 0.75},
        ]

        summary = summarizer.summarize_query_results(results, "Test query")

        assert summary.topic == "Test query"
        assert summary.synthesis.n_sources == 3
        assert len(summary.sources) == 3

    def test_empty_query_results(self, summarizer):
        """Test with empty query results."""
        summary = summarizer.summarize_query_results([], "Empty query")

        assert summary.topic == "Empty query"
        assert len(summary.sources) == 0


class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_create_evidence_summary(self, strong_belief):
        """Test create_evidence_summary function."""
        summary = create_evidence_summary(strong_belief)

        assert summary.claim_id == "belief:001"
        assert summary.strength == EvidenceStrength.STRONG

    def test_create_topic_summary(self, strong_belief, weak_belief):
        """Test create_topic_summary function."""
        summary = create_topic_summary(
            [strong_belief, weak_belief],
            "Nature benefits"
        )

        assert summary.topic == "Nature benefits"
        assert summary.synthesis is not None

    def test_format_markdown(self, strong_belief):
        """Test format_evidence_markdown function."""
        summary = create_evidence_summary(strong_belief)
        md = format_evidence_markdown(summary)

        assert isinstance(md, str)
        assert "Evidence Summary" in md

    def test_format_json(self, strong_belief):
        """Test format_evidence_json function."""
        summary = create_evidence_summary(strong_belief)
        json_str = format_evidence_json(summary)

        parsed = json.loads(json_str)
        assert "claim_id" in parsed


class TestDataClasses:
    """Test data class functionality."""

    def test_scope_metadata_to_dict(self):
        """Test ScopeMetadata serialization."""
        scope = ScopeMetadata(
            population="Adults",
            setting="Office",
            enabling_conditions=["Condition A"]
        )

        d = scope.to_dict()

        assert d["population"] == "Adults"
        assert d["setting"] == "Office"
        assert "duration" not in d  # None values excluded

    def test_source_evidence_to_dict(self):
        """Test SourceEvidence serialization."""
        source = SourceEvidence(
            paper_id="paper:001",
            paper_title="Test Paper",
            year=2024,
            credence=0.75,
            confidence_interval=(0.65, 0.85)
        )

        d = source.to_dict()

        assert d["paper_id"] == "paper:001"
        assert d["confidence_interval"] == [0.65, 0.85]

    def test_caveat_to_dict(self):
        """Test EvidenceCaveat serialization."""
        caveat = EvidenceCaveat(
            caveat_type=CaveatType.REPLICATION,
            description="Limited sources",
            severity="high",
            recommendation="Seek more studies"
        )

        d = caveat.to_dict()

        assert d["type"] == "replication"
        assert d["severity"] == "high"

    def test_synthesis_to_dict(self):
        """Test EvidenceSynthesis serialization."""
        synth = EvidenceSynthesis(
            pooled_credence=0.75,
            pooled_uncertainty=0.1,
            n_sources=5,
            heterogeneity=0.2,
            consistency="consistent",
            pooled_ci=(0.65, 0.85)
        )

        d = synth.to_dict()

        assert d["pooled_credence"] == 0.75
        assert d["pooled_confidence_interval"] == [0.65, 0.85]


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_belief_without_credence(self, summarizer):
        """Test belief with missing credence."""
        belief = MockBelief("b1", "Content", None)

        summary = summarizer.summarize_belief(belief)

        assert summary.synthesis is None
        assert summary.strength == EvidenceStrength.INSUFFICIENT

    def test_belief_without_scope(self, summarizer):
        """Test belief with no scope conditions."""
        belief = MockBelief("b1", "Content", MockCredence(0.7))

        summary = summarizer.summarize_belief(belief)

        assert summary.combined_scope is None
        assert summary.transferability == TransferabilityLevel.UNKNOWN

    def test_very_high_uncertainty(self, summarizer):
        """Test belief with very high uncertainty."""
        belief = MockBelief("b1", "Content", MockCredence(0.5, 0.5), ["p1"])

        summary = summarizer.summarize_belief(belief)

        assert summary.synthesis.pooled_uncertainty == 0.5

    def test_custom_thresholds(self):
        """Test summarizer with custom thresholds."""
        summarizer = EvidenceSummarizer(
            min_sources_for_synthesis=5,
            high_credence_threshold=0.9
        )

        belief = MockBelief("b1", "Content", MockCredence(0.85), ["p1", "p2", "p3"])
        summary = summarizer.summarize_belief(belief)

        # With threshold at 0.9, 0.85 is not "strong"
        assert summary.strength != EvidenceStrength.STRONG
