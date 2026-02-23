from src.epistemic.edge_types import EdgeType as ConstraintType
from src.services.web_of_belief import Belief, Credence, WebOfBelief
from src.services.web_of_belief_components import BeliefStatus, Constraint, EpistemicLevel


def _belief(
    belief_id: str,
    *,
    level: EpistemicLevel,
    status: BeliefStatus,
    theory_id: str | None = None,
) -> Belief:
    return Belief(
        belief_id=belief_id,
        content=f"content:{belief_id}",
        level=level,
        status=status,
        credence=Credence(0.6, 0.3),
        theory_id=theory_id,
    )


def test_replacing_belief_id_keeps_indexes_consistent() -> None:
    web = WebOfBelief(domain="mutation-safeguards")
    web.add_belief(
        _belief(
            "b:shared",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.STUB,
            theory_id="ART",
        )
    )
    web.add_belief(
        _belief(
            "b:shared",
            level=EpistemicLevel.THEORETICAL,
            status=BeliefStatus.TENTATIVE,
            theory_id="SRT",
        )
    )

    assert web.beliefs["b:shared"].level == EpistemicLevel.THEORETICAL
    assert "b:shared" not in web._beliefs_by_level[EpistemicLevel.EMPIRICAL]
    assert web._beliefs_by_level[EpistemicLevel.THEORETICAL].count("b:shared") == 1
    assert "b:shared" not in web._beliefs_by_theory["ART"]
    assert web._beliefs_by_theory["SRT"].count("b:shared") == 1
    assert "b:shared" not in web._stubs


def test_replacing_constraint_id_rewrites_indexes_without_duplicates() -> None:
    web = WebOfBelief(domain="mutation-safeguards")
    web.add_belief(_belief("a", level=EpistemicLevel.EMPIRICAL, status=BeliefStatus.TENTATIVE))
    web.add_belief(_belief("b", level=EpistemicLevel.EMPIRICAL, status=BeliefStatus.TENTATIVE))
    web.add_belief(_belief("c", level=EpistemicLevel.EMPIRICAL, status=BeliefStatus.TENTATIVE))

    web.add_constraint(
        Constraint(
            constraint_id="c:shared",
            source_id="a",
            target_id="b",
            constraint_type=ConstraintType.SUPPORTS,
            strength=0.7,
            bidirectional=True,
        )
    )
    web.add_constraint(
        Constraint(
            constraint_id="c:shared",
            source_id="c",
            target_id="a",
            constraint_type=ConstraintType.CONTRADICTS,
            strength=0.6,
            bidirectional=False,
        )
    )

    assert web.constraints["c:shared"].source_id == "c"
    assert web._constraints_by_belief["c"].count("c:shared") == 1
    assert "c:shared" not in web._constraints_by_belief["a"]
    assert "c:shared" not in web._constraints_by_belief["b"]


def test_add_evidence_deduplicates_paper_ids_for_existing_evidence_belief() -> None:
    web = WebOfBelief(domain="mutation-safeguards")
    web.add_evidence(
        belief_id="ev:1",
        content="Initial finding",
        paper_id="paper:1",
        supports_beliefs={},
        contradicts_beliefs={},
        credence=0.6,
    )
    web.add_evidence(
        belief_id="ev:1",
        content="Replicated finding",
        paper_id="paper:1",
        supports_beliefs={},
        contradicts_beliefs={},
        credence=0.6,
    )
    web.add_evidence(
        belief_id="ev:1",
        content="Replicated finding in second paper",
        paper_id="paper:2",
        supports_beliefs={},
        contradicts_beliefs={},
        credence=0.6,
    )

    paper_ids = web.beliefs["ev:1"].paper_ids
    assert paper_ids.count("paper:1") == 1
    assert "paper:2" in paper_ids


def test_seek_equilibrium_negative_iterations_matches_zero_behavior() -> None:
    web = WebOfBelief(domain="mutation-safeguards")
    result = web.seek_equilibrium(max_iterations=-5)
    assert result["iterations"] == 0
    assert "adjustments" in result
