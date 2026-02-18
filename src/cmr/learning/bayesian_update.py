"""
Bayesian Parameter Updating (Sprint 13 Task 13.5).

Conjugate normal-normal update for template parameters.
Maps calibration_status to prior_sd. When posterior mean moves
outside Goldilocks boundary, auto-generates update proposal.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Optional

from src.cmr.learning.update_proposals import (
    Evidence,
    ProposalType,
    generate_proposal,
)


# Prior standard deviation as fraction of parameter value
# Based on calibration status
CALIBRATION_PRIOR_SD: dict[str, float] = {
    "established": 0.05,     # Very tight prior - well-validated
    "substantial": 0.05,     # Same as established
    "supported": 0.10,       # Moderate prior
    "partial": 0.15,         # Looser prior
    "preliminary": 0.20,     # Even looser
    "expert_estimate": 0.25, # Expert judgment
    "protocol": 0.25,        # Standard protocol
    "speculative": 0.35,     # Very uncertain
    "uncalibrated": 0.50,    # Maximum uncertainty
}


@dataclass
class BayesianUpdate:
    """Result of a Bayesian parameter update."""

    parameter_name: str
    prior_mean: float
    prior_sd: float
    observation_mean: float
    observation_sd: float
    posterior_mean: float
    posterior_sd: float
    credible_interval_95: tuple[float, float]
    bayes_factor: float  # Evidence strength
    effective_sample_size: float
    update_magnitude: float  # |posterior - prior| / prior


@dataclass
class GoldilocksCheck:
    """Result of checking if posterior violates Goldilocks bounds."""

    parameter_name: str
    posterior_mean: float
    goldilocks_min: float
    goldilocks_max: float
    in_goldilocks: bool
    violation_direction: Optional[str]  # "below" or "above" or None
    violation_amount: float  # Distance from nearest boundary


def get_prior_sd(
    calibration_status: str,
    parameter_value: float,
) -> float:
    """
    Get prior standard deviation based on calibration status.

    Args:
        calibration_status: Current calibration status of the parameter
        parameter_value: Current parameter value (for scaling)

    Returns:
        Standard deviation for the prior distribution
    """
    status_key = calibration_status.lower().strip()
    fraction = CALIBRATION_PRIOR_SD.get(status_key, 0.25)
    return abs(parameter_value) * fraction if parameter_value != 0 else fraction


def compute_bayesian_update(
    prior_mean: float,
    prior_sd: float,
    observations: list[dict],
) -> BayesianUpdate:
    """
    Perform conjugate normal-normal Bayesian update.

    Args:
        prior_mean: Prior mean (current parameter value)
        prior_sd: Prior standard deviation
        observations: List of dicts with 'value', 'sd' (or 'se'), and optionally 'n'

    Returns:
        BayesianUpdate with posterior parameters
    """
    if not observations:
        # No data - posterior = prior
        return BayesianUpdate(
            parameter_name="",
            prior_mean=prior_mean,
            prior_sd=prior_sd,
            observation_mean=prior_mean,
            observation_sd=float("inf"),
            posterior_mean=prior_mean,
            posterior_sd=prior_sd,
            credible_interval_95=(
                prior_mean - 1.96 * prior_sd,
                prior_mean + 1.96 * prior_sd,
            ),
            bayes_factor=1.0,
            effective_sample_size=0.0,
            update_magnitude=0.0,
        )

    # Compute weighted observation mean and precision
    total_weight = 0.0
    weighted_sum = 0.0
    total_n = 0

    for obs in observations:
        obs_value = float(obs.get("value", obs.get("effect_size", 0)))
        obs_sd = float(obs.get("sd", obs.get("se", prior_sd)))
        obs_n = int(obs.get("n", obs.get("sample_n", 1)))

        if obs_sd <= 0:
            obs_sd = prior_sd

        # Precision (inverse variance)
        precision = 1.0 / (obs_sd ** 2)
        total_weight += precision
        weighted_sum += obs_value * precision
        total_n += obs_n

    if total_weight == 0:
        observation_mean = prior_mean
        observation_precision = 0.0
    else:
        observation_mean = weighted_sum / total_weight
        observation_precision = total_weight

    observation_sd = 1.0 / math.sqrt(observation_precision) if observation_precision > 0 else float("inf")

    # Prior precision
    prior_precision = 1.0 / (prior_sd ** 2) if prior_sd > 0 else 0.0

    # Posterior precision (sum of precisions)
    posterior_precision = prior_precision + observation_precision

    if posterior_precision > 0:
        # Posterior mean (precision-weighted average)
        posterior_mean = (
            prior_precision * prior_mean + observation_precision * observation_mean
        ) / posterior_precision
        posterior_sd = 1.0 / math.sqrt(posterior_precision)
    else:
        posterior_mean = prior_mean
        posterior_sd = prior_sd

    # 95% credible interval
    ci_lower = posterior_mean - 1.96 * posterior_sd
    ci_upper = posterior_mean + 1.96 * posterior_sd

    # Bayes factor (approximation using precision ratio)
    # Higher when data provides more info relative to prior
    bayes_factor = 1.0 + (observation_precision / prior_precision) if prior_precision > 0 else 1.0

    # Effective sample size
    effective_n = (posterior_precision / prior_precision) - 1 if prior_precision > 0 else total_n

    # Update magnitude
    if prior_mean != 0:
        update_magnitude = abs(posterior_mean - prior_mean) / abs(prior_mean)
    else:
        update_magnitude = abs(posterior_mean - prior_mean)

    return BayesianUpdate(
        parameter_name="",
        prior_mean=prior_mean,
        prior_sd=prior_sd,
        observation_mean=observation_mean,
        observation_sd=observation_sd,
        posterior_mean=posterior_mean,
        posterior_sd=posterior_sd,
        credible_interval_95=(ci_lower, ci_upper),
        bayes_factor=bayes_factor,
        effective_sample_size=effective_n,
        update_magnitude=update_magnitude,
    )


def check_goldilocks_violation(
    posterior_mean: float,
    goldilocks_min: float,
    goldilocks_max: float,
    parameter_name: str = "",
) -> GoldilocksCheck:
    """
    Check if posterior mean violates Goldilocks boundaries.

    Args:
        posterior_mean: Updated posterior mean
        goldilocks_min: Lower Goldilocks boundary
        goldilocks_max: Upper Goldilocks boundary
        parameter_name: Name of the parameter

    Returns:
        GoldilocksCheck with violation details
    """
    in_goldilocks = goldilocks_min <= posterior_mean <= goldilocks_max

    if in_goldilocks:
        return GoldilocksCheck(
            parameter_name=parameter_name,
            posterior_mean=posterior_mean,
            goldilocks_min=goldilocks_min,
            goldilocks_max=goldilocks_max,
            in_goldilocks=True,
            violation_direction=None,
            violation_amount=0.0,
        )

    if posterior_mean < goldilocks_min:
        return GoldilocksCheck(
            parameter_name=parameter_name,
            posterior_mean=posterior_mean,
            goldilocks_min=goldilocks_min,
            goldilocks_max=goldilocks_max,
            in_goldilocks=False,
            violation_direction="below",
            violation_amount=goldilocks_min - posterior_mean,
        )
    else:
        return GoldilocksCheck(
            parameter_name=parameter_name,
            posterior_mean=posterior_mean,
            goldilocks_min=goldilocks_min,
            goldilocks_max=goldilocks_max,
            in_goldilocks=False,
            violation_direction="above",
            violation_amount=posterior_mean - goldilocks_max,
        )


def update_parameter_bayesian(
    template_id: str,
    parameter_name: str,
    current_value: float,
    calibration_status: str,
    observations: list[dict],
    goldilocks_min: Optional[float] = None,
    goldilocks_max: Optional[float] = None,
    db_path: str = "ae.db",
    auto_propose: bool = True,
) -> dict:
    """
    Perform full Bayesian update on a parameter and optionally generate proposal.

    Args:
        template_id: Template containing the parameter
        parameter_name: Name of the parameter to update
        current_value: Current parameter value
        calibration_status: Current calibration status
        observations: List of observations with 'value', 'sd'/'se', and optionally 'n'
        goldilocks_min: Optional lower Goldilocks boundary
        goldilocks_max: Optional upper Goldilocks boundary
        db_path: Database path for proposals
        auto_propose: Whether to auto-generate proposals on boundary violation

    Returns:
        Dict with update results and any generated proposal
    """
    # Get prior from calibration status
    prior_sd = get_prior_sd(calibration_status, current_value)

    # Perform update
    update = compute_bayesian_update(
        prior_mean=current_value,
        prior_sd=prior_sd,
        observations=observations,
    )
    update.parameter_name = parameter_name

    result = {
        "template_id": template_id,
        "parameter_name": parameter_name,
        "update": {
            "prior_mean": update.prior_mean,
            "prior_sd": update.prior_sd,
            "observation_mean": update.observation_mean,
            "observation_sd": update.observation_sd,
            "posterior_mean": update.posterior_mean,
            "posterior_sd": update.posterior_sd,
            "credible_interval_95": update.credible_interval_95,
            "bayes_factor": update.bayes_factor,
            "effective_sample_size": update.effective_sample_size,
            "update_magnitude": update.update_magnitude,
        },
        "goldilocks_check": None,
        "proposal": None,
    }

    # Check Goldilocks boundaries if provided
    if goldilocks_min is not None and goldilocks_max is not None:
        check = check_goldilocks_violation(
            posterior_mean=update.posterior_mean,
            goldilocks_min=goldilocks_min,
            goldilocks_max=goldilocks_max,
            parameter_name=parameter_name,
        )
        result["goldilocks_check"] = {
            "in_goldilocks": check.in_goldilocks,
            "violation_direction": check.violation_direction,
            "violation_amount": check.violation_amount,
            "goldilocks_min": goldilocks_min,
            "goldilocks_max": goldilocks_max,
        }

        # Auto-generate proposal if boundary violated
        if auto_propose and not check.in_goldilocks:
            evidence_list = [
                Evidence(
                    paper_citation=obs.get("citation", "Bayesian update"),
                    effect_size=obs.get("value", obs.get("effect_size")),
                    sample_n=obs.get("n", obs.get("sample_n")),
                    context=f"Bayesian update: posterior={update.posterior_mean:.3f}, "
                            f"95% CI=[{update.credible_interval_95[0]:.3f}, {update.credible_interval_95[1]:.3f}]",
                )
                for obs in observations
            ]

            # Determine proposal type
            if check.violation_direction == "below":
                proposed_value = goldilocks_min
            else:
                proposed_value = goldilocks_max

            proposal = generate_proposal(
                template_id=template_id,
                proposal_type=ProposalType.BOUNDARY_REVISION,
                evidence=evidence_list,
                parameter_name=parameter_name,
                current_value=current_value,
                proposed_value=update.posterior_mean,
                confidence=min(0.9, 0.5 + update.bayes_factor * 0.1),
                db_path=db_path,
            )

            result["proposal"] = proposal.to_dict()

    return result


def format_bayesian_update_report(result: dict) -> str:
    """Format a Bayesian update result for display."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"BAYESIAN UPDATE: {result['template_id']}.{result['parameter_name']}")
    lines.append("=" * 60)
    lines.append("")

    upd = result["update"]
    lines.append("PRIOR")
    lines.append(f"  Mean: {upd['prior_mean']:.4f}")
    lines.append(f"  SD: {upd['prior_sd']:.4f}")
    lines.append("")

    lines.append("OBSERVATION")
    lines.append(f"  Mean: {upd['observation_mean']:.4f}")
    lines.append(f"  SD: {upd['observation_sd']:.4f}")
    lines.append("")

    lines.append("POSTERIOR")
    lines.append(f"  Mean: {upd['posterior_mean']:.4f}")
    lines.append(f"  SD: {upd['posterior_sd']:.4f}")
    lines.append(f"  95% CI: [{upd['credible_interval_95'][0]:.4f}, {upd['credible_interval_95'][1]:.4f}]")
    lines.append("")

    lines.append("DIAGNOSTICS")
    lines.append(f"  Bayes Factor: {upd['bayes_factor']:.2f}")
    lines.append(f"  Effective N: {upd['effective_sample_size']:.1f}")
    lines.append(f"  Update Magnitude: {upd['update_magnitude']:.1%}")
    lines.append("")

    if result.get("goldilocks_check"):
        gc = result["goldilocks_check"]
        lines.append("GOLDILOCKS CHECK")
        lines.append(f"  Boundaries: [{gc['goldilocks_min']:.4f}, {gc['goldilocks_max']:.4f}]")
        if gc["in_goldilocks"]:
            lines.append("  Status: IN GOLDILOCKS ZONE")
        else:
            lines.append(f"  Status: VIOLATION ({gc['violation_direction']} by {gc['violation_amount']:.4f})")
        lines.append("")

    if result.get("proposal"):
        lines.append("PROPOSAL GENERATED")
        lines.append(f"  ID: {result['proposal']['proposal_id']}")
        lines.append(f"  Type: {result['proposal']['proposal_type']}")
        lines.append(f"  Confidence: {result['proposal']['confidence']:.2f}")

    return "\n".join(lines)


__all__ = [
    "BayesianUpdate",
    "GoldilocksCheck",
    "CALIBRATION_PRIOR_SD",
    "get_prior_sd",
    "compute_bayesian_update",
    "check_goldilocks_violation",
    "update_parameter_bayesian",
    "format_bayesian_update_report",
]
