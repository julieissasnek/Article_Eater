"""
Article Eater - Web of Belief Persistence & Accumulation (Refined)
===================================================================

Sprint 5: Persistence & Accumulation (2026-01-18)
Expert Panel Refinements Applied (2026-01-18)

Provides persistent storage and cross-paper accumulation for the Web of Belief.

Key Features:
1. SQLite persistence for beliefs, constraints, and bridges
2. Master web accumulation across multiple papers
3. Belief merging with conflict resolution
4. Version tracking for audit trail
5. Coherence history logging with dashboard metrics

Expert Panel Refinements Incorporated:
- Decision 5.1: Web snapshots for disaster recovery; optimized indices
- Decision 5.2: Structured attribute matching; conflict type categorization
- Decision 5.3: Inverse-variance weighting for credence merge
- Decision 5.4: Paper quality weighting
- Decision 5.5: Coherence dashboard; local per-theory coherence; decline alerts

References:
- Quine, W.V.O. (1951). Two Dogmas of Empiricism
- BonJour, L. (1985). The Structure of Empirical Knowledge
- DerSimonian, R., & Laird, N. (1986). Meta-analysis in clinical trials
- Borenstein, M. et al. (2009). Introduction to meta-analysis
"""

import sqlite3
import json
import logging
import math
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Iterable
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum

# Import web of belief components
from src.services.web_of_belief import (
    WebOfBelief,
    Belief,
    Constraint,
    Credence,
    EpistemicLevel,
    BeliefStatus,
    ScopeConditions,     # Sprint 6
    create_neuroarchitecture_web,
)
from src.epistemic.edge_types import convert_legacy_constraint_type

# Import bridge warrants (Sprint 3)
try:
    from src.services.bridge_warrants import (
        BridgeWarrant,
        BridgeRegistry,
        BridgeType,
        BridgeStatus,
        ConfidenceSource,
    )
    BRIDGE_AVAILABLE = True
except ImportError:
    BRIDGE_AVAILABLE = False

# Import environment taxonomy (Sprint 7)
try:
    from src.services.environment_taxonomy import (
        resolve_environment_term,
        are_antonyms,
        get_antonym,
        normalize_environment_in_content,
    )
    ENVIRONMENT_TAXONOMY_AVAILABLE = True
except ImportError:
    ENVIRONMENT_TAXONOMY_AVAILABLE = False

logger = logging.getLogger(__name__)


# =============================================================================
# CONFLICT TYPE (Expert Panel 5.2)
# =============================================================================

class ConflictType(Enum):
    """
    Categorization of belief conflicts.

    Per expert panel (Cartwright): Distinguish types of conflicts to enable
    appropriate resolution strategies.

    Sprint 6 addition: PRECISION_BOUNDARY (per Cartwright)
    """
    GENUINE_CONTRADICTION = "genuine_contradiction"  # Same construct, opposite direction
    SCOPE_BOUNDARY = "scope_boundary"  # Opposite effects in different contexts
    METHODOLOGICAL_DIVERGENCE = "methodological_divergence"  # Different measurement methods
    PRECISION_BOUNDARY = "precision_boundary"  # Same direction, different magnitude (NEW Sprint 6)
    UNKNOWN = "unknown"  # Awaiting human classification


# =============================================================================
# SPRINT 2.6 TRACK B: QUALITY-WEIGHTED ENTRENCHMENT (P-QW Panel)
# =============================================================================

# Q4: Revised component weights per panel (Cartwright, Bates, Mayo)
# Old weights: sample_size=0.2, methodology=0.3, journal=0.1, preregistered=0.15
# New weights: more emphasis on methodology, reduced institution weight
QUALITY_WEIGHTS: Dict[str, float] = {
    'methodology': 0.28,      # Up from 0.3 (most important content signal)
    'citations': 0.18,        # New explicit weight
    'institution': 0.12,      # Q2: Reduced from 0.15
    'author_quality': 0.18,   # Author h-index/reputation
    'preregistration': 0.10,  # Slightly down from 0.15
    'sample_size': 0.10,      # Slightly down from 0.2
    'ecological_validity': 0.04,  # Q4: New optional component per R. Kaplan
}

# Q2: Institution tier list (Tier 1 = top programs for CNfA)
# Per R. Kaplan: Added Wageningen, Uppsala, JCU
INSTITUTION_TIERS: Dict[str, int] = {
    # Tier 1: Top environmental psychology / cognitive science programs
    "mit": 1,
    "michigan": 1,
    "stanford": 1,
    "berkeley": 1,
    "yale": 1,
    "harvard": 1,
    "ucsd": 1,
    "wageningen": 1,  # Q2: Added per R. Kaplan
    "uppsala": 1,      # Q2: Added per R. Kaplan
    "jcu": 1,          # Q2: James Cook University, added per R. Kaplan
    # Tier 2: Strong programs
    "cornell": 2,
    "uchicago": 2,
    "penn": 2,
    "columbia": 2,
    "duke": 2,
    "uiuc": 2,
    "wisconsin": 2,
    # Tier 3: Good programs
    # (Default for known universities not in Tier 1-2)
}
DEFAULT_INSTITUTION_TIER = 3
MAX_INSTITUTION_TIER = 5  # Tier for unknown institutions


def citation_velocity(
    citation_count: int,
    publication_year: int,
    current_year: int = 2026
) -> float:
    """
    Compute citation velocity (Q5: citations per year since publication).

    Per Cartwright/Mayo: Replace raw career stage adjustment with citation
    velocity, which directly addresses temporal accumulation effects.

    Args:
        citation_count: Total citations
        publication_year: Year paper was published
        current_year: Current year (default 2026)

    Returns:
        Citations per year
    """
    years = max(1, current_year - publication_year)
    return citation_count / years


def quality_to_entrenchment(overall_quality: float) -> float:
    """
    Convert paper quality to belief entrenchment (Q6: piecewise linear with floor).

    Per Pearl/Mayo: Low-quality papers get floor entrenchment (0.10).
    Above threshold, linear mapping to 0.70.

    Args:
        overall_quality: Overall quality score [0, 1]

    Returns:
        Entrenchment value [0.10, 0.70]
    """
    if overall_quality < 0.3:
        return 0.10  # Floor for low-quality papers
    else:
        # Linear from 0.15 at quality=0.3 to 0.70 at quality=1.0
        return 0.15 + (overall_quality - 0.3) * (0.70 - 0.15) / (1.0 - 0.3)


def get_institution_tier(institution: str) -> int:
    """
    Get institution tier from name (Q2).

    Args:
        institution: Institution name or identifier

    Returns:
        Tier (1 = top, higher = lower prestige)
    """
    if not institution:
        return MAX_INSTITUTION_TIER

    # Normalize: lowercase, strip common suffixes
    normalized = institution.lower().strip()
    for suffix in [" university", " college", " institute", "university of ", "u ", "uc"]:
        normalized = normalized.replace(suffix, "")
    normalized = normalized.strip()

    return INSTITUTION_TIERS.get(normalized, DEFAULT_INSTITUTION_TIER)


def institution_tier_to_score(tier: int) -> float:
    """
    Convert institution tier to quality score component.

    Args:
        tier: Institution tier (1 = top)

    Returns:
        Score [0, 1] where 1 = Tier 1
    """
    if tier <= 1:
        return 1.0
    elif tier == 2:
        return 0.75
    elif tier == 3:
        return 0.5
    elif tier == 4:
        return 0.25
    else:
        return 0.1


# =============================================================================
# COHERENCE DASHBOARD (Expert Panel 5.5)
# =============================================================================

@dataclass
class CoherenceDashboard:
    """
    Multi-metric coherence health dashboard.

    Per expert panel (Simon): Single coherence score masks pathological states.
    Track multiple metrics for comprehensive health assessment.
    """
    global_coherence: float  # Current overall coherence
    n_beliefs: int
    n_constraints: int
    constraint_density: float  # constraints / (beliefs * (beliefs-1))
    n_conflicts: int  # Flagged conflicts awaiting resolution
    n_isolated_beliefs: int  # Beliefs with no constraints
    n_theories: int  # Distinct theory_ids
    inter_theory_coherence: float  # Coherence of cross-theory constraints only
    entropy: float  # Belief credence distribution entropy
    mean_uncertainty: float  # Average belief uncertainty
    diversity_index: float = 0.0  # Sprint 7: Shannon entropy over environment/outcome domains

    def is_healthy(self) -> bool:
        """Check if dashboard indicates healthy web state."""
        return (
            self.global_coherence >= 0.5 and
            self.n_conflicts < self.n_beliefs * 0.1 and  # <10% conflicts
            self.n_isolated_beliefs < self.n_beliefs * 0.2 and  # <20% isolated
            self.constraint_density > 0.01  # Some connectivity
        )

    def health_summary(self) -> str:
        """Generate human-readable health summary."""
        issues = []
        if self.global_coherence < 0.5:
            issues.append(f"Low coherence ({self.global_coherence:.2f})")
        if self.n_conflicts >= self.n_beliefs * 0.1:
            issues.append(f"High conflict rate ({self.n_conflicts} conflicts)")
        if self.n_isolated_beliefs >= self.n_beliefs * 0.2:
            issues.append(f"Many isolated beliefs ({self.n_isolated_beliefs})")
        if self.constraint_density < 0.01:
            issues.append(f"Sparse connectivity ({self.constraint_density:.3f})")

        if not issues:
            return "Healthy"
        return "; ".join(issues)


@dataclass
class CoherenceAlert:
    """Alert for coherence decline or anomaly."""
    alert_type: str  # "sharp_decline", "cumulative_decline", "anomaly"
    severity: str  # "warning", "critical"
    message: str
    coherence_before: float
    coherence_after: float
    triggered_at: str
    triggered_by: Optional[str] = None  # paper_id if applicable


# =============================================================================
# DATABASE SCHEMA (Refined)
# =============================================================================

WEB_PERSISTENCE_SCHEMA = """
-- Web of Belief Persistence Schema
-- Sprint 5: Persistence & Accumulation (Refined)

-- Master web metadata
CREATE TABLE IF NOT EXISTS web_metadata (
    web_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    n_beliefs INTEGER DEFAULT 0,
    n_constraints INTEGER DEFAULT 0,
    coherence_score REAL,
    is_master INTEGER DEFAULT 0
);

-- Beliefs table (normalized)
CREATE TABLE IF NOT EXISTS beliefs (
    belief_id TEXT PRIMARY KEY,
    web_id TEXT NOT NULL,
    content TEXT NOT NULL,
    level TEXT NOT NULL,
    status TEXT NOT NULL,
    credence_value REAL NOT NULL,
    credence_uncertainty REAL,
    credence_n_supporting INTEGER DEFAULT 0,
    credence_n_contradicting INTEGER DEFAULT 0,
    credence_n_observations INTEGER DEFAULT 0,
    theory_id TEXT,
    entrenchment REAL DEFAULT 0.3,
    domain TEXT,
    attribute_id TEXT,  -- Expert Panel 5.2: Structured attribute for identity matching
    outcome_type TEXT,  -- Expert Panel 5.2: Outcome type for identity matching
    scope TEXT,  -- Sprint 6: JSON-serialized ScopeConditions
    environment_id TEXT,  -- Sprint 7: Canonical environment ID from taxonomy
    outcome_id TEXT,  -- Sprint 7: Canonical outcome ID
    evidence_cluster_id TEXT,  -- Sprint 8: Groups beliefs from same study
    tags TEXT,  -- JSON array
    paper_ids TEXT,  -- JSON array
    epistemic_v2 TEXT,  -- ARCH-4 V24: JSON-serialized v2 epistemic fields (content_v2, status_v2, provenance_v2)
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (web_id) REFERENCES web_metadata(web_id)
);

CREATE INDEX IF NOT EXISTS idx_beliefs_web ON beliefs(web_id);
CREATE INDEX IF NOT EXISTS idx_beliefs_theory ON beliefs(theory_id);
CREATE INDEX IF NOT EXISTS idx_beliefs_status ON beliefs(status);
CREATE INDEX IF NOT EXISTS idx_beliefs_web_level ON beliefs(web_id, level);  -- Expert Panel 5.1

-- Constraints table
CREATE TABLE IF NOT EXISTS constraints (
    constraint_id TEXT PRIMARY KEY,
    web_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    constraint_type TEXT NOT NULL,
    strength REAL DEFAULT 0.5,
    bidirectional INTEGER DEFAULT 0,
    evidence_ids TEXT,  -- JSON array
    warrant_type TEXT,
    provenance TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (web_id) REFERENCES web_metadata(web_id),
    FOREIGN KEY (source_id) REFERENCES beliefs(belief_id),
    FOREIGN KEY (target_id) REFERENCES beliefs(belief_id)
);

CREATE INDEX IF NOT EXISTS idx_constraints_web ON constraints(web_id);
CREATE INDEX IF NOT EXISTS idx_constraints_source ON constraints(source_id);
CREATE INDEX IF NOT EXISTS idx_constraints_target ON constraints(target_id);
CREATE INDEX IF NOT EXISTS idx_constraints_source_target ON constraints(source_id, target_id);  -- Expert Panel 5.1

-- Bridges table (Sprint 3)
CREATE TABLE IF NOT EXISTS bridges (
    bridge_id TEXT PRIMARY KEY,
    web_id TEXT NOT NULL,
    source_domain TEXT NOT NULL,
    target_domain TEXT NOT NULL,
    bridge_type TEXT NOT NULL,
    warrant_statement TEXT NOT NULL,
    assumed_mechanism TEXT,
    confidence REAL NOT NULL,
    confidence_source TEXT,
    status TEXT NOT NULL,
    source_beliefs TEXT,  -- JSON array
    target_beliefs TEXT,  -- JSON array
    evidence_for TEXT,  -- JSON array
    evidence_against TEXT,  -- JSON array
    failure_record TEXT,  -- JSON object
    voi_flag INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (web_id) REFERENCES web_metadata(web_id)
);

CREATE INDEX IF NOT EXISTS idx_bridges_web ON bridges(web_id);
CREATE INDEX IF NOT EXISTS idx_bridges_status ON bridges(status);

-- Paper integration log
CREATE TABLE IF NOT EXISTS paper_integrations (
    integration_id INTEGER PRIMARY KEY AUTOINCREMENT,
    web_id TEXT NOT NULL,
    paper_id TEXT NOT NULL,
    run_id TEXT,
    n_beliefs_added INTEGER DEFAULT 0,
    n_beliefs_updated INTEGER DEFAULT 0,
    n_constraints_added INTEGER DEFAULT 0,
    coherence_before REAL,
    coherence_after REAL,
    status TEXT DEFAULT 'active',  -- Expert Panel 5.4: 'active', 'retracted'
    integrated_at TEXT NOT NULL,
    FOREIGN KEY (web_id) REFERENCES web_metadata(web_id)
);

CREATE INDEX IF NOT EXISTS idx_paper_integrations_web ON paper_integrations(web_id);
CREATE INDEX IF NOT EXISTS idx_paper_integrations_paper ON paper_integrations(paper_id);

-- Paper publication metadata (for scholarly timeline replay)
CREATE TABLE IF NOT EXISTS paper_publication (
    paper_id TEXT PRIMARY KEY,
    publication_year INTEGER,
    publication_date TEXT,  -- ISO date (YYYY-MM-DD) when available
    first_seen_at TEXT,  -- system ingestion timestamp
    source TEXT,  -- metadata source (paper_json, bibtex, manual)
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_paper_publication_year ON paper_publication(publication_year);

-- Entrenchment snapshots (system vs scholarly timelines)
CREATE TABLE IF NOT EXISTS entrenchment_snapshots (
    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    web_id TEXT NOT NULL,
    belief_id TEXT NOT NULL,
    paper_id TEXT,
    timeline_type TEXT NOT NULL,  -- "system" or "scholarly"
    as_of_date TEXT NOT NULL,
    entrenchment REAL NOT NULL,
    connectivity REAL,
    level_weight REAL,
    coherence_contrib REAL,
    constraint_count INTEGER,
    status TEXT,
    credence_value REAL,
    credence_uncertainty REAL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (web_id) REFERENCES web_metadata(web_id),
    FOREIGN KEY (belief_id) REFERENCES beliefs(belief_id)
);

CREATE INDEX IF NOT EXISTS idx_entrenchment_snapshots_web ON entrenchment_snapshots(web_id);
CREATE INDEX IF NOT EXISTS idx_entrenchment_snapshots_belief ON entrenchment_snapshots(belief_id);
CREATE INDEX IF NOT EXISTS idx_entrenchment_snapshots_timeline ON entrenchment_snapshots(timeline_type);
CREATE INDEX IF NOT EXISTS idx_entrenchment_snapshots_asof ON entrenchment_snapshots(as_of_date);

-- Entrenchment events (delta tracking)
CREATE TABLE IF NOT EXISTS entrenchment_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    web_id TEXT NOT NULL,
    belief_id TEXT NOT NULL,
    paper_id TEXT,
    timeline_type TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    delta REAL,
    event_type TEXT NOT NULL,
    reason TEXT,
    source_paper_id TEXT,
    constraint_id TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (web_id) REFERENCES web_metadata(web_id),
    FOREIGN KEY (belief_id) REFERENCES beliefs(belief_id)
);

CREATE INDEX IF NOT EXISTS idx_entrenchment_events_web ON entrenchment_events(web_id);
CREATE INDEX IF NOT EXISTS idx_entrenchment_events_belief ON entrenchment_events(belief_id);
CREATE INDEX IF NOT EXISTS idx_entrenchment_events_timeline ON entrenchment_events(timeline_type);

-- Coherence history for tracking evolution
CREATE TABLE IF NOT EXISTS coherence_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    web_id TEXT NOT NULL,
    coherence_score REAL NOT NULL,
    n_beliefs INTEGER NOT NULL,
    n_constraints INTEGER NOT NULL,
    recorded_at TEXT NOT NULL,
    triggered_by TEXT,  -- paper_id or "merge" or "equilibrium"
    FOREIGN KEY (web_id) REFERENCES web_metadata(web_id)
);

CREATE INDEX IF NOT EXISTS idx_coherence_history_web ON coherence_history(web_id);

-- Local coherence per theory (Expert Panel 5.5)
CREATE TABLE IF NOT EXISTS local_coherence_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    web_id TEXT NOT NULL,
    theory_id TEXT NOT NULL,
    local_coherence REAL,
    n_beliefs INTEGER,
    n_constraints INTEGER,
    recorded_at TEXT NOT NULL,
    FOREIGN KEY (web_id) REFERENCES web_metadata(web_id)
);

CREATE INDEX IF NOT EXISTS idx_local_coherence_web ON local_coherence_history(web_id);
CREATE INDEX IF NOT EXISTS idx_local_coherence_theory ON local_coherence_history(theory_id);

-- Belief merge log for tracking accumulation decisions
CREATE TABLE IF NOT EXISTS belief_merge_log (
    merge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    web_id TEXT NOT NULL,
    belief_id TEXT NOT NULL,
    merge_type TEXT NOT NULL,  -- "new", "update", "conflict"
    conflict_type TEXT,  -- Expert Panel 5.2: ConflictType value
    old_credence REAL,
    new_credence REAL,
    source_paper_id TEXT,
    merge_reason TEXT,
    auto_resolved INTEGER DEFAULT 0,  -- Expert Panel 5.2: Was this auto-resolved?
    requires_review INTEGER DEFAULT 0,  -- Expert Panel 5.2: Flagged for human review?
    merged_at TEXT NOT NULL,
    FOREIGN KEY (web_id) REFERENCES web_metadata(web_id)
);

-- Paper quality weights (Expert Panel 5.4)
CREATE TABLE IF NOT EXISTS paper_quality (
    paper_id TEXT PRIMARY KEY,
    sample_size_score REAL,      -- normalized 0-1
    methodology_score REAL,       -- from extraction
    journal_impact_factor REAL,   -- if available
    citation_count INTEGER,       -- current citations
    preregistered INTEGER DEFAULT 0,
    replication_status TEXT DEFAULT 'original',  -- 'original', 'successful_replication', 'failed_replication'
    overall_quality REAL,         -- composite score
    -- Sprint 2.6 Track B: P-QW Panel additions
    institution TEXT,             -- Q2: institution for tier lookup
    author_h_index INTEGER,       -- Q4: author quality metric
    publication_year INTEGER,     -- Q5: for citation velocity
    ecological_validity_score REAL,  -- Q4: new component
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Web snapshots for disaster recovery (Expert Panel 5.1)
CREATE TABLE IF NOT EXISTS web_snapshots (
    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    web_id TEXT NOT NULL,
    snapshot_data TEXT NOT NULL,  -- Full serialized web state as JSON
    n_beliefs INTEGER,
    n_constraints INTEGER,
    coherence_score REAL,
    snapshot_reason TEXT,  -- "periodic", "pre_major_change", "manual"
    created_at TEXT NOT NULL,
    FOREIGN KEY (web_id) REFERENCES web_metadata(web_id)
);

CREATE INDEX IF NOT EXISTS idx_snapshots_web ON web_snapshots(web_id);

-- Coherence alerts (Expert Panel 5.5)
CREATE TABLE IF NOT EXISTS coherence_alerts (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
    web_id TEXT NOT NULL,
    alert_type TEXT NOT NULL,  -- "sharp_decline", "cumulative_decline", "anomaly"
    severity TEXT NOT NULL,  -- "warning", "critical"
    message TEXT NOT NULL,
    coherence_before REAL,
    coherence_after REAL,
    triggered_by TEXT,
    acknowledged INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY (web_id) REFERENCES web_metadata(web_id)
);

CREATE INDEX IF NOT EXISTS idx_alerts_web ON coherence_alerts(web_id);
CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged ON coherence_alerts(acknowledged);
"""


# =============================================================================
# WEB PERSISTENCE SERVICE (Refined)
# =============================================================================

@dataclass
class MergeResult:
    """Result of merging a belief into the master web."""
    belief_id: str
    merge_type: str  # "new", "update", "conflict"
    old_credence: Optional[float] = None
    new_credence: Optional[float] = None
    conflict_resolved: bool = False
    conflict_resolution: Optional[str] = None
    conflict_type: Optional[ConflictType] = None  # Expert Panel 5.2
    requires_review: bool = False  # Expert Panel 5.2
    auto_resolved: bool = False  # Expert Panel 5.2


@dataclass
class IntegrationReport:
    """Report from integrating a paper's web into master."""
    paper_id: str
    n_beliefs_added: int = 0
    n_beliefs_updated: int = 0
    n_beliefs_conflicted: int = 0
    n_constraints_added: int = 0
    n_bridges_added: int = 0
    coherence_before: Optional[float] = None
    coherence_after: Optional[float] = None
    merge_results: List[MergeResult] = field(default_factory=list)
    alerts: List[CoherenceAlert] = field(default_factory=list)  # Expert Panel 5.5


class WebPersistenceService:
    """
    Persistent storage and accumulation service for Web of Belief.

    Provides:
    - Save/load web state to SQLite
    - Master web accumulation across papers
    - Belief merging with conflict resolution (inverse-variance weighting)
    - Change history and audit trail
    - Coherence dashboard and alerts

    Expert Panel Refinements:
    - Inverse-variance weighting for credence merge (5.3)
    - Structured attribute matching for belief identity (5.2)
    - Coherence dashboard with multiple metrics (5.5)
    - Paper quality weighting (5.4)
    """

    # Decision matrix thresholds (Expert Panel 5.2)
    CREDENCE_GAP_SMALL = 0.1
    CREDENCE_GAP_LARGE = 0.3
    OBSERVATION_RATIO_SIMILAR_MIN = 0.5
    OBSERVATION_RATIO_SIMILAR_MAX = 2.0
    OBSERVATION_RATIO_DISPARATE = 3.0

    # Semantic similarity threshold (Expert Panel 5.2)
    SEMANTIC_SIMILARITY_THRESHOLD = 0.85

    # Alert thresholds (Expert Panel 5.5)
    SHARP_DECLINE_THRESHOLD = 0.1
    ANOMALY_STDDEV_THRESHOLD = 2.0

    def __init__(self, db_path: str = ":memory:"):
        """
        Initialize persistence service.

        Args:
            db_path: Path to SQLite database, or ":memory:" for in-memory
        """
        self.db_path = db_path
        self._is_memory = (db_path == ":memory:")
        self._persistent_conn = None

        if self._is_memory:
            self._persistent_conn = sqlite3.connect(":memory:")
            self._persistent_conn.row_factory = sqlite3.Row
            self._persistent_conn.execute("PRAGMA foreign_keys = ON")

        self._ensure_schema()

    @contextmanager
    def _get_connection(self):
        """Get a database connection with proper settings."""
        if self._is_memory and self._persistent_conn:
            yield self._persistent_conn
        else:
            # Use a short timeout to fail fast if the DB is locked by another
            # connection (e.g., SQLAlchemy session in evaluate_building).
            # The default 5s timeout caused test-suite hangs when multiple
            # tests each waited 5s for the lock to release.
            conn = sqlite3.connect(self.db_path, timeout=0.5)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

    def _ensure_schema(self):
        """Ensure tables exist."""
        with self._get_connection() as conn:
            conn.executescript(WEB_PERSISTENCE_SCHEMA)
            conn.commit()

    def _utc_now(self) -> str:
        """Get current UTC timestamp."""
        return datetime.now(timezone.utc).isoformat()

    # =========================================================================
    # PAPER PUBLICATION METADATA (for scholarly timeline)
    # =========================================================================

    def upsert_paper_publication(
        self,
        paper_id: str,
        publication_year: Optional[int] = None,
        publication_date: Optional[str] = None,
        first_seen_at: Optional[str] = None,
        source: Optional[str] = None
    ) -> None:
        """Insert or update paper publication metadata."""
        now = self._utc_now()
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO paper_publication (
                    paper_id, publication_year, publication_date,
                    first_seen_at, source, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(paper_id) DO UPDATE SET
                    publication_year = COALESCE(excluded.publication_year, paper_publication.publication_year),
                    publication_date = COALESCE(excluded.publication_date, paper_publication.publication_date),
                    first_seen_at = COALESCE(paper_publication.first_seen_at, excluded.first_seen_at),
                    source = COALESCE(excluded.source, paper_publication.source),
                    updated_at = excluded.updated_at
            """, (
                paper_id,
                publication_year,
                publication_date,
                first_seen_at,
                source,
                now,
                now
            ))

    def get_paper_publication(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """Fetch stored publication metadata for a paper."""
        with self._get_connection() as conn:
            row = conn.execute("""
                SELECT paper_id, publication_year, publication_date, first_seen_at, source
                FROM paper_publication
                WHERE paper_id = ?
            """, (paper_id,)).fetchone()
            return dict(row) if row else None

    def list_paper_publications(
        self,
        paper_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """List publication metadata ordered by scholarly time."""
        with self._get_connection() as conn:
            params: Tuple[Any, ...] = ()
            where_clause = ""
            if paper_ids:
                placeholders = ", ".join(["?"] * len(paper_ids))
                where_clause = f"WHERE paper_id IN ({placeholders})"
                params = tuple(paper_ids)

            rows = conn.execute(f"""
                SELECT paper_id, publication_year, publication_date, first_seen_at, source
                FROM paper_publication
                {where_clause}
                ORDER BY
                    COALESCE(
                        publication_date,
                        printf('%04d-01-01', publication_year),
                        '9999-12-31'
                    ),
                    paper_id
            """, params).fetchall()

            return [dict(row) for row in rows]

    # =========================================================================
    # ENTRENCHMENT TRACKING
    # =========================================================================

    def record_entrenchment_snapshots(
        self,
        web_id: str,
        web: WebOfBelief,
        belief_ids: Iterable[str],
        paper_id: Optional[str],
        timeline_type: str,
        as_of_date: Optional[str] = None,
        event_type: str = "snapshot",
        reason: Optional[str] = None
    ) -> None:
        """
        Record entrenchment snapshots for a set of beliefs.

        timeline_type: "system" or "scholarly"
        """
        belief_ids = list(belief_ids)
        if not belief_ids:
            return

        as_of = as_of_date or self._utc_now()
        created_at = self._utc_now()

        with self._get_connection() as conn:
            for belief_id in belief_ids:
                belief = web.beliefs.get(belief_id)
                if not belief:
                    continue

                components = web.get_entrenchment_components(belief_id)
                entrenchment = components["entrenchment"]

                prev = conn.execute("""
                    SELECT entrenchment
                    FROM entrenchment_snapshots
                    WHERE web_id = ? AND belief_id = ? AND timeline_type = ?
                    ORDER BY as_of_date DESC, snapshot_id DESC
                    LIMIT 1
                """, (web_id, belief_id, timeline_type)).fetchone()

                delta = None
                if prev:
                    delta = entrenchment - (prev["entrenchment"] or 0.0)

                conn.execute("""
                    INSERT INTO entrenchment_snapshots (
                        web_id, belief_id, paper_id, timeline_type, as_of_date,
                        entrenchment, connectivity, level_weight, coherence_contrib,
                        constraint_count, status, credence_value, credence_uncertainty,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    web_id,
                    belief_id,
                    paper_id,
                    timeline_type,
                    as_of,
                    entrenchment,
                    components["connectivity"],
                    components["level_weight"],
                    components["coherence_contrib"],
                    components["constraint_count"],
                    belief.status.value if hasattr(belief.status, "value") else str(belief.status),
                    belief.credence.value,
                    belief.credence.uncertainty,
                    created_at
                ))

                if delta is not None:
                    conn.execute("""
                        INSERT INTO entrenchment_events (
                            web_id, belief_id, paper_id, timeline_type,
                            occurred_at, delta, event_type, reason,
                            source_paper_id, constraint_id, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        web_id,
                        belief_id,
                        paper_id,
                        timeline_type,
                        as_of,
                        delta,
                        event_type,
                        reason,
                        paper_id,
                        None,
                        created_at
                    ))

    def get_entrenchment_history(
        self,
        belief_id: str,
        web_id: Optional[str] = None,
        timeline_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get entrenchment history for a belief.

        Args:
            belief_id: The belief to query
            web_id: Optional web ID filter
            timeline_type: "system" or "scholarly" filter
            start_date: Optional start date (ISO format)
            end_date: Optional end date (ISO format)
            limit: Maximum records to return

        Returns:
            List of entrenchment snapshot records ordered by date
        """
        with self._get_connection() as conn:
            query = "SELECT * FROM entrenchment_snapshots WHERE belief_id = ?"
            params: List[Any] = [belief_id]

            if web_id:
                query += " AND web_id = ?"
                params.append(web_id)

            if timeline_type:
                query += " AND timeline_type = ?"
                params.append(timeline_type)

            if start_date:
                query += " AND as_of_date >= ?"
                params.append(start_date)

            if end_date:
                query += " AND as_of_date <= ?"
                params.append(end_date)

            query += " ORDER BY as_of_date ASC, snapshot_id ASC LIMIT ?"
            params.append(limit)

            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def get_entrenchment_events(
        self,
        belief_id: Optional[str] = None,
        web_id: Optional[str] = None,
        timeline_type: Optional[str] = None,
        event_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get entrenchment change events.

        Args:
            belief_id: Optional belief ID filter
            web_id: Optional web ID filter
            timeline_type: "system" or "scholarly" filter
            event_type: Event type filter (e.g., "snapshot", "historical_replay")
            start_date: Optional start date
            end_date: Optional end date
            limit: Maximum records

        Returns:
            List of entrenchment event records
        """
        with self._get_connection() as conn:
            query = "SELECT * FROM entrenchment_events WHERE 1=1"
            params: List[Any] = []

            if belief_id:
                query += " AND belief_id = ?"
                params.append(belief_id)

            if web_id:
                query += " AND web_id = ?"
                params.append(web_id)

            if timeline_type:
                query += " AND timeline_type = ?"
                params.append(timeline_type)

            if event_type:
                query += " AND event_type = ?"
                params.append(event_type)

            if start_date:
                query += " AND occurred_at >= ?"
                params.append(start_date)

            if end_date:
                query += " AND occurred_at <= ?"
                params.append(end_date)

            query += " ORDER BY occurred_at DESC, event_id DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def get_latest_entrenchment(
        self,
        belief_id: str,
        web_id: Optional[str] = None,
        timeline_type: str = "system"
    ) -> Optional[Dict[str, Any]]:
        """Get the most recent entrenchment snapshot for a belief."""
        with self._get_connection() as conn:
            query = """
                SELECT * FROM entrenchment_snapshots
                WHERE belief_id = ? AND timeline_type = ?
            """
            params: List[Any] = [belief_id, timeline_type]

            if web_id:
                query += " AND web_id = ?"
                params.append(web_id)

            query += " ORDER BY as_of_date DESC, snapshot_id DESC LIMIT 1"

            row = conn.execute(query, params).fetchone()
            return dict(row) if row else None

    def compare_timeline_entrenchment(
        self,
        belief_id: str,
        web_id: Optional[str] = None,
        as_of_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare entrenchment between system and scholarly timelines.

        Returns dict with both timeline values and divergence metrics.
        """
        system = self.get_latest_entrenchment(belief_id, web_id, "system")
        scholarly = self.get_latest_entrenchment(belief_id, web_id, "scholarly")

        system_val = system["entrenchment"] if system else None
        scholarly_val = scholarly["entrenchment"] if scholarly else None

        divergence = None
        if system_val is not None and scholarly_val is not None:
            divergence = abs(system_val - scholarly_val)

        return {
            "belief_id": belief_id,
            "system_entrenchment": system_val,
            "scholarly_entrenchment": scholarly_val,
            "divergence": divergence,
            "system_snapshot": system,
            "scholarly_snapshot": scholarly
        }

    def get_entrenchment_trajectory(
        self,
        belief_id: str,
        timeline_type: str = "system",
        web_id: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get entrenchment trajectory with trend analysis.

        Returns trajectory data including volatility metrics.
        """
        history = self.get_entrenchment_history(
            belief_id=belief_id,
            web_id=web_id,
            timeline_type=timeline_type,
            limit=limit
        )

        if not history:
            return {
                "belief_id": belief_id,
                "timeline_type": timeline_type,
                "data_points": [],
                "volatility": None,
                "trend": None,
                "latest": None
            }

        values = [h["entrenchment"] for h in history if h["entrenchment"] is not None]

        volatility = None
        trend = None
        if len(values) >= 2:
            # Calculate volatility (standard deviation of changes)
            deltas = [values[i] - values[i-1] for i in range(1, len(values))]
            if deltas:
                mean_delta = sum(deltas) / len(deltas)
                variance = sum((d - mean_delta) ** 2 for d in deltas) / len(deltas)
                volatility = variance ** 0.5

            # Simple linear trend (positive = increasing, negative = decreasing)
            trend = (values[-1] - values[0]) / len(values) if len(values) > 1 else 0

        return {
            "belief_id": belief_id,
            "timeline_type": timeline_type,
            "data_points": [
                {"date": h["as_of_date"], "entrenchment": h["entrenchment"]}
                for h in history
            ],
            "volatility": volatility,
            "trend": trend,
            "latest": values[-1] if values else None,
            "n_snapshots": len(history)
        }

    # =========================================================================
    # WEB METADATA OPERATIONS
    # =========================================================================

    def create_web(
        self,
        web_id: str,
        name: str,
        description: Optional[str] = None,
        is_master: bool = False
    ) -> str:
        """Create a new web entry."""
        now = self._utc_now()
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO web_metadata (web_id, name, description, created_at, updated_at, is_master)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (web_id, name, description, now, now, 1 if is_master else 0))
        logger.info(f"Created web: {web_id} (master={is_master})")
        return web_id

    def get_master_web_id(self) -> Optional[str]:
        """Get the master web ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT web_id FROM web_metadata WHERE is_master = 1 LIMIT 1"
            ).fetchone()
            return row['web_id'] if row else None

    def create_or_get_master_web(self) -> str:
        """Get existing master web or create one."""
        master_id = self.get_master_web_id()
        if master_id:
            return master_id

        master_id = "master:web:accumulated"
        self.create_web(
            web_id=master_id,
            name="Master Accumulated Web",
            description="Accumulated web of belief from all processed papers",
            is_master=True
        )
        return master_id

    # =========================================================================
    # BELIEF OPERATIONS
    # =========================================================================

    def save_belief(self, web_id: str, belief: Belief, entrenchment: Optional[float] = None) -> None:
        """
        Save a belief to the database.

        Args:
            web_id: The web ID to save to
            belief: The belief to save
            entrenchment: V23.0.0 - Computed entrenchment value (emergent, not stored).
                         If None, uses _legacy_entrenchment for backward compatibility.
        """
        now = self._utc_now()

        # V23.0.0: Entrenchment is emergent, not stored on Belief. Use provided value or legacy.
        entrenchment_value = entrenchment if entrenchment is not None else getattr(belief, '_legacy_entrenchment', 0.5)

        # Extract credence value directly from the object
        credence_value = belief.credence.value if hasattr(belief.credence, 'value') else 0.5
        credence_uncertainty = getattr(belief.credence, 'uncertainty', 0.4)
        credence_n_supporting = getattr(belief.credence, 'n_supporting', 0)
        credence_n_contradicting = getattr(belief.credence, 'n_contradicting', 0)
        credence_n_observations = getattr(belief.credence, 'n_observations', 0)

        # Sprint 6: Serialize scope conditions
        scope_json = None
        if hasattr(belief, 'scope') and belief.scope is not None:
            scope_json = json.dumps(belief.scope.to_dict())

        # ARCH-4 V24: Serialize v2 epistemic fields as JSON
        epistemic_v2_json = None
        v2_data = {}
        if hasattr(belief, 'content_v2') and belief.content_v2 is not None:
            v2_data['content_v2'] = belief.content_v2.to_dict() if hasattr(belief.content_v2, 'to_dict') else belief.content_v2
        if hasattr(belief, 'status_v2') and belief.status_v2 is not None:
            v2_data['status_v2'] = belief.status_v2.to_dict() if hasattr(belief.status_v2, 'to_dict') else belief.status_v2
        if hasattr(belief, 'provenance_v2') and belief.provenance_v2 is not None:
            v2_data['provenance_v2'] = belief.provenance_v2.to_dict() if hasattr(belief.provenance_v2, 'to_dict') else belief.provenance_v2
        if v2_data:
            epistemic_v2_json = json.dumps(v2_data)

        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO beliefs (
                    belief_id, web_id, content, level, status,
                    credence_value, credence_uncertainty, credence_n_supporting,
                    credence_n_contradicting, credence_n_observations,
                    theory_id, entrenchment, domain, attribute_id, outcome_type,
                    scope, environment_id, outcome_id, evidence_cluster_id,
                    tags, paper_ids, epistemic_v2, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                belief.belief_id,
                web_id,
                belief.content,
                belief.level.value if hasattr(belief.level, 'value') else str(belief.level),
                belief.status.value if hasattr(belief.status, 'value') else str(belief.status),
                credence_value,
                credence_uncertainty,
                credence_n_supporting,
                credence_n_contradicting,
                credence_n_observations,
                belief.theory_id,
                entrenchment_value,
                getattr(belief, 'domain', None),
                getattr(belief, 'attribute_id', None),  # Expert Panel 5.2
                getattr(belief, 'outcome_type', None),  # Expert Panel 5.2
                scope_json,  # Sprint 6: ScopeConditions
                getattr(belief, 'environment_id', None),  # Sprint 7
                getattr(belief, 'outcome_id', None),  # Sprint 7
                getattr(belief, 'evidence_cluster_id', None),  # Sprint 8
                json.dumps(getattr(belief, 'tags', [])),
                json.dumps(getattr(belief, 'paper_ids', [])),
                epistemic_v2_json,  # ARCH-4 V24: v2 epistemic fields
                belief.created_at.isoformat() if hasattr(belief, 'created_at') and belief.created_at else now,
                now
            ))

    def load_belief(self, belief_id: str, web_id: str) -> Optional[Belief]:
        """Load a belief from the database."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM beliefs WHERE belief_id = ? AND web_id = ?",
                (belief_id, web_id)
            ).fetchone()

            if not row:
                return None

            return self._row_to_belief(row)

    def _row_to_belief(self, row: sqlite3.Row) -> Belief:
        """Convert database row to Belief object."""
        raw_level = row['level'] if 'level' in row.keys() else None
        if raw_level is None:
            belief_level = EpistemicLevel.EMPIRICAL
        else:
            level_text = str(raw_level).strip().lower()
            legacy_level_map = {
                "evidence": EpistemicLevel.EMPIRICAL,
                "observation": EpistemicLevel.OBSERVATIONAL,
                "theory": EpistemicLevel.THEORETICAL,
                "generalization": EpistemicLevel.INTERMEDIATE,
            }
            try:
                belief_level = EpistemicLevel(level_text)
            except ValueError:
                belief_level = legacy_level_map.get(level_text, EpistemicLevel.EMPIRICAL)

        raw_status = row['status'] if 'status' in row.keys() else None
        if raw_status is None:
            belief_status = BeliefStatus.STUB
        else:
            status_text = str(raw_status).strip().lower()
            legacy_status_map = {
                "active": BeliefStatus.ESTABLISHED,
                "inactive": BeliefStatus.TENTATIVE,
                "deprecated": BeliefStatus.ANOMALOUS,
            }
            try:
                belief_status = BeliefStatus(status_text)
            except ValueError:
                belief_status = legacy_status_map.get(status_text, BeliefStatus.STUB)

        credence = Credence(
            value=row['credence_value'],
            uncertainty=row['credence_uncertainty'],
            n_supporting=row['credence_n_supporting'] or 0,
            n_contradicting=row['credence_n_contradicting'] or 0,
            n_observations=row['credence_n_observations'] or 0
        )

        # Sprint 6: Deserialize scope conditions
        scope = None
        if 'scope' in row.keys() and row['scope']:
            scope = ScopeConditions.from_dict(json.loads(row['scope']))

        belief = Belief(
            belief_id=row['belief_id'],
            content=row['content'],
            level=belief_level,
            status=belief_status,
            credence=credence,
            theory_id=row['theory_id'],
            _legacy_entrenchment=row['entrenchment'] or 0.3,
            domain=row['domain'],
            tags=json.loads(row['tags']) if row['tags'] else [],
            paper_ids=json.loads(row['paper_ids']) if row['paper_ids'] else [],
            scope=scope,  # Sprint 6
            environment_id=row['environment_id'] if 'environment_id' in row.keys() else None,  # Sprint 7
            outcome_id=row['outcome_id'] if 'outcome_id' in row.keys() else None,  # Sprint 7
            evidence_cluster_id=row['evidence_cluster_id'] if 'evidence_cluster_id' in row.keys() else None  # Sprint 8
        )

        # Add structured attributes for identity matching (Expert Panel 5.2)
        belief.attribute_id = row['attribute_id'] if 'attribute_id' in row.keys() else None
        belief.outcome_type = row['outcome_type'] if 'outcome_type' in row.keys() else None

        # ARCH-4 V24: Deserialize v2 epistemic fields
        if 'epistemic_v2' in row.keys() and row['epistemic_v2']:
            try:
                v2_data = json.loads(row['epistemic_v2'])
                if 'content_v2' in v2_data:
                    from src.models.propositional_content import PropositionalContent
                    belief.content_v2 = PropositionalContent.from_dict(v2_data['content_v2'])
                if 'status_v2' in v2_data:
                    from src.models.epistemic_status import EpistemicStatus
                    belief.status_v2 = EpistemicStatus.from_dict(v2_data['status_v2'])
                if 'provenance_v2' in v2_data:
                    from src.models.provenance import Provenance
                    belief.provenance_v2 = Provenance.from_dict(v2_data['provenance_v2'])
            except Exception as e:
                logger.debug(f"Non-critical: {e}")  # Graceful degradation if v2 parsing fails

        return belief

    def get_beliefs_for_web(self, web_id: str) -> List[Belief]:
        """Get all beliefs for a web."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM beliefs WHERE web_id = ?",
                (web_id,)
            ).fetchall()
            return [self._row_to_belief(r) for r in rows]

    # =========================================================================
    # CONSTRAINT OPERATIONS
    # =========================================================================

    def save_constraint(self, web_id: str, constraint: Constraint) -> None:
        """Save a constraint to the database."""
        now = self._utc_now()

        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO constraints (
                    constraint_id, web_id, source_id, target_id, constraint_type,
                    strength, bidirectional, evidence_ids, warrant_type, provenance,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                constraint.constraint_id,
                web_id,
                constraint.source_id,
                constraint.target_id,
                constraint.constraint_type.value if hasattr(constraint.constraint_type, 'value') else str(constraint.constraint_type),
                constraint.strength,
                1 if getattr(constraint, 'bidirectional', False) else 0,
                json.dumps(getattr(constraint, 'evidence_ids', [])),
                getattr(constraint, 'warrant_type', None),
                getattr(constraint, 'provenance', None),
                now
            ))

    def _row_to_constraint(self, row: sqlite3.Row) -> Constraint:
        """Convert database row to Constraint object."""
        raw_constraint_type = row['constraint_type'] if 'constraint_type' in row.keys() else "supports"
        constraint_type = convert_legacy_constraint_type(str(raw_constraint_type))
        constraint = Constraint(
            constraint_id=row['constraint_id'],
            source_id=row['source_id'],
            target_id=row['target_id'],
            constraint_type=constraint_type,
            strength=row['strength'],
            bidirectional=bool(row['bidirectional']),
            evidence_ids=json.loads(row['evidence_ids']) if row['evidence_ids'] else []
        )
        # Preserve audit metadata so round-trips do not erase provenance fields.
        if 'warrant_type' in row.keys() and row['warrant_type'] is not None:
            constraint.warrant_type = row['warrant_type']  # type: ignore[attr-defined]
        if 'provenance' in row.keys() and row['provenance'] is not None:
            constraint.provenance = row['provenance']  # type: ignore[attr-defined]
        return constraint

    def get_constraints_for_web(self, web_id: str) -> List[Constraint]:
        """Get all constraints for a web."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM constraints WHERE web_id = ?",
                (web_id,)
            ).fetchall()
            return [self._row_to_constraint(r) for r in rows]

    # =========================================================================
    # BRIDGE OPERATIONS
    # =========================================================================

    def save_bridge(self, web_id: str, bridge: 'BridgeWarrant') -> None:
        """Save a bridge warrant to the database."""
        if not BRIDGE_AVAILABLE:
            return

        now = self._utc_now()

        failure_record_json = None
        if bridge.failure_record:
            failure_record_json = json.dumps(bridge.failure_record.to_dict())

        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO bridges (
                    bridge_id, web_id, source_domain, target_domain, bridge_type,
                    warrant_statement, assumed_mechanism, confidence, confidence_source,
                    status, source_beliefs, target_beliefs, evidence_for, evidence_against,
                    failure_record, voi_flag, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                bridge.bridge_id,
                web_id,
                bridge.source_domain,
                bridge.target_domain,
                bridge.bridge_type.value,
                bridge.warrant_statement,
                bridge.assumed_mechanism,
                bridge.confidence,
                bridge.confidence_source.value,
                bridge.status.value,
                json.dumps(bridge.source_beliefs),
                json.dumps(bridge.target_beliefs),
                json.dumps(bridge.evidence_for),
                json.dumps(bridge.evidence_against),
                failure_record_json,
                1 if bridge.voi_flag else 0,
                bridge.provenance.created_at.isoformat(),
                now
            ))

    def get_bridges_for_web(self, web_id: str) -> List['BridgeWarrant']:
        """Get all bridges for a web."""
        if not BRIDGE_AVAILABLE:
            return []

        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM bridges WHERE web_id = ?",
                (web_id,)
            ).fetchall()

            bridges = []
            for row in rows:
                # Reconstruct BridgeWarrant from row
                from src.services.bridge_warrants import BridgeWarrant, FailureRecord, Provenance

                failure_record = None
                if row['failure_record']:
                    failure_record = FailureRecord.from_dict(json.loads(row['failure_record']))

                bridge = BridgeWarrant(
                    bridge_id=row['bridge_id'],
                    source_domain=row['source_domain'],
                    target_domain=row['target_domain'],
                    bridge_type=BridgeType(row['bridge_type']),
                    warrant_statement=row['warrant_statement'],
                    assumed_mechanism=row['assumed_mechanism'],
                    confidence=row['confidence'],
                    confidence_source=ConfidenceSource(row['confidence_source']),
                    status=BridgeStatus(row['status']),
                    source_beliefs=json.loads(row['source_beliefs']) if row['source_beliefs'] else [],
                    target_beliefs=json.loads(row['target_beliefs']) if row['target_beliefs'] else [],
                    evidence_for=json.loads(row['evidence_for']) if row['evidence_for'] else [],
                    evidence_against=json.loads(row['evidence_against']) if row['evidence_against'] else [],
                    failure_record=failure_record,
                    voi_flag=bool(row['voi_flag']),
                    provenance=Provenance(
                        created_at=datetime.fromisoformat(row['created_at']),
                        last_updated=datetime.fromisoformat(row['updated_at'])
                    )
                )
                bridges.append(bridge)

            return bridges

    # =========================================================================
    # PAPER QUALITY (Expert Panel 5.4)
    # =========================================================================

    def save_paper_quality(
        self,
        paper_id: str,
        sample_size_score: Optional[float] = None,
        methodology_score: Optional[float] = None,
        journal_impact_factor: Optional[float] = None,
        citation_count: Optional[int] = None,
        preregistered: bool = False,
        replication_status: str = "original",
        # Sprint 2.6 Track B: New P-QW panel fields
        institution: Optional[str] = None,
        author_h_index: Optional[int] = None,
        publication_year: Optional[int] = None,
        ecological_validity_score: Optional[float] = None,
    ) -> float:
        """
        Save paper quality metrics and compute overall quality.

        Sprint 2.6 Track B (P-QW Panel) updates:
        - Q2: Institution tier weighting (reduced to 0.12)
        - Q4: Revised component weights
        - Q5: Citation velocity instead of raw citation count
        - Q6: Piecewise quality→entrenchment available via quality_to_entrenchment()

        Returns the computed overall quality score.
        """
        now = self._utc_now()

        # Sprint 2.6 Track B: Use new QUALITY_WEIGHTS per P-QW Q4
        weights = []
        scores = []

        # Methodology (Q4: 0.28)
        if methodology_score is not None:
            weights.append(QUALITY_WEIGHTS['methodology'])
            scores.append(methodology_score)

        # Citations - use citation velocity if publication_year available (Q5)
        if citation_count is not None:
            if publication_year is not None:
                # Q5: Use citation velocity instead of raw count
                velocity = citation_velocity(citation_count, publication_year)
                # Normalize velocity (assuming ~50 citations/year is excellent)
                normalized_velocity = min(1.0, velocity / 50.0)
                weights.append(QUALITY_WEIGHTS['citations'])
                scores.append(normalized_velocity)
            else:
                # Fallback: normalize raw citation count
                normalized_citations = min(1.0, citation_count / 500.0)
                weights.append(QUALITY_WEIGHTS['citations'])
                scores.append(normalized_citations)

        # Institution (Q2: reduced to 0.12)
        if institution is not None:
            tier = get_institution_tier(institution)
            inst_score = institution_tier_to_score(tier)
            weights.append(QUALITY_WEIGHTS['institution'])
            scores.append(inst_score)

        # Author quality via h-index
        if author_h_index is not None:
            # Normalize h-index (assuming h=50 is excellent)
            normalized_h = min(1.0, author_h_index / 50.0)
            weights.append(QUALITY_WEIGHTS['author_quality'])
            scores.append(normalized_h)

        # Preregistration (Q4: 0.10)
        if preregistered:
            weights.append(QUALITY_WEIGHTS['preregistration'])
            scores.append(1.0)

        # Sample size (Q4: 0.10)
        if sample_size_score is not None:
            weights.append(QUALITY_WEIGHTS['sample_size'])
            scores.append(sample_size_score)

        # Ecological validity (Q4: new, 0.04)
        if ecological_validity_score is not None:
            weights.append(QUALITY_WEIGHTS['ecological_validity'])
            scores.append(ecological_validity_score)

        # Journal impact factor (legacy support, uses citations weight if no citations)
        if journal_impact_factor is not None and citation_count is None:
            normalized_jif = min(1.0, journal_impact_factor / 50.0)
            weights.append(QUALITY_WEIGHTS['citations'])
            scores.append(normalized_jif)

        # Replication status adjustment (unchanged)
        replication_multiplier = 1.0
        if replication_status == "successful_replication":
            replication_multiplier = 2.0
        elif replication_status == "failed_replication":
            replication_multiplier = 0.3

        if weights:
            overall_quality = sum(w * s for w, s in zip(weights, scores)) / sum(weights)
            overall_quality *= replication_multiplier
            overall_quality = min(1.0, overall_quality)  # Cap at 1.0
        else:
            overall_quality = 0.5  # Default

        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO paper_quality (
                    paper_id, sample_size_score, methodology_score,
                    journal_impact_factor, citation_count, preregistered,
                    replication_status, overall_quality,
                    institution, author_h_index, publication_year, ecological_validity_score,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                paper_id, sample_size_score, methodology_score,
                journal_impact_factor, citation_count, 1 if preregistered else 0,
                replication_status, overall_quality,
                institution, author_h_index, publication_year, ecological_validity_score,
                now, now
            ))

        return overall_quality

    def get_paper_quality(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """Get quality metrics for a paper."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM paper_quality WHERE paper_id = ?",
                (paper_id,)
            ).fetchone()

            if not row:
                return None

            return dict(row)

    # =========================================================================
    # WEB SNAPSHOTS (Expert Panel 5.1)
    # =========================================================================

    def create_snapshot(
        self,
        web_id: str,
        reason: str = "periodic"
    ) -> int:
        """
        Create a full snapshot of web state for disaster recovery.

        Args:
            web_id: Web to snapshot
            reason: Why snapshot was created ("periodic", "pre_major_change", "manual")

        Returns:
            snapshot_id
        """
        web, bridges = self.load_web(web_id)
        if not web:
            raise ValueError(f"Web {web_id} not found")

        # Serialize complete state
        snapshot_data = {
            "beliefs": {bid: b.to_dict() for bid, b in web.beliefs.items()},
            "constraints": {cid: c.to_dict() for cid, c in web.constraints.items()},
            "bridges": [b.to_dict() for b in (bridges.all() if bridges else [])]
        }

        coherence = web.coherence_score() if hasattr(web, 'coherence_score') else 0.0

        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO web_snapshots (
                    web_id, snapshot_data, n_beliefs, n_constraints,
                    coherence_score, snapshot_reason, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                web_id,
                json.dumps(snapshot_data),
                len(web.beliefs),
                len(web.constraints),
                coherence,
                reason,
                self._utc_now()
            ))
            return cursor.lastrowid

    def restore_from_snapshot(self, snapshot_id: int) -> Tuple[Optional[WebOfBelief], Optional['BridgeRegistry']]:
        """
        Restore a web from a snapshot.

        Note: This creates a new in-memory web; use save_web to persist.
        """
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM web_snapshots WHERE snapshot_id = ?",
                (snapshot_id,)
            ).fetchone()

            if not row:
                return None, None

        snapshot_data = json.loads(row['snapshot_data'])

        web = create_neuroarchitecture_web()
        web.beliefs.clear()
        web.constraints.clear()

        # Restore beliefs
        for belief_dict in snapshot_data.get("beliefs", {}).values():
            belief = Belief.from_dict(belief_dict)
            web.beliefs[belief.belief_id] = belief

        # Restore constraints
        for constraint_dict in snapshot_data.get("constraints", {}).values():
            constraint = Constraint.from_dict(constraint_dict)
            web.constraints[constraint.constraint_id] = constraint

        # Restore bridges
        bridge_registry = None
        if BRIDGE_AVAILABLE and snapshot_data.get("bridges"):
            bridge_registry = BridgeRegistry()
            for bridge_dict in snapshot_data["bridges"]:
                bridge = BridgeWarrant.from_dict(bridge_dict)
                bridge_registry.add(bridge)

        return web, bridge_registry

    # =========================================================================
    # WEB SAVE/LOAD
    # =========================================================================

    def save_web(
        self,
        web: WebOfBelief,
        web_id: str,
        name: Optional[str] = None,
        is_master: bool = False,
        bridge_registry: Optional['BridgeRegistry'] = None
    ) -> None:
        """
        Save complete web state to database.

        Args:
            web: WebOfBelief instance to save
            web_id: Unique identifier for this web
            name: Human-readable name
            is_master: Whether this is the master accumulated web
            bridge_registry: Optional bridge registry to save
        """
        now = self._utc_now()

        with self._get_connection() as conn:
            # Create or update web metadata
            existing = conn.execute(
                "SELECT web_id FROM web_metadata WHERE web_id = ?",
                (web_id,)
            ).fetchone()

            coherence = web.coherence_score() if hasattr(web, 'coherence_score') else 0.0

            if existing:
                conn.execute("""
                    UPDATE web_metadata SET
                        updated_at = ?,
                        version = version + 1,
                        n_beliefs = ?,
                        n_constraints = ?,
                        coherence_score = ?
                    WHERE web_id = ?
                """, (now, len(web.beliefs), len(web.constraints), coherence, web_id))
            else:
                conn.execute("""
                    INSERT INTO web_metadata (
                        web_id, name, description, created_at, updated_at,
                        n_beliefs, n_constraints, coherence_score, is_master
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    web_id, name or web_id, None, now, now,
                    len(web.beliefs), len(web.constraints), coherence,
                    1 if is_master else 0
                ))

        # Save beliefs
        for belief in web.beliefs.values():
            self.save_belief(web_id, belief)

        # Save constraints
        for constraint in web.constraints.values():
            self.save_constraint(web_id, constraint)

        # Save bridges
        if bridge_registry and BRIDGE_AVAILABLE:
            for bridge in bridge_registry.all():
                self.save_bridge(web_id, bridge)

        # Record coherence history
        self._record_coherence(web_id, coherence, len(web.beliefs), len(web.constraints), "save")

        logger.info(f"Saved web {web_id}: {len(web.beliefs)} beliefs, {len(web.constraints)} constraints")

    def load_web(self, web_id: str) -> Tuple[Optional[WebOfBelief], Optional['BridgeRegistry']]:
        """
        Load complete web state from database.

        Args:
            web_id: Web identifier to load

        Returns:
            (WebOfBelief, BridgeRegistry) or (None, None) if not found
        """
        with self._get_connection() as conn:
            metadata = conn.execute(
                "SELECT * FROM web_metadata WHERE web_id = ?",
                (web_id,)
            ).fetchone()

            if not metadata:
                return None, None

        # Create web and load beliefs
        web = create_neuroarchitecture_web()

        # Clear default beliefs
        web.beliefs.clear()
        web.constraints.clear()

        # Load beliefs
        for belief in self.get_beliefs_for_web(web_id):
            web.beliefs[belief.belief_id] = belief

        # Load constraints
        for constraint in self.get_constraints_for_web(web_id):
            web.constraints[constraint.constraint_id] = constraint

        # Load bridges
        bridge_registry = None
        if BRIDGE_AVAILABLE:
            bridge_registry = BridgeRegistry()
            for bridge in self.get_bridges_for_web(web_id):
                bridge_registry.add(bridge)

        logger.info(f"Loaded web {web_id}: {len(web.beliefs)} beliefs, {len(web.constraints)} constraints")

        return web, bridge_registry

    # =========================================================================
    # BELIEF IDENTITY (Expert Panel 5.2)
    # =========================================================================

    def _beliefs_same_content(self, b1: Belief, b2: Belief) -> bool:
        """
        Check if two beliefs represent the same claim.

        Expert Panel 5.2: Two-stage identity check:
        1. High string similarity (for exact/near-exact matches)
        2. Structured attribute matching (theory_id, attribute_id, outcome_type)
        """
        # Normalize content
        c1 = b1.content.lower().strip()
        c2 = b2.content.lower().strip()

        # Exact match
        if c1 == c2:
            return True

        # Check string similarity first
        from difflib import SequenceMatcher
        string_similarity = SequenceMatcher(None, c1, c2).ratio()

        # High string similarity - likely same
        if string_similarity > 0.9:
            return True

        # Moderate similarity - check structured attributes
        if string_similarity > 0.7:
            # Check structured attributes match (Expert Panel 5.2)
            attr_match = self._structured_attributes_match(b1, b2)
            if attr_match:
                return True

        # Lower similarity - only match if all structured attributes align
        if string_similarity > 0.5:
            # Need strong attribute match
            if (b1.theory_id == b2.theory_id and b1.theory_id is not None and
                getattr(b1, 'attribute_id', None) == getattr(b2, 'attribute_id', None) and
                getattr(b1, 'attribute_id', None) is not None):
                return True

        return False

    def _structured_attributes_match(self, b1: Belief, b2: Belief) -> bool:
        """
        Check if beliefs have matching structured attributes.

        Per Expert Panel 5.2: Compare theory_id, attribute_id, outcome_type.
        """
        matches = 0
        checks = 0

        # Theory match
        if b1.theory_id and b2.theory_id:
            checks += 1
            if b1.theory_id == b2.theory_id:
                matches += 1

        # Attribute ID match
        attr1 = getattr(b1, 'attribute_id', None)
        attr2 = getattr(b2, 'attribute_id', None)
        if attr1 and attr2:
            checks += 1
            if attr1 == attr2:
                matches += 1

        # Outcome type match
        out1 = getattr(b1, 'outcome_type', None)
        out2 = getattr(b2, 'outcome_type', None)
        if out1 and out2:
            checks += 1
            if out1 == out2:
                matches += 1

        # Need at least 2 matching attributes
        return checks >= 2 and matches >= 2

    def _scopes_overlap(self, s1: Optional[ScopeConditions], s2: Optional[ScopeConditions]) -> bool:
        """
        Check if two scope conditions overlap (per Cartwright).

        Per expert panel: Any dimension mismatch blocks GENUINE_CONTRADICTION.

        Panel Fix 3 (Cartwright): Unknown scope ≠ Universal scope.
        - If scope_specified=True and a dimension is None: truly universal for that dimension
        - If scope_specified=False and a dimension is None: unknown for that dimension
        - Unknown dimensions should be treated charitably (assume possible overlap)
          but with lower confidence than specified dimensions.

        Returns True if scopes overlap (could apply to same population/context).
        """
        # If either scope is None, treat as universal (overlaps with everything)
        if s1 is None or s2 is None:
            return True

        # Panel Fix 3: Handle scope_specified field
        s1_specified = getattr(s1, 'scope_specified', False)
        s2_specified = getattr(s2, 'scope_specified', False)

        # If neither scope was explicitly specified, be charitable - assume overlap
        # (This is the "both unknown" case - we can't determine non-overlap)
        if not s1_specified and not s2_specified:
            return True

        # Check each dimension - if both specified and different, no overlap
        for field_name in ['population', 'setting', 'duration', 'measurement', 'geography']:
            v1 = getattr(s1, field_name, None)
            v2 = getattr(s2, field_name, None)

            # Panel Fix 3: Only count as "universal" if scope was specified
            # If scope was not specified, treat None as "unknown" not "universal"
            v1_is_universal = (v1 is None) and s1_specified
            v2_is_universal = (v2 is None) and s2_specified
            v1_is_unknown = (v1 is None) and not s1_specified
            v2_is_unknown = (v2 is None) and not s2_specified

            # If both have explicit values and they don't match, no overlap
            if v1 and v2 and not self._values_compatible(v1, v2):
                return False

            # If one is explicit and one is truly universal, they overlap
            # If one is explicit and one is unknown, be charitable (assume overlap)
            # Only fail overlap if both are explicit and incompatible (handled above)

        return True

    def _values_compatible(self, v1: str, v2: str) -> bool:
        """
        Check if scope values are compatible (could apply to same case).

        Per expert panel (Cartwright): Exact match or hierarchical compatibility.
        """
        # Exact match
        if v1.lower() == v2.lower():
            return True

        # Hierarchical compatibility - child-parent relationships
        hierarchies = {
            # Population hierarchies
            'healthy_adults': ['adults', 'healthy'],
            'clinical_adults': ['adults', 'clinical'],
            'healthy_children': ['children', 'healthy'],
            'clinical_children': ['children', 'clinical'],
            'adolescents': ['children', 'adults'],  # Overlaps with both
            'older_adults': ['adults'],
            'general': ['adults', 'children', 'clinical', 'healthy'],  # Universal

            # Setting hierarchies
            'field_natural': ['field', 'natural'],
            'field_structured': ['field'],
            'lab_vr': ['lab', 'simulated'],
            'lab_photos': ['lab'],
            'lab_video': ['lab'],

            # Duration hierarchies
            'single_exposure': ['acute'],
            'repeated_exposure': ['chronic'],
        }

        v1_lower = v1.lower()
        v2_lower = v2.lower()

        # Check if v1 is parent of v2 or vice versa
        if v1_lower in hierarchies.get(v2_lower, []):
            return True
        if v2_lower in hierarchies.get(v1_lower, []):
            return True

        return False

    def _is_precision_boundary(self, b1: Belief, b2: Belief) -> bool:
        """
        Check if conflict is a precision boundary (same direction, different magnitude).

        Per expert panel (Cartwright): Not a true conflict - just precision difference.
        """
        # Check if same effect direction
        same_direction = self._same_effect_direction(b1.content, b2.content)
        if not same_direction:
            return False

        # Check if credences differ by meaningful amount (0.3 threshold)
        credence_diff = abs(b1.credence.value - b2.credence.value)
        return credence_diff >= 0.1 and credence_diff < 0.3

    def _same_effect_direction(self, content1: str, content2: str) -> bool:
        """Check if two belief contents claim the same effect direction."""
        c1 = content1.lower()
        c2 = content2.lower()

        positive_terms = {"increase", "improve", "enhance", "promote", "facilitate", "positive", "benefit", "help"}
        negative_terms = {"decrease", "reduce", "impair", "inhibit", "negative", "worsen", "harm", "hinder"}

        b1_positive = any(term in c1 for term in positive_terms)
        b1_negative = any(term in c1 for term in negative_terms)
        b2_positive = any(term in c2 for term in positive_terms)
        b2_negative = any(term in c2 for term in negative_terms)

        # Same direction if both positive or both negative
        return (b1_positive and b2_positive) or (b1_negative and b2_negative)

    def _get_effect_direction(self, content: str) -> Optional[str]:
        """
        Get the effect direction from belief content.

        Sprint 7 (Bates): Used for antonym equivalence checking.

        Returns:
            "positive", "negative", or None if unclear
        """
        c = content.lower()
        positive_terms = {"increase", "improve", "enhance", "promote", "facilitate", "positive", "benefit", "help"}
        negative_terms = {"decrease", "reduce", "impair", "inhibit", "negative", "worsen", "harm", "hinder"}

        is_positive = any(term in c for term in positive_terms)
        is_negative = any(term in c for term in negative_terms)

        if is_positive and not is_negative:
            return "positive"
        elif is_negative and not is_positive:
            return "negative"
        return None

    def _get_environment_id(self, belief: Belief) -> Optional[str]:
        """
        Extract environment ID from belief.

        Sprint 7 (Bates): Resolve environment term from content using taxonomy.

        Returns:
            Canonical environment ID or None
        """
        # First check if belief has explicit environment_id attribute
        if hasattr(belief, 'environment_id') and belief.environment_id:
            return belief.environment_id

        # Otherwise, try to resolve from content using taxonomy
        if ENVIRONMENT_TAXONOMY_AVAILABLE:
            match = resolve_environment_term(belief.content)
            if match:
                return match.environment_id

        return None

    def _check_antonym_equivalence(self, b1: Belief, b2: Belief) -> bool:
        """
        Check if two beliefs are antonym-equivalent (same finding, opposite phrasing).

        Sprint 7 (Bates): If environments are antonyms and effects are opposite,
        this is the SAME finding expressed differently, not a conflict.

        Example:
            "Openness increases wellbeing" ≡ "Enclosure decreases wellbeing"

        Returns:
            True if beliefs are antonym-equivalent (NOT a conflict)
        """
        if not ENVIRONMENT_TAXONOMY_AVAILABLE:
            return False

        env1 = self._get_environment_id(b1)
        env2 = self._get_environment_id(b2)

        if not (env1 and env2):
            return False

        # Check if environments are antonyms
        if not are_antonyms(env1, env2):
            return False

        # Check if effects are opposite directions
        dir1 = self._get_effect_direction(b1.content)
        dir2 = self._get_effect_direction(b2.content)

        if not (dir1 and dir2):
            return False

        # Antonym environments + opposite effects = same finding
        return dir1 != dir2

    def _compute_diversity_index(self, beliefs: List[Belief]) -> float:
        """
        Compute diversity index over environment and outcome domains.

        Sprint 7 (Bates): Shannon entropy weighted 0.6 environment, 0.4 outcome.
        Higher diversity = better coverage of the research space.

        Args:
            beliefs: List of beliefs to analyze

        Returns:
            Diversity index (0.0 to ~2.0, higher = more diverse)
        """
        from collections import Counter

        # Count environment IDs
        env_ids = []
        for b in beliefs:
            env_id = self._get_environment_id(b)
            if env_id:
                env_ids.append(env_id)

        # Count outcome types (from attribute_id, outcome_type, or domain)
        outcome_ids = []
        for b in beliefs:
            outcome = getattr(b, 'outcome_type', None) or getattr(b, 'domain', None)
            if outcome:
                outcome_ids.append(outcome)

        # Shannon entropy for environments
        env_entropy = self._shannon_entropy(Counter(env_ids)) if env_ids else 0.0

        # Shannon entropy for outcomes
        outcome_entropy = self._shannon_entropy(Counter(outcome_ids)) if outcome_ids else 0.0

        # Weighted combination per Bates
        return 0.6 * env_entropy + 0.4 * outcome_entropy

    def _shannon_entropy(self, counts: Dict[str, int]) -> float:
        """
        Compute Shannon entropy from a counter.

        Sprint 7 (Bates): Used for diversity index calculation.
        """
        if not counts:
            return 0.0

        total = sum(counts.values())
        if total == 0:
            return 0.0

        entropy = 0.0
        for count in counts.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log(p)

        return entropy

    def _detect_conflict_type(self, b1: Belief, b2: Belief) -> ConflictType:
        """
        Detect type of conflict between beliefs.

        Expert Panel 5.2: Categorize conflicts for appropriate resolution.
        Sprint 6 additions: Scope overlap check, PRECISION_BOUNDARY.
        """
        c1 = b1.content.lower()
        c2 = b2.content.lower()

        # Sprint 6: Check scope overlap first (per Cartwright)
        scopes_overlap = self._scopes_overlap(b1.scope, b2.scope)

        # Check for valence indicators
        positive_terms = {"increase", "improve", "enhance", "promote", "facilitate", "positive"}
        negative_terms = {"decrease", "reduce", "impair", "inhibit", "negative", "worsen"}

        b1_positive = any(term in c1 for term in positive_terms)
        b1_negative = any(term in c1 for term in negative_terms)
        b2_positive = any(term in c2 for term in positive_terms)
        b2_negative = any(term in c2 for term in negative_terms)

        # Opposite valence suggests genuine contradiction
        if (b1_positive and b2_negative) or (b1_negative and b2_positive):
            # Sprint 7: Check antonym equivalence (per Bates)
            # "Openness increases wellbeing" ≡ "Enclosure decreases wellbeing"
            if self._check_antonym_equivalence(b1, b2):
                # Not a conflict - same finding expressed with antonym environment
                return ConflictType.UNKNOWN  # Will be handled as equivalent, not conflict

            # Sprint 6: Check scope conditions (per Cartwright)
            if not scopes_overlap:
                return ConflictType.SCOPE_BOUNDARY

            # Check if different contexts/populations in text
            context_markers = {"in ", "for ", "among ", "when ", "under "}
            b1_context = any(m in c1 for m in context_markers)
            b2_context = any(m in c2 for m in context_markers)

            if b1_context and b2_context:
                return ConflictType.SCOPE_BOUNDARY

            return ConflictType.GENUINE_CONTRADICTION

        # Sprint 6: Check for precision boundary (per Cartwright)
        if self._is_precision_boundary(b1, b2):
            return ConflictType.PRECISION_BOUNDARY

        # Different measurement methods
        method_markers = {"measured by", "assessed via", "using ", "self-report", "cortisol", "eeg"}
        b1_method = any(m in c1 for m in method_markers)
        b2_method = any(m in c2 for m in method_markers)

        if b1_method or b2_method:
            return ConflictType.METHODOLOGICAL_DIVERGENCE

        return ConflictType.UNKNOWN

    # =========================================================================
    # CREDENCE MERGE (Expert Panel 5.3)
    # =========================================================================

    def _merge_credences(
        self,
        c1: Credence,
        c2: Credence,
        paper_quality: Optional[float] = None
    ) -> Credence:
        """
        Merge two credences using inverse-variance weighting.

        Expert Panel 5.3 (Wasserman): Use inverse-variance weighting instead of
        observation-weighted averaging. This properly accounts for different
        study precisions.

        Args:
            c1: First credence
            c2: Second credence
            paper_quality: Optional quality weight for c2 (from paper_quality table)
        """
        # Get uncertainties (default to 0.3 if not specified)
        u1 = max(0.01, c1.uncertainty or 0.3)  # Avoid division by zero
        u2 = max(0.01, c2.uncertainty or 0.3)

        # Apply paper quality adjustment to uncertainty
        # Lower quality = higher effective uncertainty
        if paper_quality is not None and paper_quality > 0:
            quality_adjustment = 1.0 / paper_quality
            u2 = u2 * quality_adjustment

        # Inverse-variance weights (Expert Panel 5.3)
        var1 = u1 ** 2
        var2 = u2 ** 2

        w1 = 1.0 / var1
        w2 = 1.0 / var2
        total_weight = w1 + w2

        # Weighted average
        merged_value = (w1 * c1.value + w2 * c2.value) / total_weight

        # Merged variance (Expert Panel 5.3)
        # This properly combines uncertainties
        merged_variance = 1.0 / total_weight
        merged_uncertainty = math.sqrt(merged_variance)

        # Combine observation counts
        total_observations = (c1.n_observations or 1) + (c2.n_observations or 1)
        total_supporting = (c1.n_supporting or 0) + (c2.n_supporting or 0)
        total_contradicting = (c1.n_contradicting or 0) + (c2.n_contradicting or 0)

        return Credence(
            value=merged_value,
            uncertainty=merged_uncertainty,
            n_supporting=total_supporting,
            n_contradicting=total_contradicting,
            n_observations=total_observations
        )

    def _merge_credences_cluster_aware(
        self,
        b1: Belief,
        b2: Belief,
        paper_quality: Optional[float] = None
    ) -> Credence:
        """
        Merge credences with awareness of evidence clusters.

        Sprint 8 (Panel Consensus): When beliefs share the same evidence_cluster_id,
        don't boost credence (would be double-counting same study evidence).

        Args:
            b1: First belief
            b2: Second belief
            paper_quality: Optional quality weight

        Returns:
            Merged credence
        """
        # Check if same evidence cluster (same study)
        cluster1 = getattr(b1, 'evidence_cluster_id', None)
        cluster2 = getattr(b2, 'evidence_cluster_id', None)

        if cluster1 and cluster2 and cluster1 == cluster2:
            # Same study - don't boost credence (would be double-counting)
            # Return average without uncertainty reduction
            c1, c2 = b1.credence, b2.credence
            return Credence(
                value=(c1.value + c2.value) / 2,
                uncertainty=max(c1.uncertainty or 0.3, c2.uncertainty or 0.3),  # No reduction
                n_supporting=c1.n_supporting or 0,  # Don't sum
                n_contradicting=c1.n_contradicting or 0,
                n_observations=c1.n_observations or 1  # Don't sum
            )

        # Different studies - use normal inverse-variance merge
        return self._merge_credences(b1.credence, b2.credence, paper_quality)

    def _should_auto_resolve(
        self,
        c1: Credence,
        c2: Credence
    ) -> Tuple[bool, str]:
        """
        Determine if credence conflict should be auto-resolved or flagged.

        Expert Panel 5.2 (Simon): Decision matrix based on credence gap
        and observation ratio.

        Returns:
            (should_auto_resolve, reason)
        """
        credence_gap = abs(c1.value - c2.value)

        n1 = max(1, c1.n_observations or 1)
        n2 = max(1, c2.n_observations or 1)
        obs_ratio = max(n1, n2) / min(n1, n2)

        # Small gap - auto-resolve
        if credence_gap < self.CREDENCE_GAP_SMALL:
            if obs_ratio <= self.OBSERVATION_RATIO_SIMILAR_MAX:
                return True, "Small credence gap with similar observation counts"
            elif obs_ratio > self.OBSERVATION_RATIO_DISPARATE:
                return True, "Small credence gap, favoring higher-n study"

        # Large gap - flag for review
        if credence_gap > self.CREDENCE_GAP_LARGE:
            return False, f"Large credence gap ({credence_gap:.2f}) requires review"

        # Medium gap
        if self.CREDENCE_GAP_SMALL <= credence_gap <= self.CREDENCE_GAP_LARGE:
            return True, "Medium credence gap - auto-merging with elevated uncertainty"

        return True, "Default auto-resolve"

    # =========================================================================
    # ACCUMULATION (MERGE)
    # =========================================================================

    def merge_belief_into_master(
        self,
        master_web_id: str,
        belief: Belief,
        source_paper_id: str
    ) -> MergeResult:
        """
        Merge a belief into the master web.

        Expert Panel Refinements:
        - 5.2: Structured attribute matching for identity
        - 5.2: Conflict type categorization
        - 5.2: Decision matrix for auto-resolution
        - 5.3: Inverse-variance weighting for credence merge

        Args:
            master_web_id: Master web identifier
            belief: Belief to merge
            source_paper_id: Paper the belief came from

        Returns:
            MergeResult describing what happened
        """
        existing = self.load_belief(belief.belief_id, master_web_id)

        # Get paper quality for weighting
        paper_quality_data = self.get_paper_quality(source_paper_id)
        paper_quality = paper_quality_data['overall_quality'] if paper_quality_data else None

        if existing is None:
            # New belief - add it
            belief.paper_ids = list(set(getattr(belief, 'paper_ids', []) + [source_paper_id]))
            self.save_belief(master_web_id, belief)

            self._log_merge(
                master_web_id, belief.belief_id, "new",
                None, belief.credence.value, source_paper_id, "New belief added",
                auto_resolved=True, requires_review=False
            )

            return MergeResult(
                belief_id=belief.belief_id,
                merge_type="new",
                new_credence=belief.credence.value,
                auto_resolved=True
            )

        # Check for content similarity
        if self._beliefs_same_content(existing, belief):
            # Same content - check if should auto-resolve
            should_auto, reason = self._should_auto_resolve(existing.credence, belief.credence)

            old_credence = existing.credence.value
            merged_credence = self._merge_credences(
                existing.credence, belief.credence, paper_quality
            )

            existing.credence = merged_credence
            existing.paper_ids = list(set(
                getattr(existing, 'paper_ids', []) + [source_paper_id]
            ))

            self.save_belief(master_web_id, existing)

            self._log_merge(
                master_web_id, belief.belief_id, "update",
                old_credence, merged_credence.value, source_paper_id,
                f"Inverse-variance merge: {reason}",
                auto_resolved=should_auto, requires_review=not should_auto
            )

            return MergeResult(
                belief_id=belief.belief_id,
                merge_type="update",
                old_credence=old_credence,
                new_credence=merged_credence.value,
                auto_resolved=should_auto,
                requires_review=not should_auto
            )

        # Different content - conflict
        # Detect conflict type (Expert Panel 5.2)
        conflict_type = self._detect_conflict_type(existing, belief)

        # Genuine contradictions should never auto-resolve
        should_auto = conflict_type not in [
            ConflictType.GENUINE_CONTRADICTION,
            ConflictType.UNKNOWN
        ]

        # Create a new belief with modified ID
        # V23.0.0: entrenchment is now emergent (computed from web position)
        conflict_id = f"{belief.belief_id}:conflict:{source_paper_id}"
        conflict_belief = Belief(
            belief_id=conflict_id,
            content=belief.content,
            level=belief.level,
            status=belief.status,
            credence=belief.credence,
            theory_id=belief.theory_id,
            paper_ids=[source_paper_id]
        )

        self.save_belief(master_web_id, conflict_belief)

        self._log_merge(
            master_web_id, belief.belief_id, "conflict",
            None, belief.credence.value, source_paper_id,
            f"Content conflict ({conflict_type.value}) - created {conflict_id}",
            conflict_type=conflict_type.value,
            auto_resolved=False, requires_review=True
        )

        return MergeResult(
            belief_id=belief.belief_id,
            merge_type="conflict",
            new_credence=belief.credence.value,
            conflict_resolved=False,
            conflict_resolution=f"Created separate belief: {conflict_id}",
            conflict_type=conflict_type,
            requires_review=True
        )

    def integrate_paper_web(
        self,
        paper_web: WebOfBelief,
        paper_id: str,
        bridge_registry: Optional['BridgeRegistry'] = None,
        publication_year: Optional[int] = None,
        publication_date: Optional[str] = None,
        first_seen_at: Optional[str] = None,
        metadata_source: Optional[str] = None
    ) -> IntegrationReport:
        """
        Integrate a paper's web into the master accumulated web.

        This is the main entry point for accumulation across papers.

        Args:
            paper_web: WebOfBelief from a single paper
            paper_id: Paper identifier
            bridge_registry: Optional bridge registry from the paper

        Returns:
            IntegrationReport summarizing what happened
        """
        master_id = self.create_or_get_master_web()
        now = self._utc_now()
        report = IntegrationReport(paper_id=paper_id)

        # Record publication metadata for scholarly replay (best effort)
        existing_pub = self.get_paper_publication(paper_id)
        if existing_pub:
            if publication_year is None:
                publication_year = existing_pub.get("publication_year")
            if publication_date is None:
                publication_date = existing_pub.get("publication_date")
            if first_seen_at is None:
                first_seen_at = existing_pub.get("first_seen_at")
            if metadata_source is None:
                metadata_source = existing_pub.get("source")

        if publication_year is None:
            quality = self.get_paper_quality(paper_id)
            if quality:
                publication_year = quality.get("publication_year")
        self.upsert_paper_publication(
            paper_id=paper_id,
            publication_year=publication_year,
            publication_date=publication_date,
            first_seen_at=first_seen_at or now,
            source=metadata_source
        )

        # Load current master web
        master_web, master_bridges = self.load_web(master_id)
        if master_web is None:
            master_web = create_neuroarchitecture_web()
            master_bridges = BridgeRegistry() if BRIDGE_AVAILABLE else None

        report.coherence_before = master_web.coherence_score() if hasattr(master_web, 'coherence_score') else 0.0

        # Merge beliefs
        for belief in paper_web.beliefs.values():
            result = self.merge_belief_into_master(master_id, belief, paper_id)
            report.merge_results.append(result)

            if result.merge_type == "new":
                report.n_beliefs_added += 1
            elif result.merge_type == "update":
                report.n_beliefs_updated += 1
            elif result.merge_type == "conflict":
                report.n_beliefs_conflicted += 1

        # Merge constraints (only if both endpoints exist in master)
        for constraint in paper_web.constraints.values():
            if self._constraint_endpoints_exist(master_id, constraint):
                self.save_constraint(master_id, constraint)
                report.n_constraints_added += 1

        # Merge bridges
        if bridge_registry and master_bridges and BRIDGE_AVAILABLE:
            for bridge in bridge_registry.all():
                self.save_bridge(master_id, bridge)
                master_bridges.add(bridge)
                report.n_bridges_added += 1

        # Reload master web to get merged state
        master_web, _ = self.load_web(master_id)
        if master_web:
            # Seek equilibrium on merged web
            if hasattr(master_web, 'seek_equilibrium'):
                master_web.seek_equilibrium(max_iterations=5)

            report.coherence_after = master_web.coherence_score() if hasattr(master_web, 'coherence_score') else 0.0

            # Save updated master
            self.save_web(master_web, master_id, "Master Accumulated Web", is_master=True)

            # Check for coherence alerts (Expert Panel 5.5)
            alerts = self._check_coherence_alerts(
                master_id, report.coherence_before, report.coherence_after, paper_id
            )
            report.alerts = alerts

            # Record local coherence per theory (Expert Panel 5.5)
            self._record_local_coherence(master_id, master_web)

            # Entrenchment snapshots for beliefs tied to this paper (system timeline)
            belief_ids = [
                b.belief_id for b in master_web.beliefs.values()
                if paper_id in getattr(b, "paper_ids", [])
            ]
            if belief_ids:
                self.record_entrenchment_snapshots(
                    web_id=master_id,
                    web=master_web,
                    belief_ids=belief_ids,
                    paper_id=paper_id,
                    timeline_type="system",
                    as_of_date=now,
                    event_type="integration",
                    reason="paper_integration"
                )

        # Log integration
        self._log_integration(
            master_id, paper_id, None,
            report.n_beliefs_added, report.n_beliefs_updated, report.n_constraints_added,
            report.coherence_before, report.coherence_after
        )

        logger.info(
            f"Integrated paper {paper_id} into master: "
            f"+{report.n_beliefs_added} beliefs, "
            f"~{report.n_beliefs_updated} updated, "
            f"!{report.n_beliefs_conflicted} conflicts"
        )

        return report

    def _constraint_endpoints_exist(self, web_id: str, constraint: Constraint) -> bool:
        """Check if both endpoints of a constraint exist in the web."""
        with self._get_connection() as conn:
            source = conn.execute(
                "SELECT 1 FROM beliefs WHERE belief_id = ? AND web_id = ?",
                (constraint.source_id, web_id)
            ).fetchone()

            target = conn.execute(
                "SELECT 1 FROM beliefs WHERE belief_id = ? AND web_id = ?",
                (constraint.target_id, web_id)
            ).fetchone()

            return source is not None and target is not None

    # =========================================================================
    # COHERENCE DASHBOARD (Expert Panel 5.5)
    # =========================================================================

    def get_coherence_dashboard(self, web_id: str) -> Optional[CoherenceDashboard]:
        """
        Get comprehensive coherence dashboard for a web.

        Expert Panel 5.5: Multiple metrics for comprehensive health assessment.
        """
        web, _ = self.load_web(web_id)
        if not web:
            return None

        n_beliefs = len(web.beliefs)
        n_constraints = len(web.constraints)

        # Global coherence
        global_coherence = web.coherence_score() if hasattr(web, 'coherence_score') else 0.0

        # Constraint density
        max_constraints = n_beliefs * (n_beliefs - 1) if n_beliefs > 1 else 1
        constraint_density = n_constraints / max_constraints if max_constraints > 0 else 0.0

        # Count conflicts
        with self._get_connection() as conn:
            n_conflicts = conn.execute(
                "SELECT COUNT(*) FROM belief_merge_log WHERE web_id = ? AND merge_type = 'conflict' AND requires_review = 1",
                (web_id,)
            ).fetchone()[0]

        # Count isolated beliefs
        connected_beliefs = set()
        for c in web.constraints.values():
            connected_beliefs.add(c.source_id)
            connected_beliefs.add(c.target_id)
        n_isolated = n_beliefs - len(connected_beliefs)

        # Count distinct theories
        theories = set(b.theory_id for b in web.beliefs.values() if b.theory_id)
        n_theories = len(theories)

        # Inter-theory coherence (constraints between different theories)
        inter_theory_constraints = []
        for c in web.constraints.values():
            source_belief = web.beliefs.get(c.source_id)
            target_belief = web.beliefs.get(c.target_id)
            if source_belief and target_belief:
                if source_belief.theory_id != target_belief.theory_id:
                    inter_theory_constraints.append(c)

        # Simple inter-theory coherence: average strength of cross-theory constraints
        if inter_theory_constraints:
            inter_theory_coherence = sum(c.strength for c in inter_theory_constraints) / len(inter_theory_constraints)
        else:
            inter_theory_coherence = 0.0

        # Entropy of credence distribution
        credences = [b.credence.value for b in web.beliefs.values()]
        if credences:
            # Bin credences and compute entropy
            import numpy as np
            hist, _ = np.histogram(credences, bins=10, range=(0, 1), density=True)
            hist = hist / hist.sum() if hist.sum() > 0 else hist
            entropy = -sum(p * np.log(p + 1e-10) for p in hist if p > 0)
        else:
            entropy = 0.0

        # Mean uncertainty
        uncertainties = [
            b.credence.uncertainty for b in web.beliefs.values()
            if b.credence.uncertainty is not None
        ]
        mean_uncertainty = sum(uncertainties) / len(uncertainties) if uncertainties else 0.3

        # Sprint 7: Diversity index (per Bates)
        diversity_index = self._compute_diversity_index(list(web.beliefs.values()))

        return CoherenceDashboard(
            global_coherence=global_coherence,
            n_beliefs=n_beliefs,
            n_constraints=n_constraints,
            constraint_density=constraint_density,
            n_conflicts=n_conflicts,
            n_isolated_beliefs=n_isolated,
            n_theories=n_theories,
            inter_theory_coherence=inter_theory_coherence,
            entropy=entropy,
            mean_uncertainty=mean_uncertainty,
            diversity_index=diversity_index
        )

    def _record_local_coherence(self, web_id: str, web: WebOfBelief) -> None:
        """
        Record local coherence for each theory.

        Expert Panel 5.5: Track per-theory coherence to detect local incoherence.
        """
        theories = set(b.theory_id for b in web.beliefs.values() if b.theory_id)
        now = self._utc_now()

        with self._get_connection() as conn:
            for theory_id in theories:
                # Get beliefs for this theory
                theory_beliefs = {
                    bid: b for bid, b in web.beliefs.items()
                    if b.theory_id == theory_id
                }

                # Get constraints involving only this theory's beliefs
                theory_constraints = {
                    cid: c for cid, c in web.constraints.items()
                    if c.source_id in theory_beliefs and c.target_id in theory_beliefs
                }

                # Compute local coherence (simplified)
                if theory_constraints:
                    local_coherence = sum(c.strength for c in theory_constraints.values()) / len(theory_constraints)
                else:
                    local_coherence = 0.5  # Neutral if no internal constraints

                conn.execute("""
                    INSERT INTO local_coherence_history (
                        web_id, theory_id, local_coherence, n_beliefs, n_constraints, recorded_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    web_id, theory_id, local_coherence,
                    len(theory_beliefs), len(theory_constraints), now
                ))

    # =========================================================================
    # COHERENCE ALERTS (Expert Panel 5.5)
    # =========================================================================

    def _check_coherence_alerts(
        self,
        web_id: str,
        coherence_before: float,
        coherence_after: float,
        triggered_by: Optional[str] = None
    ) -> List[CoherenceAlert]:
        """
        Check for coherence decline and generate alerts.

        Expert Panel 5.5: Alert on sharp decline, cumulative decline, or anomaly.
        """
        alerts = []
        now = self._utc_now()

        # Sharp decline check
        decline = coherence_before - coherence_after
        if decline > self.SHARP_DECLINE_THRESHOLD:
            alert = CoherenceAlert(
                alert_type="sharp_decline",
                severity="critical" if decline > 0.2 else "warning",
                message=f"Coherence dropped by {decline:.3f} after integrating {triggered_by}",
                coherence_before=coherence_before,
                coherence_after=coherence_after,
                triggered_at=now,
                triggered_by=triggered_by
            )
            alerts.append(alert)
            self._save_alert(web_id, alert)

        # Cumulative decline check (3+ consecutive declines)
        history = self.get_coherence_history(web_id, limit=4)
        if len(history) >= 3:
            consecutive_declines = 0
            for i in range(len(history) - 1):
                if history[i]['coherence_score'] < history[i + 1]['coherence_score']:
                    consecutive_declines += 1
                else:
                    break

            if consecutive_declines >= 3:
                alert = CoherenceAlert(
                    alert_type="cumulative_decline",
                    severity="warning",
                    message=f"Coherence has declined in {consecutive_declines} consecutive integrations",
                    coherence_before=history[-1]['coherence_score'],
                    coherence_after=coherence_after,
                    triggered_at=now,
                    triggered_by=triggered_by
                )
                alerts.append(alert)
                self._save_alert(web_id, alert)

        # Anomaly detection (>2 stddev from historical mean)
        if len(history) >= 10:
            historical_scores = [h['coherence_score'] for h in history]
            mean_score = sum(historical_scores) / len(historical_scores)
            variance = sum((s - mean_score) ** 2 for s in historical_scores) / len(historical_scores)
            stddev = math.sqrt(variance) if variance > 0 else 0.1

            if abs(coherence_after - mean_score) > self.ANOMALY_STDDEV_THRESHOLD * stddev:
                alert = CoherenceAlert(
                    alert_type="anomaly",
                    severity="warning",
                    message=f"Coherence {coherence_after:.3f} is {abs(coherence_after - mean_score) / stddev:.1f} stddev from historical mean {mean_score:.3f}",
                    coherence_before=coherence_before,
                    coherence_after=coherence_after,
                    triggered_at=now,
                    triggered_by=triggered_by
                )
                alerts.append(alert)
                self._save_alert(web_id, alert)

        return alerts

    def _save_alert(self, web_id: str, alert: CoherenceAlert) -> None:
        """Save a coherence alert to the database."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO coherence_alerts (
                    web_id, alert_type, severity, message,
                    coherence_before, coherence_after, triggered_by, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                web_id, alert.alert_type, alert.severity, alert.message,
                alert.coherence_before, alert.coherence_after,
                alert.triggered_by, alert.triggered_at
            ))

    def get_unacknowledged_alerts(self, web_id: str) -> List[Dict[str, Any]]:
        """Get all unacknowledged alerts for a web."""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM coherence_alerts
                WHERE web_id = ? AND acknowledged = 0
                ORDER BY created_at DESC
            """, (web_id,)).fetchall()
            return [dict(row) for row in rows]

    def acknowledge_alert(self, alert_id: int) -> None:
        """Mark an alert as acknowledged."""
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE coherence_alerts SET acknowledged = 1 WHERE alert_id = ?",
                (alert_id,)
            )

    # =========================================================================
    # LOGGING
    # =========================================================================

    def _record_coherence(
        self,
        web_id: str,
        coherence: float,
        n_beliefs: int,
        n_constraints: int,
        triggered_by: str
    ) -> None:
        """Record coherence history entry."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO coherence_history (web_id, coherence_score, n_beliefs, n_constraints, recorded_at, triggered_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (web_id, coherence, n_beliefs, n_constraints, self._utc_now(), triggered_by))

    def _log_merge(
        self,
        web_id: str,
        belief_id: str,
        merge_type: str,
        old_credence: Optional[float],
        new_credence: float,
        source_paper_id: str,
        reason: str,
        conflict_type: Optional[str] = None,
        auto_resolved: bool = True,
        requires_review: bool = False
    ) -> None:
        """Log a belief merge operation."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO belief_merge_log (
                    web_id, belief_id, merge_type, conflict_type, old_credence, new_credence,
                    source_paper_id, merge_reason, auto_resolved, requires_review, merged_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                web_id, belief_id, merge_type, conflict_type, old_credence, new_credence,
                source_paper_id, reason, 1 if auto_resolved else 0,
                1 if requires_review else 0, self._utc_now()
            ))

    def _log_integration(
        self,
        web_id: str,
        paper_id: str,
        run_id: Optional[str],
        n_added: int,
        n_updated: int,
        n_constraints: int,
        coherence_before: Optional[float],
        coherence_after: Optional[float]
    ) -> None:
        """Log a paper integration operation."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO paper_integrations (
                    web_id, paper_id, run_id, n_beliefs_added, n_beliefs_updated,
                    n_constraints_added, coherence_before, coherence_after, integrated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                web_id, paper_id, run_id, n_added, n_updated, n_constraints,
                coherence_before, coherence_after, self._utc_now()
            ))

    # =========================================================================
    # QUERIES
    # =========================================================================

    def get_integration_history(self, web_id: str) -> List[Dict[str, Any]]:
        """Get paper integration history for a web."""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM paper_integrations
                WHERE web_id = ?
                ORDER BY integrated_at DESC
            """, (web_id,)).fetchall()

            return [dict(row) for row in rows]

    def get_coherence_history(self, web_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get coherence history for a web."""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM coherence_history
                WHERE web_id = ?
                ORDER BY recorded_at DESC
                LIMIT ?
            """, (web_id, limit)).fetchall()

            return [dict(row) for row in rows]

    def get_local_coherence_history(
        self,
        web_id: str,
        theory_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get local coherence history for a web, optionally filtered by theory."""
        with self._get_connection() as conn:
            if theory_id:
                rows = conn.execute("""
                    SELECT * FROM local_coherence_history
                    WHERE web_id = ? AND theory_id = ?
                    ORDER BY recorded_at DESC
                    LIMIT ?
                """, (web_id, theory_id, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM local_coherence_history
                    WHERE web_id = ?
                    ORDER BY recorded_at DESC
                    LIMIT ?
                """, (web_id, limit)).fetchall()

            return [dict(row) for row in rows]

    def get_merge_log(self, web_id: str, belief_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get merge log entries."""
        with self._get_connection() as conn:
            if belief_id:
                rows = conn.execute("""
                    SELECT * FROM belief_merge_log
                    WHERE web_id = ? AND belief_id = ?
                    ORDER BY merged_at DESC
                """, (web_id, belief_id)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM belief_merge_log
                    WHERE web_id = ?
                    ORDER BY merged_at DESC
                """, (web_id,)).fetchall()

            return [dict(row) for row in rows]

    def get_statistics(self, web_id: str) -> Dict[str, Any]:
        """Get summary statistics for a web."""
        with self._get_connection() as conn:
            metadata = conn.execute(
                "SELECT * FROM web_metadata WHERE web_id = ?",
                (web_id,)
            ).fetchone()

            if not metadata:
                return {}

            n_papers = conn.execute(
                "SELECT COUNT(DISTINCT paper_id) FROM paper_integrations WHERE web_id = ?",
                (web_id,)
            ).fetchone()[0]

            n_conflicts = conn.execute(
                "SELECT COUNT(*) FROM belief_merge_log WHERE web_id = ? AND merge_type = 'conflict'",
                (web_id,)
            ).fetchone()[0]

            n_requiring_review = conn.execute(
                "SELECT COUNT(*) FROM belief_merge_log WHERE web_id = ? AND requires_review = 1",
                (web_id,)
            ).fetchone()[0]

            n_unacknowledged_alerts = conn.execute(
                "SELECT COUNT(*) FROM coherence_alerts WHERE web_id = ? AND acknowledged = 0",
                (web_id,)
            ).fetchone()[0]

            return {
                "web_id": metadata['web_id'],
                "name": metadata['name'],
                "n_beliefs": metadata['n_beliefs'],
                "n_constraints": metadata['n_constraints'],
                "coherence_score": metadata['coherence_score'],
                "version": metadata['version'],
                "n_papers_integrated": n_papers,
                "n_conflicts": n_conflicts,
                "n_requiring_review": n_requiring_review,
                "n_unacknowledged_alerts": n_unacknowledged_alerts,
                "created_at": metadata['created_at'],
                "updated_at": metadata['updated_at']
            }


# =============================================================================
# MAIN (Demo/Test)
# =============================================================================

if __name__ == "__main__":
    # Demo
    service = WebPersistenceService(":memory:")

    print("=== Web Persistence Demo (Refined) ===\n")

    # Create a test web
    web = create_neuroarchitecture_web()

    # Add some beliefs
    web.add_belief(Belief(
        belief_id="belief:test:001",
        content="Nature exposure reduces cortisol levels",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.TENTATIVE,
        credence=Credence(0.7, 0.2),
        theory_id="SRT",
        paper_ids=["paper:001"]
    ))

    web.add_belief(Belief(
        belief_id="belief:test:002",
        content="Angular shapes increase amygdala activation",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.TENTATIVE,
        credence=Credence(0.65, 0.25),
        theory_id="ART",
        paper_ids=["paper:001"]
    ))

    # Save web
    service.save_web(web, "test:web:001", "Test Web 1")
    print(f"Saved web with {len(web.beliefs)} beliefs")

    # Load web
    loaded_web, loaded_bridges = service.load_web("test:web:001")
    print(f"Loaded web with {len(loaded_web.beliefs)} beliefs")

    # Test accumulation
    print("\n=== Testing Accumulation (Inverse-Variance Weighting) ===")

    # Add paper quality
    service.save_paper_quality(
        "paper:002",
        sample_size_score=0.8,
        methodology_score=0.7,
        preregistered=True
    )

    # Create second paper's web
    web2 = create_neuroarchitecture_web()
    web2.add_belief(Belief(
        belief_id="belief:test:001",  # Same ID - will merge
        content="Nature exposure reduces cortisol levels",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.TENTATIVE,
        credence=Credence(0.8, 0.15),  # Higher credence, lower uncertainty
        theory_id="SRT",
        paper_ids=["paper:002"]
    ))

    web2.add_belief(Belief(
        belief_id="belief:test:003",  # New belief
        content="Biophilic design improves wellbeing",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.TENTATIVE,
        credence=Credence(0.75, 0.2),
        theory_id="Biophilia",
        paper_ids=["paper:002"]
    ))

    # Integrate into master
    report = service.integrate_paper_web(web2, "paper:002")

    print(f"Integration report:")
    print(f"  Beliefs added: {report.n_beliefs_added}")
    print(f"  Beliefs updated: {report.n_beliefs_updated}")
    print(f"  Beliefs conflicted: {report.n_beliefs_conflicted}")
    print(f"  Coherence: {report.coherence_before:.3f} -> {report.coherence_after:.3f}")
    print(f"  Alerts: {len(report.alerts)}")

    # Get coherence dashboard
    dashboard = service.get_coherence_dashboard(service.get_master_web_id())
    if dashboard:
        print(f"\nCoherence Dashboard:")
        print(f"  Global coherence: {dashboard.global_coherence:.3f}")
        print(f"  Constraint density: {dashboard.constraint_density:.4f}")
        print(f"  Isolated beliefs: {dashboard.n_isolated_beliefs}")
        print(f"  Distinct theories: {dashboard.n_theories}")
        print(f"  Health: {dashboard.health_summary()}")

    # Get statistics
    stats = service.get_statistics(service.get_master_web_id())
    print(f"\nMaster web statistics:")
    print(f"  Beliefs: {stats['n_beliefs']}")
    print(f"  Papers integrated: {stats['n_papers_integrated']}")
    print(f"  Conflicts: {stats['n_conflicts']}")
    print(f"  Requiring review: {stats['n_requiring_review']}")
