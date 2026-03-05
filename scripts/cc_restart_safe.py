#!/usr/bin/env python3
"""
CC Full Pipeline — Post-Crash Restart
=======================================

Runs ALL 5 processes that should be active after crash restart:

  1. DB health check           (MT-18: 10 success conditions)
  2. Env/outcome backfill      (MT-19: URGENT, blocks template matching)
  3. Card generation            (Gemini 2.0 Flash — Pass 1, ~$0.60)
  4. Stimulus extraction        (parallel, backfill stimulus_description)
  5. AESHI re-score             (MT-1: with lowered Tier2 gate)

Architecture:
  Pass 1: gemini-2.5-flash → draft cards ($0.60, ~3-4 hrs for all 4,002)
  Pass 2: Opus (CC session, free) → publication quality rewrite

PREREQUISITE:
  pip install google-genai

Usage:
  python3 scripts/cc_restart_safe.py session --terminal CC-1        # ALL 5 processes
  python3 scripts/cc_restart_safe.py session --terminal CC-1 --max 5  # Test with 5 cards
  python3 scripts/cc_restart_safe.py session --type t1-framework      # Just T1 ($0.01)
  python3 scripts/cc_restart_safe.py audit                            # Safety check only

Author: AG
Date: 2026-03-04
"""

from __future__ import annotations
import argparse, json, logging, os, subprocess, sys, time, traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# Colors + helpers
# ═══════════════════════════════════════════════════════════════
class C:
    R="\033[91m"; G="\033[92m"; Y="\033[93m"; B="\033[94m"
    BOLD="\033[1m"; DIM="\033[2m"; END="\033[0m"

def ok(m):  print(f"  {C.G}✓{C.END} {m}")
def wrn(m): print(f"  {C.Y}⚠{C.END} {m}")
def err(m): print(f"  {C.R}✗{C.END} {m}")
def hdr(m):
    print(f"\n{C.BOLD}{C.B}{'═'*60}{C.END}")
    print(f"{C.BOLD}{C.B}  {m}{C.END}")
    print(f"{C.BOLD}{C.B}{'═'*60}{C.END}")

# ═══════════════════════════════════════════════════════════════
# Paths
# ═══════════════════════════════════════════════════════════════
LOCK_FILES = [
    "data/extraction_pipeline/work_claims.lock",
    "data/extractions/progress_v2.lock", "data/extractions/recovery_claims.lock",
    "data/extractions/work_claims.lock",
    "data/review/garbled_rules_reaudit_queue.csv.lock",
    "data/review/noise_retry_single_queue.csv.lock",
    "data/review/noise_table_remake_paper_queue.csv.lock",
    "data/review/table_remake_paper_queue.csv.lock",
    "data/review/table_remake_paper_queue_round2.csv.lock",
]
CLAIMS_FILE = PROJECT_ROOT / "data" / "session_card_claims.json"
CARD_DIR = PROJECT_ROOT / "data" / "cards"
MV_DIR = PROJECT_ROOT / "data" / "materialized_views" / "cards"
SESSION_LOG = PROJECT_ROOT / "data" / "card_generation_session_log.json"
LOGS_DIR = PROJECT_ROOT / "logs"

# ═══════════════════════════════════════════════════════════════
# Gemini 2.0 Flash — Direct, no anthropic
# ═══════════════════════════════════════════════════════════════
class GeminiClient:
    def __init__(self):
        key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not key:
            raise RuntimeError("Set GEMINI_API_KEY or GOOGLE_API_KEY")
        try:
            import google.genai as genai
            self._client = genai.Client(api_key=key)
        except ImportError:
            raise RuntimeError("Run: pip install google-genai")

    def call(self, system: str, user: str, retries: int = 1) -> Tuple[str, int, int]:
        """Call gemini-2.5-flash. Returns (text, in_tokens, out_tokens).
        Retries once on transient errors with 5s backoff."""
        from google.genai import types

        for attempt in range(retries + 1):
            try:
                resp = self._client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=user,
                    config=types.GenerateContentConfig(
                        system_instruction=system,
                        temperature=0.3,
                        max_output_tokens=4096,
                    ),
                )
                text = resp.text or ""
                usage = getattr(resp, "usage_metadata", None)
                in_t = getattr(usage, "prompt_token_count", 0) if usage else 0
                out_t = getattr(usage, "candidates_token_count", 0) if usage else 0
                return text, in_t, out_t
            except Exception as e:
                if attempt < retries:
                    time.sleep(5)
                    continue
                raise

# ═══════════════════════════════════════════════════════════════
# PROCESS 0: Audit + Clean
# ═══════════════════════════════════════════════════════════════
def run_audit() -> Dict[str, Any]:
    hdr("CRASH RECOVERY AUDIT")
    results = {"all_clear": True}

    # Processes
    print(f"\n{C.BOLD}1. Conflicting Processes{C.END}")
    try:
        ps = subprocess.run(["ps","aux"], capture_output=True, text=True, timeout=5)
        bad = [s for s in ["batch_generate","session_generate","terminal_card_gen",
               "v3_reextraction","v3_surgical","backfill_template","nightly_integration"]
               if s in ps.stdout]
        if bad:
            results["all_clear"] = False
            for b in bad: err(f"Running: {b}")
        else: ok("No conflicts")
    except: ok("Could not check (sandbox)")

    # Locks
    print(f"\n{C.BOLD}2. Stale Locks{C.END}")
    stale = [r for r in LOCK_FILES if (PROJECT_ROOT/r).exists()]
    if stale:
        results["all_clear"] = False
        for s in stale: wrn(f"Stale: {s}")
    else: ok("No stale locks")
    results["stale_locks"] = stale

    # Claims
    print(f"\n{C.BOLD}3. Session Claims{C.END}")
    if CLAIMS_FILE.exists():
        try:
            data = json.loads(CLAIMS_FILE.read_text())
            orph = sum(1 for v in data.values() if v.get("status") in ("claimed","in_progress"))
            if orph:
                results["all_clear"] = False
                wrn(f"{orph} orphaned claims")
            else: ok(f"Claims OK ({len(data)})")
        except: results["all_clear"] = False; err("Claims corrupted")
    else: ok("No claims (fresh)")

    # Gemini
    print(f"\n{C.BOLD}4. Gemini API{C.END}")
    has_key = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    has_pkg = False
    try:
        import google.genai; has_pkg = True
    except ImportError: pass
    results["gemini_ready"] = has_key and has_pkg
    if has_key and has_pkg: ok("API key + google-genai ✓")
    elif has_key: results["all_clear"]=False; err("pip install google-genai")
    else: results["all_clear"]=False; err("No GEMINI_API_KEY")

    print(f"\n  {'✓ ALL CLEAR' if results['all_clear'] else '⚠ ISSUES FOUND'}")
    return results

def run_clean():
    hdr("CLEANING")
    for r in LOCK_FILES:
        p = PROJECT_ROOT/r
        if p.exists() and (time.time()-p.stat().st_mtime)>300:
            p.unlink(); ok(f"Removed: {r}")
    if CLAIMS_FILE.exists():
        try:
            data = json.loads(CLAIMS_FILE.read_text())
            cleaned = {k:v for k,v in data.items() if v.get("status")=="completed"}
            n = len(data)-len(cleaned)
            CLAIMS_FILE.write_text(json.dumps(cleaned, indent=2))
            if n: ok(f"Released {n} orphaned claims")
        except: CLAIMS_FILE.unlink(); ok("Reset corrupted claims")
    print(f"  {C.G}Clean done.{C.END}")

# ═══════════════════════════════════════════════════════════════
# PROCESS 1: DB Health Check (MT-18)
# ═══════════════════════════════════════════════════════════════
def run_db_health():
    hdr("PROCESS 1: DB HEALTH CHECK (MT-18)")
    script = PROJECT_ROOT / "scripts" / "check_db_health.py"
    if not script.exists():
        wrn("check_db_health.py not found, skipping")
        return
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True, text=True, timeout=30, cwd=str(PROJECT_ROOT)
        )
        # Print relevant output lines
        for line in result.stdout.splitlines():
            if any(k in line.lower() for k in ["pass","fail","warn","error","beliefs","template"]):
                print(f"  {line.strip()}")
        if result.returncode == 0: ok("DB health check complete")
        else: wrn(f"DB health check exit code {result.returncode}")
    except Exception as e:
        wrn(f"DB health check failed: {e}")

# ═══════════════════════════════════════════════════════════════
# PROCESS 2: Env/Outcome Backfill (MT-19)
# ═══════════════════════════════════════════════════════════════
def run_env_outcome_backfill():
    hdr("PROCESS 2: ENV/OUTCOME BACKFILL (MT-19)")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "src.services.belief_env_outcome_extractor",
             "--db", str(PROJECT_ROOT / "data" / "web_persistence.db"), "--write"],
            capture_output=True, text=True, timeout=120, cwd=str(PROJECT_ROOT)
        )
        for line in result.stdout.splitlines()[-10:]:
            print(f"  {line.strip()}")
        if result.returncode == 0: ok("Env/outcome backfill complete")
        else: wrn(f"Backfill exit code {result.returncode}")
    except subprocess.TimeoutExpired:
        wrn("Backfill timed out (2 min) — may need manual run")
    except Exception as e:
        wrn(f"Backfill failed: {e}")

# ═══════════════════════════════════════════════════════════════
# PROCESS 3: Card Generation (Gemini 2.0 Flash)
# ═══════════════════════════════════════════════════════════════
PRIORITY = [
    ("T1 Frameworks","t1-framework"), ("Molecules","molecule"),
    ("T2 Mechanisms","t2-mechanism"), ("Competitions","competition"),
    ("Layers","layer"), ("Methods","method"), ("Math","math"),
    ("T3 Beliefs","t3-belief"),
]

def _load_sources() -> Dict[str, List[Dict]]:
    data = {}
    try:
        from scripts.populate_all_cards import (
            load_t1_frameworks, load_molecules, load_t2_mechanisms,
            load_t3_beliefs, load_competitions, load_system_cards,
        )
        from src.qa.cards import CardType
        for name, fn in [("t1-framework",load_t1_frameworks),("molecule",load_molecules),
                         ("t2-mechanism",load_t2_mechanisms),("t3-belief",load_t3_beliefs),
                         ("competition",load_competitions)]:
            try:
                items = fn()
                if items: data[name] = items; ok(f"{len(items):,} {name}")
            except Exception as e: wrn(f"{name}: {e}")
        for st in ("layer","method","math"):
            try:
                items = load_system_cards(CardType(st))
                if items: data[st] = items; ok(f"{len(items)} {st}")
            except: pass
    except ImportError as e:
        wrn(f"populate_all_cards import failed: {e}")
    return data

def _card_done(ct: str, eid: str, done_set: set = None) -> bool:
    """Check if card already exists on disk OR was processed in this session."""
    if done_set and f"{ct}/{eid}" in done_set:
        return True
    for base in [CARD_DIR/ct, CARD_DIR]:
        if (base/f"{eid}.json").exists(): return True
    for tier in ("A","B","C"):
        if (MV_DIR/tier/ct/f"{eid}.json").exists(): return True
    return False

def _save_checkpoint(log: Dict, terminal: str):
    """Save session log to disk after every card. Crash-resilient."""
    checkpoint = {
        "terminal": terminal, "model": "gemini-2.5-flash",
        "last_checkpoint": datetime.now(timezone.utc).isoformat(),
        **log,
    }
    SESSION_LOG.parent.mkdir(parents=True, exist_ok=True)
    # Write to temp file first, then rename (atomic on most filesystems)
    tmp = SESSION_LOG.with_suffix(".tmp")
    tmp.write_text(json.dumps(checkpoint, indent=2, default=str))
    tmp.rename(SESSION_LOG)

def _load_previous_session() -> set:
    """Load IDs of cards already processed from a previous session log."""
    done = set()
    if SESSION_LOG.exists():
        try:
            data = json.loads(SESSION_LOG.read_text())
            for card in data.get("generated", []):
                done.add(f"{card['type']}/{card['id']}")
            for card in data.get("skipped", []):
                done.add(f"{card['type']}/{card['id']}")
        except Exception:
            pass
    return done

def _gen_card(gemini: GeminiClient, ct: str, src: Dict, term: str) -> Optional[Dict]:
    from src.qa.card_tab_generators import (
        TAB_GENERATOR_CONFIG, _parse_llm_response, _check_prose_health, _omega_to_confidence,
    )
    from src.qa.cards.card_schema import (
        CardTab, CardBody, CardSurface, CardIceberg,
        IcebergSourceMap, IcebergAgentContext, IcebergQualityScores, create_card,
    )
    from src.qa.cards import CardType
    from src.qa.cards.card_types import get_card_type_spec

    card_type = CardType(ct)
    eid = src.get("entity_id", "unknown")
    spec = get_card_type_spec(card_type)
    tabs = {}
    tin = tout = 0
    t0 = time.time()

    for tab_name in sorted(spec.required_tabs | spec.optional_tabs):
        if tab_name == "history" or tab_name not in TAB_GENERATOR_CONFIG:
            continue
        sys_prompt, ctx_fn = TAB_GENERATOR_CONFIG[tab_name]
        user_prompt = ctx_fn(src, card_type)
        user_prompt += f"\n\nWrite the {tab_name.upper()} tab. Follow all norms. Wrap structured data in ```json ... ```."

        try:
            text, it, ot = gemini.call(sys_prompt, user_prompt, retries=1)
            tin += it; tout += ot
            prose, sdata = _parse_llm_response(text)
            health = _check_prose_health(prose)
            if health < 6.0 and prose:
                prose = f"[DRAFT — prose_health={health:.1f}] {prose}"
            tabs[tab_name] = CardTab(tab_name=tab_name, prose=prose, structured_data=sdata)
            time.sleep(0.3)  # rate limit
        except Exception as e:
            logger.warning(f"Tab {tab_name} failed for {eid}: {e}")

    if not tabs: return None

    omega = src.get("omega", src.get("confidence_omega", 0.5))
    # Map omega to ConfidenceLevel enum
    from src.qa.cards.card_schema import ConfidenceLevel, Direction, Staleness
    if omega >= 0.75:
        conf = ConfidenceLevel.HIGH
    elif omega >= 0.60:
        conf = ConfidenceLevel.MOD_HIGH
    elif omega >= 0.40:
        conf = ConfidenceLevel.MODERATE
    else:
        conf = ConfidenceLevel.LOW

    card = create_card(
        card_type=card_type,
        entity_id=eid,
        title=src.get("title", eid),
        confidence_level=conf,
        confidence_omega=omega,
        direction=Direction.NA,
        n_findings=src.get("n_findings", 0),
        n_papers=src.get("n_papers", 0),
    )
    # Attach generated body
    card.body = CardBody(tabs=tabs)
    # Build provenance from enriched source data
    source_prov = src.get("provenance", {})
    # Extract DOIs and template IDs from findings for provenance
    paper_dois = list(set(
        f.get("paper_doi", "") for f in src.get("findings", [])
        if f.get("paper_doi")
    ))[:20]
    template_ids = [ct.get("template_id", "") for ct in src.get("child_templates", [])][:20]
    framework_ids = [src.get("t1_code", "")] if src.get("t1_code") else []

    source_map = IcebergSourceMap(
        paper_dois=paper_dois,
        template_ids=template_ids,
        framework_ids=framework_ids,
    )
    card.iceberg = CardIceberg(
        source_map=source_map,
        agent_context=IcebergAgentContext(
            model=f"gemini-2.5-flash",
            prompt_template=f"tab_generators_{term}",
            token_count_input=tin,
            token_count_output=tout,
            generation_duration_ms=int((time.time()-t0)*1000),
        ),
        quality_scores=IcebergQualityScores(),
        raw_data={
            # --- Core stats ---
            "n_findings_in_source": src.get("all_findings_count", src.get("n_findings", 0)),
            "n_papers_in_source": src.get("n_papers", 0),
            "omega_in_source": src.get("omega", 0),
            "has_enriched_data": bool(source_prov),
            "enrichment_timestamp": source_prov.get("enrichment_timestamp", ""),
            "data_layers": source_prov.get("data_layers", []),
            # --- Deep layer data for follow-up questions ---
            # Evidence / effect magnitude layer (a14)
            "effect_magnitudes": src.get("effect_magnitudes", []),
            "n_effect_magnitudes": src.get("n_effect_magnitudes", 0),
            # Debate layer: disputes (a11), surprises (a9), unanswered Qs (a18)
            "disputes": src.get("disputes", []),
            "surprise_flags": src.get("surprise_flags", []),
            "unanswered_questions": src.get("unanswered_questions", []),
            # Design layer: CVA (stimuli, measurements)
            "cva_stimuli": src.get("cva_stimuli", []),
            "cva_measurements": src.get("cva_measurements", []),
            "cva_molecule_links": src.get("cva_molecule_links", []),
            # Evidence layer: replication & design implications
            "replication_status": src.get("replication_status", []),
            "design_implications": src.get("design_implications", []),
            # Narrative hooks for engagement
            "narrative_hooks": src.get("narrative_hooks", []),
            # Interpretation layer (T3)
            "credence": src.get("credence"),
            "entrenchment": src.get("entrenchment"),
            "interrogation_score": src.get("interrogation_score"),
            # Provenance source files
            "source_files": source_prov.get("source_files", [])[:20],
        },
    )
    out = CARD_DIR / ct; out.mkdir(parents=True, exist_ok=True)
    card.save(out / f"{eid}.json")
    return {"id":eid,"type":ct,"tabs":list(tabs.keys()),"tin":tin,"tout":tout}

def run_cards(gemini: GeminiClient, terminal: str, max_cards: int, type_filter: Optional[str]):
    hdr("PROCESS 3: CARD GENERATION (Gemini 2.0 Flash)")

    sources = _load_sources()
    if not sources:
        err("No source data — run populate_all_cards.py first")
        return {"generated":[],"failed":[],"skipped":[]}

    total = sum(len(v) for v in sources.values())
    print(f"\n  Total entities: {C.BOLD}{total:,}{C.END}")

    # Resume: load IDs already processed in previous session
    prev_done = _load_previous_session()
    if prev_done:
        ok(f"Resuming — {len(prev_done)} cards already processed in previous session")

    log = {"generated":[],"failed":[],"skipped":[]}
    n = 0; target = max_cards or total; tin_all = tout_all = 0

    for label, ct in PRIORITY:
        if type_filter and ct != type_filter: continue
        items = sources.get(ct, [])
        if not items: continue
        print(f"\n{C.BOLD}  ── {label} ({len(items)}) ──{C.END}")

        for item in items:
            if max_cards and n >= max_cards: break
            eid = item.get("entity_id", item.get("id", "unknown"))
            if _card_done(ct, eid, prev_done):
                log["skipped"].append({"id":eid,"type":ct}); continue
            n += 1
            pct = n/target*100
            filled = int(30*n/target)
            print(f"\r  [{'█'*filled}{'░'*(30-filled)}] {pct:5.1f}% ({n}/{target}) {label}: {eid[:40]}  ", end="", flush=True)
            try:
                r = _gen_card(gemini, ct, item, terminal)
                if r:
                    log["generated"].append(r)
                    tin_all += r.get("tin",0); tout_all += r.get("tout",0)
                else:
                    log["failed"].append({"id":eid,"type":ct,"err":"no tabs"})
            except Exception as e:
                log["failed"].append({"id":eid,"type":ct,"err":str(e)[:200]})

            # CHECKPOINT: save after every card so laptop close → re-run resumes
            _save_checkpoint(log, terminal)

        if max_cards and n >= max_cards:
            print(f"\n  Reached limit ({max_cards})"); break

    cost = (tin_all/1e6)*0.10 + (tout_all/1e6)*0.40
    print(f"\n\n  Generated: {C.G}{len(log['generated'])}{C.END}")
    print(f"  Skipped:   {C.DIM}{len(log['skipped'])}{C.END}")
    if log["failed"]: print(f"  Failed:    {C.R}{len(log['failed'])}{C.END}")
    print(f"  Tokens:    {tin_all:,} in / {tout_all:,} out")
    print(f"  Cost:      ${cost:.2f}")
    return log

# ═══════════════════════════════════════════════════════════════
# PROCESS 4: Stimulus Extraction (parallel)
# ═══════════════════════════════════════════════════════════════
def run_stimulus_bg() -> Optional[subprocess.Popen]:
    script = PROJECT_ROOT / "scripts" / "run_stimulus_extraction.py"
    if not script.exists():
        wrn("run_stimulus_extraction.py not found"); return None
    LOGS_DIR.mkdir(exist_ok=True)
    log_file = LOGS_DIR / "stimulus_extraction.log"
    try:
        proc = subprocess.Popen(
            [sys.executable, str(script), "--max-articles", "50"],
            stdout=open(log_file, "w"), stderr=subprocess.STDOUT, cwd=str(PROJECT_ROOT),
        )
        ok(f"Stimulus extraction launched (PID {proc.pid})")
        ok(f"  Log: tail -f {log_file}")
        return proc
    except Exception as e:
        wrn(f"Could not launch stimulus extraction: {e}"); return None

# ═══════════════════════════════════════════════════════════════
# PROCESS 5: AESHI Re-score (MT-1)
# ═══════════════════════════════════════════════════════════════
def run_aeshi():
    hdr("PROCESS 5: AESHI RE-SCORE (MT-1)")
    script = PROJECT_ROOT / "scripts" / "run_blocked_tasks.py"
    if not script.exists():
        wrn("run_blocked_tasks.py not found"); return
    try:
        result = subprocess.run(
            [sys.executable, str(script), "--task", "mt1"],
            capture_output=True, text=True, timeout=60, cwd=str(PROJECT_ROOT),
        )
        for line in result.stdout.splitlines()[-15:]:
            print(f"  {line.strip()}")
        if result.returncode == 0: ok("AESHI re-score complete")
        else: wrn(f"AESHI exit code {result.returncode}")
    except Exception as e:
        wrn(f"AESHI re-score failed: {e}")

# ═══════════════════════════════════════════════════════════════
# SESSION: Run all 5 processes
# ═══════════════════════════════════════════════════════════════
def run_session(terminal: str, max_cards: int = 0, type_filter: Optional[str] = None):
    hdr("CC FULL PIPELINE — POST-CRASH RESTART")
    print(f"  Terminal:  {terminal}")
    print(f"  Model:     gemini-2.5-flash (Pass 1) → Opus (Pass 2, free)")
    print(f"  Cards:     {'all' if not max_cards else max_cards}")
    print(f"  Time:      {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 0. Audit + clean
    results = run_audit()
    if not results["all_clear"]:
        print(f"\n{C.Y}Auto-cleaning...{C.END}")
        run_clean()
        results = run_audit()
    if not results.get("gemini_ready"):
        err("Gemini not ready. Fix issues above."); sys.exit(1)

    # Init Gemini
    gemini = GeminiClient()
    ok("Gemini client initialized")

    # 1. DB health
    run_db_health()

    # 2. Env/outcome backfill
    run_env_outcome_backfill()

    # 3. Card generation (main workload)
    # 4. Stimulus extraction (launched in parallel with cards)
    stim_proc = run_stimulus_bg()
    card_log = run_cards(gemini, terminal, max_cards, type_filter)

    # 5. AESHI re-score
    run_aeshi()

    # Check stimulus
    if stim_proc:
        if stim_proc.poll() is not None:
            ok(f"Stimulus extraction finished (exit {stim_proc.returncode})")
        else:
            ok(f"Stimulus extraction still running (PID {stim_proc.pid})")

    # Final save (checkpoint already saved per-card, this adds final metadata)
    _save_checkpoint(card_log, terminal)

    # Final report
    hdr("ALL PROCESSES COMPLETE")
    print(f"  Cards generated: {len(card_log['generated'])}")
    print(f"  Cards failed:    {len(card_log['failed'])}")
    print(f"  Cards skipped:   {len(card_log['skipped'])}")
    if card_log["generated"]:
        print(f"\n  {C.BOLD}Next: Opus polish (free in CC session):{C.END}")
        print(f"    python3 scripts/batch_generate_cards.py --process-opus-queue")
    if card_log["failed"]:
        print(f"\n  {C.BOLD}Failed cards (re-run with same command to retry):{C.END}")
        for f in card_log["failed"][:5]:
            print(f"    {f['type']}/{f['id']}: {f.get('err','?')[:60]}")
    print()

# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════
def main():
    p = argparse.ArgumentParser(
        description="CC post-crash restart: all 5 pipeline processes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Prerequisite: pip install google-genai

THE ONE COMMAND:
  python3 scripts/cc_restart_safe.py session --terminal CC-1

Test run:
  python3 scripts/cc_restart_safe.py session --terminal CC-1 --max 2

Other:
  audit          Safety check only
  clean          Remove stale locks only
""")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("audit")
    sub.add_parser("clean")
    s = sub.add_parser("session")
    s.add_argument("--terminal", default="CC-1")
    s.add_argument("--max", type=int, default=0, dest="max_cards")
    s.add_argument("--type", dest="type_filter")

    args = p.parse_args()
    if not args.cmd: p.print_help(); return
    if args.cmd == "audit": run_audit()
    elif args.cmd == "clean": run_clean()
    elif args.cmd == "session": run_session(args.terminal, args.max_cards, args.type_filter)

if __name__ == "__main__":
    main()
