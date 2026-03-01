#!/usr/bin/env python3
"""
AI Search Prompt Generator — create clipboard-ready prompts for AI search tools.

Takes open research targets from the queue and generates tailored prompts for:
- Elicit (structured research question)
- Scholar GPT / ChatGPT (conversational with domain context)
- Consensus (claim-style query)
- Scholar AI (keyword + context)
- Google Scholar AI mode (natural language)

Usage:
  python scripts/generate_ai_search_prompts.py              # Write to data/production/
  python scripts/generate_ai_search_prompts.py --top 10     # Limit to top 10 gaps
  python scripts/generate_ai_search_prompts.py --output FILE
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

STATE_DIR = PROJECT_ROOT / "data" / "production"
QUEUE_STATE = STATE_DIR / "research_queue_state.json"
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"


def load_open_targets() -> list[dict[str, Any]]:
    """Load open/searching research targets from queue state."""
    if not QUEUE_STATE.exists():
        return []
    data = json.loads(QUEUE_STATE.read_text(encoding="utf-8"))
    targets = []
    for t in data.get("targets", []):
        if t.get("status") in ("open", "searching"):
            targets.append(t)
    # Sort by priority score descending
    targets.sort(key=lambda t: t.get("priority_score", 0), reverse=True)
    return targets


def load_mechanism_terms() -> list[str]:
    """Sample mechanism terms from templates for context enrichment."""
    terms: set[str] = set()
    if not TEMPLATES_DIR.exists():
        return []
    for f in list(TEMPLATES_DIR.glob("*.json"))[:20]:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            for mc in data.get("mechanism_claims", []):
                stmt = mc.get("statement", "")
                if stmt:
                    # Extract short mechanism phrases
                    words = stmt.split()[:6]
                    terms.add(" ".join(words))
        except Exception:
            continue
    return list(terms)[:15]


def generate_elicit_prompt(target: dict[str, Any]) -> str:
    """Structured research question for Elicit."""
    gap = target.get("gap_description", "")
    queries = target.get("suggested_queries", [])
    mechanisms = target.get("mechanism_predictions", [])

    prompt = f"Research question: {gap}\n"
    if mechanisms:
        prompt += f"Mechanism keywords: {', '.join(mechanisms[:3])}\n"
    prompt += "\nPlease find empirical studies (experimental or quasi-experimental) "
    prompt += "that measure the effect described above. Prioritize studies with "
    prompt += "quantitative data (effect sizes, p-values, confidence intervals). "
    prompt += "Focus on built environment, environmental psychology, and neuroarchitecture.\n"
    if queries:
        prompt += f"\nAlternative search terms: {'; '.join(queries[:3])}"
    return prompt


def generate_scholar_gpt_prompt(target: dict[str, Any]) -> str:
    """Conversational prompt for Scholar GPT / ChatGPT."""
    gap = target.get("gap_description", "")
    mechanisms = target.get("mechanism_predictions", [])

    prompt = (
        f"I'm researching the intersection of architecture, environmental psychology, "
        f"and neuroscience. I need to find research papers about:\n\n"
        f"**{gap}**\n\n"
    )
    if mechanisms:
        prompt += f"Relevant mechanisms: {', '.join(mechanisms[:3])}\n\n"
    prompt += (
        "Please find 5-10 peer-reviewed papers that provide empirical evidence "
        "on this topic. For each paper, provide:\n"
        "1. Full citation (authors, year, title, journal)\n"
        "2. DOI\n"
        "3. Key finding relevant to my question\n"
        "4. Sample size and method\n\n"
        "Prioritize recent (2015+) experimental or quasi-experimental studies. "
        "Include meta-analyses if available."
    )
    return prompt


def generate_consensus_prompt(target: dict[str, Any]) -> str:
    """Claim-style query for Consensus."""
    gap = target.get("gap_description", "")
    # Consensus works best with claim-like statements
    # Convert question-form to assertion-form
    claim = gap.replace("?", "").strip()
    if not claim.endswith("."):
        claim += "."
    return claim


def generate_scholar_ai_prompt(target: dict[str, Any]) -> str:
    """Keyword + context format for Scholar AI."""
    gap = target.get("gap_description", "")
    queries = target.get("suggested_queries", [])
    cross_field = target.get("cross_field_terms", [])

    parts = [gap]
    if cross_field:
        parts.append(f"Cross-field terms: {', '.join(cross_field[:3])}")
    if queries:
        parts.append(f"Related queries: {'; '.join(queries[:2])}")
    parts.append(
        "Domain: built environment, environmental psychology, neuroarchitecture. "
        "Provide DOIs for all results."
    )
    return "\n".join(parts)


def generate_google_scholar_prompt(target: dict[str, Any]) -> str:
    """Natural language query for Google Scholar AI mode."""
    gap = target.get("gap_description", "")
    mechanisms = target.get("mechanism_predictions", [])

    prompt = gap
    if mechanisms:
        prompt += f" involving {', '.join(mechanisms[:2])}"
    prompt += " in built environment architecture"
    return prompt


def render_prompts(targets: list[dict[str, Any]], top: int = 0) -> str:
    """Render all prompts as a markdown document."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    if top > 0:
        targets = targets[:top]

    lines: list[str] = []
    lines.append("# AI Search Prompts")
    lines.append("")
    lines.append(f"> Generated: **{now}**")
    lines.append(f"> Open research targets: **{len(targets)}**")
    lines.append("")
    lines.append("Copy-paste each prompt into the corresponding AI search tool.")
    lines.append("Mark targets as `found` in the research queue once papers are located.")
    lines.append("")

    for i, target in enumerate(targets, 1):
        tid = target.get("target_id", f"target_{i}")
        gap = target.get("gap_description", "Unknown gap")
        priority = target.get("priority_score", 0)

        lines.append(f"---")
        lines.append("")
        lines.append(f"## {i}. {gap[:80]}")
        lines.append(f"**Target ID:** `{tid}` | **Priority:** {priority:.2f}")
        lines.append("")

        lines.append("### 🔬 Elicit")
        lines.append("```")
        lines.append(generate_elicit_prompt(target))
        lines.append("```")
        lines.append("")

        lines.append("### 🤖 Scholar GPT / ChatGPT")
        lines.append("```")
        lines.append(generate_scholar_gpt_prompt(target))
        lines.append("```")
        lines.append("")

        lines.append("### ✅ Consensus")
        lines.append("```")
        lines.append(generate_consensus_prompt(target))
        lines.append("```")
        lines.append("")

        lines.append("### 📚 Scholar AI")
        lines.append("```")
        lines.append(generate_scholar_ai_prompt(target))
        lines.append("```")
        lines.append("")

        lines.append("### 🔍 Google Scholar AI")
        lines.append("```")
        lines.append(generate_google_scholar_prompt(target))
        lines.append("```")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", "-o", type=Path, help="Output file path")
    parser.add_argument("--top", type=int, default=0, help="Limit to top N targets")
    args = parser.parse_args()

    targets = load_open_targets()
    if not targets:
        print("No open research targets in queue.")
        return 0

    content = render_prompts(targets, args.top)

    if args.output:
        out_path = args.output
    else:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        out_path = STATE_DIR / f"ai_search_prompts_{date_str}.md"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    print(f"✅  Wrote prompts for {len(targets)} targets to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
