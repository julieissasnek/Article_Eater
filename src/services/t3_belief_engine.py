"""
t3_belief_engine.py — T3 Empirical Belief Engine
=================================================

Orchestrates the formation, maintenance, and querying of T3 beliefs.
Sits between the Web of Belief (ground-level findings) and T2 templates
(mechanism predictions).

Responsibilities:
  1. Extract findings from EN beliefs and convert to T3 Finding format
  2. Run GeneralizationEngine to form T3 beliefs
  3. Link T3 beliefs to T2 templates
  4. Maintain T3 beliefs over time (re-aggregate on new findings)
  5. Expose query API for other modules via T3Integration contracts

ADR: Extension layer — new file, no existing code modified.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from src.services.stimulus_taxonomy import (
    StimulusTaxonomy, get_stimulus_taxonomy,
    DeliveryMode, SensoryModality,
)
from src.services.dv_generalization import (
    DVAccessLevel, get_dv_node, can_generalize_dvs,
)
from src.services.generalization_tree import (
    Finding, T3Belief, CoverageGap, GeneralizationEngine,
    GranularityLevel, BeliefStatus,
)

LOGGER = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════
# Belief Extraction (EN → Findings)
# ══════════════════════════════════════════════════════════════════

def extract_finding_from_belief(belief_dict: Dict[str, Any]) -> Optional[Finding]:
    """
    Convert an EN Belief (dict form) into a T3 Finding.

    Extracts IV (environment_id), DV (outcome_id), effect direction,
    and metadata from the serialized belief.

    Uses the IV/DV classifier to map raw antecedent/consequent strings
    to taxonomy node IDs for proper T3 generalization.
    """
    env_id = belief_dict.get("environment_id")
    out_id = belief_dict.get("outcome_id")

    if not env_id or not out_id:
        return None  # Cannot form T3 finding without IV and DV

    # ── IV/DV Classification ──
    # Classify raw strings to taxonomy nodes (3-stage: pattern → semantic → keyword)
    try:
        from src.services.iv_dv_classifier import get_classifier
        classifier = get_classifier()

        iv_result = classifier.classify_iv(env_id)
        dv_result = classifier.classify_dv(out_id)

        # Use classified node_id if confidence is sufficient (≥0.40)
        classified_iv = iv_result.node_id if iv_result.confidence >= 0.40 else env_id
        classified_dv = dv_result.node_id if dv_result.confidence >= 0.40 else out_id

        # Use access level from classifier if available
        access = dv_result.access_level
    except Exception:
        # Graceful fallback: use raw IDs if classifier unavailable
        classified_iv = env_id
        classified_dv = out_id
        access = DVAccessLevel.UNSPECIFIED

    # Determine effect direction from content heuristics
    content = (belief_dict.get("content") or "").lower()
    direction = _infer_direction(content, belief_dict)

    # Determine delivery mode from content/tags
    delivery = _infer_delivery_mode(content, belief_dict.get("tags", []))

    # Fallback: try DV node from dv_generalization hierarchy
    if access == DVAccessLevel.UNSPECIFIED:
        dv_node = get_dv_node(classified_dv)
        if dv_node:
            access = dv_node.access_level

    return Finding(
        finding_id=belief_dict.get("belief_id", "unknown"),
        iv_node=classified_iv,
        dv_node=classified_dv,
        effect_direction=direction,
        effect_size=belief_dict.get("evidence_effect_size"),
        sample_n=belief_dict.get("evidence_sample_n"),
        paper_id=(belief_dict.get("paper_ids", [None]) or [None])[0],
        delivery_mode=delivery,
        population=belief_dict.get("scope_population", ""),
        temporal_scope=belief_dict.get("scope_temporal", ""),
        study_design=belief_dict.get("study_design", ""),
        access_level=access,
    )


def _infer_direction(content: str, belief_dict: Dict) -> str:
    """Infer effect direction from belief content."""
    # Check explicit effect_direction field
    explicit = belief_dict.get("effect_direction")
    if explicit and explicit in ("positive", "negative", "null", "mixed"):
        return explicit

    # Heuristic from content
    positive_words = ["increase", "enhance", "improve", "higher", "more", "promote", "facilitate"]
    negative_words = ["decrease", "reduce", "impair", "lower", "less", "inhibit", "diminish"]
    null_words = ["no effect", "no significant", "null", "not significant", "failed to"]

    pos_score = sum(1 for w in positive_words if w in content)
    neg_score = sum(1 for w in negative_words if w in content)
    null_score = sum(1 for w in null_words if w in content)

    if null_score > 0:
        return "null"
    if pos_score > neg_score:
        return "positive"
    if neg_score > pos_score:
        return "negative"
    return "positive"  # Default assumption


def _infer_delivery_mode(content: str, tags: List[str]) -> DeliveryMode:
    """Infer delivery mode from content and tags."""
    text = content + " " + " ".join(tags)
    text = text.lower()

    if any(w in text for w in ["virtual reality", "vr ", "vr,", "immersive"]):
        return DeliveryMode.VR
    if any(w in text for w in ["augmented reality", " ar "]):
        return DeliveryMode.AR
    if any(w in text for w in ["photograph", "photo", "image", "picture"]):
        return DeliveryMode.PHOTOGRAPH
    if any(w in text for w in ["video", "film", "recording"]):
        return DeliveryMode.VIDEO
    if any(w in text for w in ["render", "3d model", "digital twin"]):
        return DeliveryMode.RENDER_3D
    if any(w in text for w in ["drawing", "plan", "sketch", "elevation"]):
        return DeliveryMode.PLAN_DRAWING
    if any(w in text for w in ["real", "field study", "in situ", "on-site", "actual"]):
        return DeliveryMode.REAL
    return DeliveryMode.UNSPECIFIED


# ══════════════════════════════════════════════════════════════════
# T3 Belief Engine
# ══════════════════════════════════════════════════════════════════

class T3BeliefEngine:
    """
    Orchestrates T3 belief formation and maintenance.

    Lifecycle:
    1. load_beliefs() — extract findings from EN
    2. aggregate() — form T3 beliefs
    3. link_templates() — connect to T2 templates
    4. on_new_finding() — incremental update
    """

    def __init__(self, taxonomy: Optional[StimulusTaxonomy] = None):
        self.taxonomy = taxonomy or get_stimulus_taxonomy()
        self.engine = GeneralizationEngine(self.taxonomy)
        self.findings: List[Finding] = []
        self.t3_beliefs: Dict[str, T3Belief] = {}
        self.last_aggregation: Optional[datetime] = None
        self._callbacks: List[Any] = []

    def load_from_belief_dicts(self, belief_dicts: List[Dict[str, Any]]) -> int:
        """
        Load findings from serialized EN beliefs.

        Returns number of findings extracted.
        """
        extracted = 0
        for bd in belief_dicts:
            finding = extract_finding_from_belief(bd)
            if finding:
                self.findings.append(finding)
                extracted += 1
        LOGGER.info("Extracted %d findings from %d beliefs", extracted, len(belief_dicts))
        return extracted

    def aggregate(self) -> Dict[str, T3Belief]:
        """Run full aggregation pipeline."""
        self.engine = GeneralizationEngine(self.taxonomy)
        self.engine.add_findings(self.findings)
        self.t3_beliefs = self.engine.aggregate()
        self.last_aggregation = datetime.now(timezone.utc)

        # Fire callbacks
        for cb in self._callbacks:
            try:
                cb("aggregation_complete", self.summary())
            except Exception as e:
                LOGGER.warning("Callback error: %s", e)

        return self.t3_beliefs

    def on_new_finding(self, finding: Finding) -> Optional[T3Belief]:
        """
        Incremental update: add a new finding and re-aggregate.

        Returns the most affected T3 belief, if any.
        """
        self.findings.append(finding)
        # Re-aggregate (could be optimized to incremental, but full is safer)
        old_beliefs = dict(self.t3_beliefs)
        self.aggregate()

        # Find which belief changed most
        for t3_id, new_belief in self.t3_beliefs.items():
            old = old_beliefs.get(t3_id)
            if old and old.status != new_belief.status:
                return new_belief
            if not old:
                return new_belief
        return None

    def link_templates(self, template_predictions: Dict[str, List[str]]) -> int:
        """
        Link T3 beliefs to T2 templates.

        Args:
            template_predictions: {template_id: [predicted_env_ids]}

        Returns number of links created.
        """
        links_created = 0
        for t3_id, belief in self.t3_beliefs.items():
            for template_id, predicted_ivs in template_predictions.items():
                # Check if any predicted IV matches the belief's IV
                for pred_iv in predicted_ivs:
                    if (pred_iv == belief.iv_node or
                        self.taxonomy.is_ancestor_of(pred_iv, belief.iv_node) or
                        self.taxonomy.is_ancestor_of(belief.iv_node, pred_iv)):
                        if template_id not in belief.linked_templates:
                            belief.linked_templates.append(template_id)
                            links_created += 1
                        break
        return links_created

    def register_callback(self, callback) -> None:
        """Register a callback for T3 events."""
        self._callbacks.append(callback)

    # ── Query API ──

    def query(self, iv_pattern: str = "", dv_pattern: str = "",
              min_confidence: float = 0.0,
              status: Optional[str] = None) -> List[T3Belief]:
        """
        Query T3 beliefs with filters.

        Args:
            iv_pattern: Substring match on IV node
            dv_pattern: Substring match on DV node
            min_confidence: Minimum confidence threshold
            status: Filter by status string
        """
        results = []
        for belief in self.t3_beliefs.values():
            if iv_pattern and iv_pattern not in belief.iv_node:
                continue
            if dv_pattern and dv_pattern not in belief.dv_node:
                continue
            if belief.confidence < min_confidence:
                continue
            if status and belief.status.value != status:
                continue
            results.append(belief)
        return sorted(results, key=lambda b: -b.confidence)

    def what_does_en_believe(self, topic: str) -> List[Dict[str, Any]]:
        """
        Answer: "What does the EN believe about X?"

        Uses keyword matching against both IV and DV taxonomy to find
        relevant T3 beliefs and return natural-language summaries.
        """
        # Try IV match
        iv_matches = self.taxonomy.match_keywords(topic)
        # Try as DV pattern
        results = []

        for iv_id, score in iv_matches[:5]:
            for belief in self.t3_beliefs.values():
                if (belief.iv_node == iv_id or
                    self.taxonomy.is_ancestor_of(iv_id, belief.iv_node)):
                    results.append({
                        "belief": belief.natural_language,
                        "confidence": belief.confidence,
                        "status": belief.status.value,
                        "n_studies": belief.n_total,
                        "t3_id": belief.t3_id,
                    })

        # Also try DV pattern matching
        topic_lower = topic.lower()
        for belief in self.t3_beliefs.values():
            if topic_lower in belief.dv_node:
                entry = {
                    "belief": belief.natural_language,
                    "confidence": belief.confidence,
                    "status": belief.status.value,
                    "n_studies": belief.n_total,
                    "t3_id": belief.t3_id,
                }
                if entry not in results:
                    results.append(entry)

        return sorted(results, key=lambda r: -r["confidence"])

    def coverage_gaps(self, min_priority: float = 0.3) -> List[Dict[str, Any]]:
        """Get coverage gaps formatted for VOI search."""
        return [g.to_dict() for g in self.engine.get_coverage_gaps(min_priority)]

    def argumentation_targets(self) -> List[Dict[str, Any]]:
        """Get contested beliefs suitable for argumentation analysis."""
        contested = self.engine.get_contested_beliefs()
        return [
            {
                "t3_id": b.t3_id,
                "claim": b.natural_language,
                "consistency": b.consistency,
                "n_positive": b.n_positive,
                "n_negative": b.n_negative,
                "n_null": b.n_null,
                "boundary_conditions": b.boundary_conditions,
            }
            for b in contested
        ]

    def summary(self) -> Dict[str, Any]:
        """Full T3 layer summary."""
        engine_summary = self.engine.summary()
        engine_summary["last_aggregation"] = (
            self.last_aggregation.isoformat() if self.last_aggregation else None
        )
        engine_summary["n_findings"] = len(self.findings)
        return engine_summary

    def export_beliefs(self) -> List[Dict[str, Any]]:
        """Export all T3 beliefs as dicts."""
        return [b.to_dict() for b in sorted(
            self.t3_beliefs.values(),
            key=lambda b: (-b.confidence, b.t3_id),
        )]
