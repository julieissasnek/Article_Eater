"""
Article Eater - Outcome Resolver
Resolves raw outcome terms to canonical vocabulary during claim extraction.

Usage in claim extraction:
    from lib.outcome_resolver import resolve_outcome, queue_unknown_outcome
    
    # During claim building
    raw_outcome = "sustained attention"
    resolved = resolve_outcome(raw_outcome)
    
    if resolved:
        outcome_id = resolved['canonical_id']  # "cog.attention.sustained"
    else:
        queue_unknown_outcome(raw_outcome, paper_id)
        outcome_id = f"UNRESOLVED:{raw_outcome}"
"""

import json
from pathlib import Path
from typing import Optional, Dict, List
from difflib import SequenceMatcher
from datetime import datetime

# Lookup table path
_LOOKUP_PATH = Path(__file__).parent.parent / "contracts" / "outcome_vocab" / "outcome_lookup.json"
_QUEUE_PATH = Path(__file__).parent.parent / "data" / "unresolved_outcomes.jsonl"

_lookup_data = None

def _load_lookup() -> Dict:
    """Load outcome lookup table."""
    global _lookup_data
    if _lookup_data is None:
        if _LOOKUP_PATH.exists():
            with open(_LOOKUP_PATH) as f:
                _lookup_data = json.load(f)
        else:
            print(f"WARNING: Outcome lookup not found at {_LOOKUP_PATH}")
            print("Run integrate_oc_with_ae.py to generate it")
            _lookup_data = {"lookup": {}, "terms": {}}
    return _lookup_data

def resolve_outcome(raw_term: str, fuzzy_threshold: float = 0.85) -> Optional[Dict]:
    """
    Resolve a raw outcome term to canonical form.
    
    Args:
        raw_term: The raw outcome term from the paper
        fuzzy_threshold: Minimum similarity for fuzzy match (0-1)
    
    Returns:
        Dict with canonical_id, name, domain, confidence, match_type
        or None if no match found
    """
    data = _load_lookup()
    raw_lower = raw_term.lower().strip()
    
    # 1. Exact match in lookup
    if raw_lower in data['lookup']:
        term_id = data['lookup'][raw_lower]
        term_info = data['terms'].get(term_id, {})
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
    
    for lookup_text, term_id in data['lookup'].items():
        score = SequenceMatcher(None, raw_lower, lookup_text).ratio()
        if score > best_score and score >= fuzzy_threshold:
            best_score = score
            best_match = term_id
    
    if best_match:
        term_info = data['terms'].get(best_match, {})
        return {
            'canonical_id': best_match,
            'name': term_info.get('name', best_match),
            'domain': term_info.get('domain', ''),
            'confidence': best_score,
            'match_type': 'fuzzy'
        }
    
    return None

def queue_unknown_outcome(
    raw_term: str,
    paper_id: Optional[str] = None,
    claim_id: Optional[str] = None,
    context: Optional[str] = None
) -> None:
    """
    Queue an unresolved outcome term for human review.
    
    These will be imported into Outcome_Contractor for review.
    """
    _QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "raw_term": raw_term,
        "paper_id": paper_id,
        "claim_id": claim_id,
        "context": context,
        "queued_at": datetime.utcnow().isoformat() + "Z"
    }
    
    with open(_QUEUE_PATH, 'a') as f:
        f.write(json.dumps(entry) + "\n")

def resolve_or_queue(
    raw_term: str,
    paper_id: Optional[str] = None,
    claim_id: Optional[str] = None,
    context: Optional[str] = None
) -> Dict:
    """
    Resolve outcome term, or queue and return placeholder.
    
    Always returns a dict - either resolved canonical or placeholder.
    """
    resolved = resolve_outcome(raw_term)
    
    if resolved:
        return resolved
    
    # Queue for review
    queue_unknown_outcome(raw_term, paper_id, claim_id, context)
    
    # Return placeholder
    return {
        'canonical_id': f"UNRESOLVED:{raw_term.lower().replace(' ', '_')}",
        'name': raw_term,
        'domain': 'unknown',
        'confidence': 0.0,
        'match_type': 'unresolved'
    }

def get_suggestions(raw_term: str, limit: int = 5) -> List[Dict]:
    """Get resolution suggestions for a term."""
    data = _load_lookup()
    raw_lower = raw_term.lower().strip()
    
    candidates = []
    for lookup_text, term_id in data['lookup'].items():
        score = SequenceMatcher(None, raw_lower, lookup_text).ratio()
        if score >= 0.5:
            term_info = data['terms'].get(term_id, {})
            candidates.append({
                'term_id': term_id,
                'name': term_info.get('name', term_id),
                'score': score,
                'matched_text': lookup_text
            })
    
    candidates.sort(key=lambda x: -x['score'])
    return candidates[:limit]

def suggest_domain(raw_term: str) -> Optional[str]:
    """Suggest which domain a term likely belongs to."""
    raw_lower = raw_term.lower()
    
    domain_keywords = {
        'cog': ['attention', 'memory', 'cognit', 'think', 'learn', 'focus', 'concentrate'],
        'affect': ['mood', 'emotion', 'affect', 'stress', 'anxiety', 'depress', 'happy'],
        'behav': ['behavior', 'behaviour', 'action', 'activity', 'sleep', 'product', 'perform'],
        'social': ['social', 'interact', 'communicat', 'collaborat', 'team'],
        'physio': ['heart', 'blood', 'cortisol', 'fatigue', 'pain', 'alertness'],
        'neural': ['brain', 'neural', 'cortex', 'eeg', 'fmri'],
        'health': ['health', 'wellbeing', 'well-being', 'illness', 'disease']
    }
    
    scores = {d: 0 for d in domain_keywords}
    for domain, keywords in domain_keywords.items():
        for kw in keywords:
            if kw in raw_lower:
                scores[domain] += 1
    
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else None

def get_queued_count() -> int:
    """Get count of queued unresolved terms."""
    if not _QUEUE_PATH.exists():
        return 0
    with open(_QUEUE_PATH) as f:
        return sum(1 for _ in f)

def get_stats() -> Dict:
    """Get resolver statistics."""
    data = _load_lookup()
    return {
        'terms_count': len(data.get('terms', {})),
        'lookup_entries': len(data.get('lookup', {})),
        'queued_count': get_queued_count()
    }
