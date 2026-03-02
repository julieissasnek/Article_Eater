# Web of Belief Database Schema Reference
# Auto-generated from web_persistence.py + db_migrations.py
# Last updated: 2026-03-01

## Core Schema (web_persistence.py)

```sql
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
```

## Migration-added Tables (db_migrations.py)

