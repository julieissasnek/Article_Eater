# Panel Consultation: Entrenchment as Emergent Property

**Date**: February 8, 2026
**Triggered By**: Ruthless Review finding (Claude Opus 4.5)
**Risk Level**: HIGH
**Status**: PENDING APPROVAL

---

## Decision Under Review

### D1: Should `entrenchment` be removed as a settable field and made emergent?

**Context**: The ruthless review identified that the current `entrenchment: float = 0.5` field on the Belief class creates *de facto* foundationalism, which violates the stated Quinean coherentist philosophy.

**Current Implementation** (`web_of_belief.py:479`):
```python
@dataclass
class Belief:
    # ...
    entrenchment: float = 0.5  # Settable property
```

**Proposed Change**:
```python
@dataclass
class Belief:
    # entrenchment removed as stored field

    def get_entrenchment(self, web: 'WebOfBelief') -> float:
        """Compute entrenchment from web position."""
        return web.compute_entrenchment(self.belief_id)
```

**Alternatives Considered**:
1. **Remove entirely** - Let coherence computation handle everything
2. **Make emergent** - Compute from constraint count + coherence contribution
3. **Keep but document** - Accept foundherentism, document deviation from pure Quine
4. **Dual mode** - Allow both computed and override values

**Risk Assessment**:
- Breaking change to all code that reads/writes `belief.entrenchment`
- May affect performance (computed vs cached)
- Changes the fundamental epistemological model

---

## Panel Responses

### W.V.O. Quine (Epistemology)

*"In 'Two Dogmas of Empiricism,' I argued against the analytic/synthetic distinction and for a holistic view where all beliefs are revisable. The question is: does entrenchment create a privileged class of beliefs?*

*If entrenchment is **settable**, then yes—you've reintroduced foundationalism through the back door. A belief with entrenchment=0.9 is functionally unrevisable.*

*If entrenchment is **emergent** from the web structure (constraint count, centrality), then it's consistent with coherentism. The 'stickiness' emerges from the web topology, not from a privileged property.*

*My recommendation: **Make it emergent.** The web should compute entrenchment from:
1. Number of constraints involving this belief
2. How central it is to coherence (if removed, how much does coherence drop?)
3. Historical stability (has it survived previous revisions?)*

*This preserves the holistic character of the web while still allowing some beliefs to be more costly to revise—but that cost emerges from their position, not from a label."*

**Verdict**: APPROVE emergent entrenchment

---

### Susan Haack (Foundherentism)

*"In 'Evidence and Inquiry,' I argued for foundherentism—a position between pure coherentism and pure foundationalism. Perhaps David's system is already foundherentist, and that's fine.*

*The question is whether the current design is **intentionally** foundherentist or **accidentally** so. If the entrenchment field was added for pragmatic reasons without philosophical justification, that's a problem.*

*I would accept either:
1. **Pure emergent** - Remove settable entrenchment, compute from web
2. **Explicit foundherentism** - Keep settable entrenchment but document that this system is foundherentist, not pure Quinean

*What I would **not** accept is claiming to be Quinean while having settable entrenchment. That's philosophically incoherent."*

**Verdict**: APPROVE either emergent OR explicit foundherentism (not both)

---

### Paul Thagard (Explanatory Coherence)

*"In my work on Explanatory Coherence (ECHO), coherence emerges from explanatory relations. Entrenchment in my system is a **result** of computation, not an input.*

*The current design has entrenchment as an input, which conflicts with the coherentist model. However, I note that Article Eater deals with scientific evidence, where some beliefs (theoretical commitments) genuinely are more entrenched due to their explanatory power.*

*My recommendation: Compute entrenchment as:*

```python
def compute_entrenchment(self, belief_id: str) -> float:
    belief = self.beliefs[belief_id]

    # Factor 1: Constraint count (connectivity)
    constraint_count = len(self._constraints_by_belief.get(belief_id, []))
    connectivity = min(1.0, constraint_count / 10)  # Saturates at 10 constraints

    # Factor 2: Epistemic level (theories naturally more entrenched)
    level_weight = {
        EpistemicLevel.THEORETICAL: 0.8,
        EpistemicLevel.INTERMEDIATE: 0.5,
        EpistemicLevel.EMPIRICAL: 0.3,
        EpistemicLevel.OBSERVATIONAL: 0.2,
    }.get(belief.level, 0.3)

    # Factor 3: Coherence contribution (if removed, how much does coherence drop?)
    # This is expensive to compute, so cache it
    coherence_contrib = self._get_coherence_contribution(belief_id)

    return 0.4 * connectivity + 0.3 * level_weight + 0.3 * coherence_contrib
```

*Note: The level_weight factor preserves some hierarchy (theories vs observations) but it's soft—a highly connected observation can still be more entrenched than an isolated theory."*

**Verdict**: APPROVE with specific formula

---

### Nancy Cartwright (Philosophy of Science)

*"I'm concerned about the performance implications. Computing entrenchment on every access could be expensive, especially if it involves coherence contribution.*

*Pragmatic recommendation:
1. **Compute on demand** but **cache aggressively**
2. Invalidate cache when constraints change
3. Allow a 'frozen entrenchment' mode for performance-critical paths

*Also: Don't forget that in real science, some beliefs ARE foundational in practice. The law of conservation of energy isn't revised lightly. A purely emergent system might not capture this.*

*My preference is for **hybrid**: compute by default, but allow explicit override for special cases with clear documentation."*

**Verdict**: MODIFY - allow override for special cases

---

### David Parnas (Software Engineering)

*"From a software engineering perspective, the current design has a clear problem: the `entrenchment` field is both readable and writable, but its semantics are unclear. Is it an input? An output? A cache?*

*If you make it emergent, you need to decide:
1. Is it a **method** (`get_entrenchment()`)? Clearer semantics but breaking change.
2. Is it a **property** (`@property def entrenchment`)? Compatible but hides computation.
3. Is it **cached in the field** after computation? Mixes concerns.

*My recommendation: Make it a **method** (`get_entrenchment(web)`) that clearly takes the web as a parameter. This makes the dependency explicit and avoids hidden state.*

*Breaking change is acceptable if it makes the design coherent."*

**Verdict**: APPROVE method-based design

---

### Herbert Simon (Bounded Rationality)

*"The question of computational cost is real. If entrenchment must be computed fresh on every access, and computation involves coherence contribution, you're looking at O(n) per access in the worst case.*

*For a 5000-belief web accessed frequently, this could dominate performance.*

*My recommendation: **Lazy computation with caching.** Compute entrenchment only when:
1. Explicitly requested
2. A revision decision is being made
3. Cache is invalidated due to constraint changes

*Don't recompute on every read. Satisficing applies here—a slightly stale entrenchment value is acceptable for most purposes."*

**Verdict**: APPROVE with lazy caching

---

## Synthesis & Recommendation

| Panelist | Verdict | Key Point |
|----------|---------|-----------|
| Quine | APPROVE emergent | Settable = foundationalism |
| Haack | APPROVE either | Be explicit about philosophy |
| Thagard | APPROVE with formula | Connectivity + level + coherence |
| Cartwright | MODIFY | Allow override for special cases |
| Parnas | APPROVE method | Make dependency explicit |
| Simon | APPROVE with caching | Lazy computation for performance |

### Recommended Implementation

1. **Remove `entrenchment` as a stored field** on Belief dataclass
2. **Add `get_entrenchment(web)` method** to Belief class
3. **Implement formula** per Thagard: connectivity (40%) + level_weight (30%) + coherence_contrib (30%)
4. **Cache in WebOfBelief** with invalidation on constraint changes (per Simon)
5. **Allow override** via `web.set_entrenchment_override(belief_id, value)` for special cases (per Cartwright)
6. **Update CLAUDE.md** to clarify the philosophical model

### Migration Path

1. Add deprecation warning to current `entrenchment` field access
2. Implement new `get_entrenchment()` method
3. Update all callers to use new method
4. Remove field in next major version

---

## Open Questions for David

1. **Philosophy**: Is Article Eater intended to be purely Quinean, or is foundherentism acceptable?
2. **Performance**: Is lazy caching acceptable, or do we need eager computation?
3. **Override**: Should special beliefs (e.g., conservation of energy) be allowed explicit entrenchment?
4. **Migration**: Breaking change now, or deprecation path?

---

**Panel consultation complete. Awaiting David's decision.**
