#!/usr/bin/env python3
"""
Analyze unresolved outcomes to expand vocabulary from 24 to 80+ terms.
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import List, Set, Tuple

def load_unresolved_outcomes() -> List[str]:
    """Load all unresolved outcome terms."""
    path = Path("data/unresolved_outcomes.jsonl")
    terms = []

    with open(path) as f:
        for line in f:
            if line.strip():
                entry = json.loads(line)
                terms.append(entry['raw_term'])

    return terms

def is_garbage(term: str) -> bool:
    """Identify obvious OCR artifacts and noise."""
    # Too short or too long
    if len(term) < 3 or len(term) > 100:
        return True

    # Mostly non-alphabetic
    alpha_count = sum(1 for c in term.lower() if c.isalpha() or c in '-. ')
    if alpha_count / max(len(term), 1) < 0.5:
        return True

    # Clear OCR artifacts
    artifacts = ['amp', 'ocr', 'b0', 'b1', 'f2', 'nnz', 'vasad', 'ricreationi']
    for artifact in artifacts:
        if artifact in term.lower():
            return True

    # Mathematical/formula fragments
    if re.search(r'[°<>μ]', term) or '0.9' in term or '(p<0' in term:
        return True

    # Clearly technical/unrelated to human outcomes
    unrelated = [
        'graphene', 'polymer', 'lattice', 'qcd', 'planck', 'magnetohydrodynamic',
        'image', 'dataset', 'learning', 'algorithm', 'framework', 'model',
        'segmentation', 'classification', 'routing', 'network', 'optical',
        'semiconductor', 'circuit', 'biotech', 'chemical', 'molecular',
        'phytoplankton', 'mitochondria', 'hydrogen'
    ]
    for term_check in unrelated:
        if term_check in term.lower():
            return True

    return False

def cluster_by_keywords(terms: List[str]) -> dict:
    """Cluster terms by keyword overlap."""
    clusters = defaultdict(list)

    # Define domain-specific keywords
    keyword_map = {
        'cognition': ['attention', 'memory', 'cognit', 'think', 'learn', 'focus', 'concentration', 'executive', 'reasoning', 'creativity', 'perception', 'decision'],
        'affect': ['mood', 'emotion', 'affect', 'stress', 'anxiety', 'depression', 'happy', 'sadness', 'frustration', 'calm', 'well-being', 'satisfaction'],
        'behavior': ['behavior', 'behaviour', 'activity', 'action', 'productivity', 'sleep', 'performance', 'task', 'engagement', 'occupancy', 'mobility'],
        'social': ['social', 'interaction', 'communication', 'collaboration', 'team', 'relationship', 'cooperation', 'interpersonal'],
        'physiology': ['heart', 'blood', 'cortisol', 'fatigue', 'pain', 'alertness', 'arousal', 'thermal', 'comfort', 'respiration', 'pressure'],
        'neural': ['brain', 'neural', 'cortex', 'eeg', 'fmri', 'neuronal', 'activity'],
        'health': ['health', 'wellbeing', 'well-being', 'wellness', 'illness', 'disease', 'recovery', 'fitness', 'nutrition'],
        'environmental': ['environment', 'quality', 'air', 'light', 'noise', 'natural', 'landscape', 'setting', 'space'],
        'creativity': ['creativity', 'creative', 'innovation', 'design', 'artistic']
    }

    for term in terms:
        term_lower = term.lower()
        best_domain = None
        max_matches = 0

        for domain, keywords in keyword_map.items():
            matches = sum(1 for kw in keywords if kw in term_lower)
            if matches > max_matches:
                max_matches = matches
                best_domain = domain

        if best_domain:
            clusters[best_domain].append(term)
        else:
            clusters['other'].append(term)

    return clusters

def deduplicate_case_insensitive(terms: List[str]) -> Tuple[List[str], dict]:
    """Deduplicate case-insensitively and track originals."""
    canonical = {}
    seen = {}

    for term in terms:
        canonical_form = term.lower().strip()

        if canonical_form not in seen:
            seen[canonical_form] = term
            canonical[canonical_form] = canonical_form

    return list(seen.values()), seen

def extract_key_terms(terms: List[str]) -> List[Tuple[str, int]]:
    """Extract most frequent meaningful terms."""
    # Simple frequency counter
    term_freq = Counter(t.lower() for t in terms)

    # Filter for meaningful terms
    meaningful = []
    for term, freq in term_freq.most_common(100):
        words = term.split()
        # Prefer multi-word or domain-specific terms
        if len(words) >= 2 or any(d in term for d in ['stress', 'attention', 'memory', 'mood', 'fatigue', 'comfort', 'satisfaction', 'wellbeing', 'creativity', 'productivity']):
            meaningful.append((term, freq))

    return meaningful

def main():
    print("=" * 80)
    print("OUTCOME VOCABULARY EXPANSION ANALYSIS")
    print("=" * 80)

    # Load data
    raw_terms = load_unresolved_outcomes()
    print(f"\nTotal unresolved outcomes: {len(raw_terms)}")

    # Filter garbage
    clean_terms = [t for t in raw_terms if not is_garbage(t)]
    print(f"After garbage filtering: {len(clean_terms)}")

    # Deduplicate case-insensitively
    dedup, seen_map = deduplicate_case_insensitive(clean_terms)
    print(f"Unique (case-insensitive): {len(dedup)}")

    # Cluster by domain
    clusters = cluster_by_keywords(dedup)
    print(f"\nDomain clustering:")
    for domain in sorted(clusters.keys()):
        print(f"  {domain:20} {len(clusters[domain]):4} terms")

    # Top terms per domain
    print(f"\nTop 15 terms per domain:")
    for domain in sorted(clusters.keys()):
        terms_in_domain = clusters[domain]
        freq = Counter(t.lower() for t in terms_in_domain)
        top = freq.most_common(15)
        print(f"\n{domain.upper()}:")
        for term, count in top:
            print(f"    {term:40} (freq: {count})")

    # Extract and display candidate terms
    print(f"\nMost frequent meaningful terms (top 50):")
    meaningful = extract_key_terms(dedup)
    for i, (term, freq) in enumerate(meaningful[:50], 1):
        print(f"  {i:2}. {term:50} freq={freq}")

    print("\n" + "=" * 80)
    print("RECOMMENDATIONS:")
    print("=" * 80)
    print("""
Based on the analysis:

1. COGNITION DOMAIN (expand from 4 to 10-12 terms):
   - Attention types: sustained, selective, divided, broad
   - Memory: working, episodic, semantic, long-term
   - Executive function, processing speed
   - Creativity, problem-solving

2. AFFECTIVE DOMAIN (expand from 6 to 12-15 terms):
   - Stress-related: perceived stress, burnout, relaxation
   - Mood: positive/negative affect, contentment, satisfaction
   - Emotional regulation, resilience

3. BEHAVIORAL DOMAIN (expand from 3 to 8-10 terms):
   - Productivity, task engagement, focus
   - Sleep quality and duration
   - Physical activity, movement
   - Occupancy/presence, dwell time

4. PHYSIOLOGICAL (expand from 3 to 10-12 terms):
   - Stress markers: cortisol, heart rate variability
   - Thermal comfort, alertness, arousal
   - Pain, fatigue, recovery

5. ENVIRONMENTAL PSYCHOLOGY (NEW 1-2 domains):
   - Environmental quality assessment
   - Prospect-Refuge constructs
   - Lighting, noise, air quality perception

6. SOCIAL (expand from 3 to 5-7 terms):
   - Collaboration quality, trust
   - Social presence, cohesion

7. NEURAL (keep 1, expand to 3-5):
   - EEG signatures, brain activation patterns
   - Neural efficiency, synchrony
""")

if __name__ == '__main__':
    main()
