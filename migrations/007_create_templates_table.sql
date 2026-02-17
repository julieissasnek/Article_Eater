-- Migration 007: Create templates table for CMR pipeline
-- Per Doc 68 Part 2.1 and Part 4.1
-- Date: 2026-02-17

-- TemplateRecord: DB index for template JSON files
-- Source of truth remains the JSON files; this table provides queryable metadata.

CREATE TABLE IF NOT EXISTS templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Identifiers (unique)
    template_id TEXT UNIQUE NOT NULL,     -- e.g. "COLLABORATIVE_CREATIVITY_ARCHITECTURE_001"
    display_id TEXT UNIQUE NOT NULL,      -- e.g. "CREA4"
    name TEXT NOT NULL,

    -- Classification
    series TEXT NOT NULL,                 -- e.g. "CREA", "L", "MAT", "T"
    generation INTEGER NOT NULL,          -- 1 = T/M/AX series; 2 = domain series

    -- Deduplication status (Doc 67 Part 1)
    dedup_status TEXT NOT NULL,           -- "active" | "superseded" | "residual" | "reference" | "gap"
    superseded_by TEXT,                   -- display_id of superseding template, if applicable

    -- Metadata
    pe_contribution TEXT NOT NULL,        -- "predictive" | "explanatory" | "organizational"
    maturity TEXT NOT NULL,               -- "established" | "supported" | ... | "speculative"
    calibration_status TEXT NOT NULL,     -- "substantial" | "partial" | "protocol" | "uncalibrated"
    practical_accessibility TEXT NOT NULL, -- "A" | "B" | "C" | "D"
    ecological_validation BOOLEAN DEFAULT 0,

    -- File reference
    json_path TEXT NOT NULL,              -- Relative path to JSON file in data/templates/

    -- Source documents
    source_docs TEXT NOT NULL             -- Comma-separated doc numbers, e.g. "55,58,65"
);

-- Indices for common queries
CREATE INDEX IF NOT EXISTS idx_templates_series ON templates(series);
CREATE INDEX IF NOT EXISTS idx_templates_generation ON templates(generation);
CREATE INDEX IF NOT EXISTS idx_templates_dedup_status ON templates(dedup_status);
CREATE INDEX IF NOT EXISTS idx_templates_display_id ON templates(display_id);
CREATE INDEX IF NOT EXISTS idx_templates_series_gen_status ON templates(series, generation, dedup_status);


-- CMREvaluation: A single evaluation run
CREATE TABLE IF NOT EXISTS cmr_evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT DEFAULT (datetime('now')),
    evaluation_type TEXT NOT NULL,        -- "paper" | "building" | "design_review"
    target_description TEXT NOT NULL,
    status TEXT DEFAULT 'in_progress',    -- "in_progress" | "complete" | "failed"
    building_context TEXT                 -- JSON blob for building evaluations
);


-- CMRTemplateActivation: Which templates were activated for an evaluation
CREATE TABLE IF NOT EXISTS cmr_template_activations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id INTEGER REFERENCES cmr_evaluations(id) ON DELETE CASCADE,
    template_display_id TEXT REFERENCES templates(display_id),

    activation_reason TEXT,
    inputs TEXT NOT NULL,                 -- JSON blob
    outputs TEXT,                         -- JSON blob
    wis_score REAL,
    wis_confidence REAL,
    interaction_adjustments TEXT          -- JSON blob
);

CREATE INDEX IF NOT EXISTS idx_cmr_activations_eval ON cmr_template_activations(evaluation_id);


-- CMRDomainScore: Aggregated domain-level scores
CREATE TABLE IF NOT EXISTS cmr_domain_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id INTEGER REFERENCES cmr_evaluations(id) ON DELETE CASCADE,
    domain TEXT NOT NULL,                 -- "A1" through "A10"

    wis_score REAL NOT NULL,
    wis_confidence REAL NOT NULL,
    n_templates_activated INTEGER NOT NULL,
    template_ids TEXT,                    -- Comma-separated

    aggregation_method TEXT DEFAULT 'weighted_average',
    weight_basis TEXT DEFAULT 'calibration_confidence'
);

CREATE INDEX IF NOT EXISTS idx_cmr_domain_eval ON cmr_domain_scores(evaluation_id);


-- CMROverallScore: Overall assessment score
CREATE TABLE IF NOT EXISTS cmr_overall_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id INTEGER REFERENCES cmr_evaluations(id) ON DELETE CASCADE,

    wis_geometric_mean REAL NOT NULL,
    wis_confidence REAL NOT NULL,
    n_domains_assessed INTEGER NOT NULL,

    severe_deficit_domains TEXT,          -- Domains with WIS < 30
    data_gaps TEXT                        -- Domains with insufficient input data
);


-- ReductionClaim: Maps Tier 2 theory constructs to Tier 1 template mechanisms
CREATE TABLE IF NOT EXISTS reduction_claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    tier2_theory TEXT NOT NULL,           -- e.g. "ART", "SRT", "Biophilia"
    tier2_construct TEXT NOT NULL,        -- e.g. "Soft Fascination", "Prospect"

    reduction_type TEXT NOT NULL,         -- "full" | "partial" | "irreducible_residual"
    template_mappings TEXT NOT NULL,      -- JSON blob

    irreducible_residual TEXT,
    confidence TEXT NOT NULL,             -- "high" | "moderate" | "low"
    source_panel TEXT,

    staging_links_reconciled INTEGER DEFAULT 0,
    staging_links_total INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_reduction_theory ON reduction_claims(tier2_theory);
