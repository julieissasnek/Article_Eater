"""
ATLAS Card System — Unified Knowledge Artifact Schema
======================================================

Nine card types across three tiers, unified by the Surface/Body/Iceberg
architecture defined in master doc §178.

Tier A (Entity Cards): T1Framework, T1_5DomainTheory, T2Mechanism, Molecule
Tier B (Evidence Cards): T3Belief, Competition
Tier C (System Cards): Layer, Method, Math

Every card shares the same three-layer structure:
  - Surface: what the user sees at a glance (title, badge, thermometer, direction)
  - Body: the readable entry organized as tabs (Overview, Mechanism, Evidence, etc.)
  - Iceberg: provenance, raw data, agent context, quality scores, diff archive

See: docs/master_doc_parts/PART_XXVI_section_178.md
See: docs/CARD_SYSTEM_SPECIFICATION_PLAN_2026-03-04.md

Author: CW (Claude/Cowork)
Date: 2026-03-04
"""

from src.qa.cards.card_types import CardType, CardTier, CARD_TYPE_REGISTRY
from src.qa.cards.card_schema import (
    CardSurface,
    CardTab,
    CardBody,
    IcebergSourceMap,
    IcebergAgentContext,
    IcebergQualityScores,
    CardIceberg,
    Card,
    ConfidenceLevel,
    Direction,
    Staleness,
    UserType,
    create_card,
    make_card_id,
)
from src.qa.cards.tab_config import (
    TAB_DEFINITIONS,
    USER_TYPE_TAB_ORDER,
    get_tabs_for_card_type,
    get_tab_order_for_user,
    TabDefinition,
)
from src.qa.cards.staleness import (
    StalenessLedgerEntry,
    StalenessLedger,
    compute_staleness_score,
    StalenessConfig,
)

__all__ = [
    # Types
    "CardType",
    "CardTier",
    "CARD_TYPE_REGISTRY",
    # Schema
    "CardSurface",
    "CardTab",
    "CardBody",
    "IcebergSourceMap",
    "IcebergAgentContext",
    "IcebergQualityScores",
    "CardIceberg",
    "Card",
    "ConfidenceLevel",
    "Direction",
    "Staleness",
    "UserType",
    # Factory functions
    "create_card",
    "make_card_id",
    # Tabs
    "TAB_DEFINITIONS",
    "USER_TYPE_TAB_ORDER",
    "get_tabs_for_card_type",
    "get_tab_order_for_user",
    "TabDefinition",
    # Staleness
    "StalenessLedgerEntry",
    "StalenessLedger",
    "compute_staleness_score",
    "StalenessConfig",
]
