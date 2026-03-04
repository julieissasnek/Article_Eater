# Subsystem Inventory — For Addition to Master Doc

**Date**: 2026-03-03  
**Author**: AG (Antigravity)  
**Purpose**: CW should incorporate this subsystem inventory into the Master Document (CMR). The master doc currently has NO engineering subsystem inventory section — only domain-level subsystems (DMN, allostatic, etc.).

---

## Why This Is Needed

The system has been audited multiple times (V7, V9, V13) and each audit defines subsystems independently. There is no single canonical list. The master doc should have one.

## Canonical Subsystem Inventory

Sources cross-referenced: V9 Audit (17 subsystems), V13 Full Audit (10 enrichment subsystems), Panel Feb 25 (7 epistemological subsystems), QA Annotation Plan (9 QA subsystems + 12 annotation SCs).

### Tier 1: System-Level Subsystems (17, from V9 Audit)

| # | Subsystem | Files | LOC | Key Modules |
|:--|:----------|:------|:----|:------------|
| 1 | QA & Query | 9 | 10,228 | `arbitrary_qa_handler`, `card_retriever`, `query_classifier`, `answer_renderer` |
| 2 | Export & Reporting | 7 | 7,262 | `export_engine`, `export_bundles`, `report_generator`, `bibtex_generator` |
| 3 | Web of Belief | 5 | 6,784 | `web_of_belief`, `web_persistence`, `knowledge_catalog` |
| 4 | Paper Acquisition | 5 | 5,748 | `paper_fetcher`, `paper_integration/orchestrator` |
| 5 | Theory & Templates | 6 | 5,495 | `theory_guide_service`, `template_quality_assurance` |
| 6 | DB & Infrastructure | 6 | 5,895 | `db_locator`, `db_migrations` |
| 7 | Bayesian Network | 4 | 5,238 | `incremental_bn`, `bbn_calibrator`, `bn_coherence_client` |
| 8 | Extraction & Integration | 5 | 5,128 | `extraction_to_web`, `evidence_integration`, `auto_ingest_pdfs` |
| 9 | Overseer & Self-Monitoring | 5 | 4,861 | `overseer`, `overseer_self_healing`, `compute_system_health` |
| 10 | Interpretation Space | 4 | 4,692 | `interpretive_intelligence`, `epistemic_projection` |
| 11 | Warrant & Credence | 4 | 3,316 | `credence_intervals`, `warrant_service` |
| 12 | T3 Belief Engine | 6 | 3,334 | `belief_clustering`, `generalization` |
| 13 | Image Pipeline | 6 | 3,251 | `image_tag_service`, `environment_image_db` |
| 14 | Taxonomy & Vocabulary | 4 | 3,127 | `environment_taxonomy`, `canonical_variables` |
| 15 | CVA | 8 | 2,741 | `cva_valuation_engine`, `cva_beauty`, `cva_constraint_engine` |
| 16 | Argumentation | 2 | 1,903 | `argumentation_graph`, `argument_attack` |
| 17 | Annotation | 2 | 1,121 | `annotation_service`, `cva_annotation_service` |

### Tier 2: Enrichment Pipeline Subsystems (10, from V13 Audit)

These live inside `answer_enrichment_orchestrator.py` as the 9-step enrichment pipeline:

| # | Subsystem | V13 Score | Steps |
|:--|:----------|:---------|:------|
| E1 | Orchestration & Budget | 7/10 | Pipeline coordination |
| E2 | Grounding Gate | 8/10 | Step 0 (pre-enrichment) |
| E3 | Credence Enrichment | 3/10 | Steps 1-2 |
| E4 | Warrant Trace | 2/10 | Steps 3-4 |
| E5 | Framework Voices | 2/10 | Step 7 |
| E6 | Language Adaptation | 1/10 | Step 7 |
| E7 | Gap Analysis | 4/10 | Steps 5-6 |
| E8 | Follow-Ups | 3/10 | Step 8 |
| E9 | Figure Suggestions | 2/10 | Step 9 |
| E10 | Data Integrity | 5/10 | Cross-cutting |

### Tier 3: Epistemological Subsystems (7, from Panel Feb 25)

These address the philosophical architecture of belief management:

| # | Subsystem | Panel Verdict |
|:--|:----------|:-------------|
| A | Web of Belief Credence Computation | Wire immediately (critical gap) |
| B | Provenance & Haack Foundherentism | Synchronous computation in Step 5 |
| C | Bayesian Network & Coupling | Hierarchical one-directional (web → BN) |
| D | QA Cache Recomputation | Batched nightly |
| E | Coherence Computation & Alerting | Per-theory tracking with baselines |
| F | Social Epistemology & Community Identification | Surface contestation explicitly |
| G | Value of Information (VOI) Gap Closure | Expert panel to define high-VOI questions |

### Tier 4: QA System Subsystems (9, from QA Annotation Plan)

| # | Subsystem | Wired? | Tests? |
|:--|:----------|:-------|:-------|
| 1 | Reflex System | ✅ Nightly | ✅ 23 classes |
| 2 | Template QA | ❌ Manual only | ⚠️ Partial |
| 3 | Argument QA | ❌ Manual only | ⚠️ Partial |
| 4 | Warrant Service | ❌ Not nightly | ⚠️ Partial |
| 5 | Source Quality | ❌ Computed unused | ✅ |
| 6 | Gap Predictor | ⚠️ Added to nightly | ⚠️ Partial |
| 7 | VOI Scoring | ❌ | ⚠️ |
| 8 | VOI Search | ❌ | ⚠️ |
| 9 | QA Cache | ✅ Nightly | ✅ |

---

## Where to Place in Master Doc

This inventory should go as a new section in the infrastructure/architecture portion of the CMR, after the epistemic architecture sections. Suggested heading:

```markdown
## §XX. Engineering Subsystem Architecture

### XX.1 System-Level Subsystems (17)
### XX.2 Enrichment Pipeline Subsystems (10)
### XX.3 Epistemological Subsystems (7)
### XX.4 QA System Subsystems (9)
```

## Success Conditions Reference

Full success conditions for all subsystems are documented in:
- `docs/SUCCESS_CONDITIONS_2026-03-03.md` (AG)
- `docs/QA_SYSTEM_SPEC.md` §8 (22 QA SCs)
- `docs/AG_QA_ANNOTATION_IMPLEMENTATION_PLAN_2026-03-01.md` (12 annotation SCs)
