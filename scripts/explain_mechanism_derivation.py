"""
Panel Derivation Explorer
=========================

Surfaces the deep panel-sourced mechanism derivation text (panel_reasoning_excerpt)
from templates, matched to a natural language query.

This shows:
  - The expert panel's explanation of WHY a mechanism works
  - The causal derivation leading to a mechanism chain
  - Source documents the panel used

Run:
    python3 scripts/explain_mechanism_derivation.py "why is wood restorative"
    python3 scripts/explain_mechanism_derivation.py "stress recovery" --templates SRT1 MAT4
    python3 scripts/explain_mechanism_derivation.py "involuntary attention" --all-steps
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path
from typing import List, Dict, Optional, Tuple

TEMPLATE_DIR = Path("data/templates")

# Map mechanism: node theory_ids → template filenames to try
THEORY_TO_TEMPLATES: Dict[str, List[str]] = {
    "attention_restoration_theory":  ["DT_DIRECTED_ATTENTION_001.json", "VIEW1.json"],
    "stress_recovery_theory":        ["SRT1.json", "MAT4_natural_material_convergence.json"],
    "biophilic_design":              ["MAT4_natural_material_convergence.json", "VIEW1.json"],
    "circadian_regulation":          ["L3_daylight_multichannel_convergence.json"],
    "neuromodulatory":               ["NM2.json", "NM3.json"],
    "DMN_TPN_DYNAMICS":              ["DT1.json"],
}

# Also search all templates when keyword-matching
OUTCOME_KEYWORDS = [
    "restorative", "restoration", "wood", "plants", "biophilia",
    "attention", "stress", "cortisol", "sympathetic", "amygdala",
    "involuntary", "fascination", "daylight", "circadian", "social",
    "olfactory", "smell", "terpene", "natural material",
]


def load_template(filename: str) -> Optional[Dict]:
    path = TEMPLATE_DIR / filename
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        import logging; logging.getLogger(__name__).debug(f"Returning None: {e}")
        return None


def score_template_for_query(template: Dict, query_words: set) -> float:
    """Score how relevant a template is to the query."""
    score = 0.0
    name = template.get("name", "").lower()
    excerpt = template.get("panel_reasoning_excerpt", "").lower()
    chain = " ".join(
        str(s) for s in
        (template.get("mechanism_chain") or [])
        + [l.get("from_variable", "") + " " + l.get("to_variable", "")
           for l in (template.get("causal_links") or [])]
    ).lower()

    for w in query_words:
        if w in name:
            score += 2.0
        if w in chain:
            score += 1.5
        if w in excerpt:
            score += 1.0

    return score


def find_relevant_templates(query: str, explicit: Optional[List[str]] = None) -> List[Tuple[str, Dict, float]]:
    """Return (filename, template_data, score) for relevant templates."""
    results = []

    if explicit:
        for name in explicit:
            fname = name if name.endswith(".json") else name + ".json"
            t = load_template(fname)
            if t:
                results.append((fname, t, 99.0))
            else:
                print(f"  Warning: template '{fname}' not found", file=sys.stderr)
        return results

    query_words = {w.lower() for w in query.split() if len(w) > 3}

    for f in sorted(TEMPLATE_DIR.glob("*.json")):
        try:
            t = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Skipped: {e}")
            continue
        if t.get("dedup_status") not in ("active", None):
            continue
        if not t.get("panel_reasoning_excerpt") and not t.get("mechanism_chain") and not t.get("causal_links"):
            continue
        score = score_template_for_query(t, query_words)
        if score > 1.0:
            results.append((f.name, t, score))

    return sorted(results, key=lambda x: -x[2])[:5]


def render_template_derivation(filename: str, t: Dict, score: float, all_steps: bool = False) -> str:
    lines = []
    tid = t.get("template_id", filename)
    name = t.get("name", "?")

    lines.append(f"{'=' * 70}")
    lines.append(f"TEMPLATE: {tid}")
    lines.append(f"  {name}")
    lines.append(f"  Relevance score: {score:.1f}")

    # Source documents
    panel_source = t.get("panel_source", "")
    panel_docs = t.get("panel_docs", [])
    if panel_source:
        lines.append(f"  Panel source: {panel_source}")
    if panel_docs:
        lines.append(f"  Source docs: {', '.join(panel_docs[:3])}")

    lines.append("")

    # Structural pattern (concise summary of the chain)
    sp = t.get("structural_pattern")
    if sp:
        lines.append(f"STRUCTURAL PATTERN:")
        lines.append(f"  {sp}")
        lines.append("")

    # Higher-order principle
    hop = t.get("higher_order_principle")
    if hop:
        lines.append(f"HIGHER-ORDER PRINCIPLE:")
        for line in textwrap.wrap(hop, width=70):
            lines.append(f"  {line}")
        lines.append("")

    # Mechanism chain (ordered steps)
    chain = t.get("mechanism_chain", [])
    if chain:
        lines.append("MECHANISM CHAIN (from template):")
        for i, step in enumerate(chain, 1):
            step_str = str(step) if isinstance(step, str) else json.dumps(step)
            for line in textwrap.wrap(step_str, width=68, initial_indent=f"  {i}. ", subsequent_indent="     "):
                lines.append(line)
        lines.append("")

    # Causal links
    links = t.get("causal_links", [])
    if links:
        lines.append("CAUSAL LINKS:")
        for lk in links:
            frm = lk.get("from_variable") or lk.get("from_entity", "?")
            to = lk.get("to_variable") or lk.get("to_entity", "?")
            act = lk.get("activity", "→")
            ev = lk.get("evidence_base", "")
            lines.append(f"  {frm} --[{act}]--> {to}")
            if ev:
                lines.append(f"    Evidence: {ev}")
        lines.append("")

    # Panel reasoning excerpt — this is the deep derivation text
    excerpt = t.get("panel_reasoning_excerpt", "")
    if excerpt:
        lines.append("PANEL DERIVATION (expert reasoning source):")
        lines.append(f"  [Source: {t.get('excerpt_source', 'unknown')}]")
        lines.append("")
        # Show first 2000 chars by default, full if --all-steps
        max_chars = len(excerpt) if all_steps else 2000
        display = excerpt[:max_chars]
        if len(excerpt) > max_chars:
            display += f"\n  ... [{len(excerpt) - max_chars} more chars — run with --all-steps to see full text]"
        for line in display.split("\n"):
            lines.append(f"  {line}")
        lines.append("")

    # Key references
    refs = t.get("key_references", [])
    if refs:
        lines.append("KEY REFERENCES:")
        for r in refs[:5]:
            if isinstance(r, dict):
                cit = r.get("citation") or r.get("id", str(r))
            else:
                cit = str(r)
            lines.append(f"  • {cit}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Show deep panel-sourced mechanism derivation from templates"
    )
    parser.add_argument(
        "query",
        nargs="?",
        default="wood restorative stress recovery",
        help="Natural language query to find relevant templates",
    )
    parser.add_argument(
        "--templates", "-t",
        nargs="+",
        metavar="TEMPLATE_ID",
        help="Specific template IDs to show (e.g. SRT1 MAT4 DT_DIRECTED_ATTENTION_001)",
    )
    parser.add_argument(
        "--all-steps",
        action="store_true",
        help="Show full panel_reasoning_excerpt (can be very long)",
    )
    args = parser.parse_args()

    print(f"\nPanel Derivation Explorer")
    print(f"Query: '{args.query}'")
    print()

    results = find_relevant_templates(args.query, explicit=args.templates)

    if not results:
        print("No relevant templates found. Try broader keywords or use --templates.")
        return

    print(f"Found {len(results)} relevant template(s):\n")
    for filename, t, score in results:
        print(render_template_derivation(filename, t, score, all_steps=args.all_steps))


if __name__ == "__main__":
    main()
