-- Article Eater v20.8 - Theory System Schema Extension
-- Sprint TH-1: Theory Data Model & Registry
-- Date: 2026-01-09
-- Version: 20.8.0

-- ============================================================
-- PREREQUISITE TABLES (created if not exist for standalone use)
-- ============================================================

-- Minimal articles table for foreign key references
CREATE TABLE IF NOT EXISTS articles (
    article_id TEXT PRIMARY KEY,
    doi TEXT UNIQUE,
    title TEXT NOT NULL,
    authors TEXT,
    year INTEGER,
    abstract TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Minimal findings table for foreign key references  
CREATE TABLE IF NOT EXISTS findings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id TEXT,
    finding_level TEXT,
    consequent TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- ============================================================
-- THEORY REGISTRY TABLES
-- ============================================================

-- Core theories table: Named theoretical frameworks
CREATE TABLE IF NOT EXISTS theories (
    theory_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    aliases TEXT,  -- JSON array of alternative names
    
    -- Origins
    originators TEXT,  -- JSON array: [{name, year, doi}]
    year_introduced INTEGER,
    
    -- Structure
    domain TEXT NOT NULL,  -- JSON array of domain_ids this theory addresses
    scope_description TEXT,
    level TEXT NOT NULL CHECK(level IN (
        'framework_theory', 'domain_theory', 'methodological', 'mechanism',
        'meta_principle', 'theory', 'principle'  -- Legacy values for backwards compatibility
    )),
    
    -- Confidence assessment
    overall_confidence REAL CHECK(overall_confidence BETWEEN 0.0 AND 1.0),
    confidence_rationale TEXT,
    quantitative_precision TEXT CHECK(quantitative_precision IN ('high', 'medium', 'low', 'none')),
    
    -- Relations to other theories
    parent_theories TEXT,  -- JSON array of theory_ids (more abstract theories this instantiates)
    child_theories TEXT,  -- JSON array of theory_ids (more specific theories)
    compatible_theories TEXT,  -- JSON array of theory_ids
    competing_theories TEXT,  -- JSON array of theory_ids
    
    -- Evidence summary
    replication_status TEXT CHECK(replication_status IN ('strong', 'moderate', 'mixed', 'weak', 'contested')),
    
    -- Metadata
    extraction_source TEXT,  -- Papers from which theory was extracted
    extracted_by TEXT,  -- Who/what performed extraction
    version INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_theories_level ON theories(level);
CREATE INDEX IF NOT EXISTS idx_theories_confidence ON theories(overall_confidence DESC);

-- Theory core claims: Fundamental propositions of each theory
CREATE TABLE IF NOT EXISTS theory_claims (
    claim_id TEXT PRIMARY KEY,
    theory_id TEXT NOT NULL,
    
    statement TEXT NOT NULL,
    formalization TEXT,  -- Structured/logical representation
    
    necessity TEXT NOT NULL CHECK(necessity IN ('core', 'auxiliary')),
    testability TEXT CHECK(testability IN ('directly_testable', 'indirectly_testable', 'framework')),
    
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (theory_id) REFERENCES theories(theory_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_theory_claims_theory ON theory_claims(theory_id);

-- Theory assumptions: What the theory takes for granted
CREATE TABLE IF NOT EXISTS theory_assumptions (
    assumption_id TEXT PRIMARY KEY,
    theory_id TEXT NOT NULL,
    
    statement TEXT NOT NULL,
    dependent_claims TEXT,  -- JSON array of claim_ids that depend on this assumption
    violation_consequence TEXT,  -- What happens if assumption fails
    
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (theory_id) REFERENCES theories(theory_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_theory_assumptions_theory ON theory_assumptions(theory_id);

-- Theory boundary conditions: Known limits of applicability
CREATE TABLE IF NOT EXISTS theory_boundaries (
    boundary_id TEXT PRIMARY KEY,
    theory_id TEXT NOT NULL,
    
    condition_description TEXT NOT NULL,
    evidence_for_boundary TEXT,  -- JSON array of citations/study_ids
    mechanism_of_failure TEXT,  -- Why theory fails under this condition
    confidence_penalty REAL DEFAULT 0.0,  -- How much to reduce confidence when boundary applies
    
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (theory_id) REFERENCES theories(theory_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_theory_boundaries_theory ON theory_boundaries(theory_id);

-- ============================================================
-- PREDICTION TABLES
-- ============================================================

-- Predictions: Both explicit and derived from theories
CREATE TABLE IF NOT EXISTS predictions (
    prediction_id TEXT PRIMARY KEY,
    source_theory_id TEXT NOT NULL,
    
    -- Content
    statement TEXT NOT NULL,
    prediction_type TEXT NOT NULL CHECK(prediction_type IN ('explicit', 'derived', 'newly_derived')),
    
    -- Structured form
    antecedent_env_conditions TEXT,  -- JSON: environmental conditions
    antecedent_population TEXT,  -- JSON: population conditions  
    antecedent_temporal TEXT,  -- JSON: timing requirements
    antecedent_state TEXT,  -- JSON: required baseline states
    
    consequent_outcome TEXT NOT NULL,  -- variable_id from ontology
    consequent_direction TEXT CHECK(consequent_direction IN ('positive', 'negative', 'null', 'inverted_u', 'complex')),
    consequent_magnitude TEXT CHECK(consequent_magnitude IN ('strong', 'moderate', 'weak', 'unspecified')),
    consequent_mechanism TEXT,  -- Optional mechanism pathway
    
    relation_type TEXT CHECK(relation_type IN ('deterministic', 'probabilistic', 'tendency')),
    
    -- Derivation (for derived predictions)
    derivation_chain TEXT,  -- JSON: [{claim_id, inference_type}]
    auxiliary_assumptions TEXT,  -- JSON array of additional assumptions needed
    
    -- Quantitative (if specified by theory)
    quantitative_point_estimate REAL,
    quantitative_ci_lower REAL,
    quantitative_ci_upper REAL,
    functional_form TEXT,  -- For complex relationships (e.g., inverted-U parameters)
    
    -- Scope
    generality TEXT CHECK(generality IN ('universal', 'domain_specific', 'population_specific', 'context_specific')),
    applicable_populations TEXT,  -- JSON array or "all"
    applicable_contexts TEXT,  -- JSON array
    known_exceptions TEXT,  -- JSON array of documented failure cases
    
    -- Testing status
    testing_status TEXT CHECK(testing_status IN ('untested', 'partially_tested', 'well_tested', 'disconfirmed')),
    overall_support TEXT CHECK(overall_support IN ('strongly_supported', 'supported', 'mixed', 'unsupported', 'disconfirmed', 'untested')),
    test_summary TEXT,
    
    -- Confidence
    prior_confidence REAL CHECK(prior_confidence BETWEEN 0.0 AND 1.0),  -- Before testing
    current_confidence REAL CHECK(current_confidence BETWEEN 0.0 AND 1.0),  -- Given evidence
    theory_contribution REAL,  -- Portion from theory validity
    derivation_contribution REAL,  -- Portion from derivation chain strength
    empirical_contribution REAL,  -- Portion from direct/indirect evidence
    uncertainty_type TEXT CHECK(uncertainty_type IN ('aleatory', 'epistemic', 'both')),
    
    -- Network mapping
    maps_to_edge_id TEXT,  -- If this corresponds to a network edge
    maps_to_nodes TEXT,  -- JSON array of network node ids
    contributes_prior INTEGER DEFAULT 1,  -- Boolean: contributes to edge prior
    prior_weight REAL DEFAULT 1.0,  -- Weight in prior calculation
    
    -- Metadata
    extraction_source TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    
    FOREIGN KEY (source_theory_id) REFERENCES theories(theory_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_predictions_theory ON predictions(source_theory_id);
CREATE INDEX IF NOT EXISTS idx_predictions_status ON predictions(testing_status);
CREATE INDEX IF NOT EXISTS idx_predictions_support ON predictions(overall_support);
CREATE INDEX IF NOT EXISTS idx_predictions_confidence ON predictions(current_confidence DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_outcome ON predictions(consequent_outcome);

-- Prediction evidence: Studies that test predictions
CREATE TABLE IF NOT EXISTS prediction_evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prediction_id TEXT NOT NULL,
    paper_id TEXT NOT NULL,
    finding_id INTEGER,  -- Link to specific finding if available
    
    test_type TEXT CHECK(test_type IN ('direct', 'indirect', 'incidental')),
    result TEXT CHECK(result IN ('supports', 'partial', 'null', 'contradicts')),
    test_strength TEXT CHECK(test_strength IN ('strong', 'moderate', 'weak')),
    
    -- Details
    conditions_met INTEGER DEFAULT 1,  -- Boolean: were theory's conditions met?
    notes TEXT,
    
    -- Impact on confidence
    confidence_delta REAL,  -- How much this evidence changed prediction confidence
    
    created_at TEXT DEFAULT (datetime('now')),
    
    FOREIGN KEY (prediction_id) REFERENCES predictions(prediction_id) ON DELETE CASCADE,
    FOREIGN KEY (paper_id) REFERENCES articles(article_id) ON DELETE CASCADE,
    FOREIGN KEY (finding_id) REFERENCES findings(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_prediction_evidence_prediction ON prediction_evidence(prediction_id);
CREATE INDEX IF NOT EXISTS idx_prediction_evidence_paper ON prediction_evidence(paper_id);
CREATE INDEX IF NOT EXISTS idx_prediction_evidence_result ON prediction_evidence(result);

-- ============================================================
-- THEORY-PAPER RELATIONSHIPS
-- ============================================================

-- Papers that articulate or develop theories (theoretical papers)
CREATE TABLE IF NOT EXISTS theory_papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    theory_id TEXT NOT NULL,
    paper_id TEXT NOT NULL,
    
    contribution_type TEXT CHECK(contribution_type IN ('origination', 'refinement', 'extension', 'critique', 'integration', 'review')),
    contribution_description TEXT,
    
    created_at TEXT DEFAULT (datetime('now')),
    
    FOREIGN KEY (theory_id) REFERENCES theories(theory_id) ON DELETE CASCADE,
    FOREIGN KEY (paper_id) REFERENCES articles(article_id) ON DELETE CASCADE,
    UNIQUE(theory_id, paper_id)
);

CREATE INDEX IF NOT EXISTS idx_theory_papers_theory ON theory_papers(theory_id);
CREATE INDEX IF NOT EXISTS idx_theory_papers_paper ON theory_papers(paper_id);

-- Papers that empirically test theory predictions
CREATE TABLE IF NOT EXISTS theory_testing_papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    theory_id TEXT NOT NULL,
    paper_id TEXT NOT NULL,
    prediction_id TEXT,  -- Specific prediction tested (if identifiable)
    
    -- Test characteristics
    tests_explicitly INTEGER DEFAULT 0,  -- Boolean: paper explicitly frames as theory test
    prediction_tested TEXT,  -- Description of what was tested
    result TEXT CHECK(result IN ('supports', 'partial', 'null', 'contradicts')),
    
    -- Implications
    theory_update_direction TEXT CHECK(theory_update_direction IN ('increase', 'decrease', 'no_change')),
    theory_update_magnitude REAL,  -- How much theory confidence changed
    notes TEXT,
    
    created_at TEXT DEFAULT (datetime('now')),
    
    FOREIGN KEY (theory_id) REFERENCES theories(theory_id) ON DELETE CASCADE,
    FOREIGN KEY (paper_id) REFERENCES articles(article_id) ON DELETE CASCADE,
    FOREIGN KEY (prediction_id) REFERENCES predictions(prediction_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_theory_testing_theory ON theory_testing_papers(theory_id);
CREATE INDEX IF NOT EXISTS idx_theory_testing_paper ON theory_testing_papers(paper_id);
CREATE INDEX IF NOT EXISTS idx_theory_testing_result ON theory_testing_papers(result);

-- ============================================================
-- CONFIDENCE HISTORY (AUDIT TRAIL)
-- ============================================================

-- Track confidence changes over time for theories
CREATE TABLE IF NOT EXISTS theory_confidence_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    theory_id TEXT NOT NULL,
    
    old_confidence REAL,
    new_confidence REAL,
    change_reason TEXT,
    triggered_by TEXT,  -- paper_id or prediction_id that caused update
    
    created_at TEXT DEFAULT (datetime('now')),
    
    FOREIGN KEY (theory_id) REFERENCES theories(theory_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_theory_conf_history_theory ON theory_confidence_history(theory_id);

-- Track confidence changes for predictions
CREATE TABLE IF NOT EXISTS prediction_confidence_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prediction_id TEXT NOT NULL,
    
    old_confidence REAL,
    new_confidence REAL,
    change_reason TEXT,
    triggered_by TEXT,  -- paper_id or finding_id that caused update
    
    created_at TEXT DEFAULT (datetime('now')),
    
    FOREIGN KEY (prediction_id) REFERENCES predictions(prediction_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_pred_conf_history_prediction ON prediction_confidence_history(prediction_id);

-- ============================================================
-- SCHEMA VERSION
-- ============================================================

CREATE TABLE IF NOT EXISTS schema_version (
    version TEXT PRIMARY KEY,
    applied_at TEXT DEFAULT (datetime('now')),
    description TEXT
);

INSERT OR REPLACE INTO schema_version (version, description) VALUES
    ('20.8.0', 'Theory system schema: theories, claims, assumptions, boundaries, predictions, evidence, confidence history');

-- ============================================================
-- END OF SCHEMA
-- ============================================================
