-- ============================================================================
-- Migration 006: Discovery Funnel Tracking
-- Article Eater v23.1.0
-- Date: 2026-02-09
--
-- Purpose: Track the full discovery funnel from VOI gap identification
-- through article search, PDF retrieval, and gap closure verification.
--
-- Funnel stages:
--   VOI Gap Identified → Search Executed → Articles Found → PDF Retrieved →
--   Paper Ingested → Gap Closure Assessed
--
-- Key insight: VOI gaps are PREDICTIONS about where articles should exist.
-- This schema tracks how well those predictions pan out.
-- ============================================================================

-- ============================================================
-- VOI GAPS TABLE
-- ============================================================
-- Tracks identified gaps in the web of belief with their predicted value

CREATE TABLE IF NOT EXISTS voi_gaps (
    gap_id TEXT PRIMARY KEY,

    -- What the gap is about
    topic TEXT NOT NULL,                    -- Human-readable topic description
    gap_type TEXT NOT NULL,                 -- missing_evidence, weak_support, contradiction, boundary_unclear

    -- Where the gap was identified
    belief_id TEXT,                         -- Belief with weak support or missing connection
    constraint_id TEXT,                     -- Constraint lacking evidence
    theory_id TEXT,                         -- Theory with gaps

    -- VOI metrics at identification time
    predicted_voi REAL NOT NULL,            -- Expected value of information (0-1)
    uncertainty_reduction REAL,             -- Expected uncertainty reduction
    coherence_impact REAL,                  -- Expected coherence improvement

    -- Search guidance
    search_terms TEXT,                      -- JSON array of suggested search terms
    target_article_types TEXT,              -- JSON array: ["rct", "meta_analysis", etc.]
    target_sources TEXT,                    -- JSON array: ["semantic_scholar", "pubmed", etc.]

    -- Status tracking
    status TEXT NOT NULL DEFAULT 'open',    -- open, searching, found, closed, stale
    priority REAL DEFAULT 0.5,              -- Search priority (0-1)

    -- Timestamps
    identified_at TEXT NOT NULL DEFAULT (datetime('now')),
    last_searched_at TEXT,
    closed_at TEXT,

    -- Context
    identified_by TEXT,                     -- voi_search, manual, credibility_check
    web_id TEXT,                            -- Web of belief where gap was found

    FOREIGN KEY (belief_id) REFERENCES beliefs(belief_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_voi_gaps_status ON voi_gaps(status);
CREATE INDEX IF NOT EXISTS idx_voi_gaps_priority ON voi_gaps(priority DESC);
CREATE INDEX IF NOT EXISTS idx_voi_gaps_voi ON voi_gaps(predicted_voi DESC);
CREATE INDEX IF NOT EXISTS idx_voi_gaps_theory ON voi_gaps(theory_id);
CREATE INDEX IF NOT EXISTS idx_voi_gaps_identified ON voi_gaps(identified_at DESC);

-- ============================================================
-- GAP SEARCHES TABLE
-- ============================================================
-- Tracks search executions linked to gaps

CREATE TABLE IF NOT EXISTS gap_searches (
    search_id TEXT PRIMARY KEY,
    gap_id TEXT NOT NULL,

    -- Search parameters
    query TEXT NOT NULL,                    -- Actual search query executed
    source TEXT NOT NULL,                   -- semantic_scholar, pubmed, google_scholar, crossref
    search_type TEXT DEFAULT 'keyword',     -- keyword, citation, author, doi_lookup
    filters TEXT,                           -- JSON: year range, journal, etc.

    -- Results
    n_results INTEGER DEFAULT 0,            -- Total results returned
    n_relevant INTEGER DEFAULT 0,           -- Results deemed relevant
    n_new INTEGER DEFAULT 0,                -- Results not already in system
    top_results TEXT,                       -- JSON array of top N article IDs/DOIs

    -- Relevance assessment
    avg_relevance_score REAL,               -- Average relevance to gap (0-1)
    best_relevance_score REAL,              -- Best single result relevance

    -- Execution info
    executed_at TEXT NOT NULL DEFAULT (datetime('now')),
    duration_ms INTEGER,
    api_response_code INTEGER,
    error_message TEXT,

    -- Cost tracking (API credits, rate limits)
    api_credits_used REAL DEFAULT 0,

    FOREIGN KEY (gap_id) REFERENCES voi_gaps(gap_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_gap_searches_gap ON gap_searches(gap_id);
CREATE INDEX IF NOT EXISTS idx_gap_searches_source ON gap_searches(source);
CREATE INDEX IF NOT EXISTS idx_gap_searches_executed ON gap_searches(executed_at DESC);

-- ============================================================
-- PDF RETRIEVAL ATTEMPTS TABLE
-- ============================================================
-- Tracks each attempt to retrieve a PDF with detailed failure categorization

CREATE TABLE IF NOT EXISTS pdf_retrieval_attempts (
    attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- What we're trying to get
    article_id TEXT,                        -- Internal article ID if known
    doi TEXT,                               -- DOI if known
    title TEXT,                             -- Title for matching
    url TEXT,                               -- URL attempted

    -- Link to discovery
    gap_id TEXT,                            -- Gap that motivated this retrieval
    search_id TEXT,                         -- Search that found this article

    -- Retrieval method
    method TEXT NOT NULL,                   -- direct_link, unpaywall, scihub, library, author_request, manual
    source_domain TEXT,                     -- Domain of the retrieval source

    -- Result
    status TEXT NOT NULL,                   -- success, paywall, not_found, timeout, rate_limited,
                                            -- access_denied, format_error, corrupt, size_exceeded

    -- Success details
    pdf_path TEXT,                          -- Local path if successful
    pdf_size_bytes INTEGER,
    pdf_pages INTEGER,
    content_hash TEXT,                      -- SHA256 for deduplication

    -- Failure details
    http_status_code INTEGER,
    error_message TEXT,
    retry_after TEXT,                       -- When to retry (for rate limits)

    -- Timing
    attempted_at TEXT NOT NULL DEFAULT (datetime('now')),
    duration_ms INTEGER,

    -- Retry tracking
    attempt_number INTEGER DEFAULT 1,
    max_retries INTEGER DEFAULT 3,

    FOREIGN KEY (gap_id) REFERENCES voi_gaps(gap_id) ON DELETE SET NULL,
    FOREIGN KEY (search_id) REFERENCES gap_searches(search_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_pdf_retrieval_article ON pdf_retrieval_attempts(article_id);
CREATE INDEX IF NOT EXISTS idx_pdf_retrieval_doi ON pdf_retrieval_attempts(doi);
CREATE INDEX IF NOT EXISTS idx_pdf_retrieval_status ON pdf_retrieval_attempts(status);
CREATE INDEX IF NOT EXISTS idx_pdf_retrieval_method ON pdf_retrieval_attempts(method);
CREATE INDEX IF NOT EXISTS idx_pdf_retrieval_gap ON pdf_retrieval_attempts(gap_id);
CREATE INDEX IF NOT EXISTS idx_pdf_retrieval_attempted ON pdf_retrieval_attempts(attempted_at DESC);

-- ============================================================
-- GAP CLOSURE TABLE
-- ============================================================
-- Tracks whether papers actually closed the gaps they were expected to address

CREATE TABLE IF NOT EXISTS gap_closure (
    closure_id INTEGER PRIMARY KEY AUTOINCREMENT,
    gap_id TEXT NOT NULL,
    paper_id TEXT NOT NULL,

    -- Before/after VOI
    voi_before REAL NOT NULL,               -- Gap VOI before this paper
    voi_after REAL NOT NULL,                -- Gap VOI after ingestion
    voi_reduction REAL,                     -- voi_before - voi_after

    -- What the paper contributed
    n_beliefs_added INTEGER DEFAULT 0,
    n_constraints_added INTEGER DEFAULT 0,
    relevance_to_gap REAL,                  -- How relevant was this paper? (0-1)

    -- Assessment
    closure_type TEXT,                      -- full (gap closed), partial (VOI reduced),
                                            -- none (no impact), negative (increased uncertainty)
    assessment_method TEXT,                 -- automatic, manual_review
    assessor_notes TEXT,

    -- Timestamps
    paper_ingested_at TEXT,
    assessed_at TEXT NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY (gap_id) REFERENCES voi_gaps(gap_id) ON DELETE CASCADE,
    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_gap_closure_gap ON gap_closure(gap_id);
CREATE INDEX IF NOT EXISTS idx_gap_closure_paper ON gap_closure(paper_id);
CREATE INDEX IF NOT EXISTS idx_gap_closure_type ON gap_closure(closure_type);
CREATE INDEX IF NOT EXISTS idx_gap_closure_reduction ON gap_closure(voi_reduction DESC);

-- ============================================================
-- DISCOVERY FUNNEL METRICS VIEW
-- ============================================================
-- Aggregate view for funnel dashboard

CREATE VIEW IF NOT EXISTS v_discovery_funnel_metrics AS
SELECT
    -- Gap metrics
    (SELECT COUNT(*) FROM voi_gaps WHERE status = 'open') as open_gaps,
    (SELECT COUNT(*) FROM voi_gaps WHERE status = 'searching') as searching_gaps,
    (SELECT COUNT(*) FROM voi_gaps WHERE status = 'closed') as closed_gaps,
    (SELECT AVG(predicted_voi) FROM voi_gaps WHERE status = 'open') as avg_open_gap_voi,

    -- Search metrics (last 30 days)
    (SELECT COUNT(*) FROM gap_searches
     WHERE executed_at >= datetime('now', '-30 days')) as searches_30d,
    (SELECT SUM(n_results) FROM gap_searches
     WHERE executed_at >= datetime('now', '-30 days')) as results_found_30d,
    (SELECT AVG(n_relevant * 1.0 / NULLIF(n_results, 0)) FROM gap_searches
     WHERE executed_at >= datetime('now', '-30 days') AND n_results > 0) as relevance_rate_30d,

    -- PDF retrieval metrics (last 30 days)
    (SELECT COUNT(*) FROM pdf_retrieval_attempts
     WHERE attempted_at >= datetime('now', '-30 days')) as retrieval_attempts_30d,
    (SELECT COUNT(*) FROM pdf_retrieval_attempts
     WHERE attempted_at >= datetime('now', '-30 days') AND status = 'success') as retrieval_success_30d,
    (SELECT COUNT(*) * 100.0 / NULLIF(COUNT(*), 0) FROM pdf_retrieval_attempts
     WHERE attempted_at >= datetime('now', '-30 days') AND status = 'success') as pdf_success_rate_30d,

    -- Failure breakdown (last 30 days)
    (SELECT COUNT(*) FROM pdf_retrieval_attempts
     WHERE attempted_at >= datetime('now', '-30 days') AND status = 'paywall') as paywall_failures_30d,
    (SELECT COUNT(*) FROM pdf_retrieval_attempts
     WHERE attempted_at >= datetime('now', '-30 days') AND status = 'not_found') as not_found_failures_30d,
    (SELECT COUNT(*) FROM pdf_retrieval_attempts
     WHERE attempted_at >= datetime('now', '-30 days') AND status = 'timeout') as timeout_failures_30d,

    -- Gap closure metrics (last 30 days)
    (SELECT COUNT(*) FROM gap_closure
     WHERE assessed_at >= datetime('now', '-30 days')) as closures_assessed_30d,
    (SELECT AVG(voi_reduction) FROM gap_closure
     WHERE assessed_at >= datetime('now', '-30 days')) as avg_voi_reduction_30d,
    (SELECT COUNT(*) FROM gap_closure
     WHERE assessed_at >= datetime('now', '-30 days') AND closure_type = 'full') as full_closures_30d;

-- ============================================================
-- GAP STATUS VIEW
-- ============================================================
-- Current status of all gaps with search/retrieval summary

CREATE VIEW IF NOT EXISTS v_gap_status AS
SELECT
    g.gap_id,
    g.topic,
    g.gap_type,
    g.predicted_voi,
    g.status,
    g.priority,
    g.identified_at,
    g.theory_id,
    -- Search summary
    (SELECT COUNT(*) FROM gap_searches gs WHERE gs.gap_id = g.gap_id) as n_searches,
    (SELECT SUM(n_results) FROM gap_searches gs WHERE gs.gap_id = g.gap_id) as total_results,
    (SELECT MAX(executed_at) FROM gap_searches gs WHERE gs.gap_id = g.gap_id) as last_search,
    -- Retrieval summary
    (SELECT COUNT(*) FROM pdf_retrieval_attempts pra WHERE pra.gap_id = g.gap_id) as n_retrieval_attempts,
    (SELECT COUNT(*) FROM pdf_retrieval_attempts pra
     WHERE pra.gap_id = g.gap_id AND pra.status = 'success') as n_pdfs_retrieved,
    -- Closure summary
    (SELECT COUNT(*) FROM gap_closure gc WHERE gc.gap_id = g.gap_id) as n_papers_assessed,
    (SELECT SUM(voi_reduction) FROM gap_closure gc WHERE gc.gap_id = g.gap_id) as total_voi_reduction
FROM voi_gaps g
ORDER BY g.priority DESC, g.predicted_voi DESC;

-- ============================================================
-- RETRIEVAL FAILURE ANALYSIS VIEW
-- ============================================================
-- Breakdown of retrieval failures by method and status

CREATE VIEW IF NOT EXISTS v_retrieval_failure_analysis AS
SELECT
    method,
    status,
    COUNT(*) as count,
    AVG(duration_ms) as avg_duration_ms,
    MIN(attempted_at) as first_seen,
    MAX(attempted_at) as last_seen
FROM pdf_retrieval_attempts
WHERE status != 'success'
GROUP BY method, status
ORDER BY count DESC;

-- ============================================================
-- SCHEMA VERSION
-- ============================================================

-- Create schema_version table if it doesn't exist (for standalone usage)
CREATE TABLE IF NOT EXISTS schema_version (
    version TEXT PRIMARY KEY,
    description TEXT,
    applied_at TEXT DEFAULT (datetime('now'))
);

INSERT OR REPLACE INTO schema_version (version, description) VALUES
    ('23.1.0', 'Discovery funnel: VOI gaps, search tracking, PDF retrieval, gap closure');

-- ============================================================
-- END OF MIGRATION
-- ============================================================
