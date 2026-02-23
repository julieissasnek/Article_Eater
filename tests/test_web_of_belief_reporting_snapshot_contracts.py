from datetime import datetime

import pytest

from src.epistemic.edge_types import EdgeType as ConstraintType
from src.services.web_of_belief import Belief, Credence, WebOfBelief
from src.services.web_of_belief_components import BeliefStatus, Constraint, EpistemicLevel
from src.services.web_of_belief_modules.reporting import build_web_dict
from src.services.web_of_belief_modules.snapshots import build_snapshot_fields


def _belief(
    belief_id: str,
    content: str,
    *,
    level: EpistemicLevel = EpistemicLevel.EMPIRICAL,
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


@pytest.fixture
def demo_web() -> WebOfBelief:
    web = WebOfBelief(domain="demo")
    web.register_theory("ART")
    web.register_theory("SRT")

    t1 = _belief(
        "theory:art",
        "Attention restoration theory core claim",
        level=EpistemicLevel.THEORETICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=0.75,
        uncertainty=0.2,
        theory_id="ART",
    )
    e1 = _belief(
        "emp:long",
        "L" * 90,
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.TENTATIVE,
        credence=0.62,
        uncertainty=0.25,
    )
    anomaly = _belief(
        "emp:anom",
        "Anomalous finding",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.ANOMALOUS,
        credence=0.72,
        uncertainty=0.4,
    )
    stub = _belief(
        "stub:1",
        "Unintegrated finding",
        level=EpistemicLevel.OBSERVATIONAL,
        status=BeliefStatus.STUB,
        credence=0.55,
        uncertainty=0.35,
    )

    web.add_belief(t1)
    web.add_belief(e1)
    web.add_belief(anomaly)
    web.add_belief(stub)

    web.add_constraint(
        Constraint(
            constraint_id="c:t1:e1",
            source_id="theory:art",
            target_id="emp:long",
            constraint_type=ConstraintType.SUPPORTS,
            strength=0.8,
        )
    )
    web.add_constraint(
        Constraint(
            constraint_id="c:e1:anom",
            source_id="emp:long",
            target_id="emp:anom",
            constraint_type=ConstraintType.CONTRADICTS,
            strength=0.9,
        )
    )
    return web


def test_summary_contains_expected_sections_and_truncation(demo_web: WebOfBelief) -> None:
    text = demo_web.summary()
    assert "# Web of Belief Summary" in text
    assert "## Beliefs by Level" in text
    assert "## Theory Probabilities" in text
    assert "## Joint Distribution (top 5 worlds)" in text
    assert "## Tensions" in text
    assert "## Stubs (Unintegrated Findings)" in text
    assert "..." in text


def test_summary_without_theories_omits_theory_sections() -> None:
    web = WebOfBelief(domain="empty")
    web.add_belief(_belief("b1", "single belief"))
    text = web.summary()
    assert "## Theory Probabilities" not in text
    assert "## Joint Distribution (top 5 worlds)" not in text


def test_web_to_dict_shape_and_theory_marginals(demo_web: WebOfBelief) -> None:
    payload = demo_web.to_dict()
    assert payload["domain"] == "demo"
    assert payload["n_beliefs"] == len(demo_web.beliefs)
    assert payload["n_constraints"] == len(demo_web.constraints)
    assert set(payload["theory_marginals"].keys()) == {"ART", "SRT"}
    for value in payload["theory_marginals"].values():
        assert 0.0 <= value <= 1.0


def test_snapshot_isolation_deep_copy(demo_web: WebOfBelief) -> None:
    snapshot = demo_web.snapshot()
    before = snapshot.beliefs["emp:long"].content

    demo_web.beliefs["emp:long"].content = "changed after snapshot"
    demo_web.add_belief(_belief("new:belief", "new content"))

    assert snapshot.beliefs["emp:long"].content == before
    assert "new:belief" not in snapshot.beliefs


def test_snapshot_accessors_and_to_dict(demo_web: WebOfBelief) -> None:
    snapshot = demo_web.snapshot()
    assert any(b.belief_id == "stub:1" for b in snapshot.get_stubs())
    assert any(b.belief_id == "emp:anom" for b in snapshot.get_anomalies())
    assert any(
        b.belief_id == "theory:art"
        for b in snapshot.get_beliefs_by_level(EpistemicLevel.THEORETICAL)
    )

    payload = snapshot.to_dict()
    assert payload["n_beliefs"] == len(snapshot.beliefs)
    assert payload["n_constraints"] == len(snapshot.constraints)
    datetime.fromisoformat(payload["snapshot_at"])


def test_reporting_helper_build_web_dict_copies_input_map() -> None:
    marginals = {"ART": 0.7}
    payload = build_web_dict(
        domain="demo",
        version=2,
        n_beliefs=5,
        n_constraints=3,
        n_stubs=1,
        coherence=0.6,
        n_tensions=0,
        theory_marginals=marginals,
    )
    marginals["ART"] = 0.1
    assert payload["theory_marginals"]["ART"] == pytest.approx(0.7)


def test_snapshot_helper_build_snapshot_fields_deep_copies() -> None:
    beliefs = {"b1": _belief("b1", "before")}
    constraints: dict[str, Constraint] = {}
    fields = build_snapshot_fields(
        domain="demo",
        version=1,
        beliefs=beliefs,
        constraints=constraints,
        coherence_score=0.5,
        tensions=[],
        theory_ids={"ART"},
        stubs=set(),
    )

    beliefs["b1"].content = "after"
    assert fields["beliefs"]["b1"].content == "before"
