#!/usr/bin/env python3
"""
Link outcome vocabulary terms to instrument registry IDs.

Reads outcome_vocab.json and instruments_registry.json, matches operationalizations
to instrument IDs via abbreviation and full name matching, and writes updated
outcome_vocab.json with instrument_ids field.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


def build_instrument_lookup(instruments: List[Dict]) -> Dict[str, str]:
    """
    Build a lookup table mapping instrument names/abbreviations to instrument_id.

    Returns dict where keys are normalized names/abbreviations and values are instrument_ids.
    """
    lookup = {}

    for inst in instruments:
        instrument_id = inst.get("instrument_id")

        # Add abbreviation (exact match)
        if "abbreviation" in inst:
            abbrev = inst["abbreviation"].strip()
            lookup[abbrev] = instrument_id

        # Add full name (exact match)
        if "full_name" in inst:
            full_name = inst["full_name"].strip()
            lookup[full_name] = instrument_id

        # Add lowercase versions for case-insensitive matching
        if "abbreviation" in inst:
            abbrev_lower = inst["abbreviation"].strip().lower()
            if abbrev_lower not in lookup:
                lookup[abbrev_lower] = instrument_id

        if "full_name" in inst:
            full_name_lower = inst["full_name"].strip().lower()
            if full_name_lower not in lookup:
                lookup[full_name_lower] = instrument_id

    return lookup


def extract_abbreviations(text: str) -> List[str]:
    """
    Extract potential abbreviations from operationalization text.
    Looks for patterns like "XXX" in parentheses or standalone abbreviations.
    """
    abbrevs = []

    # Pattern 1: "Anything (ABBREV)" or "Anything (ABBREV-X)"
    matches = re.findall(r'\(([A-Z][A-Z0-9\-]*)\)', text)
    abbrevs.extend(matches)

    # Pattern 2: Standalone at start like "STAI score" (without parentheses)
    # Only if it looks like a real abbreviation (2-4 uppercase letters/numbers)
    words = text.split()
    if words and re.match(r'^[A-Z][A-Z0-9]{1,3}$', words[0]):
        abbrevs.append(words[0])

    return abbrevs


def match_instrument(operationalization: str, lookup: Dict[str, str]) -> Set[str]:
    """
    Match an operationalization string to instrument IDs.

    Returns set of matching instrument_ids (can be multiple if abbreviation
    matches multiple instruments, though this is unlikely).
    """
    matched_ids = set()

    # Try exact match with the full operationalization text
    if operationalization in lookup:
        matched_ids.add(lookup[operationalization])

    # Try case-insensitive exact match
    if operationalization.lower() in lookup:
        matched_ids.add(lookup[operationalization.lower()])

    # Extract and match abbreviations from the text
    abbrevs = extract_abbreviations(operationalization)
    for abbrev in abbrevs:
        if abbrev in lookup:
            matched_ids.add(lookup[abbrev])
        # Try lowercase
        abbrev_lower = abbrev.lower()
        if abbrev_lower in lookup:
            matched_ids.add(lookup[abbrev_lower])

    return matched_ids


def main():
    repo_root = Path(__file__).parent.parent
    outcome_vocab_path = repo_root / "contracts" / "outcome_vocab" / "outcome_vocab.json"
    instruments_path = repo_root / "contracts" / "instruments" / "instruments_registry.json"

    # Load files
    print(f"Loading outcome vocabulary from {outcome_vocab_path}...")
    with open(outcome_vocab_path, 'r') as f:
        outcome_data = json.load(f)

    print(f"Loading instruments registry from {instruments_path}...")
    with open(instruments_path, 'r') as f:
        instruments_data = json.load(f)

    # Build lookup
    instruments = instruments_data.get("instruments", [])
    lookup = build_instrument_lookup(instruments)

    print(f"\nInstrument lookup contains {len(lookup)} entries from {len(instruments)} instruments")

    # Process outcome terms
    terms = outcome_data.get("terms", [])
    print(f"\nProcessing {len(terms)} outcome terms...")

    stats = {
        "total_terms": len(terms),
        "terms_with_matches": 0,
        "total_matches": 0,
        "terms_without_matches": 0,
        "match_details": defaultdict(lambda: {"operationalizations": [], "instruments": []}),
    }

    for term in terms:
        operationalizations = term.get("operationalizations", [])

        # Collect all instrument IDs for this term
        all_instrument_ids = set()

        for operationalization in operationalizations:
            matched = match_instrument(operationalization, lookup)
            all_instrument_ids.update(matched)

            if matched:
                stats["match_details"][term["term_id"]]["operationalizations"].append({
                    "text": operationalization,
                    "matched_to": list(matched)
                })
                stats["total_matches"] += len(matched)

        # Add instrument_ids field
        term["instrument_ids"] = sorted(list(all_instrument_ids))

        if all_instrument_ids:
            stats["terms_with_matches"] += 1
            stats["match_details"][term["term_id"]]["instruments"] = sorted(list(all_instrument_ids))
        else:
            stats["terms_without_matches"] += 1

    # Save updated outcome vocabulary
    print(f"\nSaving updated outcome vocabulary to {outcome_vocab_path}...")
    with open(outcome_vocab_path, 'w') as f:
        json.dump(outcome_data, f, indent=2)

    # Print summary
    print("\n" + "=" * 70)
    print("LINKING SUMMARY")
    print("=" * 70)
    print(f"Total outcome terms processed: {stats['total_terms']}")
    print(f"Terms with at least one instrument match: {stats['terms_with_matches']}")
    print(f"Terms with no instrument matches: {stats['terms_without_matches']}")
    print(f"Total operationalization→instrument matches: {stats['total_matches']}")
    print(f"\nCoverage: {stats['terms_with_matches']}/{stats['total_terms']} terms ({100*stats['terms_with_matches']/stats['total_terms']:.1f}%)")

    # Show some examples
    print("\n" + "-" * 70)
    print("EXAMPLE MATCHES (first 5 terms with instruments):")
    print("-" * 70)

    shown = 0
    for term_id, details in stats["match_details"].items():
        if shown >= 5:
            break
        if details["instruments"]:
            print(f"\n{term_id}")
            for op_match in details["operationalizations"]:
                print(f"  • '{op_match['text']}' → {op_match['matched_to']}")
            shown += 1

    # Show terms with no matches (for inspection)
    no_match_terms = [tid for tid, details in stats["match_details"].items()
                       if not details["instruments"]]
    if no_match_terms:
        print("\n" + "-" * 70)
        print(f"TERMS WITH NO INSTRUMENT MATCHES ({len(no_match_terms)} total):")
        print("-" * 70)
        for term_id in no_match_terms[:10]:
            term = next((t for t in terms if t["term_id"] == term_id), None)
            if term and term.get("operationalizations"):
                print(f"\n{term_id}:")
                for op in term["operationalizations"][:2]:
                    print(f"  • {op}")
        if len(no_match_terms) > 10:
            print(f"\n  ... and {len(no_match_terms) - 10} more")

    print("\n" + "=" * 70)
    print(f"✓ Updated outcome_vocab.json saved to {outcome_vocab_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
