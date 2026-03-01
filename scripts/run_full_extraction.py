#!/usr/bin/env python3
"""Run full extraction on all paper types using gemini-2.5-flash.

Usage:
    python scripts/run_full_extraction.py
    python scripts/run_full_extraction.py --no-verify  # Skip 2-run verification
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from google import genai
from google.genai import types

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.gemini_extraction_queue import (
    PROMPT_MAP,
    PRICING,
    ExtractionStatus,
    QueueItem,
    compare_extractions,
    merge_extractions,
)

# Paths
AF_ROOT = Path("/Users/davidusa/REPOS/Article_Finder_v3_2_3")
PDF_DIR = AF_ROOT / "data" / "pdfs"
TRIAGE_FILE = PROJECT_ROOT / "data" / "triage" / "keyword_triage.json"
OUTPUT_DIR = PROJECT_ROOT / "data" / "extractions"

MODEL = "gemini-2.5-flash"


def get_client() -> genai.Client:
    """Get configured Gemini client."""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Set GOOGLE_API_KEY or GEMINI_API_KEY")
        sys.exit(1)
    return genai.Client(api_key=api_key)


def extract_paper(client: genai.Client, pdf_path: Path, article_type: str) -> dict:
    """Run extraction on a single paper."""
    start = time.time()

    if not pdf_path.exists():
        return {"success": False, "error": f"PDF not found: {pdf_path}"}

    prompt = PROMPT_MAP.get(article_type, PROMPT_MAP["unknown"])

    try:
        # Upload PDF
        with open(pdf_path, "rb") as f:
            uploaded = client.files.upload(file=f, config={"mime_type": "application/pdf"})

        # Wait for processing
        while uploaded.state.name == "PROCESSING":
            time.sleep(1)
            uploaded = client.files.get(name=uploaded.name)

        if uploaded.state.name == "FAILED":
            return {"success": False, "error": "Upload failed"}

        # Generate
        response = client.models.generate_content(
            model=MODEL,
            contents=[
                types.Part.from_uri(file_uri=uploaded.uri, mime_type="application/pdf"),
                prompt,
            ],
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=65536,
            ),
        )

        elapsed = time.time() - start

        # Parse JSON
        text = response.text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

        result = json.loads(text)

        # Calculate cost
        usage = {}
        cost = 0.0
        if response.usage_metadata:
            m = response.usage_metadata
            pricing = PRICING.get(MODEL, PRICING["gemini-2.5-flash"])
            cost = (m.prompt_token_count * pricing["input"] + m.candidates_token_count * pricing["output"]) / 1_000_000
            usage = {
                "input_tokens": m.prompt_token_count,
                "output_tokens": m.candidates_token_count,
                "cost_usd": round(cost, 6),
            }

        # Cleanup
        try:
            client.files.delete(name=uploaded.name)
        except Exception:
            pass

        return {
            "success": True,
            "data": result,
            "usage": usage,
            "elapsed": round(elapsed, 1),
            "model": MODEL,
        }

    except json.JSONDecodeError as e:
        return {"success": False, "error": f"JSON parse: {e}", "raw": text[:500] if "text" in dir() else None}
    except Exception as e:
        return {"success": False, "error": str(e)}


def process_paper(client: genai.Client, doi: str, article_type: str, pdf_path: Path, verify: bool = True) -> dict:
    """Process a single paper with optional verification."""
    result = {
        "doi": doi,
        "article_type": article_type,
        "status": "pending",
        "run1": None,
        "run2": None,
        "final_result": None,
        "total_cost": 0.0,
        "error": None,
    }

    # Run 1
    run1 = extract_paper(client, pdf_path, article_type)
    result["run1"] = {"success": run1.get("success"), "n_findings": len(run1.get("data", {}).get("findings", run1.get("data", {}).get("pooled_effects", run1.get("data", {}).get("themes", run1.get("data", {}).get("propositions", run1.get("data", {}).get("key_claims", []))))))}
    result["total_cost"] += run1.get("usage", {}).get("cost_usd", 0)

    if not run1.get("success"):
        result["status"] = "failed"
        result["error"] = run1.get("error")
        return result

    if not verify:
        result["final_result"] = run1.get("data")
        result["status"] = "completed"
        return result

    # Run 2 for verification
    time.sleep(1)
    run2 = extract_paper(client, pdf_path, article_type)
    result["run2"] = {"success": run2.get("success"), "n_findings": len(run2.get("data", {}).get("findings", run2.get("data", {}).get("pooled_effects", run2.get("data", {}).get("themes", run2.get("data", {}).get("propositions", run2.get("data", {}).get("key_claims", []))))))}
    result["total_cost"] += run2.get("usage", {}).get("cost_usd", 0)

    if not run2.get("success"):
        # Use run1 if run2 failed
        result["final_result"] = run1.get("data")
        result["status"] = "completed"
        return result

    # Compare and merge
    comparison = compare_extractions(run1, run2)
    result["agreement_rate"] = comparison.get("agreement_rate", 0)

    # Merge results
    result["final_result"] = merge_extractions(run1, run2)
    result["status"] = "completed"

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-verify", action="store_true", help="Skip 2-run verification (faster, cheaper)")
    parser.add_argument("--limit", type=int, default=0, help="Limit total papers (0 = no limit)")
    args = parser.parse_args()

    print("=" * 70)
    print("FULL EXTRACTION: gemini-2.5-flash")
    print(f"Verification: {'disabled' if args.no_verify else 'enabled (2-run)'}")
    print("=" * 70)

    # Load triage
    with open(TRIAGE_FILE) as f:
        triage = json.load(f)

    queue = triage.get("extraction_queue", {})

    # Load already extracted
    extracted_dois = set()
    for f in OUTPUT_DIR.glob("*.json"):
        if "queue_state" in f.name or "scored" in f.name or "comparison" in f.name:
            continue
        with open(f) as fp:
            data = json.load(fp)
            if isinstance(data, list):
                for item in data:
                    if "doi" in item:
                        extracted_dois.add(item["doi"])
            elif isinstance(data, dict) and "results" in data:
                for item in data["results"]:
                    if "doi" in item:
                        extracted_dois.add(item["doi"])

    # Build work list
    work = []
    for article_type in ["empirical", "meta_analysis", "systematic_review", "narrative_review", "theoretical", "qualitative", "methods", "unknown"]:
        dois = queue.get(article_type, [])
        for doi in dois:
            if doi in extracted_dois:
                continue
            pdf_path = PDF_DIR / (doi.replace("/", "_") + ".pdf")
            if pdf_path.exists():
                work.append({"doi": doi, "article_type": article_type, "pdf_path": pdf_path})

    if args.limit > 0:
        work = work[:args.limit]

    print(f"\nPapers to process: {len(work)}")
    if not work:
        print("No papers to process.")
        return

    # Count by type
    by_type = {}
    for w in work:
        by_type[w["article_type"]] = by_type.get(w["article_type"], 0) + 1
    for t, c in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {t}: {c}")

    # Initialize client
    client = get_client()

    # Process
    results = []
    total_cost = 0.0
    completed = 0
    failed = 0
    start_time = time.time()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"full_extraction_{timestamp}.json"

    for i, paper in enumerate(work):
        elapsed = time.time() - start_time
        rate = (i + 1) / elapsed if elapsed > 0 else 0
        eta = (len(work) - i - 1) / rate if rate > 0 else 0

        print(f"\n[{i+1}/{len(work)}] {paper['doi'][:50]} ({paper['article_type']})")
        print(f"  Progress: {completed} completed, {failed} failed, ${total_cost:.2f} spent")
        print(f"  ETA: {eta/60:.0f} min remaining")

        try:
            result = process_paper(
                client,
                paper["doi"],
                paper["article_type"],
                paper["pdf_path"],
                verify=not args.no_verify,
            )

            if result["status"] == "completed":
                completed += 1
                n_findings = len(result.get("final_result", {}).get("findings", result.get("final_result", {}).get("pooled_effects", result.get("final_result", {}).get("themes", result.get("final_result", {}).get("propositions", result.get("final_result", {}).get("key_claims", []))))))
                print(f"  ✓ {n_findings} findings, ${result['total_cost']:.4f}")
            else:
                failed += 1
                print(f"  ✗ Failed: {result.get('error', 'unknown')[:50]}")

            total_cost += result["total_cost"]
            results.append(result)

        except Exception as e:
            failed += 1
            print(f"  ✗ Exception: {str(e)[:50]}")
            results.append({
                "doi": paper["doi"],
                "article_type": paper["article_type"],
                "status": "failed",
                "error": str(e),
                "total_cost": 0,
            })

        # Save incrementally every 10 papers
        if (i + 1) % 10 == 0:
            with open(output_file, "w") as f:
                json.dump({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "model": MODEL,
                    "verification": not args.no_verify,
                    "total_cost": round(total_cost, 4),
                    "completed": completed,
                    "failed": failed,
                    "results": results,
                }, f, indent=2)
            print(f"  [Saved checkpoint: {output_file.name}]")

        # Brief pause between papers
        time.sleep(1)

    # Final save
    elapsed_total = time.time() - start_time
    with open(output_file, "w") as f:
        json.dump({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": MODEL,
            "verification": not args.no_verify,
            "total_cost": round(total_cost, 4),
            "completed": completed,
            "failed": failed,
            "elapsed_minutes": round(elapsed_total / 60, 1),
            "results": results,
        }, f, indent=2)

    # Summary
    print("\n" + "=" * 70)
    print("EXTRACTION COMPLETE")
    print("=" * 70)
    print(f"Total papers: {len(work)}")
    print(f"Completed: {completed}")
    print(f"Failed: {failed}")
    print(f"Total cost: ${total_cost:.2f}")
    print(f"Time: {elapsed_total/60:.1f} minutes")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()
