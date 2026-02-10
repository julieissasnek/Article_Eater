# Archived Features: Epistemic-Causal Bridge

**Date**: 2026-02-10
**Sprint**: ECB (Epistemic-Causal Bridge Repair)
**Panel**: P-ECB-R (Haack, Pearl, van Fraassen, Simon, Cartwright, Parnas, Brooks)

---

## Why These Were Archived

Per Panel P-ECB-R recommendation: Simplify the bridge to ~500 lines before adding features. These modules are valuable but premature—they add complexity without the core integration being stable.

**Simon**: "Cut 80% of the file. A working 200-line bridge is better than a non-working 2400-line bridge."

---

## Archived Files

| File | Original Lines | Purpose |
|------|----------------|---------|
| `individual_differences.py` | 352-406 | Personalized inference based on traits |
| `cultural_meaning.py` | 231-238 | Cross-cultural construct meaning |
| `argument_attack.py` | 83-92, 413-465 | Scientific disagreement as contrast shifts |
| `generalization_elaborate.py` | 811-850 | Full transfer assessment |
| `demo_and_stub_web.py` | 2000-2330 | Demo functions, stub WebOfBelief (Sprint ECB-2) |

---

## Reintegration Roadmap

### Phase 1: After Core Bridge Stable
- **Individual Differences** (IND-1 to IND-4)
  - Needs: Literature review of moderator effect sizes
  - Enables: Personalized recommendations

### Phase 2: After Contrast Transfer Working
- **Cultural Meanings** (CULT-1 to CULT-5)
  - Needs: Anthropology/cultural psychology input
  - Enables: Cross-cultural validity checking

- **Argument Attack Analysis** (ATK-1 to ATK-4)
  - Needs: NLP attack detection in extraction
  - Enables: Distinguishing true contradictions from contrast shifts

### Phase 3: After Simple Scope Validated
- **Elaborate Generalization** (GEN-1 to GEN-4)
  - Needs: All above features
  - Enables: Full "will it work for me?" assessment

---

## How to Reintegrate

1. **Check dependencies** — Each file header lists what's needed
2. **Import from web_of_belief.py** — Don't recreate classes
3. **Add tests first** — Before adding to bridge
4. **Update CLAUDE.md** — Document the capability
5. **Panel review** — For significant additions

---

## Full Documentation

See: `docs/ARCHIVED_FEATURES_EPISTEMIC_CAUSAL_BRIDGE_2026-02-10.md`

---

*These are not deleted—they're waiting for the right time.*
