"""
Tab Configuration — Definitions, Ordering, and User-Type Adaptation
====================================================================

Defines the 7 possible tabs that can appear on a card body, their
content requirements, and how they are ordered and filtered for
different user types.

Tab Architecture (per §178.3.2):
  Overview    — 2-3 paragraph prose summary (Zone 1 committed prose)
  Mechanism   — Causal pathway: env feature → neural process → outcome
  Evidence    — Quantitative summary: effect sizes, CIs, replication
  Design      — Actionable implications: design parameters with ranges
  Connections — Relationships to other cards in the knowledge graph
  Debate      — Competing accounts, unresolved tensions, active frontiers
  History     — Version history, regeneration log, diff view

See: docs/master_doc_parts/PART_XXVI_section_178.md §178.3.2
See: docs/CARD_SYSTEM_SPECIFICATION_PLAN_2026-03-04.md §3.2

Author: CW (Claude/Cowork)
Date: 2026-03-04
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Optional

from src.qa.cards.card_types import CardType, CARD_TYPE_REGISTRY


# ---------------------------------------------------------------------------
# Tab Definitions
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TabDefinition:
    """Immutable specification for one tab type."""
    name: str                   # Machine name (lowercase, used as key)
    display_name: str           # Human-readable label
    description: str            # What this tab contains
    primary_user: str           # Which user type this tab primarily serves
    min_prose_words: int        # Minimum word count for prose content
    requires_visual: bool       # Whether at least one figure is expected
    visual_type: Optional[str]  # What kind of visual (diagram, plot, table, etc.)


TAB_DEFINITIONS: Dict[str, TabDefinition] = {
    "overview": TabDefinition(
        name="overview",
        display_name="Overview",
        description=(
            "2-3 paragraph prose summary (Zone 1 committed prose). "
            "Written at prose health ≥ 6.5. Cites key references inline. "
            "Addresses the 'what and why' question."
        ),
        primary_user="all",
        min_prose_words=150,
        requires_visual=False,
        visual_type=None,
    ),
    "mechanism": TabDefinition(
        name="mechanism",
        display_name="Mechanism",
        description=(
            "The causal pathway. For T2 cards: full mechanism chain "
            "(environmental feature → neural process → outcome). For T1/T1.5: "
            "the theoretical architecture and its neural implementation."
        ),
        primary_user="researcher",
        min_prose_words=200,
        requires_visual=True,
        visual_type="mechanism_diagram",
    ),
    "evidence": TabDefinition(
        name="evidence",
        display_name="Evidence",
        description=(
            "Quantitative evidence summary. Effect sizes with CIs. Study count, "
            "replication status, population scope. Meta-analytic forest plot or "
            "evidence weight chart."
        ),
        primary_user="researcher",
        min_prose_words=100,
        requires_visual=True,
        visual_type="forest_plot_or_evidence_chart",
    ),
    "design": TabDefinition(
        name="design",
        display_name="Design",
        description=(
            "Actionable implications. For T2: specific design parameters with "
            "ranges. For T1/T1.5: broad design principles. For T3: what this "
            "finding means for practice."
        ),
        primary_user="designer",
        min_prose_words=100,
        requires_visual=True,
        visual_type="design_parameter_table",
    ),
    "connections": TabDefinition(
        name="connections",
        display_name="Connections",
        description=(
            "How this card relates to others. Parent/child in tier hierarchy. "
            "Cross-template interactions. Competition relationships. Molecule "
            "membership. Network neighborhood diagram."
        ),
        primary_user="researcher",
        min_prose_words=80,
        requires_visual=True,
        visual_type="network_neighborhood_diagram",
    ),
    "debate": TabDefinition(
        name="debate",
        display_name="Debate",
        description=(
            "Competing accounts, unresolved tensions, active frontiers. "
            "Who disagrees and why. What evidence would resolve the debate."
        ),
        primary_user="researcher",
        min_prose_words=150,
        requires_visual=True,
        visual_type="argument_map",
    ),
    "history": TabDefinition(
        name="history",
        display_name="History",
        description=(
            "Version history of this card. When created, when last regenerated, "
            "what changed. Diff view showing previous vs. current prose."
        ),
        primary_user="all",
        min_prose_words=0,  # History is mostly structured data, not prose
        requires_visual=False,
        visual_type=None,
    ),
    "sources": TabDefinition(
        name="sources",
        display_name="Sources",
        description=(
            "Per-paper method details, stimulus descriptions, and experimental materials. "
            "Shows what each contributing study actually did. Sample sizes, populations, "
            "measurement instruments, and visual stimuli are documented here."
        ),
        primary_user="researcher",
        min_prose_words=100,
        requires_visual=False,
        visual_type=None,
    ),
}


# ---------------------------------------------------------------------------
# User-Type Tab Ordering
# ---------------------------------------------------------------------------

# Per §178.3.2: tab order and default-open state varies by user type.
# The first tab in each list is the default-open tab.

USER_TYPE_TAB_ORDER: Dict[str, List[str]] = {
    "researcher": [
        "overview", "evidence", "mechanism", "sources", "connections",
        "debate", "design", "history",
    ],
    "designer": [
        "design", "overview", "mechanism", "evidence",
        "connections", "sources", "history",
    ],
    "clinician": [
        "overview", "design", "evidence", "mechanism",
        "connections", "history",
    ],
    "policymaker": [
        "overview", "design", "evidence", "history",
    ],
    "student": [
        "overview", "mechanism", "evidence", "design",
        "connections", "sources", "debate", "history",
    ],
}

# Tabs hidden by default for each user type (can still be accessed)
USER_TYPE_HIDDEN_TABS: Dict[str, FrozenSet[str]] = {
    "researcher": frozenset(),  # Sees everything
    "designer": frozenset({"debate"}),  # Unless competition exists
    "clinician": frozenset({"debate"}),
    "policymaker": frozenset({"mechanism", "connections", "debate"}),
    "student": frozenset(),  # Sees everything, different order
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_tabs_for_card_type(card_type: CardType) -> Dict[str, TabDefinition]:
    """Return the tab definitions applicable to a card type.

    Includes both required and optional tabs from the card type spec.
    """
    spec = CARD_TYPE_REGISTRY[card_type]
    all_tab_names = spec.required_tabs | spec.optional_tabs
    return {
        name: TAB_DEFINITIONS[name]
        for name in all_tab_names
        if name in TAB_DEFINITIONS
    }


def get_tab_order_for_user(
    user_type: str,
    card_type: CardType,
    has_competition: bool = False,
) -> List[str]:
    """Return the ordered list of visible tabs for a user viewing a card.

    Filters the user's preferred tab order to only include tabs that
    exist on this card type. If the user type hides the debate tab but
    the card has active competition, the debate tab is shown anyway.

    Args:
        user_type: One of "researcher", "designer", "clinician",
                   "policymaker", "student"
        card_type: The card type being viewed
        has_competition: Whether the card has active competing accounts

    Returns:
        Ordered list of tab names to display
    """
    # Get the user's preferred order
    order = USER_TYPE_TAB_ORDER.get(user_type, USER_TYPE_TAB_ORDER["researcher"])

    # Get tabs available on this card type
    spec = CARD_TYPE_REGISTRY[card_type]
    available = spec.required_tabs | spec.optional_tabs

    # Get tabs hidden for this user
    hidden = USER_TYPE_HIDDEN_TABS.get(user_type, frozenset())

    # If debate is hidden but competition exists, un-hide it
    if has_competition and "debate" in hidden:
        hidden = hidden - {"debate"}

    # Filter to available and not hidden, preserving order
    result = [tab for tab in order if tab in available and tab not in hidden]

    # Add any available tabs not in the user's order list (at end)
    for tab in sorted(available):
        if tab not in result and tab not in hidden:
            result.append(tab)

    return result


def get_required_tabs(card_type: CardType) -> FrozenSet[str]:
    """Return only the required (non-optional) tabs for a card type."""
    return CARD_TYPE_REGISTRY[card_type].required_tabs
