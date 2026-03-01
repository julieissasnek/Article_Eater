#!/usr/bin/env python3
"""
Acquisition Digest — generate a shareable report of papers needing PDFs.

Scans research queue state, scholar expansion candidates, and snowball
candidates to produce a prioritized markdown file listing articles that
still need manual PDF retrieval.

Usage:
  python scripts/acquisition_digest.py                      # Write to data/production/
  python scripts/acquisition_digest.py --output FILE        # Custom output path
  python scripts/acquisition_digest.py --top 20             # Limit to top N
  python scripts/acquisition_digest.py --format dois        # DOI-only list (for Zotero import)
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

# ── Sources ──
STATE_DIR = PROJECT_ROOT / "data" / "production"
SCHOLAR_CANDIDATES = PROJECT_ROOT / "data" / "extractions" / "scholar_expansion_candidates.json"
SNOWBALL_CANDIDATES = PROJECT_ROOT / "data" / "extractions" / "snowball_candidates.json"
QUEUE_STATE = STATE_DIR / "research_queue_state.json"

# ── Already-downloaded PDFs ──
PDF_DIRS = [
    PROJECT_ROOT / "data" / "papers",
    PROJECT_ROOT / "data" / "pdfs",
]


def _existing_pdf_dois() -> set[str]:
    """Collect DOIs from PDF filenames (often DOI-encoded as filename)."""
    dois: set[str] = set()
    for d in PDF_DIRS:
        if not d.exists():
            continue
        for f in d.rglob("*.pdf"):
            # Try extracting DOI from filename patterns like 10.1234_foo.pdf
            name = f.stem.replace("_", "/", 1)
            if name.startswith("10."):
                dois.add(name.lower())
    return dois


def _load_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    return data.get("candidates", data.get("items", []))


def collect_needing_pdfs(existing_dois: set[str]) -> list[dict[str, Any]]:
    """Gather all candidate articles that don't have PDFs yet."""
    seen: dict[str, dict[str, Any]] = {}

    # Scholar expansion candidates
    for item in _load_json_list(SCHOLAR_CANDIDATES):
        doi = (item.get("doi") or "").strip().lower()
        if doi and doi not in existing_dois and doi not in seen:
            seen[doi] = {
                "doi": doi,
                "title": item.get("title", ""),
                "authors": item.get("authors", []),
                "year": item.get("year"),
                "venue": item.get("venue", item.get("journal", "")),
                "citations": item.get("citation_count", item.get("citationCount", 0)),
                "relevance": item.get("relevance_score", item.get("relevance", 0)),
                "source": "scholar_expansion",
                "gap_description": "",
            }

    # Snowball candidates
    for item in _load_json_list(SNOWBALL_CANDIDATES):
        doi = (item.get("doi") or "").strip().lower()
        if doi and doi not in existing_dois and doi not in seen:
            seen[doi] = {
                "doi": doi,
                "title": item.get("title", ""),
                "authors": item.get("authors", []),
                "year": item.get("year"),
                "venue": item.get("venue", ""),
                "citations": item.get("citation_count", item.get("in_corpus_citations", 0)),
                "relevance": item.get("relevance_score", item.get("relevance", 0)),
                "source": "snowball",
                "gap_description": "",
            }

    # Research queue targets with found articles
    if QUEUE_STATE.exists():
        qdata = json.loads(QUEUE_STATE.read_text(encoding="utf-8"))
        for target in qdata.get("targets", []):
            gap_desc = target.get("gap_description", "")
            for sr in target.get("search_results", []):
                for art in sr.get("articles_found", []):
                    doi = (art.get("doi") or "").strip().lower()
                    if doi and doi not in existing_dois and doi not in seen:
                        seen[doi] = {
                            "doi": doi,
                            "title": art.get("title", ""),
                            "authors": art.get("authors", []),
                            "year": art.get("year"),
                            "venue": art.get("venue", ""),
                            "citations": 0,
                            "relevance": art.get("relevance_score", 0),
                            "source": "research_queue",
                            "gap_description": gap_desc,
                        }

    # Sort by relevance (desc), then citations (desc)
    results = sorted(seen.values(),
                     key=lambda x: (x.get("relevance") or 0, x.get("citations") or 0),
                     reverse=True)
    return results


def render_markdown(articles: list[dict[str, Any]], top: int = 0) -> str:
    """Render the acquisition digest as markdown."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    if top > 0:
        articles = articles[:top]

    lines: list[str] = []
    lines.append("# Article Acquisition Digest")
    lines.append("")
    lines.append(f"> Generated: **{now}**")
    lines.append(f"> Papers needing PDFs: **{len(articles)}**")
    lines.append("")
    lines.append("## How to use this list")
    lines.append("")
    lines.append("1. **Zotero**: Run `python scripts/zotero_push.py` to push these into your library,")
    lines.append("   then right-click → \"Find Available PDF\" in the Zotero desktop client")
    lines.append("2. **UCSD Library**: Search each DOI at [library.ucsd.edu](https://library.ucsd.edu)")
    lines.append("3. **Sci-Hub / LibGen**: As a last resort for paywalled articles")
    lines.append("4. **AI Tools**: Run `python scripts/generate_ai_search_prompts.py` for search prompts")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Priority tiers
    high = [a for a in articles if a.get("relevance", 0) >= 0.6]
    medium = [a for a in articles if 0.3 <= a.get("relevance", 0) < 0.6]
    low = [a for a in articles if a.get("relevance", 0) < 0.3]

    for tier, label, items in [
        ("🔴", "High Priority", high),
        ("🟡", "Medium Priority", medium),
        ("🟢", "Lower Priority", low),
    ]:
        if not items:
            continue
        lines.append(f"## {tier} {label} ({len(items)} papers)")
        lines.append("")
        lines.append("| # | DOI | Title | Year | Citations | Relevance | Source |")
        lines.append("|---|-----|-------|------|-----------|-----------|--------|")
        for i, art in enumerate(items, 1):
            doi = art.get("doi", "")
            doi_link = f"[{doi}](https://doi.org/{doi})"
            title = (art.get("title") or "")[:60]
            if len(art.get("title", "")) > 60:
                title += "…"
            year = art.get("year") or "?"
            cites = art.get("citations", 0)
            rel = f"{art.get('relevance', 0):.2f}"
            source = art.get("source", "")
            lines.append(f"| {i} | {doi_link} | {title} | {year} | {cites} | {rel} | {source} |")
        lines.append("")

    # DOI quick-copy section
    lines.append("---")
    lines.append("")
    lines.append("## DOI Quick-Copy (for Zotero / library search)")
    lines.append("")
    lines.append("```")
    for art in articles:
        lines.append(art.get("doi", ""))
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def render_dois_only(articles: list[dict[str, Any]], top: int = 0) -> str:
    if top > 0:
        articles = articles[:top]
    return "\n".join(a.get("doi", "") for a in articles if a.get("doi")) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", "-o", type=Path, help="Output file path")
    parser.add_argument("--top", type=int, default=0, help="Limit to top N papers (0=all)")
    parser.add_argument("--format", choices=["markdown", "dois"], default="markdown",
                        help="Output format")
    args = parser.parse_args()

    existing = _existing_pdf_dois()
    articles = collect_needing_pdfs(existing)

    if not articles:
        print("✅  No articles need PDFs — corpus is fully covered!")
        return 0

    if args.format == "dois":
        content = render_dois_only(articles, args.top)
        suffix = ".txt"
    else:
        content = render_markdown(articles, args.top)
        suffix = ".md"

    if args.output:
        out_path = args.output
    else:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        out_path = STATE_DIR / f"acquisition_digest_{date_str}{suffix}"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    print(f"✅  Wrote {len(articles)} articles to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
