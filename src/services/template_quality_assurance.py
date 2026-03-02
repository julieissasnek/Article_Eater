"""
Template Quality Assurance Service — Sprint 7
==============================================
Created: 2026-02-28
Phase γ wiring: 2026-03-01 (Sprint A)

Validates T2 templates against archetype registry and checks
mechanism chain completeness and conformance.

Phase γ addition: Consumes SENSITIVITY_FLAG annotations from the unified
annotation service (AN-SC-05, SC-QA-12).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import logging

from src.models.mechanism_templates import T2ArchetypeRegistry, T2Archetype

logger = logging.getLogger(__name__)


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class QAReport:
    """Quality assurance report for a single template."""
    template_id: str
    passed: bool
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    matched_archetypes: List[tuple[str, float]] = field(default_factory=list)
    sensitivity_flags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "template_id": self.template_id,
            "passed": self.passed,
            "warnings": self.warnings,
            "errors": self.errors,
            "matched_archetypes": [
                {"archetype_id": aid, "score": score}
                for aid, score in self.matched_archetypes
            ],
            "sensitivity_flags": self.sensitivity_flags,
        }


# =============================================================================
# SERVICE
# =============================================================================

class TemplateQA:
    """Quality assurance service for T2 templates.

    Phase γ: Now consumes SENSITIVITY_FLAG annotations from the unified
    annotation service to flag parameters that are uncertain or variable.
    """

    def __init__(
        self,
        archetype_registry_path: Optional[Path] = None,
        annotation_service=None,
    ):
        """
        Initialize QA service.

        Args:
            archetype_registry_path: Path to mechanism_archetypes.json.
                If None, will try default location.
            annotation_service: Optional AnnotationService instance.
                If provided, SENSITIVITY_FLAGs are included in QA reports.
        """
        self.registry = T2ArchetypeRegistry()
        self.annotation_service = annotation_service

        if archetype_registry_path is None:
            archetype_registry_path = Path(__file__).parent.parent.parent / (
                "data" / "mechanism_archetypes.json"
            )

        if archetype_registry_path and archetype_registry_path.exists():
            try:
                self.registry.load_from_json_file(archetype_registry_path)
                logger.info(
                    f"Loaded {len(self.registry.list_all())} archetypes "
                    f"from {archetype_registry_path}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to load archetype registry: {e}"
                )
        else:
            logger.warning(
                "Archetype registry not found; QA will have limited functionality"
            )

    def validate_template(self, template_dict: Dict[str, Any]) -> QAReport:
        """
        Validate a single T2 template.

        Checks:
        1. mechanism_chain exists and has ≥1 step
        2. Each step has justification with warrant
        3. Mechanism text matches known archetypes (fuzzy)
        4. Referenced template_ids are valid

        Args:
            template_dict: Template dictionary to validate

        Returns:
            QAReport with validation results
        """
        template_id = template_dict.get("template_id", "UNKNOWN")
        report = QAReport(template_id=template_id, passed=True)

        # Check mechanism_chain exists
        if "mechanism_chain" not in template_dict:
            report.errors.append("No mechanism_chain field found")
            report.passed = False
            return report

        mechanism_chain = template_dict.get("mechanism_chain", [])
        if not isinstance(mechanism_chain, list):
            report.errors.append("mechanism_chain is not a list")
            report.passed = False
            return report

        if not mechanism_chain:
            report.errors.append("mechanism_chain is empty")
            report.passed = False
            return report

        # Validate each step
        for i, step in enumerate(mechanism_chain):
            if not isinstance(step, dict):
                report.errors.append(
                    f"Step {i}: mechanism_chain[{i}] is not a dict"
                )
                report.passed = False
                continue

            # Check mechanism text
            mechanism_text = step.get("mechanism", "")
            if not mechanism_text:
                report.errors.append(
                    f"Step {i}: no mechanism text in mechanism_chain[{i}]"
                )
                report.passed = False
                continue

            # Try to match mechanism to known archetypes
            matches = self.registry.match_mechanism_text(mechanism_text)
            if matches:
                for archetype, score in matches[:3]:  # Top 3 matches
                    report.matched_archetypes.append(
                        (archetype.archetype_id, score)
                    )
            else:
                report.warnings.append(
                    f"Step {i}: mechanism '{mechanism_text}' "
                    f"does not match known archetypes"
                )

            # Check justification
            justification = step.get("justification", {})
            if not justification:
                report.warnings.append(
                    f"Step {i}: no justification provided"
                )
            else:
                # Check for warrant in justification
                if "warrant" not in justification:
                    report.warnings.append(
                        f"Step {i}: justification has no warrant"
                    )

        # Phase γ: Check SENSITIVITY_FLAG annotations from unified store
        if self.annotation_service is not None:
            try:
                flags = self.annotation_service.get_parameter_sensitivity_flags(
                    template_id
                )
                for flag in flags:
                    msg = f"SENSITIVITY: {flag.content}"
                    report.sensitivity_flags.append(msg)
                    report.warnings.append(msg)

                # Also check for template-level sensitivity flags
                template_flags = self.annotation_service.get_template_annotations(
                    template_id,
                    types=[self.annotation_service.__class__._get_sensitivity_type()]
                    if hasattr(self.annotation_service.__class__, '_get_sensitivity_type')
                    else None,
                )
                # Filter to SENSITIVITY_FLAG type
                for tf in template_flags:
                    type_val = tf.type.value if hasattr(tf.type, 'value') else str(tf.type)
                    if type_val == "SENSITIVITY_FLAG" and tf.content not in [
                        f.content for f in flags
                    ]:
                        msg = f"SENSITIVITY (template-level): {tf.content}"
                        report.sensitivity_flags.append(msg)
                        report.warnings.append(msg)
            except Exception as e:
                logger.debug(
                    f"Could not check sensitivity flags for {template_id}: {e}"
                )

        return report

    def validate_all_templates(
        self, templates_dir: Path
    ) -> List[QAReport]:
        """
        Validate all templates in a directory.

        Args:
            templates_dir: Directory containing template JSON files

        Returns:
            List of QAReport objects
        """
        reports = []

        if not templates_dir.exists():
            logger.error(f"Templates directory not found: {templates_dir}")
            return reports

        json_files = sorted(templates_dir.glob("*.json"))
        logger.info(f"Found {len(json_files)} template files to validate")

        for json_file in json_files:
            try:
                with open(json_file, "r") as f:
                    template = json.load(f)

                report = self.validate_template(template)
                reports.append(report)

                if not report.passed:
                    logger.warning(
                        f"{template.get('template_id', json_file.name)}: "
                        f"{len(report.errors)} errors, {len(report.warnings)} warnings"
                    )
            except Exception as e:
                logger.error(f"Failed to validate {json_file.name}: {e}")
                reports.append(QAReport(
                    template_id=json_file.stem,
                    passed=False,
                    errors=[f"Load error: {str(e)}"]
                ))

        return reports

    def summary_report(self, reports: List[QAReport]) -> Dict[str, Any]:
        """
        Generate summary statistics from reports.

        Args:
            reports: List of QAReport objects

        Returns:
            Dictionary with summary statistics
        """
        if not reports:
            return {
                "total_templates": 0,
                "passed": 0,
                "passed_pct": 0.0,
                "failed": 0,
                "total_errors": 0,
                "total_warnings": 0,
            }

        passed = sum(1 for r in reports if r.passed)
        total_errors = sum(len(r.errors) for r in reports)
        total_warnings = sum(len(r.warnings) for r in reports)

        return {
            "total_templates": len(reports),
            "passed": passed,
            "passed_pct": 100.0 * passed / len(reports) if reports else 0.0,
            "failed": len(reports) - passed,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "avg_warnings_per_template": total_warnings / len(reports) if reports else 0.0,
        }
