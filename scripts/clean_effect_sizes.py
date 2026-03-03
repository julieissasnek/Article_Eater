#!/usr/bin/env python
"""
Clean Effect Sizes — Data Quality Cleanup Script
==================================================

Scans all extraction JSON files in data/extractions/ and validates every
effect_size value. Problematic values are quarantined by moving them to
a _original_effect_size field and setting effect_size to null.

Usage:
    # Dry-run mode (default): preview what would be cleaned
    python scripts/clean_effect_sizes.py

    # Dry-run with verbose output
    python scripts/clean_effect_sizes.py --verbose

    # Actually modify files
    python scripts/clean_effect_sizes.py --commit

    # Custom extraction directory
    python scripts/clean_effect_sizes.py --path data/extractions --commit

Dry-run mode shows what would happen without making any changes.
Use --commit to actually modify files.

Date: 2026-03-02
Version: 1.0.0
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.qa.effect_size_validator import EffectSizeValidator, ProblemType


# ═══════════════════════════════════════════════════════════════════
# Setup logging
# ═══════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# Cleanup Logic
# ═══════════════════════════════════════════════════════════════════

class EffectSizeCleanupProcessor:
    """Processes extraction files to clean problematic effect sizes."""

    def __init__(self, validator: EffectSizeValidator, dry_run: bool = True, verbose: bool = False):
        """
        Initialize cleanup processor.

        Args:
            validator: EffectSizeValidator instance
            dry_run: If True, don't modify files
            verbose: If True, print detailed output
        """
        self.validator = validator
        self.dry_run = dry_run
        self.verbose = verbose

        # Statistics
        self.files_processed = 0
        self.files_with_problems = 0
        self.total_findings_checked = 0
        self.total_problems_found = 0
        self.problems_by_type: Dict[str, int] = {}
        self.files_report: List[Dict[str, Any]] = []

    def clean_file(self, filepath: Path) -> bool:
        """
        Clean effect sizes in a single file.

        Args:
            filepath: Path to extraction JSON file

        Returns:
            True if file had problems, False otherwise
        """

        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to read {filepath}: {e}")
            return False

        # Handle both dict and list formats
        if isinstance(data, list):
            findings = data
        elif isinstance(data, dict):
            findings = data.get("findings", [])
        else:
            return False
        if not findings:
            return False

        had_problems = False
        problems_in_file = []

        for i, finding in enumerate(findings):
            effect_size = finding.get("effect_size")
            measure_type = finding.get("effect_size_type")

            self.total_findings_checked += 1

            # Validate
            result = self.validator.validate_effect_size(effect_size, measure_type)

            if not result.is_valid:
                had_problems = True
                self.total_problems_found += 1
                problem_type = result.problem_type.value
                self.problems_by_type[problem_type] = (
                    self.problems_by_type.get(problem_type, 0) + 1
                )

                # Record the problem
                problem_record = {
                    "finding_index": i,
                    "original_effect_size": effect_size,
                    "effect_size_type": measure_type,
                    "problem_type": problem_type,
                    "message": result.message,
                }
                problems_in_file.append(problem_record)

                # Quarantine the value
                if not self.dry_run:
                    finding["_original_effect_size"] = effect_size
                    finding["_quarantine_reason"] = result.message
                    finding["effect_size"] = None

        if had_problems:
            self.files_with_problems += 1
            self.files_report.append({
                "file": str(filepath.name),
                "problems_count": len(problems_in_file),
                "problems": problems_in_file,
            })

            if self.verbose or self.dry_run:
                logger.info(f"\n{'='*70}")
                logger.info(f"File: {filepath.name}")
                logger.info(f"Problems found: {len(problems_in_file)}")
                for problem in problems_in_file:
                    logger.info(f"  [{problem['finding_index']}] {problem['problem_type']}: "
                              f"{problem['original_effect_size']} "
                              f"({problem['effect_size_type']})")
                    logger.info(f"       → {problem['message']}")

            # Write modified file if not dry-run
            if not self.dry_run:
                try:
                    with open(filepath, 'w') as f:
                        if isinstance(data, list):
                            json.dump(data, f, indent=2)
                        else:
                            json.dump(data, f, indent=2)
                    logger.info(f"✓ Cleaned: {filepath.name}")
                except Exception as e:
                    logger.error(f"Failed to write {filepath}: {e}")

        return had_problems

    def process_directory(self, directory: Path) -> None:
        """
        Process all extraction files in a directory.

        Args:
            directory: Path to directory containing extraction JSON files
        """

        if not directory.is_dir():
            logger.error(f"Directory not found: {directory}")
            return

        json_files = sorted(directory.glob("*.json"))
        logger.info(f"Found {len(json_files)} extraction files to process")
        logger.info(f"Mode: {'DRY-RUN' if self.dry_run else 'COMMIT'}")
        logger.info("")

        for filepath in json_files:
            self.files_processed += 1
            self.clean_file(filepath)

    def report(self) -> str:
        """
        Generate cleanup report.

        Returns:
            Human-readable report string
        """

        lines = [
            "",
            "=" * 70,
            "EFFECT SIZE CLEANUP REPORT",
            "=" * 70,
            "",
            f"Mode: {'DRY-RUN' if self.dry_run else 'COMMIT'}",
            f"Files processed: {self.files_processed}",
            f"Files with problems: {self.files_with_problems}",
            f"Total findings checked: {self.total_findings_checked}",
            f"Total problems found: {self.total_problems_found}",
            "",
        ]

        if self.problems_by_type:
            lines.append("Problems by type:")
            for ptype, count in sorted(self.problems_by_type.items(), key=lambda x: -x[1]):
                lines.append(f"  - {ptype}: {count}")
            lines.append("")

        if self.files_with_problems > 0:
            lines.append(f"Files needing attention: {self.files_with_problems}")
            for file_record in self.files_report[:10]:  # Show first 10
                lines.append(f"  • {file_record['file']}: {file_record['problems_count']} problems")

            if len(self.files_report) > 10:
                lines.append(f"  ... and {len(self.files_report) - 10} more files")
        else:
            lines.append("No problems found! All effect sizes are valid.")

        lines.append("")

        if self.dry_run:
            lines.append("DRY-RUN: No files were modified.")
            lines.append("Run with --commit to actually clean the data.")
        else:
            lines.append(f"✓ Cleaned {self.files_with_problems} file(s)")

        lines.extend([
            "=" * 70,
            "",
        ])

        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

def main():
    """Run cleanup script."""

    parser = argparse.ArgumentParser(
        description="Clean problematic effect sizes from extraction data"
    )
    parser.add_argument(
        "--path",
        default="data/extractions",
        help="Path to extraction directory (default: data/extractions)"
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        default=False,
        help="Actually modify files (default: dry-run mode)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Print detailed output"
    )

    args = parser.parse_args()

    # Resolve paths
    project_root = Path(__file__).resolve().parent.parent
    extraction_dir = project_root / args.path

    if not extraction_dir.is_dir():
        logger.error(f"Extraction directory not found: {extraction_dir}")
        sys.exit(1)

    # Create validator and processor
    validator = EffectSizeValidator()
    processor = EffectSizeCleanupProcessor(
        validator=validator,
        dry_run=not args.commit,
        verbose=args.verbose
    )

    # Process files
    processor.process_directory(extraction_dir)

    # Print report
    print(processor.report())

    # Exit with error code if problems found and not committed
    if processor.total_problems_found > 0 and not args.commit:
        sys.exit(1)  # Indicate that problems were found


if __name__ == "__main__":
    main()
