"""
Evidence Accumulation Engine (Sprint 13 Task 13.3).

Gathers all evidence about a template parameter from evaluated papers.
Computes weighted mean and CI using simplified fixed-effects meta-analysis.
If current template value falls outside CI, auto-generates an update proposal.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
import math
from datetime import datetime

from src.cmr.learning.update_proposals import (
    Evidence,
    ProposalType,
    generate_boundary_revision_proposal,
    generate_contradiction_proposal,
)


@dataclass
class EffectEstimate:
    """A single effect estimate from a study."""

    paper_citation: str
    effect_size: float
    sample_n: int
    standard_error: Optional[float] = None
    context: Optional[str] = None
    direction: Optional[str] = None

    def get_se(self) -> float:
        """Get or estimate standard error."""
        if self.standard_error is not None:
            return self.standard_error
        # Estimate SE from sample size (rough approximation)
        # For Cohen's d, SE ≈ sqrt(2/n + d²/(2n))
        return math.sqrt(2 / self.sample_n + (self.effect_size ** 2) / (2 * self.sample_n))

    def get_weight(self) -> float:
        """Get inverse-variance weight."""
        se = self.get_se()
        if se > 0:
            return 1 / (se ** 2)
        return 0.0


@dataclass
class AccumulatedEvidence:
    """Result of evidence accumulation for a parameter."""

    template_id: str
    parameter_name: str
    current_value: float
    n_studies: int
    total_n: int
    weighted_mean: float
    ci_lower: float
    ci_upper: float
    heterogeneity_q: float
    i_squared: float
    needs_update: bool
    contradiction_detected: bool
    individual_estimates: list[EffectEstimate] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "template_id": self.template_id,
            "parameter_name": self.parameter_name,
            "current_value": self.current_value,
            "n_studies": self.n_studies,
            "total_n": self.total_n,
            "weighted_mean": self.weighted_mean,
            "ci_lower": self.ci_lower,
            "ci_upper": self.ci_upper,
            "heterogeneity_q": self.heterogeneity_q,
            "i_squared": self.i_squared,
            "needs_update": self.needs_update,
            "contradiction_detected": self.contradiction_detected,
        }


@dataclass
class EvidencePool:
    """Collection of evidence for a template parameter."""

    template_id: str
    parameter_name: str
    estimates: list[EffectEstimate] = field(default_factory=list)

    def add_estimate(
        self,
        paper_citation: str,
        effect_size: float,
        sample_n: int,
        standard_error: Optional[float] = None,
        context: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> None:
        """Add an effect estimate to the pool."""
        self.estimates.append(
            EffectEstimate(
                paper_citation=paper_citation,
                effect_size=effect_size,
                sample_n=sample_n,
                standard_error=standard_error,
                context=context,
                direction=direction,
            )
        )

    def get_total_n(self) -> int:
        """Get total sample size across all studies."""
        return sum(e.sample_n for e in self.estimates)


def compute_fixed_effects_meta(
    estimates: list[EffectEstimate],
) -> tuple[float, float, float, float]:
    """
    Compute fixed-effects meta-analytic estimate.

    Returns:
        (weighted_mean, ci_lower, ci_upper, sum_weights)
    """
    if not estimates:
        return 0.0, 0.0, 0.0, 0.0

    weights = [e.get_weight() for e in estimates]
    effects = [e.effect_size for e in estimates]

    sum_weights = sum(weights)
    if sum_weights == 0:
        return 0.0, 0.0, 0.0, 0.0

    weighted_mean = sum(w * e for w, e in zip(weights, effects)) / sum_weights

    # Standard error of the weighted mean
    se_mean = math.sqrt(1 / sum_weights) if sum_weights > 0 else 0

    # 95% CI (z = 1.96)
    ci_lower = weighted_mean - 1.96 * se_mean
    ci_upper = weighted_mean + 1.96 * se_mean

    return weighted_mean, ci_lower, ci_upper, sum_weights


def compute_heterogeneity(
    estimates: list[EffectEstimate],
    weighted_mean: float,
) -> tuple[float, float]:
    """
    Compute heterogeneity statistics (Q and I²).

    Returns:
        (q_statistic, i_squared)
    """
    if len(estimates) < 2:
        return 0.0, 0.0

    weights = [e.get_weight() for e in estimates]
    effects = [e.effect_size for e in estimates]

    # Cochran's Q
    q = sum(w * (e - weighted_mean) ** 2 for w, e in zip(weights, effects))

    # I² = (Q - df) / Q * 100
    df = len(estimates) - 1
    if q > df:
        i_squared = ((q - df) / q) * 100
    else:
        i_squared = 0.0

    return q, i_squared


def accumulate_evidence(
    pool: EvidencePool,
    current_value: float,
    significance_threshold: float = 0.05,
) -> AccumulatedEvidence:
    """
    Accumulate evidence and compute meta-analytic summary.

    Args:
        pool: EvidencePool with effect estimates
        current_value: Current value in the template
        significance_threshold: Alpha level for CI (default 0.05)

    Returns:
        AccumulatedEvidence with meta-analytic results
    """
    estimates = pool.estimates

    if not estimates:
        return AccumulatedEvidence(
            template_id=pool.template_id,
            parameter_name=pool.parameter_name,
            current_value=current_value,
            n_studies=0,
            total_n=0,
            weighted_mean=current_value,
            ci_lower=current_value,
            ci_upper=current_value,
            heterogeneity_q=0.0,
            i_squared=0.0,
            needs_update=False,
            contradiction_detected=False,
            individual_estimates=[],
        )

    weighted_mean, ci_lower, ci_upper, _ = compute_fixed_effects_meta(estimates)
    q, i_squared = compute_heterogeneity(estimates, weighted_mean)

    # Check if current value falls outside CI
    needs_update = current_value < ci_lower or current_value > ci_upper

    # Check for contradiction (current value far from weighted mean)
    # Contradiction if current value is more than 2 SEs from weighted mean
    se_mean = (ci_upper - ci_lower) / (2 * 1.96)
    if se_mean > 0:
        z_score = abs(current_value - weighted_mean) / se_mean
        contradiction_detected = z_score > 2.5
    else:
        contradiction_detected = False

    return AccumulatedEvidence(
        template_id=pool.template_id,
        parameter_name=pool.parameter_name,
        current_value=current_value,
        n_studies=len(estimates),
        total_n=pool.get_total_n(),
        weighted_mean=weighted_mean,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        heterogeneity_q=q,
        i_squared=i_squared,
        needs_update=needs_update,
        contradiction_detected=contradiction_detected,
        individual_estimates=estimates,
    )


def generate_proposals_from_accumulated(
    accumulated: AccumulatedEvidence,
    db_path: str = "ae.db",
) -> list:
    """
    Generate update proposals based on accumulated evidence.

    Args:
        accumulated: AccumulatedEvidence result
        db_path: Database path for persisting proposals

    Returns:
        List of generated proposals (may be empty)
    """
    proposals = []

    if not accumulated.needs_update and not accumulated.contradiction_detected:
        return proposals

    # Convert estimates to Evidence objects
    evidence_list = [
        Evidence(
            paper_citation=e.paper_citation,
            effect_size=e.effect_size,
            sample_n=e.sample_n,
            context=e.context,
            direction=e.direction,
        )
        for e in accumulated.individual_estimates
    ]

    if accumulated.contradiction_detected:
        # Strong contradiction - flag for review
        if evidence_list:
            main_evidence = evidence_list[0]
            proposal = generate_contradiction_proposal(
                template_id=accumulated.template_id,
                parameter_name=accumulated.parameter_name,
                current_value=accumulated.current_value,
                observed_value=accumulated.weighted_mean,
                evidence=main_evidence,
                db_path=db_path,
            )
            proposals.append(proposal)

    elif accumulated.needs_update:
        # Value outside CI - propose boundary revision
        proposal = generate_boundary_revision_proposal(
            template_id=accumulated.template_id,
            parameter_name=accumulated.parameter_name,
            current_boundary=accumulated.current_value,
            proposed_boundary=accumulated.weighted_mean,
            evidence=evidence_list,
            db_path=db_path,
        )
        proposals.append(proposal)

    return proposals


def format_accumulation_report(accumulated: AccumulatedEvidence) -> str:
    """Format accumulated evidence as a readable report."""
    lines = []
    lines.append("=" * 60)
    lines.append("EVIDENCE ACCUMULATION REPORT")
    lines.append("=" * 60)
    lines.append(f"Template: {accumulated.template_id}")
    lines.append(f"Parameter: {accumulated.parameter_name}")
    lines.append("")
    lines.append("-" * 40)
    lines.append("META-ANALYTIC SUMMARY")
    lines.append("-" * 40)
    lines.append(f"Studies: {accumulated.n_studies}")
    lines.append(f"Total N: {accumulated.total_n}")
    lines.append(f"Weighted Mean: {accumulated.weighted_mean:.3f}")
    lines.append(f"95% CI: [{accumulated.ci_lower:.3f}, {accumulated.ci_upper:.3f}]")
    lines.append("")
    lines.append("-" * 40)
    lines.append("HETEROGENEITY")
    lines.append("-" * 40)
    lines.append(f"Q statistic: {accumulated.heterogeneity_q:.2f}")
    lines.append(f"I²: {accumulated.i_squared:.1f}%")

    if accumulated.i_squared > 75:
        lines.append("  WARNING: High heterogeneity - effects vary across studies")
    elif accumulated.i_squared > 50:
        lines.append("  CAUTION: Moderate heterogeneity - some effect variation")
    else:
        lines.append("  OK: Low heterogeneity - consistent effects")

    lines.append("")
    lines.append("-" * 40)
    lines.append("CURRENT VALUE ASSESSMENT")
    lines.append("-" * 40)
    lines.append(f"Current Value: {accumulated.current_value:.3f}")

    if accumulated.current_value >= accumulated.ci_lower and accumulated.current_value <= accumulated.ci_upper:
        lines.append("Status: WITHIN 95% CI")
    else:
        lines.append("Status: OUTSIDE 95% CI - UPDATE RECOMMENDED")

    if accumulated.contradiction_detected:
        lines.append("")
        lines.append("*** CONTRADICTION DETECTED ***")
        lines.append("Current value significantly differs from evidence")

    lines.append("")
    lines.append("-" * 40)
    lines.append("INDIVIDUAL STUDIES")
    lines.append("-" * 40)
    for i, e in enumerate(accumulated.individual_estimates, 1):
        lines.append(f"  [{i}] {e.paper_citation}")
        lines.append(f"      d = {e.effect_size:.2f}, N = {e.sample_n}")
        if e.context:
            lines.append(f"      Context: {e.context}")

    return "\n".join(lines)


# Convenience function for common use case
def accumulate_and_propose(
    template_id: str,
    parameter_name: str,
    current_value: float,
    studies: list[dict],
    db_path: str = "ae.db",
) -> tuple[AccumulatedEvidence, list]:
    """
    Convenience function: accumulate evidence and generate any needed proposals.

    Args:
        template_id: Template being assessed
        parameter_name: Parameter being assessed
        current_value: Current value in template
        studies: List of study dicts with keys: paper_citation, effect_size, sample_n, [se, context]
        db_path: Database path

    Returns:
        (AccumulatedEvidence, list of proposals)
    """
    pool = EvidencePool(template_id=template_id, parameter_name=parameter_name)

    for study in studies:
        pool.add_estimate(
            paper_citation=study["paper_citation"],
            effect_size=study["effect_size"],
            sample_n=study["sample_n"],
            standard_error=study.get("se"),
            context=study.get("context"),
            direction=study.get("direction"),
        )

    accumulated = accumulate_evidence(pool, current_value)
    proposals = generate_proposals_from_accumulated(accumulated, db_path)

    return accumulated, proposals
