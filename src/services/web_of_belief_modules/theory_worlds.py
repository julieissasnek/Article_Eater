"""Theory-world construction and probability helpers (ARCH-5d)."""

from __future__ import annotations

import math
from typing import Iterable, Mapping, Sequence

from src.services.web_of_belief_components import TheoryWorld


def _clamp_01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def canonical_world_id(true_set: set[str], false_set: set[str]) -> str:
    """Generate a canonical theory-world identifier."""
    true_str = ",".join(sorted(true_set)) if true_set else "∅"
    false_str = ",".join(sorted(false_set)) if false_set else "∅"
    return f"[+{true_str}][-{false_str}]"


def generate_world_assignments(theory_ids: Sequence[str]) -> list[tuple[frozenset[str], frozenset[str]]]:
    """Enumerate all possible truth assignments for the given theories."""
    sorted_theories = sorted(set(theory_ids))
    n_theories = len(sorted_theories)
    assignments: list[tuple[frozenset[str], frozenset[str]]] = []
    for index in range(2 ** n_theories):
        true_theories: set[str] = set()
        false_theories: set[str] = set()
        for bit, theory_id in enumerate(sorted_theories):
            if (index >> bit) & 1:
                true_theories.add(theory_id)
            else:
                false_theories.add(theory_id)
        assignments.append((frozenset(true_theories), frozenset(false_theories)))
    return assignments


def compute_world_prior(
    theory_ids: Iterable[str],
    theory_priors: Mapping[str, float],
    theories_true: frozenset[str],
) -> float:
    """Compute world prior under independent-theory approximation."""
    prior = 1.0
    for theory_id in sorted(set(theory_ids)):
        p_theory_true = _clamp_01(theory_priors.get(theory_id, 0.5))
        prior *= p_theory_true if theory_id in theories_true else (1.0 - p_theory_true)
    return prior


def build_theory_worlds(
    theory_ids: Iterable[str],
    theory_priors: Mapping[str, float],
) -> dict[str, TheoryWorld]:
    """Build full world state from theory priors."""
    sorted_theories = sorted(set(theory_ids))
    if not sorted_theories:
        return {}

    worlds: dict[str, TheoryWorld] = {}
    for theories_true, theories_false in generate_world_assignments(sorted_theories):
        world_id = canonical_world_id(set(theories_true), set(theories_false))
        prior = compute_world_prior(sorted_theories, theory_priors, theories_true)
        worlds[world_id] = TheoryWorld(
            world_id=world_id,
            theories_true=theories_true,
            theories_false=theories_false,
            prior=prior,
            posterior=prior,
        )
    return worlds


def compute_world_likelihood(
    theory_ids: Iterable[str],
    theory_likelihoods: Mapping[str, float],
    theories_true: frozenset[str],
) -> float:
    """Compute P(evidence | world) using per-theory likelihood factors."""
    likelihood = 1.0
    for theory_id in set(theory_ids):
        if theory_id not in theory_likelihoods:
            continue
        p_given_true = _clamp_01(theory_likelihoods[theory_id])
        p_given_false = 1.0 - p_given_true
        likelihood *= p_given_true if theory_id in theories_true else p_given_false
    return likelihood


def update_world_posteriors(
    worlds: Mapping[str, TheoryWorld],
    theory_ids: Iterable[str],
    theory_likelihoods: Mapping[str, float],
) -> None:
    """Apply Bayesian update over worlds and renormalize."""
    if not worlds:
        return

    total = 0.0
    theory_id_set = set(theory_ids)
    for world in worlds.values():
        likelihood = compute_world_likelihood(
            theory_id_set,
            theory_likelihoods,
            world.theories_true,
        )
        world.posterior = world.prior * likelihood
        world.log_likelihood += math.log(likelihood + 1e-10)
        total += world.posterior

    if total <= 0.0:
        return

    for world in worlds.values():
        world.posterior /= total
        world.prior = world.posterior


def marginal_probability(
    worlds: Mapping[str, TheoryWorld],
    theory_id: str,
    default: float = 0.5,
) -> float:
    if not worlds:
        return default
    return sum(world.posterior for world in worlds.values() if theory_id in world.theories_true)


def joint_probability(
    worlds: Mapping[str, TheoryWorld],
    true_theories: set[str],
) -> float:
    if not worlds:
        return 0.5 ** len(true_theories)
    return sum(world.posterior for world in worlds.values() if true_theories <= world.theories_true)


def conditional_probability(
    worlds: Mapping[str, TheoryWorld],
    target_theory: str,
    given_theories: Mapping[str, bool],
    default: float = 0.5,
) -> float:
    if not worlds:
        return default

    numerator = 0.0
    denominator = 0.0
    for world in worlds.values():
        matches_given = all(
            (theory_id in world.theories_true) == is_true
            for theory_id, is_true in given_theories.items()
        )
        if not matches_given:
            continue
        denominator += world.posterior
        if target_theory in world.theories_true:
            numerator += world.posterior

    if denominator == 0.0:
        return default
    return numerator / denominator

