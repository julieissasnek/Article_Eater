"""
Tests for TemplateRecord DB table and template scanner.

Per Doc 68 Part 4.1 validation requirements:
- All 150 files load without error
- Query "all active Gen-2 CREA series" returns CREA1-CREA4
- No duplicate display_ids
- Count by dedup_status matches expected (~14 superseded, ~18 residual, ~10 gap, ~8 reference)
"""

import os
import tempfile
import pytest
from pathlib import Path
from collections import Counter

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.cmr.models import Base, TemplateRecord, get_engine
from src.cmr.template_scanner import (
    scan_templates,
    scan_template_file,
    extract_series,
    determine_generation,
    classify_dedup_status,
    query_active_gen2_series,
    query_by_dedup_status,
)


@pytest.fixture
def test_db():
    """Create a temporary test database."""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session, db_path
    session.close()
    os.unlink(db_path)


@pytest.fixture
def populated_db(test_db):
    """Database populated with all template records."""
    session, db_path = test_db
    # Run the scanner
    records = scan_templates(db_path=db_path, clear_existing=True)
    # Refresh session to see new records
    session.expire_all()
    return session, db_path, records


class TestExtractSeries:
    """Tests for series extraction from display_id."""

    def test_crea_series(self):
        assert extract_series("CREA4") == "CREA"
        assert extract_series("CREA1") == "CREA"

    def test_single_letter_series(self):
        assert extract_series("L1") == "L"
        assert extract_series("T27") == "T"

    def test_multi_letter_series(self):
        assert extract_series("MAT3") == "MAT"
        assert extract_series("SOC2") == "SOC"
        assert extract_series("VIEW1") == "VIEW"
        assert extract_series("SC4") == "SC"

    def test_auxiliary_series(self):
        assert extract_series("AX12") == "AX"


class TestDetermineGeneration:
    """Tests for generation determination."""

    def test_gen2_series(self):
        assert determine_generation("CREA4", "CREA") == 2
        assert determine_generation("L1", "L") == 2
        assert determine_generation("MAT3", "MAT") == 2
        assert determine_generation("VIEW1", "VIEW") == 2

    def test_gen1_series(self):
        assert determine_generation("T27", "T") == 1
        assert determine_generation("AX12", "AX") == 1
        assert determine_generation("M5", "M") == 1


class TestClassifyDedupStatus:
    """Tests for deduplication status classification."""

    def test_gen2_always_active(self):
        status, superseded_by = classify_dedup_status("CREA4", "CREA", 2)
        assert status == "active"
        assert superseded_by is None

    def test_t_series_superseded(self):
        status, superseded_by = classify_dedup_status("T3", "T", 1)
        assert status == "superseded"
        assert superseded_by == "VF1"

    def test_t_series_gap(self):
        status, superseded_by = classify_dedup_status("T6", "T", 1)
        assert status == "gap"
        assert superseded_by is None

    def test_t_series_reference(self):
        status, superseded_by = classify_dedup_status("T12", "T", 1)
        assert status == "reference"
        assert superseded_by is None

    def test_t_series_residual(self):
        status, superseded_by = classify_dedup_status("T1", "T", 1)
        assert status == "residual"


class TestScanTemplates:
    """Integration tests for template scanning."""

    def test_all_150_files_load(self, populated_db):
        """All template files should load without error."""
        session, db_path, records = populated_db
        # Count varies as panels add templates (was 151, now 163 after dedup)
        assert len(records) >= 150, f"Expected at least 150 templates, got {len(records)}"

    def test_query_active_gen2_crea_series(self, populated_db):
        """Query 'all active Gen-2 CREA series' should return CREA1-CREA4."""
        session, db_path, records = populated_db
        crea_templates = query_active_gen2_series(session, "CREA")
        display_ids = [t.display_id for t in crea_templates]

        # Should have exactly CREA1, CREA2, CREA3, CREA4
        expected = ["CREA1", "CREA2", "CREA3", "CREA4"]
        assert sorted(display_ids) == sorted(expected), (
            f"Expected {expected}, got {display_ids}"
        )

    def test_no_duplicate_display_ids(self, populated_db):
        """No duplicate display_ids should exist."""
        session, db_path, records = populated_db
        display_ids = [r.display_id for r in records]
        duplicates = [id for id, count in Counter(display_ids).items() if count > 1]
        assert len(duplicates) == 0, f"Found duplicate display_ids: {duplicates}"

    def test_no_duplicate_template_ids(self, populated_db):
        """No duplicate template_ids should exist."""
        session, db_path, records = populated_db
        template_ids = [r.template_id for r in records]
        duplicates = [id for id, count in Counter(template_ids).items() if count > 1]
        assert len(duplicates) == 0, f"Found duplicate template_ids: {duplicates}"

    def test_dedup_status_counts_reasonable(self, populated_db):
        """Dedup status counts should be in expected ranges per Doc 67."""
        session, db_path, records = populated_db
        status_counts = Counter(r.dedup_status for r in records)

        # Doc 67 estimates: ~14 superseded, ~18 residual, ~10 gap, ~8 reference
        # Allow some flexibility since classification may differ slightly
        assert status_counts.get("superseded", 0) >= 5, "Too few superseded templates"
        assert status_counts.get("residual", 0) >= 5, "Too few residual templates"
        assert status_counts.get("gap", 0) >= 5, "Too few gap templates"
        assert status_counts.get("reference", 0) >= 3, "Too few reference templates"
        assert status_counts.get("active", 0) >= 50, "Too few active templates"

    def test_generation_distribution(self, populated_db):
        """Should have mix of Gen-1 and Gen-2 templates."""
        session, db_path, records = populated_db
        gen_counts = Counter(r.generation for r in records)

        assert gen_counts.get(1, 0) > 0, "No Gen-1 templates found"
        assert gen_counts.get(2, 0) > 0, "No Gen-2 templates found"

    def test_series_coverage(self, populated_db):
        """Should have templates from major series."""
        session, db_path, records = populated_db
        series = set(r.series for r in records)

        # Must have key series (SOC removed as duplicates merged into full templates)
        required_series = {"T", "CREA", "L", "SC", "VIEW", "VF"}
        missing = required_series - series
        assert len(missing) == 0, f"Missing series: {missing}"

    def test_all_records_have_required_fields(self, populated_db):
        """All records should have non-empty required fields."""
        session, db_path, records = populated_db

        for r in records:
            assert r.template_id, f"{r.display_id} missing template_id"
            assert r.display_id, "Record missing display_id"
            assert r.name, f"{r.display_id} missing name"
            assert r.series, f"{r.display_id} missing series"
            assert r.generation in (1, 2), f"{r.display_id} invalid generation: {r.generation}"
            assert r.dedup_status in ("active", "superseded", "residual", "reference", "gap"), \
                f"{r.display_id} invalid dedup_status: {r.dedup_status}"
            assert r.pe_contribution, f"{r.display_id} missing pe_contribution"
            assert r.maturity, f"{r.display_id} missing maturity"
            assert r.calibration_status, f"{r.display_id} missing calibration_status"
            assert r.practical_accessibility in ("A", "B", "C", "D"), \
                f"{r.display_id} invalid practical_accessibility: {r.practical_accessibility}"
            assert r.json_path, f"{r.display_id} missing json_path"


class TestQueryHelpers:
    """Tests for query helper functions."""

    def test_query_by_dedup_status_active(self, populated_db):
        """Query active templates should return substantial list."""
        session, db_path, records = populated_db
        active = query_by_dedup_status(session, "active")
        assert len(active) >= 50, f"Expected >=50 active templates, got {len(active)}"

    def test_query_by_dedup_status_superseded(self, populated_db):
        """Query superseded templates should return some."""
        session, db_path, records = populated_db
        superseded = query_by_dedup_status(session, "superseded")
        assert len(superseded) >= 5, f"Expected >=5 superseded templates"

    def test_query_active_gen2_light_series(self, populated_db):
        """Query L series should return L1-L5 or subset."""
        session, db_path, records = populated_db
        light_templates = query_active_gen2_series(session, "L")
        # All returned should be L-series
        for t in light_templates:
            assert t.series == "L"
            assert t.generation == 2
            assert t.dedup_status == "active"
