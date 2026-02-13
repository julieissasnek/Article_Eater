# Off-Topic Filter Criteria for CNfA Corpus

**Date**: 2026-02-11
**Purpose**: Identify and quarantine papers that passed initial triage but are NOT relevant to Cognitive Neuroarchitecture (CNfA)

---

## Core Relevance Requirements

A paper is ON-TOPIC if it satisfies ALL of:

### 1. Human Focus
The study must involve **humans** as subjects or end-users:
- Human participants, occupants, users, workers, students, patients
- Human perception, cognition, emotion, behavior, performance
- Human experience of space or environment

**EXCLUDE if about**:
- Animals only (fish, mice, rats, birds)
- Cell cultures, in vitro studies
- Pure material/structural testing without human outcomes
- Computational/algorithmic studies without human application

### 2. Built Environment Context
The study must address the **built environment** or its attributes:
- Buildings, rooms, offices, hospitals, schools, homes
- Interior spaces, workplaces, urban environments
- Environmental attributes: light, sound, temperature, air, space, nature/biophilia

**EXCLUDE if about**:
- Natural environments only (forests, oceans) without built environment connection
- Industrial processes (oil wells, manufacturing)
- Pure ecology or wildlife biology
- Transportation systems (unless station/terminal design)

### 3. Sensible Domain
The venue/journal should be plausibly related to:
- Architecture, design, building science
- Environmental psychology, cognitive science
- Human factors, ergonomics
- Health sciences (when studying environment-health links)
- Lighting, acoustics, thermal comfort research

**EXCLUDE if venue clearly indicates**:
- Petroleum/oil/gas engineering
- Materials science (polymers, alloys)
- Pure machine learning/AI (without application)
- Legal studies
- Marine biology, fisheries

---

## Exclusion Keywords (Abstract/Title)

### Strong Exclusion (likely off-topic)
```
ANIMALS: fish, mice, rats, rodents, zebrafish, larvae, animal model
INDUSTRIAL: offshore, drilling, wells, petroleum, oil rig, pipeline
MATERIALS: polymer, alloy, nanoparticle, synthesis, catalyst
MEDICAL_PROCEDURE: surgery, chemotherapy, dosage, drug trial, tumor
PURE_ML: neural network accuracy, model performance, classification accuracy
BIOLOGY: cell culture, in vitro, DNA, RNA, protein expression
LEGAL: court, litigation, legal framework, statute
```

### Weak Exclusion (check context)
```
algorithm, model, simulation  # OK if about building/environment simulation
underwater, marine            # OK if about aquariums or coastal buildings
plant                         # OK if about indoor plants/biophilia, not botany
```

---

## Inclusion Keywords (Abstract/Title)

Papers containing these are MORE LIKELY on-topic:

### Built Environment
```
building, architecture, interior, office, workplace, hospital, school
room, space, indoor, residential, commercial, urban
design, layout, facade, window, ceiling
```

### Environmental Attributes
```
light, daylight, illumination, lighting, lux, circadian
noise, sound, acoustic, soundscape, speech, auditory
thermal, temperature, HVAC, ventilation, air quality
nature, plant, green, biophilic, garden, view
spatial, density, enclosure, prospect, refuge
```

### Human Outcomes
```
cognition, attention, memory, concentration, performance
mood, stress, wellbeing, satisfaction, comfort
productivity, task performance, learning
perception, preference, experience
health, sleep, fatigue, recovery
```

### Study Indicators
```
participants, subjects, n=, sample, occupants, users
experiment, study, survey, questionnaire, field study
measured, assessed, evaluated, compared
```

---

## Filtering Algorithm

```python
def is_likely_off_topic(paper) -> Tuple[bool, str]:
    """
    Returns (is_off_topic, reason).
    """
    title = paper.title.lower()
    abstract = paper.abstract.lower()
    venue = (paper.venue or "").lower()
    combined = f"{title} {abstract} {venue}"

    # Strong exclusions
    if any(kw in combined for kw in ANIMAL_KEYWORDS):
        if not any(kw in combined for kw in ["aquarium", "zoo", "biophilic"]):
            return True, "animal_study"

    if any(kw in combined for kw in INDUSTRIAL_KEYWORDS):
        return True, "industrial_process"

    if any(kw in combined for kw in PURE_ML_KEYWORDS):
        if not any(kw in combined for kw in BUILT_ENV_KEYWORDS):
            return True, "pure_ml_no_env"

    if any(kw in combined for kw in LEGAL_KEYWORDS):
        return True, "legal_study"

    # Check for human focus
    has_human_focus = any(kw in combined for kw in HUMAN_KEYWORDS)
    has_built_env = any(kw in combined for kw in BUILT_ENV_KEYWORDS)
    has_env_attr = any(kw in combined for kw in ENV_ATTR_KEYWORDS)

    if not has_human_focus and not has_built_env:
        return True, "no_human_or_built_env"

    # Venue check
    if any(kw in venue for kw in OFFTOPIC_VENUE_KEYWORDS):
        return True, "offtopic_venue"

    return False, "on_topic"
```

---

## Quarantine Process

1. Run filter on all `triage_decision = 'send_to_eater'` papers
2. Set `off_topic_flag = 1` for filtered papers
3. Set `off_topic_score` to confidence (0-1)
4. Set `topic_decision = 'quarantine'`
5. Log reason in `topic_category` field

Papers can be manually reviewed and un-quarantined if the filter was wrong.

---

## Examples from Current Corpus

### Should be QUARANTINED

| Paper ID | Title | Reason |
|----------|-------|--------|
| sha256:798c26aa8c81 | "Complexity As A Feature Of Inte..." | Pure ML (MRSLVQ algorithms) |
| sha256:7d6ef3515eb7 | "Beyond The Visual: The Impacts" | Legal study (women's law, visual aids) |
| sha256:21e3d7b378d1 | "Literature Review On Semi..." | Statistics (functional data analysis) |
| sha256:7bb5a66126b1 | "Effects Of Sound Masking Noise On" | Animal study (fish, underwater noise) |
| doi:10.2118/216881-ms | "Offshore Wells Risk Management" | Industrial (petroleum engineering) |

### Should REMAIN on-topic

| Paper ID | Title | Reason |
|----------|-------|--------|
| sha256:16411ff2fd9e | "Biophilia Hypothesis" | Human-nature connection theory |
| sha256:70a5a275d9cf | "Light, Health..." | Light therapy, human health |
| doi:10.26687/archnet-ijar.v9i2.464 | "Sustainable Spaces with Psychological Values" | Architecture + psychology |
| doi:10.1186/s41235-020-00243-4 | "Senses of place: architectural design" | Multisensory architecture |

---

## Revision History

| Date | Change |
|------|--------|
| 2026-02-11 | Initial criteria based on corpus analysis |
