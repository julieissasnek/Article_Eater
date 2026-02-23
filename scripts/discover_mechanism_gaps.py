"""
Mechanism Gap Discovery via Backpropagation
===========================================

Finds missing mechanism nodes by reasoning backwards from known outcome beliefs:

    outcome_belief  ←  [constraints]  ←  stimulus_belief
                              ↑
                    GAP: no mechanism node here

Algorithm:
  1. Identify outcome beliefs (tags like 'restorative', 'stress_reduction',
     or content matching outcome vocabulary)
  2. Walk backwards through constraints to find upstream stimulus beliefs
  3. For each (stimulus, outcome) pair, check if any template causal_links
     could provide the intermediate mechanism steps
  4. Report: which (stimulus → outcome) paths are "un-explained", and which
     template(s) could fill the gap

Run:
    python3 scripts/discover_mechanism_gaps.py
    python3 scripts/discover_mechanism_gaps.py --min-strength 0.6
    python3 scripts/discover_mechanism_gaps.py --show-templates
"""

from __future__ import annotations

import argparse
import json
import sys
import os
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional

sys.path.insert(0, os.getcwd())

from src.services.web_accumulator import WebAccumulator
from src.services.web_of_belief import WebOfBelief, Belief, Constraint, ConstraintType


# =============================================================================
# OUTCOME & STIMULUS VOCABULARY
# (used to classify beliefs at the two ends of a causal chain)
# =============================================================================

OUTCOME_KEYWORDS = [
    # Restorative
    "restorative", "restoration", "recovered", "recovery",
    "attention restoration", "directed attention restoration",
    # Stress / physiological
    "stress reduction", "stress recovery", "cortisol", "physiological normalization",
    "blood pressure", "heart rate", "parasympathetic",
    # Cognitive
    "cognitive performance", "task performance", "concentration",
    "working memory", "executive function",
    # Mood / affect
    "positive affect", "mood", "wellbeing", "satisfaction",
    # Productivity
    "productivity", "performance", "efficiency",
]

STIMULUS_PREFIXES = [
    "env.", "env.ae.", "env.generic.", "env.v2a_",
]

STIMULUS_KEYWORDS = [
    "wood", "plant", "biophilia", "natural light", "daylight",
    "water", "nature view", "greenery", "indoor plant",
    "acoustic", "noise", "temperature", "spatial",
]

# Constraint types that represent causal/support relationships (follow these backwards)
CAUSAL_CONSTRAINT_TYPES = {
    ConstraintType.SUPPORTS,
    ConstraintType.EPISTEMIC_MEDIATION,
    ConstraintType.EPISTEMIC_DERIVATION,
    ConstraintType.PROPOSES_MECHANISM,
    ConstraintType.THEORETICALLY_PREDICTS,
    ConstraintType.CONFIRMS_PREDICTION,
}

# Constraint types that are mechanism-explaining (gap is filled if these exist)
MECHANISM_CONSTRAINT_TYPES = {
    ConstraintType.EPISTEMIC_MEDIATION,
    ConstraintType.PROPOSES_MECHANISM,
}


# =============================================================================
# GRAPH TRAVERSAL
# =============================================================================

def build_reverse_index(
    web: WebOfBelief,
) -> Dict[str, List[Tuple[str, Constraint]]]:
    """Map target_id → list of (source_id, constraint) feeding into it."""
    reverse: Dict[str, List[Tuple[str, Constraint]]] = defaultdict(list)
    for c in web.constraints.values():
        if c.constraint_type in CAUSAL_CONSTRAINT_TYPES:
            reverse[c.target_id].append((c.source_id, c))
            if c.bidirectional:
                reverse[c.source_id].append((c.target_id, c))
    return reverse


def build_forward_index(
    web: WebOfBelief,
) -> Dict[str, List[Tuple[str, Constraint]]]:
    """Map source_id → list of (target_id, constraint) leaving it."""
    forward: Dict[str, List[Tuple[str, Constraint]]] = defaultdict(list)
    for c in web.constraints.values():
        if c.constraint_type in CAUSAL_CONSTRAINT_TYPES:
            forward[c.source_id].append((c.target_id, c))
            if c.bidirectional:
                forward[c.target_id].append((c.source_id, c))
    return forward


def is_outcome_belief(belief: Belief) -> bool:
    content_lower = belief.content.lower()
    tags_lower = [t.lower() for t in belief.tags]
    return any(
        kw in content_lower or kw in tags_lower
        for kw in OUTCOME_KEYWORDS
    )


def is_stimulus_belief(belief: Belief) -> bool:
    bid_lower = belief.belief_id.lower()
    content_lower = belief.content.lower()
    return (
        any(bid_lower.startswith(p) for p in STIMULUS_PREFIXES)
        or any(kw in content_lower for kw in STIMULUS_KEYWORDS)
        or any(kw in bid_lower for kw in STIMULUS_KEYWORDS)
    )


def has_mechanism_on_path(
    web: WebOfBelief,
    source_id: str,
    target_id: str,
    max_depth: int = 4,
) -> bool:
    """Check if any EPISTEMIC_MEDIATION or PROPOSES_MECHANISM constraint links
    the two belief IDs within max_depth hops."""
    visited: Set[str] = set()
    queue = [(source_id, 0)]
    while queue:
        node, depth = queue.pop(0)
        if depth > max_depth:
            continue
        if node in visited:
            continue
        visited.add(node)
        for c in web.constraints.values():
            if c.source_id == node:
                if c.constraint_type in MECHANISM_CONSTRAINT_TYPES:
                    if c.target_id == target_id:
                        return True
                if c.target_id not in visited and depth + 1 <= max_depth:
                    queue.append((c.target_id, depth + 1))
    return False


def backprop_from_outcomes(
    web: WebOfBelief,
    min_strength: float = 0.5,
    max_depth: int = 4,
) -> List[Dict]:
    """
    For each outcome belief, walk backwards to find upstream stimulus beliefs.
    Report (stimulus, outcome) pairs that lack an intervening mechanism node.
    """
    reverse_idx = build_reverse_index(web)

    gaps = []
    outcome_beliefs = [
        b for b in web.beliefs.values() if is_outcome_belief(b)
    ]

    print(f"  Found {len(outcome_beliefs)} outcome beliefs to back-propagate from")

    for outcome in outcome_beliefs:
        # BFS backwards from this outcome
        visited: Set[str] = set()
        frontier = [(outcome.belief_id, 0, 1.0)]  # (id, depth, path_strength)

        while frontier:
            node_id, depth, path_strength = frontier.pop(0)
            if depth > max_depth or node_id in visited:
                continue
            visited.add(node_id)

            # Check if this upstream node is a stimulus
            if node_id in web.beliefs:
                upstream = web.beliefs[node_id]
                if is_stimulus_belief(upstream) and node_id != outcome.belief_id:
                    # Found a (stimulus → outcome) pair
                    # Check if there's already a mechanism node explaining it
                    any_mechanism = has_mechanism_on_path(
                        web, node_id, outcome.belief_id, max_depth
                    )
                    if not any_mechanism and path_strength >= min_strength:
                        gaps.append({
                            "stimulus_id": node_id,
                            "stimulus_content": upstream.content[:80],
                            "outcome_id": outcome.belief_id,
                            "outcome_content": outcome.content[:80],
                            "path_strength": path_strength,
                            "depth": depth,
                        })

            # Continue backwards
            for src_id, constraint in reverse_idx.get(node_id, []):
                if src_id not in visited:
                    new_strength = path_strength * constraint.strength
                    if new_strength >= min_strength:
                        frontier.append((src_id, depth + 1, new_strength))

    # Deduplicate by (stimulus_id, outcome_id)
    seen = set()
    unique_gaps = []
    for g in gaps:
        key = (g["stimulus_id"], g["outcome_id"])
        if key not in seen:
            seen.add(key)
            unique_gaps.append(g)

    return sorted(unique_gaps, key=lambda x: -x["path_strength"])


# =============================================================================
# TEMPLATE MATCHING
# =============================================================================

def load_templates(template_dir: Path) -> List[Dict]:
    templates = []
    for f in template_dir.glob("*.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            if d.get("dedup_status") not in ("active", None):
                continue
            if d.get("causal_links") or d.get("mechanism_chain"):
                d["_filename"] = f.name
                templates.append(d)
        except Exception:
            continue
    return templates


def match_template_to_gap(
    gap: Dict, templates: List[Dict]
) -> List[Tuple[str, str, float]]:
    """
    Return list of (template_id, name, match_score) for templates whose
    causal_links connect the gap's stimulus and outcome domains.
    """
    stim_lower = (gap["stimulus_id"] + " " + gap["stimulus_content"]).lower()
    out_lower = (gap["outcome_id"] + " " + gap["outcome_content"]).lower()

    matches = []
    for t in templates:
        tid = t.get("template_id", t.get("_filename", "?"))
        name = t.get("name", "?")[:60]
        score = 0.0

        links = t.get("causal_links", [])
        chain = t.get("mechanism_chain", [])

        # Check if any causal_link from/to fields mention stimulus or outcome keywords
        for link in links:
            frm = str(link.get("from_variable", link.get("from_entity", ""))).lower()
            to = str(link.get("to_variable", link.get("to_entity", ""))).lower()
            # Score: does the template bridge from something in stim → something in outcome?
            stim_words = {w for w in stim_lower.split() if len(w) > 4}
            out_words = {w for w in out_lower.split() if len(w) > 4}
            if any(w in frm for w in stim_words):
                score += 0.4
            if any(w in to for w in out_words):
                score += 0.4
            # Bonus: template explicitly mentions both ends
            if score >= 0.6:
                score = min(score + 0.2, 1.0)

        # Check mechanism_chain for keyword overlap
        for step in chain:
            step_lower = str(step).lower()
            if any(w in step_lower for w in stim_lower.split() if len(w) > 4):
                score += 0.1
            if any(w in step_lower for w in out_lower.split() if len(w) > 4):
                score += 0.1

        if score > 0.3:
            matches.append((tid, name, round(score, 2)))

    return sorted(matches, key=lambda x: -x[2])[:3]  # top 3


# =============================================================================
# MAIN
# =============================================================================

def main(min_strength: float = 0.5, show_templates: bool = False) -> None:
    print("Loading master web...")
    acc = WebAccumulator()
    web, _ = acc.get_master_web()
    print(f"Loaded: {len(web.beliefs)} beliefs, {len(web.constraints)} constraints")
    print()

    print("Back-propagating from outcome beliefs...")
    gaps = backprop_from_outcomes(web, min_strength=min_strength)
    print(f"\nFound {len(gaps)} unexplained (stimulus → outcome) pairs\n")

    template_dir = Path("data/templates")
    templates = load_templates(template_dir) if show_templates else []

    if not gaps:
        print("No gaps found — mechanism layer appears complete.")
        return

    # Group by outcome for readability
    by_outcome: Dict[str, List[Dict]] = defaultdict(list)
    for g in gaps:
        by_outcome[g["outcome_id"]].append(g)

    print("=" * 80)
    for outcome_id, outcome_gaps in list(by_outcome.items())[:20]:
        sample = outcome_gaps[0]
        print(f"\nOUTCOME: {outcome_id[:70]}")
        print(f"  Content: {sample['outcome_content'][:70]}...")
        print(f"  Upstream stimuli without mechanism explanation ({len(outcome_gaps)} found):")
        for g in sorted(outcome_gaps, key=lambda x: -x["path_strength"])[:5]:
            print(
                f"    [{g['path_strength']:.2f} strength, depth={g['depth']}] "
                f"{g['stimulus_id'][:60]}"
            )
            print(f"      ↳ {g['stimulus_content'][:65]}...")
            if show_templates:
                matches = match_template_to_gap(g, templates)
                if matches:
                    print(f"      Templates that could fill gap:")
                    for tid, name, score in matches:
                        print(f"        [{score:.2f}] {tid}: {name}")
    print()
    print("=" * 80)
    print(f"\nSummary: {len(gaps)} unexplained (stimulus → outcome) pairs across "
          f"{len(by_outcome)} distinct outcomes")
    print("\nNext steps:")
    print("  1. Run with --show-templates to see which template could fill each gap")
    print("  2. Add the missing mechanism steps to seed_mechanism_beliefs.py")
    print("  3. Or extend this script to auto-generate the MechanismBelief entries")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Discover missing mechanism nodes by backpropagating from outcomes"
    )
    parser.add_argument(
        "--min-strength", type=float, default=0.5,
        help="Minimum path strength to report (default: 0.5)"
    )
    parser.add_argument(
        "--show-templates", action="store_true",
        help="Also show which templates could fill each identified gap"
    )
    args = parser.parse_args()
    main(min_strength=args.min_strength, show_templates=args.show_templates)
