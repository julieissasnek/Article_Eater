"""
Tests for AI Panel Resolution Framework
========================================

Tests cover:
- PanelConfig instantiation and validation
- PanelistVote creation and serialization
- Consensus computation with various vote distributions
- Panelist prompt generation for different panel types
- Batch resolution in dry_run mode
- Panel report generation and statistics
"""

import pytest
from src.services.ai_panel_resolver import (
    PanelResolver,
    PanelConfig,
    PanelistVote,
    PanelistRole,
    ResolutionResult,
)


class TestPanelConfig:
    """Test PanelConfig instantiation and validation."""

    def test_valid_config(self):
        """Test creating a valid config."""
        config = PanelConfig(
            panel_type="outcome_vocab",
            n_panelists=5,
            consensus_threshold=0.6,
            confidence_floor=0.3,
        )
        assert config.panel_type == "outcome_vocab"
        assert config.n_panelists == 5
        assert config.consensus_threshold == 0.6
        assert config.confidence_floor == 0.3

    def test_config_odd_panelists_required(self):
        """Test that n_panelists must be odd."""
        with pytest.raises(ValueError, match="n_panelists must be odd"):
            PanelConfig(panel_type="outcome_vocab", n_panelists=4)

    def test_config_consensus_threshold_bounds(self):
        """Test that consensus_threshold is in (0, 1]."""
        with pytest.raises(ValueError, match="consensus_threshold must be in"):
            PanelConfig(panel_type="outcome_vocab", consensus_threshold=0.0)

        with pytest.raises(ValueError, match="consensus_threshold must be in"):
            PanelConfig(panel_type="outcome_vocab", consensus_threshold=1.5)

    def test_config_confidence_floor_bounds(self):
        """Test that confidence_floor is in [0, 1)."""
        with pytest.raises(ValueError, match="confidence_floor must be in"):
            PanelConfig(panel_type="outcome_vocab", confidence_floor=1.0)

    def test_config_dry_run_default_false(self):
        """Test that dry_run defaults to False."""
        config = PanelConfig(panel_type="outcome_vocab")
        assert config.dry_run is False

    def test_config_all_panel_types(self):
        """Test all supported panel types."""
        panel_types = ["outcome_vocab", "image_classification", "taxonomy_reconciliation", "annotation_qa"]
        for ptype in panel_types:
            config = PanelConfig(panel_type=ptype)
            assert config.panel_type == ptype


class TestPanelistVote:
    """Test PanelistVote creation and serialization."""

    def test_panelist_vote_creation(self):
        """Test creating a panelist vote."""
        vote = PanelistVote(
            panelist_id="p1",
            role=PanelistRole.DOMAIN_EXPERT,
            decision="outcome_a",
            confidence=0.85,
            reasoning="This matches domain conventions.",
        )
        assert vote.panelist_id == "p1"
        assert vote.role == PanelistRole.DOMAIN_EXPERT
        assert vote.decision == "outcome_a"
        assert vote.confidence == 0.85

    def test_panelist_vote_to_dict(self):
        """Test serializing vote to dict."""
        vote = PanelistVote(
            panelist_id="p1",
            role=PanelistRole.SKEPTIC,
            decision="outcome_b",
            confidence=0.65,
            reasoning="Requires more evidence.",
            dissent_note="This is too assumptive.",
        )
        d = vote.to_dict()
        assert d["panelist_id"] == "p1"
        assert d["role"] == "skeptic"
        assert d["decision"] == "outcome_b"
        assert d["confidence"] == 0.65
        assert d["dissent_note"] == "This is too assumptive."

    def test_panelist_vote_dissent_optional(self):
        """Test that dissent_note is optional."""
        vote = PanelistVote(
            panelist_id="p1",
            role=PanelistRole.DOMAIN_EXPERT,
            decision="outcome_a",
            confidence=0.9,
            reasoning="Clear match.",
        )
        assert vote.dissent_note is None
        d = vote.to_dict()
        assert d["dissent_note"] is None


class TestComputeConsensus:
    """Test consensus computation with various vote distributions."""

    def test_unanimous_consensus(self):
        """Test unanimous agreement."""
        resolver = PanelResolver(PanelConfig(panel_type="outcome_vocab", n_panelists=5))
        votes = [
            PanelistVote("p1", PanelistRole.DOMAIN_EXPERT, "option_a", 0.9, "Clear choice"),
            PanelistVote("p2", PanelistRole.METHODOLOGIST, "option_a", 0.85, "Valid method"),
            PanelistVote("p3", PanelistRole.SKEPTIC, "option_a", 0.8, "Justified"),
            PanelistVote("p4", PanelistRole.INTEGRATOR, "option_a", 0.88, "Coherent"),
            PanelistVote("p5", PanelistRole.CALIBRATOR, "option_a", 0.92, "Precise"),
        ]
        has_consensus, decision, confidence = resolver._compute_consensus(votes)
        assert has_consensus is True
        assert decision == "option_a"
        assert confidence > 0.85

    def test_supermajority_consensus(self):
        """Test supermajority (≥80%) agreement."""
        resolver = PanelResolver(PanelConfig(panel_type="outcome_vocab", n_panelists=5))
        votes = [
            PanelistVote("p1", PanelistRole.DOMAIN_EXPERT, "option_a", 0.9, "Best fit"),
            PanelistVote("p2", PanelistRole.METHODOLOGIST, "option_a", 0.85, "Sound"),
            PanelistVote("p3", PanelistRole.SKEPTIC, "option_a", 0.8, "OK"),
            PanelistVote("p4", PanelistRole.INTEGRATOR, "option_b", 0.7, "Alternative"),
            PanelistVote("p5", PanelistRole.CALIBRATOR, "option_a", 0.88, "Correct"),
        ]
        has_consensus, decision, confidence = resolver._compute_consensus(votes)
        assert has_consensus is True
        assert decision == "option_a"
        assert 0.7 < confidence < 1.0

    def test_majority_consensus(self):
        """Test majority (≥60%) agreement."""
        resolver = PanelResolver(
            PanelConfig(panel_type="outcome_vocab", n_panelists=5, consensus_threshold=0.6)
        )
        votes = [
            PanelistVote("p1", PanelistRole.DOMAIN_EXPERT, "option_a", 0.9, "Best"),
            PanelistVote("p2", PanelistRole.METHODOLOGIST, "option_a", 0.85, "Good"),
            PanelistVote("p3", PanelistRole.SKEPTIC, "option_b", 0.7, "Different"),
            PanelistVote("p4", PanelistRole.INTEGRATOR, "option_b", 0.75, "Other"),
            PanelistVote("p5", PanelistRole.CALIBRATOR, "option_a", 0.88, "Right"),
        ]
        has_consensus, decision, confidence = resolver._compute_consensus(votes)
        assert has_consensus is True
        assert decision == "option_a"

    def test_split_no_consensus(self):
        """Test split vote with no consensus."""
        resolver = PanelResolver(
            PanelConfig(panel_type="outcome_vocab", n_panelists=5, consensus_threshold=0.7)
        )
        votes = [
            PanelistVote("p1", PanelistRole.DOMAIN_EXPERT, "option_a", 0.9, "Option A"),
            PanelistVote("p2", PanelistRole.METHODOLOGIST, "option_a", 0.85, "Option A"),
            PanelistVote("p3", PanelistRole.SKEPTIC, "option_b", 0.8, "Option B"),
            PanelistVote("p4", PanelistRole.INTEGRATOR, "option_b", 0.75, "Option B"),
            PanelistVote("p5", PanelistRole.CALIBRATOR, "option_b", 0.88, "Option B"),
        ]
        has_consensus, decision, confidence = resolver._compute_consensus(votes)
        assert has_consensus is False
        assert decision in ["option_a", "option_b"]

    def test_consensus_respects_confidence_floor(self):
        """Test that votes below confidence_floor are excluded."""
        config = PanelConfig(panel_type="outcome_vocab", n_panelists=5, confidence_floor=0.5)
        resolver = PanelResolver(config)
        votes = [
            PanelistVote("p1", PanelistRole.DOMAIN_EXPERT, "option_a", 0.9, "Strong"),
            PanelistVote("p2", PanelistRole.METHODOLOGIST, "option_a", 0.85, "Strong"),
            PanelistVote("p3", PanelistRole.SKEPTIC, "option_b", 0.3, "Weak"),  # Below floor
            PanelistVote("p4", PanelistRole.INTEGRATOR, "option_a", 0.88, "Strong"),
            PanelistVote("p5", PanelistRole.CALIBRATOR, "option_a", 0.92, "Strong"),
        ]
        has_consensus, decision, confidence = resolver._compute_consensus(votes)
        # p3's vote should be excluded, so we have 4 valid votes, 4/4 for option_a
        assert has_consensus is True
        assert decision == "option_a"

    def test_consensus_empty_votes(self):
        """Test consensus with no valid votes."""
        resolver = PanelResolver(PanelConfig(panel_type="outcome_vocab", n_panelists=5))
        votes = [
            PanelistVote("p1", PanelistRole.DOMAIN_EXPERT, "option_a", 0.0, "No confidence"),
            PanelistVote("p2", PanelistRole.METHODOLOGIST, "option_b", 0.0, "No confidence"),
        ]
        has_consensus, decision, confidence = resolver._compute_consensus(votes)
        assert has_consensus is False


class TestBuildPanelistPrompt:
    """Test panelist prompt generation for different panel types."""

    def test_outcome_vocab_prompt(self):
        """Test outcome_vocab prompt generation."""
        config = PanelConfig(panel_type="outcome_vocab")
        resolver = PanelResolver(config)
        item = {
            "id": "item_1",
            "term": "improved mood",
            "context": "In the context of environmental psychology",
            "options": ["affect.positive", "affect.calm", "affect.engaged"],
        }
        prompt = resolver._build_panelist_prompt(item, PanelistRole.DOMAIN_EXPERT)
        assert "item_1" in prompt
        assert "improved mood" in prompt
        assert "domain_expert" in prompt
        assert "affect.positive" in prompt

    def test_image_classification_prompt(self):
        """Test image_classification prompt generation."""
        config = PanelConfig(panel_type="image_classification")
        resolver = PanelResolver(config)
        item = {
            "id": "img_1",
            "metadata": {"size": "large", "color": "yes"},
            "context": "Office environment study",
            "options": ["environmental", "social", "artifact"],
        }
        prompt = resolver._build_panelist_prompt(item, PanelistRole.SKEPTIC)
        assert "img_1" in prompt
        assert "image_classification" in prompt
        assert "skeptic" in prompt
        assert "environmental" in prompt

    def test_taxonomy_reconciliation_prompt(self):
        """Test taxonomy_reconciliation prompt generation."""
        config = PanelConfig(panel_type="taxonomy_reconciliation")
        resolver = PanelResolver(config)
        item = {
            "id": "tax_1",
            "entry1": "affect.wellbeing",
            "entry2": "emotion.well_being",
            "context": "Overlapping emotion taxonomy entries",
            "options": ["merge|keep_separate|deprecate_entry1"],
        }
        prompt = resolver._build_panelist_prompt(item, PanelistRole.INTEGRATOR)
        assert "tax_1" in prompt
        assert "affect.wellbeing" in prompt
        assert "emotion.well_being" in prompt

    def test_annotation_qa_prompt(self):
        """Test annotation_qa prompt generation."""
        config = PanelConfig(panel_type="annotation_qa")
        resolver = PanelResolver(config)
        item = {
            "id": "ann_1",
            "annotation": "improved mood",
            "source_text": "The indoor plants made workers feel happier and more relaxed.",
            "context": "Does annotation match source?",
            "options": ["GOOD", "FAIR", "POOR"],
        }
        prompt = resolver._build_panelist_prompt(item, PanelistRole.CALIBRATOR)
        assert "ann_1" in prompt
        assert "improved mood" in prompt
        assert "calibrator" in prompt
        assert "GOOD" in prompt


class TestResolveBatch:
    """Test batch resolution in dry_run mode."""

    def test_resolve_batch_dry_run(self):
        """Test resolving a batch of items in dry_run mode."""
        config = PanelConfig(
            panel_type="outcome_vocab",
            n_panelists=5,
            dry_run=True,
        )
        resolver = PanelResolver(config)
        items = [
            {
                "id": "item_1",
                "term": "improved mood",
                "context": "Environmental context",
                "options": ["affect.positive", "affect.calm"],
            },
            {
                "id": "item_2",
                "term": "reduced stress",
                "context": "Environmental context",
                "options": ["affect.calm", "physio.cortisol"],
            },
        ]
        result = resolver.resolve_batch(items)

        assert "decisions" in result
        assert "stats" in result
        assert len(result["decisions"]) == 2
        assert result["decisions"][0].item_id == "item_1"
        assert result["decisions"][1].item_id == "item_2"

    def test_resolve_batch_statistics(self):
        """Test that statistics are computed correctly."""
        config = PanelConfig(
            panel_type="outcome_vocab",
            n_panelists=5,
            dry_run=True,
        )
        resolver = PanelResolver(config)
        items = [
            {"id": f"item_{i}", "term": f"term_{i}", "context": "", "options": ["opt_a", "opt_b"]}
            for i in range(3)
        ]
        result = resolver.resolve_batch(items)

        stats = result["stats"]
        assert stats["total_resolved"] == 3
        assert "consensus_rate" in stats
        assert "avg_confidence" in stats

    def test_session_decisions_tracked(self):
        """Test that session decisions are tracked."""
        config = PanelConfig(panel_type="outcome_vocab", n_panelists=5, dry_run=True)
        resolver = PanelResolver(config)
        items = [
            {"id": "item_1", "term": "mood", "context": "", "options": ["opt_a"]},
            {"id": "item_2", "term": "stress", "context": "", "options": ["opt_b"]},
        ]
        resolver.resolve_batch(items)

        assert len(resolver.session_decisions) == 2
        assert resolver.session_decisions[0].item_id == "item_1"
        assert resolver.session_decisions[1].item_id == "item_2"


class TestGetPanelReport:
    """Test panel report generation."""

    def test_panel_report_structure(self):
        """Test that panel report has expected structure."""
        config = PanelConfig(panel_type="outcome_vocab", n_panelists=5, dry_run=True)
        resolver = PanelResolver(config)
        items = [{"id": "item_1", "term": "mood", "context": "", "options": ["opt_a"]}]
        resolver.resolve_batch(items)

        report = resolver.get_panel_report()
        assert "session_stats" in report
        assert "decisions_made" in report
        assert "generated_at" in report
        assert len(report["decisions_made"]) == 1

    def test_panel_report_empty_session(self):
        """Test panel report for empty session."""
        config = PanelConfig(panel_type="outcome_vocab", n_panelists=5)
        resolver = PanelResolver(config)

        report = resolver.get_panel_report()
        assert report["session_stats"]["total_resolved"] == 0
        assert len(report["decisions_made"]) == 0


class TestResolutionResult:
    """Test ResolutionResult creation and serialization."""

    def test_resolution_result_creation(self):
        """Test creating a resolution result."""
        votes = [
            PanelistVote("p1", PanelistRole.DOMAIN_EXPERT, "option_a", 0.9, "Good"),
        ]
        result = ResolutionResult(
            item_id="item_1",
            decision="option_a",
            confidence=0.9,
            consensus_type="unanimous",
            votes=votes,
            dissenting_views=[],
        )
        assert result.item_id == "item_1"
        assert result.decision == "option_a"
        assert result.consensus_type == "unanimous"

    def test_resolution_result_to_dict(self):
        """Test serializing result to dict."""
        votes = [
            PanelistVote("p1", PanelistRole.DOMAIN_EXPERT, "option_a", 0.9, "Good"),
        ]
        result = ResolutionResult(
            item_id="item_1",
            decision="option_a",
            confidence=0.9,
            consensus_type="majority",
            votes=votes,
            dissenting_views=["skeptic: needs more evidence"],
        )
        d = result.to_dict()
        assert d["item_id"] == "item_1"
        assert d["decision"] == "option_a"
        assert len(d["votes"]) == 1
        assert len(d["dissenting_views"]) == 1
        assert "resolved_at" in d


class TestPanelResolverInitialization:
    """Test PanelResolver initialization."""

    def test_resolver_unsupported_panel_type(self):
        """Test that unsupported panel types raise error."""
        config = PanelConfig(panel_type="unsupported_type")
        with pytest.raises(ValueError, match="Unsupported panel_type"):
            PanelResolver(config)

    def test_resolver_initialization(self):
        """Test successful resolver initialization."""
        config = PanelConfig(panel_type="outcome_vocab", n_panelists=5)
        resolver = PanelResolver(config)
        assert resolver.config == config
        assert len(resolver.session_decisions) == 0


class TestAssignRoles:
    """Test panelist role assignment."""

    def test_assign_roles_distribution(self):
        """Test that roles are distributed across panelists."""
        config = PanelConfig(panel_type="outcome_vocab", n_panelists=5)
        resolver = PanelResolver(config)
        roles = resolver._assign_roles()

        assert len(roles) == 5
        assert all(isinstance(r, PanelistRole) for r in roles)
        # With 5 panelists, we should see different roles
        assert len(set(roles)) > 1

    def test_assign_roles_respects_count(self):
        """Test that correct number of roles are assigned."""
        config = PanelConfig(panel_type="outcome_vocab", n_panelists=7)
        resolver = PanelResolver(config)
        roles = resolver._assign_roles()

        assert len(roles) == 7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
