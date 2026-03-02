#!/usr/bin/env python3
"""
RV5-3 Extraction Pipeline Audit
================================
Comprehensive audit of all extraction files focusing on:
1. Antecedent quality (vague vs specific)
2. Direction field normalization
3. Sample size coverage
4. Claim type distribution
5. Effect size and p-value coverage
6. Template matching
7. Extraction completeness by article_type
"""

import json
import logging
import random
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, stdev
from typing import Any, Dict, List, Optional, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data" / "extractions"
QUALITY_RULES_PATH = PROJECT_ROOT / "contracts" / "schemas" / "extraction_quality_rules.json"
TEMPLATE_LINKS_PATH = PROJECT_ROOT / "data" / "production" / "finding_template_theory_links.json"


# --- Audit Configuration ---

CANONICAL_DIRECTIONS = {"increase", "decrease", "no_effect", "mixed"}

VAGUE_PATTERNS = {
    # Generic environment/condition references
    r"\bthe environment\b": "vague_environment",
    r"\bthe condition\b": "vague_condition",
    r"\bthe exposure\b": "vague_exposure",
    r"\bthe treatment\b": "vague_treatment",
    r"\bthe stimulus\b": "vague_stimulus",
    r"\bthe intervention\b": "vague_intervention",
    r"\bthe factor\b": "vague_factor",
    r"\bthe variable\b": "vague_variable",
    r"\bthe study\b": "vague_study",
    # Overly general phrases
    r"\bincreased.*exposure\b": "vague_increased_exposure",
    r"\bhigh.*level\b": "vague_high_level",
    r"\bpositive.*condition\b": "vague_positive_condition",
    r"\badverse.*condition\b": "vague_adverse_condition",
}

SPECIFIC_PATTERNS = {
    # Specific decibel levels
    r"\d+\s*dB": "specific_decibel",
    # Specific wavelengths/colors
    r"\d+\s*nm|blue light|red light|green light": "specific_wavelength",
    # Specific temperatures
    r"\d+\s*°[CF]": "specific_temperature",
    # Specific measurements
    r"\d+\s*(m|cm|mm|lux|percent|μmol)": "specific_measurement",
    # Named conditions
    r"open-plan|enclosed|isolated|separated": "specific_condition",
    r"natural light|artificial light|daylight": "specific_light_type",
}


class AuditMetrics:
    """Container for audit metrics."""

    def __init__(self):
        self.total_articles = 0
        self.total_findings = 0

        # Antecedent quality
        self.vague_antecedents = 0
        self.specific_antecedents = 0
        self.antecedent_vagueness_counts = defaultdict(int)
        self.antecedent_specificity_counts = defaultdict(int)

        # Direction normalization
        self.canonical_directions = 0
        self.non_canonical_directions = defaultdict(int)
        self.null_directions = 0

        # Sample size
        self.sample_size_populated = 0
        self.sample_size_null = 0
        self.sample_sizes = []

        # Claim types
        self.claim_type_distribution = defaultdict(int)
        self.null_claim_types = 0

        # Effect size and p-value
        self.effect_size_populated = 0
        self.effect_size_null = 0
        self.p_value_populated = 0
        self.p_value_null = 0
        self.both_populated = 0
        self.neither_populated = 0

        # Article type distribution
        self.article_type_stats = defaultdict(lambda: {
            "count": 0,
            "findings": 0,
            "vague_pct": 0,
            "canonical_direction_pct": 0,
            "sample_size_pct": 0,
            "effect_size_pct": 0,
        })

        # Template matching
        self.articles_with_templates = 0
        self.findings_with_templates = 0
        self.avg_templates_per_finding = 0

        # Quality issues found
        self.quality_issues = []
        self.sampled_findings_problems = []


def is_vague_antecedent(text: str) -> Tuple[bool, Optional[str]]:
    """Check if antecedent is vague."""
    if not text:
        return False, None
    text_lower = text.lower()
    for pattern, category in VAGUE_PATTERNS.items():
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True, category
    return False, None


def is_specific_antecedent(text: str) -> Tuple[bool, Optional[str]]:
    """Check if antecedent is specific."""
    if not text:
        return False, None
    for pattern, category in SPECIFIC_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            return True, category
    return False, None


def audit_extraction_file(filepath: Path, metrics: AuditMetrics) -> Dict[str, Any]:
    """Audit a single extraction file."""
    try:
        with open(filepath, 'r') as f:
            article = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load {filepath}: {e}")
        return {}

    # Skip non-dict files (e.g., query logs that are arrays)
    if not isinstance(article, dict):
        return {}

    metrics.total_articles += 1
    article_type = article.get("article_type", "unknown")
    findings = article.get("findings", [])
    metrics.total_findings += len(findings)

    article_issues = {
        "doi": article.get("doi"),
        "article_type": article_type,
        "n_findings": len(findings),
        "problems": []
    }

    # Initialize article type stats
    if article_type not in metrics.article_type_stats:
        metrics.article_type_stats[article_type]["count"] = 0
        metrics.article_type_stats[article_type]["findings"] = 0
    metrics.article_type_stats[article_type]["count"] += 1
    metrics.article_type_stats[article_type]["findings"] += len(findings)

    # Check template matching at article level
    if any(f.get("template_ids") or f.get("template_matches") for f in findings):
        metrics.articles_with_templates += 1

    # Audit each finding
    article_vague_count = 0
    article_canonical_count = 0
    article_sample_size_count = 0
    article_effect_size_count = 0

    for finding_idx, finding in enumerate(findings):
        # --- Antecedent Quality ---
        antecedent = finding.get("antecedent", "")
        is_vague, vague_cat = is_vague_antecedent(antecedent)
        is_specific, specific_cat = is_specific_antecedent(antecedent)

        if is_vague:
            metrics.vague_antecedents += 1
            article_vague_count += 1
            if vague_cat:
                metrics.antecedent_vagueness_counts[vague_cat] += 1
            if random.random() < 0.1:  # Sample 10% of vague ones
                metrics.sampled_findings_problems.append({
                    "doi": article.get("doi"),
                    "issue": "vague_antecedent",
                    "antecedent": antecedent[:100],
                    "category": vague_cat
                })
        elif is_specific:
            metrics.specific_antecedents += 1
            if specific_cat:
                metrics.antecedent_specificity_counts[specific_cat] += 1
        else:
            # Neither vague nor specifically measurable - neutral
            pass

        # --- Direction Normalization ---
        direction = finding.get("direction", "").lower().strip() if finding.get("direction") else None
        if direction:
            if direction in CANONICAL_DIRECTIONS:
                metrics.canonical_directions += 1
                article_canonical_count += 1
            else:
                metrics.non_canonical_directions[direction] += 1
                if random.random() < 0.2:  # Sample 20% of non-canonical
                    metrics.sampled_findings_problems.append({
                        "doi": article.get("doi"),
                        "issue": "non_canonical_direction",
                        "direction": direction
                    })
        else:
            metrics.null_directions += 1

        # --- Sample Size ---
        sample_size = finding.get("sample_size")
        if sample_size is not None:
            metrics.sample_size_populated += 1
            article_sample_size_count += 1
            if isinstance(sample_size, (int, float)) and sample_size > 0:
                metrics.sample_sizes.append(sample_size)
        else:
            metrics.sample_size_null += 1

        # --- Claim Type ---
        claim_type = finding.get("claim_type")
        if claim_type:
            metrics.claim_type_distribution[claim_type] += 1
        else:
            metrics.null_claim_types += 1

        # --- Effect Size & P-value ---
        effect_size = finding.get("effect_size")
        p_value = finding.get("p_value")

        if effect_size is not None:
            metrics.effect_size_populated += 1
            article_effect_size_count += 1
        else:
            metrics.effect_size_null += 1

        if p_value is not None:
            metrics.p_value_populated += 1
        else:
            metrics.p_value_null += 1

        if effect_size is not None and p_value is not None:
            metrics.both_populated += 1
        elif effect_size is None and p_value is None:
            metrics.neither_populated += 1

        # --- Template Matching ---
        if finding.get("template_ids") or finding.get("template_matches"):
            metrics.findings_with_templates += 1

        # Collect template match count
        template_matches = finding.get("template_matches", [])
        if template_matches:
            metrics.avg_templates_per_finding += len(template_matches)

    # Finalize article-level stats
    if len(findings) > 0:
        metrics.article_type_stats[article_type]["vague_pct"] = (article_vague_count / len(findings)) * 100
        metrics.article_type_stats[article_type]["canonical_direction_pct"] = (article_canonical_count / len(findings)) * 100
        metrics.article_type_stats[article_type]["sample_size_pct"] = (article_sample_size_count / len(findings)) * 100
        metrics.article_type_stats[article_type]["effect_size_pct"] = (article_effect_size_count / len(findings)) * 100

    return article_issues


def compute_quality_score(metrics: AuditMetrics) -> Tuple[float, str]:
    """Compute overall quality score (0-10) and assign rubric level."""
    if metrics.total_findings == 0:
        return 0, "1-2"

    # Calculate coverage percentages
    proper_fields_pct = (metrics.canonical_directions / metrics.total_findings) * 100 if metrics.total_findings > 0 else 0
    vague_pct = (metrics.vague_antecedents / metrics.total_findings) * 100 if metrics.total_findings > 0 else 0
    sample_size_pct = (metrics.sample_size_populated / metrics.total_findings) * 100 if metrics.total_findings > 0 else 0
    effect_size_pct = (metrics.effect_size_populated / metrics.total_findings) * 100 if metrics.total_findings > 0 else 0

    # Weighted scoring
    direction_score = min(proper_fields_pct, 100)  # 0-100
    vagueness_score = max(0, 100 - vague_pct)  # Penalize vagueness
    sample_size_score = sample_size_pct  # 0-100
    effect_size_score = effect_size_pct  # 0-100

    # Average with direction as highest weight
    overall = (direction_score * 0.35 + vagueness_score * 0.35 + sample_size_score * 0.15 + effect_size_score * 0.15) / 100
    score = overall * 10  # Scale to 0-10

    # Assign rubric level
    if score >= 9:
        level = "9-10"
    elif score >= 7:
        level = "7-8"
    elif score >= 5:
        level = "5-6"
    elif score >= 3:
        level = "3-4"
    else:
        level = "1-2"

    return round(score, 2), level


def main():
    """Run the complete audit."""
    logger.info("Starting RV5-3 Extraction Pipeline Audit...")
    logger.info(f"Data directory: {DATA_DIR}")

    metrics = AuditMetrics()

    # Get all extraction files
    extraction_files = sorted(DATA_DIR.glob("*.json"))
    logger.info(f"Found {len(extraction_files)} extraction files")

    # Process all files
    for i, filepath in enumerate(extraction_files):
        if (i + 1) % 100 == 0:
            logger.info(f"Processing file {i+1}/{len(extraction_files)}")
        audit_extraction_file(filepath, metrics)

    # Compute template stats
    if metrics.total_findings > 0 and metrics.findings_with_templates > 0:
        metrics.avg_templates_per_finding /= metrics.findings_with_templates

    # Compute quality score
    quality_score, rubric_level = compute_quality_score(metrics)

    # Generate audit report (pass extraction_files count)
    report = generate_report(metrics, quality_score, rubric_level, len(extraction_files))

    # Write report
    report_path = PROJECT_ROOT / "docs" / "RV5_3_EXTRACTION_PIPELINE_AUDIT_2026-03-01.md"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, 'w') as f:
        f.write(report)

    logger.info(f"\nAudit complete. Report written to: {report_path}")
    print(report)


def generate_report(metrics: AuditMetrics, quality_score: float, rubric_level: str, num_extraction_files: int) -> str:
    """Generate the audit report."""

    # Calculate percentages
    if metrics.total_findings > 0:
        vague_pct = (metrics.vague_antecedents / metrics.total_findings) * 100
        specific_pct = (metrics.specific_antecedents / metrics.total_findings) * 100
        canonical_pct = (metrics.canonical_directions / metrics.total_findings) * 100
        sample_size_pct = (metrics.sample_size_populated / metrics.total_findings) * 100
        effect_size_pct = (metrics.effect_size_populated / metrics.total_findings) * 100
        p_value_pct = (metrics.p_value_populated / metrics.total_findings) * 100
        both_pct = (metrics.both_populated / metrics.total_findings) * 100
        neither_pct = (metrics.neither_populated / metrics.total_findings) * 100
    else:
        vague_pct = specific_pct = canonical_pct = sample_size_pct = effect_size_pct = p_value_pct = both_pct = neither_pct = 0

    # Sample size stats
    if metrics.sample_sizes:
        sample_size_mean = mean(metrics.sample_sizes)
        sample_size_stdev = stdev(metrics.sample_sizes) if len(metrics.sample_sizes) > 1 else 0
        sample_size_min = min(metrics.sample_sizes)
        sample_size_max = max(metrics.sample_sizes)
    else:
        sample_size_mean = sample_size_stdev = sample_size_min = sample_size_max = 0

    # Claim type distribution
    claim_type_sorted = sorted(metrics.claim_type_distribution.items(), key=lambda x: x[1], reverse=True)

    # Non-canonical directions
    non_canonical_sorted = sorted(metrics.non_canonical_directions.items(), key=lambda x: x[1], reverse=True)

    # Build report
    report = f"""# RV5-3 Extraction Pipeline Audit

**Date**: 2026-03-01
**Version**: RV5-3
**Overall Quality Score**: {quality_score}/10 (Rubric Level: {rubric_level})

---

## Executive Summary

This audit examines **{metrics.total_articles} extraction articles** containing **{metrics.total_findings} findings** extracted from the Article_Eater corpus. The pipeline shows **{rubric_level} quality** with specific strengths and critical gaps.

### Quality Score Interpretation
- **9-10**: >95% proper fields, <5% vague antecedents, canonical directions everywhere
- **7-8**: >85% proper, <15% vague, minimal non-canonical
- **5-6**: >70% proper, issues exist but manageable
- **3-4**: Significant gaps, many fields missing
- **1-2**: Systemic quality issues

**Current Score {quality_score} falls in Rubric {rubric_level}.**

---

## 1. Antecedent Quality Analysis

### Overview
- **Total Antecedents Analyzed**: {metrics.total_findings}
- **Vague Antecedents**: {metrics.vague_antecedents} ({vague_pct:.1f}%)
- **Specific/Measurable Antecedents**: {metrics.specific_antecedents} ({specific_pct:.1f}%)
- **Neutral/Contextual**: {metrics.total_findings - metrics.vague_antecedents - metrics.specific_antecedents}

### Vagueness Breakdown
Examples of vague patterns found:
"""

    # Top vague patterns
    top_vague = sorted(metrics.antecedent_vagueness_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for pattern, count in top_vague:
        report += f"\n- **{pattern}**: {count} occurrences"

    report += f"""

### Specificity Breakdown
Examples of specific/measurable patterns found:
"""

    # Top specific patterns
    top_specific = sorted(metrics.antecedent_specificity_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for pattern, count in top_specific:
        report += f"\n- **{pattern}**: {count} occurrences"

    report += f"""

### Sample Vague Antecedents (Random Sample)
"""

    # Show sampled vague examples
    vague_samples = [p for p in metrics.sampled_findings_problems if p["issue"] == "vague_antecedent"][:10]
    for i, sample in enumerate(vague_samples, 1):
        report += f"\n{i}. **DOI**: {sample['doi']}\n"
        report += f"   **Antecedent**: \"{sample['antecedent']}\"\n"
        report += f"   **Category**: {sample['category']}\n"

    report += f"""

---

## 2. Direction Field Normalization

### Canonical Direction Coverage
- **Total Findings with Direction**: {metrics.total_findings - metrics.null_directions}
- **Canonical Values** (increase, decrease, no_effect, mixed): {metrics.canonical_directions} ({canonical_pct:.1f}%)
- **Non-Canonical Values**: {sum(metrics.non_canonical_directions.values())} ({100 - canonical_pct:.1f}%)
- **Null/Missing Direction**: {metrics.null_directions} ({(metrics.null_directions / metrics.total_findings * 100):.1f}%)

### Non-Canonical Direction Values Found
"""

    for direction, count in non_canonical_sorted[:15]:
        pct = (count / metrics.total_findings) * 100
        report += f"\n- `{direction}`: {count} findings ({pct:.1f}%)"

    report += f"""

### Assessment
**Status**: {'PASS' if canonical_pct >= 95 else 'FAIL' if canonical_pct < 70 else 'WARNING'}
- Expected: ≥95% of directions should be canonical
- Current: {canonical_pct:.1f}%
- Non-canonical directions indicate extraction model drift or inconsistent labeling

---

## 3. Sample Size Coverage

### Statistics
- **Findings with sample_size populated**: {metrics.sample_size_populated} ({sample_size_pct:.1f}%)
- **Findings with sample_size NULL**: {metrics.sample_size_null} ({100 - sample_size_pct:.1f}%)

### Sample Size Distribution (Populated Fields Only)
- **Count**: {len(metrics.sample_sizes)} findings
- **Mean**: {sample_size_mean:.1f}
- **Stdev**: {sample_size_stdev:.1f}
- **Min**: {sample_size_min}
- **Max**: {sample_size_max}

### Assessment
**Status**: {'GOOD' if sample_size_pct >= 80 else 'NEEDS_WORK' if sample_size_pct >= 50 else 'POOR'}
- Current coverage: {sample_size_pct:.1f}%
- Empirical findings should have sample_size ~90%+ of the time
- Many null values suggest extraction skips this field for non-empirical findings (acceptable) or fails to extract from methods sections (problematic)

---

## 4. Claim Type Distribution

### Distribution
"""

    for claim_type, count in claim_type_sorted:
        pct = (count / metrics.total_findings) * 100
        report += f"\n- **{claim_type}**: {count} findings ({pct:.1f}%)"

    report += f"""
- **NULL claim_type**: {metrics.null_claim_types} ({(metrics.null_claim_types / metrics.total_findings * 100):.1f}%)

### Assessment
**Distribution Health**: {'SKEWED' if claim_type_sorted[0][1] > metrics.total_findings * 0.5 else 'BALANCED' if len(claim_type_sorted) > 3 else 'SPARSE'}
- Top claim type represents {(claim_type_sorted[0][1] / metrics.total_findings * 100):.1f}% of corpus
- Expected: Multiple types represented, no single type >50%
- Current diversity: {len(claim_type_sorted)} distinct types

---

## 5. Effect Size and P-value Coverage

### Coverage Statistics
- **Findings with effect_size populated**: {metrics.effect_size_populated} ({effect_size_pct:.1f}%)
- **Findings with p_value populated**: {metrics.p_value_populated} ({p_value_pct:.1f}%)
- **Both populated**: {metrics.both_populated} ({both_pct:.1f}%)
- **Neither populated**: {metrics.neither_populated} ({neither_pct:.1f}%)

### Assessment
**Status**: {'EXCELLENT' if effect_size_pct >= 85 else 'GOOD' if effect_size_pct >= 70 else 'POOR' if effect_size_pct < 50 else 'FAIR'}
- Effect size is critical for quantitative meta-analysis
- Current coverage: {effect_size_pct:.1f}%
- P-value coverage: {p_value_pct:.1f}%
- **Gap**: {neither_pct:.1f}% of findings have neither metric

---

## 6. Template Matching Coverage

### Statistics
- **Articles with template matches**: {metrics.articles_with_templates} / {metrics.total_articles} ({(metrics.articles_with_templates / metrics.total_articles * 100):.1f}%)
- **Findings with template matches**: {metrics.findings_with_templates} / {metrics.total_findings} ({(metrics.findings_with_templates / metrics.total_findings * 100):.1f}%)
- **Average templates per matched finding**: {metrics.avg_templates_per_finding:.2f}

### Assessment
**Status**: {'EXCELLENT' if metrics.findings_with_templates / metrics.total_findings > 0.8 else 'GOOD' if metrics.findings_with_templates / metrics.total_findings > 0.5 else 'POOR'}
- Template matching enables theory linking
- Current coverage: {(metrics.findings_with_templates / metrics.total_findings * 100):.1f}%
- Expected: >80% for theory-based extraction

---

## 7. Extraction Completeness by Article Type

### Summary by Article Type
| Article Type | Count | Findings | Vague % | Canonical Dir % | Sample Size % | Effect Size % |
|---|---|---|---|---|---|---|
"""

    for atype, stats in sorted(metrics.article_type_stats.items(), key=lambda x: x[1]["count"], reverse=True):
        if stats["count"] > 0:
            report += f"| {atype} | {stats['count']} | {stats['findings']} | {stats['vague_pct']:.1f}% | {stats['canonical_direction_pct']:.1f}% | {stats['sample_size_pct']:.1f}% | {stats['effect_size_pct']:.1f}% |\n"

    report += f"""

### Quality Profiles by Type
**Empirical Studies** (should have: high sample_size %, high effect_size %)
**Synthesis/Review** (should have: moderate sample_size %, lower effect_size %)
**Theoretical** (should have: low sample_size %, minimal effect_size %)
**Qualitative** (should have: null sample_size expected, varied effect_size %)

---

## 8. Critical Problems Identified

### Problem Categories

#### A. Vague Antecedents ({metrics.vague_antecedents} findings, {vague_pct:.1f}%)
**Impact**: MEDIUM - Reduces specificity and reproducibility
- Example: "the environment" instead of "open-plan office with 45 dB noise"
- These make findings difficult to operationalize in new studies

#### B. Non-Canonical Directions ({sum(metrics.non_canonical_directions.values())} findings)
**Impact**: HIGH - Breaks downstream processing
- Non-canonical values prevent automated analysis
- Indicates extraction model drift or QA failure

#### C. Missing Sample Sizes ({metrics.sample_size_null} findings, {100 - sample_size_pct:.1f}%)
**Impact**: MEDIUM - Blocks meta-analysis
- For empirical studies, sample_size should be near 100%
- Current gap suggests methods section parsing failures

#### D. Missing Effect Sizes ({metrics.effect_size_null} findings, {100 - effect_size_pct:.1f}%)
**Impact**: HIGH - Blocks quantitative synthesis
- Effect size is critical for systematic review
- {neither_pct:.1f}% have neither effect_size nor p_value

#### E. Low Template Matching ({100 - (metrics.findings_with_templates / metrics.total_findings * 100):.1f}% unmatched)
**Impact**: MEDIUM - Breaks theory linking
- Theory links require template matches
- Current coverage: {(metrics.findings_with_templates / metrics.total_findings * 100):.1f}%

---

## 9. Recommendations (Ranked by Impact)

### P1 (Critical) — Fix Direction Normalization
- **Action**: Audit all {sum(metrics.non_canonical_directions.values())} non-canonical directions
- **Rationale**: Breaks automated pipeline
- **Effort**: 2-4 hours
- **Expected Impact**: +{100 - canonical_pct:.1f}% conformance

### P1 (Critical) — Recover Missing Effect Sizes
- **Action**: Retrace {metrics.effect_size_null} findings where extraction skipped effect_size
- **Rationale**: Required for meta-analysis
- **Effort**: 8-16 hours
- **Expected Impact**: +{100 - effect_size_pct:.1f}% coverage

### P2 (High) — Improve Template Matching
- **Action**: Enhance template matching algorithm to reach >85% coverage
- **Rationale**: Currently {(metrics.findings_with_templates / metrics.total_findings * 100):.1f}%, expected >85%
- **Effort**: 4-8 hours
- **Expected Impact**: Enables theory linking for {int((0.85 * metrics.total_findings) - metrics.findings_with_templates)} additional findings

### P2 (High) — Reduce Vague Antecedents
- **Action**: Retrace {metrics.vague_antecedents} vague antecedents; add specific contextual details
- **Rationale**: {vague_pct:.1f}% vagueness exceeds acceptable threshold
- **Effort**: 6-12 hours
- **Expected Impact**: +{vague_pct:.1f}% specificity

### P3 (Medium) — Improve Sample Size Coverage for Empirical Studies
- **Action**: Audit empirical articles; ensure methods/results sections parsed for N
- **Rationale**: {sample_size_pct:.1f}% coverage is low for empirical work
- **Effort**: 4-6 hours
- **Expected Impact**: +{max(0, 90 - sample_size_pct):.1f}% for empirical subset

---

## 10. Detailed Findings Tables

### Non-Canonical Directions (Top 20)
| Direction | Count | % of Total |
|---|---|---|
"""

    for direction, count in non_canonical_sorted[:20]:
        pct = (count / metrics.total_findings) * 100
        report += f"| `{direction}` | {count} | {pct:.2f}% |\n"

    report += f"""

### Claim Type Distribution (All Types)
| Claim Type | Count | % of Total |
|---|---|---|
"""

    for claim_type, count in claim_type_sorted:
        pct = (count / metrics.total_findings) * 100
        report += f"| {claim_type} | {count} | {pct:.2f}% |\n"

    report += f"""

---

## 11. Comparison to Previous RV5 Audit

Historical trends (if previous audit data available):
- Previous RV5 quality score: [data needed]
- Improvement in vagueness: [data needed]
- Improvement in direction normalization: [data needed]
- Improvement in template coverage: [data needed]

**Note**: This is the first RV5-3 audit. Update this section in subsequent runs.

---

## 12. Recommendations for Next Steps

### Immediate (This Week)
1. Fix all {sum(metrics.non_canonical_directions.values())} non-canonical directions
2. Identify bottleneck for effect_size extraction ({metrics.effect_size_null} missing)
3. Sample 20 vague antecedents; identify extraction model issue

### Short-term (This Sprint)
1. Retrace {metrics.vague_antecedents} vague antecedents with human review
2. Enhance template matching from {(metrics.findings_with_templates / metrics.total_findings * 100):.1f}% to >85%
3. Audit sample_size extraction for empirical studies

### Medium-term (Next Sprint)
1. Implement automated vagueness detection in QA pipeline
2. Create extraction debugging logs to trace effect_size/p_value misses
3. Establish baseline metrics for continuous monitoring

---

## Conclusion

**Overall Assessment**: Rubric {rubric_level} ({quality_score}/10)

The extraction pipeline has produced {metrics.total_findings} findings from {metrics.total_articles} articles with **mixed quality**:

✓ **Strengths**:
- {canonical_pct:.1f}% of directions are canonical (adequate)
- {metrics.findings_with_templates / metrics.total_findings * 100:.1f}% of findings have template matches
- {len(metrics.sample_sizes)} findings with quantifiable sample sizes

✗ **Critical Gaps**:
- {sum(metrics.non_canonical_directions.values())} non-canonical direction values
- {metrics.effect_size_null} findings missing effect_size ({100 - effect_size_pct:.1f}%)
- {metrics.vague_antecedents} vague antecedents ({vague_pct:.1f}%)

**Next Action**: Focus on P1 items (direction normalization, effect size recovery) before scaling extraction further.

---

**Generated**: 2026-03-01
**Auditor**: Claude Code (RV5-3)
**Data Source**: {num_extraction_files} extraction JSON files from `data/extractions/`
"""

    return report


if __name__ == "__main__":
    main()
