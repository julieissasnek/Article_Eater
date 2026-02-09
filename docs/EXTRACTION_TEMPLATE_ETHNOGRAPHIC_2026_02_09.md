# ETHNOGRAPHIC STUDY EXTRACTION TEMPLATE v1.0

**Version**: 1.0.0
**Date**: February 9, 2026
**Status**: Complete (with panel additions)
**Panel Review**: Pearl, Cartwright, Simon, Bates, Kaplan, Walton, Lipton, Hearst, Teufel
**Tradition**: Anthropology → Geertz, Clifford, Marcus; Sociology → Hammersley, Atkinson

---

## PURPOSE

Ethnographic studies provide **cultural understanding through immersive fieldwork**. They uniquely contribute:
- Insider perspective on cultural practices (emic view)
- Understanding of shared meanings and values
- Documentation of behavior in natural context
- Thick description of cultural patterns
- Discovery of tacit knowledge and norms

**Key Feature**: Extended engagement with a cultural group in their natural setting.

---

## ETHNOGRAPHIC TYPES

| Type | Focus | Duration | Output |
|------|-------|----------|--------|
| **Classical** | Complete cultural system | Months-years | Holistic monograph |
| **Focused** | Specific practice/setting | Weeks-months | Focused account |
| **Critical** | Power and inequality | Variable | Critical analysis |
| **Autoethnographic** | Researcher's own culture | Variable | Reflexive narrative |
| **Digital** | Online communities | Variable | Virtual culture account |

---

## WHAT THIS TEMPLATE CAN ANSWER

| Category | Coverage | Notes |
|----------|----------|-------|
| Cultural Practices | YES | What people do in context |
| Shared Meanings | YES | What practices mean to group |
| Social Organization | YES | How groups structure activity |
| Tacit Knowledge | YES | Unspoken rules and norms |
| Causal Mechanisms | LIMITED | Observational only |
| Generalization | CULTURAL | To similar cultural contexts |

---

## HUMAN-READABLE OUTPUT STRUCTURE

### 1. INTRODUCTION

```
## Introduction

**Cultural Setting**:
| Element | Value |
|---------|-------|
| Group/Community | [Who was studied] |
| Setting | [Where fieldwork occurred] |
| Cultural focus | [Specific practices, values, or phenomena] |

**Research Questions**: [What cultural patterns are being explored?]

**Researcher Positionality**:
| Element | Value |
|---------|-------|
| Insider/Outsider | [Relationship to group] |
| Prior experience | [Background with this culture] |
| Reflexive stance | [How positionality was managed] |
```

### 2. METHODS

```
## Methods

### Fieldwork

| Element | Value |
|---------|-------|
| Duration | [Total time in field] |
| Intensity | [Full-time / Part-time / Periodic] |
| Entry | [How access was gained] |
| Role | Participant observer / Observer / Full participant |

### Data Sources

| Source | Specifics | Purpose |
|--------|-----------|---------|
| Participant observation | [What observed, how long] | [Primary culture data] |
| Interviews | [N, types, with whom] | [Emic perspectives] |
| Documents/Artifacts | [What collected] | [Cultural products] |
| Field notes | [When, how detailed] | [Recording] |

### Analysis

| Element | Value |
|---------|-------|
| Approach | Thematic / Narrative / Discourse / Framework |
| Coding | Open / Focused / Theoretical |
| Triangulation | [How sources combined] |
| Member checking | Yes / No |
```

### 3. FINDINGS

```
## Findings

### Cultural Context

**Setting Description**:
> [Thick description of the cultural setting]

**Key Actors/Roles**:
| Role | Description | Significance |
|------|-------------|--------------|
| | | |

### Cultural Themes

#### Theme 1: [Name]

**Description**: [What this cultural pattern involves]

**Observed Practices**:
- [Practice 1]
- [Practice 2]

**Emic Meanings** (insider perspective):
> "[Quote from participant]"

**Etic Analysis** (researcher interpretation):
> [Analytical interpretation]

**Vignette/Example**:
> [Rich description of a specific instance]

### Social Organization

| Structure | Description | Function |
|-----------|-------------|----------|
| | | |

### Environmental-Cultural Relationships (CNfA)

| Environmental Feature | Cultural Meaning | Practice Associated |
|----------------------|------------------|---------------------|
| [Space/nature element] | [What it signifies] | [How used] |

### Tacit Rules

| Rule | Evidence | Consequence of Violation |
|------|----------|-------------------------|
| | [How discovered] | |
```

### 4. INTERPRETATION

```
## Interpretation

### Cultural Logic

**How this culture makes sense**:
> [Synthesis of cultural coherence]

### Key Cultural Insights

| Insight | Evidence | Significance |
|---------|----------|--------------|
| | | |

### Relationship to Theory

| Theory | Relationship | Notes |
|--------|--------------|-------|
| | Supports / Extends / Challenges | |

### Transferability

**This account may transfer to**:
- [Similar cultural contexts]

**This account does NOT transfer to**:
- [Different cultural contexts]

### Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Researcher positionality | | |
| Access constraints | | |
| Duration limitations | | |

### Implications

| Domain | Implication |
|--------|-------------|
| Design | [How to design for this culture] |
| Policy | [How to work with this group] |
| Theory | [What this adds to understanding] |
```

---

## RULE CONVERSION

Ethnographic studies produce:
- **Cultural rules** (practices and their meanings)
- **Norm rules** (tacit expectations)
- **Context rules** (when cultural patterns apply)

### Causal Level

| Finding Type | Causal Level | Justification |
|--------------|--------------|---------------|
| Cultural practice description | `association` | Observational |
| Cultural meaning/significance | Not applicable | Interpretive |
| Behavior-environment link | `association` | Correlational observation |

### Argument Scheme

**Primary**: `argument_from_position_to_know` (for emic accounts) + `argument_from_sign` (for observed patterns)

**Critical Questions**:
1. Was the researcher sufficiently immersed?
2. Was the emic perspective accurately captured?
3. Are observations representative of the culture?
4. Was positionality adequately addressed?

### Rule Template

```yaml
rules:
  # Cultural practice → Cultural rule
  - rule_id: "[author]_ethno_[year]_practice"
    rule_type: "cultural"

    description: "In [cultural context], [practice] signifies [meaning]"

    cultural_context:
      group: "[who]"
      setting: "[where]"
      scope: "[when this applies]"

    practice:
      name: "[what people do]"
      description: "[how it's done]"
      frequency: "[how common]"

    meaning:
      emic: "[insider meaning]"
      etic: "[analytical interpretation]"

    evidence:
      observation_hours:
      n_informants:
      triangulated: true|false

    # PANEL ADDITIONS (v2)
    causal_level: "association"  # Observational
    argument_scheme: "argument_from_position_to_know"
    critical_questions:
      - "Was immersion sufficient?"
      - "Is emic perspective accurate?"
      - "Are observations representative?"

    extraction_difficulty: "hard"
    source_zone: "results"

    applicability:
      cultural_scope: "[this cultural group]"
      transferable_to: "[similar contexts]"
      not_transferable_to: "[different contexts]"

    ae_confidence: [0.50-0.70]

  # Tacit norm → Norm rule
  - rule_id: "[author]_ethno_[year]_norm"
    rule_type: "norm"

    description: "In [context], [behavior] is expected/prohibited"

    norm:
      content: "[what is expected]"
      type: "prescriptive|proscriptive"
      strength: "strong|moderate|weak"

    violation_consequence: "[what happens if violated]"

    evidence:
      how_discovered: "[observation of violation, informant report, etc.]"

    ae_confidence:

  # Environment-culture link → Contextual rule
  - rule_id: "[author]_ethno_[year]_env_culture"
    rule_type: "contextual"

    description: "[Environmental feature] is used for/means [X] in this culture"

    environmental_feature: "[what in environment]"
    cultural_use: "[how used/understood]"
    cultural_meaning: "[what it signifies]"

    design_implication:
      insight: "[how to design for this culture-environment relationship]"
      confidence: "cultural_specific"

    ae_confidence:
```

### Confidence Scoring

| Factor | Impact | Rationale |
|--------|--------|-----------|
| **Base** | 0.55 | Immersive observation |
| **Duration** | | |
| > 6 months | +0.10 | Deep immersion |
| 1-6 months | +0.05 | Adequate |
| < 1 month | -0.05 | Limited |
| **Triangulation** | | |
| Multiple sources combined | +0.10 | Robust |
| Single source dominant | +0.00 | Standard |
| **Positionality** | | |
| Reflexive and documented | +0.05 | Transparent |
| Not addressed | -0.05 | Bias risk |
| **Member checking** | | |
| Performed | +0.05 | Validation |

**Range**: 0.45 (brief ethnography) to 0.75 (rigorous extended ethnography)

---

## MACHINE-READABLE DATA

```yaml
# ============================================
# HEADER
# ============================================
paper_id: ""
doi: ""
extraction_date: "YYYY-MM-DD"
article_type: "ethnographic"
source_depth: "full_text|abstract|metadata"

# ============================================
# ETHNOGRAPHIC DESIGN
# ============================================
design:
  type: "classical|focused|critical|autoethnographic|digital"
  duration_months:
  intensity: "full_time|part_time|periodic"
  role: "participant_observer|observer|full_participant"

# ============================================
# CULTURAL SETTING
# ============================================
setting:
  group: ""
  location: ""
  cultural_focus: ""
  entry_method: ""

# ============================================
# RESEARCHER POSITIONALITY
# ============================================
positionality:
  insider_outsider: "insider|outsider|between"
  prior_experience: ""
  reflexive_stance: ""
  documented: true|false

# ============================================
# DATA SOURCES
# ============================================
data_sources:
  participant_observation:
    hours:
    settings: []
    activities: []

  interviews:
    n:
    types: []
    informants: []

  documents:
    types: []

  field_notes:
    frequency: ""
    detail_level: ""

# ============================================
# ANALYSIS
# ============================================
analysis:
  approach: "thematic|narrative|discourse|framework"
  coding: "open|focused|theoretical"
  triangulation: true|false
  member_checking: true|false

# ============================================
# FINDINGS
# ============================================
findings:
  setting_description: ""

  roles:
    - role: ""
      description: ""
      significance: ""

  themes:
    - name: ""
      description: ""
      practices: []
      emic_meaning: ""
      etic_analysis: ""
      vignette: ""

  social_organization:
    - structure: ""
      description: ""
      function: ""

  environmental_cultural:
    - feature: ""
      meaning: ""
      practice: ""

  tacit_rules:
    - rule: ""
      evidence: ""
      violation_consequence: ""

# ============================================
# INTERPRETATION
# ============================================
interpretation:
  cultural_logic: ""

  insights:
    - insight: ""
      evidence: ""
      significance: ""

  theory_relationship:
    - theory: ""
      relationship: "supports|extends|challenges"

  transferability:
    transfers_to: []
    does_not_transfer_to: []

  limitations:
    - limitation: ""
      impact: ""
      mitigation: ""

  implications:
    design: ""
    policy: ""
    theory: ""

# ============================================
# RULES GENERATED
# ============================================
rules:
  - rule_id: ""
    rule_type: "cultural|norm|contextual"

    description: ""

    cultural_context:
      group: ""
      setting: ""
      scope: ""

    evidence:
      observation_hours:
      n_informants:
      triangulated:

    # v2 panel additions
    causal_level: "association"
    argument_scheme: ""
    critical_questions: []
    extraction_difficulty: "hard"
    source_zone: ""

    applicability:
      cultural_scope: ""
      transferable_to: []

    ae_confidence:

# ============================================
# QUALITY
# ============================================
quality:
  immersion_depth: "high|moderate|low"
  triangulation: "high|moderate|low"
  reflexivity: "high|moderate|low"
  our_confidence:
```

---

## CNfA DOMAIN FEATURES

```yaml
environment_culture:
  # How environment features in cultural life
  environmental_affordances:
    - feature: ""
      cultural_use: ""
      meaning: ""

  # Place attachment and meaning
  place_meanings:
    - place: ""
      cultural_significance: ""
      practices_located: []

  # Nature-culture relationships
  nature_culture:
    - nature_element: ""
      cultural_interpretation: ""
      rituals_practices: []

  # Spatial organization
  spatial_culture:
    public_private: ""
    sacred_profane: ""
    territories: []

  # Design implications
  culturally_informed_design:
    - cultural_finding: ""
      design_implication: ""
      cultural_specificity: "high|moderate|universal"
```

---

## VALIDATION CHECKLIST

- [ ] **Cultural group identified** — Who was studied
- [ ] **Fieldwork duration documented** — Time in field
- [ ] **Positionality addressed** — Researcher relationship to group
- [ ] **Emic perspectives captured** — Insider meanings
- [ ] **Thick description provided** — Rich contextualized accounts
- [ ] **Triangulation performed** — Multiple data sources
- [ ] **Transferability specified** — Where findings apply

---

**END OF ETHNOGRAPHIC STUDY TEMPLATE**
