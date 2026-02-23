# QA Agent: Generated Questions from Web/Templates

**Date**: February 16, 2026
**Purpose**: Use actual knowledge base content to derive QA system requirements

---

## Method

Questions generated from templates: VIEW1, SOC2, SC3, T17, L2, T20, COL1/COL2, T58, M1-17, VF1, ART, T15, and mechanism registry content.

---

## Category A: Effect Existence Questions

| # | Question | Source | Required Capability |
|---|----------|--------|---------------------|
| A1 | Does a nature view reduce stress? | VIEW1 | Simple lookup, effect existence |
| A2 | Do curved walls affect preference? | VF1 | Lookup, binary answer |
| A3 | Does open-plan office design affect satisfaction? | SOC2 | Lookup + direction (negative) |
| A4 | Can light affect sleep? | L2 | Lookup, circadian pathway |
| A5 | Does temperature affect cognitive performance? | T20 | Lookup, deviation effects |
| A6 | Do high ceilings affect creativity? | Mechanism registry | Lookup, may need inference |

**Capability required**: Direct template/mechanism lookup, yes/no + direction

---

## Category B: Mechanism/Why Questions

| # | Question | Source | Required Capability |
|---|----------|--------|---------------------|
| B1 | Why do nature views reduce stress? | VIEW1 | Multi-channel explanation (5 pathways) |
| B2 | Why does open-plan reduce satisfaction? | SOC2 | Mechanism: privacy regulation failure |
| B3 | How does light affect circadian rhythms? | L2 | Causal chain: ipRGC → SCN → melatonin/cortisol |
| B4 | Why do people prefer curved over angular spaces? | VF1 | PE explanation: prediction error at vertices |
| B5 | How does prospect-refuge work? | T17 | Evolutionary + threat assessment |
| B6 | Why is speech more disruptive than noise? | T58/T19 | Automatic semantic processing |
| B7 | How does music affect emotion? | M12 | BRECVEMA 8-mechanism model |
| B8 | Why do thresholds in buildings feel significant? | SC3 | Multi-modal PE at transitions |

**Capability required**: Causal chain extraction, mechanism explanation, multiple pathways

---

## Category C: Comparative Questions

| # | Question | Source | Required Capability |
|---|----------|--------|---------------------|
| C1 | Which is more restorative: nature view or plants? | VIEW1 vs mechanism | Channel count comparison |
| C2 | Are natural sounds better than silence? | T58 | Category comparison + masking benefit |
| C3 | Does visual privacy matter more than acoustic privacy? | SOC2 | Mechanism comparison within domain |
| C4 | Which affects arousal more: color saturation or hue? | COL2 | Effect magnitude ordering |
| C5 | Is real nature better than photos of nature? | VIEW1.synthetic_hierarchy | Explicit hierarchy in template |
| C6 | Does morning light matter more than evening light? | L2 | Phase-dependent effects |
| C7 | What's worse: too hot or too cold? | T20 | Asymmetric effects |
| C8 | Is music more like speech or natural sounds? | T58, M1-17 | Cross-domain categorization |

**Capability required**: Effect size comparison, hierarchy extraction, domain bridging

---

## Category D: Dosage/Optimization Questions

| # | Question | Source | Required Capability |
|---|----------|--------|---------------------|
| D1 | How much nature exposure is needed for health benefits? | VIEW1.dose_response | Threshold extraction (120 min/week) |
| D2 | What's the optimal color saturation for a bedroom? | COL2 | Context-dependent goldilocks |
| D3 | How much light do elderly people need? | L2.age_correction | Age-corrected formula |
| D4 | What's the optimal threshold density in a museum? | SC3.goldilocks | PE density goldilocks |
| D5 | How loud should background masking be? | T58 | Parameter extraction (40-50 dBA) |
| D6 | What's the optimal ceiling height? | Mechanism registry | Goldilocks if available |
| D7 | How many privacy mechanisms does an office need? | SOC2 | Count from 5-mechanism model |
| D8 | What CCT is best for morning vs evening? | L2 | Time-dependent parameters |

**Capability required**: Goldilocks extraction, threshold values, context-dependent optimization

---

## Category E: Scope/Boundary Questions

| # | Question | Source | Required Capability |
|---|----------|--------|---------------------|
| E1 | Does prospect-refuge apply to all cultures? | T17.scope | Scope condition extraction |
| E2 | Do circadian light needs change with age? | L2.moderators | Moderator extraction |
| E3 | When does thermal discomfort NOT affect cognition? | T20 | Boundary conditions |
| E4 | Does the promenade effect work on repeat visits? | SC3.scope | Familiarity moderator |
| E5 | Do introverts need more privacy than extroverts? | SOC2.moderators | Individual difference moderator |
| E6 | Does birdsong work the same way in a lab as a park? | T58.scope | Context dependence |
| E7 | At what point does complexity become overwhelming? | Various goldilocks | Upper boundary |
| E8 | Does fractal fluency require natural fractals? | T1, VIEW1 | Scope: natural vs artificial |

**Capability required**: Scope condition extraction, moderator identification, boundary specification

---

## Category F: Interaction Questions

| # | Question | Source | Required Capability |
|---|----------|--------|---------------------|
| F1 | How do nature views interact with daylight? | VIEW1.interactions | Multi-template interaction |
| F2 | Does noise cancel out the benefits of plants? | T58 + plants | Cross-domain interaction |
| F3 | Can good acoustics compensate for bad privacy? | SOC2, T58 | Mechanism independence |
| F4 | Do thermal comfort and visual comfort interact? | T20, various | Cross-modality effects |
| F5 | Does circadian light conflict with visual comfort? | L2, L1 | Same stimulus, different pathways |
| F6 | Can promenade design compensate for poor materials? | SC3, MAT | Additive vs compensatory |
| F7 | Do prospect and refuge need to be in the same space? | T17 | Within-construct configuration |
| F8 | How does music interact with task type? | M1-17 | Task-dependent moderation |

**Capability required**: Cross-template reasoning, interaction detection, compensation logic

---

## Category G: Design/Application Questions

| # | Question | Source | Required Capability |
|---|----------|--------|---------------------|
| G1 | How should I design a restorative hospital room? | VIEW1, L2, SOC2, T20 | Multi-template synthesis for context |
| G2 | What makes an open office less stressful? | SOC2, T58 | Intervention recommendations |
| G3 | How do I design a museum for emotional impact? | SC3 | Compositional technique application |
| G4 | What color should a gym be? | COL2 | Context → arousal → color mapping |
| G5 | How do I light a nursing home? | L2.age_correction | Population-specific design |
| G6 | What view is better than no view? | VIEW1.hierarchy | Minimal intervention |
| G7 | How do I balance privacy and collaboration? | SOC2, SC4 | Trade-off navigation |
| G8 | What makes a building entrance feel significant? | SC3 | Threshold design principles |

**Capability required**: Multi-template synthesis, context mapping, intervention generation

---

## Category H: Theory/Framework Questions

| # | Question | Source | Required Capability |
|---|----------|--------|---------------------|
| H1 | What is predictive processing? | Multiple PP templates | Framework explanation |
| H2 | How does ART explain nature benefits? | T15, VIEW1 | Theory summary |
| H3 | What are the BRECVEMA mechanisms? | M12 | Multi-mechanism enumeration |
| H4 | What's the difference between SRT and ART? | SRT1, T15 | Theory comparison |
| H5 | What does "allostatic load" mean? | T29 | Concept definition |
| H6 | How does embodied cognition apply to architecture? | EC templates | Framework application |
| H7 | What's the evidence quality for prospect-refuge? | T17.maturity | Maturity assessment |
| H8 | Which theories explain the same phenomenon? | Multiple | Shared theory detection |

**Capability required**: Framework extraction, theory comparison, maturity reporting

---

## Category I: Evidence/Confidence Questions

| # | Question | Source | Required Capability |
|---|----------|--------|---------------------|
| I1 | How strong is the evidence for nature views? | VIEW1.key_references | Citation count, maturity |
| I2 | Is the circadian-light link well-established? | L2.maturity | Maturity: established |
| I3 | What's uncertain about color effects? | COL2.maturity | Maturity: supported vs established |
| I4 | Are there any disconfirming studies for prospect-refuge? | T17 | Disconfirming evidence field |
| I5 | Who are the key researchers on privacy? | SOC2.references | Citation extraction |
| I6 | How replicable is the open-plan dissatisfaction finding? | SOC2 | Replication status |
| I7 | What's the effect size for temperature on cognition? | T20 | Effect size if available |
| I8 | Is the 120-minute nature threshold robust? | VIEW1 | Single-study vs meta-analytic |

**Capability required**: Maturity extraction, citation reporting, confidence qualification

---

## Category J: Gap/Research Questions

| # | Question | Source | Required Capability |
|---|----------|--------|---------------------|
| J1 | What's unknown about music in architecture? | M templates | Gap identification |
| J2 | Has anyone compared wood to stone for stress? | Mechanism registry | Direct comparison gap |
| J3 | What would test the 5-channel convergence model? | VIEW1 | Study design suggestion |
| J4 | Why is promenade evidence rated "supported" not "established"? | SC3.maturity | Maturity reason |
| J5 | What population is under-studied for circadian light? | L2 | Scope gap |
| J6 | Are there any contested claims about color? | COL templates | Contestation detection |
| J7 | What's the weakest link in the privacy-stress pathway? | SOC2 | Bridging quality analysis |
| J8 | What mechanisms are "how-possibly" vs "how-actually"? | Various | Maturity distribution |

**Capability required**: Gap detection, maturity analysis, research suggestion

---

## Capability Requirements Summary

| Capability | Questions | Priority |
|------------|-----------|----------|
| **Direct lookup** | A1-A6 | ESSENTIAL |
| **Causal chain extraction** | B1-B8 | ESSENTIAL |
| **Multi-template synthesis** | G1-G8, F1-F8 | HIGH |
| **Goldilocks/parameter extraction** | D1-D8 | HIGH |
| **Comparative reasoning** | C1-C8 | HIGH |
| **Scope/moderator extraction** | E1-E8 | MEDIUM |
| **Framework explanation** | H1-H8 | MEDIUM |
| **Confidence/maturity reporting** | I1-I8 | MEDIUM |
| **Gap detection** | J1-J8 | MEDIUM |
| **Taxonomic expansion** | All categories | HIGH (Amendment 10) |

---

## New Requirements Discovered

### Requirement 1: Multi-Template Synthesis

Questions G1-G8 require combining multiple templates for a single context. Example: "How should I design a restorative hospital room?" requires:
- VIEW1 (nature view)
- L2 (circadian light)
- SOC2 (privacy)
- T20 (thermal)
- T58 (acoustic)

**Spec addition needed**: Context → relevant template retrieval → synthesis

### Requirement 2: Hierarchy/Ordering Extraction

Templates contain explicit hierarchies:
- VIEW1.synthetic_nature_hierarchy (real > video > photo > none)
- COL2.arousal_dimensions (saturation > brightness > hue)
- SOC2.five_mechanisms (visual, acoustic, withdrawal, territorial, convention)

**Spec addition needed**: Hierarchy detection and extraction

### Requirement 3: Parameter Contextualization

Questions like "What color for a gym?" require:
- Identify context (gym = high arousal activity)
- Map to mechanism (COL2.context_arousal_matching)
- Extract appropriate parameter (bright, saturated)

**Spec addition needed**: Context → activity → optimal parameter mapping

### Requirement 4: Age/Population Correction

L2 has explicit age-correction formulas. Other templates may need similar population-specific adjustments.

**Spec addition needed**: Population parameter detection and application

### Requirement 5: Cross-Domain Interaction Detection

Questions F1-F8 require knowing whether effects:
- Add (independent pathways)
- Interfere (competing for same resource)
- Compensate (one can substitute for another)

**Spec addition needed**: Interaction type classification

### Requirement 6: Bridging Quality Reporting

Templates have explicit bridging_quality fields (strong/moderate/weak). Users need to know which links are well-established vs speculative.

**Spec addition needed**: Confidence chain reporting

---

## Recommended Spec Amendments

Based on these 80 questions:

1. **Multi-template synthesis protocol** for design questions
2. **Hierarchy extraction** as standard response component
3. **Context → parameter mapping** for optimization questions
4. **Population adjustment** detection and application
5. **Interaction type classification** (additive/interfering/compensatory)
6. **Confidence chain visualization** for mechanism answers

---

*End of Generated Questions*
