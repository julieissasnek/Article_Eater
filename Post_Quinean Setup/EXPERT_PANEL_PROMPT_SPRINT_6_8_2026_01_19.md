# Expert Panel Prompt: Sprint 6-8 Implementation Review

**Date**: Sunday, January 19, 2026
**Purpose**: Convene expert panel to review implementation decisions

---

## PROMPT FOR EXPERT PANEL

You are convening five experts to review implementation decisions for the Article Eater Post-Quinean system. Each expert should speak from their area of expertise and engage with each other's perspectives.

**The Panel:**
- **Dr. Judea Pearl** (UCLA) — Bayesian networks, causal inference, do-calculus
- **Dr. Nancy Cartwright** (Durham/LSE) — Philosophy of science, capacities, patchwork laws
- **Dr. Herbert Simon** (historical voice) — Bounded rationality, satisficing, system design
- **Dr. Marcia Bates** (UCLA) — Information science, knowledge organization, faceted classification
- **Dr. Rachel Kaplan** (Michigan) — Environmental psychology, ART, the CNFA domain itself

---

## CONTEXT

The Article Eater system extracts evidence from scientific papers about Cognitive Neuroarchitecture for Affect (CNFA) — how built and natural environments affect psychological states. The system uses Quinean coherentist epistemology: no foundational beliefs, justification through coherence, everything revisable.

**Sprints 6-8 have been implemented** and contain the following key decisions that need expert review:

---

## SPRINT 6 DECISIONS

### 6.1: Causal Direction Categories

We implemented a `CausalDirection` enum with 7 values:
- UNKNOWN (default for theory)
- CORRELATIONAL (default for empirical)
- FORWARD (A→B experimental)
- REVERSE (B→A)
- BIDIRECTIONAL (mutual)
- COMMON_CAUSE (confound C→A, C→B)
- MEDIATED (A→M→B indirect)

**Questions:**
1. Pearl: Is this taxonomy complete? Does it handle the distinctions that matter for causal inference?
2. Pearl: Should MEDIATED require naming M, or is categorical sufficient?
3. All: What's missing that's common in environmental psychology?

### 6.2: Scope Conditions

We track 5 dimensions for each belief: population, setting, duration, measurement, geography.

Per Cartwright's view, we treat scope strictly: ANY dimension mismatch = no overlap.

**Questions:**
1. Cartwright: Is this too strict? Should scopes partially overlap?
2. Cartwright: How should we handle papers that don't report scope conditions?
3. Kaplan: Are these the right dimensions for CNFA research?

### 6.3: Precision Boundary Detection

We classify as PRECISION_BOUNDARY (not true conflict) when:
- Same effect direction (both positive or both negative)
- Credence difference between 0.1 and 0.3

**Questions:**
1. Simon: Are these thresholds appropriate heuristics?
2. Cartwright: Does this distinction hold up philosophically?

---

## SPRINT 7 DECISIONS

### 7.1: Environment Taxonomy Categories

We created 5 main categories:
- **spatial**: volume, openness, enclosure, prospect, refuge
- **natural**: vegetation, water, daylight, views, sounds
- **sensory**: lighting, darkness, acoustics, thermal, air
- **configurational**: wayfinding, complexity, connectivity, density
- **aesthetic**: complexity, simplicity, color, materials, order

**Questions:**
1. Bates: Is this a sound faceted classification?
2. Kaplan: Does this capture what CNFA researchers care about?
3. All: What's missing?

### 7.2: Antonym Equivalence Rule

We treat antonym environment pairs as semantically equivalent when effects are reversed:
- "Openness increases wellbeing" ≡ "Enclosure decreases wellbeing"
- Treated as SAME finding, not contradiction

**Questions:**
1. Bates: Is this semantic equivalence valid? When does it fail?
2. Kaplan: Are there pairs in CNFA where this would be misleading?
3. Cartwright: Does this fit your framework of capacities?

### 7.3: Diversity Index

Formula: `0.6 * env_entropy + 0.4 * outcome_entropy`

**Questions:**
1. Bates: Is this weighting appropriate?
2. Simon: Is Shannon entropy the right measure?
3. All: Should theory diversity be included?

---

## SPRINT 8 DECISIONS

### 8.1: Evidence Cluster Handling

Papers testing multiple theories create "evidence clusters" — beliefs from same study share a cluster ID. Same-cluster beliefs don't boost credence (prevents double-counting).

**Questions:**
1. Pearl: Is this the right solution to avoid inflated confidence?
2. Simon: Should clusters create explicit SHARED_EVIDENCE constraints?
3. All: How should we handle meta-analyses?

### 8.2: Validation Phase Gates

| Phase | Min Papers | Min Connectivity | Min LCC |
|-------|-----------|-----------------|---------|
| Annotation | 10 | 0.0 | 0.0 |
| Calibration | 20 | 1.5 | 0.5 |
| LOO | 30 | 2.0 | 0.7 |
| Bridge Validation | 50 | 2.5 | 0.8 |

**Questions:**
1. Simon: Are these thresholds appropriate?
2. Pearl: Is LCC the right connectivity metric?
3. All: Should theory coverage be gated?

### 8.3: Ecological Validity Weights

| Method | Weight |
|--------|--------|
| Field (natural) | 1.0 |
| Field (structured) | 0.95 |
| Lab (VR) | 0.85 |
| Lab (video) | 0.75 |
| Lab (photos) | 0.65 |
| Lab (abstract) | 0.50 |

**Questions:**
1. Kaplan: Is VR > video > photos empirically supported in CNFA?
2. Simon: Should these weights affect credence or uncertainty?
3. All: Is 0.50 for abstract studies too harsh?

### 8.4: Pass Thresholds by Epistemic Level

| Level | F1 | Credence-in-Range |
|-------|-----|-------------------|
| Empirical | 0.75 | 0.75 |
| Intermediate | 0.65 | 0.70 |
| Theoretical | 0.55 | 0.65 |
| Overall | 0.70 | 0.70 |

**Questions:**
1. Simon: Are these realistic for automated extraction?
2. All: Should theoretical claims have LOWER thresholds (harder to validate)?

---

## PANEL INSTRUCTIONS

For each decision area:

1. **Speak from your expertise** — Pearl on causation, Cartwright on scope, Bates on taxonomy, Kaplan on domain, Simon on system design
2. **Engage with each other** — Agree, disagree, build on
3. **Be specific** — If something is wrong, say what to change
4. **Prioritize** — Which issues need immediate fixes vs. can wait?

After individual responses, please provide a **JOINT SUMMARY** with:
- Changes that should be made NOW before Sprint 9
- Changes that can wait for a later revision
- Issues that need empirical validation (we can't decide from first principles)

---

*The implementation code is in:*
- `src/services/web_of_belief.py` (Sprint 6 additions)
- `src/services/environment_taxonomy.py` (Sprint 7)
- `src/services/validation.py` (Sprint 8)
- `src/services/web_persistence.py` (Sprint 6-8 persistence)

*Please review and provide feedback.*
