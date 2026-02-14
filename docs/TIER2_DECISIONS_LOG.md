# Epistemic Tier 2 — Implementation Decisions Log

**Started**: Friday, February 14, 2026
**Purpose**: Track all implementation decisions for panel review

---

## Decision Format

| ID | Decision | Context | Alternatives Considered | Rationale |
|----|----------|---------|------------------------|-----------|

---

## Sprint 0 Decisions

| ID | Decision | Context | Alternatives | Rationale |
|----|----------|---------|--------------|-----------|
| D0.1 | Place new enums in `web_of_belief.py` | Task 0.1 mapping found all core enums there | New `enums.py` file | Consistency with existing codebase; all epistemic enums co-located |
| D0.2 | Extend `ConstraintType` for link types | No separate `LinkType` enum exists | Create new `LinkType` enum | `ConstraintType` already serves this role; less refactoring |
| D0.3 | Accept 19 pre-existing test failures | Baseline shows failures unrelated to Tier 2 | Fix them first | Out of scope; failures are API wiring issues, not epistemic logic |

---

## Sprint 1 Decisions

| ID | Decision | Context | Alternatives | Rationale |
|----|----------|---------|--------------|-----------|
| D1.1 | Create new `NodeDomain` enum (not extend existing) | No domain enum existed; only `domain: str` field | Extend EpistemicLevel or BeliefKind | Clean separation of concerns; NodeDomain is about knowledge area, not epistemic position or functional role |
| D1.2 | Add `node_domain: Optional[NodeDomain]` field, keep legacy `domain: str` | Backward compatibility with existing serialized data | Replace domain field | Gradual migration; existing code continues to work |
| D1.3 | Place all Tier 2 enums in web_of_belief.py | All existing enums are there | Create new epistemic_enums.py | Consistency; avoid import complexity |
| D1.4 | Add epistemic link types to ConstraintType (not new enum) | ConstraintType already serves as link type enum | Create separate LinkType enum | Less refactoring; existing edge code expects ConstraintType |
| D1.5 | Default confidence for EPISTEMIC_COHERENCE_WARRANT = 0.55 | Coherence alone is moderate evidence | Higher (0.70) or lower (0.40) | Middle ground; coherence without scrutiny is informative but not definitive |
| D1.6 | Default confidence for ARGUMENTATIVE_WARRANT = 0.70 | Survived adversarial scrutiny | Same as mechanism (0.60) | Higher because adversarial testing is strong epistemic filter |
| D1.7 | Default confidence for EPISTEMIC_VIGILANCE_WARRANT = 0.65 | Source quality evaluation | Same as coherence (0.55) | Slightly higher; explicit quality check adds confidence |
| D1.8 | Add GENERALIZABILITY_WARRANT to ConstraintType (Sprint 4b prep) | Type A → Type B claims need explicit link | Defer to Sprint 4b | Pre-emptive; schema change now avoids migration later |
| D1.9 | Forward-reference enums in Belief fields with Optional['EnumName'] | Enums defined before Belief class but used in type hints | String literals only | Type safety with forward references; IDE support |
| D1.10 | Include Sprint 4b fields in Belief now (claim_type, effect_pathway, etc.) | Sprint 4b runs parallel to 2-4 | Add later in Sprint 4b | Avoid schema change mid-sprint; all fields optional so no breakage |

---

## Open Questions

*Questions requiring panel consultation*

| Q# | Question | Context | Options |
|----|----------|---------|---------|
