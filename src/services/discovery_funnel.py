"""
Discovery Funnel Service — DISC-1
Article Eater v23.1.0
2026-02-09

Tracks the full discovery funnel from VOI gap identification through
article search, PDF retrieval, and gap closure verification.

Key insight: VOI gaps are PREDICTIONS about where articles should exist.
This service tracks how well those predictions pan out.

Funnel stages:
    VOI Gap Identified → Search Executed → Articles Found →
    PDF Retrieved → Paper Ingested → Gap Closure Assessed

Expert Panel Guidance:
- Bates: Information seeking behavior, berrypicking
- Kleinberg: Network flow, bottleneck analysis
- Simon: Satisficing in search
- Pearl: Causal attribution of success/failure
"""

import sqlite3
import json
import logging
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from contextlib import contextmanager
from pathlib import Path

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class GapType(Enum):
    """Types of gaps in the web of belief."""
    MISSING_EVIDENCE = "missing_evidence"       # No empirical support
    WEAK_SUPPORT = "weak_support"               # Low credence, needs more
    CONTRADICTION = "contradiction"             # Conflicting beliefs
    BOUNDARY_UNCLEAR = "boundary_unclear"       # Scope conditions unknown


class GapStatus(Enum):
    """Status of a VOI gap."""
    OPEN = "open"               # Not yet searched
    SEARCHING = "searching"     # Active searches underway
    FOUND = "found"             # Articles found, awaiting retrieval
    CLOSED = "closed"           # Gap addressed
    STALE = "stale"             # Gap no longer relevant


class RetrievalMethod(Enum):
    """Methods for PDF retrieval."""
    DIRECT_LINK = "direct_link"         # Publisher direct link
    UNPAYWALL = "unpaywall"             # Unpaywall API
    SCIHUB = "scihub"                   # Sci-Hub (gray literature)
    LIBRARY = "library"                 # Library proxy
    AUTHOR_REQUEST = "author_request"   # Email to author
    MANUAL = "manual"                   # Manual download


class RetrievalStatus(Enum):
    """Status of a PDF retrieval attempt."""
    SUCCESS = "success"
    PAYWALL = "paywall"
    NOT_FOUND = "not_found"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    ACCESS_DENIED = "access_denied"
    FORMAT_ERROR = "format_error"
    CORRUPT = "corrupt"
    SIZE_EXCEEDED = "size_exceeded"


class ClosureType(Enum):
    """How well a paper closed a gap."""
    FULL = "full"           # Gap completely closed
    PARTIAL = "partial"     # VOI reduced but gap remains
    NONE = "none"           # No impact on gap
    NEGATIVE = "negative"   # Increased uncertainty


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class VOIGap:
    """A gap in the web of belief with predicted value of information."""
    gap_id: str
    topic: str
    gap_type: GapType
    predicted_voi: float
    status: GapStatus = GapStatus.OPEN

    # Context
    belief_id: Optional[str] = None
    constraint_id: Optional[str] = None
    theory_id: Optional[str] = None
    web_id: Optional[str] = None

    # VOI details
    uncertainty_reduction: Optional[float] = None
    coherence_impact: Optional[float] = None

    # Search guidance
    search_terms: List[str] = field(default_factory=list)
    target_article_types: List[str] = field(default_factory=list)
    target_sources: List[str] = field(default_factory=list)

    # Tracking
    priority: float = 0.5
    identified_at: Optional[str] = None
    identified_by: Optional[str] = None
    last_searched_at: Optional[str] = None
    closed_at: Optional[str] = None

    def __post_init__(self):
        if not self.gap_id:
            self.gap_id = str(uuid.uuid4())
        if not self.identified_at:
            self.identified_at = datetime.now(timezone.utc).isoformat()
        if isinstance(self.gap_type, str):
            self.gap_type = GapType(self.gap_type)
        if isinstance(self.status, str):
            self.status = GapStatus(self.status)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "gap_id": self.gap_id,
            "topic": self.topic,
            "gap_type": self.gap_type.value,
            "predicted_voi": self.predicted_voi,
            "status": self.status.value,
            "belief_id": self.belief_id,
            "constraint_id": self.constraint_id,
            "theory_id": self.theory_id,
            "web_id": self.web_id,
            "uncertainty_reduction": self.uncertainty_reduction,
            "coherence_impact": self.coherence_impact,
            "search_terms": self.search_terms,
            "target_article_types": self.target_article_types,
            "target_sources": self.target_sources,
            "priority": self.priority,
            "identified_at": self.identified_at,
            "identified_by": self.identified_by,
            "last_searched_at": self.last_searched_at,
            "closed_at": self.closed_at,
        }


@dataclass
class GapSearch:
    """A search execution linked to a gap."""
    search_id: str
    gap_id: str
    query: str
    source: str

    # Results
    n_results: int = 0
    n_relevant: int = 0
    n_new: int = 0
    top_results: List[str] = field(default_factory=list)

    # Relevance
    avg_relevance_score: Optional[float] = None
    best_relevance_score: Optional[float] = None

    # Execution
    search_type: str = "keyword"
    filters: Dict[str, Any] = field(default_factory=dict)
    executed_at: Optional[str] = None
    duration_ms: Optional[int] = None
    api_response_code: Optional[int] = None
    error_message: Optional[str] = None
    api_credits_used: float = 0.0

    def __post_init__(self):
        if not self.search_id:
            self.search_id = str(uuid.uuid4())
        if not self.executed_at:
            self.executed_at = datetime.now(timezone.utc).isoformat()

    @property
    def relevance_rate(self) -> Optional[float]:
        """Calculate relevance rate."""
        if self.n_results > 0:
            return self.n_relevant / self.n_results
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "search_id": self.search_id,
            "gap_id": self.gap_id,
            "query": self.query,
            "source": self.source,
            "search_type": self.search_type,
            "filters": self.filters,
            "n_results": self.n_results,
            "n_relevant": self.n_relevant,
            "n_new": self.n_new,
            "top_results": self.top_results,
            "avg_relevance_score": self.avg_relevance_score,
            "best_relevance_score": self.best_relevance_score,
            "executed_at": self.executed_at,
            "duration_ms": self.duration_ms,
            "api_response_code": self.api_response_code,
            "error_message": self.error_message,
            "api_credits_used": self.api_credits_used,
        }


@dataclass
class PDFRetrievalAttempt:
    """An attempt to retrieve a PDF."""
    attempt_id: Optional[int] = None
    article_id: Optional[str] = None
    doi: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None

    # Discovery context
    gap_id: Optional[str] = None
    search_id: Optional[str] = None

    # Method and result
    method: RetrievalMethod = RetrievalMethod.DIRECT_LINK
    status: RetrievalStatus = RetrievalStatus.SUCCESS

    # Success details
    pdf_path: Optional[str] = None
    pdf_size_bytes: Optional[int] = None
    pdf_pages: Optional[int] = None
    content_hash: Optional[str] = None

    # Failure details
    http_status_code: Optional[int] = None
    error_message: Optional[str] = None
    retry_after: Optional[str] = None

    # Timing
    attempted_at: Optional[str] = None
    duration_ms: Optional[int] = None
    attempt_number: int = 1
    max_retries: int = 3
    source_domain: Optional[str] = None

    def __post_init__(self):
        if not self.attempted_at:
            self.attempted_at = datetime.now(timezone.utc).isoformat()
        if isinstance(self.method, str):
            self.method = RetrievalMethod(self.method)
        if isinstance(self.status, str):
            self.status = RetrievalStatus(self.status)

    @property
    def succeeded(self) -> bool:
        """Check if retrieval succeeded."""
        return self.status == RetrievalStatus.SUCCESS

    @property
    def is_retryable(self) -> bool:
        """Check if this failure is worth retrying."""
        retryable = {
            RetrievalStatus.TIMEOUT,
            RetrievalStatus.RATE_LIMITED,
        }
        return self.status in retryable and self.attempt_number < self.max_retries

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "attempt_id": self.attempt_id,
            "article_id": self.article_id,
            "doi": self.doi,
            "title": self.title,
            "url": self.url,
            "gap_id": self.gap_id,
            "search_id": self.search_id,
            "method": self.method.value,
            "status": self.status.value,
            "pdf_path": self.pdf_path,
            "pdf_size_bytes": self.pdf_size_bytes,
            "pdf_pages": self.pdf_pages,
            "content_hash": self.content_hash,
            "http_status_code": self.http_status_code,
            "error_message": self.error_message,
            "retry_after": self.retry_after,
            "attempted_at": self.attempted_at,
            "duration_ms": self.duration_ms,
            "attempt_number": self.attempt_number,
            "max_retries": self.max_retries,
            "source_domain": self.source_domain,
        }


@dataclass
class GapClosure:
    """Assessment of whether a paper closed a gap."""
    closure_id: Optional[int] = None
    gap_id: str = ""
    paper_id: str = ""

    # VOI change
    voi_before: float = 0.0
    voi_after: float = 0.0

    # What the paper contributed
    n_beliefs_added: int = 0
    n_constraints_added: int = 0
    relevance_to_gap: Optional[float] = None

    # Assessment
    closure_type: ClosureType = ClosureType.NONE
    assessment_method: str = "automatic"
    assessor_notes: Optional[str] = None

    # Timestamps
    paper_ingested_at: Optional[str] = None
    assessed_at: Optional[str] = None

    def __post_init__(self):
        if not self.assessed_at:
            self.assessed_at = datetime.now(timezone.utc).isoformat()
        if isinstance(self.closure_type, str):
            self.closure_type = ClosureType(self.closure_type)

    @property
    def voi_reduction(self) -> float:
        """Calculate VOI reduction."""
        return self.voi_before - self.voi_after

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "closure_id": self.closure_id,
            "gap_id": self.gap_id,
            "paper_id": self.paper_id,
            "voi_before": self.voi_before,
            "voi_after": self.voi_after,
            "voi_reduction": self.voi_reduction,
            "n_beliefs_added": self.n_beliefs_added,
            "n_constraints_added": self.n_constraints_added,
            "relevance_to_gap": self.relevance_to_gap,
            "closure_type": self.closure_type.value,
            "assessment_method": self.assessment_method,
            "assessor_notes": self.assessor_notes,
            "paper_ingested_at": self.paper_ingested_at,
            "assessed_at": self.assessed_at,
        }


@dataclass
class FunnelMetrics:
    """Aggregate metrics for the discovery funnel."""
    # Gap metrics
    open_gaps: int = 0
    searching_gaps: int = 0
    closed_gaps: int = 0
    avg_open_gap_voi: Optional[float] = None

    # Search metrics
    searches_30d: int = 0
    results_found_30d: int = 0
    relevance_rate_30d: Optional[float] = None

    # Retrieval metrics
    retrieval_attempts_30d: int = 0
    retrieval_success_30d: int = 0
    pdf_success_rate_30d: Optional[float] = None

    # Failure breakdown
    paywall_failures_30d: int = 0
    not_found_failures_30d: int = 0
    timeout_failures_30d: int = 0

    # Closure metrics
    closures_assessed_30d: int = 0
    avg_voi_reduction_30d: Optional[float] = None
    full_closures_30d: int = 0

    # Computed rates
    @property
    def search_hit_rate(self) -> Optional[float]:
        """Percentage of gaps that found relevant articles."""
        total = self.open_gaps + self.searching_gaps + self.closed_gaps
        if total > 0 and self.searches_30d > 0:
            return self.results_found_30d / self.searches_30d if self.searches_30d > 0 else None
        return None

    @property
    def end_to_end_rate(self) -> Optional[float]:
        """Percentage of gaps that were fully closed."""
        total = self.open_gaps + self.searching_gaps + self.closed_gaps
        if total > 0:
            return self.closed_gaps / total
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "open_gaps": self.open_gaps,
            "searching_gaps": self.searching_gaps,
            "closed_gaps": self.closed_gaps,
            "avg_open_gap_voi": self.avg_open_gap_voi,
            "searches_30d": self.searches_30d,
            "results_found_30d": self.results_found_30d,
            "relevance_rate_30d": self.relevance_rate_30d,
            "retrieval_attempts_30d": self.retrieval_attempts_30d,
            "retrieval_success_30d": self.retrieval_success_30d,
            "pdf_success_rate_30d": self.pdf_success_rate_30d,
            "paywall_failures_30d": self.paywall_failures_30d,
            "not_found_failures_30d": self.not_found_failures_30d,
            "timeout_failures_30d": self.timeout_failures_30d,
            "closures_assessed_30d": self.closures_assessed_30d,
            "avg_voi_reduction_30d": self.avg_voi_reduction_30d,
            "full_closures_30d": self.full_closures_30d,
            "search_hit_rate": self.search_hit_rate,
            "end_to_end_rate": self.end_to_end_rate,
        }


# =============================================================================
# SERVICE CLASS
# =============================================================================

class DiscoveryFunnelService:
    """
    Service for tracking the discovery funnel.

    Manages VOI gaps, searches, PDF retrieval attempts, and gap closure.
    """

    def __init__(self, db_path: str = "ae.db"):
        """Initialize with database path."""
        self.db_path = db_path
        self._ensure_tables()

    @contextmanager
    def _get_connection(self):
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _ensure_tables(self):
        """Ensure discovery funnel tables exist."""
        migration_path = Path(__file__).parent.parent.parent / "migrations" / "006_discovery_funnel.sql"
        if migration_path.exists():
            with self._get_connection() as conn:
                # Check if tables exist
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='voi_gaps'"
                )
                if cursor.fetchone() is None:
                    # Run migration
                    with open(migration_path, 'r') as f:
                        conn.executescript(f.read())
                    conn.commit()
                    logger.info("Discovery funnel tables created")

    # -------------------------------------------------------------------------
    # VOI GAPS
    # -------------------------------------------------------------------------

    def create_gap(self, gap: VOIGap) -> VOIGap:
        """Create a new VOI gap."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO voi_gaps (
                    gap_id, topic, gap_type, belief_id, constraint_id, theory_id,
                    predicted_voi, uncertainty_reduction, coherence_impact,
                    search_terms, target_article_types, target_sources,
                    status, priority, identified_at, identified_by, web_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                gap.gap_id, gap.topic, gap.gap_type.value,
                gap.belief_id, gap.constraint_id, gap.theory_id,
                gap.predicted_voi, gap.uncertainty_reduction, gap.coherence_impact,
                json.dumps(gap.search_terms), json.dumps(gap.target_article_types),
                json.dumps(gap.target_sources),
                gap.status.value, gap.priority, gap.identified_at,
                gap.identified_by, gap.web_id
            ))
            conn.commit()
        logger.info(f"Created VOI gap: {gap.gap_id} - {gap.topic}")
        return gap

    def get_gap(self, gap_id: str) -> Optional[VOIGap]:
        """Get a VOI gap by ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM voi_gaps WHERE gap_id = ?", (gap_id,)
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_gap(row)
        return None

    def list_gaps(
        self,
        status: Optional[GapStatus] = None,
        theory_id: Optional[str] = None,
        min_voi: Optional[float] = None,
        limit: int = 100
    ) -> List[VOIGap]:
        """List VOI gaps with optional filters."""
        query = "SELECT * FROM voi_gaps WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status.value)
        if theory_id:
            query += " AND theory_id = ?"
            params.append(theory_id)
        if min_voi is not None:
            query += " AND predicted_voi >= ?"
            params.append(min_voi)

        query += " ORDER BY priority DESC, predicted_voi DESC LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return [self._row_to_gap(row) for row in cursor.fetchall()]

    def update_gap_status(
        self,
        gap_id: str,
        status: GapStatus,
        closed_at: Optional[str] = None
    ) -> bool:
        """Update gap status."""
        with self._get_connection() as conn:
            if status == GapStatus.CLOSED and not closed_at:
                closed_at = datetime.now(timezone.utc).isoformat()
            conn.execute("""
                UPDATE voi_gaps
                SET status = ?, closed_at = ?
                WHERE gap_id = ?
            """, (status.value, closed_at, gap_id))
            conn.commit()
            return conn.total_changes > 0

    def _row_to_gap(self, row: sqlite3.Row) -> VOIGap:
        """Convert database row to VOIGap."""
        return VOIGap(
            gap_id=row["gap_id"],
            topic=row["topic"],
            gap_type=GapType(row["gap_type"]),
            predicted_voi=row["predicted_voi"],
            status=GapStatus(row["status"]),
            belief_id=row["belief_id"],
            constraint_id=row["constraint_id"],
            theory_id=row["theory_id"],
            web_id=row["web_id"],
            uncertainty_reduction=row["uncertainty_reduction"],
            coherence_impact=row["coherence_impact"],
            search_terms=json.loads(row["search_terms"] or "[]"),
            target_article_types=json.loads(row["target_article_types"] or "[]"),
            target_sources=json.loads(row["target_sources"] or "[]"),
            priority=row["priority"],
            identified_at=row["identified_at"],
            identified_by=row["identified_by"],
            last_searched_at=row["last_searched_at"],
            closed_at=row["closed_at"],
        )

    # -------------------------------------------------------------------------
    # SEARCHES
    # -------------------------------------------------------------------------

    def record_search(self, search: GapSearch) -> GapSearch:
        """Record a search execution."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO gap_searches (
                    search_id, gap_id, query, source, search_type, filters,
                    n_results, n_relevant, n_new, top_results,
                    avg_relevance_score, best_relevance_score,
                    executed_at, duration_ms, api_response_code,
                    error_message, api_credits_used
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                search.search_id, search.gap_id, search.query, search.source,
                search.search_type, json.dumps(search.filters),
                search.n_results, search.n_relevant, search.n_new,
                json.dumps(search.top_results),
                search.avg_relevance_score, search.best_relevance_score,
                search.executed_at, search.duration_ms, search.api_response_code,
                search.error_message, search.api_credits_used
            ))
            # Update gap last_searched_at
            conn.execute("""
                UPDATE voi_gaps SET last_searched_at = ?, status = ?
                WHERE gap_id = ?
            """, (search.executed_at, GapStatus.SEARCHING.value, search.gap_id))
            conn.commit()
        logger.info(f"Recorded search: {search.search_id} for gap {search.gap_id}")
        return search

    def get_searches_for_gap(self, gap_id: str) -> List[GapSearch]:
        """Get all searches for a gap."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM gap_searches WHERE gap_id = ? ORDER BY executed_at DESC",
                (gap_id,)
            )
            return [self._row_to_search(row) for row in cursor.fetchall()]

    def _row_to_search(self, row: sqlite3.Row) -> GapSearch:
        """Convert database row to GapSearch."""
        return GapSearch(
            search_id=row["search_id"],
            gap_id=row["gap_id"],
            query=row["query"],
            source=row["source"],
            search_type=row["search_type"],
            filters=json.loads(row["filters"] or "{}"),
            n_results=row["n_results"],
            n_relevant=row["n_relevant"],
            n_new=row["n_new"],
            top_results=json.loads(row["top_results"] or "[]"),
            avg_relevance_score=row["avg_relevance_score"],
            best_relevance_score=row["best_relevance_score"],
            executed_at=row["executed_at"],
            duration_ms=row["duration_ms"],
            api_response_code=row["api_response_code"],
            error_message=row["error_message"],
            api_credits_used=row["api_credits_used"],
        )

    # -------------------------------------------------------------------------
    # PDF RETRIEVAL
    # -------------------------------------------------------------------------

    def record_retrieval_attempt(self, attempt: PDFRetrievalAttempt) -> PDFRetrievalAttempt:
        """Record a PDF retrieval attempt."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO pdf_retrieval_attempts (
                    article_id, doi, title, url, gap_id, search_id,
                    method, source_domain, status,
                    pdf_path, pdf_size_bytes, pdf_pages, content_hash,
                    http_status_code, error_message, retry_after,
                    attempted_at, duration_ms, attempt_number, max_retries
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                attempt.article_id, attempt.doi, attempt.title, attempt.url,
                attempt.gap_id, attempt.search_id,
                attempt.method.value, attempt.source_domain, attempt.status.value,
                attempt.pdf_path, attempt.pdf_size_bytes, attempt.pdf_pages,
                attempt.content_hash,
                attempt.http_status_code, attempt.error_message, attempt.retry_after,
                attempt.attempted_at, attempt.duration_ms,
                attempt.attempt_number, attempt.max_retries
            ))
            attempt.attempt_id = cursor.lastrowid
            conn.commit()
        status_log = "SUCCESS" if attempt.succeeded else attempt.status.value
        logger.info(f"Recorded retrieval attempt: {attempt.doi or attempt.title} - {status_log}")
        return attempt

    def get_retrieval_attempts(
        self,
        gap_id: Optional[str] = None,
        status: Optional[RetrievalStatus] = None,
        limit: int = 100
    ) -> List[PDFRetrievalAttempt]:
        """Get retrieval attempts with optional filters."""
        query = "SELECT * FROM pdf_retrieval_attempts WHERE 1=1"
        params = []

        if gap_id:
            query += " AND gap_id = ?"
            params.append(gap_id)
        if status:
            query += " AND status = ?"
            params.append(status.value)

        query += " ORDER BY attempted_at DESC LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return [self._row_to_retrieval(row) for row in cursor.fetchall()]

    def get_retrieval_stats(self) -> Dict[str, Any]:
        """Get retrieval statistics by method and status."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT method, status, COUNT(*) as count
                FROM pdf_retrieval_attempts
                WHERE attempted_at >= datetime('now', '-30 days')
                GROUP BY method, status
                ORDER BY count DESC
            """)
            stats = {}
            for row in cursor.fetchall():
                method = row["method"]
                if method not in stats:
                    stats[method] = {"total": 0, "success": 0, "failures": {}}
                stats[method]["total"] += row["count"]
                if row["status"] == "success":
                    stats[method]["success"] = row["count"]
                else:
                    stats[method]["failures"][row["status"]] = row["count"]
            return stats

    def _row_to_retrieval(self, row: sqlite3.Row) -> PDFRetrievalAttempt:
        """Convert database row to PDFRetrievalAttempt."""
        return PDFRetrievalAttempt(
            attempt_id=row["attempt_id"],
            article_id=row["article_id"],
            doi=row["doi"],
            title=row["title"],
            url=row["url"],
            gap_id=row["gap_id"],
            search_id=row["search_id"],
            method=RetrievalMethod(row["method"]),
            source_domain=row["source_domain"],
            status=RetrievalStatus(row["status"]),
            pdf_path=row["pdf_path"],
            pdf_size_bytes=row["pdf_size_bytes"],
            pdf_pages=row["pdf_pages"],
            content_hash=row["content_hash"],
            http_status_code=row["http_status_code"],
            error_message=row["error_message"],
            retry_after=row["retry_after"],
            attempted_at=row["attempted_at"],
            duration_ms=row["duration_ms"],
            attempt_number=row["attempt_number"],
            max_retries=row["max_retries"],
        )

    # -------------------------------------------------------------------------
    # GAP CLOSURE
    # -------------------------------------------------------------------------

    def record_closure(self, closure: GapClosure) -> GapClosure:
        """Record a gap closure assessment."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO gap_closure (
                    gap_id, paper_id, voi_before, voi_after,
                    n_beliefs_added, n_constraints_added, relevance_to_gap,
                    closure_type, assessment_method, assessor_notes,
                    paper_ingested_at, assessed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                closure.gap_id, closure.paper_id,
                closure.voi_before, closure.voi_after,
                closure.n_beliefs_added, closure.n_constraints_added,
                closure.relevance_to_gap,
                closure.closure_type.value, closure.assessment_method,
                closure.assessor_notes,
                closure.paper_ingested_at, closure.assessed_at
            ))
            closure.closure_id = cursor.lastrowid

            # Update gap if fully closed
            if closure.closure_type == ClosureType.FULL:
                conn.execute("""
                    UPDATE voi_gaps SET status = ?, closed_at = ?
                    WHERE gap_id = ?
                """, (GapStatus.CLOSED.value, closure.assessed_at, closure.gap_id))

            conn.commit()
        logger.info(
            f"Recorded closure: gap {closure.gap_id} - "
            f"{closure.closure_type.value} (VOI: {closure.voi_before:.2f} → {closure.voi_after:.2f})"
        )
        return closure

    def get_closures_for_gap(self, gap_id: str) -> List[GapClosure]:
        """Get all closure assessments for a gap."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM gap_closure WHERE gap_id = ? ORDER BY assessed_at DESC",
                (gap_id,)
            )
            return [self._row_to_closure(row) for row in cursor.fetchall()]

    def _row_to_closure(self, row: sqlite3.Row) -> GapClosure:
        """Convert database row to GapClosure."""
        return GapClosure(
            closure_id=row["closure_id"],
            gap_id=row["gap_id"],
            paper_id=row["paper_id"],
            voi_before=row["voi_before"],
            voi_after=row["voi_after"],
            n_beliefs_added=row["n_beliefs_added"],
            n_constraints_added=row["n_constraints_added"],
            relevance_to_gap=row["relevance_to_gap"],
            closure_type=ClosureType(row["closure_type"]),
            assessment_method=row["assessment_method"],
            assessor_notes=row["assessor_notes"],
            paper_ingested_at=row["paper_ingested_at"],
            assessed_at=row["assessed_at"],
        )

    # -------------------------------------------------------------------------
    # METRICS
    # -------------------------------------------------------------------------

    def get_funnel_metrics(self) -> FunnelMetrics:
        """Get aggregate funnel metrics."""
        with self._get_connection() as conn:
            metrics = FunnelMetrics()

            # Gap counts
            cursor = conn.execute("""
                SELECT status, COUNT(*) as count, AVG(predicted_voi) as avg_voi
                FROM voi_gaps GROUP BY status
            """)
            for row in cursor.fetchall():
                if row["status"] == "open":
                    metrics.open_gaps = row["count"]
                    metrics.avg_open_gap_voi = row["avg_voi"]
                elif row["status"] == "searching":
                    metrics.searching_gaps = row["count"]
                elif row["status"] == "closed":
                    metrics.closed_gaps = row["count"]

            # Search metrics (30 days)
            cursor = conn.execute("""
                SELECT
                    COUNT(*) as searches,
                    SUM(n_results) as results,
                    AVG(CAST(n_relevant AS REAL) / NULLIF(n_results, 0)) as relevance_rate
                FROM gap_searches
                WHERE executed_at >= datetime('now', '-30 days')
            """)
            row = cursor.fetchone()
            if row:
                metrics.searches_30d = row["searches"] or 0
                metrics.results_found_30d = row["results"] or 0
                metrics.relevance_rate_30d = row["relevance_rate"]

            # Retrieval metrics (30 days)
            cursor = conn.execute("""
                SELECT
                    COUNT(*) as attempts,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successes,
                    SUM(CASE WHEN status = 'paywall' THEN 1 ELSE 0 END) as paywalls,
                    SUM(CASE WHEN status = 'not_found' THEN 1 ELSE 0 END) as not_found,
                    SUM(CASE WHEN status = 'timeout' THEN 1 ELSE 0 END) as timeouts
                FROM pdf_retrieval_attempts
                WHERE attempted_at >= datetime('now', '-30 days')
            """)
            row = cursor.fetchone()
            if row:
                metrics.retrieval_attempts_30d = row["attempts"] or 0
                metrics.retrieval_success_30d = row["successes"] or 0
                if metrics.retrieval_attempts_30d > 0:
                    metrics.pdf_success_rate_30d = (
                        metrics.retrieval_success_30d / metrics.retrieval_attempts_30d * 100
                    )
                metrics.paywall_failures_30d = row["paywalls"] or 0
                metrics.not_found_failures_30d = row["not_found"] or 0
                metrics.timeout_failures_30d = row["timeouts"] or 0

            # Closure metrics (30 days)
            cursor = conn.execute("""
                SELECT
                    COUNT(*) as closures,
                    AVG(voi_before - voi_after) as avg_reduction,
                    SUM(CASE WHEN closure_type = 'full' THEN 1 ELSE 0 END) as full_closures
                FROM gap_closure
                WHERE assessed_at >= datetime('now', '-30 days')
            """)
            row = cursor.fetchone()
            if row:
                metrics.closures_assessed_30d = row["closures"] or 0
                metrics.avg_voi_reduction_30d = row["avg_reduction"]
                metrics.full_closures_30d = row["full_closures"] or 0

            return metrics

    def get_bottleneck_analysis(self) -> Dict[str, Any]:
        """Identify bottlenecks in the funnel."""
        metrics = self.get_funnel_metrics()

        bottlenecks = []

        # Check search effectiveness
        if metrics.relevance_rate_30d is not None and metrics.relevance_rate_30d < 0.3:
            bottlenecks.append({
                "stage": "search",
                "issue": "low_relevance",
                "value": metrics.relevance_rate_30d,
                "recommendation": "Improve search terms or try different sources"
            })

        # Check PDF retrieval
        if metrics.pdf_success_rate_30d is not None and metrics.pdf_success_rate_30d < 60:
            # Identify primary failure mode
            failures = {
                "paywall": metrics.paywall_failures_30d,
                "not_found": metrics.not_found_failures_30d,
                "timeout": metrics.timeout_failures_30d,
            }
            primary_failure = max(failures, key=failures.get)
            bottlenecks.append({
                "stage": "retrieval",
                "issue": f"high_{primary_failure}_rate",
                "value": metrics.pdf_success_rate_30d,
                "primary_failure": primary_failure,
                "recommendation": self._get_retrieval_recommendation(primary_failure)
            })

        # Check gap closure
        if metrics.closures_assessed_30d > 0:
            closure_rate = metrics.full_closures_30d / metrics.closures_assessed_30d
            if closure_rate < 0.25:
                bottlenecks.append({
                    "stage": "closure",
                    "issue": "low_full_closure_rate",
                    "value": closure_rate,
                    "recommendation": "Papers may not be well-matched to gaps"
                })

        return {
            "bottlenecks": bottlenecks,
            "metrics": metrics.to_dict(),
            "health": "good" if len(bottlenecks) == 0 else "degraded" if len(bottlenecks) == 1 else "poor"
        }

    def _get_retrieval_recommendation(self, failure_type: str) -> str:
        """Get recommendation for retrieval failures."""
        recommendations = {
            "paywall": "Try Unpaywall, library access, or author requests",
            "not_found": "Verify DOIs and try alternate URLs",
            "timeout": "Increase timeout or retry with backoff",
        }
        return recommendations.get(failure_type, "Review failure logs")


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_gap_from_voi_result(
    voi_result: Dict[str, Any],
    web_id: Optional[str] = None
) -> VOIGap:
    """Create a VOIGap from a VOI search result."""
    return VOIGap(
        gap_id=str(uuid.uuid4()),
        topic=voi_result.get("topic", voi_result.get("description", "Unknown gap")),
        gap_type=GapType(voi_result.get("gap_type", "missing_evidence")),
        predicted_voi=voi_result.get("voi", voi_result.get("expected_value", 0.5)),
        belief_id=voi_result.get("belief_id"),
        constraint_id=voi_result.get("constraint_id"),
        theory_id=voi_result.get("theory_id"),
        web_id=web_id,
        uncertainty_reduction=voi_result.get("uncertainty_reduction"),
        coherence_impact=voi_result.get("coherence_impact"),
        search_terms=voi_result.get("search_terms", []),
        target_article_types=voi_result.get("target_types", []),
        target_sources=voi_result.get("sources", ["semantic_scholar"]),
        priority=voi_result.get("priority", 0.5),
        identified_by="voi_search",
    )
