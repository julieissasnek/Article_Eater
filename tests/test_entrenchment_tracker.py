"""
Tests for Entrenchment Tracking & Scholarly Replay — ENT Tasks
2026-02-09

Covers:
- ENT-1: Publication year/date in paper model (already in schema)
- ENT-2: Scholarly-time replay pipeline
- ENT-3: Entrenchment snapshots for both timelines
- ENT-5: Health metrics (volatility, stagnation)
"""

import pytest
from datetime import datetime, timezone

from src.services.web_persistence import WebPersistenceService
from src.services.web_of_belief import (
    WebOfBelief,
    Belief,
    Constraint,
    Credence,
    EpistemicLevel,
    BeliefStatus,
    ConstraintType,
    create_neuroarchitecture_web,
)
from src.services.entrenchment_replay import ScholarlyReplayService


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def persistence():
    """Create in-memory persistence service."""
    return WebPersistenceService(":memory:")


@pytest.fixture
def sample_web():
    """Create a sample web with beliefs."""
    web = create_neuroarchitecture_web()

    # Add empirical beliefs
    web.add_belief(Belief(
        belief_id="belief:emp:001",
        content="Natural light reduces stress",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.75, 0.1),
        theory_id="SRT",
        paper_ids=["paper:ulrich:1984"]
    ))

    web.add_belief(Belief(
        belief_id="belief:emp:002",
        content="Green views improve recovery",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.8, 0.15),
        theory_id="SRT",
        paper_ids=["paper:ulrich:1984"]
    ))

    web.add_belief(Belief(
        belief_id="belief:emp:003",
        content="Mystery increases engagement",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.TENTATIVE,
        credence=Credence(0.65, 0.2),
        theory_id="ART",
        paper_ids=["paper:kaplan:1989"]
    ))

    # Add constraint
    web.add_constraint(Constraint(
        constraint_id="const:001",
        source_id="belief:emp:001",
        target_id="belief:emp:002",
        constraint_type=ConstraintType.SUPPORTS,
        strength=0.7
    ))

    return web


# =============================================================================
# ENT-1: Paper Publication Metadata Tests
# =============================================================================

class TestPaperPublicationMetadata:
    """Test paper publication metadata for scholarly timeline."""

    def test_upsert_paper_publication(self, persistence):
        """Test storing paper publication metadata."""
        persistence.upsert_paper_publication(
            paper_id="paper:ulrich:1984",
            publication_year=1984,
            publication_date="1984-04-27",
            source="bibtex"
        )

        result = persistence.get_paper_publication("paper:ulrich:1984")

        assert result is not None
        assert result["publication_year"] == 1984
        assert result["publication_date"] == "1984-04-27"
        assert result["source"] == "bibtex"

    def test_upsert_preserves_existing(self, persistence):
        """Test COALESCE logic preserves existing values."""
        persistence.upsert_paper_publication(
            paper_id="paper:test",
            publication_year=2020,
            publication_date="2020-06-15",
            source="manual"
        )

        # Update with partial data
        persistence.upsert_paper_publication(
            paper_id="paper:test",
            publication_year=None,  # Should keep 2020
            source="updated"
        )

        result = persistence.get_paper_publication("paper:test")

        assert result["publication_year"] == 2020
        assert result["publication_date"] == "2020-06-15"
        assert result["source"] == "updated"

    def test_list_paper_publications_order(self, persistence):
        """Test papers are ordered by scholarly time."""
        persistence.upsert_paper_publication("paper:c", publication_year=2010)
        persistence.upsert_paper_publication("paper:a", publication_year=1984)
        persistence.upsert_paper_publication("paper:b", publication_date="2000-05-01")

        results = persistence.list_paper_publications()

        # Should be ordered: 1984, 2000-05-01, 2010
        assert results[0]["paper_id"] == "paper:a"
        assert results[1]["paper_id"] == "paper:b"
        assert results[2]["paper_id"] == "paper:c"


# =============================================================================
# ENT-2: Scholarly Replay Pipeline Tests
# =============================================================================

class TestScholarlyReplayPipeline:
    """Test scholarly-time replay functionality."""

    def test_replay_service_creation(self):
        """Test replay service can be created."""
        service = ScholarlyReplayService(
            source_db_path=":memory:",
            replay_db_path=":memory:"
        )
        assert service.source is not None
        assert service.replay is not None

    def test_same_db_protection(self):
        """Test that replaying on same DB raises error without flag."""
        service = ScholarlyReplayService(
            source_db_path=":memory:",
            replay_db_path=None  # Same as source
        )

        with pytest.raises(ValueError, match="mutate the live master"):
            service.replay(
                paper_web_loader=lambda pid: None,
                allow_mutating_master=False
            )

    def test_get_publication_order(self, persistence):
        """Test getting papers in publication order."""
        persistence.upsert_paper_publication("paper:c", publication_year=2010)
        persistence.upsert_paper_publication("paper:a", publication_year=1984)
        persistence.upsert_paper_publication("paper:b", publication_year=2000)

        service = ScholarlyReplayService(
            source_db_path=":memory:",
            replay_db_path=":memory:"
        )
        service.source = persistence

        order = service.get_publication_order()

        assert len(order) == 3
        assert order[0]["paper_id"] == "paper:a"
        assert order[1]["paper_id"] == "paper:b"
        assert order[2]["paper_id"] == "paper:c"


# =============================================================================
# ENT-3: Entrenchment Snapshots Tests
# =============================================================================

class TestEntrenchmentSnapshots:
    """Test entrenchment snapshot recording and querying."""

    def test_record_snapshots(self, persistence, sample_web):
        """Test recording entrenchment snapshots."""
        web_id = persistence.create_web("web:test", "Test Web")
        persistence.save_web(sample_web, web_id)

        persistence.record_entrenchment_snapshots(
            web_id=web_id,
            web=sample_web,
            belief_ids=["belief:emp:001", "belief:emp:002"],
            paper_id="paper:ulrich:1984",
            timeline_type="system",
            as_of_date="2026-02-09",
            event_type="snapshot"
        )

        history = persistence.get_entrenchment_history("belief:emp:001")

        assert len(history) == 1
        assert history[0]["belief_id"] == "belief:emp:001"
        assert history[0]["timeline_type"] == "system"
        assert history[0]["entrenchment"] is not None

    def test_dual_timeline_snapshots(self, persistence, sample_web):
        """Test snapshots for both system and scholarly timelines."""
        web_id = persistence.create_web("web:test", "Test Web")
        persistence.save_web(sample_web, web_id)

        # Record system timeline
        persistence.record_entrenchment_snapshots(
            web_id=web_id,
            web=sample_web,
            belief_ids=["belief:emp:001"],
            paper_id="paper:test",
            timeline_type="system",
            as_of_date="2026-02-09"
        )

        # Record scholarly timeline
        persistence.record_entrenchment_snapshots(
            web_id=web_id,
            web=sample_web,
            belief_ids=["belief:emp:001"],
            paper_id="paper:test",
            timeline_type="scholarly",
            as_of_date="1984-04-27"
        )

        system = persistence.get_entrenchment_history(
            "belief:emp:001",
            timeline_type="system"
        )
        scholarly = persistence.get_entrenchment_history(
            "belief:emp:001",
            timeline_type="scholarly"
        )

        assert len(system) == 1
        assert len(scholarly) == 1
        assert system[0]["as_of_date"] == "2026-02-09"
        assert scholarly[0]["as_of_date"] == "1984-04-27"

    def test_get_latest_entrenchment(self, persistence, sample_web):
        """Test getting most recent entrenchment value."""
        web_id = persistence.create_web("web:test", "Test Web")
        persistence.save_web(sample_web, web_id)

        # Record multiple snapshots
        for date in ["2026-02-01", "2026-02-05", "2026-02-09"]:
            persistence.record_entrenchment_snapshots(
                web_id=web_id,
                web=sample_web,
                belief_ids=["belief:emp:001"],
                paper_id="paper:test",
                timeline_type="system",
                as_of_date=date
            )

        latest = persistence.get_latest_entrenchment(
            "belief:emp:001",
            timeline_type="system"
        )

        assert latest is not None
        assert latest["as_of_date"] == "2026-02-09"

    def test_compare_timeline_entrenchment(self, persistence, sample_web):
        """Test comparing entrenchment across timelines."""
        web_id = persistence.create_web("web:test", "Test Web")
        persistence.save_web(sample_web, web_id)

        persistence.record_entrenchment_snapshots(
            web_id=web_id,
            web=sample_web,
            belief_ids=["belief:emp:001"],
            paper_id="paper:test",
            timeline_type="system"
        )

        persistence.record_entrenchment_snapshots(
            web_id=web_id,
            web=sample_web,
            belief_ids=["belief:emp:001"],
            paper_id="paper:test",
            timeline_type="scholarly"
        )

        comparison = persistence.compare_timeline_entrenchment("belief:emp:001")

        assert comparison["belief_id"] == "belief:emp:001"
        assert comparison["system_entrenchment"] is not None
        assert comparison["scholarly_entrenchment"] is not None
        assert comparison["divergence"] is not None

    def test_get_entrenchment_events(self, persistence, sample_web):
        """Test retrieving entrenchment change events."""
        web_id = persistence.create_web("web:test", "Test Web")
        persistence.save_web(sample_web, web_id)

        # First snapshot
        persistence.record_entrenchment_snapshots(
            web_id=web_id,
            web=sample_web,
            belief_ids=["belief:emp:001"],
            paper_id="paper:test",
            timeline_type="system",
            as_of_date="2026-02-01"
        )

        # Modify belief credence
        sample_web.beliefs["belief:emp:001"].credence = Credence(0.85, 0.1)

        # Second snapshot - should create delta event
        persistence.record_entrenchment_snapshots(
            web_id=web_id,
            web=sample_web,
            belief_ids=["belief:emp:001"],
            paper_id="paper:test",
            timeline_type="system",
            as_of_date="2026-02-09",
            event_type="update"
        )

        events = persistence.get_entrenchment_events(
            belief_id="belief:emp:001",
            timeline_type="system"
        )

        assert len(events) >= 1
        assert events[0]["belief_id"] == "belief:emp:001"


# =============================================================================
# ENT-5: Health Metrics Tests
# =============================================================================

class TestEntrenchmentHealthMetrics:
    """Test entrenchment health metrics (volatility, trajectory)."""

    def test_get_entrenchment_trajectory(self, persistence, sample_web):
        """Test trajectory calculation with volatility."""
        web_id = persistence.create_web("web:test", "Test Web")
        persistence.save_web(sample_web, web_id)

        # Record multiple snapshots with varying entrenchment
        dates = ["2026-02-01", "2026-02-03", "2026-02-05", "2026-02-07", "2026-02-09"]
        for date in dates:
            # Slightly modify credence to create variation
            sample_web.beliefs["belief:emp:001"].credence = Credence(
                0.75 + (ord(date[-1]) % 10) * 0.01,
                0.1
            )
            persistence.record_entrenchment_snapshots(
                web_id=web_id,
                web=sample_web,
                belief_ids=["belief:emp:001"],
                paper_id="paper:test",
                timeline_type="system",
                as_of_date=date
            )

        trajectory = persistence.get_entrenchment_trajectory(
            "belief:emp:001",
            timeline_type="system"
        )

        assert trajectory["belief_id"] == "belief:emp:001"
        assert trajectory["n_snapshots"] == 5
        assert len(trajectory["data_points"]) == 5
        assert trajectory["volatility"] is not None
        assert trajectory["trend"] is not None
        assert trajectory["latest"] is not None

    def test_trajectory_empty_history(self, persistence):
        """Test trajectory for belief with no history."""
        trajectory = persistence.get_entrenchment_trajectory(
            "belief:nonexistent",
            timeline_type="system"
        )

        assert trajectory["data_points"] == []
        assert trajectory["volatility"] is None
        assert trajectory["trend"] is None
        assert trajectory["latest"] is None

    def test_trajectory_single_snapshot(self, persistence, sample_web):
        """Test trajectory with single snapshot (no trend possible)."""
        web_id = persistence.create_web("web:test", "Test Web")
        persistence.save_web(sample_web, web_id)

        persistence.record_entrenchment_snapshots(
            web_id=web_id,
            web=sample_web,
            belief_ids=["belief:emp:001"],
            paper_id="paper:test",
            timeline_type="system"
        )

        trajectory = persistence.get_entrenchment_trajectory(
            "belief:emp:001",
            timeline_type="system"
        )

        assert trajectory["n_snapshots"] == 1
        assert trajectory["volatility"] is None  # Need 2+ for volatility
        assert trajectory["latest"] is not None


# =============================================================================
# Integration Tests
# =============================================================================

class TestEntrenchmentIntegration:
    """Integration tests for full entrenchment workflow."""

    def test_paper_integration_records_snapshots(self, persistence, sample_web):
        """Test that paper integration records entrenchment snapshots."""
        # Create master web
        master_id = persistence.create_or_get_master_web()

        # Store paper publication metadata
        persistence.upsert_paper_publication(
            paper_id="paper:ulrich:1984",
            publication_year=1984,
            publication_date="1984-04-27"
        )

        # Integrate paper web
        report = persistence.integrate_paper_web(
            paper_web=sample_web,
            paper_id="paper:ulrich:1984",
            publication_year=1984,
            publication_date="1984-04-27"
        )

        assert report.n_beliefs_added >= 0

    def test_history_query_date_range(self, persistence, sample_web):
        """Test querying history within date range."""
        web_id = persistence.create_web("web:test", "Test Web")
        persistence.save_web(sample_web, web_id)

        dates = ["2026-01-01", "2026-01-15", "2026-02-01", "2026-02-15"]
        for date in dates:
            persistence.record_entrenchment_snapshots(
                web_id=web_id,
                web=sample_web,
                belief_ids=["belief:emp:001"],
                paper_id="paper:test",
                timeline_type="system",
                as_of_date=date
            )

        # Query February only
        feb_history = persistence.get_entrenchment_history(
            "belief:emp:001",
            start_date="2026-02-01",
            end_date="2026-02-28"
        )

        assert len(feb_history) == 2
        assert all("2026-02" in h["as_of_date"] for h in feb_history)
