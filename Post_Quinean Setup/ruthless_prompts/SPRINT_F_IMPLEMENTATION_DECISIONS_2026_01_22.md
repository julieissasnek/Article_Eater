# Sprint F Implementation Decisions for Panel Review

**Date**: January 22, 2026
**Purpose**: Validate implementation choices made during Sprint F
**Request**: Review these specific decisions and provide feedback

---

## Context

Sprint F implemented the recommendations from the ruthless review (2026-01-22). During implementation, specific choices were made that require expert validation. This document collects those decisions for panel review.

---

## Sprint F1: Domain Vocabulary Expansion (Kaplan Items)

### Decision F1.1: Neuroarchitecture Causal Patterns Added

**What I implemented** (`src/services/causal_classifier.py`):

```python
NEUROARCH_CAUSAL_PATTERNS = [
    # Original intervention patterns
    r'\bdesign\s+intervention\b',
    r'\bbuilt\s+environment\s+manipulation\b',
    # NEW: Building certification/design
    r'\bgreen\s+building\b',
    r'\bWELL\s+certif',
    r'\bLEED\b',
    r'\bbiophilic\s+design\b',
    # NEW: Lighting interventions
    r'\bdaylighting\b',
    r'\bglare\s+control\b',
    r'\blighting\s+design\b',
    r'\bcircadian\s+lighting\b',
    r'\btunable\s+lighting\b',
    # NEW: Environmental quality
    r'\bthermal\s+comfort\b',
    r'\bacoustic\s+comfort\b',
    r'\bindoor\s+air\s+quality\b',
    r'\bIAQ\b',
    r'\bair\s+quality\s+intervention\b',
    r'\bventilation\s+design\b',
]
```

**Questions for Kaplan**:
1. Are these patterns appropriate for CAUSAL tier, or should some be SUGGESTIVE?
2. Is `\bLEED\b` too broad (could match non-certification contexts)?
3. Should `thermal comfort` be causal or suggestive (it's often an outcome, not intervention)?
4. Are there critical neuroarchitecture terms I missed?

---

### Decision F1.2: Theoretical Framework Patterns

**What I implemented**:

```python
# Attention Restoration Theory (ART)
ATTENTION_RESTORATION_PATTERNS = [
    r'\bbeing\s+away\b',
    r'\bfascination\b',
    r'\bsoft\s+fascination\b',
    r'\bextent\b',  # ART component
    r'\bcompatibility\b',  # ART component
    r'\battention\s+restoration\s+theory\b',
    r'\bART\b',
    r'\bKaplan\b',  # Rachel & Stephen Kaplan
    r'\bdirected\s+attention\s+fatigue\b',
]

# Prospect-Refuge Theory
PROSPECT_REFUGE_PATTERNS = [
    r'\bprospect\b',
    r'\brefuge\b',
    r'\bmystery\b',
    r'\bcomplexity\b',
    r'\bAppleton\b',
    r'\bsavanna\s+hypothesis\b',
]

# Stress Recovery Theory (SRT)
STRESS_RECOVERY_PATTERNS = [
    r'\bstress\s+recovery\s+theory\b',
    r'\bSRT\b',
    r'\bUlrich\b',
    r'\baffective\s+response\b',
    r'\bpsychophysiological\s+stress\b',
]

# Biophilia Hypothesis
BIOPHILIA_PATTERNS = [
    r'\bbiophilia\b',
    r'\bbiophilic\b',
    r'\bWilson\b',
    r'\bnature\s+connection\b',
]
```

**Questions for Kaplan**:
1. Are `extent` and `compatibility` too generic without ART context?
2. Is `mystery` and `complexity` too broad for prospect-refuge detection?
3. Should author names (`Kaplan`, `Ulrich`, `Wilson`) be detection triggers?
4. What about Stress Reduction Theory vs Stress Recovery Theory distinction?
5. Missing frameworks? (e.g., Place Attachment, Sense of Place, Genius Loci?)

---

### Decision F1.3: Fallback Outcomes Expanded

**What I implemented** (`src/services/reporting.py`):

```python
_FALLBACK_OUTCOME_CATEGORIES = {
    # Original
    'behav.productivity', 'cog.performance', 'affect.stress', 'health.wellbeing',
    'health', 'cog.attention', 'affect.mood', 'physio.stress',
    # NEW per Kaplan
    'cog.creativity',       # Creative thinking
    'behav.collaboration',  # Teamwork, communication
    'physio.circadian',     # Circadian rhythm measures
    'affect.satisfaction',  # Job/space satisfaction
    'cog.focus',           # Concentration, focus
    'physio.cortisol',     # Stress hormone
    'behav.absenteeism',   # Attendance patterns
}
```

**Questions for Kaplan**:
1. Is the taxonomy hierarchy correct (behav/cog/affect/physio)?
2. Should `physio.circadian` be under `health` instead?
3. Is `cog.focus` distinct enough from `cog.attention`?
4. Missing outcomes? (e.g., social interaction, privacy, control/autonomy?)

---

### Decision F1.4: Domain Confounders Added

**What I implemented** (`src/services/reporting.py`):

```python
# Kaplan domain confounders
kaplan_domain = [
    'occupant density', 'crowding',
    'personal control', 'autonomy',
    'work type', 'knowledge work', 'routine work',
    'habituation', 'prior exposure', 'adaptation',
    'workstation', 'workspace configuration',
    'job demands', 'job control', 'job type'
]

# Pearl implicit confounder control patterns
implicit_control = [
    'adjusted model', 'full model', 'final model',
    'multivariate', 'multiple regression', 'multilevel',
    'after including covariates', 'Model 2', 'Model 3',
]
```

**Questions for Kaplan & Pearl**:
1. Are these the most important confounders for neuroarchitecture?
2. Should `SES`, `education level`, `cultural background` be included?
3. Is `Model 2`, `Model 3` pattern too simplistic for detecting adjusted models?
4. Missing confounders? (e.g., time of day, season, weather?)

---

## Sprint F2: Bridge & Measurement (Cartwright Items)

### Decision F2.1: CAPACITY Bridge Type

**What I implemented** (`src/services/bridge_warrants.py`):

```python
class BridgeType(Enum):
    MECHANISM = "mechanism"
    FUNCTIONAL = "functional"
    ANALOGICAL = "analogical"
    CONSTITUTIVE = "constitutive"
    CAPACITY = "capacity"  # NEW

DEFAULT_BRIDGE_CONFIDENCE = {
    BridgeType.CONSTITUTIVE: 0.75,  # Reduced from 0.85
    BridgeType.MECHANISM: 0.60,
    BridgeType.CAPACITY: 0.55,      # NEW
    BridgeType.FUNCTIONAL: 0.50,
    BridgeType.ANALOGICAL: 0.35,
}

CAPACITY_KEYWORDS = [
    "has the capacity",
    "capable of",
    "able to",
    "tends to",
    "propensity to",
    "disposition",
    "inherent ability",
    "natural capacity",
    "potential to",
    "capacity for",
]
```

**Questions for Cartwright**:
1. Is P(bridge) = 0.55 for CAPACITY correctly calibrated?
2. Was reducing CONSTITUTIVE from 0.85 to 0.75 appropriate?
3. Are the capacity keywords correct, or too broad?
4. Should "tends to" be a capacity indicator (could be statistical tendency)?
5. How does CAPACITY differ from FUNCTIONAL in practice?

---

### Decision F2.2: Measurement Categories Expanded

**What I implemented** (`src/services/query_response.py`):

```python
# Behavioral vs self-report
behavioral_keywords = ['behavioral', 'performance', 'task', 'accuracy', 'reaction time']

# Objective vs subjective
objective_keywords = ['lux', 'decibels', 'dB', 'PPM', 'ppm', 'CO2', 'temperature',
                     'measured', 'sensor', 'meter', 'dosimeter', 'photometer', 'quantified']
subjective_keywords = ['perceived', 'rated', 'reported', 'felt', 'experienced',
                      'satisfaction', 'preference', 'comfort rating', 'VAS', 'Likert']
```

**Questions for Cartwright**:
1. Is this categorization (behavioral/self-report, objective/subjective) complete?
2. Are there measurement modalities I'm missing? (e.g., observational, ecological momentary assessment?)
3. Should physiological measures be a separate category from objective?
4. Is `Likert` a reliable indicator of subjective measurement?

---

## Sprint F3: Documentation (Naur/Lamport Items)

### Decision F3.1: DESIGN_RATIONALE.md Structure

**What I created** (`docs/DESIGN_RATIONALE.md`):

1. Quinean Commitment: Why Coherentist, Not Foundationalist
2. Three-Tier Classification: Why Not Four Tiers
3. Directional Opposition: Why Not Credence Threshold
4. Pattern Selection: Why These Specific Patterns
5. Bridge Warrant Theory: Evidence Portability
6. Satisficing Principles: Bounded Rationality Throughout
7. Measurement Method Differences
8. Confounder Gap Detection
9. References + Decision Log

**Questions for Naur**:
1. Does this capture the "Theory of the System" adequately?
2. Is the tacit knowledge now sufficiently explicit?
3. Should there be more on the Quinean commitment's practical implications?
4. Is the decision log format appropriate for ongoing theory preservation?

---

### Decision F3.2: INVARIANTS.md Content

**What I created** (`docs/INVARIANTS.md`):

- Belief Invariants (INV-B1 through INV-B9)
- Web of Belief Invariants (INV-W1 through INV-W7)
- Causal Classification Invariants (INV-C1 through INV-C6)
- Bridge Warrant Invariants (INV-BR1 through INV-BR8)
- Query Response Invariants (INV-Q1 through INV-Q5)
- Reporting Invariants (INV-R1 through INV-R3)
- Consistency Model documentation
- List of invariants not yet verified

**Questions for Lamport**:
1. Are the invariants sufficiently formal?
2. Should I use TLA+ notation for any of these?
3. Is the consistency model (snapshot isolation for queries) correctly specified?
4. Which invariants should have runtime enforcement vs test-time verification?

---

## Sprint F4: Frontend (Bates Items)

### Decision F4.1: Vocabulary Expansion Display

**What I implemented** (`frontend/evidence-explorer.html`):

- Panel showing: Original terms → Expanded terms → Matched terms
- Color coding: blue (original), light blue (expanded), green (matched)
- Appears when search is performed
- Shows which expansions actually matched results

**Questions for Bates**:
1. Is this display prominent enough?
2. Should matched terms be shown separately, or highlighted within expanded?
3. Should we show WHY each expansion was added (synonym, broader term, etc.)?
4. Is the legend sufficient for user understanding?

---

### Decision F4.2: Faceted Filtering Controls

**What I implemented**:

- **Source Depth**: Dropdown (Full-text / Abstract / Metadata / All)
- **Causal Tier**: Dropdown (Causal / Suggestive / Associational / All)
- **Credence Range**: Dual sliders (0-100%)
- **Contested Status**: Toggle buttons (All / Yes / No)
- Active filter tags with remove buttons
- Reset all button

**Questions for Bates**:
1. Are these the right facets for evidence exploration?
2. Should filters be AND or OR logic (currently AND)?
3. Is the slider for credence appropriate, or should it be discrete ranges?
4. Should there be a "theoretical framework" facet (ART, SRT, etc.)?
5. Missing facets? (e.g., publication year, study type, sample size?)

---

## API Router Fixes (ChatGPT Review Items)

### Decision: Centralized Web State

**What I implemented**:

Changed `query.py`, `reports.py`, `ingestion.py` from:
```python
_web: Optional[WebOfBelief] = None
def get_web(): ...
```

To:
```python
from app.routes.web_of_belief import get_web, set_web
```

**Questions for Lamport**:
1. Is shared mutable global state acceptable, or must we use dependency injection?
2. What's the minimal change to achieve proper snapshot semantics?
3. Should queries operate on a copy of the web state?

---

## Summary: Questions Requiring Panel Response

| Expert | Key Questions |
|--------|---------------|
| **Kaplan** | Pattern appropriateness, framework completeness, outcome taxonomy |
| **Cartwright** | CAPACITY calibration, measurement categories, bridge type distinctions |
| **Pearl** | Confounder detection patterns, implicit control recognition |
| **Naur** | Theory preservation adequacy, decision log format |
| **Lamport** | Invariant formality, consistency model, runtime enforcement |
| **Bates** | Facet selection, filter logic, vocabulary display prominence |
| **Simon** | (No new decisions - satisficing principles preserved) |
| **Liskov** | (No new decisions - abstraction boundaries unchanged) |
| **Brooks** | (No new decisions - conceptual integrity maintained) |
| **Parnas** | (No new decisions - module boundaries unchanged) |

---

## Request

Please provide feedback on these implementation decisions. For each decision:

1. **APPROVE** - Implementation is correct
2. **MODIFY** - Suggest specific changes
3. **REJECT** - Fundamental approach is wrong, propose alternative

Include priority (CRITICAL/HIGH/MEDIUM/LOW) for any modifications.
