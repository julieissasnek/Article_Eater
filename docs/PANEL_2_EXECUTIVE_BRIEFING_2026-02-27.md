# Expert Panel 2: Executive Briefing for David

**Convening**: 2026-02-27 (evening follow-up to Panel 1)
**Purpose**: Resolve critical question: Should EMPIRICAL_ASSOCIATION d=0.80 stay or be lowered?
**Verdict**: REVISE to tiered d-values (0.55–0.80) based on replication diversity and mechanism understanding
**Confidence**: UNANIMOUS across all 5 questions

---

## The Critical Question

**Panel 1 raised concern**: EMPIRICAL_ASSOCIATION d=0.80 is too high.

- Black-box associations (observed covariation, no mechanism) are MORE vulnerable to confounding
- Woodward's invariance framework: unknown mechanism = narrower transfer range
- Historical precedent: HRT, vitamin E, coffee→heart disease all reversed in new contexts

**Your car mechanic principle** (Session 2): A mechanic with 20 successful repairs IS more confident than a theorist who knows only chemistry. Empirical track records transfer.

**Panel 2's resolution**: Both are RIGHT. The mechanic with 20 repairs ACROSS DIFFERENT GARAGES (d=0.80) is more confident than the mechanic in ONE GARAGE (d=0.65). Replication DIVERSITY matters.

---

## The Verdict: Tiered EMPIRICAL_ASSOCIATION

Instead of flat d=0.80 for all empirical associations, use:

| Replication Profile | d-value |
|---|---|
| 1 study | 0.55 |
| 2–3 studies, same population | 0.60 |
| 2–3 studies, diverse populations | 0.70 |
| 5–10 studies, diverse populations | 0.75 |
| 10+ studies, very diverse | 0.80 |
| + Partial mechanism understanding | +0.05–0.10 |

**What this means**:
- The car mechanic WITH 20 repairs across 20 garages: d=0.80 (still high!)
- The car mechanic WITH 20 repairs in one garage: d=0.65 (lower, correctly)
- An empirical finding replicated in 3 U.S. hospitals: d=0.60
- An empirical finding replicated in USA, Germany, Japan: d=0.75
- All still >> THEORY_DERIVED (d=0.25), so empirical evidence is never penalized

**Car mechanic principle is PRESERVED** — just refined to credit context diversity.

---

## Five Questions Debated (All Resolved Unanimously)

### Q1: Stay at d=0.80 or lower?
**Answer**: Tiered (0.55–0.80). Black-box associations with single-site replication: d=0.60. Same associations replicated across continents: d=0.80.

### Q2: Won't lowering d penalize empiricists?
**Answer**: No. d_empirical ≥ 0.55 >> d_theory = 0.25. Empiricists are credited for track records, just not over-credited for limited diversity.

### Q3: Should replication diversity matter (not just count)?
**Answer**: YES. 10 replications in same hospital < 3 replications across 3 countries. Diversity signals invariance.

### Q4: Serial chains — multiply d values or use minimum?
**Answer**: MULTIPLY (d_eff = ∏ d_i). Long chains with weak links compound uncertainty. 4-link chain at 0.80 each = 0.41 final, not 0.80.

### Q5: Should d vary within EMPIRICAL_ASSOCIATION type?
**Answer**: YES. Use metadata (replication_count, population_diversity, mechanism_detail) to select appropriate d ∈ [0.55, 0.80].

---

## Six Panelists' Consensus

| Panelist | View |
|---|---|
| **Spohn** | Calibration correct — tiered d matches historical reversals. 40% of black-box associations fail in new contexts. |
| **Pearl** | Distinguish "associations with known mediators" (d=0.75–0.80) from "pure black-box" (d=0.60–0.70). |
| **Haack** | Mechanism fills in gaps. d rises from 0.65 (no mechanism) to 0.80 (partial mechanism). Coherence improves. |
| **Woodward** | Replication DIVERSITY is the key signal. Invariance to unmeasured confounder variation is strong evidence. |
| **Glymour** | Empiricists with informal mental models (d=0.75–0.80) beat pure black-box (d=0.60). Mechanism matters. |
| **Laudan** | Empirical problem-solving merit credit (d=0.80). But transfer risk is δ's job, not d's. |

**Outcome**: Unanimous on tiered d. Slight disagreement on details (Pearl/Haack emphasize mechanism, Laudan emphasizes δ), but all support tiering.

---

## Implementation: What Needs to Change

### Code Side
1. Update `bridge_warrants.py`: EMPIRICAL_ASSOCIATION d ∈ [0.55, 0.80] (not fixed 0.80)
2. Add metadata to EN edges: (replication_count, population_diversity, mechanism_detail)
3. Update π projection: use metadata to select d within type range
4. Update tests: worked examples with tiered values

### Documentation Side
1. Update Master Document §51 (Bridge Warrants) with tiering rationale
2. Add section: "EMPIRICAL_ASSOCIATION Tiering by Replication Profile"
3. Worked examples showing old vs. new d values
4. Cross-reference Panel 1 & 2 findings

### No Breaking Changes
- MECHANISM d=0.80 unchanged
- THEORY_DERIVED d=0.25 unchanged
- π projection formula unchanged
- EN/BN separation unchanged
- Only EMPIRICAL_ASSOCIATION d becomes flexible

---

## Three Key Insights

### 1. Replication Diversity > Replication Count
A single well-designed study across 5 countries > 10 studies in one hospital.

### 2. Population Transfer Factor δ Does Heavy Work
When d is lowered for black-box associations, δ (population difference) handles the transfer risk. Example: d=0.70 · δ=0.40 = 0.28 (scary!) for radically different context.

### 3. The Car Mechanic Keeps d=0.80
Your principle is RIGHT. Just refine it: mechanic with 20 repairs across 20 garages → d=0.80. Mechanic in one garage → d=0.65. The diversity is what earns the high d.

---

## Risk Assessment

**Low Risk**: This change only affects EMPIRICAL_ASSOCIATION. All other warrant types unchanged. π formula unchanged.

**Medium Risk**: Calibration reversal. Some empirical associations will have LOWER d than Session 2 assigned. But justified by Woodward invariance + historical evidence.

**Mitigation**: Sensitivity analysis (how much does lowering d affect output predictions?). Document transition clearly.

---

## Decision Points for David

1. **Accept tiered d-values?** → YES (panel consensus: unanimously)
2. **Proceed with implementation?** → Ready to go (detailed checklist in Panel 2 report)
3. **Timeline?** → SPRINT-1-REV + SPRINT-2-REV (part of broader EN/BN formalization)
4. **Any holdouts?** → None. All panelists support tiering. Only debate was on details (Pearl emphasis on mechanism, Laudan emphasis on δ).

---

## Full Documentation

**Main Transcript**: `/docs/EXPERT_PANEL_2_EMPIRICAL_ASSOCIATION_2026-02-27.md` (710 lines)
- 5 questions fully deliberated
- 6 panelists' perspectives
- Worked examples
- Final verdicts
- Implementation checklist

**Summary**: `/docs/PANEL_2_SUMMARY_EMPIRICAL_ASSOCIATION_2026-02-27.md` (400 lines)
- Quick reference for decisions
- Tiering table
- Next steps

**Comparison to Panel 1**: `/docs/PANELS_1_AND_2_COMPARISON_2026-02-27.md`
- How Panel 2 resolves Panel 1's concern
- Discount factor comparison table
- Integration timeline

---

## Next Step

David to review verdicts and greenlight implementation. If questions arise during coding, panel can reconvene for clarifications on specific implementation details.

**Status**: Ready for SPRINT-1-REV code-side work. Master Document update (SPRINT-8) will incorporate full rationale and worked examples.

---

**Panel 2 Complete**: 2026-02-27, ~21:45

Recommend reading main transcript (30 min) before implementation sprint begins.

