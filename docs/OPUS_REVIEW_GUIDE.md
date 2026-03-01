# OPUS REVIEW GUIDE — Calibration Discipline Cheat Sheet
## Read this at the start of every review session. Do not skip.
## Last updated: February 22, 2026

---

## 1. Bridge Warrant Hierarchy (strict — never violate)

| Warrant | Prior P | Assign when… | Red flag if… |
|---------|---------|-------------|-------------|
| **CONSTITUTIVE** | 0.75 | The architectural feature IS the mechanism (e.g., window area IS daylight exposure) | Assigned to any parameter that requires a mediating neural step |
| **MECHANISM** | 0.60 | A complete neural/physiological causal pathway has been traced and experimentally tested | The pathway includes an un-tested inferential step |
| **EMPIRICAL_COVARIANCE** | 0.60 | Strong correlation exists (r > 0.40, replicated); mechanism is inferred but not directly tested | Used when only a single study exists, or r < 0.30 |
| **FUNCTIONAL** | 0.50 | Same function served but via a different mechanism (functional analogy) | Used when data exist for a MECHANISM or EMPIRICAL assignment |
| **CAPACITY** | 0.45 | System has the capacity but mechanism is unspecified | Used for a parameter where empirical data exist |
| **ANALOGICAL** | 0.35 | Structural analogy only — no direct empirical evidence in the CNFA domain | Used with confidence > 0.50 |

**Rule**: A parameter's confidence score can never exceed the ceiling implied by its bridge warrant. ANALOGICAL + confidence 0.65 is a contradiction — flag it.

---

## 2. Confidence Score Discipline

| Score Range | Meaning | When to flag |
|-------------|---------|--------------|
| > 0.65 | High confidence | Flag if an *architectural outcome measure* and no direct architectural empirical study exists |
| 0.50–0.65 | Moderate | Acceptable for MECHANISM/EMPIRICAL warrants with robust lab evidence |
| 0.40–0.50 | Low | Mark as **THEORETICAL_DEFAULT** — state the assumption explicitly |
| < 0.40 | Very low | Cannot calibrate — move to RESIDUAL GAPS with a study design recommendation |

**THEORETICAL_DEFAULT rule**: Any parameter set below 0.50 confidence MUST carry the `THEORETICAL_DEFAULT` flag AND state the assumption made. This is a hard rule, not a suggestion.

---

## 3. Coburn's R² Ceiling (Visual Domain — generalise the principle)

In the VISUAL-I panel, the Salingaros interaction analysis (D × SCI) yielded **ΔR² ≈ 0.04**. This means:

- **No single visual parameter explains more than ~25–30% of aesthetic variance** in isolation
- **Interaction terms between visual parameters are small** (4% additional variance)
- **Implication for all panels**: Be suspicious of any calibration that implies a single architectural feature explains > 30% of the target outcome. If a panel assigns d > 0.80 to any single architectural manipulation, CHALLENGE IT — the empirical literature does not support single-feature dominance at that level for subjective outcomes.

**Quick test**: If removing this one parameter from the model would change the predicted outcome by > 30%, the parameter is probably over-fitted. Flag for discussion.

---

## 4. Mandatory Per-Template Outputs (check every template)

Every calibrated template MUST have:

- [ ] Calibrated JSON with all parameter fields populated
- [ ] Confidence score (0–1) for every scalar value
- [ ] Bridge warrant type for every scalar value
- [ ] **Toulmin Justification Layer** for EVERY mechanism step (data, backing, qualifier, rebuttal, competing_accounts)
- [ ] Population modifiers (elderly, clinical, paediatric) where relevant
- [ ] Architectural modifier coefficients
- [ ] **IC2 interaction statement** (Body Budget Prediction) — even if null
- [ ] **AX4 interaction statement** (Perceived Control) — even if null
- [ ] **RESIDUAL GAPS section** with: uncalibratable params + study designs, THEORETICAL_DEFAULTs, CROSS_TEMPLATE_INTERACTION flags
- [ ] CMR integration note (T1 frameworks, T1.5 parents, IE-DPT interactions)
- [ ] APA references with DOIs for all cited papers

---

## 5. Review Red Flags — Quick Scan

When reviewing a panel output, scan for these in order:

1. **Confidence > 0.65 + no architectural RCT** → over-confident; downgrade or justify
2. **MECHANISM warrant + inferential gap** → should be EMPIRICAL_COVARIANCE or lower
3. **Missing THEORETICAL_DEFAULT flag** on any score < 0.50 → add it
4. **Missing or superficial Toulmin justification** (e.g., `< 2` independent data sources without downgrading confidence) → flag for revision
5. **No IC2/AX4 statement** on any template → mandatory, even if "no interaction identified"
6. **AWE-I referenced as a standalone panel** → ERROR; AX3 templates belong to CROSSCUT-I
7. **ART or SRT listed as T1** → ERROR; they are T1.5
8. **IE-DPT listed as T1 #11** → ERROR; it is an elevation of T1 #3 (DP)
9. **Single parameter d > 0.80** → Coburn ceiling challenge; request justification

---

## 6. The Core Credence Formula

```
P(CNFA effect) = P(parent theory) × P(bridge) × P(CNFA-specific)
```

Every calibrated parameter is ultimately a component of this product. If the final product exceeds 0.50 for an effect with only analogical bridge evidence, something is wrong upstream.

---

## 7. Panel Sequence (current state)

| Status | Panel | Templates |
|--------|-------|-----------|
| ✅ | STRESS-I | 3 |
| ✅ | LIGHT-I | 8 |
| ✅ | SPATIAL-I | 4 |
| ✅ | VISUAL-I | 8 |
| ✅ | **SOCIAL-I** | 11 |
| ✅ | MEMORY-I | 10 |
| ✅ | MULTI-I | 9 |
| ✅ | MUSIC-I | 13 |
| ✅ | THERMAL-I | 3 |
| NEXT | **CREATIVE-I** | 7 |
| — | NEUROMOD-I | 10 |
| LAST | CROSSCUT-I | 15 |

**55 calibrated / 111 remaining / 166 total**

---

*One page. Read it. Apply it. Every time.*
