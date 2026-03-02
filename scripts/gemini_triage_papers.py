#!/usr/bin/env python3
"""Quick article type triage using Gemini Flash.

Classifies papers into article types for appropriate extraction prompts.
Uses first few pages of PDF (cheap, fast).

Usage:
    python scripts/gemini_triage_papers.py --sample 10  # Test on 10 papers
    python scripts/gemini_triage_papers.py --all        # All papers
    python scripts/gemini_triage_papers.py --resume     # Continue from last run
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from google import genai
from google.genai import types

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Article Finder paths
AF_ROOT = Path("/Users/davidusa/REPOS/Article_Finder_v3_2_3")
AF_DB = AF_ROOT / "data" / "article_finder.db"
PDF_DIR = AF_ROOT / "data" / "pdfs"

# Output
OUTPUT_DIR = PROJECT_ROOT / "data" / "triage"
TRIAGE_FILE = OUTPUT_DIR / "article_type_triage.json"

# Article type families (from article_type_contract.py)
ARTICLE_TYPES = {
    "empirical": {
        "subtypes": ["experiment", "field_study", "survey", "observational", "case_study", "mixed_methods"],
        "signals": ["participants", "n=", "p<", "p=", "significant", "measured", "results show", "ANOVA", "regression", "t-test", "correlation"],
    },
    "meta_analysis": {
        "subtypes": ["meta-analysis", "quantitative synthesis"],
        "signals": ["meta-analysis", "pooled effect", "forest plot", "heterogeneity", "I²", "k=", "included studies"],
    },
    "systematic_review": {
        "subtypes": ["systematic review", "scoping review"],
        "signals": ["systematic review", "PRISMA", "inclusion criteria", "exclusion criteria", "quality assessment", "risk of bias"],
    },
    "narrative_review": {
        "subtypes": ["literature review", "narrative review", "overview"],
        "signals": ["review", "literature", "synthesis", "overview", "summarize", "state of the art"],
    },
    "theoretical": {
        "subtypes": ["theoretical", "conceptual", "framework", "model", "perspective", "commentary"],
        "signals": ["we propose", "framework", "theory", "model", "conceptual", "perspective", "argue that"],
    },
    "qualitative": {
        "subtypes": ["interview", "ethnographic", "grounded_theory", "phenomenological", "focus_group"],
        "signals": ["interviews", "qualitative", "themes", "coding", "participants reported", "thematic analysis", "focus group"],
    },
    "methods": {
        "subtypes": ["methods", "protocol", "guidelines", "instrument"],
        "signals": ["protocol", "methodology", "guidelines", "instrument development", "validation study"],
    },
}

TRIAGE_PROMPT = """Classify this scientific paper's article type based on its first pages.

Return JSON only:
{
  "article_type": "empirical|meta_analysis|systematic_review|narrative_review|theoretical|qualitative|methods|unknown",
  "subtype": "more specific type (e.g., experiment, survey, interview_study)",
  "confidence": 0.0-1.0,
  "signals": ["list", "of", "key", "indicators"],
  "has_results_tables": true|false,
  "estimated_n_tables": 0-20,
  "domains": ["A4_Light", "A2_Spatial_Scale", etc.],
  "brief_topic": "one sentence describing the paper's focus"
}

Domain codes:
- A1_Materials (wood, concrete, texture)
- A2_Spatial_Scale (ceiling height, room size, volume)
- A3_Spatial_Config (layout, wayfinding, navigation)
- A4_Light (daylight, illuminance, circadian)
- A5_Acoustic (noise, sound, reverberation)
- A6_Visual_Form (color, pattern, aesthetics)
- A7_Haptic_Thermal (temperature, touch, comfort)
- A8_Social (privacy, collaboration, density)
- A9_Task_Cognition (attention, memory, creativity)
- A10_Temporal (time, duration, seasonal)

Article type definitions:
- empirical: Original research with participants, measurements, statistical analysis
- meta_analysis: Quantitative synthesis of multiple studies with pooled effects
- systematic_review: Structured review following PRISMA or similar protocol
- narrative_review: Literature synthesis without formal meta-analysis
- theoretical: Framework/model development, perspective pieces
- qualitative: Interview, ethnographic, or other qualitative research
- methods: Protocol, guidelines, instrument development
- unknown: Cannot determine from available content
"""

# Pricing per 1M tokens
PRICING = {
    "gemini-2.5-flash": {"input": 0.15, "output": 0.60},
}


def get_client() -> genai.Client:
    """Get configured Gemini client."""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Set GOOGLE_API_KEY or GEMINI_API_KEY")
        sys.exit(1)
    return genai.Client(api_key=api_key)


def get_papers_to_triage(already_done: set[str]) -> list[dict]:
    """Get list of papers with PDFs that need triage."""
    papers = []

    # Get papers from Article Finder DB
    if AF_DB.exists():
        conn = sqlite3.connect(AF_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT doi, title, abstract, pdf_path
            FROM papers
            WHERE pdf_path IS NOT NULL
        """)
        for row in cursor:
            doi = row["doi"]
            if doi and doi not in already_done:
                pdf_path = PDF_DIR / Path(row["pdf_path"]).name
                if pdf_path.exists():
                    papers.append({
                        "doi": doi,
                        "title": row["title"],
                        "abstract": row["abstract"],
                        "pdf_path": str(pdf_path),
                    })
        conn.close()

    # Also check for PDFs not in database
    for pdf_file in PDF_DIR.glob("*.pdf"):
        doi = pdf_file.stem.replace("_", "/")
        if doi not in already_done and not any(p["doi"] == doi for p in papers):
            papers.append({
                "doi": doi,
                "title": None,
                "abstract": None,
                "pdf_path": str(pdf_file),
            })

    return papers


def triage_paper(client: genai.Client, paper: dict) -> dict:
    """Triage a single paper using Gemini Flash."""
    start = time.time()
    pdf_path = Path(paper["pdf_path"])

    if not pdf_path.exists():
        return {"doi": paper["doi"], "error": "PDF not found", "elapsed": 0}

    pdf_size_mb = pdf_path.stat().st_size / (1024 * 1024)

    try:
        # Upload PDF
        with open(pdf_path, "rb") as f:
            uploaded = client.files.upload(file=f, config={"mime_type": "application/pdf"})

        # Wait for processing
        while uploaded.state.name == "PROCESSING":
            time.sleep(1)
            uploaded = client.files.get(name=uploaded.name)

        if uploaded.state.name == "FAILED":
            return {"doi": paper["doi"], "error": "Upload failed", "elapsed": time.time() - start}

        # Build prompt with context
        context = ""
        if paper.get("title"):
            context += f"Title: {paper['title']}\n"
        if paper.get("abstract"):
            context += f"Abstract: {paper['abstract'][:500]}...\n"

        prompt = context + "\n" + TRIAGE_PROMPT

        # Generate classification
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_uri(file_uri=uploaded.uri, mime_type="application/pdf"),
                prompt,
            ],
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=1024,
            ),
        )

        elapsed = time.time() - start

        # Parse response
        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            parts = text.split("```")
            if len(parts) >= 2:
                text = parts[1]

        # Clean up common JSON issues
        text = text.strip()
        # Try to extract just the JSON object
        if "{" in text:
            start = text.index("{")
            # Find matching closing brace
            depth = 0
            end = start
            for i, c in enumerate(text[start:], start):
                if c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
            text = text[start:end]

        result = json.loads(text)

        # Add metadata
        result["doi"] = paper["doi"]
        result["pdf_size_mb"] = round(pdf_size_mb, 2)
        result["elapsed"] = round(elapsed, 1)
        result["timestamp"] = datetime.now(timezone.utc).isoformat()

        # Calculate cost
        if response.usage_metadata:
            m = response.usage_metadata
            cost = (m.prompt_token_count * 0.15 + m.candidates_token_count * 0.60) / 1_000_000
            result["cost_usd"] = round(cost, 6)
            result["input_tokens"] = m.prompt_token_count
            result["output_tokens"] = m.candidates_token_count

        # Cleanup
        try:
            client.files.delete(name=uploaded.name)
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

        return result

    except json.JSONDecodeError as e:
        return {"doi": paper["doi"], "error": f"JSON parse error: {e}", "elapsed": time.time() - start}
    except Exception as e:
        return {"doi": paper["doi"], "error": str(e), "elapsed": time.time() - start}


def load_existing_triage() -> dict:
    """Load existing triage results."""
    if TRIAGE_FILE.exists():
        with open(TRIAGE_FILE) as f:
            return json.load(f)
    return {"papers": [], "summary": {}, "last_updated": None}


def save_triage(data: dict):
    """Save triage results."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(TRIAGE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=int, help="Triage N papers as test")
    parser.add_argument("--all", action="store_true", help="Triage all papers")
    parser.add_argument("--resume", action="store_true", help="Resume from last run")
    parser.add_argument("--doi", help="Triage single DOI")
    args = parser.parse_args()

    if not any([args.sample, args.all, args.resume, args.doi]):
        parser.print_help()
        return

    # Load existing
    existing = load_existing_triage()
    already_done = {p["doi"] for p in existing["papers"] if "error" not in p}

    print(f"Already triaged: {len(already_done)} papers")

    # Get papers to process
    if args.doi:
        pdf_path = PDF_DIR / args.doi.replace("/", "_") + ".pdf"
        papers = [{"doi": args.doi, "title": None, "abstract": None, "pdf_path": str(pdf_path)}]
    else:
        papers = get_papers_to_triage(already_done if args.resume else set())

    print(f"Papers to triage: {len(papers)}")

    if args.sample:
        papers = papers[:args.sample]
        print(f"Sampling {len(papers)} papers")

    if not papers:
        print("No papers to triage.")
        return

    # Initialize client
    client = get_client()

    # Process papers
    results = existing["papers"] if args.resume else []
    total_cost = sum(p.get("cost_usd", 0) for p in results)

    for i, paper in enumerate(papers):
        print(f"\n[{i+1}/{len(papers)}] {paper['doi'][:50]}...")

        result = triage_paper(client, paper)
        results.append(result)

        if "error" in result:
            print(f"  ERROR: {result['error']}")
        else:
            print(f"  Type: {result.get('article_type')} ({result.get('subtype')})")
            print(f"  Confidence: {result.get('confidence')}")
            print(f"  Tables: {result.get('estimated_n_tables')}")
            print(f"  Cost: ${result.get('cost_usd', 0):.4f}")
            total_cost += result.get("cost_usd", 0)

        # Save incrementally
        if (i + 1) % 10 == 0:
            summary = {}
            for r in results:
                if "article_type" in r:
                    t = r["article_type"]
                    summary[t] = summary.get(t, 0) + 1

            save_triage({
                "papers": results,
                "summary": summary,
                "total_cost": round(total_cost, 4),
                "last_updated": datetime.now(timezone.utc).isoformat(),
            })
            print(f"  [Saved checkpoint: {len(results)} papers]")

        # Rate limiting
        time.sleep(0.5)

    # Final save
    summary = {}
    for r in results:
        if "article_type" in r:
            t = r["article_type"]
            summary[t] = summary.get(t, 0) + 1

    save_triage({
        "papers": results,
        "summary": summary,
        "total_cost": round(total_cost, 4),
        "last_updated": datetime.now(timezone.utc).isoformat(),
    })

    print(f"\n{'='*60}")
    print("TRIAGE SUMMARY")
    print(f"{'='*60}")
    print(f"Total papers: {len(results)}")
    print(f"Total cost: ${total_cost:.4f}")
    print("\nBy article type:")
    for t, count in sorted(summary.items(), key=lambda x: -x[1]):
        print(f"  {t}: {count}")
    print(f"\nSaved to: {TRIAGE_FILE}")


if __name__ == "__main__":
    main()
