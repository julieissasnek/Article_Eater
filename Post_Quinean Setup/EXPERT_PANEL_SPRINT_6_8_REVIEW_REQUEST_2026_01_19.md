# Expert Panel Review Request: Sprints 6-8 Implementation Decisions

**Date**: Sunday, January 19, 2026
**Purpose**: Post-implementation review of key design decisions
**Status**: AWAITING PANEL REVIEW

---

## Overview

Sprints 6-8 of the Article Eater Post-Quinean system have been implemented. Before proceeding to Sprint 9 (Gold Standard Corpus), we request expert panel review of the key design decisions made during implementation. These decisions affect how the system handles causal inference, scope conditions, terminology resolution, and validation.

---

## Sprint 6: Causal Structure & Scope Conditions

### Decision 6.1: CausalDirection Enum Values

**What was implemented:**
```python
class CausalDirection(Enum):
    UNKNOWN = "unknown"              # Default for theoretical claims
    CORRELATIONAL = "correlational"  # Default for empirical findings
    FORWARD = "forward"              # source → target (experimental)
    REVERSE = "reverse"              # target → source
    BIDIRECTIONAL = "bidirectional"  # mutual causation
    COMMON_CAUSE = "common_cause"    # C → A, C → B (confound)
    MEDIATED = "mediated"            # A → M → B (indirect)
```

**Questions for the panel:**
1. Is the distinction between CORRELATIONAL and UNKNOWN valuable, or does it create false precision?
2. Should MEDIATED require specification of the mediator M, or is the category alone sufficient?
3. Are there causal structures we're missing that are common in CNFA literature (e.g., moderation)?

---

### Decision 6.2: ScopeConditions Dimensions

**What was implemented:**
```python
@dataclass
class ScopeConditions:
    population: Optional[str] = None      # "adults", "children", "clinical"
    setting: Optional[str] = None         # "lab", "field", "simulated", "vr"
    duration: Optional[str] = None        # "acute", "chronic"
    measurement: Optional[str] = None     # "self_report", "physiological"
    geography: Optional[str] = None       # "urban", "rural", "Western"
    moderators: List[str] = field(default_factory=list)
```

**Questions for the panel:**
1. Are these the right 5 dimensions for characterizing scope in CNFA research?
2. Should "age_range" be explicit rather than part of population (e.g., "adults 18-65")?
3. Is there value in a "sample_type" dimension (students vs. community vs. clinical)?

---

### Decision 6.3: Scope Overlap Logic

**What was implemented:**
- Any dimension mismatch = no overlap (per Cartwright's emphasis on scope conditions)
- NULL = universal scope (overlaps with everything)

**Example:**
- Scope1: {population: "adults", setting: "lab"}
- Scope2: {population: "adults", setting: "field"}
- Result: NO OVERLAP (settings differ)

**Questions for the panel:**
1. Is this too strict? Should "lab" and "field" partially overlap?
2. Should we implement hierarchical compatibility (e.g., "lab" ⊂ "controlled")?
3. How do we handle scope imprecision in older papers that don't specify conditions?

---

### Decision 6.4: PRECISION_BOUNDARY Thresholds

**What was implemented:**
- Same effect direction (both increase or both decrease)
- Credence difference between 0.1 and 0.3
- Classified as PRECISION_BOUNDARY (not a true conflict)

**Questions for the panel:**
1. Are these thresholds (0.1-0.3) appropriate?
2. Should precision boundaries also require similar scope conditions?
3. Is this distinction valuable for human reviewers, or does it create confusion?

---

## Sprint 7: Environment Taxonomy & Construct Identity

### Decision 7.1: Environment Hierarchy Categories

**What was implemented:**
```
spatial: volume, openness, enclosure, prospect, refuge
natural: vegetation, water, daylight, views, sounds
sensory: lighting, darkness, acoustics, thermal, air, odor
configurational: wayfinding, complexity, connectivity, density, privacy
aesthetic: complexity, simplicity, color, materials, order, biomorphic
```

**Questions for the panel:**
1. Is this taxonomy comprehensive for CNFA research?
2. Are there major environmental features we're missing?
3. Should "social" be a category (presence of others, crowding perception)?

---

### Decision 7.2: Antonym Pairs and Equivalence Rule

**What was implemented:**
- Antonym pairs: openness↔enclosure, prospect↔refuge, lighting↔darkness, complexity↔simplicity, density↔spaciousness, privacy↔exposure, order↔disorder
- Rule: "X increases Y" ≡ "antonym(X) decreases Y" (NOT a conflict)

**Example:**
- "Openness increases wellbeing" ≡ "Enclosure decreases wellbeing"
- These are treated as the SAME finding, not a contradiction

**Questions for the panel:**
1. Is this equivalence rule sound? Are there cases where it fails?
2. Should equivalence require matching scope conditions?
3. Are there antonym pairs that are NOT semantically equivalent in this way?

---

### Decision 7.3: Diversity Index Formula

**What was implemented:**
```python
diversity_index = 0.6 * environment_entropy + 0.4 * outcome_entropy
```

**Questions for the panel:**
1. Is this weighting (0.6/0.4) appropriate?
2. Should theory diversity also be included?
3. Is Shannon entropy the right measure, or should we use Simpson's index?

---

## Sprint 8: Multi-Theory & Validation Infrastructure

### Decision 8.1: Evidence Cluster Handling

**What was implemented:**
- Beliefs from same study share an `evidence_cluster_id`
- Same-cluster beliefs don't boost credence (prevents double-counting)
- Different-cluster beliefs use normal inverse-variance merge

**Questions for the panel:**
1. Is this the right approach to avoid double-counting?
2. Should same-cluster beliefs create SHARED_EVIDENCE constraints?
3. How do we handle meta-analyses that aggregate multiple studies?

---

### Decision 8.2: Validation Phase Gates

**What was implemented:**
| Phase | Min Papers | Min Connectivity | Min LCC |
|-------|-----------|-----------------|---------|
| Phase 1: Annotation | 10 | 0.0 | 0.0 |
| Phase 2: Calibration | 20 | 1.5 | 0.5 |
| Phase 3: LOO | 30 | 2.0 | 0.7 |
| Phase 4: Bridges | 50 | 2.5 | 0.8 |

**Questions for the panel:**
1. Are these thresholds appropriate for CNFA literature?
2. Should theory-specific coverage be a gate criterion?
3. Is LCC (largest connected component) the right connectivity metric?

---

### Decision 8.3: Ecological Validity Weights

**What was implemented:**
| Method | Weight |
|--------|--------|
| Field (natural behavior) | 1.0 |
| Field (structured task) | 0.95 |
| Lab (VR) | 0.85 |
| Lab (video) | 0.75 |
| Lab (photos) | 0.65 |
| Lab (abstract) | 0.50 |

**Questions for the panel:**
1. Is the VR > video > photos ordering empirically supported?
2. Should these weights apply to credence directly, or to uncertainty?
3. Is 0.50 for abstract studies too harsh?

---

### Decision 8.4: Pass Thresholds by Epistemic Level

**What was implemented:**
| Level | F1 Threshold | Credence-in-Range |
|-------|-------------|-------------------|
| Empirical | 0.75 | 0.75 |
| Intermediate | 0.65 | 0.70 |
| Theoretical | 0.55 | 0.65 |
| Overall | 0.70 | 0.70 |

**Questions for the panel:**
1. Are these F1 thresholds realistic for automated extraction?
2. Should theoretical claims have lower thresholds (harder to validate)?
3. What happens if empirical beliefs pass but theoretical fail?

---

## Request for Panel

Please convene the expert panel (Pearl, Cartwright, Simon, Bates, Kaplan) to review these decisions. For each decision:

1. **Validate** - Is the approach sound?
2. **Critique** - What could go wrong?
3. **Improve** - What changes would you recommend?
4. **Prioritize** - Which issues need immediate attention vs. can wait?

The implementation can be adjusted based on panel feedback before proceeding to Sprint 9.

---

## Files to Review

The panel should have access to these files for context:

1. **Sprint 6**: `src/services/web_of_belief.py` (lines 82-155)
2. **Sprint 7**: `src/services/environment_taxonomy.py` (complete file)
3. **Sprint 8**: `src/services/validation.py` (complete file)
4. **Sprint 8**: `src/services/web_persistence.py` (lines 1465-1565)

---

*Awaiting expert panel review before finalizing Sprints 6-8 and proceeding to Sprint 9.*
