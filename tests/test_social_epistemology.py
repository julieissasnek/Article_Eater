"""
Test Suite for Social Epistemology Module (Sprint 2.5)
======================================================

Tests for:
- EpistemicCommunity
- BeliefProvenance
- ContestationTracker
- MethodologicalDiversityAssessor
- CommunityRegistry
- Integration with web_of_belief.py

Date: February 8, 2026
Lane: B (Implementation)
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from src.services.social_epistemology import (
    # Enums
    CommunityType,
    ContestationType,
    DisagreementResolution,
    CommunityLevel,
    # Classes
    EpistemicCommunity,
    BeliefProvenance,
    Contestation,
    ContestationTracker,
    MethodologicalProfile,
    MethodologicalDiversityAssessor,
    CommunityRegistry,
    CommunityHistoryEvent,
    # Functions
    create_cnfa_seed_communities,
    identify_community_for_belief,
)


# =============================================================================
# ENUM TESTS
# =============================================================================

class TestEnums:
    """Tests for all social epistemology enums."""

    def test_community_type_values(self):
        """Verify all CommunityType values exist."""
        assert CommunityType.JOURNAL_CLUSTER.value == "journal_cluster"
        assert CommunityType.CITATION_NETWORK.value == "citation_network"
        assert CommunityType.THEORY_COMMITMENT.value == "theory_commitment"
        assert CommunityType.METHODOLOGICAL.value == "methodological"
        assert CommunityType.INSTITUTIONAL.value == "institutional"
        assert CommunityType.PARADIGM.value == "paradigm"

    def test_community_level_values(self):
        """Verify CommunityLevel hierarchy values."""
        assert CommunityLevel.FIELD.value == "field"
        assert CommunityLevel.PARADIGM.value == "paradigm"
        assert CommunityLevel.SUBFIELD.value == "subfield"
        assert CommunityLevel.LAB.value == "lab"

    def test_contestation_type_values(self):
        """Verify all ContestationType values exist."""
        assert ContestationType.EMPIRICAL.value == "empirical"
        assert ContestationType.METHODOLOGICAL.value == "methodological"
        assert ContestationType.THEORETICAL.value == "theoretical"
        assert ContestationType.SCOPE.value == "scope"
        assert ContestationType.VALUE.value == "value"
        assert ContestationType.INCOMMENSURABLE.value == "incommensurable"

    def test_disagreement_resolution_values(self):
        """Verify DisagreementResolution values per SE-2."""
        assert DisagreementResolution.AVERAGE.value == "average"
        assert DisagreementResolution.REPORT_SEPARATELY.value == "report_separately"
        assert DisagreementResolution.FLAG_INCOMMENSURABLE.value == "flag_incommensurable"


# =============================================================================
# EPISTEMIC COMMUNITY TESTS
# =============================================================================

class TestEpistemicCommunity:
    """Tests for EpistemicCommunity class."""

    def test_create_community(self):
        """Test basic community creation."""
        comm = EpistemicCommunity(
            community_id="comm:test",
            name="Test Community",
            community_type=CommunityType.THEORY_COMMITMENT,
            level=CommunityLevel.PARADIGM
        )

        assert comm.community_id == "comm:test"
        assert comm.name == "Test Community"
        assert comm.community_type == CommunityType.THEORY_COMMITMENT
        assert comm.level == CommunityLevel.PARADIGM

    def test_community_defaults(self):
        """Test default values are set correctly."""
        comm = EpistemicCommunity(
            community_id="comm:test",
            name="Test",
            community_type=CommunityType.THEORY_COMMITMENT,
            level=CommunityLevel.FIELD
        )

        assert comm.institutional_power == 0.5
        assert comm.contestation_level == 0.0
        assert comm.foundational_works == []
        assert comm.core_theories == []
        assert isinstance(comm.characteristic_vocabulary, set)

    def test_track_record_weight_no_domain(self):
        """Test track record weight returns 0.5 for unknown domain."""
        comm = EpistemicCommunity(
            community_id="comm:test",
            name="Test",
            community_type=CommunityType.THEORY_COMMITMENT,
            level=CommunityLevel.PARADIGM
        )

        weight = comm.track_record_weight("unknown_domain")
        assert weight == 0.5  # Default

    def test_track_record_weight_with_domain(self):
        """Test track record weight uses domain-specific accuracy."""
        comm = EpistemicCommunity(
            community_id="comm:test",
            name="Test",
            community_type=CommunityType.THEORY_COMMITMENT,
            level=CommunityLevel.PARADIGM,
            domain_track_records={"attention": 0.8}
        )

        weight = comm.track_record_weight("attention")
        assert weight == 0.8

    def test_track_record_weight_with_contestation(self):
        """Test contestation discounts track record (per SE-3)."""
        comm = EpistemicCommunity(
            community_id="comm:test",
            name="Test",
            community_type=CommunityType.THEORY_COMMITMENT,
            level=CommunityLevel.PARADIGM,
            domain_track_records={"attention": 0.8},
            contestation_level=0.5
        )

        weight = comm.track_record_weight("attention")
        expected = 0.8 * (1.0 - 0.5 * 0.5)  # 0.8 * 0.75 = 0.6
        assert abs(weight - expected) < 0.001

    def test_vocabulary_overlap_empty(self):
        """Test vocabulary overlap with empty vocabularies."""
        comm1 = EpistemicCommunity(
            community_id="comm:1",
            name="Test1",
            community_type=CommunityType.THEORY_COMMITMENT,
            level=CommunityLevel.PARADIGM
        )
        comm2 = EpistemicCommunity(
            community_id="comm:2",
            name="Test2",
            community_type=CommunityType.THEORY_COMMITMENT,
            level=CommunityLevel.PARADIGM
        )

        assert comm1.vocabulary_overlap(comm2) == 0.0

    def test_vocabulary_overlap_partial(self):
        """Test vocabulary overlap with partial match."""
        comm1 = EpistemicCommunity(
            community_id="comm:1",
            name="Test1",
            community_type=CommunityType.THEORY_COMMITMENT,
            level=CommunityLevel.PARADIGM,
            characteristic_vocabulary={"attention", "restoration", "fascination"}
        )
        comm2 = EpistemicCommunity(
            community_id="comm:2",
            name="Test2",
            community_type=CommunityType.THEORY_COMMITMENT,
            level=CommunityLevel.PARADIGM,
            characteristic_vocabulary={"attention", "stress", "cortisol"}
        )

        overlap = comm1.vocabulary_overlap(comm2)
        # Jaccard: 1 intersection / 5 union = 0.2
        assert abs(overlap - 0.2) < 0.001

    def test_add_history_event(self):
        """Test adding history events (per SE-4)."""
        comm = EpistemicCommunity(
            community_id="comm:test",
            name="Test",
            community_type=CommunityType.THEORY_COMMITMENT,
            level=CommunityLevel.PARADIGM
        )

        event = comm.add_history_event(
            event_type="credence_shift",
            description="Major credence update",
            affected_beliefs=["belief:123"],
            magnitude=0.3
        )

        assert len(comm.history_events) == 1
        assert event.event_type == "credence_shift"
        assert event.magnitude == 0.3

    def test_community_to_dict(self):
        """Test community serialization."""
        comm = EpistemicCommunity(
            community_id="comm:test",
            name="Test Community",
            community_type=CommunityType.THEORY_COMMITMENT,
            level=CommunityLevel.PARADIGM,
            characteristic_vocabulary={"term1", "term2"}
        )

        d = comm.to_dict()
        assert d['community_id'] == "comm:test"
        assert d['name'] == "Test Community"
        assert d['community_type'] == "theory_commitment"
        assert d['level'] == "paradigm"
        assert set(d['characteristic_vocabulary']) == {"term1", "term2"}

    def test_community_from_dict(self):
        """Test community deserialization."""
        d = {
            'community_id': "comm:test",
            'name': "Test Community",
            'community_type': "theory_commitment",
            'level': "paradigm",
            'characteristic_vocabulary': ["term1", "term2"]
        }

        comm = EpistemicCommunity.from_dict(d)
        assert comm.community_id == "comm:test"
        assert comm.name == "Test Community"
        assert comm.community_type == CommunityType.THEORY_COMMITMENT
        assert comm.level == CommunityLevel.PARADIGM


# =============================================================================
# BELIEF PROVENANCE TESTS
# =============================================================================

class TestBeliefProvenance:
    """Tests for BeliefProvenance class."""

    def test_create_provenance(self):
        """Test basic provenance creation."""
        prov = BeliefProvenance(
            belief_id="belief:123",
            producing_communities=["comm:art"],
            methods_used=["lab_experiment"]
        )

        assert prov.belief_id == "belief:123"
        assert "comm:art" in prov.producing_communities
        assert "lab_experiment" in prov.methods_used

    def test_set_community_credence(self):
        """Test setting community credences."""
        prov = BeliefProvenance(belief_id="belief:123")
        prov.set_community_credence("comm:art", 0.7)
        prov.set_community_credence("comm:srt", 0.4)

        assert prov.get_community_credence("comm:art") == 0.7
        assert prov.get_community_credence("comm:srt") == 0.4

    def test_community_credence_clamping(self):
        """Test credence values are clamped to 0.01-0.99."""
        prov = BeliefProvenance(belief_id="belief:123")
        prov.set_community_credence("comm:test", 1.5)
        assert prov.get_community_credence("comm:test") == 0.99

        prov.set_community_credence("comm:test2", -0.5)
        assert prov.get_community_credence("comm:test2") == 0.01

    def test_is_contested_no_communities(self):
        """Test not contested with single community."""
        prov = BeliefProvenance(
            belief_id="belief:123",
            community_credences={"comm:art": 0.7}
        )

        assert not prov.is_contested()

    def test_is_contested_low_spread(self):
        """Test not contested when spread < 0.2."""
        prov = BeliefProvenance(
            belief_id="belief:123",
            community_credences={"comm:art": 0.7, "comm:srt": 0.6}
        )

        assert not prov.is_contested()

    def test_is_contested_high_spread(self):
        """Test contested when spread > 0.2 (per SE-2)."""
        prov = BeliefProvenance(
            belief_id="belief:123",
            community_credences={"comm:art": 0.8, "comm:srt": 0.3}
        )

        assert prov.is_contested()

    def test_compute_aggregated_credence_incommensurable(self):
        """Test no aggregation for incommensurable contestation."""
        prov = BeliefProvenance(
            belief_id="belief:123",
            contestation_type=ContestationType.INCOMMENSURABLE,
            community_credences={"comm:art": 0.8, "comm:srt": 0.3}
        )

        result, approach = prov.compute_aggregated_credence({}, "test")
        assert result is None
        assert approach == DisagreementResolution.FLAG_INCOMMENSURABLE

    def test_compute_aggregated_credence_theoretical(self):
        """Test no aggregation for theoretical contestation."""
        prov = BeliefProvenance(
            belief_id="belief:123",
            contestation_type=ContestationType.THEORETICAL,
            community_credences={"comm:art": 0.8, "comm:srt": 0.3}
        )

        result, approach = prov.compute_aggregated_credence({}, "test")
        assert result is None
        assert approach == DisagreementResolution.FLAG_INCOMMENSURABLE

    def test_compute_aggregated_credence_methodological(self):
        """Test report separately for methodological contestation."""
        prov = BeliefProvenance(
            belief_id="belief:123",
            contestation_type=ContestationType.METHODOLOGICAL,
            community_credences={"comm:art": 0.8, "comm:srt": 0.3}
        )

        result, approach = prov.compute_aggregated_credence({}, "test")
        assert result is None
        assert approach == DisagreementResolution.REPORT_SEPARATELY

    def test_compute_aggregated_credence_empirical(self):
        """Test weighted average for empirical contestation (per SE-2)."""
        art = EpistemicCommunity(
            community_id="comm:art",
            name="ART",
            community_type=CommunityType.THEORY_COMMITMENT,
            level=CommunityLevel.PARADIGM,
            domain_track_records={"attention": 0.8}
        )
        srt = EpistemicCommunity(
            community_id="comm:srt",
            name="SRT",
            community_type=CommunityType.THEORY_COMMITMENT,
            level=CommunityLevel.PARADIGM,
            domain_track_records={"attention": 0.6}
        )

        prov = BeliefProvenance(
            belief_id="belief:123",
            contestation_type=ContestationType.EMPIRICAL,
            community_credences={"comm:art": 0.8, "comm:srt": 0.4}
        )

        communities = {"comm:art": art, "comm:srt": srt}
        result, approach = prov.compute_aggregated_credence(communities, "attention")

        # Expected: (0.8 * 0.8 + 0.4 * 0.6) / (0.8 + 0.6) = (0.64 + 0.24) / 1.4 = 0.629
        assert approach == DisagreementResolution.AVERAGE
        assert result is not None
        assert abs(result - 0.629) < 0.01

    def test_provenance_to_dict(self):
        """Test provenance serialization."""
        prov = BeliefProvenance(
            belief_id="belief:123",
            producing_communities=["comm:art"],
            methods_used=["lab_experiment"],
            community_credences={"comm:art": 0.7}
        )

        d = prov.to_dict()
        assert d['belief_id'] == "belief:123"
        assert "comm:art" in d['producing_communities']
        assert d['community_credences']['comm:art'] == 0.7

    def test_provenance_from_dict(self):
        """Test provenance deserialization."""
        d = {
            'belief_id': "belief:123",
            'producing_communities': ["comm:art"],
            'methods_used': ["lab_experiment"],
            'contestation_type': "empirical"
        }

        prov = BeliefProvenance.from_dict(d)
        assert prov.belief_id == "belief:123"
        assert prov.contestation_type == ContestationType.EMPIRICAL


# =============================================================================
# CONTESTATION TRACKER TESTS
# =============================================================================

class TestContestationTracker:
    """Tests for ContestationTracker class."""

    def test_add_contestation(self):
        """Test adding a contestation."""
        tracker = ContestationTracker()
        contestation = Contestation(
            contestation_id="cont:1",
            belief_id="belief:123",
            contesting_community_id="comm:srt",
            target_community_id="comm:art",
            contestation_type=ContestationType.METHODOLOGICAL,
            description="Method disagreement"
        )

        tracker.add_contestation(contestation)

        assert tracker.get_contestation("cont:1") is not None
        assert len(tracker.get_contestations_for_belief("belief:123")) == 1

    def test_get_community_contestations(self):
        """Test retrieving contestations by community."""
        tracker = ContestationTracker()
        contestation = Contestation(
            contestation_id="cont:1",
            belief_id="belief:123",
            contesting_community_id="comm:srt",
            target_community_id="comm:art",
            contestation_type=ContestationType.METHODOLOGICAL,
            description="Method disagreement"
        )
        tracker.add_contestation(contestation)

        # Both communities should have this contestation
        art_contestations = tracker.get_community_contestations("comm:art")
        srt_contestations = tracker.get_community_contestations("comm:srt")

        assert len(art_contestations) == 1
        assert len(srt_contestations) == 1

    def test_compute_contestation_level_none(self):
        """Test contestation level is 0 with no contestations."""
        tracker = ContestationTracker()
        level = tracker.compute_contestation_level("comm:art")
        assert level == 0.0

    def test_compute_contestation_level_empirical(self):
        """Test contestation level for empirical disagreement (weight: 0.3)."""
        tracker = ContestationTracker()
        contestation = Contestation(
            contestation_id="cont:1",
            belief_id="belief:123",
            contesting_community_id="comm:srt",
            target_community_id="comm:art",
            contestation_type=ContestationType.EMPIRICAL,
            description="Data disagreement"
        )
        tracker.add_contestation(contestation)

        level = tracker.compute_contestation_level("comm:art")
        assert abs(level - 0.06) < 0.01  # 0.3 / 5.0

    def test_compute_contestation_level_theoretical(self):
        """Test contestation level for theoretical disagreement (weight: 0.8)."""
        tracker = ContestationTracker()
        contestation = Contestation(
            contestation_id="cont:1",
            belief_id="belief:123",
            contesting_community_id="comm:srt",
            target_community_id="comm:art",
            contestation_type=ContestationType.THEORETICAL,
            description="Framework disagreement"
        )
        tracker.add_contestation(contestation)

        level = tracker.compute_contestation_level("comm:art")
        assert abs(level - 0.16) < 0.01  # 0.8 / 5.0

    def test_compute_contestation_level_resolved_ignored(self):
        """Test resolved contestations don't affect level."""
        tracker = ContestationTracker()
        contestation = Contestation(
            contestation_id="cont:1",
            belief_id="belief:123",
            contesting_community_id="comm:srt",
            target_community_id="comm:art",
            contestation_type=ContestationType.THEORETICAL,
            description="Framework disagreement",
            is_resolved=True
        )
        tracker.add_contestation(contestation)

        level = tracker.compute_contestation_level("comm:art")
        assert level == 0.0

    def test_identify_experimenter_regress(self):
        """Test identifying experimenter's regress (per Collins)."""
        tracker = ContestationTracker()
        contestation1 = Contestation(
            contestation_id="cont:1",
            belief_id="belief:123",
            contesting_community_id="comm:srt",
            target_community_id="comm:art",
            contestation_type=ContestationType.METHODOLOGICAL,
            description="Normal disagreement",
            experimenter_regress=False
        )
        contestation2 = Contestation(
            contestation_id="cont:2",
            belief_id="belief:123",
            contesting_community_id="comm:bio",
            target_community_id="comm:art",
            contestation_type=ContestationType.INCOMMENSURABLE,
            description="Deep disagreement",
            experimenter_regress=True
        )
        tracker.add_contestation(contestation1)
        tracker.add_contestation(contestation2)

        regress = tracker.identify_experimenter_regress("belief:123")
        assert len(regress) == 1
        assert regress[0].contestation_id == "cont:2"

    def test_remove_contestation(self):
        """Test removing a contestation."""
        tracker = ContestationTracker()
        contestation = Contestation(
            contestation_id="cont:1",
            belief_id="belief:123",
            contesting_community_id="comm:srt",
            target_community_id="comm:art",
            contestation_type=ContestationType.EMPIRICAL,
            description="Test"
        )
        tracker.add_contestation(contestation)
        assert tracker.get_contestation("cont:1") is not None

        tracker.remove_contestation("cont:1")
        assert tracker.get_contestation("cont:1") is None


# =============================================================================
# METHODOLOGICAL DIVERSITY TESTS
# =============================================================================

class TestMethodologicalProfile:
    """Tests for MethodologicalProfile class."""

    def test_diversity_index_single_method(self):
        """Test diversity index is 0 for single method."""
        profile = MethodologicalProfile(
            belief_id="belief:123",
            methods={"lab_experiment": 5}
        )

        assert profile.diversity_index() == 0.0

    def test_diversity_index_multiple_methods(self):
        """Test diversity index increases with multiple methods."""
        profile = MethodologicalProfile(
            belief_id="belief:123",
            methods={"lab_experiment": 3, "field_study": 2},
            settings={"lab": 3, "field": 2}
        )

        assert profile.diversity_index() > 0.0

    def test_identify_vulnerabilities_single_method(self):
        """Test vulnerability detection for single method."""
        profile = MethodologicalProfile(
            belief_id="belief:123",
            methods={"lab_experiment": 5}
        )

        vulns = profile.identify_vulnerabilities()
        assert any("Single method" in v for v in vulns)

    def test_identify_vulnerabilities_dominant_method(self):
        """Test vulnerability detection for dominant method (>80%)."""
        profile = MethodologicalProfile(
            belief_id="belief:123",
            methods={"lab_experiment": 9, "field_study": 1}
        )

        vulns = profile.identify_vulnerabilities()
        assert any("Dominant method" in v for v in vulns)

    def test_no_vulnerabilities_diverse(self):
        """Test no vulnerabilities for diverse profile."""
        profile = MethodologicalProfile(
            belief_id="belief:123",
            methods={"lab_experiment": 3, "field_study": 3, "survey": 3},
            settings={"lab": 3, "field": 3, "online": 3},
            populations={"adults": 3, "children": 3, "elderly": 3}
        )

        vulns = profile.identify_vulnerabilities()
        assert len(vulns) == 0


class TestMethodologicalDiversityAssessor:
    """Tests for MethodologicalDiversityAssessor class."""

    def test_suggest_diversification_lab_only(self):
        """Test suggestions for lab-only studies."""
        assessor = MethodologicalDiversityAssessor()
        assessor.profiles["belief:123"] = MethodologicalProfile(
            belief_id="belief:123",
            methods={"lab_experiment": 5},
            settings={"lab": 5}
        )

        suggestions = assessor.suggest_diversification("belief:123")
        assert "setting" in suggestions
        assert "field_study" in suggestions["setting"] or "naturalistic_observation" in suggestions["setting"]


# =============================================================================
# COMMUNITY REGISTRY TESTS
# =============================================================================

class TestCommunityRegistry:
    """Tests for CommunityRegistry class."""

    def test_add_and_get_community(self):
        """Test adding and retrieving a community."""
        registry = CommunityRegistry()
        comm = EpistemicCommunity(
            community_id="comm:test",
            name="Test",
            community_type=CommunityType.THEORY_COMMITMENT,
            level=CommunityLevel.PARADIGM
        )

        registry.add_community(comm)
        retrieved = registry.get_community("comm:test")

        assert retrieved is not None
        assert retrieved.name == "Test"

    def test_get_communities_by_level(self):
        """Test filtering communities by level."""
        registry = CommunityRegistry()

        field = EpistemicCommunity(
            community_id="comm:field",
            name="Field",
            community_type=CommunityType.JOURNAL_CLUSTER,
            level=CommunityLevel.FIELD
        )
        paradigm = EpistemicCommunity(
            community_id="comm:paradigm",
            name="Paradigm",
            community_type=CommunityType.THEORY_COMMITMENT,
            level=CommunityLevel.PARADIGM
        )

        registry.add_community(field)
        registry.add_community(paradigm)

        fields = registry.get_communities_by_level(CommunityLevel.FIELD)
        paradigms = registry.get_communities_by_level(CommunityLevel.PARADIGM)

        assert len(fields) == 1
        assert len(paradigms) == 1
        assert fields[0].community_id == "comm:field"
        assert paradigms[0].community_id == "comm:paradigm"

    def test_find_by_vocabulary(self):
        """Test finding communities by vocabulary overlap."""
        registry = CommunityRegistry()
        comm = EpistemicCommunity(
            community_id="comm:art",
            name="ART",
            community_type=CommunityType.THEORY_COMMITMENT,
            level=CommunityLevel.PARADIGM,
            characteristic_vocabulary={"attention", "restoration", "fascination", "directed_attention"}
        )
        registry.add_community(comm)

        results = registry.find_by_vocabulary(
            {"attention", "cognitive", "restoration"},
            min_overlap=0.2
        )

        assert len(results) == 1
        assert results[0][0].community_id == "comm:art"
        assert results[0][1] > 0.2

    def test_registry_serialization(self):
        """Test registry serialization and deserialization."""
        registry = CommunityRegistry()
        comm = EpistemicCommunity(
            community_id="comm:test",
            name="Test",
            community_type=CommunityType.THEORY_COMMITMENT,
            level=CommunityLevel.PARADIGM
        )
        registry.add_community(comm)

        d = registry.to_dict()
        restored = CommunityRegistry.from_dict(d)

        assert len(restored.all_communities()) == 1
        assert restored.get_community("comm:test") is not None


# =============================================================================
# SEED DATA TESTS
# =============================================================================

class TestSeedData:
    """Tests for CNFA seed community data."""

    def test_create_seed_communities(self):
        """Test seed community creation."""
        communities = create_cnfa_seed_communities()

        assert len(communities) == 4

        # Check ART community
        art = next(c for c in communities if c.community_id == "comm:art")
        assert art.name == "Attention Restoration Theory"
        assert "directed_attention" in art.characteristic_vocabulary
        assert art.parent_community_id == "comm:env_psych"

        # Check SRT community
        srt = next(c for c in communities if c.community_id == "comm:srt")
        assert srt.name == "Stress Recovery Theory"
        assert "cortisol" in srt.characteristic_vocabulary

        # Check parent community
        env_psych = next(c for c in communities if c.community_id == "comm:env_psych")
        assert env_psych.level == CommunityLevel.FIELD
        assert "comm:art" in env_psych.child_community_ids


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestWebOfBeliefIntegration:
    """Tests for integration with web_of_belief.py."""

    def test_belief_with_provenance(self):
        """Test Belief can have provenance."""
        from src.services.web_of_belief import Belief, EpistemicLevel

        prov = BeliefProvenance(
            belief_id="belief:123",
            producing_communities=["comm:art"],
            community_credences={"comm:art": 0.8, "comm:srt": 0.4}
        )

        belief = Belief(
            belief_id="belief:123",
            content="Nature exposure reduces stress",
            level=EpistemicLevel.EMPIRICAL
        )
        belief.set_provenance(prov)

        assert belief.provenance is not None
        assert belief.get_community_credence("comm:art") == 0.8
        assert belief.is_community_contested()  # Spread > 0.2

    def test_belief_community_associations(self):
        """Test Belief can have community associations."""
        from src.services.web_of_belief import Belief, EpistemicLevel

        belief = Belief(
            belief_id="belief:123",
            content="Nature exposure reduces stress",
            level=EpistemicLevel.EMPIRICAL
        )

        belief.add_community_association("comm:art", 0.8)
        belief.add_community_association("comm:srt", 0.6)

        assert belief.community_associations["comm:art"] == 0.8
        assert belief.community_associations["comm:srt"] == 0.6

    def test_belief_to_dict_with_provenance(self):
        """Test Belief serialization includes provenance."""
        from src.services.web_of_belief import Belief, EpistemicLevel

        prov = BeliefProvenance(
            belief_id="belief:123",
            producing_communities=["comm:art"]
        )

        belief = Belief(
            belief_id="belief:123",
            content="Test belief",
            level=EpistemicLevel.EMPIRICAL,
            provenance=prov,
            community_associations={"comm:art": 0.7}
        )

        d = belief.to_dict()
        assert 'provenance' in d
        assert d['provenance']['belief_id'] == "belief:123"
        assert 'community_associations' in d
        assert d['community_associations']['comm:art'] == 0.7

    def test_belief_from_dict_with_provenance(self):
        """Test Belief deserialization restores provenance."""
        from src.services.web_of_belief import Belief

        d = {
            'belief_id': "belief:123",
            'content': "Test belief",
            'level': "empirical",
            'provenance': {
                'belief_id': "belief:123",
                'producing_communities': ["comm:art"],
                'community_credences': {"comm:art": 0.8}
            },
            'community_associations': {"comm:art": 0.7}
        }

        belief = Belief.from_dict(d)
        assert belief.provenance is not None
        assert belief.get_community_credence("comm:art") == 0.8
        assert belief.community_associations["comm:art"] == 0.7


# =============================================================================
# HISTORY EVENT TESTS
# =============================================================================

class TestCommunityHistoryEvent:
    """Tests for CommunityHistoryEvent class."""

    def test_create_history_event(self):
        """Test creating a history event."""
        event = CommunityHistoryEvent(
            event_id="event:123",
            timestamp=datetime.now(timezone.utc),
            event_type="credence_shift",
            description="Major shift in community credence",
            affected_beliefs=["belief:1", "belief:2"],
            magnitude=0.3,
            causal_tags=["new_evidence"],
            triggering_papers=["10.1234/test"]
        )

        assert event.event_id == "event:123"
        assert event.event_type == "credence_shift"
        assert event.magnitude == 0.3

    def test_history_event_serialization(self):
        """Test history event serialization."""
        event = CommunityHistoryEvent(
            event_id="event:123",
            timestamp=datetime.now(timezone.utc),
            event_type="theory_adoption",
            description="Adopted new theory"
        )

        d = event.to_dict()
        restored = CommunityHistoryEvent.from_dict(d)

        assert restored.event_id == event.event_id
        assert restored.event_type == event.event_type


# =============================================================================
# CONTESTATION SERIALIZATION TESTS
# =============================================================================

class TestContestationSerialization:
    """Tests for Contestation serialization."""

    def test_contestation_to_dict(self):
        """Test contestation serialization."""
        contestation = Contestation(
            contestation_id="cont:1",
            belief_id="belief:123",
            contesting_community_id="comm:srt",
            target_community_id="comm:art",
            contestation_type=ContestationType.METHODOLOGICAL,
            description="Method disagreement",
            experimenter_regress=True
        )

        d = contestation.to_dict()
        assert d['contestation_id'] == "cont:1"
        assert d['contestation_type'] == "methodological"
        assert d['experimenter_regress'] is True

    def test_contestation_from_dict(self):
        """Test contestation deserialization."""
        d = {
            'contestation_id': "cont:1",
            'belief_id': "belief:123",
            'contesting_community_id': "comm:srt",
            'target_community_id': "comm:art",
            'contestation_type': "methodological",
            'description': "Method disagreement"
        }

        contestation = Contestation.from_dict(d)
        assert contestation.contestation_id == "cont:1"
        assert contestation.contestation_type == ContestationType.METHODOLOGICAL

    def test_tracker_serialization(self):
        """Test tracker serialization."""
        tracker = ContestationTracker()
        contestation = Contestation(
            contestation_id="cont:1",
            belief_id="belief:123",
            contesting_community_id="comm:srt",
            target_community_id="comm:art",
            contestation_type=ContestationType.EMPIRICAL,
            description="Data disagreement"
        )
        tracker.add_contestation(contestation)

        d = tracker.to_dict()
        restored = ContestationTracker.from_dict(d)

        assert len(restored.contestations) == 1
        assert restored.get_contestation("cont:1") is not None
