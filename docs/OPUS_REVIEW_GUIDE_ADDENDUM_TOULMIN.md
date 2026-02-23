# OPUS REVIEW GUIDE — ADDENDUM: TOULMIN JUSTIFICATION LAYER
## Mandatory for all panel outputs from SOCIAL-I onward
## Retroactive for STRESS-I, LIGHT-I, SPATIAL-I, VISUAL-I (see Sprint TJ-03)
## February 22, 2026

---

# 1. RATIONALE

The current mechanism chain format provides assertions with citations. Each step
states that A leads to B, names a reference, and assigns a confidence score. This
is insufficient for two reasons: (a) it does not distinguish between steps where
the evidence is genuinely strong and steps where a plausible story has been told,
and (b) it does not specify the conditions under which the step would fail, making
the confidence score unjustifiable to an external reviewer.

The Toulmin justification layer (Toulmin, 1958) adds the missing argumentative
structure. Every mechanism step in a calibrated template becomes a defensible
argument rather than an assertion. The justification layer sits behind the
mechanism chain summary — it is what the Article Eater displays when a user
asks "why do you believe this step?"

---

# 2. REQUIRED FIELDS

Every mechanism step in a calibrated template's JSON must include a
`justification` object with the following fields:

```json
{
  "step": <int>,
  "from": "<variable>",
  "to": "<variable>",
  "description": "<one-paragraph summary — unchanged from current format>",
  "warrant": "<bridge warrant type>",
  "confidence": <float>,

  "justification": {
    "data": [ ... ],
    "backing": "<string>",
    "qualifier": "<string>",
    "rebuttal": "<string>",
    "competing_accounts": [ ... ]
  }
}
```

### 2.1 `data` — The specific evidence

An array of evidence objects. Each object represents one empirical finding or
computational result that supports this mechanism step.

```json
{
  "finding": "<one-sentence description of what was found>",
  "source": "<APA short citation>",
  "paradigm": "<experimental paradigm or method>",
  "effect": "<effect size or key quantitative result>",
  "n": <sample size or null>,
  "design": "<study design: within-subjects, between, longitudinal, etc.>"
}
```

Rules:
- Minimum 2 data entries per step. If fewer than 2 independent sources support
  a step, the step's confidence should be below 0.50 and carry THEORETICAL_DEFAULT.
- Data entries should come from INDEPENDENT paradigms where possible. Two fMRI
  studies using the same task are one paradigm; an fMRI study and an EEG study
  measuring the same construct are two paradigms. Converging paradigms increase
  backing strength.
- Do not invent findings. If a data entry cannot be verified, mark it `[VERIFY]`.

### 2.2 `backing` — Why the warrant connecting data to claim is trustworthy

A paragraph (2-5 sentences) explaining the inferential principle that connects
the data to the claim. This is NOT a restatement of the data — it is the
reasoning that makes the data relevant.

The backing should address:
- Why this type of evidence (this paradigm, this measurement) is informative
  about this mechanism step
- Whether multiple independent lines of evidence converge (and if so, why
  convergence increases credence)
- What assumptions the inference rests on

Example: "The warrant connecting PE reduction to metabolic savings rests on
two independent lines: biophysical energy budgets establishing that synaptic
transmission dominates cortical energy expenditure, and fMRI evidence that
predictable stimuli reduce cortical activation. The convergence across
biophysical modeling and neuroimaging increases credence beyond what either
line alone would support."

### 2.3 `qualifier` — Scope conditions and epistemic limits

A paragraph (2-5 sentences) specifying:
- The conditions under which this step's claim holds (population, context,
  timescale, stimulus type)
- The conditions under which it may not hold
- Any extrapolations made from the data (and their assumptions)
- The specific reason the confidence score is what it is (not higher, not lower)

The qualifier must address the **timescale match** between the mechanism and the
architectural claim. If the mechanism operates on a timescale (milliseconds,
hours, weeks) that differs from the architectural exposure implied by the
template, state this explicitly. (See MEMORY-I constraint #4 for the paradigm
case: systems consolidation operates on weeks-to-years; acute architectural
claims at this timescale are inconsistent.)

### 2.4 `rebuttal` — Conditions under which the step would fail

A paragraph (2-5 sentences) specifying what would have to be true for this
mechanism step to be wrong. This is the Popperian core of the justification:
the system specifies its own falsification conditions.

Rules:
- Every step MUST have a non-trivial rebuttal. "The claim would fail if the
  evidence is wrong" is trivial and not acceptable.
- The rebuttal should name specific alternative accounts, specific empirical
  findings that challenge the step, or specific assumptions that if violated
  would invalidate the inference.
- If the rebuttal describes a condition that is ACTUALLY MET by current
  evidence (i.e., there is real evidence against the step), the confidence
  score must reflect this. A step with an active rebuttal condition and
  confidence > 0.60 is a contradiction.

### 2.5 `competing_accounts` — Named alternative explanations

An array (may be empty) of objects describing alternative mechanistic accounts
for the same from→to transition.

```json
{
  "account": "<short name for the alternative>",
  "proponent": "<researcher(s) associated with this account>",
  "claim": "<one-sentence description of what the alternative claims>",
  "implication_for_template": "<what changes if this account is correct>"
}
```

Rules:
- If competing_accounts is empty, this means the step is genuinely uncontested.
  Do not leave it empty by default — actively check whether alternatives exist.
- If competing_accounts is non-empty, the confidence score should reflect the
  unresolved competition. A step with two equally supported competing accounts
  should not exceed confidence 0.55.
- The `implication_for_template` field is critical: it tells the Article Eater
  what would change in the template's calibrated parameters if the alternative
  account turned out to be correct. This enables sensitivity analysis.

---

# 3. INTERACTION WITH EXISTING FIELDS

The justification layer does NOT replace any existing fields. The mechanism chain
summary (`description`), bridge warrant, and confidence score remain. The
justification layer provides the evidential basis for those assignments.

**Consistency rule**: The confidence score must be justifiable from the
justification layer. Specifically:
- If `data` contains fewer than 2 independent paradigms → confidence ≤ 0.50
- If `rebuttal` describes a condition currently met by evidence → confidence ≤ 0.55
- If `competing_accounts` contains an equally supported alternative → confidence ≤ 0.55
- If `qualifier` identifies a timescale mismatch → reduce confidence by 0.10-0.15
- If `backing` identifies an untested extrapolation → flag THEORETICAL_DEFAULT

These are ceilings, not targets. A step can score below these ceilings for
other reasons.

---

# 4. DEPTH TIERS

Not all mechanism steps require the same depth of justification. The system
recognizes three depth tiers:

**Tier A — Full justification** (required for):
- Steps where bridge warrant is MECHANISM or higher
- Steps where confidence > 0.55
- Steps that are contested (non-empty competing_accounts)
- Steps at the critical bridge point (the step connecting laboratory mechanism
  to architectural context — usually the step where the bridge warrant is
  assigned)

**Tier B — Standard justification** (required for):
- All other steps in calibrated templates
- Minimum: 2 data entries, backing, qualifier, rebuttal (may be briefer)
- competing_accounts may be empty if genuinely uncontested

**Tier C — Stub justification** (acceptable only for):
- Steps rated below 0.40 that are in RESIDUAL GAPS
- Minimum: 1 data entry (or "no direct data — theoretical inference"), qualifier
  stating why confidence is low, rebuttal
- These stubs are placeholders to be upgraded when evidence arrives

---

# 5. PANEL PRODUCTION WORKFLOW

During panel calibration (Crucible debate method), the justification layer is
produced as follows:

1. **Opening statements** → populate `data` and `backing` for each expert's
   assigned steps. Each expert provides their strongest evidence and explains
   why it is relevant.

2. **Crucible disputes** → populate `rebuttal` and `competing_accounts`. When
   experts disagree, the disagreement IS the rebuttal/competing account content.
   Capture it rather than resolving it away.

3. **Consensus calibration** → populate `qualifier` and set final confidence.
   The qualifier explains what the panel agreed on and what remains uncertain.

This means the justification layer is a BYPRODUCT of the existing calibration
process, not an additional burden. The Crucible debate already produces this
content; the change is retaining it in structured form rather than discarding
it after the summary is written.

---

# 6. EXAMPLE — FULL TIER A JUSTIFICATION

From VISUAL-I T1 (PP_SPECTRAL_MATCH_001), step 3:

```json
{
  "step": 3,
  "from": "reduced_prediction_error_in_visual_hierarchy",
  "to": "reduced_cortical_metabolic_demand",
  "description": "Lower prediction error magnitude → smaller mismatch signals requiring upward propagation → reduced synaptic transmission load. Estimated 10-20% glucose utilization reduction in early visual cortex.",
  "warrant": "MECHANISM",
  "confidence": 0.50,

  "justification": {
    "data": [
      {
        "finding": "Cortical metabolic cost scales with synaptic transmission volume; synaptic transmission consumes approximately 75% of cortical energy budget",
        "source": "Laughlin & Sejnowski (2003)",
        "paradigm": "Biophysical modeling of neural energy budgets",
        "effect": "75% of cortical energy allocated to synaptic signaling",
        "n": null,
        "design": "Computational estimate from biophysical parameters"
      },
      {
        "finding": "Predicted visual stimuli reduce BOLD signal in V1 relative to unpredicted stimuli",
        "source": "Kok, Jehee, & de Lange (2012)",
        "paradigm": "fMRI expectation suppression",
        "effect": "Expected gratings → reduced V1 BOLD vs. unexpected (within-subjects)",
        "n": 19,
        "design": "Within-subjects orientation expectation manipulation"
      },
      {
        "finding": "Repetition of expected stimuli produces greater suppression than repetition of unexpected stimuli in V1",
        "source": "Summerfield et al. (2008)",
        "paradigm": "fMRI repetition suppression with expectation",
        "effect": "Interaction: expectation × repetition in V1 BOLD",
        "n": 16,
        "design": "Within-subjects factorial"
      }
    ],

    "backing": "The warrant connecting PE reduction to metabolic savings rests on two independent lines of evidence: (a) biophysical energy budgets establishing that synaptic transmission dominates cortical energy expenditure (Laughlin & Sejnowski, 2003; Attwell & Laughlin, 2001), and (b) neuroimaging evidence that predictable stimuli reduce cortical activation in early visual areas (Kok et al., 2012; Summerfield et al., 2008). The convergence across biophysical modeling and fMRI paradigms increases credence beyond what either line alone would support. The inference assumes that BOLD signal reduction reflects reduced neural metabolic demand rather than a redistribution of processing.",

    "qualifier": "The 10-20% glucose reduction estimate is extrapolated from single-neuron biophysics to population-level cortical processing. This extrapolation assumes approximately linear scaling from individual synapses to cortical columns, which may not hold if network-level dynamics (lateral inhibition, recurrent processing) introduce nonlinearities. The estimate applies to early visual cortex during passive viewing of stationary images. Active visual exploration, sustained attention, and task demands will modulate the effect and may reduce or eliminate metabolic savings. No study has directly measured glucose utilization in human visual cortex as a function of stimulus statistical predictability using PET or calibrated fMRI.",

    "rebuttal": "The claim would fail if: (a) predictive coding correction signals are metabolically cheap relative to feedforward processing, making PE reduction negligible for total cortical energy — Lennie (2003) argues that the energy cost of neural signaling is small relative to maintenance costs, which would make PE-driven metabolic savings functionally trivial; (b) reduced PE in early visual cortex is compensated by increased processing in higher-order areas generating the predictions, producing no net metabolic savings at the whole-brain level; (c) the BOLD signal reduction for predicted stimuli reflects sharpened representations (fewer neurons firing at higher rates) rather than overall reduced activity — Kok et al. (2012) themselves discuss this possibility, and de Lange et al. (2018) argue that sharpening is the primary mechanism.",

    "competing_accounts": [
      {
        "account": "Sharpening rather than silencing",
        "proponent": "Kok et al. (2012); de Lange, Heilbron, & Kok (2018)",
        "claim": "Prediction reduces BOLD not because total energy expenditure decreases but because neural representations become sparser and more precise — fewer neurons fire but carry more information per spike",
        "implication_for_template": "If sharpening rather than silencing, the metabolic savings may be smaller than estimated (possibly negligible), but the coding efficiency gain and downstream PE reduction still hold. T1's aesthetic prediction (efficient coding → positive valence) is preserved under both accounts; the metabolic pathway (step 3) would be weakened but the information-theoretic pathway would be strengthened. Net effect on template confidence: approximately neutral, but the mechanism description should acknowledge both pathways."
      }
    ]
  }
}
```

---

# 7. REFERENCES

Attwell, D., & Laughlin, S. B. (2001). An energy budget for signaling in the
grey matter of the brain. *Journal of Cerebral Blood Flow & Metabolism*, *21*(10),
1133-1145.

de Lange, F. P., Heilbron, M., & Kok, P. (2018). How do expectations shape
perception? *Trends in Cognitive Sciences*, *22*(9), 764-779.

Kok, P., Jehee, J. F., & de Lange, F. P. (2012). Less is more: Expectation
sharpens representations in the primary visual cortex. *Neuron*, *75*(2), 265-270.

Laughlin, S. B., & Sejnowski, T. J. (2003). Communication in neural networks.
*Science*, *301*(5641), 1870-1874.

Lennie, P. (2003). The cost of cortical computation. *Current Biology*, *13*(6),
493-497.

Summerfield, C., Trittschuh, E. H., Monti, J. M., Mesulam, M. M., & Egner, T.
(2008). Neural repetition suppression reflects fulfilled perceptual expectations.
*Nature Neuroscience*, *11*(9), 1004-1006.

Toulmin, S. E. (1958). *The uses of argument*. Cambridge University Press.

---

*OPUS_REVIEW_GUIDE_ADDENDUM_TOULMIN.md — CMR Project*
*Effective: February 22, 2026*
*Applies to: all panels from SOCIAL-I onward; retroactive for earlier panels per Sprint TJ-03*
