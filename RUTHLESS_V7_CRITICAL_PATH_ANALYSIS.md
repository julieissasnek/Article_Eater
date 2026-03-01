# RUTHLESS V7 — Critical Path Analysis

*Quick reference for blocking issues that prevent system functionality*

---

## The 5 Critical Path Breaks (Why The System Doesn't Work)

### Break 1: Extraction → Theory Linking (BROKEN)
```
Extraction produces: { antecedent, consequent, direction, theory_commitments: [] }
                                                          ↑ ALWAYS EMPTY

Expected: theory_commitments = ["Attention Restoration Theory", "Stress Recovery"]
Actual:   theory_commitments = []

Where: src/extraction/batch_extract.py line 64
Why: Pattern matching (regex) instead of semantic extraction
Evidence: 54 findings tested, 0 have theory links
Impact: Web of Belief never updates, coherence never recomputes, User 1/5 get no value
```

### Break 2: Theory Link → BN Update (MISSING)
```
Expected pipeline:
  Finding has theory link → Web.add_belief() → Coherence recomputes → User can query

Actual pipeline:
  Finding stored in JSON → (nothing) → BN ignored → User can't see connection

Missing: src/services/extraction_to_web.py
Missing: Trigger mechanism in extraction pipeline
Missing: BN update after extraction completes

Impact: System is static — new papers don't change knowledge base
User Impact: User 2/4/5 get stale answers
```

### Break 3: Query → Answer (REQUIRES LLM)
```
Expected:
  User: "theories that explain ceiling height"
  System: Searches index, finds relevant findings, returns ranked list

Actual:
  User: "theories that explain ceiling height"
  System: "Please connect an LLM (gemini-2.5-flash recommended)"

Why: No semantic search, findings not indexed, query classification fails
Evidence: Test query falls through to arbitrary_qa_handler line 161-165
Impact: 95% of queries require external LLM
User Impact: User 1 can't run own queries, must use API keys
```

### Break 4: Extraction Field Quality (NOT ENFORCED)
```
Current validation score penalty:
  CRITICAL violation:    -0.25 (1 critical = game over)
  ERROR violation:       -0.15 (hard blocker)
  WARNING violation:     -0.05 (minor issue)

Reality:
  Test article: 164 violations (mostly WARNINGS)
  Score: 0.62/1.0 (PASSING)

Example violations that don't block:
  - theory_commitments is empty
  - instruments_used is empty
  - effect_size is null
  - sample_size is missing

Why these are rated WARNING not ERROR:
  src/qa/extraction_field_validator.py assumes "we'll add these later"

Impact: Low-quality data flows through to users
User Impact: User 1/3 get incomplete/unreliable data
```

### Break 5: Cultural Personalization (DESIGNED BUT DISCONNECTED)
```
Files exist:
  data/calibration/ch-1-harmony-comfort-factors.json
  data/calibration/ch-2-*.json
  ... ch-7-*.json

CVA code exists:
  src/services/cva_constraint.py
  src/services/cva_valuation.py
  src/services/cva_constraint_engine.py

But:
  ✗ router.route_query(query) has no culture parameter
  ✗ arbitrary_qa_handler.answer(question) has no culture parameter
  ✗ No code calls CVA in response generation
  ✗ Calibration files are orphaned

Impact: System produces culturally-monolithic answers
User Impact: User 5 (international context) gets Western defaults
```

---

## Data Quality Snapshot

Testing file: `data/extractions/10.1002_ad.2031.json` (54 findings)

| Field | Populated | Missing | % Empty |
|-------|-----------|---------|---------|
| antecedent | 54 | 0 | 0% |
| consequent | 54 | 0 | 0% |
| direction | 54 | 0 | 0% |
| **theory_commitments** | **0** | **54** | **100%** |
| **instruments_used** | **0** | **54** | **100%** |
| **effect_size** | 0 | 54 | 100% |
| sample_context | 2 | 52 | 96% |

**Conclusion**: Basic extraction works. Rich linking fields don't exist.

---

## Query Failure Analysis

### Test Query 1: "theories that explain ceiling height"
```
Step 1: route_query()
  → _classify_question() → "design_synthesis" (no match)

Step 2: molecule_lookup()
  → No molecule contains "ceiling height"
  → Cache miss

Step 3: argument_handler.handle_query()
  → Can't match argumentative structure
  → Returns None

Step 4: arbitrary_qa_handler.answer()
  → No question pattern matches
  → Falls through to AI routing

Step 5: Fallback
  → Returns prompt template
  → Says: "connect an LLM to get full answer"

Result: FAILED — requires external LLM
```

### Test Query 2: "show me all theories"
```
Step 1: route_query()
  → _classify_question() → "catalog_theories" (MATCH!)

Step 2: arbitrary_qa_handler.answer()
  → format_theories_catalog() called
  → Returns list of 6 T1 + 8 T1.5 + 18 T2 items

Step 3: read_next enrichment
  → Adds suggestions

Result: SUCCESS — works for catalog queries
Note: Only works for broad catalog queries, not specific evidence queries
```

---

## What Happens When a New Paper is Extracted

1. **Day 0**: Paper PDF dropped, LLM extraction runs
   - Result: `data/extractions/NEW_PAPER.json` with 50+ findings

2. **Validation**: extraction_field_validator.validate_article()
   - Expected: Check quality, gate on issues
   - Actual: Scores 0.62, warnings logged, no blocking
   - Finding: Passes through despite theory_commitments = empty

3. **Integration**: Should update Web of Belief
   - Expected: Add findings to coherent web, recompute credence/coherence
   - Actual: No integration pipeline exists
   - Finding: New paper is invisible to knowledge base

4. **User Query**: User asks about topic covered by new paper
   - Expected: New paper shows up in results
   - Actual: New paper irrelevant (not in web, not indexed)
   - Finding: User gets stale answers

5. **Overseer Health**: Should report status
   - Expected: Dashboard shows "NEW extraction integrated, 2 theory links found"
   - Actual: Reflex logs events to JSONL, no dashboard
   - Finding: Admin can't see new paper arrived

---

## The 5 User Personas: Can They Use This System?

| User | Primary Need | Can System Deliver? | Why Not? |
|------|--------------|-------------------|---------|
| **User 1: Psych Researcher** | "Show me findings with effect sizes + instruments" | NO | effect_size=null, instruments_used=[], requires LLM for query |
| **User 2: Architect (Hospital)** | "Evidence-based design guidelines with confidence" | NO | No confidence calculation, no healthcare templates, requires LLM |
| **User 3: Meta-Analyst** | "PANAS data: studies, n, p-values, structured export" | NO | No p_value field, instruments_used=[], no export format |
| **User 4: Policy Maker** | "Strongest evidence for workplace design, plain language" | NO | No evidence ranking, no confidence labels, requires LLM |
| **User 5: PhD Student** | "Theories mapping, literature landscape" | PARTIAL | Can list theories but can't link to findings (no theory_commitments) |

**System Maturity**: Demo-ready, not user-ready

---

## Files Where Fixes Are Needed

### High Impact (Blocks Multiple Users)

| File | Issue | Fix |
|------|-------|-----|
| `src/extraction/batch_extract.py` | theory_commitments always empty | Implement semantic theory extraction (NLP or LLM-assisted) |
| `src/extraction/batch_extract.py` | instruments_used always empty | Add entity recognition for measurement instruments |
| `src/qa/router.py` | No semantic search | Implement vector indexing + similarity search |
| `src/services/` | No extraction_to_web.py | Create integration pipeline for BN updates |
| `src/services/arbitrary_qa_handler.py` | No evidence ranking | Add credence/coherence calculation to responses |

### Medium Impact (Degrades User Experience)

| File | Issue | Fix |
|------|-------|-----|
| `src/qa/extraction_field_validator.py` | Penalties too weak | Elevate theory/instrument violations to ERROR/CRITICAL |
| `src/qa/reflex_system.py` | fix() is stub | Implement auto-repair rules |
| `data/calibration/ch*.json` | Not used by system | Add culture parameter to query API, call CVA in handlers |
| `frontend/` | No health dashboard | Build dashboard consuming reflex_events |

### Low Impact (Missing Features)

| File | Issue | Fix |
|------|-------|-----|
| `src/services/` | No export format | Implement CSV/JSON export for meta-analysis |
| `src/extraction/batch_extract.py` | No p_value extraction | Add statistical result parsing |
| `src/qa/app.py` | No sample_size field | Clean up sample_context parsing |

---

## Time to Fix (Estimates)

**Critical Path (Unblock Core Functionality)**
- Theory extraction: 2-3 weeks (requires NLP model or LLM integration)
- Extraction-to-BN pipeline: 1 week
- Semantic search: 2-3 weeks
- Total: 5-7 weeks to restore core system value

**Feature Completion (Full User Personas)**
- Data quality improvements: 2 weeks
- Evidence ranking: 1 week
- Cultural calibration wiring: 1 week
- Dashboard: 1 week
- Export formats: 1 week
- Total: 6 weeks to match design spec

**Grand Total to "User Ready"**: 11-13 weeks of focused development

---

## Severity Assessment

| Severity | Count | Impact |
|----------|-------|--------|
| **CRITICAL** (blocks all users) | 4 | Cannot extract theories, cannot query, cannot personalize, requires external LLM |
| **HIGH** (blocks specific users) | 4 | User 1-5 each blocked by something different |
| **MEDIUM** (degrades experience) | 5 | Low data quality, no auto-fix, no health dashboard |
| **LOW** (missing features) | 6 | Nice-to-have exports and formats |

---

## Next Steps

1. **Immediate (This Week)**:
   - Confirm theory_commitments extraction approach
   - Plan extraction-to-BN integration
   - Identify theory extraction method (rule-based? LLM-assisted? Manual?)

2. **Short Term (Sprint)**:
   - Implement semantic search baseline
   - Fix validation penalty weights
   - Create extraction-to-BN pipeline

3. **Medium Term (Month)**:
   - Populate theory links across corpus
   - Add instruments and effect sizes
   - Wire cultural calibration
   - Build health dashboard

4. **Validation**:
   - Re-test 5 user personas
   - Re-run end-to-end scenarios
   - Measure query success rate without LLM fallback
   - Measure BN update frequency

