"""
Verification Checklists — Sprint 3.0.4-C
2026-02-09

Provides Gawande-style checklists for evidence verification, extraction
quality, and review processes. Checklists reduce errors and ensure
consistent evaluation.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class ChecklistType(Enum):
    """Types of checklists."""
    EVIDENCE_VERIFICATION = "evidence_verification"
    EXTRACTION_QUALITY = "extraction_quality"
    METHODOLOGY_REVIEW = "methodology_review"
    SCOPE_ASSESSMENT = "scope_assessment"
    CLAIM_VALIDATION = "claim_validation"
    PAPER_INTAKE = "paper_intake"
    PRE_EXPORT = "pre_export"
    CONFLICT_RESOLUTION = "conflict_resolution"


class CheckStatus(Enum):
    """Status of a checklist item."""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    NOT_APPLICABLE = "not_applicable"


class CheckSeverity(Enum):
    """Severity level of a check."""
    CRITICAL = "critical"      # Must pass or abort
    REQUIRED = "required"      # Must pass for approval
    RECOMMENDED = "recommended"  # Should pass
    OPTIONAL = "optional"      # Nice to have


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class CheckItem:
    """A single checklist item."""
    check_id: str
    description: str
    severity: CheckSeverity = CheckSeverity.REQUIRED
    category: Optional[str] = None

    status: CheckStatus = CheckStatus.PENDING
    result: Optional[str] = None
    checked_at: Optional[str] = None
    checked_by: Optional[str] = None

    # For automated checks
    auto_check: bool = False
    auto_check_fn: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_id": self.check_id,
            "description": self.description,
            "severity": self.severity.value,
            "category": self.category,
            "status": self.status.value,
            "result": self.result,
            "checked_at": self.checked_at,
            "checked_by": self.checked_by,
            "auto_check": self.auto_check
        }

    def mark_passed(self, result: Optional[str] = None, by: str = "system"):
        """Mark check as passed."""
        self.status = CheckStatus.PASSED
        self.result = result
        self.checked_at = datetime.now(timezone.utc).isoformat()
        self.checked_by = by

    def mark_failed(self, result: str, by: str = "system"):
        """Mark check as failed."""
        self.status = CheckStatus.FAILED
        self.result = result
        self.checked_at = datetime.now(timezone.utc).isoformat()
        self.checked_by = by

    def mark_skipped(self, reason: str, by: str = "system"):
        """Mark check as skipped."""
        self.status = CheckStatus.SKIPPED
        self.result = reason
        self.checked_at = datetime.now(timezone.utc).isoformat()
        self.checked_by = by


@dataclass
class Checklist:
    """A complete checklist with multiple items."""
    checklist_id: str
    checklist_type: ChecklistType
    title: str
    description: Optional[str] = None

    items: List[CheckItem] = field(default_factory=list)

    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    overall_status: CheckStatus = CheckStatus.PENDING

    # Context
    target_id: Optional[str] = None  # belief_id, paper_id, etc.
    target_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checklist_id": self.checklist_id,
            "checklist_type": self.checklist_type.value,
            "title": self.title,
            "description": self.description,
            "items": [item.to_dict() for item in self.items],
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "overall_status": self.overall_status.value,
            "target_id": self.target_id,
            "target_type": self.target_type,
            "summary": self.get_summary()
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def add_item(self, item: CheckItem):
        """Add a check item."""
        self.items.append(item)

    def get_item(self, check_id: str) -> Optional[CheckItem]:
        """Get item by ID."""
        for item in self.items:
            if item.check_id == check_id:
                return item
        return None

    def get_summary(self) -> Dict[str, int]:
        """Get summary counts by status."""
        summary = {s.value: 0 for s in CheckStatus}
        for item in self.items:
            summary[item.status.value] += 1
        return summary

    def is_complete(self) -> bool:
        """Check if all items have been evaluated."""
        return all(item.status != CheckStatus.PENDING for item in self.items)

    def is_approved(self) -> bool:
        """Check if checklist passes (no critical/required failures)."""
        for item in self.items:
            if item.status == CheckStatus.FAILED:
                if item.severity in [CheckSeverity.CRITICAL, CheckSeverity.REQUIRED]:
                    return False
        return True

    def get_failures(self) -> List[CheckItem]:
        """Get all failed items."""
        return [item for item in self.items if item.status == CheckStatus.FAILED]

    def complete(self):
        """Mark checklist as complete and set overall status."""
        self.completed_at = datetime.now(timezone.utc).isoformat()

        if not self.is_complete():
            self.overall_status = CheckStatus.PENDING
        elif self.is_approved():
            self.overall_status = CheckStatus.PASSED
        else:
            self.overall_status = CheckStatus.FAILED

    def to_markdown(self) -> str:
        """Generate markdown representation."""
        lines = [f"# {self.title}"]

        if self.description:
            lines.append(f"\n{self.description}\n")

        lines.append(f"\n**Status**: {self.overall_status.value.title()}")
        lines.append(f"**Created**: {self.created_at[:10]}")

        if self.completed_at:
            lines.append(f"**Completed**: {self.completed_at[:10]}")

        lines.append("\n## Checklist Items\n")

        # Group by category
        categories: Dict[str, List[CheckItem]] = {}
        for item in self.items:
            cat = item.category or "General"
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item)

        for category, items in categories.items():
            lines.append(f"### {category}\n")

            for item in items:
                status_icon = {
                    CheckStatus.PASSED: "[x]",
                    CheckStatus.FAILED: "[!]",
                    CheckStatus.SKIPPED: "[-]",
                    CheckStatus.PENDING: "[ ]",
                    CheckStatus.NOT_APPLICABLE: "[N/A]"
                }.get(item.status, "[ ]")

                severity_marker = ""
                if item.severity == CheckSeverity.CRITICAL:
                    severity_marker = " **CRITICAL**"
                elif item.severity == CheckSeverity.REQUIRED:
                    severity_marker = " *Required*"

                lines.append(f"- {status_icon} {item.description}{severity_marker}")

                if item.result and item.status in [CheckStatus.FAILED, CheckStatus.SKIPPED]:
                    lines.append(f"  - *{item.result}*")

            lines.append("")

        # Summary
        summary = self.get_summary()
        lines.append("## Summary\n")
        lines.append(f"- Passed: {summary['passed']}")
        lines.append(f"- Failed: {summary['failed']}")
        lines.append(f"- Skipped: {summary['skipped']}")
        lines.append(f"- Pending: {summary['pending']}")

        return "\n".join(lines)


# =============================================================================
# Checklist Templates
# =============================================================================

class ChecklistTemplates:
    """
    Pre-defined checklist templates for common verification tasks.
    Based on Gawande's checklist principles.
    """

    @staticmethod
    def evidence_verification(target_id: Optional[str] = None) -> Checklist:
        """
        Checklist for verifying evidence quality.

        Used when evaluating whether a finding should be trusted.
        """
        checklist = Checklist(
            checklist_id=f"ev-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            checklist_type=ChecklistType.EVIDENCE_VERIFICATION,
            title="Evidence Verification Checklist",
            description="Verify evidence quality before incorporating into the web of belief.",
            target_id=target_id,
            target_type="belief"
        )

        # Source quality
        checklist.add_item(CheckItem(
            "ev-01", "Source paper is peer-reviewed",
            CheckSeverity.REQUIRED, "Source Quality"
        ))
        checklist.add_item(CheckItem(
            "ev-02", "Authors have relevant expertise",
            CheckSeverity.RECOMMENDED, "Source Quality"
        ))
        checklist.add_item(CheckItem(
            "ev-03", "No obvious conflicts of interest",
            CheckSeverity.REQUIRED, "Source Quality"
        ))

        # Methodology
        checklist.add_item(CheckItem(
            "ev-04", "Methodology clearly described",
            CheckSeverity.REQUIRED, "Methodology"
        ))
        checklist.add_item(CheckItem(
            "ev-05", "Sample size adequate for claims",
            CheckSeverity.REQUIRED, "Methodology"
        ))
        checklist.add_item(CheckItem(
            "ev-06", "Statistical analysis appropriate",
            CheckSeverity.REQUIRED, "Methodology"
        ))
        checklist.add_item(CheckItem(
            "ev-07", "Control conditions present (if applicable)",
            CheckSeverity.RECOMMENDED, "Methodology"
        ))

        # Replication
        checklist.add_item(CheckItem(
            "ev-08", "Finding has been replicated",
            CheckSeverity.RECOMMENDED, "Replication"
        ))
        checklist.add_item(CheckItem(
            "ev-09", "No known failed replications",
            CheckSeverity.REQUIRED, "Replication"
        ))

        # Scope
        checklist.add_item(CheckItem(
            "ev-10", "Scope conditions clearly stated",
            CheckSeverity.REQUIRED, "Scope"
        ))
        checklist.add_item(CheckItem(
            "ev-11", "Generalization claims justified",
            CheckSeverity.RECOMMENDED, "Scope"
        ))

        return checklist

    @staticmethod
    def extraction_quality(target_id: Optional[str] = None) -> Checklist:
        """
        Checklist for extraction quality assurance.

        Used when reviewing AI extraction output.
        """
        checklist = Checklist(
            checklist_id=f"eq-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            checklist_type=ChecklistType.EXTRACTION_QUALITY,
            title="Extraction Quality Checklist",
            description="Verify extraction accuracy before acceptance.",
            target_id=target_id,
            target_type="extraction"
        )

        # Accuracy
        checklist.add_item(CheckItem(
            "eq-01", "Claim accurately reflects source text",
            CheckSeverity.CRITICAL, "Accuracy"
        ))
        checklist.add_item(CheckItem(
            "eq-02", "No fabricated information added",
            CheckSeverity.CRITICAL, "Accuracy"
        ))
        checklist.add_item(CheckItem(
            "eq-03", "Numerical values correctly extracted",
            CheckSeverity.REQUIRED, "Accuracy"
        ))

        # Completeness
        checklist.add_item(CheckItem(
            "eq-04", "Key findings captured",
            CheckSeverity.REQUIRED, "Completeness"
        ))
        checklist.add_item(CheckItem(
            "eq-05", "Limitations mentioned in source included",
            CheckSeverity.RECOMMENDED, "Completeness"
        ))

        # Classification
        checklist.add_item(CheckItem(
            "eq-06", "Epistemic level correctly assigned",
            CheckSeverity.REQUIRED, "Classification"
        ))
        checklist.add_item(CheckItem(
            "eq-07", "Theory association correct",
            CheckSeverity.REQUIRED, "Classification"
        ))
        checklist.add_item(CheckItem(
            "eq-08", "Credence appropriately calibrated",
            CheckSeverity.REQUIRED, "Classification"
        ))

        # Formatting
        checklist.add_item(CheckItem(
            "eq-09", "Claim is self-contained",
            CheckSeverity.RECOMMENDED, "Formatting"
        ))
        checklist.add_item(CheckItem(
            "eq-10", "No ambiguous pronouns or references",
            CheckSeverity.RECOMMENDED, "Formatting"
        ))

        return checklist

    @staticmethod
    def methodology_review(target_id: Optional[str] = None) -> Checklist:
        """
        Checklist for methodology assessment.

        Used when evaluating study design.
        """
        checklist = Checklist(
            checklist_id=f"mr-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            checklist_type=ChecklistType.METHODOLOGY_REVIEW,
            title="Methodology Review Checklist",
            description="Assess methodological rigor of the source study.",
            target_id=target_id,
            target_type="paper"
        )

        # Design
        checklist.add_item(CheckItem(
            "mr-01", "Study design appropriate for research question",
            CheckSeverity.CRITICAL, "Design"
        ))
        checklist.add_item(CheckItem(
            "mr-02", "Randomization used (if experimental)",
            CheckSeverity.REQUIRED, "Design"
        ))
        checklist.add_item(CheckItem(
            "mr-03", "Blinding implemented where possible",
            CheckSeverity.RECOMMENDED, "Design"
        ))

        # Sampling
        checklist.add_item(CheckItem(
            "mr-04", "Sampling method described",
            CheckSeverity.REQUIRED, "Sampling"
        ))
        checklist.add_item(CheckItem(
            "mr-05", "Sample representative of target population",
            CheckSeverity.REQUIRED, "Sampling"
        ))
        checklist.add_item(CheckItem(
            "mr-06", "Power analysis conducted",
            CheckSeverity.RECOMMENDED, "Sampling"
        ))

        # Measurement
        checklist.add_item(CheckItem(
            "mr-07", "Measures validated",
            CheckSeverity.REQUIRED, "Measurement"
        ))
        checklist.add_item(CheckItem(
            "mr-08", "Reliability reported",
            CheckSeverity.RECOMMENDED, "Measurement"
        ))

        # Analysis
        checklist.add_item(CheckItem(
            "mr-09", "Statistical methods appropriate",
            CheckSeverity.REQUIRED, "Analysis"
        ))
        checklist.add_item(CheckItem(
            "mr-10", "Effect sizes reported",
            CheckSeverity.REQUIRED, "Analysis"
        ))
        checklist.add_item(CheckItem(
            "mr-11", "Confidence intervals provided",
            CheckSeverity.RECOMMENDED, "Analysis"
        ))

        return checklist

    @staticmethod
    def scope_assessment(target_id: Optional[str] = None) -> Checklist:
        """
        Checklist for scope condition assessment.

        Based on Cartwright's capacities framework.
        """
        checklist = Checklist(
            checklist_id=f"sa-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            checklist_type=ChecklistType.SCOPE_ASSESSMENT,
            title="Scope Assessment Checklist",
            description="Assess transferability and scope conditions per Cartwright.",
            target_id=target_id,
            target_type="belief"
        )

        # Population
        checklist.add_item(CheckItem(
            "sa-01", "Target population clearly specified",
            CheckSeverity.REQUIRED, "Population"
        ))
        checklist.add_item(CheckItem(
            "sa-02", "Sample demographics reported",
            CheckSeverity.REQUIRED, "Population"
        ))
        checklist.add_item(CheckItem(
            "sa-03", "Population boundaries acknowledged",
            CheckSeverity.RECOMMENDED, "Population"
        ))

        # Context
        checklist.add_item(CheckItem(
            "sa-04", "Study setting described",
            CheckSeverity.REQUIRED, "Context"
        ))
        checklist.add_item(CheckItem(
            "sa-05", "Cultural context considered",
            CheckSeverity.RECOMMENDED, "Context"
        ))
        checklist.add_item(CheckItem(
            "sa-06", "Temporal validity assessed",
            CheckSeverity.RECOMMENDED, "Context"
        ))

        # Enabling conditions
        checklist.add_item(CheckItem(
            "sa-07", "Enabling conditions identified",
            CheckSeverity.REQUIRED, "Enabling Conditions"
        ))
        checklist.add_item(CheckItem(
            "sa-08", "Boundary conditions noted",
            CheckSeverity.REQUIRED, "Enabling Conditions"
        ))
        checklist.add_item(CheckItem(
            "sa-09", "Moderating factors documented",
            CheckSeverity.RECOMMENDED, "Enabling Conditions"
        ))

        # Transferability
        checklist.add_item(CheckItem(
            "sa-10", "Generalization risk assessed",
            CheckSeverity.REQUIRED, "Transferability"
        ))
        checklist.add_item(CheckItem(
            "sa-11", "Context sensitivity evaluated",
            CheckSeverity.RECOMMENDED, "Transferability"
        ))

        return checklist

    @staticmethod
    def paper_intake(target_id: Optional[str] = None) -> Checklist:
        """
        Checklist for paper intake/ingestion.

        Pre-processing checks before extraction.
        """
        checklist = Checklist(
            checklist_id=f"pi-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            checklist_type=ChecklistType.PAPER_INTAKE,
            title="Paper Intake Checklist",
            description="Verify paper is suitable for processing.",
            target_id=target_id,
            target_type="paper"
        )

        # Basic requirements
        checklist.add_item(CheckItem(
            "pi-01", "PDF readable and complete",
            CheckSeverity.CRITICAL, "Basic Requirements"
        ))
        checklist.add_item(CheckItem(
            "pi-02", "Paper in English or supported language",
            CheckSeverity.CRITICAL, "Basic Requirements"
        ))
        checklist.add_item(CheckItem(
            "pi-03", "Metadata available (title, authors, year)",
            CheckSeverity.REQUIRED, "Basic Requirements"
        ))

        # Relevance
        checklist.add_item(CheckItem(
            "pi-04", "Paper is relevant to domain",
            CheckSeverity.REQUIRED, "Relevance"
        ))
        checklist.add_item(CheckItem(
            "pi-05", "Paper type suitable for extraction",
            CheckSeverity.REQUIRED, "Relevance"
        ))

        # Duplicates
        checklist.add_item(CheckItem(
            "pi-06", "Not a duplicate of existing paper",
            CheckSeverity.REQUIRED, "Deduplication"
        ))
        checklist.add_item(CheckItem(
            "pi-07", "Not superseded by newer version",
            CheckSeverity.RECOMMENDED, "Deduplication"
        ))

        return checklist

    @staticmethod
    def pre_export(target_id: Optional[str] = None) -> Checklist:
        """
        Checklist before exporting results.

        Final quality gate before delivery.
        """
        checklist = Checklist(
            checklist_id=f"pe-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            checklist_type=ChecklistType.PRE_EXPORT,
            title="Pre-Export Checklist",
            description="Final verification before exporting results.",
            target_id=target_id,
            target_type="export"
        )

        # Data quality
        checklist.add_item(CheckItem(
            "pe-01", "All records validated",
            CheckSeverity.REQUIRED, "Data Quality"
        ))
        checklist.add_item(CheckItem(
            "pe-02", "No incomplete records",
            CheckSeverity.REQUIRED, "Data Quality"
        ))
        checklist.add_item(CheckItem(
            "pe-03", "Credence values in valid range",
            CheckSeverity.REQUIRED, "Data Quality"
        ))

        # Completeness
        checklist.add_item(CheckItem(
            "pe-04", "All requested fields included",
            CheckSeverity.REQUIRED, "Completeness"
        ))
        checklist.add_item(CheckItem(
            "pe-05", "Provenance information attached",
            CheckSeverity.RECOMMENDED, "Completeness"
        ))

        # Format
        checklist.add_item(CheckItem(
            "pe-06", "Output format correct",
            CheckSeverity.CRITICAL, "Format"
        ))
        checklist.add_item(CheckItem(
            "pe-07", "Encoding is UTF-8",
            CheckSeverity.REQUIRED, "Format"
        ))

        return checklist


# =============================================================================
# Checklist Runner
# =============================================================================

class ChecklistRunner:
    """
    Runs checklists with optional automated checks.

    Supports both manual and automated verification.
    """

    def __init__(self):
        self.auto_checks: Dict[str, Callable] = {}

    def register_auto_check(self, check_id: str, fn: Callable[[Any], bool]):
        """Register an automated check function."""
        self.auto_checks[check_id] = fn

    def run_auto_checks(self, checklist: Checklist, context: Any = None) -> int:
        """
        Run all registered automated checks.

        Returns number of checks run.
        """
        count = 0
        for item in checklist.items:
            if item.auto_check and item.check_id in self.auto_checks:
                try:
                    fn = self.auto_checks[item.check_id]
                    result = fn(context)
                    if result:
                        item.mark_passed("Automated check passed")
                    else:
                        item.mark_failed("Automated check failed")
                    count += 1
                except Exception as e:
                    item.mark_failed(f"Check error: {str(e)}")
                    count += 1
        return count

    def validate_checklist(self, checklist: Checklist) -> Dict[str, Any]:
        """
        Validate a completed checklist.

        Returns validation summary.
        """
        failures = checklist.get_failures()
        critical_failures = [f for f in failures if f.severity == CheckSeverity.CRITICAL]
        required_failures = [f for f in failures if f.severity == CheckSeverity.REQUIRED]

        return {
            "is_complete": checklist.is_complete(),
            "is_approved": checklist.is_approved(),
            "total_items": len(checklist.items),
            "passed": len([i for i in checklist.items if i.status == CheckStatus.PASSED]),
            "failed": len(failures),
            "critical_failures": len(critical_failures),
            "required_failures": len(required_failures),
            "pending": len([i for i in checklist.items if i.status == CheckStatus.PENDING]),
            "failure_details": [f.to_dict() for f in failures]
        }


# =============================================================================
# Convenience Functions
# =============================================================================

def create_evidence_checklist(belief_id: Optional[str] = None) -> Checklist:
    """Create evidence verification checklist."""
    return ChecklistTemplates.evidence_verification(belief_id)


def create_extraction_checklist(extraction_id: Optional[str] = None) -> Checklist:
    """Create extraction quality checklist."""
    return ChecklistTemplates.extraction_quality(extraction_id)


def create_methodology_checklist(paper_id: Optional[str] = None) -> Checklist:
    """Create methodology review checklist."""
    return ChecklistTemplates.methodology_review(paper_id)


def create_scope_checklist(belief_id: Optional[str] = None) -> Checklist:
    """Create scope assessment checklist."""
    return ChecklistTemplates.scope_assessment(belief_id)


def create_intake_checklist(paper_id: Optional[str] = None) -> Checklist:
    """Create paper intake checklist."""
    return ChecklistTemplates.paper_intake(paper_id)


def create_export_checklist(export_id: Optional[str] = None) -> Checklist:
    """Create pre-export checklist."""
    return ChecklistTemplates.pre_export(export_id)
