# Query Answer Specification V1.0

*Created: 2026-02-16*
*Purpose: Define what a "perfect answer" looks like for architectural design questions*

---

## The Five Levels of Progressive Disclosure

A complete answer system should support progressive disclosure from quick summary to full expert analysis. Each level builds on the previous.

### Level 1: HEADLINE (5 seconds)

**What the user sees**:
```
YES — high ceilings increase creativity (70% confidence)
Mechanism: reduced spatial constraint → broadened cognition
```

**Driven by**:
- Template `higher_order_principle` (compressed)
- Template `overall_maturity` → confidence

**Use case**: Quick yes/no check, Slack message, tooltip

---

### Level 2: CORE ANSWER (30 seconds)

**What the user sees**:
```
QUESTION: When do high ceilings increase creativity and for whom?

ANSWER: High ceilings (>3m) promote abstract, creative cognition through
reduced enclosure-threat and broadened attention.

HOW (Mechanism):
  ceiling_height → enclosure_affect → cognitive_processing_style

WHY (Principle):
  Architecture modulates the brain's processing mode. Spatial proportions
  don't just produce aesthetic responses—they shape how you think.

WHEN (Conditions):
  • Tasks requiring abstract, relational thinking
  • Offices, schools, libraries, studios
  • Effect strongest at transitions (low → high ceiling)
  • Minimum difference ~0.6m to produce detectable effects

FOR WHOM:
  • Creative workers benefit most
  • Detail-oriented workers may benefit from LOW ceilings
  • Effect attenuates with extended exposure
  • Cultural ceiling-height norms modulate expectations

CONFIDENCE: 70% (maturity: supported)
KEY EVIDENCE: Meyers-Levy & Zhu (2007); Vartanian et al. (2013)
```

**Driven by**:
- Template `causal_links` → HOW
- Template `higher_order_principle` → WHY
- Template `scope_conditions` → WHEN
- Template `moderators` → FOR WHOM
- Template `key_references` → evidence

**Use case**: Design decision, team discussion, client brief

---

### Level 3: FULL TEMPLATE DETAILS (2-5 minutes)

**What the user sees**:
- Complete causal chain with all links
- Maturity rating for EACH link (not just overall)
- Complete scope conditions (not just top 3)
- Complete moderators with explanations
- Related templates (via `interactions`)
- Research gaps (weak links, low maturity)
- Caveats and limitations

**Driven by**:
- Full template structure
- `interactions` field → related templates
- Link-level `maturity` and `bridging_quality` → gaps

**Use case**: Design specification, evidence review, literature search

---

### Level 4: ARTICLE-LEVEL EVIDENCE (10+ minutes)

**What the user sees**:
- Specific studies supporting each causal link
- Effect sizes (Cohen's d, r, odds ratios)
- Sample populations (N, demographics, culture)
- Methodological details (design, measures, controls)
- Replication status (replicated, failed, untested)
- Presentation validity (photos vs VR vs real building)
- Measurement validity (self-report vs physiology)

**Driven by**:
- WebOfBelief extracted claims linked to template
- Article metadata (sample size, method, etc.)
- Tier 2b validity ratings

**Use case**: Literature review, grant proposal, expert panel

---

### Level 5: BAYESIAN NETWORK CONFIDENCE (expert)

**What the user sees**:
- Prior probability before this evidence
- Likelihood ratio from each study
- Posterior probability after evidence integration
- Sensitivity analysis (how much would confidence change if X)
- Concentration risk (all evidence from same lab?)
- Temporal decay (oldest evidence from 2007)

**Driven by**:
- BN posterior computation
- Epistemic Tier 2 monitors (concentration, decay, etc.)

**Use case**: Meta-analysis, systematic review, expert testimony

---

## Answer Components in Detail

### HOW (Mechanism)

The causal pathway from environmental feature to outcome.

**Structure**:
```
FROM_ENTITY --[ACTIVITY]--> TO_ENTITY --[ACTIVITY]--> ... --> OUTCOME

Example:
ceiling_height --[modulates]--> enclosure_threat_assessment
enclosure_affect --[modulates]--> cognitive_processing_style
spatial_proportion_transition --[amplifies]--> processing_style_shift_magnitude
```

**Levels bridged**:
- environmental → neural → cognitive → behavioral

**Quality indicators**:
- `bridging_quality`: strong / moderate / weak
- `maturity`: established / supported / preliminary

---

### WHY (Principle)

The higher-order theoretical principle that EXPLAINS the mechanism.

**Sources** (in order of preference):
1. Template `higher_order_principle`
2. T1 framework principle (e.g., Predictive Processing: "PE drives attention and learning")
3. Template `structural_pattern` (if no principle available)

**Good WHY answers**:
- "Architecture modulates the brain's processing mode" (VF3)
- "PE at the optimal level is intrinsically rewarding" (T2)
- "Multi-channel confirmation produces qualitative fluency shift" (L3, MAT4)

**Bad WHY answers**:
- "Because studies show it" (this is WHAT, not WHY)
- "Evolution" (too vague)
- "The brain likes it" (not mechanistic)

---

### WHEN (Scope Conditions)

The conditions under which the mechanism operates.

**Categories**:
1. **Environmental context**: Building types, spaces, activities
2. **Temporal context**: Time of day, duration, transition vs. steady-state
3. **Physical thresholds**: Minimum/maximum values for effect
4. **Combinatorial context**: Interactions with other features

**Example WHEN conditions (VF3)**:
- Applies to buildings where cognitive tasks are performed
- Effect strongest for tasks with variable processing requirements
- Minimum ceiling height difference ~0.6m for detectable effect
- Interacts with spatial function (low ceiling may be positive if matches function)

---

### FOR WHOM (Moderators)

Individual and population differences that change the effect.

**Categories**:
1. **Task/goal moderators**: What the person is trying to do
2. **Individual difference moderators**: Traits, abilities, preferences
3. **Cultural moderators**: Norms, expectations, learned associations
4. **State moderators**: Current arousal, fatigue, mood
5. **Exposure history**: Familiarity, adaptation, sensitization

**Example FOR WHOM moderators (VF3)**:
- Task type: creative tasks benefit; detail-oriented may not
- Cultural expectations: ceiling-height norms vary
- Duration: effect attenuates with extended time
- Other spatial features: lighting, color modulate the response

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER QUERY                              │
│            "When do high ceilings increase creativity?"         │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    QUERY UNDERSTANDING                          │
│  • Extract entities: ceiling_height, creativity                 │
│  • Identify query type: mechanism question                      │
│  • Identify scope: when, for whom                               │
└─────────────────────────────────────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   TEMPLATES     │  │  ARTICLE NET    │  │  BAYESIAN NET   │
│                 │  │                 │  │                 │
│ • VF3 (0.85)    │  │ • Meyers-Levy   │  │ • Prior: 0.50   │
│ • T18 (0.60)    │  │   2007 (N=100)  │  │ • LR: 3.2       │
│ • SC2 (0.45)    │  │ • Vartanian     │  │ • Posterior:    │
│                 │  │   2013 (N=18)   │  │   0.76          │
│ HOW, WHY,       │  │                 │  │                 │
│ WHEN, FOR WHOM  │  │ Effect sizes,   │  │ Confidence      │
│                 │  │ populations,    │  │ calibration     │
│                 │  │ methods         │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ANSWER SYNTHESIS                             │
│                                                                 │
│  HEADLINE: Yes, 70% confidence                                  │
│  HOW: ceiling → enclosure → cognition (from templates)          │
│  WHY: Architecture modulates processing mode (from templates)   │
│  WHEN: Creative tasks, >0.6m difference (from templates)        │
│  FOR WHOM: Creative workers, not detail workers (from templates)│
│  EVIDENCE: 2 studies, N=118, d=0.5-0.8 (from articles)         │
│  CONFIDENCE: 76% posterior (from BN)                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PROGRESSIVE DISCLOSURE                        │
│                                                                 │
│  Level 1: Headline only                                         │
│  Level 2: + HOW, WHY, WHEN, FOR WHOM                           │
│  Level 3: + Full template details, related templates            │
│  Level 4: + Individual article details                          │
│  Level 5: + BN computation details                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Current State vs. Target State

| Component | Current State | Target State |
|-----------|---------------|--------------|
| Template search | ✅ Keyword matching | Semantic embedding |
| HOW extraction | ✅ From causal_links | Same |
| WHY extraction | ✅ From higher_order_principle | Same |
| WHEN extraction | ✅ From scope_conditions | Same |
| FOR WHOM extraction | ✅ From moderators | Same |
| Article grounding | ❌ Not connected | Link templates to extracted claims |
| BN confidence | ❌ Not connected | Pull posteriors from BN |
| Progressive disclosure | ❌ Single level only | 5 levels with drill-down |
| Related templates | ❌ Not traversed | Follow interaction links |

---

## Next Steps

1. **Improve template search**: Replace keyword matching with sentence embeddings
2. **Connect to article network**: Link template claims to extracted article evidence
3. **Connect to BN**: Pull posterior confidence from Bayesian network
4. **Add progressive disclosure**: Implement 5-level response with drill-down
5. **Add related template traversal**: Follow `interactions` to build richer answers
6. **Add gap identification**: Flag where more research is needed
