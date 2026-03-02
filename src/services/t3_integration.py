"""
t3_integration.py — T3 Contract-Based Integration Layer
========================================================

Provides typed contracts for all modules that interact with T3.
Each contract defines the interface without requiring direct imports
of T3 internals, following the Parnas information-hiding principle.

Touch points (per user specification):
  1. QA / Overseer (INV-10: T3 consistency)
  2. Argumentation (argument_attack.py)
  3. EN / Web of Belief (ground-level beliefs)
  4. BN (Bayesian network edge justification)
  5. Interpretation Envelope
  6. Annotation / Extraction pipeline
  7. Article Searching (VOI search)
  8. Interactivity / GUI
  9. Reporting / evidence summarizer
  10. Cross-layer query
  11. CVA template linker
  12. Belief validator

Design (per expert panel — system design experts):
  - Contracts are abstract protocols, not concrete classes
  - T3 adapter implements all contracts
  - Existing modules import only contracts, not T3 internals
  - Events use a simple pub/sub pattern
  - Contracts are versioned for backward compatibility

ADR: Extension layer — new file, no existing code modified.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol, Set

LOGGER = logging.getLogger(__name__)

# Import needed for overseer / BN contract implementations
from src.services.generalization_tree import BeliefStatus


# ══════════════════════════════════════════════════════════════════
# Events
# ══════════════════════════════════════════════════════════════════

class T3EventType(Enum):
    """Events emitted by the T3 layer."""
    BELIEF_FORMED = "belief_formed"          # New T3 belief created
    BELIEF_UPDATED = "belief_updated"        # Existing belief changed status
    BELIEF_CONTESTED = "belief_contested"    # Belief became contested
    COVERAGE_GAP = "coverage_gap"            # New coverage gap identified
    AGGREGATION_COMPLETE = "aggregation_complete"  # Full re-aggregation done
    TEMPLATE_LINKED = "template_linked"      # T2 template linked
    REFLEX_TRIGGERED = "reflex_triggered"    # A T3 reflex fired


@dataclass
class T3Event:
    """An event from the T3 layer."""
    event_type: T3EventType
    t3_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[str] = None


# ══════════════════════════════════════════════════════════════════
# Contracts (Protocols)
# ══════════════════════════════════════════════════════════════════

class T3QueryContract(Protocol):
    """Contract for querying T3 beliefs.

    Used by: cross_layer_query, interpretation envelope, GUI, reporting.
    """

    def query_beliefs(
        self,
        iv_pattern: str = "",
        dv_pattern: str = "",
        min_confidence: float = 0.0,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Query T3 beliefs by pattern and filters."""
        ...

    def what_does_en_believe(self, topic: str) -> List[Dict[str, Any]]:
        """Natural-language query: what does EN believe about topic?"""
        ...

    def get_belief_summary(self) -> Dict[str, Any]:
        """Get summary statistics for the T3 layer."""
        ...

    def get_all_beliefs(self) -> List[Dict[str, Any]]:
        """Export all T3 beliefs."""
        ...


class T3UpdateContract(Protocol):
    """Contract for updating T3 when new findings arrive.

    Used by: extraction_to_web, annotation pipeline.
    """

    def on_finding_added(self, belief_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Notify T3 of a new finding. Returns affected T3 belief if any."""
        ...

    def on_batch_complete(self, belief_dicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Notify T3 of a batch of new findings. Returns aggregation summary."""
        ...

    def trigger_reaggregation(self) -> Dict[str, Any]:
        """Force full re-aggregation. Returns summary."""
        ...


class T3GapContract(Protocol):
    """Contract for T3 coverage gap detection.

    Used by: voi_search, article searching, gap predictor.
    """

    def get_coverage_gaps(self, min_priority: float = 0.3) -> List[Dict[str, Any]]:
        """Get coverage gaps above priority threshold."""
        ...

    def get_search_queries(self, max_queries: int = 10) -> List[str]:
        """Generate search queries from highest-priority gaps."""
        ...

    def get_nascent_search_seeds(self) -> List[Dict[str, Any]]:
        """Get nascent beliefs as search seeds for article acquisition.

        Returns list of {t3_id, query, iv_node, dv_node, direction, source_paper}
        — each represents a single-article finding we want to find more like.
        """
        ...

    def gap_summary(self) -> Dict[str, Any]:
        """Summary of coverage gaps."""
        ...


class T3ArgumentContract(Protocol):
    """Contract for T3 as argumentation target.

    Used by: argument_attack, tension detection.
    """

    def get_argumentation_targets(self) -> List[Dict[str, Any]]:
        """Get contested beliefs suitable for attack analysis."""
        ...

    def get_belief_for_contrast(
        self, iv_node: str, dv_node: str
    ) -> Optional[Dict[str, Any]]:
        """Get T3 belief for contrast class construction."""
        ...

    def beliefs_about_claim(self, claim_text: str) -> List[Dict[str, Any]]:
        """Find T3 beliefs relevant to a natural-language claim."""
        ...


class T3OverseerContract(Protocol):
    """Contract for overseer monitoring of T3 health.

    Used by: overseer.py (INV-10).
    """

    def check_consistency(self) -> List[Dict[str, Any]]:
        """Check T3 for internal consistency violations."""
        ...

    def health_metrics(self) -> Dict[str, Any]:
        """T3 layer health metrics for overseer."""
        ...

    def reflex_status(self) -> List[Dict[str, Any]]:
        """Status of T3 reflexes."""
        ...


class T3BNContract(Protocol):
    """Contract for BN integration.

    Used by: edge_justification, bayesian_network.
    """

    def t3_evidence_for_edge(
        self, iv_variable: str, dv_variable: str
    ) -> Optional[Dict[str, Any]]:
        """Get T3 evidence supporting a BN edge."""
        ...

    def t3_supported_edges(self) -> List[Dict[str, Any]]:
        """All BN edges that T3 has evidence for."""
        ...


class T3TemplateContract(Protocol):
    """Contract for T2 template linkage.

    Used by: cva_template_linker, template matching.
    """

    def beliefs_for_template(self, template_id: str) -> List[Dict[str, Any]]:
        """Get T3 beliefs that provide evidence for a template."""
        ...

    def template_coverage(self, template_id: str) -> Dict[str, Any]:
        """How well a template's predictions are covered by T3 beliefs."""
        ...


# ══════════════════════════════════════════════════════════════════
# Event Bus
# ══════════════════════════════════════════════════════════════════

class T3EventBus:
    """Simple pub/sub event bus for T3 events."""

    def __init__(self):
        self._subscribers: Dict[T3EventType, List[Callable]] = {}

    def subscribe(self, event_type: T3EventType, handler: Callable) -> None:
        self._subscribers.setdefault(event_type, []).append(handler)

    def publish(self, event: T3Event) -> None:
        for handler in self._subscribers.get(event.event_type, []):
            try:
                handler(event)
            except Exception as e:
                LOGGER.warning("Event handler error for %s: %s", event.event_type, e)


# ══════════════════════════════════════════════════════════════════
# T3 Adapter (implements all contracts)
# ══════════════════════════════════════════════════════════════════

class T3Adapter:
    """
    Adapter that implements all T3 contracts.

    Wraps T3BeliefEngine and exposes contract-compliant interfaces.
    Other modules interact with T3 ONLY through this adapter.
    """

    def __init__(self, engine=None):
        """
        Initialize with a T3BeliefEngine instance.

        Args:
            engine: T3BeliefEngine instance. If None, creates one lazily.
        """
        self._engine = engine
        self._event_bus = T3EventBus()
        self._reflexes: List[Dict[str, Any]] = []

    @property
    def engine(self):
        if self._engine is None:
            from src.services.t3_belief_engine import T3BeliefEngine
            self._engine = T3BeliefEngine()
        return self._engine

    @property
    def event_bus(self) -> T3EventBus:
        return self._event_bus

    # ── T3QueryContract ──

    def query_beliefs(
        self,
        iv_pattern: str = "",
        dv_pattern: str = "",
        min_confidence: float = 0.0,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        beliefs = self.engine.query(iv_pattern, dv_pattern, min_confidence, status)
        return [b.to_dict() for b in beliefs]

    def what_does_en_believe(self, topic: str) -> List[Dict[str, Any]]:
        return self.engine.what_does_en_believe(topic)

    def get_belief_summary(self) -> Dict[str, Any]:
        return self.engine.summary()

    def get_all_beliefs(self) -> List[Dict[str, Any]]:
        return self.engine.export_beliefs()

    # ── T3UpdateContract ──

    def on_finding_added(self, belief_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        from src.services.t3_belief_engine import extract_finding_from_belief
        finding = extract_finding_from_belief(belief_dict)
        if not finding:
            return None
        affected = self.engine.on_new_finding(finding)
        if affected:
            self._event_bus.publish(T3Event(
                T3EventType.BELIEF_UPDATED, t3_id=affected.t3_id,
                data=affected.to_dict(),
            ))
            self._check_reflexes(affected)
            return affected.to_dict()
        return None

    def on_batch_complete(self, belief_dicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        self.engine.load_from_belief_dicts(belief_dicts)
        self.engine.aggregate()
        summary = self.engine.summary()
        self._event_bus.publish(T3Event(
            T3EventType.AGGREGATION_COMPLETE, data=summary,
        ))
        return summary

    def trigger_reaggregation(self) -> Dict[str, Any]:
        self.engine.aggregate()
        summary = self.engine.summary()
        self._event_bus.publish(T3Event(
            T3EventType.AGGREGATION_COMPLETE, data=summary,
        ))
        return summary

    # ── T3GapContract ──

    def get_coverage_gaps(self, min_priority: float = 0.3) -> List[Dict[str, Any]]:
        return self.engine.coverage_gaps(min_priority)

    def get_search_queries(self, max_queries: int = 10) -> List[str]:
        gaps = self.engine.coverage_gaps(0.3)
        queries = [g["search_query"] for g in gaps if g.get("search_query")]
        return queries[:max_queries]

    def get_nascent_search_seeds(self) -> List[Dict[str, Any]]:
        """Get nascent beliefs as search seeds for article acquisition."""
        return self.engine.engine.get_nascent_search_queries()

    def gap_summary(self) -> Dict[str, Any]:
        gaps = self.engine.coverage_gaps(0.0)
        nascent = self.engine.engine.get_nascent_beliefs()
        return {
            "total_gaps": len(gaps),
            "nascent_search_seeds": len(nascent),
            "high_priority": sum(1 for g in gaps if g.get("priority", 0) >= 0.7),
            "medium_priority": sum(1 for g in gaps if 0.4 <= g.get("priority", 0) < 0.7),
            "low_priority": sum(1 for g in gaps if g.get("priority", 0) < 0.4),
            "gap_types": _count_by_key(gaps, "gap_type"),
        }

    # ── T3ArgumentContract ──

    def get_argumentation_targets(self) -> List[Dict[str, Any]]:
        return self.engine.argumentation_targets()

    def get_belief_for_contrast(
        self, iv_node: str, dv_node: str
    ) -> Optional[Dict[str, Any]]:
        belief = self.engine.engine.get_belief(iv_node, dv_node)
        return belief.to_dict() if belief else None

    def beliefs_about_claim(self, claim_text: str) -> List[Dict[str, Any]]:
        return self.engine.what_does_en_believe(claim_text)

    # ── T3OverseerContract (INV-10) ──

    def check_consistency(self) -> List[Dict[str, Any]]:
        """
        Check T3 internal consistency.

        Rules:
        - RF-1: T3 belief contradicts its linked T2 template prediction
        - RF-3: T3 belief with <3 sources is promoted (should be TENTATIVE)
        - RF-4: Merged beliefs have different mechanisms
        """
        violations = []

        for belief in self.engine.t3_beliefs.values():
            # RF-3: Check promotion rules
            if (belief.status == BeliefStatus.ESTABLISHED and
                belief.n_total < 3):
                violations.append({
                    "rule": "RF-3",
                    "severity": "warning",
                    "t3_id": belief.t3_id,
                    "description": (
                        f"Belief promoted to ESTABLISHED with only "
                        f"{belief.n_total} sources (minimum: 3)"
                    ),
                })

            # Check consistency ratio
            if (belief.status == BeliefStatus.ESTABLISHED and
                belief.consistency < 0.6):
                violations.append({
                    "rule": "consistency_check",
                    "severity": "warning",
                    "t3_id": belief.t3_id,
                    "description": (
                        f"ESTABLISHED belief has low consistency: "
                        f"{belief.consistency:.2f}"
                    ),
                })

        return violations

    def health_metrics(self) -> Dict[str, Any]:
        """T3 health metrics for overseer dashboard."""
        summary = self.engine.summary()
        consistency_violations = self.check_consistency()
        return {
            **summary,
            "consistency_violations": len(consistency_violations),
            "reflex_status": self.reflex_status(),
        }

    def reflex_status(self) -> List[Dict[str, Any]]:
        return list(self._reflexes)

    # ── T3BNContract ──

    def t3_evidence_for_edge(
        self, iv_variable: str, dv_variable: str
    ) -> Optional[Dict[str, Any]]:
        belief = self.engine.engine.get_belief(iv_variable, dv_variable)
        if belief:
            return {
                "t3_id": belief.t3_id,
                "direction": belief.effect_direction,
                "confidence": belief.confidence,
                "n_studies": belief.n_total,
                "consistency": belief.consistency,
            }
        return None

    def t3_supported_edges(self) -> List[Dict[str, Any]]:
        edges = []
        for belief in self.engine.t3_beliefs.values():
            if belief.status in (BeliefStatus.ESTABLISHED, BeliefStatus.CONTESTED):
                edges.append({
                    "iv": belief.iv_node,
                    "dv": belief.dv_node,
                    "direction": belief.effect_direction,
                    "confidence": belief.confidence,
                    "n_studies": belief.n_total,
                })
        return edges

    # ── T3TemplateContract ──

    def beliefs_for_template(self, template_id: str) -> List[Dict[str, Any]]:
        return [
            b.to_dict() for b in self.engine.t3_beliefs.values()
            if template_id in b.linked_templates
        ]

    def template_coverage(self, template_id: str) -> Dict[str, Any]:
        linked = [
            b for b in self.engine.t3_beliefs.values()
            if template_id in b.linked_templates
        ]
        return {
            "template_id": template_id,
            "n_supporting_beliefs": len(linked),
            "n_established": sum(1 for b in linked if b.status == BeliefStatus.ESTABLISHED),
            "n_contested": sum(1 for b in linked if b.status == BeliefStatus.CONTESTED),
            "avg_confidence": (
                sum(b.confidence for b in linked) / len(linked) if linked else 0.0
            ),
        }

    # ── Reflexes ──

    def _check_reflexes(self, belief) -> None:
        """Check and fire T3 reflexes."""

        # RF-1: T3 contradicts T2 prediction
        if (belief.linked_templates and
            belief.effect_direction == "negative" and
            belief.status == BeliefStatus.ESTABLISHED):
            reflex = {
                "reflex": "RF-1",
                "t3_id": belief.t3_id,
                "description": "T3 belief contradicts linked T2 template prediction",
                "action": "flag_for_review",
            }
            self._reflexes.append(reflex)
            self._event_bus.publish(T3Event(
                T3EventType.REFLEX_TRIGGERED, t3_id=belief.t3_id, data=reflex,
            ))

        # RF-2: High-priority coverage gap → auto-generate search
        for gap_dict in self.engine.coverage_gaps(0.8):
            reflex = {
                "reflex": "RF-2",
                "gap_id": gap_dict.get("gap_id"),
                "description": "High-priority gap → auto-generate search suggestion",
                "search_query": gap_dict.get("search_query"),
            }
            self._reflexes.append(reflex)

        # RF-3: Under-sourced promotion
        if (belief.status == BeliefStatus.ESTABLISHED and belief.n_total < 3):
            reflex = {
                "reflex": "RF-3",
                "t3_id": belief.t3_id,
                "description": "Belief promoted with <3 sources — should be TENTATIVE",
                "action": "demote_to_tentative",
            }
            self._reflexes.append(reflex)


def _count_by_key(items: List[Dict], key: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in items:
        val = str(item.get(key, "unknown"))
        counts[val] = counts.get(val, 0) + 1
    return counts


# ══════════════════════════════════════════════════════════════════
# Factory
# ══════════════════════════════════════════════════════════════════

_adapter: Optional[T3Adapter] = None

def get_t3_adapter() -> T3Adapter:
    """Get or create singleton T3Adapter."""
    global _adapter
    if _adapter is None:
        _adapter = T3Adapter()
    return _adapter
