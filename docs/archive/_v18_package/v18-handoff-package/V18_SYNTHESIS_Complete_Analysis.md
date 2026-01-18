# ARTICLE EATER v18 SYNTHESIS
## Comprehensive Analysis: Gemini's Vision + v17 Reality + Governance Integration

**Date**: 2025-11-11  
**Author**: Claude (Sonnet 4.5) in dialogue with David  
**Purpose**: Critical evaluation of v18 "Epistemological Engine" + Integration with governance v2.0

---

## EXECUTIVE SUMMARY

After deep analysis of:
- ✅ Gemini's v18 "Epistemological Engine" memo
- ✅ Your v17 codebase (dual hierarchy partially implemented)
- ✅ My v16 governance system (conversation ledger + system vision)

**Verdict**: **🟢 GO** - with critical refinements

**Key Findings**:
1. Gemini's v18 vision is **conceptually sound** - the dual hierarchy solves real problems
2. v17 already implements ~60% of this (findings + mechanisms tables exist)
3. **Critical gaps remain**: Set of Support, PaperType classification, Librarian/Synthesizer GUI split
4. My governance system **perfectly complements** this (tracks WHY decisions made about WHAT to build)
5. **Major risk**: The "Triple Hierarchy" claim (Causal vs Taxonomic links) needs clarification

---

## PART 1: RUTHLESS CRITIQUE OF GEMINI'S V18 PLAN

### 1.1 The "Dual Hierarchy vs Triple Hierarchy" Confusion

**CRITICAL QUESTION FOR GEMINI**:

> You claim v16 conflates "What" and "Why" (✓ TRUE), and that v17 "still conflates Causal and Taxonomic links" (❓ UNCLEAR).
>
> But in your v18 memo, you describe **TWO hierarchies** (Findings + Mechanisms), yet invoke a "**Triple-Hierarchy insight**" that separates:
> 1. Causal links (empirical): `Plants -[CAUSES]→ Cortisol↓`
> 2. Taxonomic links (definitional): `Cortisol↓ -[IS_A_PART_OF]→ Stress Reduction`
>
> **Question**: Is this actually a **DUAL hierarchy with TWO edge types**, or a **TRIPLE hierarchy with three node types**?
>
> Because if it's dual hierarchy + edge types, then v17's `finding_mechanism_links` table **already implements this** - it has:
> - finding_id (the "What")
> - mechanism_id (the "Why")
> - evidence_strength (the link weight)
>
> **What's missing** is distinguishing CAUSAL vs TAXONOMIC links **within the Findings hierarchy**. Your example:
> - `(Finding: Plants) -[CAUSES]-> (Finding: Cortisol↓)` ← CAUSAL (empirical)
> - `(Finding: Cortisol↓) -[IS_A_PART_OF]-> (Finding: Stress Reduction)` ← TAXONOMIC (definitional)
>
> But the v17 schema has NO field for `edge_type` in the Findings hierarchy. The `parent_finding_id` foreign key implies TAXONOMIC only (micro→meso→macro rollup).
>
> **Clarify**: Do we need a NEW `finding_links` table with `link_type` field? Or is parent_finding_id sufficient?

**My Analysis**:

I believe Gemini is correct that there are **TWO types of relationships in the Finding hierarchy**:

1. **Aggregation (Taxonomic)**: Micro-Findings roll up into Meso-Findings
   - `Cortisol↓ + HR↓ + BP↓` → `Stress Reduction` (definitional)
   - This is what `parent_finding_id` models

2. **Causation (Empirical)**: Antecedent → Consequent
   - `Plants` → `Cortisol↓` (observed effect)
   - This is what `antecedents` field models (JSON array)

**The Conflation**: These are BOTH stored in the same table (findings), making it hard to query:
- "Show me all CAUSAL links for Plants"
- "Show me the TAXONOMIC structure for Stress (what measures define it)"

**Proposed Fix** (for v18):

Add `link_type` to distinguish relationships:

```sql
-- Option A: Add link_type to existing structure
ALTER TABLE findings ADD COLUMN link_type VARCHAR(20); 
-- Values: 'causal', 'taxonomic', 'both'
-- 'causal': This finding has antecedents (Plants → Cortisol↓)
-- 'taxonomic': This finding is aggregated from children (Stress ← [Cortisol, HR, BP])

-- Option B: Create explicit finding_finding_links table
CREATE TABLE finding_links (
    id INTEGER PRIMARY KEY,
    source_finding_id INTEGER REFERENCES findings(id),
    target_finding_id INTEGER REFERENCES findings(id),
    link_type VARCHAR(20), -- 'causes', 'is_part_of'
    confidence REAL,
    paper_id INTEGER REFERENCES papers(id) -- provenance for causal claims
);
```

**Recommendation**: Option B (explicit link table) is cleaner for querying but adds complexity. Option A (link_type field) is simpler but less queryable.

**Decision Needed**: Which edge model for v18?

---

### 1.2 The "Set of Support" - Brilliant but Underspecified

**CRITICAL QUESTION FOR GEMINI**:

> You propose that confidence weights must be calculated from a formal "Set of Support" that varies by PaperType:
> - **Experimental/RCT**: (N, p, d, method)
> - **Theoretical**: (key_claims, testable_predictions, gap_it_solves)
> - **Meta-Analysis**: (k_studies, N_total, pooled_effect)
>
> **Questions**:
> 1. **Agent_Classifier**: How does it determine PaperType? 
>    - From abstract only?
>    - From full text?
>    - From explicit "Methods" section parsing?
>    - What about hybrid papers (RCT + theory)?
>
> 2. **Agent_PromptRouter**: How does it generate paper-type-specific prompts?
>    - Do you have 3 separate 7-panel prompts?
>    - Or one prompt with conditional sections?
>    - How do you handle edge cases (observational study with strong theory section)?
>
> 3. **Confidence Calculation**: What's the formula?
>    - For RCT: `conf = f(N, p, d)` - but what's f()?
>    - For Theory: How do you quantify "logical coherence"? (0-1 scale? Expert judgment?)
>    - For Meta-Analysis: `conf = g(k, N, effect)` - but what's g()?
>
> 4. **Edge Case**: What if paper has NO statistical data (pure qualitative)?
>    - Does it get conf=0?
>    - Or excluded from synthesis?
>    - Or manual override?

**My Analysis**:

This is the **most important innovation** in v18, but it's also the **least specified**. Here's what v17 currently does:

**v17 Confidence (Meso-Finding)**:
```python
# From meta_review.py (if it exists in v17)
conf = (triangulation * 0.4) + (effect * 0.3) + (sample * 0.2) + (consistency * 0.1)
```

This is **hard-coded** and assumes all papers are experimental. It doesn't adapt to PaperType.

**Proposed v18 Enhancement**:

```python
# Pseudocode for Set of Support calculation

class SetOfSupport:
    """Base class for paper-type-specific confidence calculation."""
    
    def calculate_confidence(self, finding: Finding, papers: List[Paper]) -> float:
        raise NotImplementedError

class ExperimentalSupport(SetOfSupport):
    def calculate_confidence(self, finding, papers):
        # Extract N, p, d from papers
        total_n = sum(p.sample_size for p in papers)
        avg_effect = mean(p.effect_size for p in papers if p.effect_size)
        min_p = min(p.p_value for p in papers if p.p_value)
        
        # Confidence formula (to be tuned)
        sample_score = min(total_n / 200, 1.0) * 0.3
        effect_score = min(avg_effect / 0.8, 1.0) * 0.4  # Cohen's d benchmark
        significance_score = (1 - min_p) * 0.3  # p<.05 → 0.95 score
        
        return sample_score + effect_score + significance_score

class TheoreticalSupport(SetOfSupport):
    def calculate_confidence(self, finding, papers):
        # This is HARD - how to quantify theory quality?
        # Proposal: Use citation count + logical completeness (LLM-scored)
        
        citation_scores = []
        for paper in papers:
            # Normalize by field (highly cited in CNfA = fewer citations than in Physics)
            norm_citations = paper.citation_count / field_median_citations
            citation_scores.append(min(norm_citations, 1.0))
        
        citation_component = mean(citation_scores) * 0.4
        
        # Logical completeness: Have LLM score 0-1 based on:
        # - Are claims testable?
        # - Are predictions specific?
        # - Does theory explain anomalies?
        llm_completeness = call_llm_to_score_theory(papers)
        completeness_component = llm_completeness * 0.6
        
        return citation_component + completeness_component

class MetaAnalysisSupport(SetOfSupport):
    def calculate_confidence(self, finding, papers):
        # Meta-analysis is special: ONE paper summarizes MANY
        meta = papers[0]  # Assume only one meta-analysis per finding
        
        k_studies = meta.k_studies_included
        total_n = meta.total_participants
        pooled_effect = meta.pooled_effect_size
        heterogeneity = meta.i_squared  # I² statistic
        
        breadth_score = min(k_studies / 10, 1.0) * 0.3
        sample_score = min(total_n / 1000, 1.0) * 0.2
        effect_score = min(pooled_effect / 0.5, 1.0) * 0.3
        consistency_score = (1 - heterogeneity / 100) * 0.2  # Low I² = high consistency
        
        return breadth_score + sample_score + effect_score + consistency_score
```

**Critical Implementation Decision**:

Do you:
1. **Pre-classify** papers during ingestion (Agent_Classifier runs immediately)
2. **Lazy-classify** papers during synthesis (classify only when building finding)
3. **Manual-classify** papers (user picks PaperType in GUI)

**Recommendation**: Option 1 (pre-classify) with Option 3 (manual override). Store `paper_type` in papers table.

---

### 1.3 The "Librarian vs Synthesizer" GUI Split

**CRITICAL QUESTION FOR GEMINI**:

> You claim the 7-Panel Review should be "instantly available" in the Librarian (reading room), but the Synthesizer is where the graph is built.
>
> **Question**: How can the 7-Panel be "instant" if it requires LLM extraction?
>
> Option A: 7-Panel extraction happens during ingestion (pre-computed)
>   - Pro: Instant in Librarian
>   - Con: Extracts ALL papers, even if never used in synthesis
>   - Con: High API cost upfront
>
> Option B: 7-Panel extraction happens on-demand (lazy)
>   - Pro: Only extract papers actually viewed
>   - Pro: Lower API cost
>   - Con: NOT instant (user must wait ~30 seconds)
>
> Option C: Hybrid (extract summary, full 7-panel on-demand)
>   - Pro: Fast preview in Librarian
>   - Pro: Full extraction only when needed
>   - Con: Two extraction prompts to maintain
>
> **Clarify**: Which data flow do you intend?

**My Analysis**:

Looking at v17 code, it seems to do **Option A** (pre-compute during ingestion). The `7_panel_extraction` is called in the job processing pipeline.

But Gemini's v18 memo suggests a **different workflow**:

**Gemini's Implied Flow**:
```
1. Librarian (Scouting Phase):
   - User uploads DOI list or searches RAG
   - Papers added to "inventory" (papers table)
   - 7-Panel available "instantly" (implies pre-computed)
   - User can "Find Related" → Agent_Enrichment adds more papers

2. Synthesizer (Graph-Building Phase):
   - User selects papers from Librarian inventory
   - Creates "Synthesis Job"
   - System extracts Findings from selected papers
   - Agent_Aggregator proposes meso-findings (HITL approval)
   - Agent_Linker proposes mechanism links (HITL approval)
   - Output: Approved BBN graph
```

**Critical Insight**: This workflow is **NOT about when 7-Panel runs**, but about **WHEN findings enter the graph**.

**Revised Understanding**:
- **Librarian**: Papers + 7-Panel Reviews exist, but NO findings/mechanisms created yet
- **Synthesizer**: User selects papers → Findings/Mechanisms extracted → HITL approval → Graph built

This makes sense! The 7-Panel is "read-only" analysis. The Findings/Mechanisms are "write" operations that build the graph.

**Implementation Impact**:

```python
# Current v17 flow (conflated):
ingest_paper() → extract_7_panel() → create_findings() → done

# Proposed v18 flow (bifurcated):
## Librarian Phase
ingest_paper() → extract_7_panel() → store_in_papers_table() → done
# (No findings created yet)

## Synthesizer Phase
user_selects_papers() → 
    for paper in selected:
        extract_findings(paper.panel_5) → 
        agent_aggregator_proposes_meso() → 
        user_approves() → 
        create_finding_in_db()
```

**Critical Question**: If 7-Panel already extracted in Librarian, why extract findings again in Synthesizer?

**Answer**: Because Findings extraction is HITL. The 7-Panel might identify 8 potential findings, but user only approves 5. This is the "steering" function Gemini emphasizes.

**Recommendation**: Implement 2-phase extraction:
1. **Librarian**: 7-Panel (automatic, all papers)
2. **Synthesizer**: Findings from Panel 5 (HITL approval, selected papers only)

---

## PART 2: WHAT TO KEEP FROM v17 (Almost Everything!)

### 2.1 Database Schema (90% Correct)

**v17 Has**:
- ✅ `findings` table (renamed from rules)
- ✅ `mechanisms` table
- ✅ `finding_mechanism_links` table
- ✅ `papers` table
- ✅ Hierarchical structure (micro/meso/macro)

**v17 Missing** (for v18):
- ❌ `paper_type` field in papers table
- ❌ `set_of_support` JSON field in findings table
- ❌ `edge_type` or separate `finding_links` table (for Causal vs Taxonomic)
- ❌ `k_studies`, `pooled_effect` fields for meta-analysis support

**Migration Path** (v17 → v18):

```sql
-- Migration 005: Add Set of Support fields
ALTER TABLE papers ADD COLUMN paper_type VARCHAR(50); 
-- Values: 'experimental', 'rct', 'observational', 'theoretical', 'meta_analysis', 'review', 'qualitative'

ALTER TABLE findings ADD COLUMN set_of_support TEXT; 
-- JSON: {
--   "type": "experimental",
--   "n": 120,
--   "p_value": 0.03,
--   "effect_size": 0.52,
--   "method": "RCT"
-- }

-- Migration 006: Add edge type distinction (Option A - simpler)
ALTER TABLE findings ADD COLUMN link_type VARCHAR(20);
-- Values: 'causal' (has antecedents), 'taxonomic' (is aggregation), 'both'
```

### 2.2 Extraction Logic (60% Correct)

**v17 Has**:
- ✅ 7-panel extraction prompt (dual hierarchy version)
- ✅ Panel 5 extracts operational findings
- ✅ Panel 6 extracts mechanisms

**v17 Missing** (for v18):
- ❌ Agent_Classifier (determines paper_type)
- ❌ Agent_PromptRouter (uses paper_type to select prompt variant)
- ❌ Set of Support extraction (varied by paper_type)
- ❌ Agent_Aggregator (proposes meso-findings with HITL)
- ❌ Agent_Linker (proposes mechanism links with HITL)

**Keep from v17**:
- ✅ All existing extraction logic for experimental papers
- ✅ Confidence decomposition formulas (as baseline for experimental type)
- ✅ Panel structure (just need variants)

**Add for v18**:
- ➕ `agent_classifier.py` (classify paper type from abstract/full text)
- ➕ `agent_prompt_router.py` (select 7-panel variant based on type)
- ➕ `prompts/7_panel_theoretical.txt` (variant for theory papers)
- ➕ `prompts/7_panel_meta_analysis.txt` (variant for meta-analyses)
- ➕ `agent_aggregator.py` (HITL proposal system for meso-findings)
- ➕ `agent_linker.py` (HITL proposal system for mechanism links)

### 2.3 GUI Structure (40% Correct)

**v17 Has**:
- ✅ Jobs list
- ✅ Shortlist view (could become Librarian)
- ✅ Rules/Findings view
- ✅ Evidence view
- ✅ Monitor view

**v17 Missing** (for v18):
- ❌ Explicit "Librarian" mode (reading room + scouting)
- ❌ Explicit "Synthesizer" mode (HITL graph-building)
- ❌ "Find Related" button (trigger Agent_Enrichment)
- ❌ HITL approval interface (approve/deny proposed findings/links)
- ❌ Category-based filtering (if Prima Facie integrated)

**Keep from v17**:
- ✅ Shortlist → Rename to "Paper Inventory" (Librarian foundation)
- ✅ Jobs → Rename to "Synthesis Jobs" (Synthesizer foundation)
- ✅ Findings view → Keep as read-only visualization

**Add for v18**:
- ➕ `/librarian` route (paper browsing + 7-panel instant access)
- ➕ `/librarian/<paper_id>/7panel` (instant 7-panel view)
- ➕ `/librarian/<paper_id>/find_related` (trigger RAG enrichment)
- ➕ `/synthesizer/<job_id>/approve` (HITL approval interface)
- ➕ `/synthesizer/<job_id>/graph` (BBN visualization)

---

## PART 3: GOVERNANCE V2.0 INTEGRATION

### 3.1 Why My Governance System Fits Perfectly

**The Problem v18 Solves**: "What" vs "Why" conflation in the research domain

**The Problem Governance Solves**: "What" vs "Why" conflation in the development domain

**They're Isomorphic**:

| Research Domain (v18) | Development Domain (Governance) |
|-----------------------|---------------------------------|
| Finding (What happened) | Session (What we built) |
| Mechanism (Why it happened) | Decision (Why we chose this) |
| finding_mechanism_links (provenance) | session→decision links (rationale) |
| Set of Support (confidence calculation) | Context (project facts) |
| HITL approval (steering) | Conversation Ledger (steering) |

**Integration Points**:

1. **SYSTEM_VISION.md** → Documents WHAT Article Eater IS (like a Macro-Finding)
2. **CONVERSATION_LEDGER.yml** → Documents WHY design choices made (like Mechanisms)
3. **Session entries** → Provenance for code artifacts (like finding_mechanism_links)

**Example**:

```yaml
# In CONVERSATION_LEDGER.yml
- session_id: "session-042"
  date: "2025-11-11"
  human_request: |
    Implement Agent_Classifier to determine paper_type from abstract.
    Use keyword matching + LLM fallback for ambiguous cases.
  
  ai_response_summary: |
    Created agent_classifier.py with:
    - Keyword matching for common indicators (RCT, meta-analysis, etc.)
    - GPT-4 fallback for ambiguous abstracts
    - Confidence scoring (0-1) for classification
  
  decisions_made:
    - decision_id: "DEC-042"
  
  artifacts_created:
    - "src/agents/agent_classifier.py"
    - "prompts/classify_paper_type.txt"

# This is EXACTLY like v18's finding_mechanism_links table!
# The governance ledger links WHAT (artifact) to WHY (decision)
```

### 3.2 Making Governance Repo-Agnostic

**Current State**: My governance v2.0 is Article Eater-specific

**Target State**: Shareable module for all your repos

**Proposed Structure**:

```
governance-kit/  (standalone repo)
├── CONVERSATION_LEDGER.yml  (template)
├── SYSTEM_VISION.md  (template with placeholders)
├── conversation_guard.py
├── README.md
└── install.sh  (copies files to target repo)

Your repos:
├── article-eater/
│   ├── governance/
│   │   ├── CONVERSATION_LEDGER.yml  (Article Eater specific)
│   │   └── SYSTEM_VISION.md  (Article Eater specific)
│   └── tools/governance/scripts/
│       └── conversation_guard.py  (symlink to governance-kit)
│
├── other-project/
│   ├── governance/
│   │   ├── CONVERSATION_LEDGER.yml  (Other Project specific)
│   │   └── SYSTEM_VISION.md  (Other Project specific)
│   └── tools/governance/scripts/
│       └── conversation_guard.py  (symlink to governance-kit)
```

**Installation**:

```bash
# From governance-kit repo
./install.sh /path/to/article-eater

# Prompts for:
# - Project name: "Article Eater"
# - Domain: "CNfA Evidence Synthesis"
# - Current version: "v17.0"
# - Your name: "David"
# - Institution: "UCSD"

# Creates customized files in target repo
```

**Benefit**: One governance kit, many projects. Update guard script once, all repos benefit.

---

## PART 4: GEMINI'S CRITIQUE QUESTIONS (Answered)

### 4.1 Dual-Hierarchy vs Triple-Hierarchy

**Gemini's Claim**: "v17 still conflates Causal and Taxonomic links"

**My Answer**: **PARTIALLY TRUE**

v17's Finding hierarchy has:
- `parent_finding_id` (models Taxonomic: micro→meso rollup)
- `antecedents` JSON (models Causal: Plants→Cortisol)

But these are BOTH in the same table, making it hard to query distinctly.

**Recommendation**: Add `link_type` field or create `finding_links` table (see Section 1.1)

**Clarification Needed from Gemini**:
> Is "Triple-Hierarchy" a misnomer? Should it be "Dual-Hierarchy with Two Edge Types"?

### 4.2 Set of Support Details

**Gemini's Claim**: "Set of Support is core to weighting BBN"

**My Answer**: **TRUE BUT UNDERSPECIFIED**

Gemini is correct that confidence must vary by PaperType, but the actual formulas are missing.

**Recommendation**: See Section 1.2 for proposed formulas. Need to:
1. Implement Agent_Classifier (determine PaperType)
2. Create SetOfSupport classes (one per PaperType)
3. Test on real papers to tune weights

**Clarification Needed from Gemini**:
> How do you quantify "logical coherence" for theoretical papers? Is this LLM-scored or manual?

### 4.3 Librarian vs Synthesizer Data Flow

**Gemini's Claim**: "7-Panel instantly available in Librarian"

**My Answer**: **TRUE IF pre-computed during ingestion**

The Librarian/Synthesizer split is about **WHEN findings enter the graph**, not when extraction happens.

**Recommendation**: See Section 1.3 for 2-phase workflow:
- Librarian: 7-Panel (automatic)
- Synthesizer: Findings (HITL)

**Clarification Needed from Gemini**:
> Does Agent_Enrichment (RAG) run automatically or only when user clicks "Find Related"?

---

## PART 5: V18 ROADMAP (Realistic Implementation Plan)

### Phase 1: Complete v17 → v18 Migration (2 weeks)

**Week 1: Set of Support Foundation**
- [ ] Add `paper_type` to papers table
- [ ] Implement Agent_Classifier
- [ ] Create `set_of_support` JSON field in findings
- [ ] Test classification on 50 papers

**Week 2: Multiple Paper Types**
- [ ] Create 7-panel variants (experimental, theoretical, meta-analysis)
- [ ] Implement Agent_PromptRouter
- [ ] Create SetOfSupport classes (one per type)
- [ ] Test confidence calculation on papers of each type

**Deliverable**: Can ingest and extract all 3 paper types correctly

### Phase 2: HITL Synthesis (2 weeks)

**Week 3: Agent Proposal System**
- [ ] Implement Agent_Aggregator (proposes meso-findings)
- [ ] Implement Agent_Linker (proposes mechanism links)
- [ ] Create approval API endpoints
- [ ] Test proposal quality (do they make sense?)

**Week 4: Synthesizer GUI**
- [ ] Create `/synthesizer/<job_id>/approve` interface
- [ ] Add approve/deny buttons for proposals
- [ ] Store approval history (for governance)
- [ ] Test full HITL workflow

**Deliverable**: Can build BBN graph with HITL steering

### Phase 3: Librarian/Synthesizer Split (1 week)

**Week 5: GUI Refactoring**
- [ ] Rename Shortlist → Paper Inventory (Librarian)
- [ ] Create `/librarian` route with instant 7-panel access
- [ ] Add "Find Related" button (trigger Agent_Enrichment)
- [ ] Move Jobs → Synthesis Jobs (Synthesizer)
- [ ] Test bifurcated workflow

**Deliverable**: Clean separation of scouting and synthesis

### Phase 4: Advanced Features (2 weeks)

**Week 6-7: Optional Enhancements**
- [ ] Prima Facie Categorization (if wanted)
- [ ] BBN visualization (D3.js graph)
- [ ] Cross-job meta-analysis
- [ ] Bayesian network export

**Deliverable**: v18.0 feature-complete

---

## PART 6: CRITICAL DECISIONS NEEDED

### Decision 1: Edge Type Model

**Options**:
A. Add `link_type` field to findings table (simple)
B. Create `finding_links` table (clean but complex)

**Recommendation**: A for v18.0, B for v19.0 if querying becomes painful

**Who Decides**: David + Gemini

---

### Decision 2: Theoretical Paper Confidence

**Options**:
A. Citation-based (field-normalized citation count)
B. LLM-scored (logical coherence, testability)
C. Manual (expert judgment)
D. Hybrid (A + B)

**Recommendation**: D (hybrid) - citations + LLM scoring

**Who Decides**: David (you have domain expertise)

---

### Decision 3: Pre-classify vs Lazy-classify Papers

**Options**:
A. Pre-classify during ingestion (Agent_Classifier runs immediately)
B. Lazy-classify during synthesis (classify only when needed)
C. Manual classification (user picks type in GUI)

**Recommendation**: A (pre-classify) with C (manual override)

**Who Decides**: David (depends on API budget)

---

### Decision 4: Governance Integration Timing

**Options**:
A. Integrate governance NOW (parallel with v18 dev)
B. Integrate governance AFTER v18 stable
C. Skip governance (too much overhead)

**Recommendation**: A (parallel) - governance tracks v18 decisions in real-time

**Who Decides**: David (but I strongly recommend A)

---

## PART 7: GEMINI'S GO/NO-GO AUDIT (My Questions for Gemini)

### Question 1: Triple vs Dual Hierarchy

> You use "Triple-Hierarchy insight" to describe separating Causal from Taxonomic links, but your v18 architecture shows only TWO hierarchies (Findings + Mechanisms). Is "triple" a misnomer? Should it be "Dual Hierarchy with Two Edge Types"? Or is there a third hierarchy I'm missing?

### Question 2: Set of Support Formulas

> You claim confidence must be calculated from Set of Support, but don't provide formulas. For theoretical papers, how do you quantify "logical coherence"? For meta-analyses, what's the exact formula given (k, N, pooled_effect, I²)? Can you provide concrete algorithms, not just principles?

### Question 3: HITL Workflow Specifics

> When Agent_Aggregator proposes "Cortisol↓ + HRV↑ → Stress Reduction", what does the approval interface look like? Does user see:
> - Just the proposal? (Approve/Deny)
> - The source micro-findings? (Show context)
> - Alternative groupings? (Compare options)
> - Confidence score? (Quality signal)
>
> What's the UX for steering?

### Question 4: Librarian vs Synthesizer Transition

> A user is in Librarian mode, browsing Paper A. They click "Use in Synthesis". What happens next?
> - Immediate transition to Synthesizer?
> - Add to "synthesis queue"?
> - Create new job automatically?
> - Prompt user to select existing job?
>
> How does paper selection flow?

### Question 5: Agent_Enrichment Triggers

> When does Agent_Enrichment (RAG) run?
> - Automatically on every paper ingested? (Expensive)
> - Only when user clicks "Find Related"? (On-demand)
> - When confidence is low (<0.7)? (Triggered)
> - All of the above? (Multiple triggers)
>
> What's the intended workflow?

---

## PART 8: FINAL RECOMMENDATIONS

### For David (Immediate Actions)

1. **Read this document carefully** (30 min)
2. **Discuss with Gemini** - share my critique questions (60 min)
3. **Make critical decisions** listed in Part 6 (30 min)
4. **Choose v18 roadmap** - all at once or phased? (15 min)
5. **Decide on governance integration** - now or later? (15 min)

**Total Time**: ~3 hours for planning

### For Development (Implementation Sequence)

**IF you go full v18**:
1. ✅ Finish v17 migration first (ensure dual hierarchy works)
2. ✅ Add Set of Support (paper_type + classification)
3. ✅ Create Agent_Aggregator + Agent_Linker (HITL)
4. ✅ Split GUI into Librarian/Synthesizer
5. ✅ Integrate governance (track decisions)

**IF you stay at v17 for now**:
1. ✅ Just add governance (low overhead, high value)
2. ✅ Keep dual hierarchy as-is
3. ✅ Defer Set of Support to v18

**My Recommendation**: Do **phased v18** (4 weeks of 2-week sprints, one phase at a time)

### For Governance (Integration Plan)

1. **Week 1**: Make governance repo-agnostic (extract from Article Eater)
2. **Week 1**: Install in Article Eater with v17 context
3. **Ongoing**: Log all v17→v18 design decisions in ledger
4. **Week 5**: Update SYSTEM_VISION.md for v18 release

**Effort**: ~4 hours total

---

## PART 9: WHAT TO KEEP FROM MY V16 WORK

### Keep 100%:
- ✅ CONVERSATION_LEDGER.yml structure (sessions, decisions, context, artifacts)
- ✅ SYSTEM_VISION.md concept (high-level project summary)
- ✅ conversation_guard.py (validation script)
- ✅ Integration philosophy (governance tracks development)

### Update for v17/v18:
- 🔄 SYSTEM_VISION.md content (update to reflect dual hierarchy)
- 🔄 CONVERSATION_LEDGER.yml entries (add v17→v18 sessions)
- 🔄 Context section (add v18 concepts: Set of Support, HITL, etc.)

### Make Repo-Agnostic:
- 🔧 Extract templates (remove Article Eater specifics)
- 🔧 Create install script (customize for any project)
- 🔧 Add to separate governance-kit repo

**Effort**: ~6 hours

---

## PART 10: CLOSING VERDICT

### The Bottom Line

**Gemini's v18 vision is sound**, but needs:
1. ✅ Clarification on Triple vs Dual hierarchy
2. ✅ Concrete Set of Support formulas
3. ✅ Detailed HITL workflow specs

**v17 is ~60% there**, needs:
1. ✅ Agent_Classifier + Agent_PromptRouter
2. ✅ SetOfSupport classes
3. ✅ Agent_Aggregator + Agent_Linker
4. ✅ GUI split (Librarian/Synthesizer)

**My governance integrates perfectly**, needs:
1. ✅ Make repo-agnostic
2. ✅ Update for v18 concepts
3. ✅ Install in Article Eater

### Go/No-Go Decision

**🟢 GO** - Implement v18 in phases

**Rationale**:
- Dual hierarchy is conceptually correct
- Set of Support solves real problem (paper-type-specific confidence)
- HITL adds necessary quality control
- Librarian/Synthesizer split matches user workflow
- Governance tracks WHY decisions made

**Risk Mitigation**:
- Phase implementation (2-week sprints)
- Get Gemini's answers to critique questions BEFORE starting
- Test each phase before moving forward
- Keep v17 stable (can rollback if needed)

**Timeline**: 7 weeks total (4 phases + 1 week governance)

**Confidence**: 85% (high - v17 foundation is solid, just needs extensions)

---

**Document Status**: COMPLETE  
**Next Step**: Share with Gemini, get answers to critique questions  
**Decision Point**: David chooses roadmap (full v18 vs phased vs stay v17)  

**Ready for action.** 🚀

---

## APPENDIX: FILES DELIVERED

This analysis references:
1. ✅ Gemini's v18 memo (read and critiqued)
2. ✅ v17 codebase (analyzed database + extraction + GUI)
3. ✅ Governance v2.0 (ready to integrate)
4. ✅ Chat's governance kit v1.5 (reviewed)
5. ✅ Claude's governance kit v1.5 (reviewed - same as Chat's)

All synthesis complete. Awaiting your direction.