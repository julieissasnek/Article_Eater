-- ============================================================================
-- Migration 023: Paper Metadata and OVERSEER Monitoring System
-- Article Eater Sprint OVERSEER (Sprint 2)
-- Date: 2026-02-25
--
-- Adds:
--   - paper_metadata table (bibliographic enrichment)
--   - overseer_health_metrics (time-series monitoring)
--   - overseer_invariant_violations (constraint tracking)
--   - overseer_quarantine (belief quarantine with review)
--   - overseer_snapshots (baseline snapshots)
--
-- Philosophical Foundation:
--   - O-7: Parnas information hiding — OVERSEER uses dedicated overseer.db
--   - O-3: Quarantine protocol — violations trigger quarantine, not auto-retire
--   - O-2: Statistical alerting — mean ± 1σ per-theory baselines
--   - INV-0..INV-5: Dijkstra, Haack, Pearl coherentist invariants
-- ============================================================================

-- ============================================================================
-- Table 1: paper_metadata
-- ============================================================================
-- Stores enriched bibliographic data from Semantic Scholar and PDF extraction.
-- Enables temporal ordering (Quine's theory selection by recency),
-- citation graph construction (Pollock's defeat semantics), and
-- community detection (Cartwright's social epistemology).
-- ============================================================================

CREATE TABLE IF NOT EXISTS paper_metadata (
    doi TEXT PRIMARY KEY,
    title TEXT,
    authors_json TEXT,                      -- JSON array of author names
    year INTEGER,
    journal TEXT,
    volume TEXT,
    issue TEXT,
    pages TEXT,
    publisher TEXT,
    citation_count INTEGER,
    influential_citation_count INTEGER,
    references_json TEXT,                   -- JSON array of DOIs
    cited_by_json TEXT,                     -- JSON array of DOIs
    semantic_scholar_id TEXT,
    enriched BOOLEAN DEFAULT 0,
    enriched_at TEXT,
    enrichment_source TEXT,                 -- 'semantic_scholar' | 'pdf_extraction' | 'manual'
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_paper_metadata_year ON paper_metadata(year);
CREATE INDEX IF NOT EXISTS idx_paper_metadata_journal ON paper_metadata(journal);
CREATE INDEX IF NOT EXISTS idx_paper_metadata_s2id ON paper_metadata(semantic_scholar_id);
CREATE INDEX IF NOT EXISTS idx_paper_metadata_enriched ON paper_metadata(enriched);


-- ============================================================================
-- Table 2: overseer_health_metrics
-- ============================================================================
-- Time-series health measurements triggered by:
--   - POST_INTEGRATION: ~5 sec after paper integrates (trigger: PaperIntegrationEvent)
--   - PERIODIC: nightly audit (~15 min)
--   - ALERT: immediately when invariant violation detected
--   - ON_DEMAND: manual inspection
--
-- Coherence metrics (Haack):
--   - global_coherence: aggregate coherence score [0, 1]
--   - per_theory_coherence_json: per-theory scores for per-theory alerting (O-2)
--   - coherence_delta: change since last measurement (INV-4: ≤ 5% decline allowed)
--
-- Conflict metrics (Quine):
--   - conflict_count: number of active constraint violations
--   - conflict_rate: conflicts / total_constraints
--   - new_conflicts_json: constraint_ids added since last measurement
--
-- Completeness metrics (Pearl):
--   - total_beliefs: count of beliefs in web
--   - orphan_belief_count: beliefs with no theory attachment (INV-0)
--   - total_templates: count of discovery templates
--   - templates_with_evidence: count with ≥1 belief
--   - coverage_ratio: templates_with_evidence / total_templates
--
-- Cache health (Cartwright):
--   - total_qa_caches: count of QA answer caches
--   - stale_qa_caches: caches marked STALE (eager invalidation)
--   - cache_freshness: fresh / total
--
-- BN health (Pearl):
--   - bn_edge_count: number of edges in Bayesian network
--   - bn_web_sync_violations: edges not matching web credences (INV-2)
--
-- Provenance health (Haack foundherentism):
--   - beliefs_with_provenance: count with Provenance record
--   - beliefs_without_provenance: count missing Provenance (INV-1)
--   - provenance_coverage: with_provenance / total_beliefs
-- ============================================================================

CREATE TABLE IF NOT EXISTS overseer_health_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    mode TEXT NOT NULL,                     -- POST_INTEGRATION | PERIODIC | ALERT | ON_DEMAND
    trigger_paper_id TEXT,                  -- NULL for periodic/on-demand

    -- Coherence metrics (Haack)
    global_coherence REAL,
    per_theory_coherence_json TEXT,         -- JSON: {theory_id: score}
    coherence_delta REAL,                   -- Change from last measurement

    -- Conflict metrics (Quine)
    conflict_count INTEGER,
    conflict_rate REAL,                     -- conflicts / total_constraints
    new_conflicts_json TEXT,                -- JSON array of constraint_ids

    -- Completeness metrics (Pearl)
    total_beliefs INTEGER,
    orphan_belief_count INTEGER,            -- Beliefs with no theory attachment
    total_templates INTEGER,
    templates_with_evidence INTEGER,
    coverage_ratio REAL,                    -- templates_with_evidence / total_templates

    -- Cache health (Cartwright)
    total_qa_caches INTEGER,
    stale_qa_caches INTEGER,
    cache_freshness REAL,                   -- fresh / total

    -- BN health (Pearl)
    bn_edge_count INTEGER,
    bn_web_sync_violations INTEGER,

    -- Provenance health (Haack foundherentism)
    beliefs_with_provenance INTEGER,
    beliefs_without_provenance INTEGER,
    provenance_coverage REAL
);

CREATE INDEX IF NOT EXISTS idx_overseer_health_ts ON overseer_health_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_overseer_health_mode ON overseer_health_metrics(mode);
CREATE INDEX IF NOT EXISTS idx_overseer_health_paper ON overseer_health_metrics(trigger_paper_id);


-- ============================================================================
-- Table 3: overseer_invariant_violations
-- ============================================================================
-- Records constraint violations detected by health checks.
-- Invariants (Dijkstra, Haack, Pearl):
--   INV-0: System is in OPERATIONAL state (no bootstrap failures)
--   INV-1: Every belief has provenance (Haack foundherentism)
--   INV-2: BN edges reflect web credences (Pearl causal consistency)
--   INV-3: All beliefs conform to ClaimV2 schema
--   INV-4: Coherence decline ≤ 5% per integration (Dijkstra stability)
--   INV-5: No belief has credence outside [0, 1]
--
-- O-3: Violations trigger quarantine, not auto-retire. This table tracks
-- the violation; overseer_quarantine handles the quarantine protocol.
-- ============================================================================

CREATE TABLE IF NOT EXISTS overseer_invariant_violations (
    violation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    invariant_code TEXT NOT NULL,           -- INV-1, INV-2, ..., INV-5
    severity TEXT NOT NULL,                 -- CRITICAL | MAJOR | MINOR
    description TEXT,
    affected_belief_ids_json TEXT,          -- JSON array of belief IDs
    trigger_paper_id TEXT,                  -- Paper that triggered violation (if any)
    resolved BOOLEAN DEFAULT 0,
    resolved_at TEXT,
    resolution_notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_overseer_violations_inv ON overseer_invariant_violations(invariant_code);
CREATE INDEX IF NOT EXISTS idx_overseer_violations_sev ON overseer_invariant_violations(severity);
CREATE INDEX IF NOT EXISTS idx_overseer_violations_unresolved
    ON overseer_invariant_violations(resolved) WHERE resolved = 0;
CREATE INDEX IF NOT EXISTS idx_overseer_violations_ts ON overseer_invariant_violations(timestamp DESC);


-- ============================================================================
-- Table 4: overseer_quarantine
-- ============================================================================
-- O-3: Quarantine Protocol (not auto-retire)
-- When an invariant violation is detected, affected beliefs are quarantined
-- for 7-day human review instead of being automatically removed.
--
-- Workflow:
--   1. Violation detected → belief quarantined with reason + violation_id
--   2. Review deadline set to quarantine_timestamp + 7 days
--   3. Human reviewer examines belief, evidence, and violation
--   4. Reviewer chooses: RESTORED (fix violation, restore belief),
--      RETIRED (accept violation, remove belief), or revert to QUARANTINED
--   5. For restored beliefs, system retries the failing check
--
-- This ensures epistemic humility (Haack) and avoids cascading deletions.
-- ============================================================================

CREATE TABLE IF NOT EXISTS overseer_quarantine (
    quarantine_id INTEGER PRIMARY KEY AUTOINCREMENT,
    belief_id TEXT NOT NULL,
    quarantined_at TEXT NOT NULL DEFAULT (datetime('now')),
    reason TEXT NOT NULL,
    violation_id INTEGER REFERENCES overseer_invariant_violations(violation_id),
    review_deadline TEXT,                   -- 7 days from quarantine (O-3)
    status TEXT DEFAULT 'QUARANTINED',      -- QUARANTINED | REVIEWED | RESTORED | RETIRED
    reviewed_at TEXT,
    reviewer_notes TEXT,
    original_credence REAL,
    original_status TEXT
);

CREATE INDEX IF NOT EXISTS idx_overseer_quarantine_status ON overseer_quarantine(status);
CREATE INDEX IF NOT EXISTS idx_overseer_quarantine_deadline ON overseer_quarantine(review_deadline);
CREATE INDEX IF NOT EXISTS idx_overseer_quarantine_belief ON overseer_quarantine(belief_id);
CREATE INDEX IF NOT EXISTS idx_overseer_quarantine_violation ON overseer_quarantine(violation_id);


-- ============================================================================
-- Table 5: overseer_snapshots
-- ============================================================================
-- Baseline snapshots for statistical alerting (O-2: mean ± 1σ per-theory).
-- Used to detect systematic drift in coherence, conflicts, or coverage.
--
-- Snapshot types:
--   - SETUP_BASELINE: Initial post-setup measurement (defines mean)
--   - PERIODIC: Weekly/monthly measurements for trend analysis
--   - PRE_INTEGRATION: Before major paper integration (baseline shift detection)
--   - POST_INTEGRATION: After integration (delta evaluation)
--
-- metadata_json stores full snapshot data for rollback/comparison.
-- ============================================================================

CREATE TABLE IF NOT EXISTS overseer_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    snapshot_type TEXT NOT NULL,            -- SETUP_BASELINE | PERIODIC | PRE_INTEGRATION | POST_INTEGRATION
    global_coherence REAL,
    total_beliefs INTEGER,
    total_constraints INTEGER,
    total_theories INTEGER,
    metadata_json TEXT                      -- Full snapshot as JSON (for rollback)
);

CREATE INDEX IF NOT EXISTS idx_overseer_snapshots_type ON overseer_snapshots(snapshot_type);
CREATE INDEX IF NOT EXISTS idx_overseer_snapshots_ts ON overseer_snapshots(timestamp DESC);
