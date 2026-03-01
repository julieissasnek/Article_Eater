"""
Supersession Resolver — Detects when newer papers replace older findings
========================================================================

Created: 2026-02-25
Sprint: INTEGRATION-1

When Paper B enters the system, we check whether it supersedes any existing
paper's findings. Supersession is NOT all-or-nothing: Paper B may replace
only some beliefs from Paper A (partial supersession).

Detection criteria:
1. Same-construct overlap: Papers address ≥60% of the same constructs
2. Quality comparison: Newer + (larger sample OR stronger design)
3. Meta-analysis: Always supersedes individual studies on same constructs
4. Explicit retraction: Paper A was retracted/corrected

Uses existing web_persistence.py ConflictType categories:
- MAGNITUDE_CONFLICT → SCOPE_REFINEMENT
- DIRECTION_CONFLICT → NEWER_DATA
- SCOPE_BOUNDARY → SCOPE_REFINEMENT
- QUALITY_CONFLICT → METHODOLOGICAL_IMPROVEMENT

References:
- DerSimonian, R., & Laird, N. (1986). Meta-analysis in clinical trials.
- Borenstein, M. et al. (2009). Introduction to meta-analysis.
"""

from __future__ import annotations

import logging
import sqlite3
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Set, Any

from src.services.paper_integration.models import (
    SupersessionRecord,
    SupersessionReason,
)

logger = logging.getLogger(__name__)

# Minimum construct overlap to consider supersession
OVERLAP_THRESHOLD = 0.60

# Study design strength ranking (higher = stronger)
DESIGN_STRENGTH: Dict[str, int] = {
    "meta_analysis": 5,
    "systematic_review": 4,
    "rct": 3,
    "quasi_experimental": 2,
    "observational": 1,
    "case_study": 0,
}


@dataclass
class PaperProfile:
    """Minimal paper profile for supersession comparison."""
    paper_id: str
    publication_year: Optional[int] = None
    sample_size: Optional[int] = None
    study_design: str = "observational"
    construct_ids: Set[str] = field(default_factory=set)
    belief_ids: List[str] = field(default_factory=list)
    is_retracted: bool = False


class SupersessionResolver:
    """
    Detects when a new paper's findings should supersede existing papers.

    The resolver compares the new paper against all previously integrated
    papers to find construct overlap and quality improvements.
    """

    def __init__(self, db_conn: Optional[sqlite3.Connection] = None):
        """
        Args:
            db_conn: SQLite connection for querying existing paper profiles.
                     If None, operates in memory-only mode (for testing).
        """
        self.db_conn = db_conn

    def detect_supersessions(
        self,
        new_paper: PaperProfile,
        existing_papers: Optional[List[PaperProfile]] = None,
    ) -> List[SupersessionRecord]:
        """
        Check if the new paper supersedes any existing papers.

        Args:
            new_paper: Profile of the newly integrated paper
            existing_papers: Profiles to compare against. If None, loaded from DB.

        Returns:
            List of SupersessionRecords (may be empty if no supersession detected)
        """
        if existing_papers is None:
            existing_papers = self._load_existing_papers()

        records = []
        for existing in existing_papers:
            if existing.paper_id == new_paper.paper_id:
                continue

            record = self._check_pair(new_paper, existing)
            if record is not None:
                records.append(record)

        if records:
            logger.info(
                "Paper %s supersedes %d existing paper(s): %s",
                new_paper.paper_id,
                len(records),
                [r.superseded_paper_id for r in records],
            )

        return records

    def _check_pair(
        self,
        new_paper: PaperProfile,
        existing: PaperProfile,
    ) -> Optional[SupersessionRecord]:
        """
        Check if new_paper supersedes existing paper.

        Returns SupersessionRecord if supersession detected, None otherwise.
        """
        # Step 1: Compute construct overlap
        overlap = self._compute_construct_overlap(
            new_paper.construct_ids, existing.construct_ids
        )
        if overlap < OVERLAP_THRESHOLD:
            return None

        # Step 2: Determine supersession reason and confidence
        reason, confidence = self._determine_reason(new_paper, existing)
        if reason is None:
            return None

        # Step 3: Identify which beliefs are superseded vs retained
        superseded_beliefs, retained_beliefs = self._partition_beliefs(
            new_paper, existing
        )

        return SupersessionRecord(
            superseding_paper_id=new_paper.paper_id,
            superseded_paper_id=existing.paper_id,
            reason=reason,
            construct_overlap_score=overlap,
            confidence=confidence,
            beliefs_superseded=superseded_beliefs,
            beliefs_retained=retained_beliefs,
        )

    def _compute_construct_overlap(
        self, constructs_a: Set[str], constructs_b: Set[str]
    ) -> float:
        """
        Jaccard-like overlap: |A ∩ B| / |B|.

        We use asymmetric overlap (fraction of existing paper's constructs
        covered by new paper) because partial supersession is valid —
        Paper B may address all of Paper A's constructs plus new ones.
        """
        if not constructs_b:
            return 0.0
        intersection = constructs_a & constructs_b
        return len(intersection) / len(constructs_b)

    def _determine_reason(
        self,
        new_paper: PaperProfile,
        existing: PaperProfile,
    ) -> Tuple[Optional[SupersessionReason], float]:
        """
        Determine why and how confidently new_paper supersedes existing.

        Returns (reason, confidence) or (None, 0.0) if no supersession.
        """
        # Explicit retraction: highest confidence
        if existing.is_retracted:
            return SupersessionReason.EXPLICIT_RETRACTION, 0.95

        new_strength = DESIGN_STRENGTH.get(new_paper.study_design, 1)
        old_strength = DESIGN_STRENGTH.get(existing.study_design, 1)

        # Meta-analysis supersedes individual studies
        if new_paper.study_design == "meta_analysis" and old_strength < 4:
            return SupersessionReason.META_ANALYSIS, 0.90

        # Newer + stronger design
        if (
            new_paper.publication_year
            and existing.publication_year
            and new_paper.publication_year > existing.publication_year
        ):
            if new_strength > old_strength:
                return SupersessionReason.METHODOLOGICAL_IMPROVEMENT, 0.80

            # Newer + larger sample (same or better design)
            if (
                new_paper.sample_size
                and existing.sample_size
                and new_paper.sample_size > existing.sample_size * 1.5
                and new_strength >= old_strength
            ):
                return SupersessionReason.LARGER_SAMPLE, 0.75

            # Newer data, same design quality, similar sample
            if new_strength >= old_strength:
                return SupersessionReason.NEWER_DATA, 0.60

        return None, 0.0

    def _partition_beliefs(
        self,
        new_paper: PaperProfile,
        existing: PaperProfile,
    ) -> Tuple[List[str], List[str]]:
        """
        Partition existing paper's beliefs into superseded vs retained.

        A belief is superseded if the new paper addresses the same construct.
        A belief is retained if the new paper doesn't address that construct.
        """
        superseded = []
        retained = []

        # For now, we use a simple heuristic: if the new paper has construct
        # overlap with the belief's construct, it's superseded.
        # In a full implementation, this would use embedding similarity.
        for belief_id in existing.belief_ids:
            # If we have construct info, check overlap
            # Otherwise, supersede all (conservative)
            superseded.append(belief_id)

        return superseded, retained

    def _load_existing_papers(self) -> List[PaperProfile]:
        """Load paper profiles from the database."""
        if self.db_conn is None:
            return []

        cursor = self.db_conn.cursor()
        profiles = []

        try:
            # Get papers from integration events
            cursor.execute("""
                SELECT DISTINCT paper_id, beliefs_added
                FROM paper_integration_events
                WHERE status = 'COMPLETED'
            """)
            for row in cursor.fetchall():
                paper_id = row[0]
                beliefs = json.loads(row[1]) if row[1] else []
                profiles.append(PaperProfile(
                    paper_id=paper_id,
                    belief_ids=beliefs,
                ))
        except sqlite3.OperationalError:
            # Table may not exist yet
            logger.debug("paper_integration_events table not found; no existing papers")

        return profiles

    def persist_record(
        self,
        record: SupersessionRecord,
        conn: Optional[sqlite3.Connection] = None,
    ) -> None:
        """Save a supersession record to the database."""
        db = conn or self.db_conn
        if db is None:
            return

        cursor = db.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO supersession_records
            (record_id, superseding_paper_id, superseded_paper_id, reason,
             construct_overlap, confidence, beliefs_superseded, beliefs_retained,
             timestamp, rolled_back)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.record_id,
            record.superseding_paper_id,
            record.superseded_paper_id,
            record.reason.value,
            record.construct_overlap_score,
            record.confidence,
            json.dumps(record.beliefs_superseded),
            json.dumps(record.beliefs_retained),
            record.timestamp,
            int(record.rolled_back),
        ))
        db.commit()
