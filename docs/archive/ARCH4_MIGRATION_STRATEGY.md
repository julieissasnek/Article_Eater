# ARCH-4 Migration Strategy: Credence/Entrenchment → Rank/Warrant

**Date**: 2026-02-13
**Sprint**: 1.1 (Data Model Refactoring)
**Status**: Draft for panel review

---

## 1. Overview

This document describes the migration path from the legacy epistemic representation (credence + entrenchment) to the new formal epistemic calculus (rank + warrant + grounding). The migration must:

1. Preserve semantic content of existing 128+ beliefs
2. Maintain backward compatibility during transition
3. Support dual-format operation for BN_graphical bridge
4. Be reversible if issues arise

---

## 2. Legacy Format (v1)

```python
# Current belief representation
class Belief:
    id: str
    content: str
    level: EpistemicLevel  # THEORETICAL, INTERMEDIATE, EMPIRICAL, OBSERVATIONAL
    credence: Credence
        value: float  # [0, 1] - point estimate of belief strength
        uncertainty: float  # [0, 1] - meta-uncertainty about credence
    # Note: entrenchment is now computed, not stored (V23.0.0)
```

### Credence Semantics
- `credence.value = 0.8` means "80% confident this belief is true"
- `credence.uncertainty = 0.25` means "uncertain about that 80%"
- Purely cardinal (continuous 0-1 scale)
- Combines degree of belief with strength of evidence

---

## 3. New Format (v2)

```python
# New belief representation (ARCH-4)
class Belief:
    id: str
    content: PropositionalContent
    status: EpistemicStatus
        rank: int  # κ(B) - degree of disbelief [0, ∞)
        neg_rank: int  # κ(¬B) - degree of disbelief in negation
        warrant_status: WarrantStatus  # WARRANTED, DEFEATED, SUSPENDED, UNGROUNDED
    provenance: Provenance
        sources: List[Source]
        grounding_score: float  # [0, 1]
        grounding_chain: List[str]  # belief IDs to experiential basis
```

### Rank Semantics (Spohn)
- `rank = 0` means "not disbelieved" (believed)
- `rank = 5` means "strongly disbelieved"
- Ordinal, not cardinal
- Separate representation for belief (rank) and disbelief (neg_rank)
- `believed = (neg_rank > rank)`

### Warrant Semantics (Pollock)
- `WARRANTED` = justified and undefeated
- `DEFEATED` = has undefeated rebutting or undercutting defeater
- `SUSPENDED` = in defeat cycle
- `UNGROUNDED` = no chain to experiential basis

---

## 4. Migration Functions

### 4.1 Credence → Rank Conversion

**Principle**: Credence captures both strength and direction. Ranks must separate these.

```python
def credence_to_ranks(credence_value: float, uncertainty: float) -> tuple[int, int]:
    """
    Convert legacy credence to Spohn rank pair.

    Mapping logic:
    - credence < 0.5 → disbelieved (rank > neg_rank)
    - credence > 0.5 → believed (neg_rank > rank)
    - credence = 0.5 → suspended (rank = neg_rank)

    Uncertainty affects firmness (difference between ranks).
    """
    # Determine direction
    if credence_value >= 0.5:
        # Believed: B has low disbelief, ¬B has higher disbelief
        strength = credence_value - 0.5  # [0, 0.5]
        firmness = int(strength * 10 * (1 - uncertainty))  # [0, 5] typical
        rank = 0
        neg_rank = firmness
    else:
        # Disbelieved: B has high disbelief, ¬B has low disbelief
        strength = 0.5 - credence_value  # [0, 0.5]
        firmness = int(strength * 10 * (1 - uncertainty))
        rank = firmness
        neg_rank = 0

    return (rank, neg_rank)
```

**Example conversions**:

| Legacy Credence | Uncertainty | New Rank | New Neg_Rank | Firmness | Believed? |
|-----------------|-------------|----------|--------------|----------|-----------|
| 0.90 | 0.10 | 0 | 4 | 4 | Yes |
| 0.75 | 0.25 | 0 | 2 | 2 | Yes |
| 0.60 | 0.40 | 0 | 1 | 1 | Yes (weakly) |
| 0.50 | 0.50 | 0 | 0 | 0 | Suspended |
| 0.40 | 0.30 | 1 | 0 | 1 | No |
| 0.20 | 0.10 | 3 | 0 | 3 | No |

### 4.2 Level → Initial Warrant Mapping

**Principle**: Epistemic level provides initial warrant status.

```python
def level_to_warrant(level: EpistemicLevel, has_defeaters: bool) -> WarrantStatus:
    """
    Map epistemic level to initial warrant status.

    Observational beliefs are prima facie warranted (directly grounded).
    Other levels need support chain checked.
    """
    if has_defeaters:
        return WarrantStatus.DEFEATED

    if level == EpistemicLevel.OBSERVATIONAL:
        return WarrantStatus.WARRANTED  # Prima facie warranted
    elif level == EpistemicLevel.EMPIRICAL:
        # Check if grounding chain exists
        return WarrantStatus.WARRANTED  # Assume grounded for migration
    elif level in (EpistemicLevel.INTERMEDIATE, EpistemicLevel.THEORETICAL):
        # Need to check support from warranted beliefs
        return WarrantStatus.WARRANTED  # Assume supported for migration
    else:
        return WarrantStatus.UNGROUNDED
```

### 4.3 Entrenchment → Grounding Score

**Principle**: Emergent entrenchment (V23.0.0) provides some grounding signal.

```python
def entrenchment_to_grounding(
    entrenchment: float,
    level: EpistemicLevel,
    constraint_count: int
) -> float:
    """
    Convert emergent entrenchment to Haack grounding score.

    Entrenchment formula (V23.0.0):
        40% connectivity + 30% level_weight + 30% coherence_contrib

    Grounding should be more sensitive to level and less to connectivity.
    """
    # Level weights for grounding (observational = highest)
    level_grounding = {
        EpistemicLevel.OBSERVATIONAL: 1.0,
        EpistemicLevel.EMPIRICAL: 0.7,
        EpistemicLevel.INTERMEDIATE: 0.4,
        EpistemicLevel.THEORETICAL: 0.2
    }

    base_grounding = level_grounding.get(level, 0.3)

    # Integration bonus (connected beliefs are better grounded via crossword)
    integration_bonus = min(0.3, constraint_count * 0.02)

    grounding = base_grounding + integration_bonus
    return min(1.0, grounding)
```

---

## 5. Migration Script Structure

```python
# scripts/migrate_beliefs_to_v24.py

def migrate_belief(legacy_belief: dict) -> dict:
    """Migrate single belief from v1 to v2 format."""

    # 1. Convert content to PropositionalContent
    content = PropositionalContent(
        proposition_id=legacy_belief['id'],
        canonical_form=legacy_belief['content'],
        content_type=infer_content_type(legacy_belief),
        domain=extract_domain(legacy_belief)
    )

    # 2. Compute epistemic status
    rank, neg_rank = credence_to_ranks(
        legacy_belief['credence']['value'],
        legacy_belief['credence']['uncertainty']
    )

    # 3. Determine warrant (placeholder until Sprint 3)
    warrant = level_to_warrant(
        legacy_belief['level'],
        has_defeaters=False  # Will be computed in Sprint 3
    )

    status = EpistemicStatus(
        rank=rank,
        neg_rank=neg_rank,
        warrant_status=warrant,
        prima_facie_warranted=True,  # Assume for migration
        last_computed=datetime.now()
    )

    # 4. Build provenance
    provenance = Provenance(
        sources=extract_sources(legacy_belief),
        grounding_score=entrenchment_to_grounding(
            get_entrenchment(legacy_belief['id']),
            legacy_belief['level'],
            get_constraint_count(legacy_belief['id'])
        ),
        directness=level_to_directness(legacy_belief['level']),
        justification_status=JustificationStatus.WELL_JUSTIFIED  # Assume for migration
    )

    return {
        'id': legacy_belief['id'],
        'content': content.dict(),
        'status': status.dict(),
        'provenance': provenance.dict(),
        '_legacy': legacy_belief,  # Preserve original for rollback
        '_migration_date': datetime.now().isoformat(),
        '_migration_version': '1.0.0'
    }

def migrate_all():
    """Run full migration."""
    web = load_web_state()
    migrated = []
    errors = []

    for belief in web['beliefs']:
        try:
            migrated.append(migrate_belief(belief))
        except Exception as e:
            errors.append({'belief_id': belief['id'], 'error': str(e)})

    # Write results
    save_migrated_web(migrated)
    save_migration_report(migrated, errors)
```

---

## 6. Dual-Format Adapter (BN_graphical Bridge)

Per coordination with Codex (CODEX_HANDOFF_EPISTEMIC_CALCULUS_2026-02-12.md), the BN_graphical bridge needs to support both formats during transition.

```python
# src/services/epistemic_adapter.py

class EpistemicAdapter:
    """Adapter for v1 ↔ v2 epistemic format conversion."""

    def to_v1(self, belief_v2: dict) -> dict:
        """Convert v2 belief to v1 format for legacy consumers."""
        rank = belief_v2['status']['rank']
        neg_rank = belief_v2['status']['neg_rank']

        # Convert ranks back to credence
        if neg_rank > rank:
            credence = 0.5 + (neg_rank - rank) / 10
        elif rank > neg_rank:
            credence = 0.5 - (rank - neg_rank) / 10
        else:
            credence = 0.5

        # Uncertainty from firmness
        firmness = abs(rank - neg_rank)
        uncertainty = max(0.1, 1.0 - firmness / 5)

        return {
            'id': belief_v2['id'],
            'content': belief_v2['content']['canonical_form'],
            'level': infer_level_from_grounding(belief_v2),
            'credence': {
                'value': min(0.95, max(0.05, credence)),
                'uncertainty': uncertainty
            }
        }

    def to_v2(self, belief_v1: dict) -> dict:
        """Convert v1 belief to v2 format."""
        return migrate_belief(belief_v1)

    def serialize(self, belief: dict, format: str = 'v2') -> dict:
        """Serialize belief in requested format."""
        if format == 'v1':
            if 'credence' in belief:
                return belief
            return self.to_v1(belief)
        else:
            if 'status' in belief:
                return belief
            return self.to_v2(belief)
```

---

## 7. Rollback Strategy

Migration preserves `_legacy` field for rollback:

```python
def rollback_belief(migrated_belief: dict) -> dict:
    """Restore belief to v1 format from migration backup."""
    if '_legacy' not in migrated_belief:
        raise ValueError("No legacy backup available")
    return migrated_belief['_legacy']

def rollback_all():
    """Full rollback to v1 format."""
    web = load_migrated_web()
    rolled_back = [rollback_belief(b) for b in web['beliefs']]
    save_web_state(rolled_back)
```

---

## 8. Testing Strategy

### Unit Tests
- `test_credence_to_ranks`: Property tests for conversion
- `test_level_to_warrant`: All level mappings
- `test_round_trip`: v1 → v2 → v1 preserves semantics

### Integration Tests
- `test_full_migration`: All 128 beliefs migrate without error
- `test_constraint_preservation`: Constraint graph survives migration
- `test_entrenchment_recalculation`: Entrenchment computable on v2 data

### Acceptance Tests
- Coherence scores similar before/after migration (within 10%)
- No beliefs change warrant status from WARRANTED to UNGROUNDED
- BN_graphical can consume both v1 and v2 payloads

---

## 9. Timeline

| Phase | Sprint | Deliverable |
|-------|--------|-------------|
| Schema Design | 1.1 | Four JSON schemas (COMPLETE) |
| Migration Script | 1.2 | `migrate_beliefs_to_v24.py` |
| Dual Adapter | 1.2 | `epistemic_adapter.py` |
| Integration Test | 1.2 | Full migration validated |
| BN Coordination | 4 | Bridge updated with dual support |

---

## 10. Open Questions for Panel

1. **Rank scaling**: Should max rank be bounded (e.g., 10) or unbounded?
2. **Uncertainty preservation**: Is converting uncertainty to firmness sufficient?
3. **Grounding chains**: Should migration attempt to infer grounding chains or leave empty?
4. **Defeat inference**: Should migration attempt to detect defeaters from existing tensions?

---

*Draft for Liskov panel review | ARCH-4 Sprint 1.1 | 2026-02-13*
