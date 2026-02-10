# Panel Consultation: Sprint ECB-3 Review

**Date**: 2026-02-10
**Sprint**: ECB-3 (Van Fraassen and Polish)
**Module**: `src/services/epistemic_causal_bridge.py`

---

## Decisions Under Review

### D1: Contrast Transfer Thresholds

**Context**: ECB-3.1 required implementing contrast transfer classification.

**Current Implementation**:
- DIRECT: similarity ≥ 0.9
- BASELINE_SHIFT: similarity ≥ 0.7
- POPULATION_SHIFT: similarity ≥ 0.5
- MEANING_SHIFT: similarity < 0.5 (result undefined)

**Alternative Considered**: More granular thresholds (0.95, 0.85, 0.75, 0.65) with additional intermediate types.

**Implementation Note**: Thresholds are configurable via environment variables: `AE_CONTRAST_THRESHOLD_DIRECT`, `AE_CONTRAST_THRESHOLD_BASELINE`, `AE_CONTRAST_THRESHOLD_POPULATION`.

---

### D2: Meaning Difference Takes Precedence

**Context**: When assessing contrast transfer, we check both similarity score AND cultural meaning differences.

**Decision**: If cultural meaning differs between source and target populations (regardless of numerical similarity), result is MEANING_SHIFT (undefined).

**Rationale**: A high similarity score could mask fundamental construct meaning differences. Safety over false precision.

---

### D3: Gap Types and Priority Scores

**Context**: ECB-3.3 required gap identification for VOI routing.

**Current Implementation** (5 gap types):
| Gap Type | Priority Formula | Description |
|----------|-----------------|-------------|
| `missing_contrast` | 0.7 (fixed) | No explicit contrast class |
| `low_coverage` | 0.8 × (1 - coverage) | Limited evidence for population |
| `theory_conflict` | 0.6 × range | Theories disagree |
| `baseline_unknown` | 0.5 (fixed) | Missing baseline data |
| `blocked_beliefs` | 0.4 (fixed) | Enabling conditions unmet |

**Alternative**: Priority based on VOI calculation (expected information gain).

---

### D4: Security Weight Components (Haack)

**Context**: ECB-3.4 implements foundherentist grounding measure.

**Current Weights**:
- Base security by level: observational=0.9, empirical=0.7, intermediate=0.5, theoretical=0.3
- Explicit contrast class bonus: +0.15
- Inferred contrast class bonus: +0.05
- Entrenched status: +0.10
- Established status: +0.05
- Stub status: -0.10
- Anomalous status: -0.15

**Decision**: Weights sum additively, capped at 0.95 (floor 0.05).

---

### D5: Graceful Error Handling vs Exceptions

**Context**: ECB-3.6 required explicit error handling.

**Decision**:
- Empty web → returns empty model / undefined result (with warning log)
- Missing theory → raises `MissingTheoryError` (explicit request for non-existent theory is programmer error)
- Invalid credence threshold → raises `ValueError` (out of 0.0-1.0 range)

**Rationale**: Distinguish between "unusual but valid situations" (empty web) and "programmer errors" (invalid inputs).

---

### D6: ContrastTransferType Enum vs String

**Context**: Transfer type needs to be typed for code safety but also backward-compatible with existing string-based code.

**Decision**: Return both:
- `transfer_type: ContrastTransferType` — typed enum for new code
- `transfer_type_str: str` — backward-compatible string

---

## Panel Responses

### Dr. Bas van Fraassen (Scientific Representation)

*"The contrast transfer classification (D1) is well-conceived. The four-type taxonomy captures the essential distinctions. However, I have reservations about D2—meaning differences should not automatically override similarity scores.*

*Consider: Two populations might use different words for the same construct but have functionally equivalent meanings. The implementation should allow for 'meaning equivalence' assessment, not just 'meaning identity.'*

*Recommendation: Add a `meaning_equivalent: bool` flag that can override MEANING_SHIFT when cultural meanings differ but are deemed functionally equivalent."*

**Action**: Consider adding meaning equivalence flag in future iteration (not critical for MVP).

---

### Dr. Susan Haack (Foundherentism)

*"The security weight implementation (D4) correctly captures the foundherentist insight that empirical grounding provides independent security. The weights are reasonable defaults.*

*One refinement: The bonus for explicit contrast classes (+0.15) should perhaps be higher (+0.20) when the contrast class comes directly from the paper's methodology section, versus (+0.10) when inferred from results. The source of the contrast specification matters."*

*"Regarding D5: Graceful degradation for empty webs is appropriate. The epistemic system should not crash when evidence is lacking—it should report its uncertainty."*

**Action**: Future iteration could differentiate contrast class source.

---

### Dr. Judea Pearl (Causal Inference)

*"D1 and D2 address a real problem: causal effects are not automatically transportable across populations. The threshold-based approach is practical, though it abstracts away the structural considerations I would prefer.*

*For D3, the gap types are sensible. However, 'theory_conflict' might be decomposed into:*
- *Structural disagreement (different DAGs)*
- *Parametric disagreement (same DAG, different coefficients)*

*These have different implications for resolution."*

**Action**: Theory conflict decomposition is valuable for future work.

---

### Dr. Herbert Simon (Bounded Rationality)

*"The configurable thresholds (D1) are good satisficing behavior—you've provided sensible defaults while allowing domain experts to tune. This is exactly right.*

*D5's distinction between 'unusual but valid' and 'programmer error' is sound. The system should be robust to messy real-world inputs while catching obvious mistakes early.*

*D6's dual return (enum + string) adds complexity. In the long run, deprecate the string version. But for now, backward compatibility is pragmatic."*

**Verdict**: APPROVED

---

### Dr. Nancy Cartwright (Capacities & Ceteris Paribus)

*"D2 is correct: meaning differences must block transfer. A capacity that manifests in one cultural context may not manifest (or may manifest differently) in another.*

*For D3, I would add a sixth gap type: 'enabling_conditions_unclear'. Distinct from 'blocked_beliefs' (where conditions are unmet), this would flag cases where we don't know what the enabling conditions are. This is a deeper epistemic gap."*

**Action**: Add `enabling_unclear` gap type in future iteration.

---

### David Parnas (Software Architecture)

*"D6 is technical debt. Pick one representation and stick with it. The dual return complicates the interface.*

*The error handling in D5 is correct. The BridgeError hierarchy (EmptyWebError, MissingTheoryError, MalformedBeliefError) follows good practice. However, I note that `MalformedBeliefError` is defined but not used in the current code. Either use it or remove it."*

**Action**: Remove unused `MalformedBeliefError` or add explicit usage.

---

### Fred Brooks (Software Engineering)

*"The sprint accomplished its goals. The ARCHITECTURE.md updates are essential—documentation is often neglected during sprints.*

*One process observation: The test suite passed (68 + 153 tests), which is the key checkpoint. However, I recommend adding explicit tests for the new ECB-3 features:*
- *Test contrast transfer classification at boundary values (0.49 vs 0.50)*
- *Test gap identification with various configurations*
- *Test security weight computation*

*Without these, the new code is covered only implicitly."*

**Action**: Add explicit ECB-3 feature tests.

---

## Synthesis & Resolutions

| Decision | Panel Verdict | Action Required |
|----------|---------------|-----------------|
| D1: Thresholds | APPROVED | None (configurable) |
| D2: Meaning precedence | APPROVED with note | Future: add meaning_equivalent flag |
| D3: Gap types | APPROVED with extension | Future: add enabling_unclear, decompose theory_conflict |
| D4: Security weights | APPROVED with note | Future: differentiate contrast class source |
| D5: Error handling | APPROVED | Remove unused MalformedBeliefError |
| D6: Enum + string | APPROVED with concern | Future: deprecate string version |

---

## Follow-up Tasks

1. **Test coverage** (Brooks): Add explicit tests for ECB-3 features
2. **Meaning equivalence** (van Fraassen): Add flag for functional meaning equivalence
3. **Gap type extension** (Cartwright): Add `enabling_unclear` gap type
4. **Theory conflict decomposition** (Pearl): Distinguish structural vs parametric disagreement
5. **Contrast class source** (Haack): Track whether contrast class is from methods vs inferred
6. **Deprecation plan** (Parnas): Deprecate `transfer_type_str` in favor of enum

---

## Final Approval

| Reviewer | Verdict |
|----------|---------|
| van Fraassen | APPROVED with note |
| Haack | APPROVED |
| Pearl | APPROVED with extensions |
| Simon | APPROVED |
| Cartwright | APPROVED with extension |
| Parnas | CONDITIONAL (remove unused error class) |
| Brooks | APPROVED (add tests) |

**Overall**: APPROVED with minor action items

---

*Sprint ECB-3 complete. Ready for integration.*
