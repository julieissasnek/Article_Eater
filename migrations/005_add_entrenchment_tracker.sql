-- ============================================================================
-- Migration 005: Entrenchment Tracker + Paper Publication Metadata
-- Article Eater v23.0.x
-- ============================================================================

-- Paper publication metadata (scholarly timeline replay)
CREATE TABLE IF NOT EXISTS paper_publication (
    paper_id TEXT PRIMARY KEY,
    publication_year INTEGER,
    publication_date TEXT,  -- ISO date (YYYY-MM-DD) when available
    first_seen_at TEXT,  -- system ingestion timestamp
    source TEXT,  -- metadata source (paper_json, bibtex, manual)
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
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
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
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
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_entrenchment_events_web ON entrenchment_events(web_id);
CREATE INDEX IF NOT EXISTS idx_entrenchment_events_belief ON entrenchment_events(belief_id);
CREATE INDEX IF NOT EXISTS idx_entrenchment_events_timeline ON entrenchment_events(timeline_type);

-- End Migration 005
