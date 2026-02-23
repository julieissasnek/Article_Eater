# Article Eater Web Health Diagnostic — 2026-02-20 12:07:59
Database: `ae.db`

---

```
ARTICLE EATER WEB HEALTH
==================================
Section 1  Database Integrity        [PASS]
Section 2  Node Quality              [PASS]  (garbage: 0, unresolved: 0)
Section 3  Graph Connectivity        [FAIL]  (No nodes/edges)
Section 4  Constraint Quality        [FAIL]  (default-credence: 0, template bridges: 0)
Section 5  Coherence                 [FAIL]  (global: 0.000)
Section 6  Template Coverage         [FAIL]  (ungrounded: 87/87)
Section 7  Domain Coverage           [FAIL]  (underpopulated: 10/10)
Section 8  Paper Integration         [PASS]  (zero-belief papers: 0)
Section 9  Extraction Precision      [FAIL]  (precision: 0.00)
Section 10 Old vs New                [SKIP]

OVERALL: [FAIL — 6 sections failing]
```

## Section 1: Database Structural Integrity

- **Expected tables present:** Yes
- **Orphan constraint references:** 0
- **coherence_history row count:** 0
- **web_snapshots row count:** 0
- **belief_merge_log row count:** 0
- **paper_publication row count:** 0
- **paper_integrations row count:** 0
- **bridges row count:** 0
- **beliefs row count:** 0
- **paper_quality row count:** 0
- **coherence_alerts row count:** 0
- **entrenchment_events row count:** 0
- **local_coherence_history row count:** 0
- **constraints row count:** 0
- **entrenchment_snapshots row count:** 0
- **web_metadata row count:** 0

---
## Section 2: Belief / Node Quality

### 2a. Basic counts
- Total belief nodes: 0
- Beliefs with mapped IV: 0
- Beliefs with mapped DV: 0
- Beliefs with BOTH: 0
- Beliefs with NEITHER: 0

### 2b. Garbage detection
- Nodes > 50 characters: 0
- Nodes with consecutive doubled chars: 0
- Nodes in env.unresolved.*: 0
- Nodes with stoplist terms: 0

### 2c. Vocabulary coverage
- Unique IV terms: 0
- Unique DV terms: 0
- Singleton ratio: 0.00%

---
## Section 3: Graph Connectivity


---
## Section 4: Constraint / Edge Quality

### 4a. Constraint layer breakdown
- Template bridges: 0
- Domain bridges: 0

### 4b. Edge weight distribution
- Mean credence: 0.000
- Default credence (0.5) count: 0
- Out of bounds credence: 0
- Isolated beliefs: 0

---
## Section 5: Coherence Metrics

- Global coherence score: 0

---
## Section 6: Template Coverage

- Total templates referenced: 0

---
## Section 7: Domain Coverage


---
## Section 8: Paper Integration Quality


---
## Section 9: Claim Extraction Precision

Requires human/LLM audit. Displaying script auto-checks only.