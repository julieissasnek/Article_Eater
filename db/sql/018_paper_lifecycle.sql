-- Article Eater v23.0 - Paper Lifecycle Tracking Schema
-- Sprint LIFECYCLE: Unified paper processing health tracking
-- Date: 2026-02-09
-- Version: 23.0.1
--
-- Purpose: Track each paper's journey through the full processing pipeline:
--   Discovery → Search → Retrieval → Storage → Typing → Extraction → Synthesis

-- ============================================================
-- ALTER ARTICLES TABLE (add lifecycle fields)
-- ============================================================

-- Add lifecycle stage to existing articles table
-- SQLite doesn't support ADD COLUMN with CHECK in all versions,
-- so we handle validation in the application layer
ALTER TABLE articles ADD COLUMN lifecycle_stage TEXT DEFAULT 'discovered';
ALTER TABLE articles ADD COLUMN lifecycle_updated_at TEXT;
ALTER TABLE articles ADD COLUMN lifecycle_blocked_reason TEXT;

-- ============================================================
-- PAPER LIFECYCLE TABLE (audit trail)
-- ============================================================

-- Track every stage transition for each paper
CREATE TABLE IF NOT EXISTS paper_lifecycle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id TEXT NOT NULL,

    -- Stage info
    stage TEXT NOT NULL,
    -- Valid stages: discovered, searched, retrieved, stored, typed,
    --               extracting, extracted, synthesizing, synthesized, archived, failed

    status TEXT NOT NULL DEFAULT 'started',
    -- Valid statuses: started, in_progress, success, failed, blocked, skipped

    -- Timing
    started_at TEXT DEFAULT (datetime('now')),
    completed_at TEXT,
    duration_seconds REAL,

    -- Context
    run_id TEXT,                    -- Pipeline run that triggered this
    job_id TEXT,                    -- Processing queue job if applicable
    triggered_by TEXT,              -- What initiated this stage (manual, pipeline, api)

    -- Results
    details TEXT,                   -- JSON with stage-specific data
    error_message TEXT,             -- If failed
    blocking_reason TEXT,           -- If blocked

    -- Metrics (stage-specific)
    n_claims INTEGER,               -- For extraction stage
    n_rules INTEGER,                -- For extraction stage
    n_findings INTEGER,             -- For extraction stage
    text_source TEXT,               -- fulltext, abstract, pdf, paper_json_abstract
    text_length INTEGER,
    coherence_score REAL,           -- For synthesis stage

    FOREIGN KEY (paper_id) REFERENCES articles(article_id) ON DELETE CASCADE
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_paper_lifecycle_paper ON paper_lifecycle(paper_id);
CREATE INDEX IF NOT EXISTS idx_paper_lifecycle_stage ON paper_lifecycle(stage);
CREATE INDEX IF NOT EXISTS idx_paper_lifecycle_status ON paper_lifecycle(status);
CREATE INDEX IF NOT EXISTS idx_paper_lifecycle_started ON paper_lifecycle(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_paper_lifecycle_stage_status ON paper_lifecycle(stage, status);

-- ============================================================
-- PIPELINE HEALTH SUMMARY VIEW
-- ============================================================

-- Summary view for dashboard
CREATE VIEW IF NOT EXISTS v_pipeline_health AS
SELECT
    stage,
    status,
    COUNT(*) as count,
    AVG(duration_seconds) as avg_duration_seconds,
    MAX(started_at) as last_activity
FROM paper_lifecycle
WHERE started_at >= datetime('now', '-7 days')
GROUP BY stage, status
ORDER BY stage, status;

-- Papers currently in each stage
CREATE VIEW IF NOT EXISTS v_papers_by_stage AS
SELECT
    a.article_id as paper_id,
    a.title,
    a.year,
    a.lifecycle_stage as current_stage,
    a.lifecycle_updated_at as stage_since,
    a.lifecycle_blocked_reason as blocked_reason,
    (
        SELECT COUNT(*)
        FROM paper_lifecycle pl
        WHERE pl.paper_id = a.article_id
    ) as total_transitions,
    (
        SELECT MAX(started_at)
        FROM paper_lifecycle pl
        WHERE pl.paper_id = a.article_id
    ) as last_activity
FROM articles a
ORDER BY a.lifecycle_updated_at DESC;

-- Blocked papers requiring attention
CREATE VIEW IF NOT EXISTS v_blocked_papers AS
SELECT
    a.article_id as paper_id,
    a.title,
    a.lifecycle_stage as blocked_at_stage,
    a.lifecycle_blocked_reason as reason,
    a.lifecycle_updated_at as blocked_since,
    pl.error_message,
    pl.run_id
FROM articles a
LEFT JOIN paper_lifecycle pl ON (
    pl.paper_id = a.article_id
    AND pl.stage = a.lifecycle_stage
    AND pl.status = 'blocked'
)
WHERE a.lifecycle_blocked_reason IS NOT NULL
ORDER BY a.lifecycle_updated_at ASC;

-- ============================================================
-- PAPER PROCESSING METRICS TABLE
-- ============================================================

-- Aggregate metrics per paper (updated after each stage)
CREATE TABLE IF NOT EXISTS paper_metrics (
    paper_id TEXT PRIMARY KEY,

    -- Processing stats
    first_seen_at TEXT,
    last_processed_at TEXT,
    total_processing_time_seconds REAL,
    n_processing_attempts INTEGER DEFAULT 0,
    n_failures INTEGER DEFAULT 0,

    -- Extraction metrics
    text_source TEXT,
    text_length INTEGER,
    n_claims INTEGER DEFAULT 0,
    n_rules INTEGER DEFAULT 0,
    n_findings INTEGER DEFAULT 0,
    n_tables_extracted INTEGER DEFAULT 0,
    n_table_claims INTEGER DEFAULT 0,

    -- Quality metrics
    extraction_confidence REAL,
    coherence_score REAL,
    has_blocking_issues INTEGER DEFAULT 0,

    -- Web integration
    n_beliefs_added INTEGER DEFAULT 0,
    n_stubs_created INTEGER DEFAULT 0,
    n_tensions_detected INTEGER DEFAULT 0,

    -- Timestamps
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),

    FOREIGN KEY (paper_id) REFERENCES articles(article_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_paper_metrics_updated ON paper_metrics(updated_at DESC);

-- ============================================================
-- SCHEMA VERSION
-- ============================================================

INSERT OR REPLACE INTO schema_version (version, description) VALUES
    ('23.0.1', 'Paper lifecycle tracking: lifecycle stages, audit trail, metrics, health views');

-- ============================================================
-- END OF SCHEMA
-- ============================================================
