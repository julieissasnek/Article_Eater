"""Experiment suggestion contracts and helpers (ARCH-5d)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Sequence

from src.services.web_of_belief_components import EpistemicLevel, ScopeConditions


@dataclass(frozen=True)
class ExperimentBeliefInput:
    """Contract snapshot for experiment suggestion logic."""

    belief_id: str
    content: str
    level: EpistemicLevel
    entrenchment: float
    scope: Optional[ScopeConditions] = None

    def validate(self) -> None:
        if not self.belief_id:
            raise ValueError("belief_id must be non-empty")
        if not self.content:
            raise ValueError("content must be non-empty")


def infer_experiment_type(
    source_level: EpistemicLevel,
    target_level: EpistemicLevel,
) -> str:
    levels = {source_level, target_level}

    if EpistemicLevel.OBSERVATIONAL in levels:
        return "measurement_study"
    if EpistemicLevel.THEORETICAL in levels and EpistemicLevel.EMPIRICAL in levels:
        return "hypothesis_test"
    if levels == {EpistemicLevel.EMPIRICAL}:
        return "replication_study"
    if EpistemicLevel.INTERMEDIATE in levels:
        return "mechanism_study"
    return "exploratory_study"


def infer_test_focus_and_hypothesis(
    source: ExperimentBeliefInput,
    target: ExperimentBeliefInput,
) -> tuple[str, str]:
    source.validate()
    target.validate()

    if source.level == EpistemicLevel.THEORETICAL and target.level == EpistemicLevel.EMPIRICAL:
        return (
            "theoretical_prediction",
            f"Test whether {source.content} correctly predicts {target.content}",
        )
    if source.level == target.level == EpistemicLevel.EMPIRICAL:
        return (
            "replication",
            f"Replicate to determine whether {source.content} or {target.content} holds",
        )
    if source.level == EpistemicLevel.INTERMEDIATE:
        return (
            "mechanism",
            f"Test the mechanism: does {source.content} explain {target.content}?",
        )
    return (
        "general",
        f"Investigate conflict between {source.belief_id} and {target.belief_id}",
    )


def identify_scope_differences(scopes: Sequence[ScopeConditions]) -> list[str]:
    differences: list[str] = []
    if len(scopes) < 2:
        return differences

    s1, s2 = scopes[0], scopes[1]
    if s1.population != s2.population:
        differences.append("population")
    if s1.setting != s2.setting:
        differences.append("setting")
    if s1.duration != s2.duration:
        differences.append("duration")
    if s1.measurement != s2.measurement:
        differences.append("measurement")
    return differences


def suggest_scope(
    source_scope: Optional[ScopeConditions],
    target_scope: Optional[ScopeConditions],
) -> dict[str, Any]:
    scopes = [scope for scope in [source_scope, target_scope] if scope is not None]
    if not scopes:
        return {
            "population": "unspecified",
            "setting": "unspecified",
            "note": "Neither belief specifies scope - consider multiple settings",
        }

    populations = [scope.population for scope in scopes if scope.population]
    settings = [scope.setting for scope in scopes if scope.setting]
    return {
        "population": populations[0] if populations else "unspecified",
        "setting": settings[0] if settings else "unspecified",
        "should_vary": identify_scope_differences(scopes),
        "note": "Test under conditions specified by both beliefs",
    }


def suggest_contested_scope(scope: Optional[ScopeConditions]) -> dict[str, str]:
    if scope:
        return {
            "population": scope.population or "unspecified",
            "setting": scope.setting or "unspecified",
            "note": "Replicate across multiple contexts to test generalizability",
        }
    return {
        "population": "unspecified",
        "setting": "unspecified",
        "note": "Scope not specified - systematic replication recommended",
    }


def estimate_resolution(
    source: ExperimentBeliefInput,
    target: ExperimentBeliefInput,
) -> dict[str, Any]:
    source.validate()
    target.validate()
    return {
        "if_source_confirmed": f"{source.belief_id} credence increases, {target.belief_id} decreases",
        "if_target_confirmed": f"{target.belief_id} credence increases, {source.belief_id} decreases",
        "if_scope_boundary": "Both may be correct in different contexts",
        "entrenchment_impact": {
            "source": source.entrenchment,
            "target": target.entrenchment,
            "easier_to_revise": source.belief_id if source.entrenchment < target.entrenchment else target.belief_id,
        },
    }

