import math
import random
from typing import Dict

import pytest

from src.epistemic.edge_types import EdgeType as ConstraintType
from src.services.web_of_belief import Belief, Credence, WebOfBelief
from src.services.web_of_belief_components import (
    BeliefStatus,
    Constraint,
    EpistemicLevel,
    UncertainQuantity,
)


def _make_belief(
    belief_id: str,
    *,
    content: str,
    level: EpistemicLevel,
    status: BeliefStatus = BeliefStatus.TENTATIVE,
    credence: float = 0.6,
    uncertainty: float = 0.3,
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


def _assert_probability_invariants(web: WebOfBelief) -> None:
    if not web.theory_worlds:
        return

    posteriors = [world.posterior for world in web.theory_worlds.values()]
    assert all(math.isfinite(value) for value in posteriors)
    assert all(value >= 0.0 for value in posteriors)
    assert sum(posteriors) == pytest.approx(1.0, abs=1e-6)

    for theory_id in web.theory_ids:
        marginal = web.marginal_theory_probability(theory_id)
        assert 0.0 <= marginal <= 1.0

    sorted_theories = sorted(web.theory_ids)
    if len(sorted_theories) >= 2:
        cond = web.conditional_probability(
            target_theory=sorted_theories[0],
            given_theories={sorted_theories[1]: True},
        )
        assert 0.0 <= cond <= 1.0


def _assert_web_invariants(web: WebOfBelief) -> None:
    assert 0.0 <= web.coherence_score() <= 1.0
    assert math.isfinite(web.coherence_score())

    for belief_id, belief in web.beliefs.items():
        entrenchment = web.get_entrenchment(belief_id)
        assert 0.0 <= entrenchment <= 1.0
        assert math.isfinite(entrenchment)
        assert belief.level in EpistemicLevel
        assert belief.status in BeliefStatus

    for level, belief_ids in web._beliefs_by_level.items():
        for belief_id in belief_ids:
            assert belief_id in web.beliefs
            assert web.beliefs[belief_id].level == level

    for theory_id, belief_ids in web._beliefs_by_theory.items():
        for belief_id in belief_ids:
            assert belief_id in web.beliefs
            assert web.beliefs[belief_id].theory_id == theory_id

    for belief_id in web._stubs:
        assert belief_id in web.beliefs
        assert web.beliefs[belief_id].status == BeliefStatus.STUB

    for constraint_id, constraint in web.constraints.items():
        assert constraint.source_id in web.beliefs
        assert constraint.target_id in web.beliefs
        assert 0.0 <= constraint.strength <= 1.0
        assert constraint_id in web._constraints_by_belief.get(constraint.source_id, [])
        if constraint.bidirectional:
            assert constraint_id in web._constraints_by_belief.get(constraint.target_id, [])

    for belief_id, constraint_ids in web._constraints_by_belief.items():
        for constraint_id in constraint_ids:
            assert constraint_id in web.constraints
            constraint = web.constraints[constraint_id]
            assert belief_id in (constraint.source_id, constraint.target_id)

    for tension in web.tensions():
        assert tension["source"] in web.beliefs
        assert tension["target"] in web.beliefs
        assert 0.0 <= float(tension.get("source_credence", 0.0)) <= 1.0
        assert 0.0 <= float(tension.get("target_credence", 0.0)) <= 1.0

    _assert_probability_invariants(web)


def test_global_invariants_after_mutating_calls() -> None:
    web = WebOfBelief(domain="invariants")
    web.register_theory("ART")
    web.register_theory("SRT")

    t_art = _make_belief(
        "theory:art",
        content="ART core",
        level=EpistemicLevel.THEORETICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=0.72,
        uncertainty=0.2,
        theory_id="ART",
    )
    t_srt = _make_belief(
        "theory:srt",
        content="SRT core",
        level=EpistemicLevel.THEORETICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=0.68,
        uncertainty=0.2,
        theory_id="SRT",
    )
    e1 = _make_belief(
        "emp:stress",
        content="Nature reduces stress",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.TENTATIVE,
        credence=0.63,
        uncertainty=0.28,
    )
    e1.temporal_params = {
        "lag": UncertainQuantity(estimate=15.0, standard_error=2.0, n_observations=2),
    }

    web.add_belief(t_art)
    web.add_belief(t_srt)
    web.add_belief(e1, connect_to=[("theory:art", ConstraintType.SUPPORTS, 0.7)])
    web.add_constraint(
        Constraint(
            constraint_id="c:srt:stress",
            source_id="theory:srt",
            target_id="emp:stress",
            constraint_type=ConstraintType.SUPPORTS,
            strength=0.65,
        )
    )
    _assert_web_invariants(web)

    web.add_evidence(
        belief_id="ev:001",
        content="RCT confirms stress reduction",
        paper_id="paper:001",
        supports_beliefs={"emp:stress": 0.8},
        contradicts_beliefs={"theory:srt": 0.1},
        observed_temporal={"lag": (13.0, 1.5)},
        theory_relevance={"ART": 0.78, "SRT": 0.42},
        credence=0.7,
    )
    _assert_web_invariants(web)

    web.seek_equilibrium(max_iterations=5)
    _assert_web_invariants(web)


@pytest.mark.parametrize(
    "payload",
    [
        {
            "belief_id": "",
            "content": "",
            "paper_id": "",
            "supports_beliefs": {"missing": 2.0},
            "contradicts_beliefs": {"other": -1.2},
            "observed_temporal": {"bad": ("x", "y")},
            "credence": -3.0,
        },
        {
            "belief_id": "ev:bad2",
            "content": "ok",
            "paper_id": "paper:ok",
            "supports_beliefs": {None: 0.9},  # type: ignore[dict-item]
            "contradicts_beliefs": {"existing": "nan"},  # type: ignore[dict-item]
            "theory_relevance": {"ART": 5.0},
            "observed_temporal": {"lag": (10.0, -4.0)},
            "credence": 2.0,
        },
    ],
)
def test_malformed_add_evidence_never_crashes_and_preserves_invariants(
    payload: Dict[str, object],
) -> None:
    web = WebOfBelief(domain="robustness")
    web.register_theory("ART")
    web.add_belief(
        _make_belief(
            "existing",
            content="Existing belief",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=0.55,
            uncertainty=0.3,
        )
    )

    result = web.add_evidence(**payload)
    assert "belief_updates" in result
    assert "theory_world_updates" in result
    assert "temporal_updates" in result
    _assert_web_invariants(web)


@pytest.mark.slow
def test_randomized_health_probe_invariants_stay_stable() -> None:
    rng = random.Random(1337)
    web = WebOfBelief(domain="stochastic")
    for theory_id in ["ART", "SRT", "BIOPHILIA"]:
        web.register_theory(theory_id)

    counter = 0
    for theory_id in sorted(web.theory_ids):
        belief = _make_belief(
            f"theory:{theory_id.lower()}",
            content=f"{theory_id} core",
            level=EpistemicLevel.THEORETICAL,
            status=BeliefStatus.ESTABLISHED,
            credence=0.6 + rng.random() * 0.2,
            uncertainty=0.2,
            theory_id=theory_id,
        )
        web.add_belief(belief)

    operation_count = 240
    for step in range(operation_count):
        op = rng.choice(["add_belief", "add_constraint", "add_evidence", "equilibrium"])

        if op == "add_belief":
            counter += 1
            level = rng.choice(
                [
                    EpistemicLevel.OBSERVATIONAL,
                    EpistemicLevel.EMPIRICAL,
                    EpistemicLevel.INTERMEDIATE,
                ]
            )
            status = rng.choice([BeliefStatus.STUB, BeliefStatus.TENTATIVE, BeliefStatus.ESTABLISHED])
            theory_id = rng.choice(sorted(web.theory_ids)) if rng.random() < 0.25 else None
            web.add_belief(
                _make_belief(
                    f"b:{counter}",
                    content=f"Random belief {counter}",
                    level=level,
                    status=status,
                    credence=0.2 + rng.random() * 0.7,
                    uncertainty=0.2 + rng.random() * 0.3,
                    theory_id=theory_id,
                )
            )

        elif op == "add_constraint" and len(web.beliefs) >= 2:
            source_id, target_id = rng.sample(list(web.beliefs.keys()), 2)
            constraint_type = rng.choice(
                [
                    ConstraintType.SUPPORTS,
                    ConstraintType.CONTRADICTS,
                    ConstraintType.EXPLAINS,
                    ConstraintType.INSTANTIATES,
                ]
            )
            web.add_constraint(
                Constraint(
                    constraint_id=f"c:r:{step}:{source_id}:{target_id}",
                    source_id=source_id,
                    target_id=target_id,
                    constraint_type=constraint_type,
                    strength=rng.random(),
                    bidirectional=bool(rng.getrandbits(1)),
                )
            )

        elif op == "add_evidence":
            counter += 1
            supports = {}
            contradicts = {}
            existing_ids = list(web.beliefs.keys())
            if existing_ids:
                sampled = rng.sample(existing_ids, min(3, len(existing_ids)))
                for belief_id in sampled[:2]:
                    supports[belief_id] = rng.random()
                if len(sampled) > 2:
                    contradicts[sampled[2]] = rng.random()

            web.add_evidence(
                belief_id=f"ev:r:{counter}",
                content=f"Random evidence {counter}",
                paper_id=f"paper:r:{counter}",
                supports_beliefs=supports,
                contradicts_beliefs=contradicts,
                theory_relevance={theory_id: rng.random() for theory_id in web.theory_ids if rng.random() < 0.4},
                observed_temporal={"lag": (rng.uniform(1, 30), rng.uniform(0.1, 5.0))}
                if rng.random() < 0.2
                else None,
                credence=rng.uniform(-0.5, 1.5),
            )

        else:
            web.seek_equilibrium(max_iterations=rng.randint(0, 4))

        if step % 8 == 0:
            _assert_web_invariants(web)

    _assert_web_invariants(web)
