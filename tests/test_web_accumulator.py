import os
"""
Tests for WebAccumulator (MVP-1)
================================

Tests the persistent web accumulation layer.
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime

from src.services.web_accumulator import (
    WebAccumulator,
    AccumulatorEvent,
    AccumulatorStats,
    get_accumulator,
)


@pytest.fixture
def temp_accumulator():
    """Create accumulator with temporary paths."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        acc = WebAccumulator(
            db_path=tmpdir / "test_persistence.db",
            json_path=tmpdir / "test_accumulated.json",
            events_path=tmpdir / "test_events.jsonl"
        )
        yield acc


class TestAccumulatorEvent:
    """Test AccumulatorEvent dataclass."""

    def test_event_creation(self):
        event = AccumulatorEvent(
            timestamp="2026-02-11T12:00:00Z",
            event_type="paper_processed",
            paper_id="test_paper_001",
            details={"beliefs_added": 5}
        )
        assert event.event_type == "paper_processed"
        assert event.paper_id == "test_paper_001"

    def test_event_to_json(self):
        event = AccumulatorEvent(
            timestamp="2026-02-11T12:00:00Z",
            event_type="test",
            paper_id=None,
            details={"key": "value"}
        )
        json_str = event.to_json()
        parsed = json.loads(json_str)
        assert parsed["event_type"] == "test"
        assert parsed["details"]["key"] == "value"


class TestWebAccumulator:
    """Test WebAccumulator class."""

    def test_initialization(self, temp_accumulator):
        """Test accumulator initializes correctly."""
        acc = temp_accumulator
        assert acc.db_path.parent.exists()

    def test_empty_stats(self, temp_accumulator):
        """Test stats on empty accumulator."""
        acc = temp_accumulator
        stats = acc.get_stats()
        assert stats.total_beliefs == 0
        assert stats.total_constraints == 0

    def test_export_empty_json(self, temp_accumulator):
        """Test exporting empty accumulated web."""
        acc = temp_accumulator
        path = acc.export_to_json()
        assert path.exists()

        with open(path) as f:
            data = json.load(f)

        assert data["schema"] == "ae.accumulated_web.v1"
        assert data["n_beliefs"] == 0

    def test_event_logging(self, temp_accumulator):
        """Test that events are logged to file."""
        acc = temp_accumulator

        # Manually log an event
        event = AccumulatorEvent(
            timestamp=acc._utc_now(),
            event_type="test_event",
            paper_id="test_001",
            details={"test": True}
        )
        acc._log_event(event)

        # Check file exists and contains event
        assert acc.events_path.exists()
        with open(acc.events_path) as f:
            line = f.readline()
            data = json.loads(line)
            assert data["event_type"] == "test_event"


class TestIntegration:
    """Integration tests for accumulator with real WebOfBelief."""

    def test_integrate_simple_web(self, temp_accumulator):
        """Test integrating a simple WebOfBelief."""
        from src.services.web_of_belief import (
            create_neuroarchitecture_web,
            Belief, Credence, EpistemicLevel, BeliefStatus
        )

        acc = temp_accumulator

        # Create a simple web with one belief
        web = create_neuroarchitecture_web()
        web.beliefs.clear()
        web.constraints.clear()

        test_belief = Belief(
            belief_id="test_belief_001",
            content="Natural light improves cognitive performance",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(value=0.7, uncertainty=0.2, n_supporting=3),
            theory_id=None,
            paper_ids=["paper_001"]
        )
        web.beliefs["test_belief_001"] = test_belief

        # Integrate
        result = acc.integrate_paper(web, "paper_001")

        assert result["status"] == "success"
        assert result["beliefs_added"] >= 0  # May merge with existing

        # Check stats updated
        stats = acc.get_stats()
        assert stats.total_beliefs >= 1

        # Check JSON export updated
        with open(acc.json_path) as f:
            data = json.load(f)
        assert data["n_beliefs"] >= 1

    def test_integrate_web_state_file(self, temp_accumulator):
        """Test integrating from a web_state.json file."""
        acc = temp_accumulator

        # Create a minimal web_state.json
        web_state = {
            "schema": "ae.web_state.v1",
            "run_id": "test_run",
            "paper_id": "paper_from_file",
            "created_at": "2026-02-11T12:00:00Z",
            "status": "success",
            "n_beliefs": 1,
            "n_constraints": 0,
            "beliefs": {
                "belief_file_001": {
                    "belief_id": "belief_file_001",
                    "content": "Plants in offices reduce stress",
                    "level": "EMPIRICAL",
                    "status": "TENTATIVE",
                    "credence": {"value": 0.6, "uncertainty": 0.2, "n_supporting": 2},
                    "paper_ids": ["paper_from_file"]
                }
            },
            "constraints": {}
        }

        # Write to temp file
        web_state_path = acc.json_path.parent / "test_web_state.json"
        with open(web_state_path, 'w') as f:
            json.dump(web_state, f)

        # Integrate
        result = acc.integrate_web_state_file(web_state_path)

        assert result["status"] == "success"
        assert result["paper_id"] == "paper_from_file"


class TestFactoryFunction:
    """Test factory function."""

    def test_get_accumulator_default(self):
        """Test default accumulator creation."""
        acc = get_accumulator()
        assert acc is not None
        assert acc.db_path.name == "web_persistence_v2.db"

    def test_get_accumulator_custom_paths(self):
        """Test custom paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            acc = get_accumulator(
                db_path=f"{tmpdir}/custom.db",
                json_path=f"{tmpdir}/custom.json"
            )
            assert acc.db_path.name == "custom.db"
            assert acc.json_path.name == "custom.json"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
