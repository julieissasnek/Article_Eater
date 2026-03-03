#!/usr/bin/env python3
"""
generate_t3_scholar_queries.py — Generate Google Scholar queries from T3 beliefs
=================================================================================

Reads extraction findings and generates targeted Scholar search queries
to find confirmations, disconfirmations, and extensions of existing beliefs.

Output formats:
  1. Scholar queries (copy-pasteable into Google Scholar AI)
  2. Zotero search prompts (for HITL workflow)
  3. DOI lookup queries (for API-based acquisition)

Usage:
  python scripts/generate_t3_scholar_queries.py                # all beliefs
  python scripts/generate_t3_scholar_queries.py --theory ART   # filter by theory
  python scripts/generate_t3_scholar_queries.py --limit 20     # top 20 by priority
  python scripts/generate_t3_scholar_queries.py --format zotero # Zotero prompts

Author: AG (Antigravity)
Date: 2026-03-02
"""

import json
import glob
import argparse
import sys
import re
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
from typing import List, Dict, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def load_findings(theory_filter: Optional[str] = None) -> List[Dict]:
    """Load all extraction findings, optionally filtered by theory."""
    findings = []
    for f in sorted(glob.glob(str(PROJECT_ROOT / "data" / "extractions" / "*.json"))):
        try:
            with open(f) as fh:
                d = json.load(fh)
            doi = d.get("doi", "")
            title = d.get("title", "")
            theories_raw = d.get("theory_commitments", []) or d.get("theory_links", [])
            # Flatten to strings
            theories = []
            for t in (theories_raw if isinstance(theories_raw, list) else [theories_raw]):
                if isinstance(t, dict):
                    theories.append(t.get("theory_name", t.get("name", str(t))))
                elif isinstance(t, str):
                    theories.append(t)

            for finding in d.get("findings", []):
                ant = finding.get("antecedent", "")
                cons = finding.get("consequent", "")
                direction = finding.get("direction", "")
                p_val = finding.get("p_value")
                effect = finding.get("effect_size")
                sample = finding.get("sample_size")

                if not ant or not cons:
                    continue

                # Priority scoring: beliefs with partial evidence are most valuable to expand
                priority = 0
                if p_val and p_val < 0.05:
                    priority += 1  # Statistically significant — worth confirming
                if effect and abs(float(effect)) > 0.5:
                    priority += 1  # Large effect — high-value confirmation
                if sample and int(sample) < 50:
                    priority += 2  # Small sample — MOST needs replication
                if not p_val and not effect:
                    priority += 1  # Missing stats — needs quantification

                f_theories = finding.get("theory_commitments", theories) or []
                if isinstance(f_theories, str):
                    f_theories = [f_theories]
                # Flatten dicts to strings if needed
                f_theories = [
                    (t.get("name", str(t)) if isinstance(t, dict) else str(t))
                    for t in f_theories
                ]

                if theory_filter and not any(theory_filter.lower() in t.lower() for t in f_theories):
                    continue

                findings.append({
                    "antecedent": ant,
                    "consequent": cons,
                    "direction": direction,
                    "priority": priority,
                    "p_value": p_val,
                    "effect_size": effect,
                    "sample_size": sample,
                    "doi": doi,
                    "source_title": title,
                    "theories": f_theories,
                })
        except Exception:
            continue

    # Sort by priority (highest first)
    findings.sort(key=lambda x: x["priority"], reverse=True)
    return findings


def generate_scholar_query(finding: Dict) -> str:
    """Convert a finding into a Google Scholar search query."""
    ant = finding["antecedent"]
    cons = finding["consequent"]

    # Clean up for search
    ant_clean = re.sub(r'[^\w\s]', '', ant)[:60].strip()
    cons_clean = re.sub(r'[^\w\s]', '', cons)[:60].strip()

    # Extract key noun phrases (simplified)
    ant_words = [w for w in ant_clean.split() if len(w) > 3][:4]
    cons_words = [w for w in cons_clean.split() if len(w) > 3][:4]

    query = f'"{" ".join(ant_words[:2])}" "{" ".join(cons_words[:2])}"'

    # Add theory context if available
    if finding.get("theories"):
        theory = finding["theories"][0]
        # Map theory names to search terms
        theory_terms = {
            "ART": "attention restoration",
            "SRT": "stress reduction",
            "biophilia": "biophilia nature",
            "predictive_processing": "predictive processing",
            "prospect-refuge": "prospect refuge",
            "place_attachment": "place attachment",
            "BRECVEMA": "music emotion",
            "embodied_cognition": "embodied cognition",
        }
        t_term = theory_terms.get(theory, theory.replace("_", " "))
        query += f' {t_term}'

    return query


def generate_confirmation_query(finding: Dict) -> str:
    """Generate query specifically seeking CONFIRMING evidence."""
    base = generate_scholar_query(finding)
    return f'{base} meta-analysis systematic review'


def generate_disconfirmation_query(finding: Dict) -> str:
    """Generate query seeking DISCONFIRMING evidence (replication failures, critiques)."""
    ant_words = finding["antecedent"].split()[:3]
    cons_words = finding["consequent"].split()[:3]
    return f'{" ".join(ant_words)} {" ".join(cons_words)} replication failure critique null result'


def generate_citation_graph_query(finding: Dict) -> str:
    """Generate query for citation graph exploration."""
    if finding.get("doi"):
        return f'cites:{finding["doi"]}'
    return f'{finding["antecedent"][:50]} {finding["consequent"][:50]} cited by'


def main():
    parser = argparse.ArgumentParser(description="Generate Scholar queries from T3 beliefs")
    parser.add_argument("--theory", type=str, help="Filter by theory (e.g., ART, SRT)")
    parser.add_argument("--limit", type=int, default=30, help="Max queries to generate")
    parser.add_argument("--format", choices=["scholar", "zotero", "elicit", "all"], default="all")
    parser.add_argument("--output", type=str, help="Output file (default: stdout + file)")
    args = parser.parse_args()

    findings = load_findings(theory_filter=args.theory)
    findings = findings[:args.limit]

    print(f"\n{'='*70}")
    print(f"T3 BELIEF SCHOLAR QUERY GENERATOR")
    print(f"{'='*70}")
    print(f"Total findings loaded: {len(findings)}")
    if args.theory:
        print(f"Filtered to theory: {args.theory}")
    print()

    # Theory distribution
    theory_counts = Counter()
    for f in findings:
        for t in f.get("theories", []):
            theory_counts[t] += 1
    if theory_counts:
        print("Theory distribution in queries:")
        for t, c in theory_counts.most_common(10):
            print(f"  {t}: {c}")
        print()

    scholar_queries = []
    zotero_queries = []
    elicit_queries = []

    for i, finding in enumerate(findings, 1):
        ant = finding["antecedent"][:80]
        cons = finding["consequent"][:80]
        priority_stars = "⭐" * min(finding["priority"], 5)

        # Scholar queries
        q_confirm = generate_confirmation_query(finding)
        q_disconfirm = generate_disconfirmation_query(finding)
        q_cite = generate_citation_graph_query(finding)

        scholar_queries.append({
            "index": i,
            "belief": f"{ant} → {cons}",
            "direction": finding["direction"],
            "priority": finding["priority"],
            "confirm_query": q_confirm,
            "disconfirm_query": q_disconfirm,
            "citation_query": q_cite,
            "theories": finding["theories"],
            "source_doi": finding["doi"],
        })

        # Elicit format
        elicit_q = f'Does {ant.lower()} affect {cons.lower()}? What is the evidence?'
        elicit_queries.append(elicit_q)

        # Zotero format
        zotero_q = generate_scholar_query(finding)
        zotero_queries.append(zotero_q)

        if args.format in ("scholar", "all"):
            print(f"[{i}/{len(findings)}] {priority_stars}")
            print(f"  Belief: {ant} → {cons} ({finding['direction']})")
            print(f"  📗 Confirm:    {q_confirm}")
            print(f"  📕 Disconfirm: {q_disconfirm}")
            if finding["doi"]:
                print(f"  📊 Citations:  {q_cite}")
            print()

    # Save outputs
    output_dir = PROJECT_ROOT / "data" / "acquisition"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Scholar queries JSON
    out_scholar = output_dir / "t3_scholar_queries.json"
    with open(out_scholar, "w") as f:
        json.dump({
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "theory_filter": args.theory,
            "total_queries": len(scholar_queries),
            "queries": scholar_queries,
        }, f, indent=2)
    print(f"\n✅ Scholar queries saved: {out_scholar}")

    # Elicit batch file
    out_elicit = output_dir / "t3_elicit_batch.txt"
    with open(out_elicit, "w") as f:
        for q in elicit_queries:
            f.write(q + "\n")
    print(f"✅ Elicit batch saved: {out_elicit}")

    # Zotero/Scholar search list
    out_zotero = output_dir / "t3_zotero_searches.txt"
    with open(out_zotero, "w") as f:
        for q in zotero_queries:
            f.write(q + "\n")
    print(f"✅ Zotero/Scholar searches saved: {out_zotero}")

    # Google Scholar AI prompt
    out_prompt = output_dir / "t3_google_scholar_ai_prompt.md"
    with open(out_prompt, "w") as f:
        f.write("# Google Scholar AI — T3 Belief Verification Queries\n\n")
        f.write(f"Generated: {datetime.now(timezone.utc).isoformat()}\n\n")
        f.write("## Instructions\n")
        f.write("1. Open Google Scholar AI (scholar.google.com with AI Overview enabled)\n")
        f.write("2. Paste each query below\n")
        f.write("3. If Scholar shows a paper you can access, download PDF\n")
        f.write("4. Drop PDF in `data/pdfs_incoming/` for auto-ingestion\n")
        f.write("5. Or add to Zotero → sync\n\n")
        f.write("## Priority Queries (highest value for evidence expansion)\n\n")
        for sq in scholar_queries[:20]:
            f.write(f"### Query {sq['index']}: {sq['belief'][:80]}\n")
            f.write(f"- **Confirm**: `{sq['confirm_query']}`\n")
            f.write(f"- **Disconfirm**: `{sq['disconfirm_query']}`\n")
            if sq['source_doi']:
                f.write(f"- **Citing papers**: `{sq['citation_query']}`\n")
            f.write(f"- Theories: {', '.join(sq['theories'][:3])}\n\n")
    print(f"✅ Google Scholar AI prompt saved: {out_prompt}")

    print(f"\n{'='*70}")
    print(f"WORKFLOW: Copy queries → Google Scholar AI → Download PDFs → data/pdfs_incoming/")
    print(f"The auto_ingest_pdfs.py script will handle extraction → integration → Overseer.")
    print(f"{'='*70}")


if __name__ == "__main__":
    sys.exit(main() or 0)
