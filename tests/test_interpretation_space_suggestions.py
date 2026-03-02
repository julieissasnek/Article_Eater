"""
Tests for interpretation_space_suggestions table and InterpretationSpaceSuggestionsManager.

Tests verify:
1. Table gets created during migrations
2. QA follow-ups populate the table correctly
3. Gap predictor suggestions populate the table correctly
4. SearchSuggestionTracker can query the populated table
5. Status updates and staleness tracking work
"""

import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path

from src.services.db_migrations import MigrationManager
from src.services.interpretation_space_suggestions import (
    InterpretationSpaceSuggestionsManager,
    SuggestionRecord,
)
from src.services.overseer_management import SearchSuggestionTracker


def _create_test_schema(db_path: str):
    """Create the interpretation_space_suggestions table for testing."""
    conn = sqlite3.connect(db_path)
    try:
        from src.services.db_migrations import _m011_create_interpretation_space_suggestions
        cursor = conn.cursor()
        _m011_create_interpretation_space_suggestions(cursor)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


class TestInterpretationSpaceSuggestionsTable(unittest.TestCase):
    """Test table creation and schema."""

    def setUp(self):
        """Create a temporary test database."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()

    def tearDown(self):
        """Clean up temporary database."""
        Path(self.db_path).unlink(missing_ok=True)

    def test_migration_creates_table(self):
        """Test that migration 11 creates the interpretation_space_suggestions table."""
        conn = sqlite3.connect(self.db_path)
        mgr = MigrationManager(conn)
        # Only run the specific migration we care about
        try:
            from src.services.db_migrations import _m011_create_interpretation_space_suggestions
            cursor = conn.cursor()
            _m011_create_interpretation_space_suggestions(cursor)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

        # Verify table exists
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='interpretation_space_suggestions'
        """)
        result = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(result, "interpretation_space_suggestions table was not created")

    def test_table_has_required_columns(self):
        """Test that table has all required columns."""
        _create_test_schema(self.db_path)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(interpretation_space_suggestions)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        conn.close()

        required_columns = {
            'id': 'INTEGER',
            'source': 'TEXT',
            'status': 'TEXT',
            'description': 'TEXT',
            'suggested_search': 'TEXT',
            'priority_score': 'REAL',
            'created_at': 'TEXT',
            'updated_at': 'TEXT',
            'resolved_at': 'TEXT',
            'article_id': 'TEXT',
        }

        for col_name, col_type in required_columns.items():
            self.assertIn(col_name, columns, f"Column {col_name} not found in table")

    def test_table_indices_created(self):
        """Test that required indices are created."""
        _create_test_schema(self.db_path)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index' AND tbl_name='interpretation_space_suggestions'
        """)
        indices = {row[0] for row in cursor.fetchall()}
        conn.close()

        expected_indices = {
            'idx_interp_sugg_status',
            'idx_interp_sugg_source',
            'idx_interp_sugg_created_at',
            'idx_interp_sugg_priority',
            'idx_interp_sugg_status_source',
        }

        for idx in expected_indices:
            self.assertIn(idx, indices, f"Index {idx} not created")


class TestInterpretationSpaceSuggestionsManager(unittest.TestCase):
    """Test InterpretationSpaceSuggestionsManager operations."""

    def setUp(self):
        """Create a temporary test database with migrations applied."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()

        # Apply the schema
        _create_test_schema(self.db_path)

        self.manager = InterpretationSpaceSuggestionsManager(self.db_path)

    def tearDown(self):
        """Clean up temporary database."""
        Path(self.db_path).unlink(missing_ok=True)

    def test_insert_single_suggestion(self):
        """Test inserting a single suggestion record."""
        record = SuggestionRecord(
            source='qa',
            status='proposed',
            description='Follow-up from QA handler',
            suggested_search='cognitive load theory',
            priority_score=0.6,
        )

        suggestion_id = self.manager.insert_suggestion(record)
        self.assertIsNotNone(suggestion_id)
        self.assertGreater(suggestion_id, 0)

        # Verify it was inserted
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM interpretation_space_suggestions WHERE id = ?", (suggestion_id,))
        row = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row['source'], 'qa')
        self.assertEqual(row['status'], 'proposed')
        self.assertEqual(row['suggested_search'], 'cognitive load theory')

    def test_insert_qa_followups(self):
        """Test inserting QA follow-up suggestions."""
        followups = [
            "What evidence supports this design approach?",
            "How does this affect cultural considerations?",
            "What are the boundary conditions?",
        ]

        count = self.manager.insert_qa_followups(followups, priority_score=0.6)
        self.assertEqual(count, 3)

        # Verify all were inserted
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM interpretation_space_suggestions WHERE source = 'qa'")
        total = cursor.fetchone()[0]
        conn.close()

        self.assertEqual(total, 3)

    def test_insert_gap_predictor_suggestions(self):
        """Test inserting gap predictor suggestions."""
        gaps = [
            {
                'gap_id': 'gap_001',
                'description': 'Missing evidence for boundary conditions',
                'suggested_search': 'boundary conditions cognitive load',
                'voi_score': 0.75,
            },
            {
                'gap_id': 'gap_002',
                'description': 'Mechanism unclear',
                'suggested_search': 'neural mechanism cognitive control',
                'voi_score': 0.68,
            },
        ]

        count = self.manager.insert_gap_predictor_suggestions(gaps)
        self.assertEqual(count, 2)

        # Verify all were inserted with correct source
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM interpretation_space_suggestions WHERE source = 'gap_predictor'")
        total = cursor.fetchone()[0]
        conn.close()

        self.assertEqual(total, 2)

    def test_insert_argumentation_suggestions(self):
        """Test inserting argumentation layer suggestions."""
        suggestions = [
            {
                'description': 'Test robustness across cultures',
                'search_query': 'cultural robustness cross-cultural',
            },
            {
                'description': 'Examine mechanisms in children',
                'search_query': 'developmental mechanisms children',
            },
        ]

        count = self.manager.insert_argumentation_suggestions(suggestions)
        self.assertEqual(count, 2)

    def test_update_suggestion_status(self):
        """Test updating suggestion status."""
        # Insert a suggestion
        record = SuggestionRecord(
            source='qa',
            status='proposed',
            description='Test suggestion',
            suggested_search='test query',
            priority_score=0.5,
        )
        suggestion_id = self.manager.insert_suggestion(record)

        # Update status to searching
        updated = self.manager.update_suggestion_status(suggestion_id, 'searching')
        self.assertTrue(updated)

        # Verify status changed
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM interpretation_space_suggestions WHERE id = ?", (suggestion_id,))
        status = cursor.fetchone()[0]
        conn.close()

        self.assertEqual(status, 'searching')

    def test_update_suggestion_resolved_with_article(self):
        """Test marking suggestion as resolved with article ID."""
        record = SuggestionRecord(
            source='qa',
            status='proposed',
            description='Test suggestion',
            suggested_search='test query',
            priority_score=0.5,
        )
        suggestion_id = self.manager.insert_suggestion(record)

        # Mark as resolved with article
        updated = self.manager.update_suggestion_status(
            suggestion_id, 'resolved', article_id='arxiv_12345'
        )
        self.assertTrue(updated)

        # Verify resolved_at was set
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT status, resolved_at, article_id FROM interpretation_space_suggestions WHERE id = ?",
                      (suggestion_id,))
        row = cursor.fetchone()
        conn.close()

        self.assertEqual(row['status'], 'resolved')
        self.assertIsNotNone(row['resolved_at'])
        self.assertEqual(row['article_id'], 'arxiv_12345')

    def test_get_unacted_suggestions_count(self):
        """Test getting count of unacted suggestions."""
        # Insert mix of statuses
        self.manager.insert_qa_followups(['q1', 'q2'], priority_score=0.6)  # 2 proposed
        self.manager.insert_gap_predictor_suggestions([
            {'gap_id': 'g1', 'description': 'd1', 'suggested_search': 's1', 'voi_score': 0.5}
        ])  # 1 identified

        # Insert resolved one
        record = SuggestionRecord(
            source='qa',
            status='resolved',
            description='Resolved',
            suggested_search='query',
            priority_score=0.5,
        )
        self.manager.insert_suggestion(record)

        count = self.manager.get_unacted_suggestions_count()
        self.assertEqual(count, 3, "Should count 2 proposed + 1 identified = 3 unacted")

    def test_get_suggestions_by_source(self):
        """Test filtering suggestions by source."""
        self.manager.insert_qa_followups(['q1', 'q2'], priority_score=0.6)
        self.manager.insert_gap_predictor_suggestions([
            {'gap_id': 'g1', 'description': 'd1', 'suggested_search': 's1', 'voi_score': 0.5}
        ])

        qa_suggestions = self.manager.get_suggestions_by_source('qa')
        gap_suggestions = self.manager.get_suggestions_by_source('gap_predictor')

        self.assertEqual(len(qa_suggestions), 2)
        self.assertEqual(len(gap_suggestions), 1)

    def test_get_suggestions_by_source_and_status(self):
        """Test filtering by both source and status."""
        self.manager.insert_qa_followups(['q1', 'q2'], priority_score=0.6)

        # Mark one as searching
        record = SuggestionRecord(
            source='qa',
            status='proposed',
            description='Test',
            suggested_search='query',
            priority_score=0.5,
        )
        record_id = self.manager.insert_suggestion(record)
        self.manager.update_suggestion_status(record_id, 'searching')

        proposed = self.manager.get_suggestions_by_source('qa', status='proposed')
        searching = self.manager.get_suggestions_by_source('qa', status='searching')

        # Original 2 from insert_qa_followups + 1 new record = 3 total
        # 2 proposed, 1 searching
        self.assertEqual(len(proposed), 2)
        self.assertEqual(len(searching), 1)

    def test_get_stale_suggestions(self):
        """Test identifying stale suggestions."""
        now = datetime.now(timezone.utc)
        old_time = (now - timedelta(days=10)).isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Manually insert an old suggestion
        cursor.execute("""
            INSERT INTO interpretation_space_suggestions
            (source, status, description, suggested_search, priority_score,
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ('qa', 'proposed', 'Old suggestion', 'old query', 0.5, old_time, old_time))

        # Insert a recent one
        cursor.execute("""
            INSERT INTO interpretation_space_suggestions
            (source, status, description, suggested_search, priority_score,
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ('qa', 'proposed', 'New suggestion', 'new query', 0.5,
              now.isoformat(), now.isoformat()))
        conn.commit()
        conn.close()

        stale = self.manager.get_stale_suggestions(days=7)
        self.assertEqual(len(stale), 1, "Should find 1 stale suggestion older than 7 days")

    def test_mark_stale_suggestions(self):
        """Test marking old suggestions as stale."""
        now = datetime.now(timezone.utc)
        old_time = (now - timedelta(days=10)).isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO interpretation_space_suggestions
            (source, status, description, suggested_search, priority_score,
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ('qa', 'proposed', 'Old', 'query', 0.5, old_time, old_time))
        conn.commit()
        conn.close()

        count = self.manager.mark_stale_suggestions(days=7)
        self.assertEqual(count, 1)

        # Verify it's marked stale
        stale_suggestions = self.manager.get_suggestions_by_source('qa', status='stale')
        self.assertEqual(len(stale_suggestions), 1)


class TestSearchSuggestionTracker(unittest.TestCase):
    """Test SearchSuggestionTracker with populated suggestions table."""

    def setUp(self):
        """Create a temporary database with suggestions."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()

        # Apply the schema
        _create_test_schema(self.db_path)

        # Populate with test data
        manager = InterpretationSpaceSuggestionsManager(self.db_path)
        manager.insert_qa_followups(['q1', 'q2'], priority_score=0.6)
        manager.insert_gap_predictor_suggestions([
            {'gap_id': 'g1', 'description': 'd1', 'suggested_search': 's1', 'voi_score': 0.7},
            {'gap_id': 'g2', 'description': 'd2', 'suggested_search': 's2', 'voi_score': 0.65},
        ])

        # Insert some old ones
        now = datetime.now(timezone.utc)
        old_time = (now - timedelta(days=10)).isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO interpretation_space_suggestions
            (source, status, description, suggested_search, priority_score,
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ('qa', 'proposed', 'Very old', 'old', 0.5, old_time, old_time))
        conn.commit()
        conn.close()

    def tearDown(self):
        """Clean up temporary database."""
        Path(self.db_path).unlink(missing_ok=True)

    def test_suggestion_backlog_report(self):
        """Test SearchSuggestionTracker.check_suggestion_backlog() on populated table."""
        tracker = SearchSuggestionTracker(self.db_path, staleness_threshold_days=7)
        report = tracker.check_suggestion_backlog()

        # Should have 5 total unacted suggestions (2 qa + 2 gap_predictor + 1 old)
        self.assertEqual(report.total_unacted_suggestions, 5)

        # Should have at least one old suggestion
        self.assertEqual(report.suggestions_exceeding_staleness, 1)

        # Should have mix by source
        # 3 QA (2 recent + 1 old), 2 gap_predictor tracked as 'other' since source='gap_predictor'
        self.assertEqual(report.by_qa_gaps, 3)
        self.assertEqual(report.by_other, 2)  # gap_predictor uses source='gap_predictor', counts as other
        self.assertGreater(report.age_distribution.oldest_suggestion_days, 7)

    def test_health_status_red_for_stale(self):
        """Test that health status is RED when stale suggestions exist."""
        tracker = SearchSuggestionTracker(self.db_path, staleness_threshold_days=7)
        report = tracker.check_suggestion_backlog()

        self.assertEqual(report.health_status, 'RED')
        self.assertTrue(report.staleness_alert)

    def test_age_distribution_calculation(self):
        """Test age distribution of suggestions."""
        tracker = SearchSuggestionTracker(self.db_path, staleness_threshold_days=7)
        report = tracker.check_suggestion_backlog()

        age_dist = report.age_distribution
        total_in_dist = (
            age_dist.count_0_1d +
            age_dist.count_1_3d +
            age_dist.count_3_7d +
            age_dist.count_7_30d +
            age_dist.count_30plus_d
        )

        self.assertEqual(total_in_dist, 5, "Age distribution should account for all 5 suggestions")


class TestIntegrationQAHandlerWithSuggestions(unittest.TestCase):
    """Test QA handler integration with suggestions tracking."""

    def setUp(self):
        """Create a test database."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()

        # Apply the schema
        _create_test_schema(self.db_path)

    def tearDown(self):
        """Clean up."""
        Path(self.db_path).unlink(missing_ok=True)

    def test_qa_handler_tracks_followups(self):
        """Test that ArbitraryQAHandler tracks follow-ups when initialized with db_path."""
        from src.services.arbitrary_qa_handler import ArbitraryQAHandler

        handler = ArbitraryQAHandler(db_path=self.db_path)
        self.assertIsNotNone(handler.suggestions_mgr)

        # When answer() is called, it should track follow-ups
        # (We won't test the full answer flow here, just verify the manager exists)
        self.assertIsInstance(handler.suggestions_mgr, InterpretationSpaceSuggestionsManager)


if __name__ == '__main__':
    unittest.main()
