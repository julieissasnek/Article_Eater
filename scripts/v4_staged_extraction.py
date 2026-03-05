#!/usr/bin/env python3
"""
V4 STAGED EXTRACTION PILOT SYSTEM
==================================

Production-quality staged extraction pipeline with 4 stages:

Stage 1: Classification (cheap, fast)
  - Upload PDF to Gemini Flash
  - Classify: article_type (15 families), family group
  - Output confidence + signals
  - SUCCESS: confidence >= 0.70

Stage 2: Core Extraction (family-specific)
  - Use family-specific V4 prompt (empirical, meta, systematic, etc.)
  - Extract ALL fields from extraction_template.v2.schema.json
  - Enforce field completeness via validation suffix

Stage 3: Verification (optional, 20% of papers by default)
  - Send extraction JSON + PDF text to Claude Haiku/Sonnet
  - Verify: statistics in paper? Hallucinations? Plausible?
  - Output: verification_score, flagged_issues[]

Stage 4: Metrics & Reporting
  - Compare V4 vs V3 for same DOI
  - Field-by-field coverage improvement
  - Regression detection (V4 worse than V3 for same finding)

USAGE:
  # Single PDF
  python v4_staged_extraction.py --pdf /path/to/file.pdf

  # Single DOI
  python v4_staged_extraction.py --doi 10.1234/example

  # Batch from file (one DOI per line)
  python v4_staged_extraction.py --batch dois.txt --limit 10

  # Run specific stages
  python v4_staged_extraction.py --doi 10.1234/example --stage 1
  python v4_staged_extraction.py --doi 10.1234/example --stage all

  # Control verification
  python v4_staged_extraction.py --batch dois.txt --verify-fraction 0.2

  # Dry run
  python v4_staged_extraction.py --batch dois.txt --dry-run

  # Compare against V3
  python v4_staged_extraction.py --batch dois.txt --compare-v3

Author: Claude Opus 4.6
Date: 2026-03-05
Sprint: V4 Staged Extraction Pilot
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import platform
import signal
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

try:
    from google import genai
    from google.genai import types
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.extraction.v4_prompts import (
        PROMPT_CLASSIFY_V4,
        get_family_prompt,
        get_validation_suffix,
        get_verification_prompt,
    )
    HAS_V4_PROMPTS = True
except ImportError:
    HAS_V4_PROMPTS = False

# Setup logging — dual output: console + rotating log file
_log_format = "%(asctime)s [%(levelname)s] %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=_log_format,
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)


def _setup_file_logging(output_dir: Path):
    """Add a file handler so the full session log is saved to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = output_dir / f"v4_extraction_log_{timestamp}.txt"
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)  # File gets everything
    file_handler.setFormatter(logging.Formatter(_log_format))
    logging.getLogger().addHandler(file_handler)
    logger.info(f"Log file: {log_path}")
    return log_path

# Constants
PRICING = {
    "gemini-2.5-flash": {"input": 0.075, "output": 0.30},
    "gemini-2.5-pro": {"input": 1.25, "output": 10.00},
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
}

# Output directory
OUTPUT_DIR = PROJECT_ROOT / "data" / "v4_pilot"

# Lock file for single-instance enforcement
LOCK_FILE = PROJECT_ROOT / "data" / ".v4_extraction.lock"

# Parallelism defaults
DEFAULT_CONCURRENCY = 3  # concurrent Gemini API calls
MAX_CONCURRENCY = 8


# ═══════════════════════════════════════════════════════════════════════════
# PRE-FLIGHT CHECKS: Kill competing processes, validate environment
# ═══════════════════════════════════════════════════════════════════════════

def preflight_check(force: bool = False) -> dict:
    """
    Pre-flight environment check. Run BEFORE any API calls.

    Checks for:
    1. Competing extraction processes (gemini_extraction_queue, auto_ingest, etc.)
    2. Stale lock files from crashed runs
    3. API key validity (format check, not live test)
    4. Disk space for output
    5. Python version and dependency availability

    Returns: dict with preflight report (also logged)
    """
    report = {
        "timestamp": datetime.now().isoformat(),
        "checks_passed": 0,
        "checks_failed": 0,
        "warnings": [],
        "killed_processes": [],
        "environment": {},
    }

    logger.info("=" * 60)
    logger.info("PRE-FLIGHT CHECK")
    logger.info("=" * 60)

    # ── Check 1: Competing extraction processes ──
    competing_scripts = [
        "gemini_extraction_queue",
        "auto_ingest_pdfs",
        "run_stimulus_extraction",
        "reextract_from_pdfs",
        "two_pass_extraction",
        "pdf_extraction_module",
        "v4_staged_extraction",  # another instance of ourselves
    ]

    found_competitors = []
    my_pid = os.getpid()

    try:
        # Use ps to find Python processes
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.splitlines():
            if "python" not in line.lower():
                continue
            for script_name in competing_scripts:
                if script_name in line:
                    # Parse PID (second column in ps aux)
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            pid = int(parts[1])
                            if pid != my_pid:
                                found_competitors.append({
                                    "pid": pid,
                                    "script": script_name,
                                    "cmdline": " ".join(parts[10:])[:120],
                                })
                        except ValueError:
                            pass
    except Exception as e:
        report["warnings"].append(f"Could not scan processes: {e}")

    if found_competitors:
        logger.warning(f"  FOUND {len(found_competitors)} competing extraction process(es):")
        for comp in found_competitors:
            logger.warning(f"    PID {comp['pid']}: {comp['script']} — {comp['cmdline']}")

        if force:
            for comp in found_competitors:
                try:
                    os.kill(comp["pid"], signal.SIGTERM)
                    logger.info(f"    KILLED PID {comp['pid']} ({comp['script']})")
                    report["killed_processes"].append(comp)
                    time.sleep(0.5)
                except ProcessLookupError:
                    logger.info(f"    PID {comp['pid']} already gone")
                except PermissionError:
                    logger.error(f"    Cannot kill PID {comp['pid']} — permission denied")
                    report["checks_failed"] += 1
            report["checks_passed"] += 1
        else:
            logger.error("  Use --force to kill competing processes, or stop them manually.")
            logger.error("  Alternatively, use --skip-preflight to bypass this check.")
            report["checks_failed"] += 1
    else:
        logger.info("  [PASS] No competing extraction processes found")
        report["checks_passed"] += 1

    # ── Check 2: Stale lock file ──
    if LOCK_FILE.exists():
        try:
            lock_data = json.loads(LOCK_FILE.read_text())
            lock_pid = lock_data.get("pid")
            lock_time = lock_data.get("started_at", "unknown")

            # Check if that PID is still alive
            pid_alive = False
            if lock_pid:
                try:
                    os.kill(lock_pid, 0)  # signal 0 = check existence
                    pid_alive = True
                except (ProcessLookupError, PermissionError):
                    pid_alive = False

            if pid_alive and not force:
                logger.error(f"  Lock file held by PID {lock_pid} (started {lock_time})")
                logger.error("  Another V4 extraction is running. Use --force to override.")
                report["checks_failed"] += 1
            else:
                if pid_alive and force:
                    logger.warning(f"  Killing stale lock holder PID {lock_pid}")
                    try:
                        os.kill(lock_pid, signal.SIGTERM)
                        time.sleep(1)
                    except Exception:
                        pass
                logger.info("  [PASS] Removed stale lock file")
                LOCK_FILE.unlink(missing_ok=True)
                report["checks_passed"] += 1
        except Exception:
            LOCK_FILE.unlink(missing_ok=True)
            report["checks_passed"] += 1
    else:
        logger.info("  [PASS] No stale lock file")
        report["checks_passed"] += 1

    # ── Check 3: API keys ──
    gemini_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")

    if gemini_key and len(gemini_key) > 10:
        logger.info(f"  [PASS] Gemini API key found ({gemini_key[:8]}...)")
        report["environment"]["gemini_key"] = True
        report["checks_passed"] += 1
    else:
        logger.error("  [FAIL] No Gemini API key. Set GEMINI_API_KEY or GOOGLE_API_KEY")
        report["environment"]["gemini_key"] = False
        report["checks_failed"] += 1

    if anthropic_key and len(anthropic_key) > 10:
        logger.info(f"  [PASS] Anthropic API key found ({anthropic_key[:8]}...)")
        report["environment"]["anthropic_key"] = True
        report["checks_passed"] += 1
    else:
        logger.info("  [INFO] No Anthropic API key — Stage 3 verification will be skipped")
        report["environment"]["anthropic_key"] = False
        report["warnings"].append("No Anthropic API key; Stage 3 disabled")

    # ── Check 4: Disk space ──
    try:
        import shutil
        usage = shutil.disk_usage(str(OUTPUT_DIR.parent))
        free_gb = usage.free / (1024**3)
        if free_gb < 1.0:
            logger.warning(f"  [WARN] Only {free_gb:.1f} GB free disk space")
            report["warnings"].append(f"Low disk: {free_gb:.1f} GB free")
        else:
            logger.info(f"  [PASS] Disk space: {free_gb:.1f} GB free")
        report["environment"]["disk_free_gb"] = round(free_gb, 1)
        report["checks_passed"] += 1
    except Exception:
        report["checks_passed"] += 1

    # ── Check 5: Dependencies ──
    report["environment"]["python"] = platform.python_version()
    report["environment"]["platform"] = platform.system()
    report["environment"]["has_gemini_sdk"] = HAS_GEMINI
    report["environment"]["has_v4_prompts"] = HAS_V4_PROMPTS

    if HAS_GEMINI:
        logger.info(f"  [PASS] google-genai SDK available")
        report["checks_passed"] += 1
    else:
        logger.error("  [FAIL] google-genai SDK not installed. Run: pip install google-genai")
        report["checks_failed"] += 1

    # ── Summary ──
    logger.info("-" * 60)
    status = "READY" if report["checks_failed"] == 0 else "BLOCKED"
    logger.info(f"  Pre-flight: {status} ({report['checks_passed']} passed, {report['checks_failed']} failed)")
    if report["warnings"]:
        for w in report["warnings"]:
            logger.info(f"  Warning: {w}")
    if report["killed_processes"]:
        logger.info(f"  Killed {len(report['killed_processes'])} competing process(es)")
    logger.info("=" * 60)

    return report


def acquire_lock() -> bool:
    """Write lock file to prevent concurrent V4 runs."""
    try:
        LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
        LOCK_FILE.write_text(json.dumps({
            "pid": os.getpid(),
            "started_at": datetime.now().isoformat(),
            "hostname": platform.node(),
        }))
        return True
    except Exception as e:
        logger.error(f"Could not write lock file: {e}")
        return False


def release_lock():
    """Remove lock file on exit."""
    try:
        LOCK_FILE.unlink(missing_ok=True)
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════
# TELEMETRY: System "experience" logging — what it's doing, seeing, deciding
# ═══════════════════════════════════════════════════════════════════════════

class ExtractionTelemetry:
    """
    Rich telemetry for extraction pipeline. Logs what the system is doing
    and 'experiencing' at each stage — decisions, observations, surprises,
    difficulties. Produces a structured log that David can review.
    """

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.events: list[dict] = []
        self.start_time = time.time()
        self.paper_timings: dict[str, dict] = {}  # doi -> {stage: seconds}
        self.field_observations: list[dict] = []   # per-paper field notes
        self.anomalies: list[dict] = []            # unexpected findings
        self.stage_stats = Counter()                # counts per stage outcome
        self._current_paper: Optional[str] = None
        self._paper_start: float = 0
        self._stage_start: float = 0

    def log_event(self, event_type: str, message: str, data: dict = None):
        """Log a telemetry event with timestamp and optional structured data."""
        event = {
            "time": datetime.now().isoformat(),
            "elapsed_s": round(time.time() - self.start_time, 2),
            "type": event_type,
            "message": message,
            "paper": self._current_paper,
        }
        if data:
            event["data"] = data
        self.events.append(event)

        # Also emit to logger with telemetry prefix
        prefix = f"[TEL/{event_type.upper()}]"
        if event_type == "anomaly":
            logger.warning(f"  {prefix} {message}")
        elif event_type == "decision":
            logger.info(f"  {prefix} {message}")
        elif event_type == "observation":
            logger.info(f"  {prefix} {message}")
        elif event_type == "difficulty":
            logger.warning(f"  {prefix} {message}")
        else:
            logger.debug(f"  {prefix} {message}")

    def start_paper(self, doi: str, pdf_path: str):
        """Mark start of processing for a paper."""
        self._current_paper = doi
        self._paper_start = time.time()
        self.paper_timings[doi] = {}
        self.log_event("start", f"Beginning extraction: {doi}", {
            "pdf_path": pdf_path,
            "pdf_exists": Path(pdf_path).exists(),
            "pdf_size_mb": round(Path(pdf_path).stat().st_size / 1024 / 1024, 2) if Path(pdf_path).exists() else 0,
        })

    def start_stage(self, stage: str):
        """Mark start of a pipeline stage."""
        self._stage_start = time.time()
        self.log_event("stage_start", f"Entering {stage}")

    def end_stage(self, stage: str, success: bool, details: dict = None):
        """Mark end of a pipeline stage with timing and outcome."""
        elapsed = round(time.time() - self._stage_start, 2)
        self.paper_timings.get(self._current_paper, {})[stage] = elapsed
        outcome = "success" if success else "failure"
        self.stage_stats[f"{stage}_{outcome}"] += 1
        self.log_event("stage_end", f"{stage} completed in {elapsed}s — {outcome}", {
            "elapsed_s": elapsed,
            "success": success,
            **(details or {}),
        })

    def end_paper(self, doi: str, status: str, cost: float):
        """Mark end of processing for a paper."""
        elapsed = round(time.time() - self._paper_start, 2)
        self.log_event("complete", f"Finished {doi} in {elapsed}s — {status}, ${cost:.4f}", {
            "elapsed_s": elapsed,
            "status": status,
            "cost_usd": cost,
        })
        self._current_paper = None

    def observe_classification(self, article_type: str, confidence: float, signals: list):
        """Log what the classifier saw."""
        self.log_event("observation", f"Classified as '{article_type}' (conf={confidence:.2f})", {
            "article_type": article_type,
            "confidence": confidence,
            "signals": signals,
        })
        if confidence < 0.70:
            self.log_event("anomaly", f"LOW confidence classification ({confidence:.2f}) — extraction may be unreliable", {
                "article_type": article_type,
                "confidence": confidence,
            })
            self.anomalies.append({
                "paper": self._current_paper,
                "type": "low_classification_confidence",
                "confidence": confidence,
            })

    def observe_extraction(self, n_findings: int, field_coverage: dict, article_type: str):
        """Log what the extractor produced and what it noticed about field coverage."""
        # Identify fields that are surprisingly empty or surprisingly full
        surprises = []
        expected_high = ["antecedent", "consequent", "direction"]
        expected_medium = ["sample_size", "effect_size", "quote", "source"]

        for f in expected_high:
            if field_coverage.get(f, 0) < 0.80:
                surprises.append(f"'{f}' unexpectedly low ({field_coverage.get(f, 0):.0%})")

        for f in expected_medium:
            if field_coverage.get(f, 0) > 0.90:
                surprises.append(f"'{f}' surprisingly complete ({field_coverage.get(f, 0):.0%})")

        self.log_event("observation", f"Extracted {n_findings} findings from {article_type}", {
            "n_findings": n_findings,
            "field_coverage": field_coverage,
            "surprises": surprises,
        })

        if n_findings == 0:
            self.log_event("anomaly", "ZERO findings extracted — possibly wrong article type or extraction failure", {
                "article_type": article_type,
            })
            self.anomalies.append({
                "paper": self._current_paper,
                "type": "zero_findings",
                "article_type": article_type,
            })

        if n_findings > 50:
            self.log_event("anomaly", f"Unusually high finding count ({n_findings}) — possible duplication or over-extraction", {
                "n_findings": n_findings,
            })
            self.anomalies.append({
                "paper": self._current_paper,
                "type": "high_finding_count",
                "n_findings": n_findings,
            })

        self.field_observations.append({
            "paper": self._current_paper,
            "article_type": article_type,
            "n_findings": n_findings,
            "field_coverage": field_coverage,
            "surprises": surprises,
        })

    def observe_verification(self, score: float, n_issues: int, issues: list):
        """Log what the verifier found."""
        self.log_event("observation", f"Verification score: {score:.2f}, {n_issues} issues flagged", {
            "score": score,
            "n_issues": n_issues,
        })
        if score < 0.60:
            self.log_event("anomaly", f"LOW verification score ({score:.2f}) — possible hallucinations", {
                "issues": issues[:5],
            })
            self.anomalies.append({
                "paper": self._current_paper,
                "type": "low_verification_score",
                "score": score,
                "n_issues": n_issues,
            })

    def log_decision(self, decision: str, rationale: str, alternatives: list = None):
        """Log a decision the system made and why."""
        self.log_event("decision", f"{decision} — {rationale}", {
            "alternatives": alternatives or [],
        })

    def log_difficulty(self, description: str, resolution: str = None):
        """Log a difficulty encountered and how it was handled."""
        self.log_event("difficulty", description, {
            "resolution": resolution,
        })

    def save_telemetry(self):
        """Save full telemetry log to disk."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.output_dir / f"v4_telemetry_{timestamp}.json"

        total_elapsed = round(time.time() - self.start_time, 2)

        # Build summary
        summary = {
            "total_elapsed_s": total_elapsed,
            "total_papers": len(self.paper_timings),
            "stage_outcomes": dict(self.stage_stats),
            "anomaly_count": len(self.anomalies),
            "anomaly_types": dict(Counter(a["type"] for a in self.anomalies)),
        }

        # Compute per-field coverage across all papers
        all_coverages: dict[str, list] = {}
        for obs in self.field_observations:
            for field_name, cov in obs.get("field_coverage", {}).items():
                all_coverages.setdefault(field_name, []).append(cov)

        field_summary = {}
        for field_name, values in sorted(all_coverages.items()):
            if values:
                field_summary[field_name] = {
                    "mean": round(sum(values) / len(values), 3),
                    "min": round(min(values), 3),
                    "max": round(max(values), 3),
                    "n_papers": len(values),
                }

        telemetry_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": summary,
            "field_coverage_summary": field_summary,
            "anomalies": self.anomalies,
            "paper_timings": self.paper_timings,
            "field_observations": self.field_observations,
            "events": self.events,
        }

        with open(filepath, "w") as f:
            json.dump(telemetry_data, f, indent=2, default=str)

        logger.info(f"Telemetry saved: {filepath}")

        # Also print human-readable summary
        self._print_experience_summary(summary, field_summary)

        return filepath

    def _print_experience_summary(self, summary: dict, field_summary: dict):
        """Print a human-readable summary of what the system experienced."""
        logger.info("")
        logger.info("=" * 60)
        logger.info("SYSTEM EXPERIENCE REPORT")
        logger.info("=" * 60)
        logger.info(f"  Processed {summary['total_papers']} papers in {summary['total_elapsed_s']:.0f}s")

        # Stage outcomes
        for key, count in sorted(summary["stage_outcomes"].items()):
            logger.info(f"  {key}: {count}")

        # Anomalies
        if self.anomalies:
            logger.info("")
            logger.info(f"  ANOMALIES ({len(self.anomalies)} total):")
            for atype, count in summary["anomaly_types"].items():
                logger.info(f"    {atype}: {count}")
            logger.info("  Top anomalies:")
            for a in self.anomalies[:5]:
                logger.info(f"    [{a['type']}] {a['paper']}")

        # Field coverage
        if field_summary:
            logger.info("")
            logger.info("  FIELD COVERAGE (mean across papers):")
            for fname, stats in sorted(field_summary.items(), key=lambda x: x[1]["mean"], reverse=True):
                bar = "#" * int(stats["mean"] * 20)
                logger.info(f"    {fname:25s} {stats['mean']:.0%} {bar}")

        logger.info("=" * 60)


# ═══════════════════════════════════════════════════════════════════════════
# RETRY WITH EXPONENTIAL BACKOFF + JITTER
# Best practice: tenacity pattern, but stdlib-only for zero extra deps
# ═══════════════════════════════════════════════════════════════════════════

import random as _random

# Error classification
TRANSIENT_STATUS_CODES = {429, 500, 502, 503, 504}
PERMANENT_STATUS_CODES = {400, 401, 403, 404}


def retry_with_backoff(
    func,
    max_retries: int = 5,
    initial_delay: float = 2.0,
    max_delay: float = 30.0,
    jitter: float = 3.0,
    telemetry: Optional['ExtractionTelemetry'] = None,
    context: str = "",
):
    """
    Retry a callable with exponential backoff + jitter.

    Classifies errors as transient (retry) or permanent (fail immediately).
    Logs every retry attempt with timing and reason.

    Returns: result of func()
    Raises: last exception if max retries exceeded
    """
    last_exception = None

    for attempt in range(1, max_retries + 1):
        try:
            return func()
        except Exception as e:
            last_exception = e
            error_str = str(e).lower()

            # Classify: permanent errors don't retry
            is_permanent = (
                "invalid" in error_str and "api" in error_str
                or "permission" in error_str
                or "not found" in error_str
                or "authentication" in error_str
            )

            if is_permanent:
                if telemetry:
                    telemetry.log_difficulty(
                        f"Permanent error on attempt {attempt}: {e}",
                        resolution="No retry — error is not transient"
                    )
                raise

            if attempt == max_retries:
                if telemetry:
                    telemetry.log_difficulty(
                        f"Max retries ({max_retries}) exceeded: {e}",
                        resolution="Giving up — will dead-letter this paper"
                    )
                raise

            # Exponential backoff with full jitter
            delay = min(initial_delay * (2 ** (attempt - 1)), max_delay)
            delay += _random.uniform(0, jitter)

            logger.warning(
                f"  [RETRY {attempt}/{max_retries}] {context}: {e.__class__.__name__}: {e} "
                f"— waiting {delay:.1f}s"
            )
            if telemetry:
                telemetry.log_event("retry", f"Attempt {attempt}/{max_retries} for {context}", {
                    "error": str(e),
                    "delay_s": round(delay, 1),
                    "attempt": attempt,
                })

            time.sleep(delay)

    raise last_exception


# ═══════════════════════════════════════════════════════════════════════════
# CHECKPOINT / CRASH RECOVERY (Write-Ahead Log)
# ═══════════════════════════════════════════════════════════════════════════

class CheckpointManager:
    """
    Write-ahead log for crash recovery. Every paper's status is logged
    BEFORE processing, so if the process crashes, we know exactly
    which papers were completed and can resume from there.
    """

    def __init__(self, checkpoint_dir: Path):
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.wal_file = self.checkpoint_dir / "wal.jsonl"
        self.state_file = self.checkpoint_dir / "checkpoint_state.json"

    def write_wal(self, doi: str, action: str, status: str, data: dict = None):
        """Append to write-ahead log. Called BEFORE and AFTER each paper."""
        entry = {
            "ts": datetime.now().isoformat(),
            "doi": doi,
            "action": action,  # "starting" | "completed" | "failed"
            "status": status,
        }
        if data:
            entry["data"] = data
        with open(self.wal_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def get_completed_dois(self) -> set[str]:
        """Read WAL to find all successfully completed DOIs."""
        completed = set()
        if not self.wal_file.exists():
            return completed
        with open(self.wal_file) as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("action") == "completed":
                        completed.add(entry["doi"])
                except (json.JSONDecodeError, KeyError):
                    continue
        return completed

    def save_state(self, processed: int, failed: int, total_cost: float):
        """Save periodic checkpoint for dashboard monitoring."""
        state = {
            "timestamp": datetime.now().isoformat(),
            "processed": processed,
            "failed": failed,
            "total_cost_usd": round(total_cost, 4),
            "pid": os.getpid(),
        }
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

    def load_state(self) -> dict:
        """Load last checkpoint state."""
        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)
        return {"processed": 0, "failed": 0, "total_cost_usd": 0}


# ═══════════════════════════════════════════════════════════════════════════
# DEAD LETTER QUEUE — permanent failures go here for human review
# ═══════════════════════════════════════════════════════════════════════════

class DeadLetterQueue:
    """
    Papers that fail permanently (not transient) are written here.
    David can review these to understand what went wrong:
    - Malformed PDFs
    - Unparseable Gemini responses
    - Papers that consistently produce zero findings
    - Budget-killed papers
    """

    def __init__(self, output_dir: Path):
        self.dlq_file = output_dir / "dead_letter_queue.jsonl"
        self.count = 0

    def add(self, doi: str, reason: str, error_type: str, details: dict = None):
        """Add a paper to the dead letter queue."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "doi": doi,
            "reason": reason,
            "error_type": error_type,  # "parse_error" | "zero_findings" | "budget_exceeded" | "upload_failed" | "max_retries"
            "details": details or {},
        }
        with open(self.dlq_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        self.count += 1
        logger.warning(f"  [DLQ] {doi}: {reason} ({error_type})")

    def summary(self) -> str:
        """Return summary of dead-lettered papers."""
        if self.count == 0:
            return "No dead-lettered papers"
        types = Counter()
        if self.dlq_file.exists():
            with open(self.dlq_file) as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        types[entry.get("error_type", "unknown")] += 1
                    except Exception:
                        pass
        parts = [f"{k}: {v}" for k, v in types.most_common()]
        return f"{self.count} dead-lettered papers ({', '.join(parts)})"


# ═══════════════════════════════════════════════════════════════════════════
# BUDGET TRACKER — kill switch when spend exceeds limit
# ═══════════════════════════════════════════════════════════════════════════

class BudgetTracker:
    """
    Tracks cumulative API cost and halts processing when budget is exceeded.
    David authorized $200 — this prevents runaway spend.
    """

    def __init__(self, budget_limit: float = 200.0):
        self.budget_limit = budget_limit
        self.spent = 0.0
        self.per_paper_costs: list[float] = []

    def add_cost(self, cost: float, doi: str = ""):
        """Record cost for a paper."""
        self.spent += cost
        self.per_paper_costs.append(cost)
        if cost > 0:
            logger.debug(f"  [COST] +${cost:.4f} (total: ${self.spent:.4f} / ${self.budget_limit:.2f})")

    def check_budget(self) -> bool:
        """Returns True if budget is exceeded (should stop)."""
        return self.spent >= self.budget_limit

    def remaining(self) -> float:
        return max(0, self.budget_limit - self.spent)

    def avg_cost_per_paper(self) -> float:
        if self.per_paper_costs:
            return sum(self.per_paper_costs) / len(self.per_paper_costs)
        return 0

    def estimate_papers_remaining(self) -> int:
        """Estimate how many more papers the budget can handle."""
        avg = self.avg_cost_per_paper()
        if avg > 0:
            return int(self.remaining() / avg)
        return 999999

    def budget_report(self) -> str:
        """Human-readable budget status."""
        pct = (self.spent / self.budget_limit * 100) if self.budget_limit > 0 else 0
        return (
            f"Budget: ${self.spent:.4f} / ${self.budget_limit:.2f} "
            f"({pct:.1f}% used, ~{self.estimate_papers_remaining()} papers remaining)"
        )


# ═══════════════════════════════════════════════════════════════════════════
# GRACEFUL SHUTDOWN — handle SIGTERM/SIGINT, save state, exit cleanly
# ═══════════════════════════════════════════════════════════════════════════

class GracefulShutdown:
    """
    Registers signal handlers so Ctrl-C or kill saves state before exiting.
    Sets a flag that the processing loop checks between papers.
    """

    def __init__(self):
        self.should_stop = False
        self._original_sigint = None
        self._original_sigterm = None

    def register(self):
        """Install signal handlers."""
        self._original_sigint = signal.getsignal(signal.SIGINT)
        self._original_sigterm = signal.getsignal(signal.SIGTERM)
        signal.signal(signal.SIGINT, self._handler)
        signal.signal(signal.SIGTERM, self._handler)

    def _handler(self, signum, frame):
        """Handle shutdown signal."""
        sig_name = signal.Signals(signum).name
        logger.warning(f"\n  [{sig_name}] Graceful shutdown requested — finishing current paper...")
        logger.warning("  (Press Ctrl-C again to force-quit)")
        self.should_stop = True
        # Second Ctrl-C forces immediate exit
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    def restore(self):
        """Restore original signal handlers."""
        if self._original_sigint:
            signal.signal(signal.SIGINT, self._original_sigint)
        if self._original_sigterm:
            signal.signal(signal.SIGTERM, self._original_sigterm)


class ExtractionStage(str, Enum):
    """Extraction stages."""
    CLASSIFICATION = "stage_1_classification"
    CORE_EXTRACTION = "stage_2_core_extraction"
    VERIFICATION = "stage_3_verification"
    METRICS = "stage_4_metrics"


class ExtractionStatus(str, Enum):
    """Extraction status."""
    PENDING = "pending"
    CLASSIFIED = "classified"
    EXTRACTED = "extracted"
    VERIFIED = "verified"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ClassificationResult:
    """Result from Stage 1."""
    article_type: str
    family_group: str
    confidence: float
    signals: list[str]
    rationale: str
    cost_usd: float = 0.0
    tokens_input: int = 0
    tokens_output: int = 0


@dataclass
class ExtractionResult:
    """Result from Stage 2."""
    data: dict
    n_findings: int
    field_coverage: dict[str, float]  # field -> % coverage
    cost_usd: float = 0.0
    tokens_input: int = 0
    tokens_output: int = 0


@dataclass
class VerificationResult:
    """Result from Stage 3."""
    score: float  # 0.0-1.0
    flagged_issues: list[dict]
    summary: str
    cost_usd: float = 0.0


@dataclass
class V4ExtractionRecord:
    """Complete extraction record for one paper."""
    doi: str
    pdf_path: str
    status: ExtractionStatus = ExtractionStatus.PENDING

    # Stage 1
    classification: Optional[ClassificationResult] = None

    # Stage 2
    extraction: Optional[ExtractionResult] = None

    # Stage 3
    verification: Optional[VerificationResult] = None

    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    total_cost_usd: float = 0.0
    error_message: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════
# GEMINI CLIENT AND UTILITIES
# ═══════════════════════════════════════════════════════════════════════════

def get_gemini_client() -> genai.Client:
    """Get configured Gemini client."""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
    return genai.Client(api_key=api_key)


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate API cost in USD."""
    pricing = PRICING.get(model, PRICING["gemini-2.5-flash"])
    return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000


def upload_pdf(client: genai.Client, pdf_path: Path, telemetry: Optional[ExtractionTelemetry] = None) -> Optional[str]:
    """Upload PDF and return file URI. Retries on transient failures."""
    if not pdf_path.exists():
        logger.error(f"PDF not found: {pdf_path}")
        return None

    def _do_upload():
        with open(pdf_path, "rb") as f:
            uploaded = client.files.upload(file=f, config={"mime_type": "application/pdf"})

        # Wait for processing
        max_wait = 60  # seconds (increased for large PDFs)
        start = time.time()
        while uploaded.state.name == "PROCESSING":
            if time.time() - start > max_wait:
                raise TimeoutError(f"Upload processing timeout after {max_wait}s: {pdf_path}")
            time.sleep(1)
            uploaded = client.files.get(name=uploaded.name)

        if uploaded.state.name != "ACTIVE":
            raise RuntimeError(f"Upload failed with state: {uploaded.state.name}")

        logger.debug(f"Uploaded: {uploaded.uri}")
        return uploaded.uri

    try:
        return retry_with_backoff(
            _do_upload,
            max_retries=3,
            initial_delay=2.0,
            max_delay=15.0,
            telemetry=telemetry,
            context=f"upload {pdf_path.name}",
        )
    except Exception as e:
        logger.error(f"Upload error after retries: {e}")
        return None


def extract_text_from_pdf(client: genai.Client, pdf_uri: str) -> Optional[str]:
    """Extract raw text from PDF for verification stage."""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_uri(file_uri=pdf_uri, mime_type="application/pdf"),
                "Extract all text from this PDF and return it as plain text. Include numbers, tables, and all content."
            ],
            config=types.GenerateContentConfig(
                temperature=0,
                max_output_tokens=32000,
            ),
        )
        return response.text
    except Exception as e:
        logger.error(f"Text extraction error: {e}")
        return None


def parse_json_response(text: str, context: str = "") -> Optional[dict]:
    """Parse JSON from LLM response, handling markdown blocks."""
    text = text.strip()

    # Remove markdown code blocks
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error{f' ({context})' if context else ''}: {e}")
        logger.debug(f"Failed text: {text[:200]}...")
        return None


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 1: CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════════

def run_stage_1_classification(
    client: genai.Client,
    pdf_uri: str,
    model: str = "gemini-2.5-flash",
    telemetry: Optional[ExtractionTelemetry] = None,
) -> Optional[ClassificationResult]:
    """
    Stage 1: Classify article type. Retries on transient API failures.

    Returns: ClassificationResult or None on error
    """
    logger.info("Stage 1: Classifying article type...")

    def _do_classify():
        response = client.models.generate_content(
            model=model,
            contents=[
                types.Part.from_uri(file_uri=pdf_uri, mime_type="application/pdf"),
                PROMPT_CLASSIFY_V4,
            ],
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=1000,
            ),
        )

        result_data = parse_json_response(response.text, "Stage 1")
        if not result_data:
            raise ValueError("Stage 1 JSON parse failed — will retry")

        usage = response.usage_metadata if response.usage_metadata else None
        cost = 0.0
        if usage:
            cost = calculate_cost(model, usage.prompt_token_count, usage.candidates_token_count)

        return ClassificationResult(
            article_type=result_data.get("article_type", "unknown"),
            family_group=result_data.get("family_group", "unknown"),
            confidence=float(result_data.get("classification_confidence", 0.0)),
            signals=result_data.get("classification_signals", []),
            rationale=result_data.get("brief_rationale", ""),
            cost_usd=cost,
            tokens_input=usage.prompt_token_count if usage else 0,
            tokens_output=usage.candidates_token_count if usage else 0,
        )

    try:
        return retry_with_backoff(
            _do_classify,
            max_retries=3,
            initial_delay=2.0,
            telemetry=telemetry,
            context="Stage 1 classification",
        )
    except Exception as e:
        logger.error(f"Stage 1 error after retries: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 2: CORE EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════

def run_stage_2_extraction(
    client: genai.Client,
    pdf_uri: str,
    article_type: str,
    model: str = "gemini-2.5-flash",
    telemetry: Optional[ExtractionTelemetry] = None,
) -> Optional[ExtractionResult]:
    """
    Stage 2: Extract findings using family-specific prompt. Retries on transient failures.

    Returns: ExtractionResult or None on error
    """
    logger.info(f"Stage 2: Extracting findings ({article_type})...")

    if not HAS_V4_PROMPTS:
        logger.error("V4 prompts not available")
        return None

    family_prompt = get_family_prompt(article_type)
    if not family_prompt:
        logger.error(f"No prompt for article type: {article_type}")
        return None

    full_prompt = family_prompt + get_validation_suffix()

    def _do_extract():
        response = client.models.generate_content(
            model=model,
            contents=[
                types.Part.from_uri(file_uri=pdf_uri, mime_type="application/pdf"),
                full_prompt,
            ],
            config=types.GenerateContentConfig(
                temperature=0.05,
                max_output_tokens=65536,
            ),
        )

        result_data = parse_json_response(response.text, f"Stage 2 ({article_type})")
        if not result_data:
            raise ValueError(f"Stage 2 JSON parse failed for {article_type} — will retry")

        n_findings = len(result_data.get("findings", []))
        field_coverage = compute_field_coverage(result_data, article_type)

        usage = response.usage_metadata if response.usage_metadata else None
        cost = 0.0
        if usage:
            cost = calculate_cost(model, usage.prompt_token_count, usage.candidates_token_count)

        logger.info(f"  Extracted {n_findings} findings")

        return ExtractionResult(
            data=result_data,
            n_findings=n_findings,
            field_coverage=field_coverage,
            cost_usd=cost,
            tokens_input=usage.prompt_token_count if usage else 0,
            tokens_output=usage.candidates_token_count if usage else 0,
        )

    try:
        return retry_with_backoff(
            _do_extract,
            max_retries=3,
            initial_delay=3.0,
            max_delay=30.0,
            telemetry=telemetry,
            context=f"Stage 2 extraction ({article_type})",
        )
    except Exception as e:
        logger.error(f"Stage 2 error after retries: {e}")
        return None


def compute_field_coverage(extraction_data: dict, article_type: str) -> dict[str, float]:
    """
    Compute field coverage percentage for findings.

    Returns: {field_name: coverage_percent, ...}
    """
    findings = extraction_data.get("findings", [])
    if not findings:
        return {}

    # Key fields to track
    critical_fields = {
        "antecedent": 0,
        "consequent": 0,
        "direction": 0,
        "claim_type": 0,
        "p_value": 0,
        "effect_size": 0,
        "sample_size": 0,
        "instruments_used": 0,
        "scope_conditions": 0,
        "source": 0,
        "quote": 0,
    }

    for finding in findings:
        for field in critical_fields:
            value = finding.get(field)
            # Check if field is non-null/non-empty
            is_filled = (
                value is not None and
                (not isinstance(value, (list, dict)) or len(value) > 0) and
                value != ""
            )
            if is_filled:
                critical_fields[field] += 1

    # Compute percentages
    n = len(findings)
    coverage = {
        field: round(count / n, 2)
        for field, count in critical_fields.items()
    }

    return coverage


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 3: VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════

def run_stage_3_verification(
    extraction_data: dict,
    pdf_text: str,
    model: str = "claude-3-5-haiku-20241022"
) -> Optional[VerificationResult]:
    """
    Stage 3: Verify extraction against source text.

    Currently requires Claude API. On David's machine, this will use
    the Anthropic API (ANTHROPIC_API_KEY or CLAUDE_API_KEY).

    Returns: VerificationResult or None
    """
    logger.info("Stage 3: Verifying extraction...")

    try:
        import anthropic
    except ImportError:
        logger.warning("Anthropic SDK not available; skipping verification")
        return None

    api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
    if not api_key:
        logger.warning("ANTHROPIC_API_KEY not set; skipping verification")
        return None

    try:
        client = anthropic.Anthropic(api_key=api_key)

        # Prepare verification prompt
        verify_prompt = get_verification_prompt()
        verify_message = f"""
{verify_prompt}

PAPER TEXT:
{pdf_text[:20000]}

EXTRACTED JSON:
{json.dumps(extraction_data, indent=2)[:10000]}

Now verify this extraction against the paper text above.
"""

        response = client.messages.create(
            model=model,
            max_tokens=2000,
            messages=[
                {"role": "user", "content": verify_message}
            ]
        )

        result_text = response.content[0].text
        result_data = parse_json_response(result_text, "Stage 3 verification")

        if not result_data:
            logger.warning("Stage 3: Could not parse verification result")
            return VerificationResult(
                score=0.5,
                flagged_issues=[],
                summary="Verification parsing failed"
            )

        return VerificationResult(
            score=float(result_data.get("verification_score", 0.5)),
            flagged_issues=result_data.get("flagged_issues", []),
            summary=result_data.get("summary", ""),
        )
    except Exception as e:
        logger.error(f"Stage 3 error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════
# PROCESSING PIPELINE
# ═══════════════════════════════════════════════════════════════════════════

def process_paper(
    client: Optional[genai.Client],
    record: V4ExtractionRecord,
    stages: list[str] = ["1", "2", "3", "4"],
    verify_fraction: float = 0.2,
    dry_run: bool = False,
    model: str = "gemini-2.5-flash",
    telemetry: Optional[ExtractionTelemetry] = None,
) -> V4ExtractionRecord:
    """
    Process a single paper through the extraction pipeline.

    Args:
        client: Gemini client (None for dry runs)
        record: Extraction record
        stages: Which stages to run (1-4)
        verify_fraction: Fraction of papers to verify (Stage 3)
        dry_run: If True, don't actually call APIs
        model: Gemini model name
        telemetry: Telemetry logger for system experience

    Returns: Updated record
    """
    logger.info(f"\n{'─'*40}")
    logger.info(f"Processing: {record.doi}")

    if telemetry:
        telemetry.start_paper(record.doi, record.pdf_path)

    # Check PDF exists
    pdf_path = Path(record.pdf_path)
    if not pdf_path.exists():
        record.error_message = f"PDF not found: {pdf_path}"
        record.status = ExtractionStatus.FAILED
        if telemetry:
            telemetry.log_difficulty(f"PDF not found: {pdf_path}", "Marked as FAILED")
            telemetry.end_paper(record.doi, "failed", 0)
        return record

    # Upload PDF
    logger.info("  Uploading PDF...")
    pdf_uri = None
    if not dry_run:
        if telemetry:
            telemetry.start_stage("upload")
        pdf_uri = upload_pdf(client, pdf_path, telemetry=telemetry)
        if not pdf_uri:
            record.error_message = "PDF upload failed"
            record.status = ExtractionStatus.FAILED
            if telemetry:
                telemetry.log_difficulty("PDF upload failed — Gemini rejected or timed out", "Marked as FAILED")
                telemetry.end_stage("upload", False)
                telemetry.end_paper(record.doi, "failed", 0)
            return record
        if telemetry:
            telemetry.end_stage("upload", True)

    # Stage 1: Classification
    if "1" in stages:
        if telemetry:
            telemetry.start_stage("classification")

        if dry_run:
            logger.info("  [DRY RUN] Stage 1: Classification")
            record.classification = ClassificationResult(
                article_type="empirical_research",
                family_group="empirical",
                confidence=0.95,
                signals=["Methods section", "Results"],
                rationale="DRY RUN",
            )
            if telemetry:
                telemetry.end_stage("classification", True, {"dry_run": True})
        else:
            record.classification = run_stage_1_classification(client, pdf_uri, model=model, telemetry=telemetry)
            if not record.classification:
                record.error_message = "Classification failed"
                record.status = ExtractionStatus.FAILED
                if telemetry:
                    telemetry.log_difficulty("Stage 1 classification returned None", "Marked as FAILED")
                    telemetry.end_stage("classification", False)
                    telemetry.end_paper(record.doi, "failed", 0)
                return record

            record.total_cost_usd += record.classification.cost_usd
            logger.info(f"    → {record.classification.article_type} (conf={record.classification.confidence:.2f})")

            if telemetry:
                telemetry.observe_classification(
                    record.classification.article_type,
                    record.classification.confidence,
                    record.classification.signals,
                )
                telemetry.end_stage("classification", True, {
                    "article_type": record.classification.article_type,
                    "confidence": record.classification.confidence,
                    "cost": record.classification.cost_usd,
                    "tokens_in": record.classification.tokens_input,
                    "tokens_out": record.classification.tokens_output,
                })

        record.status = ExtractionStatus.CLASSIFIED

    # Stage 2: Core Extraction
    if "2" in stages and record.classification:
        article_type = record.classification.article_type

        if telemetry:
            telemetry.start_stage("extraction")
            telemetry.log_decision(
                f"Using '{article_type}' family prompt",
                f"Classified with {record.classification.confidence:.2f} confidence",
                alternatives=["generic prompt", "manual override"],
            )

        if dry_run:
            logger.info("  [DRY RUN] Stage 2: Core Extraction")
            record.extraction = ExtractionResult(
                data={"article_type": article_type, "findings": []},
                n_findings=0,
                field_coverage={}
            )
            if telemetry:
                telemetry.end_stage("extraction", True, {"dry_run": True})
        else:
            record.extraction = run_stage_2_extraction(client, pdf_uri, article_type, model=model, telemetry=telemetry)
            if not record.extraction:
                record.error_message = "Extraction failed"
                record.status = ExtractionStatus.FAILED
                if telemetry:
                    telemetry.log_difficulty(
                        f"Stage 2 extraction failed for {article_type}",
                        "Marked as FAILED — JSON parse error or API failure"
                    )
                    telemetry.end_stage("extraction", False)
                    telemetry.end_paper(record.doi, "failed", record.total_cost_usd)
                return record

            record.total_cost_usd += record.extraction.cost_usd
            logger.info(f"    → {record.extraction.n_findings} findings extracted")

            if telemetry:
                telemetry.observe_extraction(
                    record.extraction.n_findings,
                    record.extraction.field_coverage,
                    article_type,
                )
                telemetry.end_stage("extraction", True, {
                    "n_findings": record.extraction.n_findings,
                    "cost": record.extraction.cost_usd,
                    "tokens_in": record.extraction.tokens_input,
                    "tokens_out": record.extraction.tokens_output,
                    "field_coverage": record.extraction.field_coverage,
                })

        record.status = ExtractionStatus.EXTRACTED

    # Stage 3: Verification
    if "3" in stages and record.extraction and not dry_run:
        import random
        should_verify = random.random() < verify_fraction

        if telemetry:
            telemetry.log_decision(
                f"{'Verifying' if should_verify else 'Skipping verification'} for this paper",
                f"verify_fraction={verify_fraction:.0%}, random draw={'in' if should_verify else 'out'}",
            )

        if should_verify:
            if telemetry:
                telemetry.start_stage("verification")

            pdf_text = extract_text_from_pdf(client, pdf_uri)
            if pdf_text:
                record.verification = run_stage_3_verification(
                    record.extraction.data,
                    pdf_text
                )
                if record.verification:
                    record.total_cost_usd += record.verification.cost_usd
                    logger.info(f"    → Verification score: {record.verification.score:.2f}")
                    if telemetry:
                        telemetry.observe_verification(
                            record.verification.score,
                            len(record.verification.flagged_issues),
                            record.verification.flagged_issues,
                        )
                        telemetry.end_stage("verification", True, {
                            "score": record.verification.score,
                            "n_issues": len(record.verification.flagged_issues),
                        })
                else:
                    if telemetry:
                        telemetry.log_difficulty("Verification returned None — API unavailable?", "Skipped")
                        telemetry.end_stage("verification", False)
            else:
                if telemetry:
                    telemetry.log_difficulty("Could not extract text for verification", "Skipped")
        else:
            logger.info("    → Verification skipped (outside verify_fraction)")

        record.status = ExtractionStatus.VERIFIED

    # Stage 4: Metrics (computed locally, no API call)
    if "4" in stages and record.extraction:
        logger.info("  Stage 4: Computing metrics...")

    if not dry_run:
        record.status = ExtractionStatus.COMPLETED

    record.updated_at = datetime.now(timezone.utc).isoformat()

    if telemetry:
        telemetry.end_paper(record.doi, record.status.value, record.total_cost_usd)

    return record


# ═══════════════════════════════════════════════════════════════════════════
# PARALLEL BATCH PROCESSING
# ═══════════════════════════════════════════════════════════════════════════

async def process_paper_async(
    semaphore: asyncio.Semaphore,
    client: Optional[genai.Client],
    record: V4ExtractionRecord,
    stages: list[str],
    verify_fraction: float,
    dry_run: bool,
    model: str,
    telemetry: Optional[ExtractionTelemetry],
) -> V4ExtractionRecord:
    """Async wrapper for process_paper with semaphore-based concurrency."""
    async with semaphore:
        # Run the synchronous function in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: process_paper(
                client, record, stages, verify_fraction,
                dry_run, model, telemetry,
            )
        )
        return result


async def process_batch_parallel(
    client: Optional[genai.Client],
    work: list[V4ExtractionRecord],
    stages: list[str],
    verify_fraction: float,
    dry_run: bool,
    model: str,
    concurrency: int,
    output_dir: Path,
    telemetry: Optional[ExtractionTelemetry],
) -> list[V4ExtractionRecord]:
    """
    Process a batch of papers with bounded parallelism.

    Uses asyncio + thread pool to run N papers concurrently.
    Saves incrementally every 5 completions.
    """
    semaphore = asyncio.Semaphore(concurrency)
    results: list[V4ExtractionRecord] = []
    completed = 0

    logger.info(f"  Parallel mode: {concurrency} concurrent workers")

    if telemetry:
        telemetry.log_decision(
            f"Running {len(work)} papers with concurrency={concurrency}",
            f"Bounded by semaphore to avoid API rate limits",
            alternatives=[f"sequential (concurrency=1)", f"max parallel (concurrency={len(work)})"],
        )

    tasks = []
    for record in work:
        task = asyncio.create_task(
            process_paper_async(
                semaphore, client, record, stages,
                verify_fraction, dry_run, model, telemetry,
            )
        )
        tasks.append(task)

    # Gather with progress tracking
    for coro in asyncio.as_completed(tasks):
        result = await coro
        results.append(result)
        completed += 1

        logger.info(f"  [{completed}/{len(work)}] {result.doi}: {result.status.value}")

        # Incremental save every 5
        if completed % 5 == 0:
            save_batch(results, output_dir, completed)

    return results


# ═══════════════════════════════════════════════════════════════════════════
# MAIN AND CLI
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="V4 Staged Extraction Pilot System",
        epilog="Pre-flight checks run automatically. Use --skip-preflight to bypass."
    )

    # Input sources
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--pdf", type=str, help="Path to single PDF file")
    input_group.add_argument("--doi", type=str, help="Single DOI (finds PDF by convention)")
    input_group.add_argument("--batch", type=str, help="Batch file (one DOI per line)")

    # Processing options
    parser.add_argument(
        "--stage",
        choices=["1", "2", "3", "4", "all"],
        default="all",
        help="Which stage to run (default: all)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Limit number of papers to process"
    )
    parser.add_argument(
        "--verify-fraction",
        type=float,
        default=0.2,
        help="Fraction of papers to verify in Stage 3 (0.0-1.0)"
    )

    # API options
    parser.add_argument(
        "--model",
        default="gemini-2.5-flash",
        choices=["gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-pro"],
        help="Gemini model to use"
    )

    # Parallelism
    parser.add_argument(
        "--parallel",
        type=int,
        default=DEFAULT_CONCURRENCY,
        help=f"Number of concurrent papers to process (default: {DEFAULT_CONCURRENCY}, max: {MAX_CONCURRENCY})"
    )
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Force sequential processing (overrides --parallel)"
    )

    # Output options
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(OUTPUT_DIR),
        help="Output directory for results"
    )
    parser.add_argument(
        "--compare-v3",
        action="store_true",
        help="Compare extraction against existing V3 results"
    )

    # Budget and recovery
    parser.add_argument(
        "--budget",
        type=float,
        default=200.0,
        help="Maximum API spend in dollars (default: $200). Kill switch triggers at limit."
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from checkpoint (skip already-completed DOIs)"
    )

    # Safety and debug options
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force start: kill competing processes and override stale locks"
    )
    parser.add_argument(
        "--skip-preflight",
        action="store_true",
        help="Skip pre-flight checks (not recommended)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run (don't call APIs)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose logging"
    )
    parser.add_argument(
        "--no-telemetry",
        action="store_true",
        help="Disable telemetry logging"
    )

    args = parser.parse_args()

    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # ── Pre-flight checks ──
    if not args.skip_preflight and not args.dry_run:
        preflight = preflight_check(force=args.force)
        if preflight["checks_failed"] > 0 and not args.force:
            logger.error("Pre-flight failed. Fix issues above or use --force / --skip-preflight")
            sys.exit(1)
    elif args.skip_preflight:
        logger.warning("Pre-flight checks SKIPPED (--skip-preflight)")

    # Validate dependencies
    if not HAS_GEMINI and not args.dry_run:
        logger.error("Gemini SDK not available. Install: pip install google-genai")
        sys.exit(1)

    if not HAS_V4_PROMPTS:
        logger.error("V4 prompts module not available")
        sys.exit(1)

    # ── Acquire lock ──
    if not args.dry_run:
        if not acquire_lock():
            logger.error("Could not acquire process lock")
            sys.exit(1)

    # Register cleanup on exit
    import atexit
    atexit.register(release_lock)

    # ── Build work list ──
    work = []

    # Load PDF mapping if available
    pdf_mapping_path = PROJECT_ROOT / "data" / "pdf_doi_mapping.json"
    pdf_mapping = {}
    if pdf_mapping_path.exists():
        try:
            with open(pdf_mapping_path) as f:
                pdf_mapping = json.load(f)
            logger.info(f"Loaded PDF-DOI mapping: {len(pdf_mapping)} entries")
        except Exception:
            logger.warning("Could not load pdf_doi_mapping.json")

    if args.pdf:
        pdf_path = Path(args.pdf)
        work.append(V4ExtractionRecord(
            doi="unknown",
            pdf_path=str(pdf_path),
        ))
    elif args.doi:
        doi = args.doi
        # Try mapping first, fall back to convention
        pdf_path_str = pdf_mapping.get(doi, {}).get("pdf_path") if isinstance(pdf_mapping.get(doi), dict) else pdf_mapping.get(doi)
        if pdf_path_str:
            pdf_path = Path(pdf_path_str)
        else:
            pdf_path = PROJECT_ROOT / "data" / "pdfs" / (doi.replace("/", "_") + ".pdf")
        work.append(V4ExtractionRecord(
            doi=doi,
            pdf_path=str(pdf_path),
        ))
    elif args.batch:
        batch_path = Path(args.batch)
        if not batch_path.exists():
            logger.error(f"Batch file not found: {batch_path}")
            sys.exit(1)

        with open(batch_path) as f:
            for line in f:
                doi = line.strip()
                if doi and not doi.startswith("#"):
                    # Try mapping first
                    pdf_path_str = pdf_mapping.get(doi, {}).get("pdf_path") if isinstance(pdf_mapping.get(doi), dict) else pdf_mapping.get(doi)
                    if pdf_path_str:
                        pdf_path = Path(pdf_path_str)
                    else:
                        pdf_path = PROJECT_ROOT / "data" / "pdfs" / (doi.replace("/", "_") + ".pdf")
                    work.append(V4ExtractionRecord(
                        doi=doi,
                        pdf_path=str(pdf_path),
                    ))

    work = work[:args.limit]

    if not work:
        logger.error("No papers to process")
        release_lock()
        sys.exit(1)

    # ── Setup ──
    concurrency = 1 if args.sequential else min(args.parallel, MAX_CONCURRENCY)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stages = [args.stage] if args.stage != "all" else ["1", "2", "3", "4"]

    # Setup file logging (full transcript saved to disk)
    log_path = _setup_file_logging(output_dir)

    # Initialize infrastructure
    telemetry = ExtractionTelemetry(output_dir) if not args.no_telemetry else None
    checkpoint = CheckpointManager(output_dir / "checkpoints")
    dlq = DeadLetterQueue(output_dir)
    budget = BudgetTracker(budget_limit=getattr(args, 'budget', 200.0))
    shutdown = GracefulShutdown()
    shutdown.register()

    # ── Resume from checkpoint: skip already-completed DOIs ──
    completed_dois = checkpoint.get_completed_dois()
    if completed_dois:
        before = len(work)
        work = [r for r in work if r.doi not in completed_dois]
        skipped = before - len(work)
        if skipped > 0:
            logger.info(f"  Resuming: skipped {skipped} already-completed papers")
            if telemetry:
                telemetry.log_event("resume", f"Skipped {skipped} already-completed papers from checkpoint")

    logger.info(f"\nProcessing {len(work)} papers")
    logger.info(f"  Model: {args.model}")
    logger.info(f"  Stages: {args.stage}")
    logger.info(f"  Verify fraction: {args.verify_fraction:.0%}")
    logger.info(f"  Concurrency: {concurrency}")
    logger.info(f"  Budget: ${budget.budget_limit:.2f}")
    if args.dry_run:
        logger.info("  MODE: DRY RUN (no API calls)")

    # Initialize Gemini client
    client = None
    if not args.dry_run:
        try:
            client = get_gemini_client()
            logger.info("  Gemini client initialized")
        except RuntimeError as e:
            logger.error(f"Client initialization failed: {e}")
            release_lock()
            sys.exit(1)

    # ── Process papers (sequential with all infrastructure wired in) ──
    # Note: parallel mode available but sequential is default for the pilot
    # because it gives cleaner telemetry and easier debugging.
    results = []
    n_processed = 0
    n_failed = 0

    for i, record in enumerate(work):
        # ── Graceful shutdown check ──
        if shutdown.should_stop:
            logger.warning(f"  Graceful shutdown: stopping after {i} papers")
            if telemetry:
                telemetry.log_event("shutdown", f"Graceful shutdown after {i} papers")
            break

        # ── Budget check ──
        if budget.check_budget():
            logger.error(f"  BUDGET EXCEEDED: ${budget.spent:.4f} >= ${budget.budget_limit:.2f}")
            logger.error(f"  Stopping. {len(work) - i} papers remaining.")
            if telemetry:
                telemetry.log_event("budget_exceeded", budget.budget_report())
            dlq.add(record.doi, "Budget exceeded before processing", "budget_exceeded")
            break

        # ── WAL: mark paper as starting ──
        checkpoint.write_wal(record.doi, "starting", "in_progress")

        try:
            record = process_paper(
                client,
                record,
                stages=stages,
                verify_fraction=args.verify_fraction,
                dry_run=args.dry_run,
                model=args.model,
                telemetry=telemetry,
            )
            results.append(record)

            if record.status == ExtractionStatus.COMPLETED:
                checkpoint.write_wal(record.doi, "completed", "success", {
                    "n_findings": record.extraction.n_findings if record.extraction else 0,
                    "cost": record.total_cost_usd,
                })
                budget.add_cost(record.total_cost_usd, record.doi)
                n_processed += 1
            elif record.status == ExtractionStatus.FAILED:
                checkpoint.write_wal(record.doi, "failed", "error", {
                    "error": record.error_message,
                })
                dlq.add(record.doi, record.error_message or "Unknown error", "extraction_failed")
                n_failed += 1
            else:
                # Partial completion (e.g., classified but not extracted)
                checkpoint.write_wal(record.doi, "completed", record.status.value)
                budget.add_cost(record.total_cost_usd, record.doi)
                n_processed += 1

            # Progress display
            pct = (i + 1) / len(work) * 100
            logger.info(
                f"  [{i+1}/{len(work)}] ({pct:.0f}%) "
                f"{record.status.value} | "
                f"${record.total_cost_usd:.4f} | "
                f"{budget.budget_report()}"
            )

            # Incremental save every 5 papers
            if (i + 1) % 5 == 0:
                save_batch(results, output_dir, i + 1)
                checkpoint.save_state(n_processed, n_failed, budget.spent)

        except Exception as e:
            logger.error(f"  Unhandled error processing {record.doi}: {e}")
            record.error_message = str(e)
            record.status = ExtractionStatus.FAILED
            results.append(record)
            checkpoint.write_wal(record.doi, "failed", "unhandled_exception", {"error": str(e)})
            dlq.add(record.doi, str(e), "unhandled_exception")
            n_failed += 1

    # ── Restore signal handlers ──
    shutdown.restore()

    # ── Final summary and save ──
    logger.info(f"\n{'='*60}")
    logger.info("EXTRACTION SUMMARY")
    logger.info(f"{'='*60}")
    n_completed = sum(1 for r in results if r.status == ExtractionStatus.COMPLETED)
    n_failed_final = sum(1 for r in results if r.status == ExtractionStatus.FAILED)
    total_findings = sum(r.extraction.n_findings for r in results if r.extraction)

    logger.info(f"  Papers: {len(results)} total, {n_completed} completed, {n_failed_final} failed")
    logger.info(f"  Findings: {total_findings} total")
    logger.info(f"  {budget.budget_report()}")
    if n_completed > 0:
        logger.info(f"  Avg cost/paper: ${budget.spent / n_completed:.4f}")
        logger.info(f"  Avg findings/paper: {total_findings / n_completed:.1f}")

    # Dead letter summary
    dlq_summary = dlq.summary()
    if dlq.count > 0:
        logger.info(f"  {dlq_summary}")
        logger.info(f"  Review: {dlq.dlq_file}")

    # Aggregate field coverage across all papers
    all_coverage: dict[str, list[float]] = {}
    for r in results:
        if r.extraction:
            for fname, val in r.extraction.field_coverage.items():
                all_coverage.setdefault(fname, []).append(val)

    if all_coverage:
        logger.info(f"\n  FIELD COVERAGE (across {n_completed} papers):")
        for fname in sorted(all_coverage, key=lambda k: sum(all_coverage[k])/len(all_coverage[k]), reverse=True):
            vals = all_coverage[fname]
            mean = sum(vals) / len(vals)
            bar = "█" * int(mean * 20) + "░" * (20 - int(mean * 20))
            logger.info(f"    {fname:25s} {mean:5.0%}  {bar}")

    # Save final results
    save_batch(results, output_dir, len(results), final=True)

    # Save checkpoint and telemetry
    checkpoint.save_state(n_completed, n_failed_final, budget.spent)
    if telemetry:
        telemetry.save_telemetry()

    # ── PROGRESS DASHBOARD: Key metrics David wants to see ──────────
    logger.info(f"\n{'='*60}")
    logger.info("PROGRESS DASHBOARD")
    logger.info(f"{'='*60}")

    # 1. PDFs found vs not found
    n_pdfs_found = sum(1 for r in results if r.pdf_path and Path(r.pdf_path).exists())
    n_pdfs_missing = len(results) - n_pdfs_found
    logger.info(f"\n  PDFs:")
    logger.info(f"    Found:   {n_pdfs_found}/{len(results)} ({n_pdfs_found/max(len(results),1)*100:.0f}%)")
    if n_pdfs_missing > 0:
        logger.info(f"    Missing: {n_pdfs_missing} (need acquisition)")

    # 2. Papers processed
    logger.info(f"\n  Processing:")
    logger.info(f"    Processed: {n_completed}/{len(results)}")
    logger.info(f"    Failed:    {n_failed_final}")
    if n_completed > 0:
        logger.info(f"    Avg cost:  ${budget.spent / n_completed:.4f}/paper")

    # 3. Field coverage percentages
    if all_coverage:
        total_fields = len(all_coverage)
        fields_above_50 = sum(1 for vals in all_coverage.values() if sum(vals)/len(vals) > 0.50)
        fields_above_80 = sum(1 for vals in all_coverage.values() if sum(vals)/len(vals) > 0.80)
        logger.info(f"\n  Field Coverage ({total_fields} fields):")
        logger.info(f"    >80% populated: {fields_above_80}/{total_fields} ({fields_above_80/max(total_fields,1)*100:.0f}%)")
        logger.info(f"    >50% populated: {fields_above_50}/{total_fields} ({fields_above_50/max(total_fields,1)*100:.0f}%)")

        # Show bottom 5 fields (the gaps David cares about)
        sorted_fields = sorted(all_coverage.items(), key=lambda kv: sum(kv[1])/len(kv[1]))
        if sorted_fields:
            logger.info(f"    Lowest coverage fields:")
            for fname, vals in sorted_fields[:5]:
                mean = sum(vals) / len(vals)
                logger.info(f"      {fname:30s} {mean:5.0%}")

    # 4. Plausibility check on completed results
    n_plausible_es = 0
    n_total_es = 0
    n_stim_descriptions = 0
    n_stim_images = 0
    n_total_findings = 0

    for r in results:
        if r.extraction and r.extraction.data:
            findings = r.extraction.data.get("findings", [])
            n_total_findings += len(findings)
            for finding in findings:
                # Effect size plausibility
                es = finding.get("effect_size")
                if es is not None:
                    n_total_es += 1
                    es_val = _safe_float_for_dashboard(es)
                    if es_val is not None and abs(es_val) < 5.0:
                        n_plausible_es += 1

                # Stimulus descriptions
                stim = finding.get("stimulus_description", "")
                if stim and len(str(stim).strip()) > 10:
                    n_stim_descriptions += 1

                # Stimulus images
                stim_img = finding.get("stimulus_image", "")
                if stim_img and len(str(stim_img).strip()) > 5:
                    n_stim_images += 1

    if n_total_findings > 0:
        logger.info(f"\n  Content Quality ({n_total_findings} findings):")
        if n_total_es > 0:
            logger.info(f"    Effect sizes present:    {n_total_es}/{n_total_findings} ({n_total_es/n_total_findings*100:.0f}%)")
            logger.info(f"    Effect sizes plausible:  {n_plausible_es}/{n_total_es} ({n_plausible_es/max(n_total_es,1)*100:.0f}%)")
        logger.info(f"    Stimulus descriptions:   {n_stim_descriptions}/{n_total_findings} ({n_stim_descriptions/n_total_findings*100:.0f}%)")
        logger.info(f"    Stimulus images:         {n_stim_images}/{n_total_findings} ({n_stim_images/n_total_findings*100:.0f}%)")

    # 5. Cross-article consistency (if enough results)
    if n_completed >= 3:
        try:
            sys.path.insert(0, str(PROJECT_ROOT))
            from src.qa.cross_article_consistency_validator import (
                CrossArticleValidator,
                FindingRecord as CARFindingRecord,
            )
            clusters: dict[str, list] = {}
            for r in results:
                if r.extraction and r.extraction.data:
                    for idx, finding in enumerate(r.extraction.data.get("findings", [])):
                        rec = CARFindingRecord.from_extraction(r.doi, finding, idx)
                        if rec.cluster_label is None:
                            ant = str(finding.get("antecedent", "")).lower().strip()
                            con = str(finding.get("consequent", "")).lower().strip()
                            if ant and con:
                                label = f"{ant}→{con}"
                                rec.cluster_label = label
                                clusters.setdefault(label, []).append(rec)
                        else:
                            clusters.setdefault(rec.cluster_label, []).append(rec)

            if clusters:
                validator = CrossArticleValidator()
                batch_report = validator.validate_batch(clusters, run_design_checks=True)

                n_cross_flags = sum(c.n_flags for c in batch_report.clusters)
                n_design_flags = len(batch_report.design_flags)
                logger.info(f"\n  Consistency Checks:")
                logger.info(f"    Clusters analyzed:       {len(batch_report.clusters)}")
                logger.info(f"    Cross-article flags:     {n_cross_flags}")
                logger.info(f"    Design plausibility flags: {n_design_flags}")

                # Show most flagged clusters
                flagged = sorted(
                    [c for c in batch_report.clusters if c.n_flags > 0],
                    key=lambda c: c.n_critical, reverse=True
                )
                if flagged:
                    logger.info(f"    Flagged clusters (top 5):")
                    for c in flagged[:5]:
                        logger.info(f"      {c.cluster_label}: {c.n_critical}C/{c.n_warnings}W")

                # Save cross-article report
                car_path = output_dir / "cross_article_consistency.json"
                batch_report.save(car_path)
                logger.info(f"    Full report: {car_path}")

        except Exception as e:
            logger.warning(f"  Cross-article check skipped: {e}")

    logger.info(f"\n{'='*60}")
    logger.info(f"\nResults saved to: {output_dir}")
    logger.info(f"Checkpoint: {checkpoint.checkpoint_dir}")
    if dlq.count > 0:
        logger.info(f"Dead letters: {dlq.dlq_file}")

    # Release lock
    release_lock()


def save_batch(results: list[V4ExtractionRecord], output_dir: Path, count: int, final: bool = False) -> None:
    """Save batch of results to JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"v4_extraction_final_{timestamp}.json" if final else f"v4_extraction_batch_{count}_{timestamp}.json"
    filepath = output_dir / filename

    # Convert dataclass to dict
    records_data = []
    for r in results:
        d = {
            "doi": r.doi,
            "pdf_path": r.pdf_path,
            "status": r.status.value,
            "created_at": r.created_at,
            "updated_at": r.updated_at,
            "total_cost_usd": round(r.total_cost_usd, 4),
            "error_message": r.error_message,
        }

        if r.classification:
            d["classification"] = {
                "article_type": r.classification.article_type,
                "family_group": r.classification.family_group,
                "confidence": round(r.classification.confidence, 2),
                "signals": r.classification.signals,
            }

        if r.extraction:
            d["extraction"] = {
                "n_findings": r.extraction.n_findings,
                "field_coverage": {k: round(v, 2) for k, v in r.extraction.field_coverage.items()},
                "data": r.extraction.data,
            }

        if r.verification:
            d["verification"] = {
                "score": round(r.verification.score, 2),
                "n_issues": len(r.verification.flagged_issues),
                "summary": r.verification.summary,
            }

        records_data.append(d)

    with open(filepath, "w") as f:
        json.dump({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_papers": len(results),
            "results": records_data,
        }, f, indent=2)

    logger.info(f"Saved: {filepath}")


def _safe_float_for_dashboard(val) -> float | None:
    """Parse a numeric value for the dashboard display."""
    import math as _math
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val) if _math.isfinite(float(val)) else None
    if isinstance(val, str):
        try:
            cleaned = val.strip()
            if cleaned.startswith("inferred:"):
                cleaned = cleaned.split(":", 1)[1].strip()
            result = float(cleaned)
            return result if _math.isfinite(result) else None
        except (ValueError, OverflowError):
            return None
    return None


if __name__ == "__main__":
    main()
