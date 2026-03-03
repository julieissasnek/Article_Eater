# ATLAS Formula Audit: Checklist & Scorecard

**Date**: March 2, 2026
**Format**: Quick-reference checklist for each formula

---

## LEGEND

- ✓ = Present and justified
- ✓/✗ = Partially present
- ✗ = Missing
- **GOOD** = All three criteria met
- **PARTIAL** = 1–2 criteria met
- **NEEDS WORK** = <2 criteria met
- **CRITICAL GAP** = Central to system, completely missing

---

## MAIN FORMULAS: SCORECARD

### 1. ✓✓✓ PROJECTION FORMULA
```
logit(p_target) = d(τ) · ω · δ · logit(p_lab)
p_target = σ(logit(p_target))
```
**Location**: PART_IV, §48.3 (lines 119–127)
**Status**: **GOOD** ✓

| Criterion | Status | Notes |
|-----------|--------|-------|
| **Intuition** | ✓✓ | Excellent: epistemological problem clearly stated (lines 81–95) |
| **Derivation** | ✓/✗ | Why log-odds explained (line 95), but not why multiplicative structure |
| **Provenance** | ✓ | Session 8 Phase 2 (Feb 27, 2026), references Woodward (2003) |

**Action**: Add 1 paragraph: "Why combine d·ω·δ multiplicatively? [Answer: Each factor is independent uncertainty source...]"

---

### 2. ✓/✗ LOGIT FUNCTION
```
logit(p) = ln(p/(1−p))
```
**Location**: PART_IV, §48.2 (lines 97–99)
**Status**: **PARTIAL** ✓/✗

| Criterion | Status | Notes |
|-----------|--------|-------|
| **Intuition** | ✓ | Maps (0,1) → ℝ, logit(0.50) = 0 explained |
| **Derivation** | ✗ | Why ln(·)? Why not probit or other transform? Not explained |
| **Provenance** | ✗ | Not cited; appears as standard formula without source |

**Action**: Add derivation or cite source (e.g., "Following Bayesian convention...")

---

### 3. ✓✓ WARRANT STRENGTH COMPOSITION
```
ω = ω_base × ω_conf × ω_rep × ω_meta
```
**Location**: PART_IV, §48.3B (lines 314–336)
**Status**: **PARTIAL** ✓/✗

| Criterion | Status | Notes |
|-----------|--------|-------|
| **Intuition** | ✓✓ | Five components beautifully explained (lines 255–308) |
| **Derivation** | ✓/✗ | Why multiply? Why not add? Not justified |
| **Provenance** | ✓ | References Mayo (1996, 2018), Stegenga (2018), Panel Revisions S1, S4 |

**Action**: Add paragraph: "Why multiplicative? Each factor scales the prior warrant (Bayesian principle). Additive combination would assume independence; we assume modulation."

---

### 4. ✗✗✗ TRANSFER RELIABILITY VALUES (d)
```
d(CONSTITUTIVE)    = 0.95
d(MECHANISM)       = 0.80
d(EMPIRICAL_ASSOC) = 0.80
d(FUNCTIONAL)      = 0.65
d(CAPACITY)        = 0.55
d(ANALOGICAL)      = 0.40
d(THEORY_DERIVED)  = 0.25
```
**Location**: PART_IV, §48.1 (line 50)
**Status**: **NEEDS WORK** ✗/✗

| Criterion | Status | Notes |
|-----------|--------|-------|
| **Intuition** | ✓ | Rationales for ordering are clear |
| **Derivation** | ✗ | **WHY these specific values?** No empirical or theoretical basis |
| **Provenance** | ✗ | Stated as facts, no panel decision cited |

**Action** (HIGH PRIORITY): Choose ONE:
- [ ] Cite meta-analysis showing replication rates by warrant type
- [ ] Conduct sensitivity analysis: show how predictions change if d ± 10%
- [ ] Reference panel decision document (Decision D-X.Y)

---

### 5. ✓✓ CANONICAL δ VALUES (Population Transfer)
**Location**: PART_IV, §48.3A (lines 137–200)
**Status**: **PARTIAL** ✓/✗

| Criterion | Status | Notes |
|-----------|--------|-------|
| **Intuition** | ✓✓ | Outstanding: heatmap + worked examples (lines 189–209) |
| **Derivation** | ✓/✗ | Decision rules present (lines 168–175), but why start at 0.90? Why minimum 0.30? |
| **Provenance** | ✗ | No source cited; described as "canonical" without attribution |

**Action**: Add sources for:
- [ ] Default starting value δ = 0.90
- [ ] Minimum feasible δ = 0.30
- [ ] Reduction rules ("reduce by 0.10 for cultural difference")

---

### 6. ✓✓ SERIAL COMBINATION RULES
```
ω_eff = ∏ ω_i
d_eff = min(d_i)
logit(p_target) = d_eff · ω_eff · δ_eff · logit(p_lab)
```
**Location**: PART_IV, §48.4 (lines 625–637)
**Status**: **GOOD** ✓

| Criterion | Status | Notes |
|-----------|--------|-------|
| **Intuition** | ✓ | "Multiple uncertain links cascade" — clear (lines 625–627) |
| **Derivation** | ✓/✗ | Why multiply ω but minimize d? Implicit but not explicit |
| **Provenance** | ✓ | Logic is standard (causal chains compound uncertainty) |

**Action**: Add 2–3 sentences explaining why minimum rule for d (type property) but product for ω (quality property).

---

### 7. ✓✓ PARALLEL COMBINATION RULE
```
credence(belief) = σ(Σ d_i · ω_i · δ_i · logit(p_lab_i))
```
**Location**: PART_IV, §48.5 (line 245)
**Status**: **GOOD** ✓

| Criterion | Status | Notes |
|-----------|--------|-------|
| **Intuition** | ✓ | Presented as reflexive application of single-edge formula |
| **Derivation** | ✓ | Logic follows from single-edge derivation |
| **Provenance** | ✗ | Not cited to external source, but derived from prior formula |

**Action**: None required (acceptable as derived formula).

---

### 8. ✓ TEA (THEORY ENTRENCHMENT ASSESSMENT)
```
TEA = 0.30·E_conf + 0.25·P_nov + 0.15·Prec + 0.20·U_uptake + 0.10·Coh
```
**Location**: PART_IV, §48.3C (lines 424–560)
**Status**: **PARTIAL** ✓/✗

| Criterion | Status | Notes |
|-----------|--------|-------|
| **Intuition** | ✓ | Five dimensions well-explained (lines 436–512) |
| **Derivation** | ✓/✗ | Rationale for weights stated (line 512): "empirical confirmation and predictive novelty strongest" — but not fully justified |
| **Provenance** | ✓/✗ | References Decision D-48C.1 (line 512) but document not shown |

**Action**:
- [ ] Show Decision D-48C.1 in full OR cite its content
- [ ] Add sensitivity analysis: how much do theory rankings change if weights = {0.25, 0.25, 0.20, 0.20, 0.10}?

---

### 9. ✓ AESHI (SYSTEM HEALTH INDEX)
```
AESHI = 0.24·Contract + 0.19·Pipeline + 0.24·Web_BN + 0.19·Theory + 0.09·Stability + 0.05·QA_Epistemic
```
**Location**: PART_IV, §53.8 (lines 1822–1925)
**Status**: **PARTIAL** ✓/✗

| Criterion | Status | Notes |
|-----------|--------|-------|
| **Intuition** | ✓ | Six components explained (lines 1873–1912), but overall logic weak |
| **Derivation** | ✗ | Why 0.24 for Contract? Why only 0.05 for QA_Epistemic? Not justified |
| **Provenance** | ✗ | No source; appears to be novel metric |

**Action**:
- [ ] Explain weight hierarchy (why Contract > Theory?)
- [ ] Add sensitivity: if weights = (1/6) each, AESHI = ?
- [ ] Justify threshold values: GREEN ≥ 0.85, YELLOW ≥ 0.70, RED < 0.70

---

### 10. ✓✓✓ CCI (COMPLETE CHAIN INDEX)
```
CCI = (Findings with complete T3→T2→T1 chain) / (Total findings)
```
**Location**: PART_IV, §50.9 (lines 1385–1407)
**Status**: **GOOD** ✓

| Criterion | Status | Notes |
|-----------|--------|-------|
| **Intuition** | ✓✓ | Excellent: shows CCI meaning at 1.0, 0.5, 0.1 with examples |
| **Derivation** | ✓ | Seven-gate algorithm transparent (lines 1935–1951) |
| **Provenance** | ✓ | Novel metric, but justified by system architecture |

**Action**: None required (exemplary).

---

### 11. ✗✗✗ COHERENCE COMPUTATION (C*)
```
C* = ???
```
**Location**: PART_IX, §84–89 + PART_XVII, §7.2
**Status**: **CRITICAL GAP** ✗

| Criterion | Status | Notes |
|-----------|--------|-------|
| **Intuition** | ✗ | Discussed philosophically but never formalized |
| **Derivation** | ✗ | No formula provided; line 1718 states full computation NOT implemented |
| **Provenance** | ✗ | Based on Thagard (1989) but custom version not specified |

**BLOCKER** for reproducibility. Cannot implement or validate coherence-based belief revision without formal specification.

**Action** (URGENT):
- [ ] Formalize C* with explicit formula (2–3 equations)
- [ ] Provide worked example (5–10 node web)
- [ ] Define algorithm: how to compute agreement links, contradiction links, normalization

---

### 12. ✗✗✗ VOI (VALUE OF INFORMATION)
```
VOI(gap) = ???
```
**Location**: PART_XV, §121.3 (lines 236–302)
**Status**: **CRITICAL GAP** ✗

| Criterion | Status | Notes |
|-----------|--------|-------|
| **Intuition** | ✓ | Conceptual components clear (Structural, Epistemic) |
| **Derivation** | ✗ | **No mathematical formula provided**, only worked example (lines 280–302) |
| **Provenance** | ✗ | Described as "VOI formula" but formula is missing |

**BLOCKER** for literature search automation. Cannot rank papers or decide to search without formal VOI computation.

**Action** (URGENT):
- [ ] State the VOI formula explicitly (2–3 equations)
- [ ] Define: P(close|search), P(partial|search), Coherence_gain(·), cost(·)
- [ ] Provide 2–3 worked examples
- [ ] Specify decision rule: "VOI ≥ [threshold] triggers search?"

---

## SECONDARY ITEMS: MAGIC NUMBERS

### δ Default Starting Value
```
δ_start = 0.90
```
**Status**: Unjustified
**Location**: PART_IV, §48.3A, line 169
**Action**: Add one sentence explaining the choice

---

### δ Minimum Feasible Value
```
δ_min = 0.30
```
**Status**: Unjustified
**Location**: PART_IV, §48.3A, line 175
**Action**: Explain: below 0.30, uncertainty from population difference exceeds [threshold]

---

### ω Floor & Ceiling
```
ω ∈ [0.05, 0.98]
```
**Status**: Partially justified (line 336)
**Location**: PART_IV, §48.3B, line 336
**Action**: Add sensitivity: if bounds were [0.01, 0.99], how much do predictions change?

---

### ω_rep Harmonic Discount
```
ω_rep = 1.0 + Σ (bonus_j / j)
```
**Status**: Intuitive, not derived
**Location**: PART_IV, §48.3B, line 284
**Action**: Add: "Why 1/j and not 1/j²? Answer: [empirical or theoretical basis]"

---

### TEA Weights
```
{0.30, 0.25, 0.15, 0.20, 0.10}
```
**Status**: Unjustified
**Location**: PART_IV, §48.3C, line 512
**Action**: Show sensitivity table; reference Decision D-48C.1

---

### AESHI Weights
```
{0.24, 0.19, 0.24, 0.19, 0.09, 0.05}
```
**Status**: Unjustified
**Location**: PART_IV, §53.8, line 1914
**Action**: Explain weight hierarchy; add sensitivity

---

### AESHI Thresholds
```
GREEN ≥ 0.85
YELLOW ≥ 0.70
RED < 0.70
```
**Status**: Stated, not justified
**Location**: PART_IV, §53.8, lines 1921–1923
**Action**: Why these breakpoints? Empirically calibrated?

---

## QUICK-FIX CHECKLIST (< 2 hours total)

Print and check off as you fix:

### For Each Unjustified Constant:

- [ ] **d values (CONSTITUTIVE, MECHANISM, etc.)**
  - Add margin note: `[RESEARCH NEEDED: empirical basis for these values]`
  - Add 1 sentence: "These values reflect [source]"

- [ ] **δ default (0.90) and minimum (0.30)**
  - Add 1 sentence each explaining the rationale

- [ ] **ω bounds [0.05, 0.98]**
  - Add sensitivity: "If bounds were [0.01, 0.99], predictions shift by ±[Z%]"

- [ ] **TEA weights**
  - Add sensitivity table (15 minutes to construct)

- [ ] **AESHI weights**
  - Add explanation of hierarchy

- [ ] **AESHI thresholds**
  - Add one sentence: "These were set by [method]"

### For Each Missing Derivation:

- [ ] **Multiplicative ω structure**
  - Add 1 paragraph: "Why multiply rather than add?"

- [ ] **Minimum d rule vs. product ω rule**
  - Add 3 sentences explaining the distinction

- [ ] **Logit transform**
  - Add source citation or brief derivation

---

## PRIORITY MATRIX

```
┌─────────────────────────────────────────────────────────┐
│  URGENCY & IMPACT: Where to Focus Effort                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  HIGH URGENCY (Blockers)                                │
│  ├─ Coherence formula (C*)                              │
│  ├─ VOI formula                                         │
│  └─ d value justification                               │
│                                                          │
│  MEDIUM URGENCY (Rigor)                                 │
│  ├─ δ and ω constant justifications                     │
│  ├─ TEA weight sensitivity                              │
│  ├─ AESHI weight justification                          │
│  └─ Multiplicative structure derivations                │
│                                                          │
│  LOW URGENCY (Polish)                                   │
│  ├─ Add figures/diagrams                                │
│  ├─ Cross-reference decision logs                       │
│  └─ Margin notes for gaps                               │
│                                                          │
└─────────────────────────────────────────────────────────┘

RECOMMENDATION: Fix HIGH first (4–6 weeks), then MEDIUM (2–3 weeks)
```

---

## ESTIMATED TIME PER FORMULA

| Formula | Formalize | Justify | Worked Example | Total |
|---------|-----------|---------|---|---|
| Coherence (C*) | 4 hrs | 2 hrs | 2 hrs | **8 hrs** |
| VOI | 3 hrs | 2 hrs | 2 hrs | **7 hrs** |
| d values | 0 | 8 hrs | 0 | **8 hrs** |
| δ/ω constants | 0 | 2 hrs | 0 | **2 hrs** |
| ω composition | 0 | 2 hrs | 0 | **2 hrs** |
| TEA weights | 0 | 2 hrs | 2 hrs | **4 hrs** |
| AESHI weights | 0 | 3 hrs | 0 | **3 hrs** |
| Figures (6) | 0 | 0 | 16 hrs | **16 hrs** |
| **TOTAL** | 7 hrs | 21 hrs | 6 hrs | **~34 hrs** |

**In person-weeks**: ~1 week for a dedicated writer (40 hrs/week)

---

## DECISION REQUIRED FROM DAVID

Before starting fixes, clarify:

1. **Scope**: Fix ONLY high-priority items? Or all?
   - Recommend: All high-priority + medium-priority = 6–9 weeks total

2. **Standards**: For magic numbers, which approach?
   - [ ] Empirical justification (meta-analysis) — expensive
   - [ ] Sensitivity analysis + panel attribution — faster
   - [ ] Leave as provisional, flag for future validation

3. **Ownership**: Who fixes each gap?
   - David? Panel members? Claude?

4. **Timeline**: Target completion date?
   - Recommend: 6–9 weeks from now (by mid-April 2026)

5. **Validation**: Who reviews fixes?
   - Recommend: David + 2 panel members per major formula

---

## TRACKING

Use this template to track fixes:

```
### Formula: [NAME]
- **Date Started**: [DATE]
- **Assigned to**: [NAME]
- **Status**: IN_PROGRESS / COMPLETED / BLOCKED
- **Changes Made**: [BRIEF SUMMARY]
- **Reviewed by**: [NAMES]
- **Date Completed**: [DATE]
```

---

## MASTER CHECKLIST

Print this page and check off as work proceeds:

**HIGH PRIORITY (Blockers)**
- [ ] Coherence (C*) formula formalized
- [ ] Coherence worked example added
- [ ] VOI formula stated
- [ ] VOI worked examples added
- [ ] d value justification complete

**MEDIUM PRIORITY (Rigor)**
- [ ] δ/ω constant justifications added
- [ ] ω composition multiplicative structure derived
- [ ] d_eff min vs. ω_eff product distinction explained
- [ ] TEA weight sensitivity table added
- [ ] AESHI weight justification added
- [ ] AESHI threshold justification added

**LOW PRIORITY (Polish)**
- [ ] 6 proposed figures added
- [ ] Decision log references embedded
- [ ] Margin notes added to gaps
- [ ] Logit derivation/source added

**VERIFICATION**
- [ ] All line number references verified against current document
- [ ] All formulas tested with worked examples
- [ ] All constants sensitivity-analyzed
- [ ] All sources cross-checked

