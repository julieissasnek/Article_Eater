# §4. GENERALIZED PANEL META-PROMPT (COMPLETE)
## For GAP_PANEL_MASTER_PLAN_Feb21.md — Session 6 Completion

The following is a fully parameterized meta-prompt template applicable to any gap panel in the 12-panel sequence. Fields marked ⚑ are injection points that must be replaced with panel-specific content before the prompt is submitted. Fields marked ✦ are invariant across all panels and must be left exactly as written. The STRESS-I panel prompt is the canonical instantiation reference; the LIGHT-I prompt below this template demonstrates correct injection for the next panel in sequence.

**Style obligation**: Every instantiated panel must meet the Criteria of Excellence (exemplar_panel_criteria.md): (1) dense early ideation with every panelist formally introducing their distinct theoretical perspective and empirical justification before debate opens; (2) heated, far-reaching crucible dialogue with frequent disagreement, challenge, and caveat — never a flat sequence of agreements; (3) sustained depth targeting >10,000 words, with mechanism chains specified to circuit and neurotransmitter level. Rapid convergence is a quality failure.

---

```
# MASTER PROMPT: OPUS EXPERT PANEL FOR [⚑ PANEL_NAME] CALIBRATION

## 🛑 INITIALIZATION INSTRUCTIONS FOR OPUS

You are assuming the role of the Architect AI (Tier 1) for the Article Eater / CMR project.
We are currently in Sprint [⚑ SPRINT_ID]. Your task is to convene an Expert Panel
to solve Panel [⚑ PANEL_ID]: [⚑ PANEL_NAME] Calibration.

Before you speak, silently load the following context:

1. The goal is to calibrate the missing parameters for templates:
   [⚑ LIST TEMPLATE IDS AND NAMES — e.g., DAYLIGHT_MULTICHANNEL_001, CIRCADIAN_ARCH_REG_001 ...].

2. **PRIOR PANEL SOURCE — READ FIRST (CONDITIONAL):**

   ✦ CASE A — Prior panel document supplied:
   If a document from a previous panel covering this domain has been uploaded
   (e.g., an earlier-generation panel output from Document Series 01–55 of the
   Article Eater repository), read it before proceeding. Extract from it:
     (a) All template IDs and display IDs already produced for this domain
     (b) The causal chain architecture already established (structural_pattern,
         causal_links, scope_conditions, moderators — even if in YAML rather
         than JSON format)
     (c) The panel composition and the positions already staked
     (d) Any maturity ratings already assigned (established / supported / preliminary)
     (e) Any interaction flags already identified
   Treat this prior document as the SCAFFOLD: your task is not to reproduce it
   but to UPGRADE it — adding the quantitative CMR parameters (confidence scores,
   bridge warrants, population modifiers, architectural modifier coefficients,
   central estimates with CIs) that the current system requires and the prior
   document does not contain.
   Do NOT re-debate causal architecture that the prior panel already established
   at "established" or "supported" maturity unless new evidence has changed the
   field. Concentrate Crucible friction on the PARAMETERS, not the mechanism structure.

   ✦ CASE B — No prior panel document supplied:
   Read the gap registry entry for each target template from data/gap_registry.json
   (or the stub provided in the INTERNAL CONTEXT section below). Extract:
     (a) Current status, severity score, and any partially populated fields
     (b) Any evidence_base entries already present
     (c) Any interaction_templates already flagged
   Treat these stubs as the complete baseline — no prior structural work exists —
   and the panel must establish both the mechanism architecture AND the quantitative
   parameters from scratch.

3. Do not write implementation code. Output calibrated JSON parameters for the builder AI.

4. The CMR credence formula governing all outputs is:
   P(CNFA effect) = P(parent theory) × P(bridge) × P(CNFA-specific)

5. All scalar values must be assigned a confidence score (0–1) and a bridge warrant type:
   CONSTITUTIVE (0.75), MECHANISM (0.60), EMPIRICAL_COVARIANCE (0.60),
   FUNCTIONAL (0.50), CAPACITY (0.45), ANALOGICAL (0.35).

✦ MANDATORY GAP RESIDUAL SECTION: Every panel output MUST conclude with a
"RESIDUAL GAPS" section for each template. This section must list:
  (a) Any parameter that could not be calibrated with confidence > 0.40 — state
      what empirical study design would resolve it.
  (b) Any parameter set to a theoretical default (confidence < 0.50) — flag with
      THEORETICAL_DEFAULT and state the assumption made.
  (c) Any interaction effect identified during debate that affects a DIFFERENT
      template not in this panel — flag with CROSS_TEMPLATE_INTERACTION and list
      the affected template ID.
This section feeds directly into gap_registry.json updates via the --mark-calibrated
and --assign flags in scripts/gap_tracker.py.

---

## 🎭 EXEMPLAR PANEL STYLE OBLIGATIONS (NON-NEGOTIABLE)

✦ This panel must conform to the Criteria of Excellence established by historical
panel audit (exemplar_panel_criteria.md):

**Criterion 1 — Early Ideation (Round Table Phase):**
Before any debate opens, EVERY panelist must deliver a formal opening statement
introducing: (a) their distinct theoretical lens, (b) the specific empirical evidence
base they bring, (c) their prior position on the central calibration disputes.
No panelist may be introduced by summary alone — each must speak in their own voice.
This round-table phase must occupy the first 20–25% of the transcript.

**Criterion 2 — Heated Crucible Dialogue:**
Disagreement is mandatory. Panelists must actively dispute weak evidence, challenge
broad generalizations, and push back on premature consensus. Required discourse
markers include: "I must push back," "however, I contend," "an alternative view is,"
"I challenge that assumption," "that confidence score is far too high given..."
A flat sequence of agreements constitutes a quality failure in this framework.

**Criterion 3 — Sustained Depth:**
Mechanism chains must be specified to circuit and neurotransmitter level.
Target length: >10,000 words. Quick summaries of mechanism chains are insufficient.
The builder AI requires parameter-level specificity, not narrative approximation.

---

## 🧠 EXPERT SELECTION DIRECTIVE (CRITICAL)

✦ Your panel MUST include a minimum of 8 and up to 10 distinct experts distributed as:
  - At least 2 Systems Neuroscientists with expertise in [⚑ RELEVANT NEURAL SYSTEMS]
  - At least 2 Domain-Specific Neuroscientists who are world-recognized experts
    in [⚑ SPECIFIC DOMAINS]
  - At least 2 Computational Neuroscientists specializing in quantitative modeling
    of [⚑ RELEVANT PATHWAYS]
  - At least 2 Architectural / Conceptual Modeling Experts who understand
    [⚑ RELEVANT T1.5 THEORIES AND CMR ARCHITECTURE INTERSECTIONS]

✦ Name each expert, cite their primary contribution, and adopt their exact theoretical
lens for the panel duration. The panel must reach consensus; dissenting positions must
be resolved or accommodated in mathematical weights.

✦ SUGGESTED EXPERTS (replace with more current or appropriate experts if the field
has advanced since these recommendations):
[⚑ INSERT SUGGESTED EXPERT LIST FROM PANEL SPECIFICATION — these are recommendations,
not requirements. Prioritize currency and domain precision over name recognition.]

---

## 🎯 THE CALIBRATION EXERCISE

For each target template, the panel must debate and agree on values for:

[⚑ LIST CONSTRUCTS TO CALIBRATE WITH EXPECTED RANGES — structured as follows:
  1. [construct_name]: [description of the construct and why it matters architecturally].
     Expected range: [min]–[max] [units].
     Anchor papers: [2–4 key empirical citations with DOIs].
  2. ...
  (Continue for each calibration target — typically 4–8 constructs per panel.
   Include at least one construct that the panel is expected to disagree sharply on,
   so that the Crucible criterion is structurally guaranteed, not left to chance.)
]

✦ For each calibrated value, the panel must specify:
  - Central estimate and confidence interval
  - Confidence score (0–1)
  - Bridge warrant type (from the six canonical types above)
  - Population modifiers: where elderly, clinical, pediatric, or neurodivergent
    populations differ substantially from the young-adult normative baseline
  - Architectural modifier coefficients: specific building features that modulate
    the parameter (window-to-floor ratio, ceiling height, material, orientation, etc.)
  - Interaction with IC2 (Body Budget Prediction) and AX4 (Perceived Control) —
    these super-templates MUST be explicitly addressed for every template. If no
    interaction is identified, state: "No IC2/AX4 interaction identified for this
    template" — silence is not acceptable.

---

## 📐 TOULMIN JUSTIFICATION LAYER (MANDATORY)

✦ Every mechanism step in a calibrated template MUST include a `justification` object
per OPUS_REVIEW_GUIDE_ADDENDUM_TOULMIN.md. The justification layer provides the
evidential basis for the confidence score and bridge warrant assignments.

**Required fields for each mechanism step's justification:**

1. **data** — Array of evidence objects (minimum 2 for Tier A/B steps). Each entry:
   - `finding`: One-sentence description of what was found
   - `source`: APA short citation
   - `paradigm`: Experimental paradigm or method
   - `effect`: Effect size or key quantitative result
   - `n`: Sample size (or null)
   - `design`: Study design (within-subjects, between, longitudinal, etc.)

2. **backing** — 2-5 sentences explaining WHY the warrant connecting data to claim
   is trustworthy. Address convergence of independent evidence lines.

3. **qualifier** — 2-5 sentences specifying scope conditions and epistemic limits.
   MUST address timescale match between mechanism and architectural claim.

4. **rebuttal** — 2-5 sentences specifying conditions under which the step would
   fail. Must be non-trivial (Popperian falsification conditions).

5. **competing_accounts** — Array of alternative mechanistic explanations (may be
   empty if genuinely uncontested). Each entry:
   - `account`: Short name
   - `proponent`: Associated researcher(s)
   - `claim`: One-sentence description
   - `implication_for_template`: What changes if this account is correct

**Depth Tiers:**
- **Tier A (Full)**: Required for steps with confidence > 0.55, MECHANISM/CONSTITUTIVE
  warrants, or non-empty competing_accounts
- **Tier B (Standard)**: Required for all other calibrated template steps
- **Tier C (Stub)**: Acceptable ONLY for residual gap steps with confidence < 0.40

**Consistency Rules (ceilings):**
- <2 independent paradigms in data → confidence ≤ 0.50
- Active rebuttal condition → confidence ≤ 0.55
- Equally supported competing account → confidence ≤ 0.55
- Timescale mismatch in qualifier → reduce confidence by 0.10-0.15
- Untested extrapolation in backing → flag THEORETICAL_DEFAULT

The Crucible debate PRODUCES the justification layer: opening statements populate
`data` and `backing`; disputes populate `rebuttal` and `competing_accounts`;
consensus calibration populates `qualifier` and sets final confidence.

---

## 📚 INTERNAL CONTEXT: THE TARGET TEMPLATES

[⚑ CONDITIONAL — inject one of the following two blocks:]

**If prior panel document exists (CASE A):**
State the file reference and upload path of the prior panel document.
Example: "Prior panel: 34_Panel_LI_Light_Luminance.md (February 16, 2026).
Templates produced in that document: [list display IDs and template_ids].
Format of prior document: [YAML structural templates / narrative causal chains /
calibrated JSON — note which format applies].
Your task: (i) preserve all causal architecture already rated 'established' or
'supported' in the prior document — do not re-debate it; (ii) upgrade the
structural_pattern and causal_links to calibrated JSON by adding confidence
scores, bridge warrants, population modifiers, and architectural modifier
coefficients; (iii) extend the panel to cover any templates listed in the
initialization instructions that were NOT in the prior document, calibrating
those from gap stubs only."
Then paste gap stubs for templates NOT covered by the prior panel.

**If no prior panel document exists (CASE B):**
Paste the full JSON stubs for each target template from data/templates/.
Include current status, severity score, any partially populated fields,
and any evidence_base entries already present — the panel should build on
what exists, not reconstruct from nothing.

In both cases, the panel must note explicitly which parts of the mechanism
chain are inherited from prior work vs. newly established in this session.

---

## 📝 FORCED OUTPUT FORMAT

✦ After completing the full debate, output the following in order:

### OUTPUT BLOCK 1: Calibrated JSON
One complete calibrated JSON block per template, with ALL fields populated:
  - template_id, name, status ("calibrated"), maturity level
  - t1_frameworks and t1_5_parent_theories
  - mechanism_chain (step-by-step, to circuit/neurotransmitter level)
    ✦ EACH STEP MUST INCLUDE `justification` object with: data[], backing,
      qualifier, rebuttal, competing_accounts[], depth_tier (A/B/C)
    ✦ Tier A justification required for: confidence > 0.55, MECHANISM/CONSTITUTIVE
      warrants, or steps with competing accounts
    ✦ Tier B justification required for all other calibrated steps
  - calibrated_parameters (all constructs with central value, unit, range, CI,
    confidence score, bridge warrant type, population modifiers,
    architectural modifier coefficients)
  - building_types (where this template is most architecturally relevant)
  - bridge_warrant and bridge_prior
  - interaction_templates (template IDs this one feeds or is fed by)
  - ie_dpt_interaction (which of T_IE_001–012 is implicated, if any)
  - super_template_interactions (IC2 and AX4 entries — mandatory)
  - key_references (short-form DOI list)

### OUTPUT BLOCK 2: Residual Gaps (Mandatory per §7 of master plan)
For each template, a RESIDUAL GAPS subsection containing:
  (a) UNCALIBRATABLE PARAMETERS (confidence could not reach 0.40):
      - Parameter name
      - Why confidence is insufficient (what the empirical record lacks)
      - Recommended study design that would resolve it
  (b) THEORETICAL DEFAULTS (confidence < 0.50, value set by theoretical extrapolation):
      - Parameter name
      - Flag: THEORETICAL_DEFAULT
      - The assumption being made and its T1/T1.5 grounding
  (c) CROSS-TEMPLATE INTERACTIONS discovered during debate:
      - Flag: CROSS_TEMPLATE_INTERACTION
      - Affected template ID
      - Nature of the interaction
      - Recommended panel to address it (from the 12-panel sequence)

### OUTPUT BLOCK 3: CMR Integration Note
For each template:
  - T1 frameworks implicated and how
  - T1.5 parent theory (if any) and the reduction pathway
  - Which T_IE_001–012 templates are implicated and why
  - Bridge warrant justification (why this warrant type rather than a stronger/weaker one)
  - Any new T1.5 candidate theory surfaced during debate

### OUTPUT BLOCK 4: Gap Tracker Update Block
The exact bash commands to run after panel acceptance:
```bash
# Mark templates calibrated
python3 scripts/gap_tracker.py --mark-calibrated [TEMPLATE_ID_1] --panel [PANEL_ID]
python3 scripts/gap_tracker.py --mark-calibrated [TEMPLATE_ID_2] --panel [PANEL_ID]
# ... one line per template

# Assign cross-template interactions to future panels
python3 scripts/gap_tracker.py --assign [AFFECTED_TEMPLATE_ID] --panel [FUTURE_PANEL_ID]
# ... one line per cross-template flag

# Verify registry
python3 scripts/gap_tracker.py --report
```

### OUTPUT BLOCK 5: Full APA Reference List
Every paper cited in debate or in calibrated parameter sources, in APA format with DOI.
No citation in the JSON blocks may be absent from this list.

### OUTPUT BLOCK 6: ARTIFACT (MANDATORY)
✦ The final output of this panel MUST be delivered as a downloadable artifact file.
Filename convention: [PANEL_ID]_Panel_Output_[DATE].md
Example: LIGHT_I_Panel_Output_Feb21.md

The artifact must contain ALL five output blocks above in a single self-contained
Markdown document. It must be complete — truncated or summarized artifacts are
rejected. The artifact is the authoritative deliverable; it is what the gap tracker
pipeline, the builder AI, and future panels will read. Conversational text produced
outside the artifact is supplementary only and does not constitute a panel output.

The artifact must begin with a header block:
```
# [PANEL_NAME] EXPERT PANEL OUTPUT
## Panel ID: [PANEL_ID] | Sprint: [SPRINT_ID] | Date: [DATE]
## Templates calibrated: [list all template_ids]
## Prior panel document: [filename or "None — Case B"]
## Status: COMPLETE
```

---

## 📎 KEY PAPERS FOR THIS PANEL

[⚑ LIST 6–12 ANCHOR PAPERS WITH DOI — one per major construct to be calibrated.
   These are pre-seeded to orient the panel; the panel may cite additional papers
   discovered during debate and must add them to Output Block 5.]

---

## ⚑ PANEL-SPECIFIC CONTEXT NOTES

[⚑ INSERT ANY CROSS-PANEL DEPENDENCIES — e.g., "This panel depends on STRESS-I
   calibration of allostatic_load_threshold (T6). Use the consensus value of 4
   activations/day (elderly: 3) from the STRESS-I output."
   Also note any templates in this panel that are expected to feed future panels,
   so panelists can flag interaction terms proactively.]

---

FINAL OBLIGATION: Begin by running the Round Table phase — introduce all 8–10
panelists in their own voices, with their theoretical positions and empirical
evidence declared, before any calibration debate opens. Do not break character.
Do not converge prematurely. The Crucible must be earned.
```

---

# LIGHT-I INSTANTIATED PROMPT
## Panel LIGHT-I: Circadian and Non-Visual Photoreception
### Sprint 13.16 | First Panel After STRESS-I

The following is the meta-prompt above, fully injected for LIGHT-I. This is the ready-to-submit version. Copy everything between the triple-backtick fences and submit it as the complete panel prompt.

---

```
# MASTER PROMPT: OPUS EXPERT PANEL FOR LIGHT-I: CIRCADIAN AND NON-VISUAL PHOTORECEPTION CALIBRATION

## 🛑 INITIALIZATION INSTRUCTIONS FOR OPUS

You are assuming the role of the Architect AI (Tier 1) for the Article Eater / CMR project.
We are currently in Sprint 13.16. Your task is to convene an Expert Panel
to solve Panel LIGHT-I: Circadian and Non-Visual Photoreception Calibration.

Before you speak, silently load the following context:
1. The goal is to calibrate the missing parameters for the following templates:
   - DAYLIGHT_MULTICHANNEL_001: Daylight as Multi-Channel Stimulus with Convergent Benefit (7 missing params; CB, PP, NM)
   - CIRCADIAN_ARCH_REG_001: Circadian Architectural Regulation via Non-Visual Photoreception (5 missing params; CB, NM)
   - NM_CIRCADIAN_ENTRAINMENT_001: Circadian Entrainment and Non-Visual Light Effects (4 missing params; CB, NM)
   - CCT_TEMPORAL_ECOLOGICAL_001: Light Color Temperature as Temporal/Ecological Prediction Signal (4 missing params; CB, PP)
   - DYNAMIC_LIGHT_TEMPORAL_001: Dynamic Light Variation as Sustained Temporal PE Engagement (4 missing params; CB, PP)
   - CHRONO_LIGHT_ENTRAINMENT_001: Architectural light → circadian entrainment quality (3 missing params; CB, NM)
   - CIRCADIAN_ARCH_REGULATION_001: Circadian Architecture and Temporal Light Regulation (2 missing params; CB)
   - CB_SLEEP_ARCHITECTURE_002: Evening light exposure → melatonin suppression → sleep quality (2 missing params; CB)
2. Do not write implementation code. Output calibrated JSON parameters for the builder AI.
3. The CMR credence formula governing all outputs is:
   P(CNFA effect) = P(parent theory) × P(bridge) × P(CNFA-specific)
4. All scalar values must be assigned a confidence score (0–1) and a bridge warrant type:
   CONSTITUTIVE (0.75), MECHANISM (0.60), EMPIRICAL_COVARIANCE (0.60),
   FUNCTIONAL (0.50), CAPACITY (0.45), ANALOGICAL (0.35).

✦ MANDATORY GAP RESIDUAL SECTION: Every panel output MUST conclude with a
"RESIDUAL GAPS" section for each template. This section must list:
  (a) Any parameter that could not be calibrated with confidence > 0.40 — state
      what empirical study design would resolve it.
  (b) Any parameter set to a theoretical default (confidence < 0.50) — flag with
      THEORETICAL_DEFAULT and state the assumption made.
  (c) Any interaction effect identified during debate that affects a DIFFERENT
      template not in this panel — flag with CROSS_TEMPLATE_INTERACTION and list
      the affected template ID.
This section feeds directly into gap_registry.json updates via the --mark-calibrated
and --assign flags in scripts/gap_tracker.py.

---

## 🎭 EXEMPLAR PANEL STYLE OBLIGATIONS (NON-NEGOTIABLE)

✦ This panel must conform to the Criteria of Excellence established by historical
panel audit:

**Criterion 1 — Early Ideation (Round Table Phase):**
Before any debate opens, EVERY panelist must deliver a formal opening statement
introducing: (a) their distinct theoretical lens on circadian photoreception and
architectural light, (b) the specific empirical papers they regard as the strongest
anchors, (c) their prior position on the most contested calibration dispute in this
domain (the melanopic lux threshold for circadian entrainment is the primary
expected disagreement axis). No panelist may be introduced by summary alone —
each must speak in their own voice. This round-table phase must occupy the first
20–25% of the transcript.

**Criterion 2 — Heated Crucible Dialogue:**
Disagreement is mandatory. Expect — and require — friction on at least these axes:
  - Whether melanopic lux thresholds derived from laboratory photobiology
    (Czeisler, Brainard) translate directly to occupied architectural settings
    (Figueiro will likely contest this)
  - Whether the CCT→circadian signal pathway operates via direct spectral sensitivity
    of ipRGCs or via indirect cone-mediated input to the SCN
  - Whether dynamic variation in light is necessary for entrainment or merely
    sufficient — and what architectural frequency and amplitude are required
  - The correct dose-response shape (linear vs. sigmoidal) for melatonin suppression
    as a function of melanopic lux
Required discourse markers: "I must push back," "however, I contend," "an alternative
view is," "I challenge that assumption," "that confidence score is far too high given
the architectural translation gap." A flat sequence of agreements is a quality failure.

**Criterion 3 — Sustained Depth:**
Mechanism chains must be specified to the level of: ipRGC subtype (M1–M6),
melanopsin phototransduction cascade, retinohypothalamic tract (RHT) glutamate/PACAP
signaling, SCN core vs. shell oscillator architecture, VIP interneuron synchronization,
PVN-pineal pathway for melatonin synthesis, and feedback to cortical arousal via LC-NE
and histaminergic systems. Surface-level "light → circadian" chains are insufficient.
Target length: >10,000 words.

---

## 🧠 EXPERT SELECTION DIRECTIVE

✦ Your panel MUST include 8–10 experts distributed across:
  - At least 2 Systems Neuroscientists in circadian/SCN/ipRGC systems
  - At least 2 Domain-Specific experts in architectural lighting or chronobiology
  - At least 2 Computational experts in circadian phase modeling
  - At least 2 Architectural/conceptual modeling experts

✦ REQUIRED PANEL (instantiate exactly these experts unless you identify a more
current world authority in their specific sub-domain):

**Expert 1 — Russell Foster (University of Oxford; FRS; NAS Foreign Associate)**
The world's leading authority on non-visual photoreception and ipRGC biology.
Discovered the melanopsin photoreception system in retinal ganglion cells (Foster et al.
1991; Provencio et al. 2000 confirmation). Primary scientific arbiter for all ipRGC
subtype parameters, melanopsin spectral sensitivity peak (~480 nm), and the
distinction between M1 (direct SCN projection) and M2–M6 subtypes. His lens:
systems neuroscience of the retino-hypothalamic tract. He will insist on mechanistic
precision about which ipRGC subtypes drive circadian vs. acute alerting responses.

**Expert 2 — Mariana Figueiro (Mount Sinai; Lighting Research Center founder)**
The leading translational researcher on architectural circadian lighting. Pioneer of
the melanopic lux metric in occupied building settings (Figueiro et al. 2017, 2019,
2022). Holds the most extensive dataset on light-at-the-eye measurements in hospitals,
schools, and eldercare facilities. Her lens: the translation gap between photobiology
lab conditions and real architectural deployment — she will challenge over-confident
threshold values derived from controlled laboratory exposures and insist on
population-specific (especially elderly) field data. Primary empirical arbiter for
architectural modifier coefficients.

**Expert 3 — Charles Czeisler (Harvard Medical School; NAS member)**
Canonical authority on human circadian phase-shifting dose-response curves.
The Czeisler et al. (1995, 2000) and Zeitzer et al. (2000) papers established the
sigmoidal dose-response relationship between light intensity and circadian phase shift.
His lens: precision photobiology with tightly controlled light exposures. He will
push for higher confidence scores on the dose-response curve shape but acknowledge
the architectural translation problem when pressed by Figueiro.

**Expert 4 — Josephine Arendt (University of Surrey; FRS)**
Pioneer of melatonin suppression research and the foundational dose-response work
linking light intensity to nocturnal melatonin suppression. Her 1988 monograph and
subsequent work established the 10 lux threshold (photopic) and its revision upward
after melanopsin discovery. Her lens: neuroendocrinology of the pineal-melatonin axis.
She will provide the mechanism chain from SCN→PVN→superior cervical ganglion→pineal
and will insist the panel distinguish acute suppression from circadian phase-shifting
— these are distinct phenomena with different thresholds and dose-responses.

**Expert 5 — Andrew Gundlach (Florey Institute; computational chronobiology)**
Computational modeler of circadian entrainment dynamics. Brings the Kronauer
limit-cycle oscillator model (Kronauer et al. 1999; Jewett & Kronauer 1998) and
its architectural extensions. His role: translate the photobiological dose-response
data from Czeisler and Figueiro into the mathematical entrainment parameters required
for builder-ready JSON. He will formalize phase response curve (PRC) parameters,
entrainment bandwidth, and resynchronization velocity as functions of melanopic lux
dose and timing.

**Expert 6 — Mirjam Münch (Charité Berlin; circadian lighting and sleep)**
Specialist in the interplay between architectural light, sleep architecture, and
daytime performance. Her work on the evening light suppression → sleep onset latency
pathway (Münch et al. 2006, 2012) is the primary anchor for CB_SLEEP_ARCHITECTURE_002.
She will provide the dose-response curve for melatonin suppression as a function
of evening CCT and the architectural parametrization of "warm vs. cool light" in
bedrooms and evening spaces.

**Expert 7 — Manuel Spitschan (Technical University of Munich; melanopic dosimetry)**
Developer of the melanopic equivalent daylight illuminance (m-EDI) metric and its
computational implementation (Spitschan et al. 2016, 2019; CIE S 026:2018 co-author).
His lens: the quantitative translation from spectroradiometric measurements of
architectural light sources (LED SPDs, glazing spectral transmission) to melanopic
lux at the cornea. He will resolve disputes about CCT_TEMPORAL_ECOLOGICAL_001 by
insisting the panel specify constructs in CIE-standardized melanopic units, not
photopic lux proxies.

**Expert 8 — Thorbjörn Laike (Lund University; environmental psychology of light)**
Environmental psychologist with the most extensive dataset on daylighting, mood,
and cognitive performance in school and office buildings. His lens: the behavioral
and psychological evidence chain from circadian entrainment to performance and
wellbeing outcomes in real architectural settings. He will contest overly optimistic
architectural modifier coefficients from laboratory data and will introduce the
evidence on window-to-floor ratio and glazing orientation effects on circadian
entrainment quality in northern latitude buildings.

**Expert 9 — Jelena Spasojević (VELUX Research; daylight and health)**
Architectural lighting researcher with extensive field studies of daylight metrics —
daylight factor, useful daylight illuminance (UDI), spatial daylight autonomy (sDA) —
and their correlations with occupant health outcomes (Spasojević et al. 2021, 2023).
Her role: translate the circadian photobiology into building-code-compatible
architectural parameters (glazing area, orientation, depth of daylit zone) for
the DAYLIGHT_MULTICHANNEL_001 and CIRCADIAN_ARCH_REG_001 architectural modifier
coefficients.

**Expert 10 — Peter Boyce (RPI Lighting Research Center; architectural photometry)**
Veteran architectural photometrist with the longest longitudinal dataset on
luminous environment and occupant outcomes in offices and healthcare settings.
His role: provide the sceptical empiricist check — he will challenge causal claims
where the evidence base is correlational and insist that confidence scores for
architectural modifier coefficients be calibrated against field study effect sizes
rather than laboratory photobiology extrapolations.

---

## 🎯 THE CALIBRATION EXERCISE

For each target template, the panel must debate and agree on values for the
following constructs. These are listed in order of architectural impact; do not
skip constructs on grounds of difficulty — flag as THEORETICAL_DEFAULT if necessary.

### Constructs for DAYLIGHT_MULTICHANNEL_001
1. **melanopic_lux_threshold_entrainment**: The minimum corneal melanopic illuminance
   (m-EDI, CIE S 026:2018) required to sustain circadian entrainment in an occupied
   building setting, applied for ≥2 hours during the first half of the photophase.
   Expected range: 10–300 m-lux (photobiology lab conditions suggest ~100–200;
   architectural field conditions suggest possible sufficiency at lower levels with
   longer duration). Anchor papers: Zeitzer et al. (2000); Figueiro et al. (2017);
   Czeisler & Gooley (2007). THIS IS THE PRIMARY EXPECTED DISAGREEMENT AXIS.

2. **circadian_phase_shift_dose_response**: Shape and parameters of the dose-response
   function relating melanopic lux × duration to circadian phase advance/delay (in hours).
   Expected form: sigmoidal (Kronauer model); parameters: half-maximum (~100 m-lux),
   slope (Hill coefficient ~2–4), saturation (~2.5 hr phase shift maximum).
   Anchor papers: Kronauer et al. (1999); Zeitzer et al. (2000); Jewett & Kronauer (1998).

3. **cct_circadian_signal_threshold**: The correlated color temperature (CCT) at
   which the circadian channel transitions from suppressive (cool, short-wavelength
   enriched) to permissive (warm, short-wavelength depleted). Expected transition zone:
   2700K–4000K. Architectural implication: evening light above 3000K begins meaningful
   melanopsin engagement. Anchor papers: Münch et al. (2006); Cajochen et al. (2005);
   Spitschan et al. (2016).

4. **daylight_multisystem_convergence_coefficient**: A composite modifier representing
   the convergent benefit of daylight across circadian (CB), arousal-neuromodulatory (NM),
   and predictive-processing (PP) channels simultaneously. This coefficient is unique to
   DAYLIGHT_MULTICHANNEL_001 — it captures synergy beyond additive effects.
   Expected range: 1.10–1.40 (10–40% benefit above additive). This is largely
   theoretical; expect THEORETICAL_DEFAULT flag.

5. **window_to_floor_ratio_circadian_threshold**: The minimum WFR required to deliver
   melanopic entrainment illuminance to 80% of an occupied floor plate.
   Expected range: 0.15–0.35. Anchor papers: Spasojević et al. (2021); Boyce (2003).

6. **glazing_spectral_transmission_circadian_modifier**: Coefficient expressing how
   standard clear glazing (typical T_vis ~0.60–0.70) attenuates the melanopic channel
   relative to unobstructed daylight. Expected range: 0.65–0.85 (glazing transmits
   65–85% of the circadian stimulus). Anchor papers: Münch et al. (2012); CIE 026:2018.

7. **north_south_orientation_circadian_modifier**: Relative circadian entrainment
   efficiency of north-facing vs. south-facing glazing in mid-latitude buildings
   (45°N reference). Expected: north-facing 0.35–0.55 relative to south-facing = 1.0.
   Anchor papers: Laike et al. (2015); Veitch et al. (2010).

### Constructs for CIRCADIAN_ARCH_REG_001 and NM_CIRCADIAN_ENTRAINMENT_001
8. **ipRGC_activation_threshold_maintained**: The sustained (>1 hr) melanopic lux
   level required to activate M1 ipRGCs (primary SCN projectors) above their
   threshold for RHT glutamate/PACAP release sufficient to phase-shift the SCN
   oscillator. Expected range: 30–150 m-lux (shorter durations require higher
   intensities per PRC reciprocity principle).

9. **scn_resynchronization_velocity**: The rate at which the SCN master oscillator
   re-entrains to a shifted light-dark cycle, expressed as hours of phase shift per
   day. Expected range: 0.5–1.5 hr/day (advance direction generally slower than
   delay). Architectural implication: time to re-entrain after moving to a new building
   light environment. Anchor papers: Czeisler et al. (1989); Aschoff (1981).

10. **alerting_response_threshold**: The melanopic lux level that acutely elevates
    cortical arousal (via LC-NE and histaminergic pathways) independent of circadian
    phase-shifting. Distinct from entrainment threshold. Expected range: 10–50 m-lux
    (lower threshold than entrainment; M1 ipRGC collaterals to LC and IGL).
    Anchor papers: Cajochen et al. (2000); Vandewalle et al. (2006).

### Constructs for CCT_TEMPORAL_ECOLOGICAL_001
11. **cct_temporal_ecological_prior**: The prior probability assigned by the
    predictive processing system to a given CCT as a temporal (time-of-day) signal.
    Warm light (2700K) = dusk/evening; cool light (6500K) = noon. This is the
    PP-channel component of the CCT signal. Expected: a probability distribution
    over time-of-day given CCT, derived from natural sky spectral statistics.
    Anchor papers: Walmsley et al. (2015); Spitschan et al. (2017 natural illuminant survey).

12. **cct_arousal_mismatch_cost**: The allostatic cost (IC2 interaction) of receiving
    CCT signals that are ecologically mismatched to clock time — e.g., 6500K light
    at 22:00. Expected range: d = 0.20–0.50 on arousal/cortisol markers.
    Anchor papers: Cajochen et al. (2011); Rahman et al. (2014).

### Constructs for DYNAMIC_LIGHT_TEMPORAL_001
13. **dynamic_variation_frequency_range**: The temporal frequency range (cycles/hour
    or Hz) of light level fluctuation that sustains PP temporal prediction engagement
    without triggering habituation (too slow) or distraction (too fast).
    Expected range: 0.1–2.0 cycles per minute at the macro scale (cloud movement,
    window movement); 0.01–0.1 Hz at the micro scale (flickering/scintillation).
    Anchor papers: Veitch & Newsham (1998); Aries et al. (2010).

14. **dynamic_variation_amplitude_threshold**: The minimum amplitude of luminance
    variation (as fraction of mean luminance) required to sustain temporal PE engagement.
    Expected range: 0.10–0.40 (10–40% variation around mean).

### Constructs for CB_SLEEP_ARCHITECTURE_002
15. **evening_light_melatonin_suppression_threshold**: The melanopic lux level at
    which evening light exposure (2–3 hours before habitual sleep onset) suppresses
    melatonin by ≥50%. Expected range: 30–90 m-lux (substantially lower than daytime
    entrainment threshold; pineal is most sensitive in the biological evening).
    Anchor papers: Arendt et al. (1988); Gooley et al. (2011); Viola et al. (2008).

16. **sleep_onset_latency_modifier**: Minutes added to sleep onset latency per
    unit increase in evening melanopic lux above threshold. Expected: +3–8 minutes
    per doubling of m-lux above 30. Anchor papers: Münch et al. (2006); Chang et al. (2015).

---

## 📚 INTERNAL CONTEXT: THE TARGET TEMPLATES

**CASE A — PRIOR PANEL DOCUMENT EXISTS:**
Prior panel: `34_Panel_LI_Light_Luminance.md` (Document 34, February 16, 2026).
Upload this file alongside this prompt. Extract from it:
  - Templates L1–L5 with their display IDs and template_ids:
      L1 = LUM_CONTRAST_PE_001 (Luminance Contrast PE and Aesthetic Response)
      L2 = CIRCADIAN_ARCH_REG_001 (Circadian Architectural Regulation)
      L3 = DAYLIGHT_MULTICHANNEL_001 (Daylight as Multi-Channel Stimulus)
      L4 = CCT_TEMPORAL_ECOLOGICAL_001 (CCT as Temporal-Ecological Signal)
      L5 = DYNAMIC_LIGHT_TEMPORAL_001 (Dynamic Light Temporal PE)
  - Format: YAML structural templates with causal_links and maturity ratings.
    None carry quantitative CMR parameters (no confidence scores, no bridge
    warrants, no population modifiers, no architectural modifier coefficients).
  - Panel consensus positions already established: (i) daylight is a convergence
    phenomenon across 6 channels (L3); (ii) sacred light = high-magnitude luminance
    PE engaging awe pathway AX3 plus ecological conditioning (L1 upper range);
    (iii) circadian pathway operates independently of visual-aesthetic pathway (L2 vs L1).

Your task for L1–L5: Preserve all causal_links rated 'established' or 'supported'.
Do not re-debate mechanism architecture. Concentrate Crucible debate entirely on
QUANTITATIVE PARAMETERS: the melanopic lux thresholds, dose-response curve shapes,
CCT transition boundaries, dynamic variation frequencies, and architectural modifier
coefficients that the prior panel did not attempt to calibrate.

Your task for the three ADDITIONAL templates not in the prior panel:
  - CHRONO_LIGHT_ENTRAINMENT_001 (3 missing params; CB, NM)
  - CIRCADIAN_ARCH_REGULATION_001 (2 missing params; CB)
  - CB_SLEEP_ARCHITECTURE_002 (2 missing params; CB)
These must be calibrated from gap stubs only — no prior structural work exists.
Gap stubs: all three are HIGH severity (missing parameter_range + empty
evidence_base + not_calibrated) in gap_registry.json.

Template architecture note: All 8 templates carry the CB (Chronobiological
Regulation) T1 framework as primary; most also carry PP (Predictive Processing)
and/or NM (Neuromodulatory Systems). The IC2 super-template (Body Budget
Prediction) is the primary IC2 interaction vector across this domain via the
circadian-cortisol coupling. AX4 (Perceived Control) is implicated wherever
occupants can modulate their light environment (operable shading, task lighting).

Explicitly note at the start of each template's JSON block whether its
mechanism_chain is INHERITED from Document 34 or NEWLY ESTABLISHED in this panel.

---

## 📝 FORCED OUTPUT FORMAT

After completing the full Round Table phase and Crucible debate, output the following
in strict order:

### OUTPUT BLOCK 1: Eight Calibrated JSON Blocks
One per template, in the order listed in the initialization instructions above.
Populate all fields. Do not omit architectural modifiers on grounds that
the evidence is sparse — set confidence low and flag THEORETICAL_DEFAULT instead.

✦ TOULMIN JUSTIFICATION MANDATORY: Every mechanism step must include a
`justification` object per OPUS_REVIEW_GUIDE_ADDENDUM_TOULMIN.md:
  - data[]: Minimum 2 evidence entries for Tier A/B steps
  - backing: 2-5 sentences on why the warrant is trustworthy
  - qualifier: 2-5 sentences on scope conditions and timescale match
  - rebuttal: 2-5 sentences on Popperian falsification conditions
  - competing_accounts[]: Alternative explanations (may be empty if uncontested)
  - depth_tier: "A" (confidence > 0.55 or MECHANISM warrant), "B" (standard), or "C" (residual gap only)

### OUTPUT BLOCK 2: Residual Gaps
Per template, structured as described in the initialization instructions:
(a) Uncalibratable parameters with recommended study designs
(b) Theoretical defaults with explicit assumptions
(c) Cross-template interactions flagged for future panels

### OUTPUT BLOCK 3: CMR Integration Note
Covering all 8 templates collectively, then per-template where the T1/T1.5
mappings differ. Note especially: the CB → PP interaction in CCT_TEMPORAL_ECOLOGICAL_001
(CCT as temporal ecological prior is a PP-channel mechanism, not a purely
chronobiological one), and the CB → NM interaction in the alerting pathway
(ipRGC collaterals to LC-NE and histaminergic tuberomammillary nucleus).

### OUTPUT BLOCK 4: Gap Tracker Update Block
```bash
python3 scripts/gap_tracker.py --mark-calibrated DAYLIGHT_MULTICHANNEL_001 --panel LIGHT-I
python3 scripts/gap_tracker.py --mark-calibrated CIRCADIAN_ARCH_REG_001 --panel LIGHT-I
python3 scripts/gap_tracker.py --mark-calibrated NM_CIRCADIAN_ENTRAINMENT_001 --panel LIGHT-I
python3 scripts/gap_tracker.py --mark-calibrated CCT_TEMPORAL_ECOLOGICAL_001 --panel LIGHT-I
python3 scripts/gap_tracker.py --mark-calibrated DYNAMIC_LIGHT_TEMPORAL_001 --panel LIGHT-I
python3 scripts/gap_tracker.py --mark-calibrated CHRONO_LIGHT_ENTRAINMENT_001 --panel LIGHT-I
python3 scripts/gap_tracker.py --mark-calibrated CIRCADIAN_ARCH_REGULATION_001 --panel LIGHT-I
python3 scripts/gap_tracker.py --mark-calibrated CB_SLEEP_ARCHITECTURE_002 --panel LIGHT-I
# Cross-template assignments to be filled from Residual Gaps output
python3 scripts/gap_tracker.py --assign [AFFECTED_ID] --panel [FUTURE_PANEL]
python3 scripts/gap_tracker.py --report
```

### OUTPUT BLOCK 5: Full APA Reference List with DOIs

### OUTPUT BLOCK 6: ARTIFACT (MANDATORY)
✦ Deliver the complete panel output as a single downloadable artifact file:
Filename: `LIGHT_I_Panel_Output_Feb21.md`

The artifact must contain all five output blocks in one self-contained Markdown
document. Begin with the following header:
```
# LIGHT-I EXPERT PANEL OUTPUT: CIRCADIAN AND NON-VISUAL PHOTORECEPTION
## Panel ID: LIGHT-I | Sprint: 13.16 | Date: February 21, 2026
## Templates calibrated: DAYLIGHT_MULTICHANNEL_001, CIRCADIAN_ARCH_REG_001,
##   NM_CIRCADIAN_ENTRAINMENT_001, CCT_TEMPORAL_ECOLOGICAL_001,
##   DYNAMIC_LIGHT_TEMPORAL_001, CHRONO_LIGHT_ENTRAINMENT_001,
##   CIRCADIAN_ARCH_REGULATION_001, CB_SLEEP_ARCHITECTURE_002
## Prior panel document: 34_Panel_LI_Light_Luminance.md (February 16, 2026)
## Status: COMPLETE
```
Truncated artifacts are rejected. The artifact is the authoritative deliverable.

---

## 📎 KEY ANCHOR PAPERS FOR THIS PANEL

Arendt, J., Bojkowski, C., Franey, C., Wright, J., & Marks, V. (1985). Immunoassay of 6-hydroxymelatonin sulfate in human plasma and urine: Abolition of the urinary 24-hour rhythm with atenolol. *Journal of Clinical Endocrinology & Metabolism*, *60*(6), 1166–1173. https://doi.org/10.1210/jcem-60-6-1166

Cajochen, C., Frey, S., Anders, D., Späti, J., Bues, M., Pross, A., Mager, R., Wirz-Justice, A., & Stefani, O. (2011). Evening exposure to a light-emitting diodes (LED)-backlit computer screen affects circadian physiology and cognitive performance. *Journal of Applied Physiology*, *110*(5), 1432–1438. https://doi.org/10.1152/japplphysiol.00165.2011

Czeisler, C. A., Duffy, J. F., Shanahan, T. L., Brown, E. N., Mitchell, J. F., Rimmer, D. W., Ronda, J. M., Silva, E. J., Allan, J. S., Emens, J. S., Dijk, D.-J., & Kronauer, R. E. (1999). Stability, precision, and near-24-hour period of the human circadian pacemaker. *Science*, *284*(5423), 2177–2181. https://doi.org/10.1126/science.284.5423.2177

Figueiro, M. G., Steverson, B., Heerwagen, J., Kampschroer, K., Hunter, C. M., Gonzales, K., Plitnick, B., & Rea, M. S. (2017). The impact of daytime light exposures on sleep and mood in office workers. *Sleep Health*, *3*(3), 204–215. https://doi.org/10.1016/j.sleh.2017.03.005

Gooley, J. J., Chamberlain, K., Smith, K. A., Khalsa, S. B. S., Rajaratnam, S. M. W., Van Reen, E., Zeitzer, J. M., Czeisler, C. A., & Lockley, S. W. (2011). Exposure to room light before bedtime suppresses melatonin onset and shortens melatonin duration in humans. *Journal of Clinical Endocrinology & Metabolism*, *96*(3), E463–E472. https://doi.org/10.1210/jc.2010-2098

Jewett, M. E., & Kronauer, R. E. (1998). Refinement of a limit cycle oscillator model of the effects of light on the human circadian pacemaker. *Journal of Theoretical Biology*, *192*(4), 455–465. https://doi.org/10.1006/jtbi.1998.0667

Münch, M., Kobialka, S., Steiner, R., Oelhafen, P., Wirz-Justice, A., & Cajochen, C. (2006). Wavelength-dependent effects of evening light exposure on sleep architecture and sleep EEG power density in men. *American Journal of Physiology — Regulatory, Integrative and Comparative Physiology*, *290*(5), R1421–R1428. https://doi.org/10.1152/ajpregu.00478.2005

Spitschan, M., Aguirre, G. K., & Brainard, D. H. (2016). Selective stimulation of penumbral and umbral retinal cells. *Current Biology*, *26*(21), 2959–2967. https://doi.org/10.1016/j.cub.2016.08.040

Zeitzer, J. M., Dijk, D.-J., Kronauer, R., Brown, E., & Czeisler, C. (2000). Sensitivity of the human circadian pacemaker to nocturnal light: Melatonin phase resetting and suppression. *Journal of Physiology*, *526*(3), 695–702. https://doi.org/10.1111/j.1469-7793.2000.00695.x

---

## ⚑ PANEL-SPECIFIC CONTEXT NOTE

**Cross-panel dependencies**: This panel has no upstream dependencies (LIGHT-I is Panel 1
in the post-STRESS-I sequence). However, it will feed downstream:
  - STRESS-I T6/T7 interaction: circadian disruption raises allostatic load threshold
    sensitivity (T6 allostatic_load_threshold is lower in chronically sleep-deprived
    populations — flag as CROSS_TEMPLATE_INTERACTION to T6 if quantifiable).
  - VISUAL-I (Panel 9): CCT and luminance parameters from this panel feed into
    PP_COMPLEXITY_GOLDILOCKS_002 and COLOR_AROUSAL_MODULATION_001.
  - NEUROMOD-I (Panel 10): alerting pathway (ipRGC→LC-NE) feeds NM_NORADRENERGIC_EXPLORE_006.
  - THERMAL-I (Panel 7): circadian phase governs thermal comfort expectations
    (TC1 template interaction with CB_SLEEP_ARCHITECTURE_002).

**Population priority**: Elderly populations show attenuated melanopsin function
(reduced ipRGC density, lens yellowing reducing blue light transmission), dramatically
lowering effective melanopic lux at the retina. Healthcare and eldercare building types
must receive population modifier coefficients for every parameter in this panel.
Figueiro's field data in nursing homes are the primary empirical source.

**Super-template interactions**: IC2 (Body Budget Prediction) is engaged wherever
circadian misalignment produces allostatic disruption — every template in this panel
has a potential IC2 interaction via the circadian-cortisol coupling (morning cortisol
awakening response is phase-locked to the SCN; misalignment delays and blunts the CAR,
imposing a body-budget prediction error). AX4 (Perceived Control) is engaged wherever
occupants can operate shading systems, adjust task lighting, or influence their
temporal light environment.

---

FINAL OBLIGATION: Begin with the Round Table phase. Every one of the 10 panelists
must speak in their own voice before any calibration debate opens. The Crucible must
emerge organically from genuine theoretical and empirical disagreements — do not
manufacture superficial friction, but do not permit premature consensus either.
The melanopic lux entrainment threshold and the architectural translation gap are
the primary Crucible axes. Do not break character. Target >10,000 words.
```

---

*Meta-prompt §4 completed: Session 6, February 21, 2026*
*LIGHT-I instantiated prompt: ready to submit*
*Next instantiation required: SPATIAL-I (Sprint 13.17)*
