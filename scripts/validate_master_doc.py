#!/usr/bin/env python3
"""
Smart Book Validator: Dependency-Aware Documentation Consistency Checker

This script reads DEPENDENCY_MANIFEST.json and validates the ATLAS master
documentation for consistency across sections. It checks for:

1. Numeric constants (counts) matching across all sections
2. Stale references to superseded concepts
3. Missing updates when foundational concepts change
4. Undefined concept references

Usage:
    python validate_master_doc.py --mode=validate
    python validate_master_doc.py --mode=report --output=report.md
    python validate_master_doc.py --mode=suggest --diff

Author: Claude Code
Date: 2026-03-03
Version: 1.0
"""

import json
import re
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ViolationSeverity(Enum):
    """Severity levels for validation violations."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class Violation:
    """Represents a single consistency violation."""
    severity: ViolationSeverity
    section: str
    concept: str
    issue_type: str
    message: str
    suggested_fix: Optional[str] = None
    affected_text: Optional[str] = None


@dataclass
class ValidationReport:
    """Complete validation report with violations and summary."""
    violations: List[Violation]
    total_sections_scanned: int
    total_concepts_defined: int
    total_dependencies: int
    manifest_version: str
    timestamp: str


class SmartBookValidator:
    """Main validator class for ATLAS master documentation."""

    def __init__(self, manifest_path: Path, docs_path: Path):
        """
        Initialize validator with paths to manifest and documentation.

        Args:
            manifest_path: Path to DEPENDENCY_MANIFEST.json
            docs_path: Path to directory containing PART_*.md files
        """
        self.manifest_path = manifest_path
        self.docs_path = docs_path
        self.manifest = None
        self.violations: List[Violation] = []
        self.part_files: Dict[str, Path] = {}
        self.section_contents: Dict[str, str] = {}

    def load_manifest(self) -> bool:
        """Load and validate the dependency manifest."""
        try:
            with open(self.manifest_path, 'r') as f:
                self.manifest = json.load(f)
            print(f"✓ Loaded manifest: {self.manifest['document_metadata']['title']}")
            return True
        except FileNotFoundError:
            print(f"✗ Manifest not found: {self.manifest_path}")
            return False
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON in manifest: {e}")
            return False

    def discover_part_files(self) -> bool:
        """Discover all PART_*.md files in documentation directory."""
        try:
            self.part_files = {
                f.stem: f for f in self.docs_path.glob("PART_*.md")
            }
            print(f"✓ Discovered {len(self.part_files)} part files")
            return True
        except Exception as e:
            print(f"✗ Error discovering part files: {e}")
            return False

    def load_section_contents(self) -> bool:
        """Load content of all part files for searching."""
        try:
            for part_name, part_path in self.part_files.items():
                with open(part_path, 'r', encoding='utf-8') as f:
                    self.section_contents[part_name] = f.read()
            print(f"✓ Loaded content from {len(self.section_contents)} files")
            return True
        except Exception as e:
            print(f"✗ Error loading section contents: {e}")
            return False

    def validate_numeric_constants(self) -> int:
        """
        Validate that numeric constants (counts) are consistent across sections.

        Returns:
            Number of violations found
        """
        violations_found = 0
        patterns = self.manifest.get('validation_patterns', {})

        for concept_id, pattern_info in patterns.items():
            concept = self.manifest['concepts'].get(concept_id)
            if not concept or pattern_info.get('description', '').startswith('Indicates'):
                continue

            regex = pattern_info['regex']
            expected_value = pattern_info.get('expected_value')
            flags = pattern_info.get('flags', [])

            if expected_value is None:
                continue

            # Compile regex with appropriate flags
            regex_flags = 0
            if 'case_insensitive' in flags:
                regex_flags |= re.IGNORECASE

            pattern = re.compile(regex, regex_flags)

            # Search across all part files
            found_values: Dict[str, List[str]] = {}

            for part_name, content in self.section_contents.items():
                matches = pattern.findall(content)
                if matches:
                    for match in matches:
                        try:
                            # Extract numeric value if match is a tuple
                            if isinstance(match, tuple):
                                value_str = match[0]
                            else:
                                value_str = match

                            # Try to convert to int
                            value = int(value_str)

                            if value not in found_values:
                                found_values[value] = []
                            found_values[value].append(part_name)
                        except (ValueError, IndexError):
                            continue

            # Check for inconsistencies
            if found_values:
                if len(found_values) > 1:
                    # Multiple different values found
                    canonical = concept.get('canonical_value', expected_value)
                    for value, parts in sorted(found_values.items()):
                        if value != canonical:
                            violation = Violation(
                                severity=ViolationSeverity.CRITICAL,
                                section=', '.join(parts),
                                concept=concept_id,
                                issue_type="COUNT_MISMATCH",
                                message=f"Section(s) {parts} state '{concept_id}' = {value}, "
                                        f"but canonical value from §{concept.get('defined_in', '?')} = {canonical}",
                                suggested_fix=f"Update {', '.join(parts)} to use value {canonical}"
                            )
                            self.violations.append(violation)
                            violations_found += 1

        return violations_found

    def validate_stale_references(self) -> int:
        """
        Check for stale references to superseded concepts.

        Returns:
            Number of violations found
        """
        violations_found = 0

        for concept_id, concept in self.manifest['concepts'].items():
            if concept.get('deprecated'):
                superseded_by = concept.get('superseded_by')
                if not superseded_by:
                    continue

                # Search for uses of deprecated concept
                patterns = self.manifest.get('validation_patterns', {})
                if concept_id not in patterns:
                    continue

                pattern_info = patterns[concept_id]
                regex = pattern_info['regex']
                flags = pattern_info.get('flags', [])

                regex_flags = 0
                if 'case_insensitive' in flags:
                    regex_flags |= re.IGNORECASE

                pattern = re.compile(regex, regex_flags)

                for part_name, content in self.section_contents.items():
                    if pattern.search(content):
                        # Found deprecated concept; check if it acknowledges the deprecation
                        deprecation_acknowledgment = False
                        for ack_word in ['deprecated', 'legacy', 'obsolete', 'note:', 'transition']:
                            if ack_word.lower() in content.lower():
                                deprecation_acknowledgment = True
                                break

                        if not deprecation_acknowledgment:
                            violation = Violation(
                                severity=ViolationSeverity.HIGH,
                                section=part_name,
                                concept=concept_id,
                                issue_type="STALE_REFERENCE",
                                message=f"Section {part_name} uses deprecated concept '{concept_id}' "
                                        f"(superseded by '{superseded_by}') without acknowledgment",
                                suggested_fix=f"Either update to use '{superseded_by}' or add "
                                              f"'deprecated' / 'legacy' acknowledgment. See §48 for transition notes."
                            )
                            self.violations.append(violation)
                            violations_found += 1

        return violations_found

    def validate_undefined_concepts(self) -> int:
        """
        Check for references to concepts that are not defined in the manifest.

        Returns:
            Number of violations found
        """
        violations_found = 0

        # Build set of all defined concepts
        defined_concepts = set(self.manifest['concepts'].keys())

        # Check all section dependencies for references to undefined concepts
        for section_num, section_info in self.manifest.get('section_dependencies', {}).items():
            for concept_id in section_info.get('uses', []):
                if concept_id not in defined_concepts:
                    violation = Violation(
                        severity=ViolationSeverity.HIGH,
                        section=section_num,
                        concept=concept_id,
                        issue_type="UNDEFINED_CONCEPT",
                        message=f"Section {section_num} references undefined concept '{concept_id}'",
                        suggested_fix=f"Either define '{concept_id}' in manifest or remove reference from §{section_num}"
                    )
                    self.violations.append(violation)
                    violations_found += 1

        return violations_found

    def validate_missing_updates(self) -> int:
        """
        Check for sections where a DEFINES has changed but USES may need review.

        This is a heuristic check; changes are flagged for manual review.

        Returns:
            Number of flagged items (not violations, just review requests)
        """
        flagged = 0

        # For each concept that was recently updated
        for concept_id, concept in self.manifest['concepts'].items():
            history = concept.get('update_history', [])
            if len(history) > 1:
                # Concept has been updated; flag all USES for review
                last_update = history[-1]['date']
                uses = concept.get('used_in', [])

                if uses:
                    violation = Violation(
                        severity=ViolationSeverity.MEDIUM,
                        section=', '.join(uses),
                        concept=concept_id,
                        issue_type="REQUIRES_REVIEW",
                        message=f"Concept '{concept_id}' was updated on {last_update}. "
                                f"The following sections may need review: {uses}",
                        suggested_fix="Manually review these sections to ensure they remain consistent "
                                      f"with the updated definition in §{concept.get('defined_in', '?')}"
                    )
                    self.violations.append(violation)
                    flagged += 1

        return flagged

    def validate_dependency_completeness(self) -> int:
        """
        Check that critical concepts are properly tracked in dependencies.

        Returns:
            Number of violations found
        """
        violations_found = 0

        critical_concepts = {
            'T1_5_COUNT': True,
            'CREDENCE_FORMULA_LOGODDS': True,
            'WARRANT_TYPES': True
        }

        for concept_id, is_critical in critical_concepts.items():
            concept = self.manifest['concepts'].get(concept_id)
            if not concept:
                violation = Violation(
                    severity=ViolationSeverity.HIGH,
                    section="MANIFEST",
                    concept=concept_id,
                    issue_type="MISSING_CRITICAL_CONCEPT",
                    message=f"Critical concept '{concept_id}' is missing from manifest",
                    suggested_fix=f"Add '{concept_id}' to concepts section with proper metadata"
                )
                self.violations.append(violation)
                violations_found += 1
            elif not concept.get('defined_in'):
                violation = Violation(
                    severity=ViolationSeverity.MEDIUM,
                    section="MANIFEST",
                    concept=concept_id,
                    issue_type="UNDEFINED_SOURCE",
                    message=f"Concept '{concept_id}' lacks 'defined_in' field",
                    suggested_fix=f"Add 'defined_in' field to concept metadata"
                )
                self.violations.append(violation)
                violations_found += 1

        return violations_found

    def run_all_validations(self) -> ValidationReport:
        """
        Run all validation checks and return consolidated report.

        Returns:
            ValidationReport with all findings
        """
        print("\n" + "="*70)
        print("SMART BOOK VALIDATION REPORT")
        print("="*70 + "\n")

        if not self.load_manifest():
            sys.exit(1)

        if not self.discover_part_files():
            sys.exit(1)

        if not self.load_section_contents():
            sys.exit(1)

        print("\nRunning validation checks...\n")

        violation_counts = {
            "numeric_constants": self.validate_numeric_constants(),
            "stale_references": self.validate_stale_references(),
            "undefined_concepts": self.validate_undefined_concepts(),
            "missing_updates": self.validate_missing_updates(),
            "dependency_completeness": self.validate_dependency_completeness(),
        }

        print(f"\n✓ Validation complete. Found {len(self.violations)} issues.\n")

        return ValidationReport(
            violations=self.violations,
            total_sections_scanned=len(self.section_contents),
            total_concepts_defined=len(self.manifest['concepts']),
            total_dependencies=sum(
                len(s.get('uses', [])) for s in self.manifest.get('section_dependencies', {}).values()
            ),
            manifest_version=self.manifest['document_metadata']['version'],
            timestamp=self.manifest['document_metadata']['last_updated']
        )

    def print_violations(self) -> None:
        """Print violations in human-readable format."""
        if not self.violations:
            print("✓ No violations found!")
            return

        # Group by severity
        by_severity = {}
        for violation in self.violations:
            if violation.severity not in by_severity:
                by_severity[violation.severity] = []
            by_severity[violation.severity].append(violation)

        # Print in order: CRITICAL, HIGH, MEDIUM, LOW, INFO
        severity_order = [
            ViolationSeverity.CRITICAL,
            ViolationSeverity.HIGH,
            ViolationSeverity.MEDIUM,
            ViolationSeverity.LOW,
            ViolationSeverity.INFO
        ]

        for severity in severity_order:
            if severity not in by_severity:
                continue

            violations = by_severity[severity]
            color = {
                ViolationSeverity.CRITICAL: "\033[91m",  # Red
                ViolationSeverity.HIGH: "\033[93m",      # Yellow
                ViolationSeverity.MEDIUM: "\033[96m",    # Cyan
                ViolationSeverity.LOW: "\033[92m",       # Green
                ViolationSeverity.INFO: "\033[97m"       # White
            }.get(severity, "\033[0m")
            reset = "\033[0m"

            print(f"{color}{'─'*70}")
            print(f"{severity.value}: {len(violations)} issue(s)")
            print('─'*70 + reset)

            for i, v in enumerate(violations, 1):
                print(f"\n  [{i}] Section: {v.section}")
                print(f"      Concept: {v.concept}")
                print(f"      Issue: {v.issue_type}")
                print(f"      Message: {v.message}")
                if v.suggested_fix:
                    print(f"      Suggested Fix: {v.suggested_fix}")
                print()

    def generate_markdown_report(self, output_path: Path) -> None:
        """Generate a markdown report of all violations."""
        md_lines = [
            "# Smart Book Validation Report",
            f"\n**Generated**: {self.violations[0] if self.violations else 'N/A'}",
            f"**Manifest Version**: {self.manifest['document_metadata']['version']}",
            f"**Last Updated**: {self.manifest['document_metadata']['last_updated']}",
            f"\n## Summary",
            f"- Total sections scanned: {len(self.section_contents)}",
            f"- Total concepts defined: {len(self.manifest['concepts'])}",
            f"- Total violations found: {len(self.violations)}",
        ]

        # Count by severity
        by_severity = {}
        for v in self.violations:
            if v.severity not in by_severity:
                by_severity[v.severity] = 0
            by_severity[v.severity] += 1

        md_lines.append("\n## Violations by Severity\n")
        for severity in [ViolationSeverity.CRITICAL, ViolationSeverity.HIGH,
                        ViolationSeverity.MEDIUM, ViolationSeverity.LOW, ViolationSeverity.INFO]:
            if severity in by_severity:
                md_lines.append(f"- **{severity.value}**: {by_severity[severity]}")

        # Detailed violations
        md_lines.append("\n## Detailed Violations\n")
        for i, v in enumerate(self.violations, 1):
            md_lines.append(f"### {i}. {v.severity.value}: {v.issue_type}\n")
            md_lines.append(f"- **Section**: {v.section}")
            md_lines.append(f"- **Concept**: {v.concept}")
            md_lines.append(f"- **Message**: {v.message}\n")
            if v.suggested_fix:
                md_lines.append(f"- **Suggested Fix**: {v.suggested_fix}\n")
            md_lines.append("")

        report_content = "\n".join(md_lines)
        with open(output_path, 'w') as f:
            f.write(report_content)
        print(f"✓ Report written to {output_path}")


def main():
    """Main entry point for validator."""
    parser = argparse.ArgumentParser(
        description="Smart Book Validator: Dependency-Aware Documentation Consistency Checker"
    )
    parser.add_argument(
        '--mode',
        choices=['validate', 'report', 'suggest'],
        default='validate',
        help='Validation mode: validate (check-only), report (generate report), suggest (suggest fixes)'
    )
    parser.add_argument(
        '--manifest',
        type=Path,
        default=Path(__file__).parent.parent / 'docs' / 'master_doc_parts' / 'DEPENDENCY_MANIFEST.json',
        help='Path to DEPENDENCY_MANIFEST.json'
    )
    parser.add_argument(
        '--docs',
        type=Path,
        default=Path(__file__).parent.parent / 'docs' / 'master_doc_parts',
        help='Path to directory containing PART_*.md files'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path(__file__).parent.parent / 'docs' / 'VALIDATION_REPORT.md',
        help='Output path for report (--mode=report only)'
    )

    args = parser.parse_args()

    validator = SmartBookValidator(args.manifest, args.docs)
    report = validator.run_all_validations()

    if args.mode == 'validate':
        validator.print_violations()
        sys.exit(0 if len(validator.violations) == 0 else 1)

    elif args.mode == 'report':
        validator.generate_markdown_report(args.output)

    elif args.mode == 'suggest':
        validator.print_violations()
        print("\n" + "="*70)
        print("SUGGESTED ACTIONS")
        print("="*70 + "\n")
        for v in validator.violations:
            if v.suggested_fix:
                print(f"→ {v.section}: {v.suggested_fix}")


if __name__ == '__main__':
    main()
