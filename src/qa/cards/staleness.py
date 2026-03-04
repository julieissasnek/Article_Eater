"""
Staleness Scoring — When Cards Need Regeneration
=================================================

Implements the staleness lifecycle from master doc §173.4 and §178.6:

A card becomes stale when its backing evidence changes — new source cards
arrive, credence values shift, competitions are resolved, or the
generating agent's prompt template is updated. The staleness score is a
weighted function of these change signals:

  S(card) = w_new × ΔN + w_cred × Δω + w_comp × C_resolved + w_prompt × P_changed

Where:
  ΔN          = fraction of new source cards since last generation
  Δω          = absolute change in confidence (ω) since last generation
  C_resolved  = 1.0 if a competition this card participates in was resolved, else 0
  P_changed   = 1.0 if the prompt template has changed, else 0

Thresholds:
  FRESH:  S < 0.20  (green dot)
  AGING:  0.20 ≤ S < 0.40  (amber dot)
  STALE:  S ≥ 0.40  (red dot — regeneration recommended)

See: docs/master_doc_parts/PART_XXVI_section_178.md §178.6

Author: CW (Claude/Cowork)
Date: 2026-03-04
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.qa.cards.card_schema import Staleness


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class StalenessConfig:
    """Weights and thresholds for staleness scoring.

    These values are calibrated based on the system's sensitivity to
    different change types. New evidence (w_new_sources) is weighted
    highest because it most directly affects the factual content of
    the card. Credence shifts (w_credence_shift) are weighted next
    because they change the epistemic status. Competition resolution
    (w_competition_resolved) and prompt changes (w_prompt_changed)
    are weighted lower because they affect framing more than substance.
    """
    # Weights (must sum to 1.0 for normalized scoring)
    w_new_sources: float = 0.40           # Weight for new backing evidence
    w_credence_shift: float = 0.30        # Weight for ω change
    w_competition_resolved: float = 0.15  # Weight for competition resolution
    w_prompt_changed: float = 0.15        # Weight for agent prompt update

    # Thresholds
    fresh_threshold: float = 0.20         # Below this → FRESH
    stale_threshold: float = 0.40         # Above this → STALE (regeneration)

    # Time decay: staleness increases by this much per day with no changes
    # (incentivizes periodic review even when evidence is stable)
    daily_decay_rate: float = 0.002       # ~0.06/month, stale after ~200 days

    # Maximum staleness score (capped to prevent unbounded growth)
    max_score: float = 1.0

    def validate(self) -> List[str]:
        """Return list of validation errors, empty if config is valid."""
        errors = []
        weight_sum = (
            self.w_new_sources + self.w_credence_shift
            + self.w_competition_resolved + self.w_prompt_changed
        )
        if abs(weight_sum - 1.0) > 0.001:
            errors.append(
                f"Weights must sum to 1.0, got {weight_sum:.3f}"
            )
        if self.fresh_threshold >= self.stale_threshold:
            errors.append(
                f"fresh_threshold ({self.fresh_threshold}) must be < "
                f"stale_threshold ({self.stale_threshold})"
            )
        if self.daily_decay_rate < 0:
            errors.append("daily_decay_rate must be non-negative")
        return errors


DEFAULT_CONFIG = StalenessConfig()


# ---------------------------------------------------------------------------
# Staleness Ledger
# ---------------------------------------------------------------------------

@dataclass
class StalenessLedgerEntry:
    """A single change event that affects a card's staleness.

    The ledger tracks all changes to backing evidence since the card
    was last regenerated. Each entry records what changed, when, and
    its impact on the staleness score.
    """
    timestamp: str          # ISO 8601
    change_type: str        # "new_source", "credence_shift", "competition_resolved",
                            # "prompt_changed", "source_retracted", "manual_review"
    description: str        # Human-readable description
    impact: float           # Contribution to staleness score (0.0–1.0)
    source_id: Optional[str] = None  # Which source triggered the change

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "timestamp": self.timestamp,
            "change_type": self.change_type,
            "description": self.description,
            "impact": round(self.impact, 4),
        }
        if self.source_id:
            result["source_id"] = self.source_id
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StalenessLedgerEntry:
        return cls(
            timestamp=data["timestamp"],
            change_type=data["change_type"],
            description=data.get("description", ""),
            impact=data.get("impact", 0.0),
            source_id=data.get("source_id"),
        )


@dataclass
class StalenessLedger:
    """Collection of change events for a card, with score computation.

    The ledger is append-only between regenerations. When a card is
    regenerated, the ledger is archived to the iceberg's diff_archive
    and a fresh ledger begins.
    """
    entries: List[StalenessLedgerEntry] = field(default_factory=list)
    last_regenerated: Optional[str] = None  # ISO 8601
    last_computed_score: float = 0.0
    last_computed_status: str = "fresh"

    def add_entry(self, entry: StalenessLedgerEntry) -> None:
        """Append a change event to the ledger."""
        self.entries.append(entry)

    def record_new_source(
        self,
        source_id: str,
        description: str = "",
    ) -> None:
        """Record that a new source card was added to the backing evidence."""
        self.entries.append(StalenessLedgerEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            change_type="new_source",
            description=description or f"New source: {source_id}",
            impact=0.0,  # Computed later by compute_staleness_score
            source_id=source_id,
        ))

    def record_credence_shift(
        self,
        old_omega: float,
        new_omega: float,
        description: str = "",
    ) -> None:
        """Record that the card's confidence (ω) has changed."""
        delta = abs(new_omega - old_omega)
        self.entries.append(StalenessLedgerEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            change_type="credence_shift",
            description=description or f"ω shifted from {old_omega:.3f} to {new_omega:.3f}",
            impact=delta,
        ))

    def record_competition_resolved(
        self,
        competition_id: str,
        description: str = "",
    ) -> None:
        """Record that a competition involving this card was resolved."""
        self.entries.append(StalenessLedgerEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            change_type="competition_resolved",
            description=description or f"Competition resolved: {competition_id}",
            impact=1.0,
            source_id=competition_id,
        ))

    def record_prompt_changed(
        self,
        old_hash: str,
        new_hash: str,
        description: str = "",
    ) -> None:
        """Record that the generation prompt template was updated."""
        self.entries.append(StalenessLedgerEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            change_type="prompt_changed",
            description=description or f"Prompt hash changed: {old_hash[:8]}→{new_hash[:8]}",
            impact=1.0,
        ))

    def clear(self) -> List[StalenessLedgerEntry]:
        """Archive and clear the ledger. Returns the archived entries."""
        archived = list(self.entries)
        self.entries = []
        self.last_regenerated = datetime.now(timezone.utc).isoformat()
        self.last_computed_score = 0.0
        self.last_computed_status = "fresh"
        return archived

    @property
    def n_entries(self) -> int:
        return len(self.entries)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entries": [e.to_dict() for e in self.entries],
            "last_regenerated": self.last_regenerated,
            "last_computed_score": round(self.last_computed_score, 4),
            "last_computed_status": self.last_computed_status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StalenessLedger:
        return cls(
            entries=[
                StalenessLedgerEntry.from_dict(e)
                for e in data.get("entries", [])
            ],
            last_regenerated=data.get("last_regenerated"),
            last_computed_score=data.get("last_computed_score", 0.0),
            last_computed_status=data.get("last_computed_status", "fresh"),
        )


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def compute_staleness_score(
    ledger: StalenessLedger,
    total_sources: int,
    config: StalenessConfig = DEFAULT_CONFIG,
    days_since_generation: float = 0.0,
) -> tuple:
    """Compute the staleness score from a ledger's change events.

    Args:
        ledger: The change events since last regeneration
        total_sources: Total number of source cards backing the card
        config: Staleness weights and thresholds
        days_since_generation: Days elapsed since last card generation

    Returns:
        (score: float, status: Staleness) — the numeric score and
        the categorical status (FRESH/AGING/STALE)
    """
    # Count change events by type
    new_source_count = sum(
        1 for e in ledger.entries if e.change_type == "new_source"
    )
    credence_shifts = [
        e.impact for e in ledger.entries if e.change_type == "credence_shift"
    ]
    competition_resolved = any(
        e.change_type == "competition_resolved" for e in ledger.entries
    )
    prompt_changed = any(
        e.change_type == "prompt_changed" for e in ledger.entries
    )

    # Compute component scores (each 0.0–1.0)
    # New sources: fraction of sources that are new
    if total_sources > 0:
        new_source_score = min(new_source_count / max(total_sources, 1), 1.0)
    else:
        new_source_score = 1.0 if new_source_count > 0 else 0.0

    # Credence shift: max absolute shift (already 0–1 range)
    credence_score = max(credence_shifts) if credence_shifts else 0.0
    credence_score = min(credence_score, 1.0)

    # Competition resolved: binary
    competition_score = 1.0 if competition_resolved else 0.0

    # Prompt changed: binary
    prompt_score = 1.0 if prompt_changed else 0.0

    # Weighted sum
    score = (
        config.w_new_sources * new_source_score
        + config.w_credence_shift * credence_score
        + config.w_competition_resolved * competition_score
        + config.w_prompt_changed * prompt_score
    )

    # Add time decay
    score += days_since_generation * config.daily_decay_rate

    # Cap at maximum
    score = min(score, config.max_score)

    # Determine status
    if score < config.fresh_threshold:
        status = Staleness.FRESH
    elif score < config.stale_threshold:
        status = Staleness.AGING
    else:
        status = Staleness.STALE

    # Update ledger with computed values
    ledger.last_computed_score = score
    ledger.last_computed_status = status.value

    return score, status


# ---------------------------------------------------------------------------
# Success Conditions
# ---------------------------------------------------------------------------

def validate_staleness_system(
    cards_with_staleness: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Run success conditions for the staleness system.

    SC-STALE-1: All cards have a staleness score
    SC-STALE-2: No card has score > 1.0
    SC-STALE-3: Stale cards (≥ 0.40) are queued for regeneration
    SC-STALE-4: Fresh cards (< 0.20) are not queued for regeneration
    SC-STALE-5: Staleness weights sum to 1.0
    SC-STALE-6: At least 80% of entity cards have staleness ledgers

    Returns:
        Dict with condition results and overall pass/fail
    """
    config = DEFAULT_CONFIG
    results: Dict[str, Any] = {}

    # SC-STALE-1: All cards have staleness score
    cards_with_score = sum(
        1 for c in cards_with_staleness
        if "staleness_score" in c and c["staleness_score"] is not None
    )
    results["SC-STALE-1"] = {
        "description": "All cards have a staleness score",
        "pass": cards_with_score == len(cards_with_staleness),
        "value": f"{cards_with_score}/{len(cards_with_staleness)}",
    }

    # SC-STALE-2: No card has score > 1.0
    over_max = sum(
        1 for c in cards_with_staleness
        if c.get("staleness_score", 0) > 1.0
    )
    results["SC-STALE-2"] = {
        "description": "No card has staleness score > 1.0",
        "pass": over_max == 0,
        "value": f"{over_max} violations",
    }

    # SC-STALE-3: Stale cards are queued for regeneration
    stale_cards = [
        c for c in cards_with_staleness
        if c.get("staleness_score", 0) >= config.stale_threshold
    ]
    stale_queued = sum(1 for c in stale_cards if c.get("is_stale", False))
    results["SC-STALE-3"] = {
        "description": "Stale cards (≥ 0.40) are queued for regeneration",
        "pass": stale_queued == len(stale_cards) if stale_cards else True,
        "value": f"{stale_queued}/{len(stale_cards)} queued",
    }

    # SC-STALE-4: Fresh cards are not queued
    fresh_cards = [
        c for c in cards_with_staleness
        if c.get("staleness_score", 0) < config.fresh_threshold
    ]
    fresh_queued = sum(1 for c in fresh_cards if c.get("is_stale", False))
    results["SC-STALE-4"] = {
        "description": "Fresh cards (< 0.20) are not queued for regeneration",
        "pass": fresh_queued == 0,
        "value": f"{fresh_queued} incorrectly queued",
    }

    # SC-STALE-5: Weights sum to 1.0
    weight_errors = config.validate()
    results["SC-STALE-5"] = {
        "description": "Staleness weights sum to 1.0",
        "pass": len(weight_errors) == 0,
        "value": "valid" if not weight_errors else "; ".join(weight_errors),
    }

    # SC-STALE-6: Entity cards have staleness ledgers
    entity_cards = [
        c for c in cards_with_staleness
        if c.get("tier") in ("entity", "A")
    ]
    with_ledger = sum(
        1 for c in entity_cards
        if c.get("has_ledger", False)
    )
    pct = (with_ledger / len(entity_cards) * 100) if entity_cards else 100
    results["SC-STALE-6"] = {
        "description": "≥80% of entity cards have staleness ledgers",
        "pass": pct >= 80.0,
        "value": f"{pct:.1f}% ({with_ledger}/{len(entity_cards)})",
    }

    # Overall
    all_pass = all(r["pass"] for r in results.values())
    results["overall"] = {"pass": all_pass}

    return results
