# CVA-7: Identifiability Experiment Design
**Sprint CVA-7 — Phase C: Empirical Design**

> Three experiment protocols to test whether CVA constraints and valuations
> can be empirically separated (Jordan's identifiability criterion).

---

## Experiment 1: Constraint Manipulation (Within-Subject)

### Research Question
Can Tier 2 constraints be independently manipulated while holding valuations constant?

### Design
- **Factor**: 2×2 (Processing Cost: high/low × Prediction Error: high/low)
- **Holding constant**: Activity frame (RESTING), subject demographics, cultural background
- **N**: 60 participants (power = .80 for medium effect d = 0.5)

### Stimuli
- 32 architectural scenes, parametrically varied on:
  - Edge density → ProcessingCost
  - Familiarity → PredictionError
- Each scene rated on 9 valuation axes + beauty

### Measurement Protocol
| Metric | Instrument | Resolution |
|--------|-----------|-----------|
| Processing Cost | RT + pupillometry | ms + mm dilation |
| Prediction Error | Surprise rating (1-7) + skin conductance | Likert + µS |
| Valuation vector | 9-axis slider (0-100) | Continuous |
| Beauty | 7-point Likert + forced choice | Ordinal |

### Analysis Plan
1. Confirm constraint manipulation checks (ANOVAs on RT, pupil)
2. Test valuation stability (ICC across conditions)
3. Compute constraint→valuation mapping residuals
4. Report identifiability index: I = 1 - R²(constraint→valuation)

### Expected Outcome
- I > 0.4 → Partial identifiability (constraints and valuations not redundant)
- I < 0.2 → Constraints may be proxies for valuations (identifiability problem)

### Pre-Registration
- Hypothesis: I ∈ [0.4, 0.7] for ProcessingCost and PredictionError
- Confirmatory: Two-sided t-test on I against 0.3 threshold
- Exploratory: Whether neurotype modulates identifiability

---

## Experiment 2: Valuation Priming (Between-Subject)

### Research Question
Can valuations be independently primed while constraints remain fixed?

### Design
- **Factor**: 3 priming conditions (Safety, Interest, Restoration)
- **Fixed**: Same 16 scenes shown to all groups
- **N**: 90 participants (30/group)

### Procedure
1. Priming task (5 min): Narrative about safety/exploration/rest
2. Scene evaluation: Rate all 16 scenes on 9 axes + beauty
3. Constraint measurement: RT + pupil for processing cost/prediction error

### Analysis
- If priming shifts valuations without shifting constraints → identifiable
- DV: Mahalanobis distance in 9D valuation space between groups
- Constraint invariance: χ² test on constraint means across groups

### Power Analysis
- Expected effect: η² = 0.06 (medium)
- Required N: 90 total for F(2,87), α = .05, power = .80

---

## Experiment 3: Cross-Context Transfer (Longitudinal)

### Research Question
Do constraint profiles transfer across spatial contexts while valuations remain person-specific?

### Design
- **Contexts**: Office → Museum → Park (within-subject, counterbalanced)
- **Sessions**: 3 sessions, 1 week apart
- **N**: 40 participants

### Predictions (from CVA architecture)
1. **Constraints should shift** across contexts (same person, different scenes)
2. **Valuations should be stable** within-person (same ψ, different x)
3. **Frame-dependent salience** should modulate which constraints matter

### Analysis
- ICC(2,k) for constraints across contexts (expect ICC < 0.5 → context-dependent)
- ICC(2,k) for valuations across contexts (expect ICC > 0.6 → person-stable)
- Identifiability = 1 - correlation(Δconstraint, Δvaluation)

---

## Pre-Registration Summary

| Study | DV | IV | N | Primary Statistic |
|-------|----|----|---|-------------------|
| Exp 1 | Identifiability index I | ProcessingCost × PredictionError | 60 | Two-sided t vs 0.3 |
| Exp 2 | Valuation Mahalanobis distance | Safety/Interest/Restoration prime | 90 | Between-group ANOVA |
| Exp 3 | Within-person ICC | Context (office/museum/park) | 40 | ICC(2,k) > 0.6 |

### Stopping Rule
Bayesian sequential design: BF₁₀ > 6 or BF₁₀ < 1/6

### Ethics
All studies require IRB approval. No deception beyond priming narratives.
Informed consent includes right to withdraw and data deletion.
