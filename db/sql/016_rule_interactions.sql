CREATE TABLE IF NOT EXISTS rule_interactions (
    interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_a_id TEXT,
    rule_b_id TEXT,
    interaction_type TEXT NOT NULL CHECK(interaction_type IN 
        ('contradiction','statistical_conflict','synergistic','antagonistic','chaining','redundant')),
    status TEXT NOT NULL DEFAULT 'pending_review' CHECK(status IN ('pending_review','resolved','ignored')),
    disambiguation_prompt TEXT,
    notes TEXT,
    detected_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_interaction_type ON rule_interactions(interaction_type);
CREATE INDEX IF NOT EXISTS idx_interaction_status ON rule_interactions(status);