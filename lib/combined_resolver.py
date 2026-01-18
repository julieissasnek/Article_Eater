"""
Article Eater - Combined Resolver
Resolves both environment (IV) and outcome (DV) terms during claim extraction.

def _resolve_construct_id(raw_id, construct_type='outcome', paper_id=None):
    """Resolve construct ID through ontology contractors.
    
    Args:
        raw_id: Raw term to resolve
        construct_type: 'environment' for IVs, 'outcome' for DVs
        paper_id: Paper ID for context
    """
    try:
        from lib.combined_resolver import resolve_single_construct
        result = resolve_single_construct(str(raw_id), construct_type, paper_id)
        return result['canonical_id']
    except ImportError:
        # Fallback to outcome-only resolver
        try:
            from lib.outcome_resolver import resolve_or_queue
            result = resolve_or_queue(str(raw_id), paper_id=paper_id)
            return result['canonical_id'] if result else str(raw_id)
        except Exception:
            return str(raw_id)
    except Exception:
        return str(raw_id)

def _resolve_outcome_id(raw_id, paper_id=None):
    """Resolve outcome (DV) ID."""
    return _resolve_construct_id(raw_id, 'outcome', paper_id)

def _resolve_environment_id(raw_id, paper_id=None):
    """Resolve environment (IV) ID."""
    return _resolve_construct_id(raw_id, 'environment', paper_id)


Usage:
    from lib.combined_resolver import resolve_claim_constructs
    
    resolved = resolve_claim_constructs(
        environment_terms=["daylight", "warm lighting"],
        outcome_terms=["mood", "attention"],
        paper_id="doi:10.1234/example"
    )
"""

from typing import Dict, List, Optional, Any
from pathlib import Path

# Import individual resolvers
try:
    from .environment_resolver import resolve_environment, resolve_or_queue_environment
except ImportError:
    resolve_environment = lambda x: None
    resolve_or_queue_environment = lambda x, **kw: (None, False)

try:
    from .outcome_resolver import resolve_outcome, resolve_or_queue
except ImportError:
    resolve_outcome = lambda x: None
    resolve_or_queue = lambda x, **kw: (None, False)


def resolve_claim_constructs(
    environment_terms: List[str],
    outcome_terms: List[str],
    paper_id: Optional[str] = None,
    queue_unresolved: bool = True
) -> Dict[str, Any]:
    """
    Resolve all constructs for a claim.
    
    Args:
        environment_terms: List of raw environment/IV terms
        outcome_terms: List of raw outcome/DV terms
        paper_id: Paper ID for queuing unresolved terms
        queue_unresolved: Whether to queue unresolved terms for review
    
    Returns:
        Dict with resolved environment_factors and outcomes
    """
    result = {
        'environment_factors': [],
        'outcomes': [],
        'unresolved_environment': [],
        'unresolved_outcomes': [],
    }
    
    # Resolve environment terms
    for term in environment_terms:
        if not term:
            continue
        
        if queue_unresolved:
            resolved, queued = resolve_or_queue_environment(term)
        else:
            resolved = resolve_environment(term)
            queued = False
        
        if resolved:
            result['environment_factors'].append({
                'id': resolved['tag_id'],
                'canonical_name': resolved['canonical_name'],
                'confidence': resolved['confidence'],
                'raw_term': term
            })
        else:
            result['unresolved_environment'].append(term)
    
    # Resolve outcome terms
    for term in outcome_terms:
        if not term:
            continue
        
        if queue_unresolved:
            resolved, queued = resolve_or_queue(term, paper_id=paper_id)
        else:
            resolved = resolve_outcome(term)
            queued = False
        
        if resolved:
            result['outcomes'].append({
                'id': resolved['canonical_id'],
                'canonical_name': resolved.get('name', resolved['canonical_id']),
                'confidence': resolved['confidence'],
                'raw_term': term
            })
        else:
            result['unresolved_outcomes'].append(term)
    
    return result


def resolve_single_construct(
    raw_term: str,
    construct_type: str,  # 'environment' or 'outcome'
    paper_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Resolve a single construct term.
    
    Args:
        raw_term: The raw term to resolve
        construct_type: 'environment' for IVs, 'outcome' for DVs
        paper_id: Paper ID for context
    
    Returns:
        Dict with canonical_id and metadata, or placeholder if unresolved
    """
    if construct_type == 'environment':
        resolved = resolve_environment(raw_term)
        if resolved:
            return {
                'canonical_id': resolved['tag_id'],
                'canonical_name': resolved['canonical_name'],
                'confidence': resolved['confidence'],
                'resolved': True
            }
    elif construct_type == 'outcome':
        resolved = resolve_outcome(raw_term)
        if resolved:
            return {
                'canonical_id': resolved['canonical_id'],
                'canonical_name': resolved.get('name', ''),
                'confidence': resolved['confidence'],
                'resolved': True
            }
    
    # Unresolved - return placeholder
    safe_id = raw_term.lower().replace(' ', '_')[:50]
    return {
        'canonical_id': f"UNRESOLVED:{construct_type}:{safe_id}",
        'canonical_name': raw_term,
        'confidence': 0.0,
        'resolved': False
    }


def get_stats() -> Dict[str, Any]:
    """Get resolver statistics."""
    from .environment_resolver import _load_lookup as load_env
    from .outcome_resolver import _load_lookup as load_out
    
    env_data = load_env()
    out_data = load_out()
    
    return {
        'environment_tags': len(env_data.get('tags', {})),
        'environment_lookup_entries': len(env_data.get('lookup', {})),
        'outcome_terms': len(out_data.get('terms', {})),
        'outcome_lookup_entries': len(out_data.get('lookup', {})),
    }
