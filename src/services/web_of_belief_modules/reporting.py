"""Reporting/serialization helpers for WebOfBelief (ARCH-5d)."""

from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence

from src.services.web_of_belief_components import EpistemicLevel


def _format_belief_line(content: str, credence: float) -> str:
    if len(content) > 60:
        return f"  - [{credence:.2f}] {content[:60]}..."
    return f"  - [{credence:.2f}] {content}"


def build_web_summary(
    *,
    domain: str,
    version: int,
    coherence_score: float,
    tensions: Sequence[Mapping[str, Any]],
    beliefs_by_level: Mapping[EpistemicLevel, Sequence[Any]],
    stubs: Sequence[Any],
    n_stubs_total: int,
    theory_ids: Iterable[str],
    theory_worlds: Mapping[str, Any],
    theory_marginals: Mapping[str, float],
) -> str:
    """Generate a human-readable summary while preserving legacy output shape."""

    lines = [
        "# Web of Belief Summary",
        f"Domain: {domain}",
        f"Version: {version}",
        f"Coherence: {coherence_score:.3f}",
        f"Tensions: {len(tensions)}",
        "",
        "## Beliefs by Level",
    ]

    for level in EpistemicLevel:
        level_beliefs = list(beliefs_by_level.get(level, []))
        lines.append(f"\n### {level.value.title()} ({len(level_beliefs)})")
        for belief in sorted(level_beliefs, key=lambda item: item.credence.value, reverse=True)[:5]:
            lines.append(_format_belief_line(str(belief.content), float(belief.credence.value)))

    if n_stubs_total:
        lines.append(f"\n## Stubs (Unintegrated Findings): {n_stubs_total}")
        for stub in stubs[:5]:
            lines.append(f"  - {str(stub.content)[:60]}...")

    if theory_worlds:
        lines.append("\n## Theory Probabilities")
        for theory_id in sorted(theory_ids):
            lines.append(f"  - P({theory_id}) = {theory_marginals.get(theory_id, 0.5):.3f}")

        lines.append("\n## Joint Distribution (top 5 worlds)")
        sorted_worlds = sorted(
            theory_worlds.values(),
            key=lambda world: world.posterior,
            reverse=True,
        )[:5]
        for world in sorted_worlds:
            lines.append(f"  - {world.world_id}: P={world.posterior:.3f}")

    if tensions:
        lines.append("\n## Tensions")
        for tension in tensions[:5]:
            lines.append(f"  - {tension['source']} vs {tension['target']}")

    return "\n".join(lines)


def build_web_dict(
    *,
    domain: str,
    version: int,
    n_beliefs: int,
    n_constraints: int,
    n_stubs: int,
    coherence: float,
    n_tensions: int,
    theory_marginals: Mapping[str, float],
) -> dict[str, Any]:
    return {
        "domain": domain,
        "version": version,
        "n_beliefs": n_beliefs,
        "n_constraints": n_constraints,
        "n_stubs": n_stubs,
        "coherence": coherence,
        "n_tensions": n_tensions,
        "theory_marginals": dict(theory_marginals),
    }

