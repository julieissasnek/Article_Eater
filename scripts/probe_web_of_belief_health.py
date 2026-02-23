#!/usr/bin/env python3
"""Deterministic health probe for WebOfBelief invariant stability."""

from __future__ import annotations

import argparse
import math
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.epistemic.edge_types import EdgeType as ConstraintType
from src.services.web_of_belief import Belief, Credence, WebOfBelief
from src.services.web_of_belief_components import BeliefStatus, Constraint, EpistemicLevel


def make_belief(
    belief_id: str,
    *,
    content: str,
    level: EpistemicLevel,
    status: BeliefStatus,
    credence: float,
    uncertainty: float,
    theory_id: str | None = None,
) -> Belief:
    return Belief(
        belief_id=belief_id,
        content=content,
        level=level,
        status=status,
        credence=Credence(credence, uncertainty),
        theory_id=theory_id,
    )


def assert_health(web: WebOfBelief) -> None:
    eps = 1e-6
    assert 0.0 <= web.coherence_score() <= 1.0
    assert math.isfinite(web.coherence_score())

    for belief_id in web.beliefs:
        entrenchment = web.get_entrenchment(belief_id)
        assert 0.0 <= entrenchment <= 1.0
        assert math.isfinite(entrenchment)

    for constraint_id, constraint in web.constraints.items():
        assert constraint_id in web._constraints_by_belief.get(constraint.source_id, [])
        assert constraint.source_id in web.beliefs
        assert constraint.target_id in web.beliefs
        assert 0.0 <= constraint.strength <= 1.0

    if web.theory_worlds:
        total = sum(world.posterior for world in web.theory_worlds.values())
        assert total > 0.0
        assert abs(total - 1.0) <= eps
        for theory_id in web.theory_ids:
            p = web.marginal_theory_probability(theory_id)
            assert -eps <= p <= 1.0 + eps


def run_probe(iterations: int, seed: int) -> dict[str, int]:
    rng = random.Random(seed)
    web = WebOfBelief(domain="probe")
    for theory_id in ["ART", "SRT", "BIOPHILIA"]:
        web.register_theory(theory_id)
        web.add_belief(
            make_belief(
                f"theory:{theory_id.lower()}",
                content=f"{theory_id} core",
                level=EpistemicLevel.THEORETICAL,
                status=BeliefStatus.ESTABLISHED,
                credence=0.65,
                uncertainty=0.2,
                theory_id=theory_id,
            )
        )

    counters = {
        "add_belief": 0,
        "add_constraint": 0,
        "add_evidence": 0,
        "seek_equilibrium": 0,
    }
    belief_counter = 0

    for step in range(iterations):
        op = rng.choice(list(counters.keys()))
        counters[op] += 1

        if op == "add_belief":
            belief_counter += 1
            web.add_belief(
                make_belief(
                    f"b:{belief_counter}",
                    content=f"Probe belief {belief_counter}",
                    level=rng.choice(
                        [
                            EpistemicLevel.OBSERVATIONAL,
                            EpistemicLevel.EMPIRICAL,
                            EpistemicLevel.INTERMEDIATE,
                        ]
                    ),
                    status=rng.choice(
                        [BeliefStatus.STUB, BeliefStatus.TENTATIVE, BeliefStatus.ESTABLISHED]
                    ),
                    credence=0.2 + rng.random() * 0.7,
                    uncertainty=0.2 + rng.random() * 0.4,
                    theory_id=rng.choice(sorted(web.theory_ids)) if rng.random() < 0.2 else None,
                )
            )

        elif op == "add_constraint" and len(web.beliefs) >= 2:
            source_id, target_id = rng.sample(list(web.beliefs), 2)
            web.add_constraint(
                Constraint(
                    constraint_id=f"c:{step}:{source_id}:{target_id}",
                    source_id=source_id,
                    target_id=target_id,
                    constraint_type=rng.choice(
                        [
                            ConstraintType.SUPPORTS,
                            ConstraintType.CONTRADICTS,
                            ConstraintType.EXPLAINS,
                            ConstraintType.INSTANTIATES,
                        ]
                    ),
                    strength=rng.random(),
                )
            )

        elif op == "add_evidence":
            belief_counter += 1
            belief_ids = list(web.beliefs)
            sampled = rng.sample(belief_ids, min(3, len(belief_ids))) if belief_ids else []
            supports = {belief_id: rng.random() for belief_id in sampled[:2]}
            contradicts = {sampled[2]: rng.random()} if len(sampled) > 2 else {}
            web.add_evidence(
                belief_id=f"ev:{belief_counter}",
                content=f"Probe evidence {belief_counter}",
                paper_id=f"paper:{belief_counter}",
                supports_beliefs=supports,
                contradicts_beliefs=contradicts,
                theory_relevance={
                    theory_id: rng.random()
                    for theory_id in web.theory_ids
                    if rng.random() < 0.4
                },
                credence=rng.uniform(-0.25, 1.25),
            )

        else:
            web.seek_equilibrium(max_iterations=rng.randint(0, 4))

        if step % 20 == 0:
            assert_health(web)

    assert_health(web)
    counters["beliefs"] = len(web.beliefs)
    counters["constraints"] = len(web.constraints)
    counters["theory_worlds"] = len(web.theory_worlds)
    return counters


def main() -> None:
    parser = argparse.ArgumentParser(description="Run WebOfBelief health probe.")
    parser.add_argument("--iterations", type=int, default=500, help="Number of randomized operations.")
    parser.add_argument("--seed", type=int, default=1337, help="Random seed for reproducibility.")
    args = parser.parse_args()

    counters = run_probe(args.iterations, args.seed)
    print("WebOfBelief health probe passed.")
    print(f"iterations={args.iterations} seed={args.seed}")
    for key in sorted(counters):
        print(f"{key}: {counters[key]}")


if __name__ == "__main__":
    main()
