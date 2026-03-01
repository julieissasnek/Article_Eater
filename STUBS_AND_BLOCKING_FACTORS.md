# Stubs and Blocking Factors Reference
**Article_Eater_PostQuinean_v1**
**Last updated: 2026-02-28**

This document provides detailed information about all stubs and TODOs in the codebase, their blocking factors, and sprint assignments.

---

## Quick Reference Table

| ID | Function | File | Line | Status | Sprint | Blocker | Notes |
|----|----|------|------|--------|--------|---------|-------|
| S1 | `find_critical_question_gaps()` | `gap_predictor.py` | 1210 | STUB | 11 | ClaimV2 argument fields | Returns `[]` |
| S2 | `find_argument_attack_gaps()` | `gap_predictor.py` | 1232 | STUB | 11 | Contrast class analysis | Returns `[]` |
| T1 | `_fetch_finding_by_iv_dv()` | `prediction_generator.py` | 614 | TODO | 9 | findings_db schema | Returns `None` |
| T2 | BN posterior/prior/likelihood | `integrated_query_service.py` | 700 | TODO | 8 | BN service API | Hardcoded `None` |
| T3 | Remove duplicates | `epistemic_causal_bridge.py` | 75,165 | TODO | 24.0 | Demo function updates | V24.0 deprecation |
| T4 | VOI-driven search integration | `interpretive_intelligence.py` | 2631 | TODO | G | VOI algorithm | Documentation present |

---

## Detailed Stub Descriptions

### STUB S1: Gap Predictor - Critical Question Detection

**File:** `/src/services/gap_predictor.py`
**Lines:** 1210-1230
**Status:** Sprint 10 stub, scheduled for Sprint 11

#### Code
```python
def find_critical_question_gaps(self) -> List[PredictedGap]:
    """
    Find gaps where Walton critical questions are unaddressed.

    Sprint 10: STUB — Not yet implemented.

    This will check ClaimV2.argument_scheme and ClaimV2.critical_questions_addressed
    to identify claims that use an argumentation scheme but haven't addressed
    the scheme's critical questions.

    Example: An "argument from expert opinion" that hasn't addressed:
    - Is the source a credible expert?
    - Is this within their field of expertise?
    - Is there consensus among experts?

    Requires: ClaimV2 fields to be populated by extraction pipeline.
    Currently blocked by: Extraction pipeline not populating these fields.
    """
    # TODO: Implement when ClaimV2 argument fields are populated
    logger.debug("find_critical_question_gaps: STUB - not yet implemented (Sprint 10)")
    return []
```

#### Purpose
Identify gaps in argument validity by checking whether Walton-style argumentation schemes have addressed their standard critical questions.

#### Blocking Factor: ClaimV2 Argument Field Enrichment
The extraction pipeline in `src/extraction/` needs to populate:
- `ClaimV2.argument_scheme` - which argumentation scheme (Expert Opinion, Analogy, Causal, etc.)
- `ClaimV2.critical_questions_addressed` - set of CQ IDs that have been addressed
- `ClaimV2.argument_strength` - subjective assessment of argument validity

**Current status:** ClaimV2 dataclass exists in `src/epistemic/contracts/claim_v2.py` but extraction pipeline doesn't populate argument-specific fields yet.

**Owner:** Extraction pipeline team (Sprint 10/11)

#### Related Code
- `src/epistemic/contracts/claim_v2.py` - ClaimV2 dataclass
- `src/extraction/claim_extractor.py` - extraction logic
- `src/services/argument_attack.py` - related attack type analysis
- `src/services/gap_predictor.py` - context (lines 1200-1260)

#### When to Implement
1. Wait for extraction pipeline to support ClaimV2 argument fields
2. Add Walton critical question templates to knowledge base
3. Implement matching logic in GapPredictor
4. Test with papers containing explicit argumentation

#### Expected Output
```python
[
    PredictedGap(
        gap_type="CRITICAL_QUESTION",
        belief_id="claim_12345",
        description="Expert Opinion argument lacks credibility assessment",
        critical_questions=[
            "Is the source a credible expert in this domain?",
            "Is there consensus among experts?",
        ],
        priority=0.73,
    )
]
```

---

### STUB S2: Gap Predictor - Argument Attack Detection

**File:** `/src/services/gap_predictor.py`
**Lines:** 1232-1251
**Status:** Sprint 10 stub, scheduled for Sprint 11

#### Code
```python
def find_argument_attack_gaps(self) -> List[PredictedGap]:
    """
    Find gaps where known argument attack types apply.

    Sprint 10: STUB — Not yet implemented.

    This will check beliefs against known attack types from argument_attack.py:
    - CONFOUNDER: Unmeasured variable explains relationship
    - BOUNDARY_CONDITION: Effect only holds under specific conditions
    - MEASUREMENT: Measurement validity concerns
    - REVERSE_CAUSATION: Direction might be reversed
    - SELECTION_BIAS: Sample not representative
    - PUBLICATION_BIAS: Only positive results published

    Requires: AttackType patterns to be matched against belief content.
    Currently blocked by: Need contrast class analysis from argument_attack.py
    """
    # TODO: Implement when AttackType matching is available
    logger.debug("find_argument_attack_gaps: STUB - not yet implemented (Sprint 10)")
    return []
```

#### Purpose
Identify gaps by detecting known attack patterns that could undermine a claim (confounders, measurement issues, reverse causation, selection bias, etc.).

#### Blocking Factor: Contrast Class Analysis
The `src/services/argument_attack.py` module needs to provide:
- `ContrastClass` definitions for each attack type
- Pattern matching logic for claims/belief text
- Confidence scoring for attacks

**Current status:** `argument_attack.py` exists but doesn't provide:
- Contrast class computation for arbitrary belief text
- Integration hooks for GapPredictor

**Owner:** Argument analysis team (Sprint 10/11)

#### Related Code
- `src/services/argument_attack.py` - attack type definitions
- `src/services/gap_predictor.py` - calling context (lines 1200-1280)
- `src/epistemic/contracts/claim_v2.py` - belief data
- `src/argument/critique_aggregator.py` - related critique logic

#### Attack Types to Detect
1. **CONFOUNDER** - Unmeasured variable explains association
   - Pattern: Claims about causation without controlling variables

2. **BOUNDARY_CONDITION** - Effect limited to specific conditions
   - Pattern: Generalization beyond study conditions

3. **MEASUREMENT** - Measurement validity issues
   - Pattern: Weak operationalizations or proxy variables

4. **REVERSE_CAUSATION** - Direction of causality unclear
   - Pattern: Correlational designs claiming causation

5. **SELECTION_BIAS** - Sample not representative
   - Pattern: Convenience sampling or attrition issues

6. **PUBLICATION_BIAS** - Positive bias in literature
   - Pattern: Only published findings, no null results

#### When to Implement
1. Wait for `argument_attack.py` to stabilize API
2. Implement contrast class computation for belief text
3. Add pattern matching for each attack type
4. Test with known problematic papers in dataset

#### Expected Output
```python
[
    PredictedGap(
        gap_type="ARGUMENT_ATTACK",
        belief_id="claim_12345",
        description="Causal claim without controlling for confounders",
        attack_type="CONFOUNDER",
        suggested_question="What unmeasured variables might explain this relationship?",
        priority=0.81,
    )
]
```

---

## Detailed TODO Descriptions

### TODO T1: Prediction Generator - Database Query Implementation

**File:** `/src/services/prediction_generator.py`
**Line:** 614
**Status:** TODO, Sprint 9

#### Code
```python
def _fetch_finding_by_iv_dv(self, iv_name: str, dv_name: str) -> Optional[dict]:
    """
    Fetch empirical finding by independent variable (IV) and dependent variable (DV).

    This queries the findings database for studies that found a relationship
    between the specified IV and DV.
    """

    if self.findings_db is None:
        return None

    # TODO: Implement actual database query
    # Would search for findings matching IV → DV

    return None
```

#### Purpose
Look up empirical findings from the literature database (findings_db) by variable pair (IV, DV) to support belief generation and credence assessment.

#### Blocking Factor: findings_db Schema and Initialization
Requires:
- `findings_db` table schema with IV, DV, effect_size, p_value columns
- Initialization logic in database migration scripts
- Index creation for efficient IV-DV lookups

**Current status:**
- `self.findings_db` is initialized but query logic not implemented
- Database schema not yet finalized
- Sample data load logic pending

**Owner:** Database services team (Sprint 9)

#### Related Code
- `src/services/prediction_generator.py` - context (lines 600-700)
- `src/services/web_of_belief.py` - belief credence calculation
- `migrations/` - database schema files
- `src/extraction/batch_process.py` - extraction pipeline (populates findings_db)

#### Expected Implementation
```python
def _fetch_finding_by_iv_dv(self, iv_name: str, dv_name: str) -> Optional[dict]:
    """Query findings_db for empirical evidence of IV -> DV relationship."""
    try:
        query = """
            SELECT effect_size, p_value, sample_size, study_design
            FROM findings
            WHERE independent_var LIKE ? AND dependent_var LIKE ?
            ORDER BY p_value ASC
            LIMIT 1
        """
        cursor = self.findings_db.execute(query, (f"%{iv_name}%", f"%{dv_name}%"))
        result = cursor.fetchone()
        return dict(result) if result else None
    except Exception as e:
        logger.warning(f"findings_db query failed: {e}")
        return None
```

#### When to Implement
1. Database schema stabilizes (Sprint 9 planning)
2. Sample data loads successfully
3. Testing with real extraction pipeline output
4. Performance tuning for large datasets

---

### TODO T2: Integrated Query Service - Bayesian Network Integration

**File:** `/src/services/integrated_query_service.py`
**Line:** 700
**Status:** TODO, Sprint 8

#### Code
```python
QueryResult(
    query=query,
    article_evidence=article_evidence[:10],
    total_supporting_papers=len(paper_ids),
    evidence_quality_summary=evidence_summary,
    bn_posterior=None,  # TODO: Connect to BN
    bn_prior=None,
    bn_likelihood_ratio=None,
    panel_comments=panel_comments,
)
```

#### Purpose
Integrate Bayesian Network calculations into query responses to provide probabilistic credence updates based on the extracted evidence.

#### Blocking Factor: BN Service API Stabilization
Requires:
- Stable BN calibration service API
- Belief-to-BN-node mapping (ontology)
- Posterior calculation method signature
- Confidence bounds calculation

**Current status:**
- BN service exists in `src/services/` but API not stable
- Node mapping incomplete
- Performance characteristics unknown

**Owner:** BN calibration team (Sprint 8)

#### Related Code
- `src/services/web_of_belief.py` - belief credence
- `src/services/bbn_calibrator.py` - BN calibration
- `src/epistemic/bn_edges.py` - edge definitions
- `src/services/integrated_query_service.py` - calling context (lines 680-720)

#### Expected Values
```python
QueryResult(
    ...
    bn_posterior=0.73,          # P(hypothesis | evidence)
    bn_prior=0.50,              # P(hypothesis) before evidence
    bn_likelihood_ratio=2.92,   # Odds ratio from evidence
    ...
)
```

#### When to Implement
1. Wait for BN service API freeze
2. Implement belief->node mapping
3. Add posterior calculation calls
4. Validate against expert priors
5. Performance testing with real queries

---

### TODO T3: Epistemic Causal Bridge - Duplicate Class Removal

**File:** `/src/services/epistemic_causal_bridge.py`
**Lines:** 75, 165
**Status:** TODO, V24.0 deprecation

#### Code
```python
# Line 75:
# TODO (Sprint ECB-2): Remove these duplicates after updating demo functions
# to use the canonical classes from web_of_belief.py.
# REMOVE_BY: V24.0 (per Parnas, Panel P-ECB-R)

# Lines 162-167:
# DEPRECATION NOTICE: See PART 1 header for details.
# CANONICAL LOCATION: src/services/web_of_belief.py
# TODO (Sprint ECB-2): Remove after demo function updates.
# REMOVE_BY: V24.0 (per Parnas, Panel P-ECB-R)
```

#### Purpose
Remove duplicate WebOfBelief, Belief, and Edge class definitions that exist in both:
- `/src/services/epistemic_causal_bridge.py` (old/deprecated)
- `/src/services/web_of_belief.py` (canonical)

#### Why Duplicates Exist
- Historical: ECB module created before web_of_belief.py
- Demo compatibility: Old demo functions still import from epistemic_causal_bridge
- Gradual deprecation strategy

#### Blocking Factor: Demo Function Updates
Requires updating all demo/example functions to import from web_of_belief:

**Files to update:**
- `src/agents/agent_panels_v2.py` - demo agents
- Any Jupyter notebooks in `notebooks/`
- Example scripts in `examples/`
- Tests that import from epistemic_causal_bridge

**Current status:**
- Canonical classes in web_of_belief.py are production-ready
- Duplicate classes in epistemic_causal_bridge still functional
- Demo functions still use old imports

**Owner:** Demo/example code maintainers (V24.0 timeline)

#### Removal Checklist
- [ ] Inventory all imports of WebOfBelief/Belief/Edge from epistemic_causal_bridge
- [ ] Update each import to use web_of_belief
- [ ] Test all demos with new imports
- [ ] Delete duplicate class definitions
- [ ] Verify no remaining references

#### Related Code
- `src/services/web_of_belief.py` - canonical location
- `src/services/epistemic_causal_bridge.py` - deprecated location
- `src/agents/agent_panels_v2.py` - uses old imports
- `src/epistemc/contracts/` - related classes

#### When to Implement
- Only after V24.0 stabilizes
- Part of normal deprecation cycle
- Can be done incrementally (per-demo)

---

### TODO T4: Interpretive Intelligence - VOI-Driven Search Integration

**File:** `/src/services/interpretive_intelligence.py`
**Lines:** 2631-2679
**Status:** TODO, Sprint G (handoff documentation)

#### Code
```python
# =============================================================================
# TODO 3 HANDOFF (Sprint G)
# =============================================================================
"""
TODO 3 Handoff Summary: VOI-Driven Search

This module provides the foundation for TODO 3 through:

1. Gap Identification (GapIdentifier class)
   - Identifies UNCERTAIN gaps (high credence uncertainty)
   - Identifies UNEXPLORED gaps (few supporting studies)
   - Returns prioritized IdentifiedGap objects

2. Search Context Generation (SearchContextGenerator class)
   - Converts IdentifiedGap -> SearchContext
   - Generates search queries based on gap type
   - Specifies target study types (RCT, longitudinal, etc.)
   - Calculates priority scores

3. Pipeline Integration Functions
   - generate_search_contexts(gaps, beliefs) -> List[SearchContext]
   - export_gaps_for_search(gaps, beliefs, path) -> JSON output

4. Data Flow for TODO 3:
   InterpretiveEngine.explain()
       |
       v
   GapIdentifier.identify_gaps()
       |
       v
   SearchContextGenerator.generate_search_context()
       |
       v
   SearchContext (contains: queries, study_types, priority, rationale)
       |
       v
   TODO 3: VOI-Driven Search

5. Key Classes for TODO 3 Integration:
   - IdentifiedGap: gap_type, description, belief_id, priority
   - SearchContext: gap, search_queries, target_study_types, priority_score, rationale
"""
```

#### Purpose
Document the handoff from TODO 2 (explain epistemic state) to TODO 3 (VOI-driven search for gap closure).

#### What's Already Implemented
- `GapIdentifier` class - identifies gaps (uncertain, unexplored, contradictory)
- `SearchContextGenerator` class - generates search queries for gaps
- `IdentifiedGap` and `SearchContext` dataclasses
- Export functions for downstream consumption

#### What Needs Implementation in Sprint G
1. **VOI Scoring Algorithm** - rank gaps by information value
2. **Source Selection** - match gaps to optimal paper types
3. **Paper Searcher Integration** - call paper search with top-ranked gaps
4. **Feedback Loop** - update beliefs with new papers

#### Blocking Factor: VOI Algorithm Finalization
Requires:
- Expert panel agreement on VOI scoring (prior credence × uncertainty × impact)
- Integration with Giles source selection framework
- Performance optimization for large belief sets

**Current status:**
- Foundation code complete
- Algorithm not yet specified
- Integration points documented

**Owner:** Sprint G planning (post-Phase D)

#### Related Code
- `src/services/interpretive_intelligence.py` - context (lines 2200-2679)
- `src/services/gap_predictor.py` - gap detection
- `src/services/paper_search.py` - paper discovery (future)
- `docs/implementation_plans/PHASE_D_REVISED_PLANS_2026_01_20.md` - planning docs

#### Expected Data Flow
```python
# Input: belief set
beliefs = {
    "claim_1": Belief(content="X causes Y", credence=0.65),
    "claim_2": Belief(content="Y affects Z", credence=0.80),
}

# Step 1: Identify gaps
gaps = gap_identifier.identify_gaps(beliefs)
# -> [IdentifiedGap(type="UNCERTAIN", belief_id="claim_1", priority=0.92)]

# Step 2: Generate search contexts
search_contexts = search_generator.generate_search_context(gaps[0], beliefs)
# -> SearchContext(gap=gap, queries=["X causes Y"], study_types=["RCT", "longitudinal"])

# Step 3: Rank by VOI (TODO 3)
ranked = voi_scorer.rank_by_information_value(search_contexts)

# Step 4: Execute searches
papers = paper_searcher.search(ranked[0].queries)

# Step 5: Update beliefs
updated_beliefs = belief_updater.integrate_papers(beliefs, papers)
```

#### When to Implement
- After Phase D specification complete
- VOI algorithm frozen by expert panel
- Integration API defined with paper search service

---

## FAQ

**Q: What happens if a blocking factor never gets resolved?**
A: The stub function returns an empty collection, so the system degrades gracefully. Gaps of that type simply won't be detected, but queries still succeed.

**Q: Can we implement a stub before its blocker is ready?**
A: The blocker is listed explicitly so teams can coordinate. If timing changes, update the comment and Slack the team. Don't implement without blocker data available.

**Q: How are new TODOs added?**
A: New TODO comments must be added to `config/sanity_todo_allowlist.txt` file before `scripts/sanity_check.py` will compile successfully. This forces deliberate review.

**Q: Are there any hidden TODOs not in the allowlist?**
A: No. The sanity check script scans all of src/ and fails if it finds TODO/STUB/NotImplementedError outside the allowlist. This is enforced at compile time.

**Q: How do I track progress on a TODO?**
A: Update the relevant task in `TASKS.md` with status and notes. Move completed TODOs to the "Completed" section with date and outcome.

---

## See Also

- **CODEBASE_AUDIT_2026-02-28.md** - Full audit report
- **AUDIT_FINDINGS_SUMMARY.txt** - Executive summary
- **config/sanity_todo_allowlist.txt** - Approved TODO files
- **scripts/sanity_check.py** - Compile-time TODO validation
- **TASKS.md** - Task tracking and sprint planning

---

*Last updated: 2026-02-28*
*Maintained by: Claude Code Auditor*
*Next review: End of Sprint 9 (check T1, T2 progress)*
