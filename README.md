# Article Eater: Cognitive-Mechanism-Referenced Building Assessment

A research system that extracts causal claims from scientific literature and evaluates buildings against evidence-based wellbeing criteria using Bayesian networks.

## What This Is

Article Eater implements **Compositional Mechanistic Reasoning (CMR)** for built environment assessment. It:

1. **Evaluates buildings** against 150+ templates derived from cognitive neuroscience of architecture research
2. **Processes research papers** to extract causal claims and match them to existing evidence
3. **Computes Wellbeing Impact Scores (WIS)** that aggregate mechanistic evidence across domains

The system bridges Tier 2 domain theories (Attention Restoration Theory, Stress Recovery Theory, Biophilia) to Tier 1 template mechanisms with explicit reduction mappings.

## Quick Start

### Tier A Quick Assessment (Visual Observation Only)

```bash
python -m src.cmr.cli quick-assess \
    --ceiling 3.0 \
    --area 25 \
    --nature-view nature \
    --material wood \
    --wayfinding \
    --thermal operable_windows
```

Output includes:
- Overall rating (Good/Fair/Needs Attention/Poor)
- Wellness Score (0-100)
- Top strengths and deficits
- Actionable recommendations
- Suggestions for deeper assessment

### Full Building Evaluation

```bash
python -m src.cmr.cli evaluate \
    --building-type research_institute \
    --ceiling-height 2.75 \
    --floor-area 18.0 \
    --illuminance 500 \
    --noise 38 \
    --has-nature-view \
    --view-content nature_with_water \
    --primary-material wood \
    --occupant-age 35
```

### Paper Evaluation

```bash
python -m src.cmr.cli evaluate-paper \
    --claims '[{"iv": "nature_view", "dv": "stress_recovery", "direction": "increase", "effect_size": 0.5}]'
```

## Architecture Overview

```
src/cmr/
├── building_eval.py       # Main building evaluation pipeline
├── paper_eval.py          # Paper claim evaluation
├── template_computations.py  # 56 compute functions
├── lifespan_moderation.py # Age-based sensitivity curves
├── reductions/            # Tier 2 theory reductions
│   ├── art_reduction.py   # Attention Restoration Theory
│   ├── srt_reduction.py   # Stress Recovery Theory
│   └── biophilia_reduction.py
├── quick_assess.py        # Tier A simplified assessment
└── cli.py                 # Command-line interface

data/
├── templates/             # 150 JSON template definitions
└── reductions/            # Theory reduction JSON files
```

## Theory Basis

The system is grounded in:

- **10 Tier 1 Frameworks**: Predictive Processing, Spatial Navigation, Dual-Process, DMN/TPN Dynamics, Neuromodulatory Systems, Interoceptive/Constructionist Affect, Memory Systems, Embodied Cognition, Chronobiological Regulation, Multisensory Integration

- **Tier 2 Domain Theories**: ART (Kaplan 1995), SRT (Ulrich 1983), Biophilia (Wilson 1984, Kellert 2005)

- **Quinean Web of Belief**: Claims accumulate coherence through mutual support, not foundational certainty

See `docs/69_Corpus_Methodology_Statement_V1_0.md` for full methodology.

## Current Status

**Operational:**
- Building evaluation with 56 real compute functions
- Paper evaluation with template matching
- Tier 2 reductions (ART, SRT, Biophilia)
- Lifespan moderation (age-sensitive responses)
- Quick assessment for Tier A inputs

**Limitations:**
- Some templates are stubs awaiting calibration data
- Gap templates (T1-T11) require future expert panels
- Field validation studies not yet conducted

## Installation

```bash
git clone <repo>
cd Article_Eater_PostQuinean_v1
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running Tests

```bash
pytest tests/ -v
```

## Contributing

This is a research project. Contributions should:
1. Maintain epistemic honesty about evidence quality
2. Document calibration status and confidence levels
3. Preserve traceability to source literature

## License

Research use only. Contact project owner for licensing.
