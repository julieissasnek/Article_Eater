#!/usr/bin/env python3
"""Parallel extraction using asyncio for 10-20x speedup."""

from __future__ import annotations

import asyncio
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

from scripts.gemini_extraction_queue import PROMPT_MAP, PRICING

AF_ROOT = Path("/Users/davidusa/REPOS/Article_Finder_v3_2_3")
PDF_DIR = AF_ROOT / "data" / "pdfs"
OUTPUT_DIR = PROJECT_ROOT / "data" / "extractions"
MODEL = "gemini-2.5-flash"

# Concurrency settings
MAX_CONCURRENT = 20  # Number of parallel requests
SAVE_INTERVAL = 50   # Save checkpoint every N completions


async def extract_paper_async(client: genai.Client, pdf_path: Path, article_type: str, semaphore: asyncio.Semaphore) -> dict:
    """Extract a single paper with semaphore-controlled concurrency."""
    async with semaphore:
        start = time.time()

        if not pdf_path.exists():
            return {"success": False, "error": f"PDF not found"}

        prompt = PROMPT_MAP.get(article_type, PROMPT_MAP["unknown"])

        try:
            # Upload PDF (sync operation wrapped)
            loop = asyncio.get_event_loop()
            with open(pdf_path, "rb") as f:
                uploaded = await loop.run_in_executor(
                    None,
                    lambda: client.files.upload(file=f, config={"mime_type": "application/pdf"})
                )

            # Wait for processing
            while uploaded.state.name == "PROCESSING":
                await asyncio.sleep(1)
                uploaded = await loop.run_in_executor(
                    None,
                    lambda: client.files.get(name=uploaded.name)
                )

            if uploaded.state.name == "FAILED":
                return {"success": False, "error": "Upload failed"}

            # Generate content using async client
            response = await client.aio.models.generate_content(
                model=MODEL,
                contents=[
                    types.Part.from_uri(file_uri=uploaded.uri, mime_type="application/pdf"),
                    prompt,
                ],
                config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=65536),
            )

            elapsed = time.time() - start
            text = response.text.strip()

            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

            result = json.loads(text)

            cost = 0.0
            if response.usage_metadata:
                m = response.usage_metadata
                pricing = PRICING.get(MODEL, PRICING["gemini-2.5-flash"])
                cost = (m.prompt_token_count * pricing["input"] + m.candidates_token_count * pricing["output"]) / 1_000_000

            # Cleanup
            try:
                await loop.run_in_executor(None, lambda: client.files.delete(name=uploaded.name))
            except Exception:  
                pass

            return {"success": True, "data": result, "cost": round(cost, 6), "elapsed": round(elapsed, 1)}

        except json.JSONDecodeError as e:
            return {"success": False, "error": f"JSON parse: {e}"}
        except Exception as e:
            return {"success": False, "error": str(e)[:100]}


async def process_batch(client: genai.Client, papers: list, results_dict: dict, stats: dict, lock: asyncio.Lock):
    """Process a batch of papers concurrently."""
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async def process_one(paper: dict):
        doi = paper["doi"]
        article_type = paper["article_type"]
        pdf_path = PDF_DIR / (doi.replace("/", "_") + ".pdf")

        result = await extract_paper_async(client, pdf_path, article_type, semaphore)

        async with lock:
            if result.get("success"):
                paper["status"] = "completed"
                paper["final_result"] = result["data"]
                paper["total_cost"] = result["cost"]
                stats["completed"] += 1
                stats["cost"] += result["cost"]

                n = len(result["data"].get("findings", result["data"].get("pooled_effects", result["data"].get("key_claims", []))))
                print(f"  ✓ {doi[:40]}... ({n} findings, ${result['cost']:.4f})")
            else:
                stats["failed"] += 1
                print(f"  ✗ {doi[:40]}... ({result.get('error', 'unknown')[:30]})")

            stats["processed"] += 1

            # Progress update
            if stats["processed"] % 10 == 0:
                elapsed = time.time() - stats["start_time"]
                rate = stats["processed"] / elapsed * 60  # per minute
                remaining = len(papers) - stats["processed"]
                eta = remaining / rate if rate > 0 else 0
                print(f"\n  [{stats['processed']}/{len(papers)}] {stats['completed']} done, ${stats['cost']:.2f}, {rate:.1f}/min, ETA: {eta:.0f} min\n")

        return paper

    tasks = [process_one(p) for p in papers]
    await asyncio.gather(*tasks)


async def main():
    print("=" * 70)
    print(f"PARALLEL EXTRACTION: {MAX_CONCURRENT} concurrent requests")
    print("=" * 70)

    # Find latest extraction file
    extraction_files = sorted(OUTPUT_DIR.glob("full_extraction_*.json"))
    if not extraction_files:
        print("No extraction file found")
        sys.exit(1)

    latest = extraction_files[-1]
    print(f"Resuming from: {latest.name}")

    with open(latest) as f:
        data = json.load(f)

    # Get papers that need processing
    to_process = [r for r in data["results"] if r.get("status") != "completed"]
    print(f"Papers to process: {len(to_process)}")

    if not to_process:
        print("All papers completed!")
        return

    # Setup client
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Set GOOGLE_API_KEY or GEMINI_API_KEY")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    # Stats
    stats = {
        "completed": data.get("completed", 0),
        "failed": 0,
        "cost": data.get("total_cost", 0),
        "processed": 0,
        "start_time": time.time(),
    }

    lock = asyncio.Lock()

    # Process in batches
    batch_size = 100
    for i in range(0, len(to_process), batch_size):
        batch = to_process[i:i+batch_size]
        print(f"\nBatch {i//batch_size + 1}: papers {i+1}-{min(i+batch_size, len(to_process))}")

        await process_batch(client, batch, data, stats, lock)

        # Save checkpoint after each batch
        data["completed"] = stats["completed"]
        data["failed"] = stats["failed"]
        data["total_cost"] = round(stats["cost"], 4)
        data["parallel_resumed_at"] = datetime.now(timezone.utc).isoformat()

        with open(latest, "w") as f:
            json.dump(data, f, indent=2)
        print(f"  [Checkpoint saved: {stats['completed']} completed]")

    # Final summary
    elapsed = time.time() - stats["start_time"]
    print(f"\n{'='*70}")
    print(f"DONE: {stats['completed']} completed, {stats['failed']} failed")
    print(f"Cost: ${stats['cost']:.2f}")
    print(f"Time: {elapsed/60:.1f} minutes ({stats['processed']/(elapsed/60):.1f} papers/min)")


if __name__ == "__main__":
    asyncio.run(main())
