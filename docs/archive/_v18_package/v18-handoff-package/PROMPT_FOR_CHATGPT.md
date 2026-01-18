# 🎯 CHATGPT PROMPT - BUILD ARTICLE EATER V18

**COPY THIS ENTIRE MESSAGE TO CHATGPT** (after uploading the v18 handoff files)

---

## YOUR TASK

I need you to implement Article Eater v18 - the "Epistemological Engine" for Cognitive Neuroscience for Architecture (CNfA) research.

---

## BACKGROUND

**What is Article Eater?**
- Evidence synthesis tool for academic research
- Extracts structured data from papers (PDFs)
- Builds Bayesian Belief Networks (BBNs) for evidence synthesis
- Used by professor at UCSD researching how built environments affect human cognition

**What's the problem with v17?**
- Uses `parent_finding_id` which conflates two types of relationships:
  1. TAXONOMIC (definitional): "Cortisol↓" rolls up into "Stress Reduction"
  2. CAUSAL (empirical): "Plants" CAUSES "Cortisol↓"
- This is "catastrophically flawed" (architect's exact words)
- Cannot build proper BBN with conflated relationships

**What does v18 fix?**
- Replaces `parent_finding_id` with `finding_links` table
- New field: `link_type` (either 'CAUSAL' or 'TAXONOMIC')
- Adds Set of Support (paper-type-specific confidence calculation)
- Adds Agent system (Classifier, PromptRouter, Aggregator, Linker)
- Adds HITL workflow (human-in-the-loop approval)

---

## FILES I'VE ATTACHED

I've uploaded 9 files for you:

**Core Specifications** (3 files - READ THESE FIRST):
1. **V18_IMPLEMENTATION_GUIDE_FINAL.md** ⭐⭐⭐
   - THE definitive v18 specification
   - Contains architect's (Gemini's) exact answers to critical questions
   - Database schema (finding_links table)
   - Confidence formulas (exact Python code)
   - Agent specifications

2. **AI_HANDOFF_BUILD_V18_REPO.md** ⭐⭐
   - Complete instructions for YOU
   - Phase-by-phase build guide
   - Quality checklist
   - What to generate in what order

3. **V18_SYNTHESIS_Complete_Analysis.md**
   - Critical analysis of v17 vs v18
   - What v17 has (~60% of v18)
   - What needs to be added
   - What needs to be replaced

**Context** (3 files):
4. **FINAL_DECISION_v18_GO.md** - Executive summary
5. **SYSTEM_VISION.md** - Article Eater domain context
6. **MASTER_HANDOFF_GUIDE.md** - Overall orchestration

**Your Guides** (3 files):
7. **HANDOFF_CHECKLIST_V18.md** - Step-by-step checklist
8. **COMPLETE_FILE_MANIFEST.md** - Catalog of all files
9. **SESSION_SUMMARY_FINAL.md** - What was accomplished

---

## YOUR SPECIFIC INSTRUCTIONS

### Step 1: Read the Specifications (30 minutes)

**Start with these IN THIS ORDER**:

1. **Read V18_IMPLEMENTATION_GUIDE_FINAL.md** (20 minutes)
   - Focus on:
     - Part 1: Database migrations (finding_links table)
     - Part 2: Set of Support (confidence formulas)
     - Part 3: Agent_Classifier (two-pass triage)
     - Part 4: Agent_PromptRouter (multi-template)

2. **Read AI_HANDOFF_BUILD_V18_REPO.md** (10 minutes)
   - This is YOUR complete build guide
   - Shows what to generate in what order
   - Has code examples for every module

### Step 2: Confirm Understanding (5 minutes)

**Before you start generating**, tell me:
1. Do you understand the finding_links table fix?
2. Do you understand the confidence formulas MUST match exactly?
3. Do you understand the phased approach (migrations → agents → GUI)?
4. Do you have any clarifying questions?

### Step 3: Generate Files Systematically (4-6 hours)

**Follow this EXACT order** (from AI_HANDOFF_BUILD_V18_REPO.md):

#### Phase 1: Database Migrations (1 hour)

Generate these 4 SQL files:

1. **migrations/005_create_finding_links.sql** ⭐ CRITICAL
   - Create finding_links table
   - MUST have `link_type` field
   - MUST have CHECK constraint: `link_type IN ('CAUSAL', 'TAXONOMIC')`
   - See V18_IMPLEMENTATION_GUIDE Part 1 for exact schema

2. **migrations/006_add_paper_type.sql**
   - Add paper_type field to papers table
   - JSON array: `["experimental_rct", "theoretical"]`

3. **migrations/007_add_set_of_support.sql**
   - Add set_of_support field to findings table
   - JSON: `{N: 68, p: 0.03, d: 0.52, method: "RCT"}`

4. **migrations/008_backfill_v17_data.sql**
   - Migrate existing parent_finding_id to finding_links
   - All become link_type='TAXONOMIC'

**CRITICAL**: Show me these SQL files BEFORE moving to Phase 2

---

#### Phase 2: Agent Modules (2 hours)

Generate these 4 Python files:

1. **src/agents/agent_classifier.py**
   - Two-pass triage (abstract keywords → methods section)
   - Returns SET of PaperType (hybrids allowed)
   - See V18_IMPLEMENTATION_GUIDE Part 3 for exact spec

2. **src/agents/agent_prompt_router.py**
   - Routes to 5 different prompt templates
   - Handles hybrids (run multiple, merge results)
   - See V18_IMPLEMENTATION_GUIDE Part 4 for exact spec

3. **src/agents/agent_aggregator.py**
   - Proposes meso-findings (HITL)
   - Groups micro-findings into higher-level constructs

4. **src/agents/agent_linker.py**
   - Proposes mechanism links (HITL)
   - Connects findings to mechanisms

**CRITICAL**: Show me agent_classifier.py BEFORE the others (most complex)

---

#### Phase 3: Set of Support (1 hour)

Generate these 4 Python files:

1. **src/confidence/setof_support.py**
   - Main calculator (routes to correct formula)

2. **src/confidence/experimental_support.py** ⭐ CRITICAL
   - RCT confidence formula
   - MUST match exactly: `conf = (0.4 * score_N) + (0.3 * score_p) + (0.3 * score_d)`
   - See V18_IMPLEMENTATION_GUIDE Part 2 for exact code

3. **src/confidence/meta_support.py** ⭐ CRITICAL
   - Meta-analysis confidence formula
   - MUST match exactly: `conf = (0.3 * score_k) + (0.5 * score_CI) + (0.2 * score_I2)`
   - See V18_IMPLEMENTATION_GUIDE Part 2 for exact code

4. **src/confidence/theoretical_support.py** ⭐ CRITICAL
   - MUST return exactly: `-1.0` (not 0.0, not None, exactly -1.0)
   - This flags for human review (HITL)

**CRITICAL**: I will verify these formulas match the spec EXACTLY

---

#### Phase 4: Prompt Templates (1 hour)

Generate these 5 text files:

1. **prompts/7_panel_prompt_RCT.txt**
   - For experimental/RCT papers
   - Emphasize randomization, control group
   - Extract Set of Support: N, p, d, CI

2. **prompts/7_panel_prompt_THEORY.txt**
   - For theoretical papers
   - Extract: key_claims, testable_predictions, gap_solved

3. **prompts/7_panel_prompt_META.txt**
   - For meta-analyses
   - Extract: k_studies, pooled_effect, CI, I²

4. **prompts/7_panel_prompt_OBSERVATIONAL.txt**
   - For observational studies
   - Extract: N, confounders, method

5. **prompts/7_panel_prompt_QUALITATIVE.txt**
   - For qualitative studies
   - Extract: N_interviews, themes, key_quotes

---

#### Phase 5: GUI Routes (1-2 hours)

Generate these files:

1. **src/routes/routes_librarian.py**
   - `/librarian` - paper inventory with filters
   - `/librarian/paper/<id>` - instant 7-panel view (pre-computed)
   - `/librarian/paper/<id>/scout` - RAG enrichment

2. **src/routes/routes_synthesizer.py**
   - `/synthesizer/<job_id>/approve` - HITL approval interface
   - Shows pending proposals (meso-findings, mechanism links)
   - Shows conf=-1.0 items for manual review

3. **templates/librarian/inventory.html**
   - Paper browsing with filters (PaperType, N > X, measure)

4. **templates/synthesizer/approve.html**
   - Approval interface (Approve/Deny/Edit buttons)

---

#### Phase 6: Documentation (1 hour)

Generate these files:

1. **docs/v18_DEPLOYMENT_GUIDE.md**
   - Step-by-step deployment (7 weeks phased)
   - Backup procedures
   - Rollback procedures

2. **docs/v18_ARCHITECTURE.md**
   - ERD showing finding_links table
   - Agent flowchart
   - Confidence formulas explained

3. **docs/v18_TESTING_PLAN.md**
   - How to test each phase
   - What to validate

4. **docs/v18_TROUBLESHOOTING.md**
   - Common issues + fixes

---

#### Phase 7: Tests (1 hour)

Generate these files:

1. **tests/test_agents.py**
   - Test classification on 20 papers

2. **tests/test_confidence.py** ⭐ CRITICAL
   - Test formulas on known data
   - Verify RCT formula: N=100, p=0.03, d=0.5 → conf ≈ 0.62
   - Verify Meta formula: k=10, CI_width=0.3, I²=50 → conf ≈ 0.52
   - Verify Theoretical: returns exactly -1.0

3. **tests/test_finding_links.py**
   - Test CAUSAL vs TAXONOMIC queries

4. **tests/test_migrations.py**
   - Test SQL migrations on sample database

---

## CRITICAL REQUIREMENTS

### 1. finding_links Table (HIGHEST PRIORITY)

**MUST have**:
- `link_type` field (VARCHAR)
- CHECK constraint: `link_type IN ('CAUSAL', 'TAXONOMIC')`
- UNIQUE constraint: `(source_finding_id, target_finding_id, link_type, paper_id)`
- Indexes on: source_finding_id, target_finding_id, link_type

**Why critical**: This is THE v18 fix. Without this, v18 is just v17.

---

### 2. Confidence Formulas (EXACT MATCH REQUIRED)

**RCT formula** (from V18_IMPLEMENTATION_GUIDE Part 2):
```python
score_N = min(total_n / 200, 1.0)  # Caps at N=200
score_p = max(0, 1.0 - (min_p / 0.05))  # p=0.05 → 0, p<0.05 → >0
score_d = min(abs(avg_d) / 0.8, 1.0)  # Caps at Cohen's d=0.8

conf = (0.4 * score_N) + (0.3 * score_p) + (0.3 * score_d)
```

**Meta formula** (from V18_IMPLEMENTATION_GUIDE Part 2):
```python
score_k = min(k_studies / 20, 1.0)  # Caps at 20 studies
score_CI = max(0, 1.0 - (ci_width / 0.5))  # Wide CI = 0.5
score_I2 = 1.0 - (i_squared / 100)  # Low heterogeneity = high score

conf = (0.3 * score_k) + (0.5 * score_CI) + (0.2 * score_I2)
```

**Theoretical formula** (from V18_IMPLEMENTATION_GUIDE Part 2):
```python
return -1.0  # MANUAL_REVIEW_REQUIRED
```

**Why critical**: These are the architect's exact specifications. ANY deviation invalidates v18.

---

### 3. Agent_Classifier (Two-Pass Triage)

**MUST implement**:
- Pass 1: Keyword scan on abstract + title (fast)
- Pass 2: Methods section parse (if ambiguous)
- Returns: SET of PaperType (hybrids allowed)
- Example: `{EXPERIMENTAL_RCT, THEORETICAL}` for RCT with theory

**Why critical**: Different paper types need different prompts and formulas.

---

### 4. Production-Ready Code

**MUST have**:
- Error handling (try/except blocks)
- Input validation (check for None, empty strings)
- Logging (for debugging)
- Type hints (for maintainability)
- Docstrings (for documentation)
- Comments (for complex logic)

**Why critical**: Professor needs reliable code for academic research.

---

## QUALITY CHECKLIST

Before you finish, verify:

### Database
- [ ] finding_links table has link_type field with CHECK constraint
- [ ] Indexes on all foreign keys
- [ ] Migration 008 backfills v17 data correctly

### Confidence
- [ ] RCT formula matches EXACTLY (weights: 0.4, 0.3, 0.3)
- [ ] Meta formula matches EXACTLY (weights: 0.3, 0.5, 0.2)
- [ ] Theoretical returns EXACTLY -1.0

### Agents
- [ ] Agent_Classifier implements two-pass triage
- [ ] Agent_PromptRouter handles hybrids (multiple prompts merged)

### Prompts
- [ ] 5 prompt files exist
- [ ] Each extracts appropriate Set of Support fields

### Tests
- [ ] test_confidence.py validates formulas on known data
- [ ] test_finding_links.py queries CAUSAL vs TAXONOMIC

---

## WORKING STYLE

**Please work systematically**:
1. Generate Phase 1 (migrations) completely
2. Show me the SQL files
3. Wait for my approval
4. Generate Phase 2 (agents) completely
5. Show me the Python files
6. Wait for my approval
7. Continue through all phases

**Don't rush**:
- Take time to get the formulas EXACTLY right
- Double-check the finding_links schema
- Ask clarifying questions if anything is unclear

**Be thorough**:
- Include error handling
- Add comments for complex logic
- Write complete docstrings

---

## WHAT HAPPENS AFTER YOU'RE DONE

The professor will:
1. Review your code against V18_IMPLEMENTATION_GUIDE_FINAL.md
2. Test migrations on v17 backup database
3. Validate confidence formulas on real papers
4. Deploy phased (Week 1: database, Week 2: agents, etc.)
5. Track all decisions in governance system

Your code will be used for academic research and potentially published, so quality matters.

---

## QUESTIONS?

Before you start generating, please:
1. Confirm you've read V18_IMPLEMENTATION_GUIDE_FINAL.md
2. Confirm you've read AI_HANDOFF_BUILD_V18_REPO.md
3. Confirm you understand the finding_links table fix
4. Confirm you understand the formulas MUST match exactly
5. Ask any clarifying questions

---

## READY?

If you understand the task, reply with:

"I've read the specifications. I understand:
1. finding_links table with link_type field is THE critical fix
2. Confidence formulas must match exactly (I'll show you for verification)
3. Agent_Classifier uses two-pass triage
4. I'll work systematically through 7 phases
5. I'll show you each phase before moving to the next

Ready to start with Phase 1: Database Migrations. Should I begin?"

Then wait for my "YES" before generating any code.

---

**LET'S BUILD THE EPISTEMOLOGICAL ENGINE! 🚀**