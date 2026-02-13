#!/usr/bin/env python3
"""
Off-Topic Paper Filter for CNfA Corpus
======================================

Identifies and quarantines papers that passed initial triage but are
NOT relevant to Cognitive Neuroarchitecture (CNfA).

See docs/OFF_TOPIC_FILTER_CRITERIA_2026-02-11.md for criteria.

Usage:
    python scripts/filter_off_topic_papers.py --dry-run
    python scripts/filter_off_topic_papers.py --apply
    python scripts/filter_off_topic_papers.py --review  # Show quarantined papers

Author: Claude Code
Created: 2026-02-11
"""

import argparse
import logging
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Article Finder database path
AF_DB_PATH = Path("/Users/davidusa/REPOS/Article_Finder_v3_2_3/data/article_finder.db")

# =============================================================================
# KEYWORD LISTS - Built from Tagging_Contractor and Outcome_Contractor vocab
# =============================================================================

# -----------------------------------------------------------------------------
# STRONG EXCLUSION - Only these trigger high-confidence exclusion
# These are domains clearly unrelated to CNfA
# -----------------------------------------------------------------------------

# Industrial/extraction processes (NOT about buildings)
INDUSTRIAL_KEYWORDS = [
    # Petroleum/oil
    "offshore", "offshore drilling", "oil well", "petroleum extraction", "oil rig",
    "pipeline inspection", "refinery process", "fracking", "subsea equipment",
    "well integrity", "wellhead", "drilling operation", "petroleum",
    # Mining
    "mining operation", "ore extraction", "coal mining",
]

# Pure cell/molecular biology (NOT environmental health)
CELL_BIOLOGY_KEYWORDS = [
    "cell culture", "in vitro assay", "DNA sequence", "RNA expression",
    "protein expression", "gene expression", "cellular mechanism",
    "molecular biology", "biochemical pathway", "cell signaling",
    "transfection", "western blot", "PCR amplification",
]

# Clinical drug trials (NOT healing environments)
DRUG_TRIAL_KEYWORDS = [
    "drug dosage", "pharmacokinetics", "phase II trial", "phase III trial",
    "placebo-controlled drug", "chemotherapy regimen", "drug efficacy",
]

# Clearly off-topic venues
OFFTOPIC_VENUE_KEYWORDS = [
    "petroleum engineer", "oil gas journal", "mining engineering",
    "fisheries science", "marine biology journal", "polymer science",
    "electrochemistry", "organic chemistry", "inorganic chemistry",
]

# -----------------------------------------------------------------------------
# INCLUSION KEYWORDS - From CNfA Taxonomies + environment_lookup.json
# Comprehensive vocabulary from /Users/davidusa/Documents/__160 Cog_Neuro_for_Architecture/
# -----------------------------------------------------------------------------

# Materials (from environment_lookup.json + taxonomy)
MATERIALS_KEYWORDS = [
    # Natural materials
    "wood", "timber", "wooden", "stone", "marble", "granite", "slate",
    "brick", "terracotta", "bamboo", "cork", "leather", "wool", "cotton",
    "natural material", "organic material", "rattan", "jute", "linen",
    # Manufactured materials
    "glass", "glazing", "steel", "metal", "aluminum", "concrete",
    "plastic", "laminate", "vinyl", "ceramic", "tile", "porcelain",
    "composite", "engineered", "synthetic",
    # Material properties
    "texture", "finish", "surface", "matte", "glossy", "reflective",
    "transparent", "translucent", "opaque", "tactile", "haptic",
    "rough", "smooth", "grainy", "polished", "weathered", "patina",
]

# Built environment (from environment_lookup.json + taxonomy)
BUILT_ENVIRONMENT_KEYWORDS = [
    # Space types
    "building", "architecture", "architectural", "interior", "office", "workplace",
    "hospital", "clinic", "healthcare", "school", "classroom", "university", "campus",
    "residential", "home", "apartment", "house", "dwelling", "housing",
    "commercial", "retail", "store", "restaurant", "cafe", "hotel", "lobby",
    "museum", "gallery", "library", "theater", "auditorium", "arena",
    "factory", "warehouse", "laboratory", "gym", "spa", "recreation",
    "prison", "nursing home", "elderly care", "daycare", "kindergarten",
    # Spatial elements
    "room", "space", "indoor", "outdoor", "courtyard", "atrium",
    "lobby", "corridor", "hallway", "staircase", "entrance", "foyer", "vestibule",
    "facade", "window", "door", "wall", "ceiling", "floor", "roof",
    "balcony", "terrace", "patio", "garden", "plaza", "street",
    # Layout/configuration
    "design", "layout", "floor plan", "open plan", "partition", "cubicle",
    "circulation", "wayfinding", "legibility", "navigation", "signage",
    "zoning", "hierarchy", "configuration", "arrangement", "organization",
    # Architectural patterns
    "bay window", "colonnade", "double height", "skylight", "mezzanine",
    "prospect", "refuge", "nook", "alcove", "threshold", "transition",
    "curvilinear", "rectilinear", "angular", "curved", "organic form",
    # Structural
    "column", "beam", "truss", "curtain wall", "envelope", "cladding",
]

# Environmental attributes (from environment_lookup.json + taxonomy)
ENVIRONMENTAL_ATTRIBUTE_KEYWORDS = [
    # Light (comprehensive from taxonomy)
    "light", "daylight", "sunlight", "illumination", "illuminance",
    "lighting", "lux", "luminance", "brightness", "glare", "dimness",
    "circadian", "spectrum", "color temperature", "CCT", "kelvin",
    "natural light", "artificial light", "daylighting", "window light",
    "LED", "fluorescent", "incandescent", "halogen",
    "direct light", "indirect light", "diffused", "ambient light",
    # Sound/acoustic
    "noise", "sound", "acoustic", "soundscape", "reverberation",
    "speech intelligibility", "background noise", "quiet", "silence",
    "auditory", "decibel", "sound masking", "acoustic panel",
    "echo", "absorption", "diffusion", "insulation",
    # Thermal
    "thermal", "temperature", "HVAC", "ventilation", "air quality",
    "humidity", "airflow", "CO2", "indoor air", "fresh air",
    "heating", "cooling", "comfort zone", "radiant", "convective",
    # Nature/biophilic
    "nature", "plant", "green", "biophilic", "biophilia",
    "garden", "vegetation", "greenery", "tree", "flower", "foliage",
    "water feature", "natural element", "nature view", "outdoor view",
    "natural pattern", "fractal", "organic form", "biomimicry",
    # Spatial qualities
    "spatial", "volume", "proportion", "scale", "density",
    "enclosure", "openness", "spaciousness", "ceiling height",
    "complexity", "coherence", "mystery", "order", "visual complexity",
    "crowding", "privacy", "territoriality", "personal space",
    "prospect-refuge", "isovist", "visual field",
    # Visual/aesthetic
    "color", "hue", "saturation", "contrast", "visual",
    "view", "vista", "sightline", "visual access", "transparency",
    "aesthetics", "beauty", "preference", "appeal",
    "symmetry", "asymmetry", "pattern", "rhythm", "repetition",
    "ornamentation", "minimalist", "clutter", "visual weight",
]

# -----------------------------------------------------------------------------
# HUMAN OUTCOME KEYWORDS - From outcome_lookup.json + CNfA Taxonomies
# Comprehensive human response vocabulary
# -----------------------------------------------------------------------------

HUMAN_OUTCOME_KEYWORDS = [
    # Cognitive (Tier 3 from taxonomy)
    "cognition", "cognitive", "attention", "memory", "concentration",
    "working memory", "sustained attention", "selective attention", "divided attention",
    "vigilance", "mental performance", "cognitive function", "cognitive load",
    "thinking", "reasoning", "problem solving", "decision making",
    "creativity", "innovation", "learning", "comprehension", "understanding",
    "focus", "distraction", "mental fatigue", "cognitive fatigue",
    "executive function", "inhibitory control", "cognitive flexibility",
    "spatial cognition", "navigation", "orientation", "wayfinding ability",
    "processing fluency", "cognitive clarity", "mental clarity",
    # Affective (Tier 2 from taxonomy)
    "mood", "emotion", "affect", "feeling", "anxiety", "stress",
    "positive mood", "negative mood", "pleasant", "unpleasant",
    "arousal", "valence", "emotional response", "emotional regulation",
    "happiness", "joy", "delight", "contentment", "serenity", "calm",
    "awe", "wonder", "inspiration", "motivation", "engagement",
    "comfort", "psychological comfort", "coziness", "warmth",
    "relaxation", "tension", "irritation", "frustration", "annoyance",
    "fear", "anxiety", "disorientation", "confusion", "alienation",
    "nostalgia", "mystery", "intrigue", "sublimity", "transcendence",
    # Behavioral (Tier 4 from taxonomy)
    "behavior", "behaviour", "productivity", "performance",
    "task performance", "work output", "efficiency", "error rate",
    "sleep", "rest", "activity", "movement", "posture", "gait",
    "social interaction", "collaboration", "communication", "conversation",
    "approach", "avoidance", "exploration", "dwelling time",
    "flow state", "immersion", "absorption",
    # Health/wellbeing (Tier 7 from taxonomy)
    "health", "wellbeing", "well-being", "wellness", "quality of life",
    "satisfaction", "comfort", "discomfort", "thermal comfort",
    "fatigue", "alertness", "drowsiness", "energy", "vitality",
    "headache", "eye strain", "sick building syndrome", "SBS",
    "recovery", "restoration", "recuperation", "rejuvenation",
    # Physiological/Neurophysiological (from taxonomy section 6)
    "heart rate", "heart rate variability", "HRV", "blood pressure",
    "cortisol", "melatonin", "oxytocin", "dopamine", "serotonin",
    "skin conductance", "galvanic skin response", "GSR", "electrodermal",
    "EEG", "fMRI", "fNIRS", "MEG", "physiological", "neurophysiological",
    "circadian rhythm", "circadian", "sleep quality", "arousal level",
    "autonomic", "sympathetic", "parasympathetic", "vagal tone",
    "pupil", "pupillometry", "pupil dilation",
    "respiration", "breathing", "respiratory",
    # Neural systems (from taxonomy section 6)
    "visual cortex", "auditory cortex", "somatosensory",
    "prefrontal cortex", "orbitofrontal", "dorsolateral",
    "anterior cingulate", "insula", "amygdala", "hippocampus",
    "reticular activating", "default mode network", "DMN",
    "reward system", "nucleus accumbens", "ventral tegmental",
    "HPA axis", "hypothalamic",
    # Sensory processing
    "photoreceptor", "ganglion cell", "ipRGC", "melanopsin",
    "cochlear", "vestibular", "proprioception", "proprioceptive",
    "mechanoreceptor", "thermoreceptor",
    # Social (Tier 5 from taxonomy)
    "social facilitation", "social inhibition", "belonging", "community",
    "privacy", "personal space", "territoriality", "crowding",
    "collaboration", "cooperation", "communication", "interaction",
    # Perceptual
    "perception", "perceived", "subjective", "rating",
    "preference", "evaluation", "assessment", "judgment",
    "visual perception", "auditory perception", "tactile perception",
    # People terms
    "participant", "subject", "occupant", "user", "worker",
    "employee", "student", "patient", "resident", "visitor",
    "people", "person", "human", "individual", "inhabitant",
]

# Study/research indicators
STUDY_INDICATOR_KEYWORDS = [
    "experiment", "study", "trial", "survey", "questionnaire",
    "field study", "laboratory", "lab study", "controlled study",
    "measured", "assessed", "evaluated", "compared", "tested",
    "n=", "sample size", "participants", "subjects", "respondents",
    "statistical", "significant", "p<", "p =", "effect size", "Cohen",
    "correlation", "regression", "ANOVA", "t-test", "chi-square",
    "qualitative", "quantitative", "mixed method", "empirical",
    "interview", "observation", "case study", "longitudinal",
    "cross-sectional", "randomized", "RCT", "quasi-experimental",
    "pre-post", "within-subjects", "between-subjects",
]

# Theoretical/conceptual - VERY GENEROUS (from CNfA Taxonomy)
THEORETICAL_KEYWORDS = [
    # Major theories in CNfA
    "biophilia", "biophilic hypothesis", "Wilson", "Kellert",
    "attention restoration", "attention restoration theory", "ART", "Kaplan",
    "stress recovery", "stress recovery theory", "SRT", "Ulrich",
    "prospect-refuge", "prospect refuge theory", "Appleton", "Hildebrand",
    "evolutionary", "adaptive", "innate", "natural selection",
    "psychological restoration", "restorative environment", "restorative",
    "environmental preference", "affordance", "Gibson", "ecological psychology",
    # Predictive/neuroscience theories
    "predictive coding", "predictive processing", "prediction error",
    "hedonic", "hedonic tagging", "valence tagging", "reward prediction",
    "embodied cognition", "embodied", "enactive", "4E cognition", "extended mind",
    "neural", "neuroscience", "neuroarchitecture", "neuroaesthetics",
    "brain", "cortex", "amygdala", "hippocampus", "prefrontal",
    "limbic", "basal ganglia", "cerebellum", "thalamus",
    # Information/complexity theories
    "fractal", "fractal dimension", "self-similarity", "1/f noise", "power law",
    "complexity theory", "edge of chaos", "optimal complexity", "optimal arousal",
    "information theory", "entropy", "redundancy", "information richness",
    "Gestalt", "figure-ground", "perceptual organization", "grouping",
    "fluency", "processing fluency", "disfluency",
    # Spatial cognition theories
    "cognitive map", "mental map", "spatial schema", "route knowledge", "survey knowledge",
    "place cell", "grid cell", "head direction cell", "border cell",
    "spatial memory", "allocentric", "egocentric",
    # Conceptual terms
    "theory", "theoretical", "hypothesis", "framework", "model",
    "conceptual", "concept", "construct", "mechanism", "principle",
    "review", "meta-analysis", "systematic review", "literature review",
    "synthesis", "integration", "overview", "taxonomy", "typology",
    # Philosophy/foundations
    "epistemology", "ontology", "phenomenology", "phenomenological",
    "situated", "ecological", "transactional", "interactionist",
    "place attachment", "sense of place", "genius loci", "topophilia",
    "atmosphere", "ambiance", "Gernot Böhme", "stimmung",
    # Methodological/research terms (from taxonomy section 8)
    "space syntax", "isovist", "visibility graph", "agent-based",
    "virtual reality", "VR", "immersive", "simulation",
    "EEG", "fMRI", "fNIRS", "MEG", "neuroimaging",
    "eye tracking", "gaze", "fixation", "saccade",
    "post-occupancy", "POE", "building performance",
]

# Venues that strongly suggest on-topic
ONTOPIC_VENUE_KEYWORDS = [
    "architecture", "architect", "building", "construction",
    "environment", "environmental", "psychology", "psychological",
    "ergonomic", "human factors", "design", "interior",
    "lighting", "illumination", "acoustic", "thermal", "HVAC",
    "cognitive", "perception", "health", "workplace", "office",
    "urban", "landscape", "planning", "housing", "facilities",
    "neuroscience", "brain", "behavior", "behavioural",
]


import re

def word_boundary_match(keyword: str, text: str) -> bool:
    """Check if keyword appears as a whole word (not substring) in text."""
    # Escape special regex chars in keyword, then add word boundaries
    pattern = r'\b' + re.escape(keyword) + r'\b'
    return bool(re.search(pattern, text, re.IGNORECASE))


def count_keyword_matches(keywords: List[str], text: str) -> List[str]:
    """Return list of keywords that match as whole words."""
    return [kw for kw in keywords if word_boundary_match(kw, text)]


def is_likely_off_topic(paper: Dict[str, Any]) -> Tuple[bool, str, float]:
    """
    Determine if a paper is likely off-topic.

    PHILOSOPHY: Be PERMISSIVE. Only exclude papers that are CLEARLY unrelated
    to CNfA (cognitive neuroarchitecture). When in doubt, keep the paper.

    Returns:
        (is_off_topic, reason, confidence)
        confidence: 0.0-1.0, higher = more confident it's off-topic
    """
    title = (paper.get("title") or "").lower()
    abstract = (paper.get("abstract") or "").lower()
    venue = (paper.get("venue") or "").lower()
    combined = f"{title} {abstract}"

    # ==========================================================================
    # FIRST: Check for STRONG exclusions that override inclusion signals
    # These are domains so clearly unrelated that even incidental keyword
    # matches shouldn't save them
    # ==========================================================================

    # Industrial extraction - "offshore" in title is a very strong signal
    industrial_hits = count_keyword_matches(INDUSTRIAL_KEYWORDS, combined)
    industrial_in_title = count_keyword_matches(INDUSTRIAL_KEYWORDS, title)

    # If industrial keyword in TITLE, it's almost certainly off-topic
    if industrial_in_title:
        return True, f"industrial_in_title:{industrial_in_title[0]}", 0.95

    # ==========================================================================
    # SECOND: Check for ON-TOPIC indicators (generous inclusion)
    # ==========================================================================

    # Check all inclusion categories (using word boundary matching)
    has_materials = any(word_boundary_match(kw, combined) for kw in MATERIALS_KEYWORDS)
    has_built_env = any(word_boundary_match(kw, combined) for kw in BUILT_ENVIRONMENT_KEYWORDS)
    has_env_attr = any(word_boundary_match(kw, combined) for kw in ENVIRONMENTAL_ATTRIBUTE_KEYWORDS)
    has_human_outcome = any(word_boundary_match(kw, combined) for kw in HUMAN_OUTCOME_KEYWORDS)
    has_theoretical = any(word_boundary_match(kw, combined) for kw in THEORETICAL_KEYWORDS)
    has_study = any(word_boundary_match(kw, combined) for kw in STUDY_INDICATOR_KEYWORDS)
    has_ontopic_venue = any(word_boundary_match(kw, venue) for kw in ONTOPIC_VENUE_KEYWORDS)

    # Count how many inclusion categories match
    inclusion_score = sum([
        has_materials,
        has_built_env,
        has_env_attr,
        has_human_outcome,
        has_theoretical,
        has_study,
        has_ontopic_venue,
    ])

    # If 2+ inclusion categories match, it's definitely on-topic
    if inclusion_score >= 2:
        return False, f"on_topic:inclusion_score={inclusion_score}", 0.0

    # Theoretical papers are ALWAYS on-topic (very generous)
    if has_theoretical:
        return False, "on_topic:theoretical", 0.0

    # Papers in clearly on-topic venues are on-topic
    if has_ontopic_venue:
        return False, "on_topic:venue", 0.0

    # ==========================================================================
    # THIRD: Check for weaker exclusions (only if low inclusion score)
    # ==========================================================================

    # Industrial extraction in abstract (weaker signal)
    if industrial_hits and inclusion_score == 0:
        return True, f"industrial:{industrial_hits[0]}", 0.90

    # Cell/molecular biology (NOT environmental health)
    biology_hits = count_keyword_matches(CELL_BIOLOGY_KEYWORDS, combined)
    if biology_hits and inclusion_score == 0:
        return True, f"cell_biology:{biology_hits[0]}", 0.95

    # Drug trials (NOT healing environments)
    drug_hits = count_keyword_matches(DRUG_TRIAL_KEYWORDS, combined)
    if drug_hits and inclusion_score == 0:
        return True, f"drug_trial:{drug_hits[0]}", 0.90

    # Off-topic venue AND no inclusion indicators
    if any(word_boundary_match(kw, venue) for kw in OFFTOPIC_VENUE_KEYWORDS) and inclusion_score == 0:
        return True, f"offtopic_venue:{venue[:30]}", 0.85

    # ==========================================================================
    # DEFAULT: Keep the paper (permissive)
    # ==========================================================================

    # Even with 0-1 inclusion matches, we keep it - might be relevant
    return False, f"on_topic:default(inclusion={inclusion_score})", 0.0


def get_papers_to_filter(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """Get papers that are marked for extraction but not yet filtered."""
    cursor = conn.execute("""
        SELECT paper_id, title, abstract, venue, year, triage_score,
               off_topic_flag, topic_decision
        FROM papers
        WHERE triage_decision = 'send_to_eater'
          AND abstract IS NOT NULL
          AND LENGTH(abstract) > 200
        ORDER BY triage_score DESC
    """)
    return [dict(row) for row in cursor.fetchall()]


def apply_filter(
    conn: sqlite3.Connection,
    paper_id: str,
    is_off_topic: bool,
    reason: str,
    confidence: float,
) -> None:
    """Update paper's topic status in database."""
    conn.execute("""
        UPDATE papers
        SET off_topic_flag = ?,
            off_topic_score = ?,
            topic_decision = ?,
            topic_category = ?,
            updated_at = ?
        WHERE paper_id = ?
    """, (
        1 if is_off_topic else 0,
        confidence if is_off_topic else None,
        "quarantine" if is_off_topic else "on_topic",
        reason,
        datetime.now().isoformat(),
        paper_id,
    ))


def main():
    parser = argparse.ArgumentParser(
        description="Filter off-topic papers from CNfA corpus"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be filtered without applying",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply filters to database",
    )
    parser.add_argument(
        "--review",
        action="store_true",
        help="Show currently quarantined papers",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show filtering statistics",
    )

    args = parser.parse_args()

    if not AF_DB_PATH.exists():
        logger.error(f"Database not found: {AF_DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(AF_DB_PATH)
    conn.row_factory = sqlite3.Row

    if args.review:
        cursor = conn.execute("""
            SELECT paper_id, title, topic_category, off_topic_score
            FROM papers
            WHERE off_topic_flag = 1
            ORDER BY off_topic_score DESC
        """)
        quarantined = cursor.fetchall()
        logger.info(f"Currently quarantined: {len(quarantined)} papers")
        for p in quarantined:
            logger.info(f"  [{p['off_topic_score']:.2f}] {p['topic_category']}: {p['title'][:50]}...")
        conn.close()
        return

    if args.stats:
        cursor = conn.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN triage_decision = 'send_to_eater' THEN 1 ELSE 0 END) as send_to_eater,
                SUM(CASE WHEN off_topic_flag = 1 THEN 1 ELSE 0 END) as quarantined,
                SUM(CASE WHEN topic_decision = 'on_topic' THEN 1 ELSE 0 END) as confirmed_on_topic
            FROM papers
            WHERE abstract IS NOT NULL
        """)
        stats = dict(cursor.fetchone())
        logger.info("Filtering Statistics:")
        logger.info(f"  Total with abstracts: {stats['total']}")
        logger.info(f"  Triaged 'send_to_eater': {stats['send_to_eater']}")
        logger.info(f"  Quarantined (off-topic): {stats['quarantined']}")
        logger.info(f"  Confirmed on-topic: {stats['confirmed_on_topic']}")
        conn.close()
        return

    # Get papers to filter
    papers = get_papers_to_filter(conn)
    logger.info(f"Analyzing {len(papers)} papers...")

    off_topic_papers = []
    on_topic_papers = []

    for paper in papers:
        is_off_topic, reason, confidence = is_likely_off_topic(paper)

        if is_off_topic:
            off_topic_papers.append({
                "paper_id": paper["paper_id"],
                "title": paper["title"],
                "reason": reason,
                "confidence": confidence,
            })
        else:
            on_topic_papers.append({
                "paper_id": paper["paper_id"],
                "title": paper["title"],
            })

    # Report results
    logger.info("=" * 70)
    logger.info(f"FILTERING RESULTS")
    logger.info(f"  Total analyzed: {len(papers)}")
    logger.info(f"  Off-topic (to quarantine): {len(off_topic_papers)}")
    logger.info(f"  On-topic (to process): {len(on_topic_papers)}")
    logger.info("=" * 70)

    if off_topic_papers:
        logger.info("\nOFF-TOPIC PAPERS:")
        # Group by reason
        reasons = {}
        for p in off_topic_papers:
            reason_type = p["reason"].split(":")[0]
            reasons.setdefault(reason_type, []).append(p)

        for reason_type, papers_list in sorted(reasons.items()):
            logger.info(f"\n  {reason_type} ({len(papers_list)} papers):")
            for p in papers_list[:5]:  # Show first 5
                logger.info(f"    [{p['confidence']:.2f}] {p['title'][:55]}...")
            if len(papers_list) > 5:
                logger.info(f"    ... and {len(papers_list) - 5} more")

    if args.dry_run:
        logger.info("\n[DRY RUN] No changes applied. Use --apply to update database.")

    elif args.apply:
        logger.info("\nApplying filters to database...")

        for p in off_topic_papers:
            apply_filter(conn, p["paper_id"], True, p["reason"], p["confidence"])

        for p in on_topic_papers:
            apply_filter(conn, p["paper_id"], False, "on_topic", 0.0)

        conn.commit()
        logger.info(f"Updated {len(off_topic_papers)} papers as off-topic")
        logger.info(f"Confirmed {len(on_topic_papers)} papers as on-topic")

    else:
        logger.info("\nUse --dry-run to preview or --apply to update database")

    conn.close()


if __name__ == "__main__":
    main()
