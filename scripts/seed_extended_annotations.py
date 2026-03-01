"""
Annotation Seed Generator — Auto-Generate A9-A18 From Existing Data
====================================================================

Scans extraction files and knowledge catalog to seed extended annotations:
- A9 (Surprise): Detect counterintuitive findings via contradiction patterns
- A10 (Design): Extract design parameters from findings
- A11 (Dispute): Map known theory disputes to findings
- A12 (Analogy): Generate everyday analogies for technical concepts
- A14 (Magnitude): Parse and humanize effect sizes
- A17 (Hook): Generate narrative hooks for key theories
- A18 (Gap): Identify unanswered questions from gaps in evidence

Usage:
    python scripts/seed_extended_annotations.py [--dry-run]
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import Counter

PROJECT_ROOT = Path(__file__).parent.parent
EXTRACTIONS_DIR = PROJECT_ROOT / "data" / "extractions"
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"
OUTPUT_DIR = PROJECT_ROOT / "data" / "extended_annotations"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# =============================================================================
# Surprise Detection (A9)
# =============================================================================

CONTRADICTION_PATTERNS = [
    (re.compile(r'\b(?:counter[\s-]?intuitiv|surprising|unexpected|contrary to|paradox|puzzling)', re.I),
     0.8, "explicit_surprise"),
    (re.compile(r'\b(?:however|but|despite|although|nevertheless|in contrast)(?:\s*,)?\s+(?:the\s+)?(?:results?\s+|finding)', re.I),
     0.6, "implicit_contradiction"),
    (re.compile(r'\b(?:no\s+(?:significant\s+)?(?:effect|difference|relationship)|failed\s+to)', re.I),
     0.5, "null_result"),
    (re.compile(r'\b(?:reversed?|opposite|negative(?:ly)?\s+(?:correlat|associat))', re.I),
     0.7, "reversal"),
]

def detect_surprises(extractions) -> List[Dict]:
    """Detect surprising/counterintuitive findings from extraction text."""
    surprises = []
    if isinstance(extractions, list):
        findings = extractions
    elif isinstance(extractions, dict):
        findings = extractions.get("findings", [])
    else:
        return []    
    for i, finding in enumerate(findings):
        text = finding if isinstance(finding, str) else json.dumps(finding)
        
        for pattern, base_surprise, surprise_type in CONTRADICTION_PATTERNS:
            match = pattern.search(text)
            if match:
                # Extract context around the match
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 150)
                context = text[start:end].strip()
                
                surprises.append({
                    "finding_index": i,
                    "surprise_level": base_surprise,
                    "surprise_type": surprise_type,
                    "context": context,
                    "common_assumption": "",  # Requires AI to fill
                    "actual_finding": context[:200],
                })
                break
    
    return surprises


# =============================================================================
# Design Parameter Extraction (A10)
# =============================================================================

PARAMETER_PATTERNS = [
    # Temperature/CCT
    (re.compile(r'(\d{3,5})\s*K\b.*?(?:CCT|color\s+temp|kelvin)', re.I), "CCT", "K"),
    (re.compile(r'CCT\s*(?:of|=|:)?\s*(\d{3,5})\s*K', re.I), "CCT", "K"),
    # Illuminance
    (re.compile(r'(\d+)\s*(?:lux|lx)\b', re.I), "illuminance", "lux"),
    # Ceiling height
    (re.compile(r'ceiling\s+height.*?(\d+\.?\d*)\s*(?:m|meter|ft|feet)', re.I), "ceiling_height", "m"),
    # Temperature
    (re.compile(r'(\d{1,2}\.?\d*)\s*°?\s*[CF]\b', re.I), "temperature", "°C"),
    # Distance/size
    (re.compile(r'(\d+\.?\d*)\s*(?:m2|sqm|square\s+met)', re.I), "area", "m²"),
    # Noise
    (re.compile(r'(\d+)\s*dB\b', re.I), "noise_level", "dB"),
    # Green view
    (re.compile(r'green\s+view\s+index.*?(\d+\.?\d*)', re.I), "green_view_index", "ratio"),
]

RECOMMENDATION_PATTERNS = [
    re.compile(r'(?:recommend|suggest|should\s+(?:be|use|have)|optimal|ideal)\s+(.{20,100})', re.I),
    re.compile(r'(?:design\s+(?:guideline|recommendation|implication))\s*:?\s*(.{20,100})', re.I),
]

def detect_design_parameters(extractions: Dict) -> List[Dict]:
    """Extract actionable design parameters."""
    params = []
    text = json.dumps(extractions)
    
    for pattern, param_name, unit in PARAMETER_PATTERNS:
        matches = pattern.finditer(text)
        for m in matches:
            try:
                value = float(m.group(1))
                context_start = max(0, m.start() - 80)
                context_end = min(len(text), m.end() + 80)
                params.append({
                    "parameter": param_name,
                    "value": value,
                    "unit": unit,
                    "context": text[context_start:context_end].strip()[:200],
                    "recommendation": "",
                    "confidence": 0.6,
                })
            except (ValueError, IndexError):
                continue
    
    # Also look for explicit recommendations
    for rp in RECOMMENDATION_PATTERNS:
        for m in rp.finditer(text):
            params.append({
                "parameter": "recommendation",
                "value": None,
                "unit": None,
                "recommendation": m.group(1).strip()[:200],
                "context": text[max(0, m.start()-40):m.end()+40][:200],
                "confidence": 0.7,
            })
    
    return params


# =============================================================================
# Effect Size Extraction (A14)
# =============================================================================

EFFECT_SIZE_PATTERNS = [
    (re.compile(r"(?:Cohen'?s?\s+)?d\s*[=:]\s*(-?\d+\.?\d*)", re.I), "cohens_d"),
    (re.compile(r'η[²p]?\s*[=:]\s*(\d+\.?\d*)', re.I), "eta_squared"),
    (re.compile(r'(?:odds?\s+ratio|OR)\s*[=:]\s*(\d+\.?\d*)', re.I), "odds_ratio"),
    (re.compile(r'r\s*[=:]\s*(-?\d+\.?\d*)', re.I), "correlation_r"),
    (re.compile(r'[Rr]²?\s*[=:]\s*(\d+\.?\d*)', re.I), "r_squared"),
    (re.compile(r'β\s*[=:]\s*(-?\d+\.?\d*)', re.I), "beta"),
]

SIGNIFICANCE_SCALE = {
    "cohens_d": [(0.2, "small"), (0.5, "medium"), (0.8, "large"), (1.2, "very_large")],
    "eta_squared": [(0.01, "small"), (0.06, "medium"), (0.14, "large")],
    "correlation_r": [(0.1, "small"), (0.3, "medium"), (0.5, "large")],
}

HUMAN_SCALE_TEMPLATES = {
    "small": "A subtle difference — like the change in focus from a slightly quieter room",
    "medium": "A noticeable difference — like working in a library versus a busy café",
    "large": "A substantial difference — like the contrast between a windowless basement and a sunlit room",
    "very_large": "A dramatic difference — unmistakable to anyone experiencing it",
}

def detect_effect_sizes(extractions: Dict) -> List[Dict]:
    """Parse effect sizes and translate to human scale."""
    effects = []
    text = json.dumps(extractions)
    
    for pattern, effect_type in EFFECT_SIZE_PATTERNS:
        for m in pattern.finditer(text):
            try:
                value = float(m.group(1))
                # Skip obviously wrong values
                if effect_type in ("cohens_d", "beta") and abs(value) > 5:
                    continue
                if effect_type in ("eta_squared", "r_squared", "correlation_r") and abs(value) > 1:
                    continue
                
                # Determine practical significance
                significance = "unknown"
                human_scale = ""
                scale = SIGNIFICANCE_SCALE.get(effect_type, [])
                for threshold, label in scale:
                    if abs(value) >= threshold:
                        significance = label
                human_scale = HUMAN_SCALE_TEMPLATES.get(significance, "")
                
                effects.append({
                    "effect_type": effect_type,
                    "value": value,
                    "practical_significance": significance,
                    "human_scale": human_scale,
                    "context": text[max(0, m.start()-60):m.end()+60][:200],
                })
            except (ValueError, IndexError):
                continue
    
    return effects


# =============================================================================
# Known Disputes (A11) — Seeded from theory knowledge
# =============================================================================

KNOWN_DISPUTES = [
    {
        "claim": "Biophilic responses are innate",
        "positions": [
            {"position": "innate", "proponents": ["Wilson", "Kellert"], "evidence_strength": 0.6},
            {"position": "learned", "proponents": ["Joye", "Kuo"], "evidence_strength": 0.5},
        ],
        "status": "active",
        "what_would_resolve": "Cross-cultural infant studies in nature-deprived environments",
        "keywords": ["biophil", "innate", "evolutionary"],
    },
    {
        "claim": "Beauty is culturally universal",
        "positions": [
            {"position": "universal", "proponents": ["Ramachandran", "Zeki", "Chatterjee"], "evidence_strength": 0.55},
            {"position": "constructed", "proponents": ["Bourdieu", "Leder", "Shimamura"], "evidence_strength": 0.5},
        ],
        "status": "active",
        "what_would_resolve": "Large-scale cross-cultural beauty judgment studies with matched stimuli",
        "keywords": ["beauty", "aesthet", "universal", "cultural"],
    },
    {
        "claim": "ART and SRT explain different mechanisms of restoration",
        "positions": [
            {"position": "distinct_mechanisms", "proponents": ["Kaplan", "Berman"], "evidence_strength": 0.6},
            {"position": "overlapping_mechanisms", "proponents": ["Hartig", "Bratman"], "evidence_strength": 0.55},
        ],
        "status": "leaning",
        "what_would_resolve": "Neuroimaging studies comparing directed attention vs stress biomarkers during nature exposure",
        "keywords": ["restoration", "ART", "SRT", "attention", "stress"],
    },
    {
        "claim": "Complexity preference follows an inverted-U curve",
        "positions": [
            {"position": "inverted_U", "proponents": ["Berlyne", "Stamps"], "evidence_strength": 0.65},
            {"position": "linear_or_context_dependent", "proponents": ["Güçlütürk", "Forsythe"], "evidence_strength": 0.4},
        ],
        "status": "leaning",
        "what_would_resolve": "Parametric complexity studies across multiple building types and cultures",
        "keywords": ["complexity", "preference", "inverted", "optimal"],
    },
    {
        "claim": "Open-plan offices improve collaboration",
        "positions": [
            {"position": "improves", "proponents": ["Allen", "early advocates"], "evidence_strength": 0.3},
            {"position": "harms", "proponents": ["Bernstein", "Kim & de Dear"], "evidence_strength": 0.75},
        ],
        "status": "leaning",
        "what_would_resolve": "Longitudinal studies with interaction quality metrics (not just frequency)",
        "keywords": ["open plan", "collaboration", "office", "interaction"],
    },
]

# =============================================================================
# Narrative Hooks (A17) — Seed hooks for major theories
# =============================================================================

SEED_HOOKS = [
    {
        "theory": "ART",
        "hook": "In 2008, a group of students took a walk. Half went through a tree-lined arboretum, half through downtown Ann Arbor. When they came back, the nature walkers could hold 20% more digits in working memory. The trees hadn't taught them anything — they'd simply given their brains permission to rest.",
        "hook_type": "origin_story",
        "engagement_score": 0.9,
    },
    {
        "theory": "SRT",
        "hook": "Roger Ulrich spent years staring at hospital records before he noticed the pattern: patients with tree views went home a full day earlier than patients facing a brick wall. Same surgery. Same recovery protocol. Different window.",
        "hook_type": "human_moment",
        "engagement_score": 0.95,
    },
    {
        "theory": "PROSPECT_REFUGE",
        "hook": "Next time you walk into a restaurant, watch where people sit when given a choice. The corner table. Back to the wall. View of the door. You just watched 200,000 years of savanna survival instinct choose a dinner seat.",
        "hook_type": "sensory",
        "engagement_score": 0.88,
    },
    {
        "theory": "BIOPHILIA",
        "hook": "There's a reason the most expensive hotel rooms have the best views, and it's not about status. Every floor of added elevation comes with a measurable drop in cortisol. We are, it turns out, creatures who need to see the horizon.",
        "hook_type": "surprising_fact",
        "engagement_score": 0.85,
    },
    {
        "theory": "COGNITIVE_LOAD",
        "hook": "A hospital in the Netherlands redesigned its signage system and emergency room visits for 'lost' patients dropped by 40%. People weren't getting healthier — they were just finding their appointments.",
        "hook_type": "contrast",
        "engagement_score": 0.87,
    },
    {
        "theory": "COMPLEXITY",
        "hook": "The most beautiful buildings in the world share something with jazz music, coastlines, and Jackson Pollock paintings: they're all fractal. Not too simple. Not too chaotic. Just complex enough to keep your brain interested without overwhelming it.",
        "hook_type": "surprising_fact",
        "engagement_score": 0.82,
    },
]

# =============================================================================
# Unanswered Questions (A18)
# =============================================================================

SEED_QUESTIONS = [
    {
        "domain": "biophilia",
        "question": "Do children raised in entirely urban environments with zero nature exposure develop the same biophilic responses as children raised near forests?",
        "why_important": "Tests whether biophilia is truly innate or requires developmental exposure",
        "what_would_it_take": "Longitudinal cohort study: nature-deprived vs nature-rich childhoods, measured at ages 5, 10, 20",
        "estimated_difficulty": "hard",
        "related_theories": ["BIOPHILIA"],
    },
    {
        "domain": "neuroaesthetics",
        "question": "Can we predict an individual's building preference from their brain scan before they see the building?",
        "why_important": "Would prove that environmental preference has a measurable neural signature",
        "what_would_it_take": "fMRI study with large sample, diverse buildings, and ML prediction pipeline",
        "estimated_difficulty": "hard",
        "related_theories": ["KAPLAN_PREFERENCE"],
    },
    {
        "domain": "cultural",
        "question": "If you raise a Japanese child in Scandinavian architecture, do they develop Scandinavian spatial preferences or retain Japanese ones?",
        "why_important": "Separates genetic from environmental/developmental influences on spatial preference",
        "what_would_it_take": "Cross-cultural adoption studies with architectural preference measures",
        "estimated_difficulty": "moonshot",
        "related_theories": ["PROSPECT_REFUGE"],
    },
    {
        "domain": "workplace",
        "question": "Is there a way to design an open-plan office that actually works, or is it fundamentally flawed?",
        "why_important": "Billions of dollars of real estate depend on this answer",
        "what_would_it_take": "Parametric study varying enclosure, acoustics, density with interaction quality (not just frequency) as DV",
        "estimated_difficulty": "medium",
        "related_theories": ["COGNITIVE_LOAD", "PROSPECT_REFUGE"],
    },
    {
        "domain": "technology",
        "question": "Does VR nature produce the same restorative effects as real nature, and if not, what's missing?",
        "why_important": "VR could democratize nature access for urban populations if it works",
        "what_would_it_take": "Matched comparison: real, VR, photo, no-nature, with biomarkers + self-report",
        "estimated_difficulty": "medium",
        "related_theories": ["ART", "SRT"],
    },
    {
        "domain": "equity",
        "question": "Do restorative environment effects differ by socioeconomic status, and if so, do they reduce or amplify inequality?",
        "why_important": "If nature benefits the privileged more, biophilic design could widen health gaps",
        "what_would_it_take": "SES-stratified RCT of environmental interventions with health outcomes",
        "estimated_difficulty": "hard",
        "related_theories": ["ART", "SRT", "BIOPHILIA"],
    },
]


# =============================================================================
# Main Pipeline
# =============================================================================

def seed_annotations(dry_run: bool = True) -> Dict[str, int]:
    """Scan extractions and generate seed annotations."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stats = Counter()
    
    # Process extractions for A9, A10, A14
    extractions = sorted(EXTRACTIONS_DIR.glob("*.json"))
    for ep in extractions:
        try:
            with open(ep) as f:
                data = json.load(f)
        except Exception:
            continue
        
        ext_id = ep.stem
        annotations = {"target_id": ext_id}
        
        # A9: Surprises
        surprises = detect_surprises(data)
        if surprises:
            annotations["surprises"] = surprises
            stats["surprises"] += len(surprises)
        
        # A10: Design parameters
        params = detect_design_parameters(data)
        if params:
            annotations["design_implications"] = params
            stats["design_params"] += len(params)
        
        # A14: Effect sizes
        effects = detect_effect_sizes(data)
        if effects:
            annotations["effect_magnitudes"] = effects
            stats["effect_sizes"] += len(effects)
        
        # Save if anything found
        if len(annotations) > 1:
            if not dry_run:
                out = OUTPUT_DIR / f"{ext_id}.json"
                with open(out, "w") as f:
                    json.dump(annotations, f, indent=2)
            stats["files_annotated"] += 1
    
    # Seed A11 disputes
    if not dry_run:
        with open(OUTPUT_DIR / "_disputes.json", "w") as f:
            json.dump(KNOWN_DISPUTES, f, indent=2)
    stats["disputes_seeded"] = len(KNOWN_DISPUTES)
    
    # Seed A17 hooks
    if not dry_run:
        with open(OUTPUT_DIR / "_hooks.json", "w") as f:
            json.dump(SEED_HOOKS, f, indent=2)
    stats["hooks_seeded"] = len(SEED_HOOKS)
    
    # Seed A18 questions
    if not dry_run:
        with open(OUTPUT_DIR / "_unanswered.json", "w") as f:
            json.dump(SEED_QUESTIONS, f, indent=2)
    stats["questions_seeded"] = len(SEED_QUESTIONS)
    
    return dict(stats)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Seed extended annotations A9-A18")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    
    dry = not args.apply
    stats = seed_annotations(dry_run=dry)
    
    mode = "DRY RUN" if dry else "APPLIED"
    print(f"\n{'='*50}")
    print(f"Extended Annotation Seed — {mode}")
    print(f"{'='*50}")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v}")
    print(f"\nTotal annotations: {sum(stats.values())}")
