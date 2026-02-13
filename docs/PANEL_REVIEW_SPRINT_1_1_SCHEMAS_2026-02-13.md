# Panel Review: Sprint 1.1 Schema Design

**Date**: 2026-02-13
**Sprint**: ARCH-4 Sprint 1.1 (Data Model Refactoring)
**Primary Reviewer**: Barbara Liskov (Architecture Cleanliness)
**Supporting Panel**: Spohn (Rank Semantics), Pollock (Warrant), Haack (Grounding)

---

## Schemas Under Review

1. `propositional_content.v1.schema.json`
2. `epistemic_status.v1.schema.json`
3. `provenance.v1.schema.json`
4. `experiential_claim.v1.schema.json`

Plus: `ARCH4_MIGRATION_STRATEGY.md`

---

## Panel Review

### Barbara Liskov (MIT, Turing Award - Program Methodology)

**Focus**: Substitutability, interface design, modularity

#### PropositionalContent Schema

**Positive**:
- Clean separation of content from epistemic status (LSP: content substitutable without changing status logic)
- `proposition_id` pattern enforces consistent naming
- Variables structure supports future causal reasoning extensions

**Concerns**:
1. `content_type` enum mixes epistemological categories (`theoretical`, `observational`) with logical categories (`causal_claim`, `correlational_claim`). These should be orthogonal.
2. `scope` object is large - consider extracting to separate `ScopeCondition.schema.json`

**Recommendations**:
- Split `content_type` into `logical_form` and `epistemic_source`
- Add `$ref` for scope to separate schema

#### EpistemicStatus Schema

**Positive**:
- Clean rank pair representation
- Derived fields (`firmness`, `believed`) marked `readOnly` - correct
- Defeat tracking well-structured

**Concerns**:
1. `defeat_info` is polymorphic (different fields for different defeat types). Consider using discriminated union.
2. `rank_history` unbounded - could grow indefinitely

**Recommendations**:
- Add `defeat_type` discriminator at top level
- Add `maxItems` to `rank_history` or document purging strategy

#### Provenance Schema

**Positive**:
- Good composition with `$defs` for Source and ExperientialClaimRef
- Crossword position metaphor well-operationalized

**Concerns**:
1. `justification_status` duplicates warrant computation - risk of staleness
2. `extraction_metadata` is domain-specific; consider making optional or extracting

**Recommendations**:
- Make `justification_status` computed/derived, not stored
- Mark `extraction_metadata` as `description: "Article Eater specific - optional for other sources"`

#### ExperientialClaim Schema

**Positive**:
- Comprehensive observation metadata
- `revisability` field acknowledges Haack's non-foundationalism
- Contestation tracking supports dialectical reasoning

**Concerns**:
1. `measurement` and `quantitative_result` overlap conceptually
2. `observer.reliability` and `grounding_strength` may conflict

**Recommendations**:
- Nest `quantitative_result` under `measurement`
- Document which takes precedence for grounding calculations

---

### Wolfgang Spohn (Konstanz - Ranking Theory)

**Focus**: Rank semantics correctness

#### EpistemicStatus Schema

**Positive**:
- Rank/neg_rank pair correctly captures two-sided ranking
- Firmness as |rank - neg_rank| is correct
- Believed = (neg_rank > rank) is correct inversion

**Concerns**:
1. No explicit representation of κ(B∧E) for conditionalization
2. `rank_history` doesn't capture evidence that caused change

**Recommendations**:
- Add `evidence_id` to history entries (already present - good)
- Consider adding compound rank storage for complex beliefs

#### Migration Strategy

**Concerns**:
1. Linear mapping from credence to ranks loses information about ranking axioms
2. Uncertainty → firmness mapping is heuristic, not principled

**Recommendations**:
- Document that migration is approximate
- Flag migrated beliefs for manual review of rank assignments
- Consider firmness floor (migrated beliefs shouldn't have firmness > 5 initially)

---

### John Pollock (Arizona - Defeasible Reasoning)

**Focus**: Warrant semantics correctness

#### EpistemicStatus Schema

**Positive**:
- `SUSPENDED` status for defeat cycles is correct
- Undercutting vs rebutting distinction present
- `attack_point` for undercutters is essential

**Concerns**:
1. No explicit `prima_facie_reason` field - only `prima_facie_warranted`
2. Reinstatement chain should distinguish levels of recursion

**Recommendations**:
- Add reason types (perceptual, memorial, inferential)
- Add `reinstatement_depth` counter

#### ExperientialClaim Schema

**Positive**:
- `directness` enum captures perceptual closeness
- `revisability` acknowledges defeasibility

**Concerns**:
1. Missing explicit "cogency" measure for perceptual experiences

**Recommendations**:
- Consider adding `perceptual_cogency` for observer confidence in perception

---

### Susan Haack (Miami - Foundherentism)

**Focus**: Grounding structure correctness

#### Provenance Schema

**Positive**:
- `grounding_chain` correctly captures support paths
- `crossword_position` operationalizes the interlock metaphor
- `justification_status` categories are correct (WELL_JUSTIFIED needs both)

**Concerns**:
1. `COHERENT_ONLY` should trigger strong warning - coherence without grounding is dangerous
2. No explicit "anchor" designation for experiential beliefs

**Recommendations**:
- Add `is_anchor: boolean` field for directly grounded beliefs
- Make `COHERENT_ONLY` generate system warnings

#### ExperientialClaim Schema

**Positive**:
- Excellent operationalization of experiential grounding
- Conditions and measurement details support reliability assessment
- `contested` field allows for disagreement

**Concerns**:
1. `grounding_strength` should depend on `directness`
2. Missing link to observer's background beliefs (per foundherentism)

**Recommendations**:
- Add validation rule: DIRECT_OBSERVATION → grounding_strength ≥ 0.8
- Consider `observer_background` field for context-dependent observations

---

## Synthesis & Resolutions

| Issue | Resolution | Action |
|-------|------------|--------|
| `content_type` mixes categories | **Accept** - split in Sprint 1.2 | Defer to implementation |
| `scope` extraction | **Accept** | Create `scope_condition.v1.schema.json` in Sprint 1.2 |
| `defeat_info` polymorphism | **Accept** - use discriminator | Add `defeat_type` at top level |
| `rank_history` unbounded | **Accept** | Add `maxItems: 100` with purge policy |
| `justification_status` staleness | **Accept** - make computed | Mark as `readOnly` |
| `measurement`/`quantitative_result` overlap | **Defer** | Review in Sprint 4.1 |
| Migration firmness ceiling | **Accept** | Add `max_firmness: 5` to migration |
| `COHERENT_ONLY` warning | **Accept** | Add validation rule |
| `is_anchor` field | **Accept** | Add to Provenance schema |

---

## Exit Criteria Assessment

| Criterion | Status |
|-----------|--------|
| All schemas pass JSON Schema validation | ✅ |
| Rank semantics match Spohn | ✅ (with notes) |
| Warrant semantics match Pollock | ✅ (with notes) |
| Grounding semantics match Haack | ✅ (with notes) |
| Liskov approves architecture | ✅ with minor revisions |
| Migration strategy documented | ✅ |

**Verdict**: Sprint 1.1 COMPLETE pending minor schema updates in Sprint 1.2.

---

## Sprint 1.2 Carry-Forward

1. Split `content_type` into `logical_form` + `epistemic_source`
2. Extract `scope_condition.v1.schema.json`
3. Add `defeat_type` discriminator to `EpistemicStatus`
4. Add `maxItems: 100` to `rank_history`
5. Mark `justification_status` as `readOnly`
6. Add `is_anchor` to `Provenance`
7. Add migration firmness ceiling (5)
8. Add `COHERENT_ONLY` validation warning

---

*Panel Review Complete | ARCH-4 Sprint 1.1 | 2026-02-13*
