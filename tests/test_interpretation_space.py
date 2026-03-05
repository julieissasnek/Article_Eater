"""
Tests for Interpretation Space Engine

Tests the generation of interpretation space questions from T2 mechanism
templates.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock

# Import the module to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.interpretation_space_engine import (
    QuestionRecord,
    CoverageStats,
    InterpretationSpaceEngine
)


class TestQuestionRecord:
    """Tests for QuestionRecord dataclass."""

    def test_question_record_creation(self):
        """QuestionRecord should be creatable with all fields."""
        q = QuestionRecord(
            id="TEMPLATE_001::definitional::0",
            text="What is architectural lighting?",
            type="definitional",
            source_template="TEMPLATE_001",
            mechanism_name="Architectural Light Entrainment",
            generated_date=datetime.now(timezone.utc).isoformat(),
            template_name="Light Entrainment Template",
            confidence=0.8
        )

        assert q.id == "TEMPLATE_001::definitional::0"
        assert q.type == "definitional"
        assert q.confidence == 0.8

    def test_question_record_to_dict(self):
        """to_dict should produce JSON-serializable output."""
        q = QuestionRecord(
            id="TEST::def::0",
            text="Test question?",
            type="definitional",
            source_template="TEST",
            mechanism_name="Test Mechanism",
            generated_date=datetime.now(timezone.utc).isoformat(),
            template_name="Test Template"
        )

        d = q.to_dict()
        assert isinstance(d, dict)
        assert d['id'] == "TEST::def::0"
        assert d['type'] == "definitional"

        # Should be JSON serializable
        json_str = json.dumps(d)
        assert isinstance(json_str, str)

    def test_question_record_from_dict(self):
        """from_dict should reconstruct from dict."""
        original_dict = {
            "id": "Q::1",
            "text": "What?",
            "type": "definitional",
            "source_template": "T",
            "mechanism_name": "M",
            "generated_date": "2026-03-05T12:00:00+00:00",
            "template_name": "Template",
            "confidence": 0.75
        }

        q = QuestionRecord.from_dict(original_dict)
        assert q.id == "Q::1"
        assert q.confidence == 0.75


class TestCoverageStats:
    """Tests for CoverageStats dataclass."""

    def test_coverage_stats_creation(self):
        """CoverageStats should be creatable."""
        stats = CoverageStats(
            total_templates=100,
            templates_with_questions=50,
            total_questions_generated=200,
            coverage_percentage=50.0,
            questions_by_type={
                "definitional": 50,
                "evidential": 50,
                "applied": 50,
                "dialectical": 50
            }
        )

        assert stats.total_templates == 100
        assert stats.coverage_percentage == 50.0
        assert stats.total_questions_generated == 200

    def test_coverage_stats_to_dict(self):
        """to_dict should produce JSON-serializable output."""
        stats = CoverageStats(
            total_templates=10,
            templates_with_questions=5,
            total_questions_generated=20,
            coverage_percentage=50.0
        )

        d = stats.to_dict()
        json_str = json.dumps(d)
        assert isinstance(json_str, str)


class TestInterpretationSpaceEngine:
    """Tests for InterpretationSpaceEngine."""

    @pytest.fixture
    def temp_repo(self, tmp_path):
        """Create a temporary repo structure for testing."""
        repo_root = tmp_path / "repo"
        repo_root.mkdir()

        templates_dir = repo_root / "data" / "templates"
        templates_dir.mkdir(parents=True)

        output_dir = repo_root / "data" / "interpretation_space"
        output_dir.mkdir(parents=True)

        return repo_root

    @pytest.fixture
    def mock_template(self):
        """Create a mock T2 mechanism template."""
        return {
            "template_id": "CHRONO_LIGHT_001",
            "name": "Architectural Light → Circadian Entrainment",
            "higher_order_principle": "Light is a primary circadian zeitgeber",
            "mechanism_chain": [
                {
                    "step": 1,
                    "from": "building_light",
                    "to": "circadian_phase",
                    "description": "Building light environment → circadian phase synchronization"
                }
            ],
            "framework_ids": ["LIGHT"]
        }

    def test_engine_initialization(self, temp_repo):
        """Engine should initialize with repo root."""
        engine = InterpretationSpaceEngine(repo_root=temp_repo)

        assert engine.repo_root == temp_repo
        assert engine.templates_dir == temp_repo / "data" / "templates"
        assert engine.output_dir == temp_repo / "data" / "interpretation_space"
        assert engine.output_dir.exists()

    def test_extract_mechanism_name(self, temp_repo, mock_template):
        """extract_mechanism_name should extract from template."""
        engine = InterpretationSpaceEngine(repo_root=temp_repo)

        # Test mechanism chain extraction
        mechanism = engine.extract_mechanism_name(mock_template)
        assert "light" in mechanism.lower() or "circadian" in mechanism.lower()

    def test_extract_mechanism_name_fallback(self, temp_repo):
        """extract_mechanism_name should fallback gracefully."""
        engine = InterpretationSpaceEngine(repo_root=temp_repo)

        # Template with only name
        template = {"name": "Test Mechanism", "template_id": "TEST"}
        mechanism = engine.extract_mechanism_name(template)
        assert mechanism == "Test Mechanism"

        # Template with only template_id
        template = {"template_id": "TEST_ONLY"}
        mechanism = engine.extract_mechanism_name(template)
        assert mechanism == "TEST_ONLY"

    def test_generate_questions_for_template(self, temp_repo, mock_template):
        """generate_questions_for_template should generate 4 questions."""
        engine = InterpretationSpaceEngine(repo_root=temp_repo)

        questions = engine.generate_questions_for_template(
            "CHRONO_LIGHT_001",
            mock_template
        )

        # Should generate exactly 4 questions (one per type)
        assert len(questions) == 4

        # Should have all types
        types = {q.type for q in questions}
        assert types == {"definitional", "evidential", "applied", "dialectical"}

        # Each question should be properly formed
        for q in questions:
            assert q.id.startswith("CHRONO_LIGHT_001::")
            assert q.source_template == "CHRONO_LIGHT_001"
            assert len(q.text) > 10
            assert q.confidence > 0.0

    def test_generate_all_questions_mock(self, temp_repo, mock_template):
        """generate_all_questions should process all templates."""
        # Create a mock template file
        template_file = temp_repo / "data" / "templates" / "TEST_001.json"
        with open(template_file, 'w') as f:
            json.dump(mock_template, f)

        engine = InterpretationSpaceEngine(repo_root=temp_repo)
        count = engine.generate_all_questions(refresh=True)

        # Should have discovered and processed 1 template
        assert count == 4  # 4 questions per template

        # Should have questions of all types
        assert len(engine.get_questions_by_type("definitional")) > 0
        assert len(engine.get_questions_by_type("evidential")) > 0

    def test_get_questions_by_type(self, temp_repo, mock_template):
        """get_questions_by_type should filter correctly."""
        template_file = temp_repo / "data" / "templates" / "TEST_002.json"
        with open(template_file, 'w') as f:
            json.dump(mock_template, f)

        engine = InterpretationSpaceEngine(repo_root=temp_repo)
        engine.generate_all_questions(refresh=True)

        # Get questions of each type
        def_qs = engine.get_questions_by_type("definitional")
        ev_qs = engine.get_questions_by_type("evidential")

        assert all(q.type == "definitional" for q in def_qs)
        assert all(q.type == "evidential" for q in ev_qs)
        assert len(def_qs) >= 1
        assert len(ev_qs) >= 1

    def test_get_questions_for_template(self, temp_repo, mock_template):
        """get_questions_for_template should filter by source."""
        template_file = temp_repo / "data" / "templates" / "SOURCE_TEMPLATE.json"
        with open(template_file, 'w') as f:
            json.dump({**mock_template, "template_id": "SOURCE_TEMPLATE"}, f)

        engine = InterpretationSpaceEngine(repo_root=temp_repo)
        engine.generate_all_questions(refresh=True)

        questions = engine.get_questions_for_template("SOURCE_TEMPLATE")

        # Should have 4 questions from this template
        assert len(questions) == 4
        assert all(q.source_template == "SOURCE_TEMPLATE" for q in questions)

    def test_get_coverage_stats(self, temp_repo, mock_template):
        """get_coverage_stats should compute correct metrics."""
        # Create 2 template files
        for i in range(2):
            template_file = temp_repo / "data" / "templates" / f"T_{i}.json"
            with open(template_file, 'w') as f:
                t = {**mock_template, "template_id": f"TEMPLATE_{i}"}
                json.dump(t, f)

        engine = InterpretationSpaceEngine(repo_root=temp_repo)
        engine.generate_all_questions(refresh=True)

        stats = engine.get_coverage_stats()

        assert stats.total_templates == 2
        assert stats.templates_with_questions == 2
        assert stats.total_questions_generated == 8  # 4 per template
        assert stats.coverage_percentage == 100.0

        # Check questions by type
        assert stats.questions_by_type["definitional"] == 2
        assert stats.questions_by_type["evidential"] == 2
        assert stats.questions_by_type["applied"] == 2
        assert stats.questions_by_type["dialectical"] == 2

    def test_save_and_load_questions(self, temp_repo, mock_template):
        """save_questions and load_existing_questions should round-trip."""
        template_file = temp_repo / "data" / "templates" / "SAVE_TEST.json"
        with open(template_file, 'w') as f:
            json.dump({**mock_template, "template_id": "SAVE_TEST"}, f)

        # Generate and save
        engine1 = InterpretationSpaceEngine(repo_root=temp_repo)
        engine1.generate_all_questions(refresh=True)
        save_path = engine1.save_questions()

        assert save_path.exists()

        # Load in new engine
        engine2 = InterpretationSpaceEngine(repo_root=temp_repo)
        loaded_count = engine2.load_existing_questions()

        assert loaded_count == 4
        assert len(engine2.questions) == 4

        # Verify structure
        with open(save_path) as f:
            data = json.load(f)
            assert 'metadata' in data
            assert 'questions' in data
            assert data['metadata']['total_questions'] == 4


class TestInterpretationSpaceIntegration:
    """Integration tests with overseer."""

    @pytest.fixture
    def mock_overseer_setup(self, tmp_path):
        """Mock overseer environment."""
        base_dir = tmp_path / "article_eater"
        base_dir.mkdir()

        # Create data structure
        templates_dir = base_dir / "data" / "templates"
        templates_dir.mkdir(parents=True)

        output_dir = base_dir / "data" / "interpretation_space"
        output_dir.mkdir(parents=True)

        return base_dir

    def test_overseer_method_signature(self):
        """Overseer check_interpretation_space_coverage should exist."""
        # This is a smoke test that the method exists and has correct signature
        from src.services.overseer import OverseerService

        assert hasattr(OverseerService, 'check_interpretation_space_coverage')

        # Method should return Dict[str, Any]
        method = getattr(OverseerService, 'check_interpretation_space_coverage')
        assert callable(method)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
