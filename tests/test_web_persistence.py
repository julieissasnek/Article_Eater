"""
Tests for Sprint 5: Web of Belief Persistence & Accumulation

This module tests the persistence layer per the Sprint 5 specification.

Test Cases:
1. Basic persistence - Save and load web state
2. Belief operations - CRUD for beliefs
3. Constraint operations - CRUD for constraints
4. Bridge operations - Save and load bridges
5. Master web accumulation - Integrate multiple papers
6. Belief merging - New/update/conflict resolution
7. History tracking - Coherence and merge logs
8. Statistics - Summary queries
"""

import pytest
import json
from pathlib import Path
from datetime import datetime, timezone

from src.services.web_persistence import (
    WebPersistenceService,
    MergeResult,
    IntegrationReport,
    WEB_PERSISTENCE_SCHEMA,
    BRIDGE_AVAILABLE,
    ConflictType,
)
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
    create_neuroarchitecture_web,
)

# Import bridge warrants if available
if BRIDGE_AVAILABLE:
    from src.services.bridge_warrants import (
        BridgeWarrant,
        BridgeRegistry,
        BridgeType,
        BridgeStatus,
        ConfidenceSource,
        create_bridge,
    )


class TestBasicPersistence:
    """Test Case 1: Basic save/load functionality."""

    def test_create_service_in_memory(self):
        """Verify service can be created with in-memory database."""
        service = WebPersistenceService(":memory:")
        assert service.db_path == ":memory:"

    def test_create_service_with_file(self, tmp_path):
        """Verify service can be created with file database."""
        db_path = tmp_path / "test.db"
        service = WebPersistenceService(str(db_path))
        assert service.db_path == str(db_path)

    def test_schema_creates_tables(self):
        """Verify schema creates all required tables."""
        service = WebPersistenceService(":memory:")

        with service._get_connection() as conn:
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            table_names = [t['name'] for t in tables]

        expected = [
            'web_metadata', 'beliefs', 'constraints',
            'bridges', 'paper_integrations', 'coherence_history',
            'belief_merge_log'
        ]

        for table in expected:
            assert table in table_names, f"Missing table: {table}"

    def test_save_and_load_web(self):
        """Verify web can be saved and loaded."""
        service = WebPersistenceService(":memory:")

        # Create web with belief
        web = create_neuroarchitecture_web()
        web.add_belief(Belief(
            belief_id="test:belief:001",
            content="Test belief content",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.2),
            theory_id="ART"
        ))

        # Save
        service.save_web(web, "test:web:001", "Test Web")

        # Load
        loaded_web, _ = service.load_web("test:web:001")

        assert loaded_web is not None
        assert "test:belief:001" in loaded_web.beliefs


class TestBeliefOperations:
    """Test Case 2: Belief CRUD operations."""

    def test_save_belief(self):
        """Verify belief can be saved."""
        service = WebPersistenceService(":memory:")
        service.create_web("test:web:001", "Test")

        belief = Belief(
            belief_id="test:belief:001",
            content="Nature reduces stress",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.75, 0.15, n_observations=10),
            theory_id="SRT",
            entrenchment=0.5,
            domain="physio",
            paper_ids=["paper:001", "paper:002"]
        )

        service.save_belief("test:web:001", belief)

        loaded = service.load_belief("test:belief:001", "test:web:001")

        assert loaded is not None
        assert loaded.content == "Nature reduces stress"
        assert loaded.credence.value == 0.75
        assert loaded.credence.n_observations == 10
        assert loaded.theory_id == "SRT"

    def test_update_belief(self):
        """Verify belief can be updated."""
        service = WebPersistenceService(":memory:")
        service.create_web("test:web:001", "Test")

        # Save initial
        belief = Belief(
            belief_id="test:belief:001",
            content="Initial content",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.5, 0.3)
        )
        service.save_belief("test:web:001", belief)

        # Update
        belief.content = "Updated content"
        belief.credence = Credence(0.8, 0.2)
        service.save_belief("test:web:001", belief)

        # Verify
        loaded = service.load_belief("test:belief:001", "test:web:001")
        assert loaded.content == "Updated content"
        assert loaded.credence.value == 0.8

    def test_get_beliefs_for_web(self):
        """Verify all beliefs for a web can be retrieved."""
        service = WebPersistenceService(":memory:")
        service.create_web("test:web:001", "Test")

        for i in range(5):
            service.save_belief("test:web:001", Belief(
                belief_id=f"test:belief:{i:03d}",
                content=f"Belief {i}",
                level=EpistemicLevel.EMPIRICAL,
                status=BeliefStatus.TENTATIVE,
                credence=Credence(0.5, 0.3)
            ))

        beliefs = service.get_beliefs_for_web("test:web:001")
        assert len(beliefs) == 5

    def test_belief_with_tags(self):
        """Verify beliefs with tags serialize correctly."""
        service = WebPersistenceService(":memory:")
        service.create_web("test:web:001", "Test")

        belief = Belief(
            belief_id="test:belief:001",
            content="Tagged belief",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.5, 0.3),
            tags=["attention", "cognitive", "restoration"]
        )
        service.save_belief("test:web:001", belief)

        loaded = service.load_belief("test:belief:001", "test:web:001")
        assert "attention" in loaded.tags
        assert len(loaded.tags) == 3


class TestConstraintOperations:
    """Test Case 3: Constraint CRUD operations."""

    def test_save_constraint(self):
        """Verify constraint can be saved."""
        service = WebPersistenceService(":memory:")
        service.create_web("test:web:001", "Test")

        # Create beliefs first
        service.save_belief("test:web:001", Belief(
            belief_id="belief:A",
            content="A",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.5, 0.3)
        ))
        service.save_belief("test:web:001", Belief(
            belief_id="belief:B",
            content="B",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.5, 0.3)
        ))

        constraint = Constraint(
            constraint_id="constraint:001",
            source_id="belief:A",
            target_id="belief:B",
            constraint_type=ConstraintType.SUPPORTS,
            strength=0.8,
            bidirectional=False,
            evidence_ids=["evidence:001"]
        )

        service.save_constraint("test:web:001", constraint)

        constraints = service.get_constraints_for_web("test:web:001")
        assert len(constraints) == 1
        assert constraints[0].strength == 0.8
        assert constraints[0].constraint_type == ConstraintType.SUPPORTS

    def test_bidirectional_constraint(self):
        """Verify bidirectional constraints are stored correctly."""
        service = WebPersistenceService(":memory:")
        service.create_web("test:web:001", "Test")

        # Create beliefs first to satisfy foreign key constraint
        service.save_belief("test:web:001", Belief(
            belief_id="belief:A",
            content="A",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.5, 0.3)
        ))
        service.save_belief("test:web:001", Belief(
            belief_id="belief:B",
            content="B",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.5, 0.3)
        ))

        constraint = Constraint(
            constraint_id="constraint:001",
            source_id="belief:A",
            target_id="belief:B",
            constraint_type=ConstraintType.SUPPORTS,
            strength=0.7,
            bidirectional=True
        )

        service.save_constraint("test:web:001", constraint)

        constraints = service.get_constraints_for_web("test:web:001")
        assert constraints[0].bidirectional is True


@pytest.mark.skipif(not BRIDGE_AVAILABLE, reason="Bridge warrants not available")
class TestBridgeOperations:
    """Test Case 4: Bridge warrant operations."""

    def test_save_and_load_bridge(self):
        """Verify bridge warrant can be saved and loaded."""
        service = WebPersistenceService(":memory:")
        service.create_web("test:web:001", "Test")

        bridge = create_bridge(
            source_domain="arch",
            target_domain="affect",
            bridge_type=BridgeType.MECHANISM,
            warrant_statement="Architectural features influence emotional responses",
            assumed_mechanism="Visual processing pathway activation"
        )

        service.save_bridge("test:web:001", bridge)

        bridges = service.get_bridges_for_web("test:web:001")
        assert len(bridges) == 1
        assert bridges[0].source_domain == "arch"
        assert bridges[0].target_domain == "affect"

    def test_bridge_evidence_tracking(self):
        """Verify bridge evidence lists are preserved."""
        service = WebPersistenceService(":memory:")
        service.create_web("test:web:001", "Test")

        bridge = create_bridge(
            source_domain="enviro",
            target_domain="cog",
            bridge_type=BridgeType.FUNCTIONAL,
            warrant_statement="Test warrant"
        )
        bridge.evidence_for = ["paper:001", "paper:002"]
        bridge.evidence_against = ["paper:003"]

        service.save_bridge("test:web:001", bridge)

        bridges = service.get_bridges_for_web("test:web:001")
        assert "paper:001" in bridges[0].evidence_for
        assert "paper:003" in bridges[0].evidence_against


class TestMasterWebAccumulation:
    """Test Case 5: Master web accumulation across papers."""

    def test_create_or_get_master_web(self):
        """Verify master web is created if not exists."""
        service = WebPersistenceService(":memory:")

        master_id = service.create_or_get_master_web()
        assert master_id is not None

        # Second call should return same ID
        master_id2 = service.create_or_get_master_web()
        assert master_id == master_id2

    def test_integrate_paper_adds_new_beliefs(self):
        """Verify integration adds new beliefs to master."""
        service = WebPersistenceService(":memory:")

        # Create paper web
        paper_web = create_neuroarchitecture_web()
        paper_web.add_belief(Belief(
            belief_id="paper1:belief:001",
            content="New finding from paper 1",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.2)
        ))

        report = service.integrate_paper_web(paper_web, "paper:001")

        assert report.n_beliefs_added >= 1
        assert report.paper_id == "paper:001"

    def test_multiple_paper_integration(self):
        """Verify multiple papers can be integrated."""
        service = WebPersistenceService(":memory:")

        # Paper 1
        web1 = create_neuroarchitecture_web()
        web1.add_belief(Belief(
            belief_id="finding:001",
            content="Finding from paper 1",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.6, 0.3, n_observations=5)
        ))

        report1 = service.integrate_paper_web(web1, "paper:001")

        # Paper 2
        web2 = create_neuroarchitecture_web()
        web2.add_belief(Belief(
            belief_id="finding:002",
            content="Finding from paper 2",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.3, n_observations=3)
        ))

        report2 = service.integrate_paper_web(web2, "paper:002")

        # Check statistics
        stats = service.get_statistics(service.get_master_web_id())
        assert stats['n_papers_integrated'] == 2


class TestBeliefMerging:
    """Test Case 6: Belief merging with conflict resolution."""

    def test_merge_new_belief(self):
        """Verify new beliefs are added correctly."""
        service = WebPersistenceService(":memory:")
        master_id = service.create_or_get_master_web()

        belief = Belief(
            belief_id="test:belief:new",
            content="Completely new belief",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.6, 0.3)
        )

        result = service.merge_belief_into_master(master_id, belief, "paper:001")

        assert result.merge_type == "new"
        assert result.new_credence == 0.6

    def test_merge_update_same_content(self):
        """Verify beliefs with same content merge credences."""
        service = WebPersistenceService(":memory:")
        master_id = service.create_or_get_master_web()

        # Add initial belief
        belief1 = Belief(
            belief_id="shared:belief:001",
            content="Nature exposure improves mood",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.6, 0.2, n_observations=10)
        )
        service.merge_belief_into_master(master_id, belief1, "paper:001")

        # Merge same belief from different paper
        belief2 = Belief(
            belief_id="shared:belief:001",
            content="Nature exposure improves mood",  # Same content
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.8, 0.15, n_observations=20)  # Higher credence
        )

        result = service.merge_belief_into_master(master_id, belief2, "paper:002")

        assert result.merge_type == "update"
        assert result.old_credence == 0.6
        # Merged credence should be weighted average
        # (0.6*10 + 0.8*20) / 30 = (6 + 16) / 30 = 0.733...
        assert 0.7 < result.new_credence < 0.8

    def test_merge_conflict_different_content(self):
        """Verify beliefs with different content create conflicts."""
        service = WebPersistenceService(":memory:")
        master_id = service.create_or_get_master_web()

        # Add initial belief
        belief1 = Belief(
            belief_id="conflict:belief:001",
            content="Nature exposure reduces stress through parasympathetic activation",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.2)
        )
        service.merge_belief_into_master(master_id, belief1, "paper:001")

        # Try to merge belief with same ID but very different content
        # (similarity must be < 0.9 to trigger conflict)
        belief2 = Belief(
            belief_id="conflict:belief:001",
            content="Urban noise increases cortisol through amygdala hyperactivation",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.6, 0.3)
        )

        result = service.merge_belief_into_master(master_id, belief2, "paper:002")

        assert result.merge_type == "conflict"
        assert not result.conflict_resolved
        assert "conflict" in result.conflict_resolution.lower()

    def test_credence_merge_formula(self):
        """Verify credence merge uses inverse-variance weighting (Expert Panel 5.3)."""
        service = WebPersistenceService(":memory:")

        # Note: Credence values are clamped to [0.01, 0.99] in __post_init__
        c1 = Credence(value=0.4, uncertainty=0.3, n_observations=10)
        c2 = Credence(value=0.8, uncertainty=0.3, n_observations=10)

        merged = service._merge_credences(c1, c2)

        # Expert Panel 5.3: Inverse-variance weighting
        # Equal uncertainties means equal weights: (0.4 + 0.8) / 2 = 0.6
        assert merged.value == pytest.approx(0.6, rel=1e-6)
        assert merged.n_observations == 20
        # Merged uncertainty should be sqrt(1/(1/0.09 + 1/0.09)) = sqrt(0.045) ~= 0.212
        assert merged.uncertainty == pytest.approx(0.212, rel=0.01)


class TestHistoryTracking:
    """Test Case 7: Coherence and merge history tracking."""

    def test_coherence_history_recorded(self):
        """Verify coherence history is recorded on save."""
        service = WebPersistenceService(":memory:")

        web = create_neuroarchitecture_web()
        service.save_web(web, "test:web:001", "Test")

        history = service.get_coherence_history("test:web:001")

        assert len(history) >= 1
        assert "coherence_score" in history[0]

    def test_merge_log_tracked(self):
        """Verify merge operations are logged."""
        service = WebPersistenceService(":memory:")
        master_id = service.create_or_get_master_web()

        belief = Belief(
            belief_id="logged:belief:001",
            content="Test belief",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.5, 0.3)
        )

        service.merge_belief_into_master(master_id, belief, "paper:001")

        log = service.get_merge_log(master_id)

        assert len(log) >= 1
        assert any(entry['belief_id'] == "logged:belief:001" for entry in log)

    def test_integration_history(self):
        """Verify paper integration is tracked."""
        service = WebPersistenceService(":memory:")

        web = create_neuroarchitecture_web()
        service.integrate_paper_web(web, "paper:tracked:001")

        master_id = service.get_master_web_id()
        history = service.get_integration_history(master_id)

        assert len(history) >= 1
        assert any(entry['paper_id'] == "paper:tracked:001" for entry in history)


class TestStatistics:
    """Test Case 8: Summary statistics and queries."""

    def test_get_statistics(self):
        """Verify statistics are computed correctly."""
        service = WebPersistenceService(":memory:")

        # Create web with multiple beliefs
        web = create_neuroarchitecture_web()
        for i in range(5):
            web.add_belief(Belief(
                belief_id=f"stat:belief:{i:03d}",
                content=f"Statistic test belief {i}",
                level=EpistemicLevel.EMPIRICAL,
                status=BeliefStatus.TENTATIVE,
                credence=Credence(0.5, 0.3)
            ))

        service.save_web(web, "test:stats:001", "Stats Test")

        stats = service.get_statistics("test:stats:001")

        assert stats['n_beliefs'] >= 5
        assert stats['version'] >= 1
        assert 'coherence_score' in stats

    def test_conflict_count_in_statistics(self):
        """Verify conflict count is tracked in statistics."""
        service = WebPersistenceService(":memory:")
        master_id = service.create_or_get_master_web()

        # Create conflict
        b1 = Belief(
            belief_id="conflict:stat:001",
            content="Content version A",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.5, 0.3)
        )
        service.merge_belief_into_master(master_id, b1, "paper:001")

        b2 = Belief(
            belief_id="conflict:stat:001",
            content="Completely different content version B that is quite dissimilar",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.5, 0.3)
        )
        service.merge_belief_into_master(master_id, b2, "paper:002")

        stats = service.get_statistics(master_id)

        assert stats['n_conflicts'] >= 1


class TestIntegrationReport:
    """Test integration report data structure."""

    def test_report_fields(self):
        """Verify integration report has all expected fields."""
        service = WebPersistenceService(":memory:")

        web = create_neuroarchitecture_web()
        web.add_belief(Belief(
            belief_id="report:test:001",
            content="Report test",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.5, 0.3)
        ))

        report = service.integrate_paper_web(web, "paper:report:001")

        assert hasattr(report, 'paper_id')
        assert hasattr(report, 'n_beliefs_added')
        assert hasattr(report, 'n_beliefs_updated')
        assert hasattr(report, 'n_beliefs_conflicted')
        assert hasattr(report, 'coherence_before')
        assert hasattr(report, 'coherence_after')
        assert hasattr(report, 'merge_results')

    def test_report_merge_results_populated(self):
        """Verify merge results list is populated."""
        service = WebPersistenceService(":memory:")

        web = create_neuroarchitecture_web()
        web.add_belief(Belief(
            belief_id="report:merge:001",
            content="Merge result test",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.5, 0.3)
        ))

        report = service.integrate_paper_web(web, "paper:merge:001")

        assert len(report.merge_results) >= 1


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_load_nonexistent_web(self):
        """Verify loading nonexistent web returns None."""
        service = WebPersistenceService(":memory:")

        web, bridges = service.load_web("nonexistent:web:id")

        assert web is None
        assert bridges is None

    def test_load_nonexistent_belief(self):
        """Verify loading nonexistent belief returns None."""
        service = WebPersistenceService(":memory:")
        service.create_web("test:web:001", "Test")

        belief = service.load_belief("nonexistent:belief", "test:web:001")

        assert belief is None

    def test_empty_web_integration(self):
        """Verify empty web can be integrated."""
        service = WebPersistenceService(":memory:")

        web = create_neuroarchitecture_web()
        # Clear all beliefs
        web.beliefs.clear()

        report = service.integrate_paper_web(web, "paper:empty:001")

        assert report.n_beliefs_added == 0

    def test_same_content_similarity_threshold(self):
        """Verify similar (not exact) content is recognized."""
        service = WebPersistenceService(":memory:")

        b1 = Belief(
            belief_id="test:similar:001",
            content="Nature exposure significantly reduces cortisol levels",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.5, 0.3)
        )

        b2 = Belief(
            belief_id="test:similar:001",
            content="Nature exposure significantly reduces cortisol levels.",  # Just added period
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.2)
        )

        assert service._beliefs_same_content(b1, b2) is True


class TestRoundTrip:
    """Test full round-trip serialization."""

    def test_full_round_trip(self):
        """Verify complete web survives round-trip."""
        service = WebPersistenceService(":memory:")

        # Create complex web
        web = create_neuroarchitecture_web()

        belief1 = Belief(
            belief_id="rt:belief:001",
            content="Round trip belief 1",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.2, n_supporting=5, n_contradicting=1, n_observations=6),
            theory_id="ART",
            entrenchment=0.6,
            domain="cog",
            tags=["attention", "test"],
            paper_ids=["paper:001"]
        )

        belief2 = Belief(
            belief_id="rt:belief:002",
            content="Round trip belief 2",
            level=EpistemicLevel.INTERMEDIATE,
            status=BeliefStatus.ESTABLISHED,
            credence=Credence(0.85, 0.1),
            theory_id="SRT"
        )

        web.add_belief(belief1)
        web.add_belief(belief2)

        web.add_constraint(Constraint(
            constraint_id="rt:constraint:001",
            source_id="rt:belief:001",
            target_id="rt:belief:002",
            constraint_type=ConstraintType.SUPPORTS,
            strength=0.75
        ))

        # Save
        service.save_web(web, "rt:web:001", "Round Trip Test")

        # Load
        loaded, _ = service.load_web("rt:web:001")

        # Verify beliefs
        assert "rt:belief:001" in loaded.beliefs
        assert "rt:belief:002" in loaded.beliefs

        loaded_b1 = loaded.beliefs["rt:belief:001"]
        assert loaded_b1.content == "Round trip belief 1"
        assert loaded_b1.credence.value == 0.7
        assert loaded_b1.credence.n_supporting == 5
        assert loaded_b1.theory_id == "ART"
        assert "attention" in loaded_b1.tags

        # Verify constraints
        assert "rt:constraint:001" in loaded.constraints


class TestSprint6CausalDirectionAndScope:
    """
    Sprint 6 Tests: Causal Direction, Scope Conditions, and PRECISION_BOUNDARY.

    Per expert panel recommendations:
    - Pearl: Distinguish correlation from causation
    - Cartwright: Most "contradictions" are scope boundaries
    """

    def test_causal_direction_enum_values(self):
        """Verify CausalDirection enum has all required values."""
        assert CausalDirection.UNKNOWN.value == "unknown"
        assert CausalDirection.CORRELATIONAL.value == "correlational"
        assert CausalDirection.FORWARD.value == "forward"
        assert CausalDirection.REVERSE.value == "reverse"
        assert CausalDirection.BIDIRECTIONAL.value == "bidirectional"
        assert CausalDirection.COMMON_CAUSE.value == "common_cause"
        assert CausalDirection.MEDIATED.value == "mediated"  # Sprint 6 addition

    def test_scope_conditions_creation(self):
        """Verify ScopeConditions can be created with all fields."""
        scope = ScopeConditions(
            population="adults",
            setting="lab",
            duration="acute",
            measurement="self_report",
            geography="Western",
            moderators=["age", "gender"]
        )

        assert scope.population == "adults"
        assert scope.setting == "lab"
        assert scope.duration == "acute"
        assert scope.measurement == "self_report"
        assert scope.geography == "Western"
        assert "age" in scope.moderators

    def test_scope_conditions_to_dict(self):
        """Verify ScopeConditions serializes to dict correctly."""
        scope = ScopeConditions(
            population="children",
            setting="field"
        )

        d = scope.to_dict()

        assert d['population'] == "children"
        assert d['setting'] == "field"
        assert d['duration'] is None
        assert d['moderators'] == []

    def test_scope_conditions_from_dict(self):
        """Verify ScopeConditions deserializes from dict correctly."""
        d = {
            'population': 'clinical',
            'setting': 'simulated',
            'duration': 'chronic',
            'measurement': 'physiological',
            'geography': 'urban',
            'moderators': ['stress_level']
        }

        scope = ScopeConditions.from_dict(d)

        assert scope.population == "clinical"
        assert scope.setting == "simulated"
        assert scope.duration == "chronic"
        assert "stress_level" in scope.moderators

    def test_scopes_overlap_both_none(self):
        """Verify None scopes are treated as universal (overlap with everything)."""
        service = WebPersistenceService(":memory:")

        # Both None = universal scope, should overlap
        assert service._scopes_overlap(None, None) is True

    def test_scopes_overlap_one_none(self):
        """Verify None scope overlaps with any specified scope."""
        service = WebPersistenceService(":memory:")

        scope = ScopeConditions(population="adults", setting="lab")

        assert service._scopes_overlap(None, scope) is True
        assert service._scopes_overlap(scope, None) is True

    def test_scopes_overlap_matching_values(self):
        """Verify scopes with matching values overlap."""
        service = WebPersistenceService(":memory:")

        s1 = ScopeConditions(population="adults", setting="lab")
        s2 = ScopeConditions(population="adults", setting="lab")

        assert service._scopes_overlap(s1, s2) is True

    def test_scopes_no_overlap_different_population(self):
        """Verify scopes with different populations don't overlap when scope_specified."""
        service = WebPersistenceService(":memory:")

        # Panel Fix 3: Must set scope_specified=True for explicit non-overlap
        s1 = ScopeConditions(population="adults", scope_specified=True)
        s2 = ScopeConditions(population="children", scope_specified=True)

        assert service._scopes_overlap(s1, s2) is False

    def test_scopes_no_overlap_different_setting(self):
        """Verify scopes with different settings don't overlap when scope_specified."""
        service = WebPersistenceService(":memory:")

        # Panel Fix 3: Must set scope_specified=True for explicit non-overlap
        s1 = ScopeConditions(setting="lab", scope_specified=True)
        s2 = ScopeConditions(setting="field", scope_specified=True)

        assert service._scopes_overlap(s1, s2) is False

    def test_scopes_overlap_partial_specification(self):
        """Verify scopes overlap when only some fields specified and those match."""
        service = WebPersistenceService(":memory:")

        s1 = ScopeConditions(population="adults")
        s2 = ScopeConditions(population="adults", setting="lab")  # More specific

        # Should overlap because population matches and s1 doesn't specify setting
        assert service._scopes_overlap(s1, s2) is True

    def test_conflict_type_precision_boundary_exists(self):
        """Verify PRECISION_BOUNDARY is in ConflictType enum."""
        assert hasattr(ConflictType, 'PRECISION_BOUNDARY')
        assert ConflictType.PRECISION_BOUNDARY.value == "precision_boundary"

    def test_precision_boundary_detection_same_direction_different_magnitude(self):
        """Verify precision boundary detected for same direction, different magnitude."""
        service = WebPersistenceService(":memory:")

        b1 = Belief(
            belief_id="prec:001",
            content="Nature exposure increases wellbeing",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.6, 0.2)  # Lower credence
        )

        b2 = Belief(
            belief_id="prec:002",
            content="Nature exposure improves wellbeing",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.75, 0.15)  # Higher credence, same direction
        )

        # Same effect direction, credence difference = 0.15 (within 0.1-0.3 range)
        assert service._is_precision_boundary(b1, b2) is True

    def test_precision_boundary_not_detected_opposite_direction(self):
        """Verify precision boundary NOT detected for opposite effect directions."""
        service = WebPersistenceService(":memory:")

        b1 = Belief(
            belief_id="prec:001",
            content="Nature exposure increases stress",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.6, 0.2)
        )

        b2 = Belief(
            belief_id="prec:002",
            content="Nature exposure decreases stress",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.75, 0.15)
        )

        # Opposite directions = not precision boundary
        assert service._is_precision_boundary(b1, b2) is False

    def test_same_effect_direction_both_positive(self):
        """Verify same direction detected for both positive effects."""
        service = WebPersistenceService(":memory:")

        assert service._same_effect_direction(
            "Nature increases wellbeing",
            "Plants improve mood"
        ) is True

    def test_same_effect_direction_both_negative(self):
        """Verify same direction detected for both negative effects."""
        service = WebPersistenceService(":memory:")

        assert service._same_effect_direction(
            "Noise decreases concentration",
            "Crowding reduces cognitive performance"
        ) is True

    def test_same_effect_direction_opposite(self):
        """Verify opposite directions detected correctly."""
        service = WebPersistenceService(":memory:")

        assert service._same_effect_direction(
            "Nature increases wellbeing",
            "Crowding decreases comfort"
        ) is False

    def test_detect_conflict_type_scope_boundary(self):
        """Verify SCOPE_BOUNDARY detected for opposite effects in different scopes."""
        service = WebPersistenceService(":memory:")

        # Panel Fix 3: scope_specified=True for explicit scope boundary detection
        b1 = Belief(
            belief_id="scope:001",
            content="Open offices increase collaboration among adults",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.2),
            scope=ScopeConditions(population="adults", setting="office", scope_specified=True)
        )

        b2 = Belief(
            belief_id="scope:002",
            content="Open offices decrease focus among children",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.2),
            scope=ScopeConditions(population="children", setting="school", scope_specified=True)
        )

        conflict_type = service._detect_conflict_type(b1, b2)

        # Different populations (both scope_specified), so should be SCOPE_BOUNDARY
        assert conflict_type == ConflictType.SCOPE_BOUNDARY

    def test_detect_conflict_type_genuine_contradiction(self):
        """Verify GENUINE_CONTRADICTION detected for opposite effects in same scope."""
        service = WebPersistenceService(":memory:")

        # Panel Fix 3: scope_specified=True for proper genuine contradiction detection
        b1 = Belief(
            belief_id="conflict:001",
            content="Plants increase productivity",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.2),
            scope=ScopeConditions(population="adults", setting="office", scope_specified=True)
        )

        b2 = Belief(
            belief_id="conflict:002",
            content="Plants decrease productivity",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.2),
            scope=ScopeConditions(population="adults", setting="office", scope_specified=True)
        )

        conflict_type = service._detect_conflict_type(b1, b2)

        # Same scope (both scope_specified), opposite effects = genuine contradiction
        assert conflict_type == ConflictType.GENUINE_CONTRADICTION

    def test_detect_conflict_type_precision_boundary(self):
        """Verify PRECISION_BOUNDARY detected for same direction, different magnitude."""
        service = WebPersistenceService(":memory:")

        b1 = Belief(
            belief_id="prec:type:001",
            content="Daylight improves mood significantly",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.65, 0.2)
        )

        b2 = Belief(
            belief_id="prec:type:002",
            content="Daylight enhances mood moderately",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.80, 0.15)  # 0.15 difference
        )

        conflict_type = service._detect_conflict_type(b1, b2)

        assert conflict_type == ConflictType.PRECISION_BOUNDARY

    def test_detect_conflict_type_methodological_divergence(self):
        """Verify METHODOLOGICAL_DIVERGENCE detected for different methods."""
        service = WebPersistenceService(":memory:")

        b1 = Belief(
            belief_id="method:001",
            content="Stress measured by self-report shows increase",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.2)
        )

        b2 = Belief(
            belief_id="method:002",
            content="Stress assessed via cortisol shows stability",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.6, 0.2)
        )

        conflict_type = service._detect_conflict_type(b1, b2)

        assert conflict_type == ConflictType.METHODOLOGICAL_DIVERGENCE

    def test_belief_with_scope_round_trip(self):
        """Verify belief with ScopeConditions survives round-trip persistence."""
        service = WebPersistenceService(":memory:")
        service.create_web("test:web:scope", "Scope Test")

        scope = ScopeConditions(
            population="adults",
            setting="field",
            duration="acute",
            measurement="physiological",
            geography="Western",
            moderators=["stress", "time_of_day"]
        )

        belief = Belief(
            belief_id="scope:rt:001",
            content="Nature walk reduces cortisol",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.75, 0.15),
            scope=scope
        )

        service.save_belief("test:web:scope", belief)
        loaded = service.load_belief("scope:rt:001", "test:web:scope")

        assert loaded is not None
        assert loaded.scope is not None
        assert loaded.scope.population == "adults"
        assert loaded.scope.setting == "field"
        assert loaded.scope.duration == "acute"
        assert "stress" in loaded.scope.moderators

    def test_mediated_requires_mediator_raises_on_none(self):
        """
        Panel Fix 1 (Pearl): MEDIATED causal direction MUST specify mediator.
        Without mediator, we can't reason about blocking/confounding.
        """
        from src.services.web_of_belief import WebOfBelief, Constraint, ConstraintType

        web = WebOfBelief("test:mediated")

        # Add two beliefs to connect
        b1 = Belief(
            belief_id="med:001",
            content="Nature exposure affects mood",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.2)
        )
        b2 = Belief(
            belief_id="med:002",
            content="Mood affects productivity",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.2)
        )
        web.add_belief(b1)
        web.add_belief(b2)

        # Attempt to add MEDIATED constraint without mediator
        constraint = Constraint(
            constraint_id="c:med:001:002",
            source_id="med:001",
            target_id="med:002",
            constraint_type=ConstraintType.SUPPORTS,
            causal_direction=CausalDirection.MEDIATED,
            mediator=None  # This should raise!
        )

        with pytest.raises(ValueError) as exc_info:
            web.add_constraint(constraint)

        assert "MEDIATED causal direction requires mediator" in str(exc_info.value)
        assert "med:001" in str(exc_info.value)

    def test_mediated_with_mediator_succeeds(self):
        """
        Panel Fix 1 (Pearl): MEDIATED with specified mediator should succeed.
        """
        from src.services.web_of_belief import WebOfBelief, Constraint, ConstraintType

        web = WebOfBelief("test:mediated:ok")

        b1 = Belief(
            belief_id="med:ok:001",
            content="Nature exposure affects attention restoration",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.2)
        )
        b2 = Belief(
            belief_id="med:ok:002",
            content="Attention restoration affects productivity",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.2)
        )
        web.add_belief(b1)
        web.add_belief(b2)

        # MEDIATED with mediator specified - should succeed
        constraint = Constraint(
            constraint_id="c:med:ok:001:002",
            source_id="med:ok:001",
            target_id="med:ok:002",
            constraint_type=ConstraintType.SUPPORTS,
            causal_direction=CausalDirection.MEDIATED,
            mediator="attention_restoration"  # Specifies M in A→M→B
        )

        # Should not raise
        web.add_constraint(constraint)
        assert "c:med:ok:001:002" in web.constraints

    def test_non_mediated_directions_allow_none_mediator(self):
        """
        Panel Fix 1 (Pearl): Only MEDIATED requires mediator.
        Other causal directions should allow mediator=None.
        """
        from src.services.web_of_belief import WebOfBelief, Constraint, ConstraintType

        web = WebOfBelief("test:nonmediated")

        b1 = Belief(
            belief_id="nonmed:001",
            content="Nature exposure causes wellbeing",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.2)
        )
        b2 = Belief(
            belief_id="nonmed:002",
            content="Wellbeing measured improves",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.2)
        )
        web.add_belief(b1)
        web.add_belief(b2)

        # Test FORWARD without mediator - should succeed
        constraint_forward = Constraint(
            constraint_id="c:nonmed:forward",
            source_id="nonmed:001",
            target_id="nonmed:002",
            constraint_type=ConstraintType.SUPPORTS,
            causal_direction=CausalDirection.FORWARD,
            mediator=None
        )
        web.add_constraint(constraint_forward)
        assert "c:nonmed:forward" in web.constraints

        # Test CORRELATIONAL without mediator - should succeed
        constraint_corr = Constraint(
            constraint_id="c:nonmed:corr",
            source_id="nonmed:001",
            target_id="nonmed:002",
            constraint_type=ConstraintType.SUPPORTS,
            causal_direction=CausalDirection.CORRELATIONAL,
            mediator=None
        )
        web.add_constraint(constraint_corr)
        assert "c:nonmed:corr" in web.constraints

    def test_scope_specified_field_exists(self):
        """
        Panel Fix 3 (Cartwright): ScopeConditions has scope_specified field.
        """
        scope = ScopeConditions(population="adults")
        assert hasattr(scope, 'scope_specified')
        assert scope.scope_specified is False  # Default is False

    def test_scope_specified_true_explicit(self):
        """
        Panel Fix 3: scope_specified=True means scope was explicitly reported.
        """
        scope = ScopeConditions(
            population="adults",
            setting="lab",
            scope_specified=True
        )
        assert scope.scope_specified is True

    def test_scope_specified_round_trip(self):
        """
        Panel Fix 3: scope_specified survives to_dict/from_dict round trip.
        """
        scope = ScopeConditions(
            population="clinical",
            setting="field",
            scope_specified=True
        )

        d = scope.to_dict()
        assert d['scope_specified'] is True

        restored = ScopeConditions.from_dict(d)
        assert restored.scope_specified is True

    def test_scopes_overlap_both_unspecified(self):
        """
        Panel Fix 3: Two unspecified scopes should overlap (charitable).
        Both unknown = assume possible overlap.
        """
        service = WebPersistenceService(":memory:")

        s1 = ScopeConditions(population="adults", scope_specified=False)
        s2 = ScopeConditions(population="children", scope_specified=False)

        # Both unspecified - be charitable even if values differ
        assert service._scopes_overlap(s1, s2) is True

    def test_scopes_overlap_both_specified_match(self):
        """
        Panel Fix 3: Two specified scopes with matching values overlap.
        """
        service = WebPersistenceService(":memory:")

        s1 = ScopeConditions(population="adults", setting="lab", scope_specified=True)
        s2 = ScopeConditions(population="adults", setting="lab", scope_specified=True)

        assert service._scopes_overlap(s1, s2) is True

    def test_scopes_no_overlap_both_specified_different(self):
        """
        Panel Fix 3: Two specified scopes with different values don't overlap.
        """
        service = WebPersistenceService(":memory:")

        s1 = ScopeConditions(population="adults", scope_specified=True)
        s2 = ScopeConditions(population="children", scope_specified=True)

        assert service._scopes_overlap(s1, s2) is False

    def test_scopes_overlap_one_specified_one_not(self):
        """
        Panel Fix 3: One specified, one not - be charitable (overlap).
        Unknown scope may or may not match, so assume possible overlap.
        """
        service = WebPersistenceService(":memory:")

        s1 = ScopeConditions(population="adults", scope_specified=True)
        s2 = ScopeConditions(population=None, scope_specified=False)  # Unknown

        # Should overlap - unknown could apply to adults
        assert service._scopes_overlap(s1, s2) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
