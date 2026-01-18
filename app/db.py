import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "ae.db"


def connect() -> sqlite3.Connection:
    """Create a SQLite connection with sane defaults for concurrent workers.

    This is the *canonical* DB entrypoint for the v20.7.x line. It is used by:

    - app.main (API layer / job enqueuing)
    - app.worker (ResearchWorker queue consumer)
    - scripts/ae_streamlit_control_room.py (dashboard)

    All of those components expect the same core tables:
    - processing_queue
    - articles
    - findings
    plus the security/cost tables from earlier versions.
    """
    con = sqlite3.connect(DB, timeout=30.0)
    # Enable WAL journaling for better concurrency with multiple worker processes.
    con.execute("PRAGMA journal_mode=WAL;")
    # Normal synchronous mode is a good balance of durability vs speed for this use case.
    con.execute("PRAGMA synchronous=NORMAL;")
    # Row factory gives dict-like access in dashboards and utilities.
    con.row_factory = sqlite3.Row
    return con


def ensure_db() -> None:
    """Create the minimal schema required by the v20 research worker.

    This is intentionally aligned with:
    - app.worker.ResearchWorker (job queue + findings)
    - init_database.py sample data
    - scripts/ae_streamlit_control_room.py (status dashboard)

    It does *not* attempt full scientific schema setup (for that, use the
    migration SQL files in db/sql/), but it guarantees that a fresh checkout
    has the tables the worker and dashboard need.
    """
    con = connect()
    cur = con.cursor()

    # ------------------------------------------------------------------
    # 1. Processing Queue
    # ------------------------------------------------------------------
    # Design notes:
    # - `id` is an internal surrogate key used by older pipeline code.
    # - `job_id` is the public, stable identifier used by ResearchWorker.
    # - `params` is JSON-encoded job parameters.
    # - `status` is textual and intentionally *not* CHECK-constrained so we
    #   can support legacy values like 'done' alongside 'pending/complete'.
    cur.execute(
        """CREATE TABLE IF NOT EXISTS processing_queue(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id TEXT UNIQUE,
        job_type TEXT NOT NULL,
        params TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        priority INTEGER DEFAULT 100,
        result TEXT,
        error TEXT,
        created_at TEXT,
        started_at TEXT,
        completed_at TEXT,
        updated_at TEXT
    )"""
    )
    # Backfill schema for existing DBs that used a minimal queue definition.
    cur.execute("PRAGMA table_info(processing_queue)")
    pq_cols = {row[1] for row in cur.fetchall()}
    for col, col_type in {
        "priority": "INTEGER DEFAULT 100",
        "result": "TEXT",
        "error": "TEXT",
        "created_at": "TEXT",
        "started_at": "TEXT",
        "completed_at": "TEXT",
        "updated_at": "TEXT",
    }.items():
        if col not in pq_cols:
            cur.execute(f"ALTER TABLE processing_queue ADD COLUMN {col} {col_type}")

    cur.execute(
        """CREATE INDEX IF NOT EXISTS idx_queue_status
        ON processing_queue(status, priority DESC, created_at ASC)"""
    )

    # ------------------------------------------------------------------
    # 2. Articles
    # ------------------------------------------------------------------
    # This is a superset of the earlier minimal articles table and matches
    # what the worker and sample-data initializer expect.
    cur.execute(
        """CREATE TABLE IF NOT EXISTS articles(
        article_id TEXT PRIMARY KEY,
        title TEXT,
        abstract TEXT,
        doi TEXT,
        corpus_id TEXT,
        authors TEXT,
        year INTEGER,
        venue TEXT,
        full_text TEXT,
        sections TEXT,
        text_length INTEGER,
        is_open_access INTEGER DEFAULT 0,
        citation_count INTEGER DEFAULT 0,
        url_pdf TEXT,
        ingested_at TEXT,
        created_at TEXT
    )"""
    )

    cur.execute(
        """CREATE UNIQUE INDEX IF NOT EXISTS ux_articles_doi
        ON articles(doi)"""
    )
    cur.execute(
        """CREATE UNIQUE INDEX IF NOT EXISTS ux_articles_corpus
        ON articles(corpus_id)"""
    )

    # ------------------------------------------------------------------
    # 3. Findings
    # ------------------------------------------------------------------
    # Minimal causal findings table used by the worker and dashboards.
    cur.execute(
        """CREATE TABLE IF NOT EXISTS findings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        finding_level TEXT,
        consequent TEXT,
        antecedents TEXT,
        operational_measure TEXT,
        measure_type TEXT,
        measure_direction TEXT,
        p_value REAL,
        effect_size REAL,
        effect_size_type TEXT,
        sample_size INTEGER,
        ci_lower REAL,
        ci_upper REAL,
        job_id TEXT,
        paper_id TEXT,
        created_at TEXT,
        FOREIGN KEY(paper_id) REFERENCES articles(article_id)
    )"""
    )
    # Backfill schema for existing DBs missing newer columns.
    cur.execute("PRAGMA table_info(findings)")
    existing_cols = {row[1] for row in cur.fetchall()}
    for col, col_type in {
        "effect_size_type": "TEXT",
        "ci_lower": "REAL",
        "ci_upper": "REAL",
    }.items():
        if col not in existing_cols:
            cur.execute(f"ALTER TABLE findings ADD COLUMN {col} {col_type}")
    cur.execute(
        """CREATE INDEX IF NOT EXISTS idx_findings_paper
        ON findings(paper_id)"""
    )

    # ------------------------------------------------------------------
    # 3b. Rules + Evidence (for /rules API)
    # ------------------------------------------------------------------
    cur.execute(
        """CREATE TABLE IF NOT EXISTS rules(
        rule_id TEXT PRIMARY KEY,
        rule TEXT NOT NULL,
        confidence REAL,
        triangulation_score REAL,
        contradiction_count INTEGER DEFAULT 0,
        job_id TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS rule_evidence(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rule_id TEXT NOT NULL,
        article_id TEXT NOT NULL,
        passage TEXT,
        page_number INTEGER,
        stance TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(rule_id) REFERENCES rules(rule_id) ON DELETE CASCADE,
        FOREIGN KEY(article_id) REFERENCES articles(article_id) ON DELETE CASCADE
    )"""
    )
    cur.execute(
        """CREATE INDEX IF NOT EXISTS idx_rule_evidence_rule
        ON rule_evidence(rule_id)"""
    )
    cur.execute(
        """CREATE INDEX IF NOT EXISTS idx_rule_evidence_article
        ON rule_evidence(article_id)"""
    )

    # ------------------------------------------------------------------
    # 4. Legacy seven_panel summary (kept for compatibility)
    # ------------------------------------------------------------------
    cur.execute(
        """CREATE TABLE IF NOT EXISTS seven_panel(
        article_id TEXT PRIMARY KEY,
        hypothesis TEXT,
        population_context TEXT,
        manipulations_measures TEXT,
        findings_effect TEXT,
        limitations_confounds TEXT,
        design_type TEXT,
        stats_effect_sizes TEXT
    )"""
    )

    # ------------------------------------------------------------------
    # 5. Auth & Usage (from v18 security schema)
    # ------------------------------------------------------------------
    cur.execute(
        """CREATE TABLE IF NOT EXISTS user_api_keys(
        user_id TEXT NOT NULL,
        provider TEXT NOT NULL,
        enc_key BLOB NOT NULL,
        created_at TEXT,
        PRIMARY KEY (user_id, provider)
    )"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS api_usage_events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        provider TEXT,
        model TEXT,
        tokens_in INTEGER,
        tokens_out INTEGER,
        cost_usd REAL,
        created_at TEXT
    )"""
    )


    # ------------------------------------------------------------------
    # 6. UI Events (lightweight usability telemetry)
    # ------------------------------------------------------------------
    # This table records anonymised interaction events from GUIs
    # (e.g. dashboard, search, admin). It is intentionally small and
    # low-friction: enough to understand what users try to do and
    # where they stumble, without turning into a heavy analytics system.
    cur.execute(
        """CREATE TABLE IF NOT EXISTS ui_events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        user_hash TEXT,
        surface TEXT,
        action TEXT,
        detail_json TEXT
    )"""
    )

    con.commit()
    con.close()


if __name__ == "__main__":
    ensure_db()
