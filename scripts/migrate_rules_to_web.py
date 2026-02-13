#!/usr/bin/env python3
"""
Migration Script: ae.db Rules → Web of Belief
Sprint INT — 2026-02-11

Converts the 115 extracted rules from ae.db into Web of Belief beliefs,
enabling the layered network visualization and gap prediction.

Rule format in ae.db:
    rule_id: "abstract_10.1038/..." or "ceiling_001" or "spatial_001"
    rule: "Environment factor -> Outcome (details)"
    confidence: 0.0 to 1.0

Output:
    Beliefs added to web_persistence.db via WebAccumulator
"""

import sys
from pathlib import Path
import sqlite3
import re
import logging
from datetime import datetime, timezone
from typing import List, Tuple, Optional, Dict, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.services.web_of_belief import (
    WebOfBelief, Belief, Credence, EpistemicLevel, BeliefStatus,
    Constraint, ConstraintType
)
from src.services.web_accumulator import WebAccumulator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# Environment and Outcome Taxonomy Mappings
# =============================================================================

# Map keywords in rules to canonical environment IDs
ENVIRONMENT_KEYWORDS = {
    # Light/daylight
    'daylight': 'sensory.light.natural',
    'natural light': 'sensory.light.natural',
    'sunlight': 'sensory.light.natural',
    'artificial light': 'sensory.light.artificial',
    'lighting': 'sensory.light',

    # Plants/biophilia
    'plants': 'natural.vegetation.indoor',
    'virtual plants': 'natural.vegetation.virtual',
    'biophilic': 'natural.biophilic',
    'nature': 'natural.general',
    'greenery': 'natural.vegetation',
    'vegetation': 'natural.vegetation',

    # Noise
    'noise': 'sensory.noise',
    'traffic noise': 'sensory.noise.traffic',
    'road traffic noise': 'sensory.noise.traffic',
    'classroom noise': 'sensory.noise.classroom',
    'background noise': 'sensory.noise.background',

    # Spatial
    'ceiling': 'spatial.ceiling',
    'high ceiling': 'spatial.ceiling.high',
    'low ceiling': 'spatial.ceiling.low',
    'room size': 'spatial.size',
    'open room': 'spatial.openness.open',
    'enclosed room': 'spatial.openness.enclosed',
    'prospect': 'spatial.prospect',
    'refuge': 'spatial.refuge',
    'openness': 'spatial.openness',
    'reverberation': 'sensory.acoustic.reverberation',

    # Temperature/climate
    'temperature': 'sensory.thermal.temperature',
    'thermal': 'sensory.thermal',

    # Views
    'view': 'natural.view',
    'window': 'natural.view.window',

    # Materials
    'wood': 'material.wood',
    'wood coverage': 'material.wood',

    # Space habitat (special case)
    'space habitat': 'spatial.habitat.space',
    'VR': 'config.virtual',
}

# Map keywords to canonical outcome IDs
OUTCOME_KEYWORDS = {
    # Cognitive
    'attention': 'cog.attention',
    'working memory': 'cog.memory.working',
    'memory': 'cog.memory',
    'cognitive': 'cog.general',
    'concentration': 'cog.attention.concentration',
    'focus': 'cog.attention.focus',
    'thinking': 'cog.processing',
    'relational processing': 'cog.processing.relational',
    'abstract thinking': 'cog.processing.abstract',
    'creativity': 'cog.creativity',
    'creative performance': 'cog.creativity',
    'cognitive load': 'cog.load',
    'cognitive development': 'cog.development',

    # Affect/mood
    'mood': 'affect.mood',
    'stress': 'affect.stress',
    'anxiety': 'affect.anxiety',
    'calm': 'affect.calm',
    'relaxation': 'affect.relaxation',
    'tension': 'affect.tension',
    'contentment': 'affect.contentment',
    'satisfaction': 'affect.satisfaction',
    'positive affect': 'affect.positive',
    'negative affect': 'affect.negative',

    # Psychological
    'restoration': 'psych.restoration',
    'restorativeness': 'psych.restoration',
    'preference': 'psych.preference',
    'beauty': 'psych.aesthetics.beauty',
    'aesthetic': 'psych.aesthetics',

    # Performance
    'productivity': 'perf.productivity',
    'performance': 'perf.general',
    'path steering': 'perf.motor.navigation',

    # Physiological
    'heart rate': 'physio.cardiac.hr',

    # Behavioral
    'approach': 'behav.approach',
    'avoidance': 'behav.avoidance',
    'enter': 'behav.approach.enter',
    'exit': 'behav.avoidance.exit',
    'inattentiveness': 'behav.attention.inattention',
}


def parse_rule_text(rule_text: str) -> Tuple[str, str, bool]:
    """
    Parse rule text to extract environment description, outcome description, and null finding flag.

    Format: "Environment factor -> Outcome (details)"

    Returns:
        (environment_desc, outcome_desc, is_null_finding)
    """
    is_null = 'null finding' in rule_text.lower() or 'no effect' in rule_text.lower()

    # Split on arrow
    if ' -> ' in rule_text:
        parts = rule_text.split(' -> ', 1)
        env_desc = parts[0].strip()
        outcome_desc = parts[1].strip()
    elif ' → ' in rule_text:
        parts = rule_text.split(' → ', 1)
        env_desc = parts[0].strip()
        outcome_desc = parts[1].strip()
    else:
        # No arrow, treat whole thing as content
        env_desc = ""
        outcome_desc = rule_text

    return env_desc, outcome_desc, is_null


def extract_environment_id(text: str) -> Optional[str]:
    """Extract canonical environment ID from text."""
    text_lower = text.lower()

    # Check each keyword (longer matches first)
    sorted_keywords = sorted(ENVIRONMENT_KEYWORDS.keys(), key=len, reverse=True)
    for keyword in sorted_keywords:
        if keyword in text_lower:
            return ENVIRONMENT_KEYWORDS[keyword]

    return None


def extract_outcome_id(text: str) -> Optional[str]:
    """Extract canonical outcome ID from text."""
    text_lower = text.lower()

    # Check each keyword (longer matches first)
    sorted_keywords = sorted(OUTCOME_KEYWORDS.keys(), key=len, reverse=True)
    for keyword in sorted_keywords:
        if keyword in text_lower:
            return OUTCOME_KEYWORDS[keyword]

    return None


def determine_epistemic_level(rule_id: str, rule_text: str) -> EpistemicLevel:
    """Determine epistemic level from rule ID and content."""
    rule_lower = rule_text.lower()

    # Check for theoretical markers
    if any(marker in rule_lower for marker in ['theory:', 'theory predicts', 'according to']):
        return EpistemicLevel.THEORETICAL

    # Check for experimental/empirical markers
    if any(marker in rule_lower for marker in ['experiment', 'study', 'fmri', 'n=', 'p<', 'p=']):
        return EpistemicLevel.EMPIRICAL

    # Abstract rules are empirical
    if rule_id.startswith('abstract_'):
        return EpistemicLevel.EMPIRICAL

    # Ceiling and spatial rules with citations are typically empirical
    if rule_id.startswith('ceiling_') or rule_id.startswith('spatial_'):
        if '[' in rule_text:  # Has citation brackets
            return EpistemicLevel.EMPIRICAL

    # Default to intermediate for generalizations
    return EpistemicLevel.INTERMEDIATE


def extract_paper_id(rule_id: str) -> Optional[str]:
    """Extract paper ID (DOI) from rule_id if present."""
    if rule_id.startswith('abstract_'):
        # Format: abstract_10.1038/s41598-025-19113-4_1
        parts = rule_id.split('_', 1)
        if len(parts) > 1:
            # Remove trailing _number
            doi_part = '_'.join(parts[1].rsplit('_', 1)[:-1]) if '_' in parts[1] else parts[1]
            return doi_part
    return None


def extract_tags(rule_id: str, rule_text: str) -> List[str]:
    """Extract tags from rule content."""
    tags = []
    rule_lower = rule_text.lower()

    # Setting tags
    if 'office' in rule_lower:
        tags.append('setting:office')
    if 'school' in rule_lower or 'classroom' in rule_lower:
        tags.append('setting:educational')
    if 'hospital' in rule_lower or 'healthcare' in rule_lower:
        tags.append('setting:healthcare')
    if 'space' in rule_lower and 'habitat' in rule_lower:
        tags.append('setting:space')
    if 'vr' in rule_lower or 'virtual' in rule_lower:
        tags.append('method:VR')
    if 'fmri' in rule_lower:
        tags.append('method:fMRI')
        tags.append('method:neuroimaging')

    # Population tags
    if 'children' in rule_lower or 'child' in rule_lower:
        tags.append('population:children')
    if 'adult' in rule_lower:
        tags.append('population:adults')

    # Theory tags
    if 'biophil' in rule_lower:
        tags.append('theory:biophilia')
    if 'prospect' in rule_lower or 'refuge' in rule_lower:
        tags.append('theory:prospect-refuge')
    if 'restoration' in rule_lower or 'restorative' in rule_lower:
        tags.append('theory:ART')

    # Source tags
    if rule_id.startswith('ceiling_'):
        tags.append('domain:ceiling-height')
    if rule_id.startswith('spatial_'):
        tags.append('domain:spatial')
    if rule_id.startswith('abstract_'):
        tags.append('source:abstract')

    return tags


def convert_rule_to_belief(rule_id: str, rule_text: str, confidence: float) -> Belief:
    """Convert a rule from ae.db to a Belief object."""

    # Parse rule text
    env_desc, outcome_desc, is_null = parse_rule_text(rule_text)

    # Extract canonical IDs
    environment_id = extract_environment_id(rule_text)
    outcome_id = extract_outcome_id(rule_text)

    # Determine epistemic level
    level = determine_epistemic_level(rule_id, rule_text)

    # Extract paper ID if present
    paper_id = extract_paper_id(rule_id)
    paper_ids = [paper_id] if paper_id else []

    # Extract tags
    tags = extract_tags(rule_id, rule_text)

    # Determine status
    if is_null:
        status = BeliefStatus.TENTATIVE  # Null findings are less certain
        tags.append('finding:null')
    else:
        status = BeliefStatus.ESTABLISHED

    # Adjust confidence for null findings
    if is_null and confidence > 0.5:
        confidence = min(confidence, 0.5)

    # Calculate uncertainty (inverse of confidence, with floor)
    uncertainty = max(0.1, 1.0 - confidence)

    # Create belief
    belief = Belief(
        belief_id=f"b_{rule_id}",
        content=rule_text,
        level=level,
        status=status,
        credence=Credence(confidence, uncertainty),
        paper_ids=paper_ids,
        environment_id=environment_id,
        outcome_id=outcome_id,
        tags=tags
    )

    return belief


def load_rules_from_db(db_path: Path) -> List[Tuple[str, str, float]]:
    """Load all rules from ae.db."""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("SELECT rule_id, rule, confidence FROM rules ORDER BY rule_id")
    rules = cursor.fetchall()

    conn.close()
    return rules


def create_theory_beliefs() -> List[Belief]:
    """Create theoretical beliefs for major theories referenced in the rules."""
    theories = [
        Belief(
            belief_id="b_theory_art",
            content="Attention Restoration Theory (ART): Natural environments restore directed attention capacity through soft fascination and being away from demands",
            level=EpistemicLevel.THEORETICAL,
            status=BeliefStatus.ESTABLISHED,
            credence=Credence(0.85, 0.12),
            paper_ids=["kaplan_1989", "kaplan_1995"],
            theory_id="ART",
            tags=["theory:ART", "domain:environmental-psychology"]
        ),
        Belief(
            belief_id="b_theory_srt",
            content="Stress Recovery Theory (SRT): Natural environments trigger parasympathetic activation, reducing stress through evolutionary affiliation with nature",
            level=EpistemicLevel.THEORETICAL,
            status=BeliefStatus.ESTABLISHED,
            credence=Credence(0.82, 0.14),
            paper_ids=["ulrich_1991", "ulrich_1984"],
            theory_id="SRT",
            tags=["theory:SRT", "domain:environmental-psychology"]
        ),
        Belief(
            belief_id="b_theory_biophilia",
            content="Biophilia Hypothesis: Humans have an innate tendency to seek connections with nature and other forms of life, with psychological benefits",
            level=EpistemicLevel.THEORETICAL,
            status=BeliefStatus.ESTABLISHED,
            credence=Credence(0.78, 0.16),
            paper_ids=["wilson_1984", "kellert_1993"],
            theory_id="biophilia",
            tags=["theory:biophilia", "domain:environmental-psychology"]
        ),
        Belief(
            belief_id="b_theory_prospect_refuge",
            content="Prospect-Refuge Theory: Humans prefer environments that offer both prospect (open views for surveillance) and refuge (protected spaces for safety)",
            level=EpistemicLevel.THEORETICAL,
            status=BeliefStatus.ESTABLISHED,
            credence=Credence(0.80, 0.15),
            paper_ids=["appleton_1975"],
            theory_id="prospect-refuge",
            tags=["theory:prospect-refuge", "domain:environmental-psychology"]
        ),
        Belief(
            belief_id="b_theory_ceiling_priming",
            content="Ceiling Height Priming Theory: High ceilings prime freedom-related concepts promoting relational processing; low ceilings prime confinement promoting item-specific processing",
            level=EpistemicLevel.THEORETICAL,
            status=BeliefStatus.ESTABLISHED,
            credence=Credence(0.75, 0.18),
            paper_ids=["meyers_levy_2007"],
            theory_id="ceiling-priming",
            tags=["theory:ceiling-priming", "domain:spatial-cognition"]
        ),
    ]
    return theories


def migrate_rules_to_web(
    ae_db_path: Path,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Migrate rules from ae.db to Web of Belief.

    Args:
        ae_db_path: Path to ae.db
        dry_run: If True, don't actually save to database

    Returns:
        Migration report dict
    """
    logger.info(f"Loading rules from {ae_db_path}")
    rules = load_rules_from_db(ae_db_path)
    logger.info(f"Found {len(rules)} rules")

    # Create web of belief
    web = WebOfBelief()

    # Add theory beliefs first
    theory_beliefs = create_theory_beliefs()
    for belief in theory_beliefs:
        web.add_belief(belief)
    logger.info(f"Added {len(theory_beliefs)} theory beliefs")

    # Convert and add rules
    converted = 0
    skipped = 0
    errors = []

    for rule_id, rule_text, confidence in rules:
        try:
            belief = convert_rule_to_belief(rule_id, rule_text, confidence or 0.5)
            web.add_belief(belief)
            converted += 1
        except Exception as e:
            errors.append(f"{rule_id}: {str(e)}")
            skipped += 1

    logger.info(f"Converted {converted} rules, skipped {skipped}")

    # Add constraints linking empirical beliefs to theories
    constraint_count = 0
    for belief_id, belief in web.beliefs.items():
        if belief.level == EpistemicLevel.EMPIRICAL:
            # Link to relevant theories based on tags
            for tag in belief.tags:
                if tag == 'theory:ART' and 'b_theory_art' in web.beliefs:
                    web.add_constraint(Constraint(
                        constraint_id=f"c_{belief_id}_art",
                        source_id="b_theory_art",
                        target_id=belief_id,
                        constraint_type=ConstraintType.EXPLAINS,
                        strength=0.6
                    ))
                    constraint_count += 1
                elif tag == 'theory:biophilia' and 'b_theory_biophilia' in web.beliefs:
                    web.add_constraint(Constraint(
                        constraint_id=f"c_{belief_id}_biophilia",
                        source_id="b_theory_biophilia",
                        target_id=belief_id,
                        constraint_type=ConstraintType.EXPLAINS,
                        strength=0.6
                    ))
                    constraint_count += 1
                elif tag == 'theory:prospect-refuge' and 'b_theory_prospect_refuge' in web.beliefs:
                    web.add_constraint(Constraint(
                        constraint_id=f"c_{belief_id}_pr",
                        source_id="b_theory_prospect_refuge",
                        target_id=belief_id,
                        constraint_type=ConstraintType.EXPLAINS,
                        strength=0.6
                    ))
                    constraint_count += 1

    logger.info(f"Added {constraint_count} theory-empirical constraints")

    # Save to persistence if not dry run
    if not dry_run:
        accumulator = WebAccumulator()
        # We need to save the web - this requires using the persistence service directly
        from src.services.web_persistence import WebPersistenceService
        persistence = WebPersistenceService(str(accumulator.db_path))

        # Create or get master web
        master_id = persistence.create_or_get_master_web()

        # Save our web as the master
        persistence.save_web(web, master_id)
        logger.info(f"Saved web to {accumulator.db_path}")

    report = {
        'total_rules': len(rules),
        'converted': converted,
        'skipped': skipped,
        'theory_beliefs': len(theory_beliefs),
        'total_beliefs': len(web.beliefs),
        'constraints': constraint_count,
        'errors': errors[:10],  # First 10 errors
        'dry_run': dry_run
    }

    return report, web


def main():
    """Run the migration."""
    import argparse

    parser = argparse.ArgumentParser(description='Migrate rules from ae.db to Web of Belief')
    parser.add_argument('--dry-run', action='store_true', help='Do not save to database')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    ae_db_path = PROJECT_ROOT / 'ae.db'

    if not ae_db_path.exists():
        print(f"Error: {ae_db_path} not found")
        sys.exit(1)

    print("=" * 70)
    print("ARTICLE EATER: Rule Migration to Web of Belief")
    print("=" * 70)

    report, web = migrate_rules_to_web(ae_db_path, dry_run=args.dry_run)

    print(f"\nMigration Report:")
    print(f"  Total rules in ae.db: {report['total_rules']}")
    print(f"  Converted to beliefs: {report['converted']}")
    print(f"  Skipped: {report['skipped']}")
    print(f"  Theory beliefs added: {report['theory_beliefs']}")
    print(f"  Total beliefs in web: {report['total_beliefs']}")
    print(f"  Constraints added: {report['constraints']}")

    if report['errors']:
        print(f"\n  Errors (first 10):")
        for err in report['errors']:
            print(f"    - {err}")

    if args.dry_run:
        print(f"\n  [DRY RUN - no data saved]")
    else:
        print(f"\n  Data saved to web_persistence.db")

    # Show sample beliefs
    print(f"\nSample Beliefs:")
    for i, (bid, belief) in enumerate(list(web.beliefs.items())[:5]):
        print(f"  {i+1}. [{belief.level.value}] {belief.content[:80]}...")
        if belief.environment_id:
            print(f"      env: {belief.environment_id} -> out: {belief.outcome_id}")

    print("\n" + "=" * 70)
    print("MIGRATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
