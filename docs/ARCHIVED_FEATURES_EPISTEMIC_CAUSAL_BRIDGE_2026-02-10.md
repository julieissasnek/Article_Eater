# Archived Features: Epistemic-Causal Bridge

**Date**: 2026-02-10
**Archive Reason**: Simplification sprint — stabilize core before adding complexity
**Location**: `quarantine/2026-02-10/epistemic_causal_bridge_features/`
**Status**: ARCHIVED FOR FUTURE REINTEGRATION

---

## Overview

During the P-ECB-R panel consultation, the following features were identified as valuable but premature. They are being archived (not deleted) to enable reintegration once the core epistemic-causal bridge is stable.

Each archived feature includes:
- What it does / was supposed to do
- Why it's valuable
- What's needed before reintegration
- References for implementation

---

## 1. Individual Difference System

### Files Affected
- `IndividualDifferenceProfile` class (lines 352-375)
- `IndividualDifferenceFactor` class (lines 378-406)
- Related methods in `EpistemicCausalBridge`

### What It Does

Enables **personalized counterfactual inference** by adjusting estimates based on individual characteristics.

```python
@dataclass
class IndividualDifferenceProfile:
    """Individual difference profile for personalized inference."""

    # Trait factors
    chronotype: Optional[float] = None  # MEQ score (morningness-eveningness)
    nature_connectedness: Optional[float] = None  # CNS score
    big_five: Dict[str, float] = field(default_factory=dict)

    # State factors
    current_stress: Optional[float] = None
    current_fatigue: Optional[float] = None
    baseline_mood: Optional[float] = None

    # History/context
    typical_nature_exposure: Optional[float] = None  # hours/week
    typical_sunlight_exposure: Optional[float] = None
    urbanicity: Optional[float] = None

    # Cultural
    cultural_background: Optional[str] = None
```

### Why It's Valuable

1. **Precision medicine analogy**: Just as drug effects vary by genotype, environmental effects vary by individual differences
2. **Known moderators in CNfA literature**:
   - Nature connectedness (Mayer & Frantz, 2004) moderates restoration effects
   - Chronotype affects optimal timing of light exposure
   - Urbanicity affects baseline nature exposure (saturation effects)
3. **Design implications**: Personalized recommendations for neuroarchitecture

### Example Use Case

```python
# Query: "Does nature exposure reduce stress for THIS person?"
profile = IndividualDifferenceProfile(
    nature_connectedness=0.8,  # High CNS score
    typical_nature_exposure=2.0,  # 2 hours/week (low)
    urbanicity=0.9  # Very urban
)

result = bridge.counterfactual(
    intervention={'nature_exposure': 30},  # 30 min exposure
    outcome='stress_reduction',
    target_individual=profile
)
# Should show larger effect for high-CNS, low-baseline individuals
```

### What's Needed Before Reintegration

1. **Core bridge must be stable**: Basic counterfactual inference working end-to-end
2. **Moderator data**: Literature review to populate effect modifiers:
   - Nature connectedness × restoration effect
   - Chronotype × optimal lighting timing
   - Urbanicity × baseline saturation
3. **Validation**: Compare personalized predictions to actual individual data
4. **UI**: Way to input individual profiles (CNS questionnaire, etc.)

### Key References

- Mayer, F.S., & Frantz, C.M. (2004). The connectedness to nature scale. *Environment and Behavior*.
- Nisbet, E.K., Zelenski, J.M., & Murphy, S.A. (2009). The nature relatedness scale. *Environment and Behavior*.
- Roenneberg, T., et al. (2003). Life between clocks: Daily temporal patterns of human chronotypes. *Journal of Biological Rhythms*.

### Future TODO

| ID | Task | Priority | Dependencies |
|----|------|----------|--------------|
| IND-1 | Literature review: individual difference moderators in CNfA | P2 | Core bridge stable |
| IND-2 | Populate IndividualDifferenceFactor with literature data | P2 | IND-1 |
| IND-3 | Add CNS questionnaire to Streamlit UI | P3 | IND-2 |
| IND-4 | Validate personalized predictions | P3 | IND-3 |

---

## 2. Cultural Meaning System

### Files Affected
- `CulturalMeaning` class (lines 232-238)
- `PopulationContext.cultural_meanings` field
- Related methods in contrast transfer

### What It Does

Tracks how the **meaning of constructs varies across cultures**, affecting contrast class interpretation.

```python
@dataclass
class CulturalMeaning:
    """Cultural meaning of a construct."""
    culture: str
    meaning: str
    associations: List[str]
    valence: str
    behavioral_implications: str
```

### Why It's Valuable

1. **Architecture is culturally situated**:
   - "Nature" means different things in different cultures
   - Japanese "forest bathing" (shinrin-yoku) has specific cultural meanings
   - Western biophilia discourse differs from indigenous land relationships

2. **Van Fraassen implication**: Contrast class transfer fails when meaning shifts
   - "Nature exposure" in urban Tokyo ≠ "nature exposure" in rural Norway
   - Same intervention, different constructs

3. **Design validity**: Neuroarchitecture recommendations must be culturally appropriate

### Example Use Case

```python
# Query: Does forest viewing reduce stress in Japanese office workers?

japanese_meaning = CulturalMeaning(
    culture='Japanese',
    meaning='shinrin-yoku (forest bathing) - contemplative practice',
    associations=['mindfulness', 'tradition', 'health practice'],
    valence='very positive',
    behavioral_implications='dedicated time, specific practices'
)

western_meaning = CulturalMeaning(
    culture='Western (US)',
    meaning='exposure to trees - passive environmental factor',
    associations=['recreation', 'exercise', 'scenery'],
    valence='positive',
    behavioral_implications='incidental, no specific practice'
)

# These are NOT the same construct
# Cannot directly transfer effect sizes
```

### What's Needed Before Reintegration

1. **Core contrast class system working**: Basic van Fraassen flow operational
2. **Cultural meaning database**: Systematic documentation of:
   - How "nature" is conceptualized across cultures
   - Cultural associations with architectural elements (light, space, materials)
   - Regional differences in baseline environments
3. **Expert consultation**: Cultural psychology / anthropology input
4. **Meaning similarity metric**: Algorithm to assess construct equivalence

### Key References

- Kellert, S.R., & Wilson, E.O. (Eds.). (1993). *The Biophilia Hypothesis*. (Chapter on cross-cultural perspectives)
- Park, B.J., et al. (2010). The physiological effects of Shinrin-yoku. *Environmental Health and Preventive Medicine*.
- Joye, Y., & De Block, A. (2011). 'Nature and I are Two': A critical examination of the biophilia hypothesis. *Environmental Values*.
- Indigenous perspectives on land relationships (various sources)

### Future TODO

| ID | Task | Priority | Dependencies |
|----|------|----------|--------------|
| CULT-1 | Literature review: cultural variation in nature concepts | P2 | Core contrast working |
| CULT-2 | Design cultural meaning schema with anthropology input | P2 | CULT-1 |
| CULT-3 | Populate for major cultural contexts (Western, East Asian, Indigenous) | P3 | CULT-2 |
| CULT-4 | Implement meaning similarity metric | P3 | CULT-3 |
| CULT-5 | Add cultural context to PopulationContext | P3 | CULT-4 |

---

## 3. Argument Attack Analysis

### Files Affected
- `ArgumentAttack` class (lines 413-446)
- `AttackContrastAnalysis` class (lines 449-465)
- `AttackType` enum (lines 84-92)
- `ContrastShiftType` enum (lines 95-102)

### What It Does

Analyzes how **scientific disagreements relate to contrast classes**. Key insight: many apparent contradictions are actually contrast shifts, not refutations.

```python
@dataclass
class ArgumentAttack:
    attack_id: str
    source_paper_id: str
    target_belief_id: str
    attack_type: AttackType  # CONFOUNDER, BOUNDARY_CONDITION, OVERGENERALIZATION, etc.

    # Contrast class analysis
    original_contrast: Optional[ContrastClass] = None
    shifted_contrast: Optional[ContrastClass] = None
    shift_type: ContrastShiftType = ContrastShiftType.PRESERVING

    # Outcome under each contrast
    outcome_under_original: Optional[str] = None
    outcome_under_shifted: Optional[str] = None
```

### Why It's Valuable

1. **Resolves apparent contradictions**:
   - Paper A: "Nature reduces stress" (urban population, vs. office)
   - Paper B: "No effect of nature on stress" (rural population, vs. outdoors)
   - Not a contradiction—different contrast classes

2. **Improves coherence assessment**: Tensions in the web may be false alarms

3. **Literature synthesis**: Systematic review should categorize disagreements by type

### Example Use Case

```python
# Paper B attacks Paper A's finding

attack = ArgumentAttack(
    attack_id='attack_001',
    source_paper_id='paper_b_2020',
    target_belief_id='belief:nature_reduces_stress',
    attack_type=AttackType.BOUNDARY_CONDITION,
    original_contrast=ContrastClass(
        focal=ConditionSpec('nature_exposure', 'park_view', 'View of park'),
        contrasts=[ConditionSpec('nature_exposure', 'urban_view', 'View of buildings')],
        population_context=PopulationContext(population_id='urban_office_workers')
    ),
    shifted_contrast=ContrastClass(
        focal=ConditionSpec('nature_exposure', 'outdoor_nature', 'Time outdoors'),
        contrasts=[ConditionSpec('nature_exposure', 'outdoor_urban', 'Time outdoors in city')],
        population_context=PopulationContext(population_id='rural_residents')
    ),
    shift_type=ContrastShiftType.POPULATION_SHIFT
)

# Analysis: Not a refutation—boundary condition identified
# Both papers may be correct within their contrast classes
```

### What's Needed Before Reintegration

1. **Core contrast system working**: ContrastClass extraction and comparison
2. **Attack detection**: NLP to identify when papers cite and critique each other
3. **Shift classification**: Rules or ML to categorize shift type
4. **Integration with coherence**: Feed attack analysis into web tension detection

### Key References

- Ioannidis, J.P.A. (2005). Contradicted and initially stronger effects in highly cited clinical research. *JAMA*.
- Walton, D. (2008). *Informal Logic: A Pragmatic Approach*. (Attack types)
- Van Fraassen, B.C. (1980). *The Scientific Image*. (Contrast and explanation)

### Future TODO

| ID | Task | Priority | Dependencies |
|----|------|----------|--------------|
| ATK-1 | Integrate attack analysis with coherence violation detection | P2 | Core contrast working |
| ATK-2 | Add attack detection to claim extraction pipeline | P3 | ATK-1 |
| ATK-3 | Train classifier for shift type identification | P3 | ATK-2 |
| ATK-4 | UI for reviewing detected attacks | P3 | ATK-3 |

---

## 4. Generalization Assessment (Elaborate Version)

### Files Affected
- `GeneralizationAssessment` class (lines 811-850)
- Related helper methods

### What It Does

Full-featured assessment of whether a finding generalizes to a new context, including individual adjustment.

```python
@dataclass
class GeneralizationAssessment:
    belief_id: str
    source_context: PopulationContext
    target_context: PopulationContext
    target_individual: Optional[IndividualDifferenceProfile]

    source_contrast: ContrastClass
    target_contrast: ContrastClass

    generalization_type: str
    adjustment_factor: float

    original_estimate: float
    generalized_estimate: float
    generalization_uncertainty: float

    warnings: List[str]
    recommendations: List[str]
```

### Why It's Valuable

1. **Explicit uncertainty about transfer**: Generalizing from lab to field, from one population to another
2. **Practitioner-facing**: Designers need to know "will this work for MY project?"
3. **Combines contrast + scope + individual**: Full assessment

### What's Needed Before Reintegration

1. **Simpler scope assessment working**: The current `_assess_scope()` method
2. **PopulationContext populated**: Real baseline data
3. **Individual difference system**: The archived feature above
4. **Adjustment algorithms**: How to compute generalization penalties

### Overlap Note

This overlaps with the simpler `ScopeAssessment` class that is being kept. The elaborate version should be reintegrated when the simpler version is proven.

### Future TODO

| ID | Task | Priority | Dependencies |
|----|------|----------|--------------|
| GEN-1 | Validate simpler ScopeAssessment first | P2 | Core bridge stable |
| GEN-2 | Add generalization_type classification | P3 | GEN-1 |
| GEN-3 | Implement adjustment algorithms | P3 | GEN-2, IND-2 |
| GEN-4 | Integrate with individual differences | P3 | GEN-3 |

---

## Summary: Archived Feature Reintegration Roadmap

| Feature | Priority | Earliest Reintegration | Key Dependency |
|---------|----------|----------------------|----------------|
| Argument Attack Analysis | P2 | After core contrast working | Contrast extraction |
| Individual Differences | P2 | After core bridge stable | Moderator literature review |
| Cultural Meanings | P2 | After contrast transfer working | Cultural psychology input |
| Elaborate Generalization | P3 | After simple scope validated | All above |

---

## Archive Location

Files will be moved to:
```
quarantine/2026-02-10/epistemic_causal_bridge_features/
├── individual_differences.py     # IndividualDifferenceProfile, Factor
├── cultural_meaning.py           # CulturalMeaning, related methods
├── argument_attack.py            # ArgumentAttack, AttackContrastAnalysis
├── generalization_elaborate.py   # GeneralizationAssessment (elaborate)
└── README.md                     # This documentation
```

These files preserve the complete implementation for future reintegration.

---

*Document complete. Features documented for archive.*
