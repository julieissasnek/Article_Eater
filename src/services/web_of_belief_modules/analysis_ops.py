"""Analysis, query, experiment, and reporting orchestration for WebOfBelief."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import logging
from typing import Any, Callable, Optional, Sequence

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AnalysisContracts:
    """Dependency contract for analysis/query orchestration."""

    credence_factory: Callable[..., Any]
    centrality_input_factory: Callable[..., Any]
    compute_centrality: Callable[..., float]
    epistemic_value_input_factory: Callable[..., Any]
    compute_epistemic_value: Callable[..., float]
    belief_value_record_factory: Callable[..., Any]
    sort_value_records: Callable[..., Sequence[Any]]
    compute_independence_score: Callable[..., dict[str, float]]
    experiment_belief_input_factory: Callable[..., Any]
    infer_experiment_type: Callable[..., str]
    infer_test_focus_and_hypothesis: Callable[..., tuple[str, str]]
    suggest_scope: Callable[..., dict[str, Any]]
    suggest_contested_scope: Callable[..., dict[str, Any]]
    identify_scope_differences: Callable[..., list[str]]
    estimate_resolution: Callable[..., dict[str, Any]]
    epistemic_levels: Sequence[Any]
    level_theoretical: Any
    level_empirical: Any
    level_observational: Any
    status_anomalous: Any


class WebAnalysisOperations:
    """Extracted read/orchestration operations for WebOfBelief."""

    def __init__(self, contracts: AnalysisContracts):
        self._contracts = contracts

    def belief_centrality(self, web: Any, belief_id: str) -> float:
        if belief_id not in web.beliefs:
            return 0.0

        constraint_count = 0
        for constraint in web.constraints.values():
            if constraint.source_id == belief_id or constraint.target_id == belief_id:
                constraint_count += 1

        payload = self._contracts.centrality_input_factory(
            belief_id=belief_id,
            constraint_count=constraint_count,
            total_beliefs=len(web.beliefs),
        )
        try:
            return self._contracts.compute_centrality(payload)
        except ValueError as exc:
            logger.warning("Centrality contract violation for %s: %s", belief_id, exc)
            return 0.0

    def belief_sensitivity(self, web: Any, belief_id: str, delta: float = 0.1) -> float:
        if belief_id not in web.beliefs:
            return 0.0
        if delta <= 0:
            logger.warning("belief_sensitivity received non-positive delta: %s", delta)
            return 0.0

        belief = web.beliefs[belief_id]
        original_uncertainty = belief.credence.uncertainty
        original_n_supporting = belief.credence.n_supporting
        original_n_contradicting = belief.credence.n_contradicting
        original_n_observations = belief.credence.n_observations
        original_credence = belief.credence.value
        original_coherence = web._coherence_score

        if original_credence + delta <= 1.0:
            test_credence = original_credence + delta
        else:
            test_credence = original_credence - delta

        belief.credence = self._contracts.credence_factory(
            value=test_credence,
            uncertainty=original_uncertainty,
            n_supporting=original_n_supporting,
            n_contradicting=original_n_contradicting,
            n_observations=original_n_observations,
        )
        web._update_coherence()
        new_coherence = web._coherence_score

        belief.credence = self._contracts.credence_factory(
            value=original_credence,
            uncertainty=original_uncertainty,
            n_supporting=original_n_supporting,
            n_contradicting=original_n_contradicting,
            n_observations=original_n_observations,
        )
        web._update_coherence()

        sensitivity = abs(new_coherence - original_coherence) / delta
        return min(1.0, sensitivity)

    def belief_value(self, web: Any, belief_id: str, centrality_weight: float = 0.5) -> float:
        centrality = self.belief_centrality(web, belief_id)
        sensitivity = self.belief_sensitivity(web, belief_id)

        normalized_weight = max(0.0, min(1.0, centrality_weight))
        if normalized_weight != centrality_weight:
            logger.warning(
                "belief_value clamped centrality_weight %.3f -> %.3f",
                centrality_weight,
                normalized_weight,
            )

        try:
            return self._contracts.compute_epistemic_value(
                self._contracts.epistemic_value_input_factory(
                    centrality=centrality,
                    sensitivity=sensitivity,
                    centrality_weight=normalized_weight,
                )
            )
        except ValueError as exc:
            logger.warning("Value metric contract violation for %s: %s", belief_id, exc)
            return 0.0

    def beliefs_by_value(
        self,
        web: Any,
        top_n: Optional[int] = None,
    ) -> list[tuple[str, float, float, float]]:
        records = []
        for belief_id in web.beliefs:
            centrality = self.belief_centrality(web, belief_id)
            sensitivity = self.belief_sensitivity(web, belief_id)
            value = self._contracts.compute_epistemic_value(
                self._contracts.epistemic_value_input_factory(
                    centrality=centrality,
                    sensitivity=sensitivity,
                    centrality_weight=0.5,
                )
            )
            records.append(
                self._contracts.belief_value_record_factory(
                    belief_id=belief_id,
                    value=value,
                    centrality=centrality,
                    sensitivity=sensitivity,
                )
            )

        ranked = self._contracts.sort_value_records(records, top_n=top_n)
        return [record.to_tuple() for record in ranked]

    def compute_independence_score(
        self,
        web: Any,
        belief_ids: Optional[list[str]] = None,
    ) -> dict[str, float]:
        ids = belief_ids or list(web.beliefs.keys())
        records: list[dict[str, str | None]] = []
        for belief_id in ids:
            belief = web.beliefs.get(belief_id)
            if not belief:
                continue
            records.append(
                {
                    "lab": belief.source_lab or belief.source_institution,
                    "method": belief.study_method or belief.source_depth.value,
                    "population": belief.scope_population,
                }
            )
        return self._contracts.compute_independence_score(records)

    def high_value_beliefs(self, web: Any, threshold: float = 0.5) -> list[dict[str, Any]]:
        results = []
        for belief_id, value, centrality, sensitivity in self.beliefs_by_value(web):
            if value < threshold:
                break
            belief = web.beliefs[belief_id]
            results.append(
                {
                    "belief_id": belief_id,
                    "content": belief.content,
                    "level": belief.level.value,
                    "credence": belief.credence.value,
                    "entrenchment": belief.entrenchment,
                    "value": value,
                    "centrality": centrality,
                    "sensitivity": sensitivity,
                    "inference_type": belief.inference_type.value,
                    "belief_kind": belief.belief_kind.value,
                }
            )
        return results

    def to_experiment_input(self, belief: Any) -> Any:
        return self._contracts.experiment_belief_input_factory(
            belief_id=belief.belief_id,
            content=belief.content or belief.belief_id,
            level=belief.level,
            entrenchment=belief.entrenchment,
            scope=belief.scope,
        )

    def infer_experiment_type(self, source: Any, target: Any) -> str:
        return self._contracts.infer_experiment_type(source.level, target.level)

    def suggest_scope(self, source: Any, target: Any) -> dict[str, Any]:
        return self._contracts.suggest_scope(source.scope, target.scope)

    def suggest_contested_scope(self, belief: Any) -> dict[str, Any]:
        return self._contracts.suggest_contested_scope(belief.scope)

    def identify_scope_differences(self, scopes: list[Any]) -> list[str]:
        return self._contracts.identify_scope_differences(scopes)

    def estimate_resolution(self, source: Any, target: Any) -> dict[str, Any]:
        return self._contracts.estimate_resolution(
            self.to_experiment_input(source),
            self.to_experiment_input(target),
        )

    def generate_experiment_suggestion(
        self,
        web: Any,
        source: Any,
        target: Any,
        tension: dict[str, Any],
    ) -> Optional[dict[str, Any]]:
        source_input = self.to_experiment_input(source)
        target_input = self.to_experiment_input(target)
        exp_type = self._contracts.infer_experiment_type(source_input.level, target_input.level)

        try:
            test_focus, hypothesis = self._contracts.infer_test_focus_and_hypothesis(
                source_input,
                target_input,
            )
        except ValueError as exc:
            logger.warning(
                "Experiment focus contract violation for %s/%s: %s",
                source.belief_id,
                target.belief_id,
                exc,
            )
            test_focus = "general"
            hypothesis = f"Investigate conflict between {source.belief_id} and {target.belief_id}"

        priority = max(
            self.belief_value(web, source.belief_id),
            self.belief_value(web, target.belief_id),
        )
        scope_suggestion = self._contracts.suggest_scope(source.scope, target.scope)

        return {
            "experiment_id": f"exp:tension:{source.belief_id}:{target.belief_id}",
            "type": exp_type,
            "tension_type": tension.get("type", "unknown"),
            "test_focus": test_focus,
            "hypothesis": hypothesis,
            "source_belief": {
                "id": source.belief_id,
                "content": source.content,
                "credence": source.credence.value,
                "level": source.level.value,
            },
            "target_belief": {
                "id": target.belief_id,
                "content": target.content,
                "credence": target.credence.value,
                "level": target.level.value,
            },
            "priority": priority,
            "scope_suggestion": scope_suggestion,
            "expected_resolution": self._contracts.estimate_resolution(
                source_input,
                target_input,
            ),
        }

    def generate_contested_experiment(self, web: Any, belief: Any) -> Optional[dict[str, Any]]:
        credence_range = belief.credence_range()
        return {
            "experiment_id": f"exp:contested:{belief.belief_id}",
            "type": "replication_study",
            "tension_type": "credence_oscillation",
            "test_focus": "replication",
            "hypothesis": f"Determine stable credence for: {belief.content}",
            "source_belief": {
                "id": belief.belief_id,
                "content": belief.content,
                "credence": belief.credence.value,
                "credence_range": credence_range,
                "level": belief.level.value,
            },
            "target_belief": None,
            "priority": self.belief_value(web, belief.belief_id),
            "scope_suggestion": self._contracts.suggest_contested_scope(belief.scope),
            "expected_resolution": {
                "if_confirmed": f"Credence stabilizes above {credence_range[1]:.2f}",
                "if_refuted": f"Credence stabilizes below {credence_range[0]:.2f}",
                "uncertainty_reduction": abs(credence_range[1] - credence_range[0]),
            },
        }

    def suggest_experiments(self, web: Any, max_suggestions: int = 5) -> list[dict[str, Any]]:
        web._update_coherence()
        suggestions: list[dict[str, Any]] = []

        for tension in web._tensions[:max_suggestions]:
            source = web.beliefs.get(tension["source"])
            target = web.beliefs.get(tension["target"])
            if not source or not target:
                continue
            suggestion = self.generate_experiment_suggestion(web, source, target, tension)
            if suggestion:
                suggestions.append(suggestion)

        contested = [belief for belief in web.beliefs.values() if belief.contested]
        for belief in contested[: max_suggestions - len(suggestions)]:
            if len(suggestions) >= max_suggestions:
                break
            suggestion = self.generate_contested_experiment(web, belief)
            if suggestion:
                suggestions.append(suggestion)

        return suggestions

    def generate_research_directions(self, web: Any) -> list[dict[str, str]]:
        directions: list[dict[str, str]] = []
        tension_types = defaultdict(int)
        for tension in web._tensions:
            tension_types[tension.get("type", "unknown")] += 1

        if tension_types["contradiction_tension"] > 0:
            directions.append(
                {
                    "direction": "Resolve contradictory findings",
                    "rationale": (
                        f"{tension_types['contradiction_tension']} pairs of "
                        "high-credence beliefs contradict each other"
                    ),
                    "approach": "Systematic replication with scope variation",
                }
            )

        if tension_types["bridge_failure_tension"] > 0:
            directions.append(
                {
                    "direction": "Strengthen knowledge transfer",
                    "rationale": (
                        f"{tension_types['bridge_failure_tension']} bridge "
                        "relationships have failed"
                    ),
                    "approach": "Test enabling conditions for knowledge transfer",
                }
            )

        levels = defaultdict(int)
        for belief in web.beliefs.values():
            levels[belief.level] += 1

        if levels[self._contracts.level_theoretical] > levels[self._contracts.level_empirical]:
            directions.append(
                {
                    "direction": "More empirical testing needed",
                    "rationale": "More theoretical than empirical beliefs",
                    "approach": "Design experiments to test theoretical predictions",
                }
            )

        if levels[self._contracts.level_observational] == 0:
            directions.append(
                {
                    "direction": "Add observational grounding",
                    "rationale": "No observational-level beliefs",
                    "approach": "Conduct direct measurement studies",
                }
            )

        return directions

    def get_research_priorities(self, web: Any, top_n: int = 10) -> dict[str, Any]:
        web._update_coherence()
        return {
            "web_coherence": web._coherence_score,
            "n_tensions": len(web._tensions),
            "n_contested": sum(1 for belief in web.beliefs.values() if belief.contested),
            "suggested_experiments": self.suggest_experiments(web, max_suggestions=top_n),
            "high_value_beliefs": self.high_value_beliefs(web, threshold=0.3)[:top_n],
            "research_directions": self.generate_research_directions(web),
        }

    def get_stubs(self, web: Any) -> list[Any]:
        return [web.beliefs[belief_id] for belief_id in web._stubs if belief_id in web.beliefs]

    def get_anomalies(self, web: Any) -> list[Any]:
        return [
            belief
            for belief in web.beliefs.values()
            if belief.status == self._contracts.status_anomalous
        ]

    def get_beliefs_by_level(self, web: Any, level: Any) -> list[Any]:
        return [
            web.beliefs[belief_id]
            for belief_id in web._beliefs_by_level.get(level, [])
            if belief_id in web.beliefs
        ]

    def get_beliefs_for_theory(self, web: Any, theory_id: str) -> list[Any]:
        return [
            web.beliefs[belief_id]
            for belief_id in web._beliefs_by_theory.get(theory_id, [])
            if belief_id in web.beliefs
        ]

    def summary(self, web: Any) -> str:
        beliefs_by_level = {
            level: self.get_beliefs_by_level(web, level)
            for level in self._contracts.epistemic_levels
        }
        stubs = [
            web.beliefs[stub_id]
            for stub_id in list(web._stubs)[:5]
            if stub_id in web.beliefs
        ]
        theory_marginals = {
            theory_id: web.marginal_theory_probability(theory_id) for theory_id in web.theory_ids
        }
        return web._engines.reporting.summary(
            domain=web.domain,
            version=web.version,
            coherence_score=web._coherence_score,
            tensions=web._tensions,
            beliefs_by_level=beliefs_by_level,
            stubs=stubs,
            n_stubs_total=len(web._stubs),
            theory_ids=web.theory_ids,
            theory_worlds=web.theory_worlds,
            theory_marginals=theory_marginals,
        )

    def to_dict(self, web: Any) -> dict[str, Any]:
        theory_marginals = {
            theory_id: web.marginal_theory_probability(theory_id) for theory_id in web.theory_ids
        }
        return web._engines.reporting.to_dict(
            domain=web.domain,
            version=web.version,
            n_beliefs=len(web.beliefs),
            n_constraints=len(web.constraints),
            n_stubs=len(web._stubs),
            coherence=web._coherence_score,
            n_tensions=len(web._tensions),
            theory_marginals=theory_marginals,
        )
