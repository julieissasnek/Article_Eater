# ChatGPT Task List: Evidence Processing Pipeline

**Date**: 2026-02-12
**Task List ID**: CHAT-TASKS-2026-02-12
**Purpose**: Offload long-running evidence processing tasks to ChatGPT

---

## Overview

These tasks are suitable for ChatGPT because they:
- Require careful reading and extraction from text
- Are tedious but not technically complex
- Benefit from language understanding
- Can be batched and parallelized
- Don't require real-time system integration

---

## TASK 1: Abstract Processing

**ID**: CHAT-T1-ABSTRACT-PROCESSING
**Priority**: HIGH
**Estimated Work**: 4-6 hours per 100 abstracts

### Context
We have a corpus of scientific paper abstracts about built environment psychology. Each abstract needs to be processed into structured findings that can become beliefs in our epistemic web.

### Input Format
```json
{
  "doi": "10.1234/example",
  "title": "Effects of daylight on worker productivity",
  "abstract": "This study examined...",
  "year": 2023,
  "journal": "Building and Environment"
}
```

### Output Format
```json
{
  "doi": "10.1234/example",
  "findings": [
    {
      "finding_id": "f1",
      "content": "Daylight exposure (>300 lux) increases worker productivity by 12% compared to artificial lighting",
      "environment_variable": "daylight",
      "outcome_variable": "productivity",
      "effect_direction": "positive",
      "effect_size": "12% increase",
      "population": "office workers",
      "setting": "open-plan office",
      "sample_size": 156,
      "study_type": "field_experiment",
      "credence_estimate": 0.75,
      "confidence_notes": "Controlled study but single site"
    }
  ],
  "causal_claims": ["daylight → productivity"],
  "theories_mentioned": ["circadian rhythm", "alertness"],
  "limitations_noted": ["single building", "self-report measures"]
}
```

### Prompt for ChatGPT

```
You are an expert research assistant extracting structured findings from scientific abstracts about built environment psychology (how physical spaces affect human cognition, mood, stress, productivity).

For each abstract, extract:

1. **FINDINGS**: Each distinct empirical finding as a separate entry
   - Content: Clear statement of what was found (IV → DV, effect direction, magnitude if stated)
   - Environment variable: The physical/spatial variable (daylight, noise, plants, temperature, crowding, ceiling height, etc.)
   - Outcome variable: The psychological/behavioral outcome (stress, productivity, mood, attention, satisfaction, etc.)
   - Effect direction: positive, negative, null, or mixed
   - Effect size: Quantitative if available (%, r, d, β)
   - Population: Who was studied
   - Setting: Where (office, hospital, school, lab, etc.)
   - Sample size: N if stated
   - Study type: experiment, quasi-experiment, survey, observation, meta-analysis
   - Credence estimate: Your estimate 0-1 of how confident we should be
   - Confidence notes: Why you assigned that credence

2. **CAUSAL CLAIMS**: List any causal relationships claimed (format: A → B)

3. **THEORIES**: Any theoretical frameworks mentioned (ART, SRT, Biophilia, etc.)

4. **LIMITATIONS**: Any limitations the authors note

IMPORTANT RULES:
- Only extract what the abstract actually states, don't infer
- If effect size is not stated, leave blank
- Separate distinct findings (don't merge multiple IVs or DVs)
- Use canonical variable names when possible:
  - Environment: daylight, noise, plants, vegetation, wood, temperature, crowding, ceiling_height, view, air_quality
  - Outcomes: stress, productivity, mood, attention, focus, satisfaction, creativity, wellbeing, fatigue, cognitive_load

ABSTRACT TO PROCESS:
[INSERT ABSTRACT HERE]
```

### Batch Instructions
Process abstracts in batches of 10. Save output as JSONL (one JSON object per line) to:
`data/processed_abstracts/batch_YYYYMMDD_NNN.jsonl`

---

## TASK 2: Table Extraction

**ID**: CHAT-T2-TABLE-EXTRACTION
**Priority**: HIGH
**Estimated Work**: 2-3 hours per 50 tables

### Context
Scientific papers often contain results tables that summarize multiple findings. These need to be extracted into structured format.

### Input
Provide ChatGPT with:
- Paper DOI and title
- Table caption
- Table content (as markdown or text)

### Prompt for ChatGPT

```
You are extracting structured findings from a results table in a scientific paper about built environment effects on human outcomes.

TABLE CONTEXT:
Paper: [TITLE]
DOI: [DOI]
Table Caption: [CAPTION]

TABLE CONTENT:
[PASTE TABLE AS MARKDOWN]

For each row in the table that represents a finding, extract:
{
  "row_id": "r1",
  "independent_variable": "the environmental factor",
  "dependent_variable": "the outcome measured",
  "effect_direction": "positive/negative/null",
  "statistic_type": "β/r/d/OR/etc",
  "statistic_value": 0.00,
  "p_value": 0.00,
  "confidence_interval": [lower, upper],
  "sample_size": N,
  "notes": "any qualifiers or conditions"
}

Output as JSON array. Include ALL rows, even null findings (important for meta-analysis).
```

---

## TASK 3: Citation Relevance Filtering

**ID**: CHAT-T3-CITATION-PRUNING
**Priority**: MEDIUM
**Estimated Work**: 1-2 hours per 200 citations

### Context
We have lists of papers from literature searches. Many are irrelevant to built environment psychology. Filter to keep only relevant ones.

### Input Format
```json
{
  "citation_id": "c1",
  "title": "Paper title",
  "abstract": "Abstract text if available",
  "keywords": ["keyword1", "keyword2"]
}
```

### Prompt for ChatGPT

```
You are filtering a list of academic citations to identify papers relevant to BUILT ENVIRONMENT PSYCHOLOGY.

RELEVANT topics include:
- Effects of physical space features on human psychology/behavior
- Daylight, lighting, views, nature exposure
- Noise, acoustics, sound environments
- Temperature, thermal comfort, air quality
- Space layout, crowding, density, ceiling height
- Biophilic design, plants, natural materials
- Color, aesthetics, visual complexity
- Outcomes: stress, productivity, mood, attention, wellbeing, health, satisfaction

NOT RELEVANT:
- Pure architecture without human outcomes
- Urban planning without psychological measures
- Building energy/sustainability without occupant effects
- Medical/clinical studies without environmental factors
- Animal studies
- Outdoor/wilderness (unless compared to indoor)

For each citation, output:
{
  "citation_id": "c1",
  "relevant": true/false,
  "confidence": 0.0-1.0,
  "reason": "brief explanation",
  "primary_topic": "best topic category if relevant"
}

CITATIONS TO FILTER:
[INSERT CITATIONS]
```

---

## TASK 4: Canonical ID Mapping

**ID**: CHAT-T4-CANONICAL-MAPPING
**Priority**: HIGH
**Estimated Work**: 1 hour per 100 findings

### Context
Extracted findings use varied terminology. Map them to our canonical ontology.

### Canonical Environment Variables
```
sensory.light.natural (daylight, sunlight, natural light)
sensory.light.artificial (electric light, LED, fluorescent)
sensory.noise (noise, sound, acoustics)
sensory.thermal (temperature, thermal, heat, cold)
natural.vegetation (plants, greenery, vegetation, biophilia)
natural.wood (wood, timber, natural materials)
natural.view (nature view, window view, outdoor view)
spatial.density (crowding, density, occupancy)
spatial.ceiling (ceiling height, volume)
spatial.layout (open plan, private office, layout)
aesthetic.color (color, hue, saturation)
aesthetic.complexity (visual complexity, detail)
```

### Canonical Outcome Variables
```
psych.stress (stress, anxiety, tension, cortisol)
psych.mood (mood, affect, emotional state)
psych.satisfaction (satisfaction, contentment)
psych.wellbeing (wellbeing, wellness, quality of life)
cog.attention (attention, focus, concentration)
cog.cognitive_load (cognitive load, mental effort)
cog.creativity (creativity, creative thinking)
cog.memory (memory, recall, retention)
perf.productivity (productivity, performance, output)
health.fatigue (fatigue, tiredness, energy)
health.sleep (sleep quality, circadian)
```

### Prompt for ChatGPT

```
You are mapping extracted environment and outcome variables to our canonical ontology.

For each finding, provide:
{
  "original_env": "the term used in the paper",
  "canonical_env_id": "our canonical ID",
  "env_confidence": 0.0-1.0,
  "original_outcome": "the term used",
  "canonical_outcome_id": "our canonical ID",
  "outcome_confidence": 0.0-1.0,
  "mapping_notes": "any ambiguity or uncertainty"
}

If a term doesn't map cleanly, use "UNMAPPED" and explain in notes.

ONTOLOGY:
[INSERT CANONICAL LISTS ABOVE]

FINDINGS TO MAP:
[INSERT FINDINGS]
```

---

## TASK 5: Belief Statement Generation

**ID**: CHAT-T5-BELIEF-GENERATION
**Priority**: MEDIUM
**Estimated Work**: 2 hours per 50 findings

### Context
Convert structured findings into natural language belief statements suitable for the epistemic web.

### Prompt for ChatGPT

```
Convert each structured finding into a clear, precise belief statement for an epistemic knowledge base.

RULES:
1. State the causal relationship clearly (X affects/increases/decreases Y)
2. Include effect magnitude if known
3. Include population/setting as scope conditions
4. Be specific but not verbose (1-2 sentences)
5. Use present tense for general findings, past tense for specific studies
6. Include confidence qualifiers where appropriate (e.g., "may", "tends to")

EXAMPLE INPUT:
{
  "environment_variable": "daylight",
  "outcome_variable": "productivity",
  "effect_direction": "positive",
  "effect_size": "12% increase",
  "population": "office workers",
  "setting": "open-plan office"
}

EXAMPLE OUTPUT:
"Daylight exposure increases worker productivity by approximately 12% in open-plan office environments. This effect has been demonstrated in office worker populations."

FINDINGS TO CONVERT:
[INSERT FINDINGS]
```

---

## TASK 6: Scope Condition Extraction

**ID**: CHAT-T6-SCOPE-EXTRACTION
**Priority**: MEDIUM
**Estimated Work**: 1.5 hours per 100 findings

### Context
Extract the boundary conditions under which findings apply.

### Prompt for ChatGPT

```
For each finding, extract the scope conditions - the boundaries within which the finding is claimed to hold.

SCOPE DIMENSIONS:
- Population: Who (age, occupation, health status, culture)
- Setting: Where (office, hospital, school, residential, lab)
- Duration: Time scale (acute exposure, chronic, seasonal)
- Dose: Amount/intensity (lux levels, dB, temperature range)
- Moderators: Conditions that change the effect

OUTPUT FORMAT:
{
  "finding_id": "f1",
  "scope_conditions": {
    "population": {
      "specified": true/false,
      "value": "description or null",
      "constraints": ["list", "of", "constraints"]
    },
    "setting": {
      "specified": true/false,
      "value": "type or null",
      "generalizability": "high/medium/low"
    },
    "duration": {
      "specified": true/false,
      "value": "description or null"
    },
    "dose": {
      "specified": true/false,
      "value": "range or threshold",
      "unit": "lux/dB/°C/etc"
    },
    "moderators": ["list of mentioned moderating factors"]
  },
  "scope_specified": true/false (overall)
}

FINDINGS TO PROCESS:
[INSERT FINDINGS]
```

---

## TASK 7: Theory Linkage

**ID**: CHAT-T7-THEORY-LINKAGE
**Priority**: LOW
**Estimated Work**: 2 hours per 100 findings

### Context
Link empirical findings to theoretical frameworks.

### Known Theories
```
ART: Attention Restoration Theory (Kaplan) - nature restores directed attention
SRT: Stress Recovery Theory (Ulrich) - nature reduces stress via evolution
Biophilia: (Wilson) - innate affiliation with nature
Prospect-Refuge: (Appleton) - preference for views + shelter
Thermal Comfort: (Fanger) - PMV/PPD models
Circadian: light affects circadian rhythm and alertness
Cognitive Load: (Sweller) - limited working memory capacity
Environmental Affordances: (Gibson) - environment offers action possibilities
Place Attachment: emotional bonds with physical spaces
```

### Prompt for ChatGPT

```
For each empirical finding, identify which theoretical framework(s) could explain the mechanism.

OUTPUT:
{
  "finding_id": "f1",
  "primary_theory": "theory name",
  "theory_fit": 0.0-1.0,
  "mechanism_explanation": "how the theory explains this finding",
  "alternative_theories": ["other", "possible", "explanations"],
  "theoretical_gap": true/false (finding not explained by known theories)
}

THEORIES:
[INSERT THEORY LIST]

FINDINGS TO LINK:
[INSERT FINDINGS]
```

---

## TASK 8: Conflict Detection

**ID**: CHAT-T8-CONFLICT-DETECTION
**Priority**: MEDIUM
**Estimated Work**: 3 hours per 200 finding pairs

### Context
Identify findings that conflict with each other.

### Prompt for ChatGPT

```
Compare pairs of findings to identify conflicts.

CONFLICT TYPES:
1. GENUINE_CONTRADICTION: Same IV, same DV, opposite direction, same scope
2. SCOPE_BOUNDARY: Opposite effects but different populations/settings
3. METHODOLOGICAL: Different measurement methods may explain difference
4. PRECISION: Same direction but very different magnitudes

For each pair:
{
  "finding_a_id": "f1",
  "finding_b_id": "f2",
  "conflict_detected": true/false,
  "conflict_type": "type or null",
  "conflict_severity": 0.0-1.0,
  "resolution_hypothesis": "possible explanation for difference",
  "scope_difference": "what differs between the two"
}

FINDINGS TO COMPARE:
[INSERT FINDING PAIRS]
```

---

## Execution Instructions

### For ChatGPT Users

1. **Start each session** with the task ID (e.g., "Working on CHAT-T1-ABSTRACT-PROCESSING")

2. **Request batch size** appropriate to context window:
   - Abstracts: 10-15 per batch
   - Tables: 5-10 per batch
   - Citations: 50-100 per batch
   - Short tasks: 20-30 per batch

3. **Save outputs** to the specified directory with naming convention:
   `{task_id}_{date}_{batch_number}.jsonl`

4. **Track progress** in:
   `data/processing_logs/CHAT_PROGRESS_2026-02-12.md`

5. **Report issues** with specific finding IDs if:
   - Ambiguous cases
   - Missing information
   - Possible errors in source

### Quality Control

After each batch:
- Spot-check 10% of outputs
- Verify JSON validity
- Check for obvious errors
- Note edge cases for review

---

## Data Locations

### Input Data
- Abstracts: `data/abstracts/*.json`
- Tables: `data/tables/*.md`
- Citations: `data/citations/*.json`
- Raw findings: `data/extracted_findings/*.jsonl`

### Output Data
- Processed abstracts: `data/processed_abstracts/`
- Mapped findings: `data/mapped_findings/`
- Filtered citations: `data/filtered_citations/`
- Belief statements: `data/belief_statements/`
- Scope conditions: `data/scope_conditions/`

---

## Priority Order

Execute tasks in this order:

1. **CHAT-T3**: Citation Pruning (reduce corpus to relevant papers)
2. **CHAT-T1**: Abstract Processing (extract findings from relevant abstracts)
3. **CHAT-T4**: Canonical Mapping (standardize terminology)
4. **CHAT-T5**: Belief Generation (create belief statements)
5. **CHAT-T6**: Scope Extraction (identify boundary conditions)
6. **CHAT-T2**: Table Extraction (detailed data from full papers)
7. **CHAT-T7**: Theory Linkage (connect to theoretical frameworks)
8. **CHAT-T8**: Conflict Detection (identify contradictions)

---

## Estimated Total Work

| Task | Per-Unit Time | Estimated Units | Total Hours |
|------|---------------|-----------------|-------------|
| T1: Abstracts | 5 min each | 500 | 42 |
| T2: Tables | 10 min each | 100 | 17 |
| T3: Citations | 1 min each | 2000 | 33 |
| T4: Mapping | 2 min each | 500 | 17 |
| T5: Beliefs | 3 min each | 500 | 25 |
| T6: Scopes | 2 min each | 500 | 17 |
| T7: Theory | 3 min each | 300 | 15 |
| T8: Conflicts | 2 min each | 200 pairs | 7 |
| **TOTAL** | | | **~170 hours** |

This can be parallelized across multiple ChatGPT sessions.
