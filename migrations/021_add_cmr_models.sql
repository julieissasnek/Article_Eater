-- ============================================================================
-- Migration 021: Add CMR evaluation models
-- Article Eater Sprint 10 / Doc 68 Part 2.2 + 2.3
-- Date: 2026-02-17
--
-- Adds:
--   - cmr_evaluations
--   - cmr_template_activations
--   - cmr_domain_scores
--   - cmr_overall_scores
--   - reduction_claims
-- ============================================================================

CREATE TABLE IF NOT EXISTS cmr_evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT DEFAULT (datetime('now')),
    evaluation_type TEXT NOT NULL,
    target_description TEXT NOT NULL,
    status TEXT DEFAULT 'in_progress',
    building_context TEXT
);

CREATE INDEX IF NOT EXISTS idx_cmr_eval_type ON cmr_evaluations(evaluation_type);
CREATE INDEX IF NOT EXISTS idx_cmr_eval_created ON cmr_evaluations(created_at DESC);

CREATE TABLE IF NOT EXISTS cmr_template_activations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id INTEGER NOT NULL,
    template_display_id TEXT,
    activation_reason TEXT,
    inputs TEXT NOT NULL,
    outputs TEXT,
    wis_score REAL,
    wis_confidence REAL,
    interaction_adjustments TEXT,
    FOREIGN KEY (evaluation_id) REFERENCES cmr_evaluations(id) ON DELETE CASCADE,
    FOREIGN KEY (template_display_id) REFERENCES templates(display_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_cmr_activation_eval ON cmr_template_activations(evaluation_id);
CREATE INDEX IF NOT EXISTS idx_cmr_activation_template ON cmr_template_activations(template_display_id);

CREATE TABLE IF NOT EXISTS cmr_domain_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id INTEGER NOT NULL,
    domain TEXT NOT NULL,
    wis_score REAL NOT NULL,
    wis_confidence REAL NOT NULL,
    n_templates_activated INTEGER NOT NULL,
    template_ids TEXT,
    aggregation_method TEXT DEFAULT 'weighted_average',
    weight_basis TEXT DEFAULT 'calibration_confidence',
    FOREIGN KEY (evaluation_id) REFERENCES cmr_evaluations(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_cmr_domain_eval ON cmr_domain_scores(evaluation_id);
CREATE INDEX IF NOT EXISTS idx_cmr_domain_domain ON cmr_domain_scores(domain);

CREATE TABLE IF NOT EXISTS cmr_overall_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id INTEGER NOT NULL,
    wis_geometric_mean REAL NOT NULL,
    wis_confidence REAL NOT NULL,
    n_domains_assessed INTEGER NOT NULL,
    severe_deficit_domains TEXT,
    data_gaps TEXT,
    FOREIGN KEY (evaluation_id) REFERENCES cmr_evaluations(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_cmr_overall_eval ON cmr_overall_scores(evaluation_id);

CREATE TABLE IF NOT EXISTS reduction_claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tier2_theory TEXT NOT NULL,
    tier2_construct TEXT NOT NULL,
    reduction_type TEXT NOT NULL,
    template_mappings TEXT NOT NULL,
    irreducible_residual TEXT,
    confidence TEXT NOT NULL,
    source_panel TEXT,
    staging_links_reconciled INTEGER DEFAULT 0,
    staging_links_total INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_reduction_claim_theory ON reduction_claims(tier2_theory);
CREATE INDEX IF NOT EXISTS idx_reduction_claim_construct ON reduction_claims(tier2_construct);
