#!/usr/bin/env python3
"""Idempotent migration for Article Eater v20.0.
- Adds CI columns to findings (if missing)
- Creates rule_interactions (if missing)
Usage:
  python scripts/migrate_v20.py [db_path]
Defaults to ./ae.db if db_path omitted.
"""
import sys, sqlite3, os
from pathlib import Path

def column_exists(c, table, col):
    c.execute("PRAGMA table_info(%s)" % table)
    return any(r[1]==col for r in c.fetchall())

def ensure_columns(conn):
    c = conn.cursor()
    # findings columns
    for colspec in [("effect_size_type","TEXT"),("ci_lower","REAL"),("ci_upper","REAL")]:
        col, typ = colspec
        if not column_exists(c, "findings", col):
            c.execute(f"ALTER TABLE findings ADD COLUMN {col} {typ};")
    conn.commit()

def ensure_interactions(conn):
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS rule_interactions (
    interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_a_id TEXT,
    rule_b_id TEXT,
    interaction_type TEXT NOT NULL CHECK(interaction_type IN 
        ('contradiction','statistical_conflict','synergistic','antagonistic','chaining','redundant')),
    status TEXT NOT NULL DEFAULT 'pending_review' CHECK(status IN ('pending_review','resolved','ignored')),
    disambiguation_prompt TEXT,
    notes TEXT,
    detected_at TEXT DEFAULT (datetime('now'))
);""")
    c.execute("CREATE INDEX IF NOT EXISTS idx_interaction_type ON rule_interactions(interaction_type);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_interaction_status ON rule_interactions(status);")
    conn.commit()

def main():
    db = sys.argv[1] if len(sys.argv)>1 else "ae.db"
    conn = sqlite3.connect(db)
    ensure_columns(conn)
    ensure_interactions(conn)
    print("Migration complete for", db)

if __name__ == "__main__":
    main()