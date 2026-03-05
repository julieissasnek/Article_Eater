"""
Tests for cross-article consistency validator.
Tests design-based plausibility (DPR-*) and cross-article bell-curve checks (CAC-*).

Date: 2026-03-05
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.qa.cross_article_consistency_validator import (
    CrossArticleValidator,
    DesignPlausibilityChecker,
    FindingRecord,
    ClusterConsistencyReport,
    ConsistencyFlag,
    FlagSeverity,
    _safe_float,
    _safe_int,
    _normalize_es_type,
)


# ═══════════════════════════════════════════════════════════════════════════
# DESIGN PLAUSIBILITY CHECKER TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestDesignPlausibilityChecker:
    """Test DPR-1 through DPR-5 rules."""

    def setup_method(self):
        self.checker = DesignPlausibilityChecker()

    # ── DPR-1: Small N + extreme d ────────────────────────────────────

    def test_dpr1_small_n_extreme_d_flagged(self):
        """N=20, d=2.5 → should be flagged."""
        flags = self.checker.check(
            effect_size=2.5, sample_size=20, es_type="cohens_d",
            doi="test/001", finding_index=0
        )
        rule_ids = [f.rule_id for f in flags]
        assert "DPR-1" in rule_ids

    def test_dpr1_large_n_extreme_d_not_flagged(self):
        """N=200, d=2.5 → NOT flagged (large sample)."""
        flags = self.checker.check(
            effect_size=2.5, sample_size=200, es_type="cohens_d",
            doi="test/002", finding_index=0
        )
        rule_ids = [f.rule_id for f in flags]
        assert "DPR-1" not in rule_ids

    def test_dpr1_small_n_small_d_not_flagged(self):
        """N=20, d=0.5 → NOT flagged (small effect)."""
        flags = self.checker.check(
            effect_size=0.5, sample_size=20, es_type="cohens_d",
            doi="test/003", finding_index=0
        )
        rule_ids = [f.rule_id for f in flags]
        assert "DPR-1" not in rule_ids

    # ── DPR-2: Tiny N + large d ──────────────────────────────────────

    def test_dpr2_tiny_n_large_d_critical(self):
        """N=10, d=2.0 → CRITICAL flag."""
        flags = self.checker.check(
            effect_size=2.0, sample_size=10, es_type="cohens_d",
            doi="test/004", finding_index=0
        )
        dpr2 = [f for f in flags if f.rule_id == "DPR-2"]
        assert len(dpr2) == 1
        assert dpr2[0].severity == FlagSeverity.CRITICAL

    def test_dpr2_tiny_n_small_d_not_flagged(self):
        """N=10, d=0.3 → NOT flagged."""
        flags = self.checker.check(
            effect_size=0.3, sample_size=10, es_type="cohens_d",
            doi="test/005", finding_index=0
        )
        rule_ids = [f.rule_id for f in flags]
        assert "DPR-2" not in rule_ids

    # ── DPR-3: d/p inconsistency ─────────────────────────────────────

    def test_dpr3_large_d_high_p_flagged(self):
        """d=2.0, p=0.15 → inconsistent, flagged."""
        flags = self.checker.check(
            effect_size=2.0, sample_size=50, es_type="cohens_d",
            p_value=0.15, doi="test/006", finding_index=0
        )
        rule_ids = [f.rule_id for f in flags]
        assert "DPR-3" in rule_ids

    def test_dpr3_large_d_low_p_not_flagged(self):
        """d=2.0, p=0.001 → consistent, NOT flagged."""
        flags = self.checker.check(
            effect_size=2.0, sample_size=50, es_type="cohens_d",
            p_value=0.001, doi="test/007", finding_index=0
        )
        rule_ids = [f.rule_id for f in flags]
        assert "DPR-3" not in rule_ids

    # ── DPR-5: Power-impossible ───────────────────────────────────────

    def test_dpr5_impossibly_small_n_for_d(self):
        """N=8, d=0.3, p=0.04 → need N≈340 to detect d=0.3, so N=8 is impossible."""
        flags = self.checker.check(
            effect_size=0.3, sample_size=8, es_type="cohens_d",
            p_value=0.04, doi="test/008", finding_index=0
        )
        rule_ids = [f.rule_id for f in flags]
        assert "DPR-5" in rule_ids

    # ── Correlation checks ────────────────────────────────────────────

    def test_dpr1r_small_n_strong_r_flagged(self):
        """N=15, r=0.85 → flagged."""
        flags = self.checker.check(
            effect_size=0.85, sample_size=15, es_type="pearsons_r",
            doi="test/009", finding_index=0
        )
        rule_ids = [f.rule_id for f in flags]
        assert "DPR-1R" in rule_ids

    def test_dpr1r_large_n_strong_r_not_flagged(self):
        """N=200, r=0.85 → NOT flagged."""
        flags = self.checker.check(
            effect_size=0.85, sample_size=200, es_type="pearsons_r",
            doi="test/010", finding_index=0
        )
        rule_ids = [f.rule_id for f in flags]
        assert "DPR-1R" not in rule_ids

    # ── None handling ─────────────────────────────────────────────────

    def test_none_effect_size_returns_empty(self):
        flags = self.checker.check(
            effect_size=None, sample_size=20, es_type="cohens_d",
            doi="test/011", finding_index=0
        )
        assert flags == []

    def test_none_sample_size_no_n_rules_fire(self):
        """Without N, DPR-1/2/5 should not fire."""
        flags = self.checker.check(
            effect_size=3.0, sample_size=None, es_type="cohens_d",
            doi="test/012", finding_index=0
        )
        rule_ids = [f.rule_id for f in flags]
        assert "DPR-1" not in rule_ids
        assert "DPR-2" not in rule_ids


# ═══════════════════════════════════════════════════════════════════════════
# CROSS-ARTICLE VALIDATOR TESTS
# ═══════════════════════════════════════════════════════════════════════════

def _make_finding(doi: str, d: float, n: int = 50, idx: int = 0,
                  direction: str = "increase") -> FindingRecord:
    """Helper to create test findings."""
    return FindingRecord(
        doi=doi, finding_index=idx,
        antecedent="green space exposure",
        consequent="stress reduction",
        effect_size=d, effect_size_type="cohens_d",
        sample_size=n, direction=direction,
        p_value=0.01,
    )


class TestCrossArticleValidator:
    """Test CAC-1 through CAC-5 rules."""

    def setup_method(self):
        self.validator = CrossArticleValidator()

    # ── CAC-1: Z-score outlier ────────────────────────────────────────

    def test_cac1_outlier_detected(self):
        """One finding at d=3.5 in a cluster of d≈0.5 → flagged."""
        findings = [
            _make_finding("paper/1", 0.45, 100),
            _make_finding("paper/2", 0.52, 80),
            _make_finding("paper/3", 0.38, 120),
            _make_finding("paper/4", 0.60, 90),
            _make_finding("paper/5", 3.50, 30),  # The outlier
        ]
        report = self.validator.validate_cluster(findings, "green→stress")
        assert "paper/5" in report.outlier_dois

    def test_cac1_no_outlier_in_consistent_cluster(self):
        """Tight cluster: d ∈ [0.3, 0.7] → no outliers."""
        findings = [
            _make_finding("paper/1", 0.45, 100),
            _make_finding("paper/2", 0.52, 80),
            _make_finding("paper/3", 0.38, 120),
            _make_finding("paper/4", 0.60, 90),
            _make_finding("paper/5", 0.55, 110),
        ]
        report = self.validator.validate_cluster(findings, "green→stress")
        assert len(report.outlier_dois) == 0

    # ── CAC-2: Direction reversal ─────────────────────────────────────

    def test_cac2_direction_reversal_flagged(self):
        """One tiny negative in a mostly-positive cluster with low I²."""
        # Use many similar values and only a tiny negative to keep I² < 50%
        # With inverse-variance weighting, we need the reversal to be
        # very close to zero so it doesn't inflate heterogeneity.
        findings = [
            _make_finding("paper/1", 0.30, 500, direction="increase"),
            _make_finding("paper/2", 0.32, 500, direction="increase"),
            _make_finding("paper/3", 0.28, 500, direction="increase"),
            _make_finding("paper/4", 0.31, 500, direction="increase"),
            _make_finding("paper/5", 0.29, 500, direction="increase"),
            _make_finding("paper/6", 0.33, 500, direction="increase"),
            _make_finding("paper/7", 0.30, 500, direction="increase"),
            _make_finding("paper/8", 0.31, 500, direction="increase"),
            _make_finding("paper/9", -0.02, 500, direction="decrease"),  # Tiny reversal
        ]
        report = self.validator.validate_cluster(findings, "green→stress")
        # Verify I² is low enough for CAC-2 to trigger
        assert report.i_squared is not None and report.i_squared < 50.0, \
            f"I²={report.i_squared:.1f}% is too high; need < 50% for CAC-2"
        cac2 = [f for f in report.flags if f.rule_id == "CAC-2"]
        assert len(cac2) >= 1
        assert cac2[0].doi == "paper/9"

    # ── CAC-4: High heterogeneity ─────────────────────────────────────

    def test_cac4_high_heterogeneity_flagged(self):
        """Wildly varying d-values → I² > 75%, flagged."""
        findings = [
            _make_finding("paper/1", 0.10, 200),
            _make_finding("paper/2", 1.80, 30),
            _make_finding("paper/3", 0.05, 500),
            _make_finding("paper/4", 2.50, 20),
            _make_finding("paper/5", 0.30, 100),
        ]
        report = self.validator.validate_cluster(findings, "diverse→outcomes")
        cac4 = [f for f in report.flags if f.rule_id == "CAC-4"]
        assert len(cac4) >= 1
        assert report.i_squared is not None
        assert report.i_squared > 75.0

    # ── CAC-5: Singleton ──────────────────────────────────────────────

    def test_cac5_singleton_flagged(self):
        """Only 1 finding → CAC-5 info flag."""
        findings = [_make_finding("paper/1", 0.45, 100)]
        report = self.validator.validate_cluster(findings, "single")
        cac5 = [f for f in report.flags if f.rule_id == "CAC-5"]
        assert len(cac5) == 1
        assert cac5[0].severity == FlagSeverity.INFO

    # ── Statistics computation ─────────────────────────────────────────

    def test_cluster_mean_computed(self):
        findings = [
            _make_finding("paper/1", 0.40, 100),
            _make_finding("paper/2", 0.60, 100),
        ]
        report = self.validator.validate_cluster(findings, "test")
        assert report.mean_d is not None
        assert abs(report.mean_d - 0.50) < 0.01

    def test_heterogeneity_computed(self):
        findings = [
            _make_finding("p/1", 0.5, 100),
            _make_finding("p/2", 0.5, 100),
            _make_finding("p/3", 0.5, 100),
        ]
        report = self.validator.validate_cluster(findings, "test")
        # Identical d-values → I² ≈ 0
        assert report.i_squared is not None
        assert report.i_squared < 5.0

    def test_direction_consensus_consistent(self):
        findings = [
            _make_finding("p/1", 0.5, 100, direction="increase"),
            _make_finding("p/2", 0.6, 100, direction="increase"),
        ]
        report = self.validator.validate_cluster(findings, "test")
        assert report.direction_consensus == "consistent"

    def test_direction_consensus_contradictory(self):
        findings = [
            _make_finding("p/1", 0.5, 100, direction="increase"),
            _make_finding("p/2", -0.5, 100, direction="decrease"),
        ]
        report = self.validator.validate_cluster(findings, "test")
        assert report.direction_consensus == "contradictory"

    # ── Batch validation ──────────────────────────────────────────────

    def test_batch_validation(self):
        clusters = {
            "cluster_a": [
                _make_finding("p/1", 0.5, 100),
                _make_finding("p/2", 0.6, 100),
                _make_finding("p/3", 3.5, 10),  # Outlier + design flag
            ],
            "cluster_b": [
                _make_finding("p/4", 0.3, 200),
            ],
        }
        report = self.validator.validate_batch(clusters, run_design_checks=True)
        assert len(report.clusters) == 2
        # Design flag should fire for N=10, d=3.5
        dpr_flags = [f for f in report.design_flags if f.doi == "p/3"]
        assert len(dpr_flags) >= 1

    # ── Empty/edge cases ──────────────────────────────────────────────

    def test_empty_cluster(self):
        report = self.validator.validate_cluster([], "empty")
        assert report.n_findings == 0
        assert report.n_flags == 0

    def test_no_effect_sizes(self):
        findings = [
            FindingRecord(
                doi="p/1", finding_index=0,
                antecedent="x", consequent="y",
                effect_size=None, effect_size_type=None,
                sample_size=100, direction="increase", p_value=0.05,
            )
        ]
        report = self.validator.validate_cluster(findings, "no_es")
        assert report.n_with_effect_sizes == 0


# ═══════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTION TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestUtilities:

    def test_safe_float_int(self):
        assert _safe_float(42) == 42.0

    def test_safe_float_str(self):
        assert _safe_float("0.45") == 0.45

    def test_safe_float_inferred(self):
        assert _safe_float("inferred: 0.65") == 0.65

    def test_safe_float_none(self):
        assert _safe_float(None) is None

    def test_safe_float_nan(self):
        assert _safe_float(float('nan')) is None

    def test_safe_int_range(self):
        assert _safe_int("50-100") == 75

    def test_safe_int_inferred(self):
        assert _safe_int("inferred: 50") == 50

    def test_normalize_es_type_cohens_d(self):
        assert _normalize_es_type("Cohen's d") == "cohens_d"

    def test_normalize_es_type_r(self):
        assert _normalize_es_type("Pearson's r") == "pearsons_r"

    def test_normalize_es_type_or(self):
        assert _normalize_es_type("odds ratio") == "odds_ratio"

    def test_normalize_es_type_none(self):
        assert _normalize_es_type(None) is None


# ═══════════════════════════════════════════════════════════════════════════
# REPORT SERIALIZATION TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestReportSerialization:

    def test_cluster_report_to_dict(self):
        report = ClusterConsistencyReport(
            cluster_label="test",
            n_findings=5,
            n_with_effect_sizes=4,
            mean_d=0.50,
            sd_d=0.15,
            median_d=0.48,
            i_squared=25.0,
        )
        d = report.to_dict()
        assert d["cluster_label"] == "test"
        assert d["mean_d"] == 0.5
        assert d["i_squared"] == 25.0

    def test_flag_to_dict(self):
        flag = ConsistencyFlag(
            rule_id="CAC-1", severity=FlagSeverity.WARNING,
            doi="test/001", finding_index=0,
            message="Outlier detected",
            details={"z_score": 3.1},
        )
        d = flag.to_dict()
        assert d["rule_id"] == "CAC-1"
        assert d["z_score"] == 3.1

    def test_report_save(self, tmp_path):
        from src.qa.cross_article_consistency_validator import BatchConsistencyReport
        report = BatchConsistencyReport()
        report.clusters.append(ClusterConsistencyReport(
            cluster_label="test", n_findings=3, n_with_effect_sizes=3,
        ))
        out = tmp_path / "test_report.json"
        report.save(out)
        assert out.exists()
        import json
        data = json.loads(out.read_text())
        assert data["n_clusters"] == 1
