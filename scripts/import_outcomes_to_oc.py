#!/usr/bin/env python3
"""
Import queued outcome terms from AE back to Outcome_Contractor.

Run periodically to review and approve new terms.
"""

import sys
import json
from pathlib import Path

OC_PATH = Path.home() / "REPOS" / "Outcome_Contractor"
AE_PATH = Path.home() / "REPOS" / "Article_Eater_v20_7_43"
QUEUE_PATH = AE_PATH / "data" / "unresolved_outcomes.jsonl"

def main():
    if not QUEUE_PATH.exists():
        print("No queued terms to import")
        return 0
    
    # Read queued terms
    terms = []
    with open(QUEUE_PATH) as f:
        for line in f:
            if line.strip():
                terms.append(json.loads(line))
    
    if not terms:
        print("No queued terms to import")
        return 0
    
    print(f"Found {len(terms)} queued terms")
    
    # Import to OC
    sys.path.insert(0, str(OC_PATH))
    from core.database import get_database
    
    db = get_database(OC_PATH / "data" / "outcome_contractor.db")
    
    imported = 0
    for term in terms:
        raw = term.get('raw_term', '')
        if raw and not db.candidate_exists(raw):
            db.add_candidate(
                raw_text=raw,
                source_paper_id=term.get('paper_id'),
                source_claim_id=term.get('claim_id'),
                context=term.get('context')
            )
            imported += 1
    
    print(f"Imported {imported} new candidates to Outcome_Contractor")
    print()
    print("To review:")
    print(f"  cd {OC_PATH}")
    print("  python cli/main.py candidates")
    
    # Clear queue after import
    if imported > 0:
        QUEUE_PATH.rename(QUEUE_PATH.with_suffix('.jsonl.imported'))
        print()
        print(f"Archived queue to {QUEUE_PATH.with_suffix('.jsonl.imported')}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
