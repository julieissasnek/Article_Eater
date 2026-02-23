# PRE-PANEL REVIEW CLEARANCE — THERMAL-I (S-05)
## Issued by: OPUS/CHAT
## Date: February 23, 2026
## Status: **CLEARED WITH MODIFICATIONS**

---

# VERDICT

THERMAL-I is cleared to proceed. The pre-panel review correctly identified
the three unnamed expert slots, the allesthesia coverage gap, and the
critical risk of conflating empirical adaptive comfort data with the
predictive processing interpretation. Three modifications are required.

---

# MODIFICATION 1: EXPERT ROSTER (required)

## 1a. Name all expert slots

Three of eight proposed experts were placeholder descriptions. Unacceptable
for execution. Assignments:

| Slot | Placeholder | Named Expert | Rationale |
|------|-------------|--------------|-----------|
| 6 | "Computational thermoregulation modeler" | **Denis Blondin** (Université de Sherbrooke) | Cold-exposure metabolic modeling; co-authored with van Marken Lichtenbelt; quantitative thermoregulatory dynamics |
| 7 | "Environmental psychologist" | **Marcel Schweiker** (Karlsruhe Institute of Technology) | Thermal adaptation psychology, perceived control in buildings (Schweiker et al., 2012; Schweiker & Wagner, 2015); AX4 interaction expertise; also serves as secondary architectural bridge |
| 8 | "Architect (clinical building)" | **George Havenith** (Loughborough University) | Thermal physiology, parametric allesthesia studies; replaces the architect slot to fill the allesthesia gap (see 1b) |

## 1b. Allesthesia coverage

Cabanac (1971, 1979) coined the term and established the physiological
basis. His foundational work is textual authority regardless. But the
panel needs a researcher who has RECENTLY measured thermal pleasure
responses parametrically. Havenith's thermal physiology laboratory at
Loughborough has conducted exactly these studies.

Derek Clements-Croome (the pre-panel's architect recommendation) becomes
a cited authority in debate rather than a speaking panelist. The
architectural bridge is adequately provided by Wargocki (IEQ field data)
and Schweiker (thermal satisfaction in healthcare and office buildings).

## Final roster:

| # | Expert | Institution | Primary | Secondary |
|---|--------|------------|---------|-----------|
| 1 | Richard de Dear | University of Sydney | THERMAL_ADAPTIVE_PE_001 | THERMAL_COMFORT_ADAPTIVE_PE_001 |
| 2 | Lisa Feldman Barrett | Northeastern University | IC_THERMAL_COMFORT_001 | — |
| 3 | Bud Craig | Barrow Neurological Institute | IC_THERMAL_COMFORT_001 (competing) | THERMAL_ADAPTIVE_PE_001 |
| 4 | Wim van Marken Lichtenbelt | Maastricht University | THERMAL_ADAPTIVE_PE_001 (metabolic) | — |
| 5 | Pawel Wargocki | Technical University of Denmark | Architectural bridge (all templates) | — |
| 6 | Denis Blondin | Université de Sherbrooke | THERMAL_ADAPTIVE_PE_001 (computational modeling) | — |
| 7 | Marcel Schweiker | Karlsruhe Institute of Technology | THERMAL_ADAPTIVE_PE_001 (perceived control) | Architectural bridge |
| 8 | George Havenith | Loughborough University | THERMAL_COMFORT_ADAPTIVE_PE_001 (allesthesia) | — |

## Coverage:

| Template | Anchor(s) | Status |
|----------|-----------|--------|
| IC_THERMAL_COMFORT_001 | Barrett + Craig (competing) | ✓ — genuine theoretical debate |
| THERMAL_ADAPTIVE_PE_001 | de Dear + Craig + van Marken Lichtenbelt + Blondin | ✓ — strong four-person team |
| THERMAL_COMFORT_ADAPTIVE_PE_001 | Havenith + de Dear | ✓ — allesthesia specialist + adaptive comfort originator |

All 3 templates have at least one identified anchor. No placeholders remain.

---

# MODIFICATION 2: SCOPE PARTITION CONFIRMED (required)

The pre-panel review correctly identified the scope boundary. Confirm:

- **IC_THERMAL_COMFORT_001** = Neural substrate. Thermal signals ascend
  via lamina I spinothalamocortical pathway to insular cortex, are
  integrated with body budget predictions, produce comfort/discomfort
  as interoceptive inference. Craig's neuroanatomy vs. Barrett's
  constructionist account.

- **THERMAL_ADAPTIVE_PE_001** = Computational mechanism. Predictive
  processing framework: the brain predicts thermal input based on
  recent experience and environmental cues; deviations from prediction
  generate interoceptive PE that is metabolically costly. References
  IC_THERMAL_COMFORT_001 for the neural substrate.

- **THERMAL_COMFORT_ADAPTIVE_PE_001** = Hedonic valence. Allesthesia:
  the pleasure/displeasure response to thermal deviations is a function
  of the body's current thermal state (Cabanac, 1971). Tier C treatment
  (1 missing param, medium severity).

---

# MODIFICATION 3: CALIBRATION ORDER (required)

1. **IC_THERMAL_COMFORT_001** (Tier A) — neural substrate first
2. **THERMAL_ADAPTIVE_PE_001** (Tier A) — computational mechanism second,
   references IC neural substrate
3. **THERMAL_COMFORT_ADAPTIVE_PE_001** (Tier C) — hedonic valence last,
   abbreviated treatment

---

# CONSTRAINTS

| # | Constraint | Source | Status |
|---|-----------|--------|--------|
| C-01 | Inherit STRESS-I T7 allostatic anticipation mechanism; do not re-derive. STRESS-I owns general allostasis; THERMAL-I owns thermal-specific parameters and architectural modifiers. | Partial-out rule | **CONFIRMED** |
| C-02 | Adaptive comfort regression parameters (de Dear & Brager, 1998) carry EMPIRICAL_COVARIANCE warrant. The predictive processing interpretation (thermal PE as mechanism) carries FUNCTIONAL warrant at most. Do NOT stack — the PP interpretation is a theoretical reinterpretation of the same empirical data, not independent evidence. This is the most important constraint for this panel. | Evidence inflation prevention | **CONFIRMED — CRITICAL** |
| C-03 | Thermal load output format must be compatible with NEUROMOD-I ALLOSTATIC_MASTER_001 (T29) additive weighted-sum specification. Output thermal allostatic cost in units that can be summed with other allostatic inputs. | Forward compatibility | **CONFIRMED** |
| C-04 | IC_THERMAL_COMFORT_001 calibrated first; THERMAL_COMFORT_ADAPTIVE_PE_001 calibrated last. | Scope partition ordering | **CONFIRMED** |
| C-05 | Architectural bridge steps with < 2 independent paradigms → confidence ≤ 0.50 | Toulmin consistency ceiling | **CONFIRMED** |
| C-06 | No single thermal comfort parameter d > 0.80 | Coburn ceiling | **CONFIRMED** |
| C-07 | Flag thermal-acoustic cross-modal interaction to CROSSCUT-I AX series (Humphreys & Nicol, 2007: noise annoyance lowers thermal satisfaction by 0.5-1.0 scale points) | Cross-domain modulation | **CONFIRMED** |
| C-08 | Barrett vs. Craig debate on IC_THERMAL_COMFORT_001 must produce explicit competing_accounts in Toulmin justification — constructionist interoception (Barrett, 2017) vs. labelled-line thermoreception (Craig, 2002, 2009). Neither account may be dismissed; both must appear in the justification object with specific implications for the template. | Competing accounts requirement | **NEW** |
| C-09 | Cabanac (1971, 1979) cited as textual authority for allesthesia. Havenith provides contemporary parametric data. Clements-Croome cited as textual authority for healthcare thermal zoning. | Legacy authority protocol | **NEW** |
| C-10 | Use canonical field names per schemas/template_canonical.json. All 3 output templates must pass validate_templates.py scaffold + calibrated tiers, lint_bridge_ceilings.py with 0 violations, and validate_toulmin.py. | Structural repair enforcement | **NEW** |

---

# OPERATIONAL NOTES

1. **Output length**: 3 templates with inline Toulmin — estimated
   800-1,200 lines. Crash-resilience save protocol still applies
   (save after every JSON block).

2. **Barrett-Craig debate**: This is the scientific core of the panel.
   Constructionist interoception (Barrett) holds that thermal comfort
   is a constructed percept — the brain infers thermal state from
   interoceptive signals combined with prior expectations and context.
   Labelled-line theory (Craig) holds that thermal comfort has a
   dedicated neural pathway (lamina I → posterior insular cortex)
   with modality-specific processing. The debate has direct CMR
   implications: if Barrett is right, thermal comfort is highly
   context-dependent and modifiable by expectations (stronger
   architectural lever); if Craig is right, thermal comfort is more
   stimulus-bound and less context-modifiable (weaker architectural
   lever). The Tier A justification must preserve both accounts.

3. **Adaptive comfort is not the same as predictive processing**.
   De Dear's adaptive model is an empirical regression. The PP
   interpretation (thermal prediction error) is a theoretical gloss
   that explains WHY the regression works but has not been
   independently tested. The panel will be tempted to treat PP as
   adding confidence to the empirical finding. It does not. C-02
   prevents this.

4. **Inline Toulmin**: Same format as MUSIC-I. Depth tiers:
   - Tier A: IC_THERMAL_COMFORT_001, THERMAL_ADAPTIVE_PE_001
   - Tier C: THERMAL_COMFORT_ADAPTIVE_PE_001

5. **Template count**: 3 is authoritative per Sprint Brief.

---

*PRE_PANEL_REVIEW_CLEARANCE_THERMAL_I.md — CMR Project*
*Cleared with 3 modifications + 3 new constraints*
*OPUS/CHAT, February 23, 2026*
