#!/usr/bin/env python3
"""
Article Eater v20.7.25 - Research Queue Worker

This worker polls the v20 processing_queue table (job_id, job_type, params, status, ...)
and executes *real* L0/L2 jobs using:

- Semantic Scholar search (app.services.semantic_scholar)
- Article-essence LLM extraction (app.services.extract_article_essence)

It is governed by config/app.policy.json:

- engine.use_mocks == False  -> worker runs in *research* mode and never fabricates findings.
- engine.use_mocks == True   -> worker refuses to start and points operators to the
  offline smoke test instead of silently returning mock data.

This is deliberately conservative: there is no longer a "pretend we found 10 papers"
path in the default worker entry point.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sqlite3
import sys
import time
import socket
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List

from app.core.policy import load_policy
from app.services.semantic_scholar import search as s2_search
try:
    from app.services.extract_article_essence import extract_findings_from_text
except Exception:  # pragma: no cover - legacy fallback
    from app.services.extract_7panel import extract_findings_from_text

LOGGER = logging.getLogger("ae.worker")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

def _load_env_file() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        if key and key not in os.environ:
            os.environ[key] = val


_load_env_file()

INACTIVITY_TIMEOUT_SECONDS = int(
    os.environ.get("AE_WORKER_IDLE_TIMEOUT_SECONDS", "1800")
)  # default 30 minutes


@dataclass
class Job:
    job_id: str
    job_type: str
    params: Dict[str, Any]
    priority: int
    created_at: str



def get_process_lock(port: int = 4004):
    """Enforce a single worker instance by binding a localhost port."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", port))
    except OSError:
        print("\n" + "-" * 60)
        print(f"❌ FATAL ERROR: Worker is already running (port {port} busy).")
        print("   Running multiple workers can corrupt the job queue.")
        print("   Please close the other worker process before starting a new one.")
        print("-" * 60 + "\n")
        sys.exit(1)
    return s

class ResearchWorker:
    """
    Minimal but *real* worker for L0/L2.

    It never fabricates papers or findings. If upstream services (Semantic Scholar,
    LLM providers) are unavailable, jobs fail with explicit errors and the queue
    status reflects that failure.
    """

    def __init__(self, db_path: str, poll_interval: int = 5):
        self.db_path = db_path
        self.poll_interval = poll_interval
        self.running = False
        self.processed_count = 0
        self.error_count = 0
        # Track when we last processed or saw a job
        self.last_activity = time.time()


    def cleanup_zombies(self) -> None:
        """Reset any jobs that were left in 'running' on worker restart.

        This prevents "zombie" jobs from staying stuck forever if the worker
        crashes mid-run. On startup we mark such jobs as failed with a clear
        error message and completed_at timestamp so dashboards and operators
        can see what happened.
        """
        try:
            with self._conn() as con:
                cur = con.cursor()
                cur.execute(
                    """
                    UPDATE processing_queue
                    SET status = 'failed',
                        error = 'Zombie Job: Detected as stuck on worker restart',
                        completed_at = datetime('now')
                    WHERE status = 'running'
                    """
                )
                if cur.rowcount > 0:
                    LOGGER.warning("🧹 Cleanup: Found and killed %s zombie jobs.", cur.rowcount)
        except Exception as exc:
            LOGGER.error("Failed to cleanup zombies: %s", exc)

    # ---------------------------------------------------------------------
    # DB helpers
    # ---------------------------------------------------------------------
    def _conn(self) -> sqlite3.Connection:
        """Create a SQLite connection against the worker's DB path.

        We mirror the global app.db.connect() behaviour here by:

        - enabling WAL mode, so readers and writers can coexist; and
        - using a 30s timeout to reduce spurious 'database is locked' errors.
        """
        con = sqlite3.connect(self.db_path, timeout=30.0)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA journal_mode=WAL;")
        return con


    def fetch_next_job(self) -> Optional[Job]:
        """Fetch the next pending job, ordered by priority and recency."""
        with self._conn() as con:
            cur = con.cursor()
            cur.execute(
                """
                SELECT job_id, job_type, params, priority, created_at
                FROM processing_queue
                WHERE status = 'pending'
                ORDER BY priority DESC, created_at ASC
                LIMIT 1
                """
            )
            row = cur.fetchone()
            if not row:
                return None
            raw_params = row["params"]
            if isinstance(raw_params, str):
                params = json.loads(raw_params) if raw_params else {}
            else:
                params = raw_params or {}
            return Job(
                job_id=row["job_id"],
                job_type=row["job_type"],
                params=params,
                priority=row["priority"],
                created_at=row["created_at"],
            )

    def _update_status(
        self,
        job_id: str,
        status: str,
        error: Optional[str] = None,
    ) -> None:
        """Update processing_queue row for job_id with new status and optional error."""
        now = datetime.now(timezone.utc).isoformat()
        with self._conn() as con:
            cur = con.cursor()
            cur.execute(
                """
                UPDATE processing_queue
                SET status = ?,
                    error = CASE WHEN ? IS NULL THEN error ELSE ? END,
                    started_at = COALESCE(started_at, ?),
                    completed_at = CASE
                        WHEN ? IN ('complete','failed') THEN ?
                        ELSE completed_at
                    END
                WHERE job_id = ?
                """,
                (
                    status,
                    error,
                    error,
                    now,
                    status,
                    now,
                    job_id,
                ),
            )

    # ---------------------------------------------------------------------
    # L0: Semantic Scholar harvest
    # ---------------------------------------------------------------------
    def run_l0_harvest(self, job: Job) -> None:
        params = job.params
        query = (params.get("query") or "").strip()
        limit = int(params.get("limit", 20))

        if not query:
            raise ValueError("L0_harvest requires a non-empty 'query' parameter")

        LOGGER.info("L0_harvest: query=%r, limit=%d", query, limit)

        # Real Semantic Scholar call; relies on app.services.semantic_scholar.search
        hits = s2_search(query, limit=limit)
        now = datetime.now(timezone.utc).isoformat()

        inserted = 0
        with self._conn() as con:
            cur = con.cursor()
            for h in hits or []:
                paper_id = h.get("paperId") or h.get("paper_id")
                if not paper_id:
                    continue

                ext = h.get("externalIds") or {}
                doi = ext.get("DOI")
                corpus_id = str(ext.get("CorpusId") or h.get("corpusId") or "") or None
                authors = [
                    a.get("name")
                    for a in (h.get("authors") or [])
                    if a.get("name")
                ]
                title = h.get("title") or ""
                abstract = h.get("abstract")
                year = h.get("year")
                venue = h.get("venue") or (h.get("journal") or {}).get("name")
                is_open = bool(h.get("isOpenAccess"))
                citation_count = int(h.get("citationCount") or 0)

                open_pdf = h.get("openAccessPdf") or {}
                url_pdf = open_pdf.get("url") or h.get("url")

                cur.execute(
                    """
                    INSERT OR IGNORE INTO articles(
                        article_id, doi, corpus_id, title, authors, year,
                        venue, abstract, is_open_access, citation_count,
                        url_pdf, ingested_at, created_at
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        str(paper_id),
                        doi,
                        corpus_id,
                        title,
                        json.dumps(authors),
                        year,
                        venue,
                        abstract,
                        is_open,
                        citation_count,
                        url_pdf,
                        now,
                        now,
                    ),
                )
                if cur.rowcount > 0:
                    inserted += 1

            # Record a human-readable result string for dashboards
            cur.execute(
                """
                UPDATE processing_queue
                SET result = ?
                WHERE job_id = ?
                """,
                (f"l0_harvested:{inserted}", job.job_id),
            )

        LOGGER.info("L0_harvest complete: %d articles stored", inserted)

    # ---------------------------------------------------------------------
    # L2: Seven-panel extraction via LLM
    # ---------------------------------------------------------------------
    
    def run_l2_extract(self, job: Job) -> None:
        """
        L2: Extract empirical findings from a set of articles using the seven‑panel LLM.

        This implementation uses a three‑phase Read‑Think‑Write pattern to avoid
        holding SQLite locks while calling the LLM:

        1) Read:  pull all required article text into memory, then close the DB.
        2) Think: call extract_findings_from_text on that in‑memory data only.
        3) Write: reopen the DB and insert all findings in a single write phase.
        """
        params = job.params
        article_ids: List[str] = params.get("article_ids") or []
        topic = (
            params.get("topic")
            or params.get("query")
            or "architecture and built environment"
        )

        if not article_ids:
            raise ValueError("L2_extract requires 'article_ids': list[str] in params")

        LOGGER.info("L2_extract: %d articles (topic=%r)", len(article_ids), topic)

        # ------------------------------------------------------------------
        # Phase 1: READ — fetch article text into local memory, then close DB
        # ------------------------------------------------------------------
        articles: List[Dict[str, Any]] = []

        with self._conn() as con:
            cur = con.cursor()
            for aid in article_ids:
                row = cur.execute(
                    """
                    SELECT abstract, full_text
                    FROM articles
                    WHERE article_id = ?
                    """,
                    (aid,),
                ).fetchone()

                if not row:
                    LOGGER.warning("L2_extract: no article row for id=%r", aid)
                    continue

                full_text = row["full_text"]
                abstract = row["abstract"]
                text = (full_text or abstract or "").strip()
                if not text:
                    LOGGER.warning(
                        "L2_extract: article %r has no full_text/abstract", aid
                    )
                    continue

                articles.append(
                    {
                        "article_id": str(aid),
                        "text": text,
                    }
                )

        if not articles:
            LOGGER.warning(
                "L2_extract: no usable article text found for job %s", job.job_id
            )
            # We still mark the job result so operators see that we ran.
            with self._conn() as con:
                cur = con.cursor()
                cur.execute(
                    """
                    UPDATE processing_queue
                    SET result = ?
                    WHERE job_id = ?
                    """,
                    ("l2_extracted:0", job.job_id),
                )
            return

        # ------------------------------------------------------------------
        # Phase 2: THINK — call the LLM on in‑memory texts only
        # ------------------------------------------------------------------
        results_buffer: List[Dict[str, Any]] = []

        for article in articles:
            aid = article["article_id"]
            text_body = article["text"]

            try:
                findings = extract_findings_from_text(
                    text=text_body,
                    topic=topic,
                    is_admin=False,
                )
            except Exception as exc:
                LOGGER.exception(
                    "L2_extract: error calling extract_findings_from_text for article %r: %s",
                    aid,
                    exc,
                )
                continue

            if not findings:
                LOGGER.info("L2_extract: no findings returned for article %r", aid)
                continue

            for f in findings:
                if not isinstance(f, dict):
                    # The seven‑panel prompt should return dicts; ignore bare strings.
                    continue

                stats = f.get("statistics") or {}
                results_buffer.append(
                    {
                        "article_id": aid,
                        "level": f.get("level") or "meso",
                        "consequent": f.get("finding_text")
                        or f.get("consequent")
                        or "",
                        "antecedents": json.dumps(f.get("antecedents") or []),
                        "operational_measure": f.get("operationalization")
                        or f.get("operational_measure"),
                        "measure_type": f.get("measure_type"),
                        "measure_direction": f.get("measure_direction"),
                        "p_value": stats.get("p_value"),
                        "effect_size": stats.get("effect_size"),
                        "effect_size_type": stats.get("effect_size_type"),
                        "sample_size": stats.get("sample_size"),
                        "ci_lower": stats.get("ci_lower"),
                        "ci_upper": stats.get("ci_upper"),
                    }
                )

        # ------------------------------------------------------------------
        # Phase 3: WRITE — reopen DB and insert findings in a single write pass
        # ------------------------------------------------------------------
        total_inserted = 0
        rules_added = 0
        now = datetime.now(timezone.utc).isoformat()

        with self._conn() as con:
            cur = con.cursor()

            for r in results_buffer:
                cur.execute(
                    """
                    INSERT INTO findings(
                        finding_level,
                        consequent,
                        antecedents,
                        operational_measure,
                        measure_type,
                        measure_direction,
                        p_value,
                        effect_size,
                        effect_size_type,
                        sample_size,
                        ci_lower,
                        ci_upper,
                        job_id,
                        paper_id,
                        created_at
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        r["level"],
                        r["consequent"],
                        r["antecedents"],
                        r["operational_measure"],
                        r["measure_type"],
                        r["measure_direction"],
                        r["p_value"],
                        r["effect_size"],
                        r["effect_size_type"],
                        r["sample_size"],
                        r["ci_lower"],
                        r["ci_upper"],
                        job.job_id,
                        r["article_id"],
                        now,
                    ),
                )
                total_inserted += 1

                # Minimal rule synthesis for API consumers.
                antecedents = []
                try:
                    antecedents = json.loads(r["antecedents"] or "[]")
                except Exception:
                    antecedents = []
                consequent = r["consequent"] or ""
                if antecedents:
                    rule_text = f"{', '.join(antecedents)} -> {consequent}"
                else:
                    rule_text = consequent

                rule_id = f"rule-{job.job_id}-{rules_added + 1}"
                try:
                    cur.execute(
                        """
                        INSERT INTO rules(
                            rule_id, rule, confidence, triangulation_score,
                            contradiction_count, job_id, created_at
                        ) VALUES(?,?,?,?,?,?,?)
                        """,
                        (
                            rule_id,
                            rule_text,
                            0.5,
                            0.0,
                            0,
                            job.job_id,
                            now,
                        ),
                    )
                    cur.execute(
                        """
                        INSERT INTO rule_evidence(
                            rule_id, article_id, passage, page_number, stance
                        ) VALUES(?,?,?,?,?)
                        """,
                        (rule_id, r["article_id"], None, None, "supporting"),
                    )
                    rules_added += 1
                except Exception as exc:
                    LOGGER.warning("L2_extract: unable to add rule for %s: %s", r["article_id"], exc)

            cur.execute(
                """
                UPDATE processing_queue
                SET result = ?
                WHERE job_id = ?
                """,
                (f"l2_extracted:{total_inserted}, rules:{rules_added}", job.job_id),
            )

        LOGGER.info(
            "L2_extract complete: %d findings, %d rules stored for job %s",
            total_inserted,
            rules_added,
            job.job_id,
        )

    def process_job(self, job: Job) -> None:
        LOGGER.info("Processing job %s (%s)", job.job_id, job.job_type)
        self._update_status(job.job_id, "running")
        try:
            if job.job_type == "L0_harvest":
                self.run_l0_harvest(job)
            elif job.job_type == "L2_extract":
                self.run_l2_extract(job)
            else:
                raise ValueError(f"Unsupported job_type: {job.job_type}")
            self._update_status(job.job_id, "complete")
            self.processed_count += 1
        except Exception as exc:  # pragma: no cover - defensive logging
            LOGGER.error("Job %s failed: %s", job.job_id, exc, exc_info=True)
            self._update_status(job.job_id, "failed", error=str(exc))
            self.error_count += 1


    def start(self) -> None:
        """Run the main worker loop with zombie cleanup and idle shutdown."""
        self.running = True
        self.cleanup_zombies()
        LOGGER.info(
            "ResearchWorker starting: db=%s, poll_interval=%ss (idle timeout=%ss)",
            self.db_path,
            self.poll_interval,
            INACTIVITY_TIMEOUT_SECONDS,
        )
        try:
            while self.running:
                job = self.fetch_next_job()
                if job:
                    # Found work: reset idle timer and process job
                    self.last_activity = time.time()
                    self.process_job(job)
                    continue

                idle_time = time.time() - self.last_activity
                if idle_time > INACTIVITY_TIMEOUT_SECONDS:
                    minutes = int(idle_time / 60)
                    LOGGER.info(
                        "Idle timeout reached (%s minutes); shutting down worker.",
                        minutes,
                    )
                    print("\n" + "-" * 60)
                    print(f"💤 IDLE TIMEOUT: No jobs for {minutes} minutes.")
                    print("   Shutting down to free the worker slot for the next user.")
                    print("-" * 60 + "\n")
                    self.running = False
                    break

                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            LOGGER.info("ResearchWorker interrupted by user; stopping.")
        finally:
            self.running = False
            LOGGER.info(
                "ResearchWorker stopped. processed=%s errors=%s",
                self.processed_count,
                self.error_count,
            )

def main() -> None:
    lock_socket = get_process_lock()
    parser = argparse.ArgumentParser(description="Article Eater research-mode worker")
    parser.add_argument(
        "--db",
        dest="db",
        default=os.environ.get("AE_DB", "ae.db"),
        help="Path to SQLite database (default: %(default)s)",
    )
    parser.add_argument(
        "--poll-interval",
        dest="poll_interval",
        type=int,
        default=int(os.environ.get("AE_WORKER_POLL_SECONDS", "5")),
        help="Polling interval in seconds (default: %(default)s)",
    )
    args = parser.parse_args()

    try:
        from app import db as db_mod

        db_mod.DB = Path(args.db)
        db_mod.ensure_db()
    except Exception as exc:
        LOGGER.warning("DB bootstrap failed for %s: %s", args.db, exc)

    policy = load_policy()
    engine_cfg = policy.get("engine", {})
    use_mocks = bool(engine_cfg.get("use_mocks", False))

    if use_mocks:
        LOGGER.error(
            "engine.use_mocks is TRUE in config/app.policy.json; "
            "the research worker will not run in mock mode.\n"
            "To run an offline demo, use scripts/offline_pipeline_smoke.py instead, "
            "or set engine.use_mocks=false for real Semantic Scholar + LLM calls."
        )
        sys.exit(1)

    worker = ResearchWorker(db_path=args.db, poll_interval=args.poll_interval)
    worker.start()


if __name__ == "__main__":
    main()
