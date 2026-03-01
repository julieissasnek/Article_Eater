"""
Extraction Field Validator — H1 Coordination Handoff
=====================================================
Validates all 11 extraction finding fields per rules in
contracts/schemas/extraction_quality_rules.json and the spec in
docs/EXTRACTION_FIELD_QUALITY_FRAMEWORK_2026-02-28.md.

Usage:
    from src.qa.extraction_field_validator import ExtractionFieldValidator

    validator = ExtractionFieldValidator()
    report = validator.validate_article("data/extractions/10.1234_example.json")
    print(report.quality_score)     # 0.0–1.0
    print(report.critical_errors)   # List of critical violations
    print(report.summary())         # Human-readable summary

    # Batch validation
    batch = validator.validate_batch("data/extractions/")
    print(batch.mean_score)
    print(batch.articles_below_threshold(0.75))
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RULES_FILE = PROJECT_ROOT / "contracts" / "schemas" / "extraction_quality_rules.json"


# --- Data models ---

class Severity(str, Enum):
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Violation:
    """A single rule violation."""
    rule_id: str
    field: str
    severity: Severity
    message: str
    finding_index: int = 0
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "field": self.field,
            "severity": self.severity.value,
            "message": self.message,
            "finding_index": self.finding_index,
            **self.details,
        }


@dataclass
class FindingReport:
    """Validation report for a single finding."""
    index: int
    violations: list[Violation] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not any(v.severity in (Severity.CRITICAL, Severity.ERROR) for v in self.violations)

    @property
    def score(self) -> float:
        """Quality score: 1.0 minus penalty for violations."""
        penalty = 0.0
        for v in self.violations:
            if v.severity == Severity.CRITICAL:
                penalty += 0.25
            elif v.severity == Severity.ERROR:
                penalty += 0.15
            elif v.severity == Severity.WARNING:
                penalty += 0.05
            # INFO: no penalty
        return max(0.0, 1.0 - penalty)


@dataclass
class ArticleReport:
    """Validation report for an entire article."""
    source_file: str
    finding_reports: list[FindingReport] = field(default_factory=list)
    article_family: str | None = None  # For family-specific threshold lookup

    @property
    def quality_score(self) -> float:
        if not self.finding_reports:
            return 0.0
        return sum(r.score for r in self.finding_reports) / len(self.finding_reports)

    @property
    def total_findings(self) -> int:
        return len(self.finding_reports)

    @property
    def critical_errors(self) -> list[Violation]:
        return [v for r in self.finding_reports for v in r.violations
                if v.severity == Severity.CRITICAL]

    @property
    def all_violations(self) -> list[Violation]:
        return [v for r in self.finding_reports for v in r.violations]

    def violations_by_severity(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for v in self.all_violations:
            counts[v.severity.value] = counts.get(v.severity.value, 0) + 1
        return counts

    def violations_by_field(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for v in self.all_violations:
            counts[v.field] = counts.get(v.field, 0) + 1
        return counts

    def summary(self) -> str:
        sev = self.violations_by_severity()
        fld = self.violations_by_field()
        lines = [
            f"Article: {self.source_file}",
            f"Findings: {self.total_findings}",
            f"Quality Score: {self.quality_score:.3f}",
            f"Violations: {len(self.all_violations)} "
            f"(critical={sev.get('critical', 0)}, error={sev.get('error', 0)}, "
            f"warning={sev.get('warning', 0)}, info={sev.get('info', 0)})",
        ]
        if fld:
            top = sorted(fld.items(), key=lambda x: -x[1])[:5]
            lines.append("Top violation fields: " + ", ".join(f"{k}={v}" for k, v in top))
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "source_file": self.source_file,
            "quality_score": round(self.quality_score, 4),
            "total_findings": self.total_findings,
            "violations_by_severity": self.violations_by_severity(),
            "violations_by_field": self.violations_by_field(),
            "finding_reports": [
                {
                    "index": r.index,
                    "score": round(r.score, 4),
                    "violations": [v.to_dict() for v in r.violations],
                }
                for r in self.finding_reports
            ],
        }


@dataclass
class BatchReport:
    """Validation report for a batch of articles."""
    articles: list[ArticleReport] = field(default_factory=list)

    @property
    def mean_score(self) -> float:
        if not self.articles:
            return 0.0
        return sum(a.quality_score for a in self.articles) / len(self.articles)

    @property
    def total_findings(self) -> int:
        return sum(a.total_findings for a in self.articles)

    @property
    def total_violations(self) -> int:
        return sum(len(a.all_violations) for a in self.articles)

    def articles_below_threshold(self, threshold: float = 0.75) -> list[ArticleReport]:
        return [a for a in self.articles if a.quality_score < threshold]

    def summary(self) -> str:
        below = self.articles_below_threshold(0.75)
        return (
            f"Batch: {len(self.articles)} articles, {self.total_findings} findings\n"
            f"Mean quality: {self.mean_score:.3f}\n"
            f"Total violations: {self.total_violations}\n"
            f"Articles below 0.75: {len(below)}/{len(self.articles)}"
        )

    def to_dict(self) -> dict:
        return {
            "mean_score": round(self.mean_score, 4),
            "total_articles": len(self.articles),
            "total_findings": self.total_findings,
            "total_violations": self.total_violations,
            "articles_below_075": len(self.articles_below_threshold(0.75)),
            "articles": [a.to_dict() for a in self.articles],
        }


# --- Validator ---

class ExtractionFieldValidator:
    """Validates extraction findings against quality rules.

    Loads rules from contracts/schemas/extraction_quality_rules.json.
    Validates each field per the spec in the Extraction Field Quality Framework.
    """

    def __init__(self, rules_path: Path | str | None = None):
        rules_path = Path(rules_path) if rules_path else RULES_FILE
        if rules_path.exists():
            with open(rules_path) as f:
                self._rules = json.load(f)
        else:
            logger.warning(f"Rules file not found: {rules_path}; using built-in rules")
            self._rules = {"fields": {}}

        self._field_rules = self._rules.get("fields", {})

    # --- Public API ---

    def validate_finding(self, finding: dict, index: int = 0,
                         article_type: str | None = None,
                         article_family: str | None = None) -> FindingReport:
        """
        Validate a single finding dict against all field rules.

        Args:
            finding: Finding dict from extraction JSON
            index: Finding index (for error reporting)
            article_type: Article type (e.g., 'experimental', 'qualitative')
            article_family: Article family (e.g., 'empirical', 'qualitative')
        """
        report = FindingReport(index=index)

        # Extract fields with defaults
        antecedent = finding.get("antecedent", "")
        consequent = finding.get("consequent", "")
        direction = finding.get("direction")
        claim_type = finding.get("claim_type")
        measure_type = finding.get("measure_type")
        p_value = finding.get("p_value")
        effect_size = finding.get("effect_size")
        effect_size_type = finding.get("effect_size_type")
        sample_size = finding.get("sample_size") or finding.get("n")
        ci = finding.get("confidence_interval")
        test_statistic = finding.get("test_statistic")

        # 1. ANTECEDENT
        report.violations.extend(
            self._validate_antecedent(antecedent, consequent, claim_type, index)
        )

        # 2. CONSEQUENT
        report.violations.extend(
            self._validate_consequent(consequent, antecedent,
                                      finding.get("outcome_domain"), measure_type, index)
        )

        # 3. DIRECTION
        report.violations.extend(
            self._validate_direction(direction, effect_size, p_value, claim_type, index)
        )

        # 4. CLAIM TYPE
        report.violations.extend(
            self._validate_claim_type(claim_type, p_value, effect_size,
                                      test_statistic, article_type, index)
        )

        # 5. MEASURE TYPE
        report.violations.extend(
            self._validate_measure_type(measure_type, consequent, claim_type, index)
        )

        # 6. P-VALUE
        report.violations.extend(
            self._validate_p_value(p_value, direction, claim_type, test_statistic, index)
        )

        # 7. EFFECT SIZE
        report.violations.extend(
            self._validate_effect_size(effect_size, effect_size_type, direction,
                                       claim_type, index)
        )

        # 8. EFFECT SIZE TYPE
        report.violations.extend(
            self._validate_effect_size_type(effect_size_type, effect_size, index)
        )

        # 9. SAMPLE SIZE
        report.violations.extend(
            self._validate_sample_size(sample_size, claim_type, index)
        )

        # 10. CONFIDENCE INTERVAL
        report.violations.extend(
            self._validate_confidence_interval(ci, effect_size, index)
        )

        # 11. TEST STATISTIC
        report.violations.extend(
            self._validate_test_statistic(test_statistic, p_value, sample_size, index)
        )

        # 12. CONSISTENCY RULES (Panel B, B2)
        report.violations.extend(
            self._check_consistency_rules(finding, article_family, index)
        )

        return report

    def validate_article(self, path: str | Path) -> ArticleReport:
        """Validate all findings in an extraction JSON file."""
        path = Path(path)
        report = ArticleReport(source_file=str(path.name))

        try:
            with open(path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Cannot load {path}: {e}")
            return report

        # Find findings array
        findings = self._extract_findings(data)
        article_type = data.get("article_type") or data.get("_meta", {}).get("article_type")
        article_family = data.get("article_family") or data.get("_meta", {}).get("article_family")

        # Store article_family in report for later use
        report.article_family = article_family

        for i, finding in enumerate(findings):
            finding_report = self.validate_finding(finding, index=i,
                                                    article_type=article_type,
                                                    article_family=article_family)
            report.finding_reports.append(finding_report)

        return report

    def validate_batch(self, directory: str | Path,
                       pattern: str = "*.json") -> BatchReport:
        """Validate all extraction JSONs in a directory."""
        directory = Path(directory)
        batch = BatchReport()

        for path in sorted(directory.glob(pattern)):
            if path.name.startswith("_") or "batch_" in path.name:
                continue  # Skip batch log files
            try:
                article_report = self.validate_article(path)
                if article_report.total_findings > 0:
                    batch.articles.append(article_report)
            except Exception as e:
                logger.error(f"Error validating {path}: {e}")

        return batch

    # --- Field validators ---

    def _validate_antecedent(self, antecedent: Any, consequent: str,
                             claim_type: str | None, idx: int) -> list[Violation]:
        violations = []

        # A1: Not empty
        if not antecedent or not isinstance(antecedent, str) or not antecedent.strip():
            violations.append(Violation(
                rule_id="A1_NULL_ANTECEDENT", field="antecedent",
                severity=Severity.CRITICAL,
                message="Antecedent cannot be null or empty",
                finding_index=idx,
            ))
            return violations  # Can't check further

        # A2: Vague patterns
        vague_patterns = [
            r"environmental features",
            r"various\s+\w+",
            r"multiple\s+factors",
            r"different\s+\w+",
            r"various\s+conditions",
            r"^conditions?$",
            r"^factors?$",
        ]
        for pat in vague_patterns:
            if re.search(pat, antecedent, re.IGNORECASE):
                violations.append(Violation(
                    rule_id="A2_VAGUE_ANTECEDENT", field="antecedent",
                    severity=Severity.ERROR,
                    message=f"Vague antecedent matched: '{pat}'",
                    finding_index=idx,
                ))
                break

        # A3: Outcome language in antecedent
        outcome_markers = [
            "improved", "increased well-being", "better", "worse",
            "reduced stress", "better performance", "higher anxiety",
            "lower depression",
        ]
        for marker in outcome_markers:
            if marker.lower() in antecedent.lower():
                violations.append(Violation(
                    rule_id="A3_OUTCOME_IN_ANTECEDENT", field="antecedent",
                    severity=Severity.ERROR,
                    message=f"Antecedent contains outcome language: '{marker}'",
                    finding_index=idx,
                ))
                break

        # A4: Bare demographic as IV
        if claim_type in ("causal", "empirical_finding"):
            demo_patterns = [r"^age\s+group", r"^gender", r"^education\s+level", r"^socioeconomic"]
            for pat in demo_patterns:
                if re.search(pat, antecedent, re.IGNORECASE):
                    violations.append(Violation(
                        rule_id="A4_BARE_DEMOGRAPHIC", field="antecedent",
                        severity=Severity.WARNING,
                        message=f"Demographic variable used as IV: '{pat}'",
                        finding_index=idx,
                    ))
                    break

        # A5: Length check
        alen = len(antecedent.strip())
        if alen < 5:
            violations.append(Violation(
                rule_id="A5_LENGTH_CHECK", field="antecedent",
                severity=Severity.WARNING,
                message=f"Antecedent too short ({alen} chars)",
                finding_index=idx,
            ))
        elif alen > 500:
            violations.append(Violation(
                rule_id="A5_LENGTH_CHECK", field="antecedent",
                severity=Severity.WARNING,
                message=f"Antecedent too long ({alen} chars)",
                finding_index=idx,
            ))

        return violations

    def _validate_consequent(self, consequent: Any, antecedent: str,
                             outcome_domain: str | None, measure_type: str | None,
                             idx: int) -> list[Violation]:
        violations = []

        # C1: Not empty
        if not consequent or not isinstance(consequent, str) or not consequent.strip():
            violations.append(Violation(
                rule_id="C1_NULL_CONSEQUENT", field="consequent",
                severity=Severity.CRITICAL,
                message="Consequent cannot be null or empty",
                finding_index=idx,
            ))
            return violations

        # C2: Restatement of antecedent
        if antecedent and isinstance(antecedent, str):
            ant_tokens = set(antecedent.lower().split())
            con_tokens = set(consequent.lower().split())
            if con_tokens:
                overlap = ant_tokens & con_tokens
                ratio = len(overlap) / len(con_tokens)
                if ratio > 0.6:
                    violations.append(Violation(
                        rule_id="C2_RESTATEMENT_OF_ANTECEDENT", field="consequent",
                        severity=Severity.ERROR,
                        message=f"Consequent overlaps {ratio:.0%} with antecedent",
                        finding_index=idx,
                    ))

        # C3: Domain mismatch
        domain_keywords = {
            "health": ["health", "well-being", "wellbeing", "illness", "disease", "disorder"],
            "affect": ["mood", "emotion", "affect", "anxiety", "depression", "stress",
                       "happiness", "satisfaction"],
            "cognition": ["memory", "attention", "working memory", "cognitive", "mental",
                          "learning", "comprehension", "performance", "reasoning"],
            "behavior": ["behavior", "action", "activity", "engagement", "avoidance",
                         "approach", "movement"],
            "perception": ["perception", "aesthetic", "preference", "liking", "judgment",
                           "beauty", "appeal", "valence"],
            "physiology": ["cortisol", "heart rate", "blood pressure", "eeg", "fmri",
                           "pupil", "galvanic", "respiration", "hpa axis", "hormone"],
        }
        if outcome_domain and outcome_domain in domain_keywords:
            kws = domain_keywords[outcome_domain]
            if not any(kw in consequent.lower() for kw in kws):
                violations.append(Violation(
                    rule_id="C3_DOMAIN_MISMATCH", field="consequent",
                    severity=Severity.ERROR,
                    message=f"Consequent doesn't match outcome_domain='{outcome_domain}'",
                    finding_index=idx,
                ))

        # C4: Measure type mismatch
        measure_keywords = {
            "physiological": ["cortisol", "heart rate", "eeg", "fmri", "blood pressure",
                              "pupil", "galvanic", "hpa", "amygdala"],
            "behavioral": ["behavior", "action", "movement", "choice", "approach", "avoidance"],
            "self_report": ["reported", "self-reported", "perceived", "subjective",
                            "rated", "questionnaire"],
        }
        if measure_type and measure_type in measure_keywords:
            kws = measure_keywords[measure_type]
            if not any(kw in consequent.lower() for kw in kws):
                violations.append(Violation(
                    rule_id="C4_MEASURE_TYPE_MISMATCH", field="consequent",
                    severity=Severity.WARNING,
                    message=f"Consequent doesn't match measure_type='{measure_type}'",
                    finding_index=idx,
                ))

        # C5: Length
        clen = len(consequent.strip())
        if clen < 3:
            violations.append(Violation(
                rule_id="C5_LENGTH_CHECK", field="consequent",
                severity=Severity.WARNING,
                message=f"Consequent too short ({clen} chars)",
                finding_index=idx,
            ))
        elif clen > 300:
            violations.append(Violation(
                rule_id="C5_LENGTH_CHECK", field="consequent",
                severity=Severity.WARNING,
                message=f"Consequent too long ({clen} chars)",
                finding_index=idx,
            ))

        return violations

    def _validate_direction(self, direction: Any, effect_size: Any,
                            p_value: Any, claim_type: str | None,
                            idx: int) -> list[Violation]:
        violations = []
        canonical = {"increase", "decrease", "no_effect", "mixed", None}

        # D1: Canonical value
        if direction not in canonical:
            violations.append(Violation(
                rule_id="D1_INVALID_DIRECTION", field="direction",
                severity=Severity.CRITICAL,
                message=f"Invalid direction '{direction}'. Must be increase/decrease/no_effect/mixed.",
                finding_index=idx,
            ))
            return violations

        # D2: Mixed + effect_size
        if direction == "mixed" and effect_size is not None:
            violations.append(Violation(
                rule_id="D2_MIXED_WITH_EFFECT_SIZE", field="direction",
                severity=Severity.ERROR,
                message=f"direction='mixed' paired with effect_size={effect_size}",
                finding_index=idx,
            ))

        # D3: Direction-ES sign mismatch
        if effect_size is not None and direction is not None:
            try:
                es = float(effect_size)
                tol = 0.01
                if direction == "increase" and es < -tol:
                    violations.append(Violation(
                        rule_id="D3_DIRECTION_EFFECT_MISMATCH", field="direction",
                        severity=Severity.ERROR,
                        message=f"direction='increase' but effect_size={es}",
                        finding_index=idx,
                    ))
                elif direction == "decrease" and es > tol:
                    violations.append(Violation(
                        rule_id="D3_DIRECTION_EFFECT_MISMATCH", field="direction",
                        severity=Severity.ERROR,
                        message=f"direction='decrease' but effect_size={es}",
                        finding_index=idx,
                    ))
            except (TypeError, ValueError):
                pass

        # D4: Significance mismatch
        if claim_type in ("causal", "empirical_finding", "associational") and p_value is not None:
            try:
                pv = float(p_value)
                if pv >= 0.05 and direction in ("increase", "decrease"):
                    violations.append(Violation(
                        rule_id="D4_SIGNIFICANCE_MISMATCH", field="direction",
                        severity=Severity.WARNING,
                        message=f"direction='{direction}' but p={pv}>=0.05 (not significant)",
                        finding_index=idx,
                    ))
                if pv < 0.05 and direction == "no_effect":
                    violations.append(Violation(
                        rule_id="D4_SIGNIFICANCE_MISMATCH", field="direction",
                        severity=Severity.ERROR,
                        message=f"direction='no_effect' but p={pv}<0.05 (significant)",
                        finding_index=idx,
                    ))
            except (TypeError, ValueError):
                pass

        # D5: Null direction for empirical
        if claim_type in ("causal", "empirical_finding") and direction is None:
            violations.append(Violation(
                rule_id="D5_NULL_DIRECTION_EMPIRICAL", field="direction",
                severity=Severity.ERROR,
                message="Direction is null for empirical claim",
                finding_index=idx,
            ))

        return violations

    def _validate_claim_type(self, claim_type: Any, p_value: Any,
                             effect_size: Any, test_statistic: Any,
                             article_type: str | None, idx: int) -> list[Violation]:
        violations = []
        canonical_types = {
            "empirical_finding", "theoretical_proposition", "causal", "associational",
            "synthesized", "narrative", "qualitative_theme", "null", "moderated",
            "pooled_effect", "cited", "vote_count", "methodological",
            "derived_guideline", "claimed", "statistical", "comparative",
            "limitation", "theoretical_critique", None,
        }

        # CT1: Valid enum
        if claim_type not in canonical_types:
            violations.append(Violation(
                rule_id="CT1_INVALID_CLAIM_TYPE", field="claim_type",
                severity=Severity.ERROR,
                message=f"Invalid claim_type '{claim_type}'",
                finding_index=idx,
            ))

        # CT2: Empirical without stats
        if claim_type == "empirical_finding":
            has_stats = any(x is not None for x in [p_value, effect_size, test_statistic])
            if not has_stats:
                violations.append(Violation(
                    rule_id="CT2_EMPIRICAL_WITHOUT_STATS", field="claim_type",
                    severity=Severity.ERROR,
                    message="empirical_finding has no statistics (p, ES, or test stat)",
                    finding_index=idx,
                ))

        # CT3: Article-claim coherence
        if article_type in ("empirical_research", "experimental"):
            if claim_type in ("narrative", "theoretical_proposition"):
                violations.append(Violation(
                    rule_id="CT3_ARTICLE_CLAIM_TYPE_MISMATCH", field="claim_type",
                    severity=Severity.WARNING,
                    message=f"claim_type='{claim_type}' unusual for article_type='{article_type}'",
                    finding_index=idx,
                ))

        return violations

    def _validate_measure_type(self, measure_type: Any, consequent: str,
                                claim_type: str | None, idx: int) -> list[Violation]:
        violations = []
        canonical = {"self_report", "behavioral", "physiological", "cognitive_task",
                     "observational", "mixed", None}

        # MT1: Valid value
        if measure_type not in canonical:
            violations.append(Violation(
                rule_id="MT1_INVALID_MEASURE_TYPE", field="measure_type",
                severity=Severity.ERROR,
                message=f"Invalid measure_type '{measure_type}'",
                finding_index=idx,
            ))

        # MT2: Null for empirical
        if claim_type in ("empirical_finding", "causal") and measure_type is None:
            violations.append(Violation(
                rule_id="MT2_NULL_MEASURE_EMPIRICAL", field="measure_type",
                severity=Severity.ERROR,
                message="measure_type null for empirical claim",
                finding_index=idx,
            ))

        # MT3: Consistency with consequent
        if measure_type == "physiological" and consequent:
            physio = ["cortisol", "heart rate", "eeg", "fmri", "blood pressure", "pupil"]
            if not any(t in consequent.lower() for t in physio):
                violations.append(Violation(
                    rule_id="MT3_MEASURE_CONSEQUENT_MISMATCH", field="measure_type",
                    severity=Severity.WARNING,
                    message="measure_type='physiological' but no physio terms in consequent",
                    finding_index=idx,
                ))

        return violations

    def _validate_p_value(self, p_value: Any, direction: Any,
                          claim_type: str | None, test_statistic: Any,
                          idx: int) -> list[Violation]:
        violations = []

        if p_value is not None:
            # PV1: Range
            try:
                pv = float(p_value)
                if pv < 0 or pv > 1:
                    violations.append(Violation(
                        rule_id="PV1_OUT_OF_RANGE", field="p_value",
                        severity=Severity.ERROR,
                        message=f"p_value={pv} out of [0,1]",
                        finding_index=idx,
                    ))
            except (TypeError, ValueError):
                if isinstance(p_value, str):
                    m = re.search(r"<?\\s*(0\\.\\d+)", str(p_value))
                    if m:
                        violations.append(Violation(
                            rule_id="PV2_STRING_FORMAT", field="p_value",
                            severity=Severity.WARNING,
                            message="p_value stored as string, should be numeric",
                            finding_index=idx,
                        ))
                    else:
                        violations.append(Violation(
                            rule_id="PV1_OUT_OF_RANGE", field="p_value",
                            severity=Severity.ERROR,
                            message=f"p_value unparseable: {p_value}",
                            finding_index=idx,
                        ))
                else:
                    violations.append(Violation(
                        rule_id="PV1_OUT_OF_RANGE", field="p_value",
                        severity=Severity.ERROR,
                        message=f"p_value invalid type: {type(p_value)}",
                        finding_index=idx,
                    ))

        # PV4: Null for empirical
        if claim_type in ("empirical_finding", "causal") and p_value is None:
            violations.append(Violation(
                rule_id="PV4_NULL_P_EMPIRICAL", field="p_value",
                severity=Severity.ERROR,
                message="p_value null for empirical claim",
                finding_index=idx,
            ))

        # PV5: p in narrative
        if claim_type in ("narrative", "theoretical_proposition") and p_value is not None:
            violations.append(Violation(
                rule_id="PV5_P_IN_NARRATIVE", field="p_value",
                severity=Severity.WARNING,
                message="p_value present for narrative/theoretical claim",
                finding_index=idx,
            ))

        return violations

    def _validate_effect_size(self, effect_size: Any, effect_size_type: Any,
                               direction: Any, claim_type: str | None,
                               idx: int) -> list[Violation]:
        violations = []

        if effect_size is not None:
            try:
                es = float(effect_size)

                # ES1: Range by type
                ranges = {
                    "eta_squared": (0, 1),
                    "partial_eta_squared": (0, 1),
                    "r": (-1, 1),
                    "r_correlation": (-1, 1),
                    "Cohen's d": (-5, 5),
                    "cohen_d": (-5, 5),
                    "odds_ratio": (0, 1000),
                    "Cohen's f": (0, 1),
                    "cohen_f": (0, 1),
                }
                if effect_size_type and effect_size_type in ranges:
                    lo, hi = ranges[effect_size_type]
                    if es < lo or es > hi:
                        violations.append(Violation(
                            rule_id="ES1_RANGE_VALIDATION", field="effect_size",
                            severity=Severity.ERROR,
                            message=f"effect_size={es} out of range [{lo},{hi}] for {effect_size_type}",
                            finding_index=idx,
                        ))

                # ES2: Direction consistency
                if direction is not None:
                    tol = 0.01
                    if direction == "increase" and es < -tol:
                        violations.append(Violation(
                            rule_id="ES2_DIRECTION_MISMATCH", field="effect_size",
                            severity=Severity.ERROR,
                            message=f"direction='increase' but effect_size={es}",
                            finding_index=idx,
                        ))
                    elif direction == "decrease" and es > tol:
                        violations.append(Violation(
                            rule_id="ES2_DIRECTION_MISMATCH", field="effect_size",
                            severity=Severity.ERROR,
                            message=f"direction='decrease' but effect_size={es}",
                            finding_index=idx,
                        ))
                    elif direction == "mixed":
                        violations.append(Violation(
                            rule_id="ES2_DIRECTION_MISMATCH", field="effect_size",
                            severity=Severity.ERROR,
                            message=f"direction='mixed' should have null effect_size",
                            finding_index=idx,
                        ))

            except (TypeError, ValueError):
                violations.append(Violation(
                    rule_id="ES1_RANGE_VALIDATION", field="effect_size",
                    severity=Severity.ERROR,
                    message=f"effect_size not numeric: {effect_size}",
                    finding_index=idx,
                ))

        # ES3: Null for empirical
        if claim_type in ("empirical_finding", "causal") and effect_size is None:
            violations.append(Violation(
                rule_id="ES3_NULL_ES_EMPIRICAL", field="effect_size",
                severity=Severity.ERROR,
                message="effect_size null for empirical claim",
                finding_index=idx,
            ))

        # ES4: Type required with ES
        if effect_size is not None and effect_size_type is None:
            violations.append(Violation(
                rule_id="ES4_NULL_TYPE_WITH_ES", field="effect_size",
                severity=Severity.ERROR,
                message="effect_size present but effect_size_type is null",
                finding_index=idx,
            ))

        return violations

    def _validate_effect_size_type(self, est: Any, effect_size: Any,
                                    idx: int) -> list[Violation]:
        violations = []

        # EST1: Required if ES present
        if effect_size is not None and est is None:
            violations.append(Violation(
                rule_id="EST1_REQUIRED_WITH_ES", field="effect_size_type",
                severity=Severity.ERROR,
                message="effect_size present but effect_size_type null",
                finding_index=idx,
            ))

        # EST2: Standardization
        if est and isinstance(est, str):
            normalized = est.strip().lower()
            suggestions = {
                "cohens d": "Cohen's d",
                "cohen d": "Cohen's d",
                "d": "Cohen's d",
                "eta squared": "eta_squared",
                "eta2": "eta_squared",
                "eta^2": "eta_squared",
                "partial eta squared": "partial_eta_squared",
                "partial eta-squared": "partial_eta_squared",
                "correlation coefficient": "r",
                "pearson r": "r",
            }
            if normalized in suggestions:
                violations.append(Violation(
                    rule_id="EST2_STANDARDIZATION", field="effect_size_type",
                    severity=Severity.WARNING,
                    message=f"'{est}' should be '{suggestions[normalized]}'",
                    finding_index=idx,
                ))

        return violations

    def _validate_sample_size(self, sample_size: Any, claim_type: str | None,
                               idx: int) -> list[Violation]:
        violations = []

        if sample_size is not None:
            # SS1: Type and range
            try:
                n = int(sample_size)
                if n <= 0:
                    violations.append(Violation(
                        rule_id="SS1_TYPE_RANGE", field="sample_size",
                        severity=Severity.ERROR,
                        message=f"sample_size={n} is non-positive",
                        finding_index=idx,
                    ))
                elif n > 1_000_000:
                    violations.append(Violation(
                        rule_id="SS1_TYPE_RANGE", field="sample_size",
                        severity=Severity.ERROR,
                        message=f"sample_size={n} implausibly large",
                        finding_index=idx,
                    ))
            except (TypeError, ValueError):
                violations.append(Violation(
                    rule_id="SS1_TYPE_RANGE", field="sample_size",
                    severity=Severity.ERROR,
                    message=f"sample_size not integer: {sample_size}",
                    finding_index=idx,
                ))

        # SS2: Null for empirical
        if claim_type in ("empirical_finding", "causal") and sample_size is None:
            violations.append(Violation(
                rule_id="SS2_NULL_FOR_EMPIRICAL", field="sample_size",
                severity=Severity.WARNING,
                message="sample_size null for empirical claim",
                finding_index=idx,
            ))

        # SS3: N in narrative
        if claim_type in ("narrative", "theoretical_proposition") and sample_size is not None:
            violations.append(Violation(
                rule_id="SS3_N_IN_NARRATIVE", field="sample_size",
                severity=Severity.INFO,
                message="sample_size present for narrative claim",
                finding_index=idx,
            ))

        return violations

    def _validate_confidence_interval(self, ci: Any, effect_size: Any,
                                       idx: int) -> list[Violation]:
        violations = []

        if ci is None:
            return violations

        # CI1: Format
        if not isinstance(ci, (list, tuple)):
            violations.append(Violation(
                rule_id="CI1_FORMAT", field="confidence_interval",
                severity=Severity.ERROR,
                message=f"confidence_interval not a list: {type(ci)}",
                finding_index=idx,
            ))
            return violations

        if len(ci) != 2:
            violations.append(Violation(
                rule_id="CI1_FORMAT", field="confidence_interval",
                severity=Severity.ERROR,
                message=f"confidence_interval has {len(ci)} elements, expected 2",
                finding_index=idx,
            ))
            return violations

        try:
            lower, upper = float(ci[0]), float(ci[1])

            # CI2: Ordering
            if lower >= upper:
                violations.append(Violation(
                    rule_id="CI2_ORDERING", field="confidence_interval",
                    severity=Severity.ERROR,
                    message=f"CI lower ({lower}) >= upper ({upper})",
                    finding_index=idx,
                ))

            # CI3: ES containment
            if effect_size is not None:
                es = float(effect_size)
                if not (lower <= es <= upper):
                    violations.append(Violation(
                        rule_id="CI3_ES_CONTAINMENT", field="confidence_interval",
                        severity=Severity.WARNING,
                        message=f"effect_size={es} outside CI [{lower}, {upper}]",
                        finding_index=idx,
                    ))

            # CI4: Plausibility
            width = upper - lower
            if width > 100:
                violations.append(Violation(
                    rule_id="CI4_PLAUSIBILITY", field="confidence_interval",
                    severity=Severity.WARNING,
                    message=f"CI very wide (width={width:.1f})",
                    finding_index=idx,
                ))

        except (TypeError, ValueError):
            violations.append(Violation(
                rule_id="CI1_FORMAT", field="confidence_interval",
                severity=Severity.ERROR,
                message=f"CI contains non-numeric values: {ci}",
                finding_index=idx,
            ))

        return violations

    def _validate_test_statistic(self, test_statistic: Any, p_value: Any,
                                  sample_size: Any, idx: int) -> list[Violation]:
        violations = []

        if test_statistic is None:
            # TS4: Null with other data present
            if sample_size is not None:
                violations.append(Violation(
                    rule_id="TS4_NULL_WITH_DATA", field="test_statistic",
                    severity=Severity.INFO,
                    message="test_statistic null while sample_size is present",
                    finding_index=idx,
                ))
            return violations

        if not isinstance(test_statistic, str):
            return violations

        # TS1: Format check
        standard_patterns = [
            r"[tT]\s*\(\s*\d+\s*\)",       # t(df)
            r"[Ff]\s*\(\s*\d+\s*,\s*\d+",  # F(df1, df2)
            r"[χX]²?\s*\(\s*\d+",          # χ²(df)
            r"[zZ]\s*=",                     # z =
            r"[rR]\s*=",                     # r =
        ]
        matches_any = any(re.search(p, test_statistic) for p in standard_patterns)
        if not matches_any and len(test_statistic.strip()) > 0:
            violations.append(Violation(
                rule_id="TS1_FORMAT", field="test_statistic",
                severity=Severity.WARNING,
                message=f"Non-standard test_statistic format: '{test_statistic[:60]}'",
                finding_index=idx,
            ))

        # TS2: DF vs N consistency (basic)
        if sample_size is not None:
            df_match = re.search(r"\(\s*(\d+)\s*\)", test_statistic)
            if df_match:
                try:
                    df = int(df_match.group(1))
                    n = int(sample_size)
                    if df > n:
                        violations.append(Violation(
                            rule_id="TS2_DF_VS_N", field="test_statistic",
                            severity=Severity.WARNING,
                            message=f"Degrees of freedom ({df}) > sample_size ({n})",
                            finding_index=idx,
                        ))
                except (TypeError, ValueError):
                    pass

        return violations

    def _check_consistency_rules(self, finding: dict, article_family: str | None,
                                 idx: int) -> list[Violation]:
        """
        Check cross-field consistency rules (Panel B, B2).

        These rules validate relationships between multiple fields that might be
        contradictory or implausible even if individually valid.
        """
        violations = []

        direction = finding.get('direction')
        effect_size = finding.get('effect_size')
        effect_size_type = finding.get('effect_size_type')
        p_value = finding.get('p_value')
        claim_type = finding.get('claim_type')
        sample_size = finding.get('sample_size')

        # CONSIST-1: Direction vs effect_size consistency
        if (direction in ['increase', 'decrease'] and
                effect_size is not None and
                effect_size_type in ["Cohen's d", 'r', "Hedges' g"]):
            if direction == 'increase' and effect_size < 0:
                violations.append(Violation(
                    rule_id="CONSIST-1", field="cross_field",
                    severity=Severity.ERROR,
                    message="Direction is 'increase' but effect_size is negative",
                    finding_index=idx,
                ))
            elif direction == 'decrease' and effect_size > 0:
                violations.append(Violation(
                    rule_id="CONSIST-1", field="cross_field",
                    severity=Severity.ERROR,
                    message="Direction is 'decrease' but effect_size is positive",
                    finding_index=idx,
                ))

        # CONSIST-2: P-value vs direction for causal claims
        if (p_value is not None and
                direction in ['increase', 'decrease'] and
                claim_type == 'causal'):
            try:
                p_float = float(p_value) if isinstance(p_value, (int, float)) else None
                if p_float is not None and p_float > 0.05:
                    violations.append(Violation(
                        rule_id="CONSIST-2", field="cross_field",
                        severity=Severity.ERROR,
                        message=f"Effect not significant (p={p_float}) but claim_type is 'causal'",
                        finding_index=idx,
                    ))
            except (ValueError, TypeError):
                pass

        # CONSIST-3: Causal claim in qualitative paper
        if claim_type == 'causal' and article_family == 'qualitative':
            violations.append(Violation(
                rule_id="CONSIST-3", field="cross_field",
                severity=Severity.WARNING,
                message="Causal claim in qualitative article (qualitative studies cannot establish causality)",
                finding_index=idx,
            ))

        # CONSIST-4: Effect size type without value
        if effect_size_type is not None and effect_size is None:
            violations.append(Violation(
                rule_id="CONSIST-4", field="cross_field",
                severity=Severity.ERROR,
                message=f"effect_size_type={effect_size_type} specified but effect_size is null",
                finding_index=idx,
            ))

        # CONSIST-5: Underpowered causal claim
        if sample_size is not None and sample_size < 10 and claim_type == 'causal':
            violations.append(Violation(
                rule_id="CONSIST-5", field="cross_field",
                severity=Severity.WARNING,
                message=f"Small sample (N={sample_size}) with causal claim (likely underpowered)",
                finding_index=idx,
            ))

        return violations

    # --- Helpers ---

    def _extract_findings(self, data: dict) -> list[dict]:
        """Find the findings array in various extraction JSON formats."""
        # Standard format: data["findings"]
        if "findings" in data and isinstance(data["findings"], list):
            return data["findings"]

        # Nested: data["data"]["findings"]
        if "data" in data and isinstance(data["data"], dict):
            if "findings" in data["data"]:
                return data["data"]["findings"]

        # Key findings format (from new neuroarch extractions)
        if "key_findings" in data and isinstance(data["key_findings"], list):
            # These are string lists, not structured findings — skip validation
            return []

        # Try claims/rules format
        for key in ("claims", "rules", "results"):
            if key in data and isinstance(data[key], list):
                return data[key]

        return []

    # --- Quality Gating (Phase 1B) ---

    def validate_and_gate(self, extraction_path: str | Path,
                          threshold: float = None) -> tuple[bool, float, list[dict]]:
        """
        Validate an extraction file and determine if it passes the quality gate.

        This is the entry point for pipeline-level gating. Returns structured
        results suitable for routing: passing articles proceed, failing articles
        go to repair queue.

        Uses family-specific thresholds if available in extraction data; falls
        back to provided threshold (default 0.75) if family not available.

        Args:
            extraction_path: Path to extraction JSON file
            threshold: Quality score threshold (default 0.75); overridden by family-specific if present

        Returns:
            Tuple of (passed: bool, score: float, violations: list[dict])
            where violations are serializable dicts for logging/repair queue.
        """
        extraction_path = Path(extraction_path)
        report = self.validate_article(extraction_path)

        # Determine threshold: use family-specific if available, else default
        if threshold is None:
            threshold = 0.75

        effective_threshold = threshold
        article_family = getattr(report, 'article_family', None)

        if article_family and hasattr(self, 'rules'):
            family_thresholds = self.rules.get('quality_scoring', {}).get('family_thresholds', {})
            if article_family in family_thresholds:
                # Use blocking threshold for family
                effective_threshold = family_thresholds[article_family].get('blocking', threshold)
                logger.info(f"Using family-specific threshold for '{article_family}': {effective_threshold}")

        violations_dicts = [v.to_dict() for v in report.all_violations]
        passed = report.quality_score >= effective_threshold

        return (passed, report.quality_score, violations_dicts)


# --- CLI ---

def main():
    """Run validation from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="Extraction Field Validator")
    parser.add_argument("path", help="File or directory to validate")
    parser.add_argument("--threshold", type=float, default=0.75,
                        help="Quality threshold for flagging (default: 0.75)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--verbose", action="store_true", help="Show per-finding details")
    args = parser.parse_args()

    validator = ExtractionFieldValidator()
    path = Path(args.path)

    if path.is_dir():
        report = validator.validate_batch(path)
        if args.json:
            print(json.dumps(report.to_dict(), indent=2))
        else:
            print(report.summary())
            print()
            below = report.articles_below_threshold(args.threshold)
            if below:
                print(f"\n--- Articles below {args.threshold} ---")
                for a in sorted(below, key=lambda x: x.quality_score):
                    print(f"  {a.quality_score:.3f} | {a.source_file} "
                          f"({len(a.critical_errors)} critical)")
    else:
        report = validator.validate_article(path)
        if args.json:
            print(json.dumps(report.to_dict(), indent=2))
        else:
            print(report.summary())
            if args.verbose:
                for fr in report.finding_reports:
                    if fr.violations:
                        print(f"\n  Finding #{fr.index} (score={fr.score:.3f}):")
                        for v in fr.violations:
                            print(f"    [{v.severity.value}] {v.rule_id}: {v.message}")


# --- Module-level gating function ---

def gate_extraction(extraction_path: str | Path,
                    threshold: float = 0.75) -> dict:
    """
    Gate an extraction file: passes go through, failing articles move to repair queue.

    This function:
    1. Validates the extraction file using validate_and_gate
    2. If passes: returns success dict
    3. If fails: moves file to data/extractions/needs_repair/ with companion .violations.json

    Args:
        extraction_path: Path to extraction JSON file
        threshold: Quality score threshold (default 0.75)

    Returns:
        dict with keys:
        - passed (bool): Whether the extraction passed the gate
        - score (float): Quality score
        - original_path (str): Original file path
        - new_path (str | None): Path to repair queue (if failed), None if passed
        - n_violations (int): Number of violations found
        - message (str): Human-readable status
    """
    extraction_path = Path(extraction_path)
    validator = ExtractionFieldValidator()

    # Run validation
    passed, score, violations = validator.validate_and_gate(
        extraction_path, threshold
    )

    result = {
        "passed": passed,
        "score": round(score, 4),
        "original_path": str(extraction_path),
        "new_path": None,
        "n_violations": len(violations),
        "message": "",
    }

    if passed:
        result["message"] = (
            f"PASSED: {extraction_path.name} (score={score:.4f}, "
            f"{len(violations)} violations)"
        )
        logger.info(result["message"])
        return result

    # File failed — move to repair queue
    repair_dir = extraction_path.parent / "needs_repair"
    repair_dir.mkdir(exist_ok=True, parents=True)

    new_path = repair_dir / extraction_path.name
    violations_file = repair_dir / f"{extraction_path.stem}.violations.json"

    try:
        # Move extraction to repair queue
        extraction_path.rename(new_path)

        # Write violations manifest
        violations_manifest = {
            "original_path": str(extraction_path),
            "repair_queue_path": str(new_path),
            "quality_score": round(score, 4),
            "threshold": threshold,
            "timestamp": datetime.now().isoformat(),
            "violation_count": len(violations),
            "violations": violations,
        }
        violations_file.write_text(
            json.dumps(violations_manifest, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        result["new_path"] = str(new_path)
        result["message"] = (
            f"FAILED: {extraction_path.name} moved to repair queue "
            f"(score={score:.4f}, {len(violations)} violations). "
            f"See {violations_file.name}"
        )
        logger.warning(result["message"])

    except Exception as e:
        result["message"] = (
            f"ERROR moving {extraction_path.name} to repair queue: {e}"
        )
        logger.error(result["message"])

    return result


if __name__ == "__main__":
    main()
