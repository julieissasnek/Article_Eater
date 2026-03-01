# Expert Panel Evaluations of QA Success Conditions + Extended Use Cases

**Date:** 2026-02-27
**Author:** Gemini (Antigravity)
**Companion to:** `QA_BROWSE_SYSTEM_APPRAISAL_2026-02-27.md`

> Each panel consists of 3 domain experts role-playing the user persona. They evaluate the success conditions from the appraisal document using a concrete test query, scoring each dimension 1–5 and identifying gaps. All panelists are fictional composites drawn from real professional archetypes.

---

## Panel 1: The Architect Panel 🏗️

**Panelists:**
- **Marina Voss** — Principal, biophilic design firm (15 years practice, LEED AP)
- **James Okonkwo** — Healthcare architect specializing in evidence-based hospital design
- **Suki Tanaka** — Computational design researcher, parametric architecture

**Test Query:** *"How should I design a pediatric waiting room to reduce anxiety in children aged 3–8?"*

### Panel Evaluation

| Success Dimension | Score (1–5) | Panel Commentary |
|---|---|---|
| **Provides quantitative thresholds** | 2/5 | Marina: "I need lux ranges, ceiling heights in meters, color temperature in Kelvin. The system gives me mechanisms but not *numbers*. I can't put 'reduced enclosure-threat' in a spec sheet." |
| **Spatial parameters given** | 2/5 | James: "For a pediatric waiting room I need minimum square footage per child, sight-line recommendations, acoustical RT60 targets. The system talks about *what* environments do but not *how big* they should be." |
| **Material recommendations** | 3/5 | Suki: "The template library has haptic/material templates, but the QA doesn't synthesize them into a materials palette. I want: 'use wood surfaces (reduces cortisol per T17), avoid polished concrete (increases acoustic stress per AUD_003).'" |
| **Multi-template synthesis** | 1/5 | Marina: "This is the critical failure. A pediatric waiting room touches biophilia, acoustics, color, spatial enclosure, thermal comfort, AND circadian rhythm. The system answers one template at a time. I need a *design brief* that orchestrates all of them." |
| **Persona-appropriate vocabulary** | 4/5 | James: "The design vocabulary is appropriate. It says 'spatial configuration' not 'hippocampal place cell activation.' Good." |

**Panel Verdict:** The system is **architecturally literate but not architecturally useful**. It explains *why* design decisions matter but doesn't make the decisions. The gap is in synthesis and quantification.

**Panel Recommendations:**
1. 💡 **Design Brief Generator** — A new query mode that takes a room type + population and generates a multi-template synthesis document with quantitative specs.
2. 💡 **Threshold Extraction** — Mine the `calibration_parameters` field from templates and surface specific values (lux, dB, °C, m²) in architect-mode answers.
3. 💡 **Material Palette Mode** — Cross-reference haptic, visual, and thermal templates to produce a materials recommendation matrix.

---

## Panel 2: The Researcher Panel 🔬

**Panelists:**
- **Dr. Elena Marchetti** — Cognitive neuroscientist, environmental perception lab
- **Prof. Kwame Asante** — Environmental psychologist, meta-analysis specialist
- **Dr. Priya Chandrasekaran** — Computational psychiatrist, Bayesian modeling

**Test Query:** *"What is the neural mechanism linking natural light exposure to improved sleep quality in office workers?"*

### Panel Evaluation

| Success Dimension | Score (1–5) | Panel Commentary |
|---|---|---|
| **Effect sizes reported** | 1/5 | Kwame: "No Cohen's d, no odds ratios, no confidence intervals from the primary literature. The system reports its own *credence* values, but those are internal Bayesian posteriors, not the effect sizes from the actual studies. I need both." |
| **Evidence quality assessment** | 3/5 | Elena: "The maturity ratings (established/supported/preliminary) are useful but coarse. I need to see sample sizes, study designs (RCT vs. cross-sectional), and population demographics for each supporting claim." |
| **Gap analysis with study designs** | 4/5 | Priya: "The `ResearchGap` system is genuinely excellent. It identifies weak links, proposes study designs with sample size recommendations, and even suggests measurement instruments. This is better than most systematic review software." |
| **Causal ladder classification** | 5/5 | Kwame: "Pearl's causal ladder integration is superb. Distinguishing 'light is *associated with* sleep' from 'light *causes* sleep improvement' from 'sleep *would have been worse* without light' is exactly what every reviewer should demand." |
| **BN posterior integration** | 2/5 | Priya: "The BN posterior is mentioned in the architecture but I've never seen it surface in an actual QA response. The `integrated_query_service.py` has `bn_posterior` fields but they appear to be None in practice. This is a phantom feature." |

**Panel Verdict:** The system is **epistemically sophisticated but empirically thin**. It classifies evidence beautifully but doesn't report the actual numbers from the primary literature. The gap identification is world-class.

**Panel Recommendations:**
1. 💡 **Effect Size Extraction** — The extraction pipeline should pull Cohen's d, r, odds ratios, and CIs from papers and attach them to beliefs. The QA should report these alongside credence.
2. 💡 **Study Design Badges** — Each evidence item should carry a badge: 🟢 RCT, 🟡 Quasi-experimental, 🟠 Cross-sectional, 🔴 Case study. Researchers filter by design quality.
3. 💡 **Live BN Posteriors** — Fix the phantom BN integration so that `bn_posterior` actually returns computed values. This would make ATLAS the only QA system that gives calibrated uncertainty.

---

## Panel 3: The Facilities Manager Panel 🔧

**Panelists:**
- **Bob Henriksen** — VP Facilities, Fortune 500 tech campus (manages 2M sq ft)
- **Diane Okafor** — Sustainability director, hospital network (12 facilities)
- **Carlos Medina** — Operations manager, K-12 school district (45 buildings)

**Test Query:** *"Will replacing fluorescent lighting with tunable LED in our open-plan office improve productivity enough to justify the cost?"*

### Panel Evaluation

| Success Dimension | Score (1–5) | Panel Commentary |
|---|---|---|
| **Cost-benefit framing** | 1/5 | Bob: "Zero cost data. I need $/sqft for retrofit, energy savings, and estimated productivity gain in $/employee/year. The system tells me *why* tunable LEDs work neurobiologically. I don't care about melanopsin. I care about my budget." |
| **Implementation timeline** | 1/5 | Diane: "No phasing recommendation. Should I do one floor first? How long before we see results? Weeks? Months? The system is silent on temporal implementation." |
| **Measurable outcomes** | 2/5 | Carlos: "The system mentions 'improved circadian entrainment' as an outcome. I can't measure circadian entrainment. Give me: absenteeism rate, self-reported comfort surveys, task completion rates — things my team can actually track." |
| **Risk/downside flagged** | 3/5 | Bob: "The scope conditions mention contexts where the effect may not apply. That's useful — it tells me tunable LEDs won't help in windowless server rooms. But it doesn't flag *implementation risks* like glare complaints or photosensitive employees." |
| **Actionable next steps** | 2/5 | Diane: "I'd want: 'Step 1: Audit current lux levels. Step 2: Pilot one floor. Step 3: Measure absenteeism over 90 days. Step 4: Calculate ROI.' The system gives me science, not a project plan." |

**Panel Verdict:** The system is **scientifically rigorous but operationally useless** for facilities managers. It answers "should I?" with "here's the neuroscience" when the user needs "here's the project plan."

**Panel Recommendations:**
1. 💡 **ROI Calculator Mode** — For FACILITIES persona, translate mechanism templates into cost-benefit estimates using published benchmarks (e.g., World Green Building Council productivity data).
2. 💡 **Implementation Playbook** — Generate a phased project plan: audit → pilot → measure → scale. Include specific KPIs to track.
3. 💡 **Proxy Metrics Translation** — Map every scientific outcome ("circadian entrainment") to a facilities-measurable proxy ("absenteeism rate," "sick days per quarter").

---

## Panel 4: The Student Panel 📚

**Panelists:**
- **Alex Chen** — 3rd year architecture student, first exposure to neuroarchitecture
- **Fatima Al-Rashid** — PhD student, cognitive science, studying for qualifying exams
- **Marcus Johnson** — Masters in public health, elective in built environment

**Test Query:** *"Why does natural lighting make people feel better in buildings?"*

### Panel Evaluation

| Success Dimension | Score (1–5) | Panel Commentary |
|---|---|---|
| **Jargon-free explanation** | 3/5 | Alex: "The headline level is great — plain English, one sentence. But the moment I click into detail, I'm hit with 'melanopic lux,' 'ipRGC activation,' 'SCN entrainment.' I need a glossary sidebar or progressive terminology introduction." |
| **Step-by-step mechanism** | 4/5 | Fatima: "The causal chain visualization (environment → neural → cognitive → behavioral) is exactly what I need for my qualifying exam. I can trace the logic. Each link has a maturity rating. This is pedagogically strong." |
| **Analogies and examples** | 1/5 | Marcus: "Zero analogies. The system never says 'think of it like…' or 'for example, in Hospital X, they found…' It's all abstraction. Students learn from concrete cases." |
| **Learning path suggested** | 1/5 | Alex: "No curriculum. I don't know what to read first. Should I understand predictive processing before circadian biology? The system treats every question as standalone. I need a map of prerequisite knowledge." |
| **Practice questions** | 0/5 | Fatima: "The follow-up questions are good, but they're not *practice questions*. For exam prep, I'd want: 'Explain 3 mechanisms by which natural light affects occupant wellbeing. Cite at least one study per mechanism.' The system could generate these from its template library." |

**Panel Verdict:** The system is **structurally excellent for learning but pedagogically passive**. It has the knowledge to be a great tutor but presents it as a reference, not a curriculum.

**Panel Recommendations:**
1. 💡 **Glossary Sidebar** — Every technical term gets a hover-definition on first use. Progressive: L1 uses plain English, L2 introduces terms with definitions, L3 uses terms freely.
2. 💡 **Concrete Case Studies** — Mine the extraction database for named buildings, real interventions, specific study locations. "In the Khoo Teck Puat Hospital (Singapore), biophilic design reduced patient anxiety by 37% (credence 0.68)."
3. 💡 **Learning Path Generator** — For STUDENT persona, generate prerequisite chains: "To understand this answer fully, first read about: (1) Circadian Biology [§CB], (2) Predictive Processing [§PP], (3) Stress Physiology [§NM]."
4. 💡 **Exam Question Generator** — Generate practice questions at Bloom's taxonomy levels: Remember, Understand, Apply, Analyze, Evaluate, Create.

---

## Panel 5: The Policy Maker Panel 📜

**Panelists:**
- **Commissioner Sarah Lindqvist** — Building codes division, Nordic country
- **Dr. Raj Patel** — WHO advisor, healthy built environments initiative
- **Assemblywoman Keiko Nakamura** — State legislator sponsoring healthy buildings bill

**Test Query:** *"Should we require minimum daylight access in all new residential buildings to improve population mental health?"*

### Panel Evaluation

| Success Dimension | Score (1–5) | Panel Commentary |
|---|---|---|
| **Population-level evidence** | 2/5 | Raj: "The system gives me mechanism-level evidence (individual circadian effects) but not population-level data. I need: 'In countries with daylight mandates, depression rates are X% lower (controlling for latitude and GDP).' Ecological studies, not lab experiments." |
| **Standards/codes referenced** | 1/5 | Sarah: "No mention of existing standards — EN 17037, WELL Building Standard daylight credits, LEED IEQ credits. I need to know what already exists before proposing new requirements." |
| **Equity considerations** | 1/5 | Keiko: "Who is harmed by *not* having daylight? Low-income housing, basement apartments, shift workers. The system doesn't flag equity dimensions. A mandate affects the vulnerable most — that's the political argument, and the system doesn't help me make it." |
| **Cost of inaction** | 2/5 | Raj: "I need to say: 'Insufficient daylight costs the healthcare system $X billion annually in depression treatment.' The system has the causal chain (light → mood) but not the economic modeling." |
| **Implementation feasibility** | 1/5 | Sarah: "What percentage of existing building stock would fail a 300 lux mandate? What's the renovation cost? What's the exemption process for heritage buildings? The system can't answer any operational policy question." |

**Panel Verdict:** The system provides **scientific justification but not political ammunition**. Policy requires numbers at the population and economic scale, not individual mechanism descriptions.

**Panel Recommendations:**
1. 💡 **Standards Cross-Reference** — Maintain a registry of existing building codes/standards (EN 17037, WELL, LEED, BREEAM) and cross-reference them with template evidence. When a user asks a policy question, show which standards already address it.
2. 💡 **Equity Impact Layer** — For POLICY persona, flag differential impacts by socioeconomic status, housing type, and demographic group.
3. 💡 **Population Extrapolation Mode** — If we know the individual effect (Cohen's d = 0.4 for daylight → mood), and we know the population distribution of daylight access, we can estimate the population-attributable fraction of mood disorders due to inadequate daylight.
4. 💡 **Cost-of-Inaction Calculator** — Combine mechanism evidence with healthcare cost data to produce economic arguments.

---

## Panel 6: The Clinician Panel 🩺

**Panelists:**
- **Dr. Amara Obi** — Psychiatrist, inpatient psychiatric unit redesign committee
- **Dr. Henrik Johansson** — Rehabilitation medicine, sensory environment specialist
- **Dr. Mei-Lin Wu** — Geriatrician, dementia care environments

**Test Query:** *"What environmental modifications can reduce sundowning episodes in dementia patients?"*

### Panel Evaluation

| Success Dimension | Score (1–5) | Panel Commentary |
|---|---|---|
| **Patient population specificity** | 3/5 | Mei-Lin: "The system knows about circadian disruption and light exposure, which applies to dementia. But it doesn't distinguish Alzheimer's from Lewy body dementia — the circadian pathology is different and the interventions differ." |
| **Contraindications flagged** | 1/5 | Henrik: "Bright light therapy can trigger seizures in photosensitive patients. High-contrast flooring can cause visual illusions in Lewy body dementia. These contraindications are clinically critical and the system mentions *none* of them." |
| **Therapeutic dosing** | 2/5 | Amara: "For light therapy, I need: what intensity (2,500–10,000 lux), what duration (30–120 min), what time of day (morning vs. afternoon), what spectral composition (blue-enriched vs. full spectrum). Some templates have calibration parameters, but they're not surfaced in the clinical context." |
| **Interaction effects** | 1/5 | Mei-Lin: "My patients are on melatonin supplements, antipsychotics, and cholinesterase inhibitors. Does bright light interact with melatonin dosing? Does acoustic environment affect antipsychotic efficacy? The system has no pharmacological interaction layer." |
| **Evidence grade for clinical use** | 2/5 | Henrik: "For clinical decisions I need GRADE evidence ratings (High/Moderate/Low/Very Low), not 'maturity' levels. The maturity system is epistemologically interesting but not clinically actionable. I need to know if this is guideline-level evidence." |

**Panel Verdict:** The system has **relevant knowledge but is clinically dangerous** in its current form. It omits contraindications, doesn't grade evidence for clinical use, and ignores pharmacological interactions. A clinician using this system uncritically could harm patients.

**Panel Recommendations:**
1. 💡 **Contraindication Registry** — For each template, maintain a list of conditions where the intervention is contraindicated or requires caution. Surface prominently for CLINICIAN persona.
2. 💡 **GRADE Evidence Mapping** — Map the maturity ratings to GRADE system equivalents (established → High, supported → Moderate, preliminary → Low, speculative → Very Low).
3. 💡 **Clinical Protocol Mode** — For CLINICIAN persona, format answers as clinical protocols: Indication, Contraindications, Dosing, Monitoring, Expected Timeline, When to Escalate.
4. 💡 **Interaction Awareness** — Flag when environmental interventions may interact with common pharmacological treatments in the target population.

---

## Consolidated Cross-Panel Scoring Matrix

| Dimension | Architect | Researcher | Facilities | Student | Policy | Clinician | **Mean** |
|---|---|---|---|---|---|---|---|
| Core need met | 2.4/5 | 3.0/5 | 1.8/5 | 1.8/5 | 1.4/5 | 1.8/5 | **2.0/5** |
| Strongest dimension | Vocabulary | Causal ladder | Risk flagging | Mechanism chain | Mechanism | Population relevance | — |
| Critical gap | Multi-template synthesis | Effect sizes | ROI/cost | Analogies, curriculum | Equity, standards | Contraindications | — |

> **Overall Verdict:** The system scores an average of **2.0/5** across all personas. It is uniformly strong on *explaining mechanisms* and uniformly weak on *translating mechanisms into persona-specific actionable outputs*. The knowledge is there; the last mile of delivery is not.

---

## Extended Use Cases (Beyond the Original 4) 💡

### Use Case 5: Post-Occupancy Diagnostician
**Persona:** Facilities + Researcher
**Scenario:** A new office building has been occupied for 6 months. Employees report headaches, difficulty concentrating, and poor sleep. The facilities manager uploads the building's environmental data (lux levels, noise dB, temperature, CO₂) and asks: *"What is causing these complaints?"*

**System Response (envisioned):**
The system cross-references the symptom profile against its template library and produces a differential diagnosis:
1. **Most likely:** Insufficient melanopic lux (measured: 180, threshold: 250+) → circadian disruption → poor sleep → daytime fatigue (Template CB_003, credence 0.72)
2. **Contributing:** CO₂ above 1000 ppm during afternoon → cognitive load increase (Template RESP_001, credence 0.65)
3. **Unlikely but check:** Acoustic masking frequency mismatch causing auditory fatigue (Template AUD_005, credence 0.45)

**What we'd need to build:** Environmental data ingestion API, symptom-to-mechanism reverse mapping, ranked differential diagnosis engine.

---

### Use Case 6: The Grant Proposal Assistant
**Persona:** Researcher
**Scenario:** A researcher is writing an NSF grant on "biophilic design in neonatal intensive care units." They ask: *"What is the state of evidence for nature exposure reducing stress in premature infants, and where are the critical gaps?"*

**System Response (envisioned):**
1. **Evidence summary** with effect sizes from extracted papers
2. **Gap analysis** showing that no RCTs exist for nature exposure in NICU settings (only observational studies in adult hospitals)
3. **Proposed study design** auto-generated from the gap predictor: "Cluster-randomized trial, 4 NICUs, biophilic vs. standard environment, primary outcome: cortisol saliva assay at 72 hours, secondary: length of stay"
4. **Significance paragraph** drafted from template evidence: "This study would fill a critical gap (VOI score 0.82) in the evidence base for environmental interventions in neonatal care..."

**What we'd need to build:** Grant-writing template formatter, auto-significance paragraph from VOI scores, study design generator connected to the gap predictor.

---

### Use Case 7: The Design Review Critic
**Persona:** Architect + Researcher
**Scenario:** An architect uploads a floor plan (or describes it) and asks: *"Critique this hospital room design from a neuroarchitecture perspective."*

**System Response (envisioned):**
1. **Strengths:** "Window placement provides daylight access from bed position (aligns with Template CB_001). Natural materials on wall surface (aligns with Template HAPTIC_002)."
2. **Risks:** "Bed faces away from door → increased vigilance/threat response (contradicts Template PP_ENCLOSURE_003). No acoustic separation from corridor → sleep disruption (contradicts Template AUD_REVERBERATION_003)."
3. **Missing:** "No biophilic element within direct sight-line from bed. Template BIOPHILIA_001 recommends nature view or living plant within 3m of patient head."
4. **Suggested modifications** ranked by impact and cost.

**What we'd need to build:** Spatial description parser (or image analysis), template-to-spatial-feature mapping, design critique generator.

---

### Use Case 8: The Systematic Review Accelerator
**Persona:** Researcher
**Scenario:** A researcher asks: *"Generate a PRISMA-style evidence map for all studies on acoustic environment and cognitive performance."*

**System Response (envisioned):**
1. Auto-filter the 812 papers for acoustic + cognitive keywords
2. Extract and tabulate: Author, Year, N, Design, Acoustic Variable, Cognitive Outcome, Effect Size, Quality Rating
3. Generate a forest plot of effect sizes across studies
4. Identify publication bias via funnel plot analysis
5. Flag studies that contradict the majority finding

**What we'd need to build:** Automated PRISMA table generator from extraction database, forest plot rendering, publication bias analysis (already partially in `stability_engine.py`).

---

### Use Case 9: The Cross-Cultural Consultant
**Persona:** Policy + Architect
**Scenario:** A Middle Eastern architect asks: *"How should biophilic design principles be adapted for desert climates where 'nature' means sand, not trees?"*

**System Response (envisioned):**
1. Identify which biophilic templates are **climate-dependent** (outdoor nature views → interior courtyard gardens in arid climates)
2. Identify which are **climate-independent** (fractal patterns, natural materials, water sounds)
3. Flag cultural moderators: privacy requirements (mashrabiya screens modify enclosure-threat dynamics), gender-segregated spaces
4. Cite cross-cultural studies where available, flag where WEIRD (Western, Educated, Industrialized, Rich, Democratic) bias limits generalizability

**What we'd need to build:** Climate adaptation layer for templates, cultural moderator database, WEIRD bias flag on each evidence item.

---

### Use Case 10: The Real-Time Monitoring Dashboard
**Persona:** Facilities
**Scenario:** A smart building feeds live sensor data (light, temperature, CO₂, noise, occupancy) to ATLAS. The system continuously evaluates: *"Are current conditions supporting or undermining occupant wellbeing?"*

**System Response (envisioned):**
- 🟢 **Daylight:** 450 melanopic lux (above 250 lux threshold, Template CB_001)
- 🟡 **Noise:** 52 dB (approaching 55 dB threshold, Template AUD_003)
- 🔴 **CO₂:** 1,200 ppm (above 1,000 ppm threshold, Template RESP_001)
- **Recommendation:** Increase ventilation rate in Zone 3. Predicted improvement: concentration +8% (credence 0.65)

**What we'd need to build:** Real-time sensor API, threshold comparison engine from template calibration parameters, alert system.

---

### Use Case 11: The Interdisciplinary Translator
**Persona:** Any
**Scenario:** A neuroscientist and an architect are in a meeting. The neuroscientist says "amygdala hyperactivation due to enclosure-threat." The architect needs this translated to: "the ceiling is too low and the walls are too close."

The system receives: *"Translate 'amygdala hyperactivation from enclosure-threat' into architectural language."*

**System Response (envisioned):**
- **Neuroscience:** Enclosed spaces activate threat circuits (amygdala → sympathetic NS → cortisol release)
- **Architecture:** Ceiling height below 2.7m AND room width below 3.5m increases perceived enclosure
- **Design Recommendation:** Minimum 3.0m ceiling, visual access to distance (windows or transparency), curved vs. angular wall profiles reduce threat response by ~15%
- **Bridging Template:** PP_ENCLOSURE_THREAT_001

**What we'd need to build:** Bidirectional vocabulary bridge (neuroscience ↔ architecture ↔ facilities ↔ policy), with persona-aware rendering.

---

## Implementation Priority Summary

| Use Case | Complexity | Impact | Priority |
|---|---|---|---|
| UC5: Post-Occupancy Diagnostician | High | Very High | P1 |
| UC6: Grant Proposal Assistant | Medium | High | P1 |
| UC7: Design Review Critic | Very High | Very High | P2 |
| UC8: Systematic Review Accelerator | Medium | High | P2 |
| UC9: Cross-Cultural Consultant | Medium | Medium | P2 |
| UC10: Real-Time Monitoring | Very High | Very High | P3 (infrastructure) |
| UC11: Interdisciplinary Translator | Low | High | P1 |

---

*This document was generated by Gemini (Antigravity) on 2026-02-27. All panel evaluations are role-played by the AI based on documented professional archetypes and real-world information needs. They represent realistic but fictional expert opinions designed to stress-test the system's design. Use cases marked 💡 are speculative proposals requiring further design and user validation.*
