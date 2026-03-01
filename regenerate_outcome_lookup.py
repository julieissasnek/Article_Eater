#!/usr/bin/env python3
"""
Regenerate outcome_lookup.json from expanded outcome_vocab.json
"""

import json
from pathlib import Path
from datetime import datetime

def generate_lookup():
    """Generate comprehensive lookup from outcome vocabulary."""
    vocab_path = Path("contracts/outcome_vocab/outcome_vocab.json")
    lookup_path = Path("contracts/outcome_vocab/outcome_lookup.json")

    # Load vocabulary
    with open(vocab_path) as f:
        vocab = json.load(f)

    # Build lookup table
    lookup = {}
    terms_index = {}

    for term in vocab.get('terms', []):
        term_id = term['term_id']
        name = term['name']
        cognates = term.get('cognates', [])

        # Index by term_id
        terms_index[term_id] = {
            'name': name,
            'domain': term['domain'],
            'level': term['level'],
            'definition': term.get('definition', '')
        }

        # Lookup: term name (lowercase)
        name_lower = name.lower()
        if name_lower not in lookup:
            lookup[name_lower] = term_id

        # Lookup: all cognates
        for cognate in cognates:
            cognate_lower = cognate.lower()
            if cognate_lower not in lookup:
                lookup[cognate_lower] = term_id

    # Generate output
    output = {
        "schema": "oc.ae_lookup.v1",
        "version": "1.0.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "lookup": lookup,
        "terms": terms_index
    }

    # Write lookup
    with open(lookup_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Generated {lookup_path}")
    print(f"  Lookup entries: {len(lookup)}")
    print(f"  Indexed terms: {len(terms_index)}")
    print(f"  Domains: {len(set(t['domain'] for t in terms_index.values()))}")

if __name__ == '__main__':
    generate_lookup()
