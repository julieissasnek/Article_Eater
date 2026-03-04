#!/usr/bin/env python3
"""
Stimulus Description Backfill Script

Scans all extraction JSONs to identify findings with missing or minimal
stimulus_description fields. Reports on coverage and identifies candidates
for re-extraction with focused stimulus-extraction prompts.

Usage:
    python scripts/backfill_stimulus_descriptions.py
    python scripts/backfill_stimulus_descriptions.py --output report.json
    python scripts/backfill_stimulus_descriptions.py --with-antecedent-text
"""

import json
import logging
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict, field

# Setup paths
REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════
# Data Models
# ════════════════════════════════════════════════════════════════════════════

@dataclass
class StimulusCoverage:
    """Coverage of a single finding's stimulus fields."""
    finding_id: str
    has_stimulus_description: bool
    stimulus_is_null: bool
    stimulus_is_empty_dict: bool
    components_count: int
    delivery_method_present: bool
    primary_type_present: bool
    has_images: bool
    antecedent_mentions_sensory: bool
    antecedent_text: Optional[str] = None
    needs_backfill: bool = False

    def to_dict(self):
        """Serialize to dict."""
        result = asdict(self)
        # Remove antecedent_text from default output unless needed
        if self.antecedent_text is None:
            result.pop('antecedent_text', None)
        return result


@dataclass
class ArticleStimulusCoverage:
    """Stimulus field coverage for entire article."""
    doi: str
    title: str
    article_type: Optional[str]
    article_family: Optional[str]
    file_path: str
    total_findings: int
    findings_with_stimulus: int
    findings_needing_backfill: int
    coverage_pct: float
    finding_details: List[StimulusCoverage] = field(default_factory=list)

    def to_dict(self):
        return {
            'doi': self.doi,
            'title': self.title,
            'article_type': self.article_type,
            'article_family': self.article_family,
            'file_path': self.file_path,
            'total_findings': self.total_findings,
            'findings_with_stimulus': self.findings_with_stimulus,
            'findings_needing_backfill': self.findings_needing_backfill,
            'coverage_pct': round(self.coverage_pct, 1),
            'finding_details': [f.to_dict() for f in self.finding_details],
        }


@dataclass
class BackfillReport:
    """Overall report on stimulus description backfill readiness."""
    generated_at: str
    total_articles: int
    total_findings: int
    findings_with_stimulus: int
    findings_needing_backfill: int
    overall_coverage_pct: float
    articles_zero_coverage: List[str] = field(default_factory=list)
    articles_partial_coverage: List[str] = field(default_factory=list)
    articles_full_coverage: List[str] = field(default_factory=list)
    article_details: List[ArticleStimulusCoverage] = field(default_factory=list)

    def to_dict(self):
        return {
            'generated_at': self.generated_at,
            'total_articles': self.total_articles,
            'total_findings': self.total_findings,
            'findings_with_stimulus': self.findings_with_stimulus,
            'findings_needing_backfill': self.findings_needing_backfill,
            'overall_coverage_pct': round(self.overall_coverage_pct, 1),
            'articles_zero_coverage': len(self.articles_zero_coverage),
            'articles_partial_coverage': len(self.articles_partial_coverage),
            'articles_full_coverage': len(self.articles_full_coverage),
            'articles': [a.to_dict() for a in self.article_details],
        }


# ════════════════════════════════════════════════════════════════════════════
# Validation Logic
# ════════════════════════════════════════════════════════════════════════════

SENSORY_PATTERNS = [
    r'light|lighting|lux|illuminance|CCT|kelvin|candela|brightness',
    r'sound|acoustic|dB|decibel|noise|reverberation|RT60|frequency',
    r'room|space|ceiling|height|dimension|area|volume|floor|wall',
    r'material|texture|finish|wood|concrete|stone|fabric|surface',
    r'color|hue|saturation|chroma|blue|red|green|warm|cool',
    r'thermal|temperature|warm|cool|radiant|thermal comfort',
    r'smell|olfactory|odor|scent|aroma',
    r'view|window|vista|prospect|refuge|biophilic|plant|nature',
]


def check_antecedent_sensory_content(antecedent: str) -> bool:
    """Check if antecedent mentions sensory/environmental terms."""
    if not antecedent or not isinstance(antecedent, str):
        return False
    for pattern in SENSORY_PATTERNS:
        if re.search(pattern, antecedent, re.IGNORECASE):
            return True
    return False


def analyze_finding_stimulus(finding: dict, finding_id: str,
                            include_text: bool = False) -> StimulusCoverage:
    """Analyze stimulus_description coverage for a single finding."""
    stimulus = finding.get('stimulus_description')
    antecedent = finding.get('antecedent', '')
    claim_type = finding.get('claim_type')

    # Basic presence checks
    has_stimulus = stimulus is not None and isinstance(stimulus, dict)
    is_null = stimulus is None
    is_empty = stimulus is not None and isinstance(stimulus, dict) and not stimulus

    # Detailed checks if stimulus exists
    components = []
    delivery_method_present = False
    primary_type_present = False
    has_images = False

    if has_stimulus:
        components = stimulus.get('components', [])
        delivery_method_present = stimulus.get('delivery_method') is not None
        primary_type_present = stimulus.get('primary_type') is not None
        has_images = bool(finding.get('stimulus_images'))

    # Check if antecedent has sensory language
    has_sensory = check_antecedent_sensory_content(antecedent)

    # Determine if needs backfill
    # For empirical claims: stimulus_description should be present with components
    is_empirical = claim_type in (
        'empirical_finding', 'causal', 'associational', 'statistical',
    )

    needs_backfill = (
        is_empirical and (
            not has_stimulus or
            not components or
            (has_sensory and not delivery_method_present)
        )
    )

    coverage = StimulusCoverage(
        finding_id=finding_id,
        has_stimulus_description=has_stimulus,
        stimulus_is_null=is_null,
        stimulus_is_empty_dict=is_empty,
        components_count=len(components) if components else 0,
        delivery_method_present=delivery_method_present,
        primary_type_present=primary_type_present,
        has_images=has_images,
        antecedent_mentions_sensory=has_sensory,
        antecedent_text=antecedent if include_text else None,
        needs_backfill=needs_backfill,
    )
    return coverage


def analyze_article_stimulus(data: dict, file_path: str,
                             include_text: bool = False) -> ArticleStimulusCoverage:
    """Analyze stimulus_description coverage for entire article."""
    # Extract metadata
    doi = data.get('doi', 'unknown')
    title = data.get('title', 'Untitled')
    article_type = data.get('article_type')
    article_family = data.get('article_family')

    # Extract findings
    findings = data.get('findings', [])
    if not findings:
        return ArticleStimulusCoverage(
            doi=doi, title=title, article_type=article_type,
            article_family=article_family, file_path=file_path,
            total_findings=0, findings_with_stimulus=0,
            findings_needing_backfill=0, coverage_pct=0.0,
        )

    # Analyze each finding
    finding_details = []
    for i, finding in enumerate(findings):
        finding_id = finding.get('id', f'F{i}')
        coverage = analyze_finding_stimulus(finding, finding_id,
                                          include_text=include_text)
        finding_details.append(coverage)

    # Compute summary
    total = len(findings)
    with_stimulus = sum(1 for f in finding_details if f.has_stimulus_description)
    needs_backfill = sum(1 for f in finding_details if f.needs_backfill)
    coverage_pct = (with_stimulus / total * 100) if total > 0 else 0.0

    return ArticleStimulusCoverage(
        doi=doi, title=title, article_type=article_type,
        article_family=article_family, file_path=file_path,
        total_findings=total, findings_with_stimulus=with_stimulus,
        findings_needing_backfill=needs_backfill, coverage_pct=coverage_pct,
        finding_details=finding_details,
    )


def analyze_extraction_directory(directory: Path,
                                include_text: bool = False) -> BackfillReport:
    """Scan all extraction JSONs and analyze stimulus coverage."""
    logger.info(f"Scanning extraction directory: {directory}")

    articles = []
    total_findings = 0
    total_with_stimulus = 0

    for ext_file in sorted(directory.glob('*.json')):
        # Skip internal files
        if ext_file.name.startswith('_') or 'batch' in ext_file.name:
            continue

        try:
            data = json.loads(ext_file.read_text(errors='replace'))
            if not isinstance(data, dict):
                continue

            # Skip if no findings
            if not data.get('findings'):
                continue

            article_cov = analyze_article_stimulus(data, str(ext_file),
                                                  include_text=include_text)
            articles.append(article_cov)
            total_findings += article_cov.total_findings
            total_with_stimulus += article_cov.findings_with_stimulus

        except json.JSONDecodeError as e:
            logger.warning(f"Skipped {ext_file.name}: {e}")
            continue

    # Compute overall stats
    total_articles = len(articles)
    total_backfill = sum(a.findings_needing_backfill for a in articles)
    overall_coverage = (total_with_stimulus / total_findings * 100) \
        if total_findings > 0 else 0.0

    # Categorize articles
    zero_coverage = [a.doi for a in articles if a.coverage_pct == 0]
    partial_coverage = [a.doi for a in articles
                       if 0 < a.coverage_pct < 100]
    full_coverage = [a.doi for a in articles if a.coverage_pct == 100]

    report = BackfillReport(
        generated_at=datetime.utcnow().isoformat(),
        total_articles=total_articles,
        total_findings=total_findings,
        findings_with_stimulus=total_with_stimulus,
        findings_needing_backfill=total_backfill,
        overall_coverage_pct=overall_coverage,
        articles_zero_coverage=zero_coverage,
        articles_partial_coverage=partial_coverage,
        articles_full_coverage=full_coverage,
        article_details=articles,
    )

    return report


# ════════════════════════════════════════════════════════════════════════════
# Reporting
# ════════════════════════════════════════════════════════════════════════════

def print_report_summary(report: BackfillReport):
    """Print human-readable summary."""
    print("\n" + "="*80)
    print("STIMULUS DESCRIPTION BACKFILL REPORT")
    print("="*80)
    print(f"Generated: {report.generated_at}")
    print(f"\nOVERALL STATISTICS:")
    print(f"  Articles scanned:           {report.total_articles}")
    print(f"  Total findings:             {report.total_findings}")
    print(f"  Findings with stimulus:     {report.findings_with_stimulus} ({report.overall_coverage_pct:.1f}%)")
    print(f"  Findings needing backfill:  {report.findings_needing_backfill}")
    print(f"\nARTICLE CATEGORIES:")
    print(f"  Zero coverage (0%):         {len(report.articles_zero_coverage)}")
    print(f"  Partial coverage (1-99%):   {len(report.articles_partial_coverage)}")
    print(f"  Full coverage (100%):       {len(report.articles_full_coverage)}")

    # Show articles needing most work
    articles_by_backfill = sorted(
        report.article_details,
        key=lambda a: a.findings_needing_backfill,
        reverse=True
    )
    if articles_by_backfill and articles_by_backfill[0].findings_needing_backfill > 0:
        print(f"\nTOP 5 ARTICLES NEEDING BACKFILL:")
        for i, article in enumerate(articles_by_backfill[:5], 1):
            print(f"  {i}. {article.doi}")
            print(f"     Title: {article.title[:70]}")
            print(f"     Coverage: {article.coverage_pct:.1f}% "
                  f"({article.findings_with_stimulus}/{article.total_findings})")
            print(f"     Backfill needed: {article.findings_needing_backfill} findings")

    print("\n" + "="*80 + "\n")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Analyze stimulus_description coverage in extractions'
    )
    parser.add_argument(
        '--output', type=str, default=None,
        help='Output JSON file for detailed report (default: print summary only)'
    )
    parser.add_argument(
        '--with-antecedent-text', action='store_true',
        help='Include antecedent text in output (verbose)'
    )
    parser.add_argument(
        '--directory', type=Path, default=None,
        help='Extraction directory (default: data/extractions/)'
    )
    args = parser.parse_args()

    # Determine directory
    ext_dir = args.directory or (REPO / 'data' / 'extractions')
    if not ext_dir.exists():
        logger.error(f"Extraction directory not found: {ext_dir}")
        sys.exit(1)

    # Run analysis
    report = analyze_extraction_directory(ext_dir,
                                         include_text=args.with_antecedent_text)

    # Print summary
    print_report_summary(report)

    # Write output file if requested
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(json.dumps(report.to_dict(), indent=2))
        logger.info(f"Detailed report written to: {output_path}")


if __name__ == '__main__':
    main()
