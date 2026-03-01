#!/usr/bin/env python3
"""
Zotero Push — create items in your Zotero library from research queue candidates.

Uses the Zotero Web API v3 (via pyzotero) to push discovered articles so that
"Find Available PDF" can be used from the Zotero desktop client.

Setup:
  pip install pyzotero
  # Add to .env:
  ZOTERO_LIBRARY_ID=<your numeric user ID>
  ZOTERO_API_KEY=<your API key from zotero.org/settings/keys>
  ZOTERO_LIBRARY_TYPE=user  # or 'group'

Usage:
  python scripts/zotero_push.py                    # Push all un-pushed candidates
  python scripts/zotero_push.py --dry-run          # Preview without writing
  python scripts/zotero_push.py --from-dois FILE   # Push DOIs from a text file
  python scripts/zotero_push.py --status           # Show push statistics
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load .env file if present
_env_file = PROJECT_ROOT / ".env"
if _env_file.exists():
    for line in _env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())

# ── State file tracks which DOIs have already been pushed ──
STATE_DIR = PROJECT_ROOT / "data" / "production"
STATE_FILE = STATE_DIR / "zotero_push_state.json"

# ── Candidate sources ──
SCHOLAR_CANDIDATES = PROJECT_ROOT / "data" / "extractions" / "scholar_expansion_candidates.json"
SNOWBALL_CANDIDATES = PROJECT_ROOT / "data" / "extractions" / "snowball_candidates.json"
QUEUE_STATE = PROJECT_ROOT / "data" / "production" / "research_queue_state.json"


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def load_state() -> dict[str, Any]:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"pushed_dois": {}, "stats": {"total_pushed": 0, "last_push_at": None}}


def save_state(state: dict[str, Any]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")


# ---------------------------------------------------------------------------
# Candidate collection
# ---------------------------------------------------------------------------

def collect_candidates_from_files() -> list[dict[str, Any]]:
    """Gather un-pushed article candidates from all discovery outputs."""
    candidates: dict[str, dict[str, Any]] = {}  # keyed by DOI

    for path in (SCHOLAR_CANDIDATES, SNOWBALL_CANDIDATES):
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        items = data if isinstance(data, list) else data.get("candidates", [])
        for item in items:
            doi = (item.get("doi") or "").strip()
            if doi and doi not in candidates:
                candidates[doi] = {
                    "doi": doi,
                    "title": item.get("title", ""),
                    "authors": item.get("authors", []),
                    "year": item.get("year"),
                    "venue": item.get("venue", item.get("journal", "")),
                    "relevance": item.get("relevance_score", item.get("relevance", 0)),
                    "source": item.get("source", str(path.name)),
                }

    # Also pull from research queue found articles
    if QUEUE_STATE.exists():
        qdata = json.loads(QUEUE_STATE.read_text(encoding="utf-8"))
        for target in qdata.get("targets", []):
            for sr in target.get("search_results", []):
                for art in sr.get("articles_found", []):
                    doi = (art.get("doi") or "").strip()
                    if doi and doi not in candidates:
                        candidates[doi] = {
                            "doi": doi,
                            "title": art.get("title", ""),
                            "authors": art.get("authors", []),
                            "year": art.get("year"),
                            "venue": art.get("venue", ""),
                            "relevance": art.get("relevance_score", 0),
                            "source": "research_queue",
                        }

    return list(candidates.values())


def collect_candidates_from_doi_file(path: Path) -> list[dict[str, Any]]:
    """Read DOIs from a text file (one per line)."""
    dois = [line.strip() for line in path.read_text().splitlines() if line.strip()]
    return [{"doi": doi, "title": "", "authors": [], "year": None,
             "venue": "", "relevance": 0, "source": "manual"} for doi in dois]


# ---------------------------------------------------------------------------
# Zotero push
# ---------------------------------------------------------------------------

def push_to_zotero(
    candidates: list[dict[str, Any]],
    dry_run: bool = False,
    library_id: Optional[str] = None,
    api_key: Optional[str] = None,
    library_type: str = "user",
) -> dict[str, Any]:
    """Push candidate articles to Zotero library."""
    lib_id = library_id or os.environ.get("ZOTERO_LIBRARY_ID")
    key = api_key or os.environ.get("ZOTERO_API_KEY")
    lib_type = os.environ.get("ZOTERO_LIBRARY_TYPE", library_type)

    if not lib_id or not key:
        if dry_run:
            print("⚠️  ZOTERO_LIBRARY_ID / ZOTERO_API_KEY not set — dry-run only")
        else:
            print("❌  Set ZOTERO_LIBRARY_ID and ZOTERO_API_KEY in .env")
            return {"pushed": 0, "skipped": 0, "errors": 0}

    zot = None
    if not dry_run:
        try:
            from pyzotero import zotero
            zot = zotero.Zotero(lib_id, lib_type, key)
        except ImportError:
            print("❌  pyzotero not installed. Run: pip install pyzotero")
            return {"pushed": 0, "skipped": 0, "errors": 0}

    state = load_state()
    pushed_dois = state["pushed_dois"]
    stats = {"pushed": 0, "skipped": 0, "errors": 0}

    for cand in candidates:
        doi = cand.get("doi", "").strip()
        if not doi:
            continue
        doi_lower = doi.lower()
        if doi_lower in pushed_dois:
            stats["skipped"] += 1
            continue

        # Build Zotero item
        item = {
            "itemType": "journalArticle",
            "title": cand.get("title") or f"[DOI: {doi}]",
            "DOI": doi,
            "url": f"https://doi.org/{doi}",
            "date": str(cand.get("year", "")),
            "publicationTitle": cand.get("venue", ""),
            "tags": [{"tag": f"ae:source:{cand.get('source', 'unknown')}"},
                     {"tag": "ae:auto-push"}],
            "creators": [],
        }

        # Add authors
        authors_raw = cand.get("authors", [])
        for author in authors_raw[:10]:  # Limit to 10
            if isinstance(author, str):
                parts = author.rsplit(" ", 1)
                item["creators"].append({
                    "creatorType": "author",
                    "firstName": parts[0] if len(parts) > 1 else "",
                    "lastName": parts[-1],
                })
            elif isinstance(author, dict):
                item["creators"].append({
                    "creatorType": "author",
                    "firstName": author.get("given", author.get("firstName", "")),
                    "lastName": author.get("family", author.get("lastName", author.get("name", ""))),
                })

        if dry_run:
            print(f"  [DRY-RUN] Would push: {doi}  —  {item['title'][:60]}")
            stats["pushed"] += 1
        else:
            try:
                template = zot.item_template("journalArticle")
                template.update(item)
                resp = zot.create_items([template])
                if resp.get("successful") or resp.get("success"):
                    pushed_dois[doi_lower] = {
                        "pushed_at": datetime.now(timezone.utc).isoformat(),
                        "title": item["title"][:100],
                    }
                    stats["pushed"] += 1
                    print(f"  ✅ Pushed: {doi}")
                else:
                    stats["errors"] += 1
                    print(f"  ❌ Failed: {doi}  —  {resp}")
            except Exception as exc:
                stats["errors"] += 1
                print(f"  ❌ Error pushing {doi}: {exc}")

    state["pushed_dois"] = pushed_dois
    state["stats"]["total_pushed"] = len(pushed_dois)
    state["stats"]["last_push_at"] = datetime.now(timezone.utc).isoformat()
    save_state(state)

    return stats


def show_status() -> None:
    state = load_state()
    total = state["stats"].get("total_pushed", 0)
    last = state["stats"].get("last_push_at", "never")
    print(f"Zotero push state:")
    print(f"  Total pushed:  {total}")
    print(f"  Last push:     {last}")
    print(f"  State file:    {STATE_FILE}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing to Zotero")
    parser.add_argument("--from-dois", type=Path, help="Text file with one DOI per line")
    parser.add_argument("--status", action="store_true", help="Show push statistics")
    args = parser.parse_args()

    if args.status:
        show_status()
        return 0

    if args.from_dois:
        if not args.from_dois.exists():
            print(f"❌  File not found: {args.from_dois}")
            return 1
        candidates = collect_candidates_from_doi_file(args.from_dois)
    else:
        candidates = collect_candidates_from_files()

    if not candidates:
        print("No candidates to push.")
        return 0

    print(f"Found {len(candidates)} candidate(s) to push to Zotero")
    stats = push_to_zotero(candidates, dry_run=args.dry_run)
    print(f"\nPushed: {stats['pushed']}  Skipped: {stats['skipped']}  Errors: {stats['errors']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
