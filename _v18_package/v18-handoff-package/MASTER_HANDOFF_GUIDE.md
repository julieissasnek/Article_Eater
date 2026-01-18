# 🎯 MASTER HANDOFF GUIDE - COMPLETE ARTICLE EATER v18 + GOVERNANCE

**Date**: 2025-11-11  
**Status**: COMPLETE - Ready for AI handoff  
**What this delivers**: Full v18 implementation + governance tracking system

---

## 📖 TABLE OF CONTENTS

1. [Quick Start (5 minutes)](#quick-start)
2. [What You're Getting](#what-youre-getting)
3. [Two-Track Approach](#two-track-approach)
4. [Files Required](#files-required)
5. [Handoff Workflow](#handoff-workflow)
6. [Quality Assurance](#quality-assurance)
7. [Deployment Strategy](#deployment-strategy)
8. [Inspection Protocol](#inspection-protocol)

---

## QUICK START

### If You Want Governance First (Recommended)

1. Download 5 files (see [Track 1 Files](#track-1-governance-kit))
2. Start new Claude chat
3. Upload files + paste [Governance Magic Prompt](#governance-magic-prompt)
4. Wait 2-3 hours (AI builds governance repo)
5. Test install, deploy to Article Eater
6. **THEN** do Track 2 (v18)

### If You Want v18 First

1. Download 8 files (see [Track 2 Files](#track-2-v18-implementation))
2. Start new Claude chat
3. Upload files + paste [v18 Magic Prompt](#v18-magic-prompt)
4. Wait 4-6 hours (AI builds v18)
5. Review, test migrations, integrate
6. **THEN** do Track 1 (governance) to track deployment

### If You Want Both Simultaneously

1. Start TWO AI instances (e.g., Claude + Gemini)
2. One builds governance (2-3 hours)
3. Other builds v18 (4-6 hours)
4. Both finish around same time
5. Install governance on Article Eater
6. Use governance to track v18 deployment

---

## WHAT YOU'RE GETTING

### 🎯 Track 1: Governance Kit v3.0

**What it is**: Universal conversation tracking system

**What it includes**:
- `CONVERSATION_LEDGER.yml` template
- `SYSTEM_VISION.md` template
- `install.sh` (one-command installer)
- `conversation_guard.py` (validation)
- Complete documentation
- 3 example projects
- Test suite

**Why you need it**:
- Solve "Intent Rot" (AI forgets between sessions)
- Track v18 implementation decisions as you go
- Load context into any new AI instance
- Document provenance for academic rigor

**Time to build**: 2-3 hours (AI) + 1 hour (you review)  
**Time to install**: 15 minutes  
**Repository size**: ~15-20 files, 50KB  

---

### 🚀 Track 2: Article Eater v18

**What it is**: Complete "Epistemological Engine" implementation

**What it includes**:
- 4 SQL migrations (finding_links table - THE CRITICAL FIX)
- 4 agent modules (Classifier, PromptRouter, Aggregator, Linker)
- 3 confidence classes (with Gemini's exact formulas)
- 5 prompt templates (one per paper type)
- Librarian/Synthesizer GUI split
- Complete documentation
- Test suite

**Why you need it**:
- Fixes v17's "catastrophic" parent_finding_id conflation
- Enables proper BBN construction (CAUSAL ≠ TAXONOMIC)
- Adds Set of Support (transparent confidence calculation)
- Adds HITL workflow (human approves proposals)

**Time to build**: 4-6 hours (AI) + 2 hours (you review)  
**Time to deploy**: 7 weeks (phased)  
**Repository size**: ~40-50 files, 200KB code  

---

## TWO-TRACK APPROACH

### Strategy: Governance THEN v18 (Recommended)

**Rationale**:
1. Build governance first (2-3 hours)
2. Install on Article Eater immediately
3. Start logging v18 sessions as you build it
4. Track all tuning decisions (confidence weights, etc.)
5. Full provenance from day 1

**Timeline**:
- Day 1: Build governance (4 hours)
- Day 2: Install governance + build v18 (8 hours)
- Day 3-4: Review v18, test migrations (8 hours)
- Weeks 1-7: Deploy v18 phased, log everything

**Advantage**: Complete audit trail of entire v18 development

---

### Strategy: v18 THEN Governance (Alternative)

**Rationale**:
1. Build v18 first (4-6 hours)
2. Start testing immediately
3. Build governance later (2-3 hours)
4. Backfill governance ledger with v18 sessions

**Timeline**:
- Day 1-2: Build v18 (10 hours)
- Day 3: Test v18 (4 hours)
- Day 4: Build governance + backfill (5 hours)
- Weeks 1-7: Deploy v18 phased

**Advantage**: Get to v18 code faster, document retroactively

**Disadvantage**: Have to backfill session logs (less rigorous)

---

### Strategy: Both Simultaneously (Ambitious)

**Rationale**:
1. Use TWO AI instances in parallel
2. One builds governance (Claude)
3. Other builds v18 (Gemini)
4. Both finish ~6 hours
5. Install governance immediately
6. Already have v18 ready to integrate

**Timeline**:
- Day 1: Both AIs work (6 hours max)
- Day 2: Review both, test both (6 hours)
- Day 3: Install governance, integrate v18 (4 hours)
- Weeks 1-7: Deploy v18 phased

**Advantage**: Fastest path to both systems operational

**Disadvantage**: Harder to supervise two AIs at once

---

## FILES REQUIRED

### Track 1: Governance Kit

**Essential (5 files)**:

1. [GOVERNANCE_KIT_v3_Repo_Agnostic.md](computer:///mnt/user-data/outputs/GOVERNANCE_KIT_v3_Repo_Agnostic.md)
   - Complete specification
   - What governance kit v3.0 IS and DOES
   - Size: 25KB

2. [CONVERSATION_LEDGER.template.yml](computer:///mnt/user-data/outputs/CONVERSATION_LEDGER.template.yml)
   - Template with {{placeholders}}
   - Exact structure AI must follow
   - Size: 5KB

3. [SYSTEM_VISION.template.md](computer:///mnt/user-data/outputs/SYSTEM_VISION.template.md)
   - Template with {{placeholders}}
   - Section structure for vision doc
   - Size: 9KB

4. [install.sh](computer:///mnt/user-data/outputs/install.sh)
   - Already-working installer
   - AI may refine for production
   - Size: 3KB

5. [conversation_guard.py](computer:///mnt/user-data/outputs/conversation_guard.py)
   - Validation script
   - AI should copy as-is
   - Size: 5KB

**Recommended (3 more)**:

6. [CONVERSATION_LEDGER.yml](computer:///mnt/user-data/outputs/CONVERSATION_LEDGER.yml)
   - Example output (Article Eater v2.0)
   - Shows what customized ledger looks like
   - Size: 12KB

7. [AI_HANDOFF_BUILD_GOVERNANCE_REPO.md](computer:///mnt/user-data/outputs/AI_HANDOFF_BUILD_GOVERNANCE_REPO.md)
   - Complete instructions for AI
   - File structure, quality checklist
   - Size: 15KB

8. [HANDOFF_CHECKLIST.md](computer:///mnt/user-data/outputs/HANDOFF_CHECKLIST.md)
   - Step-by-step guide for YOU
   - What to check at each phase
   - Size: 11KB

**Total**: 8 files, 85KB

---

### Track 2: v18 Implementation

**Essential (4 files)**:

1. [V18_IMPLEMENTATION_GUIDE_FINAL.md](computer:///mnt/user-data/outputs/V18_IMPLEMENTATION_GUIDE_FINAL.md)
   - Gemini's definitive answers
   - Database schema, confidence formulas, agent specs
   - Size: 29KB

2. [V18_SYNTHESIS_Complete_Analysis.md](computer:///mnt/user-data/outputs/V18_SYNTHESIS_Complete_Analysis.md)
   - Critical analysis of v17 vs v18
   - What to keep, what to replace
   - Size: 29KB

3. [FINAL_DECISION_v18_GO.md](computer:///mnt/user-data/outputs/FINAL_DECISION_v18_GO.md)
   - Executive summary
   - Gemini's key insights
   - Size: 6KB

4. [AI_HANDOFF_BUILD_V18_REPO.md](computer:///mnt/user-data/outputs/AI_HANDOFF_BUILD_V18_REPO.md)
   - Complete instructions for AI
   - Phase-by-phase build guide
   - Size: 37KB

**Critical (1 file - you already have)**:

5. Article_Eater_v17_0_real_with_UPGRADE_not_sure_if_dual_concatenated.txt
   - v17 codebase
   - AI needs this to extend, not rewrite
   - Size: ~100KB

**Recommended (3 more)**:

6. [SYSTEM_VISION.md](computer:///mnt/user-data/outputs/SYSTEM_VISION.md)
   - Article Eater domain context
   - CNfA vocabulary, user profile
   - Size: 20KB

7. Gemini_handoff_explanation.docx (you have this)
   - Original v18 memo from architect
   - High-level vision
   - Size: ~30KB

8. Claudes_questions_to_gemini_and_its_answers.docx (you have this)
   - Full Q&A with Gemini
   - Context for critical decisions
   - Size: ~40KB

**Optional**:

9. [HANDOFF_CHECKLIST_V18.md](computer:///mnt/user-data/outputs/HANDOFF_CHECKLIST_V18.md)
   - Step-by-step guide for YOU
   - What to check at each phase
   - Size: 18KB

**Total**: 8-9 files, ~250KB

---

## HANDOFF WORKFLOW

### Phase 1: Prepare (10 minutes)

**For Governance**:
```bash
mkdir ~/handoff-governance
cd ~/handoff-governance

# Download from this chat:
# - GOVERNANCE_KIT_v3_Repo_Agnostic.md
# - CONVERSATION_LEDGER.template.yml
# - SYSTEM_VISION.template.md
# - install.sh
# - conversation_guard.py
# - CONVERSATION_LEDGER.yml (example)
# - AI_HANDOFF_BUILD_GOVERNANCE_REPO.md
# - HANDOFF_CHECKLIST.md
```

**For v18**:
```bash
mkdir ~/handoff-v18
cd ~/handoff-v18

# Download from this chat:
# - V18_IMPLEMENTATION_GUIDE_FINAL.md
# - V18_SYNTHESIS_Complete_Analysis.md
# - FINAL_DECISION_v18_GO.md
# - AI_HANDOFF_BUILD_V18_REPO.md
# - SYSTEM_VISION.md

# Copy from your files:
# - Article_Eater_v17_0_real_with_UPGRADE_not_sure_if_dual_concatenated.txt
# - Gemini_handoff_explanation.docx
# - Claudes_questions_to_gemini_and_its_answers.docx

# Optional:
# - HANDOFF_CHECKLIST_V18.md
```

---

### Phase 2: Start AI Instance(s) (2 minutes)

**Single AI Approach**:
```
1. Open https://claude.ai (or Gemini/ChatGPT)
2. Start new chat
3. Upload files for Track 1 OR Track 2
```

**Dual AI Approach**:
```
1. Open https://claude.ai in one tab
2. Open https://gemini.google.com in another tab
3. Upload governance files to Claude
4. Upload v18 files to Gemini
5. Work both in parallel
```

---

### Phase 3: Send Magic Prompts

#### Governance Magic Prompt

```
I need you to build the "governance-kit-v3" repository from specifications.

CONTEXT:
I'm doing AI-assisted development ("vibe coding"). AI has no memory between 
sessions, causing "Intent Rot" - I forget why code exists.

Governance kit v3.0 solves this with:
- CONVERSATION_LEDGER.yml (tracks sessions, decisions, context)
- SYSTEM_VISION.md (high-level project overview)
- install.sh (one-command installation for any project)

I'm attaching 5-8 files for reference.

YOUR TASK:
Read AI_HANDOFF_BUILD_GOVERNANCE_REPO.md first (complete instructions).
Then generate ALL files for standalone repo:
- README.md (main docs)
- Refined install.sh (production quality)
- docs/ directory (4 guides)
- examples/ directory (3 projects: article-eater, biometric-tool, web-scraper)
- tests/ directory (3 test scripts)
- scripts/ directory (validation)

CRITICAL REQUIREMENTS:
- Must work pre-Git (I'm not on GitHub yet)
- Must be installable with: ./install.sh /path/to/target
- Must be repo-agnostic (works on ANY project)
- Must be production-ready (error handling, validation)
- Templates must use {{VARIABLE}} syntax

Generate files one by one, starting with README.md.
Ready? Please confirm you understand before starting.
```

---

#### v18 Magic Prompt

```
I need you to implement Article Eater v18 from complete specifications.

CONTEXT:
Article Eater is an evidence synthesis tool for Cognitive Neuroscience for 
Architecture (CNfA). It extracts data from papers to build Bayesian Belief Networks.

CRITICAL PROBLEM v18 FIXES:
v17 uses parent_finding_id which conflates CAUSAL and TAXONOMIC relationships.
This is "catastrophically flawed" - cannot build proper BBN.

v18 SOLUTION:
- finding_links table with link_type field (CAUSAL vs TAXONOMIC)
- Set of Support (paper-type-specific confidence calculation)
- Agent_Classifier (detect RCT, Theory, Meta-Analysis)
- Agent_PromptRouter (different prompts per type)
- HITL workflow (human approves proposals)

I'm attaching:
1. V18_IMPLEMENTATION_GUIDE_FINAL.md (architect's definitive answers)
2. V18_SYNTHESIS_Complete_Analysis.md (critical analysis)
3. AI_HANDOFF_BUILD_V18_REPO.md (complete instructions)
4. v17 codebase (what exists, what to extend)
5. Context docs (domain knowledge, original memo)

YOUR TASK:
Read AI_HANDOFF_BUILD_V18_REPO.md first (complete instructions).
Then generate ALL v18 files:
- 4 SQL migrations (finding_links, paper_type, set_of_support, backfill)
- 4 agent modules (Classifier, PromptRouter, Aggregator, Linker)
- 3 confidence classes (Experimental, Meta, Theoretical)
- 5 prompt templates (RCT, Theory, Meta, Obs, Qual)
- 2 route modules (Librarian, Synthesizer)
- Documentation + tests

CRITICAL REQUIREMENTS:
- finding_links MUST have link_type field (CAUSAL vs TAXONOMIC)
- Confidence formulas MUST match architect's exact specs:
  * RCT: conf = (0.4*N) + (0.3*p) + (0.3*d)
  * Meta: conf = (0.3*k) + (0.5*CI) + (0.2*I²)
  * Theory: conf = -1.0 (HITL required)
- Production-ready code (error handling, validation)

Generate systematically starting with migrations.
Ready? Please confirm you understand before starting.
```

---

### Phase 4: Guide AI Generation

**For Governance (2-3 hours)**:

Follow [HANDOFF_CHECKLIST.md](computer:///mnt/user-data/outputs/HANDOFF_CHECKLIST.md) exactly:

1. **README.md** (20 min)
   - Check: Comprehensive (200+ lines)
   - Check: Clear install instructions
   - Check: Examples of usage

2. **Refined install.sh** (15 min)
   - Check: Error handling
   - Check: Colorized output
   - Check: Dry-run mode

3. **docs/** (45 min)
   - USAGE_GUIDE.md
   - CI_INTEGRATION.md
   - EXAMPLES.md
   - TROUBLESHOOTING.md

4. **examples/** (50 min)
   - article-eater/ (CNfA domain)
   - biometric-tool/ (generic)
   - web-scraper/ (simple)

5. **tests/** (30 min)
   - test_install.sh
   - test_templates.py
   - test_guard.py

6. **Finalize** (10 min)
   - LICENSE (MIT)
   - CHANGELOG.md

**For v18 (4-6 hours)**:

Follow [HANDOFF_CHECKLIST_V18.md](computer:///mnt/user-data/outputs/HANDOFF_CHECKLIST_V18.md) exactly:

1. **Migrations** (1 hour)
   - 005_create_finding_links.sql (CRITICAL)
   - 006_add_paper_type.sql
   - 007_add_set_of_support.sql
   - 008_backfill_v17_data.sql

2. **Agents** (2 hours)
   - agent_classifier.py (two-pass triage)
   - agent_prompt_router.py (multi-template)
   - agent_aggregator.py (HITL)
   - agent_linker.py (HITL)

3. **Confidence** (1 hour)
   - setof_support.py (calculator)
   - experimental_support.py (MUST match Gemini's formula)
   - meta_support.py (MUST match Gemini's formula)
   - theoretical_support.py (return -1.0)

4. **Prompts** (1 hour)
   - 7_panel_prompt_RCT.txt
   - 7_panel_prompt_THEORY.txt
   - 7_panel_prompt_META.txt
   - 7_panel_prompt_OBSERVATIONAL.txt
   - 7_panel_prompt_QUALITATIVE.txt

5. **GUI** (1-2 hours)
   - routes_librarian.py (instant 7-panel)
   - routes_synthesizer.py (HITL approval)
   - Templates (inventory, approve)

6. **Docs + Tests** (1 hour)
   - v18_DEPLOYMENT_GUIDE.md
   - v18_ARCHITECTURE.md
   - test_agents.py, test_confidence.py, etc.

---

### Phase 5: Review & Validate

**Governance Review (1 hour)**:

```bash
cd governance-kit-v3

# Test install
./install.sh /tmp/test-governance

# Expected prompts:
# - Project name?
# - Tagline?
# - Domain?
# - Version?
# - Your name?
# - Role?
# - Institution?
# - Tech stack?

# Validate
cd /tmp/test-governance
python tools/governance/scripts/conversation_guard.py

# Expected: ✅ CONVERSATION GUARD PASSED

# Check customization
grep "project:" governance/CONVERSATION_LEDGER.yml
# Should show: project: "[YOUR INPUT]"
# NOT: project: "{{PROJECT_NAME}}"
```

**v18 Review (2 hours)**:

```bash
cd article-eater-v18

# Test migrations on v17 backup
cp ~/article-eater/ae.db ae_v17_backup.db
cp ae_v17_backup.db ae_test.db

sqlite3 ae_test.db < migrations/005_create_finding_links.sql
sqlite3 ae_test.db < migrations/006_add_paper_type.sql
sqlite3 ae_test.db < migrations/007_add_set_of_support.sql
sqlite3 ae_test.db < migrations/008_backfill_v17_data.sql

# Validate migrations
sqlite3 ae_test.db "SELECT sql FROM sqlite_master WHERE name='finding_links';"
# Check: link_type field exists with CHECK constraint

sqlite3 ae_test.db "SELECT link_type, COUNT(*) FROM finding_links GROUP BY link_type;"
# Expected:
# TAXONOMIC | [number of v17 parent_finding_id relationships]
# CAUSAL    | 0

# Test confidence formulas
python tests/test_confidence.py
# Check: RCT formula matches Gemini's exactly
# Check: Meta formula matches Gemini's exactly
# Check: Theoretical returns -1.0
```

---

## QUALITY ASSURANCE

### Governance QA Checklist

- [ ] README.md is comprehensive (200+ lines)
- [ ] install.sh has error handling and colorized output
- [ ] Templates use {{VARIABLE}} syntax (not hardcoded)
- [ ] Examples are realistic (Article Eater, BioMetric, WebScraper)
- [ ] docs/ has 4 guides (Usage, CI, Examples, Troubleshooting)
- [ ] tests/ has 3 working tests
- [ ] Installation works: `./install.sh /tmp/test`
- [ ] Validation passes: `conversation_guard.py`
- [ ] No {{PLACEHOLDERS}} left after installation

### v18 QA Checklist

- [ ] finding_links table has link_type field with CHECK constraint
- [ ] Confidence formulas match Gemini's EXACTLY:
  - [ ] RCT: `(0.4*N) + (0.3*p) + (0.3*d)`
  - [ ] Meta: `(0.3*k) + (0.5*CI) + (0.2*I²)`
  - [ ] Theory: `-1.0`
- [ ] Agent_Classifier implements two-pass triage
- [ ] Agent_PromptRouter handles hybrids (multiple prompts merged)
- [ ] 5 prompt files exist, extract correct Set of Support
- [ ] Librarian route has instant 7-panel (no lazy loading)
- [ ] Synthesizer route has HITL approval interface
- [ ] Migrations run on v17 backup without errors
- [ ] Tests pass: `pytest tests/`

---

## DEPLOYMENT STRATEGY

### Governance Deployment (Immediate)

```bash
# Day 1: Install on Article Eater
cd governance-kit-v3
./install.sh ~/article-eater

# Customize SYSTEM_VISION.md
vim ~/article-eater/governance/SYSTEM_VISION.md
# Fill in: Vision, Problem, Architecture, Tech Stack

# Start logging immediately
vim ~/article-eater/governance/CONVERSATION_LEDGER.yml
# Add session for "Built governance kit"

# Test context loading
# 1. Start new Claude chat
# 2. Upload CONVERSATION_LEDGER.yml
# 3. Say: "Read the ledger, then help me with v18"
# 4. Verify Claude has context
```

### v18 Deployment (Phased - 7 weeks)

```bash
# Week 1: Database Only
cd ~/article-eater
cp ae.db ae_pre_v18_backup.db

python scripts/migrate_v17_to_v18.py
python tests/test_migrations.py

# Log in governance:
- session_id: "week-01-database"
  decision: DEC-006 (migrate to finding_links)

# Week 2: Agents Only
pytest tests/test_agents.py
# Tune Agent_Classifier keywords if needed

# Log tuning decisions in governance

# Week 3: Confidence
python scripts/test_confidence_tuning.py
# Tune weights if scores don't match expert judgment

# Log tuning decisions (IMPORTANT for academic rigor)

# Weeks 4-7: GUI + HITL
# Deploy Librarian (Week 5)
# Deploy Synthesizer (Weeks 6-7)
# Test full workflow

# Log all sessions in governance
```

---

## INSPECTION PROTOCOL

### When to Bring Back to Me (Original Claude Instance)

**After Governance Build**:
1. Upload generated `governance-kit-v3/` (zip file or key files)
2. Say: "Review governance kit for quality"
3. I'll check:
   - README completeness
   - Template correctness
   - Example realism
   - Test coverage
   - Install.sh robustness

**After v18 Build**:
1. Upload generated `article-eater-v18/` (zip or key files)
2. Say: "Review v18 implementation for correctness"
3. I'll check:
   - finding_links schema vs Gemini's spec
   - Confidence formulas (EXACT match required)
   - Agent implementations vs two-pass spec
   - Prompt quality
   - GUI completeness
   - Documentation quality

**During Deployment**:
1. Upload updated CONVERSATION_LEDGER.yml weekly
2. Say: "Review v18 deployment progress, Week N"
3. I'll check:
   - Session logs complete
   - Decisions documented
   - Issues tracked
   - Next steps clear

---

## FILES SUMMARY

### All Handoff Files (20 total)

**Governance Track (8 files)**:
1. GOVERNANCE_KIT_v3_Repo_Agnostic.md (25KB)
2. CONVERSATION_LEDGER.template.yml (5KB)
3. SYSTEM_VISION.template.md (9KB)
4. install.sh (3KB)
5. conversation_guard.py (5KB)
6. CONVERSATION_LEDGER.yml (12KB) - example
7. AI_HANDOFF_BUILD_GOVERNANCE_REPO.md (15KB)
8. HANDOFF_CHECKLIST.md (11KB)

**v18 Track (9 files)**:
1. V18_IMPLEMENTATION_GUIDE_FINAL.md (29KB)
2. V18_SYNTHESIS_Complete_Analysis.md (29KB)
3. FINAL_DECISION_v18_GO.md (6KB)
4. AI_HANDOFF_BUILD_V18_REPO.md (37KB)
5. SYSTEM_VISION.md (20KB)
6. Article_Eater_v17_0_real_with_UPGRADE_not_sure_if_dual.txt (100KB)
7. Gemini_handoff_explanation.docx (30KB)
8. Claudes_questions_to_gemini_and_its_answers.docx (40KB)
9. HANDOFF_CHECKLIST_V18.md (18KB)

**Master Files (3 files)**:
1. AI_HANDOFF_BUILD_GOVERNANCE_REPO.md (this file)
2. AI_HANDOFF_BUILD_V18_REPO.md (see above)
3. MASTER_HANDOFF_GUIDE.md (this file)

**Total**: 20 files, ~400KB

---

## ESTIMATED TIMELINE

### Fast Track (Governance First, Sequential)

- **Day 1 (4 hours)**: Build governance → Test → Install
- **Day 2 (6 hours)**: Build v18 (phases 1-4)
- **Day 3 (4 hours)**: Build v18 (phases 5-7) → Test
- **Day 4 (4 hours)**: Review both → Integrate v18
- **Weeks 1-7 (20-40 hours)**: Deploy v18 phased

**Total**: 18 hours upfront + 30 hours over 7 weeks = **~50 hours**

---

### Parallel Track (Both Simultaneously)

- **Day 1 (6 hours)**: Both AIs work in parallel
- **Day 2 (6 hours)**: Review both, test both
- **Day 3 (4 hours)**: Install governance, integrate v18
- **Weeks 1-7 (20-40 hours)**: Deploy v18 phased

**Total**: 16 hours upfront + 30 hours over 7 weeks = **~46 hours**

---

### Lazy Track (v18 First, Governance Later)

- **Day 1-2 (10 hours)**: Build v18
- **Day 3 (4 hours)**: Test v18, start integration
- **Day 4 (5 hours)**: Build governance, backfill ledger
- **Weeks 1-7 (20-40 hours)**: Deploy v18 phased

**Total**: 19 hours upfront + 30 hours over 7 weeks = **~50 hours**

---

## FINAL CHECKLIST

Before starting handoff:

- [ ] I understand the two-track approach
- [ ] I've chosen my strategy (Governance first / v18 first / Parallel)
- [ ] I've downloaded all required files
- [ ] I have time for 4-10 hours of AI supervision
- [ ] I have Article Eater v17 backup (for v18 testing)
- [ ] I'm ready to start tracking in governance immediately

After governance build:

- [ ] Governance kit installs without errors
- [ ] Templates get customized correctly
- [ ] conversation_guard.py validates
- [ ] Examples look realistic
- [ ] Documentation is complete

After v18 build:

- [ ] finding_links table schema matches Gemini's spec
- [ ] Confidence formulas match EXACTLY
- [ ] Agents implement two-pass triage
- [ ] Prompts extract correct Set of Support
- [ ] Migrations run on v17 backup
- [ ] Tests pass

After integration:

- [ ] Governance installed on Article Eater
- [ ] v18 files integrated with v17 codebase
- [ ] First governance session logged
- [ ] Week 1 deployment ready to start

---

## SUPPORT & TROUBLESHOOTING

### If AI Gets Stuck

**Governance**:
- Point to specific section in AI_HANDOFF_BUILD_GOVERNANCE_REPO.md
- Show example from CONVERSATION_LEDGER.yml
- Ask: "Read section [X], implement that"

**v18**:
- Point to specific section in AI_HANDOFF_BUILD_V18_REPO.md
- Show Gemini's formula from V18_IMPLEMENTATION_GUIDE_FINAL.md
- Ask: "This MUST be exact. Regenerate."

### If Tests Fail

**Governance**:
- Installation fails → Check Python version, bash, permissions
- Guard fails → Check YAML syntax, indentation
- Templates not replaced → Check sed syntax in install.sh

**v18**:
- Migrations fail → Check v17 schema, adjust backfill logic
- Confidence wrong → Re-check formulas against Gemini's spec
- Classification wrong → Tune keywords, test on more papers

### If You Need Review

Upload generated files to this Claude instance:
1. Zip the repo
2. Upload to new message
3. Say: "Review [governance kit / v18] for quality"
4. I'll do detailed inspection

---

## FINAL NOTES

### What Makes This Handoff Special

1. **Complete Specifications**: Not vague, every detail specified
2. **Gemini's Exact Answers**: All formulas, all decisions documented
3. **Quality Checklists**: Know exactly what to verify
4. **Phased Approach**: Low risk, validation at each step
5. **Governance Integration**: Track provenance from day 1

### What You'll Achieve

**After Governance Build**:
- Universal tracking system
- Works on ANY project
- Install on Article Eater in 15 minutes
- Never lose context again

**After v18 Build**:
- "Epistemological Engine" realized
- No more CAUSAL/TAXONOMIC conflation
- Transparent confidence calculation
- HITL workflow for quality control
- Proper BBN construction possible

**After Full Deployment**:
- v18 running in production
- All sessions logged in governance
- All decisions documented
- Full academic rigor
- Ready for next project

---

**Status**: COMPLETE ✅  
**Ready to Execute**: YES ✅  
**Everything Documented**: YES ✅  

**GO BUILD! 🚀**

---

## QUICK REFERENCE

**Governance Magic Prompt**: See [Phase 3](#phase-3-send-magic-prompts)  
**v18 Magic Prompt**: See [Phase 3](#phase-3-send-magic-prompts)  
**Governance Files**: [Track 1 Files](#track-1-governance-kit)  
**v18 Files**: [Track 2 Files](#track-2-v18-implementation)  
**Governance Checklist**: [HANDOFF_CHECKLIST.md](computer:///mnt/user-data/outputs/HANDOFF_CHECKLIST.md)  
**v18 Checklist**: [HANDOFF_CHECKLIST_V18.md](computer:///mnt/user-data/outputs/HANDOFF_CHECKLIST_V18.md)  
**Deployment Strategy**: [Phase 5](#deployment-strategy)  
**Inspection Protocol**: [When to Bring Back](#inspection-protocol)