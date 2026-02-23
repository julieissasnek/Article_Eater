import pytest

from src.epistemic.edge_types import EdgeType as ConstraintType
from src.services.web_of_belief import Belief, Credence, WebOfBelief
from src.services.web_of_belief_components import BeliefStatus, Constraint, EpistemicLevel


def _belief(
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


def test_analysis_layer_methods_return_expected_shapes() -> None:
    web = WebOfBelief(domain="analysis-shapes")
    web.register_theory("ART")
    web.register_theory("SRT")

    web.add_belief(
        _belief(
            "t:art",
            content="Attention Restoration Theory",
            level=EpistemicLevel.THEORETICAL,
            status=BeliefStatus.ESTABLISHED,
            theory_id="ART",
            credence=0.72,
        )
    )
    web.add_belief(
        _belief(
            "t:srt",
            content="Stress Recovery Theory",
            level=EpistemicLevel.THEORETICAL,
            status=BeliefStatus.ESTABLISHED,
            theory_id="SRT",
            credence=0.68,
        )
    )
    web.add_belief(
        _belief(
            "e:stress_drop",
            content="Participants showed lower stress after park exposure",
            level=EpistemicLevel.EMPIRICAL,
            credence=0.64,
        )
    )
    web.add_constraint(
        Constraint(
            constraint_id="c:explain:art:stress",
            source_id="t:art",
            target_id="e:stress_drop",
            constraint_type=ConstraintType.EXPLAINS,
            strength=0.8,
        )
    )

    assert 0.0 <= web.belief_centrality("e:stress_drop") <= 1.0
    assert 0.0 <= web.belief_value("e:stress_drop") <= 1.0
    assert isinstance(web.beliefs_by_value(), list)
    assert isinstance(web.high_value_beliefs(threshold=0.0), list)
    assert isinstance(web.get_research_priorities(top_n=3), dict)
    assert isinstance(web.summary(), str)
    as_dict = web.to_dict()
    assert "n_beliefs" in as_dict
    assert "theory_marginals" in as_dict


def test_belief_sensitivity_restores_credence_and_coherence() -> None:
    web = WebOfBelief(domain="analysis-sensitivity")
    web.add_belief(
        _belief("b1", content="Belief one", level=EpistemicLevel.EMPIRICAL, credence=0.7)
    )
    web.add_belief(
        _belief("b2", content="Belief two", level=EpistemicLevel.EMPIRICAL, credence=0.65)
    )
    web.add_constraint(
        Constraint(
            constraint_id="c:b1:b2",
            source_id="b1",
            target_id="b2",
            constraint_type=ConstraintType.SUPPORTS,
            strength=0.75,
        )
    )

    cred_before = web.beliefs["b1"].credence.value
    coh_before = web.coherence_score()
    sensitivity = web.belief_sensitivity("b1", delta=0.15)
    cred_after = web.beliefs["b1"].credence.value
    coh_after = web.coherence_score()

    assert 0.0 <= sensitivity <= 1.0
    assert cred_after == pytest.approx(cred_before)
    assert coh_after == pytest.approx(coh_before)


def test_theory_can_explain_finding_and_gain_support_from_evidence() -> None:
    web = WebOfBelief(domain="analysis-explains")
    web.register_theory("ART")

    web.add_belief(
        _belief(
            "t:art",
            content="Natural settings restore directed attention",
            level=EpistemicLevel.THEORETICAL,
            status=BeliefStatus.ESTABLISHED,
            theory_id="ART",
            credence=0.7,
        )
    )
    web.add_belief(
        _belief(
            "e:attention_gain",
            content="Students exposed to greenery performed better on attention tasks",
            level=EpistemicLevel.EMPIRICAL,
            credence=0.62,
        )
    )
    web.add_constraint(
        Constraint(
            constraint_id="c:art:attention",
            source_id="t:art",
            target_id="e:attention_gain",
            constraint_type=ConstraintType.EXPLAINS,
            strength=0.85,
        )
    )

    prior_marginal = web.marginal_theory_probability("ART")
    updates = web.add_evidence(
        belief_id="ev:attention_replication",
        content="Replication found similar attention gains near trees",
        paper_id="paper:replication-1",
        supports_beliefs={"e:attention_gain": 0.8},
        theory_relevance={"ART": 0.85},
        credence=0.72,
    )
    posterior_marginal = web.marginal_theory_probability("ART")

    assert "ART" in updates["theory_world_updates"]
    assert posterior_marginal > prior_marginal
    assert web.constraints["c:art:attention"].constraint_type == ConstraintType.EXPLAINS
