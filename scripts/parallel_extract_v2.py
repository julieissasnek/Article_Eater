#!/usr/bin/env python3
"""
PARALLEL EXTRACTION V2 — Revised Prompts + WorkClaimer + Recovery
=================================================================

Integrated extraction pipeline using:
  - Revised prompts from revised_prompts_v2.py (5× more findings)
  - Lightweight classification (intro+conclusion pages only)
  - normalize_extraction + evaluate_quality_v2 (4-tier routing)
  - WorkClaimer for parallel multi-process safety
  - Rate limiting (staggered starts, per-minute caps)
  - Robust JSON recovery for partial/malformed outputs

USAGE — Single worker:
    python scripts/parallel_extract_v2.py --limit 20

USAGE — Multiple workers (run each in a separate terminal):
    python scripts/parallel_extract_v2.py --worker 1 --limit 50
    python scripts/parallel_extract_v2.py --worker 2 --limit 50
    python scripts/parallel_extract_v2.py --worker 3 --limit 50

USAGE — Status check:
    python scripts/parallel_extract_v2.py --status

USAGE — Recovery (retries all failed papers):
    python scripts/parallel_extract_v2.py --recover

USAGE — Type filter:
    python scripts/parallel_extract_v2.py --type empirical --limit 20

Author: AG (Pipeline Integration Sprint)
Date: 2026-02-25
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import io
import json
import os
import signal
import socket
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

# ── Project paths ──
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

AF_ROOT = Path("/Users/davidusa/REPOS/Article_Finder_v3_2_3")
PDF_DIR = AF_ROOT / "data" / "pdfs"
TRIAGE_FILE = PROJECT_ROOT / "data" / "triage" / "keyword_triage.json"
OUTPUT_DIR = PROJECT_ROOT / "data" / "extractions"
RAW_FAILURES_DIR = OUTPUT_DIR / "raw_failures"
CLAIMS_FILE = OUTPUT_DIR / "work_claims.json"
PROGRESS_FILE = OUTPUT_DIR / "progress_v2.json"

# ── Rate limiting ──
REQUESTS_PER_MINUTE = 10         # Gemini Flash free tier = 15 RPM; stay under
SECONDS_BETWEEN_REQUESTS = 60 / REQUESTS_PER_MINUTE  # 6 seconds

# ── Pricing ──
PRICING = {
    "gemini-2.5-flash": {"input": 0.15, "output": 0.60},
    "gemini-2.5-pro":   {"input": 1.25, "output": 10.00},
}

# ── Recovery config ──
COST_GUARDRAIL = 5.00  # Auto-run recovery if estimated cost < this
RECOVERY_MAX_OUTPUT_TOKENS = 131072  # 2× normal for truncated papers
AVG_COST_PER_RETRY = 0.008  # Estimated from first run data


# ═══════════════════════════════════════════════════════════════════════════
# ROBUST JSON PARSING — salvages partial/malformed Gemini outputs
# ═══════════════════════════════════════════════════════════════════════════

def robust_json_parse(text: str) -> Optional[dict]:
    """
    Try increasingly aggressive strategies to extract valid JSON.

    Handles:
    1. Normal JSON (fast path)
    2. "Extra data" — Gemini outputs two JSON blobs; take first balanced one
    3. "Unterminated string" — output truncated; close open strings/arrays/objects
    4. Trailing commas, missing quotes, etc.
    """
    if not text or not text.strip():
        return None

    text = text.strip()

    # Strip markdown code fences
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        text = text.strip()

    # Strategy 1: Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strategy 2: Balanced-brace extraction (for "Extra data" errors)
    # Find the first { and track brace depth to find matching }
    first_brace = text.find("{")
    if first_brace >= 0:
        depth = 0
        in_string = False
        escape = False
        for i, ch in enumerate(text[first_brace:], start=first_brace):
            if escape:
                escape = False
                continue
            if ch == "\\" and in_string:
                escape = True
                continue
            if ch == '"' and not escape:
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    candidate = text[first_brace:i+1]
                    try:
                        return json.loads(candidate)
                    except json.JSONDecodeError:
                        break  # Try next strategy

    # Strategy 3: Truncation repair — close open structures
    repaired = text
    # Remove trailing incomplete string
    if repaired.count('"') % 2 != 0:
        last_quote = repaired.rfind('"')
        if last_quote > 0:
            repaired = repaired[:last_quote+1]

    # Close open arrays and objects
    open_braces = repaired.count("{") - repaired.count("}")
    open_brackets = repaired.count("[") - repaired.count("]")

    # Remove trailing comma before closing
    repaired = repaired.rstrip()
    if repaired.endswith(","):
        repaired = repaired[:-1]

    repaired += "]" * max(0, open_brackets) + "}" * max(0, open_braces)

    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        pass

    # Strategy 4: Remove trailing garbage after last complete finding
    # Find the last "} ," or "}," pattern and close there
    last_finding_end = max(repaired.rfind("},"), repaired.rfind("}\n"))
    if last_finding_end > 0:
        truncated = repaired[:last_finding_end+1]
        open_b = truncated.count("{") - truncated.count("}")
        open_br = truncated.count("[") - truncated.count("]")
        truncated += "]" * max(0, open_br) + "}" * max(0, open_b)
        try:
            return json.loads(truncated)
        except json.JSONDecodeError:
            pass

    return None


def save_raw_failure(doi: str, raw_text: str, error: str):
    """Save raw Gemini output for failed extractions."""
    RAW_FAILURES_DIR.mkdir(parents=True, exist_ok=True)
    doi_safe = doi.replace("/", "_")
    raw_file = RAW_FAILURES_DIR / f"{doi_safe}.txt"
    meta_file = RAW_FAILURES_DIR / f"{doi_safe}.meta.json"

    raw_file.write_text(raw_text)
    meta_file.write_text(json.dumps({
        "doi": doi,
        "error": error,
        "raw_chars": len(raw_text),
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }, indent=2))

    return raw_file


# ═══════════════════════════════════════════════════════════════════════════
# WORK CLAIMER (from pdf_extraction_module.py — self-contained copy)
# ═══════════════════════════════════════════════════════════════════════════

class WorkClaimer:
    """Distributed work claiming via file lock for parallel agent execution."""

    CLAIM_TIMEOUT_SECONDS = 600  # 10 min

    def __init__(self, claims_file: Path, agent_id: Optional[str] = None):
        self.claims_file = claims_file
        self.lock_file = claims_file.with_suffix(".lock")
        self.agent_id = agent_id or f"{socket.gethostname()}_{os.getpid()}_{datetime.now().strftime('%H%M%S')}"

    def _with_lock(self, func):
        self.claims_file.parent.mkdir(parents=True, exist_ok=True)
        lock_fd = open(self.lock_file, "w")
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX)
            return func()
        finally:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            lock_fd.close()

    def _read(self) -> dict:
        if self.claims_file.exists():
            try:
                return json.loads(self.claims_file.read_text())
            except Exception as e:
                import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")
        return {"claims": {}, "completed": [], "failed": []}

    def _write(self, data: dict):
        self.claims_file.write_text(json.dumps(data, indent=2))

    def claim_papers(self, dois: list[str], max_claims: int = 5) -> list[str]:
        """Atomically claim papers. Returns DOIs successfully claimed."""
        def _do():
            data = self._read()
            claims = data.get("claims", {})
            completed = set(data.get("completed", []))
            failed = set(data.get("failed", []))
            now = datetime.now(timezone.utc)
            claimed = []

            for doi in dois:
                if len(claimed) >= max_claims:
                    break
                if doi in completed or doi in failed:
                    continue
                if doi in claims:
                    claim = claims[doi]
                    age = (now - datetime.fromisoformat(claim["claimed_at"])).total_seconds()
                    if claim["agent_id"] == self.agent_id:
                        continue
                    if age < self.CLAIM_TIMEOUT_SECONDS:
                        continue
                    # Stale claim — reclaim
                claims[doi] = {
                    "agent_id": self.agent_id,
                    "claimed_at": now.isoformat(),
                }
                claimed.append(doi)

            data["claims"] = claims
            self._write(data)
            return claimed

        return self._with_lock(_do)

    def release(self, doi: str, status: str = "completed"):
        """Release a paper after processing."""
        def _do():
            data = self._read()
            data.get("claims", {}).pop(doi, None)
            if status == "completed":
                completed = set(data.get("completed", []))
                completed.add(doi)
                data["completed"] = sorted(completed)
            elif status == "failed":
                failed = set(data.get("failed", []))
                failed.add(doi)
                data["failed"] = sorted(failed)
            self._write(data)
        self._with_lock(_do)

    def get_status(self) -> dict:
        def _do():
            data = self._read()
            return {
                "active_claims": len(data.get("claims", {})),
                "completed": len(data.get("completed", [])),
                "failed": len(data.get("failed", [])),
                "agents": list({c["agent_id"] for c in data.get("claims", {}).values()}),
            }
        return self._with_lock(_do)


# ═══════════════════════════════════════════════════════════════════════════
# PROGRESS TRACKER
# ═══════════════════════════════════════════════════════════════════════════

def update_progress(doi: str, result: dict):
    """Append a result to the shared progress file (file-locked)."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    lock_path = PROGRESS_FILE.with_suffix(".lock")
    lock_fd = open(lock_path, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        data = json.loads(PROGRESS_FILE.read_text()) if PROGRESS_FILE.exists() else {"results": [], "stats": {}}
        data["results"].append(result)

        # Update running stats
        stats = data.get("stats", {})
        stats["total_processed"] = len(data["results"])
        stats["total_accepted"] = sum(1 for r in data["results"] if r.get("action") == "accept")
        stats["total_failed"] = sum(1 for r in data["results"] if r.get("action") == "fail")
        stats["total_cost"] = round(sum(r.get("cost", 0) for r in data["results"]), 4)
        stats["last_updated"] = datetime.now(timezone.utc).isoformat()
        data["stats"] = stats

        PROGRESS_FILE.write_text(json.dumps(data, indent=2))
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()


# ═══════════════════════════════════════════════════════════════════════════
# CORE EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════

def get_client():
    from google import genai
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Set GOOGLE_API_KEY or GEMINI_API_KEY")
        sys.exit(1)
    return genai.Client(api_key=api_key)


def classify_paper(client, pdf_path: Path, model: str = "gemini-2.5-flash") -> dict:
    """Classify using intro+conclusion pages only (saves ~60% cost)."""
    from google.genai import types
    from src.extraction.revised_prompts_v2 import CLASSIFICATION_PROMPT

    try:
        import pymupdf
    except ImportError:
        import fitz as pymupdf

    doc = pymupdf.open(str(pdf_path))
    n_pages = len(doc)

    if n_pages <= 5:
        pages = list(range(n_pages))
    else:
        pages = [0, 1, 2, n_pages - 2, n_pages - 1]

    text_chunks = []
    for p in pages:
        text_chunks.append(f"--- PAGE {p+1} ---\n{doc[p].get_text()}")
    doc.close()

    extracted_text = "\n\n".join(text_chunks)

    response = client.models.generate_content(
        model=model,
        contents=[extracted_text + "\n\n" + CLASSIFICATION_PROMPT],
        config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=2048),
    )

    text = response.text.strip() if response.text else ""
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

    cost = 0.0
    if response.usage_metadata:
        m = response.usage_metadata
        p = PRICING.get(model, PRICING["gemini-2.5-flash"])
        cost = (m.prompt_token_count * p["input"] + m.candidates_token_count * p["output"]) / 1_000_000

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        result = {"article_type": "unknown", "article_family": "unknown", "confidence": 0.0}

    result["_cost"] = cost
    return result


def extract_paper(client, pdf_path: Path, article_type: str, model: str = "gemini-2.5-flash",
                  max_output_tokens: int = 65536, doi: str = "") -> dict:
    """Run extraction with revised prompts. Includes robust JSON recovery."""
    from google.genai import types
    from src.extraction.revised_prompts_v2 import PROMPT_MAP, FAMILY_MAP

    prompt = PROMPT_MAP.get(article_type, PROMPT_MAP.get("unknown"))

    start = time.time()

    with open(pdf_path, "rb") as f:
        uploaded = client.files.upload(file=f, config={"mime_type": "application/pdf"})

    try:
        while uploaded.state.name == "PROCESSING":
            time.sleep(1)
            uploaded = client.files.get(name=uploaded.name)

        if uploaded.state.name == "FAILED":
            return {"success": False, "error": "Upload processing failed"}

        response = client.models.generate_content(
            model=model,
            contents=[
                types.Part.from_uri(file_uri=uploaded.uri, mime_type="application/pdf"),
                prompt,
            ],
            config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=max_output_tokens),
        )

        elapsed = time.time() - start

        raw_text = response.text.strip() if response.text else ""

        # Cost (compute before parsing so we track even on failure)
        cost = 0.0
        if response.usage_metadata:
            m = response.usage_metadata
            p = PRICING.get(model, PRICING["gemini-2.5-flash"])
            cost = (m.prompt_token_count * p["input"] + m.candidates_token_count * p["output"]) / 1_000_000

        # Try robust JSON parsing (handles Extra data, truncation, etc.)
        result = robust_json_parse(raw_text)

        if result is None:
            # Save raw output for later analysis
            if doi and raw_text:
                save_raw_failure(doi, raw_text, "robust_json_parse failed")
            return {
                "success": False,
                "error": f"JSON parse failed after robust recovery ({len(raw_text)} chars)",
                "cost": round(cost, 6),
                "raw_chars": len(raw_text),
            }

        # Normalize extraction (canonical 'findings' key)
        from src.extraction.pipeline_repairs import normalize_extraction
        result = normalize_extraction(result)

        return {
            "success": True,
            "data": result,
            "cost": round(cost, 6),
            "elapsed": round(elapsed, 1),
            "model": model,
            "n_findings": len(result.get("findings", [])),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        try:
            client.files.delete(name=uploaded.name)
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")


def evaluate_quality(extraction_data: dict, article_type: str) -> dict:
    """Evaluate extraction quality with 4-tier routing."""
    from src.extraction.pipeline_repairs import _get_threshold, FIELD_WEIGHTS_V2

    findings = extraction_data.get("findings", [])
    n = len(findings)

    if n == 0:
        return {"action": "requeue", "score": 0.0, "n_findings": 0, "issues": ["No findings"]}

    thresholds = _get_threshold(article_type)

    has_ac = sum(1 for f in findings if f.get("antecedent") and f.get("consequent")) / n
    has_dir = sum(1 for f in findings if f.get("direction")) / n
    has_stats = sum(1 for f in findings if f.get("p_value") or f.get("effect_size")) / n
    has_theory = sum(1 for f in findings if f.get("theory_links")) / n
    has_template = sum(1 for f in findings if f.get("template_ids")) / n

    w = FIELD_WEIGHTS_V2
    score = (
        w["antecedent"] * has_ac + w["consequent"] * has_ac +
        w["direction"] * has_dir + w["p_value"] * has_stats +
        w["effect_size"] * has_stats + w["theory_links"] * has_theory +
        w["template_ids"] * has_template +
        w["quote"] * (sum(1 for f in findings if f.get("quote")) / n) +
        w["source"] * (sum(1 for f in findings if f.get("source")) / n)
    )
    score = score / sum(w.values())

    issues = []
    if has_ac < 0.7:
        issues.append(f"Low A→C coverage: {has_ac:.0%}")
    if has_stats < thresholds["require_statistics"]:
        issues.append(f"Low stats: {has_stats:.0%}")

    if score >= thresholds["min_score_accept"] and len(issues) <= 1:
        action = "accept"
    elif score >= thresholds["min_score_repair"]:
        action = "repair"
    else:
        action = "fail"

    return {"action": action, "score": round(score, 3), "n_findings": n, "issues": issues}


# ═══════════════════════════════════════════════════════════════════════════
# WORKER LOOP
# ═══════════════════════════════════════════════════════════════════════════

def process_one(client, claimer: WorkClaimer, doi: str, triage_type: str) -> dict:
    """Process a single paper: classify → extract → evaluate → save."""

    pdf_path = PDF_DIR / (doi.replace("/", "_") + ".pdf")
    if not pdf_path.exists():
        claimer.release(doi, "failed")
        return {"doi": doi, "action": "fail", "error": "PDF not found"}

    result = {
        "doi": doi,
        "triage_type": triage_type,
        "worker": claimer.agent_id,
        "started_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        # ── Step 1: Classify ──
        if triage_type == "unknown":
            classification = classify_paper(client, pdf_path)
            article_type = classification.get("article_type", "unknown")
            article_family = classification.get("article_family", "unknown")
            result["classification"] = classification
            result["cost"] = classification.get("_cost", 0)
            time.sleep(SECONDS_BETWEEN_REQUESTS)  # Rate limit
        else:
            article_type = triage_type
            article_family = None
            result["cost"] = 0

        # ── Step 2: Extract ──
        extraction = extract_paper(client, pdf_path, article_type, doi=doi)
        result["extraction_success"] = extraction.get("success", False)
        result["cost"] = result.get("cost", 0) + extraction.get("cost", 0)
        result["elapsed"] = extraction.get("elapsed", 0)
        result["n_findings"] = extraction.get("n_findings", 0)
        result["model"] = extraction.get("model", "gemini-2.5-flash")

        if not extraction.get("success"):
            result["action"] = "fail"
            result["error"] = extraction.get("error", "Unknown extraction error")
            claimer.release(doi, "failed")
            update_progress(doi, result)
            return result

        # ── Step 3: Evaluate quality ──
        quality = evaluate_quality(extraction["data"], article_type)
        result["action"] = quality["action"]
        result["quality_score"] = quality["score"]
        result["quality_issues"] = quality["issues"]

        # ── Step 4: Save ──
        doi_safe = doi.replace("/", "_")
        output_file = OUTPUT_DIR / f"{doi_safe}.json"
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        save_data = {
            "doi": doi,
            "article_type": article_type,
            "article_family": article_family,
            "quality_action": quality["action"],
            "quality_score": quality["score"],
            "n_findings": extraction.get("n_findings", 0),
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "model": extraction.get("model"),
            "cost": result.get("cost", 0),
            **extraction["data"],
        }
        output_file.write_text(json.dumps(save_data, indent=2))

        claimer.release(doi, "completed" if quality["action"] in ("accept", "repair") else "failed")
        result["completed_at"] = datetime.now(timezone.utc).isoformat()
        update_progress(doi, result)
        return result

    except Exception as e:
        result["action"] = "fail"
        result["error"] = str(e)[:200]
        claimer.release(doi, "failed")
        update_progress(doi, result)
        return result


def worker_loop(args):
    """Main worker loop — claim papers, process, release, repeat."""

    print(f"╔══════════════════════════════════════════════════════════════╗")
    print(f"║  PARALLEL EXTRACTION V2 — Worker {args.worker or 0:<3}                        ║")
    print(f"║  Using revised prompts • Rate: {REQUESTS_PER_MINUTE} req/min               ║")
    print(f"╚══════════════════════════════════════════════════════════════╝")

    client = get_client()

    agent_id = f"w{args.worker or 0}_{os.getpid()}"
    claimer = WorkClaimer(CLAIMS_FILE, agent_id)
    print(f"Agent ID: {agent_id}")

    # Load triage
    triage = json.loads(TRIAGE_FILE.read_text())
    extraction_queue = triage.get("extraction_queue", {})

    # Build work list
    all_work = []
    if args.type:
        types_to_process = [args.type]
    else:
        types_to_process = list(extraction_queue.keys())

    for article_type in types_to_process:
        for doi in extraction_queue.get(article_type, []):
            pdf_path = PDF_DIR / (doi.replace("/", "_") + ".pdf")
            if pdf_path.exists():
                all_work.append({"doi": doi, "type": article_type})

    print(f"Total papers available: {len(all_work)}")

    # Stagger start for parallel workers
    if args.worker:
        stagger = (args.worker - 1) * 3
        if stagger > 0:
            print(f"Staggering start by {stagger}s...")
            time.sleep(stagger)

    processed = 0
    total_cost = 0.0
    limit = args.limit or len(all_work)

    while processed < limit:
        # Claim a batch
        unclaimed_dois = [w["doi"] for w in all_work]
        claimed = claimer.claim_papers(unclaimed_dois, max_claims=min(3, limit - processed))

        if not claimed:
            print("No more papers to claim. Done.")
            break

        for doi in claimed:
            paper = next(w for w in all_work if w["doi"] == doi)

            processed += 1
            print(f"\n[{processed}/{limit}] {doi[:50]} ({paper['type']})")

            result = process_one(client, claimer, doi, paper["type"])

            total_cost += result.get("cost", 0)
            action_symbol = {"accept": "✓", "repair": "⚡", "requeue": "↻", "fail": "✗"}.get(result.get("action"), "?")
            print(f"  {action_symbol} {result.get('action', '?')} | {result.get('n_findings', 0)} findings | score={result.get('quality_score', '?')} | ${result.get('cost', 0):.4f}")

            if result.get("error"):
                print(f"  Error: {result['error'][:80]}")

            # Rate limit between papers
            if processed < limit:
                time.sleep(SECONDS_BETWEEN_REQUESTS)

    # Summary
    print(f"\n{'═'*60}")
    print(f"WORKER {args.worker or 0} COMPLETE")
    print(f"{'═'*60}")
    print(f"Processed: {processed}")
    print(f"Total cost: ${total_cost:.4f}")

    status = claimer.get_status()
    print(f"Global: {status['completed']} completed, {status['failed']} failed, {status['active_claims']} active")


def show_status():
    """Show global progress across all workers."""
    print("\n═══ EXTRACTION PROGRESS ═══\n")

    # Claims status
    if CLAIMS_FILE.exists():
        claims = json.loads(CLAIMS_FILE.read_text())
        print(f"Completed: {len(claims.get('completed', []))}")
        print(f"Failed:    {len(claims.get('failed', []))}")
        print(f"Active:    {len(claims.get('claims', {}))}")
        for doi, claim in claims.get("claims", {}).items():
            print(f"  → {doi[:40]}... by {claim['agent_id']}")
    else:
        print("No claims file yet.")

    # Progress stats
    if PROGRESS_FILE.exists():
        data = json.loads(PROGRESS_FILE.read_text())
        stats = data.get("stats", {})
        print(f"\nTotal processed: {stats.get('total_processed', 0)}")
        print(f"Accepted:        {stats.get('total_accepted', 0)}")
        print(f"Failed:          {stats.get('total_failed', 0)}")
        print(f"Total cost:      ${stats.get('total_cost', 0):.4f}")
        print(f"Last updated:    {stats.get('last_updated', 'never')}")

        # Show recent results
        results = data.get("results", [])
        if results:
            print(f"\nLast 5 results:")
            for r in results[-5:]:
                symbol = {"accept": "✓", "repair": "⚡", "fail": "✗"}.get(r.get("action"), "?")
                print(f"  {symbol} {r.get('doi', '?')[:40]} | {r.get('n_findings', 0)} findings | ${r.get('cost', 0):.4f}")


# ═══════════════════════════════════════════════════════════════════════════
# RECOVERY MODE
# ═══════════════════════════════════════════════════════════════════════════

def recover_failures():
    """
    Retry all failed papers with:
    - Robust JSON parsing (handles Extra data, truncation, malformed)
    - Higher max_output_tokens (131072 vs 65536)
    - Also tries to salvage raw_failures/ files from first run

    Auto-runs if estimated cost < $5. Otherwise shows cost-benefit analysis.
    """
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║  RECOVERY MODE — Retrying failed extractions                 ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    if not PROGRESS_FILE.exists():
        print("No progress file found. Run extraction first.")
        return

    progress = json.loads(PROGRESS_FILE.read_text())
    all_results = progress.get("results", [])

    # Find all failures
    failures = [r for r in all_results if r.get("action") == "fail"]
    print(f"\nTotal failures from first run: {len(failures)}")

    if not failures:
        print("No failures to recover!")
        return

    # Categorize
    from collections import Counter
    categories = Counter()
    json_parse = []
    api_retryable = []
    other = []

    for f in failures:
        err = f.get("error", "")
        if "JSON parse" in err or "robust_json_parse" in err:
            categories["JSON parse"] += 1
            json_parse.append(f)
        elif "503" in err or "UNAVAILABLE" in err or "429" in err:
            categories["API retryable (503/429)"] += 1
            api_retryable.append(f)
        elif "500" in err or "502" in err or "Connection" in err:
            categories["API retryable (500/502/conn)"] += 1
            api_retryable.append(f)
        elif "400" in err and "Upload" in err:
            categories["Upload error (400)"] += 1
            api_retryable.append(f)  # Worth a retry
        elif "not found" in err.lower():
            categories["PDF not found"] += 1
            # Don't retry — no PDF
        else:
            categories[f"Other"] += 1
            other.append(f)

    print("\n── Failure categories ──")
    for cat, count in categories.most_common():
        print(f"  {count:3d}  {cat}")

    # Build retry list (exclude PDF-not-found)
    retryable = json_parse + api_retryable + other
    retry_dois = list({f.get("doi") for f in retryable if f.get("doi")})
    print(f"\nRetryable papers: {len(retry_dois)}")

    # Step 1: Try salvaging existing raw_failures/ first (free!)
    salvaged = 0
    if RAW_FAILURES_DIR.exists():
        raw_files = list(RAW_FAILURES_DIR.glob("*.txt"))
        print(f"\n── Salvaging {len(raw_files)} raw failure files (no API cost) ──")
        for raw_file in raw_files:
            doi_safe = raw_file.stem
            doi = doi_safe.replace("_", "/", 1)  # Rough reverse
            raw_text = raw_file.read_text()
            result = robust_json_parse(raw_text)
            if result:
                from src.extraction.pipeline_repairs import normalize_extraction
                result = normalize_extraction(result)
                n_findings = len(result.get("findings", []))
                if n_findings > 0:
                    output_file = OUTPUT_DIR / f"{doi_safe}.json"
                    save_data = {
                        "doi": doi,
                        "quality_action": "salvaged",
                        "n_findings": n_findings,
                        "extracted_at": datetime.now(timezone.utc).isoformat(),
                        "recovery_source": "raw_failure_salvage",
                        **result,
                    }
                    output_file.write_text(json.dumps(save_data, indent=2))
                    salvaged += 1
                    print(f"  ✓ Salvaged {doi_safe[:40]} → {n_findings} findings")
                    # Remove from retry list
                    retry_dois = [d for d in retry_dois if d.replace("/", "_") != doi_safe]

        print(f"  Salvaged: {salvaged} papers (free!)")

    if not retry_dois:
        print("\nAll failures either salvaged or non-retryable. Done!")
        return

    # Cost estimate
    estimated_cost = len(retry_dois) * AVG_COST_PER_RETRY
    print(f"\n── Cost estimate for {len(retry_dois)} retries ──")
    print(f"  Avg cost/paper: ${AVG_COST_PER_RETRY:.4f}")
    print(f"  Estimated total: ${estimated_cost:.2f}")
    print(f"  Cost guardrail: ${COST_GUARDRAIL:.2f}")

    if estimated_cost > COST_GUARDRAIL:
        print(f"\n⚠️  COST EXCEEDS ${COST_GUARDRAIL:.2f} GUARDRAIL")
        print(f"\n── Cost-Benefit Analysis ──")
        print(f"  Papers to retry: {len(retry_dois)}")
        print(f"  Expected recovery rate: ~70% (based on error types)")
        print(f"  Expected new papers recovered: ~{int(len(retry_dois) * 0.7)}")
        print(f"  Cost per recovered paper: ~${estimated_cost / (len(retry_dois) * 0.7):.4f}")
        print(f"  Total estimated cost: ${estimated_cost:.2f}")
        print(f"\n  To override, run with: --recover --force")
        return

    print(f"\n  ✓ Under guardrail — proceeding automatically.")

    # Use WorkClaimer for parallel recovery
    RECOVERY_CLAIMS = OUTPUT_DIR / "recovery_claims.json"
    worker_id = os.environ.get("RECOVERY_WORKER_ID", f"r{os.getpid()}")
    claimer = WorkClaimer(RECOVERY_CLAIMS, worker_id)
    print(f"\nRecovery worker: {worker_id}")

    client = get_client()
    recovered = 0
    still_failed = 0
    total_cost = 0.0
    processed = 0

    while True:
        # Claim a batch of papers to retry
        claimed = claimer.claim_papers(retry_dois, max_claims=3)
        if not claimed:
            print("No more papers to claim. Done.")
            break

        for doi in claimed:
            processed += 1

            # Find PDF
            pdf_path = PDF_DIR / (doi.replace("/", "_") + ".pdf")
            if not pdf_path.exists():
                matching = list(PDF_DIR.glob(f"{doi.replace('/', '_')}*"))
                if matching:
                    pdf_path = matching[0]
                else:
                    claimer.release(doi, "failed")
                    still_failed += 1
                    continue

            print(f"\n[{processed}] Retrying: {doi[:50]}")

            # Classify
            try:
                classification = classify_paper(client, pdf_path)
                article_type = classification.get("article_type", "unknown")
                total_cost += classification.get("_cost", 0)
                time.sleep(SECONDS_BETWEEN_REQUESTS)
            except Exception as e:
                print(f"  ✗ Classification failed: {str(e)[:60]}")
                article_type = "unknown"

            # Extract with higher token limit + robust parsing
            extraction = extract_paper(
                client, pdf_path, article_type,
                max_output_tokens=RECOVERY_MAX_OUTPUT_TOKENS,
                doi=doi,
            )
            total_cost += extraction.get("cost", 0)

            if extraction.get("success"):
                quality = evaluate_quality(extraction["data"], article_type)
                doi_safe = doi.replace("/", "_")
                output_file = OUTPUT_DIR / f"{doi_safe}.json"

                save_data = {
                    "doi": doi,
                    "article_type": article_type,
                    "quality_action": quality["action"],
                    "quality_score": quality["score"],
                    "n_findings": extraction.get("n_findings", 0),
                    "extracted_at": datetime.now(timezone.utc).isoformat(),
                    "recovery_source": "retry_with_robust_parse",
                    "model": extraction.get("model"),
                    "cost": extraction.get("cost", 0),
                    **extraction["data"],
                }
                output_file.write_text(json.dumps(save_data, indent=2))

                claimer.release(doi, "completed")
                recovered += 1
                print(f"  ✓ RECOVERED | {extraction.get('n_findings', 0)} findings | score={quality['score']} | ${extraction.get('cost', 0):.4f}")

                update_progress(doi, {
                    "doi": doi,
                    "action": quality["action"],
                    "n_findings": extraction.get("n_findings", 0),
                    "cost": extraction.get("cost", 0),
                    "quality_score": quality["score"],
                    "recovery": True,
                })
            else:
                claimer.release(doi, "failed")
                still_failed += 1
                err = extraction.get("error", "unknown")[:60]
                print(f"  ✗ Still failed: {err}")

            time.sleep(SECONDS_BETWEEN_REQUESTS)

    # Summary
    print(f"\n{'═'*60}")
    print(f"RECOVERY WORKER {worker_id} COMPLETE")
    print(f"{'═'*60}")
    print(f"Salvaged (free):    {salvaged}")
    print(f"Recovered (retry):  {recovered}")
    print(f"Still failed:       {still_failed}")
    print(f"Recovery cost:      ${total_cost:.4f}")

    status = claimer.get_status()
    print(f"Global: {status['completed']} recovered, {status['failed']} still failed")


def main():
    parser = argparse.ArgumentParser(description="Parallel PDF extraction with revised prompts")
    parser.add_argument("--worker", type=int, help="Worker ID (1, 2, 3, ...) for parallel execution")
    parser.add_argument("--limit", type=int, default=10, help="Max papers to process (default: 10)")
    parser.add_argument("--type", choices=["empirical", "meta_analysis", "systematic_review",
                                           "narrative_review", "theoretical", "qualitative",
                                           "methods", "unknown"],
                        help="Process only this article type")
    parser.add_argument("--status", action="store_true", help="Show progress across all workers")
    parser.add_argument("--reset", action="store_true", help="Reset claims + progress (fresh start)")
    parser.add_argument("--recover", action="store_true", help="Retry all failed papers with robust parsing")
    parser.add_argument("--force", action="store_true", help="Override cost guardrail for --recover")
    args = parser.parse_args()

    if args.status:
        show_status()
        return

    if args.reset:
        for f in [CLAIMS_FILE, PROGRESS_FILE, CLAIMS_FILE.with_suffix(".lock"), PROGRESS_FILE.with_suffix(".lock")]:
            if f.exists():
                f.unlink()
                print(f"Removed {f.name}")
        print("Reset complete.")
        return

    if args.recover:
        if args.force:
            global COST_GUARDRAIL
            COST_GUARDRAIL = float('inf')
        recover_failures()
        return

    worker_loop(args)


if __name__ == "__main__":
    main()
