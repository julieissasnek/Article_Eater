# Panel Consultation Plan: Sprint 3.0 Decisions Review
**Date**: 2026-02-09
**Trigger**: 27 unreviewed implementation decisions accumulated across 10 modules

---

## Executive Summary

Sprint 3.0 implementation (Feb 8-9, 2026) produced ~10,100 lines of new code with 27 design decisions that bypassed panel consultation. This document plans 6 panel sessions to review and validate these decisions.

---

## Panel Schedule

### Panel 1: P-VOI (Foundational)
**Topic**: Value of Information - Theoretical Grounding
**Duration**: 60-90 minutes
**Priority**: CRITICAL (foundational for DISC-* tasks)

**Core Question**: How does our gap-based VOI relate to classical VOI calculations?

**Context**:
- Classical VOI (Howard, 1966; Raiffa & Schlaifer, 1961) calculates expected value of perfect/imperfect information given:
  - Prior probability distribution
  - Decision alternatives
  - Utility function
  - Cost of information acquisition

- Our system has **structural gaps** in argument networks:
  - Missing evidence for claims
  - Weak support paths
  - Contradictions needing resolution
  - Boundary conditions unclear

**Key Differences**:
| Classical VOI | Our Gap-Based VOI |
|---------------|-------------------|
| Continuous probability space | Discrete belief network |
| No explicit "missing nodes" | Explicit gap identification via argument structure |
| Decision-theoretic utility | Coherence improvement |
| One-shot information value | Iterative refinement |

**Questions for Panel**:
1. Is treating argument gaps as "expected information locations" theoretically defensible?
2. How should gap VOI relate to belief credence and uncertainty?
3. What role does entrenchment play in gap prioritization?
4. How do we handle the exploration-exploitation tradeoff in gap search?
5. Should gap closure be measured by VOI reduction or coherence gain?

**Panelists**:
- Dr. Judea Pearl (causal networks, information value in DAGs)
- Dr. Herbert Simon (bounded rationality, satisficing)
- Dr. Paul Thagard (coherence maximization)
- Dr. Ronald Howard (decision analysis, original VOI)
- Dr. Susan Haack (foundherentism, epistemic justification)
- Dr. Marcia Bates (berrypicking, information foraging)

---

### Panel 2: P-S3-A (LLM Integration)
**Topic**: Query Routing & LLM Integration Decisions
**Duration**: 45-60 minutes
**Priority**: HIGH

**Decisions Under Review**:
| ID | Decision | Current Value | Risk |
|----|----------|---------------|------|
| D5 | 4-tier model hierarchy | NONE/FAST/CAPABLE/BEST | HIGH |
| D6 | Model-to-phase routing | Implicit | HIGH |
| D7 | Hardcoded LLM costs | Per-1k rates | MED |
| D8 | Temperature | 0.0 | LOW |
| D9 | No LLM in retrieval | Structured only | MED |
| D10 | LLM for synthesis | Yes | HIGH |
| D11 | Cost target distribution | 80/15/5% | MED |

**Panelists**:
- Dr. Dario Amodei (LLM scaling, cost-capability)
- Dr. Percy Liang (LLM limitations, HELM benchmarks)
- Dr. Yann LeCun (structured search vs. LLM)
- Dr. Emily Bender (prompt engineering, linguistics)
- Dr. Herbert Simon (bounded rationality in automation)

---

### Panel 3: P-S3-B (Search & Prioritization)
**Topic**: VOI Search Weights and Epsilon-Greedy Strategy
**Duration**: 45-60 minutes
**Priority**: HIGH

**Decisions Under Review**:
| ID | Decision | Current Value | Risk |
|----|----------|---------------|------|
| D1 | Uncertainty/Centrality/Sparsity weights | 0.4/0.3/0.3 | MED |
| D2 | Epsilon-greedy parameters | 0.3→0.05, decay=0.99 | MED |
| D3 | Uncertainty threshold | 0.3 | MED |
| D4 | Min relevance for results | 0.3 | MED |
| D19 | Default gap priority | 0.5 | LOW |

**Panelists**:
- Dr. Herbert Simon (satisficing, search strategies)
- Dr. Judea Pearl (network centrality)
- Dr. Marcia Bates (information retrieval)
- Dr. Paul Thagard (coherence-driven search)
- Dr. Jon Kleinberg (network algorithms)

---

### Panel 4: P-S3-C (Evidence Synthesis)
**Topic**: Meta-Analysis Thresholds and Evidence Pooling
**Duration**: 45-60 minutes
**Priority**: MEDIUM-HIGH

**Decisions Under Review**:
| ID | Decision | Current Value | Risk |
|----|----------|---------------|------|
| D12 | High heterogeneity threshold | I² > 0.5 | MED |
| D13 | Credence thresholds | 0.4 (low) / 0.7 (high) | MED |
| D14 | Pooling method | Inverse-variance (DerSimonian-Laird) | MED |
| D15 | Strength mapping | 0.75/0.5 | MED |

**Panelists**:
- Dr. Julian Higgins (Cochrane, meta-analysis methods)
- Dr. Nancy Cartwright (evidence diversity, external validity)
- Dr. Deborah Mayo (error statistics, severity)
- Dr. Andrew Gelman (Bayesian data analysis)
- Dr. Rachel Kaplan (CNfA domain expertise)

---

### Panel 5: P-S3-D (Visualization & Export)
**Topic**: Graph Visualization and Transferability Assessment
**Duration**: 30-45 minutes
**Priority**: MEDIUM

**Decisions Under Review**:
| ID | Decision | Current Value | Risk |
|----|----------|---------------|------|
| D17 | Transferability thresholds | 0.7 (high) / 0.4 (partial) | MED |
| D18 | Default scope confidence | 0.5 | MED |
| D21 | Min credence for visualization | 0.0 (all beliefs) | LOW |
| D22 | Node size multiplier | 1.5x for entrenchment | LOW |
| D23 | Default clustering mode | Theory-based | MED |
| D24 | JSONL vs JSON | Implicit | LOW |
| D25 | Parquet fallback | Silent | MED |

**Panelists**:
- Dr. Tamara Munzner (visualization principles)
- Dr. Nancy Cartwright (scope conditions)
- Dr. Bas van Fraassen (contrast classes)
- Dr. Herbert Simon (satisficing in display)

---

### Panel 6: P-S3-E (Discovery Funnel)
**Topic**: Gap Closure Classification and Funnel Metrics
**Duration**: 30 minutes
**Priority**: MEDIUM

**Decisions Under Review**:
| ID | Decision | Current Value | Risk |
|----|----------|---------------|------|
| D19 | Default gap priority | 0.5 | LOW |
| D20 | Closure type classification | 4 categories (full/partial/none/negative) | MED |

**Panelists**:
- Dr. Judea Pearl (causal attribution)
- Dr. Herbert Simon (satisficing categories)
- Dr. Jon Kleinberg (network flow, prioritization)
- Dr. Marcia Bates (search feedback loops)

---

## Execution Order

1. **P-VOI** (foundational) - Must complete first
2. **P-S3-B** (search) - Depends on VOI understanding
3. **P-S3-A** (LLM) - Architectural importance
4. **P-S3-C** (evidence) - Synthesis quality
5. **P-S3-E** (funnel) - Depends on search/evidence
6. **P-S3-D** (visualization) - Can be last

---

## Success Criteria

Each panel should produce:
1. **APPROVE/MODIFY/DEFER** decision for each item
2. **Specific value recommendations** for any MODIFY decisions
3. **Risk mitigation strategies** for any DEFER decisions
4. **Follow-up questions** for unresolved issues

---

## Post-Panel Actions

1. Update magic numbers in code with panel-approved values
2. Add decision documentation to code (D-### comments)
3. Create `docs/PANEL_CONSULTATION_SPRINT_3.0_RESULTS_2026-02-09.md`
4. Update TASKS.md with completed consultation items

---

*Generated: 2026-02-09*
