#!/usr/bin/env python3
"""Test Gemini 2.5 Pro Vision Extraction vs. Legacy Pipeline.

This script tests Gemini 2.5 Pro's ability to extract table data from PDFs
that the legacy extraction pipeline failed on (100% garbled rate).

Usage:
    # Test single paper
    python scripts/test_gemini_extraction.py --doi "10.1002/adfm.202008831"

    # Test all problem papers
    python scripts/test_gemini_extraction.py --all

    # Test with specific page range
    python scripts/test_gemini_extraction.py --doi "10.1002/adfm.202008831" --pages 1-5

Requirements:
    - GOOGLE_API_KEY or GEMINI_API_KEY environment variable
    - google-generativeai package
    - PDF files in Article_Finder_v3_2_3/data/pdfs/
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Problem papers with 100% extraction failure
PROBLEM_PAPERS = [
    {
        "doi": "10.1002/adfm.202008831",
        "description": "Haptic technologies review - 15 table rows, 100% garbled",
        "pdf": "10.1002_adfm.202008831.pdf",
    },
    {
        "doi": "10.1002/cne.920180503",
        "description": "Neuroscience paper - 227 table rows, 100% garbled",
        "pdf": "10.1002_cne.920180503.pdf",
    },
    {
        "doi": "10.1006/jevp.2000.0186",
        "description": "Environmental psychology - 24 table rows, 100% garbled",
        "pdf": "10.1006_jevp.2000.0186.pdf",
    },
    {
        "doi": "10.1016/j.buildenv.2018.04.029",
        "description": "Building environment - 206 table rows, 87% garbled",
        "pdf": "10.1016_j.buildenv.2018.04.029.pdf",
    },
    {
        "doi": "10.1007/s00226-021-01320-7",
        "description": "Wood science - 86 table rows, 99% garbled",
        "pdf": "10.1007_s00226-021-01320-7.pdf",
    },
]

PDF_BASE_PATH = Path("/Users/davidusa/REPOS/Article_Finder_v3_2_3/data/pdfs")
CACHE_PATH = PROJECT_ROOT / "data" / "production" / "pdf_preprocess_cache"
OUTPUT_PATH = PROJECT_ROOT / "data" / "extraction_tests"


def get_api_key() -> str:
    """Get Gemini API key from environment."""
    key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not key:
        print("ERROR: Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
        sys.exit(1)
    return key


def load_pdf_as_base64(pdf_path: Path) -> str:
    """Load PDF file and encode as base64."""
    with open(pdf_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def load_cached_extraction(doi: str) -> dict | None:
    """Load the cached (failed) extraction for comparison."""
    # Convert DOI to cache path
    prefix = doi.split("/")[0]
    suffix = doi.split("/", 1)[1]
    cache_file = CACHE_PATH / f"doi:{prefix}" / f"{suffix}.json"

    if cache_file.exists():
        with open(cache_file) as f:
            return json.load(f)
    return None


def extract_with_gemini(
    pdf_path: Path,
    api_key: str,
    model: str = "gemini-2.5-pro",
    pages: tuple[int, int] | None = None,
) -> dict:
    """Extract table data from PDF using Gemini Vision."""
    import google.generativeai as genai
    import time

    genai.configure(api_key=api_key)

    pdf_size_mb = pdf_path.stat().st_size / (1024 * 1024)

    # Build prompt for table extraction
    prompt = """Analyze this scientific paper PDF and extract ALL tables with their data.

For each table found, provide:
1. Table number/identifier
2. Table caption/title
3. Column headers
4. All data rows (preserve exact values, statistics, p-values)
5. Any notes or footnotes

Focus especially on:
- Results tables with statistics (ANOVA, regression, t-tests, correlations)
- Tables with effect sizes, sample sizes, p-values
- Any causal claims or relationships between variables

Return the extraction as JSON with this structure:
{
  "tables": [
    {
      "table_id": "Table 1",
      "caption": "...",
      "headers": ["col1", "col2", ...],
      "rows": [
        ["val1", "val2", ...],
        ...
      ],
      "statistics_found": ["p < 0.05", "r = 0.42", ...],
      "notes": "..."
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
  "extraction_notes": "Any issues or observations about the extraction"
}

Be thorough - extract ALL tables, even if partially visible or complex."""

    # Create model
    model_instance = genai.GenerativeModel(model)

    print(f"  Uploading PDF to Gemini File API ({pdf_size_mb:.1f} MB)...")

    try:
        # Use File API for reliable upload (especially for large files)
        uploaded_file = genai.upload_file(pdf_path, mime_type="application/pdf")

        # Wait for file to be ready
        while uploaded_file.state.name == "PROCESSING":
            print("  Waiting for file processing...")
            time.sleep(2)
            uploaded_file = genai.get_file(uploaded_file.name)

        if uploaded_file.state.name == "FAILED":
            return {
                "success": False,
                "error": f"File upload failed: {uploaded_file.state.name}",
                "model": model,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "pdf_size_mb": round(pdf_size_mb, 2),
            }

        print(f"  File ready, generating content...")

        # Generate content with uploaded file
        response = model_instance.generate_content(
            [uploaded_file, prompt],
            generation_config={
                "temperature": 0.1,  # Low temperature for factual extraction
                "max_output_tokens": 16384,  # Increased for large tables
            },
            request_options={"timeout": 600},  # 10 minute timeout for large PDFs
        )

        # Clean up uploaded file
        try:
            genai.delete_file(uploaded_file.name)
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")  # Ignore cleanup errors

        # Extract token usage if available
        usage = {}
        if hasattr(response, 'usage_metadata'):
            meta = response.usage_metadata
            usage = {
                "prompt_tokens": getattr(meta, 'prompt_token_count', 0),
                "output_tokens": getattr(meta, 'candidates_token_count', 0),
                "total_tokens": getattr(meta, 'total_token_count', 0),
            }
            # Calculate cost (Gemini 2.5 Pro pricing)
            input_cost = usage["prompt_tokens"] * 1.25 / 1_000_000
            output_cost = usage["output_tokens"] * 10.00 / 1_000_000
            usage["cost_usd"] = round(input_cost + output_cost, 4)

        return {
            "success": True,
            "raw_response": response.text,
            "model": model,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "usage": usage,
            "pdf_size_mb": round(pdf_size_mb, 2),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "model": model,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "pdf_size_mb": round(pdf_size_mb, 2),
        }


def parse_gemini_response(response: dict) -> dict:
    """Parse Gemini's response and extract structured data."""
    if not response.get("success"):
        return {"parsed": False, "error": response.get("error")}

    raw = response.get("raw_response", "")

    # Try to extract JSON from response
    try:
        # Look for JSON block in response
        if "```json" in raw:
            json_str = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            json_str = raw.split("```")[1].split("```")[0].strip()
        elif raw.strip().startswith("{"):
            json_str = raw.strip()
        else:
            return {
                "parsed": False,
                "error": "No JSON found in response",
                "raw_preview": raw[:500],
            }

        data = json.loads(json_str)
        return {
            "parsed": True,
            "tables": data.get("tables", []),
            "causal_claims": data.get("causal_claims", []),
            "extraction_notes": data.get("extraction_notes", ""),
        }

    except json.JSONDecodeError as e:
        # Try to salvage partial JSON by finding complete tables
        tables = []
        claims = []

        # Extract complete table objects using regex
        import re
        table_pattern = r'\{\s*"table_id"[^}]+\}(?=\s*[,\]])'
        for match in re.finditer(table_pattern, json_str, re.DOTALL):
            try:
                # Try to parse each table individually
                table_str = match.group(0)
                # This is simplified - real tables have nested arrays
                pass
            except Exception as e:
                import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

        # Try truncating to last complete object
        for end_char in ['}]', '}\n]', '},\n', '}']:
            last_complete = json_str.rfind(end_char)
            if last_complete > 0:
                try:
                    # Try to close the JSON properly
                    truncated = json_str[:last_complete + len(end_char)]
                    # Add closing brackets if needed
                    open_braces = truncated.count('{') - truncated.count('}')
                    open_brackets = truncated.count('[') - truncated.count(']')
                    truncated += '}' * open_braces + ']' * open_brackets

                    data = json.loads(truncated)
                    return {
                        "parsed": True,
                        "tables": data.get("tables", []),
                        "causal_claims": data.get("causal_claims", []),
                        "extraction_notes": data.get("extraction_notes", ""),
                        "truncated": True,
                    }
                except json.JSONDecodeError:
                    continue

        return {
            "parsed": False,
            "error": f"JSON parse error: {e}",
            "raw_preview": raw[:500],
            "raw_length": len(raw),
        }


def compare_extractions(gemini_result: dict, cached: dict | None) -> dict:
    """Compare Gemini extraction with cached legacy extraction."""
    comparison = {
        "cached_available": cached is not None,
        "gemini_success": gemini_result.get("parsed", False),
    }

    if gemini_result.get("parsed"):
        comparison["gemini_tables"] = len(gemini_result.get("tables", []))
        comparison["gemini_claims"] = len(gemini_result.get("causal_claims", []))

        # Count total rows extracted
        total_rows = sum(
            len(t.get("rows", [])) for t in gemini_result.get("tables", [])
        )
        comparison["gemini_total_rows"] = total_rows

    if cached:
        # Extract info from cached data
        pages = cached.get("pages", [])
        comparison["cached_pages"] = len(pages)
        comparison["cached_text_chars"] = cached.get("text_chars", 0)

    return comparison


def test_paper(doi: str, api_key: str, verbose: bool = True) -> dict:
    """Test extraction on a single paper."""
    # Find paper info
    paper_info = next((p for p in PROBLEM_PAPERS if p["doi"] == doi), None)

    if not paper_info:
        # Try to construct path anyway
        pdf_filename = doi.replace("/", "_") + ".pdf"
        paper_info = {"doi": doi, "description": "Custom DOI", "pdf": pdf_filename}

    pdf_path = PDF_BASE_PATH / paper_info["pdf"]

    if not pdf_path.exists():
        return {"error": f"PDF not found: {pdf_path}"}

    if verbose:
        print(f"\n{'='*60}")
        print(f"Testing: {doi}")
        print(f"Description: {paper_info['description']}")
        print(f"PDF: {pdf_path.name} ({pdf_path.stat().st_size / 1024 / 1024:.1f} MB)")
        print(f"{'='*60}")

    # Load cached extraction
    cached = load_cached_extraction(doi)
    if verbose and cached:
        print(f"  Cached extraction found: {cached.get('page_count', '?')} pages")

    # Run Gemini extraction
    if verbose:
        print(f"  Running Gemini 2.5 Pro extraction...")

    gemini_response = extract_with_gemini(pdf_path, api_key)

    if verbose:
        if gemini_response["success"]:
            print(f"  Gemini response received ({len(gemini_response['raw_response'])} chars)")
        else:
            print(f"  Gemini ERROR: {gemini_response.get('error')}")

    # Parse response
    parsed = parse_gemini_response(gemini_response)

    if verbose:
        if parsed.get("parsed"):
            print(f"  Parsed: {len(parsed.get('tables', []))} tables, {len(parsed.get('causal_claims', []))} claims")
        else:
            print(f"  Parse ERROR: {parsed.get('error')}")
            if parsed.get("raw_preview"):
                print(f"  Response preview: {parsed['raw_preview'][:200]}...")

    # Compare with cached
    comparison = compare_extractions(parsed, cached)

    if verbose:
        print(f"\n  --- Comparison ---")
        print(f"  Gemini tables: {comparison.get('gemini_tables', 'N/A')}")
        print(f"  Gemini claims: {comparison.get('gemini_claims', 'N/A')}")
        print(f"  Gemini rows: {comparison.get('gemini_total_rows', 'N/A')}")
        print(f"  Legacy status: {'FAILED (100% garbled)' if cached else 'No cache'}")

    return {
        "doi": doi,
        "paper_info": paper_info,
        "gemini_response": gemini_response,
        "parsed": parsed,
        "comparison": comparison,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def save_results(results: list[dict], output_dir: Path):
    """Save test results to JSON file."""
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"gemini_extraction_test_{timestamp}.json"

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")
    return output_file


def main():
    parser = argparse.ArgumentParser(
        description="Test Gemini 2.5 Pro extraction on problem papers"
    )
    parser.add_argument(
        "--doi",
        help="DOI of paper to test (e.g., '10.1002/adfm.202008831')",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Test all problem papers",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available problem papers",
    )
    parser.add_argument(
        "--model",
        default="gemini-2.5-pro",
        help="Gemini model to use (default: gemini-2.5-pro)",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save results to JSON file",
    )

    args = parser.parse_args()

    if args.list:
        print("\nAvailable problem papers (100%% extraction failure):\n")
        for p in PROBLEM_PAPERS:
            pdf_path = PDF_BASE_PATH / p["pdf"]
            exists = "OK" if pdf_path.exists() else "MISSING"
            print(f"  [{exists}] {p['doi']}")
            print(f"         {p['description']}")
        return

    if not args.doi and not args.all:
        parser.print_help()
        print("\nExamples:")
        print('  python scripts/test_gemini_extraction.py --doi "10.1002/adfm.202008831"')
        print("  python scripts/test_gemini_extraction.py --all")
        print("  python scripts/test_gemini_extraction.py --list")
        return

    api_key = get_api_key()
    results = []

    if args.all:
        print(f"\nTesting {len(PROBLEM_PAPERS)} problem papers with {args.model}...")
        for paper in PROBLEM_PAPERS:
            result = test_paper(paper["doi"], api_key)
            results.append(result)
    else:
        result = test_paper(args.doi, api_key)
        results.append(result)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    total_cost = 0.0
    total_input_tokens = 0
    total_output_tokens = 0

    for r in results:
        doi = r.get("doi", "?")
        parsed = r.get("parsed", {})
        gemini_resp = r.get("gemini_response", {})
        usage = gemini_resp.get("usage", {})
        cost = usage.get("cost_usd", 0)
        total_cost += cost
        total_input_tokens += usage.get("prompt_tokens", 0)
        total_output_tokens += usage.get("output_tokens", 0)

        if parsed.get("parsed"):
            tables = len(parsed.get("tables", []))
            claims = len(parsed.get("causal_claims", []))
            print(f"  {doi}: {tables} tables, {claims} claims (${cost:.4f})")
        elif r.get("error"):
            print(f"  {doi}: ERROR - {r['error']}")
        else:
            print(f"  {doi}: PARSE FAILED - {parsed.get('error', 'unknown')}")

    print(f"\n{'='*60}")
    print("COST SUMMARY")
    print(f"{'='*60}")
    print(f"  Input tokens:  {total_input_tokens:,}")
    print(f"  Output tokens: {total_output_tokens:,}")
    print(f"  TOTAL COST:    ${total_cost:.4f}")

    if args.save:
        save_results(results, OUTPUT_PATH)


if __name__ == "__main__":
    main()
