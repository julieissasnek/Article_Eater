#!/usr/bin/env python3
"""
Expert Calibration Preparation Script

Generates a calibration worksheet for expert review of warrant assignments.

Purpose:
    Prepares extraction data for expert panel review by:
    1. Loading all extraction claims
    2. Grouping by warrant type (canonical names)
    3. Selecting representative samples per warrant type
    4. Prioritizing claims with highest variance/uncertainty
    5. Generating a structured calibration worksheet

Output:
    JSON file at data/calibration/expert_calibration_prep_{DATE}.json
    Contains:
    - Warrant type distribution
    - Sample claims per type (up to 5 per type)
    - Structured questions for expert review

Usage:
    python scripts/expert_calibration_prep.py [--n-samples 5] [--output-dir data/calibration]

Author: Claude Code (ATLAS Sprint 6)
Date: 2026-02-28
Version: 1.0.0
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CALIBRATION] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

DATA_DIR = PROJECT_ROOT / "data"
CALIBRATION_DIR = DATA_DIR / "calibration"


class ExpertCalibrationPrep:
    """Prepares extraction data for expert panel calibration."""

    CANONICAL_WARRANT_TYPES = [
        "CONSTITUTIVE",
        "MECHANISM",
        "EMPIRICAL_ASSOCIATION",
        "FUNCTIONAL",
        "CAPACITY",
        "ANALOGICAL",
        "THEORY_DERIVED",
    ]

    def __init__(self, extractions_dir: Path, n_samples: int = 5):
        """
        Initialize calibration prep.

        Args:
            extractions_dir: Path to extraction JSON files
            n_samples: Number of sample claims per warrant type (default: 5)
        """
        self.extractions_dir = Path(extractions_dir)
        self.n_samples = n_samples
        self.claims_by_warrant: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.total_claims = 0

        if not self.extractions_dir.exists():
            raise FileNotFoundError(f"Extractions directory not found: {extractions_dir}")

    def load_extractions(self) -> None:
        """Load all extraction files and group claims by warrant type."""
        extraction_files = list(self.extractions_dir.glob("*.json"))
        logger.info(f"Loading {len(extraction_files)} extraction files")

        for extraction_file in extraction_files:
            try:
                extraction = json.loads(extraction_file.read_text(encoding="utf-8"))

                # Extract metadata
                doi = extraction.get("doi", "unknown")
                title = extraction.get("title", "Unknown Title")
                authors = extraction.get("authors", [])
                year = extraction.get("year")

                # Get bridge warrant from template level
                template_warrant = extraction.get("bridge_warrant")

                # Process claims if present
                claims = extraction.get("claims", [])
                if not claims:
                    # If no explicit claims, create synthetic entry from template
                    if template_warrant:
                        warrant_type = self._normalize_warrant_type(template_warrant)
                        claim_entry = {
                            "id": f"{doi}_template",
                            "doi": doi,
                            "title": title,
                            "authors": authors[:2],  # First 2 authors
                            "year": year,
                            "warrant_type": warrant_type,
                            "claim_text": f"[Template-level evidence from {title[:60]}...]",
                            "confidence": 0.5,  # Default for template-level
                            "source": "template",
                        }
                        self.claims_by_warrant[warrant_type].append(claim_entry)
                        self.total_claims += 1
                else:
                    # Process explicit claims
                    for i, claim in enumerate(claims):
                        claim_warrant = claim.get("bridge_warrant_type", template_warrant)
                        if claim_warrant:
                            warrant_type = self._normalize_warrant_type(claim_warrant)
                            claim_text = claim.get("text", claim.get("claim", ""))[:100]

                            claim_entry = {
                                "id": claim.get("id", f"{doi}_claim_{i}"),
                                "doi": doi,
                                "title": title,
                                "authors": authors[:2],
                                "year": year,
                                "warrant_type": warrant_type,
                                "claim_text": claim_text,
                                "confidence": claim.get("confidence", 0.5),
                                "credence_variance": claim.get("credence_variance", 0.0),
                                "source": "explicit_claim",
                            }
                            self.claims_by_warrant[warrant_type].append(claim_entry)
                            self.total_claims += 1

            except json.JSONDecodeError as e:
                logger.warning(f"Malformed JSON in {extraction_file.name}: {e}")
            except Exception as e:
                logger.warning(f"Error processing {extraction_file.name}: {e}")

        logger.info(f"Loaded {self.total_claims} total claims")

    def _normalize_warrant_type(self, warrant_str: str) -> str:
        """
        Normalize warrant type name to canonical form.

        Handles old/deprecated names and case variations.
        """
        # Map old names to canonical
        mapping = {
            "empirical_covariance": "EMPIRICAL_ASSOCIATION",
            "EMPIRICAL_COVARIANCE": "EMPIRICAL_ASSOCIATION",
            "theoretical_default": "THEORY_DERIVED",
            "THEORETICAL_DEFAULT": "THEORY_DERIVED",
        }

        normalized = mapping.get(warrant_str, warrant_str.upper())

        # Verify it's canonical
        if normalized not in self.CANONICAL_WARRANT_TYPES:
            logger.warning(f"Unknown warrant type: {warrant_str} -> {normalized}")
            return "UNKNOWN"

        return normalized

    def select_representative_samples(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Select representative claims per warrant type.

        Prioritizes claims with:
        1. Highest credence variance (uncertainty)
        2. Highest confidence (to validate strong assertions)
        3. Temporal diversity (across years)
        """
        samples = {}

        for warrant_type in self.CANONICAL_WARRANT_TYPES:
            claims = self.claims_by_warrant.get(warrant_type, [])

            if not claims:
                samples[warrant_type] = []
                continue

            # Sort by credence_variance (descending) then confidence (descending)
            sorted_claims = sorted(
                claims,
                key=lambda c: (-c.get("credence_variance", 0), -c.get("confidence", 0))
            )

            # Take top n samples
            selected = sorted_claims[: self.n_samples]
            samples[warrant_type] = selected

        return samples

    def generate_calibration_questions(
        self, samples: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Generate expert calibration questions for each sample."""
        questions = []

        for warrant_type in self.CANONICAL_WARRANT_TYPES:
            sample_claims = samples.get(warrant_type, [])

            for i, claim in enumerate(sample_claims):
                question = {
                    "question_id": f"Q_{warrant_type}_{i+1}",
                    "warrant_type": warrant_type,
                    "claim_id": claim.get("id"),
                    "paper_doi": claim.get("doi"),
                    "paper_title": claim.get("title"),
                    "paper_year": claim.get("year"),
                    "authors": claim.get("authors", []),
                    "claim_text": claim.get("claim_text"),
                    "current_confidence": claim.get("confidence", 0.5),
                    "current_variance": claim.get("credence_variance", 0.0),
                    "question_text": f"Is the warrant type {warrant_type} appropriate for this claim? "
                                    f"Is the confidence level ({claim.get('confidence', 0.5):.2f}) calibrated?",
                    "expert_instructions": (
                        f"Review this {warrant_type} warrant claim. "
                        f"Answer: (1) Is the warrant type correct? "
                        f"(2) Should the confidence be adjusted? Propose new value if yes."
                    ),
                }
                questions.append(question)

        return questions

    def generate_report(self) -> Dict[str, Any]:
        """Generate the complete calibration worksheet."""
        self.load_extractions()
        samples = self.select_representative_samples()
        questions = self.generate_calibration_questions(samples)

        # Compute distribution statistics
        distribution = {
            warrant_type: len(self.claims_by_warrant.get(warrant_type, []))
            for warrant_type in self.CANONICAL_WARRANT_TYPES
        }

        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "n_claims_total": self.total_claims,
            "warrant_types_found": len([w for w in distribution.values() if w > 0]),
            "warrant_distribution": distribution,
            "calibration_summary": {
                "total_questions": len(questions),
                "questions_per_type": {
                    wt: len([q for q in questions if q["warrant_type"] == wt])
                    for wt in self.CANONICAL_WARRANT_TYPES
                },
            },
            "sample_claims": samples,
            "calibration_questions": questions,
        }

        return report

    def save_report(self, report: Dict[str, Any], output_dir: Path) -> Path:
        """Save calibration report to JSON."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d")
        report_path = output_dir / f"expert_calibration_prep_{timestamp}.json"

        report_path.write_text(
            json.dumps(report, indent=2, default=str),
            encoding="utf-8",
        )

        logger.info(f"Calibration worksheet saved to {report_path}")
        return report_path


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate expert calibration worksheet from extraction data"
    )
    parser.add_argument(
        "--extractions-dir",
        type=Path,
        default=DATA_DIR / "extractions",
        help="Path to extractions directory (default: data/extractions)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=CALIBRATION_DIR,
        help="Path to output directory (default: data/calibration)",
    )
    parser.add_argument(
        "--n-samples",
        type=int,
        default=5,
        help="Number of sample claims per warrant type (default: 5)",
    )
    args = parser.parse_args()

    try:
        prep = ExpertCalibrationPrep(args.extractions_dir, n_samples=args.n_samples)
        report = prep.generate_report()
        report_path = prep.save_report(report, args.output_dir)

        # Print summary
        print(f"\n{'=' * 60}")
        print(f"CALIBRATION WORKSHEET GENERATED")
        print(f"  Total claims: {report['n_claims_total']}")
        print(f"  Warrant types found: {report['warrant_types_found']}/7")
        print(f"  Sample questions: {report['calibration_summary']['total_questions']}")
        print(f"  Output: {report_path}")
        print(f"{'=' * 60}\n")

        return 0

    except Exception as e:
        logger.error(f"Failed to generate calibration worksheet: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
