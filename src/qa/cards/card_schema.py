"""
Card Schema — The Universal Surface/Body/Iceberg Architecture
==============================================================

Every card in ATLAS, regardless of type, follows the same three-layer
structure defined in master doc §178.3:

  Surface: What the user sees at a glance — title, type badge, confidence
           thermometer, direction arrow, evidence count, staleness dot.

  Body:    The readable entry — organized as tabs (Overview, Mechanism,
           Evidence, Design, Connections, Debate, History). Tab order and
           visibility depend on user type.

  Iceberg: What lies beneath — source map, internal/external references,
           raw data, staleness ledger, agent context, quality scores,
           diff archive. Essential for regeneration, audit, and deepening.

The Card dataclass is the canonical in-memory representation of a knowledge
artifact. It serializes to/from JSON for persistence in data/qa_cache/ and
data/materialized_views/answer_cards/.

See: docs/master_doc_parts/PART_XXVI_section_178.md
See: docs/CARD_SYSTEM_SPECIFICATION_PLAN_2026-03-04.md §3

Author: CW (Claude/Cowork)
Date: 2026-03-04
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.qa.cards.card_types import CardType, CardTier


# ---------------------------------------------------------------------------
# Shared Enumerations
# ---------------------------------------------------------------------------

class ConfidenceLevel(str, Enum):
    """Four-level confidence classification per QA_ANSWER_NORMS §4.

    Maps to the credence range ω (Bayesian posterior weight).
    """
    HIGH = "high"             # ω ≥ 0.75 — strong convergent evidence
    MOD_HIGH = "mod_high"     # 0.60 ≤ ω < 0.75 — good evidence, some gaps
    MODERATE = "moderate"     # 0.40 ≤ ω < 0.60 — mixed or limited evidence
    LOW = "low"               # ω < 0.40 — sparse, conflicting, or weak evidence


class Direction(str, Enum):
    """Directional consensus of the findings backing this card."""
    INCREASE = "increase"     # ↑ Environmental feature increases outcome
    DECREASE = "decrease"     # ↓ Environmental feature decreases outcome
    MIXED = "mixed"           # ↔ Evidence points both ways
    NO_EFFECT = "no_effect"   # ∅ No significant effect detected
    NA = "na"                 # Not applicable (system cards, math cards)


class Staleness(str, Enum):
    """Three-level staleness indicator per §173.4 staleness score."""
    FRESH = "fresh"           # Score < 0.20 — recently generated/reviewed
    AGING = "aging"           # 0.20 ≤ score < 0.40 — some evidence has changed
    STALE = "stale"           # Score ≥ 0.40 — regeneration recommended


class UserType(str, Enum):
    """User types that affect tab order and rendering depth."""
    RESEARCHER = "researcher"
    DESIGNER = "designer"
    CLINICIAN = "clinician"
    POLICYMAKER = "policymaker"
    STUDENT = "student"


# ---------------------------------------------------------------------------
# Confidence Thermometer Colors (WCAG 2.1 AA compliant)
# ---------------------------------------------------------------------------

CONFIDENCE_COLORS: Dict[ConfidenceLevel, str] = {
    ConfidenceLevel.HIGH: "#2D6A4F",       # Deep green
    ConfidenceLevel.MOD_HIGH: "#40916C",   # Medium green
    ConfidenceLevel.MODERATE: "#E9C46A",   # Amber/gold
    ConfidenceLevel.LOW: "#E76F51",        # Coral/warm red
}

STALENESS_COLORS: Dict[Staleness, str] = {
    Staleness.FRESH: "#2D6A4F",    # Green dot
    Staleness.AGING: "#E9C46A",    # Amber dot
    Staleness.STALE: "#E76F51",    # Red dot
}


# ---------------------------------------------------------------------------
# Surface Layer
# ---------------------------------------------------------------------------

@dataclass
class CardSurface:
    """What the user sees before clicking in — the card face.

    Must communicate essential identity and epistemic status at a glance.
    Per §178.3.1, the surface includes:
      - Title (assertion-evidence headline, not a topic label)
      - Type badge (color-coded chip)
      - Confidence thermometer (4-level with ω score)
      - Direction arrow
      - Evidence count (N findings from M papers)
      - Staleness indicator (green/amber/red dot)
      - Key visual (thumbnail, expandable)
    """
    title: str                          # Assertion-evidence headline
    card_type: CardType                 # Which of the 9 types
    confidence_level: ConfidenceLevel   # HIGH/MOD_HIGH/MODERATE/LOW
    confidence_omega: Optional[float]   # ω score (0.0–1.0), None for system cards
    confidence_label: str               # e.g., "Mod-High (ω = 0.62)"
    direction: Direction                # ↑ / ↓ / ↔ / ∅ / NA
    n_findings: int                     # Number of backing findings
    n_papers: int                       # Number of distinct papers
    staleness: Staleness                # Fresh / Aging / Stale
    staleness_score: float              # Numeric score (0.0–1.0)
    key_visual_path: Optional[str]      # Path to thumbnail image, if any
    last_generated: str                 # ISO 8601 timestamp

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "card_type": self.card_type.value,
            "confidence_level": self.confidence_level.value,
            "confidence_omega": self.confidence_omega,
            "confidence_label": self.confidence_label,
            "confidence_color": CONFIDENCE_COLORS[self.confidence_level],
            "direction": self.direction.value,
            "n_findings": self.n_findings,
            "n_papers": self.n_papers,
            "staleness": self.staleness.value,
            "staleness_score": round(self.staleness_score, 3),
            "staleness_color": STALENESS_COLORS[self.staleness],
            "key_visual_path": self.key_visual_path,
            "last_generated": self.last_generated,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CardSurface:
        return cls(
            title=data["title"],
            card_type=CardType(data["card_type"]),
            confidence_level=ConfidenceLevel(data["confidence_level"]),
            confidence_omega=data.get("confidence_omega"),
            confidence_label=data.get("confidence_label", ""),
            direction=Direction(data.get("direction", "na")),
            n_findings=data.get("n_findings", 0),
            n_papers=data.get("n_papers", 0),
            staleness=Staleness(data.get("staleness", "fresh")),
            staleness_score=data.get("staleness_score", 0.0),
            key_visual_path=data.get("key_visual_path"),
            last_generated=data.get("last_generated", ""),
        )


# ---------------------------------------------------------------------------
# Body Layer — Tabs
# ---------------------------------------------------------------------------

@dataclass
class CardTab:
    """A single tab in the card body.

    Each tab has a name (matching TAB_DEFINITIONS keys), prose content,
    and optional structured data (figures, tables, parameter ranges).
    """
    tab_name: str              # e.g., "overview", "mechanism", "evidence"
    prose: str                 # The main text content (markdown)
    prose_health_score: Optional[float] = None  # Sword Writer's Diet score
    figures: List[Dict[str, Any]] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    structured_data: Optional[Dict[str, Any]] = None  # Tab-specific extras

    # Math card specific: three-layer explanation
    math_intuition: Optional[str] = None       # Layer 1: no equations
    math_transparent: Optional[str] = None     # Layer 2: step-by-step
    math_details: Optional[str] = None         # Layer 3: formal spec

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "tab_name": self.tab_name,
            "prose": self.prose,
        }
        if self.prose_health_score is not None:
            result["prose_health_score"] = round(self.prose_health_score, 2)
        if self.figures:
            result["figures"] = self.figures
        if self.tables:
            result["tables"] = self.tables
        if self.structured_data:
            result["structured_data"] = self.structured_data
        if self.math_intuition:
            result["math_intuition"] = self.math_intuition
        if self.math_transparent:
            result["math_transparent"] = self.math_transparent
        if self.math_details:
            result["math_details"] = self.math_details
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CardTab:
        return cls(
            tab_name=data["tab_name"],
            prose=data.get("prose", ""),
            prose_health_score=data.get("prose_health_score"),
            figures=data.get("figures", []),
            tables=data.get("tables", []),
            structured_data=data.get("structured_data"),
            math_intuition=data.get("math_intuition"),
            math_transparent=data.get("math_transparent"),
            math_details=data.get("math_details"),
        )


@dataclass
class CardBody:
    """The main content layer — organized as tabs.

    Per §178.3.2, the body contains 7 possible tabs:
      Overview, Mechanism, Evidence, Design, Connections, Debate, History

    Not all tabs are present on all card types — see card_types.py for
    which tabs are required vs optional for each type.
    """
    tabs: Dict[str, CardTab]  # tab_name → CardTab

    def get_tab(self, tab_name: str) -> Optional[CardTab]:
        """Retrieve a tab by name, or None if not present."""
        return self.tabs.get(tab_name)

    def has_tab(self, tab_name: str) -> bool:
        """Check whether a tab exists on this card."""
        return tab_name in self.tabs

    @property
    def tab_names(self) -> List[str]:
        """Return list of tab names present on this card."""
        return list(self.tabs.keys())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tabs": {
                name: tab.to_dict() for name, tab in self.tabs.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CardBody:
        tabs_data = data.get("tabs", {})
        tabs = {
            name: CardTab.from_dict(tab_data)
            for name, tab_data in tabs_data.items()
        }
        return cls(tabs=tabs)


# ---------------------------------------------------------------------------
# Iceberg Layer — Provenance, Raw Data, Quality, Agent Context
# ---------------------------------------------------------------------------

@dataclass
class IcebergSourceMap:
    """Zone 3 dependency graph — which source cards back this card.

    The source map enables provenance audit and regeneration triggering.
    When any source changes, the staleness score increases.
    """
    source_card_ids: List[str] = field(default_factory=list)
    template_ids: List[str] = field(default_factory=list)
    framework_ids: List[str] = field(default_factory=list)
    molecule_ids: List[str] = field(default_factory=list)
    finding_ids: List[str] = field(default_factory=list)
    paper_dois: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_card_ids": self.source_card_ids,
            "template_ids": self.template_ids,
            "framework_ids": self.framework_ids,
            "molecule_ids": self.molecule_ids,
            "finding_ids": self.finding_ids,
            "paper_dois": self.paper_dois,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> IcebergSourceMap:
        return cls(
            source_card_ids=data.get("source_card_ids", []),
            template_ids=data.get("template_ids", []),
            framework_ids=data.get("framework_ids", []),
            molecule_ids=data.get("molecule_ids", []),
            finding_ids=data.get("finding_ids", []),
            paper_dois=data.get("paper_dois", []),
        )


@dataclass
class IcebergAgentContext:
    """The prompt, model, and parameters used to generate this card.

    Stored for reproducibility and quality improvement. When a card is
    regenerated, the previous agent context is moved to diff_archive.
    """
    model: str = ""                    # e.g., "claude-opus-4-6"
    prompt_template: str = ""          # Which prompt template was used
    prompt_hash: str = ""              # SHA-256 of the full prompt
    temperature: float = 0.0           # Sampling temperature
    generation_timestamp: str = ""     # ISO 8601
    generation_duration_ms: int = 0    # Wall-clock time
    token_count_input: int = 0         # Input tokens
    token_count_output: int = 0        # Output tokens
    cost_usd: float = 0.0             # Estimated cost

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "prompt_template": self.prompt_template,
            "prompt_hash": self.prompt_hash,
            "temperature": self.temperature,
            "generation_timestamp": self.generation_timestamp,
            "generation_duration_ms": self.generation_duration_ms,
            "token_count_input": self.token_count_input,
            "token_count_output": self.token_count_output,
            "cost_usd": round(self.cost_usd, 6),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> IcebergAgentContext:
        return cls(
            model=data.get("model", ""),
            prompt_template=data.get("prompt_template", ""),
            prompt_hash=data.get("prompt_hash", ""),
            temperature=data.get("temperature", 0.0),
            generation_timestamp=data.get("generation_timestamp", ""),
            generation_duration_ms=data.get("generation_duration_ms", 0),
            token_count_input=data.get("token_count_input", 0),
            token_count_output=data.get("token_count_output", 0),
            cost_usd=data.get("cost_usd", 0.0),
        )


@dataclass
class IcebergQualityScores:
    """Quality metrics for the card content.

    These scores determine whether the card passes quality gates before
    being served to users. A card that fails quality gates is marked
    as DRAFT and not served until regenerated.
    """
    prose_health: Optional[float] = None        # Sword Writer's Diet score (0-10)
    confidence_calibration: Optional[float] = None  # How well ω matches evidence
    coverage_completeness: Optional[float] = None   # Fraction of backing evidence cited
    reference_accuracy: Optional[float] = None      # Fraction of refs verified
    overall_quality: Optional[float] = None         # Composite score (0-1)
    passes_quality_gate: bool = False               # Whether card is servable

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "passes_quality_gate": self.passes_quality_gate,
        }
        if self.prose_health is not None:
            result["prose_health"] = round(self.prose_health, 2)
        if self.confidence_calibration is not None:
            result["confidence_calibration"] = round(self.confidence_calibration, 3)
        if self.coverage_completeness is not None:
            result["coverage_completeness"] = round(self.coverage_completeness, 3)
        if self.reference_accuracy is not None:
            result["reference_accuracy"] = round(self.reference_accuracy, 3)
        if self.overall_quality is not None:
            result["overall_quality"] = round(self.overall_quality, 3)
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> IcebergQualityScores:
        return cls(
            prose_health=data.get("prose_health"),
            confidence_calibration=data.get("confidence_calibration"),
            coverage_completeness=data.get("coverage_completeness"),
            reference_accuracy=data.get("reference_accuracy"),
            overall_quality=data.get("overall_quality"),
            passes_quality_gate=data.get("passes_quality_gate", False),
        )


@dataclass
class CardIceberg:
    """The depth layer — not visible by default, essential for audit.

    Per §178.3.3, the iceberg contains:
      - Source map (dependency graph)
      - Internal references (master doc sections, specs, panel outputs)
      - External references (APA bibliography with DOIs)
      - Raw data (database records backing this card)
      - Staleness ledger (changes since last regeneration)
      - Agent context (prompt, model, parameters)
      - Quality scores (prose health, calibration, completeness)
      - Diff archive (previous versions with annotated diffs)
      - Questions generated during writing (context appendix)
    """
    source_map: IcebergSourceMap = field(default_factory=IcebergSourceMap)
    internal_references: List[str] = field(default_factory=list)
    external_references: List[Dict[str, str]] = field(default_factory=list)
    raw_data: Optional[Dict[str, Any]] = None
    agent_context: IcebergAgentContext = field(default_factory=IcebergAgentContext)
    quality_scores: IcebergQualityScores = field(default_factory=IcebergQualityScores)
    diff_archive: List[Dict[str, Any]] = field(default_factory=list)
    questions_generated: List[str] = field(default_factory=list)
    assumptions_identified: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "source_map": self.source_map.to_dict(),
            "internal_references": self.internal_references,
            "external_references": self.external_references,
            "agent_context": self.agent_context.to_dict(),
            "quality_scores": self.quality_scores.to_dict(),
        }
        if self.raw_data:
            result["raw_data"] = self.raw_data
        if self.diff_archive:
            result["diff_archive"] = self.diff_archive
        if self.questions_generated:
            result["questions_generated"] = self.questions_generated
        if self.assumptions_identified:
            result["assumptions_identified"] = self.assumptions_identified
        if self.improvement_suggestions:
            result["improvement_suggestions"] = self.improvement_suggestions
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CardIceberg:
        return cls(
            source_map=IcebergSourceMap.from_dict(data.get("source_map", {})),
            internal_references=data.get("internal_references", []),
            external_references=data.get("external_references", []),
            raw_data=data.get("raw_data"),
            agent_context=IcebergAgentContext.from_dict(data.get("agent_context", {})),
            quality_scores=IcebergQualityScores.from_dict(data.get("quality_scores", {})),
            diff_archive=data.get("diff_archive", []),
            questions_generated=data.get("questions_generated", []),
            assumptions_identified=data.get("assumptions_identified", []),
            improvement_suggestions=data.get("improvement_suggestions", []),
        )


# ---------------------------------------------------------------------------
# The Card — Top-Level Container
# ---------------------------------------------------------------------------

@dataclass
class Card:
    """A single ATLAS knowledge artifact with Surface/Body/Iceberg layers.

    This is the canonical in-memory representation of any card in the
    system. Cards are identified by card_id and typed by card_type.
    The card_id encodes type and entity (e.g., "t2-mechanism:LIGHT-01").

    Cards serialize to JSON for persistence and deserialize on retrieval.
    The serialization format is stable — breaking changes require a
    version bump in card_schema_version.
    """
    # Identity
    card_id: str               # "{card_type}:{entity_id}" e.g., "t2-mechanism:LIGHT-01"
    card_type: CardType
    entity_id: str             # The underlying entity's canonical ID
    card_schema_version: str = "1.0.0"

    # Three layers
    surface: CardSurface = field(default_factory=lambda: CardSurface(
        title="", card_type=CardType.T2_MECHANISM,
        confidence_level=ConfidenceLevel.LOW,
        confidence_omega=None, confidence_label="",
        direction=Direction.NA, n_findings=0, n_papers=0,
        staleness=Staleness.FRESH, staleness_score=0.0,
        key_visual_path=None, last_generated="",
    ))
    body: CardBody = field(default_factory=lambda: CardBody(tabs={}))
    iceberg: CardIceberg = field(default_factory=CardIceberg)

    # Status
    is_draft: bool = True      # Draft cards are not served to users
    is_stale: bool = False     # Stale cards are queued for regeneration
    generation_count: int = 0  # How many times this card has been generated

    @property
    def tier(self) -> CardTier:
        """Return the tier this card belongs to."""
        from src.qa.cards.card_types import CARD_TYPE_REGISTRY
        return CARD_TYPE_REGISTRY[self.card_type].tier

    @property
    def display_name(self) -> str:
        """Human-readable type name."""
        from src.qa.cards.card_types import CARD_TYPE_REGISTRY
        return CARD_TYPE_REGISTRY[self.card_type].display_name

    def validate_tabs(self) -> List[str]:
        """Check that all required tabs are present. Returns list of missing tabs."""
        from src.qa.cards.card_types import CARD_TYPE_REGISTRY
        spec = CARD_TYPE_REGISTRY[self.card_type]
        missing = []
        for tab_name in spec.required_tabs:
            if not self.body.has_tab(tab_name):
                missing.append(tab_name)
        return missing

    def to_dict(self) -> Dict[str, Any]:
        return {
            "card_id": self.card_id,
            "card_type": self.card_type.value,
            "entity_id": self.entity_id,
            "card_schema_version": self.card_schema_version,
            "surface": self.surface.to_dict(),
            "body": self.body.to_dict(),
            "iceberg": self.iceberg.to_dict(),
            "is_draft": self.is_draft,
            "is_stale": self.is_stale,
            "generation_count": self.generation_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Card:
        card_type = CardType(data["card_type"])
        surface_data = data.get("surface", {})
        # Ensure card_type is set in surface data
        surface_data.setdefault("card_type", card_type.value)

        return cls(
            card_id=data["card_id"],
            card_type=card_type,
            entity_id=data.get("entity_id", ""),
            card_schema_version=data.get("card_schema_version", "1.0.0"),
            surface=CardSurface.from_dict(surface_data),
            body=CardBody.from_dict(data.get("body", {})),
            iceberg=CardIceberg.from_dict(data.get("iceberg", {})),
            is_draft=data.get("is_draft", True),
            is_stale=data.get("is_stale", False),
            generation_count=data.get("generation_count", 0),
        )

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> Card:
        """Deserialize from JSON string."""
        return cls.from_dict(json.loads(json_str))

    def save(self, path: Path) -> None:
        """Write card to a JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(self.to_json())

    @classmethod
    def load(cls, path: Path) -> Card:
        """Read card from a JSON file."""
        with open(path) as f:
            return cls.from_json(f.read())


# ---------------------------------------------------------------------------
# Factory Helpers
# ---------------------------------------------------------------------------

def make_card_id(card_type: CardType, entity_id: str) -> str:
    """Construct a canonical card_id from type and entity.

    Examples:
        make_card_id(CardType.T1_FRAMEWORK, "predictive-processing")
        → "t1-framework:predictive-processing"

        make_card_id(CardType.T2_MECHANISM, "LIGHT-01")
        → "t2-mechanism:LIGHT-01"
    """
    return f"{card_type.value}:{entity_id}"


def create_card(
    card_type: CardType,
    entity_id: str,
    title: str,
    confidence_level: ConfidenceLevel = ConfidenceLevel.LOW,
    confidence_omega: Optional[float] = None,
    direction: Direction = Direction.NA,
    n_findings: int = 0,
    n_papers: int = 0,
) -> Card:
    """Create a new draft Card with minimal required fields.

    The card starts as a draft with empty body and iceberg. The caller
    is expected to populate tabs and iceberg data before marking it
    as non-draft.
    """
    now = datetime.now(timezone.utc).isoformat()
    omega_str = f"ω = {confidence_omega:.2f}" if confidence_omega else "ω = N/A"
    conf_names = {
        ConfidenceLevel.HIGH: "High",
        ConfidenceLevel.MOD_HIGH: "Mod-High",
        ConfidenceLevel.MODERATE: "Moderate",
        ConfidenceLevel.LOW: "Low",
    }
    label = f"{conf_names[confidence_level]} ({omega_str})"

    return Card(
        card_id=make_card_id(card_type, entity_id),
        card_type=card_type,
        entity_id=entity_id,
        surface=CardSurface(
            title=title,
            card_type=card_type,
            confidence_level=confidence_level,
            confidence_omega=confidence_omega,
            confidence_label=label,
            direction=direction,
            n_findings=n_findings,
            n_papers=n_papers,
            staleness=Staleness.FRESH,
            staleness_score=0.0,
            key_visual_path=None,
            last_generated=now,
        ),
        body=CardBody(tabs={}),
        iceberg=CardIceberg(),
        is_draft=True,
        is_stale=False,
        generation_count=0,
    )
