import pytest

from src.epistemic.edge_types import EdgeType as ConstraintType
from src.services.web_of_belief import Belief, Credence, WebOfBelief
from src.services.web_of_belief_components import (
    BeliefStatus,
    Constraint,
    EpistemicLevel,
    ScopeConditions,
)
from src.services.web_of_belief_modules.entrenchment import (
    EntrenchmentInput,
    compute_entrenchment_components,
)
from src.services.web_of_belief_modules.coherence import compute_coherence_state
from src.services.web_of_belief_modules.equilibrium import (
    CredenceAdjustment,
    choose_adjustment_target,
    compute_credence_adjustment,
)
from src.services.web_of_belief_modules.experiments import (
    ExperimentBeliefInput,
    estimate_resolution,
    identify_scope_differences,
    infer_experiment_type,
    infer_test_focus_and_hypothesis,
    suggest_contested_scope,
    suggest_scope,
)
from src.services.web_of_belief_modules.evidence_updates import (
    build_evidence_input,
    init_updates_payload,
)
from src.services.web_of_belief_modules.theory_worlds import (
    build_theory_worlds,
    conditional_probability,
    joint_probability,
    marginal_probability,
    update_world_posteriors,
)
from src.services.web_of_belief_modules.value_metrics import (
    BeliefValueRecord,
    CentralityInput,
    EpistemicValueInput,
    compute_centrality,
    compute_epistemic_value,
    sort_value_records,
)


def _make_belief(belief_id: str, credence: float) -> Belief:
    return Belief(
        belief_id=belief_id,
        content=f"content:{belief_id}",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.TENTATIVE,
        credence=Credence(value=credence, uncertainty=0.3),
    )


def test_entrenchment_contract_computation_is_bounded() -> None:
    payload = EntrenchmentInput(
        belief_id="b1",
        belief_level=EpistemicLevel.EMPIRICAL,
        credence_value=1.4,
        credence_uncertainty=-0.2,
        belief_status=BeliefStatus.ESTABLISHED,
        constraint_count=25,
    )
    result = compute_entrenchment_components(payload)
    assert 0.0 <= result.entrenchment <= 1.0
    assert 0.0 <= result.connectivity <= 1.0
    assert 0.0 <= result.level_weight <= 1.0
    assert 0.0 <= result.coherence_contrib <= 1.0
    assert result.constraint_count == 25


def test_entrenchment_contract_rejects_negative_constraint_count() -> None:
    payload = EntrenchmentInput(
        belief_id="b1",
        belief_level=EpistemicLevel.EMPIRICAL,
        credence_value=0.5,
        credence_uncertainty=0.5,
        belief_status=BeliefStatus.TENTATIVE,
        constraint_count=-1,
    )
    with pytest.raises(ValueError):
        compute_entrenchment_components(payload)


def test_value_contract_helpers_validate_and_sort() -> None:
    with pytest.raises(ValueError):
        compute_centrality(CentralityInput(belief_id="", constraint_count=1, total_beliefs=2))

    value = compute_epistemic_value(
        EpistemicValueInput(centrality=0.7, sensitivity=0.2, centrality_weight=0.75)
    )
    assert value == pytest.approx(0.575)

    records = [
        BeliefValueRecord("b1", 0.3, 0.3, 0.3),
        BeliefValueRecord("b2", 0.8, 0.8, 0.8),
    ]
    ranked = sort_value_records(records, top_n=1)
    assert [record.belief_id for record in ranked] == ["b2"]
    assert sort_value_records(records, top_n=0) == []


def test_web_belief_sensitivity_guard_and_weight_clamp() -> None:
    web = WebOfBelief(domain="test")
    b1 = _make_belief("b1", 0.7)
    b2 = _make_belief("b2", 0.4)
    web.add_belief(b1)
    web.add_belief(b2)
    web.add_constraint(
        Constraint(
            constraint_id="c:b1:b2",
            source_id="b1",
            target_id="b2",
            constraint_type=ConstraintType.SUPPORTS,
            strength=0.8,
        )
    )

    assert web.belief_sensitivity("b1", delta=0.0) == 0.0

    clamped = web.belief_value("b1", centrality_weight=1.5)
    explicit = web.belief_value("b1", centrality_weight=1.0)
    assert clamped == pytest.approx(explicit)
    assert 0.0 <= clamped <= 1.0


def test_coherence_module_matches_web_update_path() -> None:
    web = WebOfBelief(domain="test")
    b1 = _make_belief("b1", 0.8)
    b2 = _make_belief("b2", 0.75)
    web.add_belief(b1)
    web.add_belief(b2)
    web.add_constraint(
        Constraint(
            constraint_id="c:b1:b2:contradicts",
            source_id="b1",
            target_id="b2",
            constraint_type=ConstraintType.CONTRADICTS,
            strength=1.0,
        )
    )

    result = compute_coherence_state(web.beliefs, web.constraints.values())
    assert 0.0 <= result.coherence_score <= 1.0
    assert any(t.get("type") == "contradiction_tension" for t in result.tensions)


def test_equilibrium_contract_helpers_and_zero_iteration_guard() -> None:
    choice = choose_adjustment_target("a", "b", source_entrenchment=0.2, target_entrenchment=0.8)
    assert choice.belief_id == "a"
    assert "more entrenched b" in choice.reason

    adjusted = compute_credence_adjustment(
        CredenceAdjustment(
            old_credence=0.7,
            old_uncertainty=0.25,
            n_supporting=3,
            n_contradicting=1,
            n_observations=4,
        )
    )
    assert adjusted.new_credence == pytest.approx(0.595)
    assert adjusted.new_n_contradicting == 2
    assert adjusted.should_mark_anomalous is False

    with pytest.raises(ValueError):
        compute_credence_adjustment(
            CredenceAdjustment(
                old_credence=0.7,
                old_uncertainty=0.25,
                n_supporting=-1,
                n_contradicting=1,
                n_observations=4,
            )
        )

    web = WebOfBelief(domain="test")
    web.add_belief(_make_belief("x", 0.8))
    web.add_belief(_make_belief("y", 0.75))
    web.add_constraint(
        Constraint(
            constraint_id="c:x:y:contradicts",
            source_id="x",
            target_id="y",
            constraint_type=ConstraintType.CONTRADICTS,
            strength=1.0,
        )
    )
    result = web.seek_equilibrium(max_iterations=0)
    assert result["iterations"] == 0
    assert isinstance(result["adjustments"], list)


def test_experiment_contract_helpers_match_web_wrappers() -> None:
    web = WebOfBelief(domain="test")
    source = Belief(
        belief_id="theory:a",
        content="Theory A predicts reduced stress",
        level=EpistemicLevel.THEORETICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.8, 0.2),
        _legacy_entrenchment=0.4,
        scope=ScopeConditions(population="adults", setting="lab", duration="2w", measurement="hrv"),
    )
    target = Belief(
        belief_id="emp:b",
        content="Observed stress reduction in adults",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.TENTATIVE,
        credence=Credence(0.6, 0.3),
        _legacy_entrenchment=0.6,
        scope=ScopeConditions(population="adolescents", setting="field", duration="2w", measurement="cortisol"),
    )

    source_input = ExperimentBeliefInput(
        belief_id=source.belief_id,
        content=source.content,
        level=source.level,
        entrenchment=source.entrenchment,
        scope=source.scope,
    )
    target_input = ExperimentBeliefInput(
        belief_id=target.belief_id,
        content=target.content,
        level=target.level,
        entrenchment=target.entrenchment,
        scope=target.scope,
    )

    assert web._infer_experiment_type(source, target) == infer_experiment_type(source.level, target.level)
    focus, hypothesis = infer_test_focus_and_hypothesis(source_input, target_input)
    assert focus == "theoretical_prediction"
    assert "predicts" in hypothesis

    module_scope = suggest_scope(source.scope, target.scope)
    web_scope = web._suggest_scope(source, target)
    assert module_scope == web_scope

    module_diffs = identify_scope_differences([source.scope, target.scope])
    web_diffs = web._identify_scope_differences([source.scope, target.scope])
    assert module_diffs == web_diffs
    assert "population" in module_diffs
    assert "setting" in module_diffs

    assert web._suggest_contested_scope(source) == suggest_contested_scope(source.scope)

    module_resolution = estimate_resolution(source_input, target_input)
    web_resolution = web._estimate_resolution(source, target)
    assert module_resolution == web_resolution


def test_theory_world_contract_helpers_match_web_probability_wrappers() -> None:
    priors = {"A": 0.7, "B": 0.4}
    worlds_for_module = build_theory_worlds(["A", "B"], priors)
    worlds_for_web = build_theory_worlds(["A", "B"], priors)

    update_world_posteriors(
        worlds_for_module,
        theory_ids={"A", "B"},
        theory_likelihoods={"A": 0.8, "B": 0.3},
    )
    update_world_posteriors(
        worlds_for_web,
        theory_ids={"A", "B"},
        theory_likelihoods={"A": 0.8, "B": 0.3},
    )

    web = WebOfBelief(domain="test")
    web.theory_ids = {"A", "B"}
    web.theory_worlds = worlds_for_web

    assert web.marginal_theory_probability("A") == pytest.approx(
        marginal_probability(worlds_for_module, "A")
    )
    assert web.joint_probability({"A"}) == pytest.approx(
        joint_probability(worlds_for_module, {"A"})
    )
    assert web.conditional_probability("A", {"B": True}) == pytest.approx(
        conditional_probability(worlds_for_module, "A", {"B": True})
    )


def test_theory_world_posteriors_remain_normalized_after_updates() -> None:
    worlds = build_theory_worlds(["A", "B", "C"], {"A": 0.6, "B": 0.4, "C": 0.3})
    update_world_posteriors(worlds, {"A", "B", "C"}, {"A": 0.8, "B": 0.2, "C": 0.5})
    total_1 = sum(world.posterior for world in worlds.values())
    assert total_1 == pytest.approx(1.0)

    update_world_posteriors(worlds, {"A", "B", "C"}, {"A": 0.7, "B": 0.6, "C": 0.1})
    total_2 = sum(world.posterior for world in worlds.values())
    assert total_2 == pytest.approx(1.0)


def test_theory_world_default_probabilities_without_worlds() -> None:
    assert marginal_probability({}, "A") == pytest.approx(0.5)
    assert joint_probability({}, {"A", "B"}) == pytest.approx(0.25)
    assert conditional_probability({}, "A", {"B": True}) == pytest.approx(0.5)


def test_evidence_input_contract_normalizes_and_web_fallback_is_safe() -> None:
    payload = build_evidence_input(
        belief_id="ev:1",
        content="evidence item",
        paper_id="paper:1",
        supports_beliefs={"b1": 1.8, "b2": -0.2},
        contradicts_beliefs={"b3": 0.4},
        theory_relevance={"T1": 1.2},
        observed_temporal={"lag": (10, -3), "bad": ("x", 2)},
        credence=1.4,
    )
    assert payload.credence == pytest.approx(1.0)
    assert payload.supports_beliefs["b1"] == pytest.approx(1.0)
    assert payload.supports_beliefs["b2"] == pytest.approx(0.0)
    assert payload.theory_relevance["T1"] == pytest.approx(1.0)
    assert payload.observed_temporal["lag"] == pytest.approx((10.0, 3.0))
    assert "bad" not in payload.observed_temporal

    updates_seed = init_updates_payload(0.42)
    assert updates_seed["coherence_before"] == pytest.approx(0.42)
    assert updates_seed["coherence_after"] == pytest.approx(0.0)

    web = WebOfBelief(domain="test")
    result = web.add_evidence(
        belief_id="",
        content="",
        paper_id="",
        supports_beliefs={"missing": 2.5},
        contradicts_beliefs=None,
        observed_temporal={"invalid": ("bad", "data")},
        credence=-2.0,
    )
    assert "belief_updates" in result
    assert "theory_world_updates" in result
    assert "temporal_updates" in result
    assert "evidence:unknown" in web.beliefs
