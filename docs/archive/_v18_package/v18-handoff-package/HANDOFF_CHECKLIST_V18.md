# ✅ HANDOFF CHECKLIST - GET V18 IMPLEMENTATION CODE

**Goal**: Get complete Article Eater v18 implementation from new AI instance  
**Time**: 6-8 hours (AI: 4-6 hours, you: 2 hours review)

---

## STEP 1: PREPARE FILES TO UPLOAD (10 minutes)

Download these files from this chat:

### Essential (4 files - MUST HAVE):

- [ ] [V18_IMPLEMENTATION_GUIDE_FINAL.md](computer:///mnt/user-data/outputs/V18_IMPLEMENTATION_GUIDE_FINAL.md) - Gemini's answers
- [ ] [V18_SYNTHESIS_Complete_Analysis.md](computer:///mnt/user-data/outputs/V18_SYNTHESIS_Complete_Analysis.md) - Critical analysis
- [ ] [FINAL_DECISION_v18_GO.md](computer:///mnt/user-data/outputs/FINAL_DECISION_v18_GO.md) - Executive summary
- [ ] [AI_HANDOFF_BUILD_V18_REPO.md](computer:///mnt/user-data/outputs/AI_HANDOFF_BUILD_V18_REPO.md) - Instructions for AI

### Critical (1 file - v17 codebase):

- [ ] Article_Eater_v17_0_real_with_UPGRADE_not_sure_if_dual_concatenated.txt (you have this)

### Recommended (3 files - context):

- [ ] [SYSTEM_VISION.md](computer:///mnt/user-data/outputs/SYSTEM_VISION.md) - Article Eater overview
- [ ] Gemini_handoff_explanation.docx (you have this) - Original v18 memo
- [ ] Claudes_questions_to_gemini_and_its_answers.docx (you have this) - Full Q&A

---

## STEP 2: START NEW AI INSTANCE (2 minutes)

**Option A: New Claude Chat** (Recommended)
- Open https://claude.ai
- Start new chat
- Upload 7-8 files

**Option B: Gemini**
- Open https://gemini.google.com
- Start new chat
- Upload 7-8 files

**Option C: ChatGPT**
- Open https://chat.openai.com
- Start new chat
- Upload 7-8 files (may have file limit)

---

## STEP 3: SEND MAGIC PROMPT (2 minutes)

**Copy this EXACTLY**:

```
I need you to implement Article Eater v18 from complete specifications.

CONTEXT:
Article Eater is an evidence synthesis tool for Cognitive Neuroscience for 
Architecture (CNfA). It extracts data from academic papers to build Bayesian 
Belief Networks.

CRITICAL PROBLEM v18 FIXES:
v17 uses parent_finding_id which conflates TWO types of relationships:
1. TAXONOMIC (rollup): Cortisol↓ aggregates into "Stress Reduction"
2. CAUSAL (effect): Plants CAUSES Cortisol↓

This is "catastrophically flawed" (architect's words) - cannot build BBN.

v18 SOLUTION:
- finding_links table with link_type field (CAUSAL vs TAXONOMIC)
- Set of Support (paper-type-specific confidence calculation)
- Agent_Classifier (detect if paper is RCT, Theory, Meta-Analysis)
- Agent_PromptRouter (different 7-panel prompts per paper type)
- HITL workflow (human approves agent proposals)

I'm attaching:
1. V18_IMPLEMENTATION_GUIDE_FINAL.md (architect's definitive answers)
2. V18_SYNTHESIS_Complete_Analysis.md (critical analysis + what v17 has)
3. FINAL_DECISION_v18_GO.md (executive summary)
4. AI_HANDOFF_BUILD_V18_REPO.md (complete instructions for you)
5. v17 codebase (what exists, what to extend)
6. Context docs (domain knowledge, original memo)

YOUR TASK:
Read AI_HANDOFF_BUILD_V18_REPO.md first (complete build instructions).
Then generate ALL v18 implementation files:

- 4 SQL migrations (finding_links, paper_type, set_of_support, backfill)
- 4 agent modules (Classifier, PromptRouter, Aggregator, Linker)
- 3 confidence classes (Experimental, Meta, Theoretical)
- 5 prompt templates (RCT, Theory, Meta, Observational, Qualitative)
- 2 route modules (Librarian, Synthesizer)
- HTML templates (inventory, approval interface)
- Documentation (deployment, architecture, testing, troubleshooting)
- Test suite

CRITICAL REQUIREMENTS:
- finding_links MUST have link_type field (CAUSAL vs TAXONOMIC)
- Confidence formulas MUST match architect's exact specifications:
  * RCT: conf = (0.4*N) + (0.3*p) + (0.3*d)
  * Meta: conf = (0.3*k) + (0.5*CI) + (0.2*I²)
  * Theory: conf = -1.0 (HITL required)
- Agent_Classifier MUST implement two-pass triage (keywords → methods)
- Production-ready code (error handling, validation, comments)

Generate files systematically starting with migrations.
Ask clarifying questions if anything is unclear.

Ready? Please read AI_HANDOFF_BUILD_V18_REPO.md first, then confirm you 
understand the task before starting.
```

---

## STEP 4: GUIDE AI THROUGH GENERATION (4-6 hours)

AI will generate files in phases. For each phase:

### Phase 1: Database Migrations (1 hour)

**Expected files**:
- [ ] migrations/005_create_finding_links.sql
- [ ] migrations/006_add_paper_type.sql
- [ ] migrations/007_add_set_of_support.sql
- [ ] migrations/008_backfill_v17_data.sql

**Check**:
- [ ] finding_links has link_type field with CHECK constraint
- [ ] link_type is enum: 'CAUSAL', 'TAXONOMIC'
- [ ] CAUSAL links require paper_id (CHECK constraint)
- [ ] TAXONOMIC links have weight=1.0 (CHECK constraint)
- [ ] Indexes on source_finding_id, target_finding_id, link_type
- [ ] Backfill converts parent_finding_id to TAXONOMIC links

**If AI gets stuck**: Point to V18_IMPLEMENTATION_GUIDE Part 1

---

### Phase 2: Agent Modules (2 hours)

**Expected files**:
- [ ] src/agents/agent_classifier.py
- [ ] src/agents/agent_prompt_router.py
- [ ] src/agents/agent_aggregator.py
- [ ] src/agents/agent_linker.py

**Check Agent_Classifier**:
- [ ] Two-pass triage (abstract keywords → methods parse)
- [ ] Returns SET of PaperType (hybrids allowed)
- [ ] Uses Gemini's exact keyword lists
- [ ] Default to OBSERVATIONAL if ambiguous

**Check Agent_PromptRouter**:
- [ ] Routes to 5 different prompt files
- [ ] Handles hybrids (run multiple, merge panels)
- [ ] Example: [RCT, THEORETICAL] runs both prompts
- [ ] Merges: empirical (panels 3,4,5) + theory (panels 2,6)

**If AI gets stuck**: Point to V18_IMPLEMENTATION_GUIDE Part 2

---

### Phase 3: Set of Support (1 hour)

**Expected files**:
- [ ] src/confidence/setof_support.py (calculator)
- [ ] src/confidence/experimental_support.py
- [ ] src/confidence/meta_support.py
- [ ] src/confidence/theoretical_support.py

**Check Experimental formula** (CRITICAL):
```python
score_N = min(total_n / 200, 1.0)
score_p = max(0, 1.0 - (min_p / 0.05))
score_d = min(abs(avg_d) / 0.8, 1.0)
conf = (0.4 * score_N) + (0.3 * score_p) + (0.3 * score_d)
```

**Check Meta formula** (CRITICAL):
```python
score_k = min(k_studies / 20, 1.0)
score_CI = max(0, 1.0 - (ci_width / 0.5))
score_I2 = 1.0 - (i_squared / 100)
conf = (0.3 * score_k) + (0.5 * score_CI) + (0.2 * score_I2)
```

**Check Theoretical** (CRITICAL):
```python
return -1.0  # MANUAL_REVIEW_REQUIRED
```

**If formulas don't match**: STOP and correct. These are Gemini's exact specs.

---

### Phase 4: Prompt Templates (1 hour)

**Expected files**:
- [ ] prompts/7_panel_prompt_RCT.txt
- [ ] prompts/7_panel_prompt_THEORY.txt
- [ ] prompts/7_panel_prompt_META.txt
- [ ] prompts/7_panel_prompt_OBSERVATIONAL.txt
- [ ] prompts/7_panel_prompt_QUALITATIVE.txt

**Check RCT prompt**:
- [ ] Panel 4: Emphasizes randomization, control group, blinding
- [ ] Panel 5: Extracts N, p, d, CI, method as Set of Support

**Check Theory prompt**:
- [ ] Panel 2: Extracts key_claims, testable_predictions, gap_solved
- [ ] Panel 6: Extracts logical_coherence, explanatory_power

**Check Meta prompt**:
- [ ] Panel 5: Extracts k_studies, pooled_effect, CI, I²

---

### Phase 5: GUI Routes (1-2 hours)

**Expected files**:
- [ ] src/routes/routes_librarian.py
- [ ] src/routes/routes_synthesizer.py
- [ ] templates/librarian/inventory.html
- [ ] templates/librarian/paper_detail.html
- [ ] templates/synthesizer/approve.html
- [ ] static/css/librarian.css
- [ ] static/css/synthesizer.css
- [ ] static/js/approval.js

**Check Librarian**:
- [ ] /librarian route with filters (PaperType, N > X, measure)
- [ ] /librarian/paper/<id> shows 7-panel INSTANTLY (pre-computed)
- [ ] /librarian/paper/<id>/scout triggers RAG enrichment
- [ ] Gemini: "Instant means instant" (no 30-second wait)

**Check Synthesizer**:
- [ ] /synthesizer/<job_id>/approve shows pending proposals
- [ ] Shows meso-finding proposals (from Agent_Aggregator)
- [ ] Shows mechanism link proposals (from Agent_Linker)
- [ ] Shows conf=-1.0 items for manual review
- [ ] User can: Approve, Deny, Edit

---

### Phase 6: Documentation (1 hour)

**Expected files**:
- [ ] docs/v18_DEPLOYMENT_GUIDE.md
- [ ] docs/v18_ARCHITECTURE.md
- [ ] docs/v18_TESTING_PLAN.md
- [ ] docs/v18_TROUBLESHOOTING.md

**Check Deployment Guide**:
- [ ] Step-by-step for all 7 weeks
- [ ] Includes backup procedures
- [ ] Includes rollback procedures
- [ ] Includes validation tests

**Check Architecture Doc**:
- [ ] ERD showing finding_links table
- [ ] Agent flowchart (Classifier → Router → extraction)
- [ ] Confidence formulas explained
- [ ] Librarian vs Synthesizer split explained

---

### Phase 7: Tests (1 hour)

**Expected files**:
- [ ] tests/test_agents.py
- [ ] tests/test_confidence.py
- [ ] tests/test_finding_links.py
- [ ] tests/test_migrations.py

**Check tests**:
- [ ] test_agents.py classifies 20 real papers correctly
- [ ] test_confidence.py validates formulas on known data
- [ ] test_finding_links.py queries CAUSAL vs TAXONOMIC separately
- [ ] test_migrations.py runs on v17 backup without errors

---

## STEP 5: REVIEW GENERATED FILES (2 hours)

### Quick Review (30 minutes)

- [ ] All files from structure diagram exist
- [ ] Migrations have proper SQL syntax
- [ ] Agent classes implement Gemini's specs
- [ ] Confidence formulas match EXACTLY
- [ ] Prompts look comprehensive

### Deep Review (90 minutes)

**Database Migrations**:
- [ ] Run SQL linter on migrations
- [ ] Check foreign key constraints exist
- [ ] Verify CHECK constraints on link_type
- [ ] Confirm indexes on all searchable fields

**Agent_Classifier**:
- [ ] Test on 5 known papers manually:
  - [ ] RCT paper → correctly tagged
  - [ ] Theory paper → correctly tagged
  - [ ] Meta-analysis → correctly tagged
  - [ ] Hybrid (RCT+Theory) → both tags
  - [ ] Ambiguous → defaults to OBSERVATIONAL

**Confidence Formulas**:
- [ ] Run through example data:
  - [ ] N=100, p=0.03, d=0.5 → conf should be ~0.62
  - [ ] k=10, CI_width=0.3, I²=50 → conf should be ~0.52
  - [ ] Theoretical → conf should be exactly -1.0

**Prompts**:
- [ ] Read each prompt fully
- [ ] Check they extract correct Set of Support fields
- [ ] Check they emphasize appropriate methodology

**GUI**:
- [ ] Librarian has instant access (not lazy loading)
- [ ] Synthesizer has approve/deny buttons
- [ ] Templates use clear academic language
- [ ] No confusing UI elements

---

## STEP 6: TEST MIGRATIONS ON V17 BACKUP (1 hour)

### Create Test Database

```bash
# Backup v17 database
cp /path/to/article-eater/ae.db ae_v17_backup.db

# Copy for testing
cp ae_v17_backup.db ae_test.db
```

### Run Migrations

```bash
# Run migration 005 (finding_links)
sqlite3 ae_test.db < migrations/005_create_finding_links.sql

# Check table created
sqlite3 ae_test.db "SELECT sql FROM sqlite_master WHERE name='finding_links';"
# Should show: link_type field with CHECK constraint

# Run migration 006 (paper_type)
sqlite3 ae_test.db < migrations/006_add_paper_type.sql

# Run migration 007 (set_of_support)
sqlite3 ae_test.db < migrations/007_add_set_of_support.sql

# Run migration 008 (backfill)
sqlite3 ae_test.db < migrations/008_backfill_v17_data.sql

# Check backfill worked
sqlite3 ae_test.db "SELECT COUNT(*) FROM finding_links WHERE link_type='TAXONOMIC';"
# Should match: SELECT COUNT(*) FROM findings WHERE parent_finding_id IS NOT NULL;
```

### Validate Migrations

```bash
# Test CAUSAL vs TAXONOMIC query
sqlite3 ae_test.db << EOF
SELECT 
    link_type,
    COUNT(*) as count
FROM finding_links
GROUP BY link_type;
EOF

# Should show:
# TAXONOMIC | [number of parent_finding_id relationships]
# CAUSAL    | 0 (will be populated during ingestion)
```

### If Migration Fails ❌

- Go back to AI
- Say: "Migration 008 failed with error: [paste error]"
- AI will fix SQL and regenerate
- Re-test

---

## STEP 7: INTEGRATE WITH V17 CODEBASE (2 hours)

### Merge Files

```bash
cd /path/to/article-eater

# Backup v17 first
tar -czf article-eater-v17-backup.tar.gz .

# Copy v18 files (carefully, don't overwrite everything)
# Migrations
mkdir -p migrations
cp /path/to/v18/migrations/*.sql migrations/

# Agents (new directory)
mkdir -p src/agents
cp /path/to/v18/src/agents/*.py src/agents/

# Confidence (new directory)
mkdir -p src/confidence
cp /path/to/v18/src/confidence/*.py src/confidence/

# Models (UPDATE existing)
# CAREFUL: Don't overwrite good v17 models, just extend
cp -i /path/to/v18/src/models/*.py src/models/

# Routes (NEW files only)
cp /path/to/v18/src/routes/routes_librarian.py src/routes/
cp /path/to/v18/src/routes/routes_synthesizer.py src/routes/

# Prompts
mkdir -p prompts
cp /path/to/v18/prompts/*.txt prompts/

# Templates
cp -r /path/to/v18/templates/librarian templates/
cp -r /path/to/v18/templates/synthesizer templates/

# Docs
mkdir -p docs/v18
cp /path/to/v18/docs/*.md docs/v18/

# Tests
mkdir -p tests
cp /path/to/v18/tests/*.py tests/
```

### Update Dependencies

```bash
# Check if new dependencies needed
pip install -r requirements.txt

# Run tests
pytest tests/
```

---

## STEP 8: PHASED DEPLOYMENT (7 weeks)

### Week 1: Database Only

```bash
# Run migrations on production database (BACKUP FIRST!)
cp ae.db ae_pre_v18_backup.db

python scripts/migrate_v17_to_v18.py

# Validate
python tests/test_migrations.py

# If fails: Restore backup, fix issues, retry
```

### Week 2: Agents Only

```bash
# Test Agent_Classifier on 20 papers
python tests/test_agents.py

# If classification wrong: Tune keywords, re-test
```

### Week 3: Confidence Calculation

```bash
# Test formulas on real papers
python scripts/test_confidence_tuning.py

# If scores seem wrong: Tune weights (document in CONVERSATION_LEDGER)
```

### Weeks 4-7: GUI + HITL

```bash
# Deploy Librarian (Week 5)
# Deploy Synthesizer (Weeks 6-7)
# Test full HITL workflow
```

---

## STEP 9: TRACK IN GOVERNANCE (Throughout)

### Log Each Week's Session

```yaml
- session_id: "session-NNN"
  date: "2025-11-XX"
  human_request: |
    Week N of v18 implementation.
    [What you worked on]
  ai_response_summary: |
    [What got implemented]
  artifacts_created:
    - [List files]
  decisions_made:
    - decision_id: "DEC-NNN"  # If any tuning decisions
  next_steps_identified:
    - [Next week's work]
```

### Log Tuning Decisions

```yaml
- decision_id: "DEC-005"
  question: "Adjust confidence weight for sample size?"
  chosen: "Keep 0.4 weight for sample size (Gemini's original)"
  alternatives_considered:
    - option: "Increase to 0.5"
      rejected_because: "Testing on 50 papers showed 0.4 is optimal"
  rationale: |
    Tested confidence formulas on 50 real papers from corpus.
    Compared to expert judgment (David's assessment).
    0.4 weight for N produced closest match to expert ratings.
```

---

## SUCCESS CRITERIA

You'll know v18 worked when:

### Database
- [ ] finding_links table exists with link_type field
- [ ] Can query CAUSAL links separately from TAXONOMIC
- [ ] No parent_finding_id dependencies remain
- [ ] All v17 data migrated correctly

### Agents
- [ ] Agent_Classifier correctly identifies paper types
- [ ] Agent_PromptRouter uses correct prompts per type
- [ ] Hybrid papers get multiple prompts merged

### Confidence
- [ ] RCT papers get confidence from formula
- [ ] Meta papers get confidence from formula
- [ ] Theory papers get conf=-1.0 (manual review)
- [ ] Scores match expert judgment reasonably

### GUI
- [ ] Librarian shows 7-panel instantly (no wait)
- [ ] Librarian has filters working (PaperType, N, measure)
- [ ] Synthesizer shows proposals for approval
- [ ] HITL workflow works (approve/deny/edit)

### Overall
- [ ] Can ingest new paper → classified → extracted → conf calculated
- [ ] Can build BBN with HITL approval
- [ ] No "catastrophic conflation" (CAUSAL ≠ TAXONOMIC)
- [ ] System feels like "Epistemological Engine"

---

## TROUBLESHOOTING

### Issue: AI generates stub code (TODOs)

**Fix**: 
- Say: "Don't use TODOs. Actually implement [function] fully."
- Point to specific example in V18_IMPLEMENTATION_GUIDE

### Issue: Confidence formula doesn't match Gemini's

**Fix**: CRITICAL - formulas MUST match exactly
- Show Gemini's formula from V18_IMPLEMENTATION_GUIDE Part 2
- Say: "This MUST be exact. Regenerate with these weights."

### Issue: finding_links table missing link_type

**Fix**: CRITICAL - this is THE v18 fix
- Say: "The link_type field is the entire point of v18. Add CHECK constraint."
- Show example from V18_IMPLEMENTATION_GUIDE Part 1

### Issue: Migrations fail on v17 database

**Fix**:
- Check if v17 database has unexpected schema
- May need to adjust migration 008 backfill logic
- Test on fresh v17 backup

### Issue: AI generates too slowly

**Fix**:
- Ask: "Generate next 3 files in one response"
- Or: "Show me just the function signatures, I'll ask for implementations"

---

## ESTIMATED TIME

- Step 1 (Download files): 10 min
- Step 2 (Start AI): 2 min
- Step 3 (Send prompt): 2 min
- Step 4 (Guide AI): 4-6 hours
- Step 5 (Review): 2 hours
- Step 6 (Test migrations): 1 hour
- Step 7 (Integrate): 2 hours
- Step 8 (Deploy phased): 7 weeks (20-40 hours total)
- Step 9 (Track): 10 min per week

**Initial Build**: 9-11 hours  
**Deployment**: 7 weeks  
**Total**: ~50 hours over 7 weeks

---

## WHAT YOU'LL HAVE

At the end of initial build (Steps 1-7):

✅ Complete v18 implementation (code)  
✅ Tested migrations (on v17 backup)  
✅ All agent modules (Classifier, Router, Aggregator, Linker)  
✅ Set of Support classes (Experimental, Meta, Theoretical)  
✅ 5 prompt templates  
✅ Librarian/Synthesizer GUI  
✅ Documentation (deployment, architecture, testing)  
✅ Test suite  

Ready for phased deployment (Step 8).

At the end of deployment (7 weeks later):

✅ v18 running in production  
✅ finding_links working (CAUSAL vs TAXONOMIC)  
✅ Set of Support calculating confidence  
✅ HITL workflow operational  
✅ Can build proper BBN  
✅ "Epistemological Engine" realized  

---

**Ready to start!** 🚀

**Next**: Download files → Start new AI → Send magic prompt