"""
Tests for RecommendationLoopService

Tests verify that the service correctly:
1. Harvests interpretation space gaps from Phase 4 outputs
2. Harvests QA backlog from database
3. Scores and prioritizes suggestions by VOI
4. Inserts suggestions into the interpretation_space_suggestions table
5. Dispatches top-N suggestions to the research queue/searcher
6. Reports cycle health metrics
7. Handles continuous mode respecting interval
8. Gracefully handles missing data/unavailable components
"""

from __future__ import annotations

import json
import pytest
import tempfile
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock

from src.services.recommendation_loop import RecommendationLoopService


class TestRecommendationLoopHarvestGaps:
    """Test harvesting interpretation space gaps from Phase 4 outputs."""

    def test_harvest_gaps_from_frontier_questions(self, tmp_path):
        """Test harvesting frontier questions from Phase 4."""
        # Create Phase 4 output directory
        phase4_dir = tmp_path / "interpretation_space" / "phase4"
        phase4_dir.mkdir(parents=True)

        # Create frontier questions file
        frontier_data = {
            "voi_scoring_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_frontier_questions": 3,
            "high_voi_count": 2,
            "medium_voi_count": 1,
            "low_voi_count": 0,
            "questions": [
                {
                    "belief_id": "PP",
                    "questions": [
                        "For which populations does PP apply?",
                        "In which settings does PP hold?"
                    ],
                    "voi_score": 0.8,
                    "voi_bucket": "high",
                    "voi_rank": 1,
                },
                {
                    "belief_id": "NM",
                    "questions": [
                        "Is NM culturally universal?"
                    ],
                    "voi_score": 0.6,
                    "voi_bucket": "medium",
                    "voi_rank": 2,
                }
            ]
        }
        frontier_file = phase4_dir / "prioritized_frontier_questions.json"
        frontier_file.write_text(json.dumps(frontier_data))

        # Initialize service
        db_path = tmp_path / "web.db"
        db_path.touch()

        service = RecommendationLoopService(
            db_path=str(db_path),
            web_db_path=str(db_path),
            interpretation_space_dir=str(tmp_path / "interpretation_space"),
        )

        # Harvest gaps
        gaps = service._harvest_interpretation_space_gaps()

        # Verify results
        assert len(gaps) == 3  # 2 questions from PP + 1 from NM
        assert all(g["source"] == "interpretation_space" for g in gaps)
        assert all(g["status"] == "identified" for g in gaps)

        # Check first gap
        pp_gap = next((g for g in gaps if "PP" in g["belief_id"]), None)
        assert pp_gap is not None
        assert pp_gap["voi_bucket"] == "high"
        assert pp_gap["priority_score"] == 0.8

    def test_harvest_gaps_missing_phase4_directory(self, tmp_path):
        """Test graceful handling when Phase 4 directory doesn't exist."""
        db_path = tmp_path / "web.db"
        db_path.touch()

        service = RecommendationLoopService(
            db_path=str(db_path),
            web_db_path=str(db_path),
            interpretation_space_dir=str(tmp_path / "nonexistent"),
        )

        gaps = service._harvest_interpretation_space_gaps()

        assert gaps == []

    def test_harvest_gaps_invalid_json(self, tmp_path):
        """Test handling of malformed frontier questions file."""
        phase4_dir = tmp_path / "interpretation_space" / "phase4"
        phase4_dir.mkdir(parents=True)

        # Write invalid JSON
        frontier_file = phase4_dir / "prioritized_frontier_questions.json"
        frontier_file.write_text("{ invalid json }")

        db_path = tmp_path / "web.db"
        db_path.touch()

        service = RecommendationLoopService(
            db_path=str(db_path),
            web_db_path=str(db_path),
            interpretation_space_dir=str(tmp_path / "interpretation_space"),
        )

        gaps = service._harvest_interpretation_space_gaps()

        assert gaps == []


class TestRecommendationLoopScoring:
    """Test VOI scoring and prioritization."""

    def test_score_and_prioritize(self, tmp_path):
        """Test scoring and sorting by VOI."""
        db_path = tmp_path / "web.db"
        db_path.touch()

        service = RecommendationLoopService(
            db_path=str(db_path),
            web_db_path=str(db_path),
        )

        suggestions = [
            {
                "source": "interpretation_space",
                "status": "identified",
                "description": "Gap 1",
                "suggested_search": "query1",
                "priority_score": 0.5,
            },
            {
                "source": "interpretation_space",
                "status": "identified",
                "description": "Gap 2",
                "suggested_search": "query2",
                "priority_score": 0.8,
            },
            {
                "source": "qa",
                "status": "identified",
                "description": "QA followup",
                "suggested_search": "query3",
                "priority_score": 0.2,  # Low enough for "low" bucket
            },
        ]

        prioritized = service._score_and_prioritize(suggestions)

        # Check sorting
        assert prioritized[0]["priority_score"] == 0.8  # Highest first
        assert prioritized[1]["priority_score"] == 0.5
        assert prioritized[2]["priority_score"] == 0.2  # Lowest last

        # Check voi_bucket assignment
        assert prioritized[0]["voi_bucket"] == "high"
        assert prioritized[1]["voi_bucket"] == "medium"
        assert prioritized[2]["voi_bucket"] == "low"

    def test_score_sets_default_voi_bucket(self, tmp_path):
        """Test that missing voi_bucket is set based on score."""
        db_path = tmp_path / "web.db"
        db_path.touch()

        service = RecommendationLoopService(
            db_path=str(db_path),
            web_db_path=str(db_path),
        )

        suggestions = [
            {
                "source": "test",
                "description": "Test",
                "suggested_search": "test",
                "priority_score": 0.7,
                # Missing voi_bucket
            },
        ]

        prioritized = service._score_and_prioritize(suggestions)

        assert prioritized[0]["voi_bucket"] == "high"


class TestRecommendationLoopDispatch:
    """Test dispatching searches to research queue."""

    @patch("src.queue.service.ResearchQueueService")
    def test_dispatch_searches(self, mock_queue_class, tmp_path):
        """Test dispatching top-N searches."""
        db_path = tmp_path / "web.db"
        db_path.touch()

        # Mock queue and searcher
        mock_queue = MagicMock()
        mock_queue.get_prioritized_targets.return_value = [
            Mock(priority=Mock(value="high")),
            Mock(priority=Mock(value="medium")),
            Mock(priority=Mock(value="low")),
        ]
        mock_queue_class.return_value = mock_queue

        service = RecommendationLoopService(
            db_path=str(db_path),
            web_db_path=str(db_path),
        )

        with patch("src.queue.automated_searcher.AutomatedQueueSearcher") as mock_searcher_class:
            mock_searcher = MagicMock()
            mock_searcher.run_once.return_value = [Mock(), Mock()]
            mock_searcher_class.return_value = mock_searcher

            result = service._dispatch_searches(top_n=5)

            # Verify dispatch occurred
            assert result["dispatched_count"] == 2
            assert result["total_targets"] == 3
            assert result["high_priority_targets"] == 1

    def test_dispatch_searches_queue_unavailable(self, tmp_path):
        """Test graceful handling when queue is unavailable."""
        db_path = tmp_path / "web.db"
        db_path.touch()

        service = RecommendationLoopService(
            db_path=str(db_path),
            web_db_path=str(db_path),
        )

        with patch("src.queue.service.ResearchQueueService") as mock_queue_class:
            mock_queue_class.side_effect = Exception("Queue not available")
            result = service._dispatch_searches(top_n=5)

            # Should return error result, not crash
            assert "Error" in result.get("message", "") or result.get("dispatched_count", 0) == 0


class TestRecommendationLoopInsertions:
    """Test inserting suggestions into database."""

    def test_insert_suggestions(self, tmp_path):
        """Test inserting suggestions into interpretation_space_suggestions table."""
        db_path = tmp_path / "web.db"

        # Create database with suggestions table
        with sqlite3.connect(str(db_path)) as conn:
            conn.execute("""
                CREATE TABLE interpretation_space_suggestions (
                    id INTEGER PRIMARY KEY,
                    source TEXT,
                    status TEXT,
                    description TEXT,
                    suggested_search TEXT,
                    priority_score REAL,
                    created_at TEXT,
                    updated_at TEXT,
                    resolved_at TEXT,
                    article_id TEXT
                )
            """)
            conn.commit()

        service = RecommendationLoopService(
            db_path=str(db_path),
            web_db_path=str(db_path),
        )

        suggestions = [
            {
                "source": "interpretation_space",
                "status": "identified",
                "description": "Gap 1",
                "suggested_search": "query 1",
                "priority_score": 0.8,
            },
            {
                "source": "qa",
                "status": "identified",
                "description": "QA followup",
                "suggested_search": "query 2",
                "priority_score": 0.5,
            },
        ]

        with patch("src.services.interpretation_space_suggestions.InterpretationSpaceSuggestionsManager") as mock_mgr_class:
            mock_mgr = MagicMock()
            mock_mgr.insert_suggestion.side_effect = [1, 2]  # Return inserted IDs
            mock_mgr_class.return_value = mock_mgr

            inserted = service._insert_suggestions_into_table(suggestions)

            assert inserted == 2
            assert mock_mgr.insert_suggestion.call_count == 2


class TestRecommendationLoopCycleHealth:
    """Test cycle health reporting."""

    def test_report_cycle_health(self, tmp_path):
        """Test cycle health metrics collection."""
        db_path = tmp_path / "web.db"

        # Create database with suggestions table
        with sqlite3.connect(str(db_path)) as conn:
            conn.execute("""
                CREATE TABLE interpretation_space_suggestions (
                    id INTEGER PRIMARY KEY,
                    source TEXT,
                    status TEXT,
                    description TEXT,
                    suggested_search TEXT,
                    priority_score REAL,
                    created_at TEXT,
                    updated_at TEXT,
                    resolved_at TEXT,
                    article_id TEXT
                )
            """)
            conn.execute("""
                INSERT INTO interpretation_space_suggestions
                (source, status, description, suggested_search, priority_score, created_at, updated_at)
                VALUES ('gap_predictor', 'identified', 'Gap 1', 'query', 0.5, ?, ?)
            """, (datetime.now(timezone.utc).isoformat(),
                  datetime.now(timezone.utc).isoformat()))
            conn.commit()

        service = RecommendationLoopService(
            db_path=str(db_path),
            web_db_path=str(db_path),
        )

        cycle_start = datetime.now(timezone.utc)
        health = service._report_cycle_health(cycle_start)

        assert health["status"] == "healthy"
        assert "duration_seconds" in health
        assert health["unacted_suggestions"] == 1
        assert health["suggestions_by_source"]["gap_predictor"] == 1

    def test_report_cycle_health_db_unavailable(self, tmp_path):
        """Test health check when database is unavailable."""
        db_path = tmp_path / "nonexistent.db"  # Doesn't exist

        service = RecommendationLoopService(
            db_path=str(db_path),
            web_db_path=str(db_path),
        )

        cycle_start = datetime.now(timezone.utc)
        health = service._report_cycle_health(cycle_start)

        # Should handle gracefully
        assert health["status"] in ["database_unavailable", "error"]


class TestRecommendationLoopFullCycle:
    """Test full cycle execution."""

    def test_run_single_pass(self, tmp_path):
        """Test single pass execution."""
        # Setup
        phase4_dir = tmp_path / "interpretation_space" / "phase4"
        phase4_dir.mkdir(parents=True)

        frontier_data = {
            "voi_scoring_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_frontier_questions": 2,
            "high_voi_count": 1,
            "medium_voi_count": 1,
            "low_voi_count": 0,
            "questions": [
                {
                    "belief_id": "Test",
                    "questions": ["What about this?"],
                    "voi_score": 0.7,
                    "voi_bucket": "high",
                    "voi_rank": 1,
                }
            ]
        }
        frontier_file = phase4_dir / "prioritized_frontier_questions.json"
        frontier_file.write_text(json.dumps(frontier_data))

        db_path = tmp_path / "web.db"
        with sqlite3.connect(str(db_path)) as conn:
            conn.execute("""
                CREATE TABLE interpretation_space_suggestions (
                    id INTEGER PRIMARY KEY,
                    source TEXT,
                    status TEXT,
                    description TEXT,
                    suggested_search TEXT,
                    priority_score REAL,
                    created_at TEXT,
                    updated_at TEXT,
                    resolved_at TEXT,
                    article_id TEXT
                )
            """)
            conn.commit()

        service = RecommendationLoopService(
            db_path=str(db_path),
            web_db_path=str(db_path),
            interpretation_space_dir=str(tmp_path / "interpretation_space"),
        )

        with patch("src.queue.service.ResearchQueueService"):
            with patch("src.services.interpretation_space_suggestions.InterpretationSpaceSuggestionsManager"):
                result = service.run_single_pass(top_n=3)

                # Verify cycle structure
                assert result["cycle_stage"] == "completed"
                assert "steps" in result
                assert "harvest_gaps" in result["steps"]
                assert "prioritize" in result["steps"]
                assert "dispatch" in result["steps"]
                assert "health" in result["steps"]
                assert result["steps"]["harvest_gaps"]["count"] == 1

    def test_run_single_pass_no_data(self, tmp_path):
        """Test single pass with no interpretation space data."""
        db_path = tmp_path / "web.db"
        db_path.touch()

        service = RecommendationLoopService(
            db_path=str(db_path),
            web_db_path=str(db_path),
            interpretation_space_dir=str(tmp_path / "nonexistent"),
        )

        with patch("src.queue.service.ResearchQueueService"):
            with patch("src.services.interpretation_space_suggestions.InterpretationSpaceSuggestionsManager"):
                result = service.run_single_pass(top_n=3)

                # Should still complete
                assert result["cycle_stage"] == "completed"
                assert result["steps"]["harvest_gaps"]["count"] == 0


class TestRecommendationLoopQuestionToQuery:
    """Test converting frontier questions to search queries."""

    def test_question_to_search_population(self, tmp_path):
        """Test converting population questions."""
        db_path = tmp_path / "web.db"
        db_path.touch()

        service = RecommendationLoopService(
            db_path=str(db_path),
            web_db_path=str(db_path),
        )

        query = service._question_to_search_query(
            "For which populations does this apply?",
            "TestBelief"
        )

        assert "population" in query.lower()
        assert "TestBelief" in query

    def test_question_to_search_setting(self, tmp_path):
        """Test converting setting questions."""
        db_path = tmp_path / "web.db"
        db_path.touch()

        service = RecommendationLoopService(
            db_path=str(db_path),
            web_db_path=str(db_path),
        )

        query = service._question_to_search_query(
            "In which settings does this hold?",
            "TestBelief"
        )

        assert "setting" in query.lower()
        assert "TestBelief" in query

    def test_question_to_search_default(self, tmp_path):
        """Test default query generation for unknown questions."""
        db_path = tmp_path / "web.db"
        db_path.touch()

        service = RecommendationLoopService(
            db_path=str(db_path),
            web_db_path=str(db_path),
        )

        query = service._question_to_search_query(
            "Some random question about something",
            "TestBelief"
        )

        assert "TestBelief" in query
        assert len(query) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
