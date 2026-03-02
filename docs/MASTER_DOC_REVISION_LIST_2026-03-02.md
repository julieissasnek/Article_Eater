# Master Document Revision List

**Date**: 2026-03-02
**Source**: Article Recommendation Flow Audit (AUDIT_RECOMMENDATION_FLOW_2026-03-02.md) + VOI Integration Audit
**Target Document**: `docs/MASTER_DOC_CMR_2026-02-25.md` (~20,000 lines)

---

## Executive Summary

The Article Recommendation Flow Audit (March 2, 2026) identified significant disconnects between the aspirational architecture and actual implementation in the Article_Eater system. This revision list captures all topics that must be added or revised in the master document to accurately reflect:

1. **Current state**: What the system actually does (gaps detected, VOI computed but unused, researcher-agnostic recommendations)
2. **Aspirational state**: What was intended (VOI-driven prioritization, researcher-specific recommendations, closed feedback loops)
3. **Missing infrastructure**: Tables assumed but undefined, components referenced but stubs
4. **Panel review requirements**: Design decisions requiring expert input

The master document currently emphasizes the ATLAS epistemic framework (Parts II–IV, Sections 33–53) and expert panel outputs (Parts V–XVII). It requires substantial additions addressing the *operational pipeline* for article discovery, which is tangential to the core ATLAS theory but essential for the full system to function.

---

## Structure of This Revision List

Each item is categorized as:
- **Priority**: P0 (blocks deployment), P1 (required for correctness), P2 (desirable, improves clarity)
- **Type**: NEW SECTION, REVISE EXISTING, or CLARIFY/MARK ASPIRATIONAL
- **Effort**: Estimated writing/research effort in hours
- **Dependencies**: What must be completed first
- **Code Impact**: Whether this affects source code, not just documentation

---

## PART A: NEW SECTIONS NEEDED

### A1. VOI Integration Architecture (NEW SECTION)

**Priority**: P1
**Type**: NEW SECTION
**Estimated Effort**: 8–10 hours (including code review and flow diagramming)
**Dependencies**: None (foundational)
**Code Impact**: YES — Informs desired changes to queue/service.py, voi_search.py integration

**Location in Master Doc**: Should be inserted after §47 (Value of Information: Scoring and Prioritizing Experiments) and before Part IV (The Credence Calculus). Proposed new section: **§47A. VOI Integration Architecture: From Gap Detection to Queue Prioritization**.

**Content to Include**:

1. **Current State vs. Intended State Diagram**
   - Actual flow: GapPredictor → ResearchTarget → Queue (FIFO, no VOI ranking)
   - Intended flow: GapPredictor → VOI Scorer → ResearchTarget → Queue (VOI-ranked) → AutomatedSearcher
   - Key disconnects highlighted

2. **The VOI Computation Chain (3 modules)**
   - **voi_search.py (gap-level)**: VOIGapScorer.calculate_voi() → EpistemicGap wrapper → SearchRecommendation
   - **voi_scoring.py (finding-level)**: score_voi(findings) → individual finding value scores
   - **discovery_funnel.py (lifecycle tracking)**: Gap lifecycle OPEN → SEARCHING → FOUND → CLOSED + VOI revision on closure
   - When each module should be called in the full pipeline

3. **The Adjusted VOI Formula**
   - Base VOI: f(epistemic_voi, structural_voi) from voi_search.py
   - Researcher-specific adjustment: VOI_adjusted = base_VOI × researcher_fit_factor(collector_profile, gap)
   - Queue ranking: targets sorted by VOI_adjusted descending; next_highest_voi_target() returns top unassigned

4. **Queue Prioritization Logic**
   - Current: get_next_target(collector_id) returns FIFO unassigned target
   - Intended: get_next_highest_voi_target(collector_id) returns target with highest VOI_adjusted
   - Fallback when no VOI_adjusted scores available: graceful degradation to FIFO

5. **Feedback Loop (Closure Assessment)**
   - After search execution and PDF extraction, gap closure is assessed
   - If gap closed: discovery_funnel marks CLOSED, VOI feedback captured
   - If gap partially addressed: VOI revised downward, gap remains OPEN for future searches
   - Updated VOI_adjusted → queue re-ranking

6. **Full End-to-End Example**
   - Gap predicted: "Mechanism missing: How does daylight affect mood?"
   - Base VOI: 0.68 (high epistemic centrality, low sparsity)
   - Collector profile: Architectural psychologist, domain expert, high access
   - Researcher fit: 1.1 (domain match bonus for this researcher)
   - VOI_adjusted: 0.68 × 1.1 = 0.748
   - Queue position: Ranked 2nd highest among open targets
   - Searcher claims, finds 3 papers, integrates findings
   - Gap closure assessed: 60% addressed
   - VOI revised: 0.68 → 0.27 (downward due to partial closure)
   - Gap remains OPEN with lower priority

---

### A2. Researcher-Specific VOI and Collector Profiles (NEW SECTION)

**Priority**: P1
**Type**: NEW SECTION
**Estimated Effort**: 6–8 hours (design + CollectorProfile integration)
**Dependencies**: A1 (VOI Integration Architecture) completed first
**Code Impact**: YES — Requires implementation of researcher_fit_factor() function, CollectorProfile field extensions

**Location in Master Doc**: Immediately after A1. Proposed section: **§47B. Researcher-Specific VOI: Personalizing Article Recommendations**.

**Content to Include**:

1. **Why Researcher-Specific VOI Matters**
   - David Kirsh's design principle: "Before recommending a topic to a researcher, we need researcher-specific VOI"
   - Problem with universal VOI: all researchers see same gaps in same priority order, but their interests/expertise differ
   - Solution: Adjust base VOI by researcher fit before presenting recommendations

2. **The Researcher Model (CollectorProfile Extension)**
   - Existing fields in queue/models.py:CollectorProfile:
     - collector_type (HUMAN_RESEARCHER, HUMAN_ASSISTANT, AUTOMATED_SEARCHER, ZOTERO_WATCHER)
     - can_access_databases, can_access_paywalled
     - preferred_domains, typical_turnaround_hours
     - targets_completed, gap_closure_rate, avg_articles_per_target
   - New fields to add:
     - expertise_level (0–1: novice, intermediate, expert)
     - domain_interests (list of domain keywords matching gap types)
     - theoretical_alignment (mapping of researcher to theories: ART, SRT, Circadian, etc.)
     - research_stage (discovery, validation, application)
     - access_level (open access only, paywall access, institutional subscriptions)
     - closure_rate_by_gap_type (dict: GapType → historical closure_rate)

3. **The researcher_fit_factor() Function**
   - Inputs: base_gap, collector_profile
   - Outputs: adjustment factor ∈ [0.5, 1.5] applied as multiplier to base VOI
   - Components:
     - **Domain Match** (±0.3): Does the gap align with collector's preferred_domains? Match: +0.10; no match: −0.10
     - **Expertise Fit** (±0.2): Does gap complexity match expertise_level? Mismatched difficulty: −0.15; good match: +0.05
     - **Theoretical Alignment** (±0.15): Is the gap relevant to researcher's theoretical interests? Aligned: +0.10; orthogonal: −0.05
     - **Access Feasibility** (±0.1): Can researcher access required sources? Full access: +0.05; limited access: −0.05
     - **Closure History** (±0.1): Historical closure_rate on this gap_type? High (>0.60): +0.08; low (<0.30): −0.08
   - Formula: researcher_fit = 1.0 + domain_match + expertise_fit + theoretical_alignment + access_feasibility + closure_history
   - Clamped to [0.5, 1.5] to prevent extreme over/undervaluation

4. **Personalized Queue Example**
   - Same gap pool seen by three researchers with different profiles:
     - Researcher A (neuroscientist, expert, high Circadian interest): VOI_adjusted = 0.68 × 1.3 = 0.88
     - Researcher B (architect, intermediate, design-focused): VOI_adjusted = 0.68 × 0.9 = 0.61
     - Researcher C (practitioner, novice, low expertise): VOI_adjusted = 0.68 × 0.6 = 0.41
   - Each sees different priority order based on personalization

5. **Learning the researcher_fit_factor**
   - Initial factor: heuristic based on profile fields
   - Updates: As closure_rate_by_gap_type accumulates data, the fit factor can be calibrated
   - Feedback: If researcher consistently closes certain gap types, their fit factor for those types increases
   - Decay: If researcher's closure rate on a type declines, the factor decreases

6. **Interaction with CollectorProfile.gap_closure_rate**
   - Existing field: gap_closure_rate (float, overall)
   - Extension: gap_closure_rate_by_type (dict: str → float)
   - Used to update researcher_fit_factor periodically (e.g., monthly re-calibration)

---

### A3. Article Search Execution Pipeline (NEW SECTION)

**Priority**: P1
**Type**: NEW SECTION
**Estimated Effort**: 8–10 hours (orchestration diagram + design decisions)
**Dependencies**: A1 and A2 (builds on VOI integration and researcher context)
**Code Impact**: YES — Requires implementation of search orchestration, worker pool, rate limiting

**Location in Master Doc**: After §47B. Proposed section: **§47C. Article Search Execution Pipeline: From Gap to PDF Ingestion**.

**Content to Include**:

1. **End-to-End Orchestration**
   ```
   Gap Detection
     ↓ (find_all_gaps from gap_predictor)
   VOI Scoring
     ↓ (VOIGapScorer.calculate_voi, adjusted by researcher_fit_factor)
   Queue Management
     ↓ (ResearchQueueService stores targets, ranked by VOI_adjusted)
   Search Execution
     ├─ Automated: Triggered at VOI threshold or on schedule
     ├─ Manual: Human researcher claims target
     └─ Hybrid: Searcher bot + human review
   Query Generation
     ↓ (QueryGenerator with VOI-enhanced vocabulary vs. FallbackQueryGenerator)
   PDF Retrieval
     ├─ SemanticScholar API
     ├─ Crossref DOI lookup
     ├─ Institutional repository search
     └─ Fallback: Manual doi lookup if automated fails
   Extraction & Analysis
     ↓ (Publication pipeline, quality rules validation)
   Web-of-Belief Integration
     ↓ (beliefs, warrants, annotations stored)
   Discovery Funnel Tracking
     ↓ (mark gap as FOUND, assess closure)
   Closure Assessment & Feedback
     ↓ (VOI feedback loop, queue re-ranking)
   ```

2. **Automated vs. Manual Search Triggering**
   - Automated: When VOI_adjusted > threshold T_auto (config: default 0.65)
     - AutomatedQueueSearcher.run_once() claims next highest-VOI target
     - Executes search queries
     - Reports results back to queue
   - Manual: When VOI_adjusted ≤ T_auto or gap requires human judgment
     - Target remains in queue
     - Human researcher claims via UI
     - Manual search, document findings, report results
   - Configuration: T_auto should be panel-reviewed decision (see Panel Review section)

3. **Search Worker Pool & Rate Limiting**
   - Automated searcher instance: can claim up to max_targets_per_run (config: default 5)
   - Semantic Scholar API: rate limits (300 requests/sec as of 2026)
   - Backoff strategy: exponential backoff on rate-limit hits
   - Concurrency: Can run multiple AutomatedQueueSearcher instances (worker pool) if needed
   - Scheduling: Could be periodic (hourly, daily) or event-driven (gap added → trigger search)

4. **Query Generation Strategy**
   - VOI-enhanced queries (QueryGenerator with voi_search.py)
     - Uses gap description + suggested_search
     - Enriches with cross-field vocabulary from web_of_belief
     - Produces primary_queries + secondary_queries with source preferences
   - Fallback queries (FallbackQueryGenerator)
     - Simple keyword extraction from gap description
     - No cross-field vocabulary enrichment
     - Used if voi_search import fails
   - Recommendation: Master doc should clarify when each is preferred

5. **PDF Retrieval Strategy**
   - Semantic Scholar: Primary for full-text PDF links
   - Crossref: For DOI resolution and metadata
   - Institutional repository APIs: For access to paywalled content (if collector has access)
   - Fallback: Mark as "metadata only" if PDF unavailable
   - Retry: Failed retrievals re-queued for later attempt

6. **Integration with Paper Integration Pipeline**
   - PDFs ingested via paper_integration/orchestrator.py
   - Publication service extracts metadata, content
   - Extraction quality rules applied (contracts/schemas/extraction_quality_rules.json)
   - Findings stored as Belief, WarrantEdge objects in web_of_belief
   - Annotations (open_questions, evidence_types, confidence) captured

7. **Gap Closure Assessment**
   - After extraction, evaluate: does the paper address the gap?
   - Closure status: OPEN (not addressed), PARTIAL (some evidence), CLOSED (sufficient)
   - If CLOSED: discovery_funnel.mark_gap_closed(gap_id, closure_evidence)
   - VOI feedback: If closed, base_VOI→VOI_adjusted downward; gap deprioritized
   - If PARTIAL: gap remains OPEN with revised VOI (usually lower)

---

### A4. QA System as Recommendation Source (NEW SECTION)

**Priority**: P2
**Type**: NEW SECTION
**Estimated Effort**: 4–6 hours (design of QA→queue integration)
**Dependencies**: A1 (VOI framework), A3 (search execution)
**Code Impact**: YES — Requires wiring arbitrary_qa_handler.py into search recommendation flow

**Location in Master Doc**: After §47C. Proposed section: **§47D. QA System Integration: From Follow-Up Questions to Search Recommendations**.

**Content to Include**:

1. **Current QA System (arbitrary_qa_handler.py)**
   - Handles arbitrary user questions about system knowledge
   - Returns answers + follow-up suggestions (e.g., "What evidence supports these recommendations?")
   - Currently: Follow-up is *reactive only* — user must ask explicitly

2. **Intended QA→Search Flow**
   - When QA handler detects a gap in answering a question, it can generate a SearchGap
   - Example: User asks "Does red color improve focus?" → Handler answers (tentatively) but notes evidence is sparse
   - Generate implicit SearchGap with type VALIDATION_GAP or MECHANISM_GAP
   - Push to research queue with moderate VOI (lower than user-identified gaps, higher than background)
   - Researcher can claim and conduct search to validate the QA system's tentative answer

3. **QA Handler Architecture**
   - Six handler types: catalog, evidence, comparison, mechanism, definition, meta
   - Each handler should have optional follow_up_searches property
   - Example: DefinitionHandler answering "What is biophilia?" notes that definition varies across sources → generate SearchGap for coherence check

4. **Integration Point**
   - ArbitraryQAHandler.answer(question) could return tuple: (answer, follow_ups, SearchGaps)
   - SearchGaps passed to ResearchQueueService.add_qa_generated_gaps()
   - Queue service converts to ResearchTarget, ranks by VOI, adds to queue

5. **VOI for QA-Generated Gaps**
   - Generally lower than user-identified gaps (epistemic_voi based on answer confidence)
   - Based on handler type (mechanism gaps higher than definition clarifications)
   - Example: MECHANISM_GAP from mechanism handler gets base_VOI 0.55; DEFINITION_GAP gets 0.30

6. **Design Decision for Panel Review**
   - Should QA system proactively generate SearchGaps, or only on user request?
   - If proactive, what confidence threshold triggers gap generation?
   - Risk: Could flood queue with low-priority gaps; mitigation needed

---

### A5. Discovery Funnel Feedback Loop (NEW SECTION)

**Priority**: P1
**Type**: NEW SECTION
**Estimated Effort**: 6–8 hours (design + flow documentation)
**Dependencies**: A1 (VOI), A3 (search execution)
**Code Impact**: YES — Requires implementation of closure assessment → VOI revision → queue re-ranking cycle

**Location in Master Doc**: After §47D. Proposed section: **§47E. Discovery Funnel Feedback Loop: Bidirectional Tracking and VOI Revision**.

**Content to Include**:

1. **Current Funnel Design (discovery_funnel.py)**
   - Tracks gap lifecycle: OPEN → SEARCHING → FOUND → CLOSED
   - Passive monitoring: Records transitions but doesn't influence prioritization
   - Gap status enum: GapStatus.OPEN, SEARCHING, FOUND, CLOSED, STALE

2. **Bidirectional Loop (Intended)**
   - Forward: Gap detection → Search execution → PDF ingestion → Closure assessment → Gap marked CLOSED
   - Backward: Closure evidence → VOI revision → Queue re-ranking → Next target selection

3. **Closure Assessment Framework**
   - After paper extracted and findings integrated into web_of_belief:
   - Measure: Does this paper provide direct evidence on the gap?
   - Scoring: closure_evidence = min(warrant_quality for all edges addressing gap)
   - Threshold: If closure_evidence > 0.60, mark gap CLOSED; else PARTIAL or OPEN

4. **VOI Revision Formula**
   ```
   new_VOI = base_VOI × (1.0 − closure_fraction)
   where closure_fraction ∈ [0, 1] based on evidence quality
   ```
   - Closed gap (closure_fraction = 1.0): new_VOI = base_VOI × 0 = 0 (no longer valuable to search)
   - Partially closed (closure_fraction = 0.5): new_VOI = base_VOI × 0.5 (reduced but still relevant)
   - Not addressed (closure_fraction = 0.0): new_VOI = base_VOI × 1.0 (unchanged)

5. **Queue Re-Ranking on VOI Revision**
   - When a gap's VOI is revised (downward after closure), the target's priority in the queue changes
   - get_next_highest_voi_target() re-sorts at claim time or periodically
   - Previously top-ranked gap may drop if closure_fraction is high

6. **Stale Gap Handling**
   - If gap remains OPEN for >X days with no search execution: mark STALE
   - STALE gaps deprioritized (VOI decayed by 0.1 per week of staleness)
   - Can be re-activated if new evidence emerges

7. **Feedback Loop Example**
   - Day 1: Gap "Biophilic patterns → Well-being mechanism" detected, base_VOI = 0.72
   - Day 1: Target created, queued with VOI_adjusted = 0.72
   - Day 5: Searcher claims, executes search, retrieves 2 papers
   - Day 8: Papers ingested; mechanism evidence found in both (warrant_quality 0.65)
   - Day 8: closure_evidence = 0.65 → closure_fraction = 0.75 (75% closed)
   - Day 8: VOI revised: new_VOI = 0.72 × (1.0 − 0.75) = 0.18
   - Day 8: Target deprioritized in queue; next claim returns different gap
   - Gap remains in queue but at low priority for future targeted searches if new questions arise

---

### A6. Overseer Management Database Schema (NEW SECTION)

**Priority**: P1
**Type**: NEW SECTION
**Estimated Effort**: 6–8 hours (schema design + clarification of overseer_management assumptions)
**Dependencies**: None (foundational infrastructure)
**Code Impact**: YES — Requires implementation of tables referenced in overseer_management.py

**Location in Master Doc**: In a new appendix or infrastructure section. Proposed section: **§INFRA.1. Overseer Management Layer Database Schema**.

**Content to Include**:

1. **Current State (Audit Finding)**
   - overseer_management.py queries from `interpretation_space_suggestions` table (line 548)
   - Table does not exist in codebase
   - Code has try/except fallback but table is undefined

2. **Complete Schema Design**

   **Table: interpretation_space_suggestions**
   ```sql
   CREATE TABLE interpretation_space_suggestions (
       id INTEGER PRIMARY KEY,
       gap_id TEXT NOT NULL,                    -- Foreign key to gap
       source TEXT NOT NULL,                    -- 'interpretation_space', 'voi', 'qa', 'argumentation', 'other'
       status TEXT NOT NULL,                    -- 'proposed', 'identified', 'archived'
       created_at TEXT NOT NULL,                -- ISO 8601 timestamp
       updated_at TEXT NOT NULL,                -- ISO 8601 timestamp
       age_days INTEGER,                        -- Computed: days since created_at
       content TEXT NOT NULL,                   -- Suggestion description
       priority REAL,                           -- VOI score or priority ranking
       assigned_to TEXT,                        -- Collector ID if claimed
       closed_at TEXT,                          -- ISO 8601 timestamp if resolved
       closure_evidence TEXT,                   -- Free text describing resolution
       UNIQUE(gap_id, source)
   )
   ```

   **Table: management_pipelines**
   ```sql
   CREATE TABLE management_pipelines (
       id INTEGER PRIMARY KEY,
       pipeline_id TEXT UNIQUE NOT NULL,        -- 'article_discovery', 'qa_review', etc.
       status TEXT NOT NULL,                    -- 'active', 'paused', 'archived'
       created_at TEXT NOT NULL,
       updated_at TEXT NOT NULL,
       config JSON                              -- Pipeline configuration, thresholds, etc.
   )
   ```

   **Table: overseer_alerts**
   ```sql
   CREATE TABLE overseer_alerts (
       id INTEGER PRIMARY KEY,
       pipeline_id TEXT NOT NULL,               -- Foreign key to management_pipelines
       alert_type TEXT NOT NULL,                -- 'stale_suggestions', 'high_voi_unaddressed', 'low_closure_rate', etc.
       triggered_at TEXT NOT NULL,              -- ISO 8601 timestamp
       dismissed_at TEXT,                       -- ISO 8601 if manually dismissed
       content TEXT NOT NULL                    -- Alert description
   )
   ```

   **Table: suggestion_backlog_report** (Read-only view or cached summary)
   ```sql
   CREATE TABLE suggestion_backlog_report (
       id INTEGER PRIMARY KEY,
       computed_at TEXT NOT NULL,
       source TEXT NOT NULL,                    -- Aggregated by source
       count_proposed INTEGER,
       count_identified INTEGER,
       count_archived INTEGER,
       median_age_days REAL,
       max_age_days INTEGER                     -- Stalest suggestion
   )
   ```

3. **Insertion Points**
   - When gap is detected (gap_predictor.find_all_gaps): insert interpretation_space_suggestions row with source='argumentation'
   - When gap is scored (voi_search.py): update with source='voi', priority=base_VOI
   - When gap is closed (discovery_funnel): update status='archived', closed_at, closure_evidence

4. **Queries Expected by overseer_management.py**
   - check_suggestion_backlog(): Count by source, compute age stats
   - list_stale_suggestions(age_threshold): Return suggestions older than threshold
   - track_closure_rate(): Count proposed vs. closed by source

5. **Design Decision for Panel Review**
   - Should overseer queries be mandatory (blocks deployment), or optional (nice-to-have monitoring)?
   - If mandatory: implement all tables, insert at gap detection/closure points
   - If optional: document as aspirational and mark as Phase 2 feature

---

## PART B: EXISTING SECTIONS TO REVISE

### B1. VOI Computation Details (REVISE §47)

**Priority**: P1
**Type**: REVISE EXISTING SECTION
**Estimated Effort**: 4–6 hours (clarification and integration)
**Dependencies**: A1 (VOI Integration Architecture) completed first
**Code Impact**: NO (documentation only, but guides future implementation)

**Location in Master Doc**: §47. Value of Information: Scoring and Prioritizing Experiments (already exists)

**Current Issues**:
- §47 describes VOI conceptually but doesn't distinguish the 3 computation modules (voi_search, voi_scoring, discovery_funnel)
- No clear statement of when each module is called
- Doesn't explain that gap_predictor currently hardcodes voi_score=0.5 (now fixed in code, but doc unaware)

**Revisions Needed**:

1. **Add subsection: 47.1A The Three VOI Computation Modules**
   - voi_search.py (gap-level): VOIGapScorer operates on PredictedGap and Belief; produces SearchRecommendation with voi_score
     - When called: Optional (lazy import in queue/service.py)
     - Inputs: EpistemicGap (gap description + belief context), WebOfBelief
     - Outputs: voi_score ∈ [0, 1]
   - voi_scoring.py (finding-level): score_voi(findings) produces VOI bucket for extracted finding
     - When called: During paper evaluation (cmr/paper_eval.py)
     - Inputs: list of findings (extracted claims from PDF)
     - Outputs: voi_bucket ∈ {'high', 'medium', 'low'} + numeric score
   - discovery_funnel.py (lifecycle): Tracks gap status progression OPEN→FOUND→CLOSED; computes closure_fraction
     - When called: During paper integration (paper_integration/orchestrator.py)
     - Inputs: Ingested findings, gap ID
     - Outputs: closure_evidence, closure_fraction (for VOI revision)

2. **Add subsection: 47.2 Gap Predictor VOI Defaults (Fixed as of March 2026)**
   - Legacy: gap_predictor.py line 55 hardcoded voi_score=0.5 for all gaps
   - Current: Still defaults to 0.5 but designed to accept optional VOI scorer
   - Intended: gap_predictor should call VOIGapScorer during find_all_gaps() if available
   - Migration path: Accept VOIGapScorer as optional dependency; if provided, compute actual ω, δ, d; if not, use default 0.5

3. **Add subsection: 47.3 Researcher-Specific VOI Adjustment**
   - Base VOI from modules above is universal (applies to all researchers)
   - researcher_fit_factor(gap, collector_profile) multiplies base_VOI to personalize
   - Depends on collector expertise, domain alignment, historical closure rates
   - Produces VOI_adjusted for ranking in queue

4. **Clarify Optional vs. Mandatory VOI**
   - voi_search.py is optional (graceful fallback if import fails)
   - discovery_funnel.py is recommended but not strictly required
   - If VOI computation unavailable, system falls back to FIFO queue ordering
   - Master doc should clarify this is a feature, not a requirement

---

### B2. Research Queue Architecture (REVISE §46, Queue Section)

**Priority**: P1
**Type**: REVISE EXISTING SECTION
**Estimated Effort**: 4–6 hours (clarification + planned features)
**Dependencies**: A1, B1 (VOI framework)
**Code Impact**: YES — Requires implementation of get_next_highest_voi_target()

**Location in Master Doc**: Wherever §46 or the queue architecture is described (likely under "What the System Tracks")

**Current Issues**:
- Queue service described as storing targets but no mention of prioritization
- get_next_target() returns FIFO; no mention of VOI-based ordering
- CollectorProfile exists but context (domain, expertise) not integrated into target assignment

**Revisions Needed**:

1. **Replace FIFO with VOI-Ranked Targeting**
   - Old: get_next_target(collector_id) → unassigned target in order added
   - New: get_next_highest_voi_target(collector_id) → unassigned target with highest VOI_adjusted
   - Implement: Sort self._targets by voi_adjusted descending; return first unassigned (or unclaimed after >timeout)

2. **Add method: prioritized_targets_by_voi(collector_id=None)**
   - Returns ordered list of unassigned targets ranked by VOI_adjusted
   - Optional collector_id filter: if provided, filter to targets collector can access (based on can_access_databases, paywalled)
   - Used for UI display and batch claims

3. **Add method: update_target_voi(target_id, new_voi)**
   - Called by discovery_funnel when gap is closed/partially closed
   - Updates ResearchTarget.voi_score
   - Triggers queue re-ranking on next claim

4. **Add method: claim_target_with_researcher_context(collector_id, gap_id=None)**
   - Current: claim_target(collector_id) claims next available target
   - New: Optionally accept gap_id to claim a specific target
   - Both versions should use VOI-ranked selection

5. **Document Fallback Behavior**
   - If VOI scores unavailable or all zeros: fall back to FIFO
   - If collector has no preferred_domains: use universal ranking
   - If collector profile incomplete: use partial fit factor (missing fields = neutral)

---

### B3. Gap Predictor Section (REVISE gap_predictor Docs)

**Priority**: P1
**Type**: REVISE EXISTING SECTION
**Estimated Effort**: 3–4 hours (clarification)
**Dependencies**: B1, B2 (VOI context)
**Code Impact**: NO (documentation only)

**Location in Master Doc**: Wherever gap prediction is described (likely Part III or description of gap_predictor.py)

**Current Issues**:
- Describes 6 gap types (Mediation, Mechanism, Boundary, Direction, Validation, Interaction) clearly
- Describes Walton critical questions and attack vulnerability detectors
- But doesn't explain VOI integration (currently hardcoded 0.5; should call VOIGapScorer)
- Doesn't explain integration with queue (how predicted gaps become targets)

**Revisions Needed**:

1. **Add subsection: Gap Detection Workflow**
   - find_all_gaps(max_gaps) → List[PredictedGap]
   - Each gap includes: gap_id, gap_type, description, suggested_search, confidence, voi_score (default 0.5)
   - Gaps flow to ResearchQueueService.refresh_queue()
   - refresh_queue() converts gaps → ResearchTarget objects
   - Targets stored in _targets dict with VOI scores

2. **Document the 6 Gap Types with Examples**
   - Mediation gaps: Missing direct relationships (currently describes)
   - Mechanism gaps: Missing explanations (currently describes)
   - [Continue for other 4 types...]
   - Each type should include: detection heuristic, example, typical VOI range

3. **Clarify VOI Score Computation for Gap Predictor**
   - Current: voi_score = 0.5 (default for all gaps)
   - Intended: If VOIGapScorer available, compute actual epistemic_voi + structural_voi
   - Components: uncertainty (low if widely known gap), centrality (high if affects core beliefs), sparsity (high if few sources)
   - Gap predictor should accept optional VOI scorer as dependency injection

4. **Argumentation-Based Gap Detection (Walton + Attack Vulnerabilities)**
   - find_critical_question_gaps(): Uses Walton argumentation framework critical questions
   - find_argument_attack_gaps(): 4 attack vulnerability detectors
   - These are already implemented; clarify in doc:
     - When each is used
     - What gaps each produces
     - Typical confidence scores for each

---

### B4. Interpretation Space Section (CLARIFY/MARK ASPIRATIONAL)

**Priority**: P1
**Type**: CLARIFY/MARK ASPIRATIONAL
**Estimated Effort**: 2–3 hours (audit + decision)
**Dependencies**: A6 (Overseer schema decision)
**Code Impact**: YES IF implementation chosen (see design decision below)

**Location in Master Doc**: Wherever interpretation_space is discussed (likely a section on zone classification or annotation)

**Current Issues**:
- Audit found interpretation_space is aspirational: phase2-4 outputs are JSON/markdown in a data directory, but no table insertion code
- overseer_management.py queries interpretation_space_suggestions table that doesn't exist
- Unclear whether interpretation_space is still under development or deferred

**Revisions Needed**:

1. **Add note: Implementation Status (March 2, 2026)**
   - Current: Phase 2–4 interpretation space outputs exist in file system but no database backend
   - Assumption: Interpretation space is aspirational; full backend not implemented

2. **Two Options (Requires Panel Decision)**
   - **Option A: Complete the Implementation**
     - Implement interpretation_space_suggestions table (see A6)
     - Wire phase2-4 outputs to insert rows into table
     - Overseer queries will work as designed
     - Effort: ~20 hours development
     - Timeline: Phase 2 implementation
   - **Option B: Mark as Aspirational**
     - Document interpretation_space as future-state design
     - Remove or mark overseer queries that reference undefined tables
     - Phase 2–4 outputs remain offline (filesystem-based)
     - Effort: ~2 hours documentation

3. **Zone Classification (If Interpretation Space Stays)**
   - If Option A: Implement zone classification using warrant-derived credence (per §48.3B)
   - Zone 1 (Known Interior): credence > 0.65, supported by empirical edges
   - Zone 2 (Active Boundary): credence 0.45–0.65 or depends heavily on theory
   - Zone 3 (Periphery): credence 0.30–0.45
   - Zone 4 (Uncharted): insufficient warrant structure

---

## PART C: TOPICS FOR PANEL REVIEW

### C1. VOI Weighting Across Epistemic and Structural Components

**Priority**: P1
**Type**: DESIGN DECISION
**Panel**: Spohn (ranking theory), Pearl (causal inference), information scientist
**Current State**: VOI calculated as 0.5 * epistemic_voi + 0.5 * structural_voi (see voi_search.py, line 184)
**Design Question**:
- Should epistemic VOI (uncertainty, centrality, sparsity on belief) be weighted equally with structural VOI (position in network, dependency count)?
- Pearl's perspective: Structural importance (influence on downstream beliefs) might dominate
- Spohn's perspective: Epistemic strength (how certain are we) should modulate structural importance
- Information scientist: Domain-specific weighting may be better than uniform 0.5–0.5

**Recommendation for Decision**:
- Conduct 2–3 expert panel discussions
- Pilot with differential weightings (0.3–0.7, 0.5–0.5, 0.7–0.3)
- Measure outcome: do different weightings change queue prioritization meaningfully?
- Document chosen weighting in master doc with rationale

---

### C2. Researcher Taxonomy: Dimensions and Granularity

**Priority**: P1
**Type**: DESIGN DECISION
**Panel**: Cognitive science methodology expert, HCI researcher, domain librarian
**Current State**: CollectorProfile exists with basic fields (expertise_level, preferred_domains) but not empirically validated
**Design Question**:
- What are the minimal dimensions needed for researcher-specific VOI adjustment?
- Current proposal (Section A2): domain, expertise, theoretical_alignment, access, closure_history
- Alternatives: Add more granular measures (publication productivity, theoretical school, preferred evidence types)?
- Realism check: Can practitioners reliably self-report these dimensions?

**Recommendation for Decision**:
- Panel reviews proposed CollectorProfile extensions (A2)
- Consider empirical calibration: do finer-grained profiles improve closure rates?
- Recommendation: Start with 5 dimensions (A2 proposal); add more only if pilot shows improvement

---

### C3. Search Automation Threshold

**Priority**: P1
**Type**: DESIGN DECISION
**Panel**: Information scientist, risk assessment expert, system reliability engineer
**Current State**: AutomatedQueueSearcher exists but is opt-in; no automatic triggering mechanism
**Design Question**:
- At what VOI_adjusted score should automated search be triggered without human review?
- Proposal: T_auto = 0.65 (default); gaps above this are auto-searched, below are queued for manual review
- Risk: Lower thresholds increase search volume, resource costs, but capture more potential discoveries
- Upper thresholds reduce false positives, but gaps of modest interest never get searched

**Recommendation for Decision**:
- Panel reviews proposed thresholds: 0.50, 0.60, 0.65, 0.70, 0.75
- Consider resource constraints (API rate limits, storage)
- Empirical test: Run searcher with different thresholds for 1 month; measure gap closure rates
- Document chosen threshold and review schedule (should be tuned quarterly)

---

### C4. Closed Feedback Loop Frequency and Responsiveness

**Priority**: P2
**Type**: DESIGN DECISION
**Panel**: System reliability engineer, queue management expert
**Current State**: Discovery funnel designed to track closure, but frequency of VOI revision and re-ranking not specified
**Design Question**:
- When should closure assessment trigger queue re-ranking?
  - Immediately (as soon as paper ingested): Responsive but computationally expensive
  - Batch (hourly or daily): Less responsive but more efficient
  - On-demand (only when researcher requests re-ranking): Manual control
- Should STALE gaps (untouched for >7 days) decay automatically, or require manual review?

**Recommendation for Decision**:
- Panel recommends: Batch re-ranking (hourly) + manual decay review (weekly)
- Configure decay rate: 0.1 per week staleness (e.g., 7-day gap: VOI *= 0.9)
- Implement gradual deprecation, not hard cutoff

---

## PART D: CROSS-REFERENCES AND INTEGRATION POINTS

### D1. Related Documents (Must Be Kept in Sync)

The following documents are referenced or must be coordinated with the master doc revisions:

| Document | Current Status | Integration Notes |
|-----------|----------------|-------------------|
| AUDIT_RECOMMENDATION_FLOW_2026-03-02.md | Current audit | Source of all findings; should be referenced in master doc as audit trail |
| OVERSEER_MANAGEMENT_LAYER_2026-03-02.md | Separate doc | Describes overseer layer; coordinates with A6 (schema definition) |
| PANEL_COHERENCE_THRESHOLDS_2026-03-02.md | Separate doc | Documents theory entrenchment values; used in §48.3B warrant strength calculation |
| contracts/schemas/extraction_quality_rules.json | Config file | Validator rules for extracted findings; referenced in A3 (Search Execution Pipeline) |
| queue/models.py | Code (CollectorProfile) | Schema source for researcher-specific VOI (A2); must be updated if CollectorProfile extended |
| src/services/gap_predictor.py | Code (gap detection) | Source of PredictedGap objects; VOI hardcoding documented in B3 |
| src/services/voi_search.py | Code (VOI scoring) | Core VOI computation; referenced in B1, A1 |
| src/queue/service.py | Code (queue management) | Implements queue prioritization; must be updated per B2 |
| src/services/discovery_funnel.py | Code (funnel tracking) | Lifecycle tracking; closure assessment design in A5 |
| src/queue/automated_searcher.py | Code (search execution) | Searcher bot; orchestration in A3 |
| src/services/paper_integration/orchestrator.py | Code (integration) | Ingestion pipeline; closure assessment integration point in A5 |

---

### D2. Schema and Contract Dependencies

The following contracts/schemas must be updated or created to support revisions:

| Schema File | Current Status | Needed Changes |
|-------------|----------------|----------------|
| contracts/schemas/extraction_quality_rules.json | Exists | No changes needed; referenced in A3 |
| (New) contracts/schemas/interpretation_space_schema.json | MISSING | Create if A6 Option A (full implementation) chosen |
| (New) contracts/schemas/overseer_alerts_schema.json | MISSING | Create if A6 Option A chosen; defines alert types, thresholds |
| queue/models.py (CollectorProfile dataclass) | Exists, partial | Extend with: expertise_level, domain_interests, theoretical_alignment, research_stage, access_level, closure_rate_by_gap_type |
| (New) researcher_fit_schema.json | MISSING | Define researcher_fit_factor calculation schema if used in production code |

---

## PART E: IMPLEMENTATION ROADMAP

### Phase 1 (Immediate, Required for Correctness)

**Timeline**: 2–3 weeks
**Effort**: 40–50 hours
**Deliverables**:
1. Write A1 (VOI Integration Architecture)
2. Write A3 (Search Execution Pipeline)
3. Revise B1 (VOI Computation Details)
4. Revise B2 (Queue Architecture)
5. Revise B3 (Gap Predictor Section)
6. Panel decision on C1, C2, C3

**Code Changes**:
- Implement get_next_highest_voi_target() in ResearchQueueService
- Update gap_predictor to accept optional VOI scorer
- Clarify when QueryGenerator is used vs. FallbackQueryGenerator

---

### Phase 2 (Important, Builds on Phase 1)

**Timeline**: 2–3 weeks
**Effort**: 30–40 hours
**Deliverables**:
1. Write A2 (Researcher-Specific VOI)
2. Write A5 (Discovery Funnel Feedback Loop)
3. Implement researcher_fit_factor() function
4. Implement closure assessment → VOI revision cycle
5. Revise B4 (Interpretation Space) with panel decision

**Code Changes**:
- Extend CollectorProfile with new fields
- Implement researcher_fit_factor() in queue/service.py
- Update discovery_funnel to compute closure_fraction and trigger VOI revision
- If A6 Option A chosen: implement interpretation_space_suggestions table

---

### Phase 3 (Nice-to-Have, Future)

**Timeline**: 3–4 weeks
**Effort**: 20–30 hours
**Deliverables**:
1. Write A4 (QA System as Recommendation Source)
2. Write A6 (Overseer Management Schema) — if Option A chosen
3. Implement QA→SearchGap integration
4. Implement full overseer monitoring (if chosen)

**Code Changes**:
- Wire ArbitraryQAHandler into search recommendation flow
- Create/populate interpretation_space_suggestions table
- Implement overseer_management queries for backlog tracking

---

## PART F: SUMMARY TABLE

| Item | Type | Priority | Effort (hrs) | Dependencies | Code Impact |
|------|------|----------|--------------|--------------|-------------|
| A1. VOI Integration Architecture | NEW | P1 | 8–10 | None | Yes |
| A2. Researcher-Specific VOI | NEW | P1 | 6–8 | A1 | Yes |
| A3. Search Execution Pipeline | NEW | P1 | 8–10 | A1, A2 | Yes |
| A4. QA as Recommendation Source | NEW | P2 | 4–6 | A1, A3 | Yes |
| A5. Discovery Funnel Feedback Loop | NEW | P1 | 6–8 | A1, A3 | Yes |
| A6. Overseer Schema | NEW | P1 | 6–8 | None | Yes (if implemented) |
| B1. VOI Computation Details (Revise) | REVISE | P1 | 4–6 | A1 | No |
| B2. Queue Architecture (Revise) | REVISE | P1 | 4–6 | A1, B1 | Yes |
| B3. Gap Predictor (Revise) | REVISE | P1 | 3–4 | B1, B2 | No |
| B4. Interpretation Space (Clarify) | CLARIFY | P1 | 2–3 | A6 | Yes (if Option A) |
| C1. VOI Weighting | PANEL | P1 | — | A1 | No |
| C2. Researcher Taxonomy | PANEL | P1 | — | A2 | No |
| C3. Search Automation Threshold | PANEL | P1 | — | A3 | No |
| C4. Feedback Loop Frequency | PANEL | P2 | — | A5 | No |

**Total Documentation Effort (Phases 1–2)**: ~70–90 hours
**Total Code Implementation Effort** (rough estimate): ~40–60 hours
**Panel Review Effort**: ~10–15 hours (3–5 panel sessions)

---

## PART G: NOTES FOR DAVID

1. **The Core Problem**: The audit revealed that VOI is computed but not used for queue prioritization, and researcher-specific context is completely absent. The master doc (correctly) emphasizes epistemic foundations but says little about the operational article-discovery pipeline.

2. **Why This Matters**: Without VOI integration and researcher-specific adjustments, the system recommends searches in FIFO order (oldest first) regardless of importance, and treats all researchers identically. This fails your design principle: "before we can recommend to a researcher that they pursue a topic, we need researcher-specific VOI."

3. **Phase 1 vs. Phase 2 vs. Phase 3**: Phase 1 is required to document and implement what was intended. Phase 2 adds researcher personalization (your stated requirement). Phase 3 (QA system integration, overseer monitoring) is nice-to-have infrastructure.

4. **Panel Review Needs**: Four design decisions require expert panel input (C1–C4). These should be scheduled once Phase 1 documentation is ready. Recommend: 2 panel sessions, each ~1.5–2 hours.

5. **Integration Dependency**: All revisions depend on understanding A1 (VOI Integration Architecture) first. This is the lynchpin — once this is documented and agreed, the rest follows naturally.

---

**Report Generated**: 2026-03-02
**Revision List Version**: 1.0
**Recommended Action**: Schedule 30-minute sync with David to review this list, prioritize panels, and approve Phase 1 scope.
