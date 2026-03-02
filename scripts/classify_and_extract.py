#!/usr/bin/env python3
"""
Sequential two-pass extraction: classify then extract.

Design principles:
1. Sequential processing first (reliable before fast)
2. Thorough testing before full run
3. Simple prompts for reliable parsing
4. Immediate validation and retry
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from google import genai
from google.genai import types
from scripts.gemini_extraction_queue import PROMPT_MAP, PRICING

# Paths
AF_ROOT = Path("/Users/davidusa/REPOS/Article_Finder_v3_2_3")
PDF_DIR = AF_ROOT / "data" / "pdfs"
OUTPUT_DIR = PROJECT_ROOT / "data" / "extractions"
MODEL = "gemini-2.5-flash"

# Simple classification prompt - returns just the type
CLASSIFY_PROMPT = """Classify this paper. Return ONE word only:
empirical
meta_analysis
systematic_review
narrative_review
theoretical
qualitative
methods

Your answer (one word):"""


def get_client():
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Set GOOGLE_API_KEY or GEMINI_API_KEY")
    return genai.Client(api_key=api_key)


def extract_article_type(text: str) -> str | None:
    """Extract article type from response text."""
    text = text.strip().lower()

    # Valid types
    valid_types = {
        "empirical", "meta_analysis", "systematic_review",
        "narrative_review", "theoretical", "qualitative", "methods"
    }

    # Direct match
    for t in valid_types:
        if t in text:
            return t

    # Handle variations
    if "meta" in text and "analysis" in text:
        return "meta_analysis"
    if "systematic" in text:
        return "systematic_review"
    if "narrative" in text or "literature review" in text:
        return "narrative_review"

    return None


def classify_paper(client: genai.Client, pdf_path: Path, max_retries: int = 3) -> dict:
    """Classify a paper with retries."""
    if not pdf_path.exists():
        return {"success": False, "error": "PDF not found"}

    for attempt in range(max_retries):
        uploaded = None
        try:
            with open(pdf_path, "rb") as f:
                uploaded = client.files.upload(
                    file=f, config={"mime_type": "application/pdf"}
                )

            response = client.models.generate_content(
                model=MODEL,
                contents=[uploaded, CLASSIFY_PROMPT],
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    max_output_tokens=50  # Very short response expected
                ),
            )

            text = response.text.strip()
            article_type = extract_article_type(text)

            if article_type is None:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return {"success": False, "error": f"Could not parse type from: {text[:50]}"}

            # Calculate cost
            cost = 0.0
            if response.usage_metadata:
                m = response.usage_metadata
                pricing = PRICING.get(MODEL, PRICING["gemini-2.5-flash"])
                cost = (m.prompt_token_count * pricing["input"] +
                       m.candidates_token_count * pricing["output"]) / 1_000_000

            return {
                "success": True,
                "article_type": article_type,
                "raw_response": text,
                "cost": round(cost, 6)
            }

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return {"success": False, "error": f"{type(e).__name__}: {str(e)[:80]}"}

        finally:
            if uploaded:
                try:
                    client.files.delete(name=uploaded.name)
                except Exception:  
                    pass

    return {"success": False, "error": "Max retries exceeded"}


def extract_paper(client: genai.Client, pdf_path: Path, article_type: str, max_retries: int = 2) -> dict:
    """Extract findings using correct prompt."""
    if not pdf_path.exists():
        return {"success": False, "error": "PDF not found"}

    prompt = PROMPT_MAP.get(article_type, PROMPT_MAP["unknown"])

    for attempt in range(max_retries):
        uploaded = None
        try:
            with open(pdf_path, "rb") as f:
                uploaded = client.files.upload(
                    file=f, config={"mime_type": "application/pdf"}
                )

            response = client.models.generate_content(
                model=MODEL,
                contents=[uploaded, prompt],
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=65536
                ),
            )

            text = response.text.strip()

            # Strip markdown
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

            return {"success": True, "data": result, "cost": round(cost, 6)}

        except json.JSONDecodeError as e:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            return {"success": False, "error": f"JSON parse: {str(e)[:50]}"}
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return {"success": False, "error": f"{type(e).__name__}: {str(e)[:80]}"}

        finally:
            if uploaded:
                try:
                    client.files.delete(name=uploaded.name)
                except Exception:  
                    pass

    return {"success": False, "error": "Max retries exceeded"}


def test_single_paper(doi: str):
    """Test classification and extraction on a single paper."""
    print(f"\n{'='*60}")
    print(f"Testing: {doi}")
    print(f"{'='*60}")

    client = get_client()
    pdf_path = PDF_DIR / (doi.replace("/", "_") + ".pdf")

    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        return None

    print(f"PDF size: {pdf_path.stat().st_size / 1024:.1f} KB")

    # Step 1: Classify
    print("\n1. CLASSIFYING...")
    classify_result = classify_paper(client, pdf_path)
    print(f"   Result: {classify_result}")

    if not classify_result["success"]:
        print(f"   FAILED: {classify_result['error']}")
        return classify_result

    article_type = classify_result["article_type"]
    print(f"   Type: {article_type}")

    # Step 2: Extract
    print("\n2. EXTRACTING...")
    extract_result = extract_paper(client, pdf_path, article_type)

    if not extract_result["success"]:
        print(f"   FAILED: {extract_result['error']}")
        return {"classify": classify_result, "extract": extract_result}

    n_findings = len(extract_result["data"].get("findings", []))
    print(f"   Findings: {n_findings}")
    print(f"   Total cost: ${classify_result['cost'] + extract_result['cost']:.4f}")

    return {
        "doi": doi,
        "article_type": article_type,
        "n_findings": n_findings,
        "success": True
    }


def run_batch(dois: list[str], output_file: Path):
    """Process a batch of papers sequentially."""
    client = get_client()
    results = []
    stats = {"completed": 0, "failed": 0, "cost": 0.0, "findings": 0}
    start_time = time.time()

    log_file = OUTPUT_DIR / "classify_extract_log.txt"

    with open(log_file, "w") as log:
        log.write(f"Started: {datetime.now()}\n")
        log.write(f"Papers: {len(dois)}\n\n")

        for i, doi in enumerate(dois, 1):
            pdf_path = PDF_DIR / (doi.replace("/", "_") + ".pdf")

            # Classify
            classify_result = classify_paper(client, pdf_path)

            if not classify_result["success"]:
                stats["failed"] += 1
                result = {
                    "doi": doi,
                    "status": "failed",
                    "error": f"Classification: {classify_result['error']}",
                    "article_type": "unknown"
                }
                results.append(result)
                line = f"[{i}/{len(dois)}] ✗ {doi[:40]}... (classification failed)"
                print(line)
                log.write(line + "\n")
                continue

            article_type = classify_result["article_type"]

            # Extract
            extract_result = extract_paper(client, pdf_path, article_type)

            if not extract_result["success"]:
                stats["failed"] += 1
                result = {
                    "doi": doi,
                    "status": "failed",
                    "error": f"Extraction: {extract_result['error']}",
                    "article_type": article_type
                }
                results.append(result)
                line = f"[{i}/{len(dois)}] ✗ {doi[:40]}... ({article_type}, extraction failed)"
                print(line)
                log.write(line + "\n")
                continue

            # Success
            n_findings = len(extract_result["data"].get("findings", []))
            total_cost = classify_result["cost"] + extract_result["cost"]

            stats["completed"] += 1
            stats["findings"] += n_findings
            stats["cost"] += total_cost

            result = {
                "doi": doi,
                "status": "completed",
                "article_type": article_type,
                "final_result": extract_result["data"],
                "n_findings": n_findings,
                "cost": total_cost
            }
            results.append(result)

            elapsed = time.time() - start_time
            rate = i / elapsed * 60 if elapsed > 0 else 0
            eta = (len(dois) - i) / rate if rate > 0 else 0

            line = f"[{i}/{len(dois)}] ✓ {doi[:40]}... ({article_type}, {n_findings} findings)"
            print(line)
            log.write(line + "\n")

            if i % 10 == 0:
                summary = f"  >> {stats['completed']}/{i} done, ${stats['cost']:.2f}, {rate:.1f}/min, ETA: {eta:.0f}m"
                print(summary)
                log.write(summary + "\n")
                log.flush()

                # Checkpoint
                save_results(output_file, results, stats, len(dois))

        # Final save
        save_results(output_file, results, stats, len(dois))

    print(f"\n{'='*60}")
    print(f"COMPLETE: {stats['completed']}/{len(dois)}, {stats['findings']} findings, ${stats['cost']:.2f}")


def save_results(output_file: Path, results: list, stats: dict, total: int):
    """Save current results to file."""
    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total": total,
        "completed": stats["completed"],
        "failed": stats["failed"],
        "total_findings": stats["findings"],
        "total_cost": round(stats["cost"], 4),
        "results": results
    }
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)


def get_unknown_papers() -> list[str]:
    """Get DOIs of papers classified as 'unknown'."""
    extraction_files = sorted(OUTPUT_DIR.glob("full_extraction_*.json"))
    if not extraction_files:
        return []
    latest = extraction_files[-1]
    with open(latest) as f:
        data = json.load(f)
    return [r["doi"] for r in data.get("results", []) if r.get("article_type") == "unknown"]


def get_already_processed() -> set[str]:
    """Get DOIs that have already been processed in classified_extraction files."""
    processed = set()
    for f in OUTPUT_DIR.glob("classified_extraction_*.json"):
        try:
            with open(f) as fp:
                data = json.load(fp)
            for r in data.get("results", []):
                if r.get("status") == "completed":
                    processed.add(r["doi"])
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")
    return processed


def get_latest_checkpoint() -> tuple[Path | None, list, dict]:
    """Get the latest checkpoint file and its data for resuming."""
    checkpoint_files = sorted(OUTPUT_DIR.glob("classified_extraction_*.json"))
    if not checkpoint_files:
        return None, [], {"completed": 0, "failed": 0, "cost": 0.0, "findings": 0}

    latest = checkpoint_files[-1]
    try:
        with open(latest) as f:
            data = json.load(f)
        results = data.get("results", [])
        stats = {
            "completed": data.get("completed", 0),
            "failed": data.get("failed", 0),
            "cost": data.get("total_cost", 0.0),
            "findings": data.get("total_findings", 0)
        }
        return latest, results, stats
    except Exception as e:
        import logging; logging.getLogger(__name__).debug(f"Returning None: {e}")
        return None, [], {"completed": 0, "failed": 0, "cost": 0.0, "findings": 0}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=str, help="Test single DOI")
    parser.add_argument("--test-batch", type=int, default=0, help="Test N papers")
    parser.add_argument("--run", action="store_true", help="Run full extraction")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--batch-size", type=int, default=50, help="Papers per batch (for sleep-friendly processing)")
    args = parser.parse_args()

    if args.test:
        test_single_paper(args.test)

    elif args.test_batch > 0:
        dois = get_unknown_papers()[:args.test_batch]
        print(f"Testing {len(dois)} papers...")
        for doi in dois:
            result = test_single_paper(doi)
            time.sleep(1)

    elif args.run or args.resume:
        all_dois = get_unknown_papers()
        processed = get_already_processed()
        remaining_dois = [d for d in all_dois if d not in processed]

        print(f"Total unknown: {len(all_dois)}")
        print(f"Already processed: {len(processed)}")
        print(f"Remaining: {len(remaining_dois)}")

        if not remaining_dois:
            print("All papers have been processed!")
        else:
            # Process in batches for sleep-friendliness
            batch = remaining_dois[:args.batch_size]
            print(f"\nProcessing batch of {len(batch)} papers...")
            print(f"(Run with --resume to continue after this batch)")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = OUTPUT_DIR / f"classified_extraction_{timestamp}.json"
            run_batch(batch, output_file)

            remaining_after = len(remaining_dois) - len(batch)
            if remaining_after > 0:
                print(f"\n{remaining_after} papers remaining. Run --resume to continue.")

    else:
        parser.print_help()
