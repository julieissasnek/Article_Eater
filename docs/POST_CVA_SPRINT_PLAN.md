# Post-CVA Sprint Plan — Panel Recommendations & Execution Sprints

> **Generated**: 2026-02-28 · **Panels Convened**: 5 · **Sprints Planned**: 6

---

## Panel Deliberations

### Panel A: Outcome Vocabulary & Resolution Panel
*Simulated experts: Psychometrician (Barrett), Measurement Specialist (Kaplan), Taxonomist (Simon), Domain Scientist (Gifford), Skeptic (Cartwright)*

**Problem assessed**: 24-term vocab vs 4,369 unresolved terms.

**Recommendations**:
1. **Cluster-first, expand-second**: Run unsupervised clustering on 4,369 terms before proposing new canonical entries. Many are synonyms or jargon variants of existing terms.
2. **Domain-proportional expansion**: Current 7 domains are unevenly populated (cog: 6 terms, health: 2). Expand proportionally.
3. **Operationalization required**: Every new term needs ≥1 operationalization (questionnaire, task, or biomarker). Terms without operationalizations are unfalsifiable.
4. **Hierarchical depth**: Add intermediate nodes (e.g., `cog.attention.sustained`, `cog.attention.divided`) — current vocab too flat.
5. **Reject noise aggressively**: ~30% of unresolved terms are measurement artifacts ("18 h in patients receiving dexmedetomidine") not outcomes. Filter before human review.

**Estimated effort**: 12h clustering + 8h expansion + 4h validation = **24h**

### Panel B: Image Pipeline & PDF Extraction Panel
*Simulated experts: VLM Specialist, PDF Engineer, Research Librarian, Visual Psychologist (Arnheim), Image Retrieval Specialist*

**Problem assessed**: 56 HIGH-priority articles need image extraction + classification.

**Recommendations**:
1. **Two-pass strategy**: Pass 1 (cheap) — extract all images from PDFs using PyMuPDF/fitz. Pass 2 (targeted) — classify using VLM (Gemini Flash) only for images > 100×100px.
2. **Caption co-extraction**: Extract text within ±3 lines of figure references. Critical for linking images to findings.
3. **DOI-based linking**: Map extracted `Fig. N` references back to findings that cite them. Enables "show me the stimulus" queries.
4. **Cost estimate**: Pass 1 = free (local). Pass 2 = $2-4 for Gemini Flash on ~500 images from 56 articles.
5. **Quality gate**: Auto-reject decorative/logo images (< 200px either dimension, aspect ratio > 5:1). Expect ~60% of extracted images are non-stimulus.

**Estimated effort**: 8h extraction script + 6h classification + 4h linking = **18h**

### Panel C: Taxonomy Reconciliation Panel
*Simulated experts: Ontologist, Information Architect, Environmental Psychologist, Pragmatist (Dewey)*

**Problem assessed**: Three parallel classification systems (tag_engine 3 dimensions, outcome_taxonomy 7 domains, image_tagger 12 categories) with overlap and gaps.

**Recommendations**:
1. **Don't unify, cross-reference**: The three systems serve different purposes. Forcing unification loses expressiveness. Instead, build explicit mapping tables.
2. **Identify overlaps quantitatively**: tag_engine "lighting" ↔ outcome "physio.alertness" ↔ image feature "cnfa.light.*" — document these with confidence scores.
3. **Gap analysis**: Which image features have NO outcome mapping? Which outcomes have NO image representation? These are the research gaps.
4. **User-facing navigation**: When querying, user shouldn't need to know which system to search. Build a unified search layer.

**Estimated effort**: 8h mapping + 4h gap analysis + 6h search layer = **18h**

### Panel D: Annotation Quality Architecture Panel
*Simulated experts: Gold Standard Reviewer, Adversarial Critic, User Advocate, Calibration Expert*

**Recommendations**:
1. **Annotation confidence must be non-optional**: Every auto-generated annotation needs a confidence score. No defaults of 1.0.
2. **Active learning loop**: Track when annotations disagree with human corrections. Use disagreements to improve auto-annotator.
3. **10% stratified sample**: QA sample should be stratified by annotation type, not random. Oversample rare types.
4. **Outcome: calibration curves**: Plot predicted vs actual accuracy for each annotation type. Overconfident annotators are worse than underconfident ones.

**Estimated effort**: 6h framework + 4h initial evaluation + 2h calibration = **12h**

### Panel E: TRS Integration & Fallback Panel
*Simulated experts: Systems Architect, API Designer, Reliability Engineer, Product Manager*

**Recommendations**:
1. **Fallback-first design**: Build local taxonomy cache that works without TRS. TRS enriches but never blocks.
2. **Health check endpoint**: Before querying TRS, check `/health`. If response time > 2s or status != 200, use local fallback.
3. **Sync strategy**: Nightly sync TRS → local cache. Delta sync, not full dump.
4. **Version pinning**: Lock to TRS schema v0.2.8. Breaking changes require explicit migration sprint.

**Estimated effort**: 8h fallback cache + 4h sync + 4h testing = **16h**

---

## Sprint Plan

### Sprint S-1: Outcome Vocabulary Expansion (Week 1)
**Goal**: Expand vocab from 24 → 80+ terms, drain unresolved queue  
**Owner**: AG / PANEL-1  
**Effort**: 24h

| # | Task | Hours |
|---|------|-------|
| 1a | Cluster 4,369 unresolved terms by domain/similarity | 6 |
| 1b | Filter ~30% noise terms (measurement artifacts, non-outcomes) | 4 |
| 1c | Run AI panel on remaining clusters → propose canonical entries | 6 |
| 1d | Add operationalizations for new terms | 4 |
| 1e | Update `outcome_vocab.json` + re-run resolver on queue | 4 |

**Exit criteria**: vocab ≥ 80 terms, unresolved < 1,000, all new terms have operationalizations

---

### Sprint S-2: PDF Image Extraction Pipeline (Week 1-2)
**Goal**: Extract + classify images from 56 HIGH-priority articles  
**Owner**: AG or CW  
**Effort**: 18h

| # | Task | Hours |
|---|------|-------|
| 2a | Create batch extraction script using PyMuPDF | 4 |
| 2b | Extract images + captions from 56 articles | 4 |
| 2c | Classify with Gemini Flash (stimulus/chart/diagram/decorative) | 4 |
| 2d | Link figure references to findings | 4 |
| 2e | Ingest classified stimuli into image pool | 2 |

**Exit criteria**: ≥40 articles processed, stimulus images tagged and stored

---

### Sprint S-3: Outcome Backfill & Pipeline Wiring (Week 2)
**Goal**: Canonical outcome_ids on 80%+ beliefs, resolver in full pipeline  
**Owner**: AG or CW  
**Effort**: 16h

| # | Task | Hours |
|---|------|-------|
| 3a | Script to backfill existing beliefs with canonical outcome_ids | 6 |
| 3b | Wire resolver into extraction pipeline | 4 |
| 3c | Wire resolver into panel extraction | 4 |
| 3d | Verify outcome_id query coverage improvement | 2 |

**Exit criteria**: ≥80% beliefs with canonical IDs, resolver in 3 pipeline stages

---

### Sprint S-4: AI Panel Infrastructure + Taxonomy Reconciliation (Week 2-3)
**Goal**: Reusable panel framework + cross-system mapping  
**Owner**: AG  
**Effort**: 18h

| # | Task | Hours |
|---|------|-------|
| 4a | Build `ai_panel_resolver.py` (panelists, voting, thresholds) | 8 |
| 4b | Cross-reference mapping (tag × outcome × image taxonomy) | 6 |
| 4c | Gap analysis report | 4 |

**Exit criteria**: Panel framework tested, cross-reference table generated

---

### Sprint S-5: TRS Integration with Fallback (Week 3)
**Goal**: CVA uses TRS when available, local cache when not  
**Owner**: CW  
**Effort**: 16h

| # | Task | Hours |
|---|------|-------|
| 5a | Local taxonomy cache with fallback | 6 |
| 5b | TRS health check + conditional query | 4 |
| 5c | Nightly sync (TRS → local) | 4 |
| 5d | Integration tests | 2 |

**Exit criteria**: System works with TRS up AND down, sync tested

---

### Sprint S-6: CVA-QA Integration (Week 3-4)
**Goal**: CVA annotations surface in QA answers  
**Owner**: AG  
**Effort**: 20h

| # | Task | Hours |
|---|------|-------|
| 6a | `cva_annotation_service.py` — CRUD + auto-annotate | 6 |
| 6b | Migration 025 — expand cva_annotations schema | 2 |
| 6c | `cva_qa_enricher.py` — CVA → QA bridge | 6 |
| 6d | `environment_image_db.py` + Migration 026 | 4 |
| 6e | Query engine integration | 2 |

**Exit criteria**: QA answers include CVA analysis, environment matching works

---

## Total Effort: ~112h across 6 sprints over 4 weeks

| Sprint | Focus | Hours | Owner |
|--------|-------|-------|-------|
| S-1 | Outcome Vocab | 24h | AG |
| S-2 | PDF Images | 18h | AG/CW |
| S-3 | Outcome Backfill | 16h | AG/CW |
| S-4 | Panel Infra + Taxonomy | 18h | AG |
| S-5 | TRS Fallback | 16h | CW |
| S-6 | CVA-QA Integration | 20h | AG |
| **Total** | | **112h** | |
