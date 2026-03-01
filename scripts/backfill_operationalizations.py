#!/usr/bin/env python3
"""
Backfill operationalizations in outcome_vocab.json

This script reads the outcome vocabulary, identifies terms with empty operationalizations
arrays (level >= 2), and fills them with evidence-based measurement instruments from the
environmental psychology, cognitive science, neuroscience, and architecture research literature.

It does NOT overwrite existing operationalizations, only fills empty ones.
"""

import json
from pathlib import Path
from datetime import datetime

# Mapping of term_id -> list of operationalization strings
OPERATIONALIZATIONS = {
    # AFFECT domain
    "affect.anxiety": [
        "State-Trait Anxiety Inventory (STAI)",
        "Visual Analogue Scale (VAS-Anxiety)",
        "Skin conductance level"
    ],
    "affect.awe": [
        "Awe Experience Scale (Yaden et al. 2019)",
        "Self-report awe intensity",
        "Goosebumps/chills frequency"
    ],
    "affect.frustration": [
        "Frustration Discomfort Scale",
        "NASA-TLX frustration subscale",
        "Self-report VAS"
    ],
    "affect.joy": [
        "Positive and Negative Affect Schedule (PANAS-Positive)",
        "Facial Action Coding System (FACS)",
        "Experience Sampling Method (ESM)"
    ],
    "affect.mood": [
        "Profile of Mood States (POMS)",
        "Affect Grid (Russell et al. 1989)",
        "Day Reconstruction Method (DRM)"
    ],
    "affect.mood.negative": [
        "PANAS Negative Affect subscale",
        "Depression Anxiety Stress Scale (DASS-21)",
        "Ecological Momentary Assessment"
    ],
    "affect.mood.positive": [
        "PANAS Positive Affect subscale",
        "Subjective Happiness Scale (Lyubomirsky)",
        "Ecological Momentary Assessment"
    ],
    "affect.relaxation": [
        "Relaxation Inventory (Crist et al. 1989)",
        "VAS-Relaxation",
        "EMG muscle tension"
    ],
    "affect.resilience": [
        "Connor-Davidson Resilience Scale (CD-RISC)",
        "Brief Resilience Scale (BRS)",
        "Ego Resiliency Scale"
    ],
    "affect.satisfaction": [
        "Environmental Satisfaction Scale",
        "Likert satisfaction rating",
        "Building Occupant Survey (BUS)"
    ],
    "affect.serenity": [
        "Serenity Scale (Roberts & Aspy 1993)",
        "VAS-Calm",
        "PANAS serenity subscale"
    ],
    "affect.stress": [
        "Perceived Stress Scale (PSS-10)",
        "Salivary cortisol",
        "VAS-Stress"
    ],

    # BEHAV domain
    "behav.activity": [
        "Accelerometer (ActiGraph)",
        "International Physical Activity Questionnaire (IPAQ)",
        "Pedometer step count"
    ],
    "behav.comfort_seeking": [
        "Behavioral observation coding",
        "Window/thermostat adjustment frequency",
        "Clothing adjustment log"
    ],
    "behav.engagement": [
        "Behavioral Engagement Scale",
        "Time-on-task",
        "Interaction frequency coding"
    ],
    "behav.learning": [
        "Pre-post knowledge test",
        "Grades/test scores",
        "Time to criterion"
    ],
    "behav.productivity": [
        "Task completion rate",
        "Output quantity/quality metrics",
        "Self-reported productivity scale"
    ],
    "behav.risk_taking": [
        "Balloon Analogue Risk Task (BART)",
        "Domain-Specific Risk-Taking Scale (DOSPERT)",
        "Iowa Gambling Task"
    ],
    "behav.sleep": [
        "Pittsburgh Sleep Quality Index (PSQI)",
        "Actigraphy",
        "Sleep diary"
    ],
    "behav.social_behavior": [
        "Social interaction coding (Bales IPA)",
        "Conversation frequency/duration",
        "Proximity sensor data"
    ],

    # COG domain
    "cog.attention": [
        "Attention Network Test (ANT)",
        "Continuous Performance Test (CPT)",
        "d-prime signal detection"
    ],
    "cog.attention.broad": [
        "Global/local Navon task (global bias)",
        "Useful Field of View (UFOV)",
        "Attentional breadth paradigm"
    ],
    "cog.attention.divided": [
        "Dual-task paradigm",
        "Multiple Object Tracking (MOT)",
        "Divided attention RT cost"
    ],
    "cog.attention.selective": [
        "Stroop task",
        "Flanker task",
        "Visual search RT"
    ],
    "cog.attention.sustained": [
        "Sustained Attention to Response Task (SART)",
        "Psychomotor Vigilance Task (PVT)",
        "Continuous Performance Test (CPT)"
    ],
    "cog.creativity": [
        "Alternate Uses Task (AUT)",
        "Remote Associates Test (RAT)",
        "Torrance Tests of Creative Thinking (TTCT)"
    ],
    "cog.executive": [
        "Trail Making Test (TMT-B)",
        "Wisconsin Card Sorting Test (WCST)",
        "Digit Span Backward"
    ],
    "cog.executive.inhibition": [
        "Go/No-Go task",
        "Stop-Signal Reaction Time (SSRT)",
        "Stroop interference score"
    ],
    "cog.executive.planning": [
        "Tower of London/Hanoi",
        "Maze completion time",
        "Route Planning Task"
    ],
    "cog.language": [
        "Verbal fluency (FAS)",
        "Boston Naming Test",
        "Reading comprehension score"
    ],
    "cog.memory": [
        "Rey Auditory Verbal Learning Test (RAVLT)",
        "Recognition memory d-prime",
        "Free recall score"
    ],
    "cog.memory.episodic": [
        "Autobiographical Memory Test",
        "Source memory task",
        "Recollection/familiarity paradigm"
    ],
    "cog.memory.working": [
        "N-back task",
        "Operation Span (OSPAN)",
        "Digit span forward/backward"
    ],
    "cog.perception": [
        "Psychophysical threshold",
        "Signal Detection Theory (SDT) sensitivity",
        "Perceptual discrimination task"
    ],
    "cog.performance": [
        "Composite Cognitive Assessment Battery",
        "Montreal Cognitive Assessment (MoCA)",
        "Cognitive Failures Questionnaire (CFQ)"
    ],
    "cog.processing_speed": [
        "Symbol Digit Modalities Test (SDMT)",
        "Simple/Choice Reaction Time",
        "Coding task (WAIS)"
    ],
    "cog.reasoning": [
        "Raven's Progressive Matrices",
        "Wason Selection Task",
        "Syllogistic reasoning accuracy"
    ],

    # ENV domain
    "env.air_quality": [
        "CO2 concentration (ppm)",
        "PM2.5 sensor",
        "Perceived air quality rating"
    ],
    "env.color": [
        "Munsell color system rating",
        "Color preference ranking",
        "Semantic differential (warm-cool, pleasant-unpleasant)"
    ],
    "env.complexity": [
        "Fractal dimension (D)",
        "Edge density",
        "Subjective complexity rating"
    ],
    "env.lighting": [
        "Illuminance (lux meter)",
        "Correlated Color Temperature (CCT)",
        "Lighting satisfaction questionnaire"
    ],
    "env.materiality": [
        "Material preference rating",
        "Haptic evaluation scale",
        "Perceived naturalness rating"
    ],
    "env.natural_features": [
        "Biophilic design checklist",
        "Nature dose (% green visible)",
        "View content analysis"
    ],
    "env.noise": [
        "Sound Pressure Level (dB(A))",
        "Noise Annoyance Scale (ISO 15666)",
        "Speech Transmission Index (STI)"
    ],
    "env.privacy": [
        "Privacy satisfaction scale",
        "Visual exposure index",
        "Acoustic privacy rating (STC)"
    ],
    "env.prospect_refuge": [
        "Prospect-Refuge Rating Scale (Dosen & Ostwald)",
        "Isovist analysis (area, perimeter)",
        "Viewshed extent"
    ],
    "env.spaciousness": [
        "Room volume estimation",
        "Perceived spaciousness scale",
        "Ceiling height ratio"
    ],

    # HEALTH domain
    "health.immunity": [
        "Salivary IgA",
        "NK cell activity assay",
        "Self-reported illness frequency"
    ],
    "health.recovery": [
        "Length of hospital stay",
        "Analgesic medication usage",
        "Recovery satisfaction scale"
    ],
    "health.resilience": [
        "Connor-Davidson Resilience Scale (CD-RISC)",
        "Brief Resilience Scale (BRS)",
        "Allostatic load index"
    ],
    "health.wellbeing": [
        "WHO-5 Well-Being Index",
        "Warwick-Edinburgh Mental Well-being Scale (WEMWBS)",
        "SF-36 Health Survey"
    ],

    # NEURAL domain
    "neural.activation": [
        "fMRI BOLD signal",
        "PET regional cerebral blood flow",
        "fNIRS oxygenation"
    ],
    "neural.connectivity": [
        "fMRI functional connectivity (FC)",
        "DTI structural connectivity",
        "Graph-theoretic network metrics"
    ],
    "neural.eeg": [
        "EEG power spectral density (alpha/beta/theta)",
        "Event-Related Potentials (ERP)",
        "EEG frontal asymmetry index"
    ],
    "neural.synchrony": [
        "Phase-Locking Value (PLV)",
        "EEG coherence",
        "Cross-frequency coupling"
    ],

    # PHYSIO domain
    "physio.alertness": [
        "Karolinska Sleepiness Scale (KSS)",
        "Pupillometry",
        "EEG alpha suppression"
    ],
    "physio.blood_pressure": [
        "Sphygmomanometer (systolic/diastolic mmHg)",
        "Ambulatory BP monitoring (24h)",
        "Mean arterial pressure"
    ],
    "physio.eye_movement": [
        "Eye tracker (fixation count/duration)",
        "Saccade amplitude",
        "Pupil diameter change"
    ],
    "physio.fatigue": [
        "Chalder Fatigue Scale",
        "Visual Analogue Scale (VAS-Fatigue)",
        "Critical Flicker Fusion (CFF)"
    ],
    "physio.heart_rate": [
        "ECG R-R intervals",
        "Photoplethysmography (PPG)",
        "Resting heart rate (bpm)"
    ],
    "physio.heart_rate.hrv": [
        "RMSSD (time-domain HRV)",
        "HF power (0.15-0.40 Hz)",
        "LF/HF ratio"
    ],
    "physio.pain": [
        "Visual Analogue Scale (VAS-Pain)",
        "McGill Pain Questionnaire",
        "Numerical Rating Scale (NRS)"
    ],
    "physio.respiration": [
        "Respiratory belt (breaths/min)",
        "End-tidal CO2",
        "Respiratory sinus arrhythmia (RSA)"
    ],
    "physio.skin_conductance": [
        "Electrodermal Activity (EDA) tonic level",
        "Skin Conductance Response (SCR) amplitude",
        "Number of spontaneous SCRs"
    ],
    "physio.stress_hormones": [
        "Salivary cortisol (µg/dL)",
        "Salivary alpha-amylase",
        "Urinary catecholamines"
    ],
    "physio.stress_hormones.cortisol": [
        "Salivary cortisol diurnal curve",
        "Cortisol Awakening Response (CAR)",
        "Hair cortisol (chronic stress)"
    ],
    "physio.thermal_comfort": [
        "PMV/PPD (Fanger model)",
        "Thermal sensation vote (ASHRAE 7-point)",
        "Skin temperature (infrared)"
    ],

    # SOCIAL domain
    "social.affiliation": [
        "Inclusion of Other in Self Scale (IOS)",
        "Social Identity Scale",
        "Group identification measure"
    ],
    "social.cohesion": [
        "Group Environment Questionnaire (GEQ)",
        "Sociometric choice measure",
        "Social cohesion index"
    ],
    "social.collaboration": [
        "Team performance score",
        "Coordination frequency coding",
        "Collaborative problem-solving task"
    ],
    "social.interaction": [
        "Social interaction diary",
        "Behavioral observation (interaction frequency/duration)",
        "Social Network Analysis (degree centrality)"
    ],
    "social.trust": [
        "Generalized Trust Scale",
        "Trust Game (behavioral economics)",
        "Interpersonal Trust Scale (Rotter)"
    ],
}


def backfill_operationalizations(vocab_path: Path) -> dict:
    """
    Read vocabulary, backfill empty operationalizations, update stats, and return result.

    Args:
        vocab_path: Path to outcome_vocab.json

    Returns:
        Dictionary with counts of what was added
    """

    # Load vocabulary
    with open(vocab_path, 'r') as f:
        vocab = json.load(f)

    terms = vocab['terms']
    added_count = 0
    terms_filled = []

    # Process each term
    for term in terms:
        term_id = term['term_id']
        level = term['level']
        operationalizations = term['operationalizations']

        # Only fill empty operationalizations for level >= 2 (skip domain headers)
        if level >= 2 and len(operationalizations) == 0 and term_id in OPERATIONALIZATIONS:
            new_ops = OPERATIONALIZATIONS[term_id]
            term['operationalizations'] = new_ops
            added_count += len(new_ops)
            terms_filled.append({
                'term_id': term_id,
                'name': term['name'],
                'count': len(new_ops)
            })

    # Count total operationalizations and terms with them
    total_operationalizations = sum(
        len(term['operationalizations'])
        for term in terms
    )
    terms_with_ops = sum(
        1 for term in terms
        if len(term['operationalizations']) > 0
    )

    # Update stats
    vocab['stats']['operationalizations_count'] = total_operationalizations
    vocab['stats']['terms_count'] = len(terms)
    vocab['generated_at'] = datetime.utcnow().isoformat() + '+00:00'

    # Write back to file
    with open(vocab_path, 'w') as f:
        json.dump(vocab, f, indent=2)

    return {
        'operationalizations_added': added_count,
        'terms_filled': terms_filled,
        'total_operationalizations': total_operationalizations,
        'terms_with_operationalizations': terms_with_ops,
        'total_terms': len(terms),
        'terms_without_operationalizations': len(terms) - terms_with_ops
    }


def print_summary(result: dict):
    """Print a formatted summary of the backfill operation."""

    print("\n" + "="*70)
    print("OUTCOME VOCABULARY BACKFILL SUMMARY")
    print("="*70)

    print(f"\nOperationalizations Added: {result['operationalizations_added']}")
    print(f"Terms Filled: {len(result['terms_filled'])}")

    if result['terms_filled']:
        print("\nTerms with New Operationalizations:")
        print("-" * 70)
        for item in result['terms_filled']:
            print(f"  • {item['term_id']:40} ({item['count']} ops) — {item['name']}")

    print("\n" + "-"*70)
    print("FINAL STATISTICS")
    print("-"*70)
    print(f"Total Terms: {result['total_terms']}")
    print(f"Terms WITH operationalizations: {result['terms_with_operationalizations']}")
    print(f"Terms WITHOUT operationalizations: {result['terms_without_operationalizations']}")
    print(f"Total Operationalizations in Vocab: {result['total_operationalizations']}")
    print("="*70 + "\n")


if __name__ == '__main__':
    # Path to vocabulary file
    vocab_path = Path(__file__).parent.parent / 'contracts' / 'outcome_vocab' / 'outcome_vocab.json'

    if not vocab_path.exists():
        print(f"ERROR: Vocabulary file not found at {vocab_path}")
        exit(1)

    print(f"Reading vocabulary from: {vocab_path}")
    result = backfill_operationalizations(vocab_path)
    print_summary(result)
    print(f"✓ Updated vocabulary written to: {vocab_path}")
