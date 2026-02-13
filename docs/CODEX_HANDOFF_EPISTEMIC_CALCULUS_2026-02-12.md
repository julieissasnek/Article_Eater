# Codex Handoff: Epistemic Calculus & Do-Calculus Coordination

**Date**: 2026-02-12
**From**: Claude Code (Article_Eater session)
**To**: Codex (working on both repos)
**Re**: Coordination on formal calculus work

---

## Summary

Claude Code has developed a plan for a **formal epistemic calculus** (ARCH-4) using Spohn's Ranking Theory + Pollock's Defeasible Logic. This will change how Article_Eater computes belief confidence, which affects what BN_graphical receives via the API.

You (Codex) are also looking at **do-calculus** (ARCH-1). This document coordinates our work.

---

## Part 1: What's Changing in Article_Eater

### Current State (what you've been integrating with)

```python
# Current: cardinal credence + computed entrenchment
belief.credence.value = 0.75  # Point estimate
belief.credence.uncertainty = 0.25  # Meta-uncertainty
entrenchment = 0.4 * connectivity + 0.3 * level_weight + 0.3 * coherence
```

### Future State (after ARCH-4)

```python
# Future: ordinal ranks + formal warrant
belief.status.rank = 2  # Spohn rank (degree of disbelief)
belief.status.neg_rank = 0  # Rank of negation
belief.status.warrant = WarrantStatus.WARRANTED  # Pollock warrant
belief.provenance.grounding = 0.8  # Haack grounding score
```

### API Changes (will affect BN_graphical)

| Endpoint | Current Response | Future Response |
|----------|------------------|-----------------|
| `/edge/{id}/justification` | `credence`, `uncertainty` | `rank`, `warrant_status`, `grounding` |
| `/web/state` | `entrenchment` field | `rank`, `neg_rank`, `warrant_status` |
| NEW: `/edge/{id}/confidence` | N/A | `confidence_interval`, `identifiable` |

**Timeline**: These changes are in ARCH-4, which is a 12-sprint plan. Not immediate, but you should know they're coming.

---

## Part 2: Implications for BN_graphical

### What Might Break

1. **EvidencePanel.tsx** — Currently displays `credence` and `uncertainty`. Will need to display `rank` and `warrant_status` instead.

2. **Edge opacity logic** — Currently based on `credence`. Should be based on `warrant_status` + `rank`.

3. **Color coding** — If you're using credence thresholds for colors, these will change.

### Recommended Approach

**Option A**: Wait for ARCH-4 to complete, then update BN_graphical

**Option B**: Make BN_graphical flexible now:
```typescript
// Instead of hardcoding credence display:
const displayConfidence = (belief: Belief) => {
  if ('rank' in belief.status) {
    // New format
    return formatRank(belief.status.rank, belief.status.warrant);
  } else {
    // Legacy format
    return formatCredence(belief.credence);
  }
};
```

### New UI Elements to Consider

| Concept | Display Suggestion |
|---------|-------------------|
| Rank (Spohn) | Lower = more believed. Show as "Belief strength: 3/5" |
| Warrant (Pollock) | Badge: "Warranted" / "Defeated" / "Suspended" |
| Grounding (Haack) | Progress bar: how connected to evidence |
| Defeaters | Expandable list showing what challenges this belief |

---

## Part 3: Do-Calculus Decision (ARCH-1)

You're looking at do-calculus. Here's the decision framework from our panel:

### The Options

| Option | Description | Effort | Recommendation |
|--------|-------------|--------|----------------|
| **A** | Full do-calculus (do-operator, truncated factorizations, identification) | HIGH | Overkill for current use case |
| **B** | Remove causal claims entirely | LOW | Too drastic |
| **C** | Clarify scope — call it "causal hypothesis tracking" not "causal inference" | LOW | Honest but limited |
| **D** | Partial do-calculus — simple cases only | MEDIUM | **Best balance** |

### My Recommendation: Option D

Implement do-calculus for **simple cases**:
1. No confounders (direct effect estimation)
2. Single mediator paths
3. Clear intervention semantics

Skip for now:
- Full identification algorithms (backdoor, frontdoor)
- Complex confounding adjustment
- Transportability (that's ARCH-2)

### What This Means for BN_graphical

If you implement Option D:

```typescript
// New query type
interface InterventionQuery {
  intervention: { variable: string; value: number };
  outcome: string;
  confidence: number;  // From epistemic layer
}

// API call
const effect = await api.post('/bn/intervene', {
  do: { variable: 'daylight', value: 'high' },
  outcome: 'mood'
});
// Returns: { effect: 0.3, ci: [0.1, 0.5], identifiable: true }
```

The epistemic layer (ARCH-4) tells you **how confident** to be in the BN structure.
The causal layer (ARCH-1/Option D) tells you **what happens** if you intervene.

---

## Part 4: Coordination Plan

### Division of Labor

| Component | Owner | Notes |
|-----------|-------|-------|
| Epistemic calculus (ARCH-4) | Claude Code / Article_Eater | Spohn + Pollock + Haack |
| Do-calculus (ARCH-1) | Codex | Pearl, Option D recommended |
| BN_graphical updates | Codex | After API changes stabilize |
| API contract | Both | Need to agree on schemas |

### Suggested Contract

When ARCH-4 is ready, the API will return:

```json
{
  "belief_id": "env.daylight→out.mood",
  "epistemic_status": {
    "rank": 2,
    "neg_rank": 5,
    "warrant": "warranted",
    "grounding": 0.8,
    "coherence": 0.7,
    "defeaters": []
  },
  "causal_status": {
    "identifiable": true,
    "effect_estimate": 0.3,
    "confidence_interval": [0.1, 0.5],
    "do_calculus_applicable": true
  }
}
```

### Potential Inconsistencies to Watch

1. **Credence vs Rank**: Don't mix them. Pick one representation in BN_graphical.

2. **Entrenchment vs Warrant**: Old code uses entrenchment (0-1 float). New code uses warrant (enum). Check all references.

3. **Edge justification logic**: If you've hardcoded thresholds like `if (credence > 0.7)`, these need updating.

4. **API version**: Consider versioning the API (`/api/v1/` vs `/api/v2/`) to support both during transition.

---

## Part 5: Questions for Codex

1. **Have you modified the edge justification display in BN_graphical?** If so, we need to coordinate the new format.

2. **Are you implementing any causal inference in BN_graphical?** If so, let's align on where do-calculus lives (frontend vs backend).

3. **What's your timeline?** ARCH-4 is 12 sprints. Should we sync at certain milestones?

---

## Part 6: Key Documents to Read

In Article_Eater repo:
- `docs/ARCH4_SPRINT_PLAN_2026-02-12.md` — Full 12-sprint plan
- `docs/PANEL_ARCH4_EPISTEMIC_CALCULUS_2026-02-12.md` — Panel consultation with Spohn/Pollock/etc.
- `docs/EPISTEMIC_CALCULUS_SPEC_2026-02-12.md` — Draft formal specification
- `TASKS.md` — All ARCH tasks including ARCH-1 options

---

## TL;DR

1. **Epistemic layer is getting formalized** — ranks replace credence, warrant replaces entrenchment
2. **Do-calculus**: Recommend Option D (partial implementation)
3. **BN_graphical will need updates** — but not until ARCH-4 Phase 5 (Bridge) is complete
4. **Watch for inconsistencies** — especially credence/rank and entrenchment/warrant mixing
5. **Let's coordinate** — especially on API contracts

---

*Handoff document for Codex | 2026-02-12*
