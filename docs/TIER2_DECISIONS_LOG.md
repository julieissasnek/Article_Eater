# Epistemic Tier 2 — Implementation Decisions Log

**Started**: Friday, February 14, 2026
**Purpose**: Track all implementation decisions for panel review

---

## Decision Format (Enhanced)

Each decision is tracked with:

| Field | Description |
|-------|-------------|
| **ID** | Unique identifier (D{sprint}.{number}) |
| **Decision** | What was decided |
| **Context** | Why this decision arose |
| **Alternatives** | Other options considered |
| **Rationale** | Why this choice was made |
| **Risk** | What could go wrong (Low/Medium/High) |
| **Dependencies** | Other decisions this depends on or affects |
| **Panelist Concerns** | Which expert voices should review this |

---

## Risk Legend

- **Low**: Easily reversible, local impact, no data migration
- **Medium**: Requires refactoring, affects multiple files, may need migration
- **High**: Architectural impact, hard to reverse, affects external interfaces

---

## Sprint 0 Decisions

### D0.1: Place new enums in `web_of_belief.py`
- **Context**: Task 0.1 mapping found all core enums there
- **Alternatives**: Create new `enums.py` file
- **Rationale**: Consistency with existing codebase; all epistemic enums co-located
- **Risk**: Low — file organization only
- **Dependencies**: None
- **Panelist Concerns**: Simon (modularity)

### D0.2: Extend `ConstraintType` for link types
- **Context**: No separate `LinkType` enum exists
- **Alternatives**: Create new `LinkType` enum
- **Rationale**: `ConstraintType` already serves this role; less refactoring
- **Risk**: Low — enum extension is additive
- **Dependencies**: None
- **Panelist Concerns**: Liskov (interface design)

### D0.3: Accept 19 pre-existing test failures
- **Context**: Baseline shows failures unrelated to Tier 2
- **Alternatives**: Fix them first
- **Rationale**: Out of scope; failures are API wiring issues, not epistemic logic
- **Risk**: Low — tracked separately, doesn't affect Tier 2 work
- **Dependencies**: None
- **Panelist Concerns**: None (engineering decision)

---

## Sprint 1 Decisions

### D1.1: Create new `NodeDomain` enum (not extend existing)
- **Context**: No domain enum existed; only `domain: str` field
- **Alternatives**: Extend EpistemicLevel or BeliefKind
- **Rationale**: Clean separation of concerns; NodeDomain is about knowledge area, not epistemic position or functional role
- **Risk**: Low — new enum, no existing code affected
- **Dependencies**: None
- **Panelist Concerns**: Haack (domain vs. level distinction)

### D1.2: Add `node_domain: Optional[NodeDomain]` field, keep legacy `domain: str`
- **Context**: Backward compatibility with existing serialized data
- **Alternatives**: Replace domain field entirely
- **Rationale**: Gradual migration; existing code continues to work
- **Risk**: Low — additive change
- **Dependencies**: D1.1
- **Panelist Concerns**: Simon (migration strategy)

### D1.3: Place all Tier 2 enums in web_of_belief.py
- **Context**: All existing enums are there
- **Alternatives**: Create new epistemic_enums.py
- **Rationale**: Consistency; avoid import complexity
- **Risk**: Low — file grows but remains cohesive
- **Dependencies**: D0.1
- **Panelist Concerns**: Liskov (module cohesion)

### D1.4: Add epistemic link types to ConstraintType (not new enum)
- **Context**: ConstraintType already serves as link type enum
- **Alternatives**: Create separate LinkType enum
- **Rationale**: Less refactoring; existing edge code expects ConstraintType
- **Risk**: Medium — ConstraintType grows; may need splitting later
- **Dependencies**: D0.2
- **Panelist Concerns**: Liskov (single responsibility)

### D1.5: Default confidence for EPISTEMIC_COHERENCE_WARRANT = 0.55
- **Context**: Coherence alone is moderate evidence
- **Alternatives**: Higher (0.70) or lower (0.40)
- **Rationale**: Middle ground; coherence without scrutiny is informative but not definitive
- **Risk**: Medium — affects downstream probability calculations
- **Dependencies**: None
- **Panelist Concerns**: Spohn (rank calibration), Haack (coherence weight)

### D1.6: Default confidence for ARGUMENTATIVE_WARRANT = 0.70
- **Context**: Survived adversarial scrutiny
- **Alternatives**: Same as mechanism (0.60)
- **Rationale**: Higher because adversarial testing is strong epistemic filter
- **Risk**: Medium — may overweight adversarial studies
- **Dependencies**: None
- **Panelist Concerns**: Pollock (defeat resilience), Longino (social epistemics)

### D1.7: Default confidence for EPISTEMIC_VIGILANCE_WARRANT = 0.65
- **Context**: Source quality evaluation
- **Alternatives**: Same as coherence (0.55)
- **Rationale**: Slightly higher; explicit quality check adds confidence
- **Risk**: Medium — depends on quality assessment accuracy
- **Dependencies**: None
- **Panelist Concerns**: Cartwright (source reliability)

### D1.8: Add GENERALIZABILITY_WARRANT to ConstraintType (Sprint 4b prep)
- **Context**: Type A → Type B claims need explicit link
- **Alternatives**: Defer to Sprint 4b
- **Rationale**: Pre-emptive; schema change now avoids migration later
- **Risk**: Low — unused until Sprint 4b
- **Dependencies**: D1.4
- **Panelist Concerns**: None (forward planning)

### D1.9: Forward-reference enums in Belief fields with Optional['EnumName']
- **Context**: Enums defined before Belief class but used in type hints
- **Alternatives**: String literals only
- **Rationale**: Type safety with forward references; IDE support
- **Risk**: Low — Python typing convention
- **Dependencies**: D1.1, D1.3
- **Panelist Concerns**: None (engineering decision)

### D1.10: Include Sprint 4b fields in Belief now (claim_type, effect_pathway, etc.)
- **Context**: Sprint 4b runs parallel to 2-4
- **Alternatives**: Add later in Sprint 4b
- **Rationale**: Avoid schema change mid-sprint; all fields optional so no breakage
- **Risk**: Low — optional fields, no serialization impact
- **Dependencies**: D1.1, D1.3
- **Panelist Concerns**: Simon (planning ahead vs. YAGNI)

---

## Open Questions

*Questions requiring panel consultation*

| Q# | Question | Context | Options |
|----|----------|---------|---------|
