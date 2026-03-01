-- Migration 024: Annotation System (EN-0D)
-- Created: 2026-02-27
-- Purpose: General-purpose annotation layer for the Web of Belief.
--   Immutable append-only with supersession. Separate from template JSONs.

-- Annotation types registry
CREATE TABLE IF NOT EXISTS annotation_types (
    type TEXT PRIMARY KEY,
    layer TEXT NOT NULL,  -- 'evidence', 'relational', 'qa_user'
    description TEXT NOT NULL
);

-- Seed the 10 annotation types
INSERT OR IGNORE INTO annotation_types (type, layer, description) VALUES
    -- Layer 1: Evidence Annotations (attach to templates or beliefs)
    ('CALIBRATION_NOTE',  'evidence',    'Expert commentary on calibration quality'),
    ('SENSITIVITY_FLAG',  'evidence',    'Marks parameters that are uncertain or vary widely across studies'),
    ('EVIDENCE_OVERRIDE', 'evidence',    'Manual upgrade/downgrade of maturity level on a causal link'),
    ('PROVENANCE_PATCH',  'evidence',    'Backfills missing provenance (DOI, panel reference, etc.)'),
    -- Layer 2: Relational Annotations (attach to pairs of entities)
    ('CROSS_REFERENCE',   'relational',  'Links templates that interact, complement, or share mechanisms'),
    ('MOLECULE_LINK',     'relational',  'Connects a template to a molecule or T1.5 theory pathway'),
    ('CLINICAL_CAUTION',  'relational',  'Safety-relevant annotation on a causal link or parameter'),
    -- Layer 3: QA/User-Facing Annotations (attach to answers or questions)
    ('OPEN_QUESTION',     'qa_user',     'Knowledge gap marker — what we do not yet know'),
    ('SEARCH_PROMPT',     'qa_user',     'Directed search suggestion for filling a knowledge gap'),
    ('USER_FEEDBACK',     'qa_user',     'User-reported quality rating and commentary on an answer');

-- Main annotations table
CREATE TABLE IF NOT EXISTS annotations (
    id TEXT PRIMARY KEY,                       -- UUID
    type TEXT NOT NULL REFERENCES annotation_types(type),
    target_type TEXT NOT NULL,                  -- 'template', 'belief', 'answer', 'causal_link', 'parameter'
    target_id TEXT NOT NULL,                    -- ID of the annotated entity
    content TEXT NOT NULL,                      -- The annotation text
    author TEXT NOT NULL DEFAULT 'system',      -- Human name, panel name, or 'system'
    created TEXT NOT NULL,                      -- ISO 8601 timestamp
    provenance TEXT NOT NULL DEFAULT '{}',      -- JSON: how this annotation was created
    confidence REAL NOT NULL DEFAULT 1.0,       -- 0.0–1.0 reliability of the annotation
    supersedes TEXT,                            -- ID of annotation this replaces (NULL if original)
    status TEXT NOT NULL DEFAULT 'active',      -- 'active', 'superseded', 'retracted'
    metadata TEXT NOT NULL DEFAULT '{}',        -- JSON: type-specific extra data

    -- For target_type='parameter', target_id format: 'template_id:param_name'
    -- For target_type='causal_link', target_id format: 'template_id:link_id'

    CHECK (status IN ('active', 'superseded', 'retracted')),
    CHECK (confidence >= 0.0 AND confidence <= 1.0)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_annotations_target
    ON annotations(target_type, target_id);
CREATE INDEX IF NOT EXISTS idx_annotations_type
    ON annotations(type);
CREATE INDEX IF NOT EXISTS idx_annotations_status
    ON annotations(status);
CREATE INDEX IF NOT EXISTS idx_annotations_supersedes
    ON annotations(supersedes);
CREATE INDEX IF NOT EXISTS idx_annotations_author
    ON annotations(author);
