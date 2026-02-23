# Panel Consultation: MVP-0 Contracts & Schemas Design

**Date**: 2026-02-11 (Retroactive)
**Terminal**: Terminal 2
**Decisions Under Review**: D1, D2, D3, D4, D5

---

## Panel Composition

For API schema and information architecture decisions:
- **Dr. Herbert Simon** — Bounded rationality, progressive disclosure
- **Dr. Bas van Fraassen** — Pragmatic theory of explanation, contrast classes
- **Dr. Nancy Cartwright** — Enabling conditions, modularity
- **Dr. Marcia Bates** — Information science, query behavior

---

## Decisions Under Review

### D1: Progressive Disclosure Response Modes (4 Levels)
**Context**: Query responses need to support different information depth needs
**Decision**: Four modes: headline (1 sentence), summary (key evidence), detail (full trace), deep_dive (complete epistemology)
**Alternatives**:
- Binary (short/long) — too coarse
- Three levels — not enough for research use
- Five+ levels — cognitive overload
**Risk Level**: Medium

### D2: Follow-up Types (Exactly 3)
**Context**: Users need guidance on what to ask next
**Decision**: Three types: deeper (more specific), broader (related topics), uncertainty (what we don't know)
**Alternatives**:
- No follow-ups — users left stranded
- Free-form suggestions — inconsistent
- More types (related, comparative, methodological) — too many options
**Risk Level**: Low

### D3: Gap Types Taxonomy (7 Types)
**Context**: Knowledge gaps need classification for prioritization
**Decision**: Seven types: uncertain, unexplored, missing_contrast, low_coverage, theory_conflict, baseline_unknown, blocked_beliefs
**Alternatives**:
- Simple binary (gap/no-gap) — loses information
- Three types (uncertain, unexplored, conflict) — insufficient
- Domain-specific types — not generalizable
**Risk Level**: Medium

### D4: VOI Score in Gap Report
**Context**: Need to prioritize which gaps to fill first
**Decision**: Include Value of Information (VOI) score for each gap
**Alternatives**:
- Priority only (no quantification) — subjective
- Cost-benefit analysis — too complex for MVP
- No prioritization — overwhelming
**Risk Level**: Low

### D5: Contrast Class in Response Schema
**Context**: Answers depend on what they're contrasted with (per van Fraassen)
**Decision**: Include implicit contrast class in scope_conditions
**Alternatives**:
- Explicit contrast_class field — clutters API
- No contrast handling — lose explanatory context
- Contrast in metadata only — hidden from users
**Risk Level**: Low

---

## Panel Responses

### Dr. Herbert Simon (Bounded Rationality):

**On D1 (Progressive Disclosure)**:
"The four-level hierarchy is exactly right for managing cognitive load. Each level represents a different user goal:
- **Headline**: Quick answer, satisficing complete
- **Summary**: Decision support with confidence bounds
- **Detail**: Research validation
- **Deep dive**: Expert analysis

The key insight is that most users stop at summary. The deeper levels exist for when satisficing fails.

**Approved**. This is textbook bounded rationality in API design."

**On D2 (Follow-up Types)**:
"Three follow-up types is the magic number. More would cause choice paralysis; fewer would constrain exploration. The types map to natural information-seeking behavior:
- **Deeper**: Narrowing search (convergent)
- **Broader**: Expanding search (divergent)
- **Uncertainty**: Meta-search (epistemic)

**Approved**. Keep exactly three."

---

### Dr. Bas van Fraassen (Pragmatic Explanation):

**On D3 (Gap Types)**:
"The 'missing_contrast' gap type is crucial. An answer without a contrast class is not an explanation—it's just a description. I'm pleased to see this distinction preserved.

The taxonomy correctly captures that knowledge gaps are not just about missing data (unexplored) but about missing *structure* (missing_contrast, baseline_unknown).

**Approved**. Consider adding 'ambiguous_contrast' for cases where multiple contrasts are equally valid."

**On D5 (Contrast Class in Response)**:
"Embedding the contrast class in scope_conditions is pragmatically correct. Making it too explicit would burden casual users; hiding it entirely would mislead researchers.

The scope_conditions approach lets the contrast emerge naturally from population and setting.

**Approved**. Document that scope_conditions implicitly defines the contrast class."

---

### Dr. Nancy Cartwright (Capacities and Enabling Conditions):

**On D3 (Gap Types)**:
"I'm particularly interested in the 'blocked_beliefs' type. This captures my work on enabling conditions—a capacity (belief) may be true but not manifest without its enabling conditions being met.

For example: 'Natural light improves productivity' may be blocked if the enabling condition 'adequate thermal comfort' is not met.

**Approved with recommendation**: Track which enabling conditions are blocking, not just that blocking occurred."

**On D4 (VOI Score)**:
"Value of Information is the correct framework for gap prioritization. It correctly captures that some knowledge gaps matter more than others based on:
1. Decision impact (what would change if we knew)
2. Uncertainty reduction (how much we'd learn)
3. Feasibility (can we actually fill it)

**Approved**. Consider making the VOI calculation transparent in the schema."

---

### Dr. Marcia Bates (Information Seeking):

**On D1 (Progressive Disclosure)**:
"This maps well to berrypicking behavior. Users don't search linearly—they grab relevant pieces and move on. The four levels support:
- **Headline**: Quick berry pick
- **Summary**: Modest cluster harvest
- **Detail**: Systematic branch exploration
- **Deep dive**: Exhaustive tree search

**Approved**. The 'summary' default is correct—it's the most common stopping point."

**On D2 (Follow-up Types)**:
"The three types correspond to my model of query reformulation:
- **Deeper** → Specification moves (more terms)
- **Broader** → Generalization moves (fewer terms)
- **Uncertainty** → Lateral moves (different angle)

The 'uncertainty' type is particularly valuable—it explicitly invites meta-cognition about what we don't know.

**Approved**. Ensure follow-ups are executable queries, not just natural language."

---

## Synthesis & Resolutions

| Decision | Panel Verdict | Action Required |
|----------|---------------|-----------------|
| D1 | **APPROVED** | No changes; document satisficing rationale |
| D2 | **APPROVED** | Keep exactly 3 types; ensure executable |
| D3 | **APPROVED** | Consider adding 'ambiguous_contrast' (deferred) |
| D4 | **APPROVED** | Consider making VOI calculation transparent |
| D5 | **APPROVED** | Document that scope_conditions defines contrast |

---

## Action Items

### Immediate
1. [x] Schema correctly implements progressive disclosure
2. [x] Follow-up types are executable (executable_query field present)
3. [x] Gap types include blocked_beliefs per Cartwright

### Deferred
4. [ ] Add 'ambiguous_contrast' gap type if needed
5. [ ] Track which enabling conditions are blocking (enhance blocked_beliefs)
6. [ ] Make VOI calculation transparent in documentation

---

## Panel Sign-off

**Status**: APPROVED

All five decisions follow established patterns from information science (Bates), decision theory (Simon), and philosophy of science (van Fraassen, Cartwright). The schema design is appropriate for MVP with clear extension paths.

*Panel consultation complete: 2026-02-11*
