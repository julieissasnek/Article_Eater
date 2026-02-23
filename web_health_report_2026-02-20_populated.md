# Article Eater Web Health Diagnostic — 2026-02-20 12:12:33
Database: `./data/web_persistence_v2.db`

---

```
ARTICLE EATER WEB HEALTH
==================================
Section 1  Database Integrity        [PASS]
Section 2  Node Quality              [FAIL]  (garbage: 47, unresolved: 0)
Section 3  Graph Connectivity        [PASS]  (components: 1)
Section 4  Constraint Quality        [FAIL]  (default-credence: 0, template bridges: 0)
Section 5  Coherence                 [FAIL]  (global: 0.335)
Section 6  Template Coverage         [FAIL]  (ungrounded: 87/87)
Section 7  Domain Coverage           [FAIL]  (underpopulated: 9/10)
Section 8  Paper Integration         [FAIL]  (zero-belief papers: 0)
Section 9  Extraction Precision      [FAIL]  (precision: 0.00, self-ref: 0, null-dir: 208)
Section 10 Old vs New                [SKIP]

OVERALL: [FAIL — 7 sections failing]
```

## Section 1: Database Structural Integrity

- **Expected tables present:** Yes
- **Orphan constraint references:** 0
- **entrenchment_snapshots row count:** 0
- **coherence_history row count:** 1
- **paper_integrations row count:** 0
- **bridges row count:** 0
- **constraints row count:** 12206
- **paper_publication row count:** 0
- **paper_quality row count:** 0
- **entrenchment_events row count:** 0
- **web_snapshots row count:** 0
- **web_metadata row count:** 1
- **belief_merge_log row count:** 0
- **local_coherence_history row count:** 0
- **beliefs row count:** 382
- **coherence_alerts row count:** 0

---
## Section 2: Belief / Node Quality

### 2a. Basic counts
- Total belief nodes: 382
- Beliefs with mapped IV: 382
- Beliefs with mapped DV: 382
- Beliefs with BOTH: 382
- Beliefs with NEITHER: 0

### 2b. Garbage detection
- Nodes > 50 characters: 47
- Nodes with consecutive doubled chars: 0
- Nodes in env.unresolved.*: 0
- Nodes with stoplist terms: 0

### 2c. Vocabulary coverage
- Unique IV terms: 32
- Unique DV terms: 31
- Singleton ratio: 9.52%

---
## Section 3: Graph Connectivity

- Number of connected components: 1
- Size of largest component: 382 (100.0%)

---
## Section 4: Constraint / Edge Quality

### 4a. Constraint layer breakdown
- supports: 994
- bridges: 11212
- Template bridges: 0
- Domain bridges: 0

### 4b. Edge weight distribution
- Mean credence: 0.420
- Default credence (0.5) count: 0
- Out of bounds credence: 0
- Isolated beliefs: 0

---
## Section 5: Coherence Metrics

- Global coherence score: 0.3353542110438165

---
## Section 6: Template Coverage

- Total templates referenced: 0

---
## Section 7: Domain Coverage


---
## Section 8: Paper Integration Quality

- Total papers in paper_integrations: 0
- Papers contributing 0 beliefs: 0
- Average beliefs per paper: 0.0

---
## Section 9: Claim Extraction Precision

### 9a. Automated checks
- Total parsed claims: 382
- Claims where IV == DV: 0
- Claims with null/unknown direction: 208
- Duplicate IV+DV+paper combinations: 0

### 9b. Sample audit
Requires human/LLM audit. Displaying script auto-checks only.