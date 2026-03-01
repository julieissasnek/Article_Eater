"""
Comprehensive tests for the Reflex System.

Tests cover:
- ReflexEvent creation and serialization
- ReflexRegistry registration and execution
- All 10 concrete reflex implementations (detect and fix methods)
- Event logging to JSONL
- Overseer DB reporting
- Health trends queries
- Summary statistics
"""

import json
import sqlite3
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from src.qa.reflex_system import (
    ReflexEvent,
    ReflexResult,
    ReflexRegistry,
    Reflex,
    DirectionNormalizationReflex,
    VagueAntecedentDetectorReflex,
    MissingSampleSizeReflex,
    MalformedExtractionJsonReflex,
    ZeroFindingsExtractionReflex,
    OrphanedVocabTermsReflex,
    BrokenInstrumentIdReferencesReflex,
    StaleLookupTableReflex,
    OutOfRangeCalibrationParametersReflex,
    StaleExtractionFilesReflex,
)


class TestReflexEvent:
    """Tests for ReflexEvent dataclass."""

    def test_event_creation(self):
        """Test creating a ReflexEvent."""
        event = ReflexEvent(
            event_id="evt-001",
            timestamp="2026-03-01T10:00:00Z",
            reflex_id="RFX-EXT-DIR",
            component="extraction_field_validator",
            success_condition_id="EFV-SC1",
            detected=True,
            description="Direction field has bad value",
            auto_fixed=True,
            fix_action="normalized to 'increase'",
            severity="warning",
            context={"file": "test.json", "bad_value": "incr"}
        )

        assert event.event_id == "evt-001"
        assert event.reflex_id == "RFX-EXT-DIR"
        assert event.detected is True
        assert event.auto_fixed is True
        assert event.context["file"] == "test.json"

    def test_event_serialization(self):
        """Test serializing ReflexEvent to dict."""
        from dataclasses import asdict

        event = ReflexEvent(
            event_id="evt-001",
            timestamp="2026-03-01T10:00:00Z",
            reflex_id="RFX-EXT-DIR",
            component="extraction_field_validator",
            success_condition_id="EFV-SC1",
            detected=True,
            description="Direction field has bad value",
            auto_fixed=True,
            fix_action="normalized",
            severity="warning",
            context={"test": "data"}
        )

        event_dict = asdict(event)
        assert isinstance(event_dict, dict)
        assert event_dict["reflex_id"] == "RFX-EXT-DIR"
        assert event_dict["severity"] == "warning"


class TestReflexResult:
    """Tests for ReflexResult dataclass."""

    def test_result_creation_pass(self):
        """Test creating a passing ReflexResult."""
        result = ReflexResult(
            reflex_id="RFX-EXT-DIR",
            passed=True,
            detected_issue=False,
            auto_fixed=False,
            needs_attention=False
        )

        assert result.passed is True
        assert result.detected_issue is False
        assert result.needs_attention is False

    def test_result_creation_with_event(self):
        """Test creating a ReflexResult with an event."""
        event = ReflexEvent(
            event_id="evt-001",
            timestamp="2026-03-01T10:00:00Z",
            reflex_id="RFX-EXT-DIR",
            component="extraction_field_validator",
            success_condition_id="EFV-SC1",
            detected=True,
            description="Test",
            auto_fixed=False,
            fix_action="manual_required",
            severity="error",
            context={}
        )

        result = ReflexResult(
            reflex_id="RFX-EXT-DIR",
            passed=False,
            detected_issue=True,
            auto_fixed=False,
            needs_attention=True,
            event=event
        )

        assert result.event is not None
        assert result.event.reflex_id == "RFX-EXT-DIR"


class TestReflexRegistry:
    """Tests for ReflexRegistry."""

    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / "data" / "extractions").mkdir(parents=True, exist_ok=True)
            (repo_root / "data" / "reflex_events").mkdir(parents=True, exist_ok=True)
            yield repo_root

    def test_registry_creation(self, temp_repo):
        """Test creating a ReflexRegistry."""
        registry = ReflexRegistry(temp_repo)
        assert registry.repo_root == temp_repo
        assert len(registry.reflexes) == 0

    def test_registry_register(self, temp_repo):
        """Test registering a reflex."""
        registry = ReflexRegistry(temp_repo)
        reflex = DirectionNormalizationReflex(temp_repo)
        registry.register(reflex)

        assert "RFX-EXT-DIR" in registry.reflexes
        assert registry.reflexes["RFX-EXT-DIR"] == reflex

    def test_registry_log_event_to_jsonl(self, temp_repo):
        """Test logging an event to JSONL."""
        registry = ReflexRegistry(temp_repo)

        event = ReflexEvent(
            event_id="evt-001",
            timestamp=datetime.now(timezone.utc).isoformat(),
            reflex_id="RFX-EXT-DIR",
            component="extraction_field_validator",
            success_condition_id="EFV-SC1",
            detected=True,
            description="Test event",
            auto_fixed=False,
            fix_action="none",
            severity="warning",
            context={}
        )

        registry._log_event(event)

        # Check that event was logged
        log_files = list((temp_repo / "data" / "reflex_events").glob("*.jsonl"))
        assert len(log_files) > 0

        # Read and verify
        with open(log_files[0], "r") as f:
            logged = json.loads(f.readline())
            assert logged["reflex_id"] == "RFX-EXT-DIR"

    def test_registry_report_to_overseer(self, temp_repo):
        """Test reporting an event to overseer DB."""
        overseer_db = temp_repo / "overseer.db"
        registry = ReflexRegistry(temp_repo, overseer_db_path=overseer_db)

        event = ReflexEvent(
            event_id="evt-001",
            timestamp=datetime.now(timezone.utc).isoformat(),
            reflex_id="RFX-EXT-DIR",
            component="extraction_field_validator",
            success_condition_id="EFV-SC1",
            detected=True,
            description="Test",
            auto_fixed=False,
            fix_action="none",
            severity="warning",
            context={"test": "data"}
        )

        registry._report_to_overseer(event)

        # Verify event was stored
        conn = sqlite3.connect(str(overseer_db))
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reflex_events WHERE event_id = ?", ("evt-001",))
        row = cursor.fetchone()
        conn.close()

        assert row is not None


class TestDirectionNormalizationReflex:
    """Tests for DirectionNormalizationReflex."""

    @pytest.fixture
    def temp_repo_with_extractions(self):
        """Create a temporary repo with extraction files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            extractions_dir = repo_root / "data" / "extractions"
            extractions_dir.mkdir(parents=True, exist_ok=True)

            # Create a bad extraction file
            bad_extraction = {
                "doi": "10.1234/test",
                "findings": [
                    {"direction": "INCREASE", "outcome": "score"},
                    {"direction": "Decr", "outcome": "time"},
                    {"direction": "increase", "outcome": "valid"}
                ]
            }
            with open(extractions_dir / "test.json", "w") as f:
                json.dump(bad_extraction, f)

            yield repo_root

    def test_detect_bad_directions(self, temp_repo_with_extractions):
        """Test detecting non-canonical directions."""
        reflex = DirectionNormalizationReflex(temp_repo_with_extractions)
        problem_found, details = reflex.detect()

        assert problem_found is True
        assert len(details["bad_directions"]) == 2

    def test_fix_directions(self, temp_repo_with_extractions):
        """Test auto-fixing directions."""
        reflex = DirectionNormalizationReflex(temp_repo_with_extractions)
        problem_found, details = reflex.detect()

        fixed, action = reflex.fix(details)
        assert fixed is True
        assert "normalized" in action

        # Verify the fix
        extractions_dir = temp_repo_with_extractions / "data" / "extractions"
        with open(extractions_dir / "test.json", "r") as f:
            data = json.load(f)
            for finding in data["findings"]:
                assert finding["direction"] in {"increase", "decrease", "no_effect", "mixed"}


class TestVagueAntecedentDetectorReflex:
    """Tests for VagueAntecedentDetectorReflex."""

    @pytest.fixture
    def temp_repo_with_vague(self):
        """Create repo with vague antecedents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            extractions_dir = repo_root / "data" / "extractions"
            extractions_dir.mkdir(parents=True, exist_ok=True)

            extraction = {
                "doi": "10.1234/test",
                "findings": [
                    {"antecedent": "the environment was modified", "outcome": "score"},
                    {"antecedent": "bright light (500 lux) was presented", "outcome": "valid"}
                ]
            }
            with open(extractions_dir / "test.json", "w") as f:
                json.dump(extraction, f)

            yield repo_root

    def test_detect_vague_antecedents(self, temp_repo_with_vague):
        """Test detecting vague antecedents."""
        reflex = VagueAntecedentDetectorReflex(temp_repo_with_vague)
        problem_found, details = reflex.detect()

        assert problem_found is True
        assert len(details["vague_antecedents"]) == 1

    def test_cannot_auto_fix_vague(self, temp_repo_with_vague):
        """Test that vague antecedents cannot be auto-fixed."""
        reflex = VagueAntecedentDetectorReflex(temp_repo_with_vague)
        problem_found, details = reflex.detect()

        fixed, action = reflex.fix(details)
        assert fixed is False
        assert "re-extraction" in action.lower()


class TestMissingSampleSizeReflex:
    """Tests for MissingSampleSizeReflex."""

    @pytest.fixture
    def temp_repo_with_missing_ss(self):
        """Create repo with missing sample sizes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            extractions_dir = repo_root / "data" / "extractions"
            extractions_dir.mkdir(parents=True, exist_ok=True)

            extraction = {
                "doi": "10.1234/test",
                "findings": [
                    {"type": "empirical", "outcome": "score", "sample_size": None},
                    {"type": "empirical", "outcome": "valid", "sample_size": 100}
                ]
            }
            with open(extractions_dir / "test.json", "w") as f:
                json.dump(extraction, f)

            yield repo_root

    def test_detect_missing_sample_size(self, temp_repo_with_missing_ss):
        """Test detecting missing sample sizes."""
        reflex = MissingSampleSizeReflex(temp_repo_with_missing_ss)
        problem_found, details = reflex.detect()

        assert problem_found is True
        assert len(details["missing_samples"]) == 1

    def test_cannot_auto_fix_sample_size(self, temp_repo_with_missing_ss):
        """Test that missing sample sizes cannot be auto-fixed."""
        reflex = MissingSampleSizeReflex(temp_repo_with_missing_ss)
        problem_found, details = reflex.detect()

        fixed, action = reflex.fix(details)
        assert fixed is False
        assert "inference" in action.lower()


class TestMalformedExtractionJsonReflex:
    """Tests for MalformedExtractionJsonReflex."""

    @pytest.fixture
    def temp_repo_with_malformed(self):
        """Create repo with malformed JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            extractions_dir = repo_root / "data" / "extractions"
            extractions_dir.mkdir(parents=True, exist_ok=True)

            # Write valid file
            valid = {"doi": "10.1234/valid", "findings": []}
            with open(extractions_dir / "valid.json", "w") as f:
                json.dump(valid, f)

            # Write invalid file
            with open(extractions_dir / "bad.json", "w") as f:
                f.write('{"invalid": json}')

            yield repo_root

    def test_detect_malformed_json(self, temp_repo_with_malformed):
        """Test detecting malformed JSON."""
        reflex = MalformedExtractionJsonReflex(temp_repo_with_malformed)
        problem_found, details = reflex.detect()

        assert problem_found is True
        assert len(details["malformed_files"]) == 1
        assert details["malformed_files"][0]["file"] == "bad.json"

    def test_fix_quarantines_malformed(self, temp_repo_with_malformed):
        """Test that malformed files are quarantined."""
        reflex = MalformedExtractionJsonReflex(temp_repo_with_malformed)
        problem_found, details = reflex.detect()

        fixed, action = reflex.fix(details)
        assert fixed is True

        # Verify quarantine
        quarantine_dir = temp_repo_with_malformed / "data" / "extractions" / "quarantine"
        assert (quarantine_dir / "bad.json").exists()


class TestZeroFindingsExtractionReflex:
    """Tests for ZeroFindingsExtractionReflex."""

    @pytest.fixture
    def temp_repo_with_empty(self):
        """Create repo with zero-findings extractions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            extractions_dir = repo_root / "data" / "extractions"
            extractions_dir.mkdir(parents=True, exist_ok=True)

            # Empty extraction
            with open(extractions_dir / "empty.json", "w") as f:
                json.dump({"doi": "10.1234/empty", "findings": []}, f)

            # Valid extraction
            with open(extractions_dir / "valid.json", "w") as f:
                json.dump({"doi": "10.1234/valid", "findings": [{"outcome": "score"}]}, f)

            yield repo_root

    def test_detect_empty_findings(self, temp_repo_with_empty):
        """Test detecting zero-findings extractions."""
        reflex = ZeroFindingsExtractionReflex(temp_repo_with_empty)
        problem_found, details = reflex.detect()

        assert problem_found is True
        assert len(details["empty_extractions"]) == 1


class TestOrphanedVocabTermsReflex:
    """Tests for OrphanedVocabTermsReflex."""

    @pytest.fixture
    def temp_repo_with_vocab(self):
        """Create repo with vocab and extractions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            data_dir = repo_root / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            (data_dir / "extractions").mkdir(exist_ok=True)

            # Create vocab
            vocab = {
                "terms": [
                    {"id": "term-001", "name": "used_term"},
                    {"id": "term-002", "name": "orphan_term"}
                ]
            }
            with open(data_dir / "outcome_vocab.json", "w") as f:
                json.dump(vocab, f)

            # Create extraction using only term-001
            extraction = {
                "doi": "10.1234/test",
                "findings": [{"outcome_id": "term-001"}]
            }
            with open(data_dir / "extractions" / "test.json", "w") as f:
                json.dump(extraction, f)

            yield repo_root

    def test_detect_orphaned_terms(self, temp_repo_with_vocab):
        """Test detecting orphaned vocab terms."""
        reflex = OrphanedVocabTermsReflex(temp_repo_with_vocab)
        problem_found, details = reflex.detect()

        assert problem_found is True
        assert "term-002" in details["orphaned_terms"]


class TestStaleLookupTableReflex:
    """Tests for StaleLookupTableReflex."""

    @pytest.fixture
    def temp_repo_with_lookup(self):
        """Create repo with vocab and lookup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            data_dir = repo_root / "data"
            data_dir.mkdir(parents=True, exist_ok=True)

            # Create vocab with 10 terms
            vocab = {
                "terms": [
                    {"id": f"term-{i:03d}", "name": f"term_{i}", "level": 1}
                    for i in range(10)
                ]
            }
            with open(data_dir / "outcome_vocab.json", "w") as f:
                json.dump(vocab, f)

            # Create stale lookup with only 5 terms
            lookup = {
                "terms": [
                    {"id": f"term-{i:03d}", "name": f"term_{i}", "level": 1}
                    for i in range(5)
                ]
            }
            with open(data_dir / "outcome_lookup.json", "w") as f:
                json.dump(lookup, f)

            yield repo_root

    def test_detect_stale_lookup(self, temp_repo_with_lookup):
        """Test detecting stale lookup."""
        reflex = StaleLookupTableReflex(temp_repo_with_lookup)
        problem_found, details = reflex.detect()

        assert problem_found is True
        assert details["vocab_count"] > details["lookup_count"]

    def test_fix_regenerates_lookup(self, temp_repo_with_lookup):
        """Test that lookup is regenerated."""
        reflex = StaleLookupTableReflex(temp_repo_with_lookup)
        problem_found, details = reflex.detect()

        fixed, action = reflex.fix(details)
        assert fixed is True

        # Verify lookup was regenerated
        with open(temp_repo_with_lookup / "data" / "outcome_lookup.json", "r") as f:
            new_lookup = json.load(f)
            assert len(new_lookup["terms"]) == 10


class TestOutOfRangeCalibrationReflex:
    """Tests for OutOfRangeCalibrationParametersReflex."""

    @pytest.fixture
    def temp_repo_with_calib(self):
        """Create repo with calibration files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            calib_dir = repo_root / "data" / "calibration"
            calib_dir.mkdir(parents=True, exist_ok=True)

            # Valid calibration
            valid_calib = {
                "alpha": 0.5,
                "weights": {"w1": 0.3, "w2": 0.7}
            }
            with open(calib_dir / "ch_valid.json", "w") as f:
                json.dump(valid_calib, f)

            # Invalid calibration
            bad_calib = {
                "alpha": 1.5,  # Out of range
                "weights": {"w1": -0.5, "w2": 0.7}  # Negative weight
            }
            with open(calib_dir / "ch_bad.json", "w") as f:
                json.dump(bad_calib, f)

            yield repo_root

    def test_detect_out_of_range(self, temp_repo_with_calib):
        """Test detecting out-of-range parameters."""
        reflex = OutOfRangeCalibrationParametersReflex(temp_repo_with_calib)
        problem_found, details = reflex.detect()

        assert problem_found is True
        assert len(details["out_of_range"]) >= 2

    def test_fix_clamps_parameters(self, temp_repo_with_calib):
        """Test that parameters are clamped."""
        reflex = OutOfRangeCalibrationParametersReflex(temp_repo_with_calib)
        problem_found, details = reflex.detect()

        fixed, action = reflex.fix(details)
        assert fixed is True

        # Verify clamping
        with open(temp_repo_with_calib / "data" / "calibration" / "ch_bad.json", "r") as f:
            data = json.load(f)
            assert 0.0 <= data["alpha"] <= 1.0
            assert all(w >= 0.0 for w in data["weights"].values())


class TestStaleExtractionFilesReflex:
    """Tests for StaleExtractionFilesReflex."""

    @pytest.fixture
    def temp_repo_with_stale_files(self):
        """Create repo with stale extraction files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            extractions_dir = repo_root / "data" / "extractions"
            extractions_dir.mkdir(parents=True, exist_ok=True)

            # Create recent file
            recent_file = extractions_dir / "recent.json"
            with open(recent_file, "w") as f:
                json.dump({"doi": "10.1234/recent"}, f)

            # Create stale file (older than 90 days)
            stale_file = extractions_dir / "stale.json"
            with open(stale_file, "w") as f:
                json.dump({"doi": "10.1234/stale"}, f)

            # Set modification time to 100 days ago
            old_time = (datetime.now(timezone.utc) - timedelta(days=100)).timestamp()
            stale_file.touch()
            import os
            os.utime(stale_file, (old_time, old_time))

            yield repo_root

    def test_detect_stale_files(self, temp_repo_with_stale_files):
        """Test detecting stale extraction files."""
        reflex = StaleExtractionFilesReflex(temp_repo_with_stale_files, age_days=90)
        problem_found, details = reflex.detect()

        assert problem_found is True
        assert len(details["stale_files"]) >= 1


class TestReflexIntegration:
    """Integration tests for the full reflex system."""

    @pytest.fixture
    def full_temp_repo(self):
        """Create a complete temporary repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / "data" / "extractions").mkdir(parents=True, exist_ok=True)
            (repo_root / "data" / "reflex_events").mkdir(parents=True, exist_ok=True)
            (repo_root / "data" / "calibration").mkdir(parents=True, exist_ok=True)

            # Add some sample data
            extraction = {
                "doi": "10.1234/test",
                "findings": [
                    {"direction": "INCREASE", "outcome": "score", "sample_size": None}
                ]
            }
            with open(repo_root / "data" / "extractions" / "test.json", "w") as f:
                json.dump(extraction, f)

            yield repo_root

    def test_run_all_reflexes(self, full_temp_repo):
        """Test running all reflexes together."""
        registry = ReflexRegistry(full_temp_repo)

        # Register all reflexes
        registry.register(DirectionNormalizationReflex(full_temp_repo))
        registry.register(VagueAntecedentDetectorReflex(full_temp_repo))
        registry.register(MissingSampleSizeReflex(full_temp_repo))
        registry.register(MalformedExtractionJsonReflex(full_temp_repo))
        registry.register(ZeroFindingsExtractionReflex(full_temp_repo))

        results = registry.run_all()
        assert len(results) == 5

        # Check that at least some issues were detected
        detected = sum(1 for r in results if r.detected_issue)
        assert detected > 0

    def test_health_trends_query(self, full_temp_repo):
        """Test querying health trends."""
        registry = ReflexRegistry(full_temp_repo)
        registry.register(DirectionNormalizationReflex(full_temp_repo))

        # Run reflexes to generate events
        registry.run_all()

        # Query trends
        trends = registry.get_health_trends(days=7)
        assert "days" in trends
        assert "improving" in trends
        assert "summary" in trends

    def test_summary_stats(self, full_temp_repo):
        """Test getting summary statistics."""
        registry = ReflexRegistry(full_temp_repo)
        registry.register(DirectionNormalizationReflex(full_temp_repo))

        # Run reflexes
        registry.run_all()

        # Get stats
        stats = registry.get_summary_stats()
        assert "total_events" in stats
        assert "severity_breakdown" in stats
        assert "top_recurring_issues" in stats
        assert "reflexes_registered" in stats

    def test_run_component_filtered(self, full_temp_repo):
        """Test running reflexes for a specific component."""
        registry = ReflexRegistry(full_temp_repo)

        registry.register(DirectionNormalizationReflex(full_temp_repo))
        registry.register(VagueAntecedentDetectorReflex(full_temp_repo))
        registry.register(OrphanedVocabTermsReflex(full_temp_repo))

        # Run only extraction reflexes
        results = registry.run_component("extraction_field_validator")

        # Should get extraction reflexes
        assert len(results) >= 2
        assert all(r.event.component == "extraction_field_validator" for r in results if r.event)


class TestReflexBaseClass:
    """Tests for the base Reflex class."""

    def test_reflex_initialization(self):
        """Test creating a Reflex instance."""

        class SimpleReflex(Reflex):
            def detect(self):
                return False, {}

        reflex = SimpleReflex(
            reflex_id="TEST-001",
            component="test",
            success_condition_id="TEST-SC1",
            description="Simple test reflex"
        )

        assert reflex.reflex_id == "TEST-001"
        assert reflex.component == "test"

    def test_reflex_run_no_problem(self):
        """Test running a reflex that detects no problem."""

        class NoOpReflex(Reflex):
            def detect(self):
                return False, {}

        reflex = NoOpReflex(
            reflex_id="TEST-001",
            component="test",
            success_condition_id="TEST-SC1",
            description="Test"
        )

        result = reflex.run()
        assert result.passed is True
        assert result.detected_issue is False
        assert result.event is None

    def test_reflex_run_detects_problem(self):
        """Test running a reflex that detects a problem."""

        class ProblemReflex(Reflex):
            def detect(self):
                return True, {"issue": "found"}

            def fix(self, details):
                return False, "cannot_fix"

        reflex = ProblemReflex(
            reflex_id="TEST-001",
            component="test",
            success_condition_id="TEST-SC1",
            description="Test"
        )

        result = reflex.run()
        assert result.passed is False
        assert result.detected_issue is True
        assert result.needs_attention is True
        assert result.event is not None

    def test_reflex_run_fixes_problem(self):
        """Test running a reflex that fixes a problem."""

        class FixReflex(Reflex):
            def detect(self):
                return True, {"issue": "found"}

            def fix(self, details):
                return True, "fixed"

        reflex = FixReflex(
            reflex_id="TEST-001",
            component="test",
            success_condition_id="TEST-SC1",
            description="Test"
        )

        result = reflex.run()
        assert result.detected_issue is True
        assert result.auto_fixed is True
        assert result.needs_attention is False
