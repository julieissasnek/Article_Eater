# CVA-2-REV: Valuation Axes Specification

**Sprint CVA-2-REV — Phase A: Foundation**
**Reference**: CVA Sprint Plan §CVA-2, Revised Specs §Three Hard Problems

---

## Valuation Space

```
v(ψ) = V(c; g(ψ), τ(ψ), κ(ψ_culture, ψ_neuro))
```

The valuation space maps constraint vectors to subjective preference scores. It is **culture-dependent** — the same constraint vector produces structurally different valuations under different cultural decompositions.

---

## Universal Axes (9)

| Axis | Symbol | SDT Category | Definition |
|------|--------|:------------:|-----------|
| Safety | SafetyValue | Basic Need | Perceived freedom from environmental threat |
| Interest | InterestValue | Intrinsic | Novelty, curiosity, desire to explore |
| Restoration | RestorationValue | Basic Need | Recovery from directed attention fatigue |
| Status | StatusValue | Social | Social standing signaled by environment |
| Belonging | BelongingValue | Social | Sense of membership and acceptance |
| Identity Congruence | IdentityCongruenceValue | Self | Fit between self-concept and place |
| Autonomy Support | AutonomySupportValue | SDT | Environment supports volitional action |
| Competence Support | CompetenceSupportValue | SDT | Environment supports mastery and skill |
| Relatedness Support | RelatednessSupportValue | SDT | Environment supports social connection |

---

## Cultural Variants (4 Structurally Distinct Decompositions)

### Western (9D — all orthogonal)
Standard 9-axis decomposition. All axes independent.
SDT axes (Autonomy, Competence, Relatedness) are core/auxiliary split.

### Japanese (7D — 間 subsumption)
Safety and Restoration merge into **間 (Ma)** — the aesthetic-spatial concept of meaningful emptiness.
Additional axis: **甘え (Amae)** — indulgent dependence.
Total: 7 independent dimensions.

### West African / Yoruba (8D — Àṣà embedding)
Identity axis splits into **Àṣà** — community identity as collective achievement.
Status becomes **community role** rather than individual prestige.
Total: 8 dimensions.

### Indian (10D — Rasa + Dharma additions)
Standard 9 + **Rasa** (aesthetic-emotional wholeness) + **Dharma** (duty-congruence).
Beauty readout uses Rasa activation model (9 rasa categories).
Total: 10 dimensions with 2 culture-specific additions.

---

## Implementation Files

| File | LOC | Content |
|------|:---:|---------|
| `src/models/cva_valuation.py` | 339 | `CVAValuationVector`, `CulturalVariant`, `NeurotypeValuationModifier` |
| `src/services/cva_valuation_engine.py` | 439 | `CVAValuationEngine` with cultural mapping |
| `src/services/cva_beauty.py` | 245 | 4 beauty readout models |
| `src/services/cva/cva_beauty_evaluation.py` | 350 | Evaluation framework |

---

## Neurotype Valuation Modifiers

| Neurotype | Gain Adjustments | Bias |
|-----------|-----------------|------|
| PTSD | Safety ×1.5, Interest ×0.5 | Safety +0.15 |
| ASD | Belonging ×0.7, Autonomy ×1.3 | — |
| ADHD | Interest ×1.3, Restoration ×0.7 | — |
| Depression | Interest ×0.5, Belonging ×0.7 | Status -0.10 |
| Anxiety | Safety ×1.5, Autonomy ×0.7 | — |

Implementation: `NeurotypeValuationModifier` in `cva_valuation.py`
