# Sprint 1.2-1.3: Enum Reconciliation Proposal
## Version 1.0 — February 15, 2026

---

## Executive Summary

This document proposes reconciliation of competing enum pairs identified in the Audit Synthesis (doc 08):

1. **Sprint 1.2**: ConstraintType (17 values) + EdgeType (19 values) → potential merge
2. **Sprint 1.3**: NodeDomain (5 values) + NodeTypeFamily (5 values) → **NO MERGE NEEDED**

**Finding**: NodeDomain and NodeTypeFamily are **orthogonal concepts** and should remain separate. The real consolidation needed is between the 3 different EdgeType enums.

---

## Sprint 1.3: NodeDomain + NodeTypeFamily — NO MERGE

### Why These Should NOT Be Merged

These serve fundamentally different purposes:

| Enum | Purpose | Dimension | Example |
|------|---------|-----------|---------|
| `NodeTypeFamily` | **What kind of node** (epistemic role) | Epistemological classification | "This is an EVIDENCE node" |
| `NodeDomain` | **What subject area** (content domain) | Content classification | "This is about ENVIRONMENTAL_PSYCHOLOGY" |

A node has BOTH properties:
- A finding about stress reduction in nature = `NodeTypeFamily.EVIDENCE` + `NodeDomain.ENVIRONMENTAL_PSYCHOLOGY`
- A coherence assessment = `NodeTypeFamily.META` + `NodeDomain.EPISTEMIC`

**Recommendation**: Keep both. They're orthogonal. No merge needed.

### Current Definitions

**NodeTypeFamily** (`src/epistemic/node_types.py:16`):
```python
class NodeTypeFamily(str, Enum):
    EVIDENCE = "evidence"          # Family A: carry data
    STRUCTURAL = "structural"      # Family B: organize the web
    INTERPRETIVE = "interpretive"  # Family C: carry expert judgment
    GAP = "gap"                    # Family D: mark what's missing
    META = "meta"                  # Family E: organize other nodes
```

**NodeDomain** (`src/services/web_of_belief.py:216`):
```python
class NodeDomain(str, Enum):
    BASIC_SCIENCE = "basic_science"
    ENVIRONMENTAL_PSYCHOLOGY = "environmental_psychology"
    METHODOLOGY = "methodology"
    CNFA = "cnfa"
    EPISTEMIC = "epistemic"  # Meta-level: beliefs about beliefs
```

---

## Sprint 1.2: ConstraintType + EdgeType — NEEDS OPUS REVIEW

### The Problem: 3 EdgeType Enums + 1 ConstraintType

| Location | Enum | Values | Purpose |
|----------|------|--------|---------|
| `src/epistemic/edge_types.py` | `EdgeType` | 19 | Web of belief semantic edges |
| `src/services/web_of_belief.py` | `ConstraintType` | 17 | Constraint relationships (coherence/support) |
| `src/services/incremental_bn.py` | `EdgeType` | 5 | Bayesian network causal edges |
| `src/services/network_service.py` | `EdgeType` | 4 | Graph visualization edges |

### Current Enum Values

#### EdgeType (edge_types.py) — 19 values
```
Review/Synthesis:     INCLUDES_IN_SYNTHESIS, SYNTHESIZES_AS, IDENTIFIES_MODERATOR, CONTRADICTS_SYNTHESIS
Theoretical:          THEORETICALLY_PREDICTS, CONFIRMS_PREDICTION, DISCONFIRMS_PREDICTION, PROPOSES_MECHANISM, SUBSUMES_THEORY, THEORY_TENSION
Conceptual:           DEFINES_CONSTRUCT, MUST_DISTINGUISH, REDEFINES, ORGANIZES
Critique:             CHALLENGES_METHOD, CHALLENGES_PARADIGM, PROPOSES_BETTER_METHOD
Attribution:          ATTRIBUTES_FINDING, INTERPRETS_AS
```

#### ConstraintType (web_of_belief.py) — 17 values
```
Basic:                SUPPORTS, CONTRADICTS, EXPLAINS, INSTANTIATES, ANALOGOUS, INDEPENDENT
Bridges:              BRIDGES, STRONG_TENSION, SHARED_EVIDENCE
Epistemic:            EPISTEMIC_DERIVATION, EPISTEMIC_CROSS_TEMPLATE, EPISTEMIC_MEDIATION
Coherence:            COHERENCE_SUPPORT, COHERENCE_TENSION
Argumentative:        ARGUMENTATIVE_SUPPORT, ARGUMENTATIVE_CHALLENGE
Generalizability:     GENERALIZABILITY_WARRANT
```

#### EdgeType (incremental_bn.py) — 5 values
```
CAUSAL, CORRELATIONAL, MECHANISM, MODERATION, UNKNOWN
```

#### EdgeType (network_service.py) — 4 values
```
POSITIVE, NEGATIVE, NEUTRAL, CAUSAL
```

### Proposed Reconciliation Options

**NEEDS OPUS REVIEW**: The following decision requires theoretical judgment:

#### Option A: Merge All Into One Canonical EdgeType

Create one master enum with ~40 values organized by category. All files import from canonical location.

**Pro**: Single source of truth
**Con**: Very large enum; mixes different semantic levels

#### Option B: Keep Separate Enums for Different Layers

| Enum | Location | Purpose |
|------|----------|---------|
| `EpistemicEdgeType` | `src/epistemic/edge_types.py` | Web of belief semantic relationships |
| `CausalEdgeType` | `src/services/incremental_bn.py` | Bayesian network causal structure |
| `GraphEdgeType` | `src/services/network_service.py` | Visualization rendering |

Add adapters to convert between them.

**Pro**: Clean separation of concerns
**Con**: More code, potential drift

#### Option C: Merge ConstraintType INTO EdgeType

Keep `edge_types.py:EdgeType` as canonical for web relationships.
Deprecate `web_of_belief.py:ConstraintType` — add its unique values to EdgeType.

**Mapping ConstraintType → EdgeType**:

| ConstraintType | Maps To | Notes |
|----------------|---------|-------|
| `SUPPORTS` | `CONFIRMS_PREDICTION` or new `SUPPORTS` | **NEEDS OPUS REVIEW**: Keep distinct or merge? |
| `CONTRADICTS` | `DISCONFIRMS_PREDICTION` or new `CONTRADICTS` | **NEEDS OPUS REVIEW** |
| `EXPLAINS` | `PROPOSES_MECHANISM` | Theoretical edge |
| `INSTANTIATES` | New `INSTANTIATES` | No current equivalent |
| `ANALOGOUS` | New `ANALOGOUS` | No current equivalent |
| `INDEPENDENT` | New `INDEPENDENT` | Meta-info, not really an edge |
| `BRIDGES` | New `BRIDGES` | Bridge warrant edge |
| `STRONG_TENSION` | `THEORY_TENSION` | Or keep distinct? |
| `SHARED_EVIDENCE` | New `SHARED_EVIDENCE` | No current equivalent |
| `EPISTEMIC_DERIVATION` | New `EPISTEMIC_DERIVATION` | Theory tier specific |
| `EPISTEMIC_CROSS_TEMPLATE` | New `EPISTEMIC_CROSS_TEMPLATE` | Theory tier specific |
| `EPISTEMIC_MEDIATION` | New `EPISTEMIC_MEDIATION` | Theory tier specific |
| `COHERENCE_SUPPORT` | `SUPPORTS` or keep distinct | **NEEDS OPUS REVIEW** |
| `COHERENCE_TENSION` | `CONTRADICTS` or keep distinct | **NEEDS OPUS REVIEW** |
| `ARGUMENTATIVE_SUPPORT` | `CONFIRMS_PREDICTION` or keep distinct | **NEEDS OPUS REVIEW** |
| `ARGUMENTATIVE_CHALLENGE` | `DISCONFIRMS_PREDICTION` or keep distinct | **NEEDS OPUS REVIEW** |
| `GENERALIZABILITY_WARRANT` | New `GENERALIZABILITY_WARRANT` | Type A→B (Sprint T2-4b) |

---

## Questions for Opus

**Q1: Should EPISTEMIC_DERIVATION and COHERENCE_SUPPORT be merged or kept distinct?**

Context:
- `EPISTEMIC_DERIVATION` = Tier 1 framework → Tier 2 template relationship
- `COHERENCE_SUPPORT` = A increases coherence of B

These seem semantically distinct. But both represent "positive epistemic support." Do they need separate edge types, or is one a subtype of the other?

**Q2: Should SUPPORTS/CONTRADICTS (general) be merged with CONFIRMS/DISCONFIRMS_PREDICTION (specific)?**

Context:
- `SUPPORTS`/`CONTRADICTS` = General coherence relationship
- `CONFIRMS_PREDICTION`/`DISCONFIRMS_PREDICTION` = Specifically about theory predictions

These overlap but aren't identical. A study can SUPPORT a claim without being a formal prediction test.

**Q3: Should we keep Bayesian network EdgeType separate or merge?**

Context:
- `incremental_bn.py:EdgeType` has CAUSAL, CORRELATIONAL, MECHANISM, MODERATION
- These are about causal structure, not epistemic relationships

Recommend keeping separate — different semantic layer.

---

## Deprecated Enums to Remove

| Enum | Location | Action |
|------|----------|--------|
| `ConstraintType` | `src/services/epistemic_causal_bridge.py:98` | REMOVE (marked DEPRECATED, REMOVE_BY V24.0) |

---

## Implementation Plan (After Opus Review)

1. **Create canonical `src/epistemic/edge_types.py` with merged values**
2. **Update imports across codebase**
3. **Add adapter functions for BN edge types** (keep separate, but with conversion)
4. **Remove deprecated `epistemic_causal_bridge.py:ConstraintType`**
5. **Add DB migration if edge_type column values change**
6. **Update tests**

---

## Files That Will Need Updates

| File | Current Enum | Action |
|------|--------------|--------|
| `src/epistemic/edge_types.py` | `EdgeType` | Expand with ConstraintType values |
| `src/services/web_of_belief.py` | `ConstraintType` | Deprecate, import from edge_types |
| `src/services/incremental_bn.py` | `EdgeType` | Rename to `CausalEdgeType` or add adapter |
| `src/services/network_service.py` | `EdgeType` | Rename to `GraphEdgeType` or add adapter |
| `src/services/epistemic_causal_bridge.py` | `ConstraintType` | Remove (already deprecated) |

---

## Decision Record

| Item | Decision | Date | By |
|------|----------|------|-----|
| NodeDomain + NodeTypeFamily | NO MERGE (orthogonal) | 2026-02-15 | CC |
| ConstraintType + EdgeType | MERGE (keep all values distinct) | 2026-02-15 | Opus |
| BN EdgeType | KEEP SEPARATE (different layer) | 2026-02-15 | Opus |
| Graph EdgeType | KEEP SEPARATE (visualization) | 2026-02-15 | CC |

---

## Opus Decisions (2026-02-15)

### Q1: EPISTEMIC_DERIVATION vs COHERENCE_SUPPORT

**KEEP DISTINCT.**

- `EPISTEMIC_DERIVATION` = inferential relation with specific provenance chain (CMR output). Directional, deductively tight.
- `COHERENCE_SUPPORT` = holistic Quinean relation (mutual fit). Symmetric/bidirectional, defeasible.

Merging would destroy the distinction between "the system derived this" and "these happen to fit together."

### Q2: SUPPORTS/CONTRADICTS vs CONFIRMS/DISCONFIRMS_PREDICTION

**KEEP DISTINCT.**

- `SUPPORTS`/`CONTRADICTS` = general evidential relations, extracted from papers, pre-CMR. No prediction ID.
- `CONFIRMS`/`DISCONFIRMS_PREDICTION` = relations to CMR-generated predictions. Carries prediction ID, template chain, degree-of-match.

Merging would collapse the empirical feedback loop that validates the CMR pipeline.

### Q3: BN edge types separate?

**CONFIRMED SEPARATE.**

BN edges = probabilistic/causal dependencies (variables). Web edges = epistemic relations (claims). Different semantic layers. Bridge adapter per Decision 5 handles translation.

---

*Document created: 2026-02-15*
*Author: Claude Code (Sprint 1.2-1.3)*
*Opus review: 2026-02-15*
*Status: IMPLEMENTING*
