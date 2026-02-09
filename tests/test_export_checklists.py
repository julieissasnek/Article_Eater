"""
Tests for Verification Checklists — Sprint 3.0.4-C
2026-02-09
"""

import json
import pytest

from src.services.export_checklists import (
    Checklist,
    CheckItem,
    ChecklistType,
    CheckStatus,
    CheckSeverity,
    ChecklistTemplates,
    ChecklistRunner,
    create_evidence_checklist,
    create_extraction_checklist,
    create_methodology_checklist,
    create_scope_checklist,
    create_intake_checklist,
    create_export_checklist,
)


# =============================================================================
# CheckItem Tests
# =============================================================================

class TestCheckItem:
    """Test CheckItem class."""

    def test_create_item(self):
        """Test creating a check item."""
        item = CheckItem(
            check_id="test-01",
            description="Test check",
            severity=CheckSeverity.REQUIRED
        )

        assert item.check_id == "test-01"
        assert item.description == "Test check"
        assert item.severity == CheckSeverity.REQUIRED
        assert item.status == CheckStatus.PENDING

    def test_mark_passed(self):
        """Test marking item as passed."""
        item = CheckItem("test-01", "Test")
        item.mark_passed("Verified manually", by="reviewer")

        assert item.status == CheckStatus.PASSED
        assert item.result == "Verified manually"
        assert item.checked_by == "reviewer"
        assert item.checked_at is not None

    def test_mark_failed(self):
        """Test marking item as failed."""
        item = CheckItem("test-01", "Test")
        item.mark_failed("Did not meet criteria", by="reviewer")

        assert item.status == CheckStatus.FAILED
        assert "criteria" in item.result

    def test_mark_skipped(self):
        """Test marking item as skipped."""
        item = CheckItem("test-01", "Test")
        item.mark_skipped("Not applicable to this case")

        assert item.status == CheckStatus.SKIPPED
        assert "applicable" in item.result

    def test_to_dict(self):
        """Test dictionary conversion."""
        item = CheckItem(
            "test-01",
            "Test check",
            CheckSeverity.CRITICAL,
            category="Testing"
        )
        item.mark_passed()

        d = item.to_dict()

        assert d["check_id"] == "test-01"
        assert d["severity"] == "critical"
        assert d["category"] == "Testing"
        assert d["status"] == "passed"


# =============================================================================
# Checklist Tests
# =============================================================================

class TestChecklist:
    """Test Checklist class."""

    def test_create_checklist(self):
        """Test creating a checklist."""
        checklist = Checklist(
            checklist_id="cl-001",
            checklist_type=ChecklistType.EVIDENCE_VERIFICATION,
            title="Test Checklist"
        )

        assert checklist.checklist_id == "cl-001"
        assert checklist.checklist_type == ChecklistType.EVIDENCE_VERIFICATION
        assert len(checklist.items) == 0

    def test_add_items(self):
        """Test adding items to checklist."""
        checklist = Checklist("cl-001", ChecklistType.EXTRACTION_QUALITY, "Test")

        checklist.add_item(CheckItem("c1", "Check 1"))
        checklist.add_item(CheckItem("c2", "Check 2"))

        assert len(checklist.items) == 2

    def test_get_item(self):
        """Test retrieving item by ID."""
        checklist = Checklist("cl-001", ChecklistType.EXTRACTION_QUALITY, "Test")
        checklist.add_item(CheckItem("c1", "Check 1"))
        checklist.add_item(CheckItem("c2", "Check 2"))

        item = checklist.get_item("c1")

        assert item is not None
        assert item.description == "Check 1"

    def test_get_item_not_found(self):
        """Test retrieving non-existent item."""
        checklist = Checklist("cl-001", ChecklistType.EXTRACTION_QUALITY, "Test")

        item = checklist.get_item("nonexistent")

        assert item is None

    def test_get_summary(self):
        """Test summary generation."""
        checklist = Checklist("cl-001", ChecklistType.EXTRACTION_QUALITY, "Test")
        checklist.add_item(CheckItem("c1", "Check 1"))
        checklist.add_item(CheckItem("c2", "Check 2"))
        checklist.add_item(CheckItem("c3", "Check 3"))

        checklist.get_item("c1").mark_passed()
        checklist.get_item("c2").mark_failed("Failed")

        summary = checklist.get_summary()

        assert summary["passed"] == 1
        assert summary["failed"] == 1
        assert summary["pending"] == 1

    def test_is_complete(self):
        """Test completion check."""
        checklist = Checklist("cl-001", ChecklistType.EXTRACTION_QUALITY, "Test")
        checklist.add_item(CheckItem("c1", "Check 1"))
        checklist.add_item(CheckItem("c2", "Check 2"))

        assert not checklist.is_complete()

        checklist.get_item("c1").mark_passed()
        checklist.get_item("c2").mark_passed()

        assert checklist.is_complete()

    def test_is_approved_all_pass(self):
        """Test approval with all items passed."""
        checklist = Checklist("cl-001", ChecklistType.EXTRACTION_QUALITY, "Test")
        checklist.add_item(CheckItem("c1", "Check 1", CheckSeverity.REQUIRED))
        checklist.add_item(CheckItem("c2", "Check 2", CheckSeverity.REQUIRED))

        checklist.get_item("c1").mark_passed()
        checklist.get_item("c2").mark_passed()

        assert checklist.is_approved()

    def test_is_approved_with_critical_failure(self):
        """Test approval blocked by critical failure."""
        checklist = Checklist("cl-001", ChecklistType.EXTRACTION_QUALITY, "Test")
        checklist.add_item(CheckItem("c1", "Check 1", CheckSeverity.CRITICAL))
        checklist.add_item(CheckItem("c2", "Check 2", CheckSeverity.OPTIONAL))

        checklist.get_item("c1").mark_failed("Critical issue")
        checklist.get_item("c2").mark_passed()

        assert not checklist.is_approved()

    def test_is_approved_optional_failure_ok(self):
        """Test approval with only optional failure."""
        checklist = Checklist("cl-001", ChecklistType.EXTRACTION_QUALITY, "Test")
        checklist.add_item(CheckItem("c1", "Check 1", CheckSeverity.REQUIRED))
        checklist.add_item(CheckItem("c2", "Check 2", CheckSeverity.OPTIONAL))

        checklist.get_item("c1").mark_passed()
        checklist.get_item("c2").mark_failed("Optional issue")

        assert checklist.is_approved()

    def test_get_failures(self):
        """Test retrieving failed items."""
        checklist = Checklist("cl-001", ChecklistType.EXTRACTION_QUALITY, "Test")
        checklist.add_item(CheckItem("c1", "Check 1"))
        checklist.add_item(CheckItem("c2", "Check 2"))
        checklist.add_item(CheckItem("c3", "Check 3"))

        checklist.get_item("c1").mark_passed()
        checklist.get_item("c2").mark_failed("Issue A")
        checklist.get_item("c3").mark_failed("Issue B")

        failures = checklist.get_failures()

        assert len(failures) == 2
        assert failures[0].check_id == "c2"

    def test_complete(self):
        """Test completing checklist."""
        checklist = Checklist("cl-001", ChecklistType.EXTRACTION_QUALITY, "Test")
        checklist.add_item(CheckItem("c1", "Check 1"))

        checklist.get_item("c1").mark_passed()
        checklist.complete()

        assert checklist.completed_at is not None
        assert checklist.overall_status == CheckStatus.PASSED

    def test_to_dict(self):
        """Test dictionary conversion."""
        checklist = Checklist(
            "cl-001",
            ChecklistType.EVIDENCE_VERIFICATION,
            "Test Checklist",
            target_id="belief:001"
        )
        checklist.add_item(CheckItem("c1", "Check 1"))

        d = checklist.to_dict()

        assert d["checklist_id"] == "cl-001"
        assert d["checklist_type"] == "evidence_verification"
        assert d["target_id"] == "belief:001"
        assert len(d["items"]) == 1

    def test_to_json(self):
        """Test JSON serialization."""
        checklist = Checklist("cl-001", ChecklistType.EXTRACTION_QUALITY, "Test")
        checklist.add_item(CheckItem("c1", "Check 1"))

        json_str = checklist.to_json()
        parsed = json.loads(json_str)

        assert parsed["checklist_id"] == "cl-001"

    def test_to_markdown(self):
        """Test markdown generation."""
        checklist = Checklist(
            "cl-001",
            ChecklistType.EVIDENCE_VERIFICATION,
            "Evidence Verification",
            description="Verify evidence quality"
        )
        checklist.add_item(CheckItem("c1", "Source is peer-reviewed", CheckSeverity.REQUIRED, "Quality"))
        checklist.add_item(CheckItem("c2", "No conflicts of interest", CheckSeverity.CRITICAL, "Quality"))

        checklist.get_item("c1").mark_passed()
        checklist.get_item("c2").mark_failed("COI detected")

        md = checklist.to_markdown()

        assert "# Evidence Verification" in md
        assert "Verify evidence quality" in md
        assert "[x]" in md  # Passed
        assert "[!]" in md  # Failed
        assert "COI detected" in md
        assert "## Summary" in md


# =============================================================================
# Template Tests
# =============================================================================

class TestChecklistTemplates:
    """Test pre-defined checklist templates."""

    def test_evidence_verification_template(self):
        """Test evidence verification template."""
        checklist = ChecklistTemplates.evidence_verification("belief:001")

        assert checklist.checklist_type == ChecklistType.EVIDENCE_VERIFICATION
        assert checklist.target_id == "belief:001"
        assert len(checklist.items) > 5

        # Should have required methodology checks
        check_ids = [item.check_id for item in checklist.items]
        assert "ev-04" in check_ids  # Methodology described

    def test_extraction_quality_template(self):
        """Test extraction quality template."""
        checklist = ChecklistTemplates.extraction_quality()

        assert checklist.checklist_type == ChecklistType.EXTRACTION_QUALITY
        assert len(checklist.items) >= 8

        # Should have critical accuracy checks
        critical = [i for i in checklist.items if i.severity == CheckSeverity.CRITICAL]
        assert len(critical) >= 2

    def test_methodology_review_template(self):
        """Test methodology review template."""
        checklist = ChecklistTemplates.methodology_review("paper:001")

        assert checklist.checklist_type == ChecklistType.METHODOLOGY_REVIEW
        assert checklist.target_type == "paper"
        assert len(checklist.items) >= 10

    def test_scope_assessment_template(self):
        """Test scope assessment template."""
        checklist = ChecklistTemplates.scope_assessment()

        assert checklist.checklist_type == ChecklistType.SCOPE_ASSESSMENT

        # Should have scope-related categories
        categories = set(item.category for item in checklist.items if item.category)
        assert "Population" in categories
        assert "Enabling Conditions" in categories

    def test_paper_intake_template(self):
        """Test paper intake template."""
        checklist = ChecklistTemplates.paper_intake()

        assert checklist.checklist_type == ChecklistType.PAPER_INTAKE

        # Should have critical requirements
        critical = [i for i in checklist.items if i.severity == CheckSeverity.CRITICAL]
        assert len(critical) >= 2

    def test_pre_export_template(self):
        """Test pre-export template."""
        checklist = ChecklistTemplates.pre_export("export:001")

        assert checklist.checklist_type == ChecklistType.PRE_EXPORT
        assert checklist.target_id == "export:001"


# =============================================================================
# ChecklistRunner Tests
# =============================================================================

class TestChecklistRunner:
    """Test ChecklistRunner class."""

    def test_create_runner(self):
        """Test creating a runner."""
        runner = ChecklistRunner()

        assert runner.auto_checks == {}

    def test_register_auto_check(self):
        """Test registering automated check."""
        runner = ChecklistRunner()

        def check_fn(context):
            return context.get("valid", False)

        runner.register_auto_check("test-check", check_fn)

        assert "test-check" in runner.auto_checks

    def test_run_auto_checks(self):
        """Test running automated checks."""
        runner = ChecklistRunner()

        def always_pass(context):
            return True

        def always_fail(context):
            return False

        runner.register_auto_check("c1", always_pass)
        runner.register_auto_check("c2", always_fail)

        checklist = Checklist("cl-001", ChecklistType.EXTRACTION_QUALITY, "Test")
        checklist.add_item(CheckItem("c1", "Auto pass", auto_check=True))
        checklist.add_item(CheckItem("c2", "Auto fail", auto_check=True))
        checklist.add_item(CheckItem("c3", "Manual check"))

        count = runner.run_auto_checks(checklist, {})

        assert count == 2
        assert checklist.get_item("c1").status == CheckStatus.PASSED
        assert checklist.get_item("c2").status == CheckStatus.FAILED
        assert checklist.get_item("c3").status == CheckStatus.PENDING

    def test_validate_checklist(self):
        """Test checklist validation."""
        runner = ChecklistRunner()

        checklist = Checklist("cl-001", ChecklistType.EXTRACTION_QUALITY, "Test")
        checklist.add_item(CheckItem("c1", "Check 1", CheckSeverity.REQUIRED))
        checklist.add_item(CheckItem("c2", "Check 2", CheckSeverity.CRITICAL))
        checklist.add_item(CheckItem("c3", "Check 3", CheckSeverity.OPTIONAL))

        checklist.get_item("c1").mark_passed()
        checklist.get_item("c2").mark_failed("Critical issue")
        checklist.get_item("c3").mark_passed()

        validation = runner.validate_checklist(checklist)

        assert validation["is_complete"] is True
        assert validation["is_approved"] is False
        assert validation["critical_failures"] == 1
        assert validation["passed"] == 2
        assert validation["failed"] == 1


# =============================================================================
# Convenience Function Tests
# =============================================================================

class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_create_evidence_checklist(self):
        """Test evidence checklist creation."""
        checklist = create_evidence_checklist("belief:123")

        assert checklist.checklist_type == ChecklistType.EVIDENCE_VERIFICATION
        assert checklist.target_id == "belief:123"

    def test_create_extraction_checklist(self):
        """Test extraction checklist creation."""
        checklist = create_extraction_checklist()

        assert checklist.checklist_type == ChecklistType.EXTRACTION_QUALITY

    def test_create_methodology_checklist(self):
        """Test methodology checklist creation."""
        checklist = create_methodology_checklist("paper:456")

        assert checklist.checklist_type == ChecklistType.METHODOLOGY_REVIEW

    def test_create_scope_checklist(self):
        """Test scope checklist creation."""
        checklist = create_scope_checklist()

        assert checklist.checklist_type == ChecklistType.SCOPE_ASSESSMENT

    def test_create_intake_checklist(self):
        """Test intake checklist creation."""
        checklist = create_intake_checklist()

        assert checklist.checklist_type == ChecklistType.PAPER_INTAKE

    def test_create_export_checklist(self):
        """Test export checklist creation."""
        checklist = create_export_checklist()

        assert checklist.checklist_type == ChecklistType.PRE_EXPORT


# =============================================================================
# Integration Tests
# =============================================================================

class TestChecklistWorkflow:
    """Test complete checklist workflows."""

    def test_full_evidence_workflow(self):
        """Test complete evidence verification workflow."""
        # Create checklist
        checklist = create_evidence_checklist("belief:001")

        # Mark source quality checks
        for item in checklist.items:
            if item.category == "Source Quality":
                item.mark_passed("Verified")

        # Fail a methodology check
        method_items = [i for i in checklist.items if i.category == "Methodology"]
        if method_items:
            method_items[0].mark_failed("Sample size too small")

        # Skip replication
        for item in checklist.items:
            if item.category == "Replication":
                item.mark_skipped("No replication studies available")

        # Pass remaining
        for item in checklist.items:
            if item.status == CheckStatus.PENDING:
                item.mark_passed()

        # Complete
        checklist.complete()

        # Verify
        assert checklist.is_complete()
        summary = checklist.get_summary()
        assert summary["failed"] == 1
        assert summary["skipped"] >= 1

    def test_automated_intake_workflow(self):
        """Test automated paper intake workflow."""
        runner = ChecklistRunner()

        # Register automated checks
        runner.register_auto_check("pi-01", lambda ctx: ctx.get("pdf_readable", False))
        runner.register_auto_check("pi-02", lambda ctx: ctx.get("language") == "en")
        runner.register_auto_check("pi-03", lambda ctx: ctx.get("has_metadata", False))

        checklist = create_intake_checklist("paper:001")

        # Mark automated checks
        for item in checklist.items:
            if item.check_id.startswith("pi-0"):
                item.auto_check = True

        # Run with context
        context = {
            "pdf_readable": True,
            "language": "en",
            "has_metadata": True
        }
        runner.run_auto_checks(checklist, context)

        # Check results
        assert checklist.get_item("pi-01").status == CheckStatus.PASSED
        assert checklist.get_item("pi-02").status == CheckStatus.PASSED
        assert checklist.get_item("pi-03").status == CheckStatus.PASSED
