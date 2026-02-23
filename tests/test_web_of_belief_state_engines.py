from datetime import datetime, timezone

import pytest

from src.epistemic.edge_types import EdgeType as ConstraintType
from src.services.web_of_belief import Belief, Credence, WebOfBelief
from src.services.web_of_belief_components import BeliefStatus, Constraint, EpistemicLevel


def _belief(belief_id: str, credence: float = 0.6) -> Belief:
    return Belief(
        belief_id=belief_id,
        content=f"content:{belief_id}",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.TENTATIVE,
        credence=Credence(credence, 0.3),
    )


def test_web_uses_state_and_engine_layers() -> None:
    web = WebOfBelief(domain="state-layer")
    assert web.domain == "state-layer"
    assert web._state.domain == "state-layer"
    assert web._engines is not None
    assert web.beliefs is web._state.beliefs
    assert web.constraints is web._state.constraints
    assert web.theory_ids is web._state.theory_ids

    web.version = 3
    assert web.version == 3

    now = datetime.now(timezone.utc)
    web.last_updated = now
    assert web.last_updated == now


def test_assert_invariants_reports_corruption_without_raise() -> None:
    web = WebOfBelief(domain="corrupt-check")
    web.add_belief(_belief("b1"))
    web._beliefs_by_level[EpistemicLevel.EMPIRICAL].append("missing")

    errors = web.assert_invariants(raise_on_error=False)
    assert errors
    assert any("missing belief" in err for err in errors)


def test_debug_invariant_hook_raises_on_mutation_when_corrupt() -> None:
    web = WebOfBelief(domain="debug-hook")
    web.add_belief(_belief("b1"))
    web._debug_invariants = True
    web._constraints_by_belief["ghost"].append("c:ghost")

    with pytest.raises(AssertionError):
        web.add_belief(_belief("b2"))


def test_engine_backed_coherence_path_runs() -> None:
    web = WebOfBelief(domain="coherence-engine")
    web.add_belief(_belief("b1", 0.8))
    web.add_belief(_belief("b2", 0.7))
    web.add_constraint(
        Constraint(
            constraint_id="c:b1:b2",
            source_id="b1",
            target_id="b2",
            constraint_type=ConstraintType.CONTRADICTS,
            strength=0.9,
        )
    )
    assert 0.0 <= web.coherence_score() <= 1.0
    assert isinstance(web.tensions(), list)
