# Panel Consultation: MVP-3 Query Engine Implementation

**Date**: 2026-02-11
**Owner**: Terminal 2
**Component**: Query Engine (`src/services/query_engine.py`)
**Tests**: 42 tests passing

---

## Summary

MVP-3 implements the Query Engine for Article Eater, providing a natural language interface to query the accumulated web of beliefs. The engine implements the `ae.query_request.v1` → `ae.query_response.v1` contract with progressive disclosure (per Simon).

---

## Decisions Under Review

### D1: Test Fixture Design

**Context**: Unit tests need a populated WebOfBelief to test query functionality.

**Current Choice**: Use direct WebOfBelief injection for unit tests, bypassing WebAccumulator entirely.

**Alternatives Considered**:
- (a) Mock the WebAccumulator with unittest.mock
- (b) Use real WebAccumulator with temp file paths
- (c) Use factory fixtures that create both

**Risk**: May miss integration issues between QueryEngine and WebAccumulator. The test web has 7 beliefs; real accumulated webs may have thousands.

**Question for Panel**: Is direct web injection sufficient for unit testing, or should we include integration tests with the full accumulator stack?

---

### D2: Response Schema Validation

**Context**: Tests need to verify QueryEngine produces valid `ae.query_response.v1` responses.

**Current Choice**: Use structural checks (key presence, type checks) rather than full JSON Schema validation.

**Alternatives Considered**:
- (a) Full jsonschema validation on every response
- (b) Validate only in integration tests
- (c) Create a validation helper function used by both tests and production

**Risk**: Schema drift between implementation and tests. Implementation may produce fields not in schema, or miss required fields.

**Question for Panel**: Should we add schema validation as a test utility, or is structural checking sufficient given the contract tests in MVP-0?

---

### D3: Gap Detection Thresholds

**Context**: `_identify_gaps()` needs to decide what constitutes "high uncertainty" for flagging gaps.

**Current Choice**: Uncertainty > 0.3 is considered "high" (hardcoded threshold).

**Alternatives Considered**:
- (a) Make threshold configurable via request parameter
- (b) Use percentile-based threshold (top 20% most uncertain)
- (c) Use 0.25 or 0.35 as threshold

**Risk**:
- 0.3 may not align with user expectations
- Fixed threshold doesn't adapt to web diversity

**Question for Panel**: What is the epistemically justified threshold for "high uncertainty"? Should this be domain-configurable?

---

### D4: Follow-Up Generation Strategy

**Context**: Per Simon, responses must include exactly 3 follow-ups (deeper, broader, uncertainty).

**Current Choice**: Generate follow-ups from query intent using template strings:
```python
# Deeper: "What specific mechanisms explain the effect of {subject}?"
# Broader: "What other factors are related to {object or subject}?"
# Uncertainty: "What don't we know about {subject}?"
```

**Alternatives Considered**:
- (a) Use LLM to generate contextually-aware follow-ups
- (b) Use pre-defined question banks per topic
- (c) Generate from belief content itself

**Risk**: Template-based questions may feel generic. "What specific mechanisms..." doesn't adapt to domain.

**Question for Panel**: Are template-based follow-ups acceptable for MVP, or should we invest in more contextual generation?

---

### D5: Search Algorithm Heuristics

**Context**: `_search_web()` must find relevant beliefs given parsed query intent.

**Current Choice**: Term-based matching with scoring:
- +2 for term in belief content
- +1 for term in belief tags
- Sort by score (descending), then credence (descending)

**Alternatives Considered**:
- (a) TF-IDF scoring
- (b) Semantic similarity (embeddings)
- (c) Graph-based relevance (beliefs connected to matched beliefs)

**Risk**: Simple term matching may miss semantically related beliefs. "Daylight" won't match "sunlight" unless vocabulary expansion captures it.

**Question for Panel**: Is term matching sufficient for MVP? What search sophistication is justified for a research tool?

---

### D6: Theory Filter Implementation

**Context**: Requests can include `context.theory_filter` to restrict results to specific theories.

**Current Choice**: Check if `belief.theory_id in context["theory_filter"]` (singular field).

**Alternatives Considered**:
- (a) Support multiple theory_ids per belief
- (b) Use theory inheritance (ART includes sub-theories)
- (c) No theory filtering

**Risk**: Current implementation only works with single theory_id. Beliefs may relate to multiple theories.

**Question for Panel**: Should beliefs support multiple theory associations, or is the current single-theory model sufficient?

---

### D7: Clarification vs No-Results Handling

**Context**: Parser may return `needs_clarification=True` for ambiguous queries.

**Current Choice**: Return `status="clarification_needed"` with suggested refinements. Tests handle this as valid response.

**Alternatives Considered**:
- (a) Always attempt search, even for ambiguous queries
- (b) Return partial results with clarification prompt
- (c) Reject ambiguous queries as errors

**Risk**: Overly aggressive clarification requests may frustrate users who just want results.

**Question for Panel**: What is the right balance between precision (clarification) and recall (attempt search anyway)?

---

### D8: Evidence Causal Detection

**Context**: Evidence items should flag `is_causal=True` for causal claims.

**Current Choice**: Keyword detection - check for causal verbs in belief content:
```python
causal_keywords = ['cause', 'effect', 'increase', 'decrease', 'improve',
                  'reduce', 'lead to', 'result in', 'affect']
```

**Alternatives Considered**:
- (a) Use belief's EpistemicLevel (MECHANISTIC implies causal)
- (b) Parse belief for causal structure
- (c) Use causal_direction field from web_of_belief

**Risk**: Keyword matching is imprecise. "This does not affect X" would incorrectly flag as causal.

**Question for Panel**: What causal detection method is most appropriate for communicating evidential claims to users?

---

## Implementation Decisions (Already Made)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Response generation | Use QueryResponseGenerator from existing code | Reuse working code |
| Lazy initialization | Properties load components on first use | Efficient for CLI |
| Error handling | Return error response dict, not exceptions | Contract-compliant |
| CLI colors | ANSI codes with green/yellow/red status | Per WCAG accessibility |

---

## Panel Consultation Request

**Convening Panel**: Pearl (causality), Simon (progressive disclosure), Cartwright (scope conditions), Bates (vocabulary), Kaplan (domain)

**Questions**:
1. D3: What uncertainty threshold indicates a knowledge gap worth flagging?
2. D5: Is term matching sufficient for MVP search, or do we need semantic similarity?
3. D7: Should we prefer precision (clarification) or recall (attempt search) for ambiguous queries?
4. D8: How should we detect causal claims for user communication?

---

## Files Affected

| File | Change |
|------|--------|
| `src/services/query_engine.py` | NEW - 711 lines |
| `src/cli/query.py` | NEW - 255 lines |
| `tests/test_query_engine.py` | NEW - 42 tests |

---

## Testing Summary

- 42 tests passing
- Coverage: initialization, simple queries, contract queries, progressive disclosure, follow-ups, gap detection, search algorithm, evidence items, metadata, error handling, stats, integration
- Test fixture: 7 beliefs covering light/productivity, mood, cognition, noise, temperature, ART theory

---

---

## Panel Responses

### Dr. Judea Pearl (Causal Inference)

**On D3 (Gap Detection Thresholds)**:
The threshold for "high uncertainty" should be grounded in decision-theoretic value of information. A belief with uncertainty 0.3 may or may not warrant investigation depending on its centrality to causal pathways. I recommend:
- **Resolution**: Add VOI-based gap prioritization. Uncertainty alone is insufficient; multiply by entrenchment to get "value of reducing uncertainty."
- **Threshold**: 0.3 is acceptable as a first filter, but rank gaps by VOI score, not raw uncertainty.

**On D8 (Causal Detection)**:
Keyword matching for causality is epistemically problematic. "Increases" can be correlational. You should:
- **Resolution**: Check belief's `causal_direction` field from web_of_belief if available. The existing CausalDirection enum (FORWARD, CORRELATIONAL, etc.) is the proper source of truth.
- Fallback to keywords only if causal_direction is UNKNOWN.

### Dr. Herbert Simon (Bounded Rationality, Progressive Disclosure)

**On D4 (Follow-Up Generation)**:
Template-based follow-ups are acceptable for MVP. The three types (deeper, broader, uncertainty) implement satisficing—users get reasonable next steps without computational expense. However:
- **Resolution**: Track which follow-ups users actually click. Learn from usage patterns.
- Templates should be parameterized by domain vocabulary when available.

**On D7 (Clarification vs No-Results)**:
This is a classic precision-recall tradeoff. For a research tool:
- **Resolution**: Default to attempting search with warning, rather than blocking for clarification. Researchers prefer seeing partial results they can refine.
- Return `status="partial"` with clarification suggestions rather than `status="clarification_needed"` blocking results.

### Dr. Nancy Cartwright (Philosophy of Science, Capacities)

**On D3 (Gap Detection)**:
Uncertainty thresholds must account for epistemic level. A theoretical claim with uncertainty 0.25 may be more concerning than an empirical claim with uncertainty 0.35, because theoretical claims propagate to many empirical predictions.
- **Resolution**: Weight uncertainty by epistemic level. THEORETICAL uncertainty × 1.5, EMPIRICAL × 1.0.

**On D6 (Theory Filter)**:
Single theory_id is a significant limitation. Beliefs often bridge theories (e.g., "ART predicts what SRT explains"). The constraint limits cross-theoretical analysis.
- **Resolution**: Add `theory_ids: List[str]` to Belief, maintaining backward compatibility with single theory_id for now. Migration can happen incrementally.

### Dr. Marcia Bates (Information Science, Vocabulary)

**On D5 (Search Algorithm)**:
Term matching is necessary but not sufficient. Cross-field vocabulary bridging is essential for interdisciplinary research. Your vocabulary_expansions mechanism is correct in principle.
- **Resolution**: Ensure vocabulary expansions from QueryParser are actually used in search. Verify the existing vocabulary bridge is being invoked.
- For MVP, term matching + vocabulary expansion is sufficient. Semantic similarity is a Phase 2 enhancement.

**On D2 (Schema Validation)**:
Structural checking is acceptable for unit tests, but add at least one integration test that validates against the actual JSON Schema. This catches drift.
- **Resolution**: Add `test_response_validates_schema()` that loads the schema and validates a response.

### Dr. Rachel Kaplan (Environmental Psychology, Domain Expert)

**On D4 (Follow-Up Generation)**:
The template "What specific mechanisms explain the effect of {subject}?" assumes mechanistic thinking. For environmental psychology, questions about "under what conditions" or "for whom" are equally important.
- **Resolution**: Add a fourth follow-up type or modify "deeper" to include scope conditions: "Under what conditions does {subject} affect {object}?"

**On D5 (Search)**:
The test fixtures are too narrow. Seven beliefs about light/temperature miss the richness of the domain. However, for unit testing this is acceptable.
- **Resolution**: Create a separate integration test fixture with 50+ diverse beliefs from actual extraction output.

---

## Synthesis & Resolutions

| Decision | Panel Verdict | Action Required | Priority |
|----------|---------------|-----------------|----------|
| D1 | APPROVED with addition | Add integration test with full accumulator | Low |
| D2 | APPROVED with addition | Add one schema validation test | Medium |
| D3 | REVISE | Weight uncertainty by epistemic level; use VOI for ranking | Medium |
| D4 | APPROVED with note | Consider scope-condition follow-up for Phase 2 | Low |
| D5 | APPROVED | Verify vocabulary expansion is used; term matching OK for MVP | Low |
| D6 | DEFER | Multi-theory support is Phase 2; single theory OK for MVP | Low |
| D7 | REVISE | Change to `status="partial"` with clarification, not blocking | High |
| D8 | REVISE | Use causal_direction field, not keywords | High |

---

## Repairs Required

### High Priority

1. **D7: Clarification Handling** - Change clarification_needed to return partial results with suggestions, not block
2. **D8: Causal Detection** - Use belief.causal_direction instead of keyword matching

### Medium Priority

3. **D3: Gap Detection** - Weight uncertainty by epistemic level (THEORETICAL × 1.5)
4. **D2: Schema Test** - Add one test that validates response against JSON Schema

### Low Priority (Phase 2)

5. **D6: Multi-theory** - Support multiple theory_ids per belief
6. **D4: Scope Follow-up** - Add "under what conditions" type
7. **D1/D5: Integration Tests** - Larger fixture, full accumulator stack

---

## Repairs Applied

### High Priority (DONE)

1. **D7: Clarification Handling** - Changed to return `status="partial"` with clarification suggestions instead of blocking. Search is now attempted even for ambiguous queries.

2. **D8: Causal Detection** - Now uses `belief.causal_direction` field (CausalDirection enum) instead of keyword matching. Keywords are fallback only for UNKNOWN direction.

### Medium Priority (DONE)

3. **D3: Gap Detection** - Weighted uncertainty by epistemic level. THEORETICAL uncertainty × 1.5, EMPIRICAL × 1.0.

4. **D2: Schema Test** - Added `TestSchemaValidation` class with 2 tests:
   - `test_response_validates_schema()` - Full jsonschema validation
   - `test_response_has_required_fields()` - Structural validation

### Test Results

- 44 tests passing (42 original + 2 new)
- All repairs verified

---

## Next Steps

1. Update ACTIVE_TASKS.md with MVP-3 completion
2. Integration with MVP-GUI (Streamlit wiring)
3. Phase 2 items: Multi-theory support (D6), Scope follow-ups (D4), Integration tests with full accumulator (D1/D5)
