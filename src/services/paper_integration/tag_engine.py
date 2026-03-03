"""
Tag Assignment Engine — 3D Taxonomy for Beliefs
================================================

Created: 2026-02-25
Sprint: INTEGRATION-1

Implements the 3D tag taxonomy from AG's molecule deep reflection:

Dimension 1 — Entity/Topic:
    What environmental domain does the belief address?
    e.g., "lighting", "thermal", "acoustic", "spatial", "biophilic",
          "color", "social", "wayfinding", "air_quality"

Dimension 2 — Theoretical:
    Which T1 frameworks, T1.5 theories, and molecules does the belief
    connect to?
    e.g., "predictive-processing", "interoceptive-constructionist-affect",
          "neuromodulatory-systems", "ART", "SRT", "Biophilia", "GOLDILOCKS"

Dimension 3 — Effect Size:
    What is the magnitude of the reported effect?
    Categorized by Cohen's d ranges:
    - negligible: d < 0.2
    - small: 0.2 ≤ d < 0.5
    - medium: 0.5 ≤ d < 0.8
    - large: d ≥ 0.8

Tags are stored in the tag_assignments table and used by:
- QA precompute pipeline (filter by theoretical relevance)
- Discovery funnel (identify gaps per domain)
- Molecule matching (which beliefs feed which molecules)
"""

from __future__ import annotations

import logging
import re
import sqlite3
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

from src.services.paper_integration.models import TagAssignment

logger = logging.getLogger(__name__)


# =============================================================================
# ENTITY/TOPIC KEYWORD MAPPING
# =============================================================================

# Maps keywords found in belief statements to entity tags.
# These are the major environmental domains in the CMR system.
ENTITY_KEYWORDS: Dict[str, List[str]] = {
    "lighting": [
        "light", "lighting", "luminan", "illuminan", "daylight", "glare",
        "lux", "candela", "circadian", "melanopic", "photopic",
    ],
    "thermal": [
        "thermal", "temperature", "heat", "cool", "warm", "PMV", "PPD",
        "HVAC", "air conditioning", "radiant",
    ],
    "acoustic": [
        "acoustic", "sound", "noise", "decibel", "dB", "reverber",
        "soundscape", "auditory", "speech intelligib",
    ],
    "spatial": [
        "spatial", "layout", "floor plan", "room size", "ceiling height",
        "wayfinding", "navigation", "density", "crowding", "proxemic",
    ],
    "biophilic": [
        "biophil", "nature", "greenery", "vegetation", "plant", "garden",
        "water feature", "natural material", "wood", "stone",
    ],
    "visual_complexity": [
        "fractal", "complexity", "ornamentation", "pattern", "facade",
        "visual richness", "1/f", "power spectrum",
    ],
    "color": [
        "color", "colour", "hue", "saturation", "chromat", "warm color",
        "cool color", "red", "blue", "green",
    ],
    "air_quality": [
        "air quality", "CO2", "ventilation", "particulate", "VOC",
        "fresh air", "IAQ",
    ],
    "social": [
        "social", "interaction", "privacy", "personal space", "crowding",
        "community", "gathering", "collaboration",
    ],
    "temporal": [
        "temporal", "rhythm", "circadian", "diurnal", "seasonal",
        "variation over time", "dynamic",
    ],
}

# =============================================================================
# T1 FRAMEWORK KEYWORDS
# =============================================================================

T1_KEYWORDS: Dict[str, List[str]] = {
    "predictive-processing": ["predictive processing", "prediction error", "free energy", "Bayesian brain"],
    "interoceptive-constructionist-affect": ["interocepti", "allostatic", "body budget", "homeostatic"],
    "neuromodulatory-systems": ["neuromodulat", "dopamin", "serotonin", "cortisol", "norepinephrine"],
    "embodied-cognition": ["affordance", "ecological", "Gibson", "enactive"],
    "spatial-navigation": ["spatial navigation", "cognitive map", "place cell", "hippocampal"],
    "default-mode-dynamics": ["directed attention", "attention restoration", "fascination"],
    "multisensory-integration": ["multisensory", "cross-modal", "audiovisual", "congruency"],
    "memory-systems": ["mirror system", "embodied simulation", "imitation"],
    "dual-process-evaluation": ["dual process", "System 1", "System 2", "implicit", "explicit"],
    "chronobiological-regulation": ["circadian", "melatonin", "SCN", "zeitgeber", "light-dark cycle"],
}

# =============================================================================
# EFFECT SIZE CATEGORIES
# =============================================================================

EFFECT_SIZE_CATEGORIES = {
    "negligible": (0.0, 0.2),
    "small": (0.2, 0.5),
    "medium": (0.5, 0.8),
    "large": (0.8, float("inf")),
}


class TagAssignmentEngine:
    """
    Assigns 3D taxonomy tags to beliefs during paper integration.

    Each belief receives tags in three dimensions:
    1. Entity/Topic: environmental domain
    2. Theoretical: T1/T1.5/molecule connections
    3. Effect size: magnitude category
    """

    def __init__(self, db_conn: Optional[sqlite3.Connection] = None):
        self.db_conn = db_conn

    def assign_tags(
        self,
        belief_id: str,
        paper_id: str,
        statement: str,
        effect_size_d: Optional[float] = None,
        theory_names: Optional[List[str]] = None,
    ) -> List[TagAssignment]:
        """
        Assign all applicable tags to a belief.

        Args:
            belief_id: The belief being tagged
            paper_id: The paper that produced this belief
            statement: The belief's text statement (for keyword extraction)
            effect_size_d: Cohen's d value (if available)
            theory_names: Known theory connections (from extraction_to_web.py)

        Returns:
            List of TagAssignment objects
        """
        tags = []

        # Dimension 1: Entity/Topic
        entity_tags = self._extract_entity_tags(statement)
        for entity, confidence in entity_tags:
            tags.append(TagAssignment(
                belief_id=belief_id,
                tag_dimension="entity",
                tag_value=entity,
                paper_id=paper_id,
                confidence=confidence,
            ))

        # Dimension 2: Theoretical
        theoretical_tags = self._extract_theoretical_tags(
            statement, theory_names or []
        )
        for theory, confidence in theoretical_tags:
            tags.append(TagAssignment(
                belief_id=belief_id,
                tag_dimension="theoretical",
                tag_value=theory,
                paper_id=paper_id,
                confidence=confidence,
            ))

        # Dimension 3: Effect size
        if effect_size_d is not None:
            effect_tag = self._categorize_effect_size(abs(effect_size_d))
            tags.append(TagAssignment(
                belief_id=belief_id,
                tag_dimension="effect_size",
                tag_value=effect_tag,
                paper_id=paper_id,
                confidence=0.9,  # High confidence if d is reported directly
            ))

        return tags

    def _extract_entity_tags(
        self, statement: str
    ) -> List[Tuple[str, float]]:
        """
        Extract entity/topic tags from belief statement text.

        Uses keyword matching with confidence proportional to
        the number of matching keywords found.
        """
        statement_lower = statement.lower()
        results = []

        for entity, keywords in ENTITY_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw.lower() in statement_lower)
            if matches > 0:
                # Confidence scales with number of keyword hits (max 0.95)
                confidence = min(0.95, 0.5 + (matches - 1) * 0.15)
                results.append((entity, confidence))

        return results

    def _extract_theoretical_tags(
        self,
        statement: str,
        known_theories: List[str],
    ) -> List[Tuple[str, float]]:
        """
        Extract theoretical tags from belief statement + known theories.

        Known theories (from extraction_to_web.py's theory inference) get
        high confidence. Keyword-matched T1 frameworks get lower confidence.
        """
        results = []
        seen = set()

        # Known theories get high confidence
        for theory in known_theories:
            if theory not in seen:
                results.append((theory, 0.85))
                seen.add(theory)

        # Keyword-based T1 detection
        statement_lower = statement.lower()
        for framework, keywords in T1_KEYWORDS.items():
            if framework in seen:
                continue
            matches = sum(1 for kw in keywords if kw.lower() in statement_lower)
            if matches > 0:
                confidence = min(0.80, 0.4 + (matches - 1) * 0.15)
                results.append((framework, confidence))
                seen.add(framework)

        return results

    def _categorize_effect_size(self, d: float) -> str:
        """Categorize Cohen's d into standard effect size buckets."""
        for category, (low, high) in EFFECT_SIZE_CATEGORIES.items():
            if low <= d < high:
                return category
        return "large"

    def persist_tags(
        self,
        tags: List[TagAssignment],
        conn: Optional[sqlite3.Connection] = None,
    ) -> int:
        """
        Save tag assignments to the database.

        Returns the number of tags persisted.
        """
        db = conn or self.db_conn
        if db is None:
            return 0

        cursor = db.cursor()
        persisted = 0

        for tag in tags:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO tag_assignments
                    (belief_id, tag_dimension, tag_value, paper_id, confidence, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    tag.belief_id,
                    tag.tag_dimension,
                    tag.tag_value,
                    tag.paper_id,
                    tag.confidence,
                    tag.timestamp,
                ))
                persisted += 1
            except sqlite3.OperationalError as e:
                logger.warning("Failed to persist tag: %s", e)

        db.commit()
        return persisted

    def get_tags_for_belief(
        self, belief_id: str, conn: Optional[sqlite3.Connection] = None
    ) -> List[TagAssignment]:
        """Retrieve all tags for a specific belief."""
        db = conn or self.db_conn
        if db is None:
            return []

        cursor = db.cursor()
        try:
            cursor.execute("""
                SELECT belief_id, tag_dimension, tag_value, paper_id,
                       confidence, timestamp
                FROM tag_assignments
                WHERE belief_id = ?
            """, (belief_id,))
            return [
                TagAssignment(
                    belief_id=row[0],
                    tag_dimension=row[1],
                    tag_value=row[2],
                    paper_id=row[3],
                    confidence=row[4],
                    timestamp=row[5],
                )
                for row in cursor.fetchall()
            ]
        except sqlite3.OperationalError:
            return []

    def get_beliefs_by_tag(
        self,
        dimension: str,
        value: str,
        conn: Optional[sqlite3.Connection] = None,
    ) -> List[str]:
        """Get all belief_ids that have a specific tag."""
        db = conn or self.db_conn
        if db is None:
            return []

        cursor = db.cursor()
        try:
            cursor.execute("""
                SELECT belief_id FROM tag_assignments
                WHERE tag_dimension = ? AND tag_value = ?
            """, (dimension, value))
            return [row[0] for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            return []
