"""Canonical mutable state container for WebOfBelief (stabilization pass)."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class WebOfBeliefState:
    """Single container for mutable WebOfBelief runtime state."""

    domain: str
    beliefs: dict[str, Any] = field(default_factory=dict)
    constraints: dict[str, Any] = field(default_factory=dict)
    theory_ids: set[str] = field(default_factory=set)
    theory_worlds: dict[str, Any] = field(default_factory=dict)
    beliefs_by_level: dict[Any, list[str]] = field(default_factory=lambda: defaultdict(list))
    beliefs_by_theory: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    constraints_by_belief: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    stubs: set[str] = field(default_factory=set)
    tensions: list[dict[str, Any]] = field(default_factory=list)
    entrenchment_cache: dict[str, float] = field(default_factory=dict)
