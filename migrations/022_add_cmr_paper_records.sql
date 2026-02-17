-- ============================================================================
-- Migration 022: Add CMR paper processing history
-- Article Eater Sprint 13 / Task 13.4
-- Date: 2026-02-17
--
-- Adds:
--   - cmr_paper_records
-- ============================================================================

CREATE TABLE IF NOT EXISTS cmr_paper_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    citation TEXT,
    doi TEXT,
    evaluated_at TEXT DEFAULT (datetime('now')) NOT NULL,
    n_claims INTEGER NOT NULL DEFAULT 0,
    n_matched INTEGER NOT NULL DEFAULT 0,
    n_unmatched INTEGER NOT NULL DEFAULT 0,
    n_contradictions INTEGER NOT NULL DEFAULT 0,
    n_confirmations INTEGER NOT NULL DEFAULT 0,
    n_gaps INTEGER NOT NULL DEFAULT 0,
    aggregate_voi REAL NOT NULL DEFAULT 0.0,
    proposals_generated INTEGER NOT NULL DEFAULT 0,
    matched_template_ids TEXT NOT NULL DEFAULT '[]'
);

CREATE INDEX IF NOT EXISTS idx_cmr_paper_records_evaluated_at
ON cmr_paper_records(evaluated_at DESC);

CREATE INDEX IF NOT EXISTS idx_cmr_paper_records_doi
ON cmr_paper_records(doi);

CREATE INDEX IF NOT EXISTS idx_cmr_paper_records_aggregate_voi
ON cmr_paper_records(aggregate_voi DESC);
