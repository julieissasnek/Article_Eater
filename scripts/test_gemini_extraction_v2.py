#!/usr/bin/env python3
"""Test Gemini Extraction using new google.genai package.

Usage:
    python scripts/test_gemini_extraction_v2.py --doi "10.1002/adfm.202008831"
    python scripts/test_gemini_extraction_v2.py --all --save
    python scripts/test_gemini_extraction_v2.py --all --model gemini-2.5-flash --save
    python scripts/test_gemini_extraction_v2.py --doi "10.1002/adfm.202008831" --model gemini-3.1-pro-preview
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

PROBLEM_PAPERS = [
    {"doi": "10.1002/adfm.202008831", "desc": "Haptic tech review - 100% garbled", "pdf": "10.1002_adfm.202008831.pdf"},
    {"doi": "10.1002/cne.920180503", "desc": "Neuroscience - 227 rows garbled", "pdf": "10.1002_cne.920180503.pdf"},
    {"doi": "10.1006/jevp.2000.0186", "desc": "Env psychology - 100% garbled", "pdf": "10.1006_jevp.2000.0186.pdf"},
    {"doi": "10.1016/j.buildenv.2018.04.029", "desc": "Building env - 87% garbled", "pdf": "10.1016_j.buildenv.2018.04.029.pdf"},
    {"doi": "10.1007/s00226-021-01320-7", "desc": "Wood science - 99% garbled", "pdf": "10.1007_s00226-021-01320-7.pdf"},
]

PDF_BASE = Path("/Users/davidusa/REPOS/Article_Finder_v3_2_3/data/pdfs")
OUTPUT_DIR = PROJECT_ROOT / "data" / "extraction_tests"

# Pricing per 1M tokens (estimated for preview models)
PRICING = {
    "gemini-2.5-pro": {"input": 1.25, "output": 10.00},
    "gemini-2.5-flash": {"input": 0.15, "output": 0.60},
    "gemini-3-pro-preview": {"input": 1.50, "output": 12.00},  # estimated
    "gemini-3.1-pro-preview": {"input": 1.50, "output": 12.00},  # estimated
}

AVAILABLE_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-3-pro-preview",
    "gemini-3.1-pro-preview",
]

EXTRACTION_PROMPT = """Extract all statistical results and causal claims from this scientific paper.

For each results table, extract:
- Table ID and caption
- Statistical test type (ANOVA, regression, t-test, correlation, etc.)
- Key statistics (means, F-values, t-values, r, p-values, effect sizes)
- Sample sizes

Return JSON:
{
  "tables": [
    {
      "table_id": "Table 1",
      "caption": "...",
      "test_type": "ANOVA/regression/correlation/t-test/descriptive",
      "statistics": [{"variable": "...", "stat": "...", "p": "...", "effect": "..."}]
    }
  ],
  "causal_claims": [
    {
      "independent_variable": "...",
      "dependent_variable": "...",
      "direction": "increase|decrease|no_effect",
      "effect_size": "...",
      "p_value": "...",
      "sample_size": "...",
      "source_table": "Table X"
    }
  ],
  "extraction_notes": "Any issues or observations"
}

Focus on RESULTS tables, not methods or protocol tables."""


def get_client() -> genai.Client:
    """Get configured Gemini client."""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Set GOOGLE_API_KEY or GEMINI_API_KEY")
        sys.exit(1)
    return genai.Client(api_key=api_key)


def extract_paper(client: genai.Client, pdf_path: Path, model: str = "gemini-2.5-flash") -> dict:
    """Extract from a single paper using new genai API."""
    start = time.time()
    pdf_size_mb = pdf_path.stat().st_size / (1024 * 1024)

    print(f"  Uploading {pdf_size_mb:.1f}MB...")

    try:
        # Upload file
        with open(pdf_path, "rb") as f:
            uploaded = client.files.upload(file=f, config={"mime_type": "application/pdf"})

        # Wait for processing
        while uploaded.state.name == "PROCESSING":
            time.sleep(2)
            uploaded = client.files.get(name=uploaded.name)

        if uploaded.state.name == "FAILED":
            return {"success": False, "error": "Upload failed", "elapsed": time.time() - start}

        print(f"  Generating with {model}...")

        # Generate content
        response = client.models.generate_content(
            model=model,
            contents=[
                types.Part.from_uri(file_uri=uploaded.uri, mime_type="application/pdf"),
                EXTRACTION_PROMPT,
            ],
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=65536,  # Increased for papers with many tables
            ),
        )

        elapsed = time.time() - start

        # Extract usage
        usage = {}
        if response.usage_metadata:
            m = response.usage_metadata
            usage = {
                "input_tokens": m.prompt_token_count,
                "output_tokens": m.candidates_token_count,
            }
            pricing = PRICING.get(model, PRICING["gemini-2.5-flash"])
            usage["cost_usd"] = round(
                (m.prompt_token_count * pricing["input"] + m.candidates_token_count * pricing["output"]) / 1_000_000,
                4,
            )

        # Cleanup
        try:
            client.files.delete(name=uploaded.name)
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

        return {
            "success": True,
            "text": response.text,
            "usage": usage,
            "elapsed": round(elapsed, 1),
            "pdf_size_mb": round(pdf_size_mb, 2),
        }

    except Exception as e:
        return {"success": False, "error": str(e), "elapsed": time.time() - start}


def parse_response(text: str) -> dict:
    """Parse JSON from response."""
    try:
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]

        data = json.loads(text.strip())
        return {
            "parsed": True,
            "tables": data.get("tables", []),
            "claims": data.get("causal_claims", []),
            "notes": data.get("extraction_notes", ""),
        }
    except json.JSONDecodeError as e:
        return {"parsed": False, "error": str(e), "preview": text[:500]}


def test_paper(client: genai.Client, doi: str, model: str) -> dict:
    """Test extraction on a single paper."""
    paper = next((p for p in PROBLEM_PAPERS if p["doi"] == doi), None)
    if not paper:
        pdf_name = doi.replace("/", "_") + ".pdf"
        paper = {"doi": doi, "desc": "Custom", "pdf": pdf_name}

    pdf_path = PDF_BASE / paper["pdf"]
    if not pdf_path.exists():
        return {"doi": doi, "error": f"PDF not found: {pdf_path}"}

    print(f"\n{'='*60}")
    print(f"DOI: {doi}")
    print(f"Description: {paper['desc']}")
    print(f"{'='*60}")

    result = extract_paper(client, pdf_path, model)

    if result["success"]:
        parsed = parse_response(result["text"])
        print(f"  Elapsed: {result['elapsed']}s")
        print(f"  Tokens: {result['usage'].get('input_tokens', 0):,} in, {result['usage'].get('output_tokens', 0):,} out")
        print(f"  Cost: ${result['usage'].get('cost_usd', 0):.4f}")

        if parsed["parsed"]:
            print(f"  Tables: {len(parsed['tables'])}")
            print(f"  Claims: {len(parsed['claims'])}")
            for c in parsed["claims"][:2]:
                print(f"    - {c.get('independent_variable', '?')} -> {c.get('dependent_variable', '?')}")
        else:
            print(f"  Parse error: {parsed['error']}")

        return {
            "doi": doi,
            "model": model,
            "result": result,
            "parsed": parsed,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    else:
        print(f"  ERROR: {result['error']}")
        return {"doi": doi, "model": model, "error": result["error"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--doi", help="DOI to test")
    parser.add_argument("--all", action="store_true", help="Test all problem papers")
    parser.add_argument("--model", default="gemini-2.5-flash", choices=AVAILABLE_MODELS)
    parser.add_argument("--save", action="store_true", help="Save results")
    parser.add_argument("--list", action="store_true", help="List papers")
    args = parser.parse_args()

    if args.list:
        for p in PROBLEM_PAPERS:
            exists = "OK" if (PDF_BASE / p["pdf"]).exists() else "MISSING"
            print(f"[{exists}] {p['doi']}: {p['desc']}")
        return

    if not args.doi and not args.all:
        parser.print_help()
        return

    client = get_client()
    results = []
    total_cost = 0.0

    if args.all:
        for paper in PROBLEM_PAPERS:
            r = test_paper(client, paper["doi"], args.model)
            results.append(r)
            if "result" in r:
                total_cost += r["result"]["usage"].get("cost_usd", 0)
    else:
        r = test_paper(client, args.doi, args.model)
        results.append(r)
        if "result" in r:
            total_cost += r["result"]["usage"].get("cost_usd", 0)

    print(f"\n{'='*60}")
    print(f"TOTAL COST: ${total_cost:.4f}")
    print(f"{'='*60}")

    if args.save:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_file = OUTPUT_DIR / f"gemini_v2_{args.model.split('-')[-1]}_{ts}.json"
        with open(out_file, "w") as f:
            json.dump({"model": args.model, "total_cost": total_cost, "results": results}, f, indent=2, default=str)
        print(f"Saved: {out_file}")


if __name__ == "__main__":
    main()
