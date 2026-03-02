# Vocabulary Mismatch Investigation - Document Index

**Completed**: 2026-03-01
**Topic**: Template Relevance Matcher Performance Gap (86.9% raw text vs. 29.9% DB fields)

---

## Quick Reference

| Document | Purpose | Audience | Length |
|----------|---------|----------|--------|
| **VOCABULARY_MISMATCH_SUMMARY.txt** | One-page executive summary | Everyone | 2 pages |
| **VOCABULARY_MISMATCH_REPORT_2026-03-01.md** | Complete technical analysis with examples | Engineers, researchers | 15 pages |
| **NORMALIZATION_STRATEGY_SPEC.md** | Implementation specification for solution | Developers | 20 pages |
| **INVESTIGATION_INDEX.md** | This document | Navigation | - |

---

## Document Descriptions

### 1. VOCABULARY_MISMATCH_SUMMARY.txt

**Best for**: Quick understanding in 5-10 minutes

Contains:
- Problem statement (57-point performance drop)
- Root cause (complete vocabulary disjunction)
- Quantitative gap analysis (0% overlap)
- Why raw text works (86.9%)
- Why DB fields fail (29.9%)
- Recommended solution overview
- Effort estimate

**Key findings**:
- 0 template input_terms match 442 environment_ids
- 0 template output_terms match 30 outcome_ids
- Missing infrastructure for any normalization
- Extraction-time normalization is most efficient solution

**Read this first** if you only have 10 minutes.

---

### 2. VOCABULARY_MISMATCH_REPORT_2026-03-01.md

**Best for**: Deep understanding and decision-making

Contains 7 major sections:

1. **Executive Summary** (1 page)
   - 57-point performance cliff
   - Zero vocabulary overlap
   - Two independent standards

2. **Quantitative Gap Analysis** (2 pages)
   - Template vocabulary breakdown (51 input, 115 output terms)
   - DB vocabulary breakdown (442 environment_ids, 30 outcome_ids)
   - Exact-match overlap statistics (0%)
   - Directional gaps (both directions)

3. **Root Cause Analysis** (3 pages)
   - Two vocabularies with different standards
   - Template terms (natural language domain terminology)
   - DB terms (hierarchical canonical IDs)
   - Why raw text achieves 86.9% (content tokenization)
   - Why DB fields achieve 29.9% (no token overlap)
   - Missing infrastructure (no mapping layers)

4. **Detailed Examples** (2 pages)
   - Environment mismatches (ceiling_height vs env.ae.high_ceiling)
   - Outcome mismatches (aesthetic_emotion vs out.affect.mood)
   - Why bridges cannot scale

5. **Normalization Strategies** (2 pages)
   - Option A: Reverse bridge (DB → Template)
   - Option B: Extraction-time normalization ⭐
   - Option C: Template realignment (not recommended)
   - Pros/cons/effort estimates

6. **Findings Summary** (1 page)
   - Table of key findings with evidence

7. **Next Steps & Appendix** (2 pages)
   - Recommended implementation sequence
   - Bridge mechanism explanation

**Read this** to understand the problem completely and evaluate solution options.

---

### 3. NORMALIZATION_STRATEGY_SPEC.md

**Best for**: Implementation planning

Contains 5 components:

#### Component 1: Environment ID Normalizer (4 pages)
- Design specification for environment_id mapping
- Token-to-environment mapper with confidence scoring
- Ambiguity resolution strategy
- Testing approach with examples

#### Component 2: Outcome ID Normalizer (3 pages)
- Leverages existing outcome_lookup.json
- Multi-step resolution with fallback
- Subdomain mapping for specificity
- Testing approach with examples

#### Component 3: Augmented outcome_lookup.json (1 page)
- Enhancement to existing vocabulary file
- New compound_mappings and synonyms sections
- Example structure

#### Component 4: Integration Point (1 page)
- Where to apply normalization in pipeline
- How to handle multiple values (pipe-delimited)
- Optional confidence metadata storage

#### Component 5: Validation & Testing (2 pages)
- Test suite structure
- Coverage metrics (target: ≥90%)
- False positive rate (<5%)

**Implementation details**:
- 5-week implementation timeline
- Phased approach (Design → Core → Testing → Integration → Validation)
- Success criteria (≥75% coverage post-normalization)
- Risk mitigation strategies

**Read this** to plan the development work and understand technical approach.

---

## Key Data Points to Remember

### Vocabulary Sizes
- Template input_terms: **51**
- Template output_terms: **115**
- DB environment_ids: **442**
- DB outcome_ids: **30**
- **Overlap: 0%**

### Performance Gap
- Raw extraction text: **86.9% Tier2 coverage**
- DB field matching: **29.9% Tier2 coverage**
- **Performance cliff: 57 percentage points**

### Example Mismatch
```
Template expects:  "ceiling_height"
Database has:     "env.ae.high_ceiling"

Token overlap:     "ceiling" appears in both
But no matching:   Template seeks "ceiling_height" (normalized),
                   DB field is "env.ae.high_ceiling" (hierarchical)
```

### Root Cause
Two independent vocabulary systems were designed without a shared translation layer:
- **Templates**: Natural language domain terminology (expert-curated)
- **Database**: Hierarchical canonical IDs with prefixes (systematic)

### Solution
**Extraction-time normalization**: Map raw antecedent/consequent text → canonical IDs during ingestion.

**Effort**: 300-500 hours of design, implementation, and validation

**Expected outcome**: ≥75% Tier2 coverage (vs. 29.9% current)

---

## Recommended Reading Path

### For Quick Briefing (15 minutes)
1. VOCABULARY_MISMATCH_SUMMARY.txt (2 pages)
2. This index (sections: Vocabulary Sizes, Performance Gap, Root Cause, Solution)

### For Full Understanding (90 minutes)
1. VOCABULARY_MISMATCH_SUMMARY.txt
2. VOCABULARY_MISMATCH_REPORT_2026-03-01.md (Sections 1-2, 4, 6)

### For Implementation Planning (2-3 hours)
1. VOCABULARY_MISMATCH_SUMMARY.txt
2. VOCABULARY_MISMATCH_REPORT_2026-03-01.md (all sections)
3. NORMALIZATION_STRATEGY_SPEC.md (Components 1-2, Integration, Validation)

### For Development (ongoing)
1. NORMALIZATION_STRATEGY_SPEC.md (all sections)
2. Reference VOCABULARY_MISMATCH_REPORT_2026-03-01.md for examples and context
3. Use test cases in spec for validation

---

## Key Files Analyzed During Investigation

| File | Purpose | Finding |
|------|---------|---------|
| `src/services/finding_template_relevance.py` | Template matching logic | Matches against environment_id, outcome_id via ENV_BRIDGES + OUTCOME_BRIDGES (insufficient) |
| `data/templates/*.json` (166 files) | Template definitions | 51 input_terms, 115 output_terms extracted from causal_links |
| `data/web_persistence.db` | Belief storage | 4,888 beliefs; 442 environment_ids; 30 outcome_ids |
| `contracts/outcome_vocab/outcome_vocab.json` | Outcome vocabulary | Has domain structure but not hierarchical "out.cog.attention" format |
| `contracts/outcome_vocab/outcome_lookup.json` | Outcome lookup | Maps natural language (e.g., "cognitive") to domain abbr (e.g., "cog"), NOT full IDs |
| `data/extractions/*.json` | Extraction files | Contains antecedent/consequent raw text that achieves 86.9% coverage |

---

## Next Action Items

If approved to proceed with Extraction-Time Normalization:

1. **Define environment_id namespace** (Week 1)
   - What does each "env.*" prefix mean? (ae, complexity, cognitive, unresolved, etc.)
   - How do the 442 environment_ids relate to each other?
   - Create documentation of the namespace ontology

2. **Build token → environment_id mapper** (Week 2)
   - Initialize ENVIRONMENT_TOKEN_MAP with all 442 mappings
   - Design confidence scoring algorithm
   - Create test cases

3. **Build token → outcome_id mapper** (Week 2-3)
   - Extend outcome_lookup.json with compound mappings
   - Implement outcome_id_normalizer.py
   - Create test cases

4. **Validate against 4,888 beliefs** (Week 4)
   - Run normalizers on full dataset
   - Measure coverage, false positive rate, ambiguous cases
   - Identify failure modes

5. **Integrate into pipeline** (Week 5-6)
   - Wire normalizers into extraction ingestion
   - Deploy to test environment
   - Monitor performance metrics

6. **Validate template matcher improvement** (Week 7)
   - Re-run template matcher on normalized IDs
   - Target: ≥75% coverage (vs. 29.9% current)
   - Compare to raw-text baseline

---

## Questions to Resolve

1. **Namespace semantics**: What is the intended meaning of each "env.*" prefix?
   - env.ae.* (appears to be architectural elements)
   - env.complexity.* (appears to be spatial complexity measures)
   - env.cognitive.* (appears to be cognitive demands)
   - env.unresolved.* (appears to be unmapped/unknown categories)

2. **Multi-value handling**: Should a single belief support multiple environment_ids?
   - Current approach: Single field per belief
   - Proposed: Pipe-delimited (env1|env2) or JSON array in epistemic_v2
   - Impact on template matcher logic?

3. **Confidence thresholding**: What confidence threshold is acceptable?
   - Current proposal: 0.7 (skip below this)
   - Question: Better to include ambiguous cases and let template matcher decide?
   - Or be conservative and skip uncertain mappings?

4. **Backward compatibility**: Should existing beliefs be re-normalized?
   - Current proposal: Apply normalizer to all 4,888 beliefs during Phase 3
   - Impact: Will change existing environment_id and outcome_id values
   - Risk: Lose original values (should archive them)

5. **Coverage target**: Is ≥75% Tier2 coverage sufficient?
   - Current: 29.9%
   - Raw text baseline: 86.9%
   - Proposed: ≥75%
   - Question: Is 75% the right target or should we aim higher?

---

## Contact & Follow-Up

This investigation was conducted as **research only** — no files were modified.

To proceed with implementation:
1. Review the three documents above
2. Resolve the questions in the "Questions to Resolve" section
3. Approve the Extraction-Time Normalization approach (or choose alternative)
4. Allocate resources for Phase 1 (Design & Mapping)

---

**Investigation completed**: 2026-03-01 17:45 UTC
**Status**: RESEARCH / AWAITING DECISION
