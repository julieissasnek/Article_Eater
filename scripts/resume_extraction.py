#!/usr/bin/env python3
"""Resume extraction from where it left off."""

from __future__ import annotations

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


def get_client() -> genai.Client:
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Set GOOGLE_API_KEY or GEMINI_API_KEY")
        sys.exit(1)
    return genai.Client(api_key=api_key)


def extract_paper(client: genai.Client, pdf_path: Path, article_type: str) -> dict:
    start = time.time()
    if not pdf_path.exists():
        return {"success": False, "error": f"PDF not found: {pdf_path}"}

    prompt = PROMPT_MAP.get(article_type, PROMPT_MAP["unknown"])

    try:
        with open(pdf_path, "rb") as f:
            uploaded = client.files.upload(file=f, config={"mime_type": "application/pdf"})

        while uploaded.state.name == "PROCESSING":
            time.sleep(1)
            uploaded = client.files.get(name=uploaded.name)

        if uploaded.state.name == "FAILED":
            return {"success": False, "error": "Upload failed"}

        response = client.models.generate_content(
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

        try:
            client.files.delete(name=uploaded.name)
        except:
            pass

        return {"success": True, "data": result, "cost": round(cost, 6), "elapsed": round(elapsed, 1)}

    except json.JSONDecodeError as e:
        return {"success": False, "error": f"JSON parse: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    # Find the latest extraction file
    extraction_files = sorted(OUTPUT_DIR.glob("full_extraction_*.json"))
    if not extraction_files:
        print("No extraction file to resume from")
        sys.exit(1)

    latest = extraction_files[-1]
    print(f"Resuming from: {latest.name}")

    with open(latest) as f:
        data = json.load(f)

    results = data["results"]

    # Find failed papers
    to_process = []
    for r in results:
        if r.get("status") != "completed":
            to_process.append(r)

    print(f"Papers to process: {len(to_process)}")
    if not to_process:
        print("All papers already completed!")
        return

    client = get_client()

    completed = data.get("completed", 0)
    failed = data.get("failed", 0)
    total_cost = data.get("total_cost", 0)
    start_time = time.time()

    for i, paper in enumerate(to_process):
        doi = paper["doi"]
        article_type = paper["article_type"]
        pdf_path = PDF_DIR / (doi.replace("/", "_") + ".pdf")

        elapsed = time.time() - start_time
        rate = (i + 1) / elapsed if elapsed > 0 else 0
        eta = (len(to_process) - i - 1) / rate / 60 if rate > 0 else 0

        print(f"\n[{i+1}/{len(to_process)}] {doi[:50]} ({article_type})")
        print(f"  Progress: {completed} done, ${total_cost:.2f} spent, ETA: {eta:.0f} min")

        result = extract_paper(client, pdf_path, article_type)

        if result.get("success"):
            paper["status"] = "completed"
            paper["final_result"] = result["data"]
            paper["total_cost"] = result["cost"]
            completed += 1
            failed -= 1
            total_cost += result["cost"]

            n = len(result["data"].get("findings", result["data"].get("pooled_effects", result["data"].get("key_claims", []))))
            print(f"  ✓ {n} findings, ${result['cost']:.4f}")
        else:
            print(f"  ✗ {result.get('error', 'unknown')[:50]}")

        # Save every 10
        if (i + 1) % 10 == 0:
            data["completed"] = completed
            data["failed"] = failed
            data["total_cost"] = round(total_cost, 4)
            with open(latest, "w") as f:
                json.dump(data, f, indent=2)
            print(f"  [Checkpoint saved]")

        time.sleep(1)

    # Final save
    data["completed"] = completed
    data["failed"] = failed
    data["total_cost"] = round(total_cost, 4)
    data["resumed_at"] = datetime.now(timezone.utc).isoformat()
    with open(latest, "w") as f:
        json.dump(data, f, indent=2)

    print(f"\n{'='*60}")
    print(f"DONE: {completed} completed, {failed} failed, ${total_cost:.2f}")


if __name__ == "__main__":
    main()
