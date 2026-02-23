# Panel Review: Epistemic Tier 2 — Sprints 4 + 4b

**Date**: Friday, February 14, 2026
**Reviewer**: Claude Opus 4.5 (implementation agent)
**Purpose**: Expert panel consultation on extraction pipeline and method registry decisions

---

## Executive Summary

Sprints 4 (Extraction Pipeline Extensions) and 4b (Method Registry + Task-Ecological Validity) are complete. The following decisions require panel review before proceeding to Sprint 5 (Integration Testing):

| Category | Decisions | Primary Concern |
|----------|-----------|-----------------|
| **Theory Extraction** | D4.1, D4.2 | How to detect and weight argumentative structure? |
| **Pathway Classification** | D4.4, D4.5 | How to classify effect pathways and PE subtypes? |
| **Task Ecology Weights** | D4b.1, D4b.2 | How to weight task authenticity components? |
| **Construct Validity Maps** | D4b.3 | How accurate are cross-validated instrument scores? |
| **Auto-Challenge Thresholds** | D4b.4, D4b.5 | When should methodological challenges trigger? |
| **Claim Type Bifurcation** | D4b.6 | How to classify and link evaluative vs. functional claims? |

---

## Panel Composition

| Panelist | Expertise | Relevant Decisions |
|----------|-----------|-------------------|
| **Haack** | Foundherentism, coherence | D4b.1 (task weights), D4b.3 (validity maps) |
| **Pollock** | Defeasible reasoning, defeat | D4.1 (argumentative), D4b.4 (auto-challenges) |
| **Longino** | Social epistemology | D4b.3 (construct validity), D4b.6 (generalizability) |
| **Cartwright** | Causal inference, evidence | D4b.4 (channel requirements), D4b.5 (temporal) |
| **Pearl** | Structural equations, BN | D4.4 (pathway effects), D4b.6 (warrant weight) |
| **Kaplan** | Environmental psychology | D4b.2 (task authenticity), D4b.3 (method profiles) |

---

## PART I: Sprint 4 — Extraction Pipeline Extensions

### D4.1: Argumentative Structure Extraction via Weighted Regex

**Decision**: Use weighted regex patterns to detect theory support/challenge language, with weights from 0.5-1.0.

**Implementation**:
```python
THEORY_SUPPORT_PATTERNS = [
    (r"consistent with (?:the )?([a-z]+(?:'s)? (?:\w+ )*(?:theory|hypothesis|model))", 1.0),
    (r"supports? (?:the )?([a-z]+(?:'s)? (?:\w+ )*(?:theory|hypothesis|model))", 1.0),
    (r"aligns? with (?:the )?([a-z]+(?:'s)? (?:\w+ )*(?:theory|framework|model))", 0.7),
]
```

**Rationale**:
- Regex is fast, interpretable, and incrementally improvable
- Weight tiers: strong support (1.0), moderate (0.7), weak (0.5)
- Multi-word theory names captured via `(?:\w+ )*` pattern

**Risk**: Medium — may miss novel phrasings or non-standard theory names

**Questions for Panel**:
1. **Pollock**: Are these weights appropriate for defeat reasoning? Should "challenges" patterns have higher weights than "supports"?
2. **Haack**: Should we distinguish between "coherent with" (weaker) and "confirms" (stronger)?

---

### D4.2: Replication Type Classification

**Decision**: Priority hierarchy: meta_analysis > direct_replication > conceptual_replication > original

**Rationale**:
- Meta-analyses aggregate evidence (highest epistemic weight)
- Direct replications test exact protocol (strong confirmation)
- Conceptual replications test boundary conditions (moderate)
- Original studies are default (baseline)

**Risk**: Low — classification is additive metadata

**Questions for Panel**:
1. **Cartwright**: Does this hierarchy align with evidence-based medicine principles?

---

### D4.3: Adversarial Scrutiny Detection

**Decision**: Flag as adversarial-scrutiny-survived when ANY of these indicators present:
- Multi-lab, independent lab, registered report
- Different theoretical tradition, competing hypothesis
- Critics, skeptics testing the claim

**Implementation**:
```python
ADVERSARIAL_INDICATORS = [
    r"independent lab", r"multi-lab", r"competing hypothesis",
    r"rival theory", r"registered report", r"adversarial collaboration"
]
```

**Rationale**: Single indicator sufficient — conservative threshold

**Risk**: Medium — may over-detect (false positives)

**Questions for Panel**:
1. **Longino**: Should we require multiple indicators for stronger adversarial classification?

---

### D4.4: Three-Pathway Classification via Keyword Matching

**Decision**: Classify claims as SUBPERSONAL, PERSONAL_EPISTEMIC, or MIXED based on keyword presence.

**Implementation**:
- EPISTEMIC_KEYWORDS: interpretation, comprehension, wayfinding, expectation, etc. (35+ terms)
- SUBPERSONAL_KEYWORDS: thermal, circadian, cortisol, autonomic, etc. (45+ terms)
- Default: MIXED when no clear indicators

**Decision Logic**:
```python
if epistemic_count > 0 and subpersonal_count > 0:
    pathway = "mixed"
elif epistemic_count > 0:
    pathway = "personal_epistemic"
elif subpersonal_count > 0:
    pathway = "subpersonal"
else:
    pathway = "mixed"  # Conservative default
```

**Risk**: Low — conservative default handles uncertainty

**Questions for Panel**:
1. **Pearl**: Does this classification affect causal structure appropriately? Should pathway type influence edge weight?

---

### D4.5: PE Subtype Classification Requires PE Indicator

**Decision**: Only classify PE subtype (navigational, functional, social) when explicit PE indicators present.

**PE Indicators Required**:
- prediction error, mismatch, violation, expectation, surprise, anticipation

**Rationale**: Prevents false positive PE classification on non-PE claims

**Risk**: Low — conservative approach, may under-detect

---

## PART II: Sprint 4b — Method Registry + Task-Ecological Validity

### D4b.1: Task-Ecological Validity Weights

**Decision**: Weight five components as:

| Component | Weight | Rationale |
|-----------|--------|-----------|
| Task authenticity | 0.30 | Most directly captures passive observer fallacy |
| State characterization | 0.20 | Critical moderator but often unmeasured |
| Attentional ecology | 0.20 | Distinguishes spectator from goal-directed |
| Temporal ecology | 0.15 | Duration matters but less than task type |
| Social ecology | 0.15 | Context matters but often acceptable to simplify |

**Implementation**: `DEFAULT_TASK_ECOLOGY_WEIGHTS` in task_ecology.py

**Alternatives Considered**:
- Equal weights (0.20 each): Ignores theoretical importance of task authenticity
- Higher task weight (0.40): May overshadow other legitimate concerns

**Risk**: Medium — directly affects which studies are flagged as low ecological validity

**Questions for Panel**:
1. **Kaplan**: As author of ART, does 0.30 for task_authenticity appropriately capture the passive observer concern?
2. **Haack**: Should state_characterization be weighted higher (0.25) given its epistemic importance?

---

### D4b.2: Task Authenticity Score Hierarchy

**Decision**: Score task types on 0.2-1.0 scale:

| TaskClass | Score | Examples |
|-----------|-------|----------|
| EXPLICIT_EVALUATION | 0.2 | Rate images, judge aesthetics |
| LAB_COGNITIVE_TASK | 0.4 | Stroop test, digit span |
| SIMULATED_ECOLOGICAL | 0.6 | VR wayfinding, TSST stressor |
| REAL_TASK_CONTROLLED | 0.8 | Actual work in real building |
| NATURAL_BEHAVIOR | 1.0 | POE, ESM, longitudinal |

**Rationale**:
- 0.2 floor prevents zero scores
- 0.2 increments provide clear hierarchy
- TSST (simulated stressor) scores 0.6 — ecological task even if lab setting

**Risk**: Medium — scoring affects claim validity calculations

**Questions for Panel**:
1. **Kaplan**: Is 0.2 appropriate for explicit evaluation, or does this undervalue aesthetic judgment research?
2. **Cartwright**: Should SIMULATED_ECOLOGICAL (0.6) be higher when task matches real-world task (e.g., TSST as genuine stressor)?

---

### D4b.3: Construct Validity Maps in Seed Entries

**Decision**: Each instrument/modality entry includes `construct_validity_map` with validated construct scores.

**Example — Photographs_2D**:
```python
construct_validity_map={
    "visual_preference": 0.86,    # Stamps (1990) r=0.86 with in-situ
    "aesthetic_judgment": 0.80,
    "wayfinding": 0.20,           # Cannot navigate photos
    "stress_response": 0.30,      # Minimal ecological validity
}
```

**Example — Salivary Cortisol**:
```python
construct_validity_map={
    "hpa_stress_reactivity": 0.95,  # Direct measure
    "subjective_stress": 0.40,       # Poor self-report correlation
    "autonomic_arousal": 0.20,       # Different system
}
```

**Risk**: High — these values directly determine validity scores; calibration is critical

**Questions for Panel**:
1. **Longino**: Should these validity maps be marked as provisional and subject to community revision?
2. **Cartwright**: What level of empirical support should be required before assigning high (>0.8) validity scores?
3. **Kaplan**: Are the photo-to-in-situ validity estimates (0.86 for preference, 0.20 for wayfinding) defensible?

---

### D4b.4: Auto-Challenge Generation Thresholds

**Decision**: Five automatic challenges trigger based on method-claim mismatches:

| Challenge | Trigger Condition |
|-----------|------------------|
| `temporal_misalignment` | Sampling window < instrument onset (e.g., cortisol sampled <20min post-stressor) |
| `construct_presentation_mismatch` | Required sensory channels stripped by modality |
| `vr_confound_uncontrolled` | VR study without cybersickness measurement |
| `single_modality` | Only one measurement instrument used |
| `attention_directed` | Explicit evaluation task for implicit effect claim |

**Implementation**:
```python
# Cortisol temporal constraint
if duration < 20 min for cortisol measurement:
    flag "cortisol_temporal_misalignment"

# Channel requirements
CONSTRUCT_CHANNEL_REQUIREMENTS = {
    "wayfinding": ["locomotion", "spatial_updating", "proprioception"],
    "thermal_comfort": ["thermal"],
}
```

**Risk**: Medium — false positives may flag valid studies; false negatives miss issues

**Questions for Panel**:
1. **Cartwright**: Is 20 minutes the correct threshold for cortisol temporal alignment? Literature suggests 15-20 min onset.
2. **Pollock**: Should auto-challenges have confidence levels rather than binary flags?

---

### D4b.5: Channel Requirements for Constructs

**Decision**: Map constructs to required sensory/motor channels:

| Construct | Required Channels |
|-----------|------------------|
| wayfinding | locomotion, spatial_updating, proprioception |
| spatial_cognition | locomotion, vestibular, proprioception |
| thermal_comfort | thermal |
| material_preference | haptic, high_resolution |
| stress_response | (none — works with visual only) |
| preference | (none — works with visual only) |

**Modality Channels Provided**:
- photographs_2d: visual_central
- vr_hmd_stationary: visual_immersive, head_tracking
- vr_hmd_room_scale: + locomotion, proprioception
- real_building_controlled: all channels

**Risk**: Medium — determines construct_presentation_mismatch challenges

**Questions for Panel**:
1. **Kaplan**: Is it defensible that stress_response requires no specific channels? Some would argue embodied experience matters.

---

### D4b.6: Claim Type Bifurcation and Generalizability Warrant

**Decision**: Two claim types connected by GENERALIZABILITY_WARRANT:

| Type | Pattern | Example |
|------|---------|---------|
| EVALUATIVE_RESPONSE | prefer, like, rate, judge | "People prefer biophilic spaces" |
| FUNCTIONAL_EFFECT | reduce, improve, affect, health | "Nature views reduce stress" |

**Link**: GENERALIZABILITY_WARRANT connects Type A → Type B with default weight 0.5

**Rationale**:
- Type A claims (preference) well-supported by standard paradigm
- Type B claims (functional effect) require ecological evidence
- 0.5 weight reflects that preference does predict function but imperfectly

**Risk**: Medium — 0.5 may be too generous for photos-to-real-world generalization

**Questions for Panel**:
1. **Longino**: Should generalizability warrant weight depend on presentation modality? (e.g., VR→real = 0.6, photos→real = 0.4)
2. **Pearl**: From a causal perspective, is 0.5 appropriate for linking evaluative responses to functional effects?

---

## PART III: Cross-Cutting Concerns

### Concern A: Method Registry as Living Document

The 19 seed entries contain hardcoded values. As the field evolves:
- New instruments emerge
- Validity estimates get updated
- Channel requirements may change

**Question for Panel**: Should the registry support versioning and provenance tracking for validity values?

---

### Concern B: Task Ecology vs. Source Quality Interaction

Task-ecological validity (new in Sprint 4b) and source quality (Sprint 2) both affect claim confidence. Currently computed independently:

```python
composite_validity = (
    0.35 * presentation_validity +
    0.35 * measurement_validity +
    0.30 * task_ecological_validity
)
```

**Question for Panel**: Should task_ecological_validity be part of source_quality (as a 5th component), or remain separate?

---

### Concern C: Construct Validity Map Completeness

Not all construct-modality pairs have empirical validation. Current approach:
- If construct not in validity_map, score defaults to 0.0 (construct_validity lookup)
- If construct matches but score is low, reflects genuine limitation

**Question for Panel**: Should missing construct entries default to 0.5 (unknown) rather than 0.0 (invalid)?

---

## Panel Decisions Requested

Please provide guidance on:

1. **Task Ecology Weights (D4b.1)**: Is 0.30/0.20/0.20/0.15/0.15 well-balanced?

2. **Task Authenticity Scores (D4b.2)**: Is the 0.2-1.0 hierarchy appropriate? Should any levels be adjusted?

3. **Construct Validity Maps (D4b.3)**: Are the hardcoded values defensible? Should any be flagged for revision?

4. **Auto-Challenge Thresholds (D4b.4)**: Are temporal and channel requirements correctly specified?

5. **Generalizability Warrant (D4b.6)**: Is 0.5 appropriate, or should it vary by modality?

6. **Proceed to Sprint 5?**: Any blocking concerns before integration testing?

---

## Appendix: Decision Summary Table

| ID | Decision | Value/Structure | Risk | Primary Panelists |
|----|----------|-----------------|------|-------------------|
| D4.1 | Weighted regex theory extraction | 0.5-1.0 weights | Medium | Pollock, Haack |
| D4.2 | Replication type hierarchy | meta > direct > conceptual | Low | Cartwright |
| D4.3 | Adversarial scrutiny single indicator | Any indicator triggers | Medium | Longino |
| D4.4 | Three-pathway keyword classification | Default: MIXED | Low | Pearl |
| D4.5 | PE indicator required | Explicit indicators only | Low | — |
| D4b.1 | Task ecology weights | 0.30/0.20/0.20/0.15/0.15 | Medium | Kaplan, Haack |
| D4b.2 | Task authenticity scores | 0.2-1.0 hierarchy | Medium | Kaplan, Cartwright |
| D4b.3 | Construct validity maps | 19 entries, 95+ values | High | Longino, Cartwright, Kaplan |
| D4b.4 | Auto-challenge thresholds | 5 challenge types | Medium | Cartwright, Pollock |
| D4b.5 | Channel requirements | 6 constructs mapped | Medium | Kaplan |
| D4b.6 | Generalizability warrant | Type A→B, weight 0.5 | Medium | Longino, Pearl |

---

## Appendix: Sprint 4b Module Structure

```
src/methods/
├── __init__.py           # Package exports
├── registry.py           # MethodEntry, MethodRegistry, enums
├── seed_data.py          # 19 seed entries
├── task_ecology.py       # TaskClass, StateCharacterization, validity scoring
├── method_identifier.py  # identify_methods() function
└── validity_scorer.py    # compute_claim_validity(), auto-challenges
```

---

*Panel review document prepared by Claude Opus 4.5*
*Implementation: Article Eater Epistemic Tier 2*
*Date: 2026-02-14*
