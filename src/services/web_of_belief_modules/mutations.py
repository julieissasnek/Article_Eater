"""Mutation operations and contracts for WebOfBelief state transitions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import logging
from typing import Any, Callable, Mapping, Optional, Sequence

logger = logging.getLogger(__name__)


def _append_unique(items: list[Any], value: Any) -> None:
    if value not in items:
        items.append(value)


def _remove_all(items: list[Any], value: Any) -> None:
    while value in items:
        items.remove(value)


@dataclass(frozen=True)
class MutationContracts:
    """Explicit dependency contract for mutation operations."""

    belief_factory: Callable[..., Any]
    constraint_factory: Callable[..., Any]
    credence_factory: Callable[..., Any]
    credence_adjustment_factory: Callable[..., Any]
    choose_adjustment_target: Callable[..., Any]
    compute_credence_adjustment: Callable[..., Any]
    build_evidence_input: Callable[..., Any]
    init_updates_payload: Callable[[float], dict[str, Any]]
    make_belief_update_record: Callable[..., dict[str, Any]]
    make_temporal_update_record: Callable[..., dict[str, Any]]
    make_theory_world_update_records: Callable[..., dict[str, Any]]
    ensure_theory_relevance: Callable[..., None]
    status_stub: Any
    status_tentative: Any
    status_anomalous: Any
    level_theoretical: Any
    level_empirical: Any
    ctype_supports: Any
    ctype_contradicts: Any
    ctype_instantiates: Any
    ctype_bridges: Any
    ctype_strong_tension: Any
    causal_direction_mediated: Any


@dataclass(frozen=True)
class EquilibriumRequest:
    max_iterations: int = 10

    def clamped_iterations(self) -> int:
        return max(0, int(self.max_iterations))


class WebMutationOperations:
    """Mutable-state transition helpers extracted from WebOfBelief."""

    def __init__(self, contracts: MutationContracts):
        self._contracts = contracts

    def _remove_belief_indexes(self, web: Any, belief: Any) -> None:
        belief_id = getattr(belief, "belief_id", "")
        if not belief_id:
            return
        _remove_all(web._beliefs_by_level[getattr(belief, "level", None)], belief_id)
        theory_id = getattr(belief, "theory_id", None)
        if theory_id:
            _remove_all(web._beliefs_by_theory[theory_id], belief_id)
        web._stubs.discard(belief_id)

    def _remove_constraint_indexes(self, web: Any, constraint: Any, constraint_id: str) -> None:
        _remove_all(web._constraints_by_belief[getattr(constraint, "source_id", "")], constraint_id)
        _remove_all(web._constraints_by_belief[getattr(constraint, "target_id", "")], constraint_id)

    def add_belief(
        self,
        web: Any,
        *,
        belief: Any,
        connect_to: Optional[Sequence[tuple[str, Any, float]]] = None,
    ) -> None:
        existing = web.beliefs.get(belief.belief_id)
        if existing is not None:
            self._remove_belief_indexes(web, existing)

        web.beliefs[belief.belief_id] = belief
        _append_unique(web._beliefs_by_level[belief.level], belief.belief_id)

        if belief.theory_id:
            _append_unique(web._beliefs_by_theory[belief.theory_id], belief.belief_id)

        if belief.is_stub():
            web._stubs.add(belief.belief_id)
        else:
            web._stubs.discard(belief.belief_id)

        if connect_to:
            for target_id, ctype, strength in connect_to:
                if target_id not in web.beliefs:
                    continue
                web.add_constraint(
                    self._contracts.constraint_factory(
                        constraint_id=f"c:{belief.belief_id}:{target_id}",
                        source_id=belief.belief_id,
                        target_id=target_id,
                        constraint_type=ctype,
                        strength=strength,
                    )
                )

        web.version += 1
        logger.debug("Added belief: %s at level %s", belief.belief_id, getattr(belief.level, "value", ""))
        web._assert_invariants_if_enabled()

    def add_constraint(self, web: Any, *, constraint: Any) -> None:
        if getattr(constraint, "causal_direction", None) == self._contracts.causal_direction_mediated:
            if getattr(constraint, "mediator", None) is None:
                raise ValueError(
                    "MEDIATED causal direction requires mediator specification. "
                    f"Constraint {constraint.constraint_id}: source={constraint.source_id}, "
                    f"target={constraint.target_id}. Please specify what M mediates the "
                    "relationship (A->M->B)."
                )

        existing = web.constraints.get(constraint.constraint_id)
        if existing is not None:
            self._remove_constraint_indexes(web, existing, constraint.constraint_id)

        web.constraints[constraint.constraint_id] = constraint
        _append_unique(web._constraints_by_belief[constraint.source_id], constraint.constraint_id)
        if constraint.bidirectional:
            _append_unique(web._constraints_by_belief[constraint.target_id], constraint.constraint_id)
        else:
            _remove_all(web._constraints_by_belief[constraint.target_id], constraint.constraint_id)

        web._invalidate_entrenchment_cache()
        web._update_coherence()
        web._assert_invariants_if_enabled()

    def integrate_stub(
        self,
        web: Any,
        *,
        stub_id: str,
        theory_id: str,
        constraint_type: Any,
        constraint_strength: float,
    ) -> None:
        if stub_id not in web.beliefs:
            raise ValueError(f"Belief not found: {stub_id}")

        belief = web.beliefs[stub_id]
        if belief.status != self._contracts.status_stub:
            logger.warning("Belief %s is not a stub", stub_id)
            return

        belief.theory_id = theory_id
        belief.status = self._contracts.status_tentative

        web._stubs.discard(stub_id)
        _append_unique(web._beliefs_by_theory[theory_id], stub_id)

        theory_beliefs = [
            bid
            for bid in web._beliefs_by_theory.get(theory_id, [])
            if bid in web.beliefs and web.beliefs[bid].level == self._contracts.level_theoretical
        ]

        for theory_belief_id in theory_beliefs:
            web.add_constraint(
                self._contracts.constraint_factory(
                    constraint_id=f"c:{stub_id}:{theory_belief_id}",
                    source_id=stub_id,
                    target_id=theory_belief_id,
                    constraint_type=constraint_type,
                    strength=constraint_strength,
                )
            )

        logger.info("Integrated stub %s into theory %s", stub_id, theory_id)
        web._assert_invariants_if_enabled()

    def integrate_bridge(self, web: Any, *, bridge: Any, create_constraints: bool = True) -> dict[str, Any]:
        result = {
            "bridge_id": bridge.bridge_id,
            "constraints_created": 0,
            "tensions_created": 0,
            "coherence_impact": 0.0,
        }

        coherence_before = web._coherence_score
        if not create_constraints:
            return result

        source_beliefs = [bid for bid in bridge.source_beliefs if bid in web.beliefs]
        target_beliefs = [bid for bid in bridge.target_beliefs if bid in web.beliefs]

        if bridge.status.value == "failed":
            constraint_type = self._contracts.ctype_strong_tension
            strength = 0.9
        else:
            constraint_type = self._contracts.ctype_bridges
            strength = bridge.confidence

        for source_id in source_beliefs:
            for target_id in target_beliefs:
                constraint_id = f"c:bridge:{bridge.bridge_id}:{source_id}:{target_id}"
                if constraint_id in web.constraints:
                    continue
                web.add_constraint(
                    self._contracts.constraint_factory(
                        constraint_id=constraint_id,
                        source_id=source_id,
                        target_id=target_id,
                        constraint_type=constraint_type,
                        strength=strength,
                        bidirectional=True,
                        evidence_ids=[bridge.bridge_id],
                    )
                )
                result["constraints_created"] += 1
                if constraint_type == self._contracts.ctype_strong_tension:
                    result["tensions_created"] += 1

        if bridge.failure_record:
            for evidence_id in bridge.failure_record.disconfirming_evidence:
                if evidence_id not in web.beliefs:
                    continue
                for source_id in source_beliefs:
                    tension_id = f"c:tension:{bridge.bridge_id}:{source_id}:{evidence_id}"
                    if tension_id in web.constraints:
                        continue
                    web.add_constraint(
                        self._contracts.constraint_factory(
                            constraint_id=tension_id,
                            source_id=source_id,
                            target_id=evidence_id,
                            constraint_type=self._contracts.ctype_contradicts,
                            strength=0.8,
                            bidirectional=True,
                            evidence_ids=[bridge.bridge_id],
                        )
                    )
                    result["tensions_created"] += 1

        web._update_coherence()
        result["coherence_impact"] = web._coherence_score - coherence_before
        web.version += 1
        logger.info(
            "Integrated bridge %s: %s constraints, %s tensions",
            bridge.bridge_id,
            result["constraints_created"],
            result["tensions_created"],
        )
        web._assert_invariants_if_enabled()
        return result

    def seek_equilibrium(self, web: Any, *, max_iterations: int = 10) -> dict[str, Any]:
        request = EquilibriumRequest(max_iterations=max_iterations)
        iterations_budget = request.clamped_iterations()

        adjustments: list[dict[str, Any]] = []
        if iterations_budget <= 0:
            web._update_coherence()
            return {
                "iterations": 0,
                "final_coherence": web._coherence_score,
                "remaining_tensions": len(web._tensions),
                "adjustments": adjustments,
            }

        iterations_run = 0
        for iteration in range(iterations_budget):
            iterations_run = iteration + 1
            web._update_coherence()
            if not web._tensions:
                break

            for tension in web._tensions[:3]:
                source = web.beliefs.get(tension.get("source", ""))
                target = web.beliefs.get(tension.get("target", ""))
                if not source or not target:
                    continue

                source_entrenchment = web.get_entrenchment(source.belief_id)
                target_entrenchment = web.get_entrenchment(target.belief_id)
                choice = self._contracts.choose_adjustment_target(
                    source_id=source.belief_id,
                    target_id=target.belief_id,
                    source_entrenchment=source_entrenchment,
                    target_entrenchment=target_entrenchment,
                )
                to_adjust = web.beliefs.get(choice.belief_id)
                if not to_adjust:
                    continue

                old_credence = to_adjust.credence.value
                try:
                    adjustment = self._contracts.compute_credence_adjustment(
                        self._contracts.credence_adjustment_factory(
                            old_credence=to_adjust.credence.value,
                            old_uncertainty=to_adjust.credence.uncertainty,
                            n_supporting=to_adjust.credence.n_supporting,
                            n_contradicting=to_adjust.credence.n_contradicting,
                            n_observations=to_adjust.credence.n_observations,
                        )
                    )
                except ValueError as exc:
                    logger.warning("Equilibrium contract violation for %s: %s", to_adjust.belief_id, exc)
                    continue

                to_adjust.credence = self._contracts.credence_factory(
                    value=adjustment.new_credence,
                    uncertainty=adjustment.new_uncertainty,
                    n_supporting=adjustment.new_n_supporting,
                    n_contradicting=adjustment.new_n_contradicting,
                    n_observations=adjustment.new_n_observations,
                )
                if adjustment.should_mark_anomalous:
                    to_adjust.status = self._contracts.status_anomalous

                adjustments.append(
                    {
                        "belief_id": to_adjust.belief_id,
                        "old_credence": old_credence,
                        "new_credence": to_adjust.credence.value,
                        "reason": choice.reason,
                        "iteration": iteration,
                    }
                )

        web._update_coherence()
        result = {
            "iterations": iterations_run,
            "final_coherence": web._coherence_score,
            "remaining_tensions": len(web._tensions),
            "adjustments": adjustments,
        }
        web._assert_invariants_if_enabled()
        return result

    def add_evidence(
        self,
        web: Any,
        *,
        belief_id: str,
        content: str,
        paper_id: str,
        supports_beliefs: Optional[Mapping[str, float]] = None,
        contradicts_beliefs: Optional[Mapping[str, float]] = None,
        theory_relevance: Optional[Mapping[str, float]] = None,
        observed_temporal: Optional[Mapping[str, tuple[float, float]]] = None,
        moderator: Optional[str] = None,
        credence: float = 0.6,
    ) -> dict[str, Any]:
        try:
            evidence_input = self._contracts.build_evidence_input(
                belief_id=belief_id,
                content=content,
                paper_id=paper_id,
                supports_beliefs=supports_beliefs,
                contradicts_beliefs=contradicts_beliefs,
                theory_relevance=theory_relevance,
                observed_temporal=observed_temporal,
                moderator=moderator,
                credence=credence,
            )
        except ValueError as exc:
            logger.warning("add_evidence contract fallback activated: %s", exc)
            evidence_input = self._contracts.build_evidence_input(
                belief_id=str(belief_id or "evidence:unknown"),
                content=str(content or belief_id or "unspecified evidence"),
                paper_id=str(paper_id or "paper:unknown"),
                supports_beliefs=supports_beliefs,
                contradicts_beliefs=contradicts_beliefs,
                theory_relevance=theory_relevance,
                observed_temporal=observed_temporal,
                moderator=moderator,
                credence=credence,
            )

        updates = self._contracts.init_updates_payload(web._coherence_score)
        supports = dict(evidence_input.supports_beliefs)
        contradicts = dict(evidence_input.contradicts_beliefs)
        theory_weights = dict(evidence_input.theory_relevance)
        temporal_updates = dict(evidence_input.observed_temporal)
        evidence_id = evidence_input.belief_id
        evidence_content = evidence_input.content
        evidence_paper_id = evidence_input.paper_id
        evidence_credence = evidence_input.credence

        if evidence_id in web.beliefs:
            evidence_belief = web.beliefs[evidence_id]
            if evidence_paper_id not in evidence_belief.paper_ids:
                evidence_belief.paper_ids.append(evidence_paper_id)
            evidence_belief.credence = evidence_belief.credence.update(True, 0.6, 0.7)
        else:
            evidence_belief = self._contracts.belief_factory(
                belief_id=evidence_id,
                content=evidence_content,
                level=self._contracts.level_empirical,
                status=(
                    self._contracts.status_stub
                    if not (supports or contradicts)
                    else self._contracts.status_tentative
                ),
                credence=self._contracts.credence_factory(evidence_credence, 0.35),
                paper_ids=[evidence_paper_id],
            )
            web.add_belief(evidence_belief)

        for target_id, strength in supports.items():
            if target_id not in web.beliefs:
                continue
            target = web.beliefs[target_id]
            old_credence = target.credence.value
            target.credence = target.credence.update(True, strength, evidence_belief.credence.value)
            updates["belief_updates"].append(
                self._contracts.make_belief_update_record(
                    belief_id=target_id,
                    direction="supported",
                    old_credence=old_credence,
                    new_credence=target.credence.value,
                )
            )
            web.add_constraint(
                self._contracts.constraint_factory(
                    constraint_id=f"c:{evidence_id}:{target_id}",
                    source_id=evidence_id,
                    target_id=target_id,
                    constraint_type=self._contracts.ctype_supports,
                    strength=strength,
                )
            )
            self._contracts.ensure_theory_relevance(
                theory_weights,
                theory_id=target.theory_id,
                strength=strength,
                direction="supported",
            )

        for target_id, strength in contradicts.items():
            if target_id not in web.beliefs:
                continue
            target = web.beliefs[target_id]
            old_credence = target.credence.value
            target.credence = target.credence.update(False, strength, evidence_belief.credence.value)
            updates["belief_updates"].append(
                self._contracts.make_belief_update_record(
                    belief_id=target_id,
                    direction="contradicted",
                    old_credence=old_credence,
                    new_credence=target.credence.value,
                )
            )
            web.add_constraint(
                self._contracts.constraint_factory(
                    constraint_id=f"c:{evidence_id}:{target_id}",
                    source_id=evidence_id,
                    target_id=target_id,
                    constraint_type=self._contracts.ctype_contradicts,
                    strength=strength,
                )
            )
            self._contracts.ensure_theory_relevance(
                theory_weights,
                theory_id=target.theory_id,
                strength=strength,
                direction="contradicted",
            )

        if theory_weights:
            old_marginals = {tid: web.marginal_theory_probability(tid) for tid in web.theory_ids}
            web.update_theory_worlds(evidence_id, theory_weights)
            new_marginals = {tid: web.marginal_theory_probability(tid) for tid in web.theory_ids}
            updates["theory_world_updates"] = self._contracts.make_theory_world_update_records(
                web.theory_ids,
                old_marginals,
                new_marginals,
            )

        for param_name, (value, se) in temporal_updates.items():
            for belief in web.beliefs.values():
                if not getattr(belief, "temporal_params", None) or param_name not in belief.temporal_params:
                    continue
                old_est = belief.temporal_params[param_name].estimate
                belief.temporal_params[param_name] = belief.temporal_params[param_name].update(
                    value,
                    se,
                    weight=evidence_belief.credence.value,
                    moderator_key=moderator,
                )
                updates["temporal_updates"].append(
                    self._contracts.make_temporal_update_record(
                        belief_id=belief.belief_id,
                        parameter=param_name,
                        old_estimate=old_est,
                        new_estimate=belief.temporal_params[param_name].estimate,
                        moderator=moderator,
                    )
                )

        web._update_coherence()
        updates["coherence_after"] = web._coherence_score
        web.version += 1
        web.last_updated = datetime.now(timezone.utc)
        web._assert_invariants_if_enabled()
        return updates
