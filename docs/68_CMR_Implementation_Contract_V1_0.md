# DOCUMENT 68: CMR IMPLEMENTATION CONTRACT
## Frozen Schema, Ingestion Semantics, and Pipeline Specification
## February 17, 2026

---

## Status and Authority

This document is the **frozen CMR contract** that Codex identified as the primary engineering blocker. It defines the data models, ingestion semantics, and pipeline steps with enough precision for Claude Code to implement without further Opus consultation. Once accepted, this contract is IMMUTABLE for the duration of Sprint 7–8 implementation. Changes require a versioned amendment with explicit rationale.

This document supersedes:
- The CMR spec fragments in Docs 7, 9, 11, 14
- The stale task descriptions in the Feb 15 Comprehensive Task List
- Any informal CMR discussion in panel documents

---

## PART 1: CURRENT ENGINEERING REALITY

### What Exists (from Codex Feb 17 audit)

| Component | Status | Location |
|-----------|--------|----------|
| Template files | 150 JSON files | data/templates/ |
| Template loader | File-based registry | src/theory/templateRegistry.ts |
| Calibration in templates | 23 with calibration blocks; all 150 have lifespan fields | data/templates/*.json |
| Web of belief | OPERATIONAL: 10,670 beliefs, 25,959 constraints, 1,555 bridges | src/services/web_persistence.py; data/web_persistence.db |
| Test suite | 2,945 passing, 9 skipped | tests/ |
| CMR pipeline | Placeholder only | src/cmr/__init__.py |
| Staging theory-links | 1,361 in CSV, NOT loaded into web | data/review/tranche80_confirmed_rows.csv |
| Sprint tracker | LIVE: TASKS.md (canonical). STALE: docs/02-15_15 (ignore) | TASKS.md |

### What's Missing

1. CMR pipeline code (Steps 1–7)
2. Template DB schema (templates are in JSON files, not queryable DB tables)
3. Staging theory-link ingestion
4. Common effect metric (WIS from Doc 67)
5. Template ↔ web-of-belief linkage

---

## PART 2: DATA MODELS

### 2.1 Template DB Model

The 150 JSON template files need a DB-backed query layer. Do NOT replace the JSON files — add a DB index on top of them.

```python
class TemplateRecord(Base):
    """DB index for template JSON files. Source of truth remains JSON."""
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True)
    template_id = Column(String, unique=True, nullable=False)  
    # e.g. "COLLABORATIVE_CREATIVITY_ARCHITECTURE_001"
    display_id = Column(String, unique=True, nullable=False)  
    # e.g. "CREA4"
    name = Column(String, nullable=False)
    series = Column(String, nullable=False)  
    # e.g. "CREA", "L", "MAT", "T"
    generation = Column(Integer, nullable=False)  
    # 1 = T/M/AX series; 2 = domain series
    
    # Classification from Doc 67
    dedup_status = Column(String, nullable=False)  
    # "active" | "superseded" | "residual" | "reference" | "gap"
    superseded_by = Column(String, nullable=True)  
    # display_id of superseding template, if applicable
    
    # Metadata
    pe_contribution = Column(String, nullable=False)  
    # "predictive" | "explanatory" | "organizational"
    maturity = Column(String, nullable=False)  
    # "established" | "supported" | ... | "speculative"
    calibration_status = Column(String, nullable=False)  
    # "substantial" | "partial" | "protocol" | "uncalibrated"
    practical_accessibility = Column(String, nullable=False)  
    # "A" | "B" | "C" | "D"
    ecological_validation = Column(Boolean, default=False)
    
    # File reference
    json_path = Column(String, nullable=False)  
    # Relative path to JSON file in data/templates/
    
    # Source documents
    source_docs = Column(String, nullable=False)  
    # Comma-separated doc numbers, e.g. "55,58,65"
```

**Ingestion semantics**: Scan data/templates/*.json. For each file, extract the top-level metadata fields and populate the TemplateRecord. The JSON file remains the source of truth for parameters, scope conditions, interactions, etc. The DB table is an INDEX for queries like "give me all active Gen-2 templates in the CREA series with calibration_status >= partial."

**Migration**: Create table. Scan 150 existing JSON files. For each, classify per Doc 67 Part 1 deduplication map and insert record. Estimated: ~2 hours coding, ~1 hour classification mapping.

### 2.2 CMR Evaluation Model

```python
class CMREvaluation(Base):
    """A single evaluation run: paper OR building assessment."""
    __tablename__ = "cmr_evaluations"
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now())
    evaluation_type = Column(String, nullable=False)  
    # "paper" | "building" | "design_review"
    target_description = Column(Text, nullable=False)  
    # Free text: paper citation, building name, design brief
    status = Column(String, default="in_progress")  
    # "in_progress" | "complete" | "failed"
    
    # For building evaluations
    building_context = Column(JSON, nullable=True)  
    # {climate: str, building_type: str, occupant_profile: {...}}


class CMRTemplateActivation(Base):
    """Which templates were activated for this evaluation and why."""
    __tablename__ = "cmr_template_activations"
    
    id = Column(Integer, primary_key=True)
    evaluation_id = Column(Integer, ForeignKey("cmr_evaluations.id"))
    template_display_id = Column(String, ForeignKey("templates.display_id"))
    
    activation_reason = Column(Text)  
    # Why this template was activated for this evaluation
    
    # Inputs provided
    inputs = Column(JSON, nullable=False)  
    # {parameter_name: value, ...} matching template's inputs_required
    
    # Computed outputs
    outputs = Column(JSON, nullable=True)  
    # {output_name: value, ...} from template computation
    wis_score = Column(Float, nullable=True)  
    # Wellbeing Impact Score (0-100) converted from template output
    wis_confidence = Column(Float, nullable=True)  
    # Confidence interval half-width
    
    # Interaction adjustments
    interaction_adjustments = Column(JSON, nullable=True)  
    # [{with_template: str, adjustment_type: str, factor: float}, ...]


class CMRDomainScore(Base):
    """Aggregated domain-level scores."""
    __tablename__ = "cmr_domain_scores"
    
    id = Column(Integer, primary_key=True)
    evaluation_id = Column(Integer, ForeignKey("cmr_evaluations.id"))
    domain = Column(String, nullable=False)  
    # "A1" through "A10"
    
    wis_score = Column(Float, nullable=False)
    wis_confidence = Column(Float, nullable=False)
    n_templates_activated = Column(Integer, nullable=False)
    template_ids = Column(String)  # Comma-separated
    
    # Aggregation details
    aggregation_method = Column(String, default="weighted_average")
    weight_basis = Column(String, default="calibration_confidence")


class CMROverallScore(Base):
    """Overall assessment score."""
    __tablename__ = "cmr_overall_scores"
    
    id = Column(Integer, primary_key=True)
    evaluation_id = Column(Integer, ForeignKey("cmr_evaluations.id"))
    
    wis_geometric_mean = Column(Float, nullable=False)
    wis_confidence = Column(Float, nullable=False)
    n_domains_assessed = Column(Integer, nullable=False)
    
    # Flags
    severe_deficit_domains = Column(String, nullable=True)  
    # Domains with WIS < 30
    data_gaps = Column(String, nullable=True)  
    # Domains with insufficient input data
```

### 2.3 ReductionClaim Model (for Tier 2 theory work)

```python
class ReductionClaim(Base):
    """Maps a Tier 2 theory construct to Tier 1 template mechanisms."""
    __tablename__ = "reduction_claims"
    
    id = Column(Integer, primary_key=True)
    
    # The Tier 2 construct being reduced
    tier2_theory = Column(String, nullable=False)  
    # e.g. "ART", "SRT", "Biophilia"
    tier2_construct = Column(String, nullable=False)  
    # e.g. "Soft Fascination", "Prospect", "Being Away"
    
    # The reduction
    reduction_type = Column(String, nullable=False)  
    # "full" | "partial" | "irreducible_residual"
    template_mappings = Column(JSON, nullable=False)  
    # [{template_id: str, mechanism: str, coverage: float}, ...]
    # coverage: 0-1, how much of the construct this template explains
    
    irreducible_residual = Column(Text, nullable=True)  
    # What cannot be reduced to template mechanisms
    
    confidence = Column(String, nullable=False)  
    # "high" | "moderate" | "low"
    source_panel = Column(String, nullable=True)  
    # e.g. "T2-A" for ART reduction panel
    
    # Staging link reconciliation
    staging_links_reconciled = Column(Integer, default=0)
    staging_links_total = Column(Integer, default=0)
```

---

## PART 3: PIPELINE STEPS

### Overview

The CMR pipeline has TWO entry points:
1. **Building Evaluation**: environmental measurements → template activations → WIS scores → report
2. **Paper Evaluation**: paper claims → causal decomposition → template matching → assessment

Building Evaluation is simpler and should be implemented FIRST. It is immediately useful and exercises most of the infrastructure. Paper Evaluation adds NLP/claim extraction and should come second.

### 3.1 Building Evaluation Pipeline (Priority 1)

```
STEP 1: Context Definition
  Input: building_type, climate_zone, occupant_profile (age, cultural context)
  Output: CMREvaluation record + context-dependent parameter adjustments
  
STEP 2: Feature Input
  Input: measured/estimated architectural features
  Output: structured input dictionary matching template input requirements
  Method: For each feature, identify which template(s) it feeds.
    Use practical_accessibility tier to flag missing inputs.
    Architect provides Tier A inputs directly.
    System flags Tier B-D inputs as "not assessed" or "estimated."
  
STEP 3: Template Activation
  Input: feature dictionary + context
  Output: list of CMRTemplateActivation records
  Method: For each template in the active set (dedup_status = "active"):
    Check if required inputs are available.
    If yes: activate. If partial: activate with reduced confidence.
    If no required inputs available: skip (record as data gap).
  Deduplication check: if a superseded template's gen-2 replacement 
    is active, do NOT activate the superseded template.
  
STEP 4: Template Computation
  Input: activated templates + their inputs
  Output: raw template outputs (d values, zone classifications, indices)
  Method: For each activated template, run the computation defined 
    in its JSON file. This is template-specific logic.
    Apply lifespan moderation (AGE-I/DEV-I multipliers) based on 
    occupant_profile.age.
    Apply cultural moderation where applicable.
  
STEP 5: WIS Conversion
  Input: raw template outputs
  Output: template-level WIS scores with confidence intervals
  Method: Apply Doc 67 Part 3 conversion rules:
    Cohen's d → WIS = Φ(d/√2) × 100
    Goldilocks → WIS via zone mapping
    Thresholds → WIS via distance-from-threshold mapping
    Quality indices → WIS via affine scaling
  Confidence: propagate from template calibration_status:
    substantial → ±5 WIS
    partial → ±10 WIS  
    protocol → ±15 WIS
    uncalibrated → ±20 WIS
  
STEP 6: Interaction Adjustment
  Input: template-level WIS scores + interaction records
  Output: adjusted WIS scores
  Method: Check interaction matrices:
    CREA2 2×2×2: if multiple pathways active, apply sub-additivity
    VF1 × VF3: additive (no adjustment needed)
    Convergence triad (L3 + MAT4 + VIEW1): apply super-additivity
    Deduplication: VF3 → CREA2B single chain — do not double-count
  
STEP 7: Domain Aggregation
  Input: adjusted template WIS scores
  Output: CMRDomainScore records (one per assessed domain)
  Method: Weighted average within domain.
    Weights: substantial=1.0, partial=0.7, protocol=0.4, uncalibrated=0.2
  
STEP 8: Overall Assessment
  Input: domain WIS scores
  Output: CMROverallScore record
  Method: Geometric mean of domain WIS scores.
    Flag domains with WIS < 30 as severe deficits.
    Flag domains with insufficient data as gaps.
    Report confidence as propagated uncertainty.
  
STEP 9: Report Generation
  Input: all above
  Output: structured report
  Content:
    - Overall WIS score with confidence
    - Domain breakdown (table)
    - Strengths (domains WIS > 70)
    - Deficits (domains WIS < 40)
    - Data gaps (domains not assessable)
    - Specific recommendations (templates with lowest WIS, 
      what changes would improve them)
    - Uncertainty disclosure (which parameters are expert estimates,
      which are empirically validated)
```

### 3.2 Paper Evaluation Pipeline (Priority 2)

```
STEP 1: Claim Extraction
  Input: paper text (or structured abstract)
  Output: list of causal claims
    Each claim: {independent_var, dependent_var, direction, 
      effect_size, sample, context}
  Method: LLM-assisted extraction with human verification.
    Use the 150 template parameter names as extraction vocabulary.
  
STEP 2: Template Matching
  Input: extracted claims
  Output: claim-template alignment
  Method: For each claim, find templates whose causal_links 
    match the claim's IV → DV structure.
    Score alignment: exact match, partial match, no match.
    Multiple templates may match one claim.
  
STEP 3: Mechanism Tracing
  Input: aligned claims + templates
  Output: mechanistic assessment
  Method: For each claim-template pair:
    Does the claim's proposed mechanism match the template's 
    causal pathway?
    SUBSTITUTE: could an alternative mechanism explain the finding?
    VARY_MOD: do the moderators in the claim match the template's 
    scope conditions?
    BLOCK: if the template's mechanism were blocked, would the 
    claim's effect disappear?
  
STEP 4: Convergence Assessment
  Input: mechanism traces
  Output: convergence score per claim
  Method: Claims supported by multiple templates with independent 
    mechanisms get higher convergence scores.
    Claims supported by a single template get moderate scores.
    Claims contradicted by template predictions get flags.
  
STEP 5: Composition Check (Barrett R10)
  Input: all claim assessments
  Output: composition failure flags
  Method: Check for cases where individual mechanisms are valid 
    but their COMBINATION produces unexpected interactions 
    (the interaction matrices from CREA-III, VF-II help here).
  
STEP 6: Prioritization
  Input: all assessments
  Output: ranked findings
  Method: Rank by value of information — which findings, if 
    confirmed or refuted, would most change the template system?
    High VOI: claims that contradict template predictions.
    Medium VOI: claims in gap areas (no matching template).
    Low VOI: claims that confirm well-calibrated templates.
  
STEP 7: Report Generation
  Input: all above
  Output: paper evaluation report
  Content:
    - Summary of paper's claims and template coverage
    - Mechanistic assessment per claim
    - Convergence scores
    - Composition flags
    - Prioritized findings for further investigation
    - Template system update recommendations
```

---

## PART 4: INGESTION TASKS

### 4.1 Template DB Index (Sprint 7, Batch 0)

**Task**: Create TemplateRecord table. Scan 150 JSON files. Classify per Doc 67 deduplication map. Insert records.

**Input**: data/templates/*.json + Doc 67 Part 1 classification.

**Output**: Populated templates table with all 150 records classified.

**Validation**: Query "all active Gen-2 CREA series" returns CREA1–CREA4. Query "all superseded" returns ~14 templates. No duplicates.

### 4.2 Staging Theory-Links (Sprint 7, Batch 1)

**Task**: Load 1,361 rows from tranche80_confirmed_rows.csv into web of belief as theory-link constraints.

**Input**: data/review/tranche80_confirmed_rows.csv

**Mapping**:
- ART links (1,251): theory_id = "ART", constraint_type = "tier2_theory_link"
- Biophilia links (102): theory_id = "Biophilia", constraint_type = "tier2_theory_link"  
- SRT links (3): theory_id = "SRT", constraint_type = "tier2_theory_link"
- Each row becomes a constraint linking the paper's claim to the Tier 2 theory construct.

**Output**: 1,361 new constraints in web_persistence.db. Verify count matches CSV.

### 4.3 WIS Conversion Module (Sprint 7, Batch 2)

**Task**: Implement Doc 67 Part 3 conversion functions.

**Functions needed**:
```python
def cohens_d_to_wis(d: float) -> float:
    """WIS = Φ(d/√2) × 100"""

def goldilocks_to_wis(value: float, zone_boundaries: dict) -> float:
    """Map value to WIS based on zone classification."""

def threshold_to_wis(value: float, threshold: float) -> float:
    """Map distance from threshold to WIS."""

def aggregate_domain_wis(template_scores: list[dict]) -> dict:
    """Weighted average within domain."""

def aggregate_overall_wis(domain_scores: list[dict]) -> dict:
    """Geometric mean across domains."""
```

**Validation**: Cohen's d = 0 → WIS 50. Cohen's d = 0.5 → WIS ~69. Cohen's d = −0.5 → WIS ~31. Geometric mean of [90, 15] ≈ 36.7.

### 4.4 Enum Drift Resolution (Immediate)

**Task**: Resolve the 2 open enum-drift issues in voi_search.py and discovery_funnel.py.

**Method**: Run check_enum_drift.py. For each flagged file, align to canonical_enums.json. If canonical needs updating, update it. If file is stale, fix file.

**This is the smallest task and should be done FIRST** to clear the test warnings.

---

## PART 5: CANONICAL SPRINT TRACKER

### Decision

**TASKS.md is the single source of truth.** The stale tracker at docs/02-15_15_Global_Status_Task_Tracker_V1_0.md should be marked DEPRECATED with a pointer to TASKS.md.

### Updated Sprint Mapping

The original sprint numbering (0–9) from the Feb 15 task list maps imperfectly to the actual work done. Here is the CANONICAL mapping going forward:

| Sprint | Scope | Status | Remaining |
|--------|-------|--------|-----------|
| S0 Foundation | File structure, basic models | ✅ Complete | — |
| S1 Epistemic Core | Claim extensions, enum consolidation | ✅ Complete (2 drift items) | Fix enum drift |
| S2–5 Pipeline & Integration | BN, coherence, extraction, integration | Partially complete (via live tracker) | Audit needed |
| S6 Research Queue | ResearchTarget, queue service, VOI | ✅ Complete | — |
| S7 Theory Tier | Template models, encoding, bridging | 3/6 complete | Template DB index, staging links, CMR models |
| S8 Pipeline Hardening | Testing, validation | 6/6 complete | — |
| S9 Research Queue Track | Extended queue functionality | 7/7 complete | — |
| **S10 CMR Pipeline** | **Steps 1–9 of Building Eval** | **NOT STARTED** | **This is the new work** |
| **S11 Paper Evaluation** | **Steps 1–7 of Paper Eval** | **NOT STARTED** | **After S10** |

### Implementation Order for S10

1. Enum drift fix (4.4) — clear the decks, <1 hour
2. Template DB index (4.1) — make templates queryable, ~2 hours
3. Staging link ingestion (4.2) — populate theory links, ~1 hour
4. WIS module (4.3) — common metric, ~2 hours
5. Building Eval Steps 1–3 (context + input + activation) — ~4 hours
6. Building Eval Steps 4–6 (computation + WIS + interactions) — ~6 hours
7. Building Eval Steps 7–9 (aggregation + overall + report) — ~4 hours
8. End-to-end test: Salk Institute worked example — ~2 hours

**Total estimated: ~22 hours of Claude Code work across 3–4 sessions.**

---

## PART 6: CONTRACT FREEZE POLICY

### What Is Frozen

1. The data models in Part 2 (TemplateRecord, CMREvaluation, CMRTemplateActivation, CMRDomainScore, CMROverallScore, ReductionClaim)
2. The pipeline steps in Part 3 (Building Eval Steps 1–9, Paper Eval Steps 1–7)
3. The WIS conversion rules in Doc 67 Part 3
4. The deduplication classifications in Doc 67 Part 1

### What Is NOT Frozen

1. Implementation details (language choice, library choice, internal architecture)
2. The JSON template file format (existing files are not changed; new fields can be added)
3. UI/reporting format
4. Specific parameter values (these are in template JSON files and will continue to be updated by Opus panels)

### Amendment Process

If Claude Code or Codex encounters a case where the frozen contract is unworkable:
1. Document the specific problem
2. Propose the minimum change that resolves it
3. Opus approves or rejects
4. If approved, the amendment is recorded in a new section of this document (not inline edits)

---

*Document 68: CMR Implementation Contract — V1.0*
*February 17, 2026*
*Status: FROZEN for Sprint 7–10 implementation*
*Parts: (1) Engineering Reality, (2) Data Models, (3) Pipeline Steps, (4) Ingestion Tasks, (5) Sprint Tracker, (6) Freeze Policy*
*Primary deliverable: Building Evaluation Pipeline (S10) — estimated 22 hours Claude Code*
*Secondary deliverable: Paper Evaluation Pipeline (S11) — estimated after S10*
*Biggest finding: The engineering is much further along than the stale tracker suggested. Infrastructure exists. What was missing was this contract.*
