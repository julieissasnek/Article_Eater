# Panel P-ECB-R: Expert Responses

**Date**: 2026-02-10
**Panel ID**: P-ECB-R (Epistemic-Causal Bridge Repair)

---

## Susan Haack — Foundherentist Integration

### Response to Q1: How should well-entrenched theoretical beliefs manifest in the causal layer?

*"In 'Evidence and Inquiry' (1993), I argued that foundherentism acknowledges both the coherentist insight that justification is holistic and the foundationalist insight that experience plays a special role. The question here is how this applies to causal inference.*

*The key distinction is between **supportiveness** and **independent security**:*

*1. **Supportiveness**: How well does this belief support others in the web? A theoretical belief like 'Natural environments activate parasympathetic nervous system' is highly supportive—it explains many empirical findings.*

*2. **Independent security**: How well-anchored is this belief in experience? An empirical belief like 'Ulrich 1984 found faster recovery with nature views' has direct experiential grounding.*

*The current Thagard formula (40% connectivity + 30% level + 30% coherence) captures supportiveness but underweights independent security. For causal inference, I recommend:*

**Recommendation H-1**: Structural equations should carry TWO weights:
- **Supportiveness weight**: From entrenchment (the Thagard formula)
- **Security weight**: From directness of experiential grounding

*An equation derived from theoretical beliefs has high supportiveness but low security. It should be used but marked as 'theory-driven, awaiting direct evidence.' An equation derived from empirical beliefs has lower supportiveness but higher security.*

*When these conflict, the causal model should report BOTH interpretations, not force a single answer. This is foundherentism in practice: neither pure theory nor pure observation wins automatically.*

**Recommendation H-2**: The feedback loop should distinguish:
- Revising beliefs due to **incoherence** (coherentist move)
- Revising beliefs due to **new experiential evidence** (foundational move)

*The first is cheap—any belief can be revised. The second is epistemically weightier—empirical beliefs closer to experience should resist revision more.*

**Recommendation H-3**: Contrast classes are part of the **experiential content** of a belief, not just metadata. 'Nature reduces stress compared to urban' has different experiential grounding than 'Nature reduces stress compared to nothing.' Track this in the security weight."*

---

## Judea Pearl — Structural Equations from Beliefs

### Response to Q2: Is this the right relationship between beliefs and equations?

*"The current approach has a fundamental problem: structural equations are approximated with default parameters (β = 0.5). This is not causal inference—it's placeholder arithmetic.*

*In my framework, structural equations represent **interventional relationships**: what happens when we do(X = x)? These must be estimated from data, not assumed.*

*However, I understand the constraint: Article Eater synthesizes literature, not raw data. Given this:*

**Recommendation P-1**: Separate equation **structure** from equation **parameters**:
- Structure (which variables, which edges): Extract from high-credence beliefs
- Parameters (effect sizes): Should come from the papers themselves, if available

*The current design extracts structure correctly (from constraints like EXPLAINS, SUPPORTS) but guesses parameters. If a paper says 'nature exposure reduced stress by 0.4 standard deviations,' that's the β, not 0.5.*

**Recommendation P-2**: Handle conflicting beliefs about the same relationship via **meta-analysis logic**:
- Multiple papers give effect sizes for Nature → Stress
- Aggregate using inverse-variance weighting (you already do this in `web_persistence.py`)
- Report heterogeneity (I² statistic) as part of equation uncertainty

**Recommendation P-3**: Distinguish **associational**, **interventional**, and **counterfactual** claims:
- Observational study: Only justifies associational claim
- RCT: Justifies interventional claim
- Counterfactual: Requires either experiments or strong assumptions

*The causal model should track this. An equation with only observational support should be marked as associational, not causal.*

**Recommendation P-4**: For the feedback loop, use **sensitivity analysis**:
- If the counterfactual depends heavily on a low-credence belief, flag it
- If revising that belief would flip the conclusion, mark it as fragile
- The robustness analysis you have is correct—make sure it feeds back to the web

*On contrasts: I agree with van Fraassen that 'why P rather than Q' matters. In causal terms, this is the **reference level** of an intervention. 'Nature vs. urban' is a different do-operator than 'nature vs. nothing.' The structural equation should encode which reference is being used.*"

---

## Bas van Fraassen — Contrast Class Flow

### Response to Q3: How should contrast classes propagate through counterfactual inference?

*"In 'The Scientific Image' (1980) and later work, I argued that explanation is essentially contrastive. 'Why P?' is incomplete; we need 'Why P rather than Q?'*

*The current bridge has the right machinery—ContrastClass, PopulationContext, ContrastAssessment—but the flow is unclear. Let me specify:*

**Recommendation V-1**: Every belief should carry its contrast class explicitly:
```
Belief: 'Nature exposure reduces stress'
Contrast: 'nature exposure (focal) vs. urban exposure (contrast) in office workers (population)'
```

*If the paper doesn't specify the contrast, infer from methods:*
- RCT with control group → contrast is the control condition
- Observational comparison → contrast is the comparison group
- Single-arm study → contrast is implicit (baseline or population norm)

**Recommendation V-2**: Contrast transfer should follow these rules:

| Source Contrast | Target Query | Transfer Type | Adjustment |
|-----------------|--------------|---------------|------------|
| Nature vs. urban | Nature vs. urban | DIRECT | 1.0 |
| Nature vs. urban | Nature vs. nothing | BASELINE_SHIFT | Estimate urban-to-nothing baseline difference |
| Nature vs. urban | Nature vs. urban (different population) | POPULATION_SHIFT | Check baseline similarity |
| Nature vs. urban | Nature vs. virtual nature | MEANING_SHIFT | Cannot transfer—different constructs |

**Recommendation V-3**: When contrast doesn't transfer, DON'T compute the counterfactual. Return:
```python
QuineanCounterfactualResult(
    point_estimate=None,  # Explicitly undefined
    warnings=['Contrast class mismatch: source is X vs Y, query is X vs Z'],
    required_evidence=['Need studies comparing X to Z directly']
)
```

*A computed but meaningless answer is worse than an honest 'I don't know.'*

**Recommendation V-4**: Baselines are population-relative. 'Nature exposure' means different things for:
- Urban Japanese office workers (low baseline nature, high cultural meaning)
- Rural Norwegian farmers (high baseline nature, utilitarian relationship)

*The PopulationContext class you have should be populated with actual data. Currently it's mostly empty.*

**Recommendation V-5**: For the feedback loop, contrast mismatch should trigger **gap identification**:
- 'Query requires X vs. Y comparison, but evidence base only has X vs. Z'
- This is a research gap—feed to VOI search
- The web should record 'attempted query, contrast unavailable'"*

---

## Herbert Simon — Simplification

### Response to Q4: What's the minimal viable integration?

*"Bounded rationality tells us that good-enough solutions found quickly beat optimal solutions found too late. Looking at this 2400-line bridge, I see three layers:*

**Layer 1: Essential** (~300 lines)
- `build_causal_models()`: Extract DAG from web
- `counterfactual()`: Compute intervention effect
- Integration with web: Read beliefs, write updates

**Layer 2: Valuable but complex** (~500 lines)
- Van Fraassen contrast assessment
- Robustness analysis
- Scope checking

**Layer 3: Elaborate scaffolding** (~1600 lines)
- Duplicate class definitions (should import from web_of_belief.py)
- Individual difference profiles (not used)
- Cultural meaning structures (not populated)
- Generalization assessment (overlaps with scope)

**Recommendation S-1**: Start with Layer 1 only. Get it working end-to-end:
1. Pipeline calls bridge
2. Bridge extracts causal model
3. Bridge computes counterfactual
4. Result is returned and logged

**Recommendation S-2**: Delete duplicate classes immediately. The bridge should:
```python
from src.services.web_of_belief import (
    Belief, Credence, EpistemicLevel, BeliefStatus, ConstraintType
)
```

**Recommendation S-3**: Consolidate the two implementations (repo vs. research dir). One source of truth. Pick the repo version, update tests.

**Recommendation S-4**: The IndividualDifferenceProfile system is premature optimization. Cut it entirely. If needed later, add it back.

**Recommendation S-5**: For Layer 2 features, use **feature flags**:
```python
class EpistemicCausalBridge:
    def __init__(self, web, enable_contrast=True, enable_robustness=True):
        self.enable_contrast = enable_contrast
        ...
```

*This lets you run a minimal version in production while developing richer features.*

**Recommendation S-6**: Target <500 lines for the core bridge. If it's longer, you're doing too much."*

---

## Nancy Cartwright — Capacities and Enabling Conditions

### Response to Q5: How should capacities interact with the causal model?

*"In 'Nature's Capacities and Their Measurement' (1989), I argued that causal claims are about **capacities**—stable tendencies that manifest only when enabling conditions are met.*

*'Nature exposure reduces stress' is not a universal law—it's a capacity claim. It manifests when:*
- Exposure is long enough (>30 min per Kaplan)
- Baseline stress is elevated (floor effects otherwise)
- Blocking factors are absent (e.g., noise, threat)

*The current bridge checks enabling conditions (P-EC-R9), which is correct. But the implementation is too permissive:*

```python
def _check_enabling_conditions(self, belief) -> bool:
    # Currently returns True in most cases with a log warning
```

*This should be stricter.*

**Recommendation C-1**: Enabling conditions should **gate** counterfactual computation:
- If query context violates enabling conditions, the capacity doesn't manifest
- Return estimate = 0 (not baseline, literally zero effect) with explanation

**Recommendation C-2**: Track enabling conditions separately from scope:
- **Scope**: 'This finding applies to office workers' (population restriction)
- **Enabling**: 'This effect requires >30 min exposure' (activation threshold)

*Scope says 'who.' Enabling says 'under what conditions.'*

**Recommendation C-3**: For the causal model, structural equations should be **conditional**:
```python
StructuralEquation(
    outcome_var='stress_reduction',
    parent_vars=['nature_exposure'],
    parameters={'beta': 0.4},
    enabling_conditions={
        'minimum_exposure': '>30 minutes',
        'baseline_stress': 'elevated'
    },
    blocking_factors=['ambient_noise', 'perceived_threat']
)
```

*The equation only applies when conditions are met.*

**Recommendation C-4**: For the feedback loop, unmet enabling conditions should trigger:
- NOT 'this belief is wrong'
- BUT 'this capacity didn't manifest in this context'

*This is the difference between a failed prediction (revise the belief) and a blocked capacity (context problem, not belief problem).*

**Recommendation C-5**: Populate the enabling conditions from the literature:
- Kaplan & Kaplan (1989): Attention restoration requires 'soft fascination' (not hard attention demands)
- Ulrich (1991): Stress recovery requires prior stress (floor effect otherwise)
- Specific thresholds: exposure duration, nature 'dosage,' etc.

*This is domain knowledge that should be in the system.*"

---

## Q6: The Feedback Loop (All Panelists)

### Synthesis on how causal results should update the web

**Haack**: *"Distinguish revision-due-to-incoherence from revision-due-to-new-evidence. The first affects any belief; the second respects the experiential grounding of empirical beliefs."*

**Pearl**: *"Use sensitivity analysis. If the counterfactual is fragile (depends on low-credence beliefs), flag those beliefs for review. If it's robust, increase credence of supporting beliefs."*

**van Fraassen**: *"Contrast mismatches should create gaps, not revisions. 'We couldn't answer this query' is informative—feed it to research prioritization."*

**Simon**: *"Start with the simplest feedback: log which beliefs supported the counterfactual. Manual review first, automated updates later."*

**Cartwright**: *"Distinguish capacity-didn't-manifest from belief-is-wrong. Only revise beliefs when the capacity should have manifested but didn't."*

### Integrated Feedback Loop Design

```
Counterfactual Result
        │
        ├── If HIGH robustness & coherence:
        │       ├── Increase credence of supporting beliefs (small δ)
        │       └── Log as 'validated pathway'
        │
        ├── If LOW robustness:
        │       ├── Flag sensitive beliefs for review
        │       └── Don't auto-revise—human review needed
        │
        ├── If COHERENCE violation:
        │       ├── Identify conflicting beliefs
        │       ├── Apply Quine: prefer revising LESS entrenched
        │       └── Log tension for review
        │
        ├── If CONTRAST mismatch:
        │       ├── Don't compute counterfactual
        │       ├── Log gap: 'need evidence for X vs Y'
        │       └── Feed to VOI search
        │
        └── If ENABLING CONDITIONS unmet:
                ├── Return effect = 0 with explanation
                └── Don't revise beliefs—capacity blocked
```

---

## Panel Synthesis: Ordered Repair Steps

Based on all responses, here is the recommended repair sequence:

### Phase 1: Immediate Cleanup (Day 1)

| Step | Action | Owner |
|------|--------|-------|
| 1.1 | Delete duplicate class definitions from bridge | S-2 |
| 1.2 | Import from `web_of_belief.py` instead | S-2 |
| 1.3 | Consolidate to single implementation in repo | S-3 |
| 1.4 | Update test imports to use repo file | S-3 |
| 1.5 | Delete IndividualDifferenceProfile system | S-4 |

### Phase 2: Core Integration (Day 2-3)

| Step | Action | Owner |
|------|--------|-------|
| 2.1 | Implement Layer 1 (essential) only | S-1 |
| 2.2 | Wire bridge into `pipeline.py` | S-1 |
| 2.3 | Separate equation structure from parameters | P-1 |
| 2.4 | Track associational vs. interventional vs. counterfactual | P-3 |
| 2.5 | Make contrast class explicit on every belief | V-1 |

### Phase 3: Enabling Conditions (Day 4)

| Step | Action | Owner |
|------|--------|-------|
| 3.1 | Tighten enabling condition checking | C-1 |
| 3.2 | Add conditional equations | C-3 |
| 3.3 | Populate domain enabling conditions (Kaplan, Ulrich) | C-5 |

### Phase 4: Feedback Loop (Day 5)

| Step | Action | Owner |
|------|--------|-------|
| 4.1 | Implement fragility flagging | P-4 |
| 4.2 | Implement coherence violation → tension detection | Quine |
| 4.3 | Implement contrast mismatch → gap identification | V-5 |
| 4.4 | Route gaps to VOI search | V-5 |

### Phase 5: Van Fraassen Full Integration (Day 6-7)

| Step | Action | Owner |
|------|--------|-------|
| 5.1 | Implement contrast transfer rules | V-2 |
| 5.2 | Return undefined for non-transferable contrasts | V-3 |
| 5.3 | Populate PopulationContext with real data | V-4 |

### Phase 6: Foundherentist Refinement (Day 8)

| Step | Action | Owner |
|------|--------|-------|
| 6.1 | Add security weight alongside supportiveness | H-1 |
| 6.2 | Distinguish coherentist vs. foundational revisions | H-2 |
| 6.3 | Include contrast class in security weight | H-3 |

---

## Target State After Repair

```
src/services/epistemic_causal_bridge.py  (~500 lines, down from 2400)
├── EpistemicCausalBridge(web)
│   ├── build_causal_models() → MultiTheoryModel
│   ├── counterfactual() → QuineanCounterfactualResult
│   └── update_web_from_result() → List[BeliefChange]  # NEW: feedback loop
├── MultiTheoryModel
├── TheoryRelativeModel
├── StructuralEquation (with enabling_conditions)
├── CounterfactualQuery
└── QuineanCounterfactualResult (with gap_identification)  # NEW

Deleted:
- Duplicate Belief, Credence, EpistemicLevel, BeliefStatus, ConstraintType
- IndividualDifferenceProfile, IndividualDifferenceFactor
- CulturalMeaning (until actually used)
- 1600+ lines of unused scaffolding
```

---

## Panel Verdict

| Panelist | Summary Recommendation |
|----------|----------------------|
| **Haack** | Track supportiveness AND security; contrast is experiential content |
| **Pearl** | Separate structure from parameters; use meta-analysis for aggregation; track causal level |
| **van Fraassen** | Make contrast explicit; don't compute if contrast doesn't transfer; route gaps to VOI |
| **Simon** | Ruthless simplification; 500 lines not 2400; delete unused scaffolding |
| **Cartwright** | Enabling conditions gate computation; capacities don't manifest without conditions |

**Unanimous**: The feedback loop is essential. Causal results must update the web.

---

*Panel consultation complete. Ready for synthesis and plan documentation.*
