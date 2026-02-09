# PHENOMENOLOGICAL STUDY EXTRACTION TEMPLATE v1.0

**Version**: 1.0.0
**Date**: February 9, 2026
**Status**: Complete (with panel additions)
**Panel Review**: Pearl, Cartwright, Simon, Bates, Kaplan, Walton, Lipton, Hearst, Teufel
**Tradition**: Husserl, Heidegger, Merleau-Ponty → Moustakas, van Manen, Smith (IPA)

---

## PURPOSE

Phenomenological studies explore **the essence of lived experience**. They uniquely contribute:
- First-person accounts of phenomena as experienced
- Identification of essential structures of experience
- Rich description of meaning and intentionality
- Understanding of how phenomena appear to consciousness
- Basis for empathic understanding and design

**Epistemological Note**: Phenomenology brackets causal explanation to focus on experience itself.

---

## PHENOMENOLOGICAL APPROACHES

| Approach | Focus | Key Question | Output |
|----------|-------|--------------|--------|
| **Descriptive (Husserl)** | Essence of phenomenon | "What is the essential structure?" | Essence description |
| **Hermeneutic (Heidegger)** | Interpreted meaning | "What does it mean to experience X?" | Interpreted account |
| **IPA (Smith)** | Individual sense-making | "How does this person make sense of X?" | Idiographic themes |
| **Embodied (Merleau-Ponty)** | Bodily experience | "How is X lived in the body?" | Embodied description |

---

## WHAT THIS TEMPLATE CAN ANSWER

| Category | Coverage | Notes |
|----------|----------|-------|
| Lived Experience | YES | First-person accounts |
| Meaning/Significance | YES | What phenomena mean to experiencers |
| Essential Structures | YES | Common features across experiences |
| Bodily/Sensory | YES | Embodied dimensions |
| Causal Mechanisms | NO | Bracketed by method |
| Generalization | LIMITED | Essence, not population |

---

## HUMAN-READABLE OUTPUT STRUCTURE

### 1. INTRODUCTION

```
## Introduction

**Phenomenon Under Investigation**: [What experience is being studied?]

**Phenomenological Approach**:
| Element | Value |
|---------|-------|
| Approach | Descriptive / Hermeneutic / IPA / Embodied |
| Philosophical grounding | [Husserl / Heidegger / Merleau-Ponty / van Manen] |
| Bracketing/Epoché | [How preconceptions were suspended] |

**Research Question**: [What is the lived experience of X?]

**Why Phenomenology**:
- Experience itself is the phenomenon of interest
- First-person perspective required
- Meaning and significance are central
```

### 2. METHODS

```
## Methods

### Participants

| Element | Value |
|---------|-------|
| N | [typically 3-15 for phenomenology] |
| Selection criteria | [Who has lived the experience] |
| Sampling | Purposive / Criterion / Snowball |
| Relationship to phenomenon | [How participants experienced X] |

### Data Collection

| Element | Value |
|---------|-------|
| Method | In-depth interview / Written description / Both |
| Interview type | Semi-structured / Unstructured / Narrative |
| Duration | [Average length] |
| N interviews per participant | |

**Interview Guide Focus**:
| Domain | Sample Questions |
|--------|------------------|
| Description | "Describe a time when you experienced X" |
| Meaning | "What did that experience mean to you?" |
| Embodied | "How did you feel it in your body?" |
| Context | "What was the situation/setting?" |

### Analysis

| Element | Value |
|---------|-------|
| Method | [Colaizzi / Giorgi / van Manen / IPA] |
| Bracketing documented | Yes / No |
| Member checking | Yes / No |
| Peer debriefing | Yes / No |

**Analysis Steps**:
1. [Step 1]
2. [Step 2]
3. [etc.]
```

### 3. FINDINGS

```
## Findings

### Essential Structure / Essence

**The lived experience of [phenomenon] is characterized by**:
> [Synthesis statement capturing the essence]

### Constituent Themes

| Theme | Description | Prevalence |
|-------|-------------|------------|
| [Theme 1] | [What this aspect of experience involves] | All / Most / Some |

#### Theme 1: [Name]

**Description**: [Rich description of this aspect of experience]

**Illustrative Quotes**:
> "[Quote 1]" — Participant X
> "[Quote 2]" — Participant Y

**Embodied/Sensory Dimensions**:
- [How this theme manifests bodily]

#### Theme 2: [Name]

[Same structure]

### Textural Description (What)

[Description of WHAT was experienced — textures, qualities, appearances]

### Structural Description (How)

[Description of HOW it was experienced — conditions, context, situatedness]

### Environmental Features (CNfA)

| Feature | How Experienced | Meaning Assigned |
|---------|-----------------|------------------|
| [Nature element] | [Perceptual quality] | [Significance] |
```

### 4. INTERPRETATION

```
## Interpretation

### Essence Statement

> [Definitive statement of the essential structure of the experience]

### Meaning and Significance

| Finding | Meaning for Participants | Theoretical Resonance |
|---------|-------------------------|----------------------|
| | | [Connection to theory] |

### Embodied Insights

| Bodily Experience | Interpretation |
|-------------------|----------------|
| | |

### What This Study Reveals

1. [Key insight 1]
2. [Key insight 2]

### What This Study CANNOT Conclude

1. ❌ Causal claims — phenomenology brackets causation
2. ❌ Statistical generalization — not the aim
3. ❌ Universal claims — essence is for those who share the experience

### Implications

| Domain | Implication |
|--------|-------------|
| Design | [How understanding experience informs design] |
| Practice | [How to support those having this experience] |
| Theory | [What this adds to theoretical understanding] |
```

---

## RULE CONVERSION

Phenomenological studies produce:
- **Experiential rules** (what experiences involve)
- **Meaning rules** (what phenomena signify)
- **Constraint rules** (boundaries from bracketing)

### Causal Level

**ALWAYS**: Not applicable (phenomenology brackets causation)

Phenomenology explicitly suspends causal judgment to focus on experience as it appears. Any causal claims would violate the method.

### Argument Scheme

**Primary**: `argument_from_position_to_know`
- Participants ARE the experts on their own experience
- First-person authority is epistemically privileged for experience

**Critical Questions**:
1. Did participants actually have the experience studied?
2. Were they able to articulate their experience?
3. Was the researcher's interpretation faithful to accounts?
4. Was bracketing maintained?

### Rule Template

```yaml
rules:
  # Experiential finding → Experiential rule
  - rule_id: "[author]_phenom_[year]_experience"
    rule_type: "experiential"  # New type for phenomenology

    description: "The lived experience of [phenomenon] involves [essential feature]"

    phenomenon: "[what experience was studied]"
    essential_feature: "[constituent of the experience]"

    experiential_structure:
      textural: "[what was experienced]"
      structural: "[how it was experienced]"
      embodied: "[bodily dimensions]"

    # Evidence
    evidence:
      n_participants:
      prevalence: "all|most|some"
      illustrative_quotes: []

    # PANEL ADDITIONS (v2)
    causal_level: null  # Explicitly null — phenomenology brackets causation
    argument_scheme: "argument_from_position_to_know"
    critical_questions:
      - "Did participants have the experience?"
      - "Was interpretation faithful to accounts?"
      - "Was bracketing maintained?"

    # Phenomenology-specific
    phenomenological_validity:
      approach: "descriptive|hermeneutic|ipa|embodied"
      bracketing_documented: true|false
      member_checking: true|false
      essence_derived: true|false

    extraction_difficulty: "hard"  # Interpretation required
    source_zone: "results"

    applicability:
      scope: "experiential"
      applies_to: "[those who share this experience]"
      does_not_apply_to: "[those who haven't experienced it]"

    ae_confidence: [0.50-0.70]  # Based on rigor, not causation

  # Meaning finding → Meaning rule
  - rule_id: "[author]_phenom_[year]_meaning"
    rule_type: "meaning"

    description: "[Environmental feature] signifies [meaning] in the experience of [phenomenon]"

    environmental_feature: "[what in environment]"
    meaning_assigned: "[what it means to experiencers]"
    context: "[when this meaning applies]"

    # Design implication
    design_relevance:
      implication: "[how to design for this meaning]"
      confidence: "experiential_basis"

    ae_confidence:
```

### Confidence Scoring

| Factor | Impact | Rationale |
|--------|--------|-----------|
| **Base** | 0.55 | Experiential authority |
| **Sample adequacy** | | |
| N ≥ 10 with saturation | +0.10 | Rich data |
| N = 5-9 | +0.05 | Adequate for phenomenology |
| N < 5 | -0.05 | Limited perspectives |
| **Bracketing** | | |
| Documented and maintained | +0.10 | Methodological rigor |
| Mentioned but not detailed | +0.00 | Standard |
| Not addressed | -0.10 | Bias risk |
| **Member checking** | | |
| Performed | +0.05 | Validation |
| Not performed | +0.00 | Common |
| **Essence derivation** | | |
| Clear synthesis | +0.05 | Phenomenological aim achieved |
| Themes only | +0.00 | Partial achievement |

**Range**: 0.45 (weak phenomenology) to 0.75 (rigorous phenomenology)

---

## MACHINE-READABLE DATA

```yaml
# ============================================
# HEADER
# ============================================
paper_id: ""
doi: ""
extraction_date: "YYYY-MM-DD"
article_type: "phenomenological"
source_depth: "full_text|abstract|metadata"

# ============================================
# PHENOMENOLOGICAL APPROACH
# ============================================
approach:
  type: "descriptive|hermeneutic|ipa|embodied"
  philosopher: "husserl|heidegger|merleau_ponty|van_manen|smith"
  bracketing_described: true|false
  bracketing_method: ""

# ============================================
# PHENOMENON
# ============================================
phenomenon:
  name: ""
  description: ""
  context: ""
  why_phenomenology: ""

# ============================================
# PARTICIPANTS
# ============================================
participants:
  n:
  selection_criteria: ""
  sampling: "purposive|criterion|snowball"
  relationship_to_phenomenon: ""
  demographics: {}

# ============================================
# DATA COLLECTION
# ============================================
data_collection:
  method: "interview|written_description|both"
  interview_type: "semi_structured|unstructured|narrative"
  average_duration_minutes:
  interviews_per_participant:
  interview_guide_domains: []

# ============================================
# ANALYSIS
# ============================================
analysis:
  method: "colaizzi|giorgi|van_manen|ipa|other"
  steps: []
  member_checking: true|false
  peer_debriefing: true|false
  saturation_reached: true|false

# ============================================
# FINDINGS
# ============================================
findings:
  essence_statement: ""

  themes:
    - name: ""
      description: ""
      prevalence: "all|most|some"
      quotes: []
      embodied_dimension: ""

  textural_description: ""
  structural_description: ""

  environmental_features:
    - feature: ""
      how_experienced: ""
      meaning_assigned: ""

# ============================================
# INTERPRETATION
# ============================================
interpretation:
  meaning_insights:
    - finding: ""
      meaning: ""
      theoretical_resonance: ""

  embodied_insights:
    - experience: ""
      interpretation: ""

  implications:
    design: ""
    practice: ""
    theory: ""

  limitations:
    - ""

# ============================================
# RULES GENERATED
# ============================================
rules:
  - rule_id: ""
    rule_type: "experiential"

    phenomenon: ""
    essential_feature: ""

    experiential_structure:
      textural: ""
      structural: ""
      embodied: ""

    evidence:
      n_participants:
      prevalence: ""
      quotes: []

    # v2 panel additions
    causal_level: null
    argument_scheme: "argument_from_position_to_know"
    critical_questions: []
    extraction_difficulty: "hard"
    source_zone: "results"

    phenomenological_validity:
      approach: ""
      bracketing: true|false
      member_checking: true|false

    applicability:
      scope: "experiential"
      applies_to: ""

    ae_confidence:

# ============================================
# QUALITY
# ============================================
quality:
  phenomenological_rigor: "high|moderate|low"
  bracketing_quality: "high|moderate|low"
  essence_clarity: "high|moderate|low"
  our_confidence:
```

---

## CNfA DOMAIN FEATURES

For environmental phenomenology:

```yaml
environmental_experience:
  # How environment appears to consciousness
  perceptual_qualities:
    - quality: "[color, texture, form, etc.]"
      experience: "[how perceived]"

  # Embodied environmental experience
  bodily_engagement:
    movement: "[how body moves in space]"
    posture: "[bodily orientation]"
    sensation: "[felt qualities]"

  # Affective dimensions
  mood_atmosphere:
    - atmosphere: "[environmental mood]"
      feeling: "[emotional quality]"

  # Meaning and significance
  environmental_meaning:
    - feature: ""
      significance: ""
      context: ""

  # Design implications from experience
  design_insights:
    - experience_finding: ""
      design_implication: ""
      confidence: "experiential"
```

---

## VALIDATION CHECKLIST

- [ ] **Phenomenon clearly identified** — What experience was studied
- [ ] **Approach specified** — Descriptive/Hermeneutic/IPA/Embodied
- [ ] **Bracketing documented** — How preconceptions were suspended
- [ ] **Essence derived** — Synthesis of essential structure
- [ ] **Quotes support themes** — First-person evidence
- [ ] **Embodied dimensions included** — Bodily experience
- [ ] **Causal level set to null** — Phenomenology brackets causation
- [ ] **Design implications extracted** — CNfA relevance

---

**END OF PHENOMENOLOGICAL STUDY TEMPLATE**
