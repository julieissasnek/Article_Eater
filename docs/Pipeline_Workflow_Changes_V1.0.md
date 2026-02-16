# Pipeline & Workflow Changes Required by Non-Empirical Web Integration
## Version 1.0 — February 14, 2026
## Operational Change Document

---

# OVERVIEW

The Non-Empirical Web Integration Spec (V1.0) is not a documentation-only change. It requires modifications to programs, workflow sequencing, quality gates, and the operational runbook. This document specifies every concrete change, who makes it (Codex or Claude Code), and in what order.

---

# STAGE 1: ARTICLE TYPE CLASSIFIER

## Current State
- `scripts/build_article_type_tables.py` uses 11 coarse keyword-based buckets
- Gap audit M2 already flagged this as MAJOR: "Routing output is useful, but not sufficient to select the right extraction template family reliably"

## Required Change

**Program**: `scripts/build_article_type_tables.py`

**Change**: Replace 11-bucket keyword classifier with 15-family router.

```python
# CURRENT (line ~21)
BUCKETS = [
    "meta_analysis", "systematic_review", "narrative_review",
    "rct_interventional", "quasi_experimental", "observational",
    "cross_sectional_survey", "qualitative", "theoretical_conceptual",
    "methods_protocol", "unknown"
]

# REQUIRED
FAMILIES = [
    "empirical_v2", "meta_analysis", "systematic_review",
    "narrative_review", "theoretical", "conceptual_framework",
    "mixed_methods", "observational_field", "case_study",
    "interview_study", "ethnographic", "grounded_theory",
    "phenomenological", "thought_piece", "unknown"
]
```

**Implementation**: The classifier should:
1. Use LLM classification (not just keywords) with the 15-family vocabulary
2. Return `(family, confidence)` tuple
3. Route to `unknown` with `manual_review: true` when confidence < 0.70
4. Log classification decisions for audit

**Who**: Codex (it owns the extraction scripts)

**Priority**: HIGH — everything downstream depends on correct routing

---

# STAGE 2: EXTRACTION PROMPTS

## Current State
- Extraction prompts request claims in the empirical format (effect sizes, study design, etc.)
- Non-empirical papers get forced through this empirical template → produce nothing or garbage

## Required Change

**Programs**: All extraction prompt templates + `scripts/process_realtime_pdf_completion_queue.py`

**Change**: Family-aware prompt selection. Each of the 15 families gets its own extraction prompt that requests the RIGHT fields for that paper type.

```python
# CURRENT: one-size-fits-all extraction
def extract_claims(pdf_text):
    prompt = EMPIRICAL_EXTRACTION_PROMPT  # always this
    return llm_call(prompt, pdf_text)

# REQUIRED: family-routed extraction
EXTRACTION_PROMPTS = {
    "empirical_v2":         EMPIRICAL_PROMPT,        # existing
    "meta_analysis":        META_ANALYSIS_PROMPT,     # NEW
    "systematic_review":    SYSTEMATIC_REVIEW_PROMPT, # NEW
    "narrative_review":     NARRATIVE_REVIEW_PROMPT,  # NEW
    "theoretical":          THEORETICAL_PROMPT,       # NEW
    "conceptual_framework": CONCEPTUAL_PROMPT,        # NEW
    "thought_piece":        THOUGHT_PIECE_PROMPT,     # NEW
    "mixed_methods":        MIXED_METHODS_PROMPT,     # NEW
    "interview_study":      QUALITATIVE_PROMPT,       # shared
    "ethnographic":         QUALITATIVE_PROMPT,       # shared
    "grounded_theory":      GROUNDED_THEORY_PROMPT,   # NEW
    "phenomenological":     QUALITATIVE_PROMPT,       # shared
    "observational_field":  EMPIRICAL_PROMPT,         # reuse with mods
    "case_study":           CASE_STUDY_PROMPT,        # NEW
}

def extract_claims(pdf_text, article_family):
    prompt = EXTRACTION_PROMPTS[article_family]
    return llm_call(prompt, pdf_text)
```

**Each new prompt must**:
1. Request the node_type tag on every extracted claim
2. Request the edge_type tag on every extracted relation
3. Use the field names from ae.claim.v2 (`statement` not `claim_text`, `ae_confidence` not `confidence`)
4. Request family-specific fields (e.g., `derivation_chain` for theoretical, `pooled_effect_size` for meta-analysis)

**Who**: Codex (it owns extraction prompts)

**Priority**: HIGH — this is the core change that unlocks non-empirical extraction

---

# STAGE 3: EXTRACTION OUTPUT SCHEMA

## Current State
- `src/services/table_to_claims.py` emits `claim_text`, `confidence`, `metadata`
- Gap audit C1: web expects `statement`, `ae_confidence`, `statistics`, `constructs`, `study`
- Gap audit C2: claim-type vocabulary (`finding|methodology|sample|effect`) doesn't match epistemic mapper (`mechanistic|causal|associational|moderated|descriptive|null`)

## Required Change

**Program**: `src/services/table_to_claims.py`

**Change 1 — Field names**: Rename to match ae.claim.v2 contract
```python
# CURRENT
output = {
    "claim_text": claim,
    "confidence": score,
    "metadata": {...}
}

# REQUIRED
output = {
    "statement": claim,          # renamed
    "ae_confidence": score,       # renamed
    "node_type": node_type,       # NEW (one of 12)
    "article_type_family": family, # NEW (one of 15)
    "causal_level": causal_level, # from panel additions
    "argument_scheme": scheme,    # from panel additions
    "source_section": section,
    "source_page_start": start,
    "source_page_end": end,
    "source_quote": quote,
    "source_quote_hash": hash,
    "provenance_tier": tier,
    "evidence_level": level,
    # family-specific fields follow...
}
```

**Change 2 — Claim-type vocabulary**: Replace `finding|methodology|sample|effect` with node_type enum
```python
# CURRENT (line ~36)
CLAIM_TYPES = ["finding", "methodology", "sample", "effect"]

# REQUIRED
from enum import Enum
class NodeType(str, Enum):
    EMPIRICAL_FINDING = "EMPIRICAL_FINDING"
    SYNTHESIS_CONCLUSION = "SYNTHESIS_CONCLUSION"
    QUALITATIVE_FINDING = "QUALITATIVE_FINDING"
    THEORETICAL_PROPOSITION = "THEORETICAL_PROPOSITION"
    DERIVED_HYPOTHESIS = "DERIVED_HYPOTHESIS"
    CONCEPTUAL_DEFINITION = "CONCEPTUAL_DEFINITION"
    CONCEPTUAL_CONSTRAINT = "CONCEPTUAL_CONSTRAINT"
    EXPERT_SYNTHESIS = "EXPERT_SYNTHESIS"
    METHODOLOGICAL_CRITIQUE = "METHODOLOGICAL_CRITIQUE"
    KNOWLEDGE_GAP = "KNOWLEDGE_GAP"
    FRAMEWORK_STRUCTURE = "FRAMEWORK_STRUCTURE"
    BRIDGE_WARRANT = "BRIDGE_WARRANT"
```

**Who**: Codex (owns table_to_claims.py) + Claude Code (owns NodeType enum definition)

**Coordination**: Claude Code defines the enum in `src/epistemic/schema.py`; Codex imports and uses it in the extraction pipeline. Or Codex defines it locally in the extraction code and Claude Code mirrors it. Either way, the vocabulary must be identical.

**Priority**: CRITICAL — this is gap audit C1 + C2

---

# STAGE 4: RELATION EXTRACTION

## Current State
- Theory links and inter-article relations extracted with `claim_type=theory_link` or `claim_type=inter_article_relation`
- Relation types limited to `supports|explains|contradicts` plus subtypes
- No edge_type tagging

## Required Change

**Programs**: Extraction prompts + `src/services/table_to_claims.py`

**Change**: Every extracted relation gets an `edge_type` from the expanded taxonomy:

```python
class EdgeType(str, Enum):
    # Review/Synthesis edges
    INCLUDES_IN_SYNTHESIS = "INCLUDES_IN_SYNTHESIS"
    SYNTHESIZES_AS = "SYNTHESIZES_AS"
    IDENTIFIES_MODERATOR = "IDENTIFIES_MODERATOR"
    CONTRADICTS_SYNTHESIS = "CONTRADICTS_SYNTHESIS"
    # Theoretical edges
    THEORETICALLY_PREDICTS = "THEORETICALLY_PREDICTS"
    CONFIRMS_PREDICTION = "CONFIRMS_PREDICTION"
    DISCONFIRMS_PREDICTION = "DISCONFIRMS_PREDICTION"
    PROPOSES_MECHANISM = "PROPOSES_MECHANISM"
    SUBSUMES_THEORY = "SUBSUMES_THEORY"
    THEORY_TENSION = "THEORY_TENSION"
    # Conceptual edges
    DEFINES_CONSTRUCT = "DEFINES_CONSTRUCT"
    MUST_DISTINGUISH = "MUST_DISTINGUISH"
    REDEFINES = "REDEFINES"
    ORGANIZES = "ORGANIZES"
    # Critique edges
    CHALLENGES_METHOD = "CHALLENGES_METHOD"
    CHALLENGES_PARADIGM = "CHALLENGES_PARADIGM"
    PROPOSES_BETTER_METHOD = "PROPOSES_BETTER_METHOD"
    # Attribution edges
    ATTRIBUTES_FINDING = "ATTRIBUTES_FINDING"
    INTERPRETS_AS = "INTERPRETS_AS"
    # Existing (retained)
    COHERENCE_SUPPORT = "COHERENCE_SUPPORT"
    COHERENCE_TENSION = "COHERENCE_TENSION"
    ARGUMENTATIVE_SUPPORT = "ARGUMENTATIVE_SUPPORT"
    ARGUMENTATIVE_CHALLENGE = "ARGUMENTATIVE_CHALLENGE"
    GENERALIZABILITY_WARRANT = "GENERALIZABILITY_WARRANT"
```

**Who**: Codex (tagging) + Claude Code (enum definition + validation)

**Priority**: HIGH

---

# STAGE 5: WEB INGESTION

## Current State
- `src/services/extraction_to_web.py` expects empirical-only fields
- Line ~646: looks for `statement`
- Line ~649: looks for `ae_confidence`
- Lines ~648/650/651: looks for `statistics`, `constructs`, `study`
- Only creates one kind of node

## Required Change

**Program**: `src/services/extraction_to_web.py`

**Change**: Node-type-aware ingestion with different processing paths:

```python
def ingest_claim(claim_data):
    node_type = claim_data["node_type"]

    if node_type == "EMPIRICAL_FINDING":
        return ingest_empirical(claim_data)        # existing path
    elif node_type == "SYNTHESIS_CONCLUSION":
        return ingest_synthesis(claim_data)         # NEW
    elif node_type == "THEORETICAL_PROPOSITION":
        return ingest_theoretical(claim_data)       # NEW
    elif node_type == "DERIVED_HYPOTHESIS":
        return ingest_hypothesis(claim_data)        # NEW
    elif node_type == "CONCEPTUAL_DEFINITION":
        return ingest_definition(claim_data)        # NEW (feeds taxonomy)
    elif node_type == "CONCEPTUAL_CONSTRAINT":
        return ingest_constraint(claim_data)        # NEW (feeds validation)
    elif node_type == "EXPERT_SYNTHESIS":
        return ingest_expert_synthesis(claim_data)  # NEW
    elif node_type == "METHODOLOGICAL_CRITIQUE":
        return ingest_critique(claim_data)          # NEW (propagates to method registry)
    elif node_type == "KNOWLEDGE_GAP":
        return ingest_gap(claim_data)               # NEW (feeds VOI)
    elif node_type == "FRAMEWORK_STRUCTURE":
        return ingest_framework(claim_data)         # NEW (feeds taxonomy)
    elif node_type == "BRIDGE_WARRANT":
        return ingest_bridge_warrant(claim_data)    # existing path, now more sources
    else:
        log.warning(f"Unknown node_type: {node_type}")
        return ingest_fallback(claim_data)
```

Each `ingest_*` function:
- Creates the appropriate node type in the web
- Validates that required fields for that type are present
- Applies the entrenchment computation specific to that type (spec §4.2)
- Creates edges as appropriate

**Who**: Claude Code (owns extraction_to_web.py and web architecture)

**Priority**: CRITICAL — this is the bottleneck where everything converges

---

# STAGE 6: ENTRENCHMENT COMPUTATION

## Current State
- All nodes use the same entrenchment computation (coherence-based constraint satisfaction)

## Required Change

**Program**: Wherever entrenchment is computed (likely `src/epistemic/` modules)

**Change**: Per-type entrenchment with different dynamics:

| Node Type | Key New Dynamics |
|---|---|
| THEORETICAL_PROPOSITION | Asymmetric Popperian: disconfirmation -0.10 vs confirmation +0.05 |
| DERIVED_HYPOTHESIS | Upward propagation to parent theory on confirm/disconfirm |
| SYNTHESIS_CONCLUSION | Floor rule: entrenchment ≥ median of included studies |
| METHODOLOGICAL_CRITIQUE | Propagation: cascades validity penalties to all studies using criticized method |
| EXPERT_SYNTHESIS | Discount: 0.7× weight relative to systematic synthesis |
| QUALITATIVE_FINDING | Ceiling: cannot raise causal claims above observational base rate |
| CONCEPTUAL_DEFINITION | Indirect: affects construct matching, not coherence directly |

**Who**: Claude Code (Sprint 6b)

**Priority**: HIGH but can follow the basic ingestion pipeline (Stage 5)

---

# STAGE 7: METHOD REGISTRY INTEGRATION

## Current State
- Method registry is a static data structure (Sprint 4b)
- METHODOLOGICAL_CRITIQUE nodes don't exist yet, so no update mechanism

## Required Change

**Programs**: `src/methods/registry.py` + new `src/methods/critique_integration.py`

**Change**: When a METHODOLOGICAL_CRITIQUE is ingested:
1. Identify which method(s) it targets (match against registry)
2. Update the method's `confounds` list
3. Adjust `construct_validity_map` scores downward for affected constructs
4. Flag all existing claims that used the criticized method for re-scoring
5. Queue re-scoring (don't do it synchronously — could cascade widely)

```python
def apply_critique_to_registry(critique_node, registry):
    target_methods = critique_node.targets  # method_ids
    for method_id in target_methods:
        entry = registry.get(method_id)
        entry.confounds.append(critique_node.critique_content)
        for construct, score in entry.construct_validity_map.items():
            if construct in critique_node.affected_constructs:
                entry.construct_validity_map[construct] *= critique_node.severity_factor
        # Queue downstream re-scoring
        affected_claims = web.find_claims_using_method(method_id)
        rescore_queue.extend(affected_claims)
```

**Who**: Claude Code (Sprint 6b, depends on Sprint 4b method registry)

**Priority**: MEDIUM — high value but depends on method registry being stable

---

# STAGE 8: QUALITY GATES

## Current State
- `config/table_extraction_quality_thresholds.json` has empirical-centric thresholds
- `no_claims_rate <= 0.60` (i.e., tolerating 60% of papers producing nothing)

## Required Change

**Program**: `config/table_extraction_quality_thresholds.json` + `scripts/check_table_extraction_quality.py`

**Change**: Add non-empirical quality metrics and tighten thresholds:

```json
{
  "existing_gates": {
    "no_claims_rate": 0.25,
    "anchor_coverage": 0.90,
    "unresolved_environment_rate": 0.65,
    "unresolved_outcome_rate": 0.65,
    "relation_type_diversity": 8,
    "theory_link_paper_coverage": 0.60,
    "inter_article_paper_coverage": 0.60,
    "manual_review_backlog": 400
  },
  "new_gates": {
    "node_type_tag_rate": 0.95,
    "edge_type_tag_rate": 0.90,
    "theoretical_proposition_coverage": 0.80,
    "derived_hypothesis_per_theoretical_paper": 1,
    "opinion_evidence_separation_rate": 0.90,
    "field_name_v2_compliance": 1.00,
    "non_empirical_claim_rate": 0.30
  }
}
```

Key changes:
- `no_claims_rate` drops from 0.60 to **0.25** (once non-empirical extraction works, most papers should produce something)
- `relation_type_diversity` rises from 6 to **8** (more edge types available)
- `theory_link_paper_coverage` rises from 0.40 to **0.60**
- New `non_empirical_claim_rate >= 0.30` — at least 30% of extracted claims should be non-empirical types (if the corpus is representative, roughly half the papers are non-empirical)

**Who**: Codex (owns quality gate scripts) — but thresholds should be discussed with David before changing

**Priority**: MEDIUM — update after extraction changes are stable

---

# STAGE 9: TAXONOMY / LOOKUP UPDATES

## Current State
- `outcome_lookup.json` and `environment_lookup.json` are static files
- New terms from conceptual framework papers don't update them

## Required Change

**Programs**: New `src/taxonomy/updater.py` or extend existing lookup logic

**Change**: When CONCEPTUAL_DEFINITION nodes are ingested:
1. Check if term already exists in lookup tables
2. If new: add with canonical_id, definition, source paper
3. If redefinition: create REDEFINES edge, flag for review
4. When CONCEPTUAL_CONSTRAINT nodes are ingested: add validation rule to extraction pipeline

**Who**: Claude Code (new module) or Codex (if simpler script-level)

**Priority**: LOW initially — can be manual at first, automated later

---

# STAGE 10: WORKFLOW SEQUENCING

## Current State
```
PDF → classify (11 buckets) → extract (empirical template) → table_to_claims → extraction_to_web → web
```

## Required Workflow
```
PDF → classify (15 families) → select prompt (family-specific) → extract (typed output)
    → validate (ae.claim.v2 / ae.edge.v2 compliance)
    → table_to_claims (with node_type + edge_type)
    → extraction_to_web (node-type-aware routing)
    → web (typed nodes + typed edges)
    → post-ingestion hooks:
        → if METHODOLOGICAL_CRITIQUE: update method registry + queue re-scoring
        → if CONCEPTUAL_DEFINITION: update taxonomy lookups
        → if DERIVED_HYPOTHESIS: link to parent theory + check for existing confirming/disconfirming evidence
        → if SYNTHESIS_CONCLUSION: link to included studies + compute floor entrenchment
        → if KNOWLEDGE_GAP: add to VOI search queue
```

New validation step between extraction and ingestion catches:
- Missing node_type → reject
- Missing required fields for that node_type → reject or flag
- edge_type incompatible with source/target node types → reject
- Field name violations (claim_text instead of statement) → reject

**Who**: Both. Codex handles extraction-side (classify → extract → validate → table_to_claims). Claude Code handles ingestion-side (extraction_to_web → web → post-ingestion hooks).

---

# STAGE 11: PRODUCTION WORKER

## Current State
```bash
python3 scripts/run_realtime_production_worker.py --poll-seconds 20 --intake-limit 40 --pdf-batch-size 80 --pdf-workers 6 --quality-gate
```

## Required Change

**Program**: `scripts/run_realtime_production_worker.py`

The worker needs to:
1. Pass article_family through the pipeline (not just PDF bytes)
2. Select family-specific extraction prompt
3. Validate output against ae.claim.v2 before forwarding to web
4. Run updated quality gate with new thresholds
5. Log node_type distribution per batch (operational visibility)

Add monitoring output:
```
Batch 42: 80 PDFs processed
  empirical_v2: 38 (142 claims)
  theoretical: 12 (67 propositions, 23 hypotheses)
  narrative_review: 9 (41 syntheses, 18 attributed findings)
  meta_analysis: 4 (8 pooled effects, 4 moderator analyses)
  systematic_review: 6 (19 synthesis conclusions, 7 gaps)
  thought_piece: 5 (12 expert opinions, 3 critiques)
  conceptual_framework: 3 (11 definitions, 5 constraints)
  case_study: 2 (6 findings)
  interview_study: 1 (4 themes)
  no_claims: 3 (3.8% — below 25% threshold ✓)
  quality gate: PASS
```

**Who**: Codex

---

# IMPLEMENTATION ORDER

| Phase | What | Who | Depends On | Duration |
|---|---|---|---|---|
| **Phase 1** | 15-family classifier | Codex | nothing | 3–5 days |
| **Phase 2** | Family-specific extraction prompts (theoretical + meta-analysis + systematic review first) | Codex | Phase 1 | 1–2 weeks |
| **Phase 3** | table_to_claims field rename + node_type/edge_type tagging | Codex | Phase 2 | 3–5 days |
| **Phase 4** | NodeType + EdgeType enums in schema.py | Claude Code | Sprint 1 complete | 2 days |
| **Phase 5** | extraction_to_web node-type-aware routing | Claude Code | Phase 3 + Phase 4 | 1 week |
| **Phase 6** | Per-type entrenchment dynamics | Claude Code | Phase 5 | 2 weeks |
| **Phase 7** | Method registry critique integration | Claude Code | Phase 6 + Sprint 4b | 1 week |
| **Phase 8** | Quality gate updates | Codex | Phase 3 stable | 2 days |
| **Phase 9** | Taxonomy/lookup auto-update | Claude Code or Codex | Phase 5 | 1 week |
| **Phase 10** | Production worker updates | Codex | Phase 3 + Phase 8 | 3 days |
| **Phase 11** | Integration testing (Joye & Dewitte walkthrough) | Both | Phase 6 | 1 week |

**Critical path**: Phase 1 → 2 → 3 → 5 → 6

**Parallel track**: Phase 4 can start immediately (Claude Code, just enum definitions)

**Total estimated duration**: 6–8 weeks, overlapping with existing sprint work

---

# WHAT SUCCESS LOOKS LIKE

Before this work:
- ~50% of PDFs produce no claims
- Web is empirical-findings-only
- No theory nodes, no review structure, no methodological challenges
- BN has nodes but shaky edge justification

After this work:
- ~95% of PDFs produce typed claims
- Web has theoretical skeleton + empirical flesh + review connective tissue + methodological immune system
- Theories gain/lose entrenchment based on prediction accuracy
- Methodological critiques cascade validity penalties
- Conceptual distinctions prevent construct conflation
- Reviews provide cross-study connections the system couldn't infer
- BN edges have theoretical justification from THEORETICAL_PROPOSITION + PROPOSES_MECHANISM nodes

The no_claims_rate drops from ~0.50 to ~0.05. The web becomes a genuine web of belief rather than a collection of isolated empirical beads.

---

**END OF CHANGE DOCUMENT**
