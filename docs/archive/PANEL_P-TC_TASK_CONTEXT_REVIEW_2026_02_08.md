# Panel P-TC: Task Context Integration Review

**Date**: February 8, 2026
**Panel**: P-TC (Task Context)
**Trigger**: 7 decisions accumulated (≥5 threshold met)
**Status**: CONVENED

---

## Panel Members

| Expert | Expertise | Focus |
|--------|-----------|-------|
| Dr. Gary Klein | Naturalistic Decision Making | Context-sensitivity, expertise |
| Dr. K. Anders Ericsson | Deliberate practice, skill acquisition | Skill-based differences |
| Dr. Daniel Kahneman | System 1/2, cognitive load | Cognitive demand modeling |
| Dr. Rachel Kaplan | Environmental psychology (ART) | Restoration, person-environment fit |
| Dr. Herbert Simon | Bounded rationality | Satisficing, design trade-offs |
| Dr. Lucy Suchman | Situated action | Ecological validity, real-world transfer |

---

## Decisions Under Review

### D1: Default Task When Unknown

**Context**: When a paper doesn't specify what task participants performed, the system must assign a default category for the extraction schema.

**Current Choice**: `high_demand.solitary`

**Alternatives**:
- `low_demand` (less demanding default)
- Flag as `unknown` (don't assign)

**Risk**: Wrong default → incorrect environmental recommendations in downstream use.

---

### D2: Instrument Mapping Confidence

**Context**: When a paper uses a named instrument (e.g., "d2 Test of Attention", "Stroop Task"), we can infer task type with high confidence from the canonical mapping.

**Current Choice**: 0.95 confidence for named instruments

**Alternatives**:
- 0.90 (more conservative)
- 1.0 (perfect confidence)

**Risk**: Overconfidence → propagates through Quinean web with unwarranted certainty.

---

### D3: Keyword Inference Confidence

**Context**: When no named instrument is found, we use regex patterns to infer task type from descriptions (e.g., "proofreading task" → high_demand).

**Current Choice**: 0.5-0.7 range depending on pattern specificity

**Alternatives**:
- Narrower range (0.6-0.7)
- Wider range (0.4-0.8)

**Risk**: Too narrow → loses discriminability; too wide → overconfident on weak patterns.

---

### D4: Default Ecological Validity

**Context**: Papers often don't explicitly state whether findings come from lab, field, or naturalistic settings.

**Current Choice**: `lab_task` (conservative default)

**Alternatives**:
- `unknown` (don't assume)
- `real_world_analog` (middle ground)

**Risk**: Assuming lab underestimates transfer; assuming field overestimates transfer.

---

### D5: Rate Limit with API Key

**Context**: When fetching paper metadata, the system rate-limits API calls to avoid bans.

**Current Choice**: 0.1s delay (100 calls/second with API key)

**Alternatives**:
- 0.2s (more conservative)
- 0.05s (faster but riskier)

**Risk**: Too fast → API ban; too slow → pipeline bottleneck.

---

### D6: Cognitive Demand Levels

**Context**: Current taxonomy has three cognitive demand levels: high_demand, low_demand, restorative.

**Current Choice**: Three levels only

**Alternatives**:
- Add "mixed" (tasks that vary)
- Add "variable" (tasks that can be either)

**Risk**: More categories → more complex; fewer → loses distinctions.

---

### D7: Include Pure Psych/Neuro Papers

**Context**: Some papers study cognitive/affective mechanisms without any architectural component (e.g., pure attention studies with no environment manipulation).

**Current Choice**: Yes - include as mechanism grounding

**Alternatives**:
- CNfA-only scope (exclude pure psych/neuro)
- Include but tag as "mechanism_only"

**Risk**: Including → scope creep, diluted focus; excluding → miss mechanistic underpinnings.

---

## Panel Responses

### Dr. Gary Klein (Naturalistic Decision Making)

**On D1 (Default Task)**:
The choice of `high_demand.solitary` as default is sensible from a conservative standpoint—most laboratory research involves focused cognitive tasks. However, I'd argue for a more nuanced approach: **flag as unknown rather than default**.

In naturalistic decision making research, we've learned that context matters enormously. A "default" hides uncertainty that should be explicit. When the task is truly unknown, downstream users should know that—not receive a plausible-looking but potentially wrong categorization.

**Recommendation**: Flag as `unknown` with explicit uncertainty marker. Let downstream systems handle the uncertainty appropriately.

**On D7 (Pure Psych/Neuro)**:
Include them, but with clear tagging. Understanding how attention restoration *works* (the mechanism) is valuable even without direct architectural application. The key is not to conflate mechanism studies with applied studies in the coherence calculations.

**Recommendation**: Include with `mechanism_only` tag. Weight differently in environmental recommendations.

---

### Dr. K. Anders Ericsson (Deliberate Practice)

**On D2 (Instrument Mapping Confidence)**:
0.95 is appropriate for well-validated instruments. The d2 test, Stroop, n-back—these have decades of validation and their cognitive demands are well-characterized. However, I'd add a caveat: the confidence should apply to the *cognitive process*, not necessarily to how it transfers to real-world performance.

**Recommendation**: Keep 0.95 for known instruments, but add a `transfer_uncertainty` flag.

**On D6 (Cognitive Demand Levels)**:
Three levels are insufficient for capturing the skill acquisition trajectory. A novice performing the same task as an expert has fundamentally different cognitive demands. Rather than adding "mixed" (which is vague), **add the skill level modifier more prominently**.

The current taxonomy has skill_level as a modifier, but it should interact with cognitive_demand:
- high_demand × novice → very high effective demand
- high_demand × expert → moderate effective demand

**Recommendation**: Keep three base levels. Make skill_level×demand interaction explicit in the schema, with effective_demand computed values.

---

### Dr. Daniel Kahneman (Cognitive Load)

**On D3 (Keyword Inference Confidence)**:
The 0.5-0.7 range is reasonable, but I'm concerned about the lower bound. At 0.5 confidence, you're essentially saying "coin flip." This should trigger human review, not automated categorization.

**Recommendation**:
- Pattern match confidence ≥0.7 → auto-categorize
- Pattern match confidence 0.5-0.7 → flag for review
- Pattern match confidence <0.5 → leave as unknown

**On D6 (Cognitive Demand Levels)**:
The System 1/System 2 distinction isn't perfectly captured by high/low/restorative. A better framing:
- **Effortful attention required** (high_demand) — System 2 dominant
- **Automatic processing sufficient** (low_demand) — System 1 sufficient
- **Recovery mode** (restorative) — Neither system taxed

"Mixed" doesn't fit this framework well. Most tasks are mixed at some level. Instead, consider **task phases**: a lecture might be high_demand for learning, low_demand for note-taking, restorative during breaks.

**Recommendation**: Keep three levels. Add optional `phase` annotations for tasks that shift demands over time.

---

### Dr. Rachel Kaplan (Environmental Psychology)

**On D4 (Default Ecological Validity)**:
This is exactly the right question to ask. The default of `lab_task` is appropriate because:
1. Most CNfA research *is* laboratory-based
2. Underestimating transfer is safer than overestimating
3. Papers that do field research usually say so explicitly

However, "unknown" might be even better. The purpose of ART is to understand person-environment transactions in real settings. Lab findings are valuable but preliminary.

**Recommendation**: Default to `lab_task` but add explicit `transfer_warning` flag. Or: default to `unknown` with `presumed_lab` indicator.

**On D1 (Default Task)**:
For CNfA specifically, the most common task context is indeed focused cognitive work in an office-like setting. `high_demand.solitary` matches the modal case in this literature.

But I agree with Dr. Klein—hiding uncertainty is dangerous. **The default should serve the uncertainty, not hide it.**

**Recommendation**: `high_demand.solitary` with `inferred_not_stated` flag. Downstream systems can then decide how to handle inference vs. explicit categorization.

---

### Dr. Herbert Simon (Bounded Rationality)

**On D5 (Rate Limit)**:
0.1s (100/sec) is reasonable for a research tool. Production systems facing scale would need to revisit this, but for the current use case, throughput isn't the bottleneck—quality of extraction is.

**Recommendation**: Keep 0.1s. Document for future scaling needs.

**On D3 (Keyword Inference)**:
The satisficing principle applies here: we don't need perfect categorization, we need *good enough* categorization that acknowledges its limits. The current range is fine, but the system should track accuracy over time.

**Recommendation**: Keep 0.5-0.7 range. Add calibration tracking: sample extracted categorizations, compare to human judgment, adjust thresholds as needed.

**On D7 (Pure Psych/Neuro)**:
Include them. The bounded rationality perspective says: don't throw away potentially useful information. Mechanism papers provide grounding for why architectural interventions work. Without mechanisms, we're just correlating environment and outcome without understanding.

**Recommendation**: Include with clear tagging. Don't mix mechanism evidence with applied evidence in the same confidence calculations.

---

### Dr. Lucy Suchman (Situated Action)

**On D4 (Default Ecological Validity)**:
I have strong concerns about defaulting to `lab_task` without qualification. This perpetuates the assumption that laboratory findings transfer to real-world contexts—an assumption my work has repeatedly challenged.

The situated action perspective emphasizes:
1. Context isn't a variable to control; it's constitutive of the phenomenon
2. "The same task" performed in different settings is not the same task
3. Lab findings tell us what's possible under controlled conditions, not what happens in practice

**Recommendation**: Default to `unknown` with a required `context_notes` field. Force the system (and users) to articulate what's known about the study context.

**On D1 (Default Task)**:
Similar concern. Defaulting to anything obscures crucial uncertainty. The question "what were participants doing?" is fundamental—it shouldn't have a default answer.

**Recommendation**: Require explicit task categorization with `stated` vs. `inferred` marker. For inference, require confidence rating and pattern that triggered it.

**On D7 (Pure Psych/Neuro)**:
Include with appropriate framing. But be careful: mechanism studies often use highly controlled tasks precisely because they're *not* ecologically valid. The mechanism may be real, but whether it operates the same way in naturalistic settings is an empirical question.

**Recommendation**: Include with `mechanism_only` tag AND `lab_conditions_only` flag if applicable. Track whether mechanism findings have been validated in field settings.

---

## Panel Synthesis

### Unanimous or Near-Unanimous Positions

1. **D7 (Pure Psych/Neuro)**: Include mechanism papers with explicit tagging (`mechanism_only`). Don't mix with applied evidence in coherence calculations.

2. **D5 (Rate Limit)**: 0.1s is acceptable. Document for future scaling.

3. **D2 (Instrument Mapping)**: 0.95 is appropriate for canonical instruments. Add `transfer_uncertainty` caveat.

### Divided Positions

4. **D1 (Default Task)**:
   - Klein, Suchman: Flag as `unknown`, don't default
   - Kaplan: `high_demand.solitary` with `inferred_not_stated` flag
   - **Compromise**: Default to `high_demand.solitary` BUT require `inference_basis` field (stated/inferred/unknown)

5. **D4 (Default Ecological Validity)**:
   - Kaplan: `lab_task` with `transfer_warning`
   - Suchman: `unknown` with required `context_notes`
   - **Compromise**: `lab_task` with `presumed` flag indicating inference

6. **D3 (Keyword Inference)**:
   - Kahneman: ≥0.7 auto-categorize, 0.5-0.7 flag for review
   - Simon: Keep range, add calibration tracking
   - **Compromise**: Keep 0.5-0.7 range, add `review_recommended` flag for <0.7

7. **D6 (Cognitive Demand Levels)**:
   - Ericsson: Make skill×demand interaction explicit
   - Kahneman: Add optional `phase` annotations
   - **Compromise**: Keep three levels, add `effective_demand` computed from skill interaction, optional `phase` for multi-phase tasks

---

## Panel Verdict

### Recommendations Summary

| D# | Decision | Panel Verdict | Action Required |
|----|----------|---------------|-----------------|
| D1 | Default task | MODIFY | Add `inference_basis` field (stated/inferred/unknown). Default `high_demand.solitary` for inferred. |
| D2 | Instrument confidence | APPROVE | Keep 0.95. Add `transfer_uncertainty` caveat to schema. |
| D3 | Keyword confidence | MODIFY | Keep 0.5-0.7 range. Add `review_recommended: true` for confidence <0.7. |
| D4 | Default ecological validity | MODIFY | Default `lab_task`. Add `presumed: true` flag when not explicitly stated. |
| D5 | Rate limit | APPROVE | Keep 0.1s. Document in operational notes. |
| D6 | Cognitive demand levels | MODIFY | Keep 3 levels. Add `effective_demand` computed from skill×demand. Optional `phase` field. |
| D7 | Pure psych/neuro | APPROVE | Include with `mechanism_only` tag. Track field validation status. |

### Implementation Priority

1. **High Priority** (affects extraction accuracy):
   - D1: Add `inference_basis` field to task_taxonomy.json
   - D4: Add `presumed` flag to ecological_validity
   - D7: Add `mechanism_only` tag to schema

2. **Medium Priority** (improves transparency):
   - D3: Add `review_recommended` flag
   - D6: Add `effective_demand` computation

3. **Low Priority** (documentation):
   - D2: Document `transfer_uncertainty` caveat
   - D5: Document rate limit in ops notes

---

## Schema Changes Required

```json
// Additions to task_taxonomy.json

"inference_basis": {
  "description": "How was task type determined?",
  "values": ["stated", "inferred", "unknown"],
  "default": "unknown"
},

"effective_demand": {
  "description": "Computed from cognitive_demand × skill_level interaction",
  "computation": "See skill×demand matrix below"
},

"presumed": {
  "description": "Flag indicating inference rather than explicit statement",
  "type": "boolean",
  "default": false
},

"review_recommended": {
  "description": "Confidence below threshold, human review suggested",
  "type": "boolean",
  "applies_to": ["keyword_inference"]
}
```

### Skill × Demand Matrix

| Base Demand | Novice | Intermediate | Expert |
|-------------|--------|--------------|--------|
| high_demand | very_high | high | moderate |
| low_demand | moderate | low | very_low |
| restorative | low | very_low | very_low |

---

*Panel consultation complete: February 8, 2026*
*Decisions D1-D7: Reviewed with modifications*
*Implementation: Lane B or separate sprint*
