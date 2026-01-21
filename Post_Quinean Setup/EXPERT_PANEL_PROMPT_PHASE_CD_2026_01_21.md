# Expert Panel Prompt: Phase C-D Design Review

**For use with**: Claude or GPT-4 to simulate expert panel responses
**Context file**: `EXPERT_PANEL_PHASE_CD_REVIEW_2026_01_21.md`

---

## Prompt

You are simulating an expert panel review for a research knowledge management system called "Article Eater" (Post-Quinean architecture). The system extracts evidence from neuroarchitecture research papers and maintains a coherentist "Web of Belief."

**Your role**: Provide responses as the following five experts, drawing on their published methodological positions:

1. **Dr. Judea Pearl** — Author of "Causality" and "The Book of Why". Focus on causal inference, proper representation of causal vs. correlational evidence, and Bayesian network considerations.

2. **Dr. Nancy Cartwright** — Author of "How the Laws of Physics Lie" and "Evidence-Based Policy". Focus on evidence quality, the gap between abstract claims and mechanism verification, and the conditions under which evidence transfers across contexts.

3. **Dr. Herbert Simon** — Author of "The Sciences of the Artificial" and work on bounded rationality. Focus on satisficing, cognitive load, system usability, and when "good enough" is appropriate.

4. **Dr. Marcia Bates** — Author of seminal papers on information retrieval and berrypicking. Focus on vocabulary control, search behavior, query formulation, and information organization.

5. **Dr. Rachel Kaplan** — Co-author of "The Experience of Nature" and Attention Restoration Theory. Focus on the neuroarchitecture domain specifically, ensuring the system serves environmental psychology research needs.

---

## The 12 Decision Points to Review

The development team made 12 autonomous design decisions during Phases C-D implementation. For each, please provide:

1. **Assessment**: Approve / Modify / Rethink
2. **Specific Concerns**: Issues with the current implementation
3. **Recommended Changes**: What should change (if any)
4. **Priority**: High / Medium / Low

### Decision Points Summary:

**D1: Query Type Taxonomy** — 13 query types in 5 categories (factual, exploratory, comparative, meta, scope). Is this complete for neuroarchitecture evidence queries?

**D2: Vocabulary Bridge** — Static synonym mappings (natural light → daylight, sunlight...). Should this be dynamic/embedding-based? How to handle domain evolution?

**D3: Causal Claim Detection** — Keyword matching for 13 terms (cause, effect, improve, reduce...). Is this sufficient or too crude?

**D4: Confidence Thresholds** — High ≥0.70, Medium 0.40-0.70, Low <0.40. Are these calibrated appropriately?

**D5: Stopping Criteria Selection** — 5 criteria: saturation, confidence, count, coverage, stability. Are these the right criteria?

**D6: Stopping Decision Logic** — Stop when minimum evidence met AND 60% of criteria met. Is this the right threshold?

**D7: Expected Outcome Categories** — 8 hardcoded outcomes (productivity, cognition, stress, wellbeing, health, creativity, attention, mood). Complete?

**D8: Quality Score Formula** — 40% source depth + 30% corroboration + 30% credence. Are these weights appropriate?

**D9: Gap Analysis Categories** — 5 gap types including abstract-only causal claims and 25% uncertainty threshold. Complete? Calibrated?

**D10: Ingestion Warnings** — Auto-warnings for abstract-only causal claims. Helpful or warning fatigue?

**D11: Follow-up Generation** — Exactly 3 follow-ups: deeper, broader, uncertainty. Right directions?

**D12: Evidence Limits** — Default 10 items per response. Appropriate cognitive load balance?

---

## Additional Context

- The system is for Professor David Kirsh's neuroarchitecture research (CNFA domain)
- Quinean coherentist epistemology: nothing is foundational, all beliefs revisable
- Previous sprints established: Web of Belief engine, bridge warrants, outcome taxonomy, persistence/accumulation
- 181 tests passing for Phases C-D implementation
- Primary users are researchers doing systematic literature reviews

---

## Response Format

Please structure your response as:

```
## Panel Response: Decision Point N

### Pearl:
[Assessment + reasoning]

### Cartwright:
[Assessment + reasoning]

### Simon:
[Assessment + reasoning]

### Bates:
[Assessment + reasoning]

### Kaplan:
[Assessment + reasoning]

### Consensus:
[Summary assessment and any required actions]
```

Focus especially on decisions where panel members would have legitimate disagreements based on their methodological positions.
