"""
Card Quality Validator — Post-Generation Quality Gates
=======================================================

Validates generated cards against the hierarchical success conditions:
  SC-PH: Pipeline Health — basic structural integrity
  SC-SD: Source Data Completeness — enrichment coverage
  SC-PR: Content Provenance — traceability
  SC-CQ: Content Quality — prose and data quality

Usage:
    # Validate all cards
    python scripts/validate_card_quality.py

    # Validate specific type
    python scripts/validate_card_quality.py --type t1-framework

    # JSON output for CI
    python scripts/validate_card_quality.py --json

Author: AG (pipeline repair)
Date: 2026-03-04
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CARD_DIR = PROJECT_ROOT / "data" / "cards"
SOURCE_DIR = PROJECT_ROOT / "data" / "card_sources"


def _load_cards(type_filter: str = None) -> Dict[str, List[Dict]]:
    """Load all generated cards, grouped by type."""
    cards = {}
    if not CARD_DIR.exists():
        return cards
    for type_dir in sorted(CARD_DIR.iterdir()):
        if not type_dir.is_dir():
            continue
        ct = type_dir.name
        if type_filter and ct != type_filter:
            continue
        type_cards = []
        for p in sorted(type_dir.glob("*.json")):
            try:
                with open(p) as f:
                    type_cards.append(json.load(f))
            except Exception:
                pass
        if type_cards:
            cards[ct] = type_cards
    return cards


def _load_sources(type_filter: str = None) -> Dict[str, int]:
    """Count enriched sources per type."""
    counts = {}
    if not SOURCE_DIR.exists():
        return counts
    for type_dir in sorted(SOURCE_DIR.iterdir()):
        if not type_dir.is_dir():
            continue
        ct = type_dir.name
        if type_filter and ct != type_filter:
            continue
        counts[ct] = len(list(type_dir.glob("*.json")))
    return counts


# ─── Success Condition Checkers ───────────────────────────────────────


def check_pipeline_health(cards: Dict[str, List[Dict]]) -> Dict:
    """SC-PH: Pipeline Health — basic structural integrity."""
    results = {"condition": "SC-PH", "checks": []}

    # SC-PH-1: Card has all required sections (surface, body, iceberg)
    missing_sections = []
    for ct, card_list in cards.items():
        for c in card_list:
            eid = c.get("surface", {}).get("entity_id", c.get("entity_id", "?"))
            has_surface = bool(c.get("surface"))
            has_body = bool(c.get("body"))
            has_iceberg = bool(c.get("iceberg"))
            if not (has_surface and has_body and has_iceberg):
                missing_sections.append(f"{ct}/{eid}: surface={has_surface} body={has_body} iceberg={has_iceberg}")

    results["checks"].append({
        "id": "SC-PH-1",
        "name": "All cards have surface/body/iceberg",
        "pass": len(missing_sections) == 0,
        "failures": missing_sections[:5],
        "n_failures": len(missing_sections),
    })

    # SC-PH-2: Body has non-empty tabs
    empty_body = []
    for ct, card_list in cards.items():
        for c in card_list:
            eid = c.get("surface", {}).get("entity_id", "?")
            tabs = c.get("body", {}).get("tabs", {})
            if not tabs:
                empty_body.append(f"{ct}/{eid}")

    results["checks"].append({
        "id": "SC-PH-2",
        "name": "All cards have non-empty body tabs",
        "pass": len(empty_body) == 0,
        "failures": empty_body[:5],
        "n_failures": len(empty_body),
    })

    # SC-PH-3: Card count > 0 for each type
    total = sum(len(v) for v in cards.values())
    results["checks"].append({
        "id": "SC-PH-3",
        "name": f"At least one card exists ({total} total)",
        "pass": total > 0,
        "n_failures": 0 if total > 0 else 1,
    })

    results["pass"] = all(c["pass"] for c in results["checks"])
    return results


def check_source_data(cards: Dict[str, List[Dict]], sources: Dict[str, int]) -> Dict:
    """SC-SD: Source Data Completeness — enriched sources exist for all card types."""
    results = {"condition": "SC-SD", "checks": []}

    # SC-SD-1: Enriched sources exist for T1, T2, T3
    required = {"t1-framework", "t2-mechanism", "t3-belief"}
    missing = required - set(sources.keys())
    results["checks"].append({
        "id": "SC-SD-1",
        "name": "Enriched sources exist for T1, T2, T3",
        "pass": len(missing) == 0,
        "details": {k: v for k, v in sources.items()},
        "missing": list(missing),
    })

    # SC-SD-2: Cards use enriched data (have findings > 0)
    no_findings = []
    for ct, card_list in cards.items():
        for c in card_list:
            surface = c.get("surface", {})
            eid = surface.get("entity_id", "?")
            nf = surface.get("n_findings", 0)
            if nf == 0 and ct in ("t1-framework", "t2-mechanism"):
                no_findings.append(f"{ct}/{eid}")

    results["checks"].append({
        "id": "SC-SD-2",
        "name": "T1/T2 cards have findings > 0",
        "pass": len(no_findings) == 0,
        "failures": no_findings[:5],
        "n_failures": len(no_findings),
    })

    results["pass"] = all(c["pass"] for c in results["checks"])
    return results


def check_provenance(cards: Dict[str, List[Dict]]) -> Dict:
    """SC-PR: Content Provenance — traceability."""
    results = {"condition": "SC-PR", "checks": []}

    # SC-PR-1: Iceberg has agent_context with model info
    no_agent = []
    for ct, card_list in cards.items():
        for c in card_list:
            eid = c.get("surface", {}).get("entity_id", "?")
            agent = c.get("iceberg", {}).get("agent_context", {})
            if not agent.get("model"):
                no_agent.append(f"{ct}/{eid}")

    results["checks"].append({
        "id": "SC-PR-1",
        "name": "All cards have agent_context with model",
        "pass": len(no_agent) == 0,
        "failures": no_agent[:5],
        "n_failures": len(no_agent),
    })

    # SC-PR-2: Source map has paper_dois
    no_dois = []
    for ct, card_list in cards.items():
        for c in card_list:
            eid = c.get("surface", {}).get("entity_id", "?")
            dois = c.get("iceberg", {}).get("source_map", {}).get("paper_dois", [])
            if not dois and ct in ("t1-framework", "t2-mechanism"):
                no_dois.append(f"{ct}/{eid}")

    results["checks"].append({
        "id": "SC-PR-2",
        "name": "T1/T2 cards have paper DOIs in source_map",
        "pass": len(no_dois) == 0,
        "failures": no_dois[:5],
        "n_failures": len(no_dois),
    })

    results["pass"] = all(c["pass"] for c in results["checks"])
    return results


def check_content_quality(cards: Dict[str, List[Dict]]) -> Dict:
    """SC-CQ: Content Quality — prose and data quality."""
    results = {"condition": "SC-CQ", "checks": []}

    # SC-CQ-1: Tabs have prose content (not just JSON)
    empty_prose = []
    for ct, card_list in cards.items():
        for c in card_list:
            eid = c.get("surface", {}).get("entity_id", "?")
            tabs = c.get("body", {}).get("tabs", {})
            for tab_name, tab_data in tabs.items():
                prose = tab_data.get("prose", "")
                if len(prose) < 50:
                    empty_prose.append(f"{ct}/{eid}/{tab_name}")

    results["checks"].append({
        "id": "SC-CQ-1",
        "name": "All tabs have prose >= 50 chars",
        "pass": len(empty_prose) == 0,
        "failures": empty_prose[:5],
        "n_failures": len(empty_prose),
    })

    # SC-CQ-2: No [DRAFT] marked prose in production cards
    draft_tabs = []
    for ct, card_list in cards.items():
        for c in card_list:
            eid = c.get("surface", {}).get("entity_id", "?")
            tabs = c.get("body", {}).get("tabs", {})
            for tab_name, tab_data in tabs.items():
                prose = tab_data.get("prose", "")
                if "[DRAFT" in prose:
                    draft_tabs.append(f"{ct}/{eid}/{tab_name}")

    results["checks"].append({
        "id": "SC-CQ-2",
        "name": "No [DRAFT] tags in production cards",
        "pass": len(draft_tabs) == 0,
        "failures": draft_tabs[:5],
        "n_failures": len(draft_tabs),
    })

    results["pass"] = all(c["pass"] for c in results["checks"])
    return results


def main():
    parser = argparse.ArgumentParser(description="Validate card quality")
    parser.add_argument("--type", help="Card type to validate (e.g. t1-framework)")
    parser.add_argument("--json", action="store_true", help="JSON output for CI")
    args = parser.parse_args()

    cards = _load_cards(args.type)
    sources = _load_sources(args.type)

    total_cards = sum(len(v) for v in cards.values())
    if total_cards == 0:
        print("No cards found to validate. Run card generation first.")
        return

    checks = [
        check_pipeline_health(cards),
        check_source_data(cards, sources),
        check_provenance(cards),
        check_content_quality(cards),
    ]

    if args.json:
        print(json.dumps({"results": checks, "total_cards": total_cards}, indent=2))
        return

    # Pretty print
    print(f"\n{'='*60}")
    print(f"  Card Quality Validation — {total_cards} cards")
    print(f"  Types: {', '.join(f'{k}({len(v)})' for k, v in cards.items())}")
    print(f"{'='*60}\n")

    all_pass = True
    for result in checks:
        status = "✓ PASS" if result["pass"] else "✗ FAIL"
        print(f"  {result['condition']}: {status}")
        for check in result["checks"]:
            icon = "✓" if check["pass"] else "✗"
            print(f"    {icon} {check['id']}: {check['name']}")
            if not check["pass"] and check.get("failures"):
                for fail in check["failures"][:3]:
                    print(f"      → {fail}")
                nf = check.get("n_failures", 0)
                if nf > 3:
                    print(f"      ... and {nf - 3} more")
        if not result["pass"]:
            all_pass = False
        print()

    print(f"  Overall: {'✓ ALL PASS' if all_pass else '✗ SOME FAILURES'}")
    print()


if __name__ == "__main__":
    main()
