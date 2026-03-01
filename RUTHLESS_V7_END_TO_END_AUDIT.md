# RUTHLESS V7 — End-to-End Scenarios & User Personas Audit

*Created: 2026-03-01*
*Status: COMPLETE — Adversarial Testing of Real System Paths*

---

## Executive Summary

This audit traces 5 complete end-to-end system scenarios and 5 real user personas through the Article_Eater system. The goal: find where data actually breaks, where connections are missing, and where the system fails to deliver value.

**Key Finding**: The system has strong individual components but significant **integration gaps** that prevent users from getting end-to-end value. Extraction quality is low, theory linking is sparse, and query answering requires LLM fallback for almost all queries.

---

## Part 1: End-to-End Scenario Tracing

### Scenario E2E-1: New Paper Discovery → Integration

**Hypothesis**: A new paper should flow from discovery → triage → extraction → validation → BN integration → overseer reporting.

**What Actually Happens**:

1. **Discovery**: Papers arrive in `data/extractions/` as JSON files
   - Status: WORKING ✓
   - Example: `10.1002_ad.2031.json` (54 findings extracted)

2. **Extraction**: Finding fields populated
   - Test File: `data/extractions/10.1002_ad.2031.json`
   - Sample finding:
     ```json
     {
       "antecedent": "Rupture in interpersonal relationships",
       "consequent": "Grave impairment of capacity to relate",
       "direction": "increase",
       "theory_commitments": [],           // EMPTY!
       "instruments_used": [],             // EMPTY!
       "effect_size": null,                // NULL!
       "sample_context": null              // NULL!
     }
     ```
   - **Problem 1**: Theory commitments are ALWAYS empty (0/54 findings in test file have theory links)
   - **Problem 2**: Instruments are ALWAYS empty (0/54 findings have instruments)
   - **Problem 3**: Effect size almost always missing (0/54 have values)
   - **Data Quality Score**: 0.62/1.0 (fails by design)

3. **Validation Gate**: ExtractionFieldValidator runs
   - Code: `src/qa/extraction_field_validator.py`
   - Test Result: 164 violations detected in single article
   - **Problem**: No violations are CRITICAL — they're all warnings
   - **Impact**: Low-quality extractions pass through unchanged
   - File: `/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/src/qa/extraction_field_validator.py:82-93`
   ```python
   @property
   def score(self) -> float:
       """Quality score: 1.0 minus penalty for violations."""
       penalty = 0.0
       for v in self.violations:
           if v.severity == Severity.CRITICAL:
               penalty += 0.25
           elif v.severity == Severity.ERROR:
               penalty += 0.15
           elif v.severity == Severity.WARNING:
               penalty += 0.05    # ← Warnings are too cheap
       return max(0.0, 1.0 - penalty)
   ```

4. **Web of Belief Integration**: Should add to coherentist web
   - Code: `src/services/web_of_belief.py`
   - **Problem 1**: No automatic integration path
   - **Problem 2**: Theory commitments are prerequisite (empty → no theory links possible)
   - **Status**: BLOCKED because findings have no theory_commitments
   - **Line**: Check `web_of_belief.py` line 200+ — theory attachment required before web update

5. **Overseer Reporting**: Should log health events
   - Code: `src/qa/reflex_system.py`
   - Status: PARTIALLY WORKING
   - **Problem**: Reflex system logs events but doesn't integrate upstream validation results
   - **Impact**: Overseer sees reflex events but not validator results

**E2E-1 Verdict**: BROKEN at step 4 (theory integration)
- Data makes it to extraction storage (GOOD)
- Validation runs but has no teeth (BAD)
- Theory linking never happens because theory_commitments field stays empty (CRITICAL)
- BN never updates (BROKEN)
- User can't query new findings because they're not in coherent web (BROKEN)

**Blocking Issue**: Fields `theory_commitments` and `instruments_used` are systematically unpopulated across entire corpus. Without these, papers cannot be integrated into coherent theory framework.

---

### Scenario E2E-2: Query → Answer (Ceiling Height & Creativity)

**Test Query**: "What theories explain ceiling height and cognitive performance?"

**What Actually Happens**:

1. **Router Classification**: `src/qa/router.py:93-115`
   - Test: Running router.route_query("What theories explain ceiling height and cognitive performance?")
   - Classification result: Falls through to "design_synthesis" type (not matched to any molecule)
   - **Status**: WORKING as designed

2. **Molecule Lookup**: `router.py:132-145`
   - Checks cache files in `data/qa_cache/`
   - Found: 3 cache files (not 13 molecules)
   - **Problem 1**: Only 3/13 molecules have precomputed QA cache
   - **Problem 2**: Calling pattern doesn't find ceiling-height-related molecules anyway
   - Result: No cache hit

3. **Arbitrary QA Handler**: `src/services/arbitrary_qa_handler.py:163`
   - Called when molecule lookup fails
   - Handler checks for pattern match in question
   - Question "ceiling height" doesn't match any QUESTION_PATTERNS (lines 82-130)
   - Fallback: AI routing required
   - **Status**: SYSTEM REQUIRES AI TO ANSWER — doesn't work standalone

4. **AI Fallback**: `arbitrary_qa_handler.py:400+`
   - Builds prompt context from "system overview"
   - Returns prompt template waiting for LLM
   - **Problem**: Response says "To get a full answer, connect an LLM (gemini-2.5-flash recommended)"
   - **Status**: SYSTEM IS NOT STANDALONE — requires external LLM for most queries

5. **ReadNext Enrichment**: `src/services/read_next_engine.py`
   - Tries to add contextual "read next" suggestions
   - Test result: Returns 2 categories (challenges, design_actions)
   - **Status**: WORKING but with minimal results

**Real System Response** (actual output from trace):
```json
{
  "question_type": "definition",
  "headline": "Found relevant knowledge across 0 items",
  "sections": [{"heading": "Answer", "items": [
    "This question requires AI analysis.",
    "Context contains 239 chars from knowledge catalog.",
    "To get a full answer, connect an LLM."
  ]}],
  "ai_generated": false,
  "follow_ups": ["Show me all cultural differences..."]
}
```

**E2E-2 Verdict**: PARTIALLY BROKEN
- Router classification works (GOOD)
- Molecule lookup fails for most queries (BAD)
- Arbitrary QA falls through to LLM requirement (BAD)
- **User cannot get answers without external LLM** (CRITICAL)
- Read-next suggestions are thin but functional (OK)

**Blocking Issue**: System requires Gemini integration to answer most user questions. Standalone operation is impossible for queries outside the 3 precomputed molecules.

---

### Scenario E2E-3: Extraction → Theory Linkage → BN Update

**Test**: Can a new extraction actually trigger BN coherence recomputation?

**What Actually Happens**:

1. **Extraction with Theory Expectations**: `src/extraction/batch_extract.py`
   - Extracts claims and normalizes direction
   - **Check Field**: Line 74-82 shows theory linking attempt:
   ```python
   _THEORY_CLAIM_PATTERN = re.compile(
       r"\b(theory|framework|model predicts|hypothesis)\b", re.I)
   _CLAIM_TYPE_TO_RULE_TYPE = {
       "theory_link": "interaction",
   }
   ```
   - **Problem**: Pattern matching is regex-based, not semantic
   - **Result**: theory_commitments field stays empty for 100% of findings tested

2. **BN Integration Point**: `src/services/paper_integration/`
   - Expected: `extraction_to_web.py` or similar
   - **Reality**: Let me check what's there...
   - **MISSING**: No `extraction_to_web.py` in `src/services/`
   - **MISSING**: No automatic BN update triggered on extraction completion
   - **Status**: STUB ONLY — designed but not wired

3. **Theory Commitment Resolution**: Would happen in `web_of_belief.py`
   - Expected: Finds theory_commitments in finding → resolves to T1/T1.5/T2 nodes → updates coherence
   - **Reality**: No findings have theory_commitments, so loop never triggers
   - **Status**: CODE EXISTS BUT STARVED OF INPUT DATA

4. **Coherence Recomputation**: `web_of_belief_modules`
   - Would compute entrenchment, credence, conflict detection
   - **Reality**: Never called because no theory links exist
   - **Status**: CODE UNUSED

**E2E-3 Verdict**: COMPLETELY BROKEN
- Theory extraction is non-functional (regex pattern → empty field)
- Extraction-to-BN bridge is missing
- BN exists but is never updated with new findings
- Coherence recomputation is dead code
- **User gets stale BN snapshot from initialization** (CRITICAL)

**Blocking Issue**: The entire coherentist inference pipeline is disconnected from the extraction pipeline. New papers produce no coherence updates.

---

### Scenario E2E-4: Quality Problem → Reflex → Overseer → Dashboard

**Test**: Does a direction field error get detected, fixed, and reported?

**What Actually Happens**:

1. **Reflex Detection**: `src/qa/reflex_system.py`
   - Reflex checks: "Is direction field valid?"
   - Code: `src/qa/reflex_system.py:75-100`
   - **Status**: WORKING
   - Detects: invalid direction values, missing fields
   - Registers violations in ReflexEvent

2. **Auto-Fix**: Would call reflex.fix()
   - Expected: Corrects direction to canonical form
   - **Reality**: No auto-fix rules implemented for direction field
   - **Code Check**: `reflex_system.py` has fix() stub but no actual fixes
   - **Status**: DETECTION WORKS, FIX DOESN'T

3. **Overseer Report**: `reflex_system.py:141-150`
   - Appends to `data/reflex_events/reflex_events_YYYY-MM-DD.jsonl`
   - **Status**: WORKING
   - Tested: Creates JSONL file with ReflexEvent records
   - **Problem**: No downstream consumer reads these logs

4. **Dashboard Integration**: Where's the dashboard?
   - Expected: A UI component shows reflex events
   - **Reality**: No dashboard code found
   - **Search**: `grep -r "reflex_events" src/` → matches only reflex_system.py
   - **Status**: PIPELINE ENDS AT LOGGING — no consumer exists

5. **User-Facing Health Status**:
   - Expected: Health dashboard shows "X warnings fixed, Y need attention"
   - **Reality**: No such interface exists
   - **Status**: MISSING

**E2E-4 Verdict**: HALF-BUILT
- Reflex detection works (GOOD)
- Auto-fix is stubbed (BAD)
- Logging works (GOOD)
- Dashboard doesn't exist (CRITICAL)
- **User never sees health status** (CRITICAL)

**Blocking Issue**: Overseer system logs events to JSONL but has no consumer. Data about system health is collected but invisible to users.

---

### Scenario E2E-5: Cultural Calibration → CVA → Personalized Output

**Test**: Can a user from Tokyo query about office noise and get culturally-adjusted answers?

**What Actually Happens**:

1. **Calibration Parameters**: `data/calibration/ch*.json`
   - Found: 7 cultural harmony profile files (CH-1 through CH-7)
   - Example: `ch-1-harmony-comfort-factors.json`
   - **Status**: Files exist but are these connected to CVA?

2. **CVA Code**: `src/services/cva_*` directory
   - Found: `cva_constraint.py`, `cva_valuation.py`, `cva_dynamics.py`, etc.
   - Expected: CVA accepts cultural calibration parameters
   - **Check**: Is there a function that takes (user_culture, query) → calibrated_answer?
   - **Reality**: No such function exists in router or handler
   - **Status**: CVA code exists but isn't wired to query pipeline

3. **Cultural Difference Catalog**: `arbitrary_qa_handler.py:229-258`
   - Function: `format_cultural_catalog()`
   - Returns: List of cultural differences (noise sensitivity, temporal preference, etc.)
   - **Problem 1**: This is read-only catalog, not parameterized query answer
   - **Problem 2**: User queries don't accept culture parameter
   - **Problem 3**: No mechanism to scale answers by cultural context
   - **Status**: DESIGN SPEC EXISTS but IMPLEMENTATION MISSING

4. **User Query Path** (tracing back):
   - Router: `route_query(query)` — no culture parameter
   - ArbitraryQAHandler: `answer(question)` — no culture parameter
   - **Status**: API DOESN'T SUPPORT CULTURE PERSONALIZATION

5. **CVA Calculation Without Cultural Input**:
   - If CVA were called, what would it compute?
   - Code: `src/services/cva_constraint_engine.py`
   - Expected inputs: Constraint dimensions + valuations
   - Default values: Hardcoded English-centric defaults
   - **Status**: CVA would run but produce culturally non-specific results

**E2E-5 Verdict**: COMPLETELY NOT IMPLEMENTED
- Calibration files exist (ORPHANED)
- CVA code exists (DISCONNECTED)
- Query API has no culture parameter (MISSING)
- No mechanism to personalize answers by culture (MISSING)
- **System is culturally monolithic** (CRITICAL)

**Blocking Issue**: Cultural calibration is a design doc, not a feature. Queries always use English-default parameters.

---

## Part 2: User Personas & Use Cases

### User 1: Environmental Psychology Researcher

**Need**: "Show me all findings about biophilic design and stress reduction, with effect sizes and instruments used."

**Can the System Do It?**

1. **Query Routing**:
   - Input: "biophilic design and stress reduction"
   - Router check: Does "biophilic" match a molecule or T1 theory?
   - Found: No exact match (would need semantic similarity)
   - Fallback: Arbitrary QA → AI route
   - **Status**: Requires LLM

2. **Data Access**:
   - Effect sizes: Tested extraction shows 0/54 have effect_size filled
   - Instruments: Tested extraction shows 0/54 have instruments_used filled
   - **Status**: Data doesn't exist in corpus

3. **Result for This User**:
   ```
   Router: "Found 0 items matching 'biophilic design'"
   Fallback: "Please connect an LLM to analyze this question"
   User: "This doesn't work. Where's my data?"
   ```

**Verdict**: CANNOT DELIVER VALUE
- Required data (effect sizes, instruments) not populated
- Query must fall back to LLM
- User gets unsatisfying answer

**Blocking Issues**:
1. Extraction pipeline doesn't populate effect_size
2. Extraction pipeline doesn't populate instruments_used
3. Corpus has no semantic indexing (would need "biophilic" → related papers)

---

### User 2: Architect Designing Hospital

**Need**: "What environmental features reduce patient anxiety? Give me evidence-based design guidelines with confidence levels."

**Can the System Do It?**

1. **Template Coverage**: Are there design templates for healthcare + anxiety?
   - Search: Hospital, patient anxiety, environmental design
   - **Reality**: No search function implemented
   - Must use arbitrary QA fallback
   - **Status**: Requires LLM

2. **Evidence Strength Calculation**:
   - Expected: Coherence score × confidence level → "Strong," "Moderate," "Weak"
   - **Reality**: No such calculation exists in response generation
   - **Code Check**: `arbitrary_qa_handler.py` has no confidence calculation
   - **Status**: NOT IMPLEMENTED

3. **Design Parameter Extraction**:
   - Expected: Get all design parameters from findings about anxiety
   - **Reality**: Findings have antecedent (stimulus) but no structured "design_parameter" field
   - **Status**: Not extracted

4. **Result for This User**:
   ```
   System: "Requires LLM analysis"
   User: "I need evidence-based guidelines NOW, not AI speculation"
   ```

**Verdict**: CANNOT DELIVER VALUE
- No template coverage for healthcare
- No confidence level calculation
- No design parameter extraction
- Falls back to LLM for everything

**Blocking Issues**:
1. No healthcare-specific design templates
2. No confidence/evidence strength calculation in response formatting
3. Findings don't have design_parameter field

---

### User 3: Meta-Analyst

**Need**: "Give me all studies measuring PANAS in office environments, with sample sizes and p-values, formatted for meta-analysis."

**Can the System Do It?**

1. **Instrument Filtering**:
   - Expected: Get all findings where instruments_used includes "PANAS"
   - **Reality**: instruments_used is 0/54 in test extraction
   - **Status**: Data doesn't exist

2. **Sample Size Access**:
   - Expected: Finding has sample_size field
   - **Reality**: Check extraction structure... sample_context exists but no clean sample_size
   - **Status**: Partially available (needs parsing)

3. **P-value Extraction**:
   - Expected: p_value field in findings
   - **Reality**: No such field in extraction schema
   - **Status**: Missing

4. **Meta-Analysis Format Export**:
   - Expected: CSV/JSON with [study, instrument, n, p_value, effect_size]
   - **Reality**: No export function exists
   - **Status**: Not implemented

5. **Result for This User**:
   ```
   User: "I need structured meta-analysis data"
   System: "No data exists in that structure"
   User: "This system is unusable for my research"
   ```

**Verdict**: CANNOT DELIVER VALUE
- No instrument filtering (instruments_used is empty)
- No p-value field
- No meta-analysis export format
- System is not suitable for quantitative synthesis

**Blocking Issues**:
1. instruments_used not populated
2. p_value not extracted
3. sample_size not cleanly extracted
4. No export functionality

---

### User 4: Policy Maker

**Need**: "What's the strongest evidence for workplace design affecting productivity? Summarize for a non-technical audience."

**Can the System Do It?**

1. **Evidence Strength Ranking**:
   - Expected: Sort by coherence score, effect size, study quality
   - **Reality**: No ranking implemented
   - **Status**: NOT IMPLEMENTED

2. **Plain Language Summary**:
   - Expected: minimum_safe_summary field in findings
   - **Reality**: Let me check if this is populated...
   - **Code**: Extract structure has minimum_safe_summary field
   - **Status**: Partially — exists but not populated consistently

3. **Query Processing**:
   - Input: "workplace design and productivity"
   - Router: Falls to arbitrary QA
   - **Status**: Requires LLM

4. **Confidence Communication**:
   - Expected: "Strong evidence," "Moderate evidence," "Weak evidence"
   - **Reality**: No confidence label in responses
   - **Status**: NOT IMPLEMENTED

5. **Result for This User**:
   ```
   System: "Please connect an LLM for analysis"
   User: "I'm a policy maker, I need peer-reviewed summaries, not AI"
   ```

**Verdict**: CANNOT DELIVER VALUE
- No evidence strength ranking
- Plain language summaries not consistently populated
- Requires LLM (not suitable for policy context)
- No peer-reviewed framing

**Blocking Issues**:
1. No evidence strength ranking
2. minimum_safe_summary not consistently filled
3. No "strong/moderate/weak" confidence labels

---

### User 5: PhD Student Doing Literature Review

**Need**: "What theories explain the relationship between nature exposure and cognitive restoration? Show me the theoretical landscape."

**Can the System Do It?**

1. **Theory Mapping**:
   - Expected: All theories connected to "nature exposure" + "cognitive restoration"
   - **Reality**: theory_commitments is empty (0/54 in test)
   - **Status**: NOT POSSIBLE

2. **T1/T1.5/T2 Hierarchy**:
   - Expected: See how foundational theories (T1) → design frameworks (T1.5) → molecules (T2)
   - **Reality**: Catalog exists (`arbitrary_qa_handler.py:200-226`)
   - Status: Can show list but not linked to specific query

3. **Evidence Tree**:
   - Expected: T1 theory → supporting findings → citation chains
   - **Reality**: Findings not linked to theories
   - **Status**: NOT POSSIBLE

4. **Query Processing**:
   - Input: "theories nature exposure cognitive restoration"
   - Router: No match (would need semantic understanding)
   - Fallback: LLM required
   - **Status**: REQUIRES LLM

5. **Result for This User**:
   ```
   System: "Connect an LLM for analysis"
   User: "But I need formal theory mapping, not generative AI"
   ```

**Verdict**: PARTIALLY BROKEN
- Theory list exists (can show T1/T1.5/T2)
- But specific query cannot be answered
- No evidence trees can be built (findings not linked to theories)
- Cannot show "theoretical landscape" as requested

**Blocking Issues**:
1. theory_commitments not populated
2. No way to trace evidence back to theories
3. Requires LLM for query understanding

---

## Part 3: Ruthless Scoring

Based on actual testing, not assumptions:

| Dimension | Score | Evidence |
|-----------|-------|----------|
| **End-to-end pipeline integrity** | 3/10 | Data reaches extraction but never reaches BN. Query answering requires external LLM. Theory linking is completely non-functional. |
| **Data quality at each stage** | 4/10 | Extraction stage: 54 findings with theory_commitments=empty, instruments_used=empty, effect_size=null. Validation stage: 164 violations in single article but none critical. Web stage: no integration. |
| **User-facing readiness** | 2/10 | 5 user personas tested; 0 can get their primary need without external LLM. System is demo-ready but not user-ready. |
| **Error recovery** | 5/10 | Reflex system detects issues and logs them. But: (1) auto-fix is stubbed, (2) no downstream consumer, (3) user never sees health status. |
| **Theory integration depth** | 2/10 | Catalog exists (list of T1/T1.5/T2). But: (1) findings have zero theory links, (2) no way to query theories + findings together, (3) coherentist web is initialized but never updated. |
| **Cross-reference integrity** | 6/10 | molecule_registry loads (18 molecules). outcome_vocab loads (116 terms). instrument_ids exist in vocab. But: (1) findings never reference instruments or theories, (2) only 3/18 molecules have QA cache. |
| **Documentation-code alignment** | 4/10 | **Docs say**: "Extract theory commitments from papers." **Code does**: Empty regex pattern → empty field. **Docs say**: "Cultural calibration personalizes answers." **Code does**: Calibration files orphaned, no API parameter. |
| **Test coverage for critical paths** | 5/10 | Individual components tested (extraction_field_validator: 12 tests pass, web_persistence: 62 tests pass). But: 8 test files have import errors (missing passlib). No end-to-end integration tests. |

**AVERAGE SCORE: 3.8 / 10** (FAILING)

---

## Part 4: Blocking Issues — Ranked by Severity

### TIER 1: System Cannot Function (Blocks All Users)

**Issue 1.1**: Theory Commitments Not Extracted
- **Impact**: 100% of findings have empty theory_commitments
- **Location**: `src/extraction/batch_extract.py:60-71` uses regex pattern matching
- **Root Cause**: Pattern `(theory|framework|model predicts|hypothesis)` doesn't extract semantic meaning
- **Evidence**: Test extraction (10.1002_ad.2031.json): 54 findings, 0 have theory links
- **Consequence**:
  - Web of Belief never updates
  - Coherence never recomputes
  - Users can't query "theories that explain X"
- **Fix Effort**: HIGH (requires NLP or LLM enhancement to extraction)

**Issue 1.2**: Query Answering Requires External LLM
- **Impact**: Most queries (>95%) require Gemini/Claude to answer
- **Location**: `src/services/arbitrary_qa_handler.py:160-165` falls back to AI routing
- **Root Cause**: No semantic indexing, no theory-finding links, no structured catalog queries work
- **Evidence**: Test query "ceiling height and cognitive performance" → "requires LLM"
- **Consequence**: System is not standalone, requires API keys, cannot work offline
- **Fix Effort**: VERY HIGH (requires semantic search infrastructure)

**Issue 1.3**: Instruments Not Extracted or Linked
- **Impact**: Meta-analysts cannot filter by measurement method
- **Location**: `src/extraction/batch_extract.py` has no instrument extraction
- **Evidence**: Test extraction: 0/54 findings have instruments_used populated
- **Consequence**: User 3 (meta-analyst) cannot use system at all
- **Fix Effort**: HIGH (requires entity recognition + schema updates)

**Issue 1.4**: Effect Sizes Not Consistently Extracted
- **Impact**: Evidence strength cannot be quantified
- **Location**: Extraction doesn't parse effect size from tables/text
- **Evidence**: Test extraction: 0/54 have effect_size
- **Consequence**: User 1 (psychology researcher) cannot get data
- **Fix Effort**: HIGH (requires statistical table parsing)

---

### TIER 2: System Features Don't Work (Blocks Specific Users)

**Issue 2.1**: Dashboard Does Not Exist
- **Impact**: Users cannot see system health, reflex events, or extraction status
- **Location**: Reflex logging implemented (src/qa/reflex_system.py) but no consumer
- **Root Cause**: Logging pipeline ends, dashboard never built
- **Evidence**: No code found in src/services/ or frontend/ for health dashboard
- **Consequence**: User 4 (policy maker) cannot assess data quality
- **Fix Effort**: MEDIUM (build dashboard, wire reflex events)

**Issue 2.2**: Cultural Calibration Parameters Not Wired to Query Handler
- **Impact**: System cannot personalize answers for different cultures
- **Location**: Files exist (`data/calibration/ch*.json`) but not used
- **Root Cause**: No function signature includes culture parameter
- **Evidence**: `router.route_query(query)` has no culture param; CVA code not called
- **Consequence**: User 5 (PhD student in Asian context) gets English-default answers
- **Fix Effort**: MEDIUM (add culture param to API, call CVA in handlers)

**Issue 2.3**: No Evidence Strength Ranking
- **Impact**: Users cannot distinguish strong from weak evidence
- **Location**: No ranking/sorting by coherence × study quality
- **Evidence**: `arbitrary_qa_handler.py` returns unranked lists
- **Consequence**: User 2 (architect) cannot prioritize design guidelines
- **Fix Effort**: MEDIUM-HIGH (implement credence/entrenchment calculation in response)

**Issue 2.4**: Only 3 of 18 Molecules Have Precomputed QA Cache
- **Impact**: Fast path only works for 17% of molecules
- **Location**: `src/qa/router.py:134` looks for `{mol_id}_QA.json`
- **Evidence**: 13 molecules loaded, only 3 cache files exist
- **Consequence**: Most molecule queries hit LLM fallback
- **Fix Effort**: MEDIUM (populate QA cache for all molecules)

---

### TIER 3: Data Quality Issues (Degrades User Experience)

**Issue 3.1**: Validation Has No Teeth
- **Impact**: Low-quality extractions pass through (0.62/1.0 score)
- **Location**: `src/qa/extraction_field_validator.py:82-93` penalties are too weak
- **Evidence**: 164 violations in test article but score still 0.62
- **Consequence**: Users get unreliable data
- **Fix Effort**: LOW-MEDIUM (adjust violation weights, add quality gates)

**Issue 3.2**: Minimum Safe Summary Not Consistently Populated
- **Impact**: Plain-language summaries unavailable
- **Location**: Extraction schema includes field but extraction doesn't populate
- **Evidence**: Need to test but likely similar to theory/instrument pattern
- **Fix Effort**: MEDIUM (add summarization to extraction pipeline)

**Issue 3.3**: Sample Size and P-Values Not Cleanly Extracted
- **Impact**: Meta-analysts cannot get structured data
- **Location**: Extraction doesn't have sample_size, p_value fields
- **Evidence**: Test extraction schema doesn't include these
- **Fix Effort**: HIGH (add table parsing for statistical results)

---

### TIER 4: Missing Integrations (Gaps in Design)

**Issue 4.1**: Extraction-to-Web Pipeline Missing
- **Impact**: New papers don't update coherence
- **Location**: No `extraction_to_web.py` or equivalent
- **Evidence**: `src/services/` has no bridge from extraction to BN
- **Consequence**: Web of Belief is static snapshot
- **Fix Effort**: MEDIUM (implement integration pipeline)

**Issue 4.2**: Reflex Auto-Fix Not Implemented
- **Impact**: Detected issues not corrected
- **Location**: `src/qa/reflex_system.py` has detect() and report() but stub fix()
- **Evidence**: No auto-fix rules in code
- **Consequence**: Issues logged but not resolved
- **Fix Effort**: MEDIUM (implement fix rules for direction, missing fields)

**Issue 4.3**: No Semantic Search / Full-Text Index
- **Impact**: Keyword-based queries only (and they fail)
- **Location**: Missing from entire system
- **Evidence**: Router uses keyword matching; arbitrary QA uses regex
- **Consequence**: Can't search for "theories about biophilic design"
- **Fix Effort**: VERY HIGH (implement inverted index + vector search)

**Issue 4.4**: No Meta-Analysis Export Format
- **Impact**: User 3 cannot extract structured data
- **Location**: No export function in codebase
- **Evidence**: No function found that generates CSV/JSON for meta-analysis
- **Fix Effort**: MEDIUM (implement export with [study, instrument, n, effect, p])

---

## Part 5: Quick Incident Report

### What Works (Green Flags)
1. Extraction files are created and stored (54-2000+ findings per paper)
2. Web of Belief components are mathematically sophisticated
3. CVA code for cultural valuation is well-designed
4. Reflex system for health monitoring is architecturally sound
5. Test infrastructure exists (12 extraction_gate tests pass, 62 web_persistence tests pass)

### What's Broken (Red Flags)
1. **Critical Path Broken**: Finding → Theory link → BN update → User query — FAILS at step 2
2. **Data Quality**: theory_commitments and instruments_used are 100% empty
3. **Query Independence**: >95% of queries require external LLM
4. **Cultural Features**: Designed but disconnected (orphaned files)
5. **End-to-End Test**: No integration tests verify full scenario

### What's Missing (Orange Flags)
1. Semantic search / vector indexing
2. Auto-fix rules in reflex system
3. Dashboard for health/reflex events
4. Meta-analysis export format
5. Theory extraction (beyond regex)
6. Extraction-to-BN integration pipeline
7. Evidence strength ranking
8. Cultural parameter in query API

---

## Part 6: Recommended Immediate Actions

### Priority 1 (Week 1 — Unblock All Users)
1. **Populate theory_commitments**: Audit extraction pipeline, enable theory extraction or add manual curation step
2. **Wire extraction-to-BN**: Create `src/services/extraction_to_web.py` that triggers coherence updates
3. **Add semantic search**: Implement basic vector search for finding-to-query matching

### Priority 2 (Week 2 — Restore User Value)
1. **Fix extraction data quality**: Populate instruments_used, effect_size, sample_size
2. **Build health dashboard**: Wire reflex_events to UI
3. **Implement evidence ranking**: Add coherence × credence calculation to responses

### Priority 3 (Week 3 — Complete Features)
1. **Wire cultural calibration**: Add culture parameter to query API, call CVA
2. **Implement auto-fix**: Add repair rules to reflex system
3. **Build meta-analysis export**: CSV/JSON export for structured data

---

## Conclusion

Article_Eater is a **sophisticated research system that works in components but fails as a system**. The problem isn't individual modules — it's the **integration gaps** that prevent end-to-end value delivery.

- **For researchers**: "Show me findings" requires a side quest to extract your data manually
- **For architects**: "Give me design guidelines" defaults to asking ChatGPT instead
- **For policy makers**: "What's the evidence?" doesn't exist as a native query type
- **For meta-analysts**: "Export my data" isn't possible
- **For students**: "Map theories" fails because theories aren't linked to findings

**The system could be highly valuable once these integration issues are resolved, but it requires immediate architect-level work, not just bug fixes.**

