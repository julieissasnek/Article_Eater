#!/usr/bin/env python3
"""
Re-resolve unresolved outcomes using expanded vocabulary.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher

def load_lookup():
    """Load the expanded outcome lookup."""
    path = Path("contracts/outcome_vocab/outcome_lookup.json")
    with open(path) as f:
        return json.load(f)

def resolve_outcome(raw_term, lookup_data, fuzzy_threshold=0.85):
    """
    Resolve a raw outcome term using the lookup table.
    """
    raw_lower = raw_term.lower().strip()

    # 1. Exact match
    if raw_lower in lookup_data['lookup']:
        term_id = lookup_data['lookup'][raw_lower]
        term_info = lookup_data['terms'].get(term_id, {})
        return {
            'canonical_id': term_id,
            'name': term_info.get('name', term_id),
            'domain': term_info.get('domain', ''),
            'confidence': 1.0,
            'match_type': 'exact'
        }

    # 2. Fuzzy match
    best_match = None
    best_score = 0.0

    for lookup_text, term_id in lookup_data['lookup'].items():
        score = SequenceMatcher(None, raw_lower, lookup_text).ratio()
        if score > best_score and score >= fuzzy_threshold:
            best_score = score
            best_match = term_id

    if best_match:
        term_info = lookup_data['terms'].get(best_match, {})
        return {
            'canonical_id': best_match,
            'name': term_info.get('name', best_match),
            'domain': term_info.get('domain', ''),
            'confidence': best_score,
            'match_type': 'fuzzy'
        }

    return None

def main():
    print("=" * 80)
    print("RE-RESOLVING UNRESOLVED OUTCOMES WITH EXPANDED VOCABULARY")
    print("=" * 80)

    # Load lookup
    lookup_data = load_lookup()
    print(f"\nLoaded lookup with {len(lookup_data['lookup'])} entries, {len(lookup_data['terms'])} terms")

    # Load unresolved outcomes
    unresolved_path = Path("data/unresolved_outcomes.jsonl")
    with open(unresolved_path) as f:
        unresolved_entries = [json.loads(line) for line in f if line.strip()]

    print(f"Processing {len(unresolved_entries)} unresolved outcomes...")

    # Process each outcome
    resolved = []
    still_unresolved = []
    resolution_stats = {
        'exact': 0,
        'fuzzy': 0,
        'unresolved': 0
    }

    for i, entry in enumerate(unresolved_entries):
        raw_term = entry['raw_term']
        result = resolve_outcome(raw_term, lookup_data)

        if result:
            resolved.append({
                'raw_term': raw_term,
                'canonical_id': result['canonical_id'],
                'name': result['name'],
                'domain': result['domain'],
                'confidence': result['confidence'],
                'match_type': result['match_type'],
                'paper_id': entry.get('paper_id'),
                'resolved_at': datetime.utcnow().isoformat() + 'Z'
            })
            resolution_stats[result['match_type']] += 1
        else:
            still_unresolved.append(entry)
            resolution_stats['unresolved'] += 1

        if (i + 1) % 500 == 0:
            print(f"  Processed {i + 1}/{len(unresolved_entries)}")

    # Write resolved outcomes
    resolved_path = Path("data/resolved_outcomes.jsonl")
    with open(resolved_path, 'w') as f:
        for entry in resolved:
            f.write(json.dumps(entry) + '\n')

    print(f"\nResolved: {len(resolved)}")
    print(f"  Exact matches: {resolution_stats['exact']}")
    print(f"  Fuzzy matches: {resolution_stats['fuzzy']}")

    # Update unresolved outcomes file
    with open(unresolved_path, 'w') as f:
        for entry in still_unresolved:
            f.write(json.dumps(entry) + '\n')

    print(f"Still unresolved: {len(still_unresolved)}")
    print(f"Resolution rate: {len(resolved)/len(unresolved_entries)*100:.1f}%")

    # Show sample resolutions
    print(f"\nSample resolutions (first 20):")
    for i, r in enumerate(resolved[:20], 1):
        print(f"  {i:2}. '{r['raw_term'][:40]:40}' -> {r['canonical_id']:30} ({r['match_type']})")

    print(f"\nSample still unresolved (first 10):")
    for i, entry in enumerate(still_unresolved[:10], 1):
        print(f"  {i:2}. '{entry['raw_term'][:50]:50}'")

    print(f"\n" + "=" * 80)
    print(f"SUCCESS: Resolved {len(resolved)} outcomes")
    print(f"Target: < 1000 unresolved")
    if len(still_unresolved) < 1000:
        print(f"TARGET MET: {len(still_unresolved)} < 1000")
    else:
        print(f"TARGET NOT MET: {len(still_unresolved)} >= 1000")

if __name__ == '__main__':
    main()
