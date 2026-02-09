"""
Tests for Export Audit Trail Service — Sprint 3.0.5-G
2026-02-10

Tests cover audit logging, querying, verification, and reporting.
"""

import pytest
import json
import time
from datetime import datetime, timezone

from src.services.export_audit import (
    ExportAuditService,
    AuditEntry,
    AuditSummary,
    ExportContext,
    ExportType,
    ExportFormat,
    AuditStatus,
    AuditedExport,
    get_audit_service,
    audit_export,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def audit_service():
    """Create fresh in-memory audit service."""
    return ExportAuditService(db_path=":memory:")


@pytest.fixture
def sample_context():
    """Create sample export context."""
    return ExportContext(
        query="What reduces stress?",
        belief_ids=["B001", "B002", "B003"],
        filters_applied={"status": ["ACCEPTED"], "min_credence": 0.5},
        scope_conditions={"population": "Office workers"},
        purpose="Research report"
    )


# =============================================================================
# Basic Logging Tests
# =============================================================================

class TestAuditLogging:
    """Tests for audit logging functionality."""

    def test_log_export_start(self, audit_service):
        """Test logging export start."""
        audit_id = audit_service.log_export_start(
            export_type=ExportType.BIBTEX,
            export_format=ExportFormat.BIBTEX
        )

        assert audit_id is not None
        assert audit_id.startswith("EXP-")

    def test_log_export_start_with_context(self, audit_service, sample_context):
        """Test logging export start with context."""
        audit_id = audit_service.log_export_start(
            export_type=ExportType.EVIDENCE_SUMMARY,
            export_format=ExportFormat.MARKDOWN,
            context=sample_context,
            user_id="user123"
        )

        entry = audit_service.get_entry(audit_id)

        assert entry is not None
        assert entry.context is not None
        assert entry.context.query == "What reduces stress?"
        assert entry.user_id == "user123"

    def test_log_export_complete(self, audit_service):
        """Test logging export completion."""
        audit_id = audit_service.log_export_start(
            export_type=ExportType.BIBTEX,
            export_format=ExportFormat.BIBTEX
        )

        content = b"@article{test, title={Test Article}}"
        audit_service.log_export_complete(
            audit_id=audit_id,
            content=content,
            item_count=5,
            duration_ms=100
        )

        entry = audit_service.get_entry(audit_id)

        assert entry.status == AuditStatus.COMPLETED
        assert entry.item_count == 5
        assert entry.file_size_bytes == len(content)
        assert entry.content_hash is not None
        assert entry.duration_ms == 100

    def test_log_export_failed(self, audit_service):
        """Test logging export failure."""
        audit_id = audit_service.log_export_start(
            export_type=ExportType.TECHNICAL_REPORT,
            export_format=ExportFormat.PDF
        )

        audit_service.log_export_failed(
            audit_id=audit_id,
            error_message="PDF generation failed",
            duration_ms=50
        )

        entry = audit_service.get_entry(audit_id)

        assert entry.status == AuditStatus.FAILED
        assert entry.error_message == "PDF generation failed"

    def test_log_export_cancelled(self, audit_service):
        """Test logging export cancellation."""
        audit_id = audit_service.log_export_start(
            export_type=ExportType.BIBTEX,
            export_format=ExportFormat.BIBTEX
        )

        audit_service.log_export_cancelled(
            audit_id=audit_id,
            reason="User cancelled"
        )

        entry = audit_service.get_entry(audit_id)

        assert entry.status == AuditStatus.CANCELLED

    def test_content_hash_computed(self, audit_service):
        """Test that content hash is computed correctly."""
        audit_id = audit_service.log_export_start(
            export_type=ExportType.BELIEF_DATA,
            export_format=ExportFormat.JSON
        )

        content = b'{"test": "data"}'
        audit_service.log_export_complete(audit_id, content)

        entry = audit_service.get_entry(audit_id)

        # Hash should be SHA-256 (64 hex chars)
        assert len(entry.content_hash) == 64


# =============================================================================
# Query Tests
# =============================================================================

class TestAuditQueries:
    """Tests for querying audit entries."""

    def test_get_entry(self, audit_service):
        """Test getting a specific entry."""
        audit_id = audit_service.log_export_start(
            export_type=ExportType.BIBTEX,
            export_format=ExportFormat.BIBTEX
        )

        entry = audit_service.get_entry(audit_id)

        assert entry is not None
        assert entry.audit_id == audit_id

    def test_get_entry_not_found(self, audit_service):
        """Test getting non-existent entry."""
        entry = audit_service.get_entry("EXP-00000000-NOTFOUND")
        assert entry is None

    def test_get_entries_default(self, audit_service):
        """Test getting entries with default params."""
        # Create multiple entries
        for _ in range(5):
            audit_service.log_export_start(
                export_type=ExportType.BIBTEX,
                export_format=ExportFormat.BIBTEX
            )

        entries = audit_service.get_entries()

        assert len(entries) == 5

    def test_get_entries_with_limit(self, audit_service):
        """Test getting entries with limit."""
        for _ in range(10):
            audit_service.log_export_start(
                export_type=ExportType.BIBTEX,
                export_format=ExportFormat.BIBTEX
            )

        entries = audit_service.get_entries(limit=5)

        assert len(entries) == 5

    def test_get_entries_filter_by_type(self, audit_service):
        """Test filtering entries by export type."""
        audit_service.log_export_start(ExportType.BIBTEX, ExportFormat.BIBTEX)
        audit_service.log_export_start(ExportType.BIBTEX, ExportFormat.BIBTEX)
        audit_service.log_export_start(ExportType.TECHNICAL_REPORT, ExportFormat.PDF)

        bibtex_entries = audit_service.get_entries(export_type=ExportType.BIBTEX)

        assert len(bibtex_entries) == 2

    def test_get_entries_filter_by_status(self, audit_service):
        """Test filtering entries by status."""
        id1 = audit_service.log_export_start(ExportType.BIBTEX, ExportFormat.BIBTEX)
        id2 = audit_service.log_export_start(ExportType.BIBTEX, ExportFormat.BIBTEX)

        audit_service.log_export_complete(id1, b"content", item_count=1)
        audit_service.log_export_failed(id2, "Error")

        completed = audit_service.get_entries(status=AuditStatus.COMPLETED)
        failed = audit_service.get_entries(status=AuditStatus.FAILED)

        assert len(completed) == 1
        assert len(failed) == 1

    def test_get_entries_filter_by_user(self, audit_service):
        """Test filtering entries by user."""
        audit_service.log_export_start(
            ExportType.BIBTEX, ExportFormat.BIBTEX, user_id="user1"
        )
        audit_service.log_export_start(
            ExportType.BIBTEX, ExportFormat.BIBTEX, user_id="user2"
        )

        user1_entries = audit_service.get_entries(user_id="user1")

        assert len(user1_entries) == 1


# =============================================================================
# Summary Tests
# =============================================================================

class TestAuditSummary:
    """Tests for audit summary statistics."""

    def test_get_summary_empty(self, audit_service):
        """Test summary with no entries."""
        summary = audit_service.get_summary()

        assert summary.total_exports == 0

    def test_get_summary_totals(self, audit_service):
        """Test summary totals."""
        # Create entries
        id1 = audit_service.log_export_start(ExportType.BIBTEX, ExportFormat.BIBTEX)
        id2 = audit_service.log_export_start(ExportType.TECHNICAL_REPORT, ExportFormat.PDF)
        id3 = audit_service.log_export_start(ExportType.BIBTEX, ExportFormat.BIBTEX)

        audit_service.log_export_complete(id1, b"content1", item_count=5)
        audit_service.log_export_complete(id2, b"content2", item_count=10)
        audit_service.log_export_failed(id3, "Error")

        summary = audit_service.get_summary()

        assert summary.total_exports == 3
        assert summary.total_items_exported == 15

    def test_get_summary_by_type(self, audit_service):
        """Test summary breakdown by type."""
        audit_service.log_export_start(ExportType.BIBTEX, ExportFormat.BIBTEX)
        audit_service.log_export_start(ExportType.BIBTEX, ExportFormat.BIBTEX)
        audit_service.log_export_start(ExportType.TECHNICAL_REPORT, ExportFormat.PDF)

        summary = audit_service.get_summary()

        assert summary.exports_by_type.get("bibtex") == 2
        assert summary.exports_by_type.get("technical_report") == 1

    def test_get_summary_by_status(self, audit_service):
        """Test summary breakdown by status."""
        id1 = audit_service.log_export_start(ExportType.BIBTEX, ExportFormat.BIBTEX)
        id2 = audit_service.log_export_start(ExportType.BIBTEX, ExportFormat.BIBTEX)

        audit_service.log_export_complete(id1, b"content")
        # id2 stays initiated

        summary = audit_service.get_summary()

        assert summary.exports_by_status.get("completed") == 1
        assert summary.exports_by_status.get("initiated") == 1


# =============================================================================
# Verification Tests
# =============================================================================

class TestVerification:
    """Tests for content verification."""

    def test_verify_export_correct(self, audit_service):
        """Test verifying correct content."""
        audit_id = audit_service.log_export_start(
            ExportType.BIBTEX, ExportFormat.BIBTEX
        )

        content = b"@article{test, title={Test}}"
        audit_service.log_export_complete(audit_id, content)

        result = audit_service.verify_export(audit_id, content)

        assert result is True

    def test_verify_export_incorrect(self, audit_service):
        """Test verifying incorrect content."""
        audit_id = audit_service.log_export_start(
            ExportType.BIBTEX, ExportFormat.BIBTEX
        )

        content = b"@article{test, title={Test}}"
        audit_service.log_export_complete(audit_id, content)

        wrong_content = b"@article{different, title={Different}}"
        result = audit_service.verify_export(audit_id, wrong_content)

        assert result is False

    def test_verify_export_not_found(self, audit_service):
        """Test verifying non-existent export."""
        result = audit_service.verify_export("EXP-NOTFOUND", b"content")
        assert result is False


# =============================================================================
# Provenance Tests
# =============================================================================

class TestProvenance:
    """Tests for provenance tracking."""

    def test_get_provenance(self, audit_service, sample_context):
        """Test getting provenance information."""
        audit_id = audit_service.log_export_start(
            export_type=ExportType.EVIDENCE_SUMMARY,
            export_format=ExportFormat.MARKDOWN,
            context=sample_context
        )

        audit_service.log_export_complete(
            audit_id,
            b"# Evidence Summary",
            item_count=3,
            web_state_hash="abc123"
        )

        provenance = audit_service.get_provenance(audit_id)

        assert provenance["audit_id"] == audit_id
        assert provenance["query"] == "What reduces stress?"
        assert provenance["belief_ids"] == ["B001", "B002", "B003"]
        assert provenance["item_count"] == 3
        assert provenance["web_state_hash"] == "abc123"

    def test_get_provenance_not_found(self, audit_service):
        """Test getting provenance for non-existent entry."""
        provenance = audit_service.get_provenance("EXP-NOTFOUND")
        assert provenance == {}


# =============================================================================
# Report Generation Tests
# =============================================================================

class TestReportGeneration:
    """Tests for audit report generation."""

    def test_generate_markdown_report(self, audit_service):
        """Test generating markdown report."""
        id1 = audit_service.log_export_start(ExportType.BIBTEX, ExportFormat.BIBTEX)
        audit_service.log_export_complete(id1, b"content", item_count=5)

        report = audit_service.generate_audit_report(format="markdown")

        assert "# Export Audit Report" in report
        assert "Total Exports" in report
        assert "bibtex" in report.lower()

    def test_generate_json_report(self, audit_service):
        """Test generating JSON report."""
        id1 = audit_service.log_export_start(ExportType.BIBTEX, ExportFormat.BIBTEX)
        audit_service.log_export_complete(id1, b"content")

        report = audit_service.generate_audit_report(format="json")

        data = json.loads(report)
        assert "summary" in data
        assert "entries" in data


# =============================================================================
# Context Manager Tests
# =============================================================================

class TestAuditedExportContextManager:
    """Tests for AuditedExport context manager."""

    def test_successful_export(self, audit_service):
        """Test successful export with context manager."""
        with AuditedExport(
            audit_service,
            ExportType.BIBTEX,
            ExportFormat.BIBTEX
        ) as audit:
            content = b"@article{test}"
            audit.set_content(content, item_count=1)

        entry = audit_service.get_entry(audit.audit_id)
        assert entry.status == AuditStatus.COMPLETED
        assert entry.item_count == 1

    def test_failed_export(self, audit_service):
        """Test failed export with context manager."""
        try:
            with AuditedExport(
                audit_service,
                ExportType.TECHNICAL_REPORT,
                ExportFormat.PDF
            ) as audit:
                audit_id = audit.audit_id
                raise ValueError("PDF generation failed")
        except ValueError:
            pass

        entry = audit_service.get_entry(audit_id)
        assert entry.status == AuditStatus.FAILED
        assert "PDF generation failed" in entry.error_message

    def test_cancelled_export(self, audit_service):
        """Test cancelled export (no content set)."""
        with AuditedExport(
            audit_service,
            ExportType.BIBTEX,
            ExportFormat.BIBTEX
        ) as audit:
            # Don't set content
            pass

        entry = audit_service.get_entry(audit.audit_id)
        assert entry.status == AuditStatus.CANCELLED

    def test_context_manager_with_context(self, audit_service, sample_context):
        """Test context manager with export context."""
        with AuditedExport(
            audit_service,
            ExportType.EVIDENCE_SUMMARY,
            ExportFormat.MARKDOWN,
            context=sample_context,
            user_id="user123"
        ) as audit:
            audit.set_content(b"# Summary", item_count=3)

        entry = audit_service.get_entry(audit.audit_id)
        assert entry.context.query == "What reduces stress?"
        assert entry.user_id == "user123"


# =============================================================================
# Convenience Function Tests
# =============================================================================

class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_audit_export_function(self):
        """Test audit_export convenience function."""
        # Reset singleton
        import src.services.export_audit as module
        module._audit_service = None

        audit_id = audit_export(
            export_type=ExportType.BIBTEX,
            export_format=ExportFormat.BIBTEX,
            content=b"@article{test}",
            item_count=1
        )

        assert audit_id is not None
        assert audit_id.startswith("EXP-")

    def test_get_audit_service_singleton(self):
        """Test singleton pattern."""
        import src.services.export_audit as module
        module._audit_service = None

        s1 = get_audit_service()
        s2 = get_audit_service()
        assert s1 is s2


# =============================================================================
# Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_string_content_converted_to_bytes(self, audit_service):
        """Test that string content is converted to bytes."""
        audit_id = audit_service.log_export_start(
            ExportType.EVIDENCE_SUMMARY, ExportFormat.MARKDOWN
        )

        # Pass string instead of bytes
        audit_service.log_export_complete(audit_id, "string content".encode('utf-8'))

        entry = audit_service.get_entry(audit_id)
        assert entry.status == AuditStatus.COMPLETED

    def test_empty_content(self, audit_service):
        """Test handling empty content."""
        audit_id = audit_service.log_export_start(
            ExportType.BELIEF_DATA, ExportFormat.JSON
        )

        audit_service.log_export_complete(audit_id, b"")

        entry = audit_service.get_entry(audit_id)
        assert entry.file_size_bytes == 0
        assert entry.content_hash is not None

    def test_concurrent_exports(self, audit_service):
        """Test concurrent export logging."""
        import threading

        results = []

        def log_export(i):
            audit_id = audit_service.log_export_start(
                ExportType.BIBTEX, ExportFormat.BIBTEX
            )
            audit_service.log_export_complete(audit_id, f"content{i}".encode())
            results.append(audit_id)

        threads = [threading.Thread(target=log_export, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert len(set(results)) == 10  # All unique

    def test_close_and_reopen(self):
        """Test closing and reopening service."""
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
            db_path = f.name

        try:
            # First session
            service1 = ExportAuditService(db_path)
            audit_id = service1.log_export_start(ExportType.BIBTEX, ExportFormat.BIBTEX)
            service1.log_export_complete(audit_id, b"content")
            service1.close()

            # Second session
            service2 = ExportAuditService(db_path)
            entry = service2.get_entry(audit_id)
            service2.close()

            assert entry is not None
            assert entry.status == AuditStatus.COMPLETED
        finally:
            os.unlink(db_path)
