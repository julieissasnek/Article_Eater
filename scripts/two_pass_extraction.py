#!/usr/bin/env python3
"""Two-pass extraction: classify article type first, then extract with correct prompt.

Simplified version using ThreadPoolExecutor instead of asyncio for reliability.
"""

from __future__ import annotations

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from google import genai
from google.genai import types

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.gemini_extraction_queue import PROMPT_MAP, PRICING

AF_ROOT = Path("/Users/davidusa/REPOS/Article_Finder_v3_2_3")
PDF_DIR = AF_ROOT / "data" / "pdfs"
OUTPUT_DIR = PROJECT_ROOT / "data" / "extractions"
MODEL = "gemini-2.5-flash"

# Concurrency - reduced to avoid truncation
MAX_WORKERS = 3
RETRY_ATTEMPTS = 3
DELAY_BETWEEN_REQUESTS = 1.0  # seconds

# Classification prompt - simplified for more reliable JSON
CLASSIFY_PROMPT = """What type of academic paper is this?

Reply with ONLY this JSON (no markdown, no explanation):
{"article_type": "TYPE", "confidence": 0.9}

Where TYPE is one of:
- empirical (has Methods, Results, p-values, N=)
- meta_analysis (pooled effects, forest plots, k studies)
- systematic_review (PRISMA, inclusion criteria)
- narrative_review (literature synthesis)
- theoretical (frameworks, models, no data)
- qualitative (interviews, themes)
- methods (instrument validation)

JSON only:"""


def get_client():
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Set GOOGLE_API_KEY or GEMINI_API_KEY")
    return genai.Client(api_key=api_key)


import re
import time as time_module


def extract_json_from_text(text: str) -> dict | None:
    """Robustly extract JSON from potentially messy response."""
    text = text.strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except Exception:  
        pass

    # Strip any markdown code blocks (json, js, or unmarked)
    if "```" in text:
        match = re.search(r'```(?:json|js)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:  
                pass

    # Find any JSON object with article_type
    match = re.search(r'\{[^{}]*"article_type"\s*:\s*"[^"]+"\s*(?:,[^{}]*)?\}', text)
    if match:
        try:
            return json.loads(match.group())
        except Exception:  
            pass

    # Last resort: extract just the article_type value
    match = re.search(r'"article_type"\s*:\s*"([^"]+)"', text)
    if match:
        return {"article_type": match.group(1), "confidence": 0.5}

    return None


def classify_paper(client: genai.Client, pdf_path: Path) -> dict:
    """Classify a single paper's article type with retry logic."""
    if not pdf_path.exists():
        return {"success": False, "error": "PDF not found"}

    for attempt in range(RETRY_ATTEMPTS):
        uploaded = None
        try:
            time_module.sleep(DELAY_BETWEEN_REQUESTS)  # Rate limit protection

            with open(pdf_path, "rb") as f:
                uploaded = client.files.upload(file=f, config={"mime_type": "application/pdf"})

            response = client.models.generate_content(
                model=MODEL,
                contents=[uploaded, CLASSIFY_PROMPT],
                config=types.GenerateContentConfig(temperature=0.0, max_output_tokens=200),
            )

            text = response.text.strip()
            result = extract_json_from_text(text)

            if result is None:
                if attempt < RETRY_ATTEMPTS - 1:
                    continue  # Retry
                return {"success": False, "error": f"JSON parse failed: {text[:60]}"}

            # Cost
            cost = 0.0
            if response.usage_metadata:
                m = response.usage_metadata
                pricing = PRICING.get(MODEL, PRICING["gemini-2.5-flash"])
                cost = (m.prompt_token_count * pricing["input"] +
                       m.candidates_token_count * pricing["output"]) / 1_000_000

            return {
                "success": True,
                "article_type": result.get("article_type", "unknown"),
                "confidence": result.get("confidence", 0.0),
                "signals": result.get("signals", []),
                "cost": round(cost, 6)
            }

        except Exception as e:
            if attempt < RETRY_ATTEMPTS - 1:
                time_module.sleep(1)  # Wait before retry
                continue
            return {"success": False, "error": f"{type(e).__name__}: {str(e)[:80]}"}

        finally:
            # Cleanup uploaded file
            if uploaded:
                try:
                    client.files.delete(name=uploaded.name)
                except Exception:  
                    pass

    return {"success": False, "error": "Max retries exceeded"}


def extract_paper(client: genai.Client, pdf_path: Path, article_type: str) -> dict:
    """Extract findings using the correct prompt for article type."""
    if not pdf_path.exists():
        return {"success": False, "error": "PDF not found"}

    prompt = PROMPT_MAP.get(article_type, PROMPT_MAP["unknown"])

    try:
        with open(pdf_path, "rb") as f:
            uploaded = client.files.upload(file=f, config={"mime_type": "application/pdf"})

        response = client.models.generate_content(
            model=MODEL,
            contents=[uploaded, prompt],
            config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=65536),
        )

        text = response.text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

        result = json.loads(text)

        # Cost
        cost = 0.0
        if response.usage_metadata:
            m = response.usage_metadata
            pricing = PRICING.get(MODEL, PRICING["gemini-2.5-flash"])
            cost = (m.prompt_token_count * pricing["input"] +
                   m.candidates_token_count * pricing["output"]) / 1_000_000

        # Cleanup
        try:
            client.files.delete(name=uploaded.name)
        except Exception:  
            pass

        return {"success": True, "data": result, "cost": round(cost, 6)}

    except json.JSONDecodeError as e:
        return {"success": False, "error": f"JSON parse: {str(e)[:50]}"}
    except Exception as e:
        return {"success": False, "error": f"{type(e).__name__}: {str(e)[:80]}"}


def process_paper(doi: str) -> dict:
    """Process a single paper: classify then extract."""
    client = get_client()
    pdf_filename = doi.replace("/", "_") + ".pdf"
    pdf_path = PDF_DIR / pdf_filename

    # Pass 1: Classify
    classify_result = classify_paper(client, pdf_path)

    if not classify_result["success"]:
        return {
            "doi": doi,
            "status": "failed",
            "error": f"Classification: {classify_result['error']}",
            "article_type": "unknown",
            "cost": classify_result.get("cost", 0)
        }

    article_type = classify_result["article_type"]
    classify_cost = classify_result.get("cost", 0)

    # Pass 2: Extract
    extract_result = extract_paper(client, pdf_path, article_type)

    if not extract_result["success"]:
        return {
            "doi": doi,
            "status": "failed",
            "error": f"Extraction: {extract_result['error']}",
            "article_type": article_type,
            "classification": {
                "confidence": classify_result.get("confidence"),
                "signals": classify_result.get("signals", [])
            },
            "cost": classify_cost + extract_result.get("cost", 0)
        }

    # Success
    total_cost = classify_cost + extract_result.get("cost", 0)
    n_findings = len(extract_result["data"].get("findings", []))

    return {
        "doi": doi,
        "status": "completed",
        "article_type": article_type,
        "classification": {
            "confidence": classify_result.get("confidence"),
            "signals": classify_result.get("signals", [])
        },
        "final_result": extract_result["data"],
        "n_findings": n_findings,
        "cost": total_cost
    }


def get_unknown_papers() -> list[str]:
    """Get DOIs of papers classified as 'unknown'."""
    extraction_files = sorted(OUTPUT_DIR.glob("full_extraction_*.json"))
    if not extraction_files:
        print("No extraction file found")
        return []

    latest = extraction_files[-1]
    print(f"Reading from: {latest.name}")

    with open(latest) as f:
        data = json.load(f)

    return [r["doi"] for r in data.get("results", []) if r.get("article_type") == "unknown"]


def main():
    dois = get_unknown_papers()
    print(f"Papers to reprocess: {len(dois)}")

    if not dois:
        print("No unknown papers to process")
        return

    # Output files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"two_pass_extraction_{timestamp}.json"
    log_file = OUTPUT_DIR / "two_pass_log.txt"

    results = []
    stats = {"completed": 0, "failed": 0, "cost": 0.0, "findings": 0}
    start_time = time.time()

    with open(log_file, "w") as log:
        log.write(f"Two-pass extraction started: {datetime.now()}\n")
        log.write(f"Papers to process: {len(dois)}\n")
        log.write(f"Workers: {MAX_WORKERS}\n\n")
        log.flush()

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(process_paper, doi): doi for doi in dois}

            for i, future in enumerate(as_completed(futures), 1):
                doi = futures[future]
                try:
                    result = future.result(timeout=300)
                except Exception as e:
                    result = {
                        "doi": doi,
                        "status": "failed",
                        "error": f"Thread error: {type(e).__name__}: {str(e)[:80]}",
                        "article_type": "unknown",
                        "cost": 0
                    }

                results.append(result)

                # Update stats
                if result["status"] == "completed":
                    stats["completed"] += 1
                    stats["findings"] += result.get("n_findings", 0)
                else:
                    stats["failed"] += 1
                stats["cost"] += result.get("cost", 0)

                # Log
                elapsed = time.time() - start_time
                rate = i / elapsed * 60 if elapsed > 0 else 0
                eta = (len(dois) - i) / rate if rate > 0 else 0

                status = "✓" if result["status"] == "completed" else "✗"
                n = result.get("n_findings", 0)
                atype = result.get("article_type", "?")
                err = result.get("error", "")[:40] if result["status"] == "failed" else ""

                line = f"[{i}/{len(dois)}] {status} {doi[:35]}... ({atype}, {n} findings) {err}"
                print(line)
                log.write(line + "\n")

                if i % 10 == 0:
                    summary = f"  >> {stats['completed']} done, {stats['failed']} failed, ${stats['cost']:.2f}, {rate:.1f}/min, ETA: {eta:.0f}m"
                    print(summary)
                    log.write(summary + "\n")
                    log.flush()

                # Save checkpoint every 50
                if i % 50 == 0 or i == len(dois):
                    output_data = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "total": len(dois),
                        "completed": stats["completed"],
                        "failed": stats["failed"],
                        "total_findings": stats["findings"],
                        "total_cost": round(stats["cost"], 4),
                        "results": results
                    }
                    with open(output_file, "w") as f:
                        json.dump(output_data, f, indent=2)
                    print(f"  [Checkpoint saved: {output_file.name}]")

    # Final summary
    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"TWO-PASS EXTRACTION COMPLETE")
    print(f"{'='*60}")
    print(f"Total: {len(dois)}")
    print(f"Completed: {stats['completed']}")
    print(f"Failed: {stats['failed']}")
    print(f"Findings: {stats['findings']}")
    print(f"Cost: ${stats['cost']:.2f}")
    print(f"Time: {elapsed/60:.1f} min")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()
