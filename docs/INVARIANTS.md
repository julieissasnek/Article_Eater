# System Invariants

**Date**: January 22, 2026
**Version**: V21.0.0 (Post-Quinean)
**Purpose**: Document invariants and consistency model (per Lamport, ruthless review 2026-01-22)

---

## 1. Belief Invariants

### Identity Constraints
```
INV-B1: belief_id is unique across the web
        ∀ b1, b2 ∈ Web.beliefs: b1.belief_id = b2.belief_id → b1 = b2

INV-B2: belief_id format is "belief:<uuid>" or "belief:<source>:<identifier>"
        ∀ b ∈ Web.beliefs: b.belief_id.startswith("belief:")
```

### Credence Constraints
```
INV-B3: credence.value ∈ [0.0, 1.0]
        ∀ b ∈ Web.beliefs: 0.0 ≤ b.credence.value ≤ 1.0

INV-B4: credence.uncertainty ∈ [0.0, 1.0]
        ∀ b ∈ Web.beliefs: 0.0 ≤ b.credence.uncertainty ≤ 1.0

INV-B5: high uncertainty implies lower effective credence
        For practical purposes: effective_credence = credence.value × (1 - credence.uncertainty * 0.5)
```

### Source Depth Constraints
```
INV-B6: source_depth ∈ {FULL_TEXT, ABSTRACT, METADATA, null}
        ∀ b ∈ Web.beliefs: b.source_depth ∈ SourceDepth ∪ {null}

INV-B7: FULL_TEXT > ABSTRACT > METADATA (evidence quality ordering)
        When comparing evidence quality, FULL_TEXT is most authoritative
```

### Level Constraints
```
INV-B8: level ∈ {EMPIRICAL, THEORETICAL, META, METHODOLOGICAL}
        ∀ b ∈ Web.beliefs: b.level ∈ BeliefLevel

INV-B9: EMPIRICAL beliefs reference observations
        THEORETICAL beliefs reference explanatory frameworks
        META beliefs reference synthesis of multiple studies
        METHODOLOGICAL beliefs reference research design considerations
```

---

## 2. Web of Belief Invariants

### Structural Invariants
```
INV-W1: No circular dependencies in belief_dependencies
        The dependency graph must be a DAG
        ∀ b ∈ Web.beliefs: b ∉ transitive_closure(b.dependencies)

INV-W2: All paper_ids reference valid papers (when papers tracked)
        ∀ b ∈ Web.beliefs, ∀ pid ∈ b.paper_ids: pid ∈ Web.papers

INV-W3: All belief_dependencies reference existing beliefs
        ∀ b ∈ Web.beliefs, ∀ dep_id ∈ b.dependencies: dep_id ∈ Web.beliefs
```

### Contested Flag Invariants
```
INV-W4: contested flag implies either:
        (a) Explicit marking by system or user, OR
        (b) Directional opposition exists with high-credence evidence on both sides

INV-W5: directional opposition requires:
        ∃ b1, b2 ∈ Web.beliefs:
            same_topic(b1, b2) ∧
            opposite_direction(b1, b2) ∧
            b1.credence.value > 0.6 ∧
            b2.credence.value > 0.6
```

### Coherence Invariants
```
INV-W6: coherence_score ∈ [0.0, 1.0]
        ∀ snapshot: 0.0 ≤ snapshot.coherence_score ≤ 1.0

INV-W7: coherence_score monotonically increases during equilibrium-seeking
        If seek_equilibrium is enabled:
            coherence_score(t+1) ≥ coherence_score(t) - ε
            where ε is the convergence threshold (default: 0.001)

INV-W8: Credence updates must preserve transitivity (per Lamport, panel 2026-01-22)
        If A supports B and B supports C,
        then credence(A) change should propagate to C.

        Implementation note: When belief A's credence changes:
        1. Identify all beliefs B directly supported by A (SUPPORTS constraint)
        2. For each B, identify beliefs C directly supported by B
        3. Propagate credence impact: ΔC = ΔA × strength(A→B) × strength(B→C) × 0.5
        4. Propagation stops when ΔX < 0.01 (threshold)

        This ensures the web maintains coherence across transitive relationships.
```

---

## 3. Causal Classification Invariants

### Tier Invariants
```
INV-C1: tier ∈ {CAUSAL, SUGGESTIVE, ASSOCIATIONAL}
        ∀ classification: classification.tier ∈ CausalTier

INV-C2: confidence ∈ [0.0, 1.0]
        ∀ classification: 0.0 ≤ classification.confidence ≤ 1.0

INV-C3: confidence ≤ 0.95 (never certainty)
        ∀ classification: classification.confidence ≤ 0.95
```

### Design-First Invariants (Pearl)
```
INV-C4: experimental design → tier ≥ SUGGESTIVE
        If is_experimental = true, tier ∈ {CAUSAL, SUGGESTIVE}

INV-C5: quasi-experimental + causal_language → CAUSAL
        If is_quasi_experimental ∧ causal_count > 0, tier = CAUSAL

INV-C6: causal_language without (mechanism ∨ confounder) → SUGGESTIVE
        If causal_count > 0 ∧ ¬has_mechanism ∧ ¬has_confounder_control, tier = SUGGESTIVE
```

---

## 4. Bridge Warrant Invariants

### Identity Constraints
```
INV-BR1: bridge_id is unique
         ∀ b1, b2 ∈ Registry.bridges: b1.bridge_id = b2.bridge_id → b1 = b2

INV-BR2: bridge_id format is "bridge:<source>_<target>_<uuid>"
         ∀ b ∈ Registry.bridges: b.bridge_id.startswith("bridge:")
```

### Type Constraints
```
INV-BR3: bridge_type ∈ {MECHANISM, FUNCTIONAL, ANALOGICAL, CONSTITUTIVE, CAPACITY, EMPIRICAL_COVARIANCE}
         ∀ b ∈ Registry.bridges: b.bridge_type ∈ BridgeType
```

### Confidence Constraints
```
INV-BR4: confidence ∈ [0.05, 0.95]
         ∀ b ∈ Registry.bridges: 0.05 ≤ b.confidence ≤ 0.95
         (Never zero, never certain)

INV-BR5: default confidences are type-dependent
         CONSTITUTIVE: 0.75, MECHANISM: 0.60, CAPACITY: 0.45,
         FUNCTIONAL: 0.50, ANALOGICAL: 0.35, EMPIRICAL_COVARIANCE: 0.60

         Note: CAPACITY reduced from 0.55 to 0.45 per Cartwright (panel 2026-01-22)
         because capacity claims are often unfalsifiable assertions.
```

### Status Invariants
```
INV-BR6: status ∈ {HYPOTHESIZED, SUPPORTED, CONTESTED, FAILED, REVISED}
         ∀ b ∈ Registry.bridges: b.status ∈ BridgeStatus

INV-BR7: FAILED status requires:
         (evidence_against.length > 0) ∧ (confidence < 0.2)

INV-BR8: CONTESTED status requires:
         (evidence_for.length > 0) ∧ (evidence_against.length > 0)
```

---

## 5. Query Response Invariants

### Structure Invariants
```
INV-Q1: exactly three follow-ups per response
        ∀ response: len(response.follow_ups) = 3

INV-Q2: follow-up types are (deeper, scope, uncertainty)
        ∀ response:
            response.follow_ups[0].type = "deeper"
            response.follow_ups[1].type = "scope"
            response.follow_ups[2].type = "uncertainty"

INV-Q3: evidence items limited to 10
        ∀ response: len(response.evidence_items) ≤ 10
```

### Confidence Level Invariants
```
INV-Q4: confidence_level ∈ {HIGH, MEDIUM, LOW, UNKNOWN}
        ∀ response: response.confidence_level ∈ {"high", "medium", "low", "unknown"}

INV-Q5: confidence thresholds:
        HIGH: ≥1 belief with credence ≥ 0.7 and full-text source
        MEDIUM: ≥1 belief with credence ≥ 0.5
        LOW: ≥1 relevant belief
        UNKNOWN: no relevant beliefs
```

---

## 6. Reporting Invariants

### Gap Analysis Invariants
```
INV-R1: missing_outcomes ⊆ expected_outcomes
        ∀ gap_report: gap_report.missing_outcomes ⊆ taxonomy.get_expected_outcomes()

INV-R2: confounder gap severity ∈ {CRITICAL, WARNING, INFO}
        ∀ gap: gap.severity ∈ {"CRITICAL", "WARNING", "INFO"}

INV-R3: CRITICAL = abstract-only causal without confounder
        WARNING = full-text causal without confounder
        INFO = associational or has confounder mention
```

---

## 7. Consistency Model

### Read-Write Behavior
```
CONSISTENCY-1: Queries operate on snapshot of web state
               During query execution, web state does not change.
               Panel validation (2026-01-22 - Lamport): Clarified as follows:
               - Snapshot is taken at query start via web.snapshot()
               - The snapshot is an explicit deep copy (not implicit)
               - If web changes during query, snapshot remains consistent
               - Route handlers SHOULD call snapshot() before query operations

CONSISTENCY-2: Mutations are atomic at belief level
               Individual belief updates are atomic; no partial updates

CONSISTENCY-3: No read-write locking currently implemented
               Concurrent reads are safe; concurrent writes may conflict
```

### Snapshot Isolation (Per Lamport, panel validation 2026-01-22)
```
SNAPSHOT-1: When is snapshot taken?
            At query start, when web.snapshot() is called.
            This returns WebOfBeliefSnapshot, an immutable copy.

SNAPSHOT-2: What happens if web changes during query?
            Query continues with the snapshot state.
            Snapshot is NOT affected by concurrent writes.
            This provides snapshot isolation semantics.

SNAPSHOT-3: Is snapshot explicit or implicit?
            EXPLICIT: snapshot() returns a deep copy.
            Route handlers should use:
                web_snapshot = get_web().snapshot()
                # All operations use web_snapshot
```

### Recommended Practices
```
PRACTICE-1: Use snapshot() for query operations
            Route handlers should call web.snapshot() and use
            the returned snapshot for all read operations.

PRACTICE-2: Validate before write
            Check invariants before committing mutations

PRACTICE-3: Use equilibrium-seeking for batch updates
            After multiple belief additions, run seek_equilibrium()
```

### Transaction Boundaries
```
TRANSACTION-1: Pipeline extraction is atomic
               All beliefs from a single paper are added together

TRANSACTION-2: Bridge evaluation is atomic
               Evidence update and status change happen together

TRANSACTION-3: Report generation is read-only
               Reports do not mutate web state
```

---

## 8. Invariant Verification

### Runtime Checks (Enabled)
The following invariants are checked at runtime:
- INV-B3, INV-B4: Credence bounds (in `Credence.__post_init__`)
- INV-BR4: Bridge confidence bounds (in `BridgeWarrant.__post_init__`)
- INV-BR2: Bridge ID format (in `BridgeWarrant.__post_init__`)

### Design-Time Checks (Test Suite)
The following invariants are verified in tests:
- INV-B1: Belief ID uniqueness (test_web_of_belief)
- INV-C1, INV-C2: Classification bounds (test_causal_classifier)
- INV-Q1, INV-Q2: Follow-up structure (test_query_response)

### Not Currently Verified
The following invariants should be verified but are not yet:
- INV-W1: DAG structure (circular dependency detection)
- INV-W2: Paper reference validity (when papers tracked)
- CONSISTENCY-1: Snapshot isolation

---

## 9. Future Work

### Lamport's Recommendations (ruthless review 2026-01-22)
1. Add explicit consistency model documentation
2. Consider copy-on-read for query operations
3. Add semantic constraints to JSON schemas
4. Document transaction boundaries more formally

### Proposed Additions
- Add `validate_invariants()` method to WebOfBelief
- Add property-based testing for invariants
- Add pre/post-condition assertions to critical methods
