#!/usr/bin/env python3
"""Compare gemini-2.5-flash vs gemini-2.5-pro on extraction quality.

Runs both models on the same papers and compares:
- Number of findings extracted
- Direction agreement
- Effect size capture
- Cost per paper

Usage:
    python scripts/compare_models.py --limit 5
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
    EMPIRICAL_PROMPT,
    PDF_DIR,
    PRICING,
    load_triage,
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "model_comparison"


def extract_with_model(client: genai.Client, pdf_path: Path, model: str) -> dict:
    """Run extraction with specified model."""
    start = time.time()

    if not pdf_path.exists():
        return {"success": False, "error": f"PDF not found: {pdf_path}"}

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
            model=model,
            contents=[
                types.Part.from_uri(file_uri=uploaded.uri, mime_type="application/pdf"),
                EMPIRICAL_PROMPT,
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
            pricing = PRICING.get(model, PRICING["gemini-2.5-flash"])
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
            "model": model,
        }

    except json.JSONDecodeError as e:
        return {"success": False, "error": f"JSON parse: {e}", "raw": text[:500] if "text" in dir() else None}
    except Exception as e:
        return {"success": False, "error": str(e)}


def compare_results(flash_result: dict, pro_result: dict) -> dict:
    """Compare extraction results between models."""
    if not flash_result.get("success") or not pro_result.get("success"):
        return {
            "comparable": False,
            "flash_success": flash_result.get("success"),
            "pro_success": pro_result.get("success"),
        }

    flash_data = flash_result.get("data", {})
    pro_data = pro_result.get("data", {})

    flash_findings = flash_data.get("findings", [])
    pro_findings = pro_data.get("findings", [])

    # Count findings
    n_flash = len(flash_findings)
    n_pro = len(pro_findings)

    # Count findings with effect sizes
    flash_with_es = sum(1 for f in flash_findings if f.get("effect_size") is not None)
    pro_with_es = sum(1 for f in pro_findings if f.get("effect_size") is not None)

    # Count findings with p-values
    flash_with_p = sum(1 for f in flash_findings if f.get("p_value") is not None)
    pro_with_p = sum(1 for f in pro_findings if f.get("p_value") is not None)

    # Count by direction
    flash_directions = {}
    pro_directions = {}
    for f in flash_findings:
        d = f.get("direction", "unknown")
        flash_directions[d] = flash_directions.get(d, 0) + 1
    for f in pro_findings:
        d = f.get("direction", "unknown")
        pro_directions[d] = pro_directions.get(d, 0) + 1

    # Cost comparison
    flash_cost = flash_result.get("usage", {}).get("cost_usd", 0)
    pro_cost = pro_result.get("usage", {}).get("cost_usd", 0)

    return {
        "comparable": True,
        "n_findings": {"flash": n_flash, "pro": n_pro, "diff": n_pro - n_flash},
        "with_effect_size": {"flash": flash_with_es, "pro": pro_with_es},
        "with_p_value": {"flash": flash_with_p, "pro": pro_with_p},
        "directions": {"flash": flash_directions, "pro": pro_directions},
        "cost_usd": {"flash": flash_cost, "pro": pro_cost, "ratio": round(pro_cost / flash_cost, 1) if flash_cost > 0 else 0},
        "elapsed_sec": {"flash": flash_result.get("elapsed", 0), "pro": pro_result.get("elapsed", 0)},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5, help="Number of papers to compare")
    args = parser.parse_args()

    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Set GOOGLE_API_KEY or GEMINI_API_KEY")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    # Load triage and get unextracted empirical papers
    triage = load_triage()
    extraction_queue = triage.get("extraction_queue", {})
    empirical_dois = extraction_queue.get("empirical", [])

    # Load already extracted DOIs
    extracted_dois = set()
    for f in (PROJECT_ROOT / "data" / "extractions").glob("*.json"):
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

    # Get unextracted papers with PDFs
    papers_to_test = []
    for doi in empirical_dois:
        if doi in extracted_dois:
            continue
        pdf_path = PDF_DIR / (doi.replace("/", "_") + ".pdf")
        if pdf_path.exists():
            papers_to_test.append({"doi": doi, "pdf_path": pdf_path})
        if len(papers_to_test) >= args.limit:
            break

    if not papers_to_test:
        print("No unextracted papers with PDFs found")
        sys.exit(1)

    print(f"Comparing gemini-2.5-flash vs gemini-2.5-pro on {len(papers_to_test)} papers")
    print("=" * 70)

    results = []
    totals = {
        "flash": {"findings": 0, "effect_sizes": 0, "p_values": 0, "cost": 0, "time": 0},
        "pro": {"findings": 0, "effect_sizes": 0, "p_values": 0, "cost": 0, "time": 0},
    }

    for i, paper in enumerate(papers_to_test):
        print(f"\n[{i+1}/{len(papers_to_test)}] {paper['doi'][:50]}...")

        # Run flash
        print("  Running gemini-2.5-flash...")
        flash_result = extract_with_model(client, paper["pdf_path"], "gemini-2.5-flash")
        flash_n = len(flash_result.get("data", {}).get("findings", [])) if flash_result.get("success") else 0
        print(f"    → {flash_n} findings, ${flash_result.get('usage', {}).get('cost_usd', 0):.4f}")

        time.sleep(2)  # Brief pause between API calls

        # Run pro
        print("  Running gemini-2.5-pro...")
        pro_result = extract_with_model(client, paper["pdf_path"], "gemini-2.5-pro")
        pro_n = len(pro_result.get("data", {}).get("findings", [])) if pro_result.get("success") else 0
        print(f"    → {pro_n} findings, ${pro_result.get('usage', {}).get('cost_usd', 0):.4f}")

        # Compare
        comparison = compare_results(flash_result, pro_result)

        if comparison.get("comparable"):
            totals["flash"]["findings"] += comparison["n_findings"]["flash"]
            totals["pro"]["findings"] += comparison["n_findings"]["pro"]
            totals["flash"]["effect_sizes"] += comparison["with_effect_size"]["flash"]
            totals["pro"]["effect_sizes"] += comparison["with_effect_size"]["pro"]
            totals["flash"]["p_values"] += comparison["with_p_value"]["flash"]
            totals["pro"]["p_values"] += comparison["with_p_value"]["pro"]
            totals["flash"]["cost"] += comparison["cost_usd"]["flash"]
            totals["pro"]["cost"] += comparison["cost_usd"]["pro"]
            totals["flash"]["time"] += comparison["elapsed_sec"]["flash"]
            totals["pro"]["time"] += comparison["elapsed_sec"]["pro"]

        results.append({
            "doi": paper["doi"],
            "flash": flash_result,
            "pro": pro_result,
            "comparison": comparison,
        })

        time.sleep(2)  # Pause between papers

    # Summary
    print("\n" + "=" * 70)
    print("COMPARISON SUMMARY")
    print("=" * 70)

    print(f"\n{'Metric':<25} {'Flash':>12} {'Pro':>12} {'Diff':>12}")
    print("-" * 65)
    print(f"{'Total findings':<25} {totals['flash']['findings']:>12} {totals['pro']['findings']:>12} {totals['pro']['findings'] - totals['flash']['findings']:>+12}")
    print(f"{'With effect sizes':<25} {totals['flash']['effect_sizes']:>12} {totals['pro']['effect_sizes']:>12} {totals['pro']['effect_sizes'] - totals['flash']['effect_sizes']:>+12}")
    print(f"{'With p-values':<25} {totals['flash']['p_values']:>12} {totals['pro']['p_values']:>12} {totals['pro']['p_values'] - totals['flash']['p_values']:>+12}")
    print(f"{'Total cost ($)':<25} {totals['flash']['cost']:>12.4f} {totals['pro']['cost']:>12.4f} {totals['pro']['cost'] - totals['flash']['cost']:>+12.4f}")
    print(f"{'Total time (s)':<25} {totals['flash']['time']:>12.1f} {totals['pro']['time']:>12.1f} {totals['pro']['time'] - totals['flash']['time']:>+12.1f}")

    if totals["flash"]["cost"] > 0:
        print(f"\nPro costs {totals['pro']['cost'] / totals['flash']['cost']:.1f}x more than Flash")

    if totals["flash"]["findings"] > 0:
        print(f"Pro extracts {(totals['pro']['findings'] / totals['flash']['findings'] - 1) * 100:+.1f}% more findings")

    # Save detailed results
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "n_papers": len(papers_to_test),
            "totals": totals,
            "results": results,
        }, f, indent=2)

    print(f"\nDetailed results saved to: {output_file}")


if __name__ == "__main__":
    main()
