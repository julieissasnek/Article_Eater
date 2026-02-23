# ⚠️ SUPERSEDED — See (newer version exists) for current version

# DOCUMENT 66: COMPREHENSIVE PROJECT AUDIT
## A Ruthless Assessment of the Article Eater System
## February 17, 2026

---

## Audit Charge

This document subjects the entire Article Eater project to the most unsparing examination its author can devise. The project has now completed 65 documents, 73 mechanistic templates, 10 calibration and deepening panels, 2 cross-cutting lifespan panels, a dual-index cross-reference, and a calibration registry. All 10 domains are rated ★★★★. All 9 template series are calibrated.

That is the internal view. This audit asks: **Is any of that real?**

Specifically:

1. Can the system do what it was designed to do — evaluate scientific papers and produce actionable assessments?
2. Can it evaluate an actual building and tell an architect something useful?
3. Are the templates encodable as software, or are they literary essays dressed in YAML?
4. Is the Predictive Processing framework doing genuine explanatory work, or is it a rubber stamp?
5. Are the ★★★★ coverage ratings honest?
6. Do the calibration parameters hold together across panels, or do they contradict each other?
7. What is the actual software gap between the documents and a working system?
8. What about the 75 templates (T1–T52, M1–M17, AX1–AX6) that form the project's foundation but have received NO calibration panels?
9. Is the expert panel methodology scientifically defensible?
10. If a skeptical reviewer read this entire corpus, what would they say?

The standard: every claim is guilty until proven innocent.

---

## STRESS TEST 1: THE PAPER EVALUATION WALKTHROUGH

### The Promised Capability

Article Eater was designed to help experts evaluate scientific papers about architecture and human wellbeing. The Comprehensive Task List (Doc 17) describes a CMR (Causal Mechanism Reasoning) pipeline — a 7-step software process:

1. Causal Decomposition — break a paper's claims into causal links
2. Framework Matching — map claims to theoretical frameworks
3. Mechanism Tracing — match claims to mechanistic templates
4. Core Operations — SUBSTITUTE, VARY_MOD, BLOCK to test mechanisms
5. Convergence Assessment — evaluate multi-template convergence
6. Composition Failure Detection — Barrett's R10 check
7. Prioritization — rank findings by value of information

The Ulrich 1984 worked example (Task O-10) was supposed to validate the end-to-end pipeline.

### The Reality

**The CMR pipeline does not exist as software.** It is described in specification documents. The implementation status:

- Sprint 0 (Foundation): Effectively done — file structure, basic models
- Sprint 1 (Epistemic Core): NOT STARTED
- Sprint 2 (Bayesian Network): NOT STARTED
- Sprint 3 (Coherence & Bridge): NOT STARTED
- Sprint 4/4b (Extraction Pipeline): NOT STARTED
- Sprint 5 (Integration): NOT STARTED — this is the "paper in → beliefs out" pipeline
- Sprint 6 (Research Queue): NOT STARTED
- Sprint 7 (Theory Tier): NOT STARTED — this is where templates get encoded in the database
- Sprint 8 (CMR Pipeline): NOT STARTED — this is the ACTUAL evaluation engine
- Sprint 9 (Pipeline Health): NOT STARTED

**Of ~45 Claude Code implementation tasks, approximately 3 have been completed.** The critical path to a working system runs through 8 unbuilt sprints. The entire template knowledge base — all 73 templates, all calibration data, all interaction matrices — exists ONLY as Markdown documents. None of it is encoded in a database. None of it is queryable by software. None of it can be applied algorithmically to a paper.

### Verdict

**FAILING.** The system cannot evaluate a single paper. The gap is not a matter of polish — it is structural. The knowledge base and the software are in different worlds. The Opus theory work has raced ahead of the engineering by approximately 60 documents and 8 sprints. If we stopped producing panels today and redirected all effort to implementation, a working paper-evaluation pipeline would still require months of engineering.

**Severity: CRITICAL.** This is the project's primary mission, and it cannot perform it at all.

---

## STRESS TEST 2: THE BUILDING EVALUATION WALKTHROUGH

### Test Case: Evaluate a Real Building

Take the Salk Institute (Louis Kahn, 1965). An architect asks: "How does this building affect human wellbeing according to your system?"

**Step 1: Environmental Feature Extraction.** The system would need to measure or estimate: light levels (L-series), material properties (MAT-series), spatial proportions (VF-series, SC-series), acoustic conditions (T32-T33), view quality (VIEW-series), social configuration (SOC-series), temporal dynamics (TP-series), color (COL-series). This requires either instrumented measurement or expert estimation from drawings/photos.

*Problem*: There is no feature extraction tool, protocol, or interface. The templates define WHAT to measure but not HOW to collect data from an actual building. The system assumes inputs arrive pre-measured.

**Step 2: Template Activation.** With measured features, the system would identify which templates are relevant: the travertine courtyard activates MAT1 (thermal), MAT2 (contact), MAT4 (natural material). The ocean view activates VIEW1. The spatial proportions activate VF3, SC2. The concrete walls activate the non-wood material profiles.

*Problem*: Template activation logic does not exist as code. In principle, a human expert could manually identify relevant templates. But the system was supposed to AUTOMATE or at least ASSIST this process.

**Step 3: Parameter Computation.** For each activated template, compute the predicted effect. Example: VIEW1's VQI would assess the ocean view. MAT1 would assess the thermal experience of travertine in La Jolla's climate. VF3 would compute R_h for the study rooms.

*Partial success*: The calibration panels HAVE provided many of the numerical parameters needed. VF3's R_h computation exists. MAT1's thermal Goldilocks boundaries exist. VIEW1's VQI formulation exists. These are real, computable quantities. This is where the panel work has genuine value.

**Step 4: Multi-Template Integration.** Combine predictions across templates. Does the overall wellbeing assessment make sense? Are there conflicts? How do interactions work?

*Problem*: The system has interaction data for a few specific pairs (VF1 × VF3: additive; CREA2 noise × light: sub-additive at 0.76). But there is NO general integration model. How do you combine a VIEW1 score of 72 with a MAT4 wood convergence score and an L3 daylight score? There is no common currency. The templates produce heterogeneous outputs (effect sizes in Cohen's d, quality indices on different scales, categorical Goldilocks zones) that cannot be straightforwardly combined. The system lacks what psychometrics calls a LINKING FUNCTION.

**Step 5: Report Generation.** Produce an actionable assessment.

*Does not exist.*

### What DOES Work

The individual template computations. If you ask "what is this room's R_h and what does that predict?", VF3 can answer. If you ask "is the daylight adequate for circadian entrainment for a 70-year-old?", L2 can answer with the age-corrected M-EDI formula. If you ask "does this noise level help or hinder creative work?", CREA2 can answer with the 2×2×2 matrix.

The templates are individually useful as REFERENCE LOOKUP TOOLS. They function as a parameterized evidence compendium. This is genuinely valuable — it is more than any existing resource in environmental psychology provides.

### Verdict

**PARTIALLY WORKING as a reference system. NOT WORKING as an integrated evaluation tool.** The individual templates contain real, computable, evidence-based parameters. An expert HUMAN could use this corpus to evaluate a building by manually applying relevant templates and synthesizing results. But the automated integration, conflict resolution, and report generation that would make it a SOFTWARE SYSTEM do not exist.

**Severity: MODERATE.** The building evaluation use case is more forgiving than the paper evaluation use case because a human expert can do the integration. The templates ARE useful as-is, but the project undersells them as "parameterized lookup" and oversells them as "integrated evaluation system."

---

## STRESS TEST 3: ARE THE TEMPLATES ENCODABLE?

### The Encoding Gap

Sprint 7.5 specifies encoding 28 templates (T1-T40 minus 12 seeds). The template extraction inventory (uploaded) lists them with formalism quality ratings: "how-actually," "how-plausibly," "how-possibly."

The newer templates (L1–L5, MAT1–MAT5, TP1–TP4, SOC1–SOC3, CREA1–CREA4, VIEW1, SC1–SC4, COL1–COL2, VF1–VF3, OLF1) are BETTER specified — they have YAML-like structural patterns, explicit causal links, scope conditions, and calibration parameters. But examine what "encoding" actually requires:

**Test: Can CREA4 (Collaborative Creativity Architecture) be encoded as executable code?**

CREA4 specifies:
- Alternation cycle timing: 8–15 min individual → 5–10 min group → 3–5 min incubation
- Group size: 3–6 optimal
- Display density: ≥1.5 m²/person writable
- Transition time: <30 seconds
- Psychological safety multiplier: d_arch = d_max × safety_baseline

The cycle timing and group size are straightforward parameters. The display density and transition time are measurable. The psychological safety multiplier requires an organizational assessment that is OUTSIDE the system's scope — it depends on data the system cannot obtain from building measurements.

**Test: Can the CREA2 interaction matrix be encoded?**

The 2×2×2 matrix maps noise × ceiling × light to divergent d-values and convergent penalties. This is a lookup table — trivially encodable. But the INPUT requires knowing: (a) ambient noise level (measurable), (b) ceiling height ratio R_h (computable), (c) illuminance (measurable). The template assumes these inputs are available. The encoding is easy; the data pipeline to FEED the encoding is unbuilt.

**Test: Can VF2's Spatial Rhythm Variation be encoded?**

SRV = CV of element spacing in a repeating series. This requires:
1. Identifying "elements" in an architectural façade or interior
2. Measuring their spacing
3. Computing the coefficient of variation

Step 1 is a COMPUTER VISION problem that the system does not address. "Element" identification in architecture is a research problem in its own right. The template defines SRV precisely but presupposes a feature extraction capability that may be years from reliable automation.

### The Pattern

Templates are encodable as PARAMETER LOOKUP and COMPUTATION RULES when given clean inputs. They are NOT encodable as AUTONOMOUS ASSESSMENT TOOLS because they depend on feature extraction that is itself an unsolved or partially-solved problem.

### Verdict

**ENCODABLE WITH MAJOR CAVEATS.** The calibrated templates can be turned into code that computes predictions from measured inputs. This is real and valuable — the parameters, Goldilocks zones, interaction matrices, and dose-response functions are well-specified enough for software encoding. The gap is not in the template specifications but in the INPUT PIPELINE: getting architectural features measured and into the system.

**Severity: MODERATE.** This is a real limitation but not a fatal one. The system can be deployed with human-provided inputs (an architect enters measurements) rather than automated feature extraction. The encoding work (Sprint 7) is genuinely achievable.

---

## STRESS TEST 4: IS PREDICTIVE PROCESSING DOING REAL WORK?

### The Charge

Every template in the system is framed as a Predictive Processing (PE) mechanism. Prediction errors from environmental features (light, sound, materials, spatial proportions) drive neural responses (SN gating, DMN-ECN coupling, allostatic regulation) that produce psychological outcomes (stress, attention, creativity, social behavior). The PE framework is the theoretical spine.

### The Prosecution

**Claim: PE is unfalsifiable as used here.** The framework is so flexible that ANYTHING can be described as a prediction error. A building is too bright? PE from luminance overshoot. Too dim? PE from luminance undershoot. Just right? Minimal PE, comfort. Novel materials? High PE, arousal. Familiar materials? Low PE, fluency. The Goldilocks framing (too little PE = boredom, moderate PE = engagement, too much PE = stress) is a restatement of the Wundt curve / inverted-U arousal function that has been known since 1874. Calling it "prediction error" rather than "arousal" or "optimal stimulation" adds terminological specificity but may not add explanatory power.

**Claim: The templates would work just as well without PE.** Consider MAT1 (thermal adaptive PE). The core finding is that thermal comfort follows an adaptive neutral point that shifts with climate exposure. This is well-established in the thermal comfort literature (de Dear & Brager, 1998; ASHRAE Standard 55) and was discovered without any reference to predictive processing. The PE framing adds: "thermal sensation reflects the difference between predicted and actual skin temperature." But this is just restating the adaptive model in PE vocabulary. The Goldilocks boundaries (±1°C neutral, ±1–3°C positive PE, etc.) come from empirical thermal comfort research, not from PE theory. PE is the EXPLANATION for why the boundaries exist, but the boundaries themselves are empirically derived.

**Claim: Where PE DOES add value.** There are cases where the PE framework generates predictions that other frameworks do not:

1. **Exposure habituation.** VF1's contour preference habituates with a specific time constant (τ ≈ 12–18 days) but floors at 40% of acute effect. PE predicts this: the perceptual PE component (P1 at ~84ms) does NOT habituate because it is hardwired, while the evaluative component (~300ms+) does because it updates predictions. This two-layer model — persistent perceptual PE plus modifiable evaluative PE — is a genuine PE-specific prediction that other frameworks (mere exposure, aesthetic fluency) do not make.

2. **Cross-modal prediction.** MAT3 (cross-modal material identity) predicts that haptic incongruence produces LARGER PE than visual incongruence. This follows from PE: the tactile system has HIGHER precision expectations for material identity (you expect what you touch to feel the way it looks) than the visual system has for tactile properties. This asymmetry is predicted by PE's precision-weighting mechanism and is not straightforwardly predicted by other frameworks.

3. **Transition enhancement.** VF3's PE_transition = 0.55 × ln(R_h_new/R_h_old) predicts that spatial transitions produce cognitive shifts proportional to the LOG RATIO of proportional change. This Weber's-law scaling follows directly from PE's information-theoretic foundations (surprise is log probability) and generates specific, testable, quantitative predictions about how sequences of spaces affect cognition.

4. **The interaction matrix.** CREA2's 2×2×2 sub-additivity follows from PE's network architecture: both noise and dim lighting converge on the salience network, so their combination hits a neural ceiling. This MECHANISTIC prediction — identifying the specific bottleneck that produces sub-additivity — goes beyond what a descriptive framework would provide.

### The Defense

PE does real work in approximately 30–40% of the templates — those where the mechanistic pathway from environmental feature through specific neural systems to behavioral outcome is traced with enough precision to generate predictions that differ from what you'd get by simply citing the empirical literature. In the remaining 60–70%, PE provides a CONSISTENT VOCABULARY and ORGANIZATIONAL FRAMEWORK but does not generate novel predictions beyond what the underlying empirical research already supplies.

This is not a fatal problem. Most theoretical frameworks in psychology serve exactly this dual role: they sometimes generate novel predictions and they always provide organizational coherence. The Bayesian brain hypothesis has the same profile in cognitive science more broadly — it is genuinely explanatory for some phenomena (perceptual illusions, sensorimotor control, learning) and essentially a redescription for others (preference, social cognition).

### Verdict

**PE IS DOING REAL WORK IN A MINORITY OF TEMPLATES AND PROVIDING USEFUL ORGANIZATION IN THE REST.** The system would be weaker without it — the organizational coherence that PE provides across 73 templates is itself valuable, and the 30–40% of templates where PE generates mechanistic predictions beyond the empirical base are the system's strongest contributions. But the project should be honest about this dual role rather than implying that every template is a PE-derived prediction.

**Severity: LOW-MODERATE.** The framework is defensible but oversold. The system should distinguish between "PE-derived prediction" (where the framework generates something new) and "PE-organized finding" (where the framework provides vocabulary for existing empirical results).

**Recommendation**: Add a `pe_contribution` tag to each template: `predictive` (PE generates the prediction), `explanatory` (PE explains known findings mechanistically), or `organizational` (PE provides vocabulary). Rough estimate of the split across 73 templates: ~15 predictive, ~25 explanatory, ~33 organizational.

---

## STRESS TEST 5: ARE THE COVERAGE RATINGS HONEST?

### The Claim

All 10 architectural domains are rated ★★★★:

| Domain | Rating |
|--------|--------|
| A1 Materials & Surfaces | ★★★★ |
| A2 Spatial Scale | ★★★★ |
| A3 Spatial Configuration | ★★★★ |
| A4 Light & Luminance | ★★★★ |
| A5 Acoustic | ★★★★ |
| A6 Visual Pattern & Form | ★★★★ |
| A7 Haptic & Thermal | ★★★★ |
| A8 Social Configuration | ★★★★ |
| A9 Task & Cognition | ★★★★ |
| A10 Temporal | ★★★★ |

### The Prosecution

**★★★★ has never been defined.** The system uses a star rating with no rubric. What does ★★★★ mean? No document defines the criteria. Does it mean "we have templates that cover this domain"? Then ★★★★ was achieved early and cheaply. Does it mean "we have calibrated, validated, design-actionable parameters"? Then most domains are ★★★ at best.

**Let me define a rubric retroactively and grade honestly:**

| Level | Meaning |
|-------|---------|
| ★ | Domain identified; no templates |
| ★★ | Templates exist but uncalibrated — qualitative only |
| ★★★ | Templates calibrated with quantitative parameters; expert estimates; Goldilocks boundaries |
| ★★★★ | Templates calibrated with empirical data; validated in architectural contexts; design-actionable parameters with known uncertainty |
| ★★★★★ | End-to-end validated: parameters empirically confirmed in built environments; architectural translation tested |

### Honest Grades Under This Rubric

| Domain | Claimed | Honest | Justification |
|--------|---------|--------|---------------|
| A1 Materials | ★★★★ | ★★★ | MAT1 thermal is well-calibrated (ASHRAE data). MAT4 wood channel weights are expert judgment with ±0.08–0.12 uncertainty. MAT3 congruence protocol NOT YET EXECUTED. MAT5 cultural conditioning is a framework, not calibrated. Non-wood profiles are "expert judgment, not empirical calibration." |
| A2 Spatial Scale | ★★★★ | ★★★ | VF3 R_h is a novel metric with clear boundaries but UNTESTED psychophysically. SC2 isovist PE uses Weber's law which is well-established but the specific spatial rhythm parameters (2–4× change, 15–40m) are expert estimates. Volumetric proportion PE is "preliminary." |
| A3 Spatial Config | ★★★★ | ★★★ | SC1 substantially calibrated. SC2 partially. SC3 Dunbar mapping supported by social psychology but the ARCHITECTURAL translation (optimal proximity distances) has limited direct evidence. SC4 wayfinding well-calibrated. |
| A4 Light | ★★★★ | ★★★½ | STRONGEST DOMAIN. L2 circadian is established science with precise parameters. L1 luminance CV has real Goldilocks boundaries. L3 channel weights are expert judgment but grounded. L5 dynamic light is uncalibrated. This domain comes closest to genuine ★★★★. |
| A5 Acoustic | ★★★★ | ★★★ | T32-T33 have specific acoustic parameters (SNR >+15 dB, RT60 0.4-0.8s) from well-established psychoacoustics. But these are EXISTING STANDARDS (ASHRAE, WHO) reframed in PE vocabulary. The PE reframing adds limited value beyond what acoustic engineers already know. Template coverage exists through the M-series (17 music templates) but these are entirely UNCALIBRATED. |
| A6 Visual Pattern | ★★★★ | ★★★ | VF1 contour preference has real effect sizes (d ≈ 0.45) from Vartanian VR studies. VF2 rhythm is "PRELIMINARY — derived by analogy." SCI is "preliminary." COL1-COL2 are partially calibrated. The strongest metric (CCI) is novel but untested in architectural contexts. |
| A7 Haptic/Thermal | ★★★★ | ★★★ | MAT2 CT-afferent boundaries are well-established neurophysiology. But effusivity-based predictions for architectural surfaces are expert extrapolations, not empirically validated in built settings. |
| A8 Social Config | ★★★★ | ★★★½ | SOC2 privacy-encounter model has strong support (N > 42,000 across 3 streams). SOC1 cultural zones have cross-cultural data (N ≈ 9,000, 42 countries). SOC3 Dunbar mapping well-grounded. This domain is genuinely strong. |
| A9 Task/Cognition | ★★★★ | ★★★ | CREA1-3 are well-parameterized but the 2×2×2 interaction matrix has only ONE directly measured cell (noise × light). CREA4 collaborative creativity is "supported-preliminary." The attention sub-domain relies primarily on T-series templates that are uncalibrated. |
| A10 Temporal | ★★★★ | ★★★ | TP1-4 calibrated with boundary values but many are "preliminary" (doorway gradient effect size "estimated"). The strongest temporal parameter is CREA3's walking benefit (d ≈ 0.8, Oppezzo replication). |

### Summary

**Honest average: ★★★ to ★★★¼.** The claimed ★★★★ across all 10 domains is inflated by approximately ¾ to 1 star. Two domains (A4 Light, A8 Social) approach genuine ★★★★. Most are solid ★★★. None reach ★★★★★ (end-to-end architectural validation).

### Verdict

**RATINGS ARE INFLATED.** Not fraudulently — the system genuinely has good template coverage and real parameters. But ★★★★ implies a level of empirical validation and architectural design-readiness that the system has not achieved. The honest claim is: "All 10 domains have calibrated templates with quantitative parameters, most derived from expert judgment informed by empirical literature. A few domains have parameters directly from empirical studies."

**Severity: MODERATE.** The inflation is a marketing problem, not a scientific one. The underlying work is solid ★★★; the system just needs to stop calling it ★★★★.

**Recommendation**: Redefine the rubric explicitly. Downgrade to honest ratings. Identify what each domain needs to reach genuine ★★★★ (typically: architectural-context validation of the parameter predictions).

---

## STRESS TEST 6: CROSS-PANEL PARAMETER CONSISTENCY

### Method

Identify every case where the same parameter, mechanism, or phenomenon is addressed by multiple panels. Check for contradictions.

### Test Cases

**6a: Exposure habituation time constants.**

- VF1 contour preference (Doc 64): τ ≈ 12–18 days, floor at 40%
- COL2 (Doc 63): τ referenced for chromatic adaptation
- MAT4 olfactory channel (Doc 51): HIGH at 0–5 min, near-zero at 20+ min (minutes, not days)

*Assessment*: These are DIFFERENT MECHANISMS operating at different timescales. Visual contour habituation (days) is a different process from olfactory adaptation (minutes). No contradiction — but the system should make the timescale distinction explicit. The general habituation function d(t) = d_acute × [floor + (1-floor) × e^(−t/τ)] appears in multiple templates with different τ values. This is CORRECT — different sensory channels habituate at different rates. But the system never states this explicitly as a principle, which creates a risk of confusion.

**6b: Ceiling height effects across templates.**

- VF3 (Doc 54): R_h Goldilocks zones. Liberating (0.35–0.50) → positive affect.
- CREA2 Pathway B (Doc 55/65): High ceiling (R_h > 0.35) → expanded prediction envelope → divergent thinking.
- T5 (from T-series): Enclosure → safety/threat. Low ceiling → enclosure → either safety (intimate scale) or threat (coffin-like).

*Assessment*: VF3 and CREA2B are EXPLICITLY linked as a single causal chain (Doc 64, Debate 3): VF3 → affect → CREA2B. This is correctly handled. But T5's enclosure template predates VF3 and uses a different parameterization (qualitative enclosure levels rather than R_h). If the system activates BOTH T5 and VF3 for the same room, there is a risk of DOUBLE-COUNTING the ceiling height effect. The Doc 64 resolution (VF3 → CREA2B is single chain) addressed the CREA linkage but did NOT address the T5 → VF3 overlap.

*Recommendation*: Explicit deduplication rule: when computing ceiling height effects, use VF3 (quantitative R_h) as the primary template; T5 (qualitative enclosure) should be activated only for enclosure features NOT captured by ceiling height (e.g., wall proximity, structural canopy).

**6c: Noise level recommendations.**

- CREA2 Pathway A (Doc 55/65): 65–75 dB non-semantic ambient noise optimal for divergent thinking
- T32 (Sprint 7.5 inventory): Subcortical encoding requires SNR > +15 dB, RT60 0.4–0.8s
- SOC2 (Doc 57): Acoustic privacy as component of privacy-encounter model
- CREA4 (Doc 65): Individual phase 35–45 dBA; group phase 50–55 dBA; incubation 50–55 dBA

*Assessment*: These are context-dependent recommendations, not contradictions. CREA2 says 65–75 dB for creative ideation; T32 says SNR > +15 dB for speech intelligibility; CREA4 says 35–45 dBA for individual focus. A workspace that alternates between creative and focused modes needs DIFFERENT noise levels at different times — which is exactly what the three-zone model specifies. No genuine contradiction, but the system needs to manage the TRANSITIONS between recommended noise levels. What happens during the 30 seconds between the 45 dBA individual zone and the 65 dBA generative zone? The system is silent on transition acoustics.

**6d: Effect size magnitudes — are they compatible?**

- VF1 contour preference: d ≈ 0.45 beauty, d ≈ 0.35 approach-avoidance (Vartanian VR)
- CREA2 noise: d ≈ 0.42 divergent (Mehta)
- CREA3 walking: d ≈ 0.80 divergent (Oppezzo)
- VIEW1 nature view: dose-response 120 min/week (White et al.)
- L2 circadian: CS ≥ 0.3 (threshold, not effect size)
- SOC2 privacy: N > 42,000 across streams (prevalence, not effect size)

*Assessment*: The effect sizes are heterogeneous — some are Cohen's d (VF1, CREA2, CREA3), some are thresholds (L2), some are dose-response curves (VIEW1), some are prevalence data (SOC2). These CANNOT be directly compared or combined. The system lacks a COMMON EFFECT METRIC. When the system says "VF1 adds d ≈ 0.45 and CREA2 adds d ≈ 0.42," these d values are from different studies, different samples, different outcome measures. Adding them assumes they are on the same scale, which they are not.

*This is a significant methodological problem.* The interaction matrices (CREA2's 2×2×2) assume that d values from different studies can be compared within a single matrix. This is common practice in meta-analysis but requires careful attention to outcome measure equivalence that the system does not provide.

### Verdict

**NO OUTRIGHT CONTRADICTIONS, BUT SIGNIFICANT INTEGRATION PROBLEMS.** The individual panel parameters are internally consistent. The cross-panel issues are: (a) potential double-counting where T-series templates overlap with calibrated domain templates; (b) missing transition parameters between zones; (c) heterogeneous effect metrics that cannot be straightforwardly combined.

**Severity: MODERATE.** These are solvable problems but they need explicit attention before the system can produce integrated assessments.

**Recommendation**: (1) Build a DEDUPLICATION MAP identifying all T-series/domain-series overlaps. (2) Define a common effect metric or explicitly document when metrics are incommensurable. (3) Add transition parameters for environmental shifts between zones.

---

## STRESS TEST 7: THE FOUNDATION GAP

### The Problem

The system has 73 templates distributed as:

| Series | Count | Calibration Status |
|--------|-------|--------------------|
| T-series (T1–T52) | 52 | **UNCALIBRATED** — foundation panels I–V, no calibration panels |
| M-series (M1–M17) | 17 | **UNCALIBRATED** — music panels I–III, no calibration panels |
| AX-series (AX1–AX6) | 6 | **UNCALIBRATED** — auxiliary panel, no calibration panels |
| Domain series (L, MAT, TP, SOC, CREA, VIEW, SC, COL, VF, OLF) | ~33 + CREA4 | **CALIBRATED** (9 of 10 series; OLF1 remaining) |

**75 out of 73 templates are uncalibrated.** Wait — that math doesn't work. The issue: the T-series, M-series, and AX-series overlap significantly with the domain-series templates. L1–L5 were DERIVED FROM T-series light templates; MAT1–MAT5 from T-series material templates; etc. The domain-series templates are the CALIBRATED VERSIONS of concepts that first appeared in the T-series.

But this means the T-series templates that have NOT been superseded by domain-series equivalents remain uncalibrated. How many is that?

- T1 (Spectral Match/Fractal) → partially captured by VF1-VF2 (fractal, scaling) but T1 is specifically about 1/f spectral slopes, which VF2's SCI addresses at a different level of description
- T4 (Attentional Demand) → partially captured by CREA templates but CREA is about creativity, not general attention
- T5 (Enclosure/Threat) → partially captured by VF3 (ceiling) and SOC2 (privacy) but the THREAT pathway specifically is not fully in either
- T6 (Cortisol/Hippocampal) → stress pathway, not in any domain series
- T7 (Allostatic Anticipation) → stress/homeostasis, not in any domain series
- T10 (Consolidation/Restoration) → partially in VIEW1 (restoration channel) but T10 is specifically about sleep-dependent consolidation
- T13 (Nature View Multi-Path) → now VIEW1
- T17 (Dopaminergic Novelty/Reward) → partially in TP templates but reward specifically uncovered
- T19 (Social Affordance Density) → now SOC templates
- T28 (Cognitive Offloading) → referenced in CREA4 but not a standalone calibrated template
- T36 (Working Memory Load) → foundational constraint, referenced everywhere, never calibrated independently

**Estimate: 25–35 T-series templates have NO calibrated domain-series equivalent.** These include critical mechanisms: stress pathways (T6, T7), reward (T17), navigation (T14, T18, T24), memory (T10, T23), and attention (T4, T20). The domain-series calibration panels focused on ARCHITECTURAL FEATURES (light, materials, sound, space) rather than PSYCHOLOGICAL MECHANISMS (stress, reward, memory, attention). This creates a systematic gap: the system is well-calibrated for environmental inputs but poorly calibrated for many of the psychological outputs.

### Verdict

**SIGNIFICANT STRUCTURAL GAP.** The foundation templates contain critical psychological mechanisms (stress, reward, memory, navigation, attention) that have not been calibrated. The project's calibration strategy focused on the ARCHITECTURAL-FEATURE side (what the building does) and neglected the PSYCHOLOGICAL-MECHANISM side (how the person responds). The domain-series captured the architectural input → initial neural response pathway well but left many of the downstream psychological outcomes relying on uncalibrated T-series templates.

**Severity: HIGH.** This is not a gap that can be fixed by more -III panels on existing domain series. It requires a new type of panel — a MECHANISM CALIBRATION panel that takes T6 (stress), T17 (reward), T28 (cognitive offloading), etc. and provides the same quantitative treatment that L-II gave to L1–L5.

**Recommendation**: Inventory the uncalibrated T-series templates. Identify which are: (a) fully superseded by domain-series (can be deprecated), (b) partially captured (need deduplication mapping), (c) entirely uncalibrated (need new panels). Create a MECHANISM PANEL priority queue parallel to the existing DOMAIN panel queue.

---

## STRESS TEST 8: THE EXPERT PANEL METHODOLOGY

### What Are These Panels?

Every panel in the system follows the same format: a group of named researchers (typically 6–8) are convened to provide position statements, debate contested claims, and produce consensus calibrations. The panels are attributed to real, named scientists with real citations.

### The Uncomfortable Truth

**These are not actual expert panels. They are AI-generated simulations of what these experts might say, based on their published work.** No actual expert was consulted. Teresa Amabile did not review CREA4. Ravi Mehta did not provide the noise × light interaction data attributed to his "manuscript under review." Rex Jung did not estimate the neural ceiling of salience network gating.

The system attributes specific claims, effect sizes, and consensus positions to named scientists who have not endorsed these attributions. This is methodologically problematic even though the claims are consistent with the scientists' published positions, because:

1. **Extrapolation beyond published work.** The panels frequently have experts make claims that go beyond their publications — predicting unmeasured interaction effects, estimating parameters for untested conditions, extending findings to novel contexts. These extrapolations may be reasonable but they are the AI's extrapolations, not the experts'.

2. **Consensus fabrication.** The "panel consensus" represents the AI's judgment of what these experts would agree on, informed by their published disagreements. But actual consensus requires actual deliberation, and the outcome is not always predictable from publications.

3. **Citation of unpublished work.** Some panels cite "manuscript under review" or "2024 data" that may or may not exist. Mehta & Huang (2024) on noise × light interactions — is this a real paper? The system treats it as real data, but it was generated as a plausible extension of Mehta's research program.

### The Defense

The panel methodology is a structured way to ORGANIZE EXISTING EVIDENCE, not to generate new evidence. The expert attributions serve as PROVENANCE MARKERS — they indicate which researcher's work supports which claim. The "debates" structure competing views honestly by assigning them to the researchers who have actually published on different sides of the dispute. The methodology is transparent about its nature in the project documentation (David is fully aware these are simulated panels).

When the system says "Mehta provides the noise × light data," this is shorthand for "the following analysis is consistent with Mehta's published research and extends it in the direction his research program suggests." The citation apparatus (APA format with Google Scholar counts) anchors claims to REAL published work even when the specific parameter estimates are extrapolations.

### Verdict

**METHODOLOGICALLY DEFENSIBLE BUT REQUIRES EXPLICIT FRAMING.** The simulated panel format is a powerful tool for organized evidence synthesis. But any external-facing use of this corpus must explicitly state that the panels are AI-assisted evidence syntheses, not transcripts of actual expert consultations. The attribution of specific claims to named researchers must be framed as "consistent with X's published work" rather than "X states."

**Severity: HIGH for external presentation, LOW for internal use.** David understands the methodology. Any publication or external use must reframe the attributions.

**Recommendation**: Add a METHODOLOGY STATEMENT to the corpus front matter. All "expert says" framings should be understood as "analysis consistent with [Expert]'s published work in [Citation]." Distinguish between: (a) claims directly from published papers (cite normally), (b) extrapolations consistent with published work (mark as "consistent with"), (c) AI-generated parameter estimates (mark as "expert-judgment estimate").

---

## STRESS TEST 9: THE TWO-WORLDS PROBLEM

### The Gap Between Documents and Software

The Opus theory work has produced ~20,000+ lines of Markdown across 65 documents. The Claude Code engineering work has completed approximately 3 tasks out of ~45. This creates a two-worlds problem:

**World 1 (Documents)**: 73 templates with rich narrative context, calibration parameters, interaction matrices, lifespan moderators, cultural modifiers, debate records, and design recommendations. All in Markdown. Accessible to humans who read the documents.

**World 2 (Software)**: A partially-built Python/TypeScript codebase with database models, a web of belief system, and the skeleton of a CMR pipeline. The codebase contains approximately NONE of the template knowledge.

**The translation problem is enormous.** Consider what "encoding template CREA4" actually requires:

1. Define a data model that captures: alternation cycle parameters, group size constraints, display density thresholds, transition time limits, psychological safety multiplier, interactions with CREA1–3, SOC2–3, T28, T36
2. Implement the computation: given room measurements + organizational safety score → predicted collaborative creativity effect
3. Handle scope conditions: when does CREA4 activate vs. not? What inputs are required?
4. Handle interactions: CREA4 Phase 1 IS CREA1 Phase 1 — the encoding must avoid double-counting
5. Handle uncertainty: all parameters have confidence intervals that propagate through computation
6. Handle lifespan moderation: developmental multipliers from DEV-I, aging multipliers from AGE-I
7. Handle cultural moderation: organizational culture affects psychological safety baseline

This is not a simple encoding task. It requires DESIGNING A KNOWLEDGE REPRESENTATION that preserves the richness of the document while being computable. The Sprint 7.5 template extraction inventory suggests this has been considered but not executed.

### The Cost of the Gap

Every new panel document (like the one I just wrote for CREA-III) WIDENS the gap. Each panel adds parameters, interactions, and conditions that will eventually need to be encoded. At current production rate (~2 panels per Opus session), the document corpus is growing faster than the software can absorb it. The theory is building technical debt against the engineering.

### Verdict

**THE TWO-WORLDS PROBLEM IS THE PROJECT'S MOST DANGEROUS STRUCTURAL RISK.** Not because either world is bad — both are good work — but because the gap between them is growing, not shrinking. Every panel session should include encoding time, or the theory work will become so large that encoding it becomes impractical.

**Severity: CRITICAL.** If the engineering does not accelerate dramatically, the document corpus will become a beautiful, useless library.

**Recommendation**: (1) FREEZE new theory panels after this audit until Sprint 7 encoding catches up. (2) Every future Opus panel must include a MACHINE-READABLE APPENDIX — a structured YAML/JSON block that Claude Code can directly ingest. (3) Establish a 1:1 rule: no new panel until the previous panel's parameters are encoded.

---

## STRESS TEST 10: THE SKEPTICAL REVIEWER

### Scenario

A reviewer for *Architectural Science Review* receives a paper describing the Article Eater system. What do they say?

**Reviewer 1 (Environmental Psychology):**

"The authors present an ambitious knowledge base of 73 'mechanistic templates' covering architecture-wellbeing relationships. The breadth of coverage is impressive and the attempt to synthesize disparate literatures (thermal comfort, environmental aesthetics, social psychology, creativity research) under a common framework is commendable. However, I have three major concerns:

First, the predictive processing framework is applied with insufficient rigor. While PE provides a plausible account of some phenomena (contour preference habituation, cross-modal material prediction), many templates simply relabel known empirical findings in PE vocabulary without adding explanatory power. The system should clearly distinguish templates where PE generates novel predictions from those where it merely organizes existing findings.

Second, the calibration parameters are almost entirely based on laboratory studies, not architectural field studies. The CCI (Contour Curvature Index), SRV (Spatial Rhythm Variation), and most Goldilocks boundaries have never been validated in actual buildings with actual occupants going about their actual lives. The ecological validity of these parameters is unknown.

Third, the system claims to evaluate architecture-wellbeing relationships but provides no validation against actual building outcomes. Where is the comparison between system predictions and post-occupancy evaluation data? Without this, the system is a hypothesis generator, not an evaluation tool.

Recommendation: Major revision. The theoretical contribution is potentially significant, but the paper must (a) be transparent about the PE framework's variable contribution, (b) acknowledge the ecological validity gap, and (c) demonstrate at least one validated prediction in a built environment."

**Reviewer 2 (Computer Science / Knowledge Systems):**

"The paper describes a knowledge base but provides no working software. The system exists as ~20,000 lines of Markdown documents with no implemented query engine, no database encoding, and no user interface. The CMR pipeline described in the specification documents has not been built. This is a specification, not a system.

The template format mixes narrative text, YAML-like structures, numerical parameters, and natural language scope conditions in a way that would require significant natural language processing to encode programmatically. The authors should either (a) present this as a theoretical contribution (in which case the software claims should be removed) or (b) demonstrate a working prototype (in which case the engineering must be completed first).

Recommendation: Reject as submitted. The contribution as a knowledge base specification may be valuable, but the paper as written implies a working system that does not exist."

**Reviewer 3 (Architecture):**

"As a practicing architect, I find the template system intellectually stimulating but practically unhelpful. The system tells me that my conference room should have R_h between 0.25 and 0.35, CCI between 0.30 and 0.70, illuminance of 400–500 lux for evaluative work, and SCI > 0.60 for visual richness. These are specific numbers, which is refreshing compared to the usual vague guidelines. But:

I cannot measure CCI or SCI — these require image processing of my design that no architectural software currently provides. I cannot measure 'organizational psychological safety baseline' — this is an organizational psychology assessment, not an architectural measurement. The system assumes I have data I don't have and can't easily get.

What I CAN use: R_h (simple calculation), illuminance (standard measurement), RT60 (standard measurement), VIEW1's VQI (structured rubric I can apply). These are genuinely useful design tools. The system should lead with these practically accessible parameters and acknowledge which parameters require specialized measurement.

Recommendation: Restructure around practical accessibility. Lead with what architects can actually use today."

### Verdict

**THE SKEPTICAL REVIEWERS IDENTIFY REAL PROBLEMS.** Every criticism is valid:
1. PE framework is oversold (Stress Test 4 concurs)
2. Ecological validity is unknown (no field validation)
3. The software doesn't exist (Stress Test 1 concurs)
4. Practical accessibility varies widely (some parameters are usable; others require unavailable measurements)

**Severity: HIGH for external presentation. MODERATE for internal development.** The system has genuine value that the reviewers partially acknowledge, but its presentation must be more honest about limitations.

---

## SYNTHESIS: THE STATE OF THE PROJECT

### What Is Actually Good

1. **The calibrated templates are genuinely useful.** L2 circadian, MAT1 thermal, SOC2 privacy, VIEW1 nature view, VF3 spatial proportions — these contain real, evidence-based, quantitative parameters that are more specific and better grounded than anything in existing architectural guidelines. This is a real contribution.

2. **The interaction models are novel.** The CREA2 2×2×2 matrix, the VF1 × VF3 additivity finding, the convergence triad channel weights — these represent genuine synthesis that does not exist elsewhere in the literature.

3. **The lifespan model is comprehensive.** AGE-I + DEV-I provide a unified U-curve moderation framework across 6 template series. This is a novel contribution to environmental gerontology and developmental psychology.

4. **The organizational structure is excellent.** The dual-index cross-reference, the calibration registry, the panel prospectus system — these create a knowledge management infrastructure that enables systematic development.

5. **The debate format preserves uncertainty honestly.** Unlike most design guidelines, this system records where experts disagree, what is preliminary, and what needs validation. The maturity ratings are generally honest at the template level (even if the domain ratings are inflated).

### What Is Actually Bad

1. **THE SOFTWARE DOES NOT EXIST.** This is the headline finding. The project's primary deliverable — a system that evaluates papers — cannot be delivered. The knowledge base is racing ahead of the engineering by a factor of approximately 20:1 (documents to implemented sprints).

2. **The coverage ratings are inflated.** ★★★★ across all 10 domains misrepresents the actual state, which is closer to ★★★ with two domains approaching ★★★½.

3. **75 foundation templates are uncalibrated.** The calibration strategy focused on architectural-feature templates and left critical psychological-mechanism templates (stress, reward, memory, navigation) without quantitative parameters.

4. **No ecological validation.** Zero parameters have been validated in actual built environments. The system is entirely based on laboratory studies and expert extrapolation.

5. **No common effect metric.** The templates produce heterogeneous outputs (Cohen's d, quality indices, categorical zones, thresholds) that cannot be integrated without a linking function that does not exist.

6. **The two-worlds gap is growing.** Every new panel document makes the encoding problem larger. The theory is building technical debt faster than the engineering can pay it off.

### What Needs to Happen

**IMMEDIATE (before any more panels):**

1. **FREEZE theory production.** No more -III panels, no more cross-cutting panels, no new templates. The system has ENOUGH templates. It needs engineering, not more theory.

2. **Define honest coverage ratings.** Create an explicit rubric. Downgrade to honest levels. Identify what each domain needs for genuine ★★★★.

3. **Build the encoding pipeline.** Sprint 7 (template encoding) is the critical bottleneck. Every Opus session should produce MACHINE-READABLE output, not just Markdown narrative.

4. **Develop a linking function.** Design a common metric that enables cross-template integration. This is a theoretical problem that Opus should address before more calibration work.

**SHORT-TERM (next 3–5 sessions):**

5. **Deduplication map.** Identify all T-series / domain-series overlaps. Deprecate superseded T-series templates. Identify gaps.

6. **Mechanism calibration panels.** Address the psychological-mechanism gap: stress (T6, T7), reward (T17), cognitive offloading (T28), working memory (T36).

7. **Machine-readable appendices.** Every existing panel document needs a structured YAML/JSON extract that Claude Code can directly ingest.

**MEDIUM-TERM (next 10+ sessions):**

8. **Ecological validation.** Select 3–5 parameters with the highest practical accessibility (R_h, VQI, illuminance-based metrics) and validate against post-occupancy evaluation data from real buildings.

9. **Practical accessibility stratification.** Classify every parameter as: (A) immediately usable by architects with standard tools, (B) usable with specialized measurement, (C) requires research-grade assessment, (D) requires unavailable technology. Lead all outputs with Category A parameters.

10. **End-to-end demonstration.** Complete the CMR pipeline through Sprint 8. Run the Ulrich 1984 worked example. Publish a demonstration paper showing the full paper → evaluation → design recommendation workflow.

---

## OVERALL GRADE

| Dimension | Grade | Notes |
|-----------|-------|-------|
| **Theory quality** | A− | Templates are well-grounded, debates are honest, PE framework is defensible if oversold |
| **Calibration depth** | B | Individual templates well-calibrated; integration and cross-calibration incomplete |
| **Coverage breadth** | B+ | 10 domains covered; inflated to look better than it is; foundation gap significant |
| **Software readiness** | F | Pipeline not built; templates not encoded; no working system |
| **Practical utility** | C+ | Useful as reference for expert humans; not usable as software tool |
| **Ecological validity** | D | Zero field validation; entirely lab-based |
| **Documentation quality** | A | Excellent organizational structure; clear provenance; honest about uncertainty at template level |
| **Project management** | C | Theory-engineering imbalance is a strategic failure |

**Overall: B−/C+ as a knowledge base specification. F as a working system.**

The project has produced an excellent theoretical foundation and is at serious risk of never turning it into a working tool. The most urgent action is not more theory — it is engineering.

---

*Document 66: Comprehensive Project Audit — V1.0*
*February 17, 2026*
*10 stress tests, honest grades, strategic recommendations*
*Primary finding: The knowledge base is strong (B+/A−); the software is nonexistent (F); the gap is growing.*
*Next: Implement recommendations — starting with theory freeze and encoding sprint*

---

## ADDENDUM: AUDIT CORRECTION (Feb 17 2026, post-Codex reality check)

Codex provided a direct repo audit that contradicts several findings above. Corrections:

### Revised Engineering Assessment

| Claim in Audit | Reality from Codex | Correction |
|---------------|-------------------|------------|
| "3 of ~45 CC tasks done" | Sprints 0, 1, 6, 8, 9 have significant completion; Sprint 7 has 3/6 | **Multiple sprints substantially complete** |
| "Templates not encoded in database" | 150 JSON template files exist under data/templates/; 23 have calibration blocks; all 150 have lifespan_sensitivity_multiplier | **Templates ARE encoded as JSON files (not DB tables, but real structured data)** |
| "Web of belief not operational" | OPERATIONAL: 10,670 beliefs, 25,959 constraints, 1,555 bridges; 62 tests passing | **Web of belief is a working system** |
| "CMR pipeline does not exist" | src/cmr/ is a placeholder stub | **Correct — CMR pipeline IS unbuilt** |
| "Test suite unknown" | 2,945 passed, 9 skipped, green | **Healthy and growing (up from 2,578)** |

### Revised Software Grade

| Dimension | Original Grade | Revised Grade | Reason |
|-----------|---------------|---------------|--------|
| Software readiness | F | **C−/D+** | Significant infrastructure exists; CMR core missing; coordination gap real but narrower than claimed |
| Project management | C | **C+** | Theory-engineering imbalance is real but engineering team has been productive independently |

### Revised Overall

**Overall: B−/C+ as a knowledge base. C−/D+ as a software system (up from F). The gap between theory and engineering is NARROWER than initially assessed, and the primary blocker is a missing CMR contract (now delivered as Doc 68), not engineering capacity.**

### Revised Recommendation

~~FREEZE theory production~~ → The theory freeze was premised on an F-grade software. With a C− software grade and a frozen CMR contract now delivered (Doc 68), the correct strategy is:

1. **Deliver Doc 68 to Claude Code immediately.** The CMR contract is the unblocking artifact.
2. **Fix the 2 enum-drift items** (trivial, clears warnings).
3. **Build the Template DB index** (makes 150 JSON files queryable).
4. **Implement WIS conversion** (common metric from Doc 67).
5. **Build Building Evaluation Pipeline** (S10, ~22 hours estimated).
6. **THEN resume theory panels** — but only in domains identified as Gap in Doc 67 Part 1 (stress, reward, memory, attention, control).
