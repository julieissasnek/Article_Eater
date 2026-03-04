#!/usr/bin/env python3
"""
Card Model Comparison — Head-to-Head Quality Test
===================================================

Generates the SAME 5 belief cluster cards using whatever LLM model
is currently configured. Saves output with a model label so you can
compare side-by-side.

Usage:
    # Round 1: Generate with current model
    python3 scripts/card_model_comparison.py --model-label "sonnet_3_5"

    # Round 2: Switch model in your environment, run again
    python3 scripts/card_model_comparison.py --model-label "opus"

    # Round 3: Another model
    python3 scripts/card_model_comparison.py --model-label "gpt4o"

    # Compare all rounds side-by-side
    python3 scripts/card_model_comparison.py --compare
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
COMPARISON_DIR = PROJECT_ROOT / "data" / "model_comparison"
CLUSTERS_PATH = PROJECT_ROOT / "data" / "materialized_views" / "belief_clusters.json"

# Pick 5 representative clusters: diverse topics, varying sizes
TEST_CLUSTER_INDICES = [0, 50, 200, 500, 1000]


def load_test_clusters() -> list:
    with open(CLUSTERS_PATH) as f:
        data = json.load(f)
    clusters = data.get("clusters", [])
    selected = []
    for idx in TEST_CLUSTER_INDICES:
        if idx < len(clusters):
            selected.append(clusters[idx])
    return selected


def generate_card_prompt(cluster: dict) -> str:
    """Build a prompt for generating a rich belief card from cluster data."""
    ant = cluster.get("antecedent_theme", "?")
    cons = cluster.get("consequent_theme", "?")
    n_findings = cluster.get("n_findings", 0)
    n_papers = cluster.get("n_papers", 0)
    direction = cluster.get("direction_consensus", "mixed")
    theories = cluster.get("theory_links", [])
    effect = cluster.get("mean_effect_size")
    samples = cluster.get("sample_members", [])[:5]

    sample_text = ""
    for s in samples:
        sample_text += f"\n  - {s.get('antecedent', '?')} → {s.get('consequent', '?')} (direction: {s.get('direction', '?')})"

    prompt = f"""You are a science writer for a research synthesis system in architectural/environmental psychology.

Write a RICH, ENGAGING belief card for this evidence cluster. Follow these rules:
- Write as if explaining to an intelligent researcher colleague
- Use the confidence language appropriate to the evidence strength
- NEVER say "interestingly" or "it is worth noting"
- Use specific hedging: "the evidence suggests" for moderate confidence, "preliminary evidence hints at" for low
- Include a concrete, vivid example that illustrates the finding
- Explain WHY this finding matters for design
- Be fresh and specific — do NOT use templated phrases

Evidence Cluster:
- Relationship: {ant} → {cons}
- Direction: {direction}
- Findings: {n_findings} from {n_papers} papers
- Mean effect size: {effect or 'not reported'}
- Theory links: {', '.join(theories[:3]) if theories else 'none identified'}
- Sample findings:{sample_text}

Generate three levels:
1. L1 CARD (150-200 words): The core finding, confidence level, one good example
2. L2 CARD (300-400 words): Mechanisms, warrants, design implications
3. L3 DEEP READ (500-700 words): Full analysis with examples, caveats, practical applications, what we still don't know

Format as JSON:
{{"l1": "...", "l2": "...", "l3": "..."}}
"""
    return prompt


def generate_with_gemini(prompt: str) -> dict:
    """Generate using Gemini API."""
    try:
        import google.generativeai as genai
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return {"error": "GEMINI_API_KEY not set"}
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        text = response.text
        # Try to parse JSON from response
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        return json.loads(text)
    except Exception as e:
        return {"error": str(e)}


def generate_without_llm(cluster: dict) -> dict:
    """Data-only: what current system produces without LLM."""
    ant = cluster.get("antecedent_theme", "?")
    cons = cluster.get("consequent_theme", "?")
    n = cluster.get("n_findings", 0)
    np_ = cluster.get("n_papers", 0)
    d = cluster.get("direction_consensus", "mixed")
    return {
        "l1": (
            f"Research indicates a {d} relationship between {ant} and {cons}, "
            f"supported by {n} findings from {np_} papers in the corpus."
        ),
        "l2": "[PENDING — requires LLM]",
        "l3": "[PENDING — requires LLM]",
    }


def run_generation(model_label: str):
    COMPARISON_DIR.mkdir(parents=True, exist_ok=True)

    clusters = load_test_clusters()
    results = []

    print(f"\n{'='*60}")
    print(f"  Model Comparison — Round: {model_label}")
    print(f"  Generating {len(clusters)} test cards")
    print(f"{'='*60}\n")

    for i, cluster in enumerate(clusters):
        cid = cluster.get("cluster_id", f"cluster_{i}")
        ant = cluster.get("antecedent_theme", "?")
        cons = cluster.get("consequent_theme", "?")
        n = cluster.get("n_findings", 0)

        print(f"  [{i+1}/{len(clusters)}] {ant} → {cons} ({n} findings)...")

        prompt = generate_card_prompt(cluster)

        start = time.time()

        # Try Gemini if available, otherwise data-only
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            try:
                import google.generativeai  # noqa: F401
                card = generate_with_gemini(prompt)
                method = "gemini"
            except ImportError:
                card = generate_without_llm(cluster)
                method = "data_only"
                print(f"    ⚠ google.generativeai not installed — using data-only")
        else:
            card = generate_without_llm(cluster)
            method = "data_only"
            print(f"    ⚠ No GEMINI_API_KEY — using data-only generation")

        elapsed = time.time() - start

        result = {
            "cluster_id": cid,
            "antecedent": ant,
            "consequent": cons,
            "n_findings": n,
            "model_label": model_label,
            "method": method,
            "elapsed_ms": round(elapsed * 1000, 1),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "prompt_length": len(prompt),
            "card": card,
        }
        results.append(result)

        # Preview
        l1 = card.get("l1", card.get("error", "?"))
        print(f"    ✓ L1 ({len(l1)} chars): {l1[:80]}...")
        print()

    # Save
    outpath = COMPARISON_DIR / f"round_{model_label}.json"
    with open(outpath, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  Saved to {outpath}")

    return results


def run_comparison():
    """Compare all saved rounds side by side."""
    if not COMPARISON_DIR.exists():
        print("No comparison data yet. Run --model-label first.")
        return

    rounds = {}
    for f in sorted(COMPARISON_DIR.glob("round_*.json")):
        label = f.stem.replace("round_", "")
        with open(f) as fh:
            rounds[label] = json.load(fh)

    if not rounds:
        print("No rounds found. Run --model-label first.")
        return

    print(f"\n{'='*70}")
    print(f"  MODEL COMPARISON — {len(rounds)} rounds")
    print(f"{'='*70}\n")

    # For each test cluster, show all model outputs
    first = list(rounds.values())[0]
    for i, _ in enumerate(first):
        cluster_name = first[i].get("antecedent", "?") + " → " + first[i].get("consequent", "?")
        n = first[i].get("n_findings", 0)
        print(f"\n{'─'*70}")
        print(f"  Cluster: {cluster_name} ({n} findings)")
        print(f"{'─'*70}")

        for label, results in rounds.items():
            if i < len(results):
                r = results[i]
                card = r.get("card", {})
                l1 = card.get("l1", card.get("error", "N/A"))
                ms = r.get("elapsed_ms", "?")
                print(f"\n  ▸ [{label}] ({ms}ms, {r.get('method', '?')}):")
                print(f"    L1: {l1[:200]}")
                if card.get("l2") and card["l2"] != "[PENDING — requires LLM]":
                    print(f"    L2: {card['l2'][:200]}...")
                print()

    # Summary table
    print(f"\n{'='*70}")
    print(f"  SUMMARY")
    print(f"{'='*70}")
    print(f"  {'Model':<20} {'Avg L1 Len':>10} {'Avg Latency':>12} {'Method':>12}")
    for label, results in rounds.items():
        l1_lens = [len(r.get("card", {}).get("l1", "")) for r in results]
        latencies = [r.get("elapsed_ms", 0) for r in results]
        avg_len = sum(l1_lens) / max(len(l1_lens), 1)
        avg_lat = sum(latencies) / max(len(latencies), 1)
        method = results[0].get("method", "?") if results else "?"
        print(f"  {label:<20} {avg_len:>10.0f} {avg_lat:>10.0f}ms {method:>12}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Card Model Comparison")
    parser.add_argument("--model-label", type=str, help="Label for this round (e.g. 'sonnet_3_5')")
    parser.add_argument("--compare", action="store_true", help="Compare all saved rounds")
    args = parser.parse_args()

    if args.compare:
        run_comparison()
    elif args.model_label:
        run_generation(args.model_label)
    else:
        parser.print_help()
