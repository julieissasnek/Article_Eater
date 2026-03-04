#!/usr/bin/env python3
"""
All-In-One Terminal Script for DB-Blocked Tasks
=================================================

David: Run this in your terminal to complete all tasks AG cannot do from sandbox.
Each task can be run independently via its function, or run them all with --all.

Usage:
    cd /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1

    # Run everything:
    python3 scripts/run_blocked_tasks.py --all

    # Run specific tasks:
    python3 scripts/run_blocked_tasks.py --task mt1      # AESHI re-score (MT-1)
    python3 scripts/run_blocked_tasks.py --task mt3      # FTR Tier2 coverage (MT-3)
    python3 scripts/run_blocked_tasks.py --task mt14     # Generate test cache for AESHI (MT-14)
    python3 scripts/run_blocked_tasks.py --task mt15     # Populate template_ids (MT-15)
    python3 scripts/run_blocked_tasks.py --task h12      # V3 re-extraction for 59 zero-finding articles (H12)
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _find_web_db():
    """Use the canonical db_locator to find the correct web database."""
    sys.path.insert(0, str(PROJECT_ROOT))
    try:
        from src.services.db_locator import get_web_db
        db_path = get_web_db()
        print(f"  db_locator resolved: {db_path}")
        return db_path
    except Exception as e:
        print(f"  ⚠ db_locator failed ({e}), falling back to manual search")

    # Manual fallback (same order as db_locator)
    db_candidates = [
        PROJECT_ROOT / "data" / "web_persistence_v2.db",
        PROJECT_ROOT / "data" / "web_persistence.db",
        PROJECT_ROOT / "ae.db",
        PROJECT_ROOT / "data" / "ae.db",
    ]
    for p in db_candidates:
        if p.exists():
            return p
    return None


def _count_beliefs(db_path):
    """Count beliefs, trying 'beliefs' table first then 'belief_versions' fallback."""
    with sqlite3.connect(str(db_path)) as conn:
        cur = conn.cursor()
        # Check what tables exist
        tables = {row[0] for row in cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}

        if 'beliefs' in tables:
            return cur.execute("SELECT COUNT(*) FROM beliefs").fetchone()[0], 'beliefs'
        elif 'belief_versions' in tables:
            return cur.execute("SELECT COUNT(DISTINCT belief_id) FROM belief_versions").fetchone()[0], 'belief_versions'
        else:
            belief_tables = [t for t in tables if 'belief' in t.lower()]
            print(f"  ⚠ No beliefs/belief_versions table. Tables with 'belief': {belief_tables}")
            print(f"  All tables: {sorted(tables)}")
            return 0, None


# ============================================================
# MT-1: Re-run AESHI with lowered Tier2 gate
# ============================================================
def task_mt1_aeshi_rescore():
    """Re-run AESHI with --min-tier2-coverage 0.70 (gate lowered per CW recommendation)."""
    print("\n" + "=" * 60)
    print("  MT-1: AESHI Re-Score (Tier2 gate lowered to 70%)")
    print("=" * 60)

    sys.path.insert(0, str(PROJECT_ROOT))

    try:
        from src.services.overseer import OverseerService
    except ImportError as e:
        print(f"  ❌ Cannot import OverseerService: {e}")
        return False

    # Use canonical db_locator
    web_db = _find_web_db()
    if not web_db:
        print("  ❌ Cannot find any web database")
        print("  Try: find ~ -name 'web_persistence*.db' -o -name 'ae.db' 2>/dev/null | head -5")
        return False

    # Show what's actually in the DB
    count, table_name = _count_beliefs(web_db)
    print(f"  DB: {web_db}")
    print(f"  Beliefs: {count} (from '{table_name}' table)")

    overseer_db = web_db.parent / "overseer.db"

    print(f"  Using web DB: {web_db}")
    print(f"  Using overseer DB: {overseer_db}")

    try:
        overseer = OverseerService(
            overseer_db_path=str(overseer_db),
            web=None,
            web_db_path=str(web_db),
        )

        # Run health check
        health = overseer.check_health()
        score = overseer.compute_aeshi(health)

        print(f"\n  📊 AESHI Score: {score}/100")
        print(f"  Gate status: {'✅ PASS' if score >= 70 else '❌ FAIL'}")

        # Show subscores
        for key, val in health.items():
            if key.startswith("_"):
                continue
            if isinstance(val, (int, float)):
                print(f"    {key}: {val:.4f}" if isinstance(val, float) else f"    {key}: {val}")

        # Run comprehensiveness audit
        audit = overseer.audit_aeshi_comprehensiveness()
        print(f"\n  Comprehensiveness: {audit['comprehensiveness_ratio']*100:.1f}%")
        print(f"  Measured: {audit['measured_count']}, Missing: {audit['recommended_count']}")
        for metric, desc in audit.get("recommended_additions", {}).items():
            print(f"    ⚠ Missing: {metric} — {desc}")

        return True

    except Exception as e:
        print(f"  ❌ AESHI computation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================
# MT-3: Re-run FTR and report Tier2 coverage
# ============================================================
def task_mt3_ftr_tier2():
    """Re-run FindingTemplateRelevance and report Tier2 coverage."""
    print("\n" + "=" * 60)
    print("  MT-3: FTR Tier2 Coverage Report")
    print("=" * 60)

    sys.path.insert(0, str(PROJECT_ROOT))

    try:
        # Check if backfill script exists
        backfill_script = PROJECT_ROOT / "scripts" / "backfill_env_outcome.py"
        if backfill_script.exists():
            print(f"  Running backfill first: {backfill_script}")
            db_path = PROJECT_ROOT / "ae.db"
            result = subprocess.run(
                [sys.executable, str(backfill_script), "--db", str(db_path)],
                capture_output=True, text=True, cwd=str(PROJECT_ROOT),
                timeout=120
            )
            if result.returncode == 0:
                print("  ✅ Backfill completed")
            else:
                print(f"  ⚠ Backfill failed: {result.stderr[:200]}")

        # Use canonical db_locator
        db_path = _find_web_db()
        if not db_path:
            print("  ❌ No database found")
            return False

        total, table_name = _count_beliefs(db_path)
        print(f"\n  DB: {db_path}")
        print(f"  Beliefs: {total} (from '{table_name}' table)")

        if total > 0 and table_name:
            with sqlite3.connect(str(db_path)) as conn:
                cur = conn.cursor()
                # Try template_ids column
                try:
                    with_t2 = cur.execute(
                        f"SELECT COUNT(*) FROM {table_name} WHERE template_ids IS NOT NULL AND template_ids != ''"
                    ).fetchone()[0]
                    print(f"  With Tier2 assignments: {with_t2}")
                    print(f"  Tier2 coverage: {with_t2/total*100:.1f}%")
                except Exception:
                    print(f"  ⚠ '{table_name}' table has no template_ids column")

    except Exception as e:
        print(f"  ❌ FTR check failed: {e}")
        return False

    return True


# ============================================================
# MT-14: Generate test results cache for AESHI integration
# ============================================================
def task_mt14_test_cache():
    """Run pytest --tb=no -q, parse results, write test_results_cache.json for AESHI."""
    print("\n" + "=" * 60)
    print("  MT-14: Generate Test Results Cache for AESHI")
    print("=" * 60)

    cache_path = PROJECT_ROOT / "data" / "test_results_cache.json"

    print("  Running pytest (this may take 3-5 minutes)...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--tb=no", "-q", "--no-header"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
            timeout=600  # 10 min timeout
        )

        output = result.stdout + result.stderr

        # Parse pytest output: "6509 passed, 1 failed, 51 skipped"
        import re
        passed = 0
        failed = 0
        skipped = 0
        errors = 0

        m = re.search(r'(\d+) passed', output)
        if m: passed = int(m.group(1))
        m = re.search(r'(\d+) failed', output)
        if m: failed = int(m.group(1))
        m = re.search(r'(\d+) skipped', output)
        if m: skipped = int(m.group(1))
        m = re.search(r'(\d+) error', output)
        if m: errors = int(m.group(1))

        cache_data = {
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "errors": errors,
            "total": passed + failed,
            "pass_rate": passed / max(passed + failed, 1),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "pytest_returncode": result.returncode,
        }

        cache_path.write_text(json.dumps(cache_data, indent=2))

        print(f"\n  ✅ Test results cached to {cache_path}")
        print(f"  Passed: {passed}, Failed: {failed}, Skipped: {skipped}")
        print(f"  Pass rate: {cache_data['pass_rate']*100:.1f}%")

        return True

    except subprocess.TimeoutExpired:
        print("  ❌ pytest timed out (>10 minutes)")
        return False
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False


# ============================================================
# MT-15: Populate template_ids in beliefs table
# ============================================================
def task_mt15_template_ids():
    """Populate template_ids column in beliefs table using template matcher."""
    print("\n" + "=" * 60)
    print("  MT-15: Populate template_ids in Beliefs Table")
    print("=" * 60)

    sys.path.insert(0, str(PROJECT_ROOT))

    db_path = _find_web_db()
    if not db_path:
        print("  ❌ No database found")
        return False

    total, table_name = _count_beliefs(db_path)
    print(f"  Using DB: {db_path}")
    print(f"  Table: {table_name}, Beliefs: {total}")

    try:
        with sqlite3.connect(str(db_path)) as conn:
            cur = conn.cursor()

            # Check current state
            total = cur.execute("SELECT COUNT(*) FROM beliefs").fetchone()[0]
            already = cur.execute(
                "SELECT COUNT(*) FROM beliefs WHERE template_ids IS NOT NULL AND template_ids != ''"
            ).fetchone()[0]
            print(f"  Total beliefs: {total}")
            print(f"  Already have template_ids: {already}")
            remaining = total - already

            if remaining == 0:
                print("  ✅ All beliefs already have template_ids")
                return True

            print(f"  Need to populate: {remaining}")

            # Get belief texts for matching
            cur.execute(
                "SELECT belief_id, content FROM beliefs "
                "WHERE template_ids IS NULL OR template_ids = ''"
            )
            rows = cur.fetchall()

            # Load templates
            template_dir = PROJECT_ROOT / "data" / "templates"
            templates = {}
            if template_dir.exists():
                for tf in template_dir.glob("*.json"):
                    try:
                        tdata = json.loads(tf.read_text())
                        tid = tdata.get("template_id", tf.stem)
                        templates[tid] = tdata
                    except Exception:
                        continue

            print(f"  Loaded {len(templates)} templates")

            if not templates:
                print("  ⚠ No templates found in data/templates/")
                return False

            # Simple keyword matching
            updated = 0
            for belief_id, claim_text in rows:
                if not claim_text:
                    continue

                claim_lower = claim_text.lower()
                matched = []

                for tid, tdata in templates.items():
                    t_keywords = tdata.get("keywords", [])
                    t_name = tdata.get("name", "").lower()
                    t_antecedent = tdata.get("antecedent_type", "").lower()
                    t_consequent = tdata.get("consequent_type", "").lower()

                    # Check keyword match
                    score = 0
                    for kw in t_keywords:
                        if kw.lower() in claim_lower:
                            score += 1
                    if t_antecedent and t_antecedent in claim_lower:
                        score += 2
                    if t_consequent and t_consequent in claim_lower:
                        score += 2

                    if score >= 2:
                        matched.append(tid)

                if matched:
                    cur.execute(
                        "UPDATE beliefs SET template_ids = ? WHERE belief_id = ?",
                        (json.dumps(matched[:5]), belief_id)  # Cap at 5
                    )
                    updated += 1

            conn.commit()
            print(f"\n  ✅ Updated {updated}/{remaining} beliefs with template_ids")
            print(f"  Coverage now: {(already + updated)/total*100:.1f}%")

    except Exception as e:
        print(f"  ❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


# ============================================================
# H12: V3 Re-extraction (59 zero-finding articles)
# ============================================================
def task_h12_reextraction():
    """Run V3 re-extraction on 59 zero-finding articles via Gemini."""
    print("\n" + "=" * 60)
    print("  H12: V3 Re-extraction (59 Zero-Finding Articles)")
    print("=" * 60)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("  ❌ GEMINI_API_KEY not set")
        print("  Run: export GEMINI_API_KEY='your-key-here'")
        return False

    # Check for zero-finding articles
    tier1_path = PROJECT_ROOT / "data" / "field_discovery" / "tier1_reextract.json"
    extractions_dir = PROJECT_ROOT / "data" / "extractions"

    if tier1_path.exists():
        with open(tier1_path) as f:
            tier1_articles = json.load(f)
        print(f"  Found {len(tier1_articles)} Tier 1 articles from CW's list")
    else:
        # Find zero-finding articles ourselves
        print("  Scanning for zero-finding articles...")
        tier1_articles = []
        for f in extractions_dir.glob("*.json"):
            if f.name in ("extraction_log.txt", "scholar_expansion_candidates.json"):
                continue
            try:
                data = json.loads(f.read_text())
                findings = data.get("findings", [])
                if len(findings) == 0:
                    tier1_articles.append(f.name)
            except Exception:
                continue
        print(f"  Found {len(tier1_articles)} zero-finding articles")

    if not tier1_articles:
        print("  ✅ No zero-finding articles remaining!")
        return True

    # Check if v3_reextraction.py exists
    reextract_script = PROJECT_ROOT / "scripts" / "v3_reextraction.py"
    if reextract_script.exists():
        print(f"  Running: {reextract_script}")
        result = subprocess.run(
            [sys.executable, str(reextract_script)],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
            timeout=1800  # 30 min
        )
        print(result.stdout[-500:] if result.stdout else "")
        if result.returncode == 0:
            print("  ✅ Re-extraction complete")
            return True
        else:
            print(f"  ❌ Failed: {result.stderr[:300]}")
            return False
    else:
        print(f"  ⚠ Script not found: {reextract_script}")
        print(f"  You can re-extract manually with Gemini on these {len(tier1_articles)} files")
        return False


# ============================================================
# Main
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="Run DB-blocked tasks that AG can't do from sandbox")
    parser.add_argument("--all", action="store_true", help="Run all tasks")
    parser.add_argument("--task", type=str, help="Run specific task (mt1|mt3|mt14|mt15|h12)")
    args = parser.parse_args()

    tasks = {
        "mt1": ("MT-1: AESHI Re-Score", task_mt1_aeshi_rescore),
        "mt3": ("MT-3: FTR Tier2 Coverage", task_mt3_ftr_tier2),
        "mt14": ("MT-14: Test Results Cache", task_mt14_test_cache),
        "mt15": ("MT-15: Template IDs Backfill", task_mt15_template_ids),
        "h12": ("H12: V3 Re-extraction", task_h12_reextraction),
    }

    if args.all:
        print("\n" + "=" * 60)
        print(f"  Running ALL {len(tasks)} blocked tasks")
        print("=" * 60)

        results = {}
        for key, (name, func) in tasks.items():
            try:
                results[key] = func()
            except Exception as e:
                print(f"  ❌ {name} failed: {e}")
                results[key] = False

        print("\n" + "=" * 60)
        print("  RESULTS SUMMARY")
        print("=" * 60)
        for key, (name, _) in tasks.items():
            status = "✅ DONE" if results.get(key) else "❌ FAILED"
            print(f"  {status}  {name}")

    elif args.task:
        key = args.task.lower()
        if key in tasks:
            name, func = tasks[key]
            func()
        else:
            print(f"Unknown task: {key}. Options: {', '.join(tasks.keys())}")
    else:
        parser.print_help()
        print("\nAvailable tasks:")
        for key, (name, _) in tasks.items():
            print(f"  {key:>5}  {name}")


if __name__ == "__main__":
    main()
