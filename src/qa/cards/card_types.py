"""
Card Type Taxonomy — Nine Types Across Three Tiers
===================================================

Defines the nine card types that ATLAS produces, organized into three tiers
by level of synthesis. Each type has a canonical color, badge text, approximate
count, and a set of required/optional tabs.

Tier A (Entity Cards):  Synthesized, multi-source entries — epistemic loci.
Tier B (Evidence Cards): Article-anchored atomic findings.
Tier C (System Cards):   How ATLAS itself works — architecture, methods, math.

See: master doc §178.2 (Nine Card Types in Three Tiers)

Author: CW (Claude/Cowork)
Date: 2026-03-04
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, FrozenSet, List, Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class CardTier(str, Enum):
    """The three tiers of knowledge artifacts."""
    A = "entity"       # Synthesized entries (T1, T1.5, T2, Molecule)
    B = "evidence"     # Article-anchored findings (T3, Competition)
    C = "system"       # System self-documentation (Layer, Method, Math)


class CardType(str, Enum):
    """The nine card types ATLAS produces.

    Naming convention: tier prefix + descriptive name.
    Values are kebab-case identifiers used in file paths and API responses.
    """
    # Tier A — Entity Cards
    T1_FRAMEWORK = "t1-framework"
    T1_5_DOMAIN_THEORY = "t1-5-domain-theory"
    T2_MECHANISM = "t2-mechanism"
    MOLECULE = "molecule"

    # Tier B — Evidence Cards
    T3_BELIEF = "t3-belief"
    COMPETITION = "competition"

    # Tier C — System Cards
    LAYER = "layer"
    METHOD = "method"
    MATH = "math"


# ---------------------------------------------------------------------------
# Card Type Metadata
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CardTypeSpec:
    """Immutable specification for a single card type.

    Encodes the structural characteristics, visual treatment, and tab
    requirements for each of the nine card types.
    """
    card_type: CardType
    tier: CardTier
    display_name: str
    badge_text: str
    badge_color: str           # Hex color for the type badge chip
    badge_text_color: str      # Text color on the badge (WCAG contrast)
    approximate_count: str     # Human-readable estimate (e.g., "10", "12,000+")
    description: str           # One-sentence description
    required_tabs: FrozenSet[str]   # Tabs that MUST be present
    optional_tabs: FrozenSet[str]   # Tabs that MAY be present
    has_mechanism_diagram: bool     # Whether mechanism tab includes a diagram
    has_evidence_forest_plot: bool  # Whether evidence tab includes forest plot
    has_design_parameters: bool     # Whether design tab includes parameter table
    has_math_layers: bool           # Whether math three-layer explanation applies
    model_allocation: str           # Default LLM: "opus", "sonnet", "gemini"


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

CARD_TYPE_REGISTRY: Dict[CardType, CardTypeSpec] = {

    # ── Tier A: Entity Cards ─────────────────────────────────────────────

    CardType.T1_FRAMEWORK: CardTypeSpec(
        card_type=CardType.T1_FRAMEWORK,
        tier=CardTier.A,
        display_name="T1 Framework Card",
        badge_text="T1",
        badge_color="#1B4332",      # Deep forest green
        badge_text_color="#FFFFFF",
        approximate_count="10",
        description=(
            "One of 10 neurally grounded framework theories that provide "
            "the highest-level theoretical architecture for ATLAS."
        ),
        required_tabs=frozenset({
            "overview", "mechanism", "evidence", "sources", "connections", "history",
        }),
        optional_tabs=frozenset({"debate", "design"}),
        has_mechanism_diagram=True,
        has_evidence_forest_plot=True,
        has_design_parameters=False,
        has_math_layers=False,
        model_allocation="opus",
    ),

    CardType.T1_5_DOMAIN_THEORY: CardTypeSpec(
        card_type=CardType.T1_5_DOMAIN_THEORY,
        tier=CardTier.A,
        display_name="T1.5 Domain Theory Card",
        badge_text="T1.5",
        badge_color="#2D6A4F",      # Medium green
        badge_text_color="#FFFFFF",
        approximate_count="13",
        description=(
            "One of 13 formally reduced domain theories that bridge T1 "
            "frameworks to T2 mechanistic templates."
        ),
        required_tabs=frozenset({
            "overview", "mechanism", "evidence", "design", "sources", "connections", "history",
        }),
        optional_tabs=frozenset({"debate"}),
        has_mechanism_diagram=True,
        has_evidence_forest_plot=True,
        has_design_parameters=True,
        has_math_layers=False,
        model_allocation="opus",
    ),

    CardType.T2_MECHANISM: CardTypeSpec(
        card_type=CardType.T2_MECHANISM,
        tier=CardTier.A,
        display_name="T2 Mechanism Card",
        badge_text="T2",
        badge_color="#40916C",      # Sage green
        badge_text_color="#FFFFFF",
        approximate_count="166 (103 calibrated, 63 scaffold)",
        description=(
            "A mechanistic template specifying a causal pathway from "
            "environmental feature through neural process to outcome."
        ),
        required_tabs=frozenset({
            "overview", "mechanism", "evidence", "design", "sources", "connections", "history",
        }),
        optional_tabs=frozenset({"debate"}),
        has_mechanism_diagram=True,
        has_evidence_forest_plot=True,
        has_design_parameters=True,
        has_math_layers=False,
        model_allocation="sonnet",  # Bulk generation; Opus for high-stakes
    ),

    CardType.MOLECULE: CardTypeSpec(
        card_type=CardType.MOLECULE,
        tier=CardTier.A,
        display_name="Molecule Card",
        badge_text="MOL",
        badge_color="#52B788",      # Light green
        badge_text_color="#1B4332",
        approximate_count="38",
        description=(
            "A latent variable bundle discovered through factor analysis "
            "on T2 template co-occurrence — the smallest recognizable "
            "theoretical unit a user would search for."
        ),
        required_tabs=frozenset({
            "overview", "mechanism", "evidence", "sources", "connections", "history",
        }),
        optional_tabs=frozenset({"design", "debate"}),
        has_mechanism_diagram=True,
        has_evidence_forest_plot=False,
        has_design_parameters=False,
        has_math_layers=False,
        model_allocation="opus",
    ),

    # ── Tier B: Evidence Cards ───────────────────────────────────────────

    CardType.T3_BELIEF: CardTypeSpec(
        card_type=CardType.T3_BELIEF,
        tier=CardTier.B,
        display_name="T3 Belief Card",
        badge_text="T3",
        badge_color="#457B9D",      # Steel blue
        badge_text_color="#FFFFFF",
        approximate_count="12,000+",
        description=(
            "An individual empirical claim from a specific study, with "
            "full provenance including sample size, design, and effect size."
        ),
        required_tabs=frozenset({
            "overview", "evidence", "connections", "history",
        }),
        optional_tabs=frozenset({"mechanism", "design", "debate", "sources"}),
        has_mechanism_diagram=False,
        has_evidence_forest_plot=False,
        has_design_parameters=True,
        has_math_layers=False,
        model_allocation="sonnet",  # Bulk; mostly template-filled
    ),

    CardType.COMPETITION: CardTypeSpec(
        card_type=CardType.COMPETITION,
        tier=CardTier.B,
        display_name="Competition Card",
        badge_text="COMP",
        badge_color="#E76F51",      # Coral/warm
        badge_text_color="#FFFFFF",
        approximate_count="~120",
        description=(
            "A contested claim where multiple accounts compete, including "
            "the debate structure, arguments for each side, and resolution "
            "scenarios."
        ),
        required_tabs=frozenset({
            "overview", "debate", "evidence", "connections", "history",
        }),
        optional_tabs=frozenset({"mechanism", "design", "sources"}),
        has_mechanism_diagram=False,
        has_evidence_forest_plot=False,
        has_design_parameters=False,
        has_math_layers=False,
        model_allocation="opus",  # Debates need careful framing
    ),

    # ── Tier C: System Cards ─────────────────────────────────────────────

    CardType.LAYER: CardTypeSpec(
        card_type=CardType.LAYER,
        tier=CardTier.C,
        display_name="Layer Card",
        badge_text="SYS",
        badge_color="#6C757D",      # Neutral gray
        badge_text_color="#FFFFFF",
        approximate_count="~12",
        description=(
            "Documents one architectural layer of the ATLAS system — its "
            "purpose, components, data flow, and integration points."
        ),
        required_tabs=frozenset({
            "overview", "mechanism", "connections", "history",
        }),
        optional_tabs=frozenset({"sources"}),
        has_mechanism_diagram=True,  # Architecture diagrams
        has_evidence_forest_plot=False,
        has_design_parameters=False,
        has_math_layers=False,
        model_allocation="sonnet",
    ),

    CardType.METHOD: CardTypeSpec(
        card_type=CardType.METHOD,
        tier=CardTier.C,
        display_name="Method Card",
        badge_text="MTH",
        badge_color="#495057",      # Dark gray
        badge_text_color="#FFFFFF",
        approximate_count="~20",
        description=(
            "Documents a specific algorithm, process, or decision procedure "
            "used by ATLAS — such as typed credence propagation or "
            "coherence computation."
        ),
        required_tabs=frozenset({
            "overview", "mechanism", "evidence", "connections", "history",
        }),
        optional_tabs=frozenset({"sources"}),
        has_mechanism_diagram=True,  # Algorithm flowcharts
        has_evidence_forest_plot=False,
        has_design_parameters=False,
        has_math_layers=True,  # Methods often have math
        model_allocation="opus",  # Methods need precision
    ),

    CardType.MATH: CardTypeSpec(
        card_type=CardType.MATH,
        tier=CardTier.C,
        display_name="Math Card",
        badge_text="∑",
        badge_color="#343A40",      # Near-black
        badge_text_color="#FFFFFF",
        approximate_count="~30",
        description=(
            "Explains a mathematical operation using the three-layer "
            "architecture: Intuition (no equations), Transparent (step-by-step), "
            "Details (full formal specification)."
        ),
        required_tabs=frozenset({
            "overview", "mechanism", "history",
        }),
        optional_tabs=frozenset({"evidence", "connections", "sources"}),
        has_mechanism_diagram=False,
        has_evidence_forest_plot=False,
        has_design_parameters=False,
        has_math_layers=True,  # This IS a math card
        model_allocation="opus",  # Math needs Opus precision
    ),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_card_type_spec(card_type: CardType) -> CardTypeSpec:
    """Look up the specification for a given card type."""
    return CARD_TYPE_REGISTRY[card_type]


def get_types_for_tier(tier: CardTier) -> List[CardType]:
    """Return all card types belonging to a given tier."""
    return [
        spec.card_type
        for spec in CARD_TYPE_REGISTRY.values()
        if spec.tier == tier
    ]


def get_types_requiring_opus() -> List[CardType]:
    """Return card types that default to Opus model allocation."""
    return [
        spec.card_type
        for spec in CARD_TYPE_REGISTRY.values()
        if spec.model_allocation == "opus"
    ]


def get_all_tabs_for_type(card_type: CardType) -> FrozenSet[str]:
    """Return the union of required and optional tabs for a card type."""
    spec = CARD_TYPE_REGISTRY[card_type]
    return spec.required_tabs | spec.optional_tabs
