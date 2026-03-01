# Expert Panel 2 Summary: EMPIRICAL_ASSOCIATION Warrant Strength

**Date**: 2026-02-27 (evening follow-up to Panel 1)
**Panelists**: Wolfgang Spohn, Judea Pearl, Susan Haack, James Woodward, Clark Glymour, Larry Laudan
**Full Transcript**: `docs/EXPERT_PANEL_2_EMPIRICAL_ASSOCIATION_2026-02-27.md` (4,500 lines)

---

## The Issue

**Panel 1 Finding**: EMPIRICAL_ASSOCIATION d=0.80 (Session 2 decision) is too high because black-box associations (no known mechanism) are MORE vulnerable to confounding and context shifts than mechanistic associations.

**Session 2 Defense** (car mechanic principle): A mechanic with 20 successful repairs (d=0.80) is MORE confident than a theorist who knows only chemistry (d=0.25). Empirical track records ARE transferable.

**The Tension**: Should empirical evidence (even without mechanism) get same d as mechanistic evidence?

---

## Five Critical Questions

### Q1: EMPIRICAL_ASSOCIATION d-value — 0.80 or lower?

**Panel Verdict**: TIERED d-values (0.55–0.80) based on replication profile.

| Replication Profile | d-value | Basis |
|---|---|---|
| 1 study only | 0.55 | High artifact risk |
| 2–3 studies, same population | 0.60 | Limited generality |
| 2–3 studies, diverse populations | 0.70 | Decent invariance |
| 5–10 studies, diverse populations | 0.75 | Strong invariance |
| 10+ studies, very diverse | 0.80 | Robust empirical evidence |
| + Partial mechanism | +0.05–0.10 | Mechanism explains invariance |

**Rationale**:
- **Spohn** (calibration): Historical review — black-box associations reverse ~40% when hidden confounders revealed
- **Woodward** (invariance): Replication DIVERSITY signals robustness; same-context replication is weaker
- **Pearl** (transportability): Known mediator pathways make associations diagnosable → higher d
- **Haack** (coherence): Mechanism fills gaps, raising confidence through integration
- **Glymour** (discovery): Empiricists with informal causal models outperform pure black-box
- **Laudan** (problem-solving): Empirical track records merit credit, but transfer risk should be δ's job

**Car mechanic principle preserved**: A mechanic with 20 repairs across 20 garages (diverse!) gets d=0.80 via EMPIRICAL_ASSOCIATION. Same mechanic, 20 repairs in one garage → d=0.65.

---

### Q2: Avoid penalizing empirical evidence vs theory?

**Answer**: YES, easily. Even at d=0.60–0.70, EMPIRICAL_ASSOCIATION >> THEORY_DERIVED (d=0.25).

Hierarchy is preserved:
- CONSTITUTIVE: d=0.95
- MECHANISM: d=0.80
- EMPIRICAL_ASSOCIATION [diverse replications]: d=0.75–0.80
- EMPIRICAL_ASSOCIATION [limited replication]: d=0.60–0.65
- THEORY_DERIVED: d=0.25

Empiricists are never penalized below theorists.

---

### Q3: Should replication DIVERSITY matter (not just count)?

**Answer**: YES — UNANIMOUSLY.

- 10 replications in same U.S. hospital network → d=0.65
- 3 replications across three countries, healthcare systems, demographics → d=0.75–0.80

Replication across DIFFERENT unmeasured confounder structures is strongest evidence of invariance.

**Implementation**: Edge metadata records (population_1, population_2, ...). π uses diversity score to determine appropriate d within EMPIRICAL_ASSOCIATION range.

---

### Q4: Serial chains — product rule or geometric mean?

**Answer**: PRODUCT RULE (d_eff = ∏ d_i).

**Rationale**:
- Each step is independent hypothesis
- Conjunction probability = product of probabilities
- Historically accurate — long chains DO fail in new contexts
- Epistemically healthy — forces honesty about compound uncertainty

**Implementation enhancement**:
- Report component d-values alongside d_eff
- Identify BOTTLENECK (weakest step)
- Flag chains >4 links as HIGH RISK
- Allow partial-chain queries

Example: 4-link chain with all d=0.80:
- d_eff = 0.95 · 0.80 · 0.80 · 0.80 = **0.49** (not 0.80!)
- This is CORRECT — multiple failure points compound

---

### Q5: Should d vary WITHIN type based on replication count?

**Answer**: YES — use metadata to vary d within EMPIRICAL_ASSOCIATION range.

**Implementation** (Option A — preferred):
- d at TYPE level but contextual within range
- Edge carries metadata: (replication_count, population_diversity_score, mechanism_detail_level, publication_bias_flag)
- π uses metadata to select appropriate d ∈ [0.55, 0.80]
- ω captures other quality factors

Example:
```
Edge: Temperature → Ice Cream Sales
τ = EMPIRICAL_ASSOCIATION
Populations: [USA, Canada, Australia, France, Japan] (5)
Replications: 12 studies
Mechanism: 40% (customer comfort, truck operation, foot traffic)
d = 0.75 (diverse 5+ populations, strong replication)
ω = 0.80 (well-designed studies)
```

---

## Final Verdicts

### DECISION 1: EMPIRICAL_ASSOCIATION d-values

**d varies within type**: 0.55–0.80 depending on replication profile, population diversity, and mechanism understanding.

| Scenario | d-value |
|---|---|
| Black-box, 1 study | 0.55 |
| Black-box, replicated in same population only | 0.60 |
| Black-box, replicated across diverse populations | 0.70 |
| With rough mechanism, diverse replication | 0.75–0.80 |

---

### DECISION 2: Serial Chain Aggregation

**Use PRODUCT RULE**: d_eff = ∏ d_i

Report component d-values, identify bottleneck, flag long chains as HIGH RISK.

---

### DECISION 3: Replication-Dependent d

**Encode replication metadata** (count, diversity, mechanism detail) in EN edges. Allow d to vary within EMPIRICAL_ASSOCIATION type based on metadata. Keep d/ω distinction (d = TYPE property for transfer reliability; ω = EDGE property for evidence quality).

---

### DECISION 4: Population Transfer Factor δ

**δ must do heavy work** for cross-context transfer. When d is lowered for black-box associations:
- Use δ to EXPLICITLY penalize transfer to different contexts
- Example: d=0.70 · δ=0.40 for radically different population = 0.28 (back to theory-level)
- This is CORRECT — if mechanism is unknown, transferring far is scary

---

### DECISION 5: Mechanism Metadata

**Add MECHANISM field to EMPIRICAL_ASSOCIATION**:
- `EMPIRICAL_ASSOCIATION [mechanism: 30%]` — rough causal theory exists
- `EMPIRICAL_ASSOCIATION [mechanism: 0%]` — pure black-box

Allows system to distinguish mechanic with mental models (d=0.75–0.80) from mechanic with rote procedures (d=0.60).

---

## Additional Recommendations

### 1. Transparency on Long Chains

Flag chains >4 links as HIGH RISK in system output:
- Report compound probability
- Offer decomposition: "Which steps do you trust?"
- Show partial chains

**Example**: Fractal → wellbeing chain:
- Partial chain (observable mechanisms): P(wellbeing) = 0.45
- Full chain (with theory): P(wellbeing) = 0.72
- Flag: "Theory-dependent parts involve prediction error (unobservable)"

### 2. Research Prioritization Signal

Tiered d-values create natural research agenda:
- d=0.60 association → "Needs replication in [list of populations]"
- mechanism=0% association → "Needs mechanistic grounding"
- Long chain → "Needs bottleneck resolution"

### 3. Distinction: Rough Mechanism vs. Pure Black-Box

Don't treat all empirical associations equally:
- Mechanic with mental models of carburetors ≠ pure statistical correlation
- Add mechanism understanding as explicit metadata
- Allow different d values accordingly

### 4. Dual-BN Diagnostic Continues

Keep running BN twice:
- **Full projection**: All warrant types including THEORY_DERIVED
- **Empirical floor**: Only empirically grounded types

Allows decision-makers to see theory-independent predictions vs. theory-dependent ones.

---

## Panelist Consensus

| Panelist | Position |
|---|---|
| **Spohn** | Tiered d (0.55–0.80) — calibration correct. Product rule for chains. Vary within type. |
| **Pearl** | d=0.60–0.70 for pure black-box; d=0.80 for partial mechanism. Watch confounding structures. Metadata essential. |
| **Haack** | Spectrum d=0.65–0.75 as mechanism fills in. Keep d/ω distinction. Product rule with component reporting. |
| **Woodward** | d varies by replication DIVERSITY. Conditional on diversity, allow variation. Product rule correct. |
| **Glymour** | d=0.60 pure black-box; d=0.80 for empiricists with informal models. Granular metadata needed. |
| **Laudan** | Tiered by replication strength. Use δ for transfer risk. Keep d constant, vary ω. |

**UNANIMOUS** on all five questions (within implementation nuances).

---

## Next Steps

1. **Code integration**: Update `bridge_warrants.py` to support EMPIRICAL_ASSOCIATION d ∈ [0.55, 0.80]
2. **Schema update**: Add metadata fields (replication_count, population_diversity, mechanism_detail, publication_bias_flag) to EN edge specification
3. **Projection function**: Update π to use metadata-informed d values
4. **Testing**: Create worked examples showing tiered d in operation
5. **Documentation**: Update Master Document (SPRINT-8) with new tiers and rationale

---

**Panel 2 Conclusion**: The EMPIRICAL_ASSOCIATION tiering resolves the tension between car mechanic principle (empirical confidence) and Woodward invariance (context vulnerability). Empiricists are credited for track records. Mechanism understanding is incentivized without penalizing the non-mechanistic. System honestly reports uncertainty about transferability via δ.

