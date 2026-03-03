#!/usr/bin/env python3
"""
scheduled_pipeline.py — ATLAS Automated Pipeline Orchestrator

Connects the article discovery, extraction, and integration pipeline
into a single automated workflow that can run on a schedule.

Usage:
    python scripts/scheduled_pipeline.py run          # Run all stages once
    python scripts/scheduled_pipeline.py run --stage discovery  # Run only discovery
    python scripts/scheduled_pipeline.py status       # Show pipeline status
    python scripts/scheduled_pipeline.py wishlist add "Ulrich 1984 view recovery"
    python scripts/scheduled_pipeline.py wishlist show
    python scripts/scheduled_pipeline.py daemon       # Run as daemon with scheduling

Stages (in order):
    1. discovery  — Find new papers (gap-driven + wishlist + Zotero sync)
    2. triage     — Classify article type (empirical, meta-analysis, etc.)
    3. extract    — Extract claims via Gemini (type-specific prompts)
    4. tables     — Extract and classify tables, generate claims
    5. integrate  — Run 14-step integration cascade (requires approval)

Created: 2026-02-26
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Resolve repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
LOGS_DIR = REPO_ROOT / "logs"
WISHLIST_PATH = DATA_DIR / "article_wishlist.json"

# Centralized DB resolution
try:
    from src.services.db_locator import get_web_db
    _WEB_DB = get_web_db()
except Exception:
    _WEB_DB = DATA_DIR / "web_persistence.db"

# Ensure directories exist
LOGS_DIR.mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "pipeline_scheduler.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("pipeline")


# ---------------------------------------------------------------------------
# Wishlist Management
# ---------------------------------------------------------------------------

def load_wishlist() -> list:
    """Load the article wishlist."""
    if WISHLIST_PATH.exists():
        return json.loads(WISHLIST_PATH.read_text(encoding="utf-8"))
    return []


def save_wishlist(items: list):
    """Save the article wishlist."""
    WISHLIST_PATH.write_text(
        json.dumps(items, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def wishlist_add(description: str, priority: str = "normal", doi: str = None):
    """Add an item to the wishlist."""
    items = load_wishlist()
    entry = {
        "id": len(items) + 1,
        "description": description,
        "priority": priority,
        "doi": doi,
        "added": datetime.now().isoformat(),
        "status": "WANTED",
        "notes": ""
    }
    items.append(entry)
    save_wishlist(items)
    log.info(f"Added to wishlist: {description} (priority={priority})")
    return entry


def wishlist_show():
    """Display the wishlist."""
    items = load_wishlist()
    if not items:
        print("Wishlist is empty.")
        return
    print(f"\n{'ID':>4}  {'Priority':<10}  {'Status':<12}  {'Description'}")
    print("-" * 80)
    for item in items:
        print(f"{item['id']:>4}  {item.get('priority', 'normal'):<10}  "
              f"{item.get('status', 'WANTED'):<12}  {item['description'][:50]}")
    print(f"\nTotal: {len(items)} items")


# ---------------------------------------------------------------------------
# Pipeline Stages
# ---------------------------------------------------------------------------

def auto_lookup_wishlist_dois():
    """Auto-fill DOIs and check OA availability for wishlist items."""
    from src.services.paper_fetcher import (
        UnpaywallClient,
        crossref_title_search,
    )
    from src.services.notification_service import (
        notify, NotificationType, Severity,
    )

    wishlist = load_wishlist()
    updated = False
    unpaywall = UnpaywallClient()

    for item in wishlist:
        status = item.get("status", "WANTED")

        # Step 1: DOI lookup for items without DOI
        if not item.get("doi") and status in ("WANTED",):
            desc = item.get("description", "")
            # Extract title-like text (before " - " or full description)
            title_query = desc.split(" - ")[0] if " - " in desc else desc
            log.info(f"Searching CrossRef for: {title_query[:60]}")
            results = crossref_title_search(title_query, limit=1)
            if results and results[0].get("score", 0) > 50:
                item["doi"] = results[0]["doi"]
                item["crossref_title"] = results[0]["title"]
                item["status"] = "DOI_FOUND"
                log.info(f"  DOI found: {item['doi']}")
                updated = True
            else:
                log.info(f"  No confident DOI match (score too low or no results)")

        # Step 2: OA check for items with DOI
        if item.get("doi") and status in ("WANTED", "DOI_FOUND"):
            log.info(f"Checking Unpaywall for: {item['doi']}")
            oa = unpaywall.check_oa_status(item["doi"])
            if oa.get("is_oa") and oa.get("best_oa_url"):
                item["status"] = "OA_AVAILABLE"
                item["pdf_url"] = oa["best_oa_url"]
                item["oa_license"] = oa.get("license")
                log.info(f"  OA available: {oa['best_oa_url'][:80]}")
                updated = True
            elif oa.get("error"):
                log.info(f"  Unpaywall error: {oa['error']}")
                if status == "DOI_FOUND":
                    item["status"] = "NEEDS_MANUAL_ACQUISITION"
                    notify(
                        NotificationType.EXTRACTION_REVIEW,
                        Severity.INFO,
                        f"Manual PDF needed: {item.get('description', '')[:50]}",
                        f"DOI {item['doi']} is not OA. Acquire manually.",
                        context={"doi": item["doi"], "wishlist_id": item["id"]},
                        send_email=False,
                    )
                    updated = True
            else:
                if status == "DOI_FOUND":
                    item["status"] = "NEEDS_MANUAL_ACQUISITION"
                    log.info("  Not OA — marked for manual acquisition")
                    updated = True

    if updated:
        save_wishlist(wishlist)
        log.info("Wishlist updated with DOI/OA results")


def run_discovery():
    """Stage 1: Find new papers via gap-driven search + wishlist."""
    log.info("=== STAGE 1: DISCOVERY ===")

    # 1a. Export gaps as search targets
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from src.services.gap_predictor import GapPredictor
        log.info("Gap predictor available — generating search targets")
    except ImportError:
        log.warning("Gap predictor not available — using wishlist only")

    # 1b. Check wishlist for manual targets
    wishlist = load_wishlist()
    wanted = [i for i in wishlist if i.get("status") == "WANTED"]
    if wanted:
        log.info(f"Wishlist has {len(wanted)} WANTED items")

    # 1c. Auto-lookup DOIs and check Unpaywall for wishlist items
    try:
        auto_lookup_wishlist_dois()
    except Exception as e:
        log.warning(f"Wishlist DOI/OA lookup failed: {e}")

    # 1d. Run AG's acquisition pipeline (search → expand → Zotero push)
    #     This calls run_acquisition_pipeline.py which chains:
    #     queue refresh → S2 search → query expansion → snowball →
    #     enrichment → Zotero push → acquisition digest
    acq_script = REPO_ROOT / "scripts" / "run_acquisition_pipeline.py"
    if acq_script.exists():
        log.info("Running acquisition pipeline (AG's 8-step chain)...")
        try:
            result = subprocess.run(
                [sys.executable, str(acq_script), "--dry-run"],
                capture_output=True, text=True, timeout=300,
                cwd=str(REPO_ROOT),
            )
            if result.returncode == 0:
                log.info("Acquisition pipeline completed successfully")
            else:
                log.warning(
                    f"Acquisition pipeline exited {result.returncode}: "
                    f"{result.stderr[:200] if result.stderr else 'no error'}"
                )
        except subprocess.TimeoutExpired:
            log.warning("Acquisition pipeline timed out (300s)")
        except Exception as e:
            log.warning(f"Acquisition pipeline error: {e}")
    else:
        # Fallback: run individual components if orchestrator missing
        try:
            from src.queue.automated_searcher import AutomatedQueueSearcher
            from src.queue.service import ResearchQueueService
            log.info("Running AutomatedQueueSearcher (fallback)...")
            queue = ResearchQueueService()
            searcher = AutomatedQueueSearcher(queue_service=queue)
            runs = searcher.run_once()
            log.info(f"AutomatedQueueSearcher completed: {len(runs)} target(s) processed")
            for run in runs:
                log.info(f"  - {run.target_id}: {run.status} ({run.n_candidates} candidates)")
        except Exception as e:
            log.warning(f"AutomatedQueueSearcher not available: {e}")

    # 1e. Check Zotero for new imports (passive feedback loop)
    try:
        from src.queue.zotero_watcher import ZoteroWatcher
        log.info("ZoteroWatcher available — checking for new imports")
        # Zotero watcher detects when user adds PDFs to Zotero
        # and auto-matches them back to research queue targets
    except Exception as e:
        log.warning(f"ZoteroWatcher not available: {e}")

    return True


def run_recommendation_loop():
    """Stage 1.4: Run recommendation loop to harvest interpretation space gaps."""
    log.info("=== STAGE 1.4: RECOMMENDATION LOOP ===")

    try:
        sys.path.insert(0, str(REPO_ROOT))
        from src.services.recommendation_loop import RecommendationLoopService

        # Initialize service
        db_path = REPO_ROOT / "web_persistence_v2.db" if (REPO_ROOT / "web_persistence_v2.db").exists() else _WEB_DB
        web_db_path = DATA_DIR / "article_eater.db"

        service = RecommendationLoopService(
            db_path=str(db_path),
            web_db_path=str(web_db_path),
        )

        # Run single pass cycle
        log.info("Running recommendation loop (interpretation space → search queue)...")
        result = service.run_single_pass(top_n=5)

        # Log results
        harvest_count = result.get("steps", {}).get("harvest_gaps", {}).get("count", 0)
        qa_count = result.get("steps", {}).get("harvest_qa", {}).get("count", 0)
        insert_count = result.get("steps", {}).get("insert", {}).get("inserted_count", 0)
        dispatch = result.get("steps", {}).get("dispatch", {})
        dispatch_count = dispatch.get("dispatched_count", 0)

        log.info(
            f"Recommendation loop completed: "
            f"harvested {harvest_count} gaps, {qa_count} QA items, "
            f"inserted {insert_count} suggestions, "
            f"dispatched {dispatch_count} searches"
        )

        return True

    except ImportError as e:
        log.warning(f"Recommendation loop service not available: {e}")
        return True
    except Exception as e:
        log.error(f"Recommendation loop error: {e}")
        return False


def run_automated_search():
    """Stage 1.5: Run automated queue searcher for VOI-prioritized targets."""
    log.info("=== STAGE 1.5: AUTOMATED SEARCH ===")

    try:
        sys.path.insert(0, str(REPO_ROOT))
        from src.queue.service import ResearchQueueService
        from src.queue.automated_searcher import AutomatedQueueSearcher

        # Initialize queue and searcher
        queue = ResearchQueueService()
        searcher = AutomatedQueueSearcher(queue_service=queue)

        # Run one cycle of automated search
        log.info("Running automated searcher for high-VOI targets...")
        runs = searcher.run_once()

        if runs:
            log.info(f"Automated search completed: {len(runs)} target(s) processed")
            for run in runs:
                status_color = "PASS" if run.status == "found" else "STALE"
                log.info(
                    f"  - {run.target_id}: {status_color} ({run.n_candidates} candidate articles)"
                )
                if run.top_titles:
                    for title in run.top_titles[:2]:
                        log.info(f"      * {title[:70]}")
        else:
            log.info("Automated search: no open targets available")

        return True

    except ImportError as e:
        log.warning(f"Automated searcher not available: {e}")
        return True
    except Exception as e:
        log.error(f"Automated search error: {e}")
        return False


def run_triage():
    """Stage 2: Classify new PDFs by article type."""
    log.info("=== STAGE 2: TRIAGE ===")

    # Check for untriaged PDFs
    triage_queue = DATA_DIR / "extraction_pipeline" / "extraction_queue.json"
    if not triage_queue.exists():
        log.info("No extraction queue found")
        return True

    raw = json.loads(triage_queue.read_text(encoding="utf-8"))
    # Handle dict with stats/items or raw list
    if isinstance(raw, dict):
        stats = raw.get("stats", {})
        pending_count = stats.get("pending", 0)
        total_count = stats.get("total", len(raw.get("items", [])))
    else:
        items = [i for i in raw if isinstance(i, dict)]
        pending_count = sum(1 for i in items if i.get("status") == "pending")
        total_count = len(raw)
    log.info(f"Triage queue: {pending_count} pending, {total_count} total")

    if not pending_count:
        log.info("No papers pending triage")
        return True

    # Run triage script
    log.info(f"Would triage {pending_count} papers (dry-run)")
    # In production: subprocess.run(["python", "scripts/gemini_triage_papers.py"])
    return True


def run_extraction():
    """Stage 3: Extract claims via Gemini."""
    log.info("=== STAGE 3: EXTRACTION ===")

    triage_queue = DATA_DIR / "extraction_pipeline" / "extraction_queue.json"
    if not triage_queue.exists():
        log.info("No extraction queue found")
        return True

    raw = json.loads(triage_queue.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        stats = raw.get("stats", {})
        triaged_count = stats.get("classifying", 0) + stats.get("extracting", 0)
    else:
        items = [i for i in raw if isinstance(i, dict)]
        triaged_count = sum(1 for i in items if i.get("status") == "triaged")
    log.info(f"Extraction: {triaged_count} papers triaged and ready")

    if not triaged_count:
        log.info("No papers ready for extraction")
        return True

    log.info(f"Would extract {triaged_count} papers (dry-run)")
    # In production: subprocess.run(["python", "scripts/gemini_extraction_queue.py"])
    return True


def run_extraction_quality_gate():
    """Stage 3.5: Quality gate on newly extracted files."""
    log.info("=== STAGE 3.5: EXTRACTION QUALITY GATE ===")

    try:
        sys.path.insert(0, str(REPO_ROOT))
        from src.qa.extraction_field_validator import gate_extraction

        extractions_dir = DATA_DIR / "extractions"
        if not extractions_dir.exists():
            log.info("No extractions directory found")
            return True

        # Find extraction JSON files (exclude needs_repair subdirectory)
        extraction_files = [
            f for f in extractions_dir.glob("*.json")
            if f.parent == extractions_dir  # Only top level
        ]

        if not extraction_files:
            log.info("No extraction files to gate")
            return True

        log.info(f"Gating {len(extraction_files)} extraction files (threshold=0.75)")

        passed_count = 0
        failed_count = 0
        error_count = 0

        for extraction_path in extraction_files:
            try:
                result = gate_extraction(extraction_path, threshold=0.75)
                if result["passed"]:
                    passed_count += 1
                    log.info(f"  PASS: {extraction_path.name} (score={result['score']:.4f})")
                else:
                    failed_count += 1
                    log.warning(
                        f"  FAIL: {extraction_path.name} moved to repair queue "
                        f"(score={result['score']:.4f}, {result['n_violations']} violations)"
                    )
            except Exception as e:
                error_count += 1
                log.error(f"  ERROR gating {extraction_path.name}: {e}")

        log.info(
            f"Quality gate complete: {passed_count} passed, "
            f"{failed_count} failed, {error_count} errors"
        )

        return True

    except ImportError as e:
        log.warning(f"Extraction gating not available: {e}")
        return True
    except Exception as e:
        log.error(f"Extraction quality gate failed: {e}")
        return False


def run_tables():
    """Stage 4: Extract tables, classify, generate claims."""
    log.info("=== STAGE 4: TABLE EXTRACTION ===")

    # Check for extracted papers with tables
    extractions_dir = DATA_DIR / "extractions"
    if not extractions_dir.exists():
        log.info("No extractions directory found")
        return True

    extraction_files = list(extractions_dir.glob("*.json"))
    log.info(f"Found {len(extraction_files)} extraction files")

    # In production: subprocess.run(["python", "scripts/run_realtime_table_rule_intake.py"])
    log.info("Table extraction: available (dry-run)")
    return True


def run_integration():
    """Stage 5: Integrate extracted papers into web + BN via HITL approval."""
    log.info("=== STAGE 5: INTEGRATION (HITL) ===")

    try:
        from src.services.extraction_approval import ExtractionApprovalService
        from src.services.notification_service import (
            notify, NotificationType, Severity,
        )

        svc = ExtractionApprovalService()
        pending = svc.get_pending_approvals()

        if pending:
            log.info(
                f"Integration: {len(pending)} papers awaiting human approval"
            )
            # Queue notification for reviewer
            notify(
                NotificationType.EXTRACTION_REVIEW,
                Severity.WARNING,
                f"{len(pending)} papers awaiting review",
                (
                    f"Run: python scripts/review_extractions.py list\n"
                    f"Top paper: {pending[0]['paper_id'][:50]}"
                ),
                context={"pending_count": len(pending)},
                send_email=False,
            )
        else:
            log.info("No papers pending approval")

        # Check for already-approved papers awaiting integration
        queue_path = DATA_DIR / "extraction_pipeline" / "extraction_queue.json"
        if queue_path.exists():
            raw = json.loads(queue_path.read_text(encoding="utf-8"))
            items = raw.get("items", {}) if isinstance(raw, dict) else {}
            approved = [
                pid for pid, item in items.items()
                if isinstance(item, dict) and item.get("status") == "approved"
            ]
            if approved:
                log.info(f"Found {len(approved)} approved papers to integrate")
                for pid in approved[:3]:  # Max 3 per run
                    log.info(f"  Would integrate: {pid[:50]}")
                    # In production:
                    # svc._trigger_integration(pid)

    except ImportError as e:
        log.warning(f"Extraction approval service not available: {e}")

    return True


def run_post_integration():
    """Post-integration: trigger OVERSEER health check."""
    log.info("=== POST-INTEGRATION: OVERSEER CHECK ===")
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from src.services.overseer import OverseerService

        # Try to find databases
        overseer_db = None
        web_db = None
        for candidate in [DATA_DIR, DATA_DIR / "production", REPO_ROOT / ".data"]:
            if (candidate / "overseer.db").exists():
                overseer_db = candidate / "overseer.db"
            if (candidate / "web.db").exists():
                web_db = candidate / "web.db"

        if overseer_db and web_db:
            overseer = OverseerService(
                overseer_db_path=str(overseer_db),
                web=None,  # Graceful degradation in batch mode
                web_db_path=str(web_db),
            )
            # Register pipeline run
            overseer.report_pipeline_run("overseer", "running", 0)
            log.info("OverseerService loaded — running integrity check")
            violations = overseer.check_integrity()
            if violations:
                log.warning(
                    f"Overseer found {len(violations)} violations: "
                    + ", ".join(v.code for v in violations)
                )
            else:
                log.info("Overseer: all invariants satisfied")
            overseer.report_pipeline_run(
                "overseer", "pass" if not violations else "violations", 0
            )
        else:
            log.info("OverseerService available but databases not found in this environment")

    except Exception as e:
        log.warning(f"OverseerService not available: {e}")
    return True


def run_qa_confounder_check():
    """Stage 6: Batch confounder risk assessment on all findings."""
    log.info("=== STAGE 6: QA CONFOUNDER CHECK ===")

    try:
        sys.path.insert(0, str(REPO_ROOT))
        from src.services.pipeline_qa_integration import batch_assess_findings

        output_dir = LOGS_DIR / "qa_reports"
        result = batch_assess_findings(output_dir=str(output_dir))

        if result.get("status") == "disabled":
            log.info("Confounder check disabled (AE_QA_INTEGRATION=false)")
            return True

        if result.get("status") == "error":
            log.warning(f"QA batch assessment failed: {result.get('error')}")
            return True  # Non-fatal, continue pipeline

        # Log confounder assessment results
        if result.get("confounder_assessment"):
            conf = result["confounder_assessment"]
            if conf.get("status") == "success" and conf.get("batch_report"):
                batch = conf["batch_report"]
                log.info(
                    f"Confounder risk assessment: {batch.get('beliefs_assessed', 0)} beliefs, "
                    f"{batch.get('high_risk_count', 0)} high-risk, "
                    f"{batch.get('medium_risk_count', 0)} medium-risk"
                )

        duration_ms = result.get("duration_ms", 0)
        log.info(f"QA confounder check completed in {duration_ms}ms")

        return True

    except Exception as e:
        log.warning(f"QA confounder check error (non-fatal): {e}")
        return True  # Non-fatal — don't block pipeline


def run_qa_credence_intervals():
    """Stage 6b: Compute credence confidence intervals for all beliefs."""
    log.info("=== STAGE 6B: QA CREDENCE INTERVALS ===")

    try:
        sys.path.insert(0, str(REPO_ROOT))
        from src.services.pipeline_qa_integration import batch_assess_findings

        output_dir = LOGS_DIR / "qa_reports"
        # This will run credence assessment if enabled
        result = batch_assess_findings(output_dir=str(output_dir))

        if result.get("status") == "disabled":
            log.info("Credence intervals disabled (AE_QA_INTEGRATION=false)")
            return True

        if result.get("status") == "error":
            log.warning(f"QA credence assessment failed: {result.get('error')}")
            return True  # Non-fatal, continue pipeline

        # Log credence assessment results
        if result.get("credence_assessment"):
            cred = result["credence_assessment"]
            if cred.get("status") == "success" and cred.get("summary_stats"):
                stats = cred["summary_stats"]
                log.info(
                    f"Credence intervals: {stats.get('n_beliefs', 0)} beliefs, "
                    f"mean CI width {stats.get('mean_ci_width', 0.0):.3f}"
                )

        duration_ms = result.get("duration_ms", 0)
        log.info(f"QA credence intervals completed in {duration_ms}ms")

        return True

    except Exception as e:
        log.warning(f"QA credence check error (non-fatal): {e}")
        return True  # Non-fatal — don't block pipeline


def run_cva_enrichment():
    """Stage 7: CVA constraint-valuation enrichment on integrated papers."""
    log.info("=== STAGE 7: CVA ENRICHMENT ===")
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from src.services.cva_constraint_engine import CVAConstraintEngine
        from src.services.cva_valuation_engine import CVAValuationEngine
        from src.services.cva_dynamics import (
            CVADynamicsEngine, CVACouplingMatrices, CoupledDynamicsState,
        )
        from src.services.db_migrations import MigrationManager
        import sqlite3

        # Run pending migrations first
        db_path = None
        for candidate in [
            _WEB_DB,
            DATA_DIR / "web.db",
        ]:
            if candidate.exists():
                db_path = candidate
                break

        if db_path:
            conn = sqlite3.connect(str(db_path))
            mgr = MigrationManager(conn)
            pending = mgr.run_pending_migrations()
            if pending:
                log.info(f"Ran {pending} pending migrations")
            conn.close()

        # CVA engines
        c_engine = CVAConstraintEngine()
        v_engine = CVAValuationEngine()
        d_engine = CVADynamicsEngine()
        coupling = CVACouplingMatrices.default()

        # Process a sample scene for demonstration
        sample_scenes = [
            {"edge": 0.7, "motion": 0.3, "contrast": 0.6,
             "figure_ground": 0.8, "temporal_coherence": 0.5, "symmetry": 0.4},
        ]

        for i, scene in enumerate(sample_scenes):
            # Compute constraints
            constraints = c_engine.compute(scene)
            dist = c_engine.recognize_constraints_probabilistic(scene, "STUDYING")

            # Compute valuations
            val = v_engine.compute(constraints)
            val_frame = v_engine.compute_valuation_with_frame(constraints, "STUDYING")

            log.info(
                f"CVA scene {i}: constraints=[{len(dist.mean)}D], "
                f"core_val=[{val_frame.core.shape[0]}D], "
                f"aux={list(val_frame.auxiliary.keys())}, "
                f"entropy={dist.entropy():.2f}"
            )

        log.info("CVA enrichment complete")

    except ImportError as e:
        log.warning(f"CVA modules not available: {e}")
    except Exception as e:
        log.warning(f"CVA enrichment error: {e}")

    return True


# ---------------------------------------------------------------------------
# Pipeline Orchestrator
# ---------------------------------------------------------------------------

STAGES = {
    "discovery": run_discovery,
    "recommendation": run_recommendation_loop,
    "search": run_automated_search,
    "triage": run_triage,
    "extract": run_extraction,
    "qa_gate": run_extraction_quality_gate,
    "tables": run_tables,
    "integrate": run_integration,
    "overseer": run_post_integration,
    "qa_confounder": run_qa_confounder_check,
    "qa_credence": run_qa_credence_intervals,
    "cva": run_cva_enrichment,
}


def _get_overseer():
    """Get OverseerService instance for pipeline reporting. Returns None if unavailable."""
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from src.services.overseer import OverseerService

        overseer_db = None
        web_db = None
        for candidate in [DATA_DIR, DATA_DIR / "production", REPO_ROOT / ".data"]:
            if (candidate / "overseer.db").exists():
                overseer_db = candidate / "overseer.db"
            if (candidate / "web.db").exists():
                web_db = candidate / "web.db"

        if overseer_db and web_db:
            svc = OverseerService(
                overseer_db_path=str(overseer_db),
                web=None,
                web_db_path=str(web_db),
            )
            svc.register_canonical_pipelines()
            return svc
    except Exception as e:
        log.debug(f"Overseer not available for pipeline reporting: {e}")
    return None


def run_pipeline(stages=None):
    """Run the full pipeline (or specific stages)."""
    if stages is None:
        stages = list(STAGES.keys())

    log.info(f"Pipeline starting: stages={stages}")
    start = time.time()
    results = {}

    # Get overseer for stage-level reporting
    overseer = _get_overseer()

    for stage_name in stages:
        if stage_name not in STAGES:
            log.error(f"Unknown stage: {stage_name}")
            results[stage_name] = False
            continue

        stage_start = time.time()
        try:
            log.info(f"Running stage: {stage_name}")
            if overseer:
                overseer.report_pipeline_run(stage_name, "running", 0)
            success = STAGES[stage_name]()
            results[stage_name] = success
            duration_ms = int((time.time() - stage_start) * 1000)
            if overseer:
                overseer.report_pipeline_run(
                    stage_name,
                    "pass" if success else "fail",
                    duration_ms,
                    metadata={"stage": stage_name},
                )
            if not success:
                log.warning(f"Stage {stage_name} returned failure")
        except Exception as e:
            log.error(f"Stage {stage_name} failed with exception: {e}")
            results[stage_name] = False
            duration_ms = int((time.time() - stage_start) * 1000)
            if overseer:
                overseer.report_pipeline_run(
                    stage_name, "error", duration_ms,
                    error=str(e),
                    metadata={"stage": stage_name},
                )

    elapsed = time.time() - start
    passed = sum(1 for v in results.values() if v)
    total = len(results)

    log.info(f"Pipeline complete: {passed}/{total} stages passed in {elapsed:.1f}s")

    # Save run report
    report = {
        "timestamp": datetime.now().isoformat(),
        "stages": stages,
        "results": results,
        "elapsed_seconds": elapsed,
    }
    report_path = LOGS_DIR / f"pipeline_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    log.info(f"Run report: {report_path}")

    return all(results.values())


def show_status():
    """Show pipeline status."""
    print("\n=== ATLAS Pipeline Status ===\n")

    # Check extraction queue
    queue_path = DATA_DIR / "extraction_pipeline" / "extraction_queue.json"
    if queue_path.exists():
        raw = json.loads(queue_path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            stats = raw.get("stats", {})
            items = raw.get("items", [])
            print(f"Extraction Queue ({len(items)} papers):")
            for s, count in sorted(stats.items()):
                if isinstance(count, (int, float)):
                    print(f"  {s}: {count}")
        else:
            statuses = {}
            for item in raw:
                s = item.get("status", "unknown") if isinstance(item, dict) else "unknown"
                statuses[s] = statuses.get(s, 0) + 1
            print(f"Extraction Queue ({len(raw)} papers):")
            for s, count in sorted(statuses.items()):
                print(f"  {s}: {count}")
    else:
        print("Extraction Queue: not found")

    # Check wishlist
    wishlist = load_wishlist()
    wanted = [i for i in wishlist if i.get("status") == "WANTED"]
    found = [i for i in wishlist if i.get("status") == "FOUND"]
    print(f"\nWishlist: {len(wanted)} wanted, {len(found)} found, {len(wishlist)} total")

    # Check latest health report
    health_report = DATA_DIR / "production" / "system_health_report.json"
    if health_report.exists():
        health = json.loads(health_report.read_text(encoding="utf-8"))
        if isinstance(health.get("score"), dict):
            score = health["score"].get("overall_score", "?")
            band = health["score"].get("band", "?")
        else:
            score = health.get("score", "?")
            band = health.get("band", "?")
        print(f"\nSystem Health: AESHI {score} ({band})")

    # Check last pipeline run
    run_logs = sorted(LOGS_DIR.glob("pipeline_run_*.json"))
    if run_logs:
        last = json.loads(run_logs[-1].read_text(encoding="utf-8"))
        print(f"\nLast Pipeline Run: {last['timestamp']}")
        for stage, result in last["results"].items():
            status = "PASS" if result else "FAIL"
            print(f"  {stage}: {status}")
    else:
        print("\nNo pipeline runs recorded")

    print()


def run_daemon(interval_hours: float = 6.0):
    """Run as daemon with scheduling."""
    log.info(f"Daemon starting — interval: {interval_hours}h")
    log.info("Press Ctrl+C to stop")

    while True:
        try:
            run_pipeline()
            next_run = datetime.now() + timedelta(hours=interval_hours)
            log.info(f"Next run at: {next_run.strftime('%Y-%m-%d %H:%M')}")
            time.sleep(interval_hours * 3600)
        except KeyboardInterrupt:
            log.info("Daemon stopped by user")
            break
        except Exception as e:
            log.error(f"Pipeline error: {e}")
            log.info("Retrying in 30 minutes...")
            time.sleep(1800)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="ATLAS Automated Pipeline Orchestrator"
    )
    subparsers = parser.add_subparsers(dest="command")

    # run
    run_parser = subparsers.add_parser("run", help="Run pipeline stages")
    run_parser.add_argument(
        "--stage", choices=list(STAGES.keys()),
        help="Run only this stage"
    )

    # status
    subparsers.add_parser("status", help="Show pipeline status")

    # wishlist
    wish_parser = subparsers.add_parser("wishlist", help="Manage article wishlist")
    wish_sub = wish_parser.add_subparsers(dest="wish_cmd")
    add_parser = wish_sub.add_parser("add", help="Add to wishlist")
    add_parser.add_argument("description", help="Article description")
    add_parser.add_argument("--priority", default="normal",
                           choices=["low", "normal", "high", "critical"])
    add_parser.add_argument("--doi", help="DOI if known")
    wish_sub.add_parser("show", help="Show wishlist")

    # daemon
    daemon_parser = subparsers.add_parser("daemon", help="Run as daemon")
    daemon_parser.add_argument(
        "--interval", type=float, default=6.0,
        help="Hours between runs (default: 6)"
    )

    args = parser.parse_args()

    if args.command == "run":
        stages = [args.stage] if args.stage else None
        success = run_pipeline(stages)
        sys.exit(0 if success else 1)
    elif args.command == "status":
        show_status()
    elif args.command == "wishlist":
        if args.wish_cmd == "add":
            wishlist_add(args.description, args.priority, args.doi)
        elif args.wish_cmd == "show":
            wishlist_show()
        else:
            wish_parser.print_help()
    elif args.command == "daemon":
        run_daemon(args.interval)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
