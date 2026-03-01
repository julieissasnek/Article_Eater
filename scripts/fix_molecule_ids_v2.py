#!/usr/bin/env python3
"""
fix_molecule_ids_v2.py

Smarter molecule_ids remapping using paper content analysis.

PROBLEM: All 532 rasa attractor assignments were mapped to only 2 attractors:
- shringara: 339 assignments
- adbhuta: 193 assignments

SOLUTION: Use paper content (title, abstract, outcome domains, finding directions)
to assign semantically correct attractors across all 9 rasas.

RASA ATTRACTOR MAPPING HEURISTIC:
- shringara (love/beauty/aesthetic): beauty, aesthetic, preference, attractive, pleasant
- hasya (joy/humor): joy, humor, play, fun, social bonding, laughter
- karuna (compassion/sadness): empathy, care, healing, therapeutic, loss, sadness
- veera (heroism/courage): empowerment, agency, control, mastery, courage, challenge
- bibhatsa (disgust): disgust, pollution, decay, unsanitary, aversion, revulsion
- bhayanaka (fear/terror): fear, anxiety, threat, unsafe, crime, terror, worry
- raudra (anger/wrath): anger, frustration, stress, noise annoyance, crowding stress
- shanta (peace/serenity): restoration, relaxation, calm, tranquil, peace, recovery
- adbhuta (wonder): wonder, novelty, surprise, curiosity, exploration, astonishment

ASSIGNMENT RULES:
1. Look at outcome domain (e.g., affect.anxiety → bhayanaka)
2. Look at finding direction: if findings show STRESS/FEAR DECREASE, map to shanta
3. Use paper title and abstract keywords for initial hint
4. Be conservative: only assign if fairly confident
"""

import json
import os
from collections import defaultdict
from pathlib import Path
import re

EXTRACTION_DIR = "/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/data/extractions"

# Rasa attractor keywords and outcome domain associations
RASA_KEYWORDS = {
    "shanta": {
        "keywords": [
            "restoration", "restored", "relaxation", "relaxed", "calm", "calming",
            "tranquil", "tranquility", "peaceful", "peace", "serenity", "serene",
            "recovery", "recovering", "recuperation", "stress reduction", "stress recovery",
            "stress relief", "anxiety reduction", "anxiety relief", "sleep quality",
            "restorative", "unwind", "de-stress", "de-arousal", "deactivation"
        ],
        "outcome_domains": ["affect.restoration", "affect.calm", "health.sleep"],
        "find_directions": ["decrease"],  # when anxiety/stress DECREASES
        "antecedent_keywords": ["green space", "natural environment", "water feature", "garden"],
        "consequent_keywords": ["stress", "anxiety", "arousal", "cortisol"]
    },
    "bhayanaka": {
        "keywords": [
            "fear", "feared", "anxiety", "anxious", "threat", "threatening", "threat perception",
            "fear response", "fearful", "scared", "unsafe", "danger", "dangerous", "crime",
            "violence", "violent", "terror", "terror response", "panic", "phobia",
            "worry", "concerned", "threat detection", "aversion", "avoidance"
        ],
        "outcome_domains": ["affect.anxiety", "affect.fear", "health.trauma"],
        "find_directions": ["increase"],  # anxiety/fear INCREASES with antecedent
        "antecedent_keywords": ["violence", "crime", "threat", "dangerous", "dark", "isolated"],
        "consequent_keywords": ["fear", "anxiety", "threat", "danger"]
    },
    "raudra": {
        "keywords": [
            "anger", "angry", "wrath", "wrathful", "frustration", "frustrated",
            "stress", "stressed", "stressful", "stressor", "annoyance", "annoyed",
            "irritation", "irritated", "noise annoyance", "crowding stress", "agitation",
            "arousal", "negative affect", "displeasure", "dissatisfaction"
        ],
        "outcome_domains": ["affect.anger", "affect.stress", "health.cortisol"],
        "find_directions": ["increase"],
        "antecedent_keywords": ["noise", "crowding", "pollution", "heat stress", "interruption"],
        "consequent_keywords": ["stress", "anger", "frustration", "arousal", "cortisol"]
    },
    "shringara": {
        "keywords": [
            "beauty", "beautiful", "aesthetic", "aesthetics", "aesthetic pleasure",
            "aesthetic appreciation", "preference", "preferred", "attractive", "attractiveness",
            "pleasant", "pleasantness", "enjoyment", "delight", "likability", "liking",
            "visual appeal", "charm", "charming", "elegant", "elegance", "lovely"
        ],
        "outcome_domains": ["affect.pleasure", "perception.beauty", "social.attraction"],
        "find_directions": ["increase"],
        "antecedent_keywords": ["color", "symmetry", "proportion", "design", "architecture"],
        "consequent_keywords": ["preference", "liking", "pleasure", "attraction"]
    },
    "adbhuta": {
        "keywords": [
            "wonder", "wonderful", "astonishment", "astonished", "novelty", "novel",
            "surprise", "surprised", "curiosity", "curious", "exploration", "exploratory",
            "discovery", "discover", "awe", "awesome", "amazement", "amazing",
            "interest", "interesting", "intrigue", "intriguing", "fascination", "fascinated"
        ],
        "outcome_domains": ["cognitive.creativity", "cognitive.learning", "social.exploration"],
        "find_directions": ["increase"],
        "antecedent_keywords": ["new", "novel", "unexpected", "surprising", "complex"],
        "consequent_keywords": ["curiosity", "interest", "learning", "creativity"]
    },
    "hasya": {
        "keywords": [
            "joy", "joyful", "happiness", "happy", "humor", "humorous", "funny",
            "laughter", "laughing", "play", "playful", "playfulness", "fun", "enjoyment",
            "social bonding", "bonding", "affiliation", "positive affect", "amusement",
            "cheerfulness", "cheerful", "mirth"
        ],
        "outcome_domains": ["affect.joy", "social.bonding", "health.wellbeing"],
        "find_directions": ["increase"],
        "antecedent_keywords": ["social interaction", "game", "play", "humor", "joke"],
        "consequent_keywords": ["joy", "laughter", "bonding", "happiness"]
    },
    "karuna": {
        "keywords": [
            "compassion", "compassionate", "empathy", "empathic", "empathetic", "care",
            "caring", "concern", "concerned", "grief", "grieving", "sadness", "sad",
            "sorrow", "sorrowful", "loss", "healing", "therapeutic", "therapy",
            "suffering", "sympathy", "sympathetic", "concern", "support"
        ],
        "outcome_domains": ["affect.sadness", "social.empathy", "health.therapeutic"],
        "find_directions": ["increase"],  # loss/grief increases, or healing increases
        "antecedent_keywords": ["loss", "grief", "suffering", "illness", "death"],
        "consequent_keywords": ["empathy", "compassion", "healing", "support"]
    },
    "veera": {
        "keywords": [
            "empowerment", "empowered", "agency", "agentic", "control", "controllability",
            "mastery", "mastering", "achievement", "accomplishment", "challenge",
            "challenging", "courage", "courageous", "heroism", "heroic", "vigor",
            "determination", "persistence", "motivation", "achievement motivation"
        ],
        "outcome_domains": ["affect.empowerment", "social.agency", "cognitive.mastery"],
        "find_directions": ["increase"],
        "antecedent_keywords": ["challenge", "goal", "obstacle", "difficulty"],
        "consequent_keywords": ["empowerment", "mastery", "control", "achievement"]
    },
    "bibhatsa": {
        "keywords": [
            "disgust", "disgusting", "disgusted", "aversion", "aversive", "repulsion",
            "repulsive", "revulsion", "revolting", "pollution", "polluted", "contamination",
            "contaminated", "decay", "decayed", "unsanitary", "unhygienic", "filth",
            "filthy", "gross", "icky", "unpleasant", "displeasure"
        ],
        "outcome_domains": ["affect.disgust", "health.hygiene", "perception.contamination"],
        "find_directions": ["increase"],
        "antecedent_keywords": ["pollution", "waste", "decay", "unsanitary", "pathogen"],
        "consequent_keywords": ["disgust", "aversion", "avoidance", "contamination"]
    }
}

def extract_finding_keywords(extraction):
    """Extract relevant finding keywords from extraction data."""
    keywords = []
    
    if 'title' in extraction:
        keywords.extend(extraction['title'].lower().split())
    
    if 'research_question' in extraction:
        keywords.extend(extraction['research_question'].lower().split())
    
    if 'abstract' in extraction:
        keywords.extend(extraction['abstract'].lower().split())
    
    if 'central_proposition' in extraction:
        keywords.extend(extraction['central_proposition'].lower().split())
    
    if 'findings' in extraction:
        for finding in extraction.get('findings', []):
            if 'antecedent' in finding:
                keywords.extend(finding['antecedent'].lower().split())
            if 'consequent' in finding:
                keywords.extend(finding['consequent'].lower().split())
            if 'mechanism' in finding and finding['mechanism']:
                keywords.extend(finding['mechanism'].lower().split())
    
    return keywords

def calculate_rasa_scores(extraction):
    """Score each rasa attractor based on extraction content."""
    scores = {rasa: 0.0 for rasa in RASA_KEYWORDS}
    
    # Get all keywords from extraction
    extraction_keywords = extract_finding_keywords(extraction)
    text_lower = " ".join(extraction_keywords).lower()
    
    # Check outcome domains
    outcome_domains = set()
    if 'findings' in extraction:
        for finding in extraction['findings']:
            if 'outcome_domain' in finding:
                outcome_domains.add(finding['outcome_domain'])
    
    # Check finding directions
    finding_directions = []
    if 'findings' in extraction:
        for finding in extraction['findings']:
            if 'direction' in finding:
                finding_directions.append(finding['direction'])
    
    # Score each rasa
    for rasa, rasa_config in RASA_KEYWORDS.items():
        score = 0.0
        
        # Check keyword matches
        for kw in rasa_config['keywords']:
            if kw in text_lower:
                score += 2.0
        
        # Check outcome domain matches
        for od in rasa_config['outcome_domains']:
            if od in outcome_domains:
                score += 3.0
        
        # Check direction matches (important for shanta/bhayanaka)
        for fd in rasa_config['find_directions']:
            if fd in finding_directions:
                # Special case: if finding direction is 'decrease' and antecedent is stress-related
                # and rasa is shanta, boost score
                if fd == 'decrease' and rasa == 'shanta':
                    stress_keywords = ['stress', 'anxiety', 'cortisol', 'arousal']
                    for finding in extraction.get('findings', []):
                        if any(sk in finding.get('consequent', '').lower() for sk in stress_keywords):
                            if finding.get('direction') == 'decrease':
                                score += 4.0
        
        scores[rasa] = score
    
    return scores

def assign_molecule_ids(extraction):
    """Assign 1-3 rasa attractors based on content analysis."""
    scores = calculate_rasa_scores(extraction)
    
    # Get top 3 scores
    sorted_rasas = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # Assign if score > 0, up to 3 attractors
    assigned = []
    for rasa, score in sorted_rasas[:3]:
        if score > 0:
            assigned.append(rasa)
    
    # Fallback: if no rasa scored above 0, use adbhuta (wonder) as default
    # since these are all research papers and they all involve discovery
    if not assigned:
        assigned = ["adbhuta"]
    
    return assigned

def process_extractions():
    """Process all extractions and remapp molecule_ids."""
    stats = {
        'total_files': 0,
        'files_with_molecule_ids': 0,
        'files_remapped': 0,
        'rasa_distribution': defaultdict(int),
        'assignment_count': 0,
        'errors': []
    }
    
    for filename in sorted(os.listdir(EXTRACTION_DIR)):
        if not filename.endswith('.json'):
            continue
        
        filepath = os.path.join(EXTRACTION_DIR, filename)
        stats['total_files'] += 1
        
        try:
            with open(filepath) as f:
                extraction = json.load(f)
            
            # Only process files that had molecule_ids before
            if 'molecule_ids' not in extraction:
                continue
            
            stats['files_with_molecule_ids'] += 1
            old_molecule_ids = extraction['molecule_ids']
            
            # Check if this file had rasa attractors (shringara or adbhuta)
            rasa_attractors = {"shringara", "hasya", "karuna", "veera", 
                             "bibhatsa", "bhayanaka", "raudra", "shanta", "adbhuta"}
            has_old_rasa = any(mid in rasa_attractors for mid in old_molecule_ids)
            
            if not has_old_rasa:
                continue
            
            # Assign new molecule_ids using content analysis
            new_rasa_ids = assign_molecule_ids(extraction)
            
            # Preserve non-rasa molecule_ids (like "srt", "multisensory_design", etc)
            non_rasa_ids = [mid for mid in old_molecule_ids if mid not in rasa_attractors]
            
            # Combine: new rasa attractors + old non-rasa ids
            extraction['molecule_ids'] = new_rasa_ids + non_rasa_ids
            
            stats['files_remapped'] += 1
            for rasa in new_rasa_ids:
                stats['rasa_distribution'][rasa] += 1
                stats['assignment_count'] += 1
            
            # Write back
            with open(filepath, 'w') as f:
                json.dump(extraction, f, indent=2)
        
        except Exception as e:
            stats['errors'].append(f"{filename}: {str(e)}")
    
    return stats

if __name__ == '__main__':
    print("=" * 70)
    print("MOLECULE_IDS REMAPPING V2: SEMANTIC CONTENT-BASED ASSIGNMENT")
    print("=" * 70)
    
    stats = process_extractions()
    
    print(f"\nProcessing Results:")
    print(f"  Total extraction files: {stats['total_files']}")
    print(f"  Files with molecule_ids: {stats['files_with_molecule_ids']}")
    print(f"  Files remapped: {stats['files_remapped']}")
    print(f"\nNew Rasa Attractor Distribution:")
    
    rasa_attractors_ordered = [
        "shringara", "hasya", "karuna", "veera",
        "bibhatsa", "bhayanaka", "raudra", "shanta", "adbhuta"
    ]
    
    for rasa in rasa_attractors_ordered:
        count = stats['rasa_distribution'][rasa]
        pct = (count / stats['assignment_count'] * 100) if stats['assignment_count'] > 0 else 0
        print(f"  {rasa:12s}: {count:4d} ({pct:5.1f}%)")
    
    print(f"\nTotal rasa assignments: {stats['assignment_count']}")
    
    if stats['errors']:
        print(f"\nErrors encountered: {len(stats['errors'])}")
        for err in stats['errors'][:5]:
            print(f"  - {err}")

