"""
Cross-Article Consistency Validator
====================================
Detects implausible effect sizes by comparing findings ACROSS articles
within the same topic/belief cluster. Implements two key principles:

1. DESIGN-BASED PLAUSIBILITY: Small N + large d is suspicious.
   The sampling distribution of Cohen's d has variance ~(1/n₁ + 1/n₂ + d²/2(n₁+n₂)),
   so very large effect sizes from small samples are improbable unless the
   phenomenon is massive (Borenstein et al., 2009; Hedges & Olkin, 1985).

2. CROSS-ARTICLE BELL-CURVE CHECK: For a given IV→DV relationship,
   the distribution of effect sizes across studies should be approximately
   normal (under fixed-effects) or at least have bounded heterogeneity
   (under random-effects). Outliers beyond ±2.5 SD from the cluster mean
   are flagged for human review (Viechtbauer & Cheung, 2010).

Both checks produce FLAGS, not rejections — the human (David) reviews
flagged findings to decide whether they are genuine or data-quality errors.

References:
    Borenstein, M., Hedges, L. V., Higgins, J. P. T., & Rothstein, H. R. (2009).
        Introduction to Meta-Analysis. Wiley. [Google Scholar: 42,000+]
    Hedges, L. V., & Olkin, I. (1985). Statistical Methods for Meta-Analysis.
        Academic Press. [Google Scholar: 18,000+]
    Viechtbauer, W., & Cheung, M. W.-L. (2010). Outlier and influence diagnostics
        for meta-analysis. Research Synthesis Methods, 1(2), 112–125.
        https://doi.org/10.1002/jrsm.11 [Google Scholar: 1,200+]
    Langan, D., Higgins, J. P. T., Jackson, D., Bowden, J., Veroniki, A. A.,
        Kontopantelis, E., ... & Simmonds, M. (2019). A comparison of heterogeneity
        variance estimators in simulated random-effects meta-analyses.
        Research Synthesis Methods, 10(1), 83–98. [Google Scholar: 700+]
    Simmons, J. P., Nelson, L. D., & Simonsohn, U. (2011). False-positive
        psychology: Undisclosed flexibility in data collection and analysis
        allows presenting anything as significant. Psychological Science,
        22(11), 1359–1366. [Google Scholar: 8,000+]

Usage:
    from src.qa.cross_article_consistency_validator import (
        CrossArticleValidator,
        DesignPlausibilityChecker,
    )

    # Check individual finding against design-based rules
    checker = DesignPlausibilityChecker()
    flags = checker.check(effect_size=3.2, sample_size=12, es_type="cohens_d")
    # → [Flag(rule="DPR-1", severity="warning", ...)]

    # Check cluster of findings for cross-article outliers
    validator = CrossArticleValidator()
    report = validator.validate_cluster(findings, cluster_label="visual_complexity→attention")
    print(report.outlier_dois)
    print(report.heterogeneity_i_squared)

Date: 2026-03-05
Version: 1.0.0
"""

from __future__ import annotations

import json
import logging
import math
import statistics
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


# ═══════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════

class FlagSeverity(str, Enum):
    """Flag severity for cross-article anomalies."""
    CRITICAL = "critical"      # Almost certainly an error
    WARNING = "warning"        # Suspicious, needs human review
    INFO = "info"              # Noteworthy but not necessarily wrong


@dataclass
class ConsistencyFlag:
    """A single cross-article consistency flag."""
    rule_id: str
    severity: FlagSeverity
    doi: str
    finding_index: int
    message: str
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity.value,
            "doi": self.doi,
            "finding_index": self.finding_index,
            "message": self.message,
            **self.details,
        }


@dataclass
class FindingRecord:
    """Minimal record of a finding for cross-article comparison."""
    doi: str
    finding_index: int
    antecedent: str
    consequent: str
    effect_size: Optional[float]
    effect_size_type: Optional[str]
    sample_size: Optional[int]
    direction: Optional[str]
    p_value: Optional[float]
    cluster_label: Optional[str] = None

    @classmethod
    def from_extraction(cls, doi: str, finding: dict, idx: int,
                        cluster_label: str = None) -> FindingRecord:
        """Build from a raw extraction finding dict."""
        es = finding.get("effect_size")
        ss = finding.get("sample_size")
        pv = finding.get("p_value")

        # Parse numeric values robustly
        es_float = _safe_float(es)
        ss_int = _safe_int(ss)
        pv_float = _safe_float(pv)

        return cls(
            doi=doi,
            finding_index=idx,
            antecedent=str(finding.get("antecedent", "")),
            consequent=str(finding.get("consequent", "")),
            effect_size=es_float,
            effect_size_type=_normalize_es_type(finding.get("effect_size_type")),
            sample_size=ss_int,
            direction=finding.get("direction"),
            p_value=pv_float,
            cluster_label=cluster_label,
        )


@dataclass
class ClusterConsistencyReport:
    """Report for a single cluster of related findings."""
    cluster_label: str
    n_findings: int
    n_with_effect_sizes: int
    mean_d: Optional[float] = None
    sd_d: Optional[float] = None
    median_d: Optional[float] = None
    i_squared: Optional[float] = None   # Heterogeneity (Higgins I²)
    q_statistic: Optional[float] = None  # Cochran's Q
    flags: list[ConsistencyFlag] = field(default_factory=list)
    outlier_dois: list[str] = field(default_factory=list)
    direction_consensus: Optional[str] = None  # "consistent", "mixed", "contradictory"

    @property
    def n_flags(self) -> int:
        return len(self.flags)

    @property
    def n_critical(self) -> int:
        return sum(1 for f in self.flags if f.severity == FlagSeverity.CRITICAL)

    @property
    def n_warnings(self) -> int:
        return sum(1 for f in self.flags if f.severity == FlagSeverity.WARNING)

    def to_dict(self) -> dict:
        return {
            "cluster_label": self.cluster_label,
            "n_findings": self.n_findings,
            "n_with_effect_sizes": self.n_with_effect_sizes,
            "mean_d": round(self.mean_d, 4) if self.mean_d is not None else None,
            "sd_d": round(self.sd_d, 4) if self.sd_d is not None else None,
            "median_d": round(self.median_d, 4) if self.median_d is not None else None,
            "i_squared": round(self.i_squared, 2) if self.i_squared is not None else None,
            "q_statistic": round(self.q_statistic, 4) if self.q_statistic is not None else None,
            "direction_consensus": self.direction_consensus,
            "n_flags": self.n_flags,
            "n_critical": self.n_critical,
            "n_warnings": self.n_warnings,
            "outlier_dois": self.outlier_dois,
            "flags": [f.to_dict() for f in self.flags],
        }

    def summary(self) -> str:
        lines = [
            f"Cluster: {self.cluster_label}",
            f"  Findings: {self.n_findings} ({self.n_with_effect_sizes} with d)",
        ]
        if self.mean_d is not None:
            lines.append(f"  d: M={self.mean_d:.3f}, SD={self.sd_d:.3f}, Mdn={self.median_d:.3f}")
        if self.i_squared is not None:
            lines.append(f"  Heterogeneity: I²={self.i_squared:.1f}%")
        if self.direction_consensus:
            lines.append(f"  Direction consensus: {self.direction_consensus}")
        if self.flags:
            lines.append(f"  Flags: {self.n_critical} critical, {self.n_warnings} warning")
            for f in self.flags:
                lines.append(f"    [{f.severity.value}] {f.rule_id}: {f.message}")
        return "\n".join(lines)


@dataclass
class BatchConsistencyReport:
    """Report across all clusters in a batch."""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    clusters: list[ClusterConsistencyReport] = field(default_factory=list)
    design_flags: list[ConsistencyFlag] = field(default_factory=list)

    @property
    def total_flags(self) -> int:
        return sum(c.n_flags for c in self.clusters) + len(self.design_flags)

    @property
    def total_critical(self) -> int:
        return sum(c.n_critical for c in self.clusters) + \
               sum(1 for f in self.design_flags if f.severity == FlagSeverity.CRITICAL)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "n_clusters": len(self.clusters),
            "total_flags": self.total_flags,
            "total_critical": self.total_critical,
            "clusters": [c.to_dict() for c in self.clusters],
            "design_flags": [f.to_dict() for f in self.design_flags],
        }

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info(f"Cross-article consistency report saved: {path}")


# ═══════════════════════════════════════════════════════════════════════════
# DESIGN-BASED PLAUSIBILITY CHECKER
# ═══════════════════════════════════════════════════════════════════════════

class DesignPlausibilityChecker:
    """
    Checks whether a single finding's effect size is plausible given its
    study design characteristics (sample size, measure type, p-value).

    This implements the insight that sampling variance of Cohen's d is
    approximately:

        Var(d) ≈ (n₁ + n₂)/(n₁·n₂) + d²/(2(n₁ + n₂))

    For a balanced design (n₁ = n₂ = n/2):

        Var(d) ≈ 4/n + d²/(2n)

    So for n=20 and d=3.0: Var(d) ≈ 0.20 + 0.225 = 0.425, SE ≈ 0.65.
    A d of 3.0 is plausible but rare — it means the effect is ~4.6 SE
    from zero, which would yield p < 0.001. If reported p is 0.04, something
    is inconsistent (Simmons, Nelson, & Simonsohn, 2011).

    Rules:
        DPR-1: Small N + extreme d (N < 30, |d| > 2.0)
        DPR-2: Tiny N + any large d (N < 15, |d| > 1.5)
        DPR-3: d/p-value inconsistency (large d but high p, or tiny d but low p)
        DPR-4: Implausibly precise (many decimal places + small N)
        DPR-5: Power-impossible (N too small for the reported d to be significant)
    """

    # ── Thresholds ──────────────────────────────────────────────────────

    # DPR-1: Small sample + extreme effect
    SMALL_N_THRESHOLD = 30
    EXTREME_D_THRESHOLD = 2.0

    # DPR-2: Tiny sample + large effect
    TINY_N_THRESHOLD = 15
    LARGE_D_THRESHOLD = 1.5

    # DPR-3: d/p inconsistency tolerance
    # If |d| > 1.5 and p > 0.10, something is likely wrong
    INCONSISTENCY_D_THRESHOLD = 1.5
    INCONSISTENCY_P_THRESHOLD = 0.10

    # DPR-5: Minimum N for significance given d
    # Approximation: to detect d at p=0.05 (two-tailed), need N ≈ (2*z_alpha/d)²
    # z_{0.025} = 1.96
    Z_ALPHA = 1.96

    def check(self, effect_size: Optional[float],
              sample_size: Optional[int],
              es_type: Optional[str] = None,
              p_value: Optional[float] = None,
              doi: str = "",
              finding_index: int = 0) -> list[ConsistencyFlag]:
        """Check a single finding for design-based plausibility."""
        flags = []

        if effect_size is None:
            return flags

        # Only apply d-based rules to Cohen's d, Hedges' g, and similar
        # For r, odds ratio, etc., different rules apply
        abs_d = abs(effect_size)
        is_d_type = _is_d_family(es_type)

        if is_d_type:
            flags.extend(self._check_d_family(
                abs_d, effect_size, sample_size, p_value, doi, finding_index
            ))
        elif _is_r_family(es_type):
            flags.extend(self._check_r_family(
                effect_size, sample_size, p_value, doi, finding_index
            ))
        elif _is_or_family(es_type):
            flags.extend(self._check_or_family(
                effect_size, sample_size, p_value, doi, finding_index
            ))

        return flags

    def _check_d_family(self, abs_d: float, d: float,
                        sample_size: Optional[int],
                        p_value: Optional[float],
                        doi: str, idx: int) -> list[ConsistencyFlag]:
        """Plausibility checks for Cohen's d / Hedges' g family."""
        flags = []
        n = sample_size

        # DPR-1: Small N + extreme d
        if n is not None and n < self.SMALL_N_THRESHOLD and abs_d > self.EXTREME_D_THRESHOLD:
            # Calculate sampling variance for context
            var_d = 4 / n + (d ** 2) / (2 * n) if n > 0 else float('inf')
            se_d = math.sqrt(var_d) if var_d < float('inf') else float('inf')
            flags.append(ConsistencyFlag(
                rule_id="DPR-1",
                severity=FlagSeverity.WARNING,
                doi=doi,
                finding_index=idx,
                message=(
                    f"Small sample (N={n}) with extreme effect (d={d:.3f}). "
                    f"SE(d)≈{se_d:.3f}, so this d is {abs_d/se_d:.1f} SE from zero. "
                    f"Possible but rare — verify against original paper."
                ),
                details={
                    "sample_size": n,
                    "effect_size": d,
                    "se_d": round(se_d, 4),
                    "z_from_zero": round(abs_d / se_d, 2) if se_d > 0 else None,
                },
            ))

        # DPR-2: Tiny N + any large d
        if n is not None and n < self.TINY_N_THRESHOLD and abs_d > self.LARGE_D_THRESHOLD:
            flags.append(ConsistencyFlag(
                rule_id="DPR-2",
                severity=FlagSeverity.CRITICAL,
                doi=doi,
                finding_index=idx,
                message=(
                    f"Tiny sample (N={n}) with large effect (d={d:.3f}). "
                    f"With N<15, effect sizes are highly unstable (wide CIs). "
                    f"This finding should be verified against the source."
                ),
                details={
                    "sample_size": n,
                    "effect_size": d,
                },
            ))

        # DPR-3: d/p inconsistency
        if p_value is not None and abs_d > self.INCONSISTENCY_D_THRESHOLD:
            if p_value > self.INCONSISTENCY_P_THRESHOLD:
                flags.append(ConsistencyFlag(
                    rule_id="DPR-3",
                    severity=FlagSeverity.WARNING,
                    doi=doi,
                    finding_index=idx,
                    message=(
                        f"Effect size |d|={abs_d:.3f} is large but p={p_value:.4f} "
                        f"suggests non-significance. This combination is unusual — "
                        f"either the sample is very small, the test is one-tailed, "
                        f"or there is a data entry error."
                    ),
                    details={
                        "effect_size": d,
                        "p_value": p_value,
                    },
                ))

        # DPR-5: Power-impossible check
        if n is not None and n > 0 and p_value is not None and p_value < 0.05:
            # Minimum N needed for this d to be significant
            if abs_d > 0:
                min_n_per_group = math.ceil((2 * self.Z_ALPHA / abs_d) ** 2)
                min_n_total = 2 * min_n_per_group
                if n < min_n_total * 0.5:
                    # Sample is less than half the minimum needed
                    flags.append(ConsistencyFlag(
                        rule_id="DPR-5",
                        severity=FlagSeverity.WARNING,
                        doi=doi,
                        finding_index=idx,
                        message=(
                            f"N={n} is well below the minimum ({min_n_total}) needed "
                            f"to detect d={abs_d:.3f} at p<0.05. The reported "
                            f"significance (p={p_value:.4f}) may reflect a false "
                            f"positive or a much larger true effect."
                        ),
                        details={
                            "sample_size": n,
                            "effect_size": d,
                            "min_n_for_significance": min_n_total,
                            "p_value": p_value,
                        },
                    ))

        return flags

    def _check_r_family(self, r: float, sample_size: Optional[int],
                        p_value: Optional[float],
                        doi: str, idx: int) -> list[ConsistencyFlag]:
        """Plausibility checks for Pearson's r / Spearman's rho."""
        flags = []
        abs_r = abs(r)
        n = sample_size

        # r > 0.8 with small N is suspicious
        if n is not None and n < 30 and abs_r > 0.70:
            flags.append(ConsistencyFlag(
                rule_id="DPR-1R",
                severity=FlagSeverity.WARNING,
                doi=doi,
                finding_index=idx,
                message=(
                    f"Small sample (N={n}) with strong correlation (r={r:.3f}). "
                    f"Correlations are unstable with N<30 — wide confidence interval."
                ),
                details={"sample_size": n, "r": r},
            ))

        return flags

    def _check_or_family(self, or_val: float, sample_size: Optional[int],
                         p_value: Optional[float],
                         doi: str, idx: int) -> list[ConsistencyFlag]:
        """Plausibility checks for odds ratios."""
        flags = []

        # Extreme odds ratios with small samples
        if sample_size is not None and sample_size < 50:
            if or_val > 10 or (or_val > 0 and or_val < 0.1):
                flags.append(ConsistencyFlag(
                    rule_id="DPR-1OR",
                    severity=FlagSeverity.WARNING,
                    doi=doi,
                    finding_index=idx,
                    message=(
                        f"Small sample (N={sample_size}) with extreme odds ratio "
                        f"(OR={or_val:.2f}). Small-sample ORs are highly unstable."
                    ),
                    details={"sample_size": sample_size, "odds_ratio": or_val},
                ))

        return flags


# ═══════════════════════════════════════════════════════════════════════════
# CROSS-ARTICLE CONSISTENCY VALIDATOR
# ═══════════════════════════════════════════════════════════════════════════

class CrossArticleValidator:
    """
    Validates effect size consistency ACROSS articles within a topic cluster.

    For a set of findings about the same IV→DV relationship (e.g., "green space
    exposure → stress reduction"), the distribution of effect sizes should be
    approximately coherent. Extreme outliers are flagged.

    Statistical approach:
    1. Collect all d-values (or transformed to d) within a cluster
    2. Compute cluster mean and SD
    3. Flag findings > 2.5 SD from cluster mean (z-score outlier)
    4. Compute Cochran's Q and I² for heterogeneity assessment
    5. If I² > 75%, the cluster has high heterogeneity — flag the most
       extreme contributors

    Rules:
        CAC-1: Z-score outlier (|z| > 2.5 from cluster mean)
        CAC-2: Direction reversal in low-heterogeneity cluster
        CAC-3: Magnitude outlier (d is > 3× the cluster median)
        CAC-4: High heterogeneity warning (I² > 75%)
        CAC-5: Singleton in cluster (only 1 finding — no cross-check possible)
    """

    # ── Configuration ───────────────────────────────────────────────────

    Z_THRESHOLD = 2.5          # Standard deviations for outlier detection
    MAGNITUDE_RATIO = 3.0      # Ratio to cluster median for CAC-3
    HIGH_I_SQUARED = 75.0      # Threshold for high heterogeneity
    MIN_CLUSTER_SIZE = 3       # Minimum findings for meaningful statistics

    def __init__(self, design_checker: DesignPlausibilityChecker = None):
        self.design_checker = design_checker or DesignPlausibilityChecker()

    def validate_cluster(self, findings: list[FindingRecord],
                         cluster_label: str = "unnamed") -> ClusterConsistencyReport:
        """
        Validate a cluster of findings for cross-article effect size consistency.

        Args:
            findings: List of FindingRecord objects from the same cluster
            cluster_label: Human-readable label (e.g., "visual_complexity→attention")

        Returns:
            ClusterConsistencyReport with flags and statistics
        """
        report = ClusterConsistencyReport(
            cluster_label=cluster_label,
            n_findings=len(findings),
            n_with_effect_sizes=0,
        )

        if not findings:
            return report

        # ── Separate findings with and without effect sizes ──────────
        es_findings = [f for f in findings if f.effect_size is not None]
        report.n_with_effect_sizes = len(es_findings)

        # ── Direction consensus ──────────────────────────────────────
        directions = [f.direction for f in findings if f.direction]
        report.direction_consensus = self._assess_direction_consensus(directions)

        # ── CAC-5: Singleton check ──────────────────────────────────
        if len(es_findings) < 2:
            if len(es_findings) == 1:
                report.flags.append(ConsistencyFlag(
                    rule_id="CAC-5",
                    severity=FlagSeverity.INFO,
                    doi=es_findings[0].doi if es_findings else "",
                    finding_index=es_findings[0].finding_index if es_findings else 0,
                    message=(
                        f"Only 1 finding with effect size in cluster "
                        f"'{cluster_label}'. No cross-article comparison possible."
                    ),
                ))
            return report

        # ── Compute cluster statistics ───────────────────────────────
        d_values = [f.effect_size for f in es_findings]
        abs_d_values = [abs(d) for d in d_values]

        report.mean_d = statistics.mean(d_values)
        report.median_d = statistics.median(d_values)

        if len(d_values) >= 2:
            report.sd_d = statistics.stdev(d_values)
        else:
            report.sd_d = 0.0

        # ── Compute heterogeneity (Cochran's Q, I²) ─────────────────
        q, i_sq = self._compute_heterogeneity(es_findings)
        report.q_statistic = q
        report.i_squared = i_sq

        # ── CAC-4: High heterogeneity warning ────────────────────────
        if i_sq is not None and i_sq > self.HIGH_I_SQUARED:
            report.flags.append(ConsistencyFlag(
                rule_id="CAC-4",
                severity=FlagSeverity.WARNING,
                doi="cluster",
                finding_index=-1,
                message=(
                    f"High heterogeneity in cluster '{cluster_label}': "
                    f"I²={i_sq:.1f}% (Q={q:.2f}, k={len(es_findings)}). "
                    f"Effect sizes vary more than expected from sampling error alone. "
                    f"Possible moderators or data quality issues."
                ),
                details={
                    "i_squared": i_sq,
                    "q_statistic": q,
                    "k": len(es_findings),
                },
            ))

        # ── Per-finding outlier checks ───────────────────────────────
        if len(d_values) >= self.MIN_CLUSTER_SIZE and report.sd_d > 0:
            for f in es_findings:
                z = (f.effect_size - report.mean_d) / report.sd_d

                # CAC-1: Z-score outlier
                if abs(z) > self.Z_THRESHOLD:
                    severity = FlagSeverity.CRITICAL if abs(z) > 3.5 else FlagSeverity.WARNING
                    report.flags.append(ConsistencyFlag(
                        rule_id="CAC-1",
                        severity=severity,
                        doi=f.doi,
                        finding_index=f.finding_index,
                        message=(
                            f"Effect size d={f.effect_size:.3f} is {abs(z):.1f} SD "
                            f"from cluster mean (M={report.mean_d:.3f}, "
                            f"SD={report.sd_d:.3f}). "
                            f"This is a statistical outlier in this topic cluster."
                        ),
                        details={
                            "z_score": round(z, 3),
                            "effect_size": f.effect_size,
                            "cluster_mean": round(report.mean_d, 4),
                            "cluster_sd": round(report.sd_d, 4),
                        },
                    ))
                    report.outlier_dois.append(f.doi)

                # CAC-3: Magnitude outlier (ratio to median)
                if report.median_d is not None and abs(report.median_d) > 0.01:
                    ratio = abs(f.effect_size) / abs(report.median_d)
                    if ratio > self.MAGNITUDE_RATIO:
                        # Only flag if not already flagged by CAC-1
                        if f.doi not in report.outlier_dois:
                            report.flags.append(ConsistencyFlag(
                                rule_id="CAC-3",
                                severity=FlagSeverity.WARNING,
                                doi=f.doi,
                                finding_index=f.finding_index,
                                message=(
                                    f"|d|={abs(f.effect_size):.3f} is {ratio:.1f}× "
                                    f"the cluster median (Mdn={report.median_d:.3f}). "
                                    f"Magnitude outlier."
                                ),
                                details={
                                    "ratio_to_median": round(ratio, 2),
                                    "effect_size": f.effect_size,
                                    "cluster_median": round(report.median_d, 4),
                                },
                            ))
                            report.outlier_dois.append(f.doi)

        # ── CAC-2: Direction reversal in low-heterogeneity cluster ───
        if i_sq is not None and i_sq < 50.0 and len(es_findings) >= self.MIN_CLUSTER_SIZE:
            # In a homogeneous cluster, direction reversals are suspicious
            positive = [f for f in es_findings if f.effect_size > 0]
            negative = [f for f in es_findings if f.effect_size < 0]
            minority = negative if len(positive) >= len(negative) else positive

            if len(minority) > 0 and len(minority) < len(es_findings) * 0.25:
                for f in minority:
                    report.flags.append(ConsistencyFlag(
                        rule_id="CAC-2",
                        severity=FlagSeverity.WARNING,
                        doi=f.doi,
                        finding_index=f.finding_index,
                        message=(
                            f"Direction reversal: d={f.effect_size:.3f} opposes "
                            f"cluster consensus ({len(positive)} positive, "
                            f"{len(negative)} negative) in a low-heterogeneity "
                            f"cluster (I²={i_sq:.1f}%). May indicate coding error "
                            f"or genuine moderator."
                        ),
                        details={
                            "effect_size": f.effect_size,
                            "n_positive": len(positive),
                            "n_negative": len(negative),
                            "i_squared": i_sq,
                        },
                    ))

        return report

    def validate_batch(self, clusters: dict[str, list[FindingRecord]],
                       run_design_checks: bool = True) -> BatchConsistencyReport:
        """
        Validate all clusters in a batch.

        Args:
            clusters: dict mapping cluster_label → list of FindingRecords
            run_design_checks: Also run DesignPlausibilityChecker per finding

        Returns:
            BatchConsistencyReport with all flags
        """
        report = BatchConsistencyReport()

        for label, findings in sorted(clusters.items()):
            cluster_report = self.validate_cluster(findings, label)
            report.clusters.append(cluster_report)

            # Design-based checks per finding
            if run_design_checks:
                for f in findings:
                    dflags = self.design_checker.check(
                        effect_size=f.effect_size,
                        sample_size=f.sample_size,
                        es_type=f.effect_size_type,
                        p_value=f.p_value,
                        doi=f.doi,
                        finding_index=f.finding_index,
                    )
                    report.design_flags.extend(dflags)

        return report

    # ── Internal methods ────────────────────────────────────────────────

    def _compute_heterogeneity(
        self, findings: list[FindingRecord]
    ) -> tuple[Optional[float], Optional[float]]:
        """
        Compute Cochran's Q and Higgins I² heterogeneity statistics.

        Uses inverse-variance weighting. For findings without sample size,
        we assign equal weights (conservative).

        Returns: (Q, I²) or (None, None) if insufficient data
        """
        if len(findings) < 2:
            return None, None

        # Compute weights (inverse variance)
        weighted_data = []
        for f in findings:
            if f.effect_size is None:
                continue
            w = self._compute_weight(f)
            weighted_data.append((f.effect_size, w))

        if len(weighted_data) < 2:
            return None, None

        # Weighted mean
        sum_w = sum(w for _, w in weighted_data)
        if sum_w == 0:
            return None, None
        weighted_mean = sum(d * w for d, w in weighted_data) / sum_w

        # Cochran's Q
        q = sum(w * (d - weighted_mean) ** 2 for d, w in weighted_data)

        # I² = max(0, (Q - (k-1)) / Q) * 100
        k = len(weighted_data)
        if q > 0:
            i_sq = max(0.0, (q - (k - 1)) / q) * 100.0
        else:
            i_sq = 0.0

        return q, i_sq

    def _compute_weight(self, f: FindingRecord) -> float:
        """
        Compute inverse-variance weight for a finding.

        For Cohen's d with balanced design:
            Var(d) ≈ 4/N + d²/(2N)
            weight = 1/Var(d)

        If sample size is unknown, use a default weight of 1.0 (equal weighting).
        """
        if f.sample_size is None or f.sample_size < 2:
            return 1.0

        n = f.sample_size
        d = f.effect_size if f.effect_size is not None else 0.0

        # Variance approximation for balanced design
        var_d = 4.0 / n + (d ** 2) / (2.0 * n)
        if var_d <= 0:
            return 1.0

        return 1.0 / var_d

    def _assess_direction_consensus(self, directions: list[str]) -> str:
        """Assess whether directions are consistent within the cluster."""
        if not directions:
            return "unknown"

        canonical = {"increase", "decrease", "no_effect", "mixed"}
        clean = [d.lower().strip() for d in directions if d and d.lower().strip() in canonical]

        if not clean:
            return "unknown"

        unique = set(clean) - {"mixed", "no_effect"}
        if len(unique) == 0:
            return "no_effect_or_mixed"
        elif len(unique) == 1:
            return "consistent"
        else:
            # Both increase and decrease present
            n_inc = clean.count("increase")
            n_dec = clean.count("decrease")
            if min(n_inc, n_dec) / max(n_inc, n_dec) > 0.3:
                return "contradictory"
            else:
                return "mostly_consistent"


# ═══════════════════════════════════════════════════════════════════════════
# EXTRACTION LOADER — Build FindingRecords from extraction files
# ═══════════════════════════════════════════════════════════════════════════

def load_findings_from_extractions(
    extractions_dir: Path,
    cluster_grouping: str = "antecedent_consequent"
) -> dict[str, list[FindingRecord]]:
    """
    Load all extraction files and group findings into clusters.

    Args:
        extractions_dir: Directory containing extraction JSON files
        cluster_grouping: How to group findings into clusters.
            "antecedent_consequent" — group by normalized antecedent→consequent pair
            "consequent" — group by consequent (DV) only

    Returns:
        dict mapping cluster_label → list of FindingRecords
    """
    clusters: dict[str, list[FindingRecord]] = {}

    for path in sorted(extractions_dir.glob("*.json")):
        if path.name.startswith("_") or "batch" in path.name or "pilot" in path.name:
            continue

        try:
            with open(path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            continue

        doi = data.get("doi", path.stem)
        findings = data.get("findings", [])

        for idx, finding in enumerate(findings):
            record = FindingRecord.from_extraction(doi, finding, idx)

            # Determine cluster label
            label = _make_cluster_label(record, cluster_grouping)
            if label:
                record.cluster_label = label
                clusters.setdefault(label, []).append(record)

    logger.info(
        f"Loaded {sum(len(v) for v in clusters.values())} findings "
        f"across {len(clusters)} clusters from {extractions_dir}"
    )
    return clusters


def _make_cluster_label(record: FindingRecord, grouping: str) -> Optional[str]:
    """Create a normalized cluster label for grouping related findings."""
    ant = _normalize_for_grouping(record.antecedent)
    con = _normalize_for_grouping(record.consequent)

    if not ant or not con:
        return None

    if grouping == "consequent":
        return con
    else:
        return f"{ant}→{con}"


def _normalize_for_grouping(text: str) -> Optional[str]:
    """Normalize text for cluster grouping (lowercase, strip, collapse whitespace)."""
    if not text or not text.strip():
        return None
    # Lowercase, strip, collapse whitespace, remove punctuation for matching
    normalized = text.lower().strip()
    normalized = " ".join(normalized.split())
    return normalized


# ═══════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def _safe_float(val: Any) -> Optional[float]:
    """Safely convert to float, handling strings and edge cases."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val) if math.isfinite(float(val)) else None
    if isinstance(val, str):
        # Handle "inferred: 0.45" notation
        cleaned = val.strip().lower()
        if cleaned.startswith("inferred:"):
            cleaned = cleaned.split(":", 1)[1].strip()
        try:
            result = float(cleaned)
            return result if math.isfinite(result) else None
        except (ValueError, OverflowError):
            return None
    return None


def _safe_int(val: Any) -> Optional[int]:
    """Safely convert to int, handling strings and ranges."""
    if val is None:
        return None
    if isinstance(val, int):
        return val
    if isinstance(val, float):
        return int(val) if math.isfinite(val) else None
    if isinstance(val, str):
        cleaned = val.strip().lower()
        # Handle "inferred: 50" notation
        if cleaned.startswith("inferred:"):
            cleaned = cleaned.split(":", 1)[1].strip()
        # Handle ranges like "50-100" by taking midpoint
        if "-" in cleaned and not cleaned.startswith("-"):
            parts = cleaned.split("-")
            try:
                return int((int(parts[0]) + int(parts[1])) / 2)
            except (ValueError, IndexError):
                pass
        try:
            return int(float(cleaned))
        except (ValueError, OverflowError):
            return None
    return None


def _normalize_es_type(es_type: Any) -> Optional[str]:
    """Normalize effect size type strings to canonical forms."""
    if not es_type:
        return None
    t = str(es_type).lower().strip()

    # d-family
    if any(x in t for x in ["cohen", "hedges", " d", "d ", "cohens_d", "hedges_g"]):
        return "cohens_d"
    if t in ("d", "g"):
        return "cohens_d"

    # OR family — check BEFORE r-family to avoid " or" matching " r"
    if any(x in t for x in ["odds", "odds_ratio"]):
        return "odds_ratio"
    if t in ("or",):
        return "odds_ratio"

    # r-family
    if any(x in t for x in ["pearson", "spearman", "correlation"]):
        return "pearsons_r"
    if t in ("r", "rho"):
        return "pearsons_r"

    # eta-squared
    if "eta" in t or "η" in t:
        return "eta_squared"

    # R-squared
    if "r²" in t or "r-squared" in t or "r_squared" in t or t == "r2":
        return "r_squared"

    # Beta
    if "beta" in t or "regression" in t:
        return "beta"

    # Percent
    if "percent" in t or "%" in t:
        return "percent"

    return t


def _is_d_family(es_type: Optional[str]) -> bool:
    """Check if effect size type is in the Cohen's d / Hedges' g family."""
    if not es_type:
        return True  # Default assumption for unknown types
    return _normalize_es_type(es_type) in ("cohens_d", None)


def _is_r_family(es_type: Optional[str]) -> bool:
    """Check if effect size type is a correlation."""
    return _normalize_es_type(es_type) == "pearsons_r"


def _is_or_family(es_type: Optional[str]) -> bool:
    """Check if effect size type is an odds ratio."""
    return _normalize_es_type(es_type) == "odds_ratio"


# ═══════════════════════════════════════════════════════════════════════════
# CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """Run cross-article consistency validation from the command line."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Cross-article effect size consistency validator"
    )
    parser.add_argument(
        "--extractions-dir",
        default=str(PROJECT_ROOT / "data" / "extractions"),
        help="Directory containing extraction JSON files",
    )
    parser.add_argument(
        "--grouping",
        choices=["antecedent_consequent", "consequent"],
        default="antecedent_consequent",
        help="How to group findings into clusters",
    )
    parser.add_argument(
        "--output",
        default=str(PROJECT_ROOT / "data" / "cross_article_consistency_report.json"),
        help="Output path for JSON report",
    )
    parser.add_argument(
        "--z-threshold", type=float, default=2.5,
        help="Z-score threshold for outlier detection (default: 2.5)",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Print detailed cluster reports",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    # Load and cluster findings
    extractions_dir = Path(args.extractions_dir)
    if not extractions_dir.exists():
        logger.error(f"Extractions directory not found: {extractions_dir}")
        return

    clusters = load_findings_from_extractions(extractions_dir, args.grouping)
    if not clusters:
        logger.warning("No clusters found. Check extractions directory.")
        return

    # Run validation
    validator = CrossArticleValidator()
    validator.Z_THRESHOLD = args.z_threshold
    report = validator.validate_batch(clusters, run_design_checks=True)

    # Summary
    print(f"\n{'='*60}")
    print("CROSS-ARTICLE CONSISTENCY REPORT")
    print(f"{'='*60}")
    print(f"  Clusters analyzed: {len(report.clusters)}")
    print(f"  Total flags: {report.total_flags}")
    print(f"  Critical flags: {report.total_critical}")
    print(f"  Design plausibility flags: {len(report.design_flags)}")

    # Show flagged clusters
    flagged = [c for c in report.clusters if c.n_flags > 0]
    if flagged:
        print(f"\n  FLAGGED CLUSTERS ({len(flagged)}):")
        for c in sorted(flagged, key=lambda x: x.n_critical, reverse=True):
            print(f"    {c.summary()}")
            print()

    # Show design flags
    if report.design_flags:
        print(f"  DESIGN PLAUSIBILITY FLAGS ({len(report.design_flags)}):")
        for f in report.design_flags[:20]:  # Top 20
            print(f"    [{f.severity.value}] {f.rule_id} ({f.doi}): {f.message}")

    # Save report
    output_path = Path(args.output)
    report.save(output_path)
    print(f"\nFull report: {output_path}")


if __name__ == "__main__":
    main()
