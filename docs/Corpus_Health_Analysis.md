# Corpus Health Analysis: ATLAS (Architecture for Typed, Layered Assessment of Science) ATLAS System
## Investigation of Health Check Findings by AG - February 26, 2026

---

## EXECUTIVE SUMMARY

AG's corpus health report identified four categories of integrity issues in the ATLAS's calibrated template library (103 templates across 12 domain panels):

- **100 missing confidence values** — parameter-level confidence scores not assigned
- **103 missing bridge warrants** — transfer justifications not specified for key steps
- **40 unclassified templates** — templates lacking tier assignments (A/B/C quality ranking)
- **1 ceiling violation** — a parameter's confidence score exceeding its bridge warrant's epistemic ceiling

This analysis contextualizes these findings within the ATLAS's documented quality-assurance framework (§59 of MASTER_DOC_CMR_2026-02-25.md) and provides a systematic repair plan grounded in the system's theoretical architecture.

---

## PART I: UNDERSTANDING THE ATLAS CREDENCE SYSTEM

### I.1 The Three-Factor Confidence Formula

The ATLAS's core disciplinary mechanism is a multiplicative credence formula for every architectural neuroscience claim:

**P(CNFA effect) = P(parent theory) × P(bridge) × P(CNFA-specific)**

This decomposes any claim about how architecture affects the brain into three independent epistemic questions:

1. **P(parent theory)**: How well-supported is the grounding neuroscience framework? (Tier 1 theories: Predictive Processing, Spatial Navigation, Dual Processing, etc.)
2. **P(bridge)**: How confidently can we transfer laboratory findings to architectural conditions? (Bridge warrant, ranging CONSTITUTIVE 0.75 → ANALOGICAL 0.35)
3. **P(CNFA-specific)**: How strong is the domain evidence (post-occupancy evaluations, field experiments, architectural research)?

Each factor receives a scalar confidence value in [0, 1]. The multiplicative structure ensures that weakness in any factor cascades through the composite, preventing overconfidence. Example: P(parent) = 0.85 (strong neuroscience) × P(bridge) = 0.35 (weak transfer evidence) × P(CNFA) = 0.50 (modest architectural evidence) = composite 0.15, appropriately conservative for an untested speculation.

### I.2 Bridge Warrants: The Core Disciplinary Mechanism

The **bridge warrant** is the ATLAS's single most original contribution. It quantifies the inferential leap from "this was demonstrated in a laboratory" to "this applies in a real building." Six warrant types are arranged in a strict hierarchy, each with an epistemic ceiling:

| Warrant Type | Ceiling | Definition |
|---|---|---|
| **CONSTITUTIVE** | 0.75 | The architectural feature literally *is* the mechanism (window area determines daylight melanopic irradiance) |
| **MECHANISM** | 0.60 | Complete causal pathway traced, tested, and transferred (adaptive neutral temperature formula validated in 14 buildings) |
| **EMPIRICAL_COVARIANCE** | 0.60 | Strong replicated correlations with multi-method support (integration-valence r = 0.50–0.55 across 42 studies, 12,000+ occupants) |
| **FUNCTIONAL** | 0.50 | Same functional role as lab stimulus, but mechanism unspecified (outdoor courtyard produces restoration effects, less reliably than controlled nature walks) |
| **CAPACITY** | 0.45 | Demonstrated capacity without direct architectural evidence (reconsolidation in motor learning suggests spatial schema updates are possible) |
| **ANALOGICAL** | 0.35 | Structural analogy only, no direct architectural evidence (auditory rhythm groove extends to visual rhythm scanning by analogy) |
| **THEORETICAL_DEFAULT** | 0.40 | Theory-only, awaiting empirical validation in architectural contexts |

### I.3 The Critical Ceiling Rule

A parameter's confidence score **can never exceed the ceiling implied by its bridge warrant**. This is the single rule that prevents epistemic overconfidence.

**Example violation**: An ANALOGICAL warrant with confidence 0.65 is a logical contradiction. It simultaneously asserts: (a) the only evidence is a structural analogy, and (b) we are moderately confident the transfer is real. These claims contradict. The system flags and rejects such violations.

From the master document (§51.2): "These priors serve as default starting points, set by expert judgment during ATLAS specification. Individual panels may adjust within ±0.10 with explicit justification, but a strict enforcement rule applies: **a parameter's confidence score can never exceed the ceiling implied by its bridge warrant**."

### I.4 Calibrated Parameters: The Seven Classes

Each template specifies calibrated parameters across seven classes:

1. **Effect sizes** — Cohen's d, correlation r, or odds ratio for each mechanism-chain step
2. **Confidence values** — the three-factor composite and per-step values
3. **Bridge warrants** — classified into the six-type hierarchy
4. **Boundary conditions** — parameter ranges (thermal comfort 21–23°C, noise transition ~65 dB)
5. **Temporal dynamics** — habituation time constants, acute-chronic partition thresholds
6. **Moderation parameters** — how individual differences, cultural factors, and perceived control modify baseline effect
7. **Interaction weights** — how templates' mechanisms interact (additive, redundant, synergistic, antagonistic)

---

## PART II: AG'S HEALTH REPORT FINDINGS

### II.1 Finding 1: 100 Missing Confidence Values

**What this means**: 100 individual mechanism-chain steps across the template corpus lack explicitly assigned P(step) values — the scalar confidence in that particular causal transition.

**Context from documentation**: The canonical JSON schema (§57.3) specifies that every mechanism-chain step should contain:
```json
"mechanism_chain": [
  {
    "step": 1,
    "from": "architectural_feature",
    "to": "neural_substrate",
    "warrant": "MECHANISM",
    "confidence": 0.55,  // ← REQUIRED
    "justification": { ... }
  }
]
```

The confidence field is mandatory. Each step's confidence is either:
- Computed explicitly from the three-factor formula for that specific step
- Carried forward from prior template consensus if the step has well-established precedent

**Why it matters**: Without per-step confidence values, the system cannot compute composite template confidence properly. If a 4-step mechanism lacks confidence values at steps 2 and 4, the composite credence becomes ambiguous — is it P(s1) × P(s3) × undefined × undefined?

**Likely source of the gap**: The February 2026 master document (§59.4) reports that the most recent `validate_toulmin.py` run identified 131 errors, with "65% of templates missing explicit tier assignments (since remediated)." Missing per-step confidence values are a related but distinct issue, likely from the same period when templates were being converted from panel markdown to JSON schema but confidence values were not systematically extracted.

### II.2 Finding 2: 103 Missing Bridge Warrants

**What this means**: 103 mechanism-chain steps lack explicit bridge-warrant classification. That is, the panelists agreed on a causal claim (e.g., "curved contours → approach behavior") but did not specify *which type of warrant justifies the transfer* from laboratory evidence to architectural conditions.

**Context**: Every step should specify its warrant type. Example from the master document: VF2 (Visual Rhythm) has "P(bridge) ≈ 0.40 — the limiting factor" with warrant type ANALOGICAL. This means: the evidence comes from auditory rhythm studies (Witek et al., 2014), the warrant is ANALOGICAL (structural analogy to visual scanning), so the bridge ceiling is 0.35.

**Why it matters**: Without explicit warrant classification, panels cannot enforce the ceiling rule. A panelist might assign confidence 0.65 to an ANALOGICAL step (violating the 0.35 ceiling) without realizing the constraint.

**Likely source**: Early-calibrated templates (V1.4 pilot with 8 VISUAL-I templates) and templates from panels conducted in parallel may not have undergone full warrant-classification review. The enforcement run documented in §59.2 states "no templates violated the ceiling rule without documented justification," but that validation may have skipped warrant-type assignment itself.

### II.3 Finding 3: 40 Unclassified Templates

**What this means**: 40 of the 103 calibrated templates lack explicit tier assignments — they do not carry an A/B/C depth rating indicating evidence quality.

**Context**: Tier assignments are defined in §58.3:
- **Tier A** — highest confidence, well-replicated, multi-method, direct architectural evidence
- **Tier B** — moderate confidence, laboratory evidence with bridge warrant, partial in-situ support
- **Tier C** — preliminary, theoretical grounding with sparse empirical support

The master document reports (§59.3) that "the audit identified inconsistencies primarily in templates from THERMAL-I and CREATIVE-I, where confidence values were initially missing and tier assignments were assigned based on theoretical considerations without corresponding quantitative calibration. These have been remediated in the V2.1 registry."

If 40 templates remain unclassified, this represents either:
1. Templates that were remediated at the system level but not at the individual-template-field level
2. Templates from newer panels (e.g., MEMORY-I, CROSSCUT-I) where tier assignment was never performed
3. Scaffold-tier templates (identified but not yet panel-calibrated) that were inadvertently counted as calibrated templates

**Why it matters**: Tier assignments provide practitioners and researchers with a quick-reference quality indicator. Without them, a user cannot quickly assess whether a template is highly validated or highly preliminary.

### II.4 Finding 4: 1 Ceiling Violation

**What this means**: A single mechanism-chain step (1 occurrence) has a confidence value that exceeds the ceiling implied by its bridge warrant.

**Example from documentation**: If a step carries an ANALOGICAL warrant (ceiling 0.35) but is assigned confidence 0.65, this is a violation. The assertion that "only a structural analogy supports transfer" and "we are moderately confident the transfer works" are contradictory.

**Context from documentation** (§51.2): "An ANALOGICAL warrant with confidence 0.65 is a logical contradiction — the system flags and rejects it."

The master document (§59.2) notes: "In the most recent enforcement run, no templates violated the ceiling rule without documented justification — a clean pass reflecting the constraint architecture's effectiveness."

AG's finding of 1 violation suggests either:
1. A new template added after the most recent enforcement run
2. An override that was not properly documented in the ceiling_override_rationale field
3. A manual edit that bypassed the `lint_bridge_ceilings.py` validation script

---

## PART III: ROOT CAUSES AND CONTEXT FROM THE MASTER DOCUMENT

### III.1 The Acknowledged Quality Gaps (§59: Quality Assurance)

The master document itself provides a comprehensive self-audit, identifying that the ATLAS system rates at "three to three-and-a-quarter stars out of five" with documented strengths and weaknesses:

**Documented Strengths**:
- Confidence conservatism (0.40–0.55 composite range for most templates is appropriately cautious)
- Bridge-warrant transparency (every claim's transfer justification is explicit)
- Toulmin preservation (argument structure survives from debate to JSON)
- Systematic panel methodology (12 panels following identical deliberation protocol)

**Documented Weaknesses**:
- **71% cross-template interaction gap** — 36 of 51 templates (or 71% of calibrated templates) have empty cross-template interaction fields
- **Missing confidence values in early-calibrated templates** — templates from V1.4 pilot
- **Incomplete tier assignments** — identified as primarily in THERMAL-I and CREATIVE-I, reported as remediated
- **125 THEORETICAL_DEFAULT flags** — assumptions lacking direct architectural validation

AG's findings (100 missing confidences, 103 missing bridge warrants, 40 unclassified templates, 1 ceiling violation) align with the documented weaknesses and extend them with additional specificity.

### III.2 Validation Scripts and Enforcement Mechanisms

The master document (§57.4) specifies three validation scripts that should catch these errors:

1. **`validate_templates.py`** — checks schema conformity (all required fields present and correctly typed)
2. **`lint_bridge_ceilings.py`** — verifies confidence values do not exceed bridge-warrant ceilings
3. **`validate_toulmin.py`** — checks Toulmin completeness (each step has data array 3+ sources, backing 150+ chars, qualifier, rebuttal, competing accounts)

These scripts should flag:
- Missing confidence values (caught by `validate_templates.py` if confidence is a required field)
- Missing bridge warrants (caught by `validate_templates.py` if bridge_warrant is a required field)
- Unclassified templates (caught by `validate_templates.py` if tier is a required field)
- Ceiling violations (caught by `lint_bridge_ceilings.py`)

### III.3 The Calibration Registry Evolution (§57.4)

The registry has evolved through versions:
- **V1.4** (pilot) — 8 templates, incomplete Toulmin justification
- **V1.8** — 42 templates, full Toulmin coverage, inconsistent interactions
- **V2.1** (current) — 103 calibrated templates, enforced schema validation, bridge ceiling checking, Toulmin completeness

Additionally, "72 templates remain at scaffold-tier status (identified but not yet panel-calibrated), for a total corpus of 175 templates at various maturity levels."

If AG's count includes scaffold-tier templates or partially-converted templates, this explains some of the gaps.

---

## PART IV: SYSTEMATIC REPAIR PLAN

### IV.1 Assessment Framework: Severity and Priority

**Severity ranking** (from the master document's gap tracker, §59.7):
- **High severity** (116 gaps) — missing essential fields, undocumented interactions, ceiling violations
- **Medium severity** (14 gaps) — incomplete Toulmin elements, tier inconsistencies
- **Low severity** (23 gaps) — stylistic inconsistencies, missing optional fields

AG's findings map to severity:
- Missing confidence values: **HIGH** (essential for composite credence calculation)
- Missing bridge warrants: **HIGH** (essential for ceiling rule enforcement)
- Unclassified templates: **MEDIUM** (missing optional field? Or tier is required?)
- Ceiling violation: **HIGH** (logical contradiction, prevents system coherence)

### IV.2 Remediation Steps

#### Phase 1: Data Triage and Inventory (Week 1)

**Objective**: Understand the exact distribution of gaps and their root causes.

**Steps**:

1. **Run comprehensive validation suite**:
   ```bash
   python scripts/validate_templates.py --output=validation_report_Feb26.json
   python scripts/lint_bridge_ceilings.py --output=ceiling_report_Feb26.json
   python scripts/validate_toulmin.py --output=toulmin_report_Feb26.json
   python scripts/gap_tracker.py --severity=all --output=gaps_Feb26.json
   ```

2. **Cross-reference AG's 4 findings with validation output**:
   - Are the 100 missing confidences in a particular set of templates or scattered across panels?
   - Are the 103 missing bridge warrants concentrated in early templates (V1.4/V1.8) or recent panels?
   - Which 40 templates lack tier assignments? Are these from specific panels?
   - Which single template has the ceiling violation? What are its warrant and confidence values?

3. **Categorize by source**:
   - **Pre-registry templates** (markdown files that were never converted to JSON) — if so, they need manual calibration
   - **Early registry versions** (V1.4/V1.8 that were not fully updated for V2.1) — if so, they need systematic upgrade
   - **Newly added scaffolds** (not yet panel-calibrated) — if so, they should be excluded from the calibrated-template count
   - **Override cases** (confidence values that were deliberately placed above ceiling with documented rationale) — if so, verify documentation

4. **Interview AG and relevant panelists**:
   - When was the health check run? (If run against V2.1 registry, the count suggests gaps in the JSON serialization.)
   - What is the source of the data files checked? (JSON files? YAML? Markdown?)
   - Were any templates added, modified, or re-serialized between V2.1 release and the health check?

#### Phase 2: Missing Confidence Values Repair (Weeks 2–3)

**Objective**: Assign per-step confidence values to the 100 steps lacking them.

**For each missing confidence value**:

1. **Identify the mechanism step**:
   - What is the causal claim? (e.g., "increased spatial integration → reduced stress response")
   - What is the warrant type already assigned to the step?
   - What is the source evidence (laboratory study, field research, theoretical prediction)?

2. **Apply the three-factor formula to that step**:
   - P(parent): Is the mechanism grounded in a Tier 1 framework? What is the parent framework's credence? (Predictive Processing ~0.80, Spatial Navigation ~0.75, etc.)
   - P(bridge): What is the warrant type? (Use ceiling as upper bound: EMPIRICAL_COVARIANCE 0.60, ANALOGICAL 0.35, etc.)
   - P(CNFA-specific): What domain evidence exists for this specific step? (Search the Tier 3 claims database for studies supporting this architectural feature → outcome link.)
   - Composite = P(parent) × P(bridge) × P(CNFA-specific), capped at warrant ceiling

3. **Document the assignment**:
   - Record the three factors separately (transparency)
   - Add a brief justification in the JSON comment field
   - Note whether the confidence is based on: (a) direct panel consensus, (b) prior template precedent, (c) theoretical derivation with THEORETICAL_DEFAULT flag

4. **Validation**:
   - Verify confidence ≤ warrant ceiling
   - Run `lint_bridge_ceilings.py` on the updated template
   - Have a panelist from the relevant domain review the assignment

**Tools and resources**:
- Template precedent database: look at similar steps from other templates in the same panel (e.g., if SPATIAL-I has a "spatial integration → amygdala activation" step with confidence 0.55, use this as a precedent for related steps)
- Tier 1 framework credence values (from §50 of the master document):
  - Predictive Processing: ~0.80–0.85
  - Spatial Navigation: ~0.75–0.80
  - Dual-Process Evaluation: ~0.75
  - Deep Theories (Interoceptive Construction, Neuromodulation, etc.): ~0.65–0.75
- Warrant ceiling lookup table (provided above in II.2)

#### Phase 3: Missing Bridge Warrants Classification (Weeks 2–3)

**Objective**: Assign explicit warrant types to the 103 steps lacking them.

**For each missing bridge warrant**:

1. **Identify the mechanism step** and its existing evidence:
   - What is the causal claim?
   - What evidence supports it? (Laboratory study? Field study? Field observation?)
   - How direct is the evidence? (Is the lab stimulus the architectural feature itself, or an analog?)

2. **Classify the warrant**:
   - **CONSTITUTIVE** (0.75): The architectural feature *is* the mechanism input. Example: window area determines daylight melanopic irradiance (no transfer gap; the lab variable IS the architectural variable).
   - **MECHANISM** (0.60): Complete pathway traced and tested. Example: adaptive neutral temperature (lab thermoregulation studies + field-validated formula de Dear & Brager, 1998).
   - **EMPIRICAL_COVARIANCE** (0.60): Strong replicated correlations. Example: spatial integration-emotion (r ≈ 0.50 across 42 studies, 12,000+ occupants).
   - **FUNCTIONAL** (0.50): Same functional role, unspecified mechanism. Example: courtyard garden vs. nature walk (both produce restoration, but the correspondence is functional, not mechanistic).
   - **CAPACITY** (0.45): Demonstrated capacity without direct architectural evidence. Example: reconsolidation can update memory schemas (demonstrated in fear conditioning, extrapolated to spatial memory).
   - **ANALOGICAL** (0.35): Structural analogy only. Example: auditory rhythm groove → visual rhythm (analogy, no direct architectural evidence).
   - **THEORETICAL_DEFAULT** (0.40): Theory-only, awaiting empirical validation.

3. **Decision tree for warrant classification**:
   - Is the lab variable literally identical to the architectural variable? → CONSTITUTIVE
   - Is there a complete traced pathway + field validation across multiple buildings? → MECHANISM or EMPIRICAL_COVARIANCE
   - Is there strong correlational evidence (r > 0.40) replicated across 3+ studies? → EMPIRICAL_COVARIANCE
   - Is there evidence of functional equivalence but unspecified mechanism? → FUNCTIONAL
   - Is the evidence only from a different sensory domain or species? → ANALOGICAL
   - Is the evidence only theoretical, without empirical transfer validation? → THEORETICAL_DEFAULT

4. **Document and validate**:
   - Record the warrant type in the JSON schema
   - Update the confidence value: it must now respect the warrant ceiling
   - If confidence previously exceeded ceiling, **flag for override review** (Phase 4)

#### Phase 4: Tier Assignments for 40 Unclassified Templates (Week 4)

**Objective**: Assign A/B/C depth tiers to the 40 templates lacking them.

**For each unclassified template**:

1. **Determine tier from confidence value and evidence base**:
   - **Tier A** (highest): composite credence ≥ 0.70, or well-replicated multi-method evidence with direct architectural RCT, or CONSTITUTIVE/MECHANISM warrant with strong domain support
   - **Tier B** (moderate): composite credence 0.50–0.70, or EMPIRICAL_COVARIANCE warrant with partial in-situ support
   - **Tier C** (preliminary): composite credence < 0.50, or ANALOGICAL/THEORETICAL_DEFAULT warrant, or theory-only with sparse empirical support

2. **Cross-check consistency** (from §59.3):
   - A Tier A template should have credence ≥ 0.60–0.70
   - A Tier C template should have credence < 0.60
   - Tier and confidence should align

3. **Validate against panel consensus**:
   - Review the original panel output document for the template
   - If panels explicitly voted Tier A/B/C, use that assignment
   - If not, assign based on documented evidence strength

4. **Document assignment rationale**:
   - Add a "tier_rationale" field explaining the assignment
   - Flag if evidence is insufficient to confidently assign a tier

#### Phase 5: Ceiling Violation Resolution (Week 4)

**Objective**: Resolve the single ceiling violation.

**For the violating parameter**:

1. **Identify the violation**:
   - Template ID: ?
   - Step number: ?
   - Bridge warrant: ? (e.g., ANALOGICAL 0.35)
   - Assigned confidence: ? (e.g., 0.65)
   - Excess: 0.65 − 0.35 = 0.30

2. **Determine resolution path**:

   **Option A: Lower confidence to respect ceiling**
   - If the step's evidence does not support a confidence above the warrant ceiling, lower the confidence to the ceiling (or below)
   - Rationale: The warrant type was correctly assigned; the confidence was inflated
   - Example: If evidence is only an ANALOGICAL warrant, set confidence to ≤ 0.35

   **Option B: Upgrade warrant type to justify confidence**
   - If the step actually has stronger evidence than its assigned warrant suggests, upgrade the warrant
   - Rationale: The confidence is justified; the warrant was underassigned
   - Example: If auditory-visual rhythm analogy is supported by a direct field study, upgrade ANALOGICAL → EMPIRICAL_COVARIANCE (0.60 ceiling)
   - Requires: new evidence supporting the stronger warrant, documented in the updated JSON

   **Option C: Document explicit override with rationale**
   - If the panel consciously placed confidence above ceiling and the decision is defensible, document the override
   - Requires: (a) panel consensus, (b) explicit rationale in ceiling_override_rationale field, (c) review by ceiling-recalibration panel
   - From the master document (§59.2): "Ceilings are Bayesian soft priors, not hard caps: when a panel assigns confidence above the ceiling, the exceedance is permitted only with an explicit rationale documented in the ceiling_override_rationale field and reviewed during the ceiling-recalibration panel."

3. **Most likely resolution**: If the master document states "In the most recent enforcement run, no templates violated the ceiling rule without documented justification," then the single violation probably lacks proper documentation. Update the ceiling_override_rationale field with the appropriate justification, or apply Option A/B above.

#### Phase 6: Validation and Integration (Week 5)

**Objective**: Ensure all repairs are internally consistent and pass validation.

**Steps**:

1. **Run full validation suite**:
   ```bash
   python scripts/validate_templates.py --strict
   python scripts/lint_bridge_ceilings.py --strict
   python scripts/validate_toulmin.py --strict
   python scripts/gap_tracker.py --severity=all
   ```

2. **Fix any newly identified issues**:
   - If validation reveals new gaps (e.g., 100 confidences repaired but 50 new ones missing), iterate
   - Document the iteration cycle

3. **Cross-panel coherence check**:
   - Verify that similar steps across panels (e.g., "prediction error → reduced stress") have comparable confidence values
   - Identify and resolve any systematic divergences

4. **Tier distribution check**:
   - Calculate: % Tier A, % Tier B, % Tier C across all 103 templates
   - Compare to expected distribution: ~15% Tier A, ~60% Tier B, ~25% Tier C (from §58.3)
   - If distribution is skewed, investigate why

5. **Update documentation**:
   - Create a repair log: before/after counts for each finding
   - Document the rationale for each repair decision
   - File a corrected health report

---

## PART V: WHAT "CEILING VIOLATION" MEANS

### V.1 Conceptual Definition

A **ceiling violation** occurs when a parameter's confidence score contradicts its bridge warrant's epistemic ceiling. The bridge warrant makes an implicit claim about the evidential situation; the confidence score makes a claim about credibility; these two claims must align.

Example from the master document (§51.2):

> An ANALOGICAL warrant with confidence 0.65 is a logical contradiction — the system flags and rejects it.

Breaking this down:
- **ANALOGICAL warrant** asserts: "The only evidence for transfer from lab to architecture is a structural analogy between two different domains (e.g., auditory rhythm → visual rhythm)."
- **Confidence 0.65** asserts: "We have moderate-to-strong confidence that this transfer is real."
- **The contradiction**: If the only evidence is an analogy (weak transfer justification), how can we have moderate-to-strong confidence in transfer?

The ceiling rule prevents this incoherence.

### V.2 The Warrant-Ceiling Mapping

Each warrant type has an implicit "evidential ceiling" — a maximum credence that coherently corresponds to that warrant type:

| Warrant | Ceiling | Interpretation |
|---|---|---|
| CONSTITUTIVE | 0.75 | The lab variable IS the architectural variable; maximal transfer, some parametric uncertainty remains |
| MECHANISM | 0.60 | Complete pathway traced and validated in multiple buildings; substantial but not overwhelming confidence |
| EMPIRICAL_COVARIANCE | 0.60 | Strong replicated correlations; good confidence but not causal certainty |
| FUNCTIONAL | 0.50 | Same functional role without mechanistic understanding; moderate confidence only |
| CAPACITY | 0.45 | Capacity demonstrated in other domains; low-to-moderate confidence for architectural application |
| ANALOGICAL | 0.35 | Structural analogy only; minimal direct evidence; low confidence justified |
| THEORETICAL_DEFAULT | 0.40 | Theoretical grounding without empirical validation; low confidence appropriate |

The ceilings are **soft priors**, not hard caps. They can be exceeded with explicit documented justification. But exceeding a ceiling without justification is a logical error.

### V.3 Examples of Violations and Resolutions

**Example 1: Auditory-Visual Rhythm (from master document, VF2)**

- Mechanism: Auditory groove response (syncopation at ~20–30%) transfers to visual rhythm in architectural facades
- Warrant type: ANALOGICAL (0.35 ceiling) — only a structural analogy between auditory and visual domain
- Panel assigned confidence: 0.40 (per-step), contributing to composite 0.32
- Violation? No. Confidence (0.40) < Ceiling (0.35) ← **Wait, confidence exceeds ceiling by 0.05!**

This is a marginal violation. How was it handled? The master document (§60.8) notes: "the panel used EMPIRICAL_COVARIANCE (0.55) for the visual rhythm mechanism itself, reserving the ANALOGICAL warrant (0.40) only for specific SRV boundary values." Translation: the overall mechanism step received EMPIRICAL_COVARIANCE (0.55 ceiling), so confidence 0.40 is justified. The violation was avoided through careful warrant sub-typing (different warrant types for different components of the same mechanism).

**Example 2: Hypothetical Bridge Violation**

- Mechanism: Ceiling height → creative thinking
- Warrant type: CAPACITY (0.45 ceiling) — reconsolidation demonstrated in fear conditioning, extrapolated to spatial memory
- Panel assigned confidence: 0.62
- Violation? Yes. Confidence (0.62) > Ceiling (0.45)

Resolution options:
1. **Lower confidence to 0.45**: If capacity evidence doesn't support higher confidence, align with ceiling
2. **Upgrade to EMPIRICAL_COVARIANCE (0.60 ceiling)**: If there's a direct field study of ceiling height on creativity, upgrade the warrant
3. **Document override**: If the panel has a documented reason for exceeding the ceiling, formally record it in ceiling_override_rationale

---

## PART VI: MISSING CONFIDENCE VALUES AND BRIDGE WARRANTS — FREQUENCY INTERPRETATION

### VI.1 Why 100 Missing Confidences?

If the corpus contains 103 calibrated templates with an average 4 mechanism-chain steps each, the system should have approximately 412 per-step confidence values. AG found 100 missing, meaning roughly 24% of step-level confidence values are absent.

This is high but interpretable:

1. **Early templates without per-step confidence**: V1.4 pilot had "basic mechanism chains but incomplete Toulmin justification" (§57.4). If ~25% of the 103 templates are from V1.4/V1.8 without per-step updates, this explains the count.

2. **Threshold-based parameters without confidence**: Some mechanism steps might be parametric thresholds (e.g., "ceiling height > 2.7 m triggers creative thinking") rather than causal claims, in which case confidence assignment is conceptually different.

3. **Interaction terms without confidence**: If 36 templates have empty interaction fields (§59.5), their sub-steps (interaction specifications) may also lack confidence values.

### VI.2 Why 103 Missing Bridge Warrants?

103 missing bridge warrants roughly equals the number of calibrated templates (103 total). This suggests:
- Either 103 templates are missing warrants at the template level (in which case all their steps inherit an unspecified warrant)
- Or 103 individual steps across templates lack warrant assignment

If the latter, this represents roughly 25% of steps, parallel to the confidence-value count.

Interpretation: Templates were created with causal claims and confidence values but without explicit warrant classification. The warrant should be assigned at the step level, and if 103 steps lack it, this is a systematic gap, likely from:
1. Manual JSON construction without full schema conformance
2. Older templates (V1.4/V1.8) converted to V2.1 schema without full warrant specification
3. Newly added templates that were not run through the warrant-classification step

---

## PART VII: CROSS-REFERENCE WITH DOCUMENTED SYSTEM STATE

The master document's own quality-assurance section (§59) reports:

| Finding | Master Doc Assessment | AG's Health Check | Status |
|---|---|---|---|
| Missing confidence values | Not explicitly quantified, but acknowledged as part of "early-calibrated template" gaps | **100 found** | **Quantifies previously unquantified gap** |
| Missing bridge warrants | Not explicitly quantified in documented audits | **103 found** | **New finding, suggests incomplete warrant workflow** |
| Unclassified templates (no tier) | "65% missing explicit tier assignments (since remediated)" in V2.0 audit; "remediated in V2.1" | **40 found** | **Suggests remediation was incomplete or newer templates added** |
| Ceiling violations | "No templates violated ceiling rule without documented justification — clean pass" | **1 found** | **Suggests either: new template added after enforcement run, or override not properly documented** |
| Cross-template interaction gap | **"71% have empty fields" (36 of 51 templates, or 36 of 103 calibrated)** | Not assessed by AG | **Most serious documented deficiency** |

AG's findings validate and extend the master document's self-assessment. The system is less mature than the "clean pass" language suggests; it has specific, quantifiable gaps.

---

## PART VIII: REPAIR PLAN TIMELINE AND RESOURCE REQUIREMENTS

### VIII.1 Estimated Effort

| Phase | Objective | Duration | Resources |
|---|---|---|---|
| 1 | Data triage, validation runs, gap inventory | 1 week | 1 FTE (engineer) + AG (if available for interviews) |
| 2 | Per-step confidence assignments | 2–3 weeks | 1 FTE (engineer) + 2 FTE panelists/domain experts |
| 3 | Bridge warrant classification | 2–3 weeks | 1 FTE (engineer) + 2 FTE panelists/domain experts |
| 4 | Tier assignments | 1 week | 1 FTE (engineer) + 1 FTE domain expert review |
| 5 | Ceiling violation resolution | 1 week | 1 FTE (engineer) + panel lead from relevant domain |
| 6 | Validation & integration | 1 week | 1 FTE (engineer) + QA review |
| **Total** | **Complete corpus repair** | **8–10 weeks** | **1–2 FTE core engineering + 4–6 FTE panel expertise** |

### VIII.2 Parallel vs. Sequential Execution

Phases can be partially parallelized:
- Phase 1 can run independently (1 week)
- Phases 2 & 3 can run in parallel once Phase 1 triage is complete (weeks 2–4)
- Phase 4 can overlap with Phases 2 & 3 (weeks 2–4)
- Phase 5 can run once Phase 1 identifies the ceiling violation (week 2 or later)
- Phase 6 is sequential (requires completion of 2–5)

**Optimized timeline**: 5–6 weeks with parallel execution, assuming dedicated resources.

### VIII.3 Governance and Review

- **Weekly checkpoint reviews** — engineering lead + domain panelist leads assess progress
- **Repair log documentation** — every decision (why confidence was assigned as X, why warrant was classified as Y) is recorded
- **Round-robin peer review** — every repair is reviewed by a panelist from a different panel (cross-panel consistency check)
- **Master validation before release** — all 103 templates must pass `validate_templates.py`, `lint_bridge_ceilings.py`, and `validate_toulmin.py` before the V2.2 registry release

---

## PART IX: CRITICAL NEXT STEPS BEYOND REPAIR

The master document (§59.7) identifies this repair as necessary but not sufficient. The system has three major forward-facing priorities beyond the immediate repair:

### IX.1 Close the 71% Cross-Template Interaction Gap (Priority 1)

**What**: 36 of 51 calibrated templates have empty cross-template interaction fields. This means the system cannot identify when two templates make overlapping claims about the same mechanism (risking double-counting effects) or when two templates have opposing effects that partially cancel.

**Why critical**: A practitioner applying both CREA2 and CREA3 (creativity templates) simultaneously might apply their effects as additive (composite effect size = sum) when actually they are redundant (composite effect size < sum) because they both operate on the same creative-thinking pathway. Without interaction specifications, the system overestimates composite effect.

**Resource requirement**: Dedicated Interaction Panel (Panel XI-A) in Q2 2026, 3–4 weeks panel time + 4–6 weeks analytical follow-up.

### IX.2 Establish Sustainable Governance (Priority 2)

**What**: The current system treats the 103 templates as static. Establish a three-tiered governance structure:
- Annual updates for highest-uncertainty clusters
- Biennial broadening panels extending to understudied populations (children, elderly, non-Western cultures, neurodivergent)
- Reactive panels triggered by replicated falsifications

**Why critical**: Science is cumulative. New evidence will emerge that should trigger template updates. Without governance, the template library becomes stale.

**Resource requirement**: Governance framework specification (2–3 weeks) + lightweight annual panels (2–3 days per year).

### IX.3 Conduct Meta-Analysis of Panel Reliability (Priority 3)

**What**: The twelve domain panels were conducted in parallel using identical protocols. Did they produce coherent outputs or divergent frameworks? Quantify inter-panel consistency in bridge-warrant assignment, interaction patterns, and theoretical framework preferences.

**Why critical**: Informs whether the parallel-panel methodology is robust or whether domain-specific protocols are needed.

**Resource requirement**: 3–4 months structured comparative analysis.

---

## CONCLUSION

AG's corpus health report identified **4 categories of integrity issues affecting ~243 individual parameters across 103 calibrated templates**:

- **100 missing per-step confidence values** (24% of expected step-level values)
- **103 missing bridge warrants** (25% of expected step-level warrants)
- **40 unclassified templates** (39% of calibrated templates lack tier assignments)
- **1 ceiling violation** (logical contradiction between warrant and confidence)

These gaps are quantifiable, systematic, and remediable within an estimated **5–6 week effort** using the repair plan outlined in Part IV. They do not represent fundamental system failure but rather **incomplete maturation of the V2.1 registry** — a gap between the system's theoretical architecture (well-developed) and its implementation (partially complete).

The repairs restore coherence to the credence system by ensuring that:
1. Every causal claim carries an explicit per-step confidence value grounded in the three-factor formula
2. Every confidence value respects the epistemic ceiling implied by its bridge warrant
3. Every template carries a transparent tier assignment indicating evidence quality
4. No logical contradictions exist between warrants and confidences

Beyond repair, the master document's own audit (§59.7) identifies the ATLAS as a **3-star system** (of 5) with genuine strengths in confidence conservatism and bridge-warrant transparency but serious weaknesses in cross-template interaction specification and governance sustainability. The repair plan addresses immediate integrity; the follow-on priorities (interaction panel, governance framework, meta-analysis) address the deeper architectural questions about system coherence and long-term sustainability.

---

## APPENDIX: REFERENCE MATERIALS FROM MASTER DOCUMENT

### Reference 1: Three-Factor Credence Formula (§48)

**P(CNFA effect) = P(parent theory) × P(bridge) × P(CNFA-specific)**

- P(parent theory): credence in grounding neuroscience framework
- P(bridge): credence in transfer from laboratory to architecture
- P(CNFA-specific): credence in domain-specific architectural evidence

### Reference 2: Bridge Warrant Hierarchy (§51.2)

| Type | Ceiling | Meaning |
|---|---|---|
| CONSTITUTIVE | 0.75 | Architectural feature IS the mechanism |
| MECHANISM | 0.60 | Complete pathway traced & field-validated |
| EMPIRICAL_COVARIANCE | 0.60 | Strong replicated correlations |
| FUNCTIONAL | 0.50 | Same functional role, mechanism unspecified |
| CAPACITY | 0.45 | Capacity demonstrated in other domain |
| ANALOGICAL | 0.35 | Structural analogy only |
| THEORETICAL_DEFAULT | 0.40 | Theory-only, awaiting validation |

### Reference 3: Tier Assignments (§58.3)

- **Tier A**: well-replicated, multi-method, direct architectural evidence
- **Tier B**: laboratory evidence with bridge, partial in-situ support
- **Tier C**: theoretical grounding with sparse empirical support

### Reference 4: Template Structure (§57.3)

```json
{
  "template_id": "DOMAIN_NAME_NNN",
  "t1_frameworks": ["PP", "NM"],
  "calibration_status": "panel_calibrated",
  "bridge_warrant": "EMPIRICAL_COVARIANCE",
  "confidence": 0.52,
  "tier": "B",
  "mechanism_chain": [
    {
      "step": 1,
      "from": "architectural_feature",
      "to": "neural_substrate",
      "warrant": "MECHANISM",
      "confidence": 0.55,
      "justification": {
        "data": [...],
        "backing": "...",
        "qualifier": "...",
        "rebuttal": "...",
        "competing_accounts": [...]
      }
    }
  ],
  "cross_template_interactions": {...},
  "residual_gaps": [...]
}
```

### Reference 5: Quality Assurance Levels (§59)

1. **Bridge warrant ceiling enforcement** — `lint_bridge_ceilings.py`
2. **Tier consistency audit** — tier must align with confidence
3. **Toulmin completeness** — `validate_toulmin.py` (131 errors in most recent run)
4. **Cross-template interaction integrity** — 71% gap
5. **THEORETICAL_DEFAULT load audit** — 125 flags across 51 templates (mean 2.5 per template)

---

**Analysis prepared**: February 26, 2026
**Source document**: MASTER_DOC_CMR_2026-02-25.md (sections 48–71, particularly §48–59)
**Reviewed corpus**: 103 calibrated templates (Tier 1 frameworks × 12 domain panels)
**Repair timeline**: 5–6 weeks with parallel execution, 8–10 weeks sequential
**Owner**: David Kirsh, Department of Cognitive Science, UC San Diego
